# Getting Started

This guide will help you get up and running with DBJobQ in minutes.

## Installation

Install DBJobQ using pip or uv:

=== "pip"
    ```bash
    pip install dbjobq
    ```

=== "uv"
    ```bash
    uv add dbjobq
    ```

### Optional Dependencies

DBJobQ supports multiple storage backends with async drivers. Install the one you need:

=== "SQLAlchemy (Async)"
    ```bash
    pip install dbjobq[sqlalchemy]
    # Includes: aiosqlite, asyncpg for async database operations
    ```

=== "MongoDB (Async)"
    ```bash
    pip install dbjobq[mongo]
    # Includes: pymongo with native async support
    ```

=== "Redis (Async)"
    ```bash
    pip install dbjobq[redis]
    # Includes: redis with async support and hiredis
    ```

=== "DynamoDB (Async)"
    ```bash
    pip install dbjobq[dynamo]
    # Includes: aioboto3 for async AWS operations
    ```

## Basic Usage

### 1. Set Up Storage

First, create an async storage backend. We'll use SQLite for simplicity:

```python
import asyncio
from dbjobq.storage import SQLAlchemyStorage

async def main():
    # Create storage with async SQLite
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    
    # For PostgreSQL (async)
    # storage = SQLAlchemyStorage("postgresql+asyncpg://user:pass@localhost/dbname")
    
    # For MySQL (async)
    # storage = SQLAlchemyStorage("mysql+aiomysql://user:pass@localhost/dbname")
    
    # Don't forget to close when done
    await storage.close()

asyncio.run(main())
```

The storage backend automatically creates the necessary tables when `initialize()` is called.

### 2. Create a Job Queue

```python
from dbjobq import JobQueue

queue = JobQueue(storage)
```

### 3. Define and Enqueue Jobs

Define jobs using the `@job` decorator and enqueue them asynchronously:

```python
from dbjobq import job, JobQueue

@job()
def send_welcome_email(data):
    """Send a welcome email to a new user."""
    user_email = data["user_email"]
    username = data["username"]
    print(f"Sending welcome email to {user_email} for {username}")

async def enqueue_jobs():
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)
    
    # Enqueue the job
    job_id = await queue.enqueue(send_welcome_email, {
        "user_email": "user@example.com",
        "username": "John Doe"
    })
    print(f"Enqueued job: {job_id}")
    
    await storage.close()

asyncio.run(enqueue_jobs())
```

#### Configure Jobs with Decorator

```python
@job(max_retries=3, priority=5)
def process_payment(data):
    """Process a payment for an order."""
    order_id = data["order_id"]
    amount = data["amount"]
    print(f"Processing payment of ${amount} for order {order_id}")

# Enqueue (decorator config is used by default)
await queue.enqueue(process_payment, {
    "order_id": 12345,
    "amount": 99.99
})

# Override decorator config if needed
await queue.enqueue(process_payment, {
    "order_id": 12345,
    "amount": 99.99
}, max_retries=5, priority=10)
```

### 4. Process Jobs with a Worker

Create and manage a worker asynchronously:

```python
import asyncio
from dbjobq import Worker

async def process_jobs():
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)
    
    # Create and start a worker
    worker = Worker(queue, poll_interval=1.0)
    await worker.start()
    
    # The worker runs in background tasks, processing jobs
    # Your main program continues here...
    print("Worker is running...")
    
    # Let it run for a while
    await asyncio.sleep(30)
    
    # When you're done, stop the worker gracefully
    await worker.stop()
    await storage.close()

asyncio.run(process_jobs())
```

#### Worker Lifecycle Control

Workers support full lifecycle management:

```python
# Start the worker
await worker.start()
print(f"Worker running: {worker.is_running()}")

# Pause job processing (schedules still poll)
worker.pause()
print(f"Worker paused: {worker.is_paused()}")

# Resume processing
worker.resume()
print(f"Worker resumed: {worker.is_paused()}")

# Graceful shutdown
await worker.stop()
```

## Common Patterns

### Job with Retries

Configure automatic retries for unreliable operations:

```python
@job(max_retries=5)
def fetch_external_data(data):
    """Fetch data from an external API."""
    import requests
    api_url = data["api_url"]
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()

async def enqueue_fetch():
    await queue.enqueue(fetch_external_data, {
        "api_url": "https://api.example.com/data"
    })

asyncio.run(enqueue_fetch())
```

If the job fails, it will automatically retry up to 5 times with exponential backoff:
- 1st retry: after 2 seconds
- 2nd retry: after 4 seconds  
- 3rd retry: after 8 seconds
- And so on...

### Priority Jobs

Process important jobs first:

```python
# Low priority - background cleanup
@job(priority=1)
def cleanup_old_files(data):
    """Remove temporary files."""
    pass

# Medium priority - normal operations
@job(priority=5)
def generate_report(data):
    """Generate a user report."""
    user_id = data["user_id"]
    # ... generate report ...

# High priority - critical operations
@job(priority=10)
def send_password_reset(data):
    """Send password reset email immediately."""
    email = data["email"]
    # ... send email ...

async def enqueue_jobs():
    # Enqueue all jobs
    await queue.enqueue(cleanup_old_files, {})
    await queue.enqueue(generate_report, {"user_id": 123})
    await queue.enqueue(send_password_reset, {"email": "user@example.com"})

    # Worker processes them in order: send_password_reset → generate_report → cleanup_old_files

asyncio.run(enqueue_jobs())
```

Higher priority values are processed first.

### Delayed Execution

Schedule jobs to run at a specific time:

```python
from datetime import datetime, timedelta

# Schedule a job for 1 hour from now
future_time = datetime.now() + timedelta(hours=1)

@job()
def send_reminder(data):
    """Send a reminder notification."""
    user_id = data["user_id"]
    message = data["message"]
    print(f"Reminder for user {user_id}: {message}")

async def schedule_reminder():
    await queue.enqueue(
        send_reminder,
        {
            "user_id": 456,
            "message": "Don't forget to complete your profile!"
        },
        execute_at=future_time
    )

asyncio.run(schedule_reminder())
```

The worker will automatically wait and process the job when `execute_at` is reached.

### Monitoring Job Status

Query your jobs directly from the database:

```python
async def monitor_jobs():
    # Get a specific job
    job = await queue.get_job("job-id-here")
    print(f"Status: {job.status}")
    print(f"Attempts: {job.attempts}")
    print(f"Error: {job.error}")

    # List pending jobs
    pending = await queue.get_pending_jobs()
    print(f"Pending jobs: {len(pending)}")

    # List completed jobs
    completed = await queue.get_completed_jobs(limit=10)
    print(f"Last 10 completed jobs: {len(completed)}")

    # List failed jobs
    failed = await queue.get_failed_jobs()
    for failed_job in failed:
        print(f"Failed: {failed_job.type} - {failed_job.error}")

asyncio.run(monitor_jobs())
```

## Complete Example

Here's a complete example putting it all together:

```python
import asyncio
from datetime import datetime, timedelta
from dbjobq import JobQueue, Worker, job
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

# 1. Define jobs
@job(max_retries=3, priority=10)
def send_notification(data):
    """Send a high-priority notification."""
    user_id = data["user_id"]
    message = data["message"]
    print(f"📧 Notification to user {user_id}: {message}")
    
@job(priority=5)
def process_analytics(data):
    """Process analytics data."""
    event_type = data["event_type"]
    event_data = data["data"]
    print(f"📊 Processing {event_type}: {event_data}")

@job(max_retries=1, priority=1)
def cleanup_temp_files(data):
    """Clean up temporary files."""
    print("🧹 Cleaning up temp files...")

async def main():
    # 2. Setup
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)

    # 3. Enqueue jobs
    await queue.enqueue(send_notification, {
        "user_id": 100,
        "message": "Welcome to our platform!"
    })

    await queue.enqueue(process_analytics, {
        "event_type": "user_signup",
        "data": {"user_id": 100, "source": "web"}
    })

    # Schedule cleanup for 5 seconds from now
    await queue.enqueue(
        cleanup_temp_files,
        {},
        execute_at=datetime.now() + timedelta(seconds=5)
    )

    # 4. Start worker
    worker = Worker(queue, poll_interval=0.5)
    await worker.start()

    print("🚀 Worker started, processing jobs...")

    # 5. Monitor progress
    await asyncio.sleep(2)
    pending = await queue.get_pending_jobs()
    print(f"📋 Pending jobs: {len(pending)}")

    # 6. Let worker process jobs
    await asyncio.sleep(5)

    # 7. Check results
    completed = await queue.get_completed_jobs()
    print(f"✅ Completed jobs: {len(completed)}")

    # 8. Cleanup
    await worker.stop()
    await storage.close()
    print("🛑 Worker stopped")

asyncio.run(main())
```

## Worker Configuration

### Single Worker

For simple applications:

```python
async def run_worker():
    worker = Worker(
        queue, 
        poll_interval=1.0,        # Check for jobs every 1 second
        max_poll_interval=60.0    # Max wait time when queue is empty
    )
    await worker.start()
    
    # Your app logic here
    await asyncio.sleep(3600)  # Run for 1 hour
    
    await worker.stop()

asyncio.run(run_worker())
```

### Multiple Workers

Scale horizontally by running multiple workers:

```python
# In process 1
async def worker1():
    worker = Worker(queue, poll_interval=1.0)
    await worker.start()
    await asyncio.Event().wait()  # Run forever

# In process 2  
async def worker2():
    worker = Worker(queue, poll_interval=1.0)
    await worker.start()
    await asyncio.Event().wait()

# In process 3
async def worker3():
    worker = Worker(queue, poll_interval=1.0)
    await worker.start()
    await asyncio.Event().wait()
```

Each worker will automatically coordinate through the database, ensuring jobs are processed exactly once.

### Adaptive Polling

Workers use adaptive polling to balance responsiveness and efficiency:

- When jobs are available: polls quickly (respects `poll_interval`)
- When queue is empty: gradually increases wait time (up to `max_poll_interval`)
- When new jobs arrive: immediately resets to fast polling

## Error Handling

### Automatic Retries

Jobs automatically retry on failure:

```python
@job(max_retries=3)
def unreliable_operation(data):
    """This job will retry up to 3 times if it fails."""
    # If this raises an exception, it will be retried
    raise Exception("Temporary failure")

async def enqueue_unreliable():
    await queue.enqueue(unreliable_operation, {})

asyncio.run(enqueue_unreliable())
```

### Manual Error Handling

You can also handle errors in your job:

```python
@job(max_retries=2)
def safe_operation(data):
    """Handle errors gracefully."""
    try:
        # Risky operation
        result = process_data(data)
        return result
    except ValueError as e:
        # Log and re-raise to trigger retry
        print(f"Validation error: {e}")
        raise
    except Exception as e:
        # Log but don't retry for unexpected errors
        print(f"Unexpected error: {e}")
        # Don't raise - job will complete (with error logged)
```

### Inspecting Failed Jobs

```python
async def inspect_failures():
    # Get all failed jobs
    failed_jobs = await queue.get_failed_jobs()

    for job in failed_jobs:
        print(f"Job {job.id} failed:")
        print(f"  Type: {job.type}")
        print(f"  Attempts: {job.attempts}/{job.max_retries}")
        print(f"  Error: {job.error}")
        print(f"  Data: {job.data}")

asyncio.run(inspect_failures())
```

## Best Practices

### 1. Keep Jobs Idempotent

Jobs may be retried, so design them to be safely repeatable:

```python
# Good - idempotent
@job()
def update_user_email(data):
    """Update email - safe to run multiple times."""
    user_id = data["user_id"]
    new_email = data["new_email"]
    user = db.get_user(user_id)
    if user.email != new_email:
        user.email = new_email
        db.save(user)

# Bad - not idempotent
@job()
def increment_counter(data):
    """Increment counter - running twice causes incorrect count."""
    user_id = data["user_id"]
    user = db.get_user(user_id)
    user.login_count += 1  # Problem if retried!
    db.save(user)
```

### 2. Use Appropriate Priorities

Reserve high priorities for truly critical operations:

- **Priority 10**: Critical (password resets, security alerts)
- **Priority 5**: Normal (emails, notifications, reports)
- **Priority 1**: Background (cleanup, analytics, maintenance)

### 3. Set Reasonable Retry Limits

Consider the nature of your job:

```python
# Network calls - more retries
@job(max_retries=5)
def call_external_api(data):
    pass

# Database operations - fewer retries  
@job(max_retries=2)
def update_database(data):
    pass

# One-time operations - no retries
@job(max_retries=0)
def one_shot_task(data):
    pass
```

### 4. Monitor Your Queue

Set up monitoring to track queue health:

```python
async def check_queue_health():
    """Monitor queue status."""
```python
async def check_queue_health():
    """Monitor queue status."""
    pending = len(await queue.get_pending_jobs())
    failed = len(await queue.get_failed_jobs())
    
    if pending > 1000:
        alert("Queue backlog is high!")
    
    if failed > 100:
        alert("Many failed jobs!")

asyncio.run(check_queue_health())
```

### 5. Clean Up Old Jobs

Periodically clean up completed jobs to keep your database tidy:

```python
@job(priority=1)
def cleanup_old_jobs(data):
    """Remove completed jobs older than 30 days."""
    cutoff = datetime.now() - timedelta(days=30)
    # Implement cleanup logic based on your storage
    pass

async def schedule_cleanup():
    # Schedule daily cleanup
    await queue.enqueue(
        cleanup_old_jobs,
        {},
        execute_at=datetime.now() + timedelta(days=1)
    )

asyncio.run(schedule_cleanup())
```

## Next Steps

Now that you understand the basics:

- **[API Reference](api/index.md)**: Explore the complete API documentation
- **[Schedules Guide](schedules.md)**: Learn about recurring jobs with cron and intervals
- **[Migration Guide](migration-guide.md)**: Upgrading from sync to async API
- **[Advanced Examples](examples.md)**: Learn advanced patterns and real-world use cases
- **[Storage Backends](api/storage.md)**: Configure different database backends
