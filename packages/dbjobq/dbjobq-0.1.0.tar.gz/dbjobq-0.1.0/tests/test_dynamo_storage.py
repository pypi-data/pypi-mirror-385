"""Tests for DynamoDB storage backend using mocks."""

import time
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dbjobq.storage.dynamo_storage import DynamoStorage, dynamodb_to_python, python_to_dynamodb


def test_python_to_dynamodb():
    """Test Python to DynamoDB type conversion."""
    assert python_to_dynamodb(1.5) == Decimal("1.5")
    assert python_to_dynamodb({"a": 1.5}) == {"a": Decimal("1.5")}
    assert python_to_dynamodb([1.5, 2.5]) == [Decimal("1.5"), Decimal("2.5")]
    assert python_to_dynamodb("string") == "string"


def test_dynamodb_to_python():
    """Test DynamoDB to Python type conversion."""
    assert dynamodb_to_python(Decimal("1.5")) == 1.5
    assert dynamodb_to_python(Decimal("1.0")) == 1
    assert dynamodb_to_python({"a": Decimal("1.5")}) == {"a": 1.5}
    assert dynamodb_to_python([Decimal("1.5"), Decimal("2.5")]) == [1.5, 2.5]
    assert dynamodb_to_python("string") == "string"


@pytest.fixture
async def mock_dynamodb_table():
    """Create a mock DynamoDB table."""
    table = AsyncMock()
    table.put_item = AsyncMock()
    table.get_item = AsyncMock(return_value={})
    table.update_item = AsyncMock()
    table.delete_item = AsyncMock()
    table.query = AsyncMock(return_value={"Items": []})
    table.scan = AsyncMock(return_value={"Items": []})
    table.load = AsyncMock()
    table.reload = AsyncMock()
    table.table_status = "ACTIVE"
    return table


@pytest.fixture
async def dynamo_storage(mock_dynamodb_table):
    """Create a DynamoStorage instance with mocked DynamoDB."""
    with patch("dbjobq.storage.dynamo_storage.aioboto3") as mock_aioboto3:
        # Mock session and resource
        mock_session = MagicMock()
        mock_resource = AsyncMock()
        mock_resource.__aenter__ = AsyncMock(return_value=mock_resource)
        mock_resource.__aexit__ = AsyncMock(return_value=None)
        mock_resource.Table = AsyncMock(return_value=mock_dynamodb_table)
        mock_resource.create_table = AsyncMock()
        mock_session.resource.return_value = mock_resource
        mock_aioboto3.Session.return_value = mock_session

        storage = DynamoStorage(
            table_name="test_table",
            region_name="us-east-1",
            endpoint_url="http://localhost:8000",
        )
        await storage.initialize()
        yield storage
        await storage.close()


@pytest.mark.asyncio
async def test_initialize_existing_table(mock_dynamodb_table):
    """Test DynamoDB storage initialization with existing table."""
    with patch("dbjobq.storage.dynamo_storage.aioboto3") as mock_aioboto3:
        mock_session = MagicMock()
        mock_resource = AsyncMock()
        mock_resource.__aenter__ = AsyncMock(return_value=mock_resource)
        mock_resource.__aexit__ = AsyncMock(return_value=None)
        mock_resource.Table = AsyncMock(return_value=mock_dynamodb_table)
        mock_session.resource.return_value = mock_resource
        mock_aioboto3.Session.return_value = mock_session

        storage = DynamoStorage(table_name="test_table")
        await storage.initialize()

        assert storage._resource is not None


@pytest.mark.asyncio
async def test_enqueue(dynamo_storage, mock_dynamodb_table):
    """Test enqueueing a job."""
    job_id = await dynamo_storage.enqueue("test.task", {"key": "value"}, priority=5, max_retries=3)

    assert job_id is not None
    assert isinstance(job_id, str)

    mock_dynamodb_table.put_item.assert_called_once()
    call_args = mock_dynamodb_table.put_item.call_args[1]["Item"]
    assert call_args["PK"] == "job"
    assert call_args["SK"] == job_id
    assert call_args["type"] == "test.task"
    assert call_args["status"] == "pending"
    assert call_args["priority"] == 5
    assert call_args["max_retries"] == 3


@pytest.mark.asyncio
async def test_dequeue_empty_queue(dynamo_storage, mock_dynamodb_table):
    """Test dequeue from empty queue."""
    mock_dynamodb_table.query.return_value = {"Items": []}

    job = await dynamo_storage.dequeue()
    assert job is None


@pytest.mark.asyncio
async def test_dequeue_success(dynamo_storage, mock_dynamodb_table):
    """Test successfully dequeueing a job."""
    job_id = "test-job-123"
    current_time = time.time()

    # Mock query to return a pending job
    mock_dynamodb_table.query.return_value = {
        "Items": [
            {
                "PK": "job",
                "SK": job_id,
                "id": job_id,
                "type": "test.task",
                "data": {"key": "value"},
                "status": "pending",
                "priority": Decimal("5"),
                "max_retries": Decimal("3"),
                "attempts": Decimal("0"),
                "execute_at": Decimal(str(current_time - 10)),
                "created_at": Decimal(str(current_time)),
                "priority_execute_at": f"0000000005_{current_time - 10}",
            }
        ]
    }

    # Mock update_item to succeed
    mock_dynamodb_table.update_item.return_value = {}

    job = await dynamo_storage.dequeue()

    assert job is not None
    assert job.id == job_id
    assert job.type == "test.task"
    assert job.status == "running"
    assert job.priority == 5
    assert job.max_retries == 3


@pytest.mark.asyncio
async def test_dequeue_concurrent_claim(dynamo_storage, mock_dynamodb_table):
    """Test dequeue with concurrent claim (job already taken)."""
    job_id = "test-job-123"
    current_time = time.time()

    # First job returned by query
    mock_dynamodb_table.query.return_value = {
        "Items": [
            {
                "PK": "job",
                "SK": job_id,
                "id": job_id,
                "type": "test.task",
                "data": {"key": "value"},
                "status": "pending",
                "priority": Decimal("5"),
                "execute_at": Decimal(str(current_time - 10)),
                "created_at": Decimal(str(current_time)),
                "attempts": Decimal("0"),
                "max_retries": Decimal("3"),
            }
        ]
    }

    # Mock update_item to fail (condition check failed)
    mock_dynamodb_table.update_item.side_effect = Exception("ConditionalCheckFailedException")

    job = await dynamo_storage.dequeue()
    assert job is None


@pytest.mark.asyncio
async def test_complete(dynamo_storage, mock_dynamodb_table):
    """Test marking a job as completed."""
    job_id = "test-job-123"
    await dynamo_storage.complete(job_id)

    mock_dynamodb_table.update_item.assert_called_once()
    call_args = mock_dynamodb_table.update_item.call_args[1]
    assert call_args["Key"] == {"PK": "job", "SK": job_id}


@pytest.mark.asyncio
async def test_fail(dynamo_storage, mock_dynamodb_table):
    """Test marking a job as failed."""
    job_id = "test-job-123"
    error_msg = "Test error"
    await dynamo_storage.fail(job_id, error_msg)

    call_args = mock_dynamodb_table.update_item.call_args[1]
    assert call_args["Key"] == {"PK": "job", "SK": job_id}
    assert ":failed" in str(call_args["ExpressionAttributeValues"])


@pytest.mark.asyncio
async def test_get_job(dynamo_storage, mock_dynamodb_table):
    """Test retrieving a job by ID."""
    job_id = "test-job-123"
    current_time = time.time()

    mock_dynamodb_table.get_item.return_value = {
        "Item": {
            "PK": "job",
            "SK": job_id,
            "id": job_id,
            "type": "test.task",
            "data": {"key": "value"},
            "status": "pending",
            "priority": Decimal("5"),
            "max_retries": Decimal("3"),
            "attempts": Decimal("0"),
            "execute_at": Decimal(str(current_time)),
            "created_at": Decimal(str(current_time)),
        }
    }

    job = await dynamo_storage.get_job(job_id)

    assert job is not None
    assert job.id == job_id
    assert job.type == "test.task"
    assert job.status == "pending"
    assert job.priority == 5


@pytest.mark.asyncio
async def test_get_job_not_found(dynamo_storage, mock_dynamodb_table):
    """Test retrieving a non-existent job."""
    mock_dynamodb_table.get_item.return_value = {}

    job = await dynamo_storage.get_job("nonexistent")
    assert job is None


@pytest.mark.asyncio
async def test_list_jobs_by_status(dynamo_storage, mock_dynamodb_table):
    """Test listing jobs by status."""
    job_id = "test-job-123"
    current_time = time.time()

    mock_dynamodb_table.query.return_value = {
        "Items": [
            {
                "PK": "job",
                "SK": job_id,
                "id": job_id,
                "type": "test.task",
                "data": {"key": "value"},
                "status": "completed",
                "priority": Decimal("0"),
                "max_retries": Decimal("0"),
                "attempts": Decimal("0"),
                "execute_at": Decimal(str(current_time)),
                "created_at": Decimal(str(current_time)),
            }
        ]
    }

    jobs = await dynamo_storage.list_jobs(status="completed", limit=10)

    assert len(jobs) == 1
    assert jobs[0].id == job_id


@pytest.mark.asyncio
async def test_list_jobs_all(dynamo_storage, mock_dynamodb_table):
    """Test listing all jobs."""
    job_id = "test-job-123"
    current_time = time.time()

    mock_dynamodb_table.scan.return_value = {
        "Items": [
            {
                "PK": "job",
                "SK": job_id,
                "id": job_id,
                "type": "test.task",
                "data": {"key": "value"},
                "status": "pending",
                "priority": Decimal("0"),
                "max_retries": Decimal("0"),
                "attempts": Decimal("0"),
                "execute_at": Decimal(str(current_time)),
                "created_at": Decimal(str(current_time)),
            }
        ]
    }

    jobs = await dynamo_storage.list_jobs()

    assert len(jobs) == 1
    assert jobs[0].id == job_id


@pytest.mark.asyncio
async def test_retry_job(dynamo_storage, mock_dynamodb_table):
    """Test retrying a failed job."""
    job_id = "test-job-123"

    # Mock get_item to return job data
    mock_dynamodb_table.get_item.return_value = {
        "Item": {
            "id": job_id,
            "attempts": Decimal("1"),
            "max_retries": Decimal("3"),
            "priority": Decimal("5"),
        }
    }

    await dynamo_storage.retry_job(job_id, "Error message", delay=60)

    # Verify update was called
    assert mock_dynamodb_table.update_item.called


@pytest.mark.asyncio
async def test_retry_job_max_retries_reached(dynamo_storage, mock_dynamodb_table):
    """Test retry job when max retries already reached."""
    job_id = "test-job-123"

    # Mock get_item to return job at max retries
    mock_dynamodb_table.get_item.return_value = {
        "Item": {
            "id": job_id,
            "attempts": Decimal("3"),
            "max_retries": Decimal("3"),
            "priority": Decimal("5"),
        }
    }

    await dynamo_storage.retry_job(job_id, "Error message", delay=60)

    # Verify update was not called (max retries reached)
    mock_dynamodb_table.update_item.assert_not_called()


@pytest.mark.asyncio
async def test_create_schedule(dynamo_storage, mock_dynamodb_table):
    """Test creating a schedule."""
    next_run = time.time() + 300

    schedule_id = await dynamo_storage.create_schedule(
        job_type="test.task",
        job_data={"key": "value"},
        schedule_type="cron",
        schedule_expression="*/5 * * * *",
        next_run=next_run,
        enabled=True,
        max_retries=3,
        priority=5,
    )

    assert schedule_id is not None
    mock_dynamodb_table.put_item.assert_called_once()
    call_args = mock_dynamodb_table.put_item.call_args[1]["Item"]
    assert call_args["PK"] == "schedule"
    assert call_args["SK"] == schedule_id


@pytest.mark.asyncio
async def test_get_due_schedules(dynamo_storage, mock_dynamodb_table):
    """Test retrieving due schedules."""
    schedule_id = "schedule-123"
    now = time.time()

    mock_dynamodb_table.query.return_value = {
        "Items": [
            {
                "PK": "schedule",
                "SK": schedule_id,
                "id": schedule_id,
                "job_type": "test.task",
                "job_data": {"key": "value"},
                "schedule_type": "cron",
                "schedule_expression": "*/5 * * * *",
                "next_run": Decimal(str(now)),
                "last_run": None,
                "enabled": "true",
                "max_retries": Decimal("3"),
                "priority": Decimal("5"),
            }
        ]
    }

    schedules = await dynamo_storage.get_due_schedules(now + 100)

    assert len(schedules) == 1
    assert schedules[0].id == schedule_id
    assert schedules[0].enabled is True


@pytest.mark.asyncio
async def test_update_schedule_next_run(dynamo_storage, mock_dynamodb_table):
    """Test updating schedule next run."""
    schedule_id = "schedule-123"
    next_run = time.time() + 300
    last_run = time.time()

    await dynamo_storage.update_schedule_next_run(schedule_id, next_run, last_run)

    mock_dynamodb_table.update_item.assert_called_once()
    call_args = mock_dynamodb_table.update_item.call_args[1]
    assert call_args["Key"] == {"PK": "schedule", "SK": schedule_id}


@pytest.mark.asyncio
async def test_get_schedule(dynamo_storage, mock_dynamodb_table):
    """Test retrieving a schedule by ID."""
    schedule_id = "schedule-123"
    now = time.time()

    mock_dynamodb_table.get_item.return_value = {
        "Item": {
            "PK": "schedule",
            "SK": schedule_id,
            "id": schedule_id,
            "job_type": "test.task",
            "job_data": {"key": "value"},
            "schedule_type": "cron",
            "schedule_expression": "*/5 * * * *",
            "next_run": Decimal(str(now)),
            "last_run": Decimal(str(now)),
            "enabled": "true",
            "max_retries": Decimal("3"),
            "priority": Decimal("5"),
        }
    }

    schedule = await dynamo_storage.get_schedule(schedule_id)

    assert schedule is not None
    assert schedule.id == schedule_id
    assert schedule.job_type == "test.task"
    assert schedule.enabled is True


@pytest.mark.asyncio
async def test_get_schedule_not_found(dynamo_storage, mock_dynamodb_table):
    """Test retrieving a non-existent schedule."""
    mock_dynamodb_table.get_item.return_value = {}

    schedule = await dynamo_storage.get_schedule("nonexistent")
    assert schedule is None


@pytest.mark.asyncio
async def test_list_schedules_all(dynamo_storage, mock_dynamodb_table):
    """Test listing all schedules."""
    schedule_id = "schedule-123"
    now = time.time()

    mock_dynamodb_table.scan.return_value = {
        "Items": [
            {
                "PK": "schedule",
                "SK": schedule_id,
                "id": schedule_id,
                "job_type": "test.task",
                "job_data": {"key": "value"},
                "schedule_type": "cron",
                "schedule_expression": "*/5 * * * *",
                "next_run": Decimal(str(now)),
                "last_run": None,
                "enabled": "true",
                "max_retries": Decimal("3"),
                "priority": Decimal("5"),
            }
        ]
    }

    schedules = await dynamo_storage.list_schedules()

    assert len(schedules) == 1
    assert schedules[0].id == schedule_id


@pytest.mark.asyncio
async def test_list_schedules_enabled_only(dynamo_storage, mock_dynamodb_table):
    """Test listing only enabled schedules."""
    schedule_id = "schedule-123"
    now = time.time()

    mock_dynamodb_table.query.return_value = {
        "Items": [
            {
                "PK": "schedule",
                "SK": schedule_id,
                "id": schedule_id,
                "job_type": "test.task",
                "job_data": {"key": "value"},
                "schedule_type": "cron",
                "schedule_expression": "*/5 * * * *",
                "next_run": Decimal(str(now)),
                "last_run": None,
                "enabled": "true",
                "max_retries": Decimal("3"),
                "priority": Decimal("5"),
            }
        ]
    }

    schedules = await dynamo_storage.list_schedules(enabled=True)

    assert len(schedules) == 1


@pytest.mark.asyncio
async def test_delete_schedule(dynamo_storage, mock_dynamodb_table):
    """Test deleting a schedule."""
    schedule_id = "schedule-123"

    await dynamo_storage.delete_schedule(schedule_id)

    mock_dynamodb_table.delete_item.assert_called_once_with(Key={"PK": "schedule", "SK": schedule_id})


@pytest.mark.asyncio
async def test_enable_schedule(dynamo_storage, mock_dynamodb_table):
    """Test enabling/disabling a schedule."""
    schedule_id = "schedule-123"

    await dynamo_storage.enable_schedule(schedule_id, True)

    call_args = mock_dynamodb_table.update_item.call_args[1]
    assert call_args["Key"] == {"PK": "schedule", "SK": schedule_id}
    assert call_args["ExpressionAttributeValues"][":enabled"] == "true"
