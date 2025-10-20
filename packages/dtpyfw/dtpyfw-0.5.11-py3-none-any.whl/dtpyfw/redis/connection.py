import urllib.parse
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

import redis
from redis.asyncio import Redis as AsyncRedis
from redis.asyncio.connection import ConnectionPool as AsyncConnectionPool
from redis.connection import ConnectionPool

from .config import RedisConfig

__all__ = ("RedisInstance",)


class RedisInstance:

    def __init__(self, redis_config: RedisConfig):
        self.config = redis_config
        self.redis_url = self._set_redis_url()
        self._sync_pool = None
        self._async_pool = None

    def _set_redis_url(self) -> str:
        """Constructs the Redis connection URL."""
        redis_url = self.config.get("redis_url")
        if redis_url:
            return redis_url

        redis_ssl = self.config.get("redis_ssl", False)
        redis_host = self.config.get("redis_host")
        redis_port = self.config.get("redis_port")
        redis_db = self.config.get("redis_db")
        redis_username = self.config.get("redis_username", "")
        redis_password = self.config.get("redis_password", "")

        username = urllib.parse.quote(redis_username) if redis_username else ""
        password = urllib.parse.quote(redis_password) if redis_password else ""

        auth_part = (
            f"{username}:{password}@"
            if username and password
            else f"{password}@" if password else f"{username}@" if username else ""
        )
        protocol = "rediss" if redis_ssl else "redis"

        return f"{protocol}://{auth_part}{redis_host}:{redis_port}/{redis_db}"

    def _get_sync_pool(self) -> ConnectionPool:
        if not self._sync_pool:
            self._sync_pool = ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.config.get("redis_max_connections", 10),
                socket_timeout=self.config.get("redis_socket_timeout", 5),
            )
        return self._sync_pool

    def _get_async_pool(self) -> AsyncConnectionPool:
        if not self._async_pool:
            self._async_pool = AsyncConnectionPool.from_url(
                self.redis_url,
                max_connections=self.config.get("redis_max_connections", 10),
                socket_timeout=self.config.get("redis_socket_timeout", 5),
            )
        return self._async_pool

    def get_redis_client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self._get_sync_pool())

    async def get_async_redis_client(self) -> AsyncRedis:
        return AsyncRedis(connection_pool=self._get_async_pool())

    @contextmanager
    def get_redis(self) -> Generator[redis.Redis, None, None]:
        """Context manager for synchronous Redis client."""
        client = self.get_redis_client()
        try:
            yield client
        finally:
            pass

    @asynccontextmanager
    async def get_async_redis(self) -> AsyncGenerator[AsyncRedis, None]:
        client = await self.get_async_redis_client()
        try:
            yield client
        finally:
            pass
