# Advanced Examples

This section provides real-world examples and patterns for using DBJobQ in production applications.

!!! note "Job Function Types"
    DBJobQ supports **both synchronous and asynchronous job functions**:
    
    - **Sync functions** (`def`): Regular Python functions - great for CPU-bound work or wrapping existing sync code
    - **Async functions** (`async def`): Coroutine functions - ideal for I/O-bound operations like API calls, database queries, or file operations
    
    The queue automatically detects which type your function is and handles it appropriately. Only the queue operations (enqueue, dequeue, etc.) require `async/await` - your job functions can be either sync or async based on your needs.

## Retry Strategies

### Exponential Backoff (Built-in)

DBJobQ uses exponential backoff by default for both sync and async jobs:

```python
import asyncio
from dbjobq import JobQueue, job
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

# Sync job function
@job(max_retries=5)
def call_external_api_sync(data):
    """
    Sync job with retries: 2s, 4s, 8s, 16s, 32s
    Total time: ~1 minute
    """
    import requests
    url = data["url"]
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

# Async job function - ideal for I/O operations
@job(max_retries=5)
async def call_external_api_async(data):
    """
    Async job with retries - better for concurrent I/O
    """
    import aiohttp
    url = data["url"]
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            return await response.json()

# Queue operations use async/await
async def main():
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)
    
    # Both work the same way
    sync_job_id = await queue.enqueue(call_external_api_sync, {
        "url": "https://api.example.com/data"
    })
    async_job_id = await queue.enqueue(call_external_api_async, {
        "url": "https://api.example.com/data"
    })
    
    print(f"Enqueued sync job: {sync_job_id}")
    print(f"Enqueued async job: {async_job_id}")
    
    await storage.close()

asyncio.run(main())
```

### Custom Retry Logic

Implement custom retry behavior:

```python
import time
from dbjobq import job

@job(max_retries=3)
def smart_retry_task(data):
    """Custom retry logic based on error type."""
    try:
        return process_data(data)
    except ConnectionError as e:
        # Network error - let it retry automatically
        print(f"Connection error: {e}")
        raise
    except ValueError as e:
        # Data validation error - don't retry
        print(f"Invalid data: {e}")
        return None  # Complete without raising
    except Exception as e:
        # Unexpected error - log and retry
        print(f"Unexpected error: {e}")
        raise
```

### Conditional Retries

Only retry under certain conditions:

```python
class RetryableError(Exception):
    """Errors that should trigger retry."""
    pass

@job(max_retries=3)
def conditional_retry(data):
    """Only retry on specific errors."""
    item_id = data["item_id"]
    try:
        result = process_item(item_id)
        return result
    except TemporaryFailure as e:
        # This should retry
        raise RetryableError(f"Temporary failure: {e}")
    except PermanentFailure as e:
        # Don't retry - log and complete
        log_error(f"Permanent failure for {item_id}: {e}")
        return None
```

### Retry with External Monitoring

Track retry metrics:

```python
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RetryMetric:
    job_id: str
    job_type: str
    attempt: int
    timestamp: datetime
    error: str

class RetryMonitor:
    def __init__(self):
        self.metrics = []
    
    async def record_retry(self, queue, job_id, error):
        """Record retry metrics."""
        job = await queue.get_job(job_id)
        metric = RetryMetric(
            job_id=job.id,
            job_type=job.type,
            attempt=job.attempts,
            timestamp=datetime.now(),
            error=str(error)
        )
        self.metrics.append(metric)
        
        # Alert on high retry rates
        if job.attempts >= job.max_retries - 1:
            logging.warning(
                f"Job {job.id} approaching max retries: "
                f"{job.attempts}/{job.max_retries}"
            )

monitor = RetryMonitor()

@job(max_retries=5)
def monitored_task(data):
    """Task with retry monitoring."""
    # Your job logic here
    return process(data["value"])

# Note: Monitoring happens in the worker, not in the job function itself
```

## Priority Management

### Priority Levels

Define consistent priority levels:

```python
import asyncio
from enum import IntEnum
from dbjobq import job, JobQueue
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

class Priority(IntEnum):
    """Standard priority levels."""
    CRITICAL = 10  # Security alerts, password resets
    HIGH = 8       # User-facing operations
    NORMAL = 5     # Regular background jobs
    LOW = 3        # Analytics, logging
    BULK = 1       # Mass operations, cleanup

@job(priority=Priority.CRITICAL)
def send_security_alert(data):
    """Critical security notification."""
    user_id = data["user_id"]
    alert_type = data["alert_type"]
    # Send alert logic
    pass

@job(priority=Priority.NORMAL)
def generate_report(data):
    """Standard report generation."""
    user_id = data["user_id"]
    # Generate report logic
    pass

@job(priority=Priority.LOW)
def update_analytics(data):
    """Low-priority analytics."""
    event = data["event"]
    # Analytics logic
    pass

async def main():
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)
    
    # Enqueue with different priorities
    await queue.enqueue(send_security_alert, {"user_id": 123, "alert_type": "breach"})
    await queue.enqueue(generate_report, {"user_id": 123})
    await queue.enqueue(update_analytics, {"event": "login"})
    
    await storage.close()

asyncio.run(main())
```

### Dynamic Priority

Adjust priority based on context:

```python
async def enqueue_order_processing(queue, order):
    """Prioritize based on order value."""
    if order["total"] > 1000:
        priority = Priority.HIGH
    elif order["total"] > 100:
        priority = Priority.NORMAL
    else:
        priority = Priority.LOW
    
    await queue.enqueue(
        process_order,
        {"order_id": order["id"]},
        priority=priority
    )

@job()
def process_order(data):
    """Process an order."""
    order_id = data["order_id"]
    # Processing logic
    pass
```

### Priority Queue Monitoring

Track priority distribution:

```python
import asyncio
from collections import Counter

async def analyze_queue_priorities(queue):
    """Analyze priority distribution in queue."""
    pending = await queue.get_pending_jobs()
    
    priorities = Counter(job.priority for job in pending)
    
    print("Queue Priority Distribution:")
    for priority, count in sorted(priorities.items(), reverse=True):
        print(f"  Priority {priority}: {count} jobs")
    
    # Alert if too many high-priority jobs
    high_priority = sum(
        count for priority, count in priorities.items()
        if priority >= Priority.HIGH
    )
    
    if high_priority > 100:
        alert(f"High priority queue backlog: {high_priority} jobs")

# Usage
async def main():
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)
    
    await analyze_queue_priorities(queue)
    
    await storage.close()

asyncio.run(main())
```

## Scheduled Jobs

!!! tip "Recurring Schedules"
    For true recurring jobs with cron or interval schedules, see the **[Schedules Guide](schedules.md)**. This section covers one-time delayed execution.

### One-Time Scheduled Jobs

Schedule jobs for specific times:

```python
import asyncio
from datetime import datetime, timedelta
from dbjobq import job, JobQueue
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

@job()
def send_reminder(data):
    """Send a scheduled reminder."""
    user_id = data["user_id"]
    message = data["message"]
    print(f"Reminder for user {user_id}: {message}")

async def main():
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)
    
    # Schedule for specific time (datetime object)
    scheduled_time = datetime(2024, 10, 21, 9, 0, 0)  # 9 AM tomorrow
    await queue.enqueue(
        send_reminder,
        {
            "user_id": 123,
            "message": "Meeting in 30 minutes"
        },
        delay=(scheduled_time - datetime.now()).total_seconds()
    )
    
    # Schedule relative to now (in 1 hour)
    await queue.enqueue(
        expire_session,
        {"session_id": "abc123"},
        delay=3600  # 1 hour in seconds
    )
    
    await storage.close()

asyncio.run(main())
```

### Self-Scheduling Recurring Pattern

Implement self-rescheduling jobs (for simple cases):

```python
from datetime import datetime, timedelta

@job(priority=Priority.LOW)
def daily_cleanup(data):
    """Daily cleanup task that reschedules itself."""
    # Perform cleanup
    cleanup_temp_files()
    cleanup_old_logs()
    
    # Note: To re-schedule, you need access to the queue
    # This pattern works but schedules (see Schedules Guide) are better
    print("Cleanup completed - would need to re-enqueue manually")

async def start_daily_cleanup(queue):
    """Start the recurring cleanup job."""
    # Calculate next 2 AM
    tomorrow = datetime.now() + timedelta(days=1)
    next_run = tomorrow.replace(hour=2, minute=0, second=0, microsecond=0)
    delay = (next_run - datetime.now()).total_seconds()
    
    await queue.enqueue(daily_cleanup, {}, delay=delay)
```

!!! warning "Better Alternative"
    For recurring jobs, use the built-in **Schedule** system instead of self-scheduling:
    
    ```python
    from dbjobq.models import Schedule
    import time
    
    # Create a daily schedule at 2 AM
    schedule = Schedule(
        id="daily-cleanup",
        job_type="__main__.daily_cleanup",
        job_data={},
        schedule_type="cron",
        schedule_expression="0 2 * * *",  # 2 AM daily
        next_run=time.time(),
        enabled=True
    )
    
    await storage.create_schedule(schedule)
    ```
    
    See the [Schedules Guide](schedules.md) for complete documentation.
```

## Multiple Workers

### Basic Multi-Worker Setup

Run multiple workers for increased throughput:

```python
import asyncio
from dbjobq import Worker, JobQueue
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

async def start_workers(num_workers: int = 4):
    """Start multiple workers in the same process."""
    storage = SQLAlchemyStorage("postgresql+asyncpg://localhost/jobs")
    await storage.initialize()
    queue = JobQueue(storage)
    
    workers = []
    for i in range(num_workers):
        worker = Worker(queue, poll_interval=1.0)
        await worker.start()
        workers.append(worker)
        print(f"Started worker {i+1}/{num_workers}")
    
    return workers, storage

# Usage
async def main():
    workers, storage = await start_workers(4)
    
    # Run for some time
    await asyncio.sleep(3600)  # 1 hour
    
    # Shutdown
    for worker in workers:
        await worker.stop()
    await storage.close()

asyncio.run(main())
```

### Worker Pool with Context Manager

```python
class WorkerPool:
    """Manage a pool of workers with async context manager."""
    
    def __init__(self, queue, num_workers: int):
        self.queue = queue
        self.num_workers = num_workers
        self.workers = []
    
    async def __aenter__(self):
        """Start all workers."""
        for i in range(self.num_workers):
            worker = Worker(self.queue, poll_interval=1.0)
            await worker.start()
            self.workers.append(worker)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop all workers."""
        for worker in self.workers:
            await worker.stop()
    
    def get_status(self):
        """Get status of all workers."""
        return {
            "total": len(self.workers),
            "running": sum(1 for w in self.workers if w.is_running()),
            "paused": sum(1 for w in self.workers if w.is_paused())
        }

# Usage
async def main():
    storage = SQLAlchemyStorage("postgresql+asyncpg://localhost/jobs")
    await storage.initialize()
    queue = JobQueue(storage)

    async with WorkerPool(queue, num_workers=4) as pool:
        # Workers are running
        print(f"Worker status: {pool.get_status()}")
        
        # Your application logic
        await asyncio.sleep(60)
    # Workers are automatically stopped
    
    await storage.close()

asyncio.run(main())
```

### Distributed Workers

Run workers across multiple machines:

```python
# worker.py - Run on each machine
import asyncio
import os
import signal
import sys
from dbjobq import Worker, JobQueue
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

async def run_workers():
    # Shared database (async driver!)
    db_url = os.environ["DATABASE_URL"]  # e.g., postgresql+asyncpg://db-server/jobs
    storage = SQLAlchemyStorage(db_url)
    await storage.initialize()
    queue = JobQueue(storage)
    
    # Determine worker count based on CPU
    num_workers = os.cpu_count() or 4
    
    workers = []
    for i in range(num_workers):
        worker = Worker(queue, poll_interval=1.0)
        await worker.start()
        workers.append(worker)
    
    print(f"Started {num_workers} workers")
    
    # Handle shutdown
    async def shutdown():
        print("\nShutting down workers...")
        for worker in workers:
            await worker.stop()
        await storage.close()
        sys.exit(0)
    
    # Set up signal handlers
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))
    
    # Keep alive
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run_workers())
```

Run on multiple machines:

```bash
# Machine 1
DATABASE_URL=postgresql+asyncpg://db-server/jobs python worker.py

# Machine 2
DATABASE_URL=postgresql+asyncpg://db-server/jobs python worker.py

# Machine 3
DATABASE_URL=postgresql+asyncpg://db-server/jobs python worker.py
```

### Worker with Resource Limits

Limit worker resources:

```python
import resource
import os

class ResourceLimitedWorker:
    """Worker with CPU and memory limits."""
    
    def __init__(self, queue, memory_mb: int = 512):
        self.queue = queue
        self.memory_mb = memory_mb
        self.worker = None
    
    def start(self):
        """Start worker with resource limits."""
        # Set memory limit (Linux only)
        if hasattr(resource, 'RLIMIT_AS'):
            memory_bytes = self.memory_mb * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_AS,
                (memory_bytes, memory_bytes)
            )
        
        # Set CPU priority (nice value)
        os.nice(10)  # Lower priority
        
        self.worker = Worker(self.queue)
        self.worker.start()
    
    def stop(self):
        """Stop worker."""
        if self.worker:
            self.worker.stop()
```

## Error Handling Patterns

### Comprehensive Error Handling

```python
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for jobs."""
    
    @staticmethod
    def handle_job_error(job, error: Exception):
        """Handle job errors with logging and alerts."""
        error_info = {
            "job_id": job.id,
            "job_type": job.type,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "attempts": job.attempts,
            "max_retries": job.max_retries,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log error
        logger.error(
            f"Job {job.id} ({job.type}) failed: {error}",
            extra=error_info
        )
        
        # Alert on critical jobs
        if job.priority >= Priority.CRITICAL:
            send_alert(f"Critical job failed: {job.type}", error_info)
        
        # Store in error tracking system
        if hasattr(error, "__sentry__"):
            capture_exception(error, extra=error_info)

@job(max_retries=3)
def monitored_job(data: dict):
    """Job with comprehensive error handling."""
    try:
        return process_data(data)
    except Exception as e:
        job = queue.get_job(current_job_id)
        ErrorHandler.handle_job_error(job, e)
        raise
```

### Circuit Breaker Pattern

Prevent cascading failures:

```python
from datetime import datetime, timedelta
from collections import defaultdict

class CircuitBreaker:
    """Circuit breaker for external services."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout)
        self.failures = defaultdict(list)
        self.open_until = {}
    
    def is_open(self, service: str) -> bool:
        """Check if circuit is open for service."""
        if service in self.open_until:
            if datetime.now() < self.open_until[service]:
                return True
            else:
                # Timeout expired, try again
                del self.open_until[service]
                self.failures[service].clear()
        return False
    
    def record_failure(self, service: str):
        """Record a failure."""
        self.failures[service].append(datetime.now())
        
        # Remove old failures
        cutoff = datetime.now() - self.timeout
        self.failures[service] = [
            f for f in self.failures[service] if f > cutoff
        ]
        
        # Open circuit if threshold exceeded
        if len(self.failures[service]) >= self.failure_threshold:
            self.open_until[service] = datetime.now() + self.timeout
            logger.warning(f"Circuit breaker opened for {service}")
    
    def record_success(self, service: str):
        """Record a success."""
        self.failures[service].clear()

breaker = CircuitBreaker()

@job(max_retries=3)
def call_external_service(service: str, data: dict):
    """Call external service with circuit breaker."""
    if breaker.is_open(service):
        logger.warning(f"Circuit breaker open for {service}, skipping")
        return None
    
    try:
        result = external_api_call(service, data)
        breaker.record_success(service)
        return result
    except Exception as e:
        breaker.record_failure(service)
        raise
```

### Dead Letter Queue

Handle permanently failed jobs:

```python
class DeadLetterQueue:
    """Store permanently failed jobs for manual intervention."""
    
    def __init__(self, storage):
        self.storage = storage
    
    def move_to_dlq(self, job):
        """Move failed job to dead letter queue."""
        dlq_data = {
            "original_job_id": job.id,
            "job_type": job.type,
            "job_data": job.data,
            "error": job.error,
            "attempts": job.attempts,
            "failed_at": datetime.now().isoformat()
        }
        
        # Store in separate table/collection
        self.storage.save_to_dlq(dlq_data)
        
        # Send alert
        alert(f"Job moved to DLQ: {job.type} ({job.id})")
    
    def retry_from_dlq(self, dlq_job_id: str):
        """Retry a job from dead letter queue."""
        dlq_job = self.storage.get_from_dlq(dlq_job_id)
        
        # Re-enqueue with fresh retry count
        queue.enqueue(
            dlq_job["job_type"],
            **dlq_job["job_data"]
        )

# Usage with custom execute_job
def execute_job_with_dlq(queue, job):
    """Execute job and move to DLQ if permanently failed."""
    try:
        queue.execute_job(job)
    except Exception:
        # Check if job is permanently failed
        updated_job = queue.get_job(job.id)
        if updated_job.status == "failed":
            dlq = DeadLetterQueue(queue.storage)
            dlq.move_to_dlq(updated_job)
```

## Monitoring and Observability

### Prometheus Metrics

Export metrics for Prometheus:

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Define metrics
jobs_enqueued = Counter(
    'jobq_jobs_enqueued_total',
    'Total jobs enqueued',
    ['job_type']
)

jobs_completed = Counter(
    'jobq_jobs_completed_total',
    'Total jobs completed',
    ['job_type']
)

jobs_failed = Counter(
    'jobq_jobs_failed_total',
    'Total jobs failed',
    ['job_type']
)

queue_size = Gauge(
    'jobq_queue_size',
    'Current queue size',
    ['status']
)

job_duration = Histogram(
    'jobq_job_duration_seconds',
    'Job execution duration',
    ['job_type']
)

class InstrumentedJobQueue(JobQueue):
    """JobQueue with Prometheus metrics."""
    
    def enqueue(self, func, **kwargs):
        """Enqueue with metrics."""
        job_id = super().enqueue(func, **kwargs)
        job_type = func.__name__ if callable(func) else func
        jobs_enqueued.labels(job_type=job_type).inc()
        return job_id
    
    def complete(self, job_id: str):
        """Complete with metrics."""
        job = self.get_job(job_id)
        super().complete(job_id)
        jobs_completed.labels(job_type=job.type).inc()
    
    def fail(self, job_id: str, error: str):
        """Fail with metrics."""
        job = self.get_job(job_id)
        super().fail(job_id, error)
        if job.attempts >= job.max_retries:
            jobs_failed.labels(job_type=job.type).inc()

def update_queue_metrics(queue):
    """Update queue size metrics."""
    queue_size.labels(status='pending').set(
        len(queue.get_pending_jobs())
    )
    queue_size.labels(status='running').set(
        len(queue.get_running_jobs())
    )
    queue_size.labels(status='failed').set(
        len(queue.get_failed_jobs())
    )

# Start metrics server
start_http_server(8000)

# Update metrics periodically
import threading
def metrics_updater():
    while True:
        update_queue_metrics(queue)
        time.sleep(15)

threading.Thread(target=metrics_updater, daemon=True).start()
```

### Logging Integration

Structured logging for jobs:

```python
import logging
import json
from datetime import datetime

class JobLogger:
    """Structured logger for jobs."""
    
    def __init__(self):
        self.logger = logging.getLogger("jobqueue")
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter('%(message)s')
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_job_event(self, event: str, job, **extra):
        """Log job event with structured data."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "job_id": job.id,
            "job_type": job.type,
            "status": job.status,
            "attempts": job.attempts,
            "priority": job.priority,
            **extra
        }
        self.logger.info(json.dumps(log_data))

job_logger = JobLogger()

@job
def logged_task(data: dict):
    """Task with structured logging."""
    job = queue.get_job(current_job_id)
    
    job_logger.log_job_event("start", job, data=data)
    
    try:
        result = process(data)
        job_logger.log_job_event("complete", job, result=result)
        return result
    except Exception as e:
        job_logger.log_job_event("error", job, error=str(e))
        raise
```

### Health Check Endpoint

Expose queue health for monitoring:

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health")
def health_check():
    """Queue health check endpoint."""
    try:
        pending = len(queue.get_pending_jobs())
        running = len(queue.get_running_jobs())
        failed = len(queue.get_failed_jobs())
        
        # Determine health status
        is_healthy = (
            pending < 1000 and
            failed < 100 and
            running < 50
        )
        
        status = "healthy" if is_healthy else "degraded"
        
        return jsonify({
            "status": status,
            "queue": {
                "pending": pending,
                "running": running,
                "failed": failed
            },
            "timestamp": datetime.now().isoformat()
        }), 200 if is_healthy else 503
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503

@app.route("/metrics")
def metrics():
    """Detailed queue metrics."""
    jobs = queue.list_jobs()
    
    by_status = {}
    by_type = {}
    
    for job in jobs:
        by_status[job.status] = by_status.get(job.status, 0) + 1
        by_type[job.type] = by_type.get(job.type, 0) + 1
    
    return jsonify({
        "by_status": by_status,
        "by_type": by_type,
        "total": len(jobs)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## Integration Examples

### FastAPI Integration

FastAPI is async-native, making it perfect for DBJobQ:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dbjobq import JobQueue, Worker, job
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

app = FastAPI()

# Global state
storage = None
queue = None
worker = None

# Job function (sync)
@job()
def send_email_job(data):
    """Send email in background."""
    to = data["to"]
    subject = data["subject"]
    body = data["body"]
    # Email sending logic
    print(f"Sending email to {to}: {subject}")

@app.on_event("startup")
async def startup():
    """Initialize queue and worker on startup."""
    global storage, queue, worker
    
    storage = SQLAlchemyStorage("postgresql+asyncpg://localhost/jobs")
    await storage.initialize()
    queue = JobQueue(storage)
    worker = Worker(queue)
    await worker.start()

@app.on_event("shutdown")
async def shutdown():
    """Stop worker on shutdown."""
    await worker.stop()
    await storage.close()

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

@app.post("/send-email")
async def send_email(request: EmailRequest):
    """Enqueue email sending job."""
    job_id = await queue.enqueue(send_email_job, {
        "to": request.to,
        "subject": request.subject,
        "body": request.body
    })
    
    return {"job_id": job_id, "status": "enqueued"}

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Check job status."""
    job = await queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "attempts": job.attempts,
        "error": job.error
    }

@app.get("/queue/stats")
async def queue_stats():
    """Get queue statistics."""
    pending = await queue.get_pending_jobs()
    completed = await queue.get_completed_jobs(limit=100)
    failed = await queue.get_failed_jobs()
    
    return {
        "pending": len(pending),
        "completed": len(completed),
        "failed": len(failed)
    }
```

### Django Integration

Django with async views (Django 4.1+):

```python
# jobs.py
from dbjobq import job

@job(max_retries=3)
def process_upload(data):
    """Process uploaded file (sync job function)."""
    from myapp.models import Upload
    file_id = data["file_id"]
    upload = Upload.objects.get(id=file_id)
    
    # Process file
    result = process_file(upload.file.path)
    
    # Update database
    upload.status = 'processed'
    upload.result = result
    upload.save()

# queue.py - Setup module
from dbjobq import JobQueue
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage
from asgiref.sync import async_to_sync

# Initialize storage (do this in Django app ready())
storage = SQLAlchemyStorage("postgresql+asyncpg://localhost/jobs")
async_to_sync(storage.initialize)()
queue = JobQueue(storage)

# views.py
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from .queue import queue
from .jobs import process_upload

async def upload_file(request):
    """Handle file upload with async view."""
    if request.method == 'POST':
        # Save file (sync Django ORM)
        from asgiref.sync import sync_to_async
        
        @sync_to_async
        def create_upload():
            from myapp.models import Upload
            return Upload.objects.create(
                file=request.FILES['file'],
                user=request.user
            )
        
        upload = await create_upload()
        
        # Enqueue processing (async)
        job_id = await queue.enqueue(process_upload, {"file_id": upload.id})
        
        return JsonResponse({
            'upload_id': upload.id,
            'job_id': job_id
        })

# management/commands/start_workers.py
import asyncio
from django.core.management.base import BaseCommand
from myapp.queue import queue
from dbjobq import Worker

class Command(BaseCommand):
    help = 'Start job queue workers'
    
    def add_arguments(self, parser):
        parser.add_argument('--workers', type=int, default=4)
    
    def handle(self, *args, **options):
        num_workers = options['workers']
        
        async def run():
            workers = []
            for i in range(num_workers):
                worker = Worker(queue)
                await worker.start()
                workers.append(worker)
            
            self.stdout.write(f'Started {num_workers} workers')
            
            # Keep alive
            await asyncio.Event().wait()
        
        asyncio.run(run())
```
        
        return JsonResponse({
            'upload_id': upload.id,
            'job_id': job_id
        })

# management/commands/start_workers.py
from django.core.management.base import BaseCommand
from myapp.queue import queue, Worker

class Command(BaseCommand):
    help = 'Start job queue workers'
    
    def add_arguments(self, parser):
        parser.add_argument('--workers', type=int, default=4)
    
    def handle(self, *args, **options):
        num_workers = options['workers']
        
        workers = []
        for i in range(num_workers):
            worker = Worker(queue)
            worker.start()
            workers.append(worker)
        
        self.stdout.write(f'Started {num_workers} workers')
        
        # Keep alive
        import signal
        signal.pause()
```

### Celery Migration

Migrate from Celery to DBJobQ:

```python
# Before (Celery)
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def process_data(self, data_id):
    try:
        # Process
        pass
    except Exception as e:
        raise self.retry(exc=e, countdown=60)

# After (DBJobQ)
from dbjobq import job

@job(max_retries=3)
def process_data(data_id: int):
    # Same logic, automatic retry with exponential backoff
    pass

# Replace task.delay() with queue.enqueue()
# Celery: process_data.delay(123)
# DBJobQ: queue.enqueue(process_data, data_id=123)
```

## Performance Optimization

### Batch Processing

Process multiple items in one job:

```python
@job
def batch_process_users(user_ids: list[int]):
    """Process multiple users in batch."""
    # More efficient than individual jobs
    for user_id in user_ids:
        process_user(user_id)

# Instead of:
for user_id in user_ids:
    queue.enqueue(process_user, user_id=user_id)

# Do:
queue.enqueue(batch_process_users, user_ids=user_ids)
```

### Connection Pooling

Optimize database connections:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://localhost/jobs",
    poolclass=QueuePool,
    pool_size=20,           # Based on worker count
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)

storage = SQLAlchemyStorage(engine)
```

### Job Chunking

Break large jobs into smaller chunks:

```python
@job
def process_large_dataset(offset: int, limit: int):
    """Process dataset chunk."""
    records = fetch_records(offset, limit)
    
    for record in records:
        process_record(record)
    
    # Enqueue next chunk
    if len(records) == limit:
        queue.enqueue(
            process_large_dataset,
            offset=offset + limit,
            limit=limit
        )

# Start processing
queue.enqueue(process_large_dataset, offset=0, limit=1000)
```

### Optimized Polling

Tune worker polling for your workload:

```python
# High-throughput: fast polling
worker = Worker(queue, poll_interval=0.1, max_poll_interval=1.0)

# Normal load: balanced
worker = Worker(queue, poll_interval=1.0, max_poll_interval=10.0)

# Low-traffic: slow polling
worker = Worker(queue, poll_interval=5.0, max_poll_interval=60.0)
```

This comprehensive documentation covers the main advanced use cases and patterns for DBJobQ!
