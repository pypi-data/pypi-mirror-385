import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from ..models import Job as JobModel
from ..models import Schedule as ScheduleModel
from .base import BaseStorage

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    data = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, running, completed, failed
    error = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    attempts = Column(Integer, default=0)
    max_retries = Column(Integer, default=0)
    priority = Column(Integer, default=0)
    execute_at = Column(Float)  # Unix timestamp


class Schedule(Base):
    """SQLAlchemy model for schedules."""

    __tablename__ = "schedules"
    id = Column(String, primary_key=True)
    job_type = Column(String, nullable=False)
    job_data = Column(Text, nullable=False)  # JSON string
    schedule_type = Column(String, nullable=False)  # "cron" or "interval"
    schedule_expression = Column(String, nullable=False)
    next_run = Column(DateTime, nullable=False)
    last_run = Column(DateTime)
    enabled = Column(Boolean, nullable=False, default=True)
    max_retries = Column(Integer, default=0)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SQLAlchemyStorage(BaseStorage):
    def __init__(self, db_url: str = "sqlite+aiosqlite:///jobs.db") -> None:
        """Initialize SQLAlchemy storage.

        Args:
            db_url (str): Database URL (must use async driver: sqlite+aiosqlite:// or postgresql+asyncpg://).
        """
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session_maker = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def initialize(self) -> None:
        """Create database tables if they don't exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Close the database connection."""
        await self.engine.dispose()

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
        async with self.async_session_maker() as session:
            job = Job(
                id=job_id,
                type=job_type,
                data=job_data,
                priority=priority,
                max_retries=max_retries,
                execute_at=execute_at,
            )
            session.add(job)
            await session.commit()
        return job_id

    async def dequeue(self) -> Optional[JobModel]:
        """Dequeue a pending job, mark it as running, and return it.

        Respects priority (higher first) and execute_at timing.

        Returns:
            Optional[JobModel]: The Job object or None if no job available.
        """
        async with self.async_session_maker() as session:
            current_time = datetime.now().timestamp()
            stmt = (
                select(Job)
                .filter(Job.status == "pending")
                .filter((Job.execute_at.is_(None)) | (Job.execute_at <= current_time))
                .order_by(Job.priority.desc(), Job.created_at)
                .with_for_update(skip_locked=True)
                .limit(1)
            )
            result = await session.execute(stmt)
            job = result.scalar_one_or_none()
            if job:
                job.status = "running"
                # Access all attributes before committing to avoid lazy loading after detach
                job_dict = {
                    "id": job.id,
                    "type": job.type,
                    "data": job.data,
                    "status": job.status,
                    "created_at": job.created_at,
                    "updated_at": job.updated_at,
                    "error": job.error,
                    "attempts": job.attempts,
                    "max_retries": job.max_retries,
                    "priority": job.priority,
                    "execute_at": job.execute_at,
                }
                await session.commit()
                return JobModel.from_dict(job_dict)
        return None

    async def complete(self, job_id: str) -> None:
        """Mark a job as completed.

        Args:
            job_id (str): The ID of the job to complete.
        """
        async with self.async_session_maker() as session:
            stmt = select(Job).filter(Job.id == job_id)
            result = await session.execute(stmt)
            job = result.scalar_one_or_none()
            if job:
                job.status = "completed"
                await session.commit()

    async def fail(self, job_id: str, error: str) -> None:
        """Mark a job as failed with an error message.

        Args:
            job_id (str): The ID of the job to fail.
            error (str): The error message.
        """
        async with self.async_session_maker() as session:
            stmt = select(Job).filter(Job.id == job_id)
            result = await session.execute(stmt)
            job = result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error = error
                await session.commit()

    async def get_job(self, job_id: str) -> Optional[JobModel]:
        """Get a job by ID.

        Args:
            job_id (str): The ID of the job to retrieve.

        Returns:
            Optional[JobModel]: The Job object or None if not found.
        """
        async with self.async_session_maker() as session:
            stmt = select(Job).filter(Job.id == job_id)
            result = await session.execute(stmt)
            job = result.scalar_one_or_none()
            if job:
                return JobModel.from_dict(
                    {
                        "id": job.id,
                        "type": job.type,
                        "data": job.data,
                        "status": job.status,
                        "error": job.error,
                        "created_at": job.created_at,
                        "updated_at": job.updated_at,
                        "attempts": job.attempts,
                        "max_retries": job.max_retries,
                        "priority": job.priority,
                        "execute_at": job.execute_at,
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
        async with self.async_session_maker() as session:
            stmt = select(Job)
            if status:
                stmt = stmt.filter(Job.status == status)
            if limit:
                stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            jobs = result.scalars().all()
            return [
                JobModel.from_dict(
                    {
                        "id": job.id,
                        "type": job.type,
                        "data": job.data,
                        "status": job.status,
                        "error": job.error,
                        "created_at": job.created_at,
                        "updated_at": job.updated_at,
                        "attempts": job.attempts,
                        "max_retries": job.max_retries,
                        "priority": job.priority,
                        "execute_at": job.execute_at,
                    }
                )
                for job in jobs
            ]

    async def retry_job(self, job_id: str, error: str, delay: float) -> None:
        """Mark job for retry with exponential backoff.

        Args:
            job_id (str): The ID of the job to retry.
            error (str): The error message from the failed attempt.
            delay (float): Delay in seconds before retry.
        """
        async with self.async_session_maker() as session:
            stmt = select(Job).filter(Job.id == job_id)
            result = await session.execute(stmt)
            job = result.scalar_one_or_none()
            if job:
                job.status = "pending"
                job.attempts += 1
                job.error = error
                job.execute_at = datetime.now().timestamp() + delay
                await session.commit()

    async def create_schedule(self, schedule: ScheduleModel) -> None:
        """Create a new schedule.

        Args:
            schedule: Schedule object to create.
        """
        async with self.async_session_maker() as session:
            db_schedule = Schedule(
                id=schedule.id,
                job_type=schedule.job_type,
                job_data=json.dumps(schedule.job_data),
                schedule_type=schedule.schedule_type,
                schedule_expression=schedule.schedule_expression,
                next_run=datetime.fromtimestamp(schedule.next_run) if schedule.next_run else None,
                last_run=datetime.fromtimestamp(schedule.last_run) if schedule.last_run else None,
                enabled=schedule.enabled,
                max_retries=schedule.max_retries,
                priority=schedule.priority,
            )
            session.add(db_schedule)
            await session.commit()

    async def get_due_schedules(self) -> list[ScheduleModel]:
        """Get all enabled schedules that are due to run.

        Returns:
            list[ScheduleModel]: List of due schedules.
        """
        async with self.async_session_maker() as session:
            now = datetime.now()
            stmt = select(Schedule).filter(Schedule.enabled.is_(True)).filter(Schedule.next_run <= now)
            result = await session.execute(stmt)
            schedules = result.scalars().all()
            return [
                ScheduleModel.from_dict(
                    {
                        "id": s.id,
                        "job_type": s.job_type,
                        "job_data": json.loads(s.job_data),
                        "schedule_type": s.schedule_type,
                        "schedule_expression": s.schedule_expression,
                        "next_run": s.next_run.timestamp() if s.next_run else None,
                        "last_run": s.last_run.timestamp() if s.last_run else None,
                        "enabled": s.enabled,
                        "max_retries": s.max_retries,
                        "priority": s.priority,
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                    }
                )
                for s in schedules
            ]

    async def update_schedule_next_run(self, schedule_id: str, next_run: float, last_run: float) -> None:
        """Update schedule's next_run and last_run times.

        Args:
            schedule_id: ID of the schedule to update.
            next_run: Next execution time (Unix timestamp).
            last_run: Last execution time (Unix timestamp).
        """
        async with self.async_session_maker() as session:
            stmt = select(Schedule).filter(Schedule.id == schedule_id)
            result = await session.execute(stmt)
            schedule = result.scalar_one_or_none()
            if schedule:
                schedule.next_run = datetime.fromtimestamp(next_run) if next_run else None
                schedule.last_run = datetime.fromtimestamp(last_run) if last_run else None
                await session.commit()

    async def get_schedule(self, schedule_id: str) -> Optional[ScheduleModel]:
        """Get a schedule by ID.

        Args:
            schedule_id: ID of the schedule to retrieve.

        Returns:
            Optional[ScheduleModel]: Schedule object or None if not found.
        """
        async with self.async_session_maker() as session:
            stmt = select(Schedule).filter(Schedule.id == schedule_id)
            result = await session.execute(stmt)
            s = result.scalar_one_or_none()
            if s:
                return ScheduleModel.from_dict(
                    {
                        "id": s.id,
                        "job_type": s.job_type,
                        "job_data": json.loads(s.job_data),
                        "schedule_type": s.schedule_type,
                        "schedule_expression": s.schedule_expression,
                        "next_run": s.next_run.timestamp() if s.next_run else None,
                        "last_run": s.last_run.timestamp() if s.last_run else None,
                        "enabled": s.enabled,
                        "max_retries": s.max_retries,
                        "priority": s.priority,
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                    }
                )
        return None

    async def list_schedules(self, enabled_only: bool = False) -> list[ScheduleModel]:
        """List all schedules.

        Args:
            enabled_only: If True, only return enabled schedules.

        Returns:
            list[ScheduleModel]: List of schedules.
        """
        async with self.async_session_maker() as session:
            stmt = select(Schedule)
            if enabled_only:
                stmt = stmt.filter(Schedule.enabled.is_(True))
            result = await session.execute(stmt)
            schedules = result.scalars().all()
            return [
                ScheduleModel.from_dict(
                    {
                        "id": s.id,
                        "job_type": s.job_type,
                        "job_data": json.loads(s.job_data),
                        "schedule_type": s.schedule_type,
                        "schedule_expression": s.schedule_expression,
                        "next_run": s.next_run.timestamp() if s.next_run else None,
                        "last_run": s.last_run.timestamp() if s.last_run else None,
                        "enabled": s.enabled,
                        "max_retries": s.max_retries,
                        "priority": s.priority,
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                    }
                )
                for s in schedules
            ]

    async def delete_schedule(self, schedule_id: str) -> None:
        """Delete a schedule.

        Args:
            schedule_id: ID of the schedule to delete.
        """
        async with self.async_session_maker() as session:
            stmt = select(Schedule).filter(Schedule.id == schedule_id)
            result = await session.execute(stmt)
            schedule = result.scalar_one_or_none()
            if schedule:
                await session.delete(schedule)
                await session.commit()

    async def enable_schedule(self, schedule_id: str, enabled: bool) -> None:
        """Enable or disable a schedule.

        Args:
            schedule_id: ID of the schedule.
            enabled: True to enable, False to disable.
        """
        async with self.async_session_maker() as session:
            stmt = select(Schedule).filter(Schedule.id == schedule_id)
            result = await session.execute(stmt)
            schedule = result.scalar_one_or_none()
            if schedule:
                schedule.enabled = enabled
                await session.commit()
