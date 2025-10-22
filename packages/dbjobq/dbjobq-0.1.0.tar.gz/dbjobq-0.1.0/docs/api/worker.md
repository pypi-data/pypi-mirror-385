# Worker

The `Worker` class processes jobs from the queue in a background thread with adaptive polling and graceful shutdown.

## Overview

`Worker` provides:

- **Background Processing**: Runs in a separate thread, non-blocking
- **Adaptive Polling**: Adjusts polling frequency based on queue activity
- **Graceful Shutdown**: Waits for current job to complete before stopping
- **Error Handling**: Automatically handles job failures and retries
- **Job Tracking**: Exposes currently processing job for monitoring

## Class Reference

::: dbjobq.worker.Worker
    options:
      show_root_heading: true
      show_source: true

## Constructor

### \_\_init\_\_

```python
def __init__(
    self,
    job_queue: JobQueue,
    poll_interval: float = 1.0,
    max_poll_interval: float = 10.0
)
```

Create a new Worker instance.

**Parameters:**

- `job_queue` (JobQueue): The job queue to process
- `poll_interval` (float): Initial polling interval in seconds (default: 1.0)
- `max_poll_interval` (float): Maximum polling interval when idle (default: 10.0)

**Example:**

```python
from dbjobq import Worker, JobQueue
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

storage = SQLAlchemyStorage("sqlite:///jobs.db")
queue = JobQueue(storage)

# Fast polling for high-throughput
worker = Worker(queue, poll_interval=0.5, max_poll_interval=5.0)

# Slower polling for low-traffic queues
worker = Worker(queue, poll_interval=2.0, max_poll_interval=60.0)
```

## Methods

### start

Start the worker in a background thread.

```python
def start(self) -> None
```

**Raises:**

- `RuntimeError`: If worker is already running

**Example:**

```python
worker = Worker(queue)
worker.start()
print("Worker is now processing jobs in the background")

# Your application continues running...
```

**Behavior:**

- Starts a new daemon thread
- Thread continuously polls for jobs
- Non-blocking (returns immediately)
- Can be called only once per worker instance

### stop

Stop the worker gracefully.

```python
def stop(self) -> None
```

**Example:**

```python
worker.start()
# ... application runs ...
worker.stop()  # Blocks until current job completes
print("Worker stopped")
```

**Behavior:**

- Sets stop flag for the worker thread
- Waits for current job to complete (if any)
- Blocks until worker thread exits
- Safe to call multiple times (subsequent calls are no-ops)
- Timeout: Waits up to 30 seconds for graceful shutdown

### run

Main worker loop (internal method, called by start()).

```python
def run(self) -> None
```

!!! warning "Internal Method"
    This method is called automatically by `start()`. You should not call it directly.

## Properties

### current_job

Get the job currently being processed.

```python
@property
def current_job(self) -> Job | None
```

**Returns:**

- `Job | None`: Currently processing job, or None if idle

**Example:**

```python
worker.start()

# Monitor from another thread
import time
while True:
    job = worker.current_job
    if job:
        print(f"Processing: {job.type} (attempt {job.attempts + 1})")
    else:
        print("Worker is idle")
    time.sleep(5)
```

## Adaptive Polling

Workers use adaptive polling to balance responsiveness and resource usage:

### How It Works

1. **Active State** (jobs available):
   - Polls at `poll_interval` frequency
   - Minimal delay between jobs
   - Maximum throughput

2. **Idle State** (queue empty):
   - Gradually increases polling interval
   - Reduces CPU and database load
   - Up to `max_poll_interval`

3. **Recovery** (new job found):
   - Immediately resets to `poll_interval`
   - Fast response to new jobs

### Example Behavior

```python
# Worker with poll_interval=1.0, max_poll_interval=60.0
worker = Worker(queue, poll_interval=1.0, max_poll_interval=60.0)
worker.start()

# Timeline:
# t=0s: Check queue (job found) → process → wait 1s
# t=1s: Check queue (job found) → process → wait 1s
# t=2s: Check queue (empty) → wait 2s
# t=4s: Check queue (empty) → wait 4s
# t=8s: Check queue (empty) → wait 8s
# t=16s: Check queue (empty) → wait 16s
# t=32s: Check queue (empty) → wait 32s
# t=64s: Check queue (empty) → wait 60s (capped at max)
# t=124s: Check queue (job found) → process → wait 1s (reset)
```

## Usage Patterns

### Single Worker

Simple setup for moderate workloads:

```python
from dbjobq import Worker, JobQueue
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

storage = SQLAlchemyStorage("sqlite:///jobs.db")
queue = JobQueue(storage)

worker = Worker(queue, poll_interval=1.0)
worker.start()

# Application continues...
# Worker processes jobs in background

# Cleanup on exit
worker.stop()
```

### Multiple Workers (Horizontal Scaling)

Scale by running multiple workers:

```python
# Start multiple workers in same process
workers = []
for i in range(4):
    worker = Worker(queue, poll_interval=1.0)
    worker.start()
    workers.append(worker)
    print(f"Started worker {i+1}")

# Or run separate processes/containers
# Each process starts its own worker(s)

# Cleanup
for worker in workers:
    worker.stop()
```

**Benefits:**

- Increased throughput
- Parallel job processing
- Database handles coordination
- No job duplication

### Context Manager Pattern

Use worker with context manager for automatic cleanup:

```python
class WorkerContext:
    def __init__(self, queue, **kwargs):
        self.worker = Worker(queue, **kwargs)
    
    def __enter__(self):
        self.worker.start()
        return self.worker
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.worker.stop()

# Usage
with WorkerContext(queue) as worker:
    # Worker is running
    # Do other work...
    pass
# Worker is automatically stopped
```

### Monitoring Worker Status

```python
import time
from datetime import datetime

worker = Worker(queue)
worker.start()

def monitor_worker():
    """Monitor worker activity."""
    while True:
        job = worker.current_job
        if job:
            elapsed = datetime.now() - job.updated_at
            print(f"[{datetime.now()}] Processing: {job.type}")
            print(f"  Job ID: {job.id}")
            print(f"  Attempt: {job.attempts + 1}/{job.max_retries}")
            print(f"  Elapsed: {elapsed.total_seconds():.1f}s")
        else:
            pending = len(queue.get_pending_jobs())
            print(f"[{datetime.now()}] Idle (queue: {pending})")
        
        time.sleep(5)

# Run in separate thread
import threading
monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
monitor_thread.start()
```

### Graceful Application Shutdown

```python
import signal
import sys

worker = Worker(queue)
worker.start()

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    print("\nShutting down gracefully...")
    worker.stop()
    print("Worker stopped")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill

print("Worker running. Press Ctrl+C to stop.")

# Keep main thread alive
signal.pause()
```

### Worker with Health Checks

```python
from datetime import datetime, timedelta

class HealthMonitor:
    def __init__(self, worker, queue):
        self.worker = worker
        self.queue = queue
        self.last_job_time = datetime.now()
    
    def check_health(self):
        """Check if worker is healthy."""
        # Check if worker thread is alive
        if not hasattr(self.worker, '_worker_thread'):
            return False, "Worker not started"
        
        if not self.worker._worker_thread.is_alive():
            return False, "Worker thread died"
        
        # Check if jobs are being processed
        current_job = self.worker.current_job
        if current_job:
            self.last_job_time = datetime.now()
        
        # Alert if idle too long with pending jobs
        idle_time = datetime.now() - self.last_job_time
        pending = len(self.queue.get_pending_jobs())
        
        if pending > 0 and idle_time > timedelta(minutes=5):
            return False, f"Worker idle for {idle_time} with {pending} pending jobs"
        
        return True, "Healthy"

# Usage
monitor = HealthMonitor(worker, queue)
healthy, status = monitor.check_health()
if not healthy:
    alert(f"Worker unhealthy: {status}")
```

## Configuration Guidelines

### Poll Interval Selection

Choose based on your requirements:

| Use Case | poll_interval | max_poll_interval | Reason |
|----------|---------------|-------------------|---------|
| **High Throughput** | 0.1 - 0.5s | 1.0 - 5.0s | Fast response, many jobs |
| **Normal Load** | 1.0 - 2.0s | 10.0 - 30.0s | Balanced |
| **Low Traffic** | 5.0 - 10.0s | 60.0 - 120.0s | Reduce overhead |
| **Real-time** | 0.1 - 0.5s | 0.5 - 1.0s | Minimal latency |

### Worker Count

Determine workers based on:

- **CPU-bound jobs**: Workers ≈ CPU cores
- **I/O-bound jobs**: Workers > CPU cores (2-4x)
- **Database capacity**: Don't overwhelm database
- **Job duration**: Longer jobs = more workers

**Example:**

```python
import os

# CPU-bound jobs
num_workers = os.cpu_count()

# I/O-bound jobs
num_workers = os.cpu_count() * 2

# Start workers
workers = [Worker(queue) for _ in range(num_workers)]
for worker in workers:
    worker.start()
```

## Error Handling

### Worker Thread Exceptions

If a job raises an exception:

1. Worker catches it
2. Calls `queue.fail(job.id, error)`
3. Job is retried (if attempts < max_retries)
4. Worker continues processing next job

**The worker never crashes due to job errors.**

### Worker Crash Recovery

If the worker thread crashes unexpectedly:

```python
def start_worker_with_restart():
    """Start worker with automatic restart on crash."""
    while True:
        try:
            worker = Worker(queue)
            worker.start()
            
            # Monitor worker thread
            while worker._worker_thread.is_alive():
                time.sleep(1)
            
            print("Worker thread died, restarting...")
        except Exception as e:
            print(f"Worker error: {e}, restarting in 5s...")
            time.sleep(5)
```

## Performance Tips

1. **Adjust Polling**: Match `poll_interval` to job frequency
2. **Scale Horizontally**: Add workers before increasing poll frequency
3. **Database Pooling**: Use connection pooling for multiple workers
4. **Job Size**: Keep jobs small and focused
5. **Monitor**: Track `current_job` and queue metrics

## Notes

!!! tip "Daemon Thread"
    Worker runs as a daemon thread, which means it won't prevent your application from exiting. Always call `stop()` for graceful shutdown.

!!! info "Thread Safety"
    Worker is thread-safe. Multiple workers can process jobs from the same queue concurrently.

!!! warning "Resource Cleanup"
    Always call `stop()` before your application exits to ensure jobs complete and resources are freed.

!!! danger "Starting Multiple Times"
    Calling `start()` on an already running worker raises `RuntimeError`. Create a new worker instance if needed.
