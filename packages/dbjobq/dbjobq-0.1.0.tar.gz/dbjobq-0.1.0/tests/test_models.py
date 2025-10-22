"""Tests for Job model."""

import json
from datetime import datetime

from dbjobq.models import Job


def test_job_creation():
    """Test basic Job creation."""
    job = Job(
        id="test-id",
        type="test.task",
        data={"key": "value"},
        status="pending",
    )
    assert job.id == "test-id"
    assert job.type == "test.task"
    assert job.data == {"key": "value"}
    assert job.status == "pending"
    assert job.attempts == 0
    assert job.max_retries == 0
    assert job.priority == 0


def test_job_with_optional_fields():
    """Test Job creation with all optional fields."""
    now = datetime.now()
    job = Job(
        id="test-id",
        type="test.task",
        data={"key": "value"},
        status="running",
        created_at=now,
        updated_at=now,
        error="Some error",
        attempts=2,
        max_retries=3,
        priority=10,
        execute_at=now,
    )
    assert job.error == "Some error"
    assert job.attempts == 2
    assert job.max_retries == 3
    assert job.priority == 10
    assert job.created_at == now
    assert job.execute_at == now


def test_job_from_dict_with_dict_data():
    """Test Job.from_dict with data as dictionary."""
    job_dict = {
        "id": "test-id",
        "type": "test.task",
        "data": {"key": "value"},
        "status": "pending",
        "attempts": 1,
        "max_retries": 3,
        "priority": 5,
    }
    job = Job.from_dict(job_dict)
    assert job.id == "test-id"
    assert job.type == "test.task"
    assert job.data == {"key": "value"}
    assert job.status == "pending"
    assert job.attempts == 1
    assert job.max_retries == 3
    assert job.priority == 5


def test_job_from_dict_with_json_string_data():
    """Test Job.from_dict with data as JSON string."""
    job_dict = {
        "id": "test-id",
        "type": "test.task",
        "data": json.dumps({"key": "value"}),
        "status": "pending",
    }
    job = Job.from_dict(job_dict)
    assert job.data == {"key": "value"}


def test_job_from_dict_with_missing_optional_fields():
    """Test Job.from_dict with minimal required fields."""
    job_dict = {
        "id": "test-id",
        "type": "test.task",
        "data": {},
        "status": "pending",
    }
    job = Job.from_dict(job_dict)
    assert job.id == "test-id"
    assert job.error is None
    assert job.attempts == 0
    assert job.max_retries == 0
    assert job.priority == 0
