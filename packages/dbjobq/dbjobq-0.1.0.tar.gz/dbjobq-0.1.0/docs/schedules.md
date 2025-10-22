# Recurring Jobs with Schedules

DBJobQ supports recurring jobs through a powerful scheduling system that supports both cron expressions and interval-based schedules.

## Overview

Schedules allow you to automatically enqueue jobs at specific times or intervals without manual intervention. The worker automatically polls for due schedules and creates jobs when it's time to run them.

### Key Features

- **Cron Expressions**: Use standard cron syntax for complex schedules
- **Interval Schedules**: Simple interval-based scheduling in seconds
- **Automatic Execution**: Worker polls and executes schedules automatically
- **Enable/Disable**: Toggle schedules on/off without deletion
- **Priority & Retries**: Schedules inherit these settings to created jobs
- **Next Run Tracking**: Automatic calculation of next execution time

## Schedule Types

### Interval Schedules

Run a job every N seconds:

```python
import asyncio
import time
from dbjobq import JobQueue, Worker, job
from dbjobq.storage import SQLAlchemyStorage
from dbjobq.models import Schedule

@job()
def cleanup_temp_files(data):
    """Clean up temporary files."""
    print(f"Cleaning up: {data['target']}")

async def main():
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)
    
    # Create an interval schedule - runs every 5 minutes
    schedule = Schedule(
        id="cleanup-schedule",
        job_type="__main__.cleanup_temp_files",
        job_data={"target": "temp_files"},
        schedule_type="interval",
        schedule_expression="300",  # 300 seconds = 5 minutes
        next_run=time.time(),  # Start now
        enabled=True,
        priority=1,
        max_retries=2
    )
    
    await storage.create_schedule(schedule)
    
    # Start worker with schedule polling
    worker = Worker(queue, schedule_poll_interval=60.0)
    await worker.start()
    
    # Worker will automatically create jobs from the schedule
    await asyncio.sleep(600)  # Run for 10 minutes
    
    await worker.stop()
    await storage.close()

asyncio.run(main())
```

### Cron Schedules

Use familiar cron syntax for complex schedules:

```python
schedule = Schedule(
    id="daily-report",
    job_type="__main__.generate_daily_report",
    job_data={"report_type": "summary"},
    schedule_type="cron",
    schedule_expression="0 9 * * *",  # Every day at 9:00 AM
    next_run=time.time(),
    enabled=True
)

await storage.create_schedule(schedule)
```

#### Common Cron Expressions

| Expression | Description |
|-----------|-------------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour (at minute 0) |
| `0 0 * * *` | Daily at midnight |
| `0 9 * * *` | Daily at 9:00 AM |
| `0 0 * * 0` | Weekly on Sunday at midnight |
| `0 0 1 * *` | Monthly on the 1st at midnight |
| `*/15 * * * *` | Every 15 minutes |
| `0 9-17 * * 1-5` | Weekdays 9 AM to 5 PM (hourly) |

Cron format: `minute hour day month day_of_week`

- **minute**: 0-59
- **hour**: 0-23  
- **day**: 1-31
- **month**: 1-12
- **day_of_week**: 0-6 (0 = Sunday)

## Complete Example

Here's a complete example with multiple schedules:

```python
import asyncio
import time
from datetime import datetime
from dbjobq import JobQueue, Worker, job
from dbjobq.storage import SQLAlchemyStorage
from dbjobq.models import Schedule

# Define scheduled jobs
@job(priority=10)
def send_reminder_emails(data):
    """Send reminder emails to users."""
    print(f"Sending {data['count']} reminder emails")

@job(priority=5)
def generate_analytics(data):
    """Generate analytics reports."""
    print(f"Generating analytics for {data['period']}")

@job(priority=1)
def cleanup_old_data(data):
    """Clean up old data."""
    print(f"Cleaning up data older than {data['days']} days")

async def setup_schedules():
    storage = SQLAlchemyStorage("sqlite+aiosqlite:///jobs.db")
    await storage.initialize()
    queue = JobQueue(storage)
    
    # Schedule 1: Send reminders every hour
    reminder_schedule = Schedule(
        id="hourly-reminders",
        job_type="__main__.send_reminder_emails",
        job_data={"count": 100},
        schedule_type="cron",
        schedule_expression="0 * * * *",  # Every hour
        next_run=time.time(),
        enabled=True,
        priority=10,
        max_retries=3
    )
    
    # Schedule 2: Generate analytics every 6 hours
    analytics_schedule = Schedule(
        id="analytics-6h",
        job_type="__main__.generate_analytics",
        job_data={"period": "6h"},
        schedule_type="interval",
        schedule_expression="21600",  # 6 hours in seconds
        next_run=time.time(),
        enabled=True,
        priority=5,
        max_retries=2
    )
    
    # Schedule 3: Cleanup daily at 2 AM
    cleanup_schedule = Schedule(
        id="daily-cleanup",
        job_type="__main__.cleanup_old_data",
        job_data={"days": 30},
        schedule_type="cron",
        schedule_expression="0 2 * * *",  # 2 AM daily
        next_run=time.time(),
        enabled=True,
        priority=1,
        max_retries=1
    )
    
    # Create schedules
    await storage.create_schedule(reminder_schedule)
    await storage.create_schedule(analytics_schedule)
    await storage.create_schedule(cleanup_schedule)
    
    # Start worker with schedule polling every 60 seconds
    worker = Worker(
        queue,
        poll_interval=1.0,
        schedule_poll_interval=60.0
    )
    await worker.start()
    
    print("✅ Schedules created and worker started")
    print(f"  - Hourly reminders: {reminder_schedule.id}")
    print(f"  - Analytics (6h): {analytics_schedule.id}")
    print(f"  - Daily cleanup: {cleanup_schedule.id}")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
            
            # Check schedule status
            schedules = await storage.list_schedules(enabled_only=True)
            print(f"\nActive schedules: {len(schedules)}")
            for sched in schedules:
                next_time = datetime.fromtimestamp(sched.next_run)
                print(f"  - {sched.id}: next run at {next_time}")
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        await worker.stop()
        await storage.close()

asyncio.run(setup_schedules())
```

## Managing Schedules

### List All Schedules

```python
# Get all schedules
all_schedules = await storage.list_schedules()
print(f"Total schedules: {len(all_schedules)}")

# Get only enabled schedules
enabled_schedules = await storage.list_schedules(enabled_only=True)
print(f"Active schedules: {len(enabled_schedules)}")

for schedule in enabled_schedules:
    print(f"  ID: {schedule.id}")
    print(f"  Type: {schedule.schedule_type}")
    print(f"  Expression: {schedule.schedule_expression}")
    print(f"  Enabled: {schedule.enabled}")
```

### Get a Specific Schedule

```python
schedule = await storage.get_schedule("hourly-reminders")

if schedule:
    print(f"Schedule: {schedule.id}")
    print(f"Job Type: {schedule.job_type}")
    print(f"Next Run: {datetime.fromtimestamp(schedule.next_run)}")
    if schedule.last_run:
        print(f"Last Run: {datetime.fromtimestamp(schedule.last_run)}")
```

### Update Schedule Times

The worker automatically updates next_run and last_run, but you can manually update them:

```python
# Update next run to 1 hour from now
new_next_run = time.time() + 3600
await storage.update_schedule_next_run(
    "hourly-reminders",
    next_run=new_next_run,
    last_run=time.time()
)
```

### Enable/Disable Schedules

To temporarily disable a schedule without deleting it:

```python
# Get the schedule
schedule = await storage.get_schedule("daily-cleanup")

# Disable it
await storage.delete_schedule("daily-cleanup")
schedule.enabled = False
await storage.create_schedule(schedule)

# Later, re-enable it
schedule.enabled = True
await storage.create_schedule(schedule)
```

### Delete a Schedule

```python
await storage.delete_schedule("hourly-reminders")
print("Schedule deleted")
```

## How Schedules Work

### Polling Mechanism

The worker has a separate background task that periodically checks for due schedules:

```python
# Worker with custom schedule polling interval
worker = Worker(
    queue,
    poll_interval=1.0,           # Job polling interval
    schedule_poll_interval=60.0   # Schedule polling interval (60 seconds)
)
```

### Execution Flow

1. **Poll**: Worker checks for schedules where `next_run <= current_time` and `enabled=True`
2. **Create Job**: For each due schedule, a job is enqueued with the schedule's configuration
3. **Update Times**: Schedule's `next_run` and `last_run` are updated:
   - **Cron**: Uses croniter to calculate the next occurrence
   - **Interval**: Adds the interval seconds to the last run time

### Next Run Calculation

#### For Cron Schedules

DBJobQ uses `croniter` to parse cron expressions and calculate the next run:

```python
from croniter import croniter

# For expression "0 9 * * *" (9 AM daily)
cron = croniter("0 9 * * *", current_time)
next_run = cron.get_next()  # Next 9 AM
```

#### For Interval Schedules

Simple addition:

```python
# For interval of 300 seconds (5 minutes)
next_run = last_run + 300
```

## Best Practices

### 1. Choose Appropriate Poll Intervals

Balance responsiveness with resource usage:

```python
# For time-sensitive schedules (check every minute)
worker = Worker(queue, schedule_poll_interval=60.0)

# For less critical schedules (check every 5 minutes)
worker = Worker(queue, schedule_poll_interval=300.0)
```

### 2. Use Meaningful Schedule IDs

```python
# Good - descriptive and unique
schedule_id = "user-reminders-daily-9am"
schedule_id = "cleanup-logs-weekly"
schedule_id = "backup-db-hourly"

# Bad - unclear purpose
schedule_id = "schedule-1"
schedule_id = "job-a"
```

### 3. Set Appropriate Priorities

```python
# High priority - user-facing
Schedule(id="notifications", priority=10, ...)

# Medium priority - analytics
Schedule(id="analytics", priority=5, ...)

# Low priority - maintenance
Schedule(id="cleanup", priority=1, ...)
```

### 4. Handle Time Zones

Schedule times are in Unix timestamps (UTC). Convert to your timezone:

```python
from datetime import datetime, timezone
import pytz

# Create schedule in specific timezone
tz = pytz.timezone("America/New_York")
now_local = datetime.now(tz)
next_run_utc = now_local.astimezone(timezone.utc).timestamp()

schedule = Schedule(
    id="ny-schedule",
    ...
    next_run=next_run_utc,
    ...
)
```

### 5. Monitor Schedule Execution

```python
async def monitor_schedules():
    """Check if schedules are running as expected."""
    schedules = await storage.list_schedules(enabled_only=True)
    
    for schedule in schedules:
        # Check if schedule is overdue
        if schedule.next_run < time.time() - 300:  # 5 minutes overdue
            print(f"⚠️  Schedule {schedule.id} is overdue!")
        
        # Check last execution
        if schedule.last_run:
            time_since_last = time.time() - schedule.last_run
            print(f"Schedule {schedule.id} last ran {time_since_last}s ago")
```

### 6. Handle Schedule Failures

Jobs created from schedules can fail just like regular jobs:

```python
# Set max_retries on schedule for reliable execution
schedule = Schedule(
    id="critical-task",
    ...
    max_retries=5,  # Retry up to 5 times if job fails
    ...
)

# Monitor failed jobs from schedules
failed_jobs = await queue.get_failed_jobs()
for job in failed_jobs:
    if "schedule" in job.data:
        print(f"Scheduled job failed: {job.type}")
        print(f"  Error: {job.error}")
```

## Advanced Patterns

### Dynamic Schedule Updates

Update schedules based on system conditions:

```python
async def adjust_schedule_frequency():
    """Adjust schedule frequency based on load."""
    schedule = await storage.get_schedule("analytics")
    
    # Check system load
    pending_jobs = len(await queue.get_pending_jobs())
    
    if pending_jobs > 1000:
        # System busy - reduce frequency (12 hours)
        schedule.schedule_expression = "43200"
    else:
        # System idle - increase frequency (6 hours)
        schedule.schedule_expression = "21600"
    
    await storage.delete_schedule(schedule.id)
    await storage.create_schedule(schedule)
```

### Conditional Schedules

Enable/disable schedules based on business logic:

```python
async def toggle_business_hours_schedules():
    """Enable schedules only during business hours."""
    current_hour = datetime.now().hour
    
    # Business hours: 9 AM to 5 PM
    is_business_hours = 9 <= current_hour < 17
    
    schedule = await storage.get_schedule("business-reports")
    if schedule.enabled != is_business_hours:
        schedule.enabled = is_business_hours
        await storage.delete_schedule(schedule.id)
        await storage.create_schedule(schedule)
```

### Schedule Dependencies

Chain schedules by checking previous execution:

```python
@job()
def dependent_task(data):
    """Task that depends on another schedule completing."""
    parent_schedule_id = data["parent_schedule"]
    
    # Check if parent schedule ran recently
    parent = await storage.get_schedule(parent_schedule_id)
    if not parent.last_run or time.time() - parent.last_run > 3600:
        print("Parent schedule hasn't run recently, skipping")
        return
    
    # Proceed with dependent work
    print("Parent schedule completed, running dependent task")
```

## Troubleshooting

### Schedule Not Running

1. **Check if worker is polling schedules**:
   ```python
   # Ensure schedule_poll_interval is set
   worker = Worker(queue, schedule_poll_interval=60.0)
   ```

2. **Verify schedule is enabled**:
   ```python
   schedule = await storage.get_schedule("my-schedule")
   print(f"Enabled: {schedule.enabled}")
   ```

3. **Check next_run time**:
   ```python
   schedule = await storage.get_schedule("my-schedule")
   print(f"Next run: {datetime.fromtimestamp(schedule.next_run)}")
   print(f"Current time: {datetime.now()}")
   ```

### Jobs Not Being Created

1. **Check job_type is correct**:
   ```python
   # Must be fully qualified: "module.function_name"
   schedule.job_type = "__main__.my_task"  # ✅ Correct
   schedule.job_type = "my_task"           # ❌ Wrong
   ```

2. **Verify job is registered**:
   ```python
   from dbjobq.queue import _job_registry
   print("Registered jobs:", _job_registry.keys())
   ```

### Schedule Running Too Frequently

Check the schedule expression:

```python
# Interval schedules use seconds
schedule.schedule_expression = "3600"  # 1 hour, not 1 second

# Cron schedules: minute hour day month day_of_week
schedule.schedule_expression = "0 * * * *"  # Every hour
# Not: "* * * * *" which runs every minute
```

## Next Steps

- **[Getting Started](getting-started.md)**: Learn the basics of DBJobQ
- **[API Reference](api/storage.md)**: Storage backend API documentation (includes schedule methods)
- **[Examples](examples.md)**: More real-world scheduling examples
