"""API client for communicating with AnyTask backend."""

import os
from typing import Any
from urllib.parse import urljoin

import httpx


class APIError(Exception):
    """Raised when API request fails."""

    def __init__(
        self, status_code: int, message: str, details: dict[str, Any] | None = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"API Error {status_code}: {message}")


class AnyTaskClient:
    """Client for AnyTask backend API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        workspace_id: int | None = None,
    ):
        """Initialize client.

        Args:
            base_url: Backend URL (defaults to ANYTASK_API_URL env var)
            api_key: Agent API key (defaults to ANYTASK_API_KEY env var)
            workspace_id: Default workspace ID (defaults to ANYTASK_WORKSPACE_ID env var)
        """
        self.base_url = (
            base_url or os.getenv("ANYTASK_API_URL") or "http://0.0.0.0:8000"
        )
        self.api_key = api_key or os.getenv("ANYTASK_API_KEY") or ""
        self.workspace_id: int = workspace_id or int(
            os.getenv("ANYTASK_WORKSPACE_ID", "0")
        )

        if not self.api_key:
            raise ValueError("API key is required (set ANYTASK_API_KEY)")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-API-Key": self.api_key},
            timeout=30.0,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request.

        Args:
            method: HTTP method
            path: API path
            json: JSON body
            params: Query parameters

        Returns:
            Response data

        Raises:
            APIError: If request fails
        """
        url: str = urljoin(self.base_url, path)
        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=json,
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            # Handle success response format
            if data.get("success"):
                return data.get("data", {})

            return data

        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.content else {}
            raise APIError(
                status_code=e.response.status_code,
                message=error_data.get("message", str(e)),
                details=error_data,
            )
        except httpx.RequestError as e:
            raise APIError(
                status_code=0,
                message=f"Request failed: {e}",
            )

    # Workspace methods
    async def get_workspaces(self) -> dict[str, Any]:
        """Get all workspaces for the authenticated agent."""
        return await self._request("GET", "/v1/workspaces")

    async def get_workspace(self, workspace_id: int) -> dict[str, Any]:
        """Get workspace by ID."""
        return await self._request("GET", f"/v1/workspaces/{workspace_id}")

    async def get_current_workspace(self) -> dict[str, Any]:
        """Get or create default workspace."""
        return await self._request("GET", "/v1/workspaces/current")

    # Project methods
    async def get_projects(self, workspace_id: int) -> dict[str, Any]:
        """Get all projects in workspace."""
        return await self._request("GET", f"/v1/workspaces/{workspace_id}/projects")

    async def get_current_project(self, workspace_id: int) -> dict[str, Any]:
        """Get or create default project."""
        return await self._request(
            "GET", f"/v1/workspaces/{workspace_id}/projects/current"
        )

    # Task methods
    async def list_tasks(
        self,
        workspace_id: int,
        project_id: int | None = None,
        status: str | None = None,
        assignee_id: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """List tasks with optional filters."""
        params: dict[str, Any] = {"limit": limit}
        if project_id:
            params["project_id"] = project_id
        if status:
            params["status"] = status
        if assignee_id:
            params["assignee_id"] = assignee_id

        result = await self._request(
            "GET", f"/v1/workspaces/{workspace_id}/tasks", params=params
        )
        # Return the list from the response
        return result if isinstance(result, list) else result.get("tasks", [])

    async def get_task(self, workspace_id: int, task_identifier: str) -> dict[str, Any]:
        """Get task by identifier (e.g., 'DEV-123')."""
        return await self._request(
            "GET", f"/v1/workspaces/{workspace_id}/tasks/{task_identifier}"
        )

    async def create_task(
        self,
        workspace_id: int,
        title: str,
        description: str | None = None,
        project_id: int | None = None,
        priority: int | None = None,
    ) -> dict[str, Any]:
        """Create a new task."""
        json_data: dict[str, Any] = {"title": title}
        if description:
            json_data["description"] = description
        if project_id:
            json_data["project_id"] = project_id
        if priority is not None:
            json_data["priority"] = priority

        return await self._request(
            "POST", f"/v1/workspaces/{workspace_id}/tasks", json=json_data
        )

    async def update_task(
        self,
        workspace_id: int,
        task_identifier: str,
        version: int,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Update task fields."""
        json_data: dict[str, Any] = {"version": version}
        if title:
            json_data["title"] = title
        if description:
            json_data["description"] = description
        if status:
            json_data["status"] = status

        return await self._request(
            "PATCH",
            f"/v1/workspaces/{workspace_id}/tasks/{task_identifier}",
            json=json_data,
        )

    # Attempt methods
    async def start_attempt(
        self,
        workspace_id: int,
        task_identifier: str,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Start a work attempt on a task."""
        json_data: dict[str, Any] = {}
        if notes:
            json_data["notes"] = notes

        return await self._request(
            "POST",
            f"/v1/workspaces/{workspace_id}/tasks/{task_identifier}/attempts",
            json=json_data,
        )

    async def finish_attempt(
        self,
        workspace_id: int,
        task_identifier: str,
        attempt_id: int,
        status: str,
        failure_class: str | None = None,
        cost_tokens: int | None = None,
        wall_clock_ms: int | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Mark an attempt as finished."""
        json_data: dict[str, Any] = {"status": status}
        if failure_class:
            json_data["failure_class"] = failure_class
        if cost_tokens is not None:
            json_data["cost_tokens"] = cost_tokens
        if wall_clock_ms is not None:
            json_data["wall_clock_ms"] = wall_clock_ms
        if notes:
            json_data["notes"] = notes

        return await self._request(
            "PATCH",
            f"/v1/workspaces/{workspace_id}/tasks/{task_identifier}/attempts/{attempt_id}",
            json=json_data,
        )

    # Artifact methods
    async def add_artifact(
        self,
        workspace_id: int,
        task_identifier: str,
        attempt_id: int,
        artifact_type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Upload an artifact for an attempt."""
        json_data: dict[str, Any] = {
            "type": artifact_type,
            "content": content,
        }
        if metadata:
            json_data["metadata"] = metadata

        return await self._request(
            "POST",
            f"/v1/workspaces/{workspace_id}/tasks/{task_identifier}/attempts/{attempt_id}/artifacts",
            json=json_data,
        )

    # Dependency methods
    async def get_dependencies(
        self, workspace_id: int, task_identifier: str
    ) -> dict[str, Any]:
        """Get task dependencies and dependents."""
        return await self._request(
            "GET", f"/v1/workspaces/{workspace_id}/tasks/{task_identifier}/dependencies"
        )

    # Event methods
    async def get_events(
        self, workspace_id: int, task_identifier: str
    ) -> dict[str, Any]:
        """Get task event history."""
        result = await self._request(
            "GET", f"/v1/workspaces/{workspace_id}/tasks/{task_identifier}/events"
        )
        # Return the list from the response
        return result if isinstance(result, list) else result.get("events", [])
