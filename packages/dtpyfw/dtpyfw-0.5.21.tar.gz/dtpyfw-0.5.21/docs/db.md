# Database (DB) Sub-Package

**DealerTower Python Framework** — Centralized SQLAlchemy configuration, connection management, ORM utilities, health checks, and search helpers to streamline database interactions across microservices.

## Overview

The `db` sub-package encapsulates common patterns for working with relational databases using SQLAlchemy. It provides:

- **Configuration**: A fluent `DatabaseConfig` class for setting up connection parameters.
- **Connection Management**: The `DatabaseInstance` class for handling synchronous and asynchronous engines and sessions, for both read and write replicas.
- **ORM Model Base**: A `ModelBase` class that includes a UUID primary key, automatic timestamping, and helper methods for CRUD operations.
- **Health Checks**: Utilities to verify database connectivity.
- **Advanced Search**: A powerful `get_list` function for building complex, filterable, and searchable queries.
- **Bulk Operations**: `upsert_data` and `upsert_data_async` for efficient bulk inserts and updates.

This sub-package standardizes database interactions, reduces boilerplate code, and provides a robust foundation for data access layers in microservices.

## Installation

To use the database utilities, install `dtpyfw` with the `db` extra:

```bash
pip install dtpyfw[db]
```

---

## `config.py` — Database Configuration

The `DatabaseConfig` class provides a fluent interface to build a complete database configuration.

```python
from dtpyfw.db.config import DatabaseConfig

config = (
    DatabaseConfig()
    .set_db_user("user")
    .set_db_password("pass")
    .set_db_host("write-replica.db.example.com")
    .set_db_host_read("read-replica.db.example.com")
    .set_db_port(5432)
    .set_db_name("production_db")
    .set_db_ssl(True)
    .set_db_pool_size(10)
    .set_db_max_overflow(5)
)
```

Alternatively, you can provide full database URLs:

```python
config = (
    DatabaseConfig()
    .set_db_url("postgresql+asyncpg://user:pass@host:port/dbname")
    .set_db_url_read("postgresql+asyncpg://user:pass@read-host:port/dbname")
)
```

| Method                  | Description                                          |
| ----------------------- | ---------------------------------------------------- |
| `set_db_backend`        | Sets the database backend (e.g., `postgresql`).      |
| `set_db_driver_sync`    | Sets the synchronous driver (e.g., `psycopg2`).      |
| `set_db_driver_async`   | Sets the asynchronous driver (e.g., `asyncpg`).      |
| `set_db_url`            | Sets the full URL for the write database.            |
| `set_db_url_read`       | Sets the full URL for the read-only database.        |
| `set_db_user`           | Sets the database username.                          |
| `set_db_password`       | Sets the database password.                          |
| `set_db_host`           | Sets the hostname for the write database.            |
| `set_db_host_read`      | Sets the hostname for the read-only database.        |
| `set_db_port`           | Sets the database port.                              |
| `set_db_name`           | Sets the database name.                              |
| `set_db_ssl`            | Enables or disables SSL.                             |
| `set_db_pool_size`      | Configures the connection pool size.                 |
| `set_db_max_overflow`   | Configures the pool's max overflow.                  |
| `set_connect_args`      | Sets additional arguments for the DBAPI `connect`.   |

---

## `database.py` — Connection Management

The `DatabaseInstance` class is the core of the `db` package. It uses a `DatabaseConfig` object to create and manage SQLAlchemy engines and sessions for both synchronous and asynchronous operations.

```python
from dtpyfw.db.database import DatabaseInstance

# Assuming 'config' is a configured DatabaseConfig object
db_instance = DatabaseInstance(config)
```

### Key Attributes

- `base`: The declarative base for your ORM models. All models should inherit from this.
- `engine_write` / `engine_read`: Synchronous SQLAlchemy engines.
- `async_engine_write` / `async_engine_read`: Asynchronous SQLAlchemy engines.

### Synchronous Session Management

Use context managers for safe, automatic session handling.

**Write Session:**

```python
with db_instance.get_db_cm_write() as db:
    # Perform write operations
    db.add(some_object)
    db.commit()
```

**Read Session:**

```python
with db_instance.get_db_cm_read() as db:
    # Perform read-only operations
    results = db.query(MyModel).all()
```

### Asynchronous Session Management

Async context managers provide the same safety for async code.

**Async Write Session:**

```python
async with db_instance.async_get_db_cm_write() as db:
    # Perform async write operations
    await db.execute(...)
    await db.commit()
```

**Async Read Session:**

```python
async with db_instance.async_get_db_cm_read() as db:
    # Perform async read operations
    result = await db.execute(...)
    items = result.scalars().all()
```

### Creating Tables

To create all tables defined in your models:

```python
db_instance.create_tables()
```

---

## `health.py` — Health Checks

Verify that the database connections are active.

```python
from dtpyfw.db.health import is_database_connected

is_healthy, error = is_database_connected(db_instance)

if is_healthy:
    print("Database connection is OK.")
else:
    print(f"Database connection failed: {error}")
```

---

## `model.py` — ORM Model Base

The `ModelBase` class provides common functionality for all ORM models.

- **`id`**: A UUID primary key, automatically generated.
- **`created_at`**: A timestamp set when the record is created.
- **`updated_at`**: A timestamp that updates whenever the record is modified.
- **`get()`**: A method to convert the model instance to a dictionary.
- **`create()`**: A class method to create a new record from a dictionary.
- **`update()`**: An instance method to update a record from a dictionary.

### Example Usage

```python
from sqlalchemy import Column, String
from dtpyfw.db.model import ModelBase

# 'db_instance' is an initialized DatabaseInstance
class User(db_instance.base, ModelBase):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, unique=True)

# Create a user
with db_instance.get_db_cm_write() as db:
    new_user_data = {"name": "John Doe", "email": "john.doe@example.com"}
    user = User.create(db, new_user_data)

# Update a user
with db_instance.get_db_cm_write() as db:
    user_to_update = db.query(User).first()
    user_to_update.update(db, {"name": "John Smith"})
```

---

## `search.py` — Advanced Search

The `get_list` function provides a standardized way to implement complex, paginated searches with dynamic filters.

### Key Parameters

- `current_query`: A dictionary containing search parameters (e.g., from an API request).
- `db`: The SQLAlchemy session.
- `model`: The ORM model to query.
- `filters`: A list of dictionaries defining the available filters.
- `searchable_columns`: A list of columns to use for full-text search.
- `pre_conditions`: A list of initial WHERE clauses to apply to all queries.
- `joins`: A list of tables to join.

### Example Filter Definition

```python
filters = [
    {
        "label": "Status",
        "name": "status",
        "type": "select",
        "columns": [User.status],
    },
    {
        "label": "Creation Date",
        "name": "created_at",
        "type": "date",
        "columns": [User.created_at],
    },
]

search_results = get_list(
    current_query={"status": "active", "page": 1, "items_per_page": 20},
    db=db_session,
    model=User,
    filters=filters,
    searchable_columns=[User.name, User.email],
)
```

The function returns a dictionary containing `payload` (pagination info), `rows_data`, `available_filters`, and `selected_filters`.

---

## `utils.py` — Bulk Operations

For high-performance database writes, use the `upsert` utilities, which leverage PostgreSQL's `ON CONFLICT` feature.

### `upsert_data` (Synchronous)

```python
from dtpyfw.db.utils import upsert_data

data_to_upsert = [
    {"id": "some-uuid-1", "name": "New Name 1"},
    {"id": "some-uuid-2", "name": "New Name 2"},
]

with db_instance.get_db_cm_write() as db:
    upsert_data(data_to_upsert, User, db)
```

### `upsert_data_async` (Asynchronous)

```python
from dtpyfw.db.utils import upsert_data_async

async with db_instance.async_get_db_cm_write() as db:
    await upsert_data_async(data_to_upsert, User, db)
```

Both functions can be set to `only_insert=True` or `only_update=True` to restrict the operation.

---

*This documentation covers the `db` sub-package of the DealerTower Python Framework.*

