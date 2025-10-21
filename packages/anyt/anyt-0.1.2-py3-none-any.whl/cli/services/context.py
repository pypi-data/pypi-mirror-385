"""Service context helpers for resolving workspace, project, and user context.

These helpers provide utilities for commands and services to resolve
context information like current workspace, project, or user preferences.
"""

from typing import Any

from cli.config import GlobalConfig


class ServiceContext:
    """Context manager for service operations.

    Provides helper methods to resolve workspace, project, and other
    contextual information needed by services and commands.

    Example:
        ```python
        context = ServiceContext.from_config()
        workspace_id = context.get_workspace_id()
        project_id = context.get_project_id()
        ```
    """

    def __init__(self, config: GlobalConfig):
        """Initialize ServiceContext.

        Args:
            config: GlobalConfig instance
        """
        self.config = config

    @classmethod
    def from_config(cls, config: GlobalConfig | None = None) -> "ServiceContext":
        """Create context from configuration.

        Args:
            config: Optional GlobalConfig instance. If None, loads from file.

        Returns:
            ServiceContext instance
        """
        if config is None:
            config = GlobalConfig.load()
        return cls(config)

    def get_workspace_id(self) -> int | None:
        """Get workspace ID from config/context.

        Resolution order:
        1. Current environment's default_workspace
        2. None if not configured

        Returns:
            Workspace ID if available, None otherwise
        """
        try:
            env_config = self.config.get_current_env()
            if env_config.default_workspace:
                return int(env_config.default_workspace)
        except (ValueError, AttributeError):
            pass

        return None

    def get_project_id(self) -> int | None:
        """Get project ID from config/context.

        Resolution order:
        1. .anyt/anyt.json workspace config for current_project_id
        2. Global config for default project (future)
        3. None if not configured

        Returns:
            Project ID if available, None otherwise
        """
        from cli.config import WorkspaceConfig

        # Try to read from workspace config
        workspace_config = WorkspaceConfig.load()
        if workspace_config and workspace_config.current_project_id:
            return workspace_config.current_project_id

        # Future: Check global config for default project

        return None

    def get_effective_config(self) -> dict[str, Any]:
        """Get effective configuration for current environment.

        Returns:
            Dictionary with api_url, auth_token, agent_key, etc.
        """
        return self.config.get_effective_config()

    def get_api_url(self) -> str:
        """Get API URL for current environment.

        Returns:
            API base URL

        Raises:
            RuntimeError: If API URL is not configured
        """
        effective = self.config.get_effective_config()
        api_url = effective.get("api_url")
        if not api_url or api_url == "":
            raise RuntimeError("No API URL configured")
        return str(api_url)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated in current environment.

        Returns:
            True if auth_token or agent_key is configured
        """
        effective = self.config.get_effective_config()
        return bool(effective.get("auth_token") or effective.get("agent_key"))
