import os
import re
import time
import socket
import uuid
from collections import defaultdict
from typing import Dict, DefaultDict, Tuple, List, Callable, Optional

from redis.exceptions import ConnectionError, TimeoutError

from dtpyfw.core.exception import exception_to_dict
from dtpyfw.log import footprint
from dtpyfw.redis.connection import RedisInstance

DEFAULT_EXCEPTIONS = (ConnectionError, TimeoutError, Exception)
REDIS_EXCEPTIONS = (ConnectionError, TimeoutError)


class CommonMethods:

    def __init__(
        self,
        redis_instance: RedisInstance,
        consumer_name: str,
        dedup_window_ms: int = 7 * 24 * 60 * 60 * 1000,
    ):
        self.listener_name: str = self._sanitize(consumer_name, maxlen=128)
        self.consumer_instance_name: str = self._gen_consumer_name()

        self._redis_instance = redis_instance

        self._subscriptions: List[Tuple[str, str, str]] = []
        self._handlers: DefaultDict[Tuple[str, str], List[Callable]] = defaultdict(list)

        # Default dedup window: 1 day
        self._dedup_window_ms: int = dedup_window_ms

        # Maintenance control
        self._last_ledger_cleanup = 0
        self._ledger_cleanup_interval = 300_000  # 5 minutes (ms)
        self._channel_retention: Dict[str, Optional[int]] = {}

    def _gen_consumer_name(self) -> str:
        return self._consumer_name_generator(self.listener_name)

    @staticmethod
    def _sanitize(s: str, maxlen: int) -> str:
        s = re.sub(r"[^a-zA-Z0-9._:-]+", "-", s or "")
        return s[:maxlen]

    @staticmethod
    def _server_now_ms() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def _group_name(channel: str, listener_name: str) -> str:
        return f"{channel}:{listener_name}:cg"

    @staticmethod
    def _processed_zset_key(channel: str, group: str) -> str:
        return f"stream:{channel}:group:{group}:processed"

    @classmethod
    def _consumer_name_generator(cls, listener_name: str) -> str:
        host = os.getenv("POD_NAME") or os.getenv("HOSTNAME") or socket.gethostname()
        pid = os.getpid()
        rnd = uuid.uuid4().hex[:8]
        name = ".".join([listener_name, cls._sanitize(host, maxlen=64), str(pid), rnd])
        return cls._sanitize(name, maxlen=200)

    @staticmethod
    def _dead_letter(channel: str, reason: str, message_id: str, extra: Dict):
        try:
            payload = {
                "reason": reason,
                "channel": channel,
                "message_id": message_id
            }
            if extra:
                payload.update(extra)
            footprint.leave(
                log_type="error",
                subject="Message failed",
                controller=f"{__name__}.AsyncRedisStreamer._dead_letter",
                message=f"Message failure on channel '{channel}' (reason={reason})",
                payload=payload,
            )
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Dead-letter logging error",
                controller=f"{__name__}.AsyncRedisStreamer._dead_letter",
                message="Failed to log message failure",
                payload={
                    "error": exception_to_dict(e),
                    "channel": channel,
                    "reason": reason,
                    "message_id": message_id,
                },
            )

    def register_channel(
        self,
        channel_name: str,
        retention_ms: int = 24 * 60 * 60 * 1000,
    ):
        """Register channel metadata with optional retention configuration."""
        controller = f"{__name__}.AsyncRedisStreamer.register_channel"

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

    def register_handler(
        self,
        channel_name: str,
        handler_func: Callable,
        listener_name: Optional[str] = None,
    ):
        """Register a handler function for a specific channel."""
        listener = listener_name or self.listener_name
        self._handlers[(channel_name, listener)].append(handler_func)
        footprint.leave(
            log_type="info",
            subject="Handler registered",
            controller=f"{__name__}.AsyncRedisStreamer.register_handler",
            message=f"Handler '{handler_func.__name__}' registered for channel '{channel_name}'.",
            payload={
                "channel_name": channel_name,
                "handler_name": handler_func.__name__,
                "listener_name": listener,
            },
        )
        return self
