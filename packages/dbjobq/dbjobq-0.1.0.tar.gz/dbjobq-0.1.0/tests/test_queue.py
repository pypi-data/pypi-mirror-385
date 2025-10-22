"""Tests for JobQueue class."""

import asyncio

from dbjobq import Worker, job


@job(max_retries=2, priority=5)
def sample_task(data):
    """Sample task for testing."""
    return data["value"]


@job(max_retries=3)
def failing_task(_data):
    """Task that always fails."""
    raise ValueError("Task failed")


async def test_enqueue_callable(job_queue):
    """Test enqueuing a callable function."""
    job_id = await job_queue.enqueue(sample_task, {"value": 42})
    assert job_id is not None


async def test_enqueue_string(job_queue):
    """Test enqueuing by string type."""
    job_id = await job_queue.enqueue("test.module.task", {"value": 42})
    assert job_id is not None


async def test_enqueue_with_delay(job_queue):
    """Test enqueuing with delay."""
    job_id = await job_queue.enqueue(sample_task, {"value": 42}, delay=10.0)
    assert job_id is not None

    # Job should not be dequeued immediately
    job = await job_queue.dequeue()
    assert job is None


async def test_enqueue_inherits_decorator_config(job_queue):
    """Test that enqueue uses decorator configuration."""
    job_id = await job_queue.enqueue(sample_task, {"value": 42})
    job = await job_queue.get_job(job_id)
    assert job.max_retries == 2
    assert job.priority == 5


async def test_enqueue_overrides_decorator_config(job_queue):
    """Test that enqueue parameters override decorator config."""
    job_id = await job_queue.enqueue(sample_task, {"value": 42}, priority=10, max_retries=5)
    job = await job_queue.get_job(job_id)
    assert job.max_retries == 5
    assert job.priority == 10


async def test_dequeue(job_queue):
    """Test dequeuing a job."""
    job_id = await job_queue.enqueue(sample_task, {"value": 42})
    job = await job_queue.dequeue()
    assert job is not None
    assert job.id == job_id
    assert job.data == {"value": 42}


async def test_dequeue_empty_queue(job_queue):
    """Test dequeuing from empty queue."""
    job = await job_queue.dequeue()
    assert job is None


async def test_complete(job_queue):
    """Test completing a job."""
    job_id = await job_queue.enqueue(sample_task, {"value": 42})
    await job_queue.dequeue()
    await job_queue.complete(job_id)

    job = await job_queue.get_job(job_id)
    assert job.status == "completed"


async def test_fail(job_queue):
    """Test failing a job."""
    job_id = await job_queue.enqueue(sample_task, {"value": 42})
    await job_queue.dequeue()
    await job_queue.fail(job_id, "Test error")

    job = await job_queue.get_job(job_id)
    assert job.status == "failed"
    assert job.error == "Test error"


async def test_execute_job_success(job_queue):
    """Test executing a successful job."""
    job_id = await job_queue.enqueue(sample_task, {"value": 42})
    job = await job_queue.dequeue()
    await job_queue.execute_job(job)

    completed_job = await job_queue.get_job(job_id)
    assert completed_job.status == "completed"


async def test_execute_job_with_retry(job_queue):
    """Test executing a failing job that should retry."""
    job_id = await job_queue.enqueue(failing_task, {"value": 42})
    job = await job_queue.dequeue()
    await job_queue.execute_job(job)

    # Job should be back in pending state for retry
    retried_job = await job_queue.get_job(job_id)
    assert retried_job.status == "pending"
    assert retried_job.attempts == 1
    assert retried_job.error is not None


async def test_execute_job_max_retries_reached(job_queue):
    """Test executing a job that fails after max retries."""
    job_id = await job_queue.enqueue(failing_task, {"value": 42})

    # Use a worker to handle retries with delays
    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()

    # Wait long enough for all retries (initial + 3 retries with exponential backoff: 1s, 2s, 4s)
    await asyncio.sleep(10.0)
    await worker.stop()

    # Job should be marked as failed after exhausting retries
    final_job = await job_queue.get_job(job_id)
    assert final_job.status == "failed"
    assert "ValueError: Task failed" in final_job.error


async def test_get_job(job_queue):
    """Test getting a job by ID."""
    job_id = await job_queue.enqueue(sample_task, {"value": 42})
    job = await job_queue.get_job(job_id)
    assert job is not None
    assert job.id == job_id


async def test_list_jobs(job_queue):
    """Test listing all jobs."""
    await job_queue.enqueue(sample_task, {"n": 1})
    await job_queue.enqueue(sample_task, {"n": 2})
    await job_queue.enqueue(sample_task, {"n": 3})

    jobs = await job_queue.list_jobs()
    assert len(jobs) == 3


async def test_get_pending_jobs(job_queue):
    """Test getting pending jobs."""
    await job_queue.enqueue(sample_task, {"n": 1})
    id2 = await job_queue.enqueue(sample_task, {"n": 2})

    await job_queue.dequeue()  # Dequeue first job (now running)
    # Don't complete id2, just dequeue first one

    pending = await job_queue.get_pending_jobs()
    assert len(pending) == 1
    assert pending[0].id == id2


async def test_get_running_jobs(job_queue):
    """Test getting running jobs."""
    await job_queue.enqueue(sample_task, {"n": 1})
    await job_queue.enqueue(sample_task, {"n": 2})

    await job_queue.dequeue()

    running = await job_queue.get_running_jobs()
    assert len(running) == 1


async def test_get_completed_jobs(job_queue):
    """Test getting completed jobs."""
    id1 = await job_queue.enqueue(sample_task, {"n": 1})
    id2 = await job_queue.enqueue(sample_task, {"n": 2})

    await job_queue.dequeue()
    await job_queue.complete(id1)
    await job_queue.dequeue()
    await job_queue.complete(id2)

    completed = await job_queue.get_completed_jobs()
    assert len(completed) == 2


async def test_get_failed_jobs(job_queue):
    """Test getting failed jobs."""
    id1 = await job_queue.enqueue(sample_task, {"n": 1})
    await job_queue.dequeue()
    await job_queue.fail(id1, "error")

    failed = await job_queue.get_failed_jobs()
    assert len(failed) == 1
    assert failed[0].id == id1


async def test_list_jobs_with_limit(job_queue):
    """Test listing jobs with limit."""
    for i in range(10):
        await job_queue.enqueue(sample_task, {"n": i})

    jobs = await job_queue.list_jobs(limit=5)
    assert len(jobs) == 5
