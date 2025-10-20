"""Integration test configuration and fixtures.

Integration tests require a running backend server with proper authentication.
Set the ANYT_TEST_TOKEN environment variable with a valid JWT token for testing.
"""

import os
import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Provide CLI test runner."""
    return CliRunner()


@pytest.fixture
def integration_auth_token():
    """Provide authentication token for integration tests.

    Raises:
        pytest.skip: If ANYT_TEST_TOKEN environment variable is not set.

    Returns:
        str: Valid JWT token for testing.
    """
    token = os.getenv("ANYT_TEST_TOKEN")
    if not token:
        pytest.skip(
            "Integration tests require ANYT_TEST_TOKEN environment variable. "
            "Please set a valid JWT token: export ANYT_TEST_TOKEN='your-jwt-token'"
        )

    # Validate token format (JWT should have 3 parts)
    if token.count(".") != 2:
        pytest.skip(
            f"ANYT_TEST_TOKEN must be a valid JWT format (header.payload.signature). "
            f"Current token has {token.count('.') + 1} segments, expected 3."
        )

    return token


@pytest.fixture
def integration_api_url():
    """Provide API URL for integration tests.

    Returns:
        str: API URL, defaults to http://localhost:8000
    """
    return os.getenv("ANYT_TEST_API_URL", "http://localhost:8000")


def pytest_configure(config):
    """Add custom markers for integration tests."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (requires backend server)"
    )


def pytest_collection_modifyitems(config, items):
    """Auto-mark all tests in integration directory."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture
def integration_global_config(integration_auth_token, integration_api_url):
    """Provide configured GlobalConfig for integration tests.

    Returns:
        GlobalConfig: Configured with integration test credentials.
    """
    from cli.config import GlobalConfig, EnvironmentConfig

    config = GlobalConfig()
    config.environments = {
        "test": EnvironmentConfig(
            api_url=integration_api_url,
            auth_token=integration_auth_token,
        )
    }
    config.current_environment = "test"
    return config


@pytest.fixture
def integration_workspace_config(integration_api_url):
    """Provide configured WorkspaceConfig for integration tests.

    Returns:
        MagicMock: Mocked workspace config with test values.
    """
    from unittest.mock import MagicMock

    ws_config = MagicMock()
    ws_config.workspace_id = "1"
    ws_config.workspace_identifier = "DEV"
    ws_config.name = "Test Workspace"
    ws_config.api_url = integration_api_url
    return ws_config


@pytest.fixture
def mock_config_load(integration_global_config, integration_workspace_config, monkeypatch):
    """Mock config loading to use integration test credentials.

    This fixture automatically mocks GlobalConfig.load() and WorkspaceConfig.load()
    to return test configurations with proper authentication.
    """
    def mock_global_load():
        return integration_global_config

    def mock_workspace_load():
        return integration_workspace_config

    monkeypatch.setattr(
        "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
    )
    monkeypatch.setattr(
        "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
    )

    return integration_global_config, integration_workspace_config
