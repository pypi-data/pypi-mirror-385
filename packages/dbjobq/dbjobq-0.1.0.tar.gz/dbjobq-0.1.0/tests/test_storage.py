"""Tests for storage implementations."""

import time


async def test_enqueue_basic(storage):
    """Test basic job enqueue operation."""
    job_id = await storage.enqueue("test.task", '{"key": "value"}')
    assert job_id is not None
    assert isinstance(job_id, str)
    assert len(job_id) > 0


async def test_enqueue_with_priority(storage):
    """Test enqueue with priority."""
    job_id = await storage.enqueue("test.task", '{"key": "value"}', priority=10)
    assert job_id is not None


async def test_enqueue_with_max_retries(storage):
    """Test enqueue with max_retries."""
    job_id = await storage.enqueue("test.task", '{"key": "value"}', max_retries=3)
    assert job_id is not None


async def test_enqueue_with_execute_at(storage):
    """Test enqueue with delayed execution."""
    future_time = time.time() + 60  # 60 seconds in future
    job_id = await storage.enqueue("test.task", '{"key": "value"}', execute_at=future_time)
    assert job_id is not None


async def test_dequeue_empty_queue(storage):
    """Test dequeue from empty queue returns None."""
    job = await storage.dequeue()
    assert job is None


async def test_dequeue_pending_job(storage):
    """Test dequeue returns a pending job."""
    job_id = await storage.enqueue("test.task", '{"name": "test"}')
    job = await storage.dequeue()
    assert job is not None
    assert job.id == job_id
    assert job.type == "test.task"
    assert job.status == "running"


async def test_dequeue_respects_priority(storage):
    """Test dequeue returns higher priority jobs first."""
    low_priority = await storage.enqueue("test.task", '{"priority": "low"}', priority=1)
    high_priority = await storage.enqueue("test.task", '{"priority": "high"}', priority=10)
    medium_priority = await storage.enqueue("test.task", '{"priority": "medium"}', priority=5)

    job1 = await storage.dequeue()
    job2 = await storage.dequeue()
    job3 = await storage.dequeue()

    assert job1.id == high_priority
    assert job2.id == medium_priority
    assert job3.id == low_priority


async def test_dequeue_respects_execute_at(storage):
    """Test dequeue doesn't return jobs before their execute_at time."""
    future_time = time.time() + 3600  # 1 hour in future
    await storage.enqueue("test.task", '{"delayed": true}', execute_at=future_time)
    job = await storage.dequeue()
    assert job is None


async def test_dequeue_returns_ready_delayed_job(storage):
    """Test dequeue returns delayed job once time is reached."""
    past_time = time.time() - 60  # 1 minute in past
    job_id = await storage.enqueue("test.task", '{"delayed": true}', execute_at=past_time)
    job = await storage.dequeue()
    assert job is not None
    assert job.id == job_id


async def test_complete_job(storage):
    """Test marking a job as completed."""
    job_id = await storage.enqueue("test.task", '{"key": "value"}')
    await storage.dequeue()
    await storage.complete(job_id)

    job = await storage.get_job(job_id)
    assert job is not None
    assert job.status == "completed"


async def test_fail_job(storage):
    """Test marking a job as failed."""
    job_id = await storage.enqueue("test.task", '{"key": "value"}')
    await storage.dequeue()
    await storage.fail(job_id, "Test error message")

    job = await storage.get_job(job_id)
    assert job is not None
    assert job.status == "failed"
    assert job.error == "Test error message"


async def test_get_job_by_id(storage):
    """Test retrieving a specific job by ID."""
    job_id = await storage.enqueue("test.task", '{"key": "value"}', priority=5, max_retries=3)
    job = await storage.get_job(job_id)
    assert job is not None
    assert job.id == job_id
    assert job.type == "test.task"
    assert job.priority == 5
    assert job.max_retries == 3


async def test_get_nonexistent_job(storage):
    """Test retrieving a job that doesn't exist."""
    job = await storage.get_job("nonexistent-id")
    assert job is None


async def test_list_all_jobs(storage):
    """Test listing all jobs."""
    await storage.enqueue("test.task1", '{"n": 1}')
    await storage.enqueue("test.task2", '{"n": 2}')
    await storage.enqueue("test.task3", '{"n": 3}')

    jobs = await storage.list_jobs()
    assert len(jobs) == 3


async def test_list_jobs_by_status(storage):
    """Test filtering jobs by status."""
    id1 = await storage.enqueue("test.task", '{"n": 1}')
    id2 = await storage.enqueue("test.task", '{"n": 2}')
    id3 = await storage.enqueue("test.task", '{"n": 3}')

    await storage.dequeue()
    await storage.complete(id1)
    await storage.dequeue()
    await storage.fail(id2, "error")

    pending = await storage.list_jobs(status="pending")
    completed = await storage.list_jobs(status="completed")
    failed = await storage.list_jobs(status="failed")

    assert len(pending) == 1
    assert pending[0].id == id3
    assert len(completed) == 1
    assert completed[0].id == id1
    assert len(failed) == 1
    assert failed[0].id == id2


async def test_list_jobs_with_limit(storage):
    """Test limiting the number of jobs returned."""
    for i in range(10):
        await storage.enqueue("test.task", f'{{"n": {i}}}')

    jobs = await storage.list_jobs(limit=5)
    assert len(jobs) == 5


async def test_retry_job(storage):
    """Test retry job mechanism."""
    job_id = await storage.enqueue("test.task", '{"key": "value"}', max_retries=3)
    job = await storage.dequeue()
    assert job.attempts == 0

    await storage.retry_job(job_id, "First failure", delay=1.0)

    job = await storage.get_job(job_id)
    assert job.status == "pending"
    assert job.attempts == 1
    assert job.error == "First failure"


async def test_retry_job_with_delay(storage):
    """Test retry job respects delay."""
    job_id = await storage.enqueue("test.task", '{"key": "value"}', max_retries=3)
    await storage.dequeue()
    await storage.retry_job(job_id, "Error", delay=3600.0)  # 1 hour delay

    # Should not be dequeued immediately
    job = await storage.dequeue()
    assert job is None

    # Job should still exist in pending state
    job = await storage.get_job(job_id)
    assert job.status == "pending"
    assert job.attempts == 1
