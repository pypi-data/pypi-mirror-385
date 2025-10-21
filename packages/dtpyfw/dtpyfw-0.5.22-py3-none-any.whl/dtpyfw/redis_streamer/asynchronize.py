import asyncio
import json
import time
from typing import Dict, Optional

from redis.asyncio import Redis as AsyncRedis

from .common import CommonMethods, DEFAULT_EXCEPTIONS, REDIS_EXCEPTIONS
from .message import Message
from ..core.exception import exception_to_dict
from ..core.retry import retry_wrapper
from ..log import footprint
from ..redis.connection import RedisInstance


class AsyncRedisStreamer(CommonMethods):
    """
    Asynchronous Redis Streams consumer with:
      - Decoupled fan-out across microservices (one group per service).
      - Bounded at-most-once (per group) via a ZSET de-dup window.
      - Lower network load using adaptive sleeping.
      - Connection pooling for efficient connection reuse.
    """

    def __init__(
        self,
        redis_instance: RedisInstance,
        consumer_name: str,
        dedup_window_ms: int = 7 * 24 * 60 * 60 * 1000,
    ):
        super().__init__(redis_instance, consumer_name, dedup_window_ms)

        self._redis_client: Optional[AsyncRedis] = None
        self._maintenance_task: Optional[asyncio.Task] = None
        self._cleanup_channels_task: Optional[asyncio.Task] = None

    async def _reconnect(self):
        """Attempt to reconnect to Redis with retries asynchronously."""
        for attempt in range(3):
            try:
                footprint.leave(
                    log_type="warning",
                    subject="Attempting to reconnect to Redis (async)",
                    message=f"Attempt {attempt + 1} of 3",
                    controller=f"{__name__}.AsyncRedisStreamer._reconnect",
                )
                if self._redis_client is not None:
                    await self._redis_client.close()
                self._redis_client = None
                await self._redis_instance.reset_async_pool()
                client = await self._get_client()
                if await client.ping():
                    footprint.leave(
                        log_type="info",
                        subject="Successfully reconnected to Redis (async)",
                        controller=f"{__name__}.AsyncRedisStreamer._reconnect",
                    )
                    return
            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="error",
                    subject="Redis reconnection attempt failed (async)",
                    message=f"Attempt {attempt + 1} failed.",
                    controller=f"{__name__}.AsyncRedisStreamer._reconnect",
                    payload=exception_to_dict(e),
                )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        footprint.leave(
            log_type="critical",
            subject="Failed to reconnect to Redis after 3 attempts (async)",
            controller=f"{__name__}.AsyncRedisStreamer._reconnect",
        )
        raise ConnectionError("Failed to reconnect to Redis after 3 attempts")

    async def _get_client(self) -> AsyncRedis:
        """Lazily initialize and return the async Redis client."""
        if self._redis_client is None:
            self._redis_client = (
                await self._redis_instance.get_async_redis_client()
            )
        return self._redis_client

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    async def _consumer_group_exists(
        self, channel_name: str, consumer_group: str
    ) -> bool:
        try:
            client = await self._get_client()
            groups = await client.xinfo_groups(channel_name)
            return any(
                group["name"].decode("utf-8") == consumer_group for group in groups
            )
        except Exception:
            return False

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    async def send_message(self, channel: str, message: Message):
        """Send message asynchronously."""
        footprint.leave(
            log_type="info",
            subject="Sending single message asynchronously",
            controller=f"{__name__}.AsyncRedisStreamer.send_message",
            message=f"Sending message to channel '{channel}' asynchronously.",
            payload={"channel": channel, "message_name": message.name},
        )
        client = await self._get_client()
        await client.xadd(channel, message.get_json_encoded())

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    async def subscribe(self, channel_name: str, start_from_latest: bool = True):
        """Subscribe to a Redis stream channel asynchronously."""
        controller = f"{__name__}.AsyncRedisStreamer.subscribe"
        listener_name = self.listener_name
        group = self._group_name(channel_name, listener_name)

        if not await self._consumer_group_exists(channel_name, group):
            try:
                start_id = "$" if start_from_latest else "0-0"
                client = await self._get_client()
                await client.xgroup_create(channel_name, group, start_id, mkstream=True)
                footprint.leave(
                    log_type="info",
                    subject="Subscription created",
                    message=f"Listener {listener_name} has been subscribed to {channel_name}.",
                    controller=controller,
                    payload={
                        "channel": channel_name,
                        "group": group,
                        "listener": listener_name,
                        "start_from_latest": start_from_latest,
                    },
                )
            except REDIS_EXCEPTIONS as e:
                await self._reconnect()
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Error creating consumer group",
                    message=f"Error creating consumer group {group} for channel {channel_name}.",
                    controller=controller,
                    payload=exception_to_dict(e),
                )

        self._subscriptions.append((channel_name, listener_name, group))
        return self

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    async def _reserve_once(
        self, processed_key: str, message_id: str, now_ms: int
    ) -> bool:
        try:
            client = await self._get_client()
            added = await client.zadd(processed_key, {message_id: now_ms}, nx=True)
            return added == 1
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="error",
                subject="Dedup error",
                controller=f"{__name__}.AsyncRedisStreamer._reserve_once",
                message="ZADD NX failed; skipping message to avoid duplicate processing.",
                payload={
                    "error": exception_to_dict(e),
                    "message_id": message_id,
                    "key": processed_key,
                },
            )
            await self._reconnect()
            return False
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Dedup error",
                controller=f"{__name__}.AsyncRedisStreamer._reserve_once",
                message="ZADD NX failed; skipping message to avoid duplicate processing.",
                payload={
                    "error": exception_to_dict(e),
                    "message_id": message_id,
                    "key": processed_key,
                },
            )
            return False

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    async def _ack_message(self, channel: str, group: str, message_id: str):
        try:
            client = await self._get_client()
            await client.xack(channel, group, message_id)
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Ack error",
                controller=f"{__name__}.AsyncRedisStreamer._ack_message",
                message="XACK failed.",
                payload={
                    "error": exception_to_dict(e),
                    "channel": channel,
                    "group": group,
                    "message_id": message_id,
                },
            )

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    async def _consume_one(
        self,
        channel: str,
        consumer_group: str,
        listener_name: str,
        block_time: float,
        count: int = 32,
    ):
        controller = f"{__name__}.AsyncRedisStreamer._consume_one"

        try:
            client = await self._get_client()
            msgs = await client.xreadgroup(
                groupname=consumer_group,
                consumername=self.consumer_instance_name,
                streams={channel: ">"},
                block=int(block_time * 1000),
                count=count,
            )
            if not msgs:
                return

            _, batch = msgs[0]
            processed_key = self._processed_zset_key(channel, consumer_group)
            now_ms = self._server_now_ms()

            for message_id, fields in batch:
                reserved = await self._reserve_once(
                    processed_key, message_id, now_ms
                )
                if not reserved:
                    await self._ack_message(channel, consumer_group, message_id)
                    continue

                try:
                    raw_name = fields.get(b"name")
                    raw_body = fields.get(b"body")
                    if raw_name is None or raw_body is None:
                        raise ValueError("Missing name or body")
                    name = raw_name.decode("utf-8")
                    body = json.loads(raw_body.decode("utf-8"))
                except Exception as e:
                    self._dead_letter(
                        channel,
                        "decode/schema",
                        message_id,
                        {"listener": listener_name, "error": str(e)},
                    )
                    await self._ack_message(channel, consumer_group, message_id)
                    continue

                for handler in self._handlers.get((channel, listener_name), []):
                    try:
                        footprint.leave(
                            log_type="info",
                            subject="Invoking handler",
                            controller=controller,
                            message=f"Invoking message {name} handler.",
                            payload={
                                "listener": listener_name,
                                "name": name,
                                "body": body,
                            },
                        )

                        import inspect
                        if inspect.iscoroutinefunction(handler):
                            await handler(name=name, payload=body)
                        else:
                            handler(name=name, payload=body)

                        footprint.leave(
                            log_type="info",
                            subject="Handler invoked",
                            controller=controller,
                            message=f"Handler for message {name} invoked successfully.",
                            payload={
                                "listener": listener_name,
                                "name": name,
                            },
                        )
                    except Exception as e:
                        self._dead_letter(
                            channel,
                            "handler",
                            message_id,
                            {
                                "listener": listener_name,
                                "handler": handler.__name__,
                                "error": str(e),
                                "name": name,
                            },
                        )
                        break

                await self._ack_message(channel, consumer_group, message_id)

        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="error",
                message="Redis connection error in async consumer.",
                controller=controller,
                subject="Redis Connection Error",
                payload={
                    "error": exception_to_dict(e),
                    "channel": channel,
                    "group": consumer_group,
                },
            )
            await self._reconnect()

        except Exception as e:
            if "NOGROUP" in str(e):
                try:
                    footprint.leave(
                        log_type="warning",
                        subject=f"Need to resubscribe to channel {channel}",
                        message=f"Trying to resubscribe to {channel}.",
                        controller=controller,
                        payload={
                            "listener_name": listener_name,
                            "channel": channel,
                            "consumer_group": consumer_group,
                            "error": exception_to_dict(e),
                        },
                    )
                    await self.subscribe(channel_name=channel)
                except REDIS_EXCEPTIONS as e_resub:
                    footprint.leave(
                        log_type="error",
                        message=f"Error resubscribing to channel {channel}",
                        controller=controller,
                        subject="Resubscribing Error",
                        payload={
                            "error": exception_to_dict(e_resub),
                            "group": consumer_group,
                            "listener": listener_name,
                        },
                    )
                except Exception as e_resub:
                    footprint.leave(
                        log_type="error",
                        message=f"Error resubscribing to channel {channel}",
                        controller=controller,
                        subject="Resubscribing Error",
                        payload={
                            "error": exception_to_dict(e_resub),
                            "group": consumer_group,
                            "listener": listener_name,
                        },
                    )
            else:
                footprint.leave(
                    log_type="error",
                    message=f"Error consuming messages from channel {channel}",
                    controller=controller,
                    subject="Consuming Messages Error",
                    payload={
                        "error": exception_to_dict(e),
                        "group": consumer_group,
                        "listener": listener_name,
                    },
                )

    async def _consume_loop(
        self,
        channel: str,
        listener: str,
        group: str,
        block_time: float,
        count: int,
        rest_time: float,
    ):
        """Dedicated loop per channel."""
        controller = f"{__name__}.AsyncRedisStreamer._consume_loop"

        footprint.leave(
            log_type="info",
            message=f"Launching {channel} async consumer task",
            controller=controller,
            subject="Async Redis consumer",
            payload={
                "channel": channel,
                "listener": listener,
                "group": group,
            },
        )

        idle_backoff = rest_time

        while True:
            try:
                before = time.time()
                await self._consume_one(
                    channel, group, listener, block_time, count
                )
                elapsed = time.time() - before

                if elapsed < block_time:
                    idle_backoff = min(idle_backoff * 2, 2.0)
                else:
                    idle_backoff = rest_time

                await asyncio.sleep(idle_backoff)

            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="error",
                    subject="Consumer loop error",
                    controller=controller,
                    message=f"Error in consumer loop for channel {channel}. Restarting loop.",
                    payload={"error": exception_to_dict(e), "channel": channel},
                )
                await self._reconnect()
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Consumer loop error",
                    controller=controller,
                    message=f"Error in consumer loop for channel {channel}. Restarting loop.",
                    payload={"error": exception_to_dict(e), "channel": channel},
                )
                await asyncio.sleep(5)

    async def persist_consume(
        self,
        rest_time: float = 0.1,
        block_time: float = 5.0,
        count: int = 32,
        cleanup_interval: float = 300.0,
    ):
        """Continuously consume messages from all subscribed channels asynchronously."""
        controller = f"{__name__}.AsyncRedisStreamer.persist_consume"

        if self._maintenance_task is None or self._maintenance_task.done():
            self._maintenance_task = asyncio.create_task(
                self._maintenance_loop()
            )

        if self._channel_retention and (
            self._cleanup_channels_task is None
            or self._cleanup_channels_task.done()
        ):
            self._cleanup_channels_task = asyncio.create_task(
                self._cleanup_channels_loop(cleanup_interval)
            )

        tasks = {}
        for channel, listener, group in self._subscriptions:
            task_args = (channel, listener, group, block_time, count, rest_time)
            task = asyncio.create_task(self._consume_loop(*task_args))
            tasks[(channel, listener, group)] = (task, task_args)

        while True:
            await asyncio.sleep(60)
            for key, (task, args) in list(tasks.items()):
                if task.done():
                    try:
                        await task
                    except Exception as e:
                        footprint.leave(
                            log_type="warning",
                            subject="Consumer task died",
                            controller=controller,
                            message=f"Consumer task for channel {key[0]} died. Restarting.",
                            payload={
                                "channel": key[0],
                                "listener": key[1],
                                "error": exception_to_dict(e),
                            },
                        )
                    else:
                        footprint.leave(
                            log_type="warning",
                            subject="Consumer task finished unexpectedly",
                            controller=controller,
                            message=f"Consumer task for channel {key[0]} finished. Restarting.",
                            payload={"channel": key[0], "listener": key[1]},
                        )

                    new_task = asyncio.create_task(self._consume_loop(*args))
                    tasks[key] = (new_task, args)

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    async def maintain_ledgers(self):
        """Async cleanup for dedup ZSETs."""
        controller = f"{__name__}.AsyncRedisStreamer.maintain_ledgers"
        now_ms = self._server_now_ms()
        cutoff = now_ms - self._dedup_window_ms

        client = await self._get_client()

        for channel_name, _, consumer_group in self._subscriptions:
            key = self._processed_zset_key(channel_name, consumer_group)
            removed = await client.zremrangebyscore(key, min="-inf", max=f"({cutoff}")
            if removed:
                footprint.leave(
                    log_type="info",
                    message=f"Purged {removed} async dedup entries",
                    controller=controller,
                    subject="Async dedup ledger maintenance",
                    payload={"key": key, "removed": removed},
                )

    async def _maintenance_loop(self):
        """Async background task for periodic maintenance."""
        controller = f"{__name__}.AsyncRedisStreamer._maintenance_loop"

        while True:
            try:
                await asyncio.sleep(self._ledger_cleanup_interval / 1000)
                await self.maintain_ledgers()
                self._last_ledger_cleanup = self._server_now_ms()
            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="error",
                    subject="Maintenance loop error",
                    controller=f"{__name__}.AsyncRedisStreamer._maintenance_loop",
                    message="Error in maintenance loop",
                    payload={"error": exception_to_dict(e)},
                )
                await self._reconnect()
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Maintenance loop error",
                    controller=f"{__name__}.AsyncRedisStreamer._maintenance_loop",
                    message="Error in maintenance loop",
                    payload={"error": exception_to_dict(e)},
                )
                await asyncio.sleep(60)

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    async def cleanup_channels(self):
        """Async clean up messages from specified channels based on a retention period."""
        controller = f"{__name__}.AsyncRedisStreamer.cleanup_channels"
        now_ms = self._server_now_ms()

        client = await self._get_client()
        for channel, retention in self._channel_retention.items():
            if retention is None:
                continue

            try:
                group = self._group_name(channel, self.listener_name)
                processed_key = self._processed_zset_key(channel, group)
                cutoff = now_ms - retention

                removed_count = await client.zremrangebyscore(
                    processed_key, min="-inf", max=f"({cutoff}"
                )

                if removed_count:
                    footprint.leave(
                        log_type="info",
                        message=f"Cleaned up {removed_count} old async dedup entries from channel {channel}",
                        controller=controller,
                        subject="Async channel cleanup",
                        payload={"channel": channel, "removed_count": removed_count},
                    )

            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Async channel cleanup error",
                    controller=controller,
                    message=f"Error cleaning up channel {channel}",
                    payload={"error": exception_to_dict(e), "channel": channel},
                )

    async def _cleanup_channels_loop(self, cleanup_interval: float = 300.0):
        """Async background task for periodic channel cleanup."""
        controller = f"{__name__}.AsyncRedisStreamer._cleanup_channels_loop"

        while True:
            try:
                await asyncio.sleep(cleanup_interval)
                await self.cleanup_channels()
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Async cleanup channels loop error",
                    controller=controller,
                    message="Error in async cleanup channels loop",
                    payload={"error": exception_to_dict(e)},
                )
                await asyncio.sleep(60)

    async def cleanup(self):
        """Async cleanup resources."""
        try:
            await self.stop_consuming()

            footprint.leave(
                log_type="info",
                subject="Cleanup completed",
                controller=f"{__name__}.AsyncRedisStreamer.cleanup",
                message="AsyncRedisStreamer cleanup completed",
            )
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="error",
                subject="Cleanup error",
                controller=f"{__name__}.AsyncRedisStreamer.cleanup",
                message="Error during cleanup",
                payload={"error": exception_to_dict(e)},
            )
            await self._reconnect()
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Cleanup error",
                controller=f"{__name__}.AsyncRedisStreamer.cleanup",
                message="Error during cleanup",
                payload={"error": exception_to_dict(e)},
            )

    async def stop_consuming(self):
        """Stop all consuming tasks and clean up resources."""
        controller = f"{__name__}.AsyncRedisStreamer.stop_consuming"

        footprint.leave(
            log_type="info",
            subject="Stopping consumer",
            controller=controller,
            message="Stopping all consumer tasks",
        )

        try:
            if self._maintenance_task:
                self._maintenance_task.cancel()
                await self._maintenance_task
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="error",
                subject="Error stopping maintenance task",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error stopping maintenance task",
                payload={"error": exception_to_dict(e)},
            )
            await self._reconnect()
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Error stopping maintenance task",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error stopping maintenance task",
                payload={"error": exception_to_dict(e)},
            )

        try:
            if self._cleanup_channels_task:
                self._cleanup_channels_task.cancel()
                await self._cleanup_channels_task
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="error",
                subject="Error stopping cleanup channels task",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error stopping cleanup channels task",
                payload={"error": exception_to_dict(e)},
            )
            await self._reconnect()
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Error stopping cleanup channels task",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error stopping cleanup channels task",
                payload={"error": exception_to_dict(e)},
            )

        try:
            if self._redis_client:
                await self._redis_client.close()
                self._redis_client = None
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="error",
                subject="Error closing Redis client",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error closing Redis client",
                payload={"error": exception_to_dict(e)},
            )
            await self._reconnect()
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Error closing Redis client",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error closing Redis client",
                payload={"error": exception_to_dict(e)},
            )

    async def get_stats(self) -> Dict:
        """Get current statistics about the streamer."""
        stats = {
            "listener_name": self.listener_name,
            "consumer_instance": self.consumer_instance_name,
            "subscriptions": len(self._subscriptions),
            "channels": [sub[0] for sub in self._subscriptions],
            "dedup_window_ms": self._dedup_window_ms,
            "last_ledger_cleanup": self._last_ledger_cleanup,
        }

        if self._maintenance_task:
            stats["maintenance_running"] = not self._maintenance_task.done()

        return stats

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.cleanup()
        return False
