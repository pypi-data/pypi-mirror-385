# Storage

The storage layer provides persistence for jobs. DBJobQ includes a SQLAlchemy backend and defines an abstract interface for custom implementations.

## Overview

Storage backends handle:

- **Persistence**: Save and retrieve jobs
- **Concurrency**: Handle multiple workers safely
- **Querying**: Filter jobs by status and other criteria
- **Atomicity**: Ensure job state changes are atomic

## BaseStorage Interface

All storage backends must implement the `BaseStorage` abstract class.

::: dbjobq.storage.base.BaseStorage
    options:
      show_root_heading: true
      show_source: true

## SQLAlchemy Storage

The included SQLAlchemy backend supports PostgreSQL, MySQL, SQLite, and other SQLAlchemy-compatible databases.

::: dbjobq.storage.sqlalchemy_storage.SQLAlchemyStorage
    options:
      show_root_heading: true
      show_source: true

## SQLAlchemy Usage

### Basic Setup

```python
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

# SQLite (file-based)
storage = SQLAlchemyStorage("sqlite:///jobs.db")

# SQLite (in-memory, for testing)
storage = SQLAlchemyStorage("sqlite:///:memory:")

# PostgreSQL
storage = SQLAlchemyStorage(
    "postgresql://user:password@localhost:5432/mydb"
)

# MySQL
storage = SQLAlchemyStorage(
    "mysql+pymysql://user:password@localhost:3306/mydb"
)
```

### Connection Pooling

Configure connection pooling for production:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:pass@localhost/db",
    poolclass=QueuePool,
    pool_size=10,           # Number of connections to keep
    max_overflow=20,        # Additional connections when needed
    pool_timeout=30,        # Seconds to wait for connection
    pool_recycle=3600,      # Recycle connections after 1 hour
)

storage = SQLAlchemyStorage(engine)
```

### Database Schema

SQLAlchemyStorage automatically creates this table:

```sql
CREATE TABLE jobs (
    id VARCHAR PRIMARY KEY,
    type VARCHAR NOT NULL,
    data TEXT NOT NULL,           -- JSON string
    status VARCHAR NOT NULL,       -- pending, running, completed, failed
    error TEXT,
    attempts INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    priority INTEGER DEFAULT 5,
    execute_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_status_priority ON jobs(status, priority DESC);
CREATE INDEX idx_execute_at ON jobs(execute_at);
```

### Custom Engine Configuration

```python
from sqlalchemy import create_engine
from dbjobq.storage.sqlalchemy_storage import SQLAlchemyStorage

# Custom engine with options
engine = create_engine(
    "postgresql://localhost/jobs",
    echo=True,              # Log SQL queries
    pool_pre_ping=True,     # Verify connections
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    }
)

storage = SQLAlchemyStorage(engine)
```

## Implementing Custom Storage

You can implement custom storage backends for MongoDB, Redis, DynamoDB, etc.

### Storage Interface

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from dbjobq.models import Job

class BaseStorage(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def enqueue(
        self,
        job_id: str,
        job_type: str,
        data: dict,
        max_retries: int = 3,
        priority: int = 5,
        execute_at: Optional[datetime] = None
    ) -> None:
        """Add a job to storage."""
        pass
    
    @abstractmethod
    def dequeue(self) -> Optional[Job]:
        """Get next job to process. Must be atomic."""
        pass
    
    @abstractmethod
    def complete(self, job_id: str) -> None:
        """Mark job as completed."""
        pass
    
    @abstractmethod
    def fail(self, job_id: str, error: str) -> None:
        """Mark job as failed."""
        pass
    
    @abstractmethod
    def retry(self, job_id: str, delay_seconds: float) -> None:
        """Retry a failed job after delay."""
        pass
    
    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        pass
    
    @abstractmethod
    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[Job]:
        """List jobs with optional filtering."""
        pass
```

### Example: Redis Storage

```python
import json
import redis
from datetime import datetime, timedelta
from typing import Optional
from dbjobq.storage.base import BaseStorage
from dbjobq.models import Job

class RedisStorage(BaseStorage):
    """Redis-based job storage."""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    def enqueue(
        self,
        job_id: str,
        job_type: str,
        data: dict,
        max_retries: int = 3,
        priority: int = 5,
        execute_at: Optional[datetime] = None
    ) -> None:
        """Add job to Redis sorted set (priority queue)."""
        job_data = {
            "id": job_id,
            "type": job_type,
            "data": data,
            "status": "pending",
            "attempts": 0,
            "max_retries": max_retries,
            "priority": priority,
            "execute_at": execute_at.isoformat() if execute_at else None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Store job data
        self.redis.hset(f"job:{job_id}", mapping={
            k: json.dumps(v) for k, v in job_data.items()
        })
        
        # Add to priority queue (higher priority = lower score)
        score = -priority if not execute_at else execute_at.timestamp()
        self.redis.zadd("queue:pending", {job_id: score})
    
    def dequeue(self) -> Optional[Job]:
        """Atomically get next job from priority queue."""
        # Use Lua script for atomic dequeue
        lua_script = """
        local job_id = redis.call('ZPOPMIN', KEYS[1], 1)[1]
        if job_id then
            redis.call('ZADD', KEYS[2], ARGV[1], job_id)
            redis.call('HSET', 'job:' .. job_id, 'status', 'running')
            return job_id
        end
        return nil
        """
        
        script = self.redis.register_script(lua_script)
        job_id = script(
            keys=["queue:pending", "queue:running"],
            args=[datetime.now().timestamp()]
        )
        
        if not job_id:
            return None
        
        # Fetch job data
        job_data = self.redis.hgetall(f"job:{job_id}")
        return Job.from_dict({
            k.decode(): json.loads(v.decode())
            for k, v in job_data.items()
        })
    
    def complete(self, job_id: str) -> None:
        """Mark job as completed."""
        self.redis.zrem("queue:running", job_id)
        self.redis.hset(f"job:{job_id}", "status", "completed")
        self.redis.zadd("queue:completed", {
            job_id: datetime.now().timestamp()
        })
    
    def fail(self, job_id: str, error: str) -> None:
        """Mark job as failed."""
        self.redis.zrem("queue:running", job_id)
        self.redis.hset(f"job:{job_id}", mapping={
            "status": "failed",
            "error": error
        })
        self.redis.zadd("queue:failed", {
            job_id: datetime.now().timestamp()
        })
    
    def retry(self, job_id: str, delay_seconds: float) -> None:
        """Retry job after delay."""
        execute_at = datetime.now() + timedelta(seconds=delay_seconds)
        self.redis.zrem("queue:running", job_id)
        self.redis.hset(f"job:{job_id}", mapping={
            "status": "pending",
            "execute_at": execute_at.isoformat()
        })
        self.redis.zadd("queue:pending", {
            job_id: execute_at.timestamp()
        })
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        job_data = self.redis.hgetall(f"job:{job_id}")
        if not job_data:
            return None
        return Job.from_dict({
            k.decode(): json.loads(v.decode())
            for k, v in job_data.items()
        })
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[Job]:
        """List jobs by status."""
        if status:
            job_ids = self.redis.zrange(f"queue:{status}", 0, limit or -1)
        else:
            job_ids = []
            for queue in ["pending", "running", "completed", "failed"]:
                job_ids.extend(self.redis.zrange(f"queue:{queue}", 0, -1))
        
        jobs = []
        for job_id in job_ids:
            job = self.get_job(job_id.decode())
            if job:
                jobs.append(job)
        
        return jobs[:limit] if limit else jobs
```

### Example: MongoDB Storage

```python
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Optional
from dbjobq.storage.base import BaseStorage
from dbjobq.models import Job

class MongoStorage(BaseStorage):
    """MongoDB-based job storage."""
    
    def __init__(self, mongo_uri: str, database: str = "jobqueue"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        self.jobs = self.db.jobs
        
        # Create indexes
        self.jobs.create_index([
            ("status", 1),
            ("priority", -1),
            ("execute_at", 1)
        ])
    
    def enqueue(
        self,
        job_id: str,
        job_type: str,
        data: dict,
        max_retries: int = 3,
        priority: int = 5,
        execute_at: Optional[datetime] = None
    ) -> None:
        """Insert job into MongoDB."""
        self.jobs.insert_one({
            "_id": job_id,
            "type": job_type,
            "data": data,
            "status": "pending",
            "attempts": 0,
            "max_retries": max_retries,
            "priority": priority,
            "execute_at": execute_at,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        })
    
    def dequeue(self) -> Optional[Job]:
        """Atomically get and update next job."""
        job_doc = self.jobs.find_one_and_update(
            {
                "status": "pending",
                "$or": [
                    {"execute_at": None},
                    {"execute_at": {"$lte": datetime.now()}}
                ]
            },
            {"$set": {
                "status": "running",
                "updated_at": datetime.now()
            }},
            sort=[("priority", -1), ("created_at", 1)],
            return_document=True
        )
        
        if not job_doc:
            return None
        
        return self._doc_to_job(job_doc)
    
    def complete(self, job_id: str) -> None:
        """Mark job as completed."""
        self.jobs.update_one(
            {"_id": job_id},
            {"$set": {
                "status": "completed",
                "updated_at": datetime.now()
            }}
        )
    
    def fail(self, job_id: str, error: str) -> None:
        """Mark job as failed."""
        self.jobs.update_one(
            {"_id": job_id},
            {"$set": {
                "status": "failed",
                "error": error,
                "updated_at": datetime.now()
            }}
        )
    
    def retry(self, job_id: str, delay_seconds: float) -> None:
        """Retry job after delay."""
        self.jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "pending",
                    "execute_at": datetime.now() + timedelta(seconds=delay_seconds),
                    "updated_at": datetime.now()
                },
                "$inc": {"attempts": 1}
            }
        )
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        job_doc = self.jobs.find_one({"_id": job_id})
        return self._doc_to_job(job_doc) if job_doc else None
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[Job]:
        """List jobs with optional filtering."""
        query = {"status": status} if status else {}
        cursor = self.jobs.find(query).sort("created_at", -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return [self._doc_to_job(doc) for doc in cursor]
    
    def _doc_to_job(self, doc: dict) -> Job:
        """Convert MongoDB document to Job."""
        return Job(
            id=doc["_id"],
            type=doc["type"],
            data=doc["data"],
            status=doc["status"],
            error=doc.get("error"),
            attempts=doc["attempts"],
            max_retries=doc["max_retries"],
            priority=doc["priority"],
            execute_at=doc.get("execute_at"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )
```

## Storage Comparison

| Feature | SQLAlchemy | Redis | MongoDB | DynamoDB |
|---------|------------|-------|---------|----------|
| **ACID** | ✅ Full | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited |
| **Querying** | ✅ Rich | ⚠️ Basic | ✅ Rich | ⚠️ Basic |
| **Scalability** | ✅ Good | ✅✅ Excellent | ✅ Good | ✅✅ Excellent |
| **Persistence** | ✅ Disk | ⚠️ Memory+Disk | ✅ Disk | ✅ Managed |
| **Setup** | Easy | Easy | Easy | Complex |
| **Cost** | Low | Low | Low | Pay-per-use |

## Performance Considerations

### Indexing

Proper indexes are critical for performance:

```sql
-- Essential indexes for SQLAlchemy
CREATE INDEX idx_status_priority_execute 
ON jobs(status, priority DESC, execute_at);

-- For job lookup
CREATE INDEX idx_created_at ON jobs(created_at DESC);
```

### Connection Pooling

Configure pooling for multiple workers:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=10,      # Workers * 2 is a good start
    max_overflow=5
)
```

### Cleanup Strategy

Regularly clean up old jobs:

```python
def cleanup_old_jobs(storage, days=30):
    """Remove completed jobs older than X days."""
    cutoff = datetime.now() - timedelta(days=days)
    
    # SQLAlchemy example
    storage.session.query(Job).filter(
        Job.status == "completed",
        Job.updated_at < cutoff
    ).delete()
    storage.session.commit()
```

## Notes

!!! tip "Database Choice"
    For most use cases, PostgreSQL with SQLAlchemy provides the best balance of features, reliability, and performance.

!!! info "Atomicity"
    The `dequeue()` operation must be atomic to prevent multiple workers from processing the same job. Use database transactions or atomic operations.

!!! warning "Connection Management"
    Always use connection pooling in production. Create the storage instance once and share it across workers.

!!! danger "Data Consistency"
    Custom storage implementations must ensure jobs are processed exactly once, even with multiple workers and failures.
