"""Tests for preference management commands."""

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import GlobalConfig, EnvironmentConfig


# ============================================================================
# Preference Commands Tests
# ============================================================================


@pytest.mark.cli
class TestPreferenceCommands:
    """Tests for anyt preference subcommands."""

    def test_preference_show_no_auth_token(self, cli_runner: CliRunner, monkeypatch):
        """Test showing preferences without JWT authentication (agent key only)."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                agent_key="sk_test_key",  # Agent key, not JWT
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        result = cli_runner.invoke(app, ["preference", "show"])

        assert result.exit_code == 1
        assert "requires user authentication" in result.output
        assert "not supported with agent API keys" in result.output

    def test_preference_show_no_preferences_set(
        self, cli_runner: CliRunner, monkeypatch
    ):
        """Test showing preferences when none are set."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-jwt-token",
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        # Mock API client to return None for no preferences
        async def mock_get_preferences():
            return None

        with patch(
            "cli.commands.preference.APIClient.from_config"
        ) as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.auth_token = "test-jwt-token"
            mock_client.get_user_preferences = mock_get_preferences
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["preference", "show"])

        assert result.exit_code == 0
        assert "No preferences set" in result.output
        assert "set-workspace" in result.output

    def test_preference_show_with_preferences(self, cli_runner: CliRunner, monkeypatch):
        """Test showing preferences when they are set."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-jwt-token",
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        # Mock API client responses
        async def mock_get_preferences():
            return {
                "user_id": "test-user",
                "current_workspace_id": 1,
                "current_project_id": 5,
            }

        async def mock_get_workspace(workspace_id):
            return {"id": 1, "name": "My Workspace", "identifier": "WORK"}

        with patch(
            "cli.commands.preference.APIClient.from_config"
        ) as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.auth_token = "test-jwt-token"
            mock_client.get_user_preferences = mock_get_preferences
            mock_client.get_workspace = mock_get_workspace
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["preference", "show"])

        assert result.exit_code == 0
        assert "User Preferences" in result.output
        assert "My Workspace" in result.output

    def test_preference_set_workspace_success(self, cli_runner: CliRunner, monkeypatch):
        """Test setting workspace preference successfully."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-jwt-token",
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        # Mock API client responses
        async def mock_set_workspace(workspace_id):
            return {
                "user_id": "test-user",
                "current_workspace_id": workspace_id,
                "current_project_id": None,
            }

        async def mock_get_workspace(workspace_id):
            return {"id": workspace_id, "name": "Team Workspace", "identifier": "TEAM"}

        with patch(
            "cli.commands.preference.APIClient.from_config"
        ) as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.auth_token = "test-jwt-token"
            mock_client.set_current_workspace = mock_set_workspace
            mock_client.get_workspace = mock_get_workspace
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["preference", "set-workspace", "2"])

        assert result.exit_code == 0
        assert "Current workspace updated" in result.output
        assert "Team Workspace" in result.output

    def test_preference_set_workspace_no_auth_token(
        self, cli_runner: CliRunner, monkeypatch
    ):
        """Test setting workspace preference without JWT authentication."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                agent_key="sk_test_key",  # Agent key, not JWT
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        result = cli_runner.invoke(app, ["preference", "set-workspace", "2"])

        assert result.exit_code == 1
        assert "requires user authentication" in result.output

    def test_preference_set_project_success(self, cli_runner: CliRunner, monkeypatch):
        """Test setting project preference successfully."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-jwt-token",
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        # Mock API client responses
        async def mock_set_project(workspace_id, project_id):
            return {
                "user_id": "test-user",
                "current_workspace_id": workspace_id,
                "current_project_id": project_id,
            }

        async def mock_get_workspace(workspace_id):
            return {"id": workspace_id, "name": "Team Workspace", "identifier": "TEAM"}

        with patch(
            "cli.commands.preference.APIClient.from_config"
        ) as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.auth_token = "test-jwt-token"
            mock_client.set_current_project = mock_set_project
            mock_client.get_workspace = mock_get_workspace
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["preference", "set-project", "2", "10"])

        assert result.exit_code == 0
        assert "Current workspace updated" in result.output
        assert "Current project updated" in result.output

    def test_preference_set_project_no_auth_token(
        self, cli_runner: CliRunner, monkeypatch
    ):
        """Test setting project preference without JWT authentication."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                agent_key="sk_test_key",  # Agent key, not JWT
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        result = cli_runner.invoke(app, ["preference", "set-project", "2", "10"])

        assert result.exit_code == 1
        assert "requires user authentication" in result.output

    def test_preference_clear_success(self, cli_runner: CliRunner, monkeypatch):
        """Test clearing user preferences successfully."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-jwt-token",
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        # Mock API client responses
        async def mock_clear_preferences():
            return {"success": True, "message": "Preferences cleared"}

        with patch(
            "cli.commands.preference.APIClient.from_config"
        ) as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.auth_token = "test-jwt-token"
            mock_client.clear_user_preferences = mock_clear_preferences
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["preference", "clear"])

        assert result.exit_code == 0
        assert "User preferences cleared" in result.output

    def test_preference_clear_no_auth_token(self, cli_runner: CliRunner, monkeypatch):
        """Test clearing preferences without JWT authentication."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                agent_key="sk_test_key",  # Agent key, not JWT
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        result = cli_runner.invoke(app, ["preference", "clear"])

        assert result.exit_code == 1
        assert "requires user authentication" in result.output

    def test_preference_show_api_error(self, cli_runner: CliRunner, monkeypatch):
        """Test handling API errors when showing preferences."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-jwt-token",
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        # Mock API client to raise an error
        async def mock_get_preferences():
            raise Exception("API connection failed")

        with patch(
            "cli.commands.preference.APIClient.from_config"
        ) as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.auth_token = "test-jwt-token"
            mock_client.get_user_preferences = mock_get_preferences
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["preference", "show"])

        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "API connection failed" in result.output
