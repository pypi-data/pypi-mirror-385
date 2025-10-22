# DBJobQ

Database-backed Job Queue for Python. Supports multiple storage backends: SQLAlchemy, MongoDB, Redis, DynamoDB.

## Installation

```bash
# Basic installation (includes scheduling support)
pip install dbjobq

# Or install with specific storage backend(s)
pip install dbjobq[sqlalchemy]  # SQLAlchemy with async drivers
pip install dbjobq[mongo]        # MongoDB
pip install dbjobq[redis]        # Redis
pip install dbjobq[dynamo]       # DynamoDB

# Or install all storage backends
pip install dbjobq[all]
```

### Development Installation

```bash
# Install uv if not already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the project
git clone <repo-url>
cd dbjobq

# Sync dependencies with all extras and dev tools
uv sync --all-extras
```

## Usage

### Define Jobs

```python
from dbjobq import job

@job
def my_background_task(data):
    print(f"Processing {data}")
    # Do work
```

### Create Job Queue

```python
from dbjobq import JobQueue, Worker
from dbjobq.storage import SQLAlchemyStorage

# For SQLAlchemy
storage = SQLAlchemyStorage('sqlite:///jobs.db')
job_queue = JobQueue(storage)

# Enqueue a job
job_id = job_queue.enqueue(my_background_task, {'key': 'value'})

# Inspect the queue
pending_jobs = job_queue.get_pending_jobs()
running_jobs = job_queue.get_running_jobs()
completed_jobs = job_queue.get_completed_jobs()
failed_jobs = job_queue.get_failed_jobs()

# Get a specific job
job = job_queue.get_job(job_id)
if job:
    print(f"Job {job.id}: {job.type} - {job.status}")

# List all jobs or filter by status
all_jobs = job_queue.list_jobs()
pending_only = job_queue.list_jobs(status="pending", limit=10)

# Start a worker
worker = Worker(job_queue)
worker.start()

# Later, stop the worker
worker.stop()
```

### Storage Backends

- **SQLAlchemy**: Supports any SQL database.
- **MongoDB**: `MongoStorage(mongo_url, db_name)`
- **Redis**: `RedisStorage(redis_url)`
- **DynamoDB**: `DynamoStorage(table_name, region_name)`

## Features

- Cross-process job locking
- Multiple storage backends
- Simple API similar to Celery
- Suitable for web apps like FastAPI with Gunicorn

## Development

```bash
# Run tests
uv run pytest

# Run the example
uv run python hello.py
```
