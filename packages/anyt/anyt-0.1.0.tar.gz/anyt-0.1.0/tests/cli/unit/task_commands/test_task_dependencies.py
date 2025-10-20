"""Tests for CLI task dependency commands."""

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import WorkspaceConfig


@pytest.mark.cli
class TestDependencyAddCommand:
    """Tests for anyt task dep add command."""

    def test_dep_add_single_dependency(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test adding a single dependency."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1", name="Test Workspace", api_url="http://localhost:8000"
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_client = AsyncMock()
        mock_client.add_task_dependency = AsyncMock()

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "dep", "add", "DEV-2", "--on", "DEV-1"],
            )

        assert result.exit_code == 0
        assert "depends on" in result.output
        mock_client.add_task_dependency.assert_called_once_with("DEV-2", "DEV-1")

    def test_dep_add_multiple_dependencies(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test adding multiple dependencies with comma-separated list."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1", name="Test Workspace", api_url="http://localhost:8000"
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_client = AsyncMock()
        mock_client.add_task_dependency = AsyncMock()

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "dep", "add", "DEV-3", "--on", "DEV-1,DEV-2"],
            )

        assert result.exit_code == 0
        assert mock_client.add_task_dependency.call_count == 2

    def test_dep_add_self_dependency_prevented(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test that self-dependency is prevented."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1", name="Test Workspace", api_url="http://localhost:8000"
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_client = AsyncMock()

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "dep", "add", "DEV-1", "--on", "DEV-1"],
            )

        assert result.exit_code == 1
        assert "cannot depend on itself" in result.output
        mock_client.add_task_dependency.assert_not_called()

    def test_dep_add_circular_dependency_detected(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test that circular dependencies are detected and prevented."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1", name="Test Workspace", api_url="http://localhost:8000"
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_client = AsyncMock()
        mock_client.add_task_dependency = AsyncMock(
            side_effect=Exception("circular dependency")
        )

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "dep", "add", "DEV-2", "--on", "DEV-3"],
            )

        assert result.exit_code == 1
        assert "circular" in result.output.lower()


@pytest.mark.cli
class TestDependencyRemoveCommand:
    """Tests for anyt task dep rm command."""

    def test_dep_rm_single_dependency(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test removing a single dependency."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1", name="Test Workspace", api_url="http://localhost:8000"
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_client = AsyncMock()
        mock_client.remove_task_dependency = AsyncMock()

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "dep", "rm", "DEV-2", "--on", "DEV-1"],
            )

        assert result.exit_code == 0
        assert "Removed" in result.output
        mock_client.remove_task_dependency.assert_called_once()

    def test_dep_rm_multiple_dependencies(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test removing multiple dependencies."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1", name="Test Workspace", api_url="http://localhost:8000"
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_client = AsyncMock()
        mock_client.remove_task_dependency = AsyncMock()

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "dep", "rm", "DEV-3", "--on", "DEV-1,DEV-2"],
            )

        assert result.exit_code == 0
        assert mock_client.remove_task_dependency.call_count == 2


@pytest.mark.cli
class TestDependencyListCommand:
    """Tests for anyt task dep list command."""

    def test_dep_list_shows_dependencies_and_dependents(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test listing both dependencies and dependents of a task."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1", name="Test Workspace", api_url="http://localhost:8000"
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_client = AsyncMock()
        mock_client.get_task = AsyncMock(
            return_value={
                "id": 2,
                "identifier": "DEV-2",
                "title": "Current Task",
            }
        )
        mock_client.get_task_dependencies = AsyncMock(
            return_value=[
                {
                    "id": 1,
                    "identifier": "DEV-1",
                    "title": "Dependency",
                    "status": "done",
                }
            ]
        )
        mock_client.get_task_dependents = AsyncMock(
            return_value=[
                {
                    "id": 3,
                    "identifier": "DEV-3",
                    "title": "Blocked Task",
                    "status": "backlog",
                }
            ]
        )

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "dep", "list", "DEV-2"],
            )

        assert result.exit_code == 0
        assert "Dependencies" in result.output
        assert "DEV-1" in result.output
        assert "DEV-3" in result.output
