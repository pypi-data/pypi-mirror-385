# Kafka Sub-Package

**DealerTower Python Framework** — High-level Kafka messaging utilities for standardized event production and consumption across microservices.

## Overview

The `kafka` sub-package provides a robust set of tools to simplify interactions with Apache Kafka. It is designed to reduce boilerplate code, enforce consistent patterns, and provide clear configuration and error handling.

The package includes:

- **`KafkaConfig`**: A fluent builder for creating complex Kafka connection configurations.
- **`KafkaInstance`**: A factory class that uses `KafkaConfig` to create and manage producer and consumer clients.
- **`Producer`**: A high-level wrapper for sending JSON-serialized messages with built-in error handling and logging.
- **`Consumer`**: A high-level wrapper for consuming messages, with support for topic-specific handlers and manual offset control.

## Installation

To use the Kafka utilities, install `dtpyfw` with the `kafka` extra, which pulls in the required `kafka-python` dependency.

```bash
pip install dtpyfw[kafka]
```

---

## `config.py` — `KafkaConfig`

The `KafkaConfig` class provides a fluent (chainable) interface to build a Kafka client configuration. You can either provide a full Kafka connection URL or set individual parameters.

### Initialization and Chaining

```python
from dtpyfw.kafka.config import KafkaConfig

# Using a full connection URL (recommended for simplicity)
config_from_url = KafkaConfig().set_kafka_url("kafka://user:pass@host:9092")

# Using individual parameters
config_from_params = (
    KafkaConfig()
    .set_bootstrap_servers(["kafka1:9092", "kafka2:9092"])
    .set_security_protocol("SASL_SSL")
    .set_sasl_mechanism("PLAIN")
    .set_sasl_plain_username("myuser")
    .set_sasl_plain_password("mypass")
    .set_group_id("my-consumer-group")
    .set_auto_offset_reset("earliest")
    .set_enable_auto_commit(False)
)
```

### KafkaConfig Methods

| Method                                      | Description                                                              |
| ------------------------------------------- | ------------------------------------------------------------------------ |
| `set_kafka_url(url: str)`                   | Sets the full Kafka URL. This takes precedence over individual settings. |
| `set_bootstrap_servers(servers: list[str])` | Sets a list of Kafka broker host:port pairs.                             |
| `set_security_protocol(proto: str)`         | Sets the security protocol (e.g., `SASL_SSL`, `PLAINTEXT`).                |
| `set_sasl_mechanism(mech: str)`             | Sets the SASL mechanism (e.g., `PLAIN`, `SCRAM-SHA-256`).                  |
| `set_sasl_plain_username(user: str)`        | Sets the username for SASL PLAIN authentication.                         |
| `set_sasl_plain_password(pwd: str)`         | Sets the password for SASL PLAIN authentication.                         |
| `set_client_id(client_id: str)`             | Sets a logical identifier for the client.                                |
| `set_group_id(group_id: str)`               | Sets the consumer group ID.                                              |
| `set_auto_offset_reset(offset: str)`        | Sets the starting offset (`earliest` or `latest`).                       |
| `set_enable_auto_commit(flag: bool)`        | Enables (`True`) or disables (`False`) automatic offset commits.         |
| `get(key: str, default=None)`               | Retrieves a raw configuration value.                                     |

---

## `connection.py` — `KafkaInstance`

This class acts as a factory for creating `KafkaProducer` and `KafkaConsumer` instances based on a `KafkaConfig`. It automatically handles JSON serialization for producers.

### Initialization

```python
from dtpyfw.kafka.connection import KafkaInstance

# config is a KafkaConfig instance from the previous step
kafka_instance = KafkaInstance(config)
```

### Context Managers

The recommended way to use `KafkaInstance` is with its context managers, which handle resource cleanup automatically.

```python
# Producing messages
with kafka_instance.producer_context() as producer:
    producer.send("my-topic", {"event": "user_created", "user_id": 123})

# Consuming messages
topics = ["my-topic", "another-topic"]
with kafka_instance.consumer_context(topics) as consumer:
    for message in consumer:
        print(f"Received: {message.value}")
```

### Direct Client Creation

You can also get raw `kafka-python` clients if you need more control.

- `get_producer(**kwargs) -> KafkaProducer`: Returns a producer that serializes message values to JSON.
- `get_consumer(topics: list[str], **kwargs) -> KafkaConsumer`: Returns a consumer subscribed to the specified topics.

---

## `producer.py` — `Producer`

A high-level wrapper that simplifies sending messages.

### Initialization and Usage

```python
from dtpyfw.kafka.producer import Producer

# kafka_instance is from the previous step
producer = Producer(kafka_instance)

# Send a message and wait for acknowledgment
producer.send(
    topic="user-events",
    value={"action": "login", "username": "test"},
    key="user-123",  # Can be str or bytes
    timeout=10
)
```

### `send(topic, value, key, timeout)`

Sends a single message.

- **`topic` (str)**: The destination topic.
- **`value` (Any)**: The message payload, which will be JSON-encoded.
- **`key` (str | bytes | None)**: The message key. String keys are automatically encoded to UTF-8.
- **`timeout` (int)**: How long to wait for acknowledgment from Kafka before raising an exception.

The method also logs the outcome of the send operation using the framework's `footprint` logger.

---

## `consumer.py` — `Consumer`

A high-level wrapper for consuming messages that supports registering multiple handler functions per topic.

### Initialization and Handlers

```python
from dtpyfw.kafka.consumer import Consumer

def handle_user_events(topic, partition, offset, key, value):
    print(f"User Event on topic {topic}: {value}")

def log_raw_events(topic, partition, offset, key, value):
    print(f"Logging raw event from {topic} at offset {offset}")

consumer = Consumer(
    kafka_instance,
    topics=["user-events", "system-logs"],
    enable_auto_commit=False  # Example: disabling auto-commit
)

# Register handlers
consumer.register_handler("user-events", handle_user_events)
consumer.register_handler("user-events", log_raw_events) # Multiple handlers are allowed
consumer.register_handler("system-logs", log_raw_events)

# Poll for new messages
consumer.consume(timeout_ms=1000)

# If auto-commit is off, commit offsets manually
consumer.commit()
```

### Methods

- `register_handler(topic: str, handler: Callable)`: Attaches a function to be called for each message received on the specified topic. The handler receives `topic`, `partition`, `offset`, `key`, and `value` as keyword arguments.
- `consume(timeout_ms: int)`: Polls Kafka for new messages. For each message, it invokes all registered handlers for that topic. If a handler raises an exception, it is logged without stopping the consumer.
- `commit()`: Manually commits the current consumer offsets. This is only necessary if `enable_auto_commit` was set to `False`.

---

*This documentation covers the `kafka` sub-package of the DealerTower Python Framework. Ensure the `kafka` extra is installed to use these features.*

