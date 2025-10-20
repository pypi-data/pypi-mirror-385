import asyncio
import inspect
import json
import time
from typing import Optional

from redis.asyncio import Redis as AsyncRedis

from .connection import RedisInstance
from .streamer import RedisStreamer, Message
from ..core.exception import exception_to_dict
from ..log import footprint


class AsyncRedisStreamer(RedisStreamer):
    """Async version of RedisStreamer."""

    def __init__(self, redis_instance: RedisInstance, consumer_name: str, dedup_window_ms: Optional[int] = None):
        super().__init__(redis_instance, consumer_name, dedup_window_ms)
        self._redis_client: AsyncRedis = asyncio.get_event_loop().run_until_complete(
            self._redis_instance.get_async_redis_client()
        )

    async def send_message(self, channel: str, message: Message):
        """Async send message."""
        await self._redis_client.xadd(channel, message.get_json_encoded())

    async def _consumer_group_exists(self, channel_name: str, consumer_group: str) -> bool:
        try:
            groups = await self._redis_client.xinfo_groups(channel_name)
            return any(group["name"].decode("utf-8") == consumer_group for group in groups)
        except Exception:
            return False

    async def subscribe(self, channel_name: str, start_from_latest: bool = True):
        listener_name = self.listener_name
        group = self._group_name(channel_name, listener_name)

        if not await self._consumer_group_exists(channel_name, group):
            try:
                start_id = "$" if start_from_latest else "0-0"
                await self._redis_client.xgroup_create(channel_name, group, start_id, mkstream=True)
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Error creating consumer group",
                    message=f"Error creating consumer group {group} for channel {channel_name}.",
                    controller=f"{__name__}.AsyncConsumer.subscribe",
                    payload=exception_to_dict(e),
                )

        self._subscriptions.append((channel_name, listener_name, group))
        return self

    async def _reserve_once(self, processed_key: str, message_id: str, now_ms: int) -> bool:
        try:
            added = await self._redis_client.zadd(processed_key, {message_id: now_ms}, nx=True)
            return added == 1
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Dedup error",
                controller=f"{__name__}.AsyncConsumer._reserve_once",
                message="ZADD NX failed; skipping message to avoid duplicate processing.",
                payload={"error": exception_to_dict(e), "message_id": message_id, "key": processed_key},
            )
            return False

    async def _ack_message(self, channel: str, group: str, message_id: str):
        try:
            await self._redis_client.xack(channel, group, message_id)
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Ack error",
                controller=f"{__name__}.AsyncConsumer._ack_message",
                message="XACK failed.",
                payload={"error": exception_to_dict(e), "channel": channel, "group": group, "message_id": message_id},
            )

    async def _consume_one(self, channel: str, consumer_group: str, listener_name: str, block_time: float, count: int = 32):
        try:
            msgs = await self._redis_client.xreadgroup(
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

            for message_id, fields in batch:
                now_ms = self._server_now_ms()
                if not await self._reserve_once(processed_key, message_id, now_ms):
                    await self._ack_message(channel, consumer_group, message_id)
                    continue

                try:
                    raw_name = fields.get(b"name")
                    raw_body = fields.get(b"body")
                    name = raw_name.decode("utf-8")
                    body = json.loads(raw_body.decode("utf-8"))
                except Exception as e:
                    self._dead_letter(channel, "decode/schema", message_id, {"listener": listener_name, "error": str(e)})
                    await self._ack_message(channel, consumer_group, message_id)
                    continue

                handler_failed = False
                for handler in self._handlers.get((channel, listener_name), []):
                    try:
                        if inspect.iscoroutinefunction(handler):
                            await handler(name=name, payload=body)
                        else:
                            handler(name=name, payload=body)
                    except Exception as e:
                        handler_failed = True
                        self._dead_letter(channel, "handler", message_id, {
                            "listener": listener_name,
                            "handler": handler.__name__,
                            "error": str(e),
                            "name": name,
                        })
                        await self._ack_message(channel, consumer_group, message_id)
                        break

                if not handler_failed:
                    await self._ack_message(channel, consumer_group, message_id)

        except Exception as e:
            if "NOGROUP" in str(e):
                await self.subscribe(channel_name=channel)
            else:
                footprint.leave(
                    log_type="error",
                    message=f"Error consuming messages from channel {channel}",
                    controller=f"{__name__}.AsyncConsumer._consume_one",
                    subject="Consuming Messages Error",
                    payload={"error": exception_to_dict(e), "group": consumer_group, "listener": listener_name},
                )

    async def _consume_loop(self, channel: str, listener: str, group: str, block_time: float, count: int, rest_time: float):
        idle_backoff = rest_time
        while True:
            before = time.time()
            await self._consume_one(channel, group, listener, block_time, count)
            elapsed = time.time() - before
            if elapsed < block_time:
                idle_backoff = min(idle_backoff * 2, 2.0)
            else:
                idle_backoff = rest_time
            await asyncio.sleep(idle_backoff)

    async def persist_consume(self, rest_time: float = 0.1, block_time: float = 5.0, count: int = 32):
        tasks = []
        for channel, listener, group in self._subscriptions:
            tasks.append(asyncio.create_task(
                self._consume_loop(channel, listener, group, block_time, count, rest_time)
            ))
        await asyncio.gather(*tasks)
