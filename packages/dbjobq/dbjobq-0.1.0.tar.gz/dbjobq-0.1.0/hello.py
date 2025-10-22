import time

from dbjobq import JobQueue, Worker, job
from dbjobq.storage import SQLAlchemyStorage


@job(max_retries=3, priority=10)
def hello_task(data):
    print(f"Hello, {data['name']}!")


@job(max_retries=2)
def failing_task(data):
    """A task that fails to demonstrate retry logic."""
    attempt = data.get("attempt", 1)
    print(f"Failing task attempt {attempt}")
    if attempt < 3:
        raise ValueError(f"Simulated failure on attempt {attempt}")
    print("Finally succeeded!")


def main():
    # Create storage (file-based SQLite for demo)
    storage = SQLAlchemyStorage("sqlite:///test.db")
    job_queue = JobQueue(storage)

    # Enqueue a regular job
    job_id = job_queue.enqueue(hello_task, {"name": "World"})
    print(f"Enqueued job {job_id}")

    # Enqueue a delayed job (will execute after 3 seconds)
    delayed_id = job_queue.enqueue(hello_task, {"name": "Future"}, delay=3)
    print(f"Enqueued delayed job {delayed_id} (will run in 3 seconds)")

    # Enqueue a high priority job
    priority_id = job_queue.enqueue(hello_task, {"name": "Important"}, priority=100)
    print(f"Enqueued priority job {priority_id}")

    # Enqueue a task that will fail and retry
    fail_id = job_queue.enqueue(failing_task, {"attempt": 1})
    print(f"Enqueued failing task {fail_id} (will retry)")

    # Inspect the queue
    print("\n--- Queue Status ---")
    pending = job_queue.get_pending_jobs()
    print(f"Pending jobs: {len(pending)}")

    running = job_queue.get_running_jobs()
    print(f"Running jobs: {len(running)}")

    completed = job_queue.get_completed_jobs()
    print(f"Completed jobs: {len(completed)}")

    failed = job_queue.get_failed_jobs()
    print(f"Failed jobs: {len(failed)}")

    # Get specific job
    job = job_queue.get_job(job_id)
    if job:
        print(f"\nJob {job.id}: {job.type} - {job.status}")
        print(f"Priority: {job.priority}, Max Retries: {job.max_retries}")
        print(f"Data: {job.data}")

    # Start worker
    worker = Worker(job_queue)
    worker.start()

    # Wait for jobs to process
    time.sleep(6)

    # Check status again
    print("\n--- After processing ---")
    pending = job_queue.get_pending_jobs()
    print(f"Pending jobs: {len(pending)}")

    completed = job_queue.get_completed_jobs()
    print(f"Completed jobs: {len(completed)}")

    failed = job_queue.get_failed_jobs()
    print(f"Failed jobs: {len(failed)}")

    if completed:
        print("\nCompleted jobs:")
        for j in completed[:5]:
            print(f"  - {j.id}: {j.type} (attempts: {j.attempts})")

    if failed:
        print("\nFailed jobs:")
        for j in failed[:5]:
            print(f"  - {j.id}: {j.type}")
            print(f"    Error: {j.error[:100]}...")

    # Stop worker
    worker.stop()
    print("\nDone")


if __name__ == "__main__":
    main()
