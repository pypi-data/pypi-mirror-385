"""Tests for CLI task list command."""

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import WorkspaceConfig


@pytest.mark.cli
class TestTaskListCommand:
    """Tests for anyt task list command."""

    def test_task_list_with_status_filter(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test listing tasks with status filter."""
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
        mock_client.list_tasks = AsyncMock(
            return_value={
                "items": [
                    {
                        "id": 1,
                        "identifier": "DEV-1",
                        "title": "Todo Task",
                        "status": "todo",
                        "priority": 1,
                        "updated_at": "2025-10-16T10:00:00Z",
                    }
                ],
                "total": 1,
            }
        )

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "list", "--status", "todo"],
            )

        assert result.exit_code == 0
        assert "DEV-1" in result.output
        mock_client.list_tasks.assert_called_once()
        call_kwargs = mock_client.list_tasks.call_args.kwargs
        assert call_kwargs["status"] == ["todo"]

    def test_task_list_with_sorting(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test listing tasks with custom sorting."""
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
        mock_client.list_tasks = AsyncMock(
            return_value={
                "items": [
                    {
                        "id": 1,
                        "identifier": "DEV-1",
                        "title": "First",
                        "status": "todo",
                        "priority": 2,
                        "updated_at": "2025-10-16T10:00:00Z",
                    },
                    {
                        "id": 2,
                        "identifier": "DEV-2",
                        "title": "Second",
                        "status": "todo",
                        "priority": 1,
                        "updated_at": "2025-10-16T09:00:00Z",
                    },
                ],
                "total": 2,
            }
        )

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "list", "--sort", "updated_at", "--order", "asc"],
            )

        assert result.exit_code == 0
        mock_client.list_tasks.assert_called_once()
        call_kwargs = mock_client.list_tasks.call_args.kwargs
        assert call_kwargs["sort_by"] == "updated_at"
        assert call_kwargs["order"] == "asc"

    def test_task_list_mine_filter(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test listing tasks assigned to current user."""
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
        mock_client.list_tasks = AsyncMock(
            return_value={
                "items": [],
                "total": 0,
            }
        )

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "list", "--mine"],
            )

        assert result.exit_code == 0
        mock_client.list_tasks.assert_called_once()
        call_kwargs = mock_client.list_tasks.call_args.kwargs
        assert call_kwargs["owner"] == "me"

    def test_task_list_json_output(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test task list with JSON output format."""
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
        mock_client.list_tasks = AsyncMock(
            return_value={
                "items": [
                    {
                        "id": 1,
                        "identifier": "DEV-1",
                        "title": "Task 1",
                        "status": "todo",
                        "priority": 1,
                    }
                ],
                "total": 1,
            }
        )

        with patch("cli.client.APIClient.from_config", return_value=mock_client):
            result = cli_runner.invoke(
                app,
                ["task", "list", "--json"],
            )

        assert result.exit_code == 0
        assert '"success": true' in result.output
        assert '"items"' in result.output
