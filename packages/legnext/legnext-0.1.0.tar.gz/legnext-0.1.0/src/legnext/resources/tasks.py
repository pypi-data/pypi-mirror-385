"""Task management resources."""

import time
from typing import Callable, Optional

from legnext._internal.http_client import AsyncHTTPClient, HTTPClient
from legnext.types.enums import JobStatus
from legnext.types.errors import TimeoutError
from legnext.types.responses import TaskResponse


class TasksResource:
    """Synchronous task management resource."""

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the tasks resource."""
        self._http = http

    def get(self, job_id: str) -> TaskResponse:
        """Get the status and results of a task.

        Args:
            job_id: The unique identifier of the job

        Returns:
            Task response with current status and results

        Example:
            ```python
            task = client.tasks.get("job-id-here")
            print(f"Status: {task.status}")
            if task.status == JobStatus.COMPLETED:
                print(f"Results: {task.output}")
            ```
        """
        data = self._http.request("GET", f"/job/{job_id}")
        return TaskResponse.model_validate(data)

    def wait_for_completion(
        self,
        job_id: str,
        *,
        timeout: float = 300.0,
        poll_interval: float = 3.0,
        on_progress: Optional[Callable[[TaskResponse], None]] = None,
    ) -> TaskResponse:
        """Wait for a task to complete.

        Args:
            job_id: The job ID to wait for
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Time between status checks in seconds (default: 3)
            on_progress: Optional callback called on each status check

        Returns:
            Completed task response

        Raises:
            TimeoutError: If task doesn't complete within timeout
            LegnextAPIError: If task fails

        Example:
            ```python
            def print_progress(task):
                print(f"Status: {task.status}")

            result = client.tasks.wait_for_completion(
                job_id="job-id",
                on_progress=print_progress
            )
            print(f"Completed: {result.output.image_urls}")
            ```
        """
        start_time = time.time()

        while True:
            task = self.get(job_id)

            if on_progress:
                on_progress(task)

            if task.status == JobStatus.COMPLETED:
                return task

            if task.status == JobStatus.FAILED:
                error_msg = task.error.message if task.error else "Task failed"
                from legnext.types.errors import LegnextAPIError

                raise LegnextAPIError(error_msg, 500, task.error)

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Task {job_id} did not complete within {timeout} seconds"
                )

            time.sleep(poll_interval)


class AsyncTasksResource:
    """Asynchronous task management resource."""

    def __init__(self, http: AsyncHTTPClient) -> None:
        """Initialize the async tasks resource."""
        self._http = http

    async def get(self, job_id: str) -> TaskResponse:
        """Get the status and results of a task (async).

        Args:
            job_id: The unique identifier of the job

        Returns:
            Task response with current status and results
        """
        data = await self._http.request("GET", f"/job/{job_id}")
        return TaskResponse.model_validate(data)

    async def wait_for_completion(
        self,
        job_id: str,
        *,
        timeout: float = 300.0,
        poll_interval: float = 3.0,
        on_progress: Optional[Callable[[TaskResponse], None]] = None,
    ) -> TaskResponse:
        """Wait for a task to complete (async).

        Args:
            job_id: The job ID to wait for
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Time between status checks in seconds (default: 3)
            on_progress: Optional callback called on each status check

        Returns:
            Completed task response

        Raises:
            TimeoutError: If task doesn't complete within timeout
            LegnextAPIError: If task fails
        """
        import asyncio

        start_time = time.time()

        while True:
            task = await self.get(job_id)

            if on_progress:
                on_progress(task)

            if task.status == JobStatus.COMPLETED:
                return task

            if task.status == JobStatus.FAILED:
                error_msg = task.error.message if task.error else "Task failed"
                from legnext.types.errors import LegnextAPIError

                raise LegnextAPIError(error_msg, 500, task.error)

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Task {job_id} did not complete within {timeout} seconds"
                )

            await asyncio.sleep(poll_interval)
