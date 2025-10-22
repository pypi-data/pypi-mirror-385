# API Reference

Welcome to the DBJobQ API reference. This section provides detailed documentation for all classes, methods, and functions.

## Core Components

DBJobQ consists of four main components:

### [Job](job.md)
The `Job` dataclass represents a unit of work with metadata like priority, retries, and scheduling information.

### [JobQueue](jobqueue.md)
The `JobQueue` class manages the job lifecycle - enqueueing, dequeueing, completing, and retrying jobs.

### [Worker](worker.md)
The `Worker` class processes jobs from the queue in a background thread with adaptive polling.

### [Storage](storage.md)
The `BaseStorage` abstract class defines the storage interface. Implementations include `SQLAlchemyStorage` and can be extended for other backends.

## Quick Navigation

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| **Job** | Data model for jobs | `from_dict()` |
| **JobQueue** | Queue management | `enqueue()`, `dequeue()`, `complete()`, `fail()` |
| **Worker** | Job processing | `start()`, `stop()`, `current_job` |
| **Storage** | Persistence layer | `enqueue()`, `dequeue()`, `complete()`, `fail()`, `retry()` |

## Decorators

- **[@job](jobqueue.md#job-decorator)**: Decorator to configure job functions with default settings

## Type Hints

DBJobQ uses comprehensive type hints throughout. All public APIs are fully typed for better IDE support and type checking.

```python
from dbjobq import Job, JobQueue, Worker
from dbjobq.storage import BaseStorage, SQLAlchemyStorage

# All classes and functions have full type annotations
def my_typed_function(queue: JobQueue) -> str:
    job: Job = queue.dequeue()
    return job.id
```

## Imports

All main components can be imported from the root package:

```python
from dbjobq import Job, JobQueue, Worker, job
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage
from dbjobq.storage.base import BaseStorage
```
