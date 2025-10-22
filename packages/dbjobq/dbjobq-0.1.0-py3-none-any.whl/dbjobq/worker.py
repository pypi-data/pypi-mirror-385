import asyncio
import logging
import signal
import time
from typing import TYPE_CHECKING, Optional

from croniter import croniter

from .queue import JobQueue

if TYPE_CHECKING:
    from .models import Schedule

logger = logging.getLogger(__name__)


class Worker:
    def __init__(
        self,
        job_queue: JobQueue,
        poll_interval: float = 1.0,
        max_poll_interval: float = 10.0,
        graceful_shutdown: bool = True,
        schedule_poll_interval: float = 60.0,
    ) -> None:
        """Initialize an async worker.

        Args:
            job_queue (JobQueue): The job queue to process.
            poll_interval (float): Initial polling interval in seconds. Defaults to 1.0.
            max_poll_interval (float): Maximum polling interval (with backoff). Defaults to 10.0.
            graceful_shutdown (bool): Wait for current job to finish on shutdown. Defaults to True.
            schedule_poll_interval (float): Interval for checking due schedules in seconds. Defaults to 60.0.
        """
        self.job_queue = job_queue
        self.poll_interval = poll_interval
        self.max_poll_interval = max_poll_interval
        self.graceful_shutdown = graceful_shutdown
        self.schedule_poll_interval = schedule_poll_interval
        self._stop = False
        self._paused = False
        self._task: Optional[asyncio.Task] = None
        self._schedule_task: Optional[asyncio.Task] = None
        self._current_job_id: Optional[str] = None
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Setup graceful shutdown on SIGTERM/SIGINT."""

        def handle_signal(signum: int, _frame: Optional[object]) -> None:
            logger.info("Received signal %s, shutting down...", signum)
            # Store task reference to avoid RUF006 warning
            _ = asyncio.create_task(self.stop())  # noqa: RUF006

        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)

    async def start(self) -> None:
        """Start the worker with job processing and schedule polling."""
        if self._task and not self._task.done():
            logger.warning("Worker is already running")
            return

        logger.info("Starting worker")
        self._stop = False
        self._paused = False

        # Start job processing task
        self._task = asyncio.create_task(self._run())

        # Start schedule polling task
        self._schedule_task = asyncio.create_task(self._poll_schedules())

        logger.info("Worker started")

    async def stop(self) -> None:
        """Stop the worker gracefully."""
        logger.info("Stopping worker")
        self._stop = True

        # Wait for tasks to complete
        tasks = []
        if self._task and not self._task.done():
            tasks.append(self._task)
        if self._schedule_task and not self._schedule_task.done():
            tasks.append(self._schedule_task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Worker stopped")

    async def pause(self) -> None:
        """Pause job processing (schedules still poll)."""
        if self._paused:
            logger.warning("Worker is already paused")
            return

        logger.info("Pausing worker")
        self._paused = True
        logger.info("Worker paused")

    async def resume(self) -> None:
        """Resume job processing."""
        if not self._paused:
            logger.warning("Worker is not paused")
            return

        logger.info("Resuming worker")
        self._paused = False
        logger.info("Worker resumed")

    async def _run(self) -> None:
        """Main worker loop with adaptive polling."""
        current_poll_interval = self.poll_interval

        while not self._stop:
            # Skip processing if paused
            if self._paused:
                await asyncio.sleep(1.0)
                continue

            job = await self.job_queue.dequeue()
            if job:
                # Job found, reset poll interval
                current_poll_interval = self.poll_interval
                self._current_job_id = job.id

                try:
                    logger.info("Processing job %s", self._current_job_id)
                    await self.job_queue.execute_job(job)
                    logger.info("Completed job %s", self._current_job_id)
                except Exception as e:
                    logger.exception("Error executing job %s: %s", self._current_job_id, e)
                finally:
                    self._current_job_id = None
            else:
                # No job found, increase poll interval (exponential backoff)
                current_poll_interval = min(current_poll_interval * 1.5, self.max_poll_interval)
                await asyncio.sleep(current_poll_interval)

    async def _poll_schedules(self) -> None:
        """Poll for due schedules and enqueue jobs."""
        while not self._stop:
            try:
                # Get due schedules (current_time is calculated inside the method)
                due_schedules = await self.job_queue.storage.get_due_schedules()

                for schedule in due_schedules:
                    try:
                        # Enqueue job for this schedule
                        await self.job_queue.enqueue(
                            schedule.job_type,
                            schedule.job_data,
                            priority=schedule.priority,
                            max_retries=schedule.max_retries,
                        )
                        logger.info("Enqueued job from schedule %s", schedule.id)

                        # Calculate next run time
                        current_time = time.time()
                        next_run = self._calculate_next_run(schedule)
                        if next_run:
                            await self.job_queue.storage.update_schedule_next_run(schedule.id, next_run, current_time)
                        else:
                            # Disable schedule if no next run (one-time or invalid)
                            logger.warning("No next run for schedule %s, disabling", schedule.id)
                            await self.job_queue.storage.enable_schedule(schedule.id, False)

                    except Exception as e:
                        logger.exception("Error processing schedule %s: %s", schedule.id, e)

            except Exception as e:
                logger.exception("Error polling schedules: %s", e)

            # Sleep until next poll
            await asyncio.sleep(self.schedule_poll_interval)

    def _calculate_next_run(self, schedule: "Schedule") -> Optional[float]:
        """Calculate the next run time for a schedule.

        Args:
            schedule: The schedule object with schedule_type and schedule_expression.

        Returns:
            Optional[float]: Unix timestamp of next run, or None if no next run.
        """
        try:
            if schedule.schedule_type == "cron":
                # Use croniter to calculate next run from cron expression
                cron = croniter(schedule.schedule_expression, time.time())
                return cron.get_next()
            elif schedule.schedule_type == "interval":
                # Interval in seconds
                interval = float(schedule.schedule_expression)
                return time.time() + interval
            else:
                logger.error("Unknown schedule type: %s", schedule.schedule_type)
                return None
        except Exception as e:
            logger.exception("Error calculating next run for schedule: %s", e)
            return None

    def is_running(self) -> bool:
        """Check if worker is currently running.

        Returns:
            bool: True if worker task is active.
        """
        return self._task is not None and not self._task.done()

    def is_paused(self) -> bool:
        """Check if worker is currently paused.

        Returns:
            bool: True if worker is paused.
        """
        return self._paused

    def current_job(self) -> Optional[str]:
        """Get the ID of the currently processing job.

        Returns:
            Optional[str]: Job ID or None if idle.
        """
        return self._current_job_id
