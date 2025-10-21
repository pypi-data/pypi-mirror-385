"""API client for workspace operations."""

from cli.client.base import BaseAPIClient
from cli.models.workspace import Workspace, WorkspaceCreate


class WorkspacesAPIClient(BaseAPIClient):
    """API client for workspace operations with strongly-typed responses."""

    async def list_workspaces(self) -> list[Workspace]:
        """List accessible workspaces.

        Returns:
            List of Workspace objects the authenticated user/agent has access to

        Raises:
            APIError: On HTTP errors
        """
        response = await self.get("/v1/workspaces")
        data = self._unwrap_response(response)

        # Handle both list response and wrapped response
        if isinstance(data, list):
            return [Workspace(**ws) for ws in data]
        return []

    async def get_workspace(self, workspace_id: str) -> Workspace:
        """Get a specific workspace by ID.

        Args:
            workspace_id: The workspace identifier

        Returns:
            Workspace object

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/workspaces/{workspace_id}")
        data = self._unwrap_response(response)
        return Workspace(**data)

    async def get_current_workspace(self) -> Workspace:
        """Get the current/default workspace for the authenticated user.

        Returns the first workspace (by creation date) where the user is a member.
        If the user has no workspaces, automatically creates a default workspace.

        Returns:
            Workspace object

        Raises:
            APIError: On HTTP errors
        """
        response = await self.get("/v1/workspaces/current")
        data = self._unwrap_response(response)
        return Workspace(**data)

    async def create_workspace(self, workspace: WorkspaceCreate) -> Workspace:
        """Create a new workspace.

        Args:
            workspace: Workspace creation data

        Returns:
            Created Workspace object

        Raises:
            ValidationError: If workspace data is invalid
            ConflictError: If identifier already exists
            APIError: On other HTTP errors
        """
        response = await self.post(
            "/v1/workspaces",
            json=workspace.model_dump(exclude_none=True),
        )
        data = self._unwrap_response(response)
        return Workspace(**data)
