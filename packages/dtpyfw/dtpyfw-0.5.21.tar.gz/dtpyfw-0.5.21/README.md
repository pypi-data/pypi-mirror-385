# DealerTower Python Framework (dtpyfw)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checked](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

**DealerTower Python Framework** provides reusable building blocks for microservices. It is organized into modular sub-packages focused on different domains: Core, API, Database, Bucket, FTP, Redis, Kafka, Worker, Log, and Encryption.

This library follows Python packaging standards including PEP 561 for type checking support.

---

## 🚀 Installation

Requires **Python 3.11** or newer.

### Base package & Core

```bash
pip install dtpyfw
```

Using Poetry (development):

```bash
poetry install -E all
```

### Package Metadata

Query the installed version programmatically:

```python
import dtpyfw
print(dtpyfw.__version__)
```

### Optional Extras

Install just the features you need; extras can be combined, for example `pip install dtpyfw[api,db]`.

| Sub-Package | Description | Install Command | Docs |
| ----------- | ----------- | --------------- | ---- |
| **core**    | Env, errors, async bridge, utils | included in base | [Core Docs](docs/core.md) |
| **log**     | Structured logging helpers | included in base | [Log Docs](docs/log.md) |
| **api**     | FastAPI middleware & routing helpers | `pip install dtpyfw[api]` | [API Docs](docs/api.md) |
| **db**      | SQLAlchemy sync/async & search tools | `pip install dtpyfw[db]` | [DB Docs](docs/db.md) |
| **bucket**  | S3-compatible file management | `pip install dtpyfw[bucket]` | [Bucket Docs](docs/bucket.md) |
| **ftp**     | FTP and SFTP convenience wrappers | `pip install dtpyfw[ftp]` | [FTP Docs](docs/ftp.md) |
| **redis**   | Redis clients & caching utilities | `pip install dtpyfw[redis]` | [Redis Docs](docs/redis.md) |
| **redis_streamer** | Redis Streams consumer/producer | `pip install dtpyfw[redis_streamer]` | [Redis Streamer Docs](docs/redis_streamer.md) |
| **kafka**   | Kafka messaging utilities | `pip install dtpyfw[kafka]` | [Kafka Docs](docs/kafka.md) |
| **worker**  | Celery task & scheduler setup | `pip install dtpyfw[worker]` | [Worker Docs](docs/worker.md) |
| **encrypt** | Password hashing & JWT utilities | `pip install dtpyfw[encrypt]` | [Encryption Docs](docs/encrypt.md) |
| **all**       | Everything above | `pip install dtpyfw[all]` | — |

---

## 📦 Sub-Package Summaries

### Core

Essential utilities for environment management, error handling, async bridging and general helpers. [Core Docs](docs/core.md)

### Log

Structured logging configuration and helpers. [Log Docs](docs/log.md)

### API

FastAPI application factory, middleware and routing helpers. [API Docs](docs/api.md)

### Database

Sync and async SQLAlchemy orchestration with search helpers. [DB Docs](docs/db.md)

### Bucket

S3-compatible storage convenience functions. [Bucket Docs](docs/bucket.md)

### FTP/SFTP

Unified clients for FTP and SFTP operations. [FTP Docs](docs/ftp.md)

### Redis

Redis caching utilities and connection management. [Redis Docs](docs/redis.md)

### Redis Streamer

High-level producer and consumer for Redis Streams. [Redis Streamer Docs](docs/redis_streamer.md)

### Kafka

Producer and consumer wrappers for Kafka messaging. [Kafka Docs](docs/kafka.md)

### Worker

Helpers for configuring Celery workers and schedules. [Worker Docs](docs/worker.md)

### Encryption

Password hashing and JWT helpers. [Encryption Docs](docs/encrypt.md)

---

## 🤝 Contributing

We welcome contributions from authorized DealerTower employees and contractors! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Development setup
- Coding standards and style guide
- Testing requirements
- Pull request process
- Type annotations and docstring conventions

---

## 📝 Changelog

A list of changes in each release is maintained in the git commit history.

---

## 📄 License

DealerTower Python Framework is proprietary. See [LICENSE](LICENSE) for terms.

## Development

- Install dependencies: `poetry install -E all`
- Run tests: `pytest` (from repo root)
- Format and lint: `black . && isort . && ruff check . --fix`
- Type-check: `mypy dtpyfw`
