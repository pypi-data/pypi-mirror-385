"""Job dataclass and related models."""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class Job:
    """Represents a job in the queue."""

    id: str
    type: str
    data: dict[str, Any]
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    error: Optional[str] = None
    attempts: int = 0
    max_retries: int = 0
    priority: int = 0
    execute_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        """Create a Job instance from a dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing job data.

        Returns:
            Job: A Job instance.
        """
        # Handle data field which might be JSON string or dict
        job_data = data.get("data", {})
        if isinstance(job_data, str):
            job_data = json.loads(job_data)

        return cls(
            id=data["id"],
            type=data["type"],
            data=job_data,
            status=data["status"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            error=data.get("error"),
            attempts=data.get("attempts", 0),
            max_retries=data.get("max_retries", 0),
            priority=data.get("priority", 0),
            execute_at=data.get("execute_at"),
        )


@dataclass
class Schedule:
    """Represents a recurring job schedule."""

    id: str
    job_type: str
    job_data: dict[str, Any]
    schedule_type: str  # "cron" or "interval"
    schedule_expression: str  # Cron expression or interval in seconds
    next_run: datetime
    last_run: Optional[datetime] = None
    enabled: bool = True
    max_retries: int = 0
    priority: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Schedule":
        """Create a Schedule instance from a dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing schedule data.

        Returns:
            Schedule: A Schedule instance.
        """
        # Handle job_data field which might be JSON string or dict
        job_data = data.get("job_data", {})
        if isinstance(job_data, str):
            job_data = json.loads(job_data)

        return cls(
            id=data["id"],
            job_type=data["job_type"],
            job_data=job_data,
            schedule_type=data["schedule_type"],
            schedule_expression=data["schedule_expression"],
            next_run=data["next_run"],
            last_run=data.get("last_run"),
            enabled=data.get("enabled", True),
            max_retries=data.get("max_retries", 0),
            priority=data.get("priority", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
