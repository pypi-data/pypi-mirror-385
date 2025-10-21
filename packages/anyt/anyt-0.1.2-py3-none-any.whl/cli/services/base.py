"""Base service class with common patterns."""

from abc import ABC

from cli.config import GlobalConfig


class BaseService(ABC):
    """Base service class with common functionality.

    All services should inherit from BaseService to get:
    - Configuration management
    - Client initialization
    - Common error handling patterns
    - from_config() class method for easy instantiation

    Example:
        ```python
        class MyService(BaseService):
            def _init_clients(self):
                self.my_client = MyAPIClient.from_config(self.config)

            async def do_something(self):
                return await self.my_client.get_something()

        # Usage
        service = MyService.from_config()
        result = await service.do_something()
        ```
    """

    def __init__(self, config: GlobalConfig):
        """Initialize BaseService.

        Args:
            config: GlobalConfig instance
        """
        self.config = config
        self._init_clients()

    def _init_clients(self) -> None:
        """Initialize API clients.

        Override this method in subclasses to initialize the specific
        API clients needed by the service.

        Example:
            ```python
            def _init_clients(self):
                self.tasks = TasksAPIClient.from_config(self.config)
                self.workspaces = WorkspacesAPIClient.from_config(self.config)
            ```
        """
        pass

    @classmethod
    def from_config(cls, config: GlobalConfig | None = None) -> "BaseService":
        """Create service from configuration.

        This is the preferred way to instantiate services in CLI commands
        and other code.

        Args:
            config: Optional GlobalConfig instance. If None, loads from file.

        Returns:
            Configured service instance

        Raises:
            RuntimeError: If config cannot be loaded

        Example:
            ```python
            # Load from default config file
            service = MyService.from_config()

            # Use specific config instance
            config = GlobalConfig.load()
            service = MyService.from_config(config)
            ```
        """
        if config is None:
            config = GlobalConfig.load()
        return cls(config)

    def _get_effective_workspace_id(self) -> int | None:
        """Get workspace ID from config/context.

        This helper method resolves the workspace context from:
        1. Workspace config file (.anyt/anyt.json)
        2. Current environment's default_workspace
        3. None if no workspace configured

        Returns:
            Workspace ID if available, None otherwise

        Note:
            This is a convenience method. Services may need to implement
            their own workspace resolution logic based on specific needs.
        """
        try:
            # Try to get from current environment config
            env_config = self.config.get_current_env()
            if env_config.default_workspace:
                return int(env_config.default_workspace)
        except (ValueError, AttributeError):
            pass

        return None
