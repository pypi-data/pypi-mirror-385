"""Unit tests for BaseService."""

from cli.config import EnvironmentConfig, GlobalConfig
from cli.services.base import BaseService


class ConcreteService(BaseService):
    """Concrete implementation of BaseService for testing."""

    def _init_clients(self) -> None:
        """Initialize clients - no-op for testing."""
        pass


def test_base_service_initialization():
    """Test BaseService can be initialized with config."""
    config = GlobalConfig(
        current_environment="test",
        environments={
            "test": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        },
    )

    service = ConcreteService(config)

    assert service.config == config


def test_base_service_from_config(temp_config_dir):
    """Test from_config class method."""
    # Create a config file
    config = GlobalConfig(
        current_environment="test",
        environments={
            "test": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        },
    )
    config.save()

    # Load service from config
    service = ConcreteService.from_config()

    assert service.config.current_environment == "test"
    assert service.config.environments["test"].api_url == "http://localhost:8000"


def test_base_service_from_config_with_provided_config():
    """Test from_config with explicitly provided config."""
    config = GlobalConfig(
        current_environment="test",
        environments={
            "test": EnvironmentConfig(
                api_url="http://localhost:8000",
            )
        },
    )

    service = ConcreteService.from_config(config)

    assert service.config == config


def test_get_effective_workspace_id():
    """Test _get_effective_workspace_id helper."""
    config = GlobalConfig(
        current_environment="test",
        environments={
            "test": EnvironmentConfig(
                api_url="http://localhost:8000",
                default_workspace="123",
            )
        },
    )

    service = ConcreteService(config)
    workspace_id = service._get_effective_workspace_id()

    assert workspace_id == 123


def test_get_effective_workspace_id_none():
    """Test _get_effective_workspace_id returns None when not configured."""
    config = GlobalConfig(
        current_environment="test",
        environments={
            "test": EnvironmentConfig(
                api_url="http://localhost:8000",
            )
        },
    )

    service = ConcreteService(config)
    workspace_id = service._get_effective_workspace_id()

    assert workspace_id is None


def test_init_clients_called():
    """Test that _init_clients is called during initialization."""

    class TestService(BaseService):
        def __init__(self, config):
            self.clients_initialized = False
            super().__init__(config)

        def _init_clients(self):
            self.clients_initialized = True

    config = GlobalConfig(
        current_environment="test",
        environments={"test": EnvironmentConfig(api_url="http://localhost:8000")},
    )

    service = TestService(config)

    assert service.clients_initialized is True
