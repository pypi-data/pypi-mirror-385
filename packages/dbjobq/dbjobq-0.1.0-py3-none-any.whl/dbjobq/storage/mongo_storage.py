import uuid
from datetime import datetime
from typing import Optional

from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from ..models import Job as JobModel
from ..models import Schedule as ScheduleModel
from .base import BaseStorage


class MongoStorage(BaseStorage):
    def __init__(
        self, mongo_url: str, db_name: str, jobs_collection: str = "jobs", schedules_collection: str = "schedules"
    ) -> None:
        """Initialize MongoDB storage with async support.

        Args:
            mongo_url (str): The MongoDB connection URL.
            db_name (str): The database name.
            jobs_collection (str): The collection name for jobs. Defaults to "jobs".
            schedules_collection (str): The collection name for schedules. Defaults to "schedules".
        """
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.jobs_collection_name = jobs_collection
        self.schedules_collection_name = schedules_collection
        self.client: Optional[AsyncMongoClient] = None
        self.jobs_collection: Optional[AsyncCollection] = None
        self.schedules_collection: Optional[AsyncCollection] = None

    async def initialize(self) -> None:
        """Initialize MongoDB connection and create indexes."""
        self.client = AsyncMongoClient(self.mongo_url)
        db = self.client[self.db_name]
        self.jobs_collection = db[self.jobs_collection_name]
        self.schedules_collection = db[self.schedules_collection_name]

        # Create indexes for efficient queries
        await self.jobs_collection.create_index([("status", 1), ("priority", -1), ("execute_at", 1)])
        await self.schedules_collection.create_index([("enabled", 1), ("next_run", 1)])

    async def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()

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
        await self.jobs_collection.insert_one(
            {
                "_id": job_id,
                "type": job_type,
                "data": job_data,
                "status": "pending",
                "priority": priority,
                "max_retries": max_retries,
                "attempts": 0,
                "execute_at": execute_at,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )
        return job_id

    async def dequeue(self) -> Optional[JobModel]:
        """Dequeue a pending job, mark it as running, and return it.

        Respects priority (higher first) and execute_at timing.

        Returns:
            Optional[JobModel]: The Job object or None if no job available.
        """
        current_time = datetime.now().timestamp()
        # Use find_one_and_update to atomically update status
        # Query: status=pending AND (execute_at is null OR execute_at <= now)
        # Sort: priority desc, created_at asc
        job = await self.jobs_collection.find_one_and_update(
            {"status": "pending", "$or": [{"execute_at": None}, {"execute_at": {"$lte": current_time}}]},
            {"$set": {"status": "running", "started_at": datetime.now(), "updated_at": datetime.now()}},
            sort=[("priority", -1), ("created_at", 1)],
            return_document=True,
        )
        if job:
            return JobModel.from_dict(
                {
                    "id": job["_id"],
                    "type": job["type"],
                    "data": job["data"],
                    "status": job["status"],
                    "priority": job.get("priority", 0),
                    "max_retries": job.get("max_retries", 0),
                    "attempts": job.get("attempts", 0),
                    "error": job.get("error"),
                    "execute_at": datetime.fromtimestamp(job["execute_at"]) if job.get("execute_at") else None,
                    "created_at": job.get("created_at"),
                    "updated_at": job.get("updated_at"),
                }
            )
        return None

    async def complete(self, job_id: str) -> None:
        """Mark a job as completed.

        Args:
            job_id (str): The ID of the job to complete.
        """
        await self.jobs_collection.update_one(
            {"_id": job_id},
            {"$set": {"status": "completed", "completed_at": datetime.now(), "updated_at": datetime.now()}},
        )

    async def fail(self, job_id: str, error: str) -> None:
        """Mark a job as failed with an error message.

        Args:
            job_id (str): The ID of the job to fail.
            error (str): The error message.
        """
        await self.jobs_collection.update_one(
            {"_id": job_id},
            {"$set": {"status": "failed", "error": error, "failed_at": datetime.now(), "updated_at": datetime.now()}},
        )

    async def get_job(self, job_id: str) -> Optional[JobModel]:
        """Get a job by ID.

        Args:
            job_id (str): The ID of the job to retrieve.

        Returns:
            Optional[JobModel]: The Job object or None if not found.
        """
        job = await self.jobs_collection.find_one({"_id": job_id})
        if job:
            return JobModel.from_dict(
                {
                    "id": job["_id"],
                    "type": job["type"],
                    "data": job["data"],
                    "status": job["status"],
                    "priority": job.get("priority", 0),
                    "max_retries": job.get("max_retries", 0),
                    "attempts": job.get("attempts", 0),
                    "error": job.get("error"),
                    "execute_at": datetime.fromtimestamp(job["execute_at"]) if job.get("execute_at") else None,
                    "created_at": job.get("created_at"),
                    "updated_at": job.get("updated_at"),
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
        query = {}
        if status:
            query["status"] = status

        cursor = self.jobs_collection.find(query)
        if limit:
            cursor = cursor.limit(limit)

        jobs = []
        async for job in cursor:
            jobs.append(
                JobModel.from_dict(
                    {
                        "id": job["_id"],
                        "type": job["type"],
                        "data": job["data"],
                        "status": job["status"],
                        "priority": job.get("priority", 0),
                        "max_retries": job.get("max_retries", 0),
                        "attempts": job.get("attempts", 0),
                        "error": job.get("error"),
                        "execute_at": datetime.fromtimestamp(job["execute_at"]) if job.get("execute_at") else None,
                        "created_at": job.get("created_at"),
                        "updated_at": job.get("updated_at"),
                    }
                )
            )
        return jobs

    async def retry_job(self, job_id: str, error: str, delay: float) -> None:
        """Mark job for retry with exponential backoff.

        Args:
            job_id (str): The ID of the job to retry.
            error (str): The error message from the failed attempt.
            delay (float): Delay in seconds before retry.
        """
        execute_at = datetime.now().timestamp() + delay
        await self.jobs_collection.update_one(
            {"_id": job_id},
            {
                "$set": {"status": "pending", "error": error, "execute_at": execute_at, "updated_at": datetime.now()},
                "$inc": {"attempts": 1},
            },
        )

    # Schedule management methods
    async def create_schedule(self, schedule: ScheduleModel) -> None:
        """Create a recurring job schedule.

        Args:
            schedule (ScheduleModel): The schedule object to create.
        """
        await self.schedules_collection.insert_one(
            {
                "_id": schedule.id,
                "job_type": schedule.job_type,
                "job_data": schedule.job_data,
                "schedule_type": schedule.schedule_type,
                "schedule_expression": schedule.schedule_expression,
                "next_run": schedule.next_run,
                "last_run": schedule.last_run,
                "enabled": schedule.enabled,
                "max_retries": schedule.max_retries,
                "priority": schedule.priority,
                "created_at": schedule.created_at or datetime.now(),
                "updated_at": schedule.updated_at or datetime.now(),
            }
        )

    async def get_due_schedules(self) -> list[ScheduleModel]:
        """Get all enabled schedules that are due to run.

        Returns:
            list[ScheduleModel]: List of due schedules.
        """
        now = datetime.now()
        cursor = self.schedules_collection.find({"enabled": True, "next_run": {"$lte": now}})

        schedules = []
        async for doc in cursor:
            schedules.append(
                ScheduleModel.from_dict(
                    {
                        "id": doc["_id"],
                        "job_type": doc["job_type"],
                        "job_data": doc["job_data"],
                        "schedule_type": doc["schedule_type"],
                        "schedule_expression": doc["schedule_expression"],
                        "next_run": doc["next_run"],
                        "last_run": doc.get("last_run"),
                        "enabled": doc["enabled"],
                        "max_retries": doc.get("max_retries", 0),
                        "priority": doc.get("priority", 0),
                        "created_at": doc.get("created_at"),
                        "updated_at": doc.get("updated_at"),
                    }
                )
            )
        return schedules

    async def update_schedule_next_run(self, schedule_id: str, next_run: float, last_run: float) -> None:
        """Update schedule after job execution.

        Args:
            schedule_id (str): The schedule ID.
            next_run (float): Unix timestamp of next run.
            last_run (float): Unix timestamp of last run.
        """
        await self.schedules_collection.update_one(
            {"_id": schedule_id},
            {
                "$set": {
                    "next_run": datetime.fromtimestamp(next_run),
                    "last_run": datetime.fromtimestamp(last_run),
                    "updated_at": datetime.now(),
                }
            },
        )

    async def get_schedule(self, schedule_id: str) -> Optional[ScheduleModel]:
        """Get a schedule by ID.

        Args:
            schedule_id (str): The schedule ID.

        Returns:
            Optional[ScheduleModel]: The Schedule object or None if not found.
        """
        doc = await self.schedules_collection.find_one({"_id": schedule_id})
        if doc:
            return ScheduleModel.from_dict(
                {
                    "id": doc["_id"],
                    "job_type": doc["job_type"],
                    "job_data": doc["job_data"],
                    "schedule_type": doc["schedule_type"],
                    "schedule_expression": doc["schedule_expression"],
                    "next_run": doc["next_run"],
                    "last_run": doc.get("last_run"),
                    "enabled": doc["enabled"],
                    "max_retries": doc.get("max_retries", 0),
                    "priority": doc.get("priority", 0),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at"),
                }
            )
        return None

    async def list_schedules(self, enabled_only: bool = False) -> list[ScheduleModel]:
        """List all schedules.

        Args:
            enabled_only (bool): If True, only return enabled schedules.

        Returns:
            list[ScheduleModel]: List of Schedule objects.
        """
        query = {}
        if enabled_only:
            query["enabled"] = True

        cursor = self.schedules_collection.find(query)
        schedules = []
        async for doc in cursor:
            schedules.append(
                ScheduleModel.from_dict(
                    {
                        "id": doc["_id"],
                        "job_type": doc["job_type"],
                        "job_data": doc["job_data"],
                        "schedule_type": doc["schedule_type"],
                        "schedule_expression": doc["schedule_expression"],
                        "next_run": doc["next_run"],
                        "last_run": doc.get("last_run"),
                        "enabled": doc["enabled"],
                        "max_retries": doc.get("max_retries", 0),
                        "priority": doc.get("priority", 0),
                        "created_at": doc.get("created_at"),
                        "updated_at": doc.get("updated_at"),
                    }
                )
            )
        return schedules

    async def delete_schedule(self, schedule_id: str) -> None:
        """Delete a schedule.

        Args:
            schedule_id (str): The schedule ID.
        """
        await self.schedules_collection.delete_one({"_id": schedule_id})

    async def enable_schedule(self, schedule_id: str, enabled: bool) -> None:
        """Enable or disable a schedule.

        Args:
            schedule_id (str): The schedule ID.
            enabled (bool): Whether the schedule should be enabled.
        """
        await self.schedules_collection.update_one(
            {"_id": schedule_id}, {"$set": {"enabled": enabled, "updated_at": datetime.now()}}
        )
