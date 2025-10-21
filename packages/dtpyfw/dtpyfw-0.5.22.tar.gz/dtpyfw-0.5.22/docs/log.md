# Log Sub-Package

**DealerTower Python Framework** — Structured, centralized logging utilities with support for console, file, and remote API handlers, plus Celery integration.

## Overview

The `log` sub-package provides a comprehensive and configurable logging system designed for microservices. It ensures that logs are structured, consistent, and can be directed to multiple destinations simultaneously.

Key components include:

- **`LogConfig`**: A fluent builder for defining all logging parameters, from log levels to remote API endpoints.
- **`log_initializer`**: A one-call function to configure the root logger based on a `LogConfig` instance.
- **`celery_logger_handler`**: A helper to attach the same configured handlers to Celery-specific loggers.
- **`footprint.leave`**: A simple function for emitting structured, high-value log entries.
- **Handlers**: Pre-configured handlers for logging to a remote API (`LoggerHandler`), the console, and rotating files.
- **`CustomFormatter`**: Ensures all log records share a consistent, timestamped format.

## Installation

The logging module is part of the `core` package and does not require a separate extra. However, the API handler requires `requests`.

```bash
pip install dtpyfw
pip install requests # If using the API handler
```

---

## `config.py` — `LogConfig`

The `LogConfig` class uses a fluent (chainable) builder pattern to make configuration readable and straightforward.

### Initialization and Chaining

```python
from dtpyfw.log import LogConfig

log_config = (
    LogConfig()
    .set_log_level("INFO")
    .set_log_print(True)
    .set_log_store(True)
    .set_log_file_name("my_app.log")
    .set_log_file_max_size(10_000_000)  # 10 MB
    .set_log_file_backup_count(5)
    .set_api_url("https://my-log-api.com/ingest")
    .set_api_key("SECRET_API_KEY")
    .set_only_footprint_mode(True)
    .set_celery_mode(True)
)
```

### Methods

| Method                          | Description                                                              |
| ------------------------------- | ------------------------------------------------------------------------ |
| `set_log_level(level: str)`     | Sets the minimum log level (e.g., `DEBUG`, `INFO`, `WARNING`).           |
| `set_log_print(print: bool)`    | If `True`, enables logging to the console (stdout).                      |
| `set_log_store(store: bool)`    | If `True`, enables logging to a rotating file.                           |
| `set_log_file_name(name: str)`  | Sets the path for the log file.                                          |
| `set_log_file_max_size(size: int)` | Sets the maximum size in bytes before the log file is rotated.           |
| `set_log_file_backup_count(count: int)` | Sets the number of old log files to keep.                                |
| `set_api_url(url: str)`         | Sets the URL for the remote logging API endpoint.                        |
| `set_api_key(key: str)`         | Sets the authorization key for the logging API.                          |
| `set_only_footprint_mode(mode: bool)` | If `True`, only logs created via `footprint.leave` are sent to the API.  |
| `set_celery_mode(mode: bool)`   | If `True`, automatically configures Celery's logger with the same handlers. |

---

## `initializer.py` — `log_initializer`

This function takes a `LogConfig` object and sets up all the configured handlers on the root logger. Call this once at application startup.

```python
import logging
from dtpyfw.log import log_initializer, LogConfig

# Create config (as shown above)
log_config = LogConfig().set_log_level("INFO").set_log_print(True)

# Initialize logging system
log_initializer(log_config)

# Now, any standard logging call will use the configured handlers
logging.info("This is a standard log message.")
```

### `celery_logger_handler`

If you are using Celery and need to configure its loggers after the initial setup, this helper function applies the same handlers.

```python
from celery.signals import after_setup_logger
from dtpyfw.log import celery_logger_handler

@after_setup_logger.connect
def setup_celery_logging(logger, **kwargs):
    celery_logger_handler(config=log_config, logger=logger, propagate=False)
```

---

## `footprint.py` — `footprint.leave`

This is the preferred way to generate structured logs. It wraps the standard `logging` library to create log records with a `details` dictionary, making them easy to parse and query in log management systems.

### Usage

```python
from dtpyfw.log import footprint

footprint.leave(
    log_type="warning",
    subject="Payment Processing",
    controller="billing_service",
    message="Credit card was declined.",
    payload={"order_id": "ORD-12345", "reason": "insufficient_funds"},
)
```

- **`log_type`**: Determines the log level (`error`, `warning`, `info`, `debug`).
- **`message`**: A human-readable summary of the event.
- **`**kwargs`**: Any other keyword arguments (`subject`, `controller`, `payload`, etc.) are collected into the structured `details` field of the log.

---

## Handlers and Formatters

### `api_handler.py` — `LoggerHandler`

This handler sends log records to a remote HTTP endpoint. It includes a retry mechanism with backoff for transient network failures. If `only_footprint_mode` is enabled in `LogConfig`, it will only send logs that were created using `footprint.leave`.

### `handlers.py` — `get_handlers_data`

This internal function assembles the list of required handlers (API, console, file) based on the `LogConfig`.

### `formatter.py` — `CustomFormatter`

This formatter ensures a consistent output format for all handlers.

- For standard logs: `TIMESTAMP - LEVEL - MESSAGE`
- For footprint logs: `TIMESTAMP - LEVEL - {details_dictionary}`

---

*This documentation covers the `log` sub-package of the DealerTower Python Framework.*
