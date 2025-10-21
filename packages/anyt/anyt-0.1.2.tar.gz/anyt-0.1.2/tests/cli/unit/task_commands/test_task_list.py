"""Tests for CLI task list command."""

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import WorkspaceConfig
from cli.models.common import Status, Priority
from cli.models.task import Task
from cli.schemas.pagination import PaginatedResponse
from tests.cli.unit.conftest import create_test_task


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
            return_value=PaginatedResponse[Task](
                items=[
                    create_test_task(
                        id=1,
                        identifier="DEV-1",
                        title="Todo Task",
                        status=Status.TODO,
                        priority=Priority.HIGH,
                    )
                ],
                total=1,
                limit=50,
                offset=0,
            )
        )

        with patch(
            "cli.client.tasks.TasksAPIClient.from_config", return_value=mock_client
        ):
            result = cli_runner.invoke(
                app,
                ["task", "list", "--status", "todo"],
            )

        assert result.exit_code == 0
        assert "DEV-1" in result.output
        mock_client.list_tasks.assert_called_once()
        # Check that a TaskFilters object was passed
        call_args = mock_client.list_tasks.call_args
        filters = call_args[0][0]  # First positional argument
        assert filters.status == [Status.TODO]

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
            return_value=PaginatedResponse[Task](
                items=[
                    create_test_task(
                        id=1,
                        identifier="DEV-1",
                        title="First",
                        status=Status.TODO,
                        priority=Priority.HIGHEST,
                    ),
                    create_test_task(
                        id=2,
                        identifier="DEV-2",
                        title="Second",
                        status=Status.TODO,
                        priority=Priority.HIGH,
                    ),
                ],
                total=2,
                limit=50,
                offset=0,
            )
        )

        with patch(
            "cli.client.tasks.TasksAPIClient.from_config", return_value=mock_client
        ):
            result = cli_runner.invoke(
                app,
                ["task", "list", "--sort", "updated_at", "--order", "asc"],
            )

        assert result.exit_code == 0
        mock_client.list_tasks.assert_called_once()
        # Check that a TaskFilters object was passed
        call_args = mock_client.list_tasks.call_args
        filters = call_args[0][0]  # First positional argument
        assert filters.sort_by == "updated_at"
        assert filters.order == "asc"

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
            return_value=PaginatedResponse[Task](
                items=[],
                total=0,
                limit=50,
                offset=0,
            )
        )

        with patch(
            "cli.client.tasks.TasksAPIClient.from_config", return_value=mock_client
        ):
            result = cli_runner.invoke(
                app,
                ["task", "list", "--mine"],
            )

        assert result.exit_code == 0
        mock_client.list_tasks.assert_called_once()
        # Check that a TaskFilters object was passed
        call_args = mock_client.list_tasks.call_args
        filters = call_args[0][0]  # First positional argument
        assert filters.owner == "me"

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
            return_value=PaginatedResponse[Task](
                items=[
                    create_test_task(
                        id=1,
                        identifier="DEV-1",
                        title="Task 1",
                        status=Status.TODO,
                        priority=Priority.HIGH,
                    )
                ],
                total=1,
                limit=50,
                offset=0,
            )
        )

        with patch(
            "cli.client.tasks.TasksAPIClient.from_config", return_value=mock_client
        ):
            result = cli_runner.invoke(
                app,
                ["task", "list", "--json"],
            )

        assert result.exit_code == 0
        assert '"success": true' in result.output
        assert '"items"' in result.output
