"""Integration tests for the complete job queue system."""

import asyncio

from dbjobq import Worker, job
from dbjobq import job as job_decorator  # For tests that need a fresh decorator


@job(max_retries=3, priority=5)
def integration_task(data):
    """Task for integration testing."""
    data["processed"] = True
    data["multiplied"] = data["value"] * 2


@job(max_retries=0)
def flaky_task(data):
    """Task that succeeds on first try."""
    data["success"] = True


async def test_end_to_end_job_processing(job_queue):
    """Test complete flow: enqueue -> dequeue -> process -> complete."""
    # Enqueue job
    job_id = await job_queue.enqueue(integration_task, {"value": 21})

    # Dequeue job
    job = await job_queue.dequeue()
    assert job is not None
    assert job.id == job_id
    assert job.status == "running"

    # Execute job
    await job_queue.execute_job(job)

    # Verify completion
    completed_job = await job_queue.get_job(job_id)
    assert completed_job.status == "completed"


async def test_worker_end_to_end(job_queue):
    """Test complete flow with worker processing."""
    # Enqueue multiple jobs
    job_ids = []
    for i in range(5):
        job_id = await job_queue.enqueue(integration_task, {"value": i})
        job_ids.append(job_id)

    # Start worker
    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()

    # Wait for processing
    await asyncio.sleep(1.0)
    await worker.stop()

    # Verify all jobs completed
    for job_id in job_ids:
        job = await job_queue.get_job(job_id)
        assert job.status == "completed"


async def test_retry_mechanism_integration(job_queue):
    """Test retry mechanism with worker."""
    job_id = await job_queue.enqueue(flaky_task, {"value": 42})

    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()

    # Wait for job to complete
    await asyncio.sleep(1.0)
    await worker.stop()

    # Job should complete successfully
    job = await job_queue.get_job(job_id)
    assert job.status == "completed"


async def test_priority_queue_integration(job_queue):
    """Test priority-based job processing."""
    # Enqueue jobs with different priorities
    low_id = await job_queue.enqueue(integration_task, {"priority": "low"}, priority=1)
    high_id = await job_queue.enqueue(integration_task, {"priority": "high"}, priority=10)
    medium_id = await job_queue.enqueue(integration_task, {"priority": "medium"}, priority=5)

    # Dequeue and verify order
    job1 = await job_queue.dequeue()
    job2 = await job_queue.dequeue()
    job3 = await job_queue.dequeue()

    assert job1.id == high_id
    assert job2.id == medium_id
    assert job3.id == low_id


async def test_delayed_execution_integration(job_queue):
    """Test delayed job execution."""
    # Enqueue with short delay
    job_id = await job_queue.enqueue(integration_task, {"value": 42}, delay=0.5)

    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()

    # Check status before delay expires
    await asyncio.sleep(0.2)
    job = await job_queue.get_job(job_id)
    assert job.status == "pending"

    # Wait for delay and processing
    await asyncio.sleep(1.0)

    # Job should now be completed
    job = await job_queue.get_job(job_id)
    assert job.status == "completed"

    await worker.stop()


async def test_multiple_workers_scenario(job_queue):
    """Test scenario with multiple workers (simulated with sequential start/stop)."""
    # Enqueue many jobs
    for i in range(10):
        await job_queue.enqueue(integration_task, {"value": i})

    # Start first worker
    worker1 = Worker(job_queue, poll_interval=0.1)
    await worker1.start()
    await asyncio.sleep(0.5)

    # Check progress
    pending = await job_queue.get_pending_jobs()
    completed = await job_queue.get_completed_jobs()
    assert len(pending) + len(completed) == 10
    assert len(completed) > 0

    await worker1.stop()


async def test_job_failure_and_recovery(job_queue):
    """Test job failure handling and status tracking."""

    @job_decorator(max_retries=1)
    def always_failing_task(_data):
        raise RuntimeError("This task always fails")

    job_id = await job_queue.enqueue(always_failing_task, {"value": 42})

    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()

    # Wait for initial attempt and retry (exponential backoff: 1s)
    await asyncio.sleep(3.0)
    await worker.stop()

    # Should be failed after exhausting retries
    job = await job_queue.get_job(job_id)
    assert job.status == "failed"
    assert "RuntimeError: This task always fails" in job.error
    # With max_retries=1: initial attempt (0) + 1 retry = attempts becomes 1
    assert job.attempts == 1


async def test_mixed_job_types_integration(job_queue):
    """Test processing different types of jobs together."""

    @job(priority=10)
    def high_priority_task(data):
        data["high"] = True

    @job(max_retries=3)
    def retriable_task(data):
        data["retriable"] = True

    @job()
    def simple_task(data):
        data["simple"] = True

    # Enqueue mixed jobs
    high_id = await job_queue.enqueue(high_priority_task, {})
    retry_id = await job_queue.enqueue(retriable_task, {})
    simple_id = await job_queue.enqueue(simple_task, {})

    worker = Worker(job_queue, poll_interval=0.1)
    await worker.start()
    await asyncio.sleep(0.5)
    await worker.stop()

    # All should complete
    assert (await job_queue.get_job(high_id)).status == "completed"
    assert (await job_queue.get_job(retry_id)).status == "completed"
    assert (await job_queue.get_job(simple_id)).status == "completed"
