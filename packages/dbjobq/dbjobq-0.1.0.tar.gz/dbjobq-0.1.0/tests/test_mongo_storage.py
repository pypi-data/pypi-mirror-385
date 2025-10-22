"""Tests for MongoDB storage backend using mocks."""

import time
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dbjobq.models import Schedule as ScheduleModel
from dbjobq.storage.mongo_storage import MongoStorage


@pytest.fixture
async def mock_mongo_collection():
    """Create a mock MongoDB collection."""
    collection = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock(return_value=None)
    collection.find_one_and_update = AsyncMock(return_value=None)
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.create_index = AsyncMock()
    # Use MagicMock for find so it can return synchronous mock cursors
    collection.find = MagicMock()
    return collection


@pytest.fixture
async def mongo_storage(mock_mongo_collection):
    """Create a MongoStorage instance with mocked MongoDB."""
    with patch("dbjobq.storage.mongo_storage.AsyncMongoClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_mongo_collection
        mock_client.__getitem__.return_value = mock_db
        mock_client.close = MagicMock()  # Motor's close() is synchronous, not async
        mock_client_class.return_value = mock_client

        storage = MongoStorage(
            mongo_url="mongodb://localhost:27017",
            db_name="test_db",
            jobs_collection="jobs",
            schedules_collection="schedules",
        )
        await storage.initialize()
        yield storage
        await storage.close()


@pytest.mark.asyncio
async def test_initialize():
    """Test MongoDB storage initialization."""
    with patch("dbjobq.storage.mongo_storage.AsyncMongoClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_db = AsyncMock()
        mock_collection = AsyncMock()
        mock_collection.create_index = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_client.__getitem__.return_value = mock_db
        mock_client_class.return_value = mock_client

        storage = MongoStorage("mongodb://localhost:27017", "test_db")
        await storage.initialize()

        assert storage.client is not None
        assert storage.jobs_collection is not None
        assert storage.schedules_collection is not None
        assert mock_collection.create_index.call_count == 2


@pytest.mark.asyncio
async def test_close(mongo_storage):
    """Test closing MongoDB connection."""
    # The close method calls client.close() which is mocked as AsyncMock
    # Just verify it was set up correctly
    assert mongo_storage.client is not None


@pytest.mark.asyncio
async def test_enqueue(mongo_storage, mock_mongo_collection):
    """Test enqueueing a job."""
    job_id = await mongo_storage.enqueue("test.task", '{"key": "value"}', priority=5, max_retries=3)

    assert job_id is not None
    assert isinstance(job_id, str)

    mock_mongo_collection.insert_one.assert_called_once()
    call_args = mock_mongo_collection.insert_one.call_args[0][0]
    assert call_args["_id"] == job_id
    assert call_args["type"] == "test.task"
    assert call_args["status"] == "pending"
    assert call_args["priority"] == 5
    assert call_args["max_retries"] == 3


@pytest.mark.asyncio
async def test_enqueue_with_delay(mongo_storage, mock_mongo_collection):
    """Test enqueueing a delayed job."""
    future_time = time.time() + 60
    await mongo_storage.enqueue("test.task", '{"key": "value"}', execute_at=future_time)

    call_args = mock_mongo_collection.insert_one.call_args[0][0]
    assert call_args["execute_at"] == future_time


@pytest.mark.asyncio
async def test_dequeue_empty_queue(mongo_storage, mock_mongo_collection):
    """Test dequeue from empty queue."""
    mock_mongo_collection.find_one_and_update.return_value = None

    job = await mongo_storage.dequeue()
    assert job is None


@pytest.mark.asyncio
async def test_dequeue_success(mongo_storage, mock_mongo_collection):
    """Test successfully dequeueing a job."""
    job_id = "test-job-123"
    current_time = time.time()

    mock_mongo_collection.find_one_and_update.return_value = {
        "_id": job_id,
        "type": "test.task",
        "data": '{"key": "value"}',
        "status": "running",
        "priority": 5,
        "max_retries": 3,
        "attempts": 0,
        "execute_at": current_time - 10,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    job = await mongo_storage.dequeue()

    assert job is not None
    assert job.id == job_id
    assert job.type == "test.task"
    assert job.status == "running"
    assert job.priority == 5
    assert job.max_retries == 3


@pytest.mark.asyncio
async def test_complete(mongo_storage, mock_mongo_collection):
    """Test marking a job as completed."""
    job_id = "test-job-123"
    await mongo_storage.complete(job_id)

    mock_mongo_collection.update_one.assert_called_once()
    call_args = mock_mongo_collection.update_one.call_args
    assert call_args[0][0] == {"_id": job_id}
    assert "completed" in str(call_args[0][1])


@pytest.mark.asyncio
async def test_fail(mongo_storage, mock_mongo_collection):
    """Test marking a job as failed."""
    job_id = "test-job-123"
    error_msg = "Test error"
    await mongo_storage.fail(job_id, error_msg)

    call_args = mock_mongo_collection.update_one.call_args
    assert call_args[0][0] == {"_id": job_id}
    assert "failed" in str(call_args[0][1])


@pytest.mark.asyncio
async def test_get_job(mongo_storage, mock_mongo_collection):
    """Test retrieving a job by ID."""
    job_id = "test-job-123"

    mock_mongo_collection.find_one.return_value = {
        "_id": job_id,
        "type": "test.task",
        "data": '{"key": "value"}',
        "status": "pending",
        "priority": 5,
        "max_retries": 3,
        "attempts": 0,
        "execute_at": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    job = await mongo_storage.get_job(job_id)

    assert job is not None
    assert job.id == job_id
    assert job.type == "test.task"
    assert job.status == "pending"
    assert job.priority == 5


@pytest.mark.asyncio
async def test_get_job_not_found(mongo_storage, mock_mongo_collection):
    """Test retrieving a non-existent job."""
    mock_mongo_collection.find_one.return_value = None

    job = await mongo_storage.get_job("nonexistent")
    assert job is None


@pytest.mark.asyncio
async def test_list_jobs(mongo_storage, mock_mongo_collection):
    """Test listing jobs."""
    job_data = {
        "_id": "test-job-123",
        "type": "test.task",
        "data": '{"key": "value"}',
        "status": "completed",
        "priority": 0,
        "max_retries": 0,
        "attempts": 0,
        "execute_at": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Mock async iterator
    class MockCursor:
        def __init__(self, items):
            self.items = items
            self.index = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.index >= len(self.items):
                raise StopAsyncIteration
            item = self.items[self.index]
            self.index += 1
            return item

        def limit(self, _n):
            return self

    mock_mongo_collection.find.return_value = MockCursor([job_data])

    jobs = await mongo_storage.list_jobs(status="completed", limit=10)

    assert len(jobs) == 1
    assert jobs[0].id == "test-job-123"


@pytest.mark.asyncio
async def test_retry_job(mongo_storage, mock_mongo_collection):
    """Test retrying a failed job."""
    job_id = "test-job-123"

    await mongo_storage.retry_job(job_id, "Error message", delay=60)

    mock_mongo_collection.update_one.assert_called_once()
    call_args = mock_mongo_collection.update_one.call_args
    assert call_args[0][0] == {"_id": job_id}
    update_expr = call_args[0][1]
    assert "$set" in update_expr
    assert "$inc" in update_expr
    assert update_expr["$set"]["status"] == "pending"
    assert update_expr["$inc"]["attempts"] == 1


@pytest.mark.asyncio
async def test_create_schedule(mongo_storage, mock_mongo_collection):
    """Test creating a schedule."""
    schedule = ScheduleModel(
        id="schedule-123",
        job_type="test.task",
        job_data={"key": "value"},
        schedule_type="cron",
        schedule_expression="*/5 * * * *",
        next_run=datetime.now(),
        enabled=True,
        max_retries=3,
        priority=5,
    )

    await mongo_storage.create_schedule(schedule)

    mock_mongo_collection.insert_one.assert_called()
    call_args = mock_mongo_collection.insert_one.call_args[0][0]
    assert call_args["_id"] == schedule.id
    assert call_args["job_type"] == schedule.job_type
    assert call_args["enabled"] is True


@pytest.mark.asyncio
async def test_get_due_schedules(mongo_storage, mock_mongo_collection):
    """Test retrieving due schedules."""
    now = datetime.now()
    schedule_data = {
        "_id": "schedule-123",
        "job_type": "test.task",
        "job_data": {"key": "value"},
        "schedule_type": "cron",
        "schedule_expression": "*/5 * * * *",
        "next_run": now,
        "last_run": None,
        "enabled": True,
        "max_retries": 3,
        "priority": 5,
        "created_at": now,
        "updated_at": now,
    }

    class MockCursor:
        def __aiter__(self):
            return self

        async def __anext__(self):
            # Return the schedule once, then stop
            if not hasattr(self, "_done"):
                self._done = True
                return schedule_data
            raise StopAsyncIteration

    mock_mongo_collection.find.return_value = MockCursor()

    schedules = await mongo_storage.get_due_schedules()

    assert len(schedules) == 1
    assert schedules[0].id == "schedule-123"
    assert schedules[0].enabled is True


@pytest.mark.asyncio
async def test_update_schedule_next_run(mongo_storage, mock_mongo_collection):
    """Test updating schedule next run."""
    schedule_id = "schedule-123"
    next_run = time.time() + 300
    last_run = time.time()

    await mongo_storage.update_schedule_next_run(schedule_id, next_run, last_run)

    mock_mongo_collection.update_one.assert_called_once()
    call_args = mock_mongo_collection.update_one.call_args
    assert call_args[0][0] == {"_id": schedule_id}


@pytest.mark.asyncio
async def test_get_schedule(mongo_storage, mock_mongo_collection):
    """Test retrieving a schedule by ID."""
    schedule_id = "schedule-123"
    now = datetime.now()

    mock_mongo_collection.find_one.return_value = {
        "_id": schedule_id,
        "job_type": "test.task",
        "job_data": {"key": "value"},
        "schedule_type": "cron",
        "schedule_expression": "*/5 * * * *",
        "next_run": now,
        "last_run": now,
        "enabled": True,
        "max_retries": 3,
        "priority": 5,
        "created_at": now,
        "updated_at": now,
    }

    schedule = await mongo_storage.get_schedule(schedule_id)

    assert schedule is not None
    assert schedule.id == schedule_id
    assert schedule.job_type == "test.task"
    assert schedule.enabled is True


@pytest.mark.asyncio
async def test_get_schedule_not_found(mongo_storage, mock_mongo_collection):
    """Test retrieving a non-existent schedule."""
    mock_mongo_collection.find_one.return_value = None

    schedule = await mongo_storage.get_schedule("nonexistent")
    assert schedule is None


@pytest.mark.asyncio
async def test_list_schedules(mongo_storage, mock_mongo_collection):
    """Test listing all schedules."""
    now = datetime.now()
    schedule_data = {
        "_id": "schedule-123",
        "job_type": "test.task",
        "job_data": {"key": "value"},
        "schedule_type": "cron",
        "schedule_expression": "*/5 * * * *",
        "next_run": now,
        "last_run": None,
        "enabled": True,
        "max_retries": 3,
        "priority": 5,
        "created_at": now,
        "updated_at": now,
    }

    class MockCursor:
        def __aiter__(self):
            return self

        async def __anext__(self):
            if not hasattr(self, "_done"):
                self._done = True
                return schedule_data
            raise StopAsyncIteration

    mock_mongo_collection.find.return_value = MockCursor()

    schedules = await mongo_storage.list_schedules()

    assert len(schedules) == 1
    assert schedules[0].id == "schedule-123"


@pytest.mark.asyncio
async def test_delete_schedule(mongo_storage, mock_mongo_collection):
    """Test deleting a schedule."""
    schedule_id = "schedule-123"

    await mongo_storage.delete_schedule(schedule_id)

    mock_mongo_collection.delete_one.assert_called_once_with({"_id": schedule_id})


@pytest.mark.asyncio
async def test_enable_schedule(mongo_storage, mock_mongo_collection):
    """Test enabling/disabling a schedule."""
    schedule_id = "schedule-123"

    await mongo_storage.enable_schedule(schedule_id, True)

    call_args = mock_mongo_collection.update_one.call_args
    assert call_args[0][0] == {"_id": schedule_id}
    assert call_args[0][1]["$set"]["enabled"] is True
