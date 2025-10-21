import json
import threading
import time
from typing import Dict, Any

from redis import Redis

from .common import CommonMethods, DEFAULT_EXCEPTIONS, REDIS_EXCEPTIONS
from .message import Message
from ..core.exception import exception_to_dict
from ..core.retry import retry_wrapper
from ..log import footprint
from ..redis.connection import RedisInstance


class RedisStreamer(CommonMethods):
    """
    Synchronous Redis Streams consumer with:
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

        self._redis_client: Redis = self._redis_instance.get_redis_client()
        self._maintenance_thread_started = False

    def _reconnect(self):
        """Attempt to reconnect to Redis with retries."""
        for attempt in range(3):
            try:
                footprint.leave(
                    log_type="warning",
                    subject="Attempting to reconnect to Redis",
                    message=f"Attempt {attempt + 1} of 3",
                    controller=f"{__name__}.RedisStreamer._reconnect",
                )
                if self._redis_client:
                    self._redis_client.close()
                self._redis_instance.reset_sync_pool()
                self._redis_client = self._redis_instance.get_redis_client()
                if self._redis_client.ping():
                    footprint.leave(
                        log_type="info",
                        subject="Successfully reconnected to Redis",
                        controller=f"{__name__}.RedisStreamer._reconnect",
                    )
                    return
            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="error",
                    subject="Redis reconnection attempt failed",
                    message=f"Attempt {attempt + 1} failed.",
                    controller=f"{__name__}.RedisStreamer._reconnect",
                    payload=exception_to_dict(e),
                )
                time.sleep(2 ** attempt)  # Exponential backoff
        footprint.leave(
            log_type="critical",
            subject="Failed to reconnect to Redis after 3 attempts",
            controller=f"{__name__}.RedisStreamer._reconnect",
        )
        raise ConnectionError("Failed to reconnect to Redis after 3 attempts")

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    def _consumer_group_exists(self, channel_name: str, consumer_group: str) -> bool:
        try:
            groups = self._redis_client.xinfo_groups(channel_name)
            return any(
                group["name"].decode("utf-8") == consumer_group for group in groups
            )
        except REDIS_EXCEPTIONS:
            return False
        except Exception:
            return False

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    def send_message(self, channel: str, message: Message):
        """Send single message."""
        footprint.leave(
            log_type="info",
            subject="Sending single message",
            controller=f"{__name__}.RedisStreamer.send_message",
            message=f"Sending message to channel '{channel}'.",
            payload={"channel": channel, "message_name": message.name},
        )
        fields: Dict[Any, Any] = message.get_json_encoded()
        self._redis_client.xadd(channel, fields)

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    def subscribe(self, channel_name: str, start_from_latest: bool = True):
        """Subscribe to a Redis stream channel."""
        controller = f"{__name__}.RedisStreamer.subscribe"
        listener_name = self.listener_name
        group = self._group_name(channel_name, listener_name)

        if not self._consumer_group_exists(channel_name, group):
            try:
                start_id = "$" if start_from_latest else "0-0"
                self._redis_client.xgroup_create(
                    channel_name, group, start_id, mkstream=True
                )
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
                footprint.leave(
                    log_type="error",
                    subject="Error creating consumer group",
                    message=f"Error creating consumer group {group} for channel {channel_name}.",
                    controller=controller,
                    payload=exception_to_dict(e),
                )
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
    def _reserve_once(self, processed_key: str, message_id: str, now_ms: int) -> bool:
        try:
            added = self._redis_client.zadd(
                processed_key, {message_id: now_ms}, nx=True
            )
            return added == 1
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="error",
                subject="Dedup error",
                controller=f"{__name__}.RedisStreamer._reserve_once",
                message="ZADD NX failed; skipping message to avoid duplicate processing.",
                payload={
                    "error": exception_to_dict(e),
                    "message_id": message_id,
                    "key": processed_key,
                },
            )
            return False
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Dedup error",
                controller=f"{__name__}.RedisStreamer._reserve_once",
                message="ZADD NX failed; skipping message to avoid duplicate processing.",
                payload={
                    "error": exception_to_dict(e),
                    "message_id": message_id,
                    "key": processed_key,
                },
            )
            return False

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    def _ack_message(self, channel: str, group: str, message_id: str):
        try:
            self._redis_client.xack(channel, group, message_id)
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="error",
                subject="Ack error",
                controller=f"{__name__}.RedisStreamer._ack_message",
                message="XACK failed.",
                payload={
                    "error": exception_to_dict(e),
                    "channel": channel,
                    "group": group,
                    "message_id": message_id,
                },
            )
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Ack error",
                controller=f"{__name__}.RedisStreamer._ack_message",
                message="XACK failed.",
                payload={
                    "error": exception_to_dict(e),
                    "channel": channel,
                    "group": group,
                    "message_id": message_id,
                },
            )

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    def _consume_one(
        self,
        channel: str,
        consumer_group: str,
        listener_name: str,
        block_time: float,
        count: int = 32,
    ):
        controller = f"{__name__}.RedisStreamer._consume_one"
        try:
            msgs = self._redis_client.xreadgroup(
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
                reserved = self._reserve_once(processed_key, message_id, now_ms)
                if not reserved:
                    self._ack_message(channel, consumer_group, message_id)
                    continue

                try:
                    raw_name = fields.get(b"name")
                    raw_body = fields.get(b"body")
                    if raw_name is None or raw_body is None:
                        raise ValueError("Missing required fields 'name' or 'body'.")
                    name = (
                        raw_name.decode("utf-8")
                        if isinstance(raw_name, bytes)
                        else raw_name
                    )
                    body = (
                        json.loads(raw_body.decode("utf-8"))
                        if isinstance(raw_body, (bytes, bytearray))
                        else raw_body
                    )
                except Exception as e:
                    self._dead_letter(
                        channel,
                        "decode/schema",
                        message_id,
                        {"listener": listener_name, "error": str(e)},
                    )
                    self._ack_message(channel, consumer_group, message_id)
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

                self._ack_message(channel, consumer_group, message_id)

        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="error",
                message="Redis connection error in sync consumer.",
                controller=controller,
                subject="Redis Connection Error",
                payload={
                    "error": exception_to_dict(e),
                    "channel": channel,
                    "group": consumer_group,
                },
            )
            self._reconnect()

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
                    self.subscribe(channel_name=channel)
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

    def _consume_loop(
        self,
        channel: str,
        listener: str,
        group: str,
        block_time: float,
        count: int,
        rest_time: float,
    ):
        """Dedicated loop per channel."""
        controller = f"{__name__}.RedisStreamer._consume_loop"

        footprint.leave(
            log_type="info",
            message=f"Launching {channel} consumer thread",
            controller=controller,
            subject="Multi-threaded Redis consumer",
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
                self._consume_one(channel, group, listener, block_time, count)
                elapsed = time.time() - before

                if elapsed < block_time:
                    idle_backoff = min(idle_backoff * 2, 2.0)
                else:
                    idle_backoff = rest_time

                time.sleep(idle_backoff)
            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="error",
                    subject="Consumer loop error",
                    controller=controller,
                    message=f"Error in consumer loop for channel {channel}. Restarting loop.",
                    payload={"error": exception_to_dict(e), "channel": channel},
                )
                time.sleep(5)
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Consumer loop error",
                    controller=controller,
                    message=f"Error in consumer loop for channel {channel}. Restarting loop.",
                    payload={"error": exception_to_dict(e), "channel": channel},
                )
                time.sleep(5)

    def persist_consume(
        self, rest_time: float = 0.1, block_time: float = 5.0, count: int = 32
    ):
        """Continuously consume messages from all subscribed channels."""
        controller = f"{__name__}.RedisStreamer.persist_consume"

        if not self._maintenance_thread_started:
            mt = threading.Thread(target=self._maintenance_loop, daemon=True)
            mt.start()
            self._maintenance_thread_started = True

        threads = {}
        for channel, listener, group in self._subscriptions:
            thread_args = (channel, listener, group, block_time, count, rest_time)
            t = threading.Thread(
                target=self._consume_loop,
                args=thread_args,
                daemon=True,
            )
            t.start()
            threads[(channel, listener, group)] = (t, thread_args)

        while True:
            time.sleep(60)
            for key, (thread, args) in list(threads.items()):
                if not thread.is_alive():
                    footprint.leave(
                        log_type="warning",
                        subject="Consumer thread died",
                        controller=controller,
                        message=f"Consumer thread for channel {key[0]} died. Restarting.",
                        payload={"channel": key[0], "listener": key[1]},
                    )
                    new_thread = threading.Thread(
                        target=self._consume_loop, args=args, daemon=True
                    )
                    new_thread.start()
                    threads[key] = (new_thread, args)

    @retry_wrapper(exceptions=DEFAULT_EXCEPTIONS)
    def maintain_ledgers(self):
        """Cleanup for dedup ZSETs."""
        controller = f"{__name__}.RedisStreamer.maintain_ledgers"
        now_ms = self._server_now_ms()
        cutoff = now_ms - self._dedup_window_ms

        for channel_name, _, consumer_group in self._subscriptions:
            key = self._processed_zset_key(channel_name, consumer_group)
            removed = self._redis_client.zremrangebyscore(
                key, min="-inf", max=f"({cutoff}"
            )
            if removed:
                footprint.leave(
                    log_type="info",
                    message=f"Purged {removed} dedup entries",
                    controller=controller,
                    subject="Dedup ledger maintenance",
                    payload={"key": key, "removed": removed},
                )

    def _maintenance_loop(self):
        """Background thread for periodic maintenance tasks."""
        controller = f"{__name__}.RedisStreamer._maintenance_loop"

        while True:
            try:
                time.sleep(self._ledger_cleanup_interval / 1000)
                self.maintain_ledgers()
                self._last_ledger_cleanup = self._server_now_ms()
            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="error",
                    subject="Maintenance loop error",
                    controller=controller,
                    message="Error in maintenance loop",
                    payload={"error": exception_to_dict(e)},
                )
                time.sleep(60)
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Maintenance loop error",
                    controller=controller,
                    message="Error in maintenance loop",
                    payload={"error": exception_to_dict(e)},
                )
                time.sleep(60)

    def cleanup(self):
        """Cleanup resources."""
        try:
            footprint.leave(
                log_type="info",
                subject="Cleanup completed",
                controller=f"{__name__}.RedisStreamer.cleanup",
                message="RedisStreamer cleanup completed",
            )
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Cleanup error",
                controller=f"{__name__}.RedisStreamer.cleanup",
                message="Error during cleanup",
                payload={"error": exception_to_dict(e)},
            )

    def get_stats(self) -> Dict:
        """Get current statistics about the streamer."""
        stats = {
            "listener_name": self.listener_name,
            "consumer_instance": self.consumer_instance_name,
            "subscriptions": len(self._subscriptions),
            "channels": [sub[0] for sub in self._subscriptions],
            "dedup_window_ms": self._dedup_window_ms,
            "last_ledger_cleanup": self._last_ledger_cleanup,
        }

        return stats

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
        return False
