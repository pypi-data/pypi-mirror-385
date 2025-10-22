# JobQueue

The `JobQueue` class is the main interface for managing jobs. It provides methods to enqueue, dequeue, complete, fail, and query jobs.

## Overview

`JobQueue` handles:

- **Enqueuing**: Add new jobs to the queue
- **Dequeuing**: Retrieve the next job to process
- **Completion**: Mark jobs as completed or failed
- **Retrying**: Automatically retry failed jobs with backoff
- **Querying**: Get jobs by status, ID, or other criteria
- **Execution**: Execute jobs and handle retries automatically

## Class Reference

::: dbjobq.queue.JobQueue
    options:
      show_root_heading: true
      show_source: true

## Constructor

### \_\_init\_\_

```python
def __init__(self, storage: BaseStorage)
```

Create a new JobQueue instance.

**Parameters:**

- `storage` (BaseStorage): Storage backend for persisting jobs

**Example:**

```python
from dbjobq import JobQueue
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

storage = SQLAlchemyStorage("sqlite:///jobs.db")
queue = JobQueue(storage)
```

## Methods

### enqueue

Add a job to the queue.

```python
def enqueue(
    self,
    func: Callable[..., Any] | str,
    *,
    max_retries: int | None = None,
    priority: int | None = None,
    execute_at: datetime | None = None,
    **kwargs: Any
) -> str
```

**Parameters:**

- `func` (Callable | str): Function to execute or job type name
- `max_retries` (int | None): Maximum retry attempts (overrides decorator)
- `priority` (int | None): Job priority (higher processes first, overrides decorator)
- `execute_at` (datetime | None): Schedule job for future execution
- `**kwargs`: Arguments to pass to the function

**Returns:**

- `str`: Job ID (UUID)

**Examples:**

```python
# Enqueue a function
def send_email(to: str, subject: str):
    pass

job_id = queue.enqueue(send_email, to="user@example.com", subject="Hello")

# Enqueue with priority
job_id = queue.enqueue(send_email, to="admin@example.com", 
                       subject="Urgent", priority=10)

# Schedule for later
from datetime import datetime, timedelta
future = datetime.now() + timedelta(hours=1)
job_id = queue.enqueue(send_email, to="user@example.com",
                       subject="Reminder", execute_at=future)

# Enqueue by name (if using @job decorator)
from dbjobq import job

@job
def process_order(order_id: int):
    pass

job_id = queue.enqueue("process_order", order_id=123)
```

### dequeue

Retrieve the next job to process.

```python
def dequeue(self) -> Job | None
```

**Returns:**

- `Job | None`: Next job to process, or None if queue is empty

**Example:**

```python
job = queue.dequeue()
if job:
    print(f"Processing job {job.id}: {job.type}")
else:
    print("Queue is empty")
```

**Behavior:**

- Returns highest priority pending job
- Respects `execute_at` (won't return jobs scheduled for the future)
- Marks job as "running"
- Thread-safe (uses database locking)

### complete

Mark a job as successfully completed.

```python
def complete(self, job_id: str) -> None
```

**Parameters:**

- `job_id` (str): ID of the job to mark as completed

**Example:**

```python
job = queue.dequeue()
if job:
    try:
        # Process the job
        result = process(job)
        queue.complete(job.id)
    except Exception as e:
        queue.fail(job.id, str(e))
```

### fail

Mark a job as failed and handle retries.

```python
def fail(self, job_id: str, error: str) -> None
```

**Parameters:**

- `job_id` (str): ID of the job that failed
- `error` (str): Error message describing the failure

**Example:**

```python
try:
    result = risky_operation()
except Exception as e:
    queue.fail(job.id, str(e))
```

**Behavior:**

- If `job.attempts < job.max_retries`: retries with exponential backoff
- If max retries exceeded: marks as "failed"
- Stores error message for debugging

### retry

Manually retry a failed job.

```python
def retry(self, job_id: str, delay_seconds: float = 0) -> None
```

**Parameters:**

- `job_id` (str): ID of the job to retry
- `delay_seconds` (float): Delay before the job can be processed (default: 0)

**Example:**

```python
# Retry immediately
queue.retry("job-123")

# Retry after 60 seconds
queue.retry("job-123", delay_seconds=60)
```

### execute_job

Execute a job, handling success, failure, and retries automatically.

```python
def execute_job(self, job: Job) -> None
```

**Parameters:**

- `job` (Job): Job to execute

**Example:**

```python
job = queue.dequeue()
if job:
    queue.execute_job(job)  # Handles everything automatically
```

**Behavior:**

- Executes the job function with its data
- Marks as completed on success
- Retries on failure (if attempts < max_retries)
- Marks as failed if max retries exceeded
- Uses exponential backoff: 2^attempts seconds

**Note:** The `Worker` class calls this method automatically. You rarely need to call it directly.

### get_job

Retrieve a job by its ID.

```python
def get_job(self, job_id: str) -> Job | None
```

**Parameters:**

- `job_id` (str): Job ID to retrieve

**Returns:**

- `Job | None`: Job with the given ID, or None if not found

**Example:**

```python
job = queue.get_job("job-123")
if job:
    print(f"Status: {job.status}")
    print(f"Attempts: {job.attempts}/{job.max_retries}")
```

### list_jobs

List jobs with optional filtering.

```python
def list_jobs(
    self,
    status: str | None = None,
    limit: int | None = None
) -> list[Job]
```

**Parameters:**

- `status` (str | None): Filter by status (pending, running, completed, failed)
- `limit` (int | None): Maximum number of jobs to return

**Returns:**

- `list[Job]`: List of jobs matching the criteria

**Example:**

```python
# All jobs
all_jobs = queue.list_jobs()

# Only failed jobs
failed = queue.list_jobs(status="failed")

# Last 10 completed jobs
recent = queue.list_jobs(status="completed", limit=10)
```

### get_pending_jobs

Get all pending jobs.

```python
def get_pending_jobs(self) -> list[Job]
```

**Returns:**

- `list[Job]`: List of pending jobs

**Example:**

```python
pending = queue.get_pending_jobs()
print(f"Jobs in queue: {len(pending)}")
```

### get_running_jobs

Get all currently running jobs.

```python
def get_running_jobs(self) -> list[Job]
```

**Returns:**

- `list[Job]`: List of running jobs

**Example:**

```python
running = queue.get_running_jobs()
for job in running:
    print(f"Running: {job.type} (started {job.updated_at})")
```

### get_completed_jobs

Get completed jobs.

```python
def get_completed_jobs(self, limit: int | None = None) -> list[Job]
```

**Parameters:**

- `limit` (int | None): Maximum number of jobs to return

**Returns:**

- `list[Job]`: List of completed jobs

**Example:**

```python
# All completed jobs
completed = queue.get_completed_jobs()

# Last 50 completed jobs
recent = queue.get_completed_jobs(limit=50)
```

### get_failed_jobs

Get failed jobs.

```python
def get_failed_jobs(self) -> list[Job]
```

**Returns:**

- `list[Job]`: List of failed jobs

**Example:**

```python
failed = queue.get_failed_jobs()
for job in failed:
    print(f"Failed: {job.type}")
    print(f"  Error: {job.error}")
    print(f"  Attempts: {job.attempts}")
```

## Job Decorator

The `@job` decorator allows you to configure default settings for job functions.

```python
@job(max_retries: int = 3, priority: int = 5)
def func(...) -> Any
```

**Parameters:**

- `max_retries` (int): Default maximum retry attempts (default: 3)
- `priority` (int): Default priority (default: 5)

**Example:**

```python
from dbjobq import job

@job(max_retries=5, priority=10)
def critical_task(data: str):
    """High-priority task that retries up to 5 times."""
    pass

@job(max_retries=1, priority=1)
def background_task(data: str):
    """Low-priority task with minimal retries."""
    pass

# Enqueue uses decorator defaults
queue.enqueue(critical_task, data="important")

# Override decorator defaults
queue.enqueue(critical_task, data="very_important", 
              max_retries=10, priority=15)
```

## Usage Patterns

### Basic Job Processing

```python
from dbjobq import JobQueue, job
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

# Setup
storage = SQLAlchemyStorage("sqlite:///jobs.db")
queue = JobQueue(storage)

# Define job
@job
def process_order(order_id: int, user_id: int):
    print(f"Processing order {order_id} for user {user_id}")

# Enqueue
job_id = queue.enqueue(process_order, order_id=123, user_id=456)

# Process manually
job = queue.dequeue()
if job:
    queue.execute_job(job)
```

### Job Priority Management

```python
# High priority - process first
queue.enqueue(send_alert, priority=10, message="Critical error")

# Normal priority
queue.enqueue(send_email, priority=5, to="user@example.com")

# Low priority - process last
queue.enqueue(cleanup_logs, priority=1)
```

### Scheduled Jobs

```python
from datetime import datetime, timedelta

# Schedule for specific time
future = datetime(2024, 10, 20, 15, 0, 0)
queue.enqueue(send_reminder, execute_at=future, user_id=123)

# Schedule for relative time
in_one_hour = datetime.now() + timedelta(hours=1)
queue.enqueue(generate_report, execute_at=in_one_hour)
```

### Monitoring Queue Health

```python
def monitor_queue():
    """Check queue health and alert if needed."""
    pending = len(queue.get_pending_jobs())
    running = len(queue.get_running_jobs())
    failed = len(queue.get_failed_jobs())
    
    print(f"Queue Status:")
    print(f"  Pending: {pending}")
    print(f"  Running: {running}")
    print(f"  Failed: {failed}")
    
    if pending > 1000:
        alert("Queue backlog is high!")
    
    if failed > 100:
        alert("Many failed jobs - investigation needed!")
```

### Handling Failed Jobs

```python
def retry_failed_jobs():
    """Manually retry all failed jobs."""
    failed = queue.get_failed_jobs()
    
    for job in failed:
        print(f"Retrying job {job.id}: {job.type}")
        queue.retry(job.id, delay_seconds=5)
```

## Notes

!!! tip "Thread Safety"
    All `JobQueue` methods are thread-safe. Multiple workers can safely call `dequeue()` concurrently.

!!! info "Job Function Resolution"
    When you pass a function to `enqueue()`, it's stored by name. The function must be importable when the worker processes it.

!!! warning "Serialization"
    Job arguments must be JSON-serializable. Complex objects (like database connections or file handles) cannot be passed as job arguments.
