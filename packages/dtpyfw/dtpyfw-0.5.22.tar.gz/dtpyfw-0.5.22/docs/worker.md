# Worker Sub-Package

**DealerTower Python Framework** — Simplifies Celery task and worker configuration by providing `Task` and `Worker` helper classes for registering tasks, scheduling jobs, and building a Celery application with minimal boilerplate.

## Overview

The `worker` sub-package centralizes Celery setup across microservices. It offers:

- **`Task` class**: A helper for registering task import paths and defining periodic jobs with `crontab` or `timedelta` schedules.
- **`Worker` class**: A fluent builder for assembling a Celery application, configuring the broker (Redis), result backend, serializers, and other core settings.
- **Automatic Task Discovery**: Discovers and registers all tasks provided by the `Task` instance.
- **Periodic Task Scheduling**: Integrates with `celery-redbeat` to manage and run scheduled tasks.
- **Unique Task Execution**: Uses `celery-once` to ensure that tasks run only one at a time.
- **Secure Redis Integration**: Built-in support for SSL/TLS connections to Redis.

## Installation

To use the worker utilities, install `dtpyfw` with the `worker` extra. This pulls in `celery`, `celery-redbeat`, and `celery-once`.

```bash
pip install dtpyfw[worker]
```

---

## `task.py` — `Task` Class

The `Task` class is used to collect all task import paths and define periodic schedules. An instance of this class is passed to the `Worker` builder.

### Initialization and Registration

```python
from celery.schedules import crontab
from dtpyfw.worker.task import Task

# Create a task collection
tasks = (
    Task()
    .register("my_app.tasks.process_data", queue="processing")
    .register_periodic_task(
        "my_app.tasks.nightly_cleanup",
        schedule=crontab(hour=2, minute=30),
        queue="maintenance",
    )
)
```

### Methods

| Method                               | Description                                                              |
| ------------------------------------ | ------------------------------------------------------------------------ |
| `register(route, queue)`             | Registers a single task's import path and optionally assigns it to a queue. |
| `bulk_register(routes, queue)`       | Registers multiple task routes to a shared queue.                        |
| `register_periodic_task(route, schedule, queue, *args)` | Schedules a periodic task with a `crontab` or `timedelta`. |
| `bulk_register_periodic_task(tasks, queue)` | Registers multiple periodic tasks at once.                               |
| `get_tasks()`                        | Returns a list of all registered task import paths.                      |
| `get_tasks_routes()`                 | Returns a dictionary for Celery's `task_routes` configuration.           |
| `get_periodic_tasks()`               | Returns a dictionary for Celery's `beat_schedule` (for RedBeat).         |

---

## `worker.py` — `Worker` Class

The `Worker` class is a fluent builder that constructs and configures a Celery application instance.

### Initialization and Creation

```python
from dtpyfw.redis.connection import RedisInstance, RedisConfig
from dtpyfw.worker.worker import Worker
from dtpyfw.worker.task import Task

# 1. Configure Redis
redis_config = RedisConfig().set_redis_host("localhost")
redis_instance = RedisInstance(redis_config)

# 2. Define tasks
tasks = Task().register("my_app.tasks.process_data")

# 3. Build the Celery app
worker_builder = (
    Worker()
    .set_name("my_celery_app")
    .set_redis(redis_instance)
    .set_task(tasks)
    .set_timezone("UTC")
    .set_result_expires(7200)
)

# 4. Create the app instance
celery_app = worker_builder.create()
```

### Fluent Setters

| Method                                     | Description                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------ |
| `set_task(task: Task)`                     | Attaches the `Task` instance containing all routes and schedules.        |
| `set_redis(redis_instance: RedisInstance)` | Configures the Redis broker and result backend, including SSL.           |
| `set_name(name: str)`                      | Sets the Celery application name.                                        |
| `set_timezone(timezone: str)`              | Defines the timezone for the scheduler (e.g., "UTC").                    |
| `set_task_serializer(serializer: str)`     | Sets the task message serializer (default: "json").                      |
| `set_result_serializer(serializer: str)`   | Sets the result serializer (default: "json").                            |
| `set_track_started(value: bool)`           | If `True`, tasks report a 'started' state.                               |
| `set_result_persistent(value: bool)`       | If `True`, results are stored persistently in the backend.               |
| `set_worker_prefetch_multiplier(num: int)` | Sets the number of tasks a worker can prefetch.                          |
| `set_broker_prefix(prefix: str)`           | Sets the key prefix for broker data in Redis.                            |
| `set_backend_prefix(prefix: str)`          | Sets the key prefix for result backend data in Redis.                    |
| `set_redbeat_key_prefix(prefix: str)`      | Sets the key prefix for RedBeat scheduler data.                          |
| `set_redbeat_lock_key(key: str)`           | Sets the lock key used by the RedBeat scheduler.                         |
| `set_enable_utc(value: bool)`              | Enables or disables UTC support.                                         |
| `set_broker_connection_max_retries(val: int)` | Sets the maximum number of broker connection retries.                    |
| `set_broker_connection_retry_on_startup(val: bool)` | If `True`, retries broker connection on startup.                 |
| `set_result_expires(seconds: int)`         | Sets the expiration time for task results in seconds.                    |
| `set_once_default_timeout(seconds: int)`   | Sets the default lock timeout for `celery-once`.                         |
| `set_once_blocking(blocking: bool)`        | If `True`, tasks will wait for an existing lock to be released.          |
| `set_once_blocking_timeout(seconds: int)`  | Sets how long a task will wait for a lock when `blocking` is `True`.     |

### `create()`

This method finalizes the configuration and returns a `Celery` application instance, ready to be run.

---

## Running the Worker

1. Save the created `celery_app` instance in a file (e.g., `my_app/celery.py`).
2. Run the worker process from your terminal:

   ```bash
   celery -A my_app.celery worker --loglevel=info
   ```

3. Run the Celery Beat scheduler process to handle periodic tasks:

   ```bash
   celery -A my_app.celery beat --loglevel=info
   ```

---

*This documentation covers the `worker` sub-package of the DealerTower Python Framework. Ensure the `worker` extra is installed to use these features.*
