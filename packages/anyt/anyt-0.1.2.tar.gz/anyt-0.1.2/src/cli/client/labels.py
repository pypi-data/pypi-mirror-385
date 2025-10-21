"""API client for label operations."""

from cli.client.base import BaseAPIClient
from cli.models.label import Label, LabelCreate, LabelUpdate


class LabelsAPIClient(BaseAPIClient):
    """API client for label operations with strongly-typed responses."""

    async def list_labels(self, workspace_id: int) -> list[Label]:
        """List labels in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of Label objects

        Raises:
            APIError: On HTTP errors
        """
        response = await self.get(f"/v1/workspaces/{workspace_id}/labels")
        data = self._unwrap_response(response)

        # Handle both list response and wrapped response
        if isinstance(data, list):
            return [Label(**label) for label in data]
        return []

    async def create_label(self, workspace_id: int, label: LabelCreate) -> Label:
        """Create a new label in a workspace.

        Args:
            workspace_id: Workspace ID
            label: Label creation data

        Returns:
            Created Label object

        Raises:
            ValidationError: If label data is invalid
            ConflictError: If label name already exists
            APIError: On other HTTP errors
        """
        response = await self.post(
            f"/v1/workspaces/{workspace_id}/labels",
            json=label.model_dump(exclude_none=True),
        )
        data = self._unwrap_response(response)
        return Label(**data)

    async def get_label(self, workspace_id: int, label_id: int) -> Label:
        """Get a specific label by ID.

        Args:
            workspace_id: Workspace ID
            label_id: Label ID

        Returns:
            Label object

        Raises:
            NotFoundError: If label not found
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/workspaces/{workspace_id}/labels/{label_id}")
        data = self._unwrap_response(response)
        return Label(**data)

    async def update_label(
        self, workspace_id: int, label_id: int, updates: LabelUpdate
    ) -> Label:
        """Update a label.

        Args:
            workspace_id: Workspace ID
            label_id: Label ID
            updates: Label update data

        Returns:
            Updated Label object

        Raises:
            NotFoundError: If label not found
            ValidationError: If update data is invalid
            ConflictError: If name already exists
            APIError: On other HTTP errors
        """
        response = await self.patch(
            f"/v1/workspaces/{workspace_id}/labels/{label_id}",
            json=updates.model_dump(exclude_none=True),
        )
        data = self._unwrap_response(response)
        return Label(**data)

    async def delete_label(self, workspace_id: int, label_id: int) -> None:
        """Delete a label.

        Args:
            workspace_id: Workspace ID
            label_id: Label ID

        Raises:
            NotFoundError: If label not found
            APIError: On other HTTP errors
        """
        await self.delete(f"/v1/workspaces/{workspace_id}/labels/{label_id}")
