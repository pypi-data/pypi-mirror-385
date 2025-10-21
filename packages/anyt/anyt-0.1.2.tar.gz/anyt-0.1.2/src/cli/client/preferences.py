"""API client for user preferences operations."""

from cli.client.base import BaseAPIClient
from cli.models.user import UserPreferences


class PreferencesAPIClient(BaseAPIClient):
    """API client for user preferences operations with strongly-typed responses."""

    async def get_user_preferences(self) -> UserPreferences | None:
        """Get user preferences (current workspace and project).

        Returns:
            UserPreferences object with current_workspace_id and current_project_id,
            or None if no preferences are set

        Raises:
            APIError: On HTTP errors
        """
        response = await self.get("/v1/users/me/preferences")
        data = self._unwrap_response(response)

        # Handle None or empty response
        if data is None or (isinstance(data, dict) and not data):
            return None

        return UserPreferences(**data)

    async def set_current_workspace(self, workspace_id: int) -> UserPreferences:
        """Set the current workspace preference for the user.

        Args:
            workspace_id: The workspace ID to set as current

        Returns:
            Updated UserPreferences object

        Raises:
            NotFoundError: If workspace not found
            ValidationError: If workspace_id is invalid
            APIError: On other HTTP errors
        """
        # Use PUT instead of PATCH for preferences
        response = await self.patch(
            "/v1/users/me/preferences/workspace",
            json={"workspace_id": workspace_id},
        )
        data = self._unwrap_response(response)
        return UserPreferences(**data)

    async def set_current_project(
        self, workspace_id: int, project_id: int
    ) -> UserPreferences:
        """Set the current project (and workspace) preference for the user.

        Args:
            workspace_id: The workspace ID containing the project
            project_id: The project ID to set as current

        Returns:
            Updated UserPreferences object

        Raises:
            NotFoundError: If workspace or project not found
            ValidationError: If IDs are invalid
            APIError: On other HTTP errors
        """
        # Use PUT instead of PATCH for preferences
        response = await self.patch(
            "/v1/users/me/preferences/project",
            json={"workspace_id": workspace_id, "project_id": project_id},
        )
        data = self._unwrap_response(response)
        return UserPreferences(**data)

    async def clear_user_preferences(self) -> None:
        """Clear user preferences (resets current workspace and project).

        Raises:
            APIError: On HTTP errors
        """
        await self.delete("/v1/users/me/preferences")
