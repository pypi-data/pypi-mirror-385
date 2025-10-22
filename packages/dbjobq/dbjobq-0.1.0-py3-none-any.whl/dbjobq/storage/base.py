from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..models import Job, Schedule


class BaseStorage(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def enqueue(
        self, job_type: str, job_data: str, priority: int = 0, max_retries: int = 0, execute_at: Optional[float] = None
    ) -> str:
        """Enqueue a job and return job_id.

        Args:
            job_type (str): The type of the job.
            job_data (str): The job data as a JSON string.
            priority (int): Job priority (higher = more important).
            max_retries (int): Maximum number of retry attempts.
            execute_at (Optional[float]): Unix timestamp when job should be executed.

        Returns:
            str: The unique job ID.
        """
        pass

    @abstractmethod
    async def dequeue(self) -> Optional["Job"]:
        """Dequeue a job, mark as running, return Job or None.

        Returns:
            Optional[Job]: The Job object or None if no job available.
        """
        pass

    @abstractmethod
    async def complete(self, job_id: str) -> None:
        """Mark job as completed.

        Args:
            job_id (str): The ID of the job to complete.
        """
        pass

    @abstractmethod
    async def fail(self, job_id: str, error: str) -> None:
        """Mark job as failed.

        Args:
            job_id (str): The ID of the job to fail.
            error (str): The error message.
        """
        pass

    @abstractmethod
    async def get_job(self, job_id: str) -> Optional["Job"]:
        """Get a job by ID.

        Args:
            job_id (str): The ID of the job to retrieve.

        Returns:
            Optional[Job]: The Job object or None if not found.
        """
        pass

    @abstractmethod
    async def list_jobs(self, status: Optional[str] = None, limit: Optional[int] = None) -> list["Job"]:
        """List jobs, optionally filtered by status.

        Args:
            status (Optional[str]): Filter by job status (pending, running, completed, failed).
            limit (Optional[int]): Maximum number of jobs to return.

        Returns:
            list[Job]: List of Job objects.
        """
        pass

    @abstractmethod
    async def retry_job(self, job_id: str, error: str, delay: float) -> None:
        """Mark job for retry with exponential backoff.

        Args:
            job_id (str): The ID of the job to retry.
            error (str): The error message from the failed attempt.
            delay (float): Delay in seconds before retry.
        """
        pass

    # Schedule management methods
    @abstractmethod
    async def create_schedule(self, schedule: "Schedule") -> None:
        """Create a recurring job schedule.

        Args:
            schedule (Schedule): The schedule object to create.
        """
        pass

    @abstractmethod
    async def get_due_schedules(self) -> list["Schedule"]:
        """Get all enabled schedules that are due to run.

        Returns:
            list[Schedule]: List of due schedules.
        """
        pass

    @abstractmethod
    async def update_schedule_next_run(self, schedule_id: str, next_run: float, last_run: float) -> None:
        """Update schedule after job execution.

        Args:
            schedule_id (str): The schedule ID.
            next_run (float): Unix timestamp of next run.
            last_run (float): Unix timestamp of last run.
        """
        pass

    @abstractmethod
    async def get_schedule(self, schedule_id: str) -> Optional["Schedule"]:
        """Get a schedule by ID.

        Args:
            schedule_id (str): The schedule ID.

        Returns:
            Optional[Schedule]: The Schedule object or None if not found.
        """
        pass

    @abstractmethod
    async def list_schedules(self, enabled_only: bool = False) -> list["Schedule"]:
        """List all schedules.

        Args:
            enabled_only (bool): If True, only return enabled schedules.

        Returns:
            list[Schedule]: List of Schedule objects.
        """
        pass

    @abstractmethod
    async def delete_schedule(self, schedule_id: str) -> None:
        """Delete a schedule.

        Args:
            schedule_id (str): The schedule ID.
        """
        pass

    @abstractmethod
    async def enable_schedule(self, schedule_id: str, enabled: bool) -> None:
        """Enable or disable a schedule.

        Args:
            schedule_id (str): The schedule ID.
            enabled (bool): Whether the schedule should be enabled.
        """
        pass
