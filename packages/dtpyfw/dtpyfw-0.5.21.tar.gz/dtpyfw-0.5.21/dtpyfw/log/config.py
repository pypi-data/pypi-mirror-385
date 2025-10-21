"""Logging configuration management."""

from typing import Any

__all__ = ("LogConfig",)


class LogConfig:
    def __init__(self):
        self._config_data: dict[str, Any] = {}

    def set_api_url(self, api_url: str):
        self._config_data["api_url"] = api_url
        return self

    def set_api_key(self, api_key: str):
        self._config_data["api_key"] = api_key
        return self

    def set_log_print(self, log_print: str):
        self._config_data["log_print"] = log_print
        return self

    def set_log_store(self, log_store: str):
        self._config_data["log_store"] = log_store
        return self

    def set_log_level(self, log_level: str):
        self._config_data["log_level"] = log_level.upper()
        return self

    def set_log_file_name(self, log_file_name: str):
        self._config_data["log_file_name"] = log_file_name
        return self

    def set_log_file_backup_count(self, log_file_backup_count: int):
        self._config_data["log_file_backup_count"] = int(log_file_backup_count)
        return self

    def set_log_file_max_size(self, log_file_max_size: int):
        self._config_data["log_file_max_size"] = int(log_file_max_size)
        return self

    def set_only_footprint_mode(self, only_footprint_mode: bool):
        self._config_data["only_footprint_mode"] = bool(only_footprint_mode)
        return self

    def set_celery_mode(self, celery_mode: bool):
        self._config_data["celery_mode"] = bool(celery_mode)
        return self

    def get(self, key: str, default: Any = None):
        return self._config_data.get(key, default)
