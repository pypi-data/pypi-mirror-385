# DBJobQ

**A simple, production-ready, database-backed job queue for Python.**

DBJobQ provides a reliable and scalable way to manage background jobs using your database as the queue backend. Built with simplicity and reliability in mind, it offers production-ready features without the complexity of heavyweight message brokers.

## Why DBJobQ?

### Simple Yet Powerful

DBJobQ gives you enterprise-grade job queue functionality with minimal setup. If you already have a database, you already have a job queue.

```python
import asyncio
from dbjobq import JobQueue, Worker, job
from dbjobq.storage import SQLAlchemyStorage

# Define a job
@job()
async def send_email(data):
    """Send an email asynchronously."""
    to, subject, body = data["to"], data["subject"], data["body"]
    # Your async email logic here
    print(f"Sending email to {to}")

async def main():
    # Setup storage and queue
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)
    
    # Enqueue a job
    await queue.enqueue(send_email, {
        "to": "user@example.com",
        "subject": "Hello",
        "body": "Welcome!"
    })
    
    # Process jobs with a worker
    worker = Worker(queue)
    await worker.start()
    
    # ... your app runs ...
    
    # Graceful shutdown
    await worker.stop()
    await storage.close()

asyncio.run(main())
```

### Key Features

- **⚡ Async/Await Support**: Built on modern Python async/await for high concurrency
- **📅 Recurring Jobs**: Cron and interval-based schedules with automatic execution
- **🔄 Automatic Retries**: Jobs automatically retry with exponential backoff on failure
- **⚙️ Worker Lifecycle**: Full control with start/stop/pause/resume functionality
- **🔢 Priority Queues**: Process important jobs first with configurable priorities
- **⏰ Delayed Execution**: Schedule jobs to run at specific times in the future
- **🧵 Multi-Worker Support**: Scale horizontally with multiple workers processing jobs concurrently
- **📊 Job Tracking**: Monitor job status, attempts, and errors through your database
- **🔌 Pluggable Storage**: SQLAlchemy, MongoDB, Redis, and DynamoDB backends included
- **🛡️ Production Ready**: Built-in error handling, graceful shutdown, and structured logging
- **🎯 Type Safe**: Full type hints for better IDE support and fewer bugs

## Architecture Overview

DBJobQ follows a simple but robust architecture:

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   Your App  │─────▶│   JobQueue   │─────▶│   Database   │
└─────────────┘      └──────────────┘      └──────────────┘
                             │                       │
                             │                       │
                             ▼                       ▼
                      ┌──────────────┐      ┌──────────────┐
                      │    Worker    │◀─────│   Dequeue    │
                      └──────────────┘      └──────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │  Execute Job │
                      └──────────────┘
```

### Components

- **Job**: A unit of work with metadata (priority, retries, schedule)
- **JobQueue**: Manages job lifecycle (enqueue, dequeue, complete, fail, retry)
- **Storage**: Abstract interface for different database backends
- **Worker**: Processes jobs from the queue with adaptive polling

### Job Lifecycle

1. **Pending**: Job is enqueued and waiting to be processed
2. **Running**: Worker has dequeued the job and is executing it
3. **Completed**: Job executed successfully
4. **Failed**: Job failed after exhausting all retry attempts

## When to Use DBJobQ

### Perfect For

✅ **Background Jobs**: Email sending, report generation, data processing  
✅ **Scheduled Tasks**: Periodic cleanup, notifications, data synchronization  
✅ **Asynchronous Operations**: Long-running tasks that shouldn't block requests  
✅ **Reliable Processing**: Tasks that must not be lost (database persistence)  
✅ **Simple Setup**: Projects that want job queues without extra infrastructure  

### Consider Alternatives If

❌ **Extreme Throughput**: Processing millions of jobs per second (consider RabbitMQ, Kafka)  
❌ **Complex Workflows**: Multi-stage pipelines with branching (consider Airflow, Prefect)  
❌ **Real-time Streaming**: Sub-second latency requirements (consider Redis Streams)  

## Performance Characteristics

- **Throughput**: Hundreds to thousands of jobs per second (database-dependent)
- **Latency**: Sub-second to few seconds (based on polling interval)
- **Scalability**: Horizontal scaling via multiple workers
- **Reliability**: ACID guarantees from your database
- **Overhead**: Minimal - just database operations

## Comparison with Alternatives

| Feature | DBJobQ | Celery | RQ | Dramatiq |
|---------|--------|--------|-----|----------|
| **Backend Required** | Database only | Redis/RabbitMQ | Redis | Redis/RabbitMQ |
| **Setup Complexity** | Low | Medium | Low | Medium |
| **Job Persistence** | Yes (DB) | Depends | Depends | Depends |
| **Retries** | Built-in | Built-in | Basic | Built-in |
| **Priority Queues** | Yes | Yes | Limited | Yes |
| **Delayed Jobs** | Yes | Yes | No | Yes |
| **Learning Curve** | Gentle | Steep | Gentle | Medium |
| **Dependencies** | Minimal | Many | Few | Few |

## Design Philosophy

DBJobQ is built on these principles:

1. **Simplicity First**: Clear, straightforward API that does what you expect
2. **Database as Source of Truth**: Leverage ACID guarantees you already have
3. **Fail-Safe Defaults**: Sensible defaults that work for most use cases
4. **Easy to Debug**: Jobs are just rows in your database - query them directly
5. **Extensible**: Clean abstractions for adding storage backends or custom behavior

## Quick Example

Here's a complete example showing the power of DBJobQ:

```python
import asyncio
from datetime import datetime, timedelta
from dbjobq import JobQueue, Worker, job
from dbjobq.storage import SQLAlchemyStorage
from dbjobq.models import Schedule

# Setup storage
storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")

async def main():
    await storage.initialize()
    queue = JobQueue(storage)

    # Define jobs with configuration
    @job(max_retries=3, priority=10)
    def critical_task(data):
        """This job will retry up to 3 times and process before normal jobs."""
        print(f"Processing critical: {data['message']}")

    @job(max_retries=1, priority=5)
    def normal_task(data):
        """Standard priority job."""
        print(f"Processing normal: {data['message']}")

    # Enqueue immediate jobs
    await queue.enqueue(critical_task, {"message": "Important data"})
    await queue.enqueue(normal_task, {"message": "Regular data"})

    # Schedule a delayed job
    await queue.enqueue(
        normal_task, 
        {"message": "Future data"}, 
        delay=3600  # 1 hour from now
    )

    # Create a recurring schedule (every 5 minutes)
    schedule = Schedule(
        id="cleanup-task",
        job_type="__main__.cleanup_task",
        job_data={"target": "temp_files"},
        schedule_type="interval",
        schedule_expression="300",  # 300 seconds = 5 minutes
        next_run=datetime.now().timestamp(),
        enabled=True,
        priority=1
    )
    await storage.create_schedule(schedule)

    # Start worker with schedule polling
    worker = Worker(queue, poll_interval=1.0, schedule_poll_interval=60.0)
    await worker.start()

    # Worker runs in background, processing jobs as they come
    # - Jobs are automatically retried on failure with exponential backoff
    # - Higher priority jobs (critical_task) process first
    # - Delayed jobs wait until their execution time
    # - Scheduled jobs run automatically at their intervals
    
    # Pause/resume worker dynamically
    worker.pause()
    print("Worker paused")
    await asyncio.sleep(2)
    worker.resume()
    print("Worker resumed")

    # Graceful shutdown
    await asyncio.sleep(10)
    await worker.stop()
    await storage.close()

asyncio.run(main())
```

## Next Steps

- **[Getting Started](getting-started.md)**: Step-by-step guide to using DBJobQ with async/await
- **[Schedules Guide](schedules.md)**: Learn about recurring jobs with cron and interval schedules
- **[Migration Guide](migration-guide.md)**: Upgrading from sync to async
- **[API Reference](api/index.md)**: Complete API documentation
- **[Advanced Examples](examples.md)**: Real-world usage patterns and recipes

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

MIT License - feel free to use DBJobQ in your projects.
