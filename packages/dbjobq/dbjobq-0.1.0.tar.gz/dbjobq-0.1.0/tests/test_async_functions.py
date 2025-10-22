"""Tests for async job function support."""

import asyncio

import pytest

from dbjobq import job

# Track execution for verification
execution_log = []


@job()
def sync_task(data):
    """Synchronous job function."""
    execution_log.append(("sync", data["value"]))
    return f"sync: {data['value']}"


@job()
async def async_task(data):
    """Asynchronous job function."""
    await asyncio.sleep(0.01)  # Simulate async work
    execution_log.append(("async", data["value"]))
    return f"async: {data['value']}"


@job(max_retries=2)
async def async_task_with_retries(data):
    """Async task with retry configuration."""
    if data.get("should_fail"):
        raise ValueError("Intentional failure")
    execution_log.append(("async_retry", data["value"]))
    return f"async_retry: {data['value']}"


@pytest.mark.asyncio
async def test_sync_job_execution(job_queue):
    """Test that synchronous job functions work."""
    execution_log.clear()

    job_id = await job_queue.enqueue(sync_task, {"value": "test1"})
    job = await job_queue.dequeue()

    assert job is not None
    assert job.id == job_id

    await job_queue.execute_job(job)

    # Verify execution
    assert len(execution_log) == 1
    assert execution_log[0] == ("sync", "test1")

    # Verify completion
    completed_job = await job_queue.get_job(job_id)
    assert completed_job.status == "completed"


@pytest.mark.asyncio
async def test_async_job_execution(job_queue):
    """Test that asynchronous job functions work."""
    execution_log.clear()

    job_id = await job_queue.enqueue(async_task, {"value": "test2"})
    job = await job_queue.dequeue()

    assert job is not None
    assert job.id == job_id

    await job_queue.execute_job(job)

    # Verify execution
    assert len(execution_log) == 1
    assert execution_log[0] == ("async", "test2")

    # Verify completion
    completed_job = await job_queue.get_job(job_id)
    assert completed_job.status == "completed"


@pytest.mark.asyncio
async def test_mixed_sync_and_async_jobs(job_queue):
    """Test that sync and async jobs can be enqueued and executed together."""
    execution_log.clear()

    # Enqueue both types
    sync_id = await job_queue.enqueue(sync_task, {"value": "sync_mixed"})
    async_id = await job_queue.enqueue(async_task, {"value": "async_mixed"})

    # Execute both
    job1 = await job_queue.dequeue()
    await job_queue.execute_job(job1)

    job2 = await job_queue.dequeue()
    await job_queue.execute_job(job2)

    # Verify both executed
    assert len(execution_log) == 2

    # Verify both completed
    sync_job = await job_queue.get_job(sync_id)
    async_job = await job_queue.get_job(async_id)

    assert sync_job.status == "completed"
    assert async_job.status == "completed"

    # Verify we have one of each type
    types = {log[0] for log in execution_log}
    assert "sync" in types
    assert "async" in types


@pytest.mark.asyncio
async def test_async_job_with_error_handling(job_queue):
    """Test that async jobs handle errors properly."""
    execution_log.clear()

    @job(max_retries=0)
    async def failing_async_task(_data):  # Prefix unused arg with _
        """Async task that always fails."""
        raise ValueError("Intentional failure for testing")

    job_id = await job_queue.enqueue(failing_async_task, {"value": "fail_test"})

    job_obj = await job_queue.dequeue()
    await job_queue.execute_job(job_obj)

    # Should have failed (no retries)
    job_obj = await job_queue.get_job(job_id)
    assert job_obj.status == "failed"
    assert "Intentional failure for testing" in job_obj.error


@pytest.mark.asyncio
async def test_async_job_can_await_async_operations(job_queue):
    """Test that async jobs can properly await async operations."""
    execution_log.clear()
    results = []

    @job()
    async def async_io_task(data):
        """Async task that performs async I/O operations."""
        # Simulate async I/O
        await asyncio.sleep(0.01)
        results.append(data["value"])
        await asyncio.sleep(0.01)
        results.append(data["value"] + "_done")
        return "completed"

    job_id = await job_queue.enqueue(async_io_task, {"value": "async_io"})

    job_obj = await job_queue.dequeue()
    await job_queue.execute_job(job_obj)

    # Verify async operations completed
    assert len(results) == 2
    assert results[0] == "async_io"
    assert results[1] == "async_io_done"

    # Verify job completed
    job_obj = await job_queue.get_job(job_id)
    assert job_obj.status == "completed"
