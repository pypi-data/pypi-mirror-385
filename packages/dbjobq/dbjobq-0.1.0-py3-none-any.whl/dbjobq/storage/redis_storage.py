import json
import uuid
from datetime import datetime
from typing import Optional

from redis.asyncio import Redis

from ..models import Job as JobModel
from ..models import Schedule as ScheduleModel
from .base import BaseStorage


class RedisStorage(BaseStorage):
    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        """Initialize Redis storage with async support.

        Args:
            redis_url (str): The Redis connection URL. Defaults to "redis://localhost:6379/0".
        """
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        self.redis = Redis.from_url(self.redis_url, decode_responses=False)

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.aclose()

    async def enqueue(
        self, job_type: str, job_data: str, priority: int = 0, max_retries: int = 0, execute_at: Optional[float] = None
    ) -> str:
        """Enqueue a job and return the job ID.

        Args:
            job_type (str): The type of the job.
            job_data (str): The job data as a JSON string.
            priority (int): Job priority (higher = more important).
            max_retries (int): Maximum number of retry attempts.
            execute_at (Optional[float]): Unix timestamp when job should be executed.

        Returns:
            str: The unique job ID.
        """
        job_id = str(uuid.uuid4())
        job_key = f"job:{job_id}"
        await self.redis.hset(
            job_key,
            mapping={
                "type": job_type,
                "data": job_data,
                "status": "pending",
                "priority": str(priority),
                "max_retries": str(max_retries),
                "attempts": "0",
                "execute_at": str(execute_at) if execute_at else "",
                "created_at": str(datetime.now().timestamp()),
            },
        )
        # Add to pending sorted set (sorted by priority, then execute_at)
        score = -priority * 1e10 + (execute_at or datetime.now().timestamp())
        await self.redis.zadd("jobs:pending", {job_id: score})
        return job_id

    async def dequeue(self) -> Optional[JobModel]:
        """Dequeue a pending job, mark it as running, and return it.

        Respects priority (higher first) and execute_at timing.

        Returns:
            Optional[JobModel]: The Job object or None if no job available.
        """
        # Get jobs that are ready to execute
        current_time = datetime.now().timestamp()
        while True:
            # Get lowest score (highest priority, earliest execute_at)
            items = await self.redis.zrange("jobs:pending", 0, 0, withscores=True)
            if not items:
                return None

            job_id, _ = items[0]  # score not used
            job_id = job_id.decode() if isinstance(job_id, bytes) else job_id

            # Check if job is ready to execute
            job_key = f"job:{job_id}"
            job_data = await self.redis.hgetall(job_key)
            if not job_data:
                # Job was deleted, remove from pending
                await self.redis.zrem("jobs:pending", job_id)
                continue

            execute_at_str = (
                job_data.get(b"execute_at", b"").decode()
                if isinstance(job_data.get(b"execute_at"), bytes)
                else job_data.get("execute_at", "")
            )
            if execute_at_str and float(execute_at_str) > current_time:
                # Not ready yet
                return None

            # Try to atomically claim this job
            removed = await self.redis.zrem("jobs:pending", job_id)
            if removed == 0:
                # Someone else took it, try next
                continue

            # Mark as running
            await self.redis.hset(job_key, "status", "running")
            await self.redis.hset(job_key, "started_at", str(datetime.now().timestamp()))
            await self.redis.sadd("jobs:running", job_id)

            # Return Job object
            return JobModel.from_dict(
                {
                    "id": job_id,
                    "type": (
                        job_data.get(b"type", b"").decode()
                        if isinstance(job_data.get(b"type"), bytes)
                        else job_data.get("type", "")
                    ),
                    "data": (
                        job_data.get(b"data", b"").decode()
                        if isinstance(job_data.get(b"data"), bytes)
                        else job_data.get("data", "")
                    ),
                    "status": "running",
                    "priority": int(
                        (
                            job_data.get(b"priority", b"0").decode()
                            if isinstance(job_data.get(b"priority"), bytes)
                            else job_data.get("priority", "0")
                        )
                        or 0
                    ),
                    "max_retries": int(
                        (
                            job_data.get(b"max_retries", b"0").decode()
                            if isinstance(job_data.get(b"max_retries"), bytes)
                            else job_data.get("max_retries", "0")
                        )
                        or 0
                    ),
                    "attempts": int(
                        (
                            job_data.get(b"attempts", b"0").decode()
                            if isinstance(job_data.get(b"attempts"), bytes)
                            else job_data.get("attempts", "0")
                        )
                        or 0
                    ),
                    "execute_at": None if not execute_at_str else datetime.fromtimestamp(float(execute_at_str)),
                    "created_at": datetime.fromtimestamp(
                        float(
                            (
                                job_data.get(b"created_at", b"0").decode()
                                if isinstance(job_data.get(b"created_at"), bytes)
                                else job_data.get("created_at", "0")
                            )
                            or 0
                        )
                    ),
                }
            )

    async def complete(self, job_id: str) -> None:
        """Mark a job as completed.

        Args:
            job_id (str): The ID of the job to complete.
        """
        job_key = f"job:{job_id}"
        await self.redis.hset(job_key, "status", "completed")
        await self.redis.hset(job_key, "completed_at", str(datetime.now().timestamp()))
        await self.redis.srem("jobs:running", job_id)
        await self.redis.sadd("jobs:completed", job_id)

    async def fail(self, job_id: str, error: str) -> None:
        """Mark a job as failed with an error message.

        Args:
            job_id (str): The ID of the job to fail.
            error (str): The error message.
        """
        job_key = f"job:{job_id}"
        await self.redis.hset(job_key, mapping={"status": "failed", "error": error})
        await self.redis.hset(job_key, "failed_at", str(datetime.now().timestamp()))
        await self.redis.srem("jobs:running", job_id)
        await self.redis.sadd("jobs:failed", job_id)

    async def get_job(self, job_id: str) -> Optional[JobModel]:
        """Get a job by ID.

        Args:
            job_id (str): The ID of the job to retrieve.

        Returns:
            Optional[JobModel]: The Job object or None if not found.
        """
        job_key = f"job:{job_id}"
        job_data = await self.redis.hgetall(job_key)
        if job_data:
            execute_at_str = (
                job_data.get(b"execute_at", b"").decode()
                if isinstance(job_data.get(b"execute_at"), bytes)
                else job_data.get("execute_at", "")
            )
            created_at_str = (
                job_data.get(b"created_at", b"0").decode()
                if isinstance(job_data.get(b"created_at"), bytes)
                else job_data.get("created_at", "0")
            )
            return JobModel.from_dict(
                {
                    "id": job_id,
                    "type": (
                        job_data.get(b"type", b"").decode()
                        if isinstance(job_data.get(b"type"), bytes)
                        else job_data.get("type", "")
                    ),
                    "data": (
                        job_data.get(b"data", b"").decode()
                        if isinstance(job_data.get(b"data"), bytes)
                        else job_data.get("data", "")
                    ),
                    "status": (
                        job_data.get(b"status", b"").decode()
                        if isinstance(job_data.get(b"status"), bytes)
                        else job_data.get("status", "")
                    ),
                    "error": (
                        job_data.get(b"error", b"").decode()
                        if isinstance(job_data.get(b"error"), bytes)
                        else job_data.get("error")
                    )
                    or None,
                    "priority": int(
                        (
                            job_data.get(b"priority", b"0").decode()
                            if isinstance(job_data.get(b"priority"), bytes)
                            else job_data.get("priority", "0")
                        )
                        or 0
                    ),
                    "max_retries": int(
                        (
                            job_data.get(b"max_retries", b"0").decode()
                            if isinstance(job_data.get(b"max_retries"), bytes)
                            else job_data.get("max_retries", "0")
                        )
                        or 0
                    ),
                    "attempts": int(
                        (
                            job_data.get(b"attempts", b"0").decode()
                            if isinstance(job_data.get(b"attempts"), bytes)
                            else job_data.get("attempts", "0")
                        )
                        or 0
                    ),
                    "execute_at": None if not execute_at_str else datetime.fromtimestamp(float(execute_at_str)),
                    "created_at": datetime.fromtimestamp(float(created_at_str or 0)),
                }
            )
        return None

    async def list_jobs(self, status: Optional[str] = None, limit: Optional[int] = None) -> list[JobModel]:
        """List jobs, optionally filtered by status.

        Args:
            status (Optional[str]): Filter by job status (pending, running, completed, failed).
            limit (Optional[int]): Maximum number of jobs to return.

        Returns:
            list[JobModel]: List of Job objects.
        """
        if status == "pending":
            # Get from sorted set
            job_ids = await self.redis.zrange("jobs:pending", 0, (limit or 100) - 1)
        else:
            # Get from status sets
            status_sets = [f"jobs:{status}"] if status else ["jobs:running", "jobs:completed", "jobs:failed"]

            job_ids = set()
            for status_set in status_sets:
                members = await self.redis.smembers(status_set)
                job_ids.update(members)

        jobs = []
        for job_id in job_ids:
            if limit and len(jobs) >= limit:
                break
            job_id_str = job_id.decode() if isinstance(job_id, bytes) else job_id
            job = await self.get_job(job_id_str)
            if job:
                jobs.append(job)

        return jobs

    async def retry_job(self, job_id: str, error: str, delay: float) -> None:
        """Mark job for retry with exponential backoff.

        Args:
            job_id (str): The ID of the job to retry.
            error (str): The error message from the failed attempt.
            delay (float): Delay in seconds before retry.
        """
        job_key = f"job:{job_id}"
        job_data = await self.redis.hgetall(job_key)
        if not job_data:
            return

        attempts = int(
            (
                job_data.get(b"attempts", b"0").decode()
                if isinstance(job_data.get(b"attempts"), bytes)
                else job_data.get("attempts", "0")
            )
            or 0
        )
        priority = int(
            (
                job_data.get(b"priority", b"0").decode()
                if isinstance(job_data.get(b"priority"), bytes)
                else job_data.get("priority", "0")
            )
            or 0
        )

        # Update job
        execute_at = datetime.now().timestamp() + delay
        await self.redis.hset(
            job_key,
            mapping={
                "status": "pending",
                "error": error,
                "attempts": str(attempts + 1),
                "execute_at": str(execute_at),
            },
        )

        # Move from running to pending
        await self.redis.srem("jobs:running", job_id)
        score = -priority * 1e10 + execute_at
        await self.redis.zadd("jobs:pending", {job_id: score})

    # Schedule management methods
    async def create_schedule(self, schedule: ScheduleModel) -> None:
        """Create a recurring job schedule.

        Args:
            schedule (ScheduleModel): The schedule object to create.
        """
        schedule_key = f"schedule:{schedule.id}"
        await self.redis.hset(
            schedule_key,
            mapping={
                "job_type": schedule.job_type,
                "job_data": json.dumps(schedule.job_data),
                "schedule_type": schedule.schedule_type,
                "schedule_expression": schedule.schedule_expression,
                "next_run": str(schedule.next_run.timestamp()),
                "last_run": str(schedule.last_run.timestamp()) if schedule.last_run else "",
                "enabled": "1" if schedule.enabled else "0",
                "max_retries": str(schedule.max_retries),
                "priority": str(schedule.priority),
                "created_at": str(schedule.created_at.timestamp())
                if schedule.created_at
                else str(datetime.now().timestamp()),
            },
        )

        # Add to sorted set for efficient due schedule queries
        if schedule.enabled:
            await self.redis.zadd("schedules:next_run", {schedule.id: schedule.next_run.timestamp()})

    async def get_due_schedules(self) -> list[ScheduleModel]:
        """Get all enabled schedules that are due to run.

        Returns:
            list[ScheduleModel]: List of due schedules.
        """
        now = datetime.now().timestamp()
        # Get schedule IDs with next_run <= now
        schedule_ids = await self.redis.zrangebyscore("schedules:next_run", "-inf", now)

        schedules = []
        for schedule_id in schedule_ids:
            schedule_id_str = schedule_id.decode() if isinstance(schedule_id, bytes) else schedule_id
            schedule = await self.get_schedule(schedule_id_str)
            if schedule and schedule.enabled:
                schedules.append(schedule)

        return schedules

    async def update_schedule_next_run(self, schedule_id: str, next_run: float, last_run: float) -> None:
        """Update schedule after job execution.

        Args:
            schedule_id (str): The schedule ID.
            next_run (float): Unix timestamp of next run.
            last_run (float): Unix timestamp of last run.
        """
        schedule_key = f"schedule:{schedule_id}"
        await self.redis.hset(
            schedule_key,
            mapping={
                "next_run": str(next_run),
                "last_run": str(last_run),
            },
        )

        # Update sorted set
        await self.redis.zadd("schedules:next_run", {schedule_id: next_run})

    async def get_schedule(self, schedule_id: str) -> Optional[ScheduleModel]:
        """Get a schedule by ID.

        Args:
            schedule_id (str): The schedule ID.

        Returns:
            Optional[ScheduleModel]: The Schedule object or None if not found.
        """
        schedule_key = f"schedule:{schedule_id}"
        schedule_data = await self.redis.hgetall(schedule_key)
        if not schedule_data:
            return None

        last_run_str = (
            schedule_data.get(b"last_run", b"").decode()
            if isinstance(schedule_data.get(b"last_run"), bytes)
            else schedule_data.get("last_run", "")
        )
        created_at_str = (
            schedule_data.get(b"created_at", b"").decode()
            if isinstance(schedule_data.get(b"created_at"), bytes)
            else schedule_data.get("created_at", "")
        )

        return ScheduleModel.from_dict(
            {
                "id": schedule_id,
                "job_type": (
                    schedule_data.get(b"job_type", b"").decode()
                    if isinstance(schedule_data.get(b"job_type"), bytes)
                    else schedule_data.get("job_type", "")
                ),
                "job_data": json.loads(
                    schedule_data.get(b"job_data", b"{}").decode()
                    if isinstance(schedule_data.get(b"job_data"), bytes)
                    else schedule_data.get("job_data", "{}")
                ),
                "schedule_type": (
                    schedule_data.get(b"schedule_type", b"").decode()
                    if isinstance(schedule_data.get(b"schedule_type"), bytes)
                    else schedule_data.get("schedule_type", "")
                ),
                "schedule_expression": (
                    schedule_data.get(b"schedule_expression", b"").decode()
                    if isinstance(schedule_data.get(b"schedule_expression"), bytes)
                    else schedule_data.get("schedule_expression", "")
                ),
                "next_run": datetime.fromtimestamp(
                    float(
                        schedule_data.get(b"next_run", b"0").decode()
                        if isinstance(schedule_data.get(b"next_run"), bytes)
                        else schedule_data.get("next_run", "0")
                    )
                ),
                "last_run": datetime.fromtimestamp(float(last_run_str)) if last_run_str else None,
                "enabled": (
                    schedule_data.get(b"enabled", b"1").decode()
                    if isinstance(schedule_data.get(b"enabled"), bytes)
                    else schedule_data.get("enabled", "1")
                )
                == "1",
                "max_retries": int(
                    (
                        schedule_data.get(b"max_retries", b"0").decode()
                        if isinstance(schedule_data.get(b"max_retries"), bytes)
                        else schedule_data.get("max_retries", "0")
                    )
                    or 0
                ),
                "priority": int(
                    (
                        schedule_data.get(b"priority", b"0").decode()
                        if isinstance(schedule_data.get(b"priority"), bytes)
                        else schedule_data.get("priority", "0")
                    )
                    or 0
                ),
                "created_at": datetime.fromtimestamp(float(created_at_str)) if created_at_str else None,
            }
        )

    async def list_schedules(self, enabled_only: bool = False) -> list[ScheduleModel]:
        """List all schedules.

        Args:
            enabled_only (bool): If True, only return enabled schedules.

        Returns:
            list[ScheduleModel]: List of Schedule objects.
        """
        if enabled_only:
            # Get from sorted set
            schedule_ids = await self.redis.zrange("schedules:next_run", 0, -1)
        else:
            # Scan for all schedule keys
            schedule_ids = []
            async for key in self.redis.scan_iter(match="schedule:*"):
                schedule_id = (key.decode() if isinstance(key, bytes) else key).replace("schedule:", "")
                schedule_ids.append(schedule_id)

        schedules = []
        for schedule_id in schedule_ids:
            schedule_id_str = schedule_id.decode() if isinstance(schedule_id, bytes) else schedule_id
            schedule = await self.get_schedule(schedule_id_str)
            if schedule and (not enabled_only or schedule.enabled):
                schedules.append(schedule)

        return schedules

    async def delete_schedule(self, schedule_id: str) -> None:
        """Delete a schedule.

        Args:
            schedule_id (str): The schedule ID.
        """
        schedule_key = f"schedule:{schedule_id}"
        await self.redis.delete(schedule_key)
        await self.redis.zrem("schedules:next_run", schedule_id)

    async def enable_schedule(self, schedule_id: str, enabled: bool) -> None:
        """Enable or disable a schedule.

        Args:
            schedule_id (str): The schedule ID.
            enabled (bool): Whether the schedule should be enabled.
        """
        schedule_key = f"schedule:{schedule_id}"
        await self.redis.hset(schedule_key, "enabled", "1" if enabled else "0")

        if enabled:
            # Add to sorted set
            schedule = await self.get_schedule(schedule_id)
            if schedule:
                await self.redis.zadd("schedules:next_run", {schedule_id: schedule.next_run.timestamp()})
        else:
            # Remove from sorted set
            await self.redis.zrem("schedules:next_run", schedule_id)
