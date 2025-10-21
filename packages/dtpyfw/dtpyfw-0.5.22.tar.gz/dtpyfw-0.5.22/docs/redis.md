# Redis Sub-Package

**DealerTower Python Framework** — Unified Redis utilities to standardize caching and connection management across microservices.

## Overview

The `redis` sub-package provides:

- **Connection Management**: A fluent `RedisConfig` class and a `RedisInstance` for creating synchronous and asynchronous Redis clients from a single source of truth.
- **Caching Utilities**: A powerful `cache_wrapper` decorator to transparently cache function results with fine-grained control over namespaces, expiration, and conditional caching.
- **Health Checks**: A simple `is_redis_connected` function to verify Redis availability.

This sub-package centralizes Redis interactions, reduces boilerplate code, and ensures consistent, high-performance caching patterns.

## Installation

To use the Redis utilities, install `dtpyfw` with the `redis` extra:

```bash
pip install dtpyfw[redis]
```

---

## `config.py` — Redis Configuration

The `RedisConfig` class provides a fluent interface for setting up Redis connection parameters.

```python
from dtpyfw.redis.config import RedisConfig

config = (
    RedisConfig()
    .set_redis_host("localhost")
    .set_redis_port(6379)
    .set_redis_db("0")
    .set_redis_password("your-secret-password")
    .set_redis_ssl(False)
    .set_redis_max_connections(20)
    .set_redis_socket_timeout(10)
)
```

Alternatively, you can provide a full Redis URL:

```python
config = RedisConfig().set_redis_url("rediss://:password@hostname:port/0")
```

| Method                        | Description                                      |
| ----------------------------- | ------------------------------------------------ |
| `set_redis_url`               | Sets the full Redis connection URL.              |
| `set_redis_host`              | Sets the Redis host.                             |
| `set_redis_port`              | Sets the Redis port.                             |
| `set_redis_db`                | Sets the Redis database index.                   |
| `set_redis_username`          | Sets the Redis username (for ACLs).              |
| `set_redis_password`          | Sets the Redis password.                         |
| `set_redis_ssl`               | Enables or disables SSL/TLS.                     |
| `set_redis_max_connections`   | Configures the connection pool's max size.       |
| `set_redis_socket_timeout`    | Sets the socket timeout for Redis operations.    |

---

## `connection.py` — Connection Management

The `RedisInstance` class is the central hub for creating Redis clients. It uses a `RedisConfig` object to manage connection pools for both synchronous and asynchronous clients.

```python
from dtpyfw.redis.connection import RedisInstance

# Assuming 'config' is a configured RedisConfig object
redis_instance = RedisInstance(config)
```

### Getting a Client

`RedisInstance` provides context managers that handle connection acquisition and release, which is the recommended way to interact with Redis.

**Synchronous Client:**

```python
with redis_instance.get_redis() as client:
    client.set("my-key", "my-value")
    value = client.get("my-key")
```

**Asynchronous Client:**

```python
async with redis_instance.get_async_redis() as async_client:
    await async_client.set("my-key", "my-async-value")
    value = await async_client.get("my-key")
```

You can also get a direct client instance, but be mindful of managing its lifecycle.

- `get_redis_client()`: Returns a synchronous `redis.Redis` client.
- `get_async_redis_client()`: Returns an asynchronous `redis.asyncio.Redis` client.

---

## `caching.py` — Caching Utilities

The `caching` module provides a flexible and powerful decorator for caching the results of functions.

### `cache_wrapper` Decorator

The `cache_wrapper` is the easiest way to add caching to both synchronous and asynchronous functions.

```python
from dtpyfw.redis.caching import cache_wrapper

@cache_wrapper(
    redis=redis_instance,
    namespace="user_data",
    expire=3600,  # Cache for 1 hour
)
def get_user_profile(user_id: int):
    # This function will only be executed if the result is not in the cache.
    return {"id": user_id, "name": "John Doe"}

@cache_wrapper(
    redis=redis_instance,
    namespace="product_info",
    expire=600,
)
async def fetch_product_details(product_id: str):
    # This async function's result will also be cached.
    return await get_product_from_db(product_id)
```

### Advanced Caching Control

The decorator offers several parameters for fine-grained control:

- `redis`: The `RedisInstance` to use for caching.
- `namespace`: A string to prefix all cache keys, preventing collisions.
- `expire`: The cache expiration time in seconds.
- `skip_cache_keys`: A `set` of keyword argument names to exclude from the cache key. This is useful for arguments that don't affect the result, like a database session.
- `cache_only_for`: A list of conditions to decide whether to cache a result. For example, you might only want to cache results for paying users.

**Example with `skip_cache_keys` and `cache_only_for`:**

```python
@cache_wrapper(
    redis=redis_instance,
    namespace="reports",
    expire=86400,  # Cache for 24 hours
    skip_cache_keys={"db_session"},
    cache_only_for=[
        {"kwarg": "report_type", "operator": "in", "value": ["daily", "weekly"]}
    ],
)
def generate_report(report_type: str, user_id: int, db_session):
    # The 'db_session' object will not be part of the cache key.
    # Caching will only occur if 'report_type' is 'daily' or 'weekly'.
    return f"Report for {user_id} of type {report_type}"
```

### `cache_data` Function

For manual caching outside of a function call, you can use `cache_data`.

```python
from dtpyfw.redis.caching import cache_data

with redis_instance.get_redis() as client:
    response_data = {"data": "some important info"}
    cache_key = "manual_cache_key"
    cache_data(response_data, cache_key, client, expire=300)
```

---

## `health.py` — Health Checks

To verify that the Redis server is reachable and responsive, use the `is_redis_connected` function.

```python
from dtpyfw.redis.health import is_redis_connected

is_healthy, error = is_redis_connected(redis_instance)

if is_healthy:
    print("Redis connection is OK.")
else:
    print(f"Redis connection failed: {error}")
```

This function performs a `PING` command and returns a tuple of `(bool, Exception | None)`.

---

*This documentation covers the `redis` sub-package of the DealerTower Python Framework. Ensure the `redis` extra is installed to use these features.*
