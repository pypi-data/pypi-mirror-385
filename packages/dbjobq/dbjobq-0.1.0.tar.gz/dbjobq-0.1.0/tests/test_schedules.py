"""Tests for Schedule functionality."""

import asyncio
import time

from dbjobq import Worker, job
from dbjobq.models import Schedule


@job()
def scheduled_task(data):
    """Task for scheduled execution."""
    data["executed"] = True
    data["timestamp"] = time.time()


async def test_create_cron_schedule(storage):
    """Test creating a cron schedule."""
    schedule = Schedule(
        id="test-cron-1",
        job_type="test.task",
        job_data={"message": "Hello"},
        schedule_type="cron",
        schedule_expression="0 * * * *",  # Every hour
        next_run=time.time() + 3600,
        enabled=True,
        priority=5,
        max_retries=2,
    )
    await storage.create_schedule(schedule)

    retrieved = await storage.get_schedule("test-cron-1")
    assert retrieved is not None
    assert retrieved.id == "test-cron-1"
    assert retrieved.schedule_type == "cron"
    assert retrieved.schedule_expression == "0 * * * *"
    assert retrieved.enabled is True


async def test_create_interval_schedule(storage):
    """Test creating an interval schedule."""
    schedule = Schedule(
        id="test-interval-1",
        job_type="test.task",
        job_data={"message": "World"},
        schedule_type="interval",
        schedule_expression="300",  # Every 5 minutes
        next_run=time.time() + 300,
        enabled=True,
        priority=3,
        max_retries=1,
    )
    await storage.create_schedule(schedule)

    retrieved = await storage.get_schedule("test-interval-1")
    assert retrieved is not None
    assert retrieved.schedule_type == "interval"
    assert retrieved.schedule_expression == "300"


async def test_list_schedules(storage):
    """Test listing all schedules."""
    schedule1 = Schedule(
        id="sched-1",
        job_type="test.task1",
        job_data={},
        schedule_type="cron",
        schedule_expression="* * * * *",
        next_run=time.time(),
        enabled=True,
    )
    schedule2 = Schedule(
        id="sched-2",
        job_type="test.task2",
        job_data={},
        schedule_type="interval",
        schedule_expression="60",
        next_run=time.time(),
        enabled=False,
    )

    await storage.create_schedule(schedule1)
    await storage.create_schedule(schedule2)

    all_schedules = await storage.list_schedules()
    assert len(all_schedules) == 2

    enabled_only = await storage.list_schedules(enabled_only=True)
    assert len(enabled_only) == 1
    assert enabled_only[0].id == "sched-1"


async def test_update_schedule(storage):
    """Test updating a schedule by recreating it."""
    schedule = Schedule(
        id="update-test",
        job_type="test.task",
        job_data={},
        schedule_type="cron",
        schedule_expression="* * * * *",
        next_run=time.time(),
        enabled=True,
    )
    await storage.create_schedule(schedule)

    # Delete and recreate with updated values
    await storage.delete_schedule("update-test")
    schedule.enabled = False
    await storage.create_schedule(schedule)

    updated = await storage.get_schedule("update-test")
    assert updated.enabled is False


async def test_delete_schedule(storage):
    """Test deleting a schedule."""
    schedule = Schedule(
        id="delete-test",
        job_type="test.task",
        job_data={},
        schedule_type="cron",
        schedule_expression="* * * * *",
        next_run=time.time(),
        enabled=True,
    )
    await storage.create_schedule(schedule)

    await storage.delete_schedule("delete-test")

    deleted = await storage.get_schedule("delete-test")
    assert deleted is None


async def test_get_due_schedules(storage):
    """Test getting schedules that are due to run."""
    now = time.time()

    # Create a due schedule (past time)
    due_schedule = Schedule(
        id="due-schedule",
        job_type="test.task",
        job_data={},
        schedule_type="cron",
        schedule_expression="* * * * *",
        next_run=now - 60,  # 1 minute ago
        enabled=True,
    )

    # Create a future schedule
    future_schedule = Schedule(
        id="future-schedule",
        job_type="test.task",
        job_data={},
        schedule_type="cron",
        schedule_expression="* * * * *",
        next_run=now + 3600,  # 1 hour from now
        enabled=True,
    )

    # Create a disabled schedule
    disabled_schedule = Schedule(
        id="disabled-schedule",
        job_type="test.task",
        job_data={},
        schedule_type="cron",
        schedule_expression="* * * * *",
        next_run=now - 60,
        enabled=False,
    )

    await storage.create_schedule(due_schedule)
    await storage.create_schedule(future_schedule)
    await storage.create_schedule(disabled_schedule)

    due_schedules = await storage.get_due_schedules()
    assert len(due_schedules) == 1
    assert due_schedules[0].id == "due-schedule"


async def test_update_schedule_next_run(storage):
    """Test updating schedule's next run time."""
    now = time.time()
    schedule = Schedule(
        id="next-run-test",
        job_type="test.task",
        job_data={},
        schedule_type="interval",
        schedule_expression="300",
        next_run=now,
        enabled=True,
    )
    await storage.create_schedule(schedule)

    # Update next run
    new_next_run = now + 300
    await storage.update_schedule_next_run("next-run-test", new_next_run, now)

    updated = await storage.get_schedule("next-run-test")
    assert abs(updated.next_run - new_next_run) < 1  # Allow 1 second tolerance
    assert abs(updated.last_run - now) < 1


async def test_worker_processes_due_schedules(job_queue, storage):
    """Test that worker polls and processes due schedules."""
    now = time.time()

    # Create a schedule that's already due
    schedule = Schedule(
        id="worker-schedule-test",
        job_type=f"{scheduled_task.__module__}.{scheduled_task.__name__}",
        job_data={"message": "Scheduled execution"},
        schedule_type="interval",
        schedule_expression="60",  # Every minute
        next_run=now - 5,  # 5 seconds ago (already due)
        enabled=True,
        priority=5,
        max_retries=2,
    )
    await storage.create_schedule(schedule)

    # Start worker with schedule polling
    worker = Worker(job_queue, poll_interval=0.1, schedule_poll_interval=0.5)
    await worker.start()

    # Wait for schedule to be polled and job to be enqueued and processed
    await asyncio.sleep(2.0)
    await worker.stop()

    # Check that a job was created from the schedule
    jobs = await job_queue.list_jobs()
    schedule_jobs = [j for j in jobs if j.type == f"{scheduled_task.__module__}.{scheduled_task.__name__}"]
    assert len(schedule_jobs) >= 1

    # At least one should be completed or running
    completed_or_running = [j for j in schedule_jobs if j.status in ["completed", "running"]]
    assert len(completed_or_running) >= 1


async def test_cron_schedule_calculation(job_queue, storage):
    """Test that cron expressions are correctly parsed and next run is calculated."""
    now = time.time()

    # Create a cron schedule for every minute
    schedule = Schedule(
        id="cron-calc-test",
        job_type=f"{scheduled_task.__module__}.{scheduled_task.__name__}",
        job_data={"test": "cron"},
        schedule_type="cron",
        schedule_expression="* * * * *",  # Every minute
        next_run=now - 10,  # Already due
        enabled=True,
    )
    await storage.create_schedule(schedule)

    worker = Worker(job_queue, poll_interval=0.1, schedule_poll_interval=0.5)
    await worker.start()
    await asyncio.sleep(2.0)
    await worker.stop()

    # Check that next_run was updated
    updated_schedule = await storage.get_schedule("cron-calc-test")
    assert updated_schedule.next_run > now  # Next run should be in the future
    assert updated_schedule.last_run is not None  # Should have been executed


async def test_interval_schedule_calculation(job_queue, storage):
    """Test that interval schedules correctly calculate next run."""
    now = time.time()
    interval_seconds = 30

    schedule = Schedule(
        id="interval-calc-test",
        job_type=f"{scheduled_task.__module__}.{scheduled_task.__name__}",
        job_data={"test": "interval"},
        schedule_type="interval",
        schedule_expression=str(interval_seconds),
        next_run=now - 5,  # Already due
        enabled=True,
    )
    await storage.create_schedule(schedule)

    worker = Worker(job_queue, poll_interval=0.1, schedule_poll_interval=0.5)
    await worker.start()
    await asyncio.sleep(2.0)
    await worker.stop()

    # Check that next_run was updated to current time + interval
    updated_schedule = await storage.get_schedule("interval-calc-test")
    expected_next = updated_schedule.last_run + interval_seconds
    assert abs(updated_schedule.next_run - expected_next) < 2  # Allow 2 second tolerance


async def test_disabled_schedule_not_executed(job_queue, storage):
    """Test that disabled schedules are not executed."""
    now = time.time()

    schedule = Schedule(
        id="disabled-test",
        job_type=f"{scheduled_task.__module__}.{scheduled_task.__name__}",
        job_data={"test": "disabled"},
        schedule_type="interval",
        schedule_expression="60",
        next_run=now - 10,  # Already due
        enabled=False,  # But disabled
    )
    await storage.create_schedule(schedule)

    worker = Worker(job_queue, poll_interval=0.1, schedule_poll_interval=0.5)
    await worker.start()
    await asyncio.sleep(2.0)
    await worker.stop()

    # Should not have created any jobs
    jobs = await job_queue.list_jobs()
    assert len(jobs) == 0


async def test_schedule_with_priority(job_queue, storage):
    """Test that scheduled jobs inherit priority from schedule."""
    now = time.time()
    high_priority = 10

    schedule = Schedule(
        id="priority-test",
        job_type=f"{scheduled_task.__module__}.{scheduled_task.__name__}",
        job_data={"test": "priority"},
        schedule_type="interval",
        schedule_expression="60",
        next_run=now - 5,
        enabled=True,
        priority=high_priority,
    )
    await storage.create_schedule(schedule)

    worker = Worker(job_queue, poll_interval=0.1, schedule_poll_interval=0.5)
    await worker.start()
    await asyncio.sleep(2.0)
    await worker.stop()

    # Check that job was created with correct priority
    jobs = await job_queue.list_jobs()
    if jobs:
        assert jobs[0].priority == high_priority


async def test_schedule_with_max_retries(job_queue, storage):
    """Test that scheduled jobs inherit max_retries from schedule."""
    now = time.time()
    max_retries = 5

    schedule = Schedule(
        id="retries-test",
        job_type=f"{scheduled_task.__module__}.{scheduled_task.__name__}",
        job_data={"test": "retries"},
        schedule_type="interval",
        schedule_expression="60",
        next_run=now - 5,
        enabled=True,
        max_retries=max_retries,
    )
    await storage.create_schedule(schedule)

    worker = Worker(job_queue, poll_interval=0.1, schedule_poll_interval=0.5)
    await worker.start()
    await asyncio.sleep(2.0)
    await worker.stop()

    # Check that job was created with correct max_retries
    jobs = await job_queue.list_jobs()
    if jobs:
        assert jobs[0].max_retries == max_retries
