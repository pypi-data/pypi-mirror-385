"""Account information resources."""

from legnext._internal.http_client import AsyncHTTPClient, HTTPClient
from legnext.types.responses import AccountInfo, ActiveTasksResponse


class AccountResource:
    """Synchronous account operations resource."""

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the account resource."""
        self._http = http

    def get_info(self) -> AccountInfo:
        """Get account information.

        Returns:
            Account information including subscription, balance, and quota

        Example:
            ```python
            info = client.account.get_info()
            print(f"Plan: {info.plan}")
            print(f"Balance: {info.balance}")
            print(f"Remaining quota: {info.quota.remaining}")
            ```
        """
        data = self._http.request("GET", "/account/info")
        return AccountInfo.model_validate(data)

    def get_active_tasks(self) -> ActiveTasksResponse:
        """Get list of currently active tasks.

        Returns:
            Active tasks response with task list and limits

        Example:
            ```python
            active = client.account.get_active_tasks()
            print(f"Active tasks: {active.total_active}/{active.concurrent_limit}")
            for task in active.tasks:
                print(f"  {task.job_id}: {task.status} ({task.progress}%)")
            ```
        """
        data = self._http.request("GET", "/account/active_tasks")
        return ActiveTasksResponse.model_validate(data)


class AsyncAccountResource:
    """Asynchronous account operations resource."""

    def __init__(self, http: AsyncHTTPClient) -> None:
        """Initialize the async account resource."""
        self._http = http

    async def get_info(self) -> AccountInfo:
        """Get account information (async).

        Returns:
            Account information including subscription, balance, and quota
        """
        data = await self._http.request("GET", "/account/info")
        return AccountInfo.model_validate(data)

    async def get_active_tasks(self) -> ActiveTasksResponse:
        """Get list of currently active tasks (async).

        Returns:
            Active tasks response with task list and limits
        """
        data = await self._http.request("GET", "/account/active_tasks")
        return ActiveTasksResponse.model_validate(data)
