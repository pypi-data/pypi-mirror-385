"""Tests for APIClient initialization and configuration."""

from unittest.mock import patch

import pytest

from cli.client import APIClient
from cli.config import GlobalConfig, EnvironmentConfig


class TestAPIClientInitialization:
    """Test APIClient initialization and configuration."""

    @pytest.fixture(autouse=True)
    def clear_cli_env_vars(self, monkeypatch):
        """Isolate tests from ANYT_* environment variables.

        This fixture automatically clears all ANYT_* environment variables
        before each test to ensure tests are not affected by the developer's
        shell environment. Individual tests can still set specific env vars
        using monkeypatch.setenv() to test override behavior.
        """
        env_vars = ["ANYT_AUTH_TOKEN", "ANYT_AGENT_KEY", "ANYT_API_URL", "ANYT_ENV"]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

    def test_init_with_user_token(self):
        """Test APIClient initialization with user token."""
        client = APIClient(
            base_url="http://localhost:8000",
            auth_token="test-user-token-12345",
        )

        assert client.base_url == "http://localhost:8000"
        assert client.auth_token == "test-user-token-12345"
        assert client.agent_key is None
        assert client.headers["Authorization"] == "Bearer test-user-token-12345"
        assert "X-API-Key" not in client.headers

    def test_init_with_agent_key(self):
        """Test APIClient initialization with agent key."""
        client = APIClient(
            base_url="http://localhost:8000",
            agent_key="anyt_agent_abcdef123456789012345678901234",
        )

        assert client.base_url == "http://localhost:8000"
        assert client.auth_token is None
        assert client.agent_key == "anyt_agent_abcdef123456789012345678901234"
        assert "Authorization" not in client.headers
        assert (
            client.headers["X-API-Key"] == "anyt_agent_abcdef123456789012345678901234"
        )

    def test_init_with_both_auth_methods(self):
        """Test APIClient initialization with both token and agent key (token takes precedence)."""
        client = APIClient(
            base_url="http://localhost:8000",
            auth_token="test-user-token",
            agent_key="anyt_agent_key",
        )

        # Token should take precedence
        assert client.headers["Authorization"] == "Bearer test-user-token"
        assert "X-API-Key" not in client.headers

    def test_init_without_auth(self):
        """Test APIClient initialization without authentication."""
        client = APIClient(base_url="http://localhost:8000")

        assert client.base_url == "http://localhost:8000"
        assert client.auth_token is None
        assert client.agent_key is None
        assert client.headers == {}

    def test_init_base_url_trailing_slash_removed(self):
        """Test that trailing slashes are removed from base URL."""
        client = APIClient(base_url="http://localhost:8000/")

        assert client.base_url == "http://localhost:8000"

    def test_from_config_with_token(self):
        """Test APIClient.from_config() with user token."""
        config = GlobalConfig(
            current_environment="dev",
            environments={
                "dev": EnvironmentConfig(
                    api_url="http://localhost:8000",
                    auth_token="test-user-token-12345",
                )
            },
        )

        client = APIClient.from_config(config)

        assert client.base_url == "http://localhost:8000"
        assert client.auth_token == "test-user-token-12345"
        assert client.headers["Authorization"] == "Bearer test-user-token-12345"

    def test_from_config_with_agent_key(self):
        """Test APIClient.from_config() with agent key passed as auth_token.

        Agent keys are stored in auth_token field in config. The config's
        get_effective_config() detects agent keys (starting with 'anyt_agent_')
        and automatically moves them to the agent_key field for proper X-API-Key
        header authentication.
        """
        config = GlobalConfig(
            current_environment="dev",
            environments={
                "dev": EnvironmentConfig(
                    api_url="http://localhost:8000",
                    auth_token="anyt_agent_abcdef123456789012345678901234",
                )
            },
        )

        client = APIClient.from_config(config)

        assert client.base_url == "http://localhost:8000"
        # Agent key is automatically detected and moved to agent_key field
        assert client.auth_token is None
        assert client.agent_key == "anyt_agent_abcdef123456789012345678901234"
        # Uses X-API-Key header (not Bearer)
        assert "Authorization" not in client.headers
        assert (
            client.headers["X-API-Key"] == "anyt_agent_abcdef123456789012345678901234"
        )

    def test_from_config_without_auth(self):
        """Test APIClient.from_config() without authentication."""
        config = GlobalConfig(
            current_environment="dev",
            environments={
                "dev": EnvironmentConfig(
                    api_url="http://localhost:8000",
                    auth_token=None,
                )
            },
        )

        client = APIClient.from_config(config)

        assert client.base_url == "http://localhost:8000"
        assert client.auth_token is None
        assert client.headers == {}

    @patch("cli.client.GlobalConfig.load")
    def test_from_config_loads_default_config(self, mock_load):
        """Test APIClient.from_config() loads default config when not provided."""
        mock_config = GlobalConfig(
            current_environment="dev",
            environments={
                "dev": EnvironmentConfig(
                    api_url="http://localhost:8000",
                    auth_token="test-token",
                )
            },
        )
        mock_load.return_value = mock_config

        client = APIClient.from_config()

        assert client.base_url == "http://localhost:8000"
        assert client.auth_token == "test-token"
        mock_load.assert_called_once()

    def test_environment_agent_key_overrides_config_token(self, monkeypatch):
        """Test that ANYT_AGENT_KEY environment variable overrides config auth_token."""
        monkeypatch.setenv("ANYT_AGENT_KEY", "env-agent-key-12345")

        config = GlobalConfig(
            current_environment="dev",
            environments={
                "dev": EnvironmentConfig(
                    api_url="http://localhost:8000",
                    auth_token="config-file-token",  # Should be overridden
                )
            },
        )

        client = APIClient.from_config(config)

        # Environment variable should override config file
        assert client.agent_key == "env-agent-key-12345"
        assert client.auth_token is None
        assert client.headers["X-API-Key"] == "env-agent-key-12345"
        assert "Authorization" not in client.headers

    def test_environment_auth_token_overrides_config_agent_key(self, monkeypatch):
        """Test that ANYT_AUTH_TOKEN overrides config agent key."""
        monkeypatch.setenv("ANYT_AUTH_TOKEN", "env-auth-token-xyz")

        config = GlobalConfig(
            current_environment="dev",
            environments={
                "dev": EnvironmentConfig(
                    api_url="http://localhost:8000",
                    auth_token="anyt_agent_config_key_12345678901234",  # Agent key in config
                )
            },
        )

        client = APIClient.from_config(config)

        # Auth token env var should override agent key from config
        assert client.auth_token == "env-auth-token-xyz"
        assert client.agent_key is None
        assert client.headers["Authorization"] == "Bearer env-auth-token-xyz"
        assert "X-API-Key" not in client.headers

    def test_environment_api_url_overrides_config(self, monkeypatch):
        """Test that ANYT_API_URL environment variable overrides config."""
        monkeypatch.setenv("ANYT_API_URL", "https://prod.example.com")

        config = GlobalConfig(
            current_environment="dev",
            environments={
                "dev": EnvironmentConfig(
                    api_url="http://localhost:8000",
                    auth_token="test-token",
                )
            },
        )

        client = APIClient.from_config(config)

        # Environment variable should override config
        assert client.base_url == "https://prod.example.com"
        assert client.auth_token == "test-token"

    def test_environment_env_switches_to_different_environment(self, monkeypatch):
        """Test that ANYT_ENV environment variable switches to different config environment."""
        monkeypatch.setenv("ANYT_ENV", "staging")

        config = GlobalConfig(
            current_environment="dev",
            environments={
                "dev": EnvironmentConfig(
                    api_url="http://localhost:8000",
                    auth_token="dev-token",
                ),
                "staging": EnvironmentConfig(
                    api_url="https://staging.example.com",
                    auth_token="staging-token",
                ),
            },
        )

        client = APIClient.from_config(config)

        # Should use staging environment instead of dev
        assert client.base_url == "https://staging.example.com"
        assert client.auth_token == "staging-token"

    def test_multiple_environment_overrides(self, monkeypatch):
        """Test that multiple environment variables work together."""
        monkeypatch.setenv("ANYT_API_URL", "https://custom.example.com")
        monkeypatch.setenv("ANYT_AGENT_KEY", "anyt_agent_custom_key_123456789012345678")

        config = GlobalConfig(
            current_environment="dev",
            environments={
                "dev": EnvironmentConfig(
                    api_url="http://localhost:8000",
                    auth_token="config-token",
                )
            },
        )

        client = APIClient.from_config(config)

        # Both environment variables should be applied
        assert client.base_url == "https://custom.example.com"
        assert client.agent_key == "anyt_agent_custom_key_123456789012345678"
        assert client.auth_token is None
        assert client.headers["X-API-Key"] == "anyt_agent_custom_key_123456789012345678"
