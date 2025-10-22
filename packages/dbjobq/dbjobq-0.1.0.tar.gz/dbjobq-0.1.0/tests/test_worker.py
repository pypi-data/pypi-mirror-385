"""Tests for Worker class."""

import asyncio

from dbjobq import Worker, job


@job()
def success_task(data):
    """Task that succeeds."""
    data["processed"] = True


@job(max_retries=2)
def retry_task(data):
    """Task that fails on first attempt but succeeds on retry."""
    if data.get("attempts", 0) < 1:
        data["attempts"] = data.get("attempts", 0) + 1
        raise ValueError("First attempt fails")
    data["processed"] = True


async def test_worker_creation(job_queue):
    """Test creating a worker instance."""
    worker = Worker(job_queue)
    assert worker is not None
    assert worker.poll_interval == 1.0
    assert worker.max_poll_interval == 10.0


async def test_worker_custom_intervals(job_queue):
    """Test creating a worker with custom poll intervals."""
    worker = Worker(job_queue, poll_interval=0.5, max_poll_interval=30.0)
    assert worker.poll_interval == 0.5
    assert worker.max_poll_interval == 30.0


async def test_worker_start_stop(job_queue):
    """Test starting and stopping a worker."""
    worker = Worker(job_queue)
    assert not worker.is_running()

    await worker.start()
    assert worker.is_running()

    await worker.stop()
    assert not worker.is_running()


async def test_worker_processes_job(job_queue):
    """Test that worker processes a job successfully."""
    data = {"value": 42}
    job_id = await job_queue.enqueue(success_task, data)

    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()

    # Wait for job to be processed
    await asyncio.sleep(0.5)
    await worker.stop()

    job = await job_queue.get_job(job_id)
    assert job.status == "completed"


async def test_worker_processes_multiple_jobs(job_queue):
    """Test that worker processes multiple jobs."""
    job_ids = []
    for i in range(3):
        job_id = await job_queue.enqueue(success_task, {"n": i})
        job_ids.append(job_id)

    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()

    # Wait for all jobs to be processed
    await asyncio.sleep(1.0)
    await worker.stop()

    for job_id in job_ids:
        job = await job_queue.get_job(job_id)
        assert job.status == "completed"


async def test_worker_current_job(job_queue):
    """Test tracking current job ID."""
    worker = Worker(job_queue)
    assert worker.current_job() is None

    await worker.start()
    # Current job might be None if no jobs in queue
    await worker.stop()


async def test_worker_respects_priority(job_queue):
    """Test that worker processes higher priority jobs first."""
    await job_queue.enqueue(success_task, {"priority": "low"}, priority=1)
    high_id = await job_queue.enqueue(success_task, {"priority": "high"}, priority=10)

    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()

    # Give some time for processing
    await asyncio.sleep(0.3)

    # High priority should be completed first
    high_job = await job_queue.get_job(high_id)
    assert high_job.status == "completed"

    await worker.stop()


async def test_worker_handles_delayed_jobs(job_queue):
    """Test that worker waits for delayed jobs."""
    # Job with short delay
    job_id = await job_queue.enqueue(success_task, {"value": 42}, delay=0.5)

    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()

    # Check immediately - should still be pending
    await asyncio.sleep(0.2)
    job = await job_queue.get_job(job_id)
    assert job.status == "pending"

    # Wait for delay to pass and processing
    await asyncio.sleep(1.0)

    # Now should be completed
    job = await job_queue.get_job(job_id)
    assert job.status == "completed"

    await worker.stop()


async def test_worker_stop_twice(job_queue):
    """Test that stopping worker twice doesn't cause issues."""
    worker = Worker(job_queue)
    await worker.start()
    await worker.stop()
    await worker.stop()  # Should not raise error


async def test_worker_start_twice(job_queue):
    """Test that starting worker twice is handled gracefully."""
    worker = Worker(job_queue)
    await worker.start()
    await worker.start()  # Should log warning but not error
    assert worker.is_running()
    await worker.stop()
