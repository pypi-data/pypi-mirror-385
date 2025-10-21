"""API client for task view operations."""

from cli.client.base import BaseAPIClient
from cli.models.view import TaskView, TaskViewCreate, TaskViewUpdate


class ViewsAPIClient(BaseAPIClient):
    """API client for task view operations with strongly-typed responses."""

    async def list_task_views(self, workspace_id: int) -> list[TaskView]:
        """List task views in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of TaskView objects

        Raises:
            APIError: On HTTP errors
        """
        response = await self.get(f"/v1/workspaces/{workspace_id}/views")
        data = self._unwrap_response(response)

        # Handle both list response and wrapped response
        if isinstance(data, list):
            return [TaskView(**view) for view in data]
        return []

    async def create_task_view(
        self, workspace_id: int, view: TaskViewCreate
    ) -> TaskView:
        """Create a new task view in a workspace.

        Args:
            workspace_id: Workspace ID
            view: Task view creation data

        Returns:
            Created TaskView object

        Raises:
            ValidationError: If view data is invalid
            ConflictError: If view name already exists
            APIError: On other HTTP errors
        """
        response = await self.post(
            f"/v1/workspaces/{workspace_id}/views",
            json=view.model_dump(exclude_none=True),
        )
        data = self._unwrap_response(response)
        return TaskView(**data)

    async def get_task_view(self, workspace_id: int, view_id: int) -> TaskView:
        """Get a specific task view by ID.

        Args:
            workspace_id: Workspace ID
            view_id: View ID

        Returns:
            TaskView object

        Raises:
            NotFoundError: If view not found
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/workspaces/{workspace_id}/views/{view_id}")
        data = self._unwrap_response(response)
        return TaskView(**data)

    async def get_task_view_by_name(
        self, workspace_id: int, name: str
    ) -> TaskView | None:
        """Get a task view by name.

        Args:
            workspace_id: Workspace ID
            name: View name

        Returns:
            TaskView object if found, None otherwise

        Raises:
            APIError: On HTTP errors
        """
        try:
            # Use query parameter to filter by name
            response = await self.get(
                f"/v1/workspaces/{workspace_id}/views",
                params={"name": name},
            )
            data = self._unwrap_response(response)

            if isinstance(data, list) and len(data) > 0:
                return TaskView(**data[0])
            return None
        except Exception:
            return None

    async def get_default_task_view(self, workspace_id: int) -> TaskView | None:
        """Get the default task view for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Default TaskView object if found, None otherwise

        Raises:
            APIError: On HTTP errors
        """
        try:
            response = await self.get(f"/v1/workspaces/{workspace_id}/views/default")
            data = self._unwrap_response(response)
            return TaskView(**data)
        except Exception:
            return None

    async def update_task_view(
        self, workspace_id: int, view_id: int, updates: TaskViewUpdate
    ) -> TaskView:
        """Update a task view.

        Args:
            workspace_id: Workspace ID
            view_id: View ID
            updates: Task view update data

        Returns:
            Updated TaskView object

        Raises:
            NotFoundError: If view not found
            ValidationError: If update data is invalid
            ConflictError: If name already exists
            APIError: On other HTTP errors
        """
        response = await self.patch(
            f"/v1/workspaces/{workspace_id}/views/{view_id}",
            json=updates.model_dump(exclude_none=True),
        )
        data = self._unwrap_response(response)
        return TaskView(**data)

    async def delete_task_view(self, workspace_id: int, view_id: int) -> None:
        """Delete a task view.

        Args:
            workspace_id: Workspace ID
            view_id: View ID

        Raises:
            NotFoundError: If view not found
            APIError: On other HTTP errors
        """
        await self.delete(f"/v1/workspaces/{workspace_id}/views/{view_id}")
