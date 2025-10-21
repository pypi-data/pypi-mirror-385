"""API client for project operations."""

from cli.client.base import BaseAPIClient
from cli.models.project import Project, ProjectCreate


class ProjectsAPIClient(BaseAPIClient):
    """API client for project operations with strongly-typed responses."""

    async def list_projects(self, workspace_id: int) -> list[Project]:
        """List all projects in a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            List of Project objects

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/workspaces/{workspace_id}/projects")
        data = self._unwrap_response(response)

        # Handle both list response and wrapped response
        if isinstance(data, list):
            return [Project(**proj) for proj in data]
        return []

    async def create_project(
        self, workspace_id: int, project: ProjectCreate
    ) -> Project:
        """Create a new project in a workspace.

        Args:
            workspace_id: The workspace ID
            project: Project creation data

        Returns:
            Created Project object

        Raises:
            NotFoundError: If workspace not found
            ValidationError: If project data is invalid
            ConflictError: If identifier already exists
            APIError: On other HTTP errors
        """
        response = await self.post(
            f"/v1/workspaces/{workspace_id}/projects",
            json=project.model_dump(exclude_none=True),
        )
        data = self._unwrap_response(response)
        return Project(**data)

    async def get_current_project(self, workspace_id: int) -> Project:
        """Get the current/default project for a workspace.

        Returns the first project in the workspace or creates a default one if none exists.

        Args:
            workspace_id: The workspace ID

        Returns:
            Project object

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        response = await self.get(f"/v1/workspaces/{workspace_id}/projects/current")
        data = self._unwrap_response(response)
        return Project(**data)
