from typing import Any

__all__ = ("RedisConfig",)


class RedisConfig:
    def __init__(self):
        self._config_data = {}

    def set_redis_url(self, redis_url: str):
        self._config_data["redis_url"] = redis_url
        return self

    def set_redis_host(self, host: str):
        self._config_data["redis_host"] = host
        return self

    def set_redis_port(self, port: int):
        self._config_data["redis_port"] = port
        return self

    def set_redis_db(self, database: str):
        self._config_data["redis_db"] = database
        return self

    def set_redis_password(self, password: str):
        self._config_data["redis_password"] = password
        return self

    def set_redis_username(self, username: str):
        self._config_data["redis_username"] = username
        return self

    def set_redis_ssl(self, ssl: bool):
        self._config_data["redis_ssl"] = ssl
        return self

    def set_redis_max_connections(self, redis_max_connections: int):
        self._config_data["redis_max_connections"] = redis_max_connections
        return self

    def set_redis_socket_timeout(self, redis_socket_timeout: int):
        self._config_data["redis_socket_timeout"] = redis_socket_timeout
        return self

    def get(self, key: str, default: Any = None):
        return self._config_data.get(key, default)
