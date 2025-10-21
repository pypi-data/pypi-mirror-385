"""API client for task operations."""

from typing import Any

from cli.client.base import BaseAPIClient
from cli.models.dependency import TaskDependency
from cli.models.task import Task, TaskCreate, TaskFilters, TaskUpdate
from cli.schemas.pagination import PaginatedResponse


class TasksAPIClient(BaseAPIClient):
    """API client for task operations with strongly-typed responses."""

    async def list_tasks(self, filters: TaskFilters) -> PaginatedResponse[Task]:
        """List tasks with filters.

        Args:
            filters: Task filter criteria

        Returns:
            Paginated response containing Task objects

        Raises:
            APIError: On HTTP errors
        """
        params = filters.model_dump(exclude_none=True)
        response = await self.get("/v1/tasks", params=params)
        data = self._unwrap_response(response)

        # Parse paginated response
        # Backend returns: {"items": [...], "pagination": {"total": N, "limit": M, "offset": O, ...}}
        pagination = data.get("pagination", {})
        return PaginatedResponse[Task](
            items=[Task(**item) for item in data["items"]],
            total=pagination["total"],
            limit=pagination["limit"],
            offset=pagination["offset"],
        )

    async def get_task(self, identifier: str) -> Task:
        """Get task by identifier.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            Task object

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/tasks/{identifier}")
        data = self._unwrap_response(response)
        return Task(**data)

    async def get_task_by_workspace(self, workspace_id: int, identifier: str) -> Task:
        """Get task by workspace and identifier.

        Args:
            workspace_id: Workspace ID
            identifier: Task identifier within workspace

        Returns:
            Task object

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/workspaces/{workspace_id}/tasks/{identifier}")
        data = self._unwrap_response(response)
        return Task(**data)

    async def get_task_by_public_id(self, public_id: int) -> Task:
        """Get task by 9-digit public ID.

        Args:
            public_id: 9-digit public task ID

        Returns:
            Task object

        Raises:
            NotFoundError: If task not found
            ForbiddenError: If user doesn't have access to the task
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/t/{public_id}")
        data = self._unwrap_response(response)
        return Task(**data)

    async def create_task(self, project_id: int, task: TaskCreate) -> Task:
        """Create a new task.

        Args:
            project_id: Project ID to create task in
            task: Task creation data

        Returns:
            Created Task object

        Raises:
            ValidationError: If task data is invalid
            APIError: On other HTTP errors
        """
        response = await self.post(
            f"/v1/projects/{project_id}/tasks",
            json=task.model_dump(exclude_none=True),
        )
        data = self._unwrap_response(response)
        return Task(**data)

    async def update_task(self, identifier: str, updates: TaskUpdate) -> Task:
        """Update an existing task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            updates: Task update data

        Returns:
            Updated Task object

        Raises:
            NotFoundError: If task not found
            ValidationError: If update data is invalid
            APIError: On other HTTP errors
        """
        response = await self.patch(
            f"/v1/tasks/{identifier}",
            json=updates.model_dump(exclude_none=True),
        )
        data = self._unwrap_response(response)
        return Task(**data)

    async def delete_task(self, identifier: str) -> None:
        """Delete a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        await self.delete(f"/v1/tasks/{identifier}")

    async def add_task_dependency(
        self, identifier: str, depends_on: str
    ) -> TaskDependency:
        """Add a dependency to a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            depends_on: Identifier of task this depends on

        Returns:
            Created TaskDependency object

        Raises:
            NotFoundError: If either task not found
            ConflictError: If dependency would create a cycle
            APIError: On other HTTP errors
        """
        response = await self.post(
            f"/v1/tasks/{identifier}/dependencies",
            json={"depends_on": depends_on},
        )
        data = self._unwrap_response(response)
        return TaskDependency(**data)

    async def remove_task_dependency(self, identifier: str, depends_on: str) -> None:
        """Remove a dependency from a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            depends_on: Identifier of task dependency to remove

        Raises:
            NotFoundError: If task or dependency not found
            APIError: On other HTTP errors
        """
        await self.delete(f"/v1/tasks/{identifier}/dependencies/{depends_on}")

    async def get_task_dependencies(self, identifier: str) -> list[Task]:
        """Get tasks that this task depends on.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            List of Task objects this task depends on

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/tasks/{identifier}/dependencies")
        data = self._unwrap_response(response)
        return [Task(**item) for item in data]

    async def get_task_dependents(self, identifier: str) -> list[Task]:
        """Get tasks that depend on this task (blocked by this task).

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID

        Returns:
            List of Task objects that depend on this task

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/tasks/{identifier}/dependents")
        data = self._unwrap_response(response)
        return [Task(**item) for item in data]

    async def get_task_events(
        self,
        identifier: str,
        event_type: str | None = None,
        since: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get chronological timeline of events for a task.

        Args:
            identifier: Task identifier (e.g., DEV-42) or ID
            event_type: Optional filter by event type (created, updated, etc.)
            since: Optional filter events since date (ISO format: YYYY-MM-DD)
            limit: Max number of events to return (default 50)

        Returns:
            List of task events with timestamps and descriptions

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        params: dict[str, Any] = {"limit": limit}
        if event_type:
            params["event_type"] = event_type
        if since:
            params["since"] = since

        response = await self.get(f"/v1/tasks/{identifier}/events", params=params)
        data = self._unwrap_response(response)

        # Return list of events as-is (no model defined yet)
        if isinstance(data, list):
            return data
        return []
