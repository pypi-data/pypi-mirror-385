"""Workspace service with business logic for workspace operations."""

from typing import Any, cast

from cli.client.exceptions import NotFoundError
from cli.client.workspaces import WorkspacesAPIClient
from cli.models.workspace import Workspace, WorkspaceCreate
from cli.services.base import BaseService


class WorkspaceService(BaseService):
    """Business logic for workspace operations.

    WorkspaceService encapsulates business rules and workflows for workspace
    management, including:
    - Getting or creating default workspace
    - Switching workspaces with validation
    - Resolving workspace context from config/parameters
    - Getting workspace summary and statistics

    Example:
        ```python
        service = WorkspaceService.from_config()

        # Get or create default workspace
        workspace = await service.get_or_create_default_workspace()

        # Switch to a different workspace
        await service.switch_workspace(workspace_id=456)

        # Resolve workspace context
        workspace = await service.resolve_workspace_context(workspace_id=123)
        ```
    """

    workspaces: WorkspacesAPIClient

    def _init_clients(self) -> None:
        """Initialize API clients."""
        self.workspaces = cast(
            WorkspacesAPIClient, WorkspacesAPIClient.from_config(self.config)
        )

    async def list_workspaces(self) -> list[Workspace]:
        """List accessible workspaces.

        Returns:
            List of Workspace objects the authenticated user has access to
        """
        return await self.workspaces.list_workspaces()

    async def get_workspace(self, workspace_id: str | int) -> Workspace:
        """Get a specific workspace by ID.

        Args:
            workspace_id: The workspace identifier (int or string)

        Returns:
            Workspace object
        """
        return await self.workspaces.get_workspace(str(workspace_id))

    async def get_or_create_default_workspace(self) -> Workspace:
        """Get current workspace or create default if none exists.

        This is useful for CLI initialization where we want to ensure
        the user has at least one workspace to work in.

        Business logic:
        1. Try to get current workspace from API
        2. If not found, create a default "Personal" workspace
        3. Return the workspace

        Returns:
            Current or newly created Workspace object

        Raises:
            APIError: If creation fails
        """
        try:
            # Try to get current workspace (first workspace user has access to)
            return await self.workspaces.get_current_workspace()
        except NotFoundError:
            # No workspace exists, create default
            workspace = WorkspaceCreate(
                name="Personal",
                identifier="PER",
                description="Default personal workspace",
            )
            return await self.workspaces.create_workspace(workspace)

    async def create_workspace(self, workspace: WorkspaceCreate) -> Workspace:
        """Create a new workspace with validation.

        Validates:
        - Identifier is at least 3 characters
        - Name is not empty

        Args:
            workspace: Workspace creation data

        Returns:
            Created Workspace object

        Raises:
            ValueError: If validation fails
        """
        # Business rule: validate identifier length
        if len(workspace.identifier) < 3:
            raise ValueError("Workspace identifier must be at least 3 characters")

        # Business rule: validate name is not empty
        if not workspace.name or workspace.name.strip() == "":
            raise ValueError("Workspace name cannot be empty")

        return await self.workspaces.create_workspace(workspace)

    async def switch_workspace(self, workspace_id: int) -> Workspace:
        """Switch to a different workspace with validation.

        Business logic:
        1. Verify workspace exists and user has access
        2. Update config to set as default workspace
        3. Return the workspace

        Args:
            workspace_id: The workspace ID to switch to

        Returns:
            Workspace object

        Raises:
            NotFoundError: If workspace doesn't exist or user has no access
        """
        # Verify workspace exists and user has access
        workspace = await self.workspaces.get_workspace(str(workspace_id))

        # Update config to set as default workspace
        env_config = self.config.get_current_env()
        env_config.default_workspace = str(workspace_id)
        self.config.save()

        return workspace

    async def resolve_workspace_context(
        self, workspace_id: int | None = None
    ) -> Workspace:
        """Resolve workspace from context.

        Resolution order:
        1. If workspace_id provided, use that
        2. Otherwise get from config's default_workspace
        3. Otherwise get current workspace from API
        4. Otherwise create default workspace

        This is the primary method commands should use to get workspace context.

        Args:
            workspace_id: Optional explicit workspace ID

        Returns:
            Resolved Workspace object

        Raises:
            APIError: If workspace cannot be resolved
        """
        # If explicit workspace_id provided, use that
        if workspace_id is not None:
            return await self.workspaces.get_workspace(str(workspace_id))

        # Try to get from config
        effective_ws_id = self._get_effective_workspace_id()
        if effective_ws_id is not None:
            try:
                return await self.workspaces.get_workspace(str(effective_ws_id))
            except NotFoundError:
                # Configured workspace doesn't exist, fall through to default
                pass

        # Fall back to getting or creating default workspace
        return await self.get_or_create_default_workspace()

    async def get_workspace_summary(
        self, workspace_id: int | None = None
    ) -> dict[str, Any]:
        """Get workspace overview with summary statistics.

        Returns a dictionary with:
        - workspace: The workspace object
        - stats: Summary statistics (to be implemented)

        Future enhancements:
        - Count of tasks by status
        - Count of projects
        - Recent activity
        - Team member count

        Args:
            workspace_id: Optional workspace ID (uses context if not provided)

        Returns:
            Dictionary with workspace and summary data
        """
        workspace = await self.resolve_workspace_context(workspace_id)

        # Future: fetch workspace statistics
        # For now, just return the workspace
        return {
            "workspace": workspace,
            "stats": {
                # Placeholder for future statistics
                "tasks_total": 0,
                "tasks_by_status": {},
                "projects_count": 0,
            },
        }
