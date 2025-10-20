import json
import os
import re
import socket
import time
import uuid
import threading
from dataclasses import dataclass
from collections import defaultdict
from typing import Callable, DefaultDict, Dict, List, Optional, Tuple

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
    """

    def __init__(
        self,
        redis_instance: RedisInstance,
        consumer_name: str,
        dedup_window_ms: Optional[int] = None,
    ):
        self.listener_name: str = self._sanitize(consumer_name, maxlen=128)
        self.consumer_instance_name: str = self._gen_consumer_name()

        self._redis_instance = redis_instance
        self._redis_client = self._redis_instance.get_redis_client()

        self._subscriptions: List[Tuple[str, str, str]] = []
        self._handlers: DefaultDict[Tuple[str, str], List[Callable]] = defaultdict(list)

        # Default dedup window: 7 days
        self._dedup_window_ms: int = (
            dedup_window_ms if (dedup_window_ms and dedup_window_ms > 0)
            else 7 * 24 * 60 * 60 * 1000
        )

        # Maintenance control
        self._last_ledger_cleanup = 0
        self._ledger_cleanup_interval = 300_000  # 5 minutes (ms)

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
            return any(group["name"].decode("utf-8") == consumer_group for group in groups)
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
        self._redis_client.xadd(channel, message.get_json_encoded())

    def subscribe(self, channel_name: str, start_from_latest: bool = True):
        controller = f"{__name__}.Consumer.subscribe"
        listener_name = self.listener_name
        group = self._group_name(channel_name, listener_name)

        if not self._consumer_group_exists(channel_name, group):
            try:
                start_id = "$" if start_from_latest else "0-0"
                self._redis_client.xgroup_create(channel_name, group, start_id, mkstream=True)
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

    def register_handler(self, channel_name: str, handler_func: Callable, listener_name: Optional[str] = None):
        listener = listener_name or self.listener_name
        self._handlers[(channel_name, listener)].append(handler_func)
        return self

    def _reserve_once(self, processed_key: str, message_id: str, now_ms: int) -> bool:
        try:
            added = self._redis_client.zadd(processed_key, {message_id: now_ms}, nx=True)
            return added == 1
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Dedup error",
                controller=f"{__name__}.Consumer._reserve_once",
                message="ZADD NX failed; skipping message to avoid duplicate processing.",
                payload={"error": exception_to_dict(e), "message_id": message_id, "key": processed_key},
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
                controller=f"{__name__}.Consumer._dead_letter",
                message=f"Message failure on channel '{channel}' (reason={reason})",
                payload=payload,
            )
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Dead-letter logging error",
                controller=f"{__name__}.Consumer._dead_letter",
                message="Failed to log message failure",
                payload={"error": exception_to_dict(e), "channel": channel, "reason": reason, "message_id": message_id},
            )

    def _ack_pipeline(self, pipe, channel: str, group: str, message_id: str):
        try:
            pipe.xack(channel, group, message_id)
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Ack error",
                controller=f"{__name__}.Consumer._ack_pipeline",
                message="XACK failed.",
                payload={"error": exception_to_dict(e), "channel": channel, "group": group, "message_id": message_id},
            )

    @retry_wrapper()
    def _consume_one(self, channel: str, consumer_group: str, listener_name: str, block_time: float, count: int = 32):
        controller = f"{__name__}.Consumer._consume_one"
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
            pipe = self._redis_client.pipeline(transaction=False)

            for message_id, fields in batch:
                now_ms = self._server_now_ms()
                if not self._reserve_once(processed_key, message_id, now_ms):
                    self._ack_pipeline(pipe, channel, consumer_group, message_id)
                    continue

                try:
                    raw_name = fields.get(b"name")
                    raw_body = fields.get(b"body")
                    if raw_name is None or raw_body is None:
                        raise ValueError("Missing required fields 'name' or 'body'.")
                    name = raw_name.decode("utf-8") if isinstance(raw_name, bytes) else raw_name
                    body = json.loads(raw_body.decode("utf-8")) if isinstance(raw_body, (bytes, bytearray)) else raw_body
                except Exception as e:
                    self._dead_letter(channel, "decode/schema", message_id, {"listener": listener_name, "error": str(e)})
                    self._ack_pipeline(pipe, channel, consumer_group, message_id)
                    continue

                handler_failed = False
                for handler in self._handlers.get((channel, listener_name), []):
                    try:
                        handler(name=name, payload=body)
                    except Exception as e:
                        handler_failed = True
                        self._dead_letter(channel, "handler", message_id, {
                            "listener": listener_name,
                            "handler": handler.__name__,
                            "error": str(e),
                            "name": name,
                        })
                        self._ack_pipeline(pipe, channel, consumer_group, message_id)
                        break

                if not handler_failed:
                    self._ack_pipeline(pipe, channel, consumer_group, message_id)

            pipe.execute()

        except Exception as e:
            if "NOGROUP" in str(e):
                try:
                    self.subscribe(channel_name=channel)
                except ResponseError as inner_e:
                    if "BUSYGROUP" not in str(inner_e):
                        footprint.leave(
                            log_type="error",
                            controller=controller,
                            subject="Creating missing consumer group Error",
                            message="Error creating missing consumer group",
                            payload={
                                "error": exception_to_dict(inner_e),
                                "group": consumer_group,
                                "listener": listener_name
                            },
                        )
            else:
                footprint.leave(
                    log_type="error",
                    message=f"Error consuming messages from channel {channel}",
                    controller=controller,
                    subject="Consuming Messages Error",
                    payload={"error": exception_to_dict(e), "group": consumer_group, "listener": listener_name},
                )

    def consume_once(self, block_time: float = 5.0, count: int = 32):
        for channel, listener, group in self._subscriptions:
            self._consume_one(channel, group, listener, block_time, count)

    def persist_consume(self, rest_time: float = 0.1, block_time: float = 5.0, count: int = 32):
        controller = f"{__name__}.Consumer.persist_consume"
        for channel, listener, group in self._subscriptions:
            footprint.leave(
                log_type="info",
                message="Subscription configuration",
                controller=controller,
                subject="Persist consuming listeners",
                payload={"channel": channel, "listener": listener, "group": group},
            )

        idle_backoff = rest_time
        while True:
            before = time.time()
            self.consume_once(block_time=block_time, count=count)
            elapsed = time.time() - before

            # Adaptive sleep (less CPU load)
            if elapsed < block_time:
                idle_backoff = min(idle_backoff * 2, 2.0)
            else:
                idle_backoff = rest_time

            # Run maintenance periodically
            now_ms = self._server_now_ms()
            if now_ms - self._last_ledger_cleanup > self._ledger_cleanup_interval:
                threading.Thread(target=self.maintain_ledgers, daemon=True).start()
                self._last_ledger_cleanup = now_ms

            time.sleep(idle_backoff)

    @retry_wrapper()
    def maintain_ledgers(self):
        controller = f"{__name__}.Consumer.maintain_ledgers"
        now_ms = self._server_now_ms()
        cutoff = now_ms - self._dedup_window_ms

        for channel_name, _, consumer_group in self._subscriptions:
            key = self._processed_zset_key(channel_name, consumer_group)
            try:
                removed = self._redis_client.zremrangebyscore(key, min="-inf", max=f"({cutoff}")
                if removed:
                    footprint.leave(
                        log_type="info",
                        message=f"Purged {removed} dedup entries older than {self._dedup_window_ms}ms",
                        controller=controller,
                        subject="Dedup ledger maintenance",
                        payload={"key": key, "cutoff_ms": cutoff, "removed": removed},
                    )
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    message="Error purging dedup ledger",
                    controller=controller,
                    subject="Dedup maintenance error",
                    payload={"key": key, "error": exception_to_dict(e)},
                )
