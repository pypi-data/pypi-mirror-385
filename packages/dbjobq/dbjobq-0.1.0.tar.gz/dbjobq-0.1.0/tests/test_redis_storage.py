"""Tests for Redis storage backend using mocks."""

import time
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from dbjobq.models import Schedule as ScheduleModel
from dbjobq.storage.redis_storage import RedisStorage


@pytest.fixture
async def mock_redis():
    """Create a mock Redis client."""
    redis_mock = AsyncMock()
    # Mock common Redis operations
    redis_mock.hset = AsyncMock()
    redis_mock.hgetall = AsyncMock(return_value={})
    redis_mock.zadd = AsyncMock()
    redis_mock.zrange = AsyncMock(return_value=[])
    redis_mock.zrangebyscore = AsyncMock(return_value=[])
    redis_mock.zrem = AsyncMock(return_value=1)
    redis_mock.sadd = AsyncMock()
    redis_mock.srem = AsyncMock()
    redis_mock.smembers = AsyncMock(return_value=set())
    redis_mock.delete = AsyncMock()
    redis_mock.aclose = AsyncMock()
    redis_mock.scan_iter = AsyncMock()
    return redis_mock


@pytest.fixture
async def redis_storage(mock_redis):
    """Create a RedisStorage instance with mocked Redis."""
    with patch("dbjobq.storage.redis_storage.Redis") as mock_redis_class:
        mock_redis_class.from_url.return_value = mock_redis
        storage = RedisStorage("redis://localhost:6379/0")
        await storage.initialize()
        yield storage
        await storage.close()


@pytest.mark.asyncio
async def test_initialize(mock_redis):
    """Test Redis storage initialization."""
    with patch("dbjobq.storage.redis_storage.Redis") as mock_redis_class:
        mock_redis_class.from_url.return_value = mock_redis
        storage = RedisStorage("redis://localhost:6379/0")
        await storage.initialize()
        mock_redis_class.from_url.assert_called_once_with("redis://localhost:6379/0", decode_responses=False)
        assert storage.redis is not None


@pytest.mark.asyncio
async def test_close(redis_storage, mock_redis):
    """Test closing Redis connection."""
    await redis_storage.close()
    mock_redis.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_enqueue(redis_storage, mock_redis):
    """Test enqueueing a job."""
    job_id = await redis_storage.enqueue("test.task", '{"key": "value"}', priority=5, max_retries=3)

    assert job_id is not None
    assert isinstance(job_id, str)

    # Verify hset was called to store job data
    mock_redis.hset.assert_called()
    call_args = mock_redis.hset.call_args
    assert call_args[0][0] == f"job:{job_id}"
    assert "type" in call_args[1]["mapping"]
    assert call_args[1]["mapping"]["type"] == "test.task"
    assert call_args[1]["mapping"]["status"] == "pending"
    assert call_args[1]["mapping"]["priority"] == "5"
    assert call_args[1]["mapping"]["max_retries"] == "3"

    # Verify zadd was called to add to pending queue
    mock_redis.zadd.assert_called_once()


@pytest.mark.asyncio
async def test_enqueue_with_delay(redis_storage, mock_redis):
    """Test enqueueing a delayed job."""
    future_time = time.time() + 60
    await redis_storage.enqueue("test.task", '{"key": "value"}', execute_at=future_time)

    call_args = mock_redis.hset.call_args
    assert call_args[1]["mapping"]["execute_at"] == str(future_time)


@pytest.mark.asyncio
async def test_dequeue_empty_queue(redis_storage, mock_redis):
    """Test dequeue from empty queue."""
    mock_redis.zrange.return_value = []

    job = await redis_storage.dequeue()
    assert job is None


@pytest.mark.asyncio
async def test_dequeue_success(redis_storage, mock_redis):
    """Test successfully dequeueing a job."""
    job_id = "test-job-123"
    current_time = datetime.now().timestamp()

    # Mock zrange to return a job
    mock_redis.zrange.return_value = [(job_id.encode(), 0)]

    # Mock hgetall to return job data
    mock_redis.hgetall.return_value = {
        b"type": b"test.task",
        b"data": b'{"key": "value"}',
        b"status": b"pending",
        b"priority": b"5",
        b"max_retries": b"3",
        b"attempts": b"0",
        b"execute_at": str(current_time - 10).encode(),
        b"created_at": str(current_time).encode(),
    }

    # Mock zrem to succeed (job claimed)
    mock_redis.zrem.return_value = 1

    job = await redis_storage.dequeue()

    assert job is not None
    assert job.id == job_id
    assert job.type == "test.task"
    assert job.status == "running"
    assert job.priority == 5
    assert job.max_retries == 3

    # Verify job was moved to running
    mock_redis.sadd.assert_called_with("jobs:running", job_id)


@pytest.mark.asyncio
async def test_dequeue_not_ready_yet(redis_storage, mock_redis):
    """Test dequeue doesn't return jobs that aren't ready yet."""
    job_id = "test-job-123"
    future_time = datetime.now().timestamp() + 3600

    mock_redis.zrange.return_value = [(job_id.encode(), 0)]
    mock_redis.hgetall.return_value = {
        b"type": b"test.task",
        b"data": b'{"key": "value"}',
        b"execute_at": str(future_time).encode(),
    }

    job = await redis_storage.dequeue()
    assert job is None


@pytest.mark.asyncio
async def test_complete(redis_storage, mock_redis):
    """Test marking a job as completed."""
    job_id = "test-job-123"
    await redis_storage.complete(job_id)

    # Verify hset was called to update status
    assert mock_redis.hset.call_count >= 2
    # Verify job moved from running to completed
    mock_redis.srem.assert_called_with("jobs:running", job_id)
    mock_redis.sadd.assert_called_with("jobs:completed", job_id)


@pytest.mark.asyncio
async def test_fail(redis_storage, mock_redis):
    """Test marking a job as failed."""
    job_id = "test-job-123"
    error_msg = "Test error"
    await redis_storage.fail(job_id, error_msg)

    # Verify hset was called with error
    call_args = mock_redis.hset.call_args_list
    assert any("error" in str(call) for call in call_args)

    # Verify job moved from running to failed
    mock_redis.srem.assert_called_with("jobs:running", job_id)
    mock_redis.sadd.assert_called_with("jobs:failed", job_id)


@pytest.mark.asyncio
async def test_get_job(redis_storage, mock_redis):
    """Test retrieving a job by ID."""
    job_id = "test-job-123"
    current_time = datetime.now().timestamp()

    mock_redis.hgetall.return_value = {
        b"type": b"test.task",
        b"data": b'{"key": "value"}',
        b"status": b"pending",
        b"priority": b"5",
        b"max_retries": b"3",
        b"attempts": b"0",
        b"execute_at": b"",
        b"created_at": str(current_time).encode(),
    }

    job = await redis_storage.get_job(job_id)

    assert job is not None
    assert job.id == job_id
    assert job.type == "test.task"
    assert job.status == "pending"
    assert job.priority == 5


@pytest.mark.asyncio
async def test_get_job_not_found(redis_storage, mock_redis):
    """Test retrieving a non-existent job."""
    mock_redis.hgetall.return_value = {}

    job = await redis_storage.get_job("nonexistent")
    assert job is None


@pytest.mark.asyncio
async def test_list_jobs_by_status(redis_storage, mock_redis):
    """Test listing jobs by status."""
    job_id = "test-job-123"
    current_time = datetime.now().timestamp()

    mock_redis.smembers.return_value = {job_id.encode()}
    mock_redis.hgetall.return_value = {
        b"type": b"test.task",
        b"data": b'{"key": "value"}',
        b"status": b"completed",
        b"priority": b"0",
        b"max_retries": b"0",
        b"attempts": b"0",
        b"execute_at": b"",
        b"created_at": str(current_time).encode(),
    }

    jobs = await redis_storage.list_jobs(status="completed", limit=10)

    assert len(jobs) == 1
    assert jobs[0].id == job_id


@pytest.mark.asyncio
async def test_list_jobs_pending(redis_storage, mock_redis):
    """Test listing pending jobs."""
    job_id = "test-job-123"
    current_time = datetime.now().timestamp()

    mock_redis.zrange.return_value = [job_id.encode()]
    mock_redis.hgetall.return_value = {
        b"type": b"test.task",
        b"data": b'{"key": "value"}',
        b"status": b"pending",
        b"priority": b"0",
        b"max_retries": b"0",
        b"attempts": b"0",
        b"execute_at": b"",
        b"created_at": str(current_time).encode(),
    }

    jobs = await redis_storage.list_jobs(status="pending", limit=10)

    assert len(jobs) == 1
    assert jobs[0].id == job_id


@pytest.mark.asyncio
async def test_retry_job(redis_storage, mock_redis):
    """Test retrying a failed job."""
    job_id = "test-job-123"

    mock_redis.hgetall.return_value = {
        b"attempts": b"1",
        b"priority": b"5",
    }

    await redis_storage.retry_job(job_id, "Error message", delay=60)

    # Verify job was updated
    assert mock_redis.hset.called
    call_args = mock_redis.hset.call_args
    assert call_args[1]["mapping"]["status"] == "pending"
    assert call_args[1]["mapping"]["attempts"] == "2"

    # Verify job moved from running to pending
    mock_redis.srem.assert_called_with("jobs:running", job_id)
    mock_redis.zadd.assert_called()


@pytest.mark.asyncio
async def test_create_schedule(redis_storage, mock_redis):
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

    await redis_storage.create_schedule(schedule)

    # Verify schedule was stored
    assert mock_redis.hset.called
    call_args = mock_redis.hset.call_args
    assert call_args[0][0] == f"schedule:{schedule.id}"

    # Verify added to sorted set
    mock_redis.zadd.assert_called()


@pytest.mark.asyncio
async def test_get_due_schedules(redis_storage, mock_redis):
    """Test retrieving due schedules."""
    schedule_id = "schedule-123"
    now = datetime.now()

    mock_redis.zrangebyscore.return_value = [schedule_id.encode()]
    mock_redis.hgetall.return_value = {
        b"job_type": b"test.task",
        b"job_data": b'{"key": "value"}',
        b"schedule_type": b"cron",
        b"schedule_expression": b"*/5 * * * *",
        b"next_run": str(now.timestamp()).encode(),
        b"last_run": b"",
        b"enabled": b"1",
        b"max_retries": b"3",
        b"priority": b"5",
        b"created_at": str(now.timestamp()).encode(),
    }

    schedules = await redis_storage.get_due_schedules()

    assert len(schedules) == 1
    assert schedules[0].id == schedule_id
    assert schedules[0].enabled is True


@pytest.mark.asyncio
async def test_update_schedule_next_run(redis_storage, mock_redis):
    """Test updating schedule next run."""
    schedule_id = "schedule-123"
    next_run = time.time() + 300
    last_run = time.time()

    await redis_storage.update_schedule_next_run(schedule_id, next_run, last_run)

    # Verify schedule was updated
    assert mock_redis.hset.called
    mock_redis.zadd.assert_called()


@pytest.mark.asyncio
async def test_get_schedule(redis_storage, mock_redis):
    """Test retrieving a schedule by ID."""
    schedule_id = "schedule-123"
    now = datetime.now()

    mock_redis.hgetall.return_value = {
        b"job_type": b"test.task",
        b"job_data": b'{"key": "value"}',
        b"schedule_type": b"cron",
        b"schedule_expression": b"*/5 * * * *",
        b"next_run": str(now.timestamp()).encode(),
        b"last_run": str(now.timestamp()).encode(),
        b"enabled": b"1",
        b"max_retries": b"3",
        b"priority": b"5",
        b"created_at": str(now.timestamp()).encode(),
    }

    schedule = await redis_storage.get_schedule(schedule_id)

    assert schedule is not None
    assert schedule.id == schedule_id
    assert schedule.job_type == "test.task"
    assert schedule.enabled is True


@pytest.mark.asyncio
async def test_get_schedule_not_found(redis_storage, mock_redis):
    """Test retrieving a non-existent schedule."""
    mock_redis.hgetall.return_value = {}

    schedule = await redis_storage.get_schedule("nonexistent")
    assert schedule is None


@pytest.mark.asyncio
async def test_list_schedules(redis_storage, mock_redis):
    """Test listing all schedules."""
    schedule_id = "schedule-123"
    now = datetime.now()

    # Mock scan_iter to return schedule keys
    async def mock_scan_iter(*_args, **_kwargs):
        yield f"schedule:{schedule_id}".encode()

    mock_redis.scan_iter = mock_scan_iter
    mock_redis.hgetall.return_value = {
        b"job_type": b"test.task",
        b"job_data": b'{"key": "value"}',
        b"schedule_type": b"cron",
        b"schedule_expression": b"*/5 * * * *",
        b"next_run": str(now.timestamp()).encode(),
        b"last_run": b"",
        b"enabled": b"1",
        b"max_retries": b"3",
        b"priority": b"5",
        b"created_at": str(now.timestamp()).encode(),
    }

    schedules = await redis_storage.list_schedules()

    assert len(schedules) == 1
    assert schedules[0].id == schedule_id


@pytest.mark.asyncio
async def test_list_schedules_enabled_only(redis_storage, mock_redis):
    """Test listing only enabled schedules."""
    schedule_id = "schedule-123"
    now = datetime.now()

    mock_redis.zrange.return_value = [schedule_id.encode()]
    mock_redis.hgetall.return_value = {
        b"job_type": b"test.task",
        b"job_data": b'{"key": "value"}',
        b"schedule_type": b"cron",
        b"schedule_expression": b"*/5 * * * *",
        b"next_run": str(now.timestamp()).encode(),
        b"last_run": b"",
        b"enabled": b"1",
        b"max_retries": b"3",
        b"priority": b"5",
        b"created_at": str(now.timestamp()).encode(),
    }

    schedules = await redis_storage.list_schedules(enabled_only=True)

    assert len(schedules) == 1


@pytest.mark.asyncio
async def test_delete_schedule(redis_storage, mock_redis):
    """Test deleting a schedule."""
    schedule_id = "schedule-123"

    await redis_storage.delete_schedule(schedule_id)

    mock_redis.delete.assert_called_with(f"schedule:{schedule_id}")
    mock_redis.zrem.assert_called_with("schedules:next_run", schedule_id)


@pytest.mark.asyncio
async def test_enable_schedule(redis_storage, mock_redis):
    """Test enabling/disabling a schedule."""
    schedule_id = "schedule-123"
    now = datetime.now()

    # Test enabling
    mock_redis.hgetall.return_value = {
        b"next_run": str(now.timestamp()).encode(),
    }

    await redis_storage.enable_schedule(schedule_id, True)
    assert mock_redis.hset.called

    # Test disabling
    await redis_storage.enable_schedule(schedule_id, False)
    mock_redis.zrem.assert_called_with("schedules:next_run", schedule_id)
