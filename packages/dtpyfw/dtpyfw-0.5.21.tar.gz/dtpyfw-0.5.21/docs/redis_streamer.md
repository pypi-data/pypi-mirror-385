# Redis Streamer Sub-Package

**DealerTower Python Framework** — High-level abstractions for Redis Streams, providing robust producer and consumer implementations for building reliable, scalable messaging systems.

## Overview

The `redis_streamer` sub-package is designed to simplify working with Redis Streams. It offers:

- **Connection Management**: Leverages the `RedisInstance` from the `redis` sub-package for efficient connection pooling.
- **Message Abstraction**: A simple `Message` class to standardize message payloads.
- **Synchronous Streamer (`RedisStreamer`)**: A thread-safe, synchronous client for producing and consuming messages from Redis Streams.
- **Asynchronous Streamer (`AsyncRedisStreamer`)**: A high-performance, asynchronous client for modern `asyncio`-based applications.
- **Producer and Consumer Logic**: Both streamers encapsulate logic for sending messages, creating consumer groups, reading from streams, and acknowledging messages.

This sub-package is ideal for applications that require a lightweight, fast, and reliable message bus.

## Installation

To use the Redis Streamer utilities, install `dtpyfw` with the `redis_streamer` extra. This will also install the `redis` dependency.

```bash
pip install dtpyfw[redis_streamer]
```

---

## `message.py` — Message Structure

The `Message` class defines a standard structure for all messages sent through the streamer.

```python
from dtpyfw.redis_streamer.message import Message

# Create a message
message = Message(
    name="user.created",
    body={"user_id": 123, "email": "test@example.com"}
)
```

- `name`: A string identifier for the message type, used for routing or handling.
- `body`: A dictionary containing the message payload.

---

## `sync.py` — Synchronous Streamer

The `RedisStreamer` class provides a synchronous interface for interacting with Redis Streams.

### Initialization

```python
from dtpyfw.redis_streamer.sync import RedisStreamer
from dtpyfw.redis.connection import RedisInstance

# Assuming 'redis_instance' is an initialized RedisInstance
streamer = RedisStreamer(
    redis_instance=redis_instance,
    consumer_name="worker-1"
)
```

- `redis_instance`: The `RedisInstance` for connecting to Redis.
- `consumer_name`: A unique name for the consumer within its group.

### Producing Messages

```python
# Send a single message
streamer.send_message("orders_stream", message)

# Send a batch of messages for better performance
messages = [message1, message2, message3]
streamer.send_messages_batch("orders_stream", messages)
```

### Consuming Messages

The `persist_consume` method runs a loop to continuously fetch and process messages.

```python
# Define a handler function for a specific stream
def handle_order(message: Message):
    print(f"Processing order: {message.body}")

# Register the handler
streamer.register_handler("orders_stream", handle_order)

# Subscribe to the stream (this creates the consumer group if it doesn't exist)
streamer.subscribe("orders_stream")

# Start consuming
streamer.persist_consume(
    rest_time=0.1,   # Time to sleep between polls
    block_time=5.0,  # How long to block waiting for new messages
    count=50         # Max messages to fetch per poll
)
```

---

## `async.py` — Asynchronous Streamer

The `AsyncRedisStreamer` class provides an asynchronous interface, making it a perfect fit for `asyncio`-based applications like FastAPI services.

### Initialization

```python
from dtpyfw.redis_streamer.async import AsyncRedisStreamer

async_streamer = AsyncRedisStreamer(
    redis_instance=redis_instance,
    consumer_name="async-worker-1"
)
```

### Producing Messages (Async)

```python
# Send a single message
await async_streamer.send_message("events_stream", message)

# Send a batch of messages
await async_streamer.send_messages_batch("events_stream", messages)
```

### Consuming Messages (Async)

The async consumption pattern is similar to the synchronous one but uses `async` and `await`.

```python
# Define an async handler
async def handle_event(message: Message):
    await process_event_in_db(message.body)

# Register the handler
async_streamer.register_handler("events_stream", handle_event)

# Subscribe to the stream
await async_streamer.subscribe("events_stream")

# Start the async consumer loop
await async_streamer.persist_consume(
    rest_time=0.1,
    block_time=5.0,
    count=50
)
```

---

## Context Manager Support

Both `RedisStreamer` and `AsyncRedisStreamer` can be used as context managers to ensure that resources are properly cleaned up.

**Synchronous:**

```python
with RedisStreamer(redis_instance, "worker-1") as streamer:
    streamer.subscribe("orders_stream")
    # ... setup handlers and consume
```

**Asynchronous:**

```python
async with AsyncRedisStreamer(redis_instance, "async-worker-1") as streamer:
    await streamer.subscribe("events_stream")
    # ... setup handlers and consume
```

---

*This documentation covers the `redis_streamer` sub-package. Ensure the `redis_streamer` extra is installed to use these features.*
