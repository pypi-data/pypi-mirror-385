"""HTTP client for AnyTask API."""

import httpx
from typing import Any, Optional

from cli.config import GlobalConfig


class APIClient:
    """Client for interacting with the AnyTask API."""

    def __init__(
        self,
        base_url: str,
        auth_token: Optional[str] = None,
        agent_key: Optional[str] = None,
    ):
        """Initialize the API client.

        Args:
            base_url: Base URL of the API (e.g., http://localhost:8000)
            auth_token: Optional user authentication token
            agent_key: Optional agent API key
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.agent_key = agent_key

        # Build headers
        self.headers = {}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        elif agent_key:
            self.headers["X-API-Key"] = agent_key

    @classmethod
    def from_config(cls, config: Optional[GlobalConfig] = None) -> "APIClient":
        """Create an API client from the global configuration.

        Args:
            config: Optional GlobalConfig instance. If not provided, loads from file.

        Returns:
            APIClient instance configured with current environment settings.
        """
        if config is None:
            config = GlobalConfig.load()

        effective_config = config.get_effective_config()

        return cls(
            base_url=effective_config["api_url"],
            auth_token=effective_config.get("auth_token"),
            agent_key=effective_config.get("agent_key"),
        )

    def _extract_error_message(self, response: httpx.Response) -> str:
        """Extract error message from HTTP error response.

        Args:
            response: The HTTP response object

        Returns:
            Error message string
        """
        try:
            error_data = response.json()
            # Try to extract message from error response
            if isinstance(error_data, dict):
                # Check for standard error format
                if "message" in error_data:
                    return error_data["message"]
                # Check for detail field (FastAPI default)
                if "detail" in error_data:
                    return error_data["detail"]
        except Exception:
            # If JSON parsing fails, use response text or status
            pass

        # Fallback to response text or status code
        if response.text:
            return response.text
        return f"HTTP {response.status_code}"

    async def health_check(self) -> dict[str, Any]:
        """Check API health status.

        Returns:
            Health status response from the API.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/health",
                headers=self.headers,
                timeout=5.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_current_user(self) -> dict[str, Any]:
        """Get information about the currently authenticated user or agent.

        Returns:
            User/agent information.

        Raises:
            httpx.HTTPError: If the request fails or user is not authenticated.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Try to get user info - this will work for both user tokens and agent keys
            # The backend's get_current_actor() dependency handles both cases
            response = await client.get(
                f"{self.base_url}/v1/workspaces",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()

            # For now, we'll return a basic structure
            # Later we can add a dedicated /v1/auth/whoami endpoint
            return {
                "authenticated": True,
                "type": "agent" if self.agent_key else "user",
            }

    async def list_workspaces(self) -> list[dict[str, Any]]:
        """List accessible workspaces.

        Returns:
            List of workspaces the authenticated user/agent has access to.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle both SuccessResponse format and direct array
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_workspace(self, workspace_id: str) -> dict[str, Any]:
        """Get a specific workspace by ID.

        Args:
            workspace_id: The workspace identifier.

        Returns:
            Workspace details.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_current_workspace(self) -> dict[str, Any]:
        """Get the current/default workspace for the authenticated user.

        Returns the first workspace (by creation date) where the user is a member.
        If the user has no workspaces, automatically creates a default workspace.

        Returns:
            Workspace details.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/current",
                headers=self.headers,
                timeout=10.0,
            )

            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise Exception(error_msg)

            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def create_workspace(
        self,
        name: str,
        identifier: str,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new workspace.

        Args:
            name: Workspace name.
            identifier: Unique workspace identifier (e.g., "PROJ").
            description: Optional workspace description.

        Returns:
            Created workspace details.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/workspaces/",
                headers=self.headers,
                json={
                    "name": name,
                    "identifier": identifier,
                    "description": description,
                },
                timeout=10.0,
            )

            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise Exception(error_msg)

            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    # User Preferences operations

    async def get_user_preferences(self) -> Optional[dict[str, Any]]:
        """Get user preferences (current workspace and project).

        Returns:
            User preferences with current_workspace_id and current_project_id,
            or None if no preferences are set.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/users/me/preferences",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def set_current_workspace(self, workspace_id: int) -> dict[str, Any]:
        """Set the current workspace preference for the user.

        Args:
            workspace_id: The workspace ID to set as current

        Returns:
            Updated user preferences

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.put(
                f"{self.base_url}/v1/users/me/preferences/workspace",
                headers=self.headers,
                json={"workspace_id": workspace_id},
                timeout=10.0,
            )

            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise Exception(error_msg)

            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def set_current_project(
        self, workspace_id: int, project_id: int
    ) -> dict[str, Any]:
        """Set the current project (and workspace) preference for the user.

        Args:
            workspace_id: The workspace ID containing the project
            project_id: The project ID to set as current

        Returns:
            Updated user preferences

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.put(
                f"{self.base_url}/v1/users/me/preferences/project",
                headers=self.headers,
                json={"workspace_id": workspace_id, "project_id": project_id},
                timeout=10.0,
            )

            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise Exception(error_msg)

            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def clear_user_preferences(self) -> dict[str, Any]:
        """Clear user preferences (resets current workspace and project).

        Returns:
            Success response

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.delete(
                f"{self.base_url}/v1/users/me/preferences",
                headers=self.headers,
                timeout=10.0,
            )

            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise Exception(error_msg)

            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    # Task operations

    async def list_tasks(
        self,
        workspace_id: Optional[int] = None,
        project_id: Optional[int] = None,
        status: Optional[list[str]] = None,
        phase: Optional[str] = None,
        owner: Optional[str] = None,
        labels: Optional[list[str]] = None,
        priority_gte: Optional[int] = None,
        priority_lte: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "priority",
        order: str = "desc",
    ) -> dict[str, Any]:
        """List tasks with optional filtering.

        Args:
            workspace_id: Filter by workspace ID
            project_id: Filter by project ID
            status: Filter by status values
            phase: Filter by phase/milestone
            owner: Filter by owner ID or 'me'
            labels: Filter by labels (AND logic)
            priority_gte: Minimum priority
            priority_lte: Maximum priority
            limit: Items per page
            offset: Pagination offset
            sort_by: Sort field
            order: Sort order (asc/desc)

        Returns:
            Task list response with items and pagination

        Raises:
            httpx.HTTPError: If the request fails.
        """
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
            "order": order,
        }

        if workspace_id:
            params["workspace_id"] = workspace_id
        if project_id:
            params["project"] = project_id
        if status:
            params["status"] = ",".join(status)
        if phase:
            params["phase"] = phase
        if owner:
            params["owner"] = owner
        if labels:
            params["labels"] = ",".join(labels)
        if priority_gte is not None:
            params["priority_gte"] = priority_gte
        if priority_lte is not None:
            params["priority_lte"] = priority_lte

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/tasks",
                headers=self.headers,
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_task(self, identifier: str) -> dict[str, Any]:
        """Get a task by identifier or ID.

        Args:
            identifier: Task identifier (DEV-42) or ID

        Returns:
            Task details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/tasks/{identifier}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_task_by_workspace(
        self, workspace_id: int, identifier: str
    ) -> dict[str, Any]:
        """Get a task by identifier or ID within a specific workspace.

        This is the workspace-scoped version of get_task that explicitly
        specifies which workspace to query.

        Args:
            workspace_id: The workspace ID to query
            identifier: Task identifier (DEV-42) or ID

        Returns:
            Task details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}/tasks/{identifier}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def create_task(
        self,
        project_id: int,
        title: str,
        description: Optional[str] = None,
        phase: Optional[str] = None,
        status: str = "backlog",
        priority: int = 0,
        owner_id: Optional[str] = None,
        labels: Optional[list[str]] = None,
        estimate: Optional[int] = None,
        parent_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Create a new task.

        Args:
            project_id: Project ID to create task in
            title: Task title
            description: Optional task description
            phase: Optional phase/milestone identifier
            status: Task status (default: backlog)
            priority: Task priority (default: 0)
            owner_id: Optional owner ID
            labels: Optional list of labels
            estimate: Optional time estimate in hours
            parent_id: Optional parent task ID

        Returns:
            Created task details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        payload: dict[str, Any] = {
            "title": title,
            "status": status,
            "priority": priority,
        }

        if description:
            payload["description"] = description
        if phase:
            payload["phase"] = phase
        if owner_id:
            payload["owner_id"] = owner_id
        if labels:
            payload["labels"] = labels
        if estimate is not None:
            payload["estimate"] = estimate
        if parent_id is not None:
            payload["parent_id"] = parent_id

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/projects/{project_id}/tasks",
                headers=self.headers,
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def update_task(
        self,
        identifier: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        phase: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        owner_id: Optional[str] = None,
        project_id: Optional[int] = None,
        labels: Optional[list[str]] = None,
        estimate: Optional[int] = None,
        parent_id: Optional[int] = None,
        if_match: Optional[int] = None,
    ) -> dict[str, Any]:
        """Update a task.

        Args:
            identifier: Task identifier (DEV-42) or ID
            title: Optional new title
            description: Optional new description
            phase: Optional new phase/milestone identifier
            status: Optional new status
            priority: Optional new priority
            owner_id: Optional new owner ID
            project_id: Optional new project ID
            labels: Optional new labels
            estimate: Optional new estimate
            parent_id: Optional new parent task ID
            if_match: Optional version for optimistic locking

        Returns:
            Updated task details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        payload: dict[str, Any] = {}

        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if phase is not None:
            payload["phase"] = phase
        if status is not None:
            payload["status"] = status
        if priority is not None:
            payload["priority"] = priority
        if owner_id is not None:
            payload["owner_id"] = owner_id
        if project_id is not None:
            payload["project_id"] = project_id
        if labels is not None:
            payload["labels"] = labels
        if estimate is not None:
            payload["estimate"] = estimate
        if parent_id is not None:
            payload["parent_id"] = parent_id

        headers = self.headers.copy()
        if if_match is not None:
            headers["If-Match"] = str(if_match)

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.patch(
                f"{self.base_url}/v1/tasks/{identifier}",
                headers=headers,
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def delete_task(self, identifier: str) -> dict[str, Any]:
        """Delete a task (soft delete).

        Args:
            identifier: Task identifier (DEV-42) or ID

        Returns:
            Deletion confirmation

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.delete(
                f"{self.base_url}/v1/tasks/{identifier}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def add_task_dependency(
        self, identifier: str, depends_on: str
    ) -> dict[str, Any]:
        """Add a dependency to a task.

        Args:
            identifier: Task identifier (DEV-42) or ID
            depends_on: Task identifier that this task depends on

        Returns:
            Dependency details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/tasks/{identifier}/dependencies",
                headers=self.headers,
                json={"depends_on": depends_on},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def remove_task_dependency(
        self, identifier: str, depends_on: str
    ) -> dict[str, Any]:
        """Remove a dependency from a task.

        Args:
            identifier: Task identifier (DEV-42) or ID
            depends_on: Task identifier to remove dependency on

        Returns:
            Deletion confirmation

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.delete(
                f"{self.base_url}/v1/tasks/{identifier}/dependencies/{depends_on}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_task_dependencies(self, identifier: str) -> list[dict[str, Any]]:
        """Get all tasks that this task depends on.

        Args:
            identifier: Task identifier (DEV-42) or ID

        Returns:
            List of dependency tasks

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/tasks/{identifier}/dependencies",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_task_dependents(self, identifier: str) -> list[dict[str, Any]]:
        """Get all tasks that depend on this task.

        Args:
            identifier: Task identifier (DEV-42) or ID

        Returns:
            List of dependent tasks

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/tasks/{identifier}/dependents",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_task_events(
        self,
        identifier: str,
        event_type: str | None = None,
        since: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get chronological timeline of events for a task.

        Args:
            identifier: Task identifier (DEV-42) or ID
            event_type: Filter by event type (created, updated, status_changed, etc.)
            since: Filter events since date (ISO format: YYYY-MM-DD)
            limit: Max number of events to return (default 50)

        Returns:
            List of task events with timestamps and descriptions

        Raises:
            httpx.HTTPError: If the request fails.
        """
        params: dict[str, str | int] = {"limit": limit}
        if event_type:
            params["type"] = event_type
        if since:
            params["since"] = since

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/tasks/{identifier}/events",
                headers=self.headers,
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    # Label operations

    async def list_labels(self, workspace_id: int) -> list[dict[str, Any]]:
        """List all labels in a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            List of labels

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}/labels",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def create_label(
        self,
        workspace_id: int,
        name: str,
        color: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new label in a workspace.

        Args:
            workspace_id: The workspace ID
            name: Label name
            color: Optional hex color code (e.g., #FF0000)
            description: Optional label description

        Returns:
            Created label details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        payload: dict[str, Any] = {"name": name}
        if color:
            payload["color"] = color
        if description:
            payload["description"] = description

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/workspaces/{workspace_id}/labels",
                headers=self.headers,
                json=payload,
                timeout=10.0,
            )
            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise httpx.HTTPStatusError(
                    f"Failed to create label: {error_msg}",
                    request=response.request,
                    response=response,
                )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_label(self, workspace_id: int, label_id: int) -> dict[str, Any]:
        """Get a label by ID.

        Args:
            workspace_id: The workspace ID
            label_id: The label ID

        Returns:
            Label details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}/labels/{label_id}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def update_label(
        self,
        workspace_id: int,
        label_id: int,
        name: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a label.

        Args:
            workspace_id: The workspace ID
            label_id: The label ID
            name: New label name
            color: New hex color code
            description: New description

        Returns:
            Updated label details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        payload: dict[str, Any] = {}
        if name:
            payload["name"] = name
        if color:
            payload["color"] = color
        if description is not None:  # Allow empty string
            payload["description"] = description

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.patch(
                f"{self.base_url}/v1/workspaces/{workspace_id}/labels/{label_id}",
                headers=self.headers,
                json=payload,
                timeout=10.0,
            )
            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise httpx.HTTPStatusError(
                    f"Failed to update label: {error_msg}",
                    request=response.request,
                    response=response,
                )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def delete_label(self, workspace_id: int, label_id: int) -> dict[str, Any]:
        """Delete a label.

        Args:
            workspace_id: The workspace ID
            label_id: The label ID

        Returns:
            Success response

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.delete(
                f"{self.base_url}/v1/workspaces/{workspace_id}/labels/{label_id}",
                headers=self.headers,
                timeout=10.0,
            )
            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise httpx.HTTPStatusError(
                    f"Failed to delete label: {error_msg}",
                    request=response.request,
                    response=response,
                )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    # Task View operations

    async def list_task_views(self, workspace_id: int) -> list[dict[str, Any]]:
        """List all task views for the current user in a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            List of task views

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}/task-views",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def create_task_view(
        self,
        workspace_id: int,
        name: str,
        filters: dict[str, Any],
        is_default: bool = False,
    ) -> dict[str, Any]:
        """Create a new task view in a workspace.

        Args:
            workspace_id: The workspace ID
            name: View name
            filters: Filter configuration dictionary
            is_default: Whether to set as default view

        Returns:
            Created task view details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        payload: dict[str, Any] = {
            "name": name,
            "filters": filters,
            "is_default": is_default,
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/workspaces/{workspace_id}/task-views",
                headers=self.headers,
                json=payload,
                timeout=10.0,
            )
            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise httpx.HTTPStatusError(
                    f"Failed to create task view: {error_msg}",
                    request=response.request,
                    response=response,
                )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_task_view(self, workspace_id: int, view_id: int) -> dict[str, Any]:
        """Get a task view by ID.

        Args:
            workspace_id: The workspace ID
            view_id: The task view ID

        Returns:
            Task view details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}/task-views/{view_id}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_task_view_by_name(
        self, workspace_id: int, name: str
    ) -> Optional[dict[str, Any]]:
        """Get a task view by name.

        Args:
            workspace_id: The workspace ID
            name: The task view name

        Returns:
            Task view details or None if not found

        Raises:
            httpx.HTTPError: If the request fails.
        """
        # List all views and find by name
        views = await self.list_task_views(workspace_id)
        for view in views:
            if view.get("name") == name:
                return view
        return None

    async def get_default_task_view(
        self, workspace_id: int
    ) -> Optional[dict[str, Any]]:
        """Get the default task view for the current user.

        Args:
            workspace_id: The workspace ID

        Returns:
            Default task view details or None if no default set

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}/task-views/default",
                headers=self.headers,
                timeout=10.0,
            )
            # Default endpoint may return 404 if no default is set
            if response.status_code == 404:
                return None

            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def update_task_view(
        self,
        workspace_id: int,
        view_id: int,
        name: Optional[str] = None,
        filters: Optional[dict[str, Any]] = None,
        is_default: Optional[bool] = None,
    ) -> dict[str, Any]:
        """Update a task view.

        Args:
            workspace_id: The workspace ID
            view_id: The task view ID
            name: Optional new name
            filters: Optional new filter configuration
            is_default: Optional default status

        Returns:
            Updated task view details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if filters is not None:
            payload["filters"] = filters
        if is_default is not None:
            payload["is_default"] = is_default

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.patch(
                f"{self.base_url}/v1/workspaces/{workspace_id}/task-views/{view_id}",
                headers=self.headers,
                json=payload,
                timeout=10.0,
            )
            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise httpx.HTTPStatusError(
                    f"Failed to update task view: {error_msg}",
                    request=response.request,
                    response=response,
                )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def delete_task_view(self, workspace_id: int, view_id: int) -> dict[str, Any]:
        """Delete a task view.

        Args:
            workspace_id: The workspace ID
            view_id: The task view ID

        Returns:
            Success response

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.delete(
                f"{self.base_url}/v1/workspaces/{workspace_id}/task-views/{view_id}",
                headers=self.headers,
                timeout=10.0,
            )
            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise httpx.HTTPStatusError(
                    f"Failed to delete task view: {error_msg}",
                    request=response.request,
                    response=response,
                )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    # Project operations

    async def list_projects(self, workspace_id: int) -> list[dict[str, Any]]:
        """List all projects in a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            List of projects

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}/projects",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def create_project(
        self,
        workspace_id: int,
        name: str,
        identifier: str,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new project in a workspace.

        Args:
            workspace_id: The workspace ID
            name: Project name
            identifier: Unique project identifier (e.g., "API")
            description: Optional project description

        Returns:
            Created project details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/workspaces/{workspace_id}/projects",
                headers=self.headers,
                json={
                    "name": name,
                    "identifier": identifier,
                    "description": description,
                },
                timeout=10.0,
            )

            if not response.is_success:
                error_msg = self._extract_error_message(response)
                raise Exception(error_msg)

            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_current_project(self, workspace_id: int) -> dict[str, Any]:
        """Get the current/default project for a workspace.

        Returns the first project in the workspace or creates a default one if none exists.

        Args:
            workspace_id: The workspace ID

        Returns:
            Project details

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}/projects/current",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    # AI operations

    async def decompose_goal(
        self,
        goal: str,
        workspace_id: int,
        max_tasks: int = 10,
        task_size: int = 4,
    ) -> dict[str, Any]:
        """Decompose a goal into actionable tasks using AI.

        Args:
            goal: The goal description
            workspace_id: The workspace ID
            max_tasks: Maximum number of tasks to generate
            task_size: Preferred task size in hours

        Returns:
            Decomposition result with tasks and dependencies

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # First create a goal
            create_response = await client.post(
                f"{self.base_url}/v1/goals",
                headers=self.headers,
                json={
                    "title": goal,
                    "description": goal,
                    "workspace_id": workspace_id,
                },
                timeout=30.0,
            )
            create_response.raise_for_status()
            goal_data = create_response.json()

            # Extract goal ID from response
            if isinstance(goal_data, dict) and "data" in goal_data:
                goal_id = goal_data["data"]["id"]
            else:
                goal_id = goal_data["id"]

            # Then decompose it
            decompose_response = await client.post(
                f"{self.base_url}/v1/goals/{goal_id}/decompose",
                headers=self.headers,
                json={
                    "max_tasks": max_tasks,
                    "max_depth": 2,
                    "task_size_hours": task_size,
                },
                timeout=60.0,
            )
            decompose_response.raise_for_status()
            data = decompose_response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def organize_workspace(
        self, workspace_id: int, actions: list[str], dry_run: bool = False
    ) -> dict[str, Any]:
        """Organize workspace tasks using AI.

        Args:
            workspace_id: The workspace ID
            actions: List of actions to perform (e.g., ["normalize_titles", "suggest_labels"])
            dry_run: If True, preview changes without applying them

        Returns:
            Organization result with changes and suggestions

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/workspaces/{workspace_id}/organize",
                headers=self.headers,
                json={"actions": actions, "dry_run": dry_run},
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def fill_task_details(
        self, identifier: str, fields: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Auto-fill missing details for a task using AI.

        Args:
            identifier: Task identifier (e.g., DEV-42)
            fields: List of fields to fill (e.g., ["description", "acceptance", "labels"])

        Returns:
            Auto-fill result with generated content

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/tasks/{identifier}/auto-fill",
                headers=self.headers,
                json={"fields": fields or []},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_ai_suggestions(self, workspace_id: int) -> dict[str, Any]:
        """Get AI-powered suggestions for next tasks to work on.

        Args:
            workspace_id: The workspace ID

        Returns:
            Suggestions with recommended tasks and reasoning

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/v1/workspaces/{workspace_id}/suggestions",
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def review_task(self, identifier: str) -> dict[str, Any]:
        """Get AI review of a task before marking done.

        Args:
            identifier: Task identifier (e.g., DEV-42)

        Returns:
            Review result with checks, warnings, and readiness status

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/tasks/{identifier}/review",
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def generate_summary(
        self, workspace_id: int, period: str = "today"
    ) -> dict[str, Any]:
        """Generate workspace progress summary.

        Args:
            workspace_id: The workspace ID
            period: Summary period (today, weekly, monthly)

        Returns:
            Summary with activity breakdown and insights

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/v1/workspaces/{workspace_id}/summaries",
                headers=self.headers,
                json={"period": period, "include_sections": ["all"]},
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def get_ai_usage(self, workspace_id: Optional[int] = None) -> dict[str, Any]:
        """Get AI usage statistics and costs.

        Args:
            workspace_id: Optional workspace ID for workspace-level stats

        Returns:
            Usage statistics with token counts and costs

        Raises:
            httpx.HTTPError: If the request fails.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            if workspace_id:
                url = f"{self.base_url}/v1/workspaces/{workspace_id}/ai-usage"
            else:
                url = f"{self.base_url}/v1/ai-usage"

            response = await client.get(
                url,
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            # Handle SuccessResponse format
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data
