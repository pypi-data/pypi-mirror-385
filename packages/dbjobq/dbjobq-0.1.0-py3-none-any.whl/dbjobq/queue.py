"""Job queue implementation."""

import importlib
import inspect
import json
import traceback
from datetime import datetime
from typing import Any, Callable, Optional

from .models import Job
from .storage.base import BaseStorage

_job_registry: dict[str, Callable] = {}
_job_config: dict[str, dict[str, Any]] = {}


def job(max_retries: int = 0, priority: int = 0) -> Callable:
    """Decorator to register a job function with configuration.

    Args:
        max_retries (int): Maximum number of retry attempts. Defaults to 0.
        priority (int): Job priority (higher = more important). Defaults to 0.

    Returns:
        Callable: A decorator function.
    """

    def decorator(func: Callable) -> Callable:
        job_key = func.__module__ + "." + func.__name__
        _job_registry[job_key] = func
        _job_config[job_key] = {"max_retries": max_retries, "priority": priority}
        return func

    return decorator


class JobQueue:
    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    async def enqueue(
        self,
        job_func: str | Callable,
        job_data: dict[str, Any],
        delay: Optional[float] = None,
        priority: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> str:
        """Enqueue a job.

        Args:
            job_func (str | Callable): The job function or its type string (module.function).
            job_data (dict[str, Any]): The data to pass to the job function.
            delay (Optional[float]): Delay in seconds before the job can be executed.
            priority (Optional[int]): Job priority (overrides decorator default).
            max_retries (Optional[int]): Max retry attempts (overrides decorator default).

        Returns:
            str: The unique job ID.
        """
        job_type = f"{job_func.__module__}.{job_func.__name__}" if callable(job_func) else job_func

        # Get config from decorator or use provided values
        config = _job_config.get(job_type, {})
        final_priority = priority if priority is not None else config.get("priority", 0)
        final_max_retries = max_retries if max_retries is not None else config.get("max_retries", 0)

        # Calculate execute_at if delay specified
        execute_at = None
        if delay:
            execute_at = datetime.now().timestamp() + delay

        return await self.storage.enqueue(
            job_type,
            json.dumps(job_data),
            priority=final_priority,
            max_retries=final_max_retries,
            execute_at=execute_at,
        )

    async def dequeue(self) -> Optional[Job]:
        """Dequeue a job.

        Returns:
            Optional[Job]: The Job object or None if no job available.
        """
        return await self.storage.dequeue()

    async def complete(self, job_id: str) -> None:
        """Mark job as completed.

        Args:
            job_id (str): The ID of the job to complete.
        """
        await self.storage.complete(job_id)

    async def fail(self, job_id: str, error: str) -> None:
        """Mark job as failed.

        Args:
            job_id (str): The ID of the job to fail.
            error (str): The error message.
        """
        await self.storage.fail(job_id, error)

    async def execute_job(self, job: Job) -> None:
        """Execute a job with retry logic. Supports both sync and async job functions.

        Args:
            job (Job): The Job object to execute.
        """
        job_type = job.type
        if job_type not in _job_registry:
            # Try to import
            module_name, func_name = job_type.rsplit(".", 1)
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)
            _job_registry[job_type] = func
        func = _job_registry[job_type]
        try:
            # Check if function is async or sync
            if inspect.iscoroutinefunction(func):
                # Async function - await it
                await func(job.data)
            else:
                # Sync function - call directly
                func(job.data)
            await self.complete(job.id)
        except Exception as e:
            # Check if we should retry
            if job.attempts < job.max_retries:
                # Retry the job with exponential backoff
                delay = 2**job.attempts  # 1s, 2s, 4s, 8s...
                await self.storage.retry_job(job.id, str(e), delay)
            else:
                # Max retries reached, mark as failed
                error_details = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
                await self.fail(job.id, error_details)

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID.

        Args:
            job_id (str): The ID of the job to retrieve.

        Returns:
            Optional[Job]: The Job object or None if not found.
        """
        return await self.storage.get_job(job_id)

    async def list_jobs(self, status: Optional[str] = None, limit: Optional[int] = None) -> list[Job]:
        """List jobs, optionally filtered by status.

        Args:
            status (Optional[str]): Filter by job status (pending, running, completed, failed).
            limit (Optional[int]): Maximum number of jobs to return.

        Returns:
            list[Job]: List of Job objects.
        """
        return await self.storage.list_jobs(status, limit)

    async def get_pending_jobs(self, limit: Optional[int] = None) -> list[Job]:
        """Get all pending jobs.

        Args:
            limit (Optional[int]): Maximum number of jobs to return.

        Returns:
            list[Job]: List of pending Job objects.
        """
        return await self.list_jobs(status="pending", limit=limit)

    async def get_running_jobs(self, limit: Optional[int] = None) -> list[Job]:
        """Get all running jobs.

        Args:
            limit (Optional[int]): Maximum number of jobs to return.

        Returns:
            list[Job]: List of running Job objects.
        """
        return await self.list_jobs(status="running", limit=limit)

    async def get_completed_jobs(self, limit: Optional[int] = None) -> list[Job]:
        """Get all completed jobs.

        Args:
            limit (Optional[int]): Maximum number of jobs to return.

        Returns:
            list[Job]: List of completed Job objects.
        """
        return await self.list_jobs(status="completed", limit=limit)

    async def get_failed_jobs(self, limit: Optional[int] = None) -> list[Job]:
        """Get all failed jobs.

        Args:
            limit (Optional[int]): Maximum number of jobs to return.

        Returns:
            list[Job]: List of failed Job objects.
        """
        return await self.list_jobs(status="failed", limit=limit)
