# Job

The `Job` dataclass represents a unit of work in the queue with all associated metadata.

## Overview

A `Job` contains:

- **Identity**: Unique ID and job type
- **Payload**: JSON-serializable data to be processed
- **Status**: Current state (pending, running, completed, failed)
- **Configuration**: Retry limits, priority, and scheduling
- **Tracking**: Attempt count, errors, and timestamps

## Class Reference

::: dbjobq.models.Job
    options:
      show_root_heading: true
      show_source: true
      members:
        - __init__
        - from_dict

## Attributes

### id
- **Type**: `str`
- **Description**: Unique identifier for the job (UUID)
- **Example**: `"550e8400-e29b-41d4-a716-446655440000"`

### type
- **Type**: `str`
- **Description**: Job type, typically the function name
- **Example**: `"send_email"`, `"process_payment"`

### data
- **Type**: `dict[str, Any]`
- **Description**: JSON-serializable data passed to the job function
- **Example**: `{"user_id": 123, "amount": 99.99}`

### status
- **Type**: `str`
- **Description**: Current job status
- **Values**: `"pending"`, `"running"`, `"completed"`, `"failed"`
- **Default**: `"pending"`

### error
- **Type**: `str | None`
- **Description**: Error message if the job failed
- **Example**: `"ValueError: Invalid email address"`

### attempts
- **Type**: `int`
- **Description**: Number of times the job has been attempted
- **Default**: `0`

### max_retries
- **Type**: `int`
- **Description**: Maximum number of retry attempts
- **Default**: `3`

### priority
- **Type**: `int`
- **Description**: Job priority (higher values process first)
- **Default**: `5`
- **Range**: Typically 1-10, but any integer is valid

### execute_at
- **Type**: `datetime | None`
- **Description**: Scheduled execution time (None for immediate)
- **Example**: `datetime(2024, 10, 20, 15, 30, 0)`

### created_at
- **Type**: `datetime`
- **Description**: Timestamp when the job was created
- **Auto-generated**: Yes

### updated_at
- **Type**: `datetime`
- **Description**: Timestamp of last update
- **Auto-generated**: Yes

## Methods

### from_dict

Create a `Job` instance from a dictionary.

**Signature:**
```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> Job
```

**Parameters:**

- `data` (dict): Dictionary containing job data

**Returns:**

- `Job`: New Job instance

**Example:**

```python
from dbjobq.models import Job

# From dictionary with dict data
job = Job.from_dict({
    "id": "job-123",
    "type": "send_email",
    "data": {"to": "user@example.com"},
    "status": "pending"
})

# From dictionary with JSON string data
job = Job.from_dict({
    "id": "job-456",
    "type": "process_payment",
    "data": '{"order_id": 789, "amount": 99.99}',
    "status": "pending"
})
```

**Notes:**

- The `data` field can be either a dict or a JSON string
- Missing optional fields use their default values
- `created_at` and `updated_at` default to current time if not provided

## Usage Examples

### Creating a Job

```python
from datetime import datetime
from dbjobq.models import Job

# Minimal job
job = Job(
    id="job-1",
    type="send_email",
    data={"to": "user@example.com"}
)

# Job with all options
job = Job(
    id="job-2",
    type="process_payment",
    data={"order_id": 123, "amount": 99.99},
    status="pending",
    max_retries=5,
    priority=10,
    execute_at=datetime(2024, 10, 20, 15, 0, 0)
)
```

### Checking Job Status

```python
if job.status == "completed":
    print("Job finished successfully")
elif job.status == "failed":
    print(f"Job failed after {job.attempts} attempts: {job.error}")
elif job.status == "running":
    print(f"Job is currently being processed (attempt {job.attempts + 1})")
else:  # pending
    print("Job is waiting to be processed")
```

### Accessing Job Data

```python
job = Job(
    id="job-3",
    type="send_notification",
    data={
        "user_id": 456,
        "message": "Welcome!",
        "channels": ["email", "sms"]
    }
)

# Access data
user_id = job.data["user_id"]
message = job.data["message"]
channels = job.data["channels"]
```

### Serialization

```python
from dataclasses import asdict

# Convert to dictionary
job_dict = asdict(job)
print(job_dict)
# {
#     'id': 'job-3',
#     'type': 'send_notification',
#     'data': {'user_id': 456, 'message': 'Welcome!', ...},
#     'status': 'pending',
#     ...
# }

# Recreate from dictionary
restored_job = Job.from_dict(job_dict)
```

## Job Lifecycle States

```
┌─────────┐
│ PENDING │  Job is queued, waiting to be processed
└────┬────┘
     │ dequeue()
     ▼
┌─────────┐
│ RUNNING │  Worker has picked up the job
└────┬────┘
     │
     ├─────────────┬─────────────┐
     │             │             │
     │ success     │ failure     │ max retries exceeded
     ▼             ▼             ▼
┌───────────┐  ┌─────────┐  ┌────────┐
│ COMPLETED │  │ PENDING │  │ FAILED │
└───────────┘  └─────────┘  └────────┘
                   │ (with retry)
                   └─────────┘
```

## Notes

!!! tip "Immutability"
    `Job` is a dataclass. While you can modify its attributes, it's recommended to use `JobQueue` methods (`complete()`, `fail()`, `retry()`) to change job state to ensure consistency with the database.

!!! info "JSON Serialization"
    The `data` field must contain JSON-serializable values (strings, numbers, booleans, lists, dicts). Objects that can't be serialized to JSON will cause errors.

!!! warning "Manual Job Creation"
    Typically, you don't create `Job` instances directly. Use `JobQueue.enqueue()` to create and store jobs. The `Job` class is primarily used for reading job information.
