import asyncio
import inspect
import json
import os
import re
import socket
import threading
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, DefaultDict, Dict, List, Optional, Tuple

from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import ResponseError

from ..core.exception import exception_to_dict
from ..core.retry import retry_wrapper
from ..log import footprint
from .connection import RedisInstance

__all__ = (
    "RedisStreamer",
    "Message",
)


@dataclass
class Message:
    name: str
    body: Dict

    def get_json_encoded(self):
        return {"name": self.name, "body": json.dumps(self.body, default=str)}


class RedisStreamer:
    """
    Optimized Redis Streams consumer with:
      - Decoupled fan-out across microservices (one group per service).
      - Bounded at-most-once (per group) via a ZSET de-dup window.
      - Lower network load using Redis pipelining and adaptive sleeping.
      - Connection pooling for efficient connection reuse.
      - Batch operations to reduce server load.
    """

    def __init__(
        self,
        redis_instance: RedisInstance,
        consumer_name: str,
        dedup_window_ms: Optional[int] = None,
        batch_size: int = 100,  # Default batch size for operations
        pipeline_size: int = 1000,  # Max pipeline commands before execution
    ):
        self.listener_name: str = self._sanitize(consumer_name, maxlen=128)
        self.consumer_instance_name: str = self._gen_consumer_name()

        self._redis_instance = redis_instance
        self._redis_client = self._redis_instance.get_redis_client()

        # Lazy initialization for async client to avoid event loop issues
        self._redis_async_client: Optional[AsyncRedis] = None

        self._subscriptions: List[Tuple[str, str, str]] = []
        self._handlers: DefaultDict[Tuple[str, str], List[Callable]] = defaultdict(list)

        # Default dedup window: 7 days
        self._dedup_window_ms: int = (
            dedup_window_ms
            if (dedup_window_ms and dedup_window_ms > 0)
            else 7 * 24 * 60 * 60 * 1000
        )

        # Batch configuration
        self._batch_size = batch_size
        self._pipeline_size = pipeline_size
        self._message_buffer: DefaultDict[str, List[Message]] = defaultdict(list)
        self._buffer_lock = threading.Lock()
        self._last_flush_time = time.time()
        self._flush_interval = 0.5  # Flush buffer every 500ms

        # Maintenance control
        self._last_ledger_cleanup = 0
        self._ledger_cleanup_interval = 300_000  # 5 minutes (ms)
        self._maintenance_thread_started = False
        self._async_maintenance_task = None
        self._async_cleanup_channels_task = None
        self._channel_retention = {}

    async def _get_async_client(self) -> AsyncRedis:
        """Lazily initialize and return the async Redis client."""
        if self._redis_async_client is None:
            self._redis_async_client = (
                await self._redis_instance.get_async_redis_client()
            )
        return self._redis_async_client

    def register_channel(
        self,
        channel_name: str,
        retention_ms: Optional[int] = None,
    ):
        """
        Register channel metadata. If retention_ms is provided, this instance will try to
        become the channel OWNER and will clean up messages after retention_ms.
        """
        controller = f"{__name__}.RedisStreamer.register_channel"

        footprint.leave(
            log_type="info",
            subject="Channel registered",
            message=f"Channel {channel_name} registered.",
            controller=controller,
            payload={
                "channel_name": channel_name,
                "retention_ms": retention_ms,
            },
        )
        self._channel_retention[channel_name] = retention_ms
        return self

    @staticmethod
    def _sanitize(s: str, maxlen: int) -> str:
        s = re.sub(r"[^a-zA-Z0-9._:-]+", "-", s or "")
        return s[:maxlen]

    def _gen_consumer_name(self) -> str:
        host = os.getenv("POD_NAME") or os.getenv("HOSTNAME") or socket.gethostname()
        pid = os.getpid()
        rnd = uuid.uuid4().hex[:8]
        name = ".".join([self.listener_name, self._sanitize(host, 64), str(pid), rnd])
        return self._sanitize(name, maxlen=200)

    @staticmethod
    def _server_now_ms() -> int:
        return int(time.time() * 1000)

    def _consumer_group_exists(self, channel_name: str, consumer_group: str) -> bool:
        try:
            groups = self._redis_client.xinfo_groups(channel_name)
            return any(
                group["name"].decode("utf-8") == consumer_group for group in groups
            )
        except Exception:
            return False

    async def _async_consumer_group_exists(
        self, channel_name: str, consumer_group: str
    ) -> bool:
        try:
            client = await self._get_async_client()
            groups = await client.xinfo_groups(channel_name)
            return any(
                group["name"].decode("utf-8") == consumer_group for group in groups
            )
        except Exception:
            return False

    @staticmethod
    def _group_name(channel: str, listener_name: str) -> str:
        return f"{channel}:{listener_name}:cg"

    @staticmethod
    def _processed_zset_key(channel: str, group: str) -> str:
        return f"stream:{channel}:group:{group}:processed"

    @retry_wrapper()
    def send_message(self, channel: str, message: Message):
        """Send single message (backward compatibility)."""
        self._redis_client.xadd(channel, message.get_json_encoded())

    @retry_wrapper()
    def send_messages_batch(self, channel: str, messages: List[Message]):
        """Send multiple messages in a batch using pipeline."""
        if not messages:
            return

        pipe = self._redis_client.pipeline(transaction=False)
        for i, message in enumerate(messages):
            pipe.xadd(channel, message.get_json_encoded())
            # Execute pipeline periodically to avoid memory issues
            if (i + 1) % self._pipeline_size == 0:
                pipe.execute()
                pipe = self._redis_client.pipeline(transaction=False)

        # Execute remaining commands
        if len(pipe):
            pipe.execute()

    def buffer_message(self, channel: str, message: Message):
        """Buffer message for batch sending."""
        with self._buffer_lock:
            self._message_buffer[channel].append(message)

            # Auto-flush if buffer is full or time threshold reached
            if (
                len(self._message_buffer[channel]) >= self._batch_size
                or time.time() - self._last_flush_time > self._flush_interval
            ):
                self.flush_buffer(channel)

    def flush_buffer(self, channel: Optional[str] = None):
        """Flush buffered messages for a specific channel or all channels."""
        with self._buffer_lock:
            channels = [channel] if channel else list(self._message_buffer.keys())

            for ch in channels:
                if ch in self._message_buffer and self._message_buffer[ch]:
                    messages = self._message_buffer[ch]
                    self._message_buffer[ch] = []
                    # Send batch outside lock to avoid blocking
                    threading.Thread(
                        target=self.send_messages_batch,
                        args=(ch, messages),
                        daemon=True,
                    ).start()

            self._last_flush_time = time.time()

    async def async_send_message(self, channel: str, message: Message):
        """Async send message."""
        client = await self._get_async_client()
        await client.xadd(channel, message.get_json_encoded())

    async def async_send_messages_batch(self, channel: str, messages: List[Message]):
        """Async send multiple messages in a batch using pipeline."""
        if not messages:
            return

        client = await self._get_async_client()
        pipe = client.pipeline(transaction=False)
        for i, message in enumerate(messages):
            pipe.xadd(channel, message.get_json_encoded())  # noqa
            # Execute pipeline periodically
            if (i + 1) % self._pipeline_size == 0:
                await pipe.execute()
                pipe = client.pipeline(transaction=False)

        # Execute remaining commands
        if len(pipe):
            await pipe.execute()

    def subscribe(self, channel_name: str, start_from_latest: bool = True):
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

    async def async_subscribe(self, channel_name: str, start_from_latest: bool = True):
        controller = f"{__name__}.RedisStreamer.subscribe"
        listener_name = self.listener_name
        group = self._group_name(channel_name, listener_name)

        if not await self._async_consumer_group_exists(channel_name, group):
            try:
                start_id = "$" if start_from_latest else "0-0"
                client = await self._get_async_client()
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

    def register_handler(
        self,
        channel_name: str,
        handler_func: Callable,
        listener_name: Optional[str] = None,
    ):
        listener = listener_name or self.listener_name
        self._handlers[(channel_name, listener)].append(handler_func)
        return self

    def _reserve_once(self, processed_key: str, message_id: str, now_ms: int) -> bool:
        try:
            added = self._redis_client.zadd(
                processed_key, {message_id: now_ms}, nx=True
            )
            return added == 1
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

    async def _async_reserve_once(
        self, processed_key: str, message_id: str, now_ms: int
    ) -> bool:
        try:
            client = await self._get_async_client()
            added = await client.zadd(processed_key, {message_id: now_ms}, nx=True)
            return added == 1
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

    def _dead_letter(self, channel: str, reason: str, message_id: str, extra: Dict):
        try:
            payload = {"reason": reason, "channel": channel, "message_id": message_id}
            if extra:
                payload.update(extra)
            footprint.leave(
                log_type="error",
                subject="Message failed",
                controller=f"{__name__}.RedisStreamer._dead_letter",
                message=f"Message failure on channel '{channel}' (reason={reason})",
                payload=payload,
            )
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Dead-letter logging error",
                controller=f"{__name__}.RedisStreamer._dead_letter",
                message="Failed to log message failure",
                payload={
                    "error": exception_to_dict(e),
                    "channel": channel,
                    "reason": reason,
                    "message_id": message_id,
                },
            )

    def _ack_pipeline(self, pipe, channel: str, group: str, message_id: str):
        try:
            pipe.xack(channel, group, message_id)
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Ack error",
                controller=f"{__name__}.RedisStreamer._ack_pipeline",
                message="XACK failed.",
                payload={
                    "error": exception_to_dict(e),
                    "channel": channel,
                    "group": group,
                    "message_id": message_id,
                },
            )

    async def _async_ack_message(self, channel: str, group: str, message_id: str):
        try:
            client = await self._get_async_client()
            await client.xack(channel, group, message_id)
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

    @retry_wrapper()
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
            # Increase default count for better batching
            batch_count = max(count, self._batch_size)
            msgs = self._redis_client.xreadgroup(
                groupname=consumer_group,
                consumername=self.consumer_instance_name,
                streams={channel: ">"},
                block=int(block_time * 1000),
                count=batch_count,
            )
            if not msgs:
                return

            _, batch = msgs[0]
            processed_key = self._processed_zset_key(channel, consumer_group)

            # Prepare batch operations
            message_ids = [msg_id for msg_id, _ in batch]
            now_ms = self._server_now_ms()

            # Reserve all messages at once
            reserved_ids = self._reserve_batch(processed_key, message_ids, now_ms)
            reserved_set = set(reserved_ids)

            # Process messages and collect ACKs
            pipe = self._redis_client.pipeline(transaction=False)
            ack_count = 0

            for message_id, fields in batch:
                # Skip if not reserved (already processed)
                if message_id not in reserved_set:
                    pipe.xack(channel, consumer_group, message_id)  # noqa
                    ack_count += 1
                    # Execute pipeline periodically
                    if ack_count % self._pipeline_size == 0:
                        pipe.execute()
                        pipe = self._redis_client.pipeline(transaction=False)
                        ack_count = 0
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
                    pipe.xack(channel, consumer_group, message_id)  # noqa
                    ack_count += 1
                    continue

                for handler in self._handlers.get((channel, listener_name), []):
                    try:
                        handler(name=name, payload=body)
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

                # ACK the message
                pipe.xack(channel, consumer_group, message_id)  # noqa
                ack_count += 1

                if ack_count % self._pipeline_size == 0:
                    pipe.execute()
                    pipe = self._redis_client.pipeline(transaction=False)
                    ack_count = 0

            # Execute remaining ACKs
            if ack_count > 0:
                pipe.execute()

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
                except ResponseError as inner_e:
                    if "BUSYGROUP" not in str(inner_e):
                        footprint.leave(
                            log_type="error",
                            controller=controller,
                            subject="Creating missing consumer group Error",
                            message="Error creating missing consumer group",
                            payload={
                                "listener_name": listener_name,
                                "channel": channel,
                                "consumer_group": consumer_group,
                                "error": exception_to_dict(inner_e),
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

    async def _async_consume_one(
        self,
        channel: str,
        consumer_group: str,
        listener_name: str,
        block_time: float,
        count: int = 32,
    ):
        try:
            # Increase default count for better batching
            batch_count = max(count, self._batch_size)
            client = await self._get_async_client()
            msgs = await client.xreadgroup(
                groupname=consumer_group,
                consumername=self.consumer_instance_name,
                streams={channel: ">"},
                block=int(block_time * 1000),
                count=batch_count,
            )
            if not msgs:
                return

            _, batch = msgs[0]
            processed_key = self._processed_zset_key(channel, consumer_group)

            # Prepare batch operations
            message_ids = [msg_id for msg_id, _ in batch]
            now_ms = self._server_now_ms()

            # Reserve all messages at once
            reserved_ids = await self._async_reserve_batch(
                processed_key, message_ids, now_ms
            )
            reserved_set = set(reserved_ids)

            # Process messages and collect ACKs
            pipe = client.pipeline(transaction=False)
            ack_count = 0

            for message_id, fields in batch:
                # Skip if not reserved
                if message_id not in reserved_set:
                    pipe.xack(channel, consumer_group, message_id)  # noqa
                    ack_count += 1
                    if ack_count % self._pipeline_size == 0:
                        await pipe.execute()
                        pipe = client.pipeline(transaction=False)
                        ack_count = 0
                    continue

                try:
                    raw_name = fields.get(b"name")
                    raw_body = fields.get(b"body")
                    name = raw_name.decode("utf-8")
                    body = json.loads(raw_body.decode("utf-8"))
                except Exception as e:
                    self._dead_letter(
                        channel,
                        "decode/schema",
                        message_id,
                        {"listener": listener_name, "error": str(e)},
                    )
                    pipe.xack(channel, consumer_group, message_id)  # noqa
                    ack_count += 1
                    continue

                for handler in self._handlers.get((channel, listener_name), []):
                    try:
                        if inspect.iscoroutinefunction(handler):
                            await handler(name=name, payload=body)
                        else:
                            handler(name=name, payload=body)
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

                # ACK the message
                pipe.xack(channel, consumer_group, message_id)  # noqa
                ack_count += 1

                if ack_count % self._pipeline_size == 0:
                    await pipe.execute()
                    pipe = client.pipeline(transaction=False)
                    ack_count = 0

            # Execute remaining ACKs
            if ack_count > 0:
                await pipe.execute()

        except Exception as e:
            if "NOGROUP" in str(e):
                await self.async_subscribe(channel_name=channel)
            else:
                footprint.leave(
                    log_type="error",
                    message=f"Error consuming messages from channel {channel}",
                    controller=f"{__name__}.RedisStreamer._consume_one",
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
        """Dedicated loop per channel with enhanced batching."""
        idle_backoff = rest_time
        # Use larger count for better batching
        effective_count = max(count, self._batch_size)

        while True:
            before = time.time()
            self._consume_one(channel, group, listener, block_time, effective_count)
            elapsed = time.time() - before

            # adaptive sleep: slow down when idle
            if elapsed < block_time:
                idle_backoff = min(idle_backoff * 2, 2.0)
            else:
                idle_backoff = rest_time

            time.sleep(idle_backoff)

    async def _async_consume_loop(
        self,
        channel: str,
        listener: str,
        group: str,
        block_time: float,
        count: int,
        rest_time: float,
    ):
        """Dedicated loop per channel with enhanced batching."""
        idle_backoff = rest_time
        # Use larger count for better batching
        effective_count = max(count, self._batch_size)

        while True:
            before = time.time()
            await self._async_consume_one(
                channel, group, listener, block_time, effective_count
            )
            elapsed = time.time() - before

            if elapsed < block_time:
                idle_backoff = min(idle_backoff * 2, 2.0)
            else:
                idle_backoff = rest_time

            await asyncio.sleep(idle_backoff)

    def persist_consume(
        self, rest_time: float = 0.1, block_time: float = 5.0, count: int = 32
    ):
        controller = f"{__name__}.RedisStreamer.persist_consume"

        if not self._maintenance_thread_started:
            # Start maintenance thread
            mt = threading.Thread(target=self._maintenance_loop, daemon=True)
            mt.start()
            # Start buffer flush thread
            ft = threading.Thread(target=self._buffer_flush_loop, daemon=True)
            ft.start()
            self._maintenance_thread_started = True

        for channel, listener, group in self._subscriptions:
            footprint.leave(
                log_type="info",
                message="Launching per-channel consumer thread with batching",
                controller=controller,
                subject="Multi-threaded Redis consumer",
                payload={
                    "channel": channel,
                    "listener": listener,
                    "group": group,
                    "batch_size": self._batch_size,
                },
            )

            t = threading.Thread(
                target=self._consume_loop,
                args=(channel, listener, group, block_time, count, rest_time),
                daemon=True,
            )
            t.start()

        while True:
            time.sleep(60)

    async def async_persist_consume(
        self,
        rest_time: float = 0.1,
        block_time: float = 5.0,
        count: int = 32,
        cleanup_interval: float = 300.0,
    ):
        """
        Continuously consume messages from all subscribed channels.

        Args:
            rest_time (float): Time to sleep between consumption cycles (default: 0.1 seconds).
            block_time (float): Time to block waiting for messages (default: 5.0 seconds).
            count (int): Number of messages to read per batch (default: 32).
            cleanup_interval (float): How often to run channel cleanup in seconds (default: 300 = 5 minutes).
        """
        # Start a single async maintenance task for the whole process
        if self._async_maintenance_task is None or self._async_maintenance_task.done():
            self._async_maintenance_task = asyncio.create_task(
                self._async_maintenance_loop()
            )
            # Also start buffer flush task
            asyncio.create_task(self._async_buffer_flush_loop())

        # Start cleanup channels task if retention config is provided
        if self._channel_retention and (
            self._async_cleanup_channels_task is None
            or self._async_cleanup_channels_task.done()
        ):
            self._async_cleanup_channels_task = asyncio.create_task(
                self._async_cleanup_channels_loop(cleanup_interval)
            )

        tasks = []
        for channel, listener, group in self._subscriptions:
            tasks.append(
                asyncio.create_task(
                    self._async_consume_loop(
                        channel, listener, group, block_time, count, rest_time
                    )
                )
            )
        await asyncio.gather(*tasks)

    def _buffer_flush_loop(self):
        """Periodically flush message buffers."""
        while True:
            time.sleep(self._flush_interval)
            try:
                self.flush_buffer()
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    message="Buffer flush error",
                    controller=f"{__name__}.RedisStreamer._buffer_flush_loop",
                    subject="Buffer flush error",
                    payload={"error": exception_to_dict(e)},
                )

    async def _async_buffer_flush_loop(self):
        """Async periodically flush message buffers."""
        while True:
            await asyncio.sleep(self._flush_interval)
            try:
                # Flush any async buffers if implemented
                pass
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    message="Async buffer flush error",
                    controller=f"{__name__}.RedisStreamer._async_buffer_flush_loop",
                    subject="Async buffer flush error",
                    payload={"error": exception_to_dict(e)},
                )

    @retry_wrapper()
    def maintain_ledgers(self):
        controller = f"{__name__}.RedisStreamer.maintain_ledgers"
        now_ms = self._server_now_ms()
        cutoff = now_ms - self._dedup_window_ms

        # Use pipeline for batch cleanup
        pipe = self._redis_client.pipeline(transaction=False)
        cleanup_count = 0

        for channel_name, _, consumer_group in self._subscriptions:
            key = self._processed_zset_key(channel_name, consumer_group)
            pipe.zremrangebyscore(key, min="-inf", max=f"({cutoff}")  # noqa
            cleanup_count += 1

            # Execute pipeline periodically
            if cleanup_count % self._pipeline_size == 0:
                results = pipe.execute()
                for i, removed in enumerate(results):
                    if removed:
                        footprint.leave(
                            log_type="info",
                            message=f"Purged {removed} dedup entries",
                            controller=controller,
                            subject="Dedup ledger maintenance",
                            payload={"key": f"batch_{i}", "removed": removed},
                        )
                pipe = self._redis_client.pipeline(transaction=False)
                cleanup_count = 0

        # Execute remaining cleanups
        if cleanup_count > 0:
            results = pipe.execute()
            for i, removed in enumerate(results):
                if removed:
                    footprint.leave(
                        log_type="info",
                        message=f"Purged {removed} dedup entries",
                        controller=controller,
                        subject="Dedup ledger maintenance",
                        payload={"key": f"final_batch_{i}", "removed": removed},
                    )

    @retry_wrapper()
    async def async_maintain_ledgers(self):
        """Async cleanup for dedup ZSETs with batching."""
        controller = f"{__name__}.RedisStreamer.async_maintain_ledgers"
        now_ms = self._server_now_ms()
        cutoff = now_ms - self._dedup_window_ms

        # Use pipeline for batch cleanup
        client = await self._get_async_client()
        pipe = client.pipeline(transaction=False)
        cleanup_count = 0

        for channel_name, _, consumer_group in self._subscriptions:
            key = self._processed_zset_key(channel_name, consumer_group)
            pipe.zremrangebyscore(key, min="-inf", max=f"({cutoff}")  # noqa
            cleanup_count += 1

            if cleanup_count % self._pipeline_size == 0:
                results = await pipe.execute()
                for i, removed in enumerate(results):
                    if removed:
                        footprint.leave(
                            log_type="info",
                            message=f"Purged {removed} async dedup entries",
                            controller=controller,
                            subject="Async dedup ledger maintenance",
                            payload={"key": f"batch_{i}", "removed": removed},
                        )
                pipe = self._redis_async_client.pipeline(transaction=False)
                cleanup_count = 0

        if cleanup_count > 0:
            results = await pipe.execute()
            for i, removed in enumerate(results):
                if removed:
                    footprint.leave(
                        log_type="info",
                        message=f"Purged {removed} async dedup entries",
                        controller=controller,
                        subject="Async dedup ledger maintenance",
                        payload={"key": f"final_batch_{i}", "removed": removed},
                    )

    def _reserve_batch(
        self, processed_key: str, message_ids: List[str], now_ms: int
    ) -> List[str]:
        """Reserve multiple message IDs at once, return list of successfully reserved IDs."""
        if not message_ids:
            return []

        try:
            # Build mapping for ZADD
            pipe = self._redis_client.pipeline(transaction=False)

            # Check existing entries first
            for mid in message_ids:
                pipe.zscore(processed_key, mid)  # noqa
            scores = pipe.execute()

            # Filter out already processed messages
            new_ids = [mid for mid, score in zip(message_ids, scores) if score is None]

            if new_ids:
                # Add new IDs in batch with NX flag
                new_mapping = {mid: now_ms for mid in new_ids}
                self._redis_client.zadd(processed_key, new_mapping, nx=True)

            return new_ids
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Batch dedup error",
                controller=f"{__name__}.RedisStreamer._reserve_batch",
                message="Batch ZADD NX failed",
                payload={
                    "error": exception_to_dict(e),
                    "key": processed_key,
                    "count": len(message_ids),
                },
            )
            return []

    async def _async_reserve_batch(
        self, processed_key: str, message_ids: List[str], now_ms: int
    ) -> List[str]:
        """Async reserve multiple message IDs at once."""
        if not message_ids:
            return []

        try:
            client = await self._get_async_client()
            pipe = client.pipeline(transaction=False)

            # Check existing entries
            for mid in message_ids:
                pipe.zscore(processed_key, mid)  # noqa
            scores = await pipe.execute()

            # Filter out already processed messages
            new_ids = [mid for mid, score in zip(message_ids, scores) if score is None]

            if new_ids:
                # Add new IDs in batch
                new_mapping = {mid: now_ms for mid in new_ids}
                await client.zadd(processed_key, new_mapping, nx=True)

            return new_ids
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Async batch dedup error",
                controller=f"{__name__}.RedisStreamer._async_reserve_batch",
                message="Async batch ZADD NX failed",
                payload={
                    "error": exception_to_dict(e),
                    "key": processed_key,
                    "count": len(message_ids),
                },
            )
            return []

    def _maintenance_loop(self):
        """Background thread for periodic maintenance tasks."""
        controller = f"{__name__}.RedisStreamer._maintenance_loop"

        while True:
            try:
                # Sleep for the cleanup interval (convert ms to seconds)
                time.sleep(self._ledger_cleanup_interval / 1000)

                # Run ledger cleanup
                self.maintain_ledgers()

                # Update last cleanup time
                self._last_ledger_cleanup = self._server_now_ms()

            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Maintenance loop error",
                    controller=controller,
                    message="Error in maintenance loop",
                    payload={"error": exception_to_dict(e)},
                )
                # Sleep a bit before retrying
                time.sleep(60)

    async def _async_maintenance_loop(self):
        """Async background task for periodic maintenance."""
        controller = f"{__name__}.RedisStreamer._async_maintenance_loop"

        while True:
            try:
                # Sleep for the cleanup interval
                await asyncio.sleep(self._ledger_cleanup_interval / 1000)

                # Run async ledger cleanup
                await self.async_maintain_ledgers()

                # Update last cleanup time
                self._last_ledger_cleanup = self._server_now_ms()

            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Async maintenance loop error",
                    controller=controller,
                    message="Error in async maintenance loop",
                    payload={"error": exception_to_dict(e)},
                )
                # Sleep a bit before retrying
                await asyncio.sleep(60)

    async def _async_cleanup_channels_loop(self, cleanup_interval: float = 300.0):
        """
        Async background task for periodic channel cleanup.

        Args:
            cleanup_interval (float): How often to run cleanup in seconds (default: 300 = 5 minutes).
        """
        controller = f"{__name__}.RedisStreamer._async_cleanup_channels_loop"

        while True:
            try:
                # Sleep for the cleanup interval
                await asyncio.sleep(cleanup_interval)

                # Run async channel cleanup
                await self.async_cleanup_channels()

            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Async cleanup channels loop error",
                    controller=controller,
                    message="Error in async cleanup channels loop",
                    payload={"error": exception_to_dict(e)},
                )
                # Sleep a bit before retrying
                await asyncio.sleep(60)

    def cleanup(self):
        """Cleanup resources and flush remaining buffers."""
        try:
            # Flush all remaining buffers
            with self._buffer_lock:
                for channel, messages in self._message_buffer.items():
                    if messages:
                        self.send_messages_batch(channel, messages)
                self._message_buffer.clear()

            # Clean up Redis connections if needed
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

    async def async_cleanup(self):
        """Async cleanup resources."""
        try:
            # Cancel maintenance task
            if self._async_maintenance_task and not self._async_maintenance_task.done():
                self._async_maintenance_task.cancel()
                try:
                    await self._async_maintenance_task
                except asyncio.CancelledError:
                    pass

            # Cancel cleanup channels task
            if (
                self._async_cleanup_channels_task
                and not self._async_cleanup_channels_task.done()
            ):
                self._async_cleanup_channels_task.cancel()
                try:
                    await self._async_cleanup_channels_task
                except asyncio.CancelledError:
                    pass

            # Close async Redis connection
            if self._redis_async_client:
                await self._redis_async_client.close()

            footprint.leave(
                log_type="info",
                subject="Async cleanup completed",
                controller=f"{__name__}.RedisStreamer.async_cleanup",
                message="Async RedisStreamer cleanup completed",
            )
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Async cleanup error",
                controller=f"{__name__}.RedisStreamer.async_cleanup",
                message="Error during async cleanup",
                payload={"error": exception_to_dict(e)},
            )

    def cleanup_channels(self):
        """
        Clean up messages from specified channels based on a retention period.
        """
        controller = f"{__name__}.RedisStreamer.cleanup_channels"
        now_ms = self._server_now_ms()

        for channel, retention in self._channel_retention.items():
            if retention is None:
                continue

            try:
                group = self._group_name(channel, self.listener_name)
                processed_key = self._processed_zset_key(channel, group)

                # Calculate cutoff time for retention
                cutoff = now_ms - retention

                # Remove processed entries older than the retention period
                removed_count = self._redis_client.zremrangebyscore(
                    processed_key, min="-inf", max=f"({cutoff}"
                )

                if removed_count:
                    footprint.leave(
                        log_type="info",
                        message=f"Cleaned up {removed_count} old dedup entries from channel {channel}",
                        controller=controller,
                        subject="Channel cleanup",
                        payload={"channel": channel, "removed_count": removed_count},
                    )

            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Channel cleanup error",
                    controller=controller,
                    message=f"Error cleaning up channel {channel}",
                    payload={"error": exception_to_dict(e), "channel": channel},
                )

    async def async_cleanup_channels(self):
        """
        Async clean up messages from specified channels based on a retention period.
        """
        controller = f"{__name__}.RedisStreamer.async_cleanup_channels"
        now_ms = self._server_now_ms()

        client = await self._get_async_client()
        for channel, retention in self._channel_retention.items():
            if retention is None:
                continue

            try:
                group = self._group_name(channel, self.listener_name)
                processed_key = self._processed_zset_key(channel, group)

                # Calculate cutoff time for retention
                cutoff = now_ms - retention

                # Remove processed entries older than the retention period
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

    async def async_persist_cleanup_channels(self, cleanup_interval: float = 300.0):
        """
        Continuously clean up messages from specified channels based on a retention period.
        This method runs indefinitely and performs cleanup at the specified interval.

        Args:
            cleanup_interval (float): How often to run cleanup in seconds (default: 300 = 5 minutes).
        """
        # Start the cleanup channels task if not already started
        if (
            self._async_cleanup_channels_task is None
            or self._async_cleanup_channels_task.done()
        ):
            self._async_cleanup_channels_task = asyncio.create_task(
                self._async_cleanup_channels_loop(cleanup_interval)
            )

        # Keep the method running
        await self._async_cleanup_channels_task

    def get_stats(self) -> Dict:
        """Get current statistics about the streamer."""
        stats = {
            "listener_name": self.listener_name,
            "consumer_instance": self.consumer_instance_name,
            "subscriptions": len(self._subscriptions),
            "channels": [sub[0] for sub in self._subscriptions],
            "batch_size": self._batch_size,
            "pipeline_size": self._pipeline_size,
            "dedup_window_ms": self._dedup_window_ms,
            "buffer_stats": {},
            "last_ledger_cleanup": self._last_ledger_cleanup,
        }

        # Get buffer stats
        with self._buffer_lock:
            for channel, messages in self._message_buffer.items():
                stats["buffer_stats"][channel] = len(messages)

        return stats

    async def async_get_stats(self) -> Dict:
        """Async get current statistics about the streamer."""
        stats = self.get_stats()

        # Add async-specific stats
        if self._async_maintenance_task:
            stats["async_maintenance_running"] = not self._async_maintenance_task.done()

        return stats

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
        return False

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.async_cleanup()
        return False
