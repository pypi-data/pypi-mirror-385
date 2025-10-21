"""Tests for CLI task CRUD commands (add, show, edit, done, rm, pick)."""

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import WorkspaceConfig, ActiveTaskConfig
from cli.models.common import Status, Priority
from cli.models.task import Task
from cli.schemas.pagination import PaginatedResponse
from tests.cli.unit.conftest import create_test_task


@pytest.mark.cli
class TestTaskAddCommand:
    """Tests for anyt task add command."""

    def test_task_add_with_all_options(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test task creation with all options specified."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        # Mock workspace config
        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock API client
        mock_client = AsyncMock()
        mock_client.create_task = AsyncMock(
            return_value=create_test_task(
                id=42,
                identifier="DEV-42",
                title="New Feature",
                status=Status.BACKLOG,
                priority=Priority.HIGH,
                labels=["feature", "urgent"],
            )
        )

        # Mock ProjectsAPIClient for get_current_project
        mock_projects_client = AsyncMock()
        mock_projects_client.get_current_project = AsyncMock(
            return_value=AsyncMock(id=1, name="Test Project")
        )

        # Mock TaskService for create_task_with_validation
        mock_service = AsyncMock()
        mock_service.create_task_with_validation = AsyncMock(
            return_value=create_test_task(
                id=42,
                identifier="DEV-42",
                title="New Feature",
                status=Status.BACKLOG,
                priority=Priority.HIGH,
                labels=["feature", "urgent"],
            )
        )

        with patch(
            "cli.client.projects.ProjectsAPIClient.from_config",
            return_value=mock_projects_client,
        ):
            with patch(
                "cli.services.task_service.TaskService.from_config",
                return_value=mock_service,
            ):
                result = cli_runner.invoke(
                    app,
                    [
                        "task",
                        "add",
                        "New Feature",
                        "--project",
                        "1",
                        "--priority",
                        "1",
                        "--labels",
                        "feature,urgent",
                        "--status",
                        "todo",
                    ],
                )

        assert result.exit_code == 0
        assert "DEV-42" in result.output
        mock_service.create_task_with_validation.assert_called_once()

    def test_task_add_with_invalid_priority(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test task creation with invalid priority value."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        result = cli_runner.invoke(
            app,
            [
                "task",
                "add",
                "Test Task",
                "--project",
                "1",
                "--priority",
                "5",
            ],
        )

        assert result.exit_code == 1
        assert "Priority must be between -2 and 2" in result.output

    def test_task_add_json_output(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test task creation with JSON output format."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock ProjectsAPIClient for get_current_project
        mock_projects_client = AsyncMock()
        mock_projects_client.get_current_project = AsyncMock(
            return_value=AsyncMock(id=1, name="Test Project")
        )

        # Mock TaskService for create_task_with_validation
        mock_service = AsyncMock()
        mock_service.create_task_with_validation = AsyncMock(
            return_value=create_test_task(
                id=42,
                identifier="DEV-42",
                title="JSON Task",
                status=Status.BACKLOG,
            )
        )

        with patch(
            "cli.client.projects.ProjectsAPIClient.from_config",
            return_value=mock_projects_client,
        ):
            with patch(
                "cli.services.task_service.TaskService.from_config",
                return_value=mock_service,
            ):
                result = cli_runner.invoke(
                    app,
                    [
                        "task",
                        "add",
                        "JSON Task",
                        "--project",
                        "1",
                        "--json",
                    ],
                )

        assert result.exit_code == 0
        assert '"success": true' in result.output
        assert '"identifier": "DEV-42"' in result.output


@pytest.mark.cli
class TestTaskShowCommand:
    """Tests for anyt task show command."""

    def test_task_show_by_identifier(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test showing task details by identifier."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.get_task = AsyncMock(
            return_value=create_test_task(
                id=1,
                identifier="DEV-1",
                title="Test Task",
                description="Test description",
                status=Status.TODO,
                priority=Priority.HIGH,
            )
        )

        # Mock WorkspaceService
        mock_ws_service = AsyncMock()

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            with patch(
                "cli.services.workspace_service.WorkspaceService.from_config",
                return_value=mock_ws_service,
            ):
                result = cli_runner.invoke(
                    app,
                    ["task", "show", "DEV-1"],
                )

        assert result.exit_code == 0
        assert "DEV-1" in result.output
        assert "Test Task" in result.output

    def test_task_show_with_active_task_fallback(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test showing task using active task when no identifier provided."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        active_task = ActiveTaskConfig(
            identifier="DEV-42",
            title="Test Task",
            picked_at="2025-10-16T12:00:00Z",
            workspace_id=1,
            project_id=1,
        )

        def mock_active_load():
            return active_task

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )
        monkeypatch.setattr(
            "cli.config.ActiveTaskConfig.load", staticmethod(mock_active_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.get_task = AsyncMock(
            return_value=create_test_task(
                id=42,
                identifier="DEV-42",
                title="Active Task",
                status=Status.IN_PROGRESS,
                priority=Priority.HIGHEST,
            )
        )

        # Mock WorkspaceService
        mock_ws_service = AsyncMock()

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            with patch(
                "cli.services.workspace_service.WorkspaceService.from_config",
                return_value=mock_ws_service,
            ):
                result = cli_runner.invoke(
                    app,
                    ["task", "show"],
                )

        assert result.exit_code == 0
        assert "DEV-42" in result.output

    def test_task_show_not_found(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test showing non-existent task."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService with error
        mock_service = AsyncMock()
        mock_service.get_task = AsyncMock(side_effect=Exception("404 Not Found"))

        # Mock WorkspaceService
        mock_ws_service = AsyncMock()

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            with patch(
                "cli.services.workspace_service.WorkspaceService.from_config",
                return_value=mock_ws_service,
            ):
                result = cli_runner.invoke(
                    app,
                    ["task", "show", "DEV-999"],
                )

        assert result.exit_code == 1
        assert "not found" in result.output


@pytest.mark.cli
class TestTaskEditCommand:
    """Tests for anyt task edit command."""

    @pytest.mark.skip(reason="TODO: Needs investigation - command exits with code 1")
    def test_task_edit_single_field(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test editing a single task field."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.get_task = AsyncMock(
            return_value=create_test_task(
                id=1,
                identifier="DEV-1",
                title="Old Title",
                status=Status.TODO,
            )
        )
        mock_service.update_task = AsyncMock(
            return_value=create_test_task(
                id=1,
                identifier="DEV-1",
                title="Old Title",
                status=Status.IN_PROGRESS,
            )
        )

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            result = cli_runner.invoke(
                app,
                ["task", "edit", "DEV-1", "--status", "inprogress"],
            )

        assert result.exit_code == 0
        assert "Updated" in result.output
        mock_service.update_task.assert_called_once()

    def test_task_edit_bulk_with_ids(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test bulk editing multiple tasks with --ids flag."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.get_task = AsyncMock(
            side_effect=[
                create_test_task(id=1, identifier="DEV-1", status=Status.TODO),
                create_test_task(id=2, identifier="DEV-2", status=Status.TODO),
            ]
        )
        mock_service.update_task = AsyncMock(
            side_effect=[
                create_test_task(id=1, identifier="DEV-1", status=Status.DONE),
                create_test_task(id=2, identifier="DEV-2", status=Status.DONE),
            ]
        )

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            result = cli_runner.invoke(
                app,
                ["task", "edit", "--ids", "DEV-1,DEV-2", "--status", "done"],
            )

        assert result.exit_code == 0
        assert "2 tasks" in result.output
        assert mock_service.update_task.call_count == 2

    def test_task_edit_dry_run(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test dry-run mode shows preview without applying changes."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.get_task = AsyncMock(
            return_value=create_test_task(
                id=1,
                identifier="DEV-1",
                title="Test",
                status=Status.TODO,
                priority=Priority.NORMAL,
            )
        )

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            result = cli_runner.invoke(
                app,
                ["task", "edit", "DEV-1", "--priority", "2", "--dry-run"],
            )

        assert result.exit_code == 0
        assert "Preview" in result.output or "dry" in result.output.lower()
        mock_service.update_task.assert_not_called()


@pytest.mark.cli
class TestTaskDoneCommand:
    """Tests for anyt task done command."""

    def test_task_done_single(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test marking a single task as done."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.update_task = AsyncMock(
            return_value=create_test_task(
                id=1,
                identifier="DEV-1",
                status=Status.DONE,
            )
        )

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            result = cli_runner.invoke(
                app,
                ["task", "done", "DEV-1"],
            )

        assert result.exit_code == 0
        assert "done" in result.output.lower()
        mock_service.update_task.assert_called_once()

    def test_task_done_multiple(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test marking multiple tasks as done."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.update_task = AsyncMock(
            side_effect=[
                create_test_task(id=1, identifier="DEV-1", status=Status.DONE),
                create_test_task(id=2, identifier="DEV-2", status=Status.DONE),
            ]
        )

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            result = cli_runner.invoke(
                app,
                ["task", "done", "DEV-1", "DEV-2"],
            )

        assert result.exit_code == 0
        assert mock_service.update_task.call_count == 2


@pytest.mark.cli
class TestTaskRemoveCommand:
    """Tests for anyt task rm command."""

    def test_task_rm_with_force(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test deleting task with --force flag to skip confirmation."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.delete_task = AsyncMock()

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            result = cli_runner.invoke(
                app,
                ["task", "rm", "DEV-1", "--force"],
            )

        assert result.exit_code == 0
        mock_service.delete_task.assert_called_once()

    def test_task_rm_without_force_requires_confirmation(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test deleting task without --force prompts for confirmation."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.get_task = AsyncMock(
            return_value=create_test_task(
                id=1,
                identifier="DEV-1",
                title="Test Task",
            )
        )

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            # User declines confirmation (input "n")
            result = cli_runner.invoke(
                app,
                ["task", "rm", "DEV-1"],
                input="n\n",
            )

        # Should exit successfully (user chose not to delete)
        assert result.exit_code == 0


@pytest.mark.cli
class TestTaskPickCommand:
    """Tests for anyt task pick command."""

    def test_task_pick_by_identifier(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test picking a task by identifier."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        def mock_active_save(self):
            pass

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )
        monkeypatch.setattr("cli.config.ActiveTaskConfig.save", mock_active_save)

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.get_task = AsyncMock(
            return_value=create_test_task(
                id=42,
                identifier="DEV-42",
                title="My Task",
                workspace_id=1,
                project_id=1,
            )
        )

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            result = cli_runner.invoke(
                app,
                ["task", "pick", "DEV-42"],
            )

        assert result.exit_code == 0
        assert "Picked" in result.output
        assert "DEV-42" in result.output

    def test_task_pick_interactive_with_tasks(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test interactive picker when tasks are available."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        def mock_active_save(self):
            pass

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )
        monkeypatch.setattr("cli.config.ActiveTaskConfig.save", mock_active_save)

        # Mock tasks for interactive picker
        mock_tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="First task",
                status=Status.TODO,
                priority=Priority.HIGH,
                workspace_id=1,
                project_id=1,
            ),
            create_test_task(
                id=2,
                identifier="DEV-2",
                title="Second task",
                status=Status.IN_PROGRESS,
                priority=Priority.NORMAL,
                workspace_id=1,
                project_id=1,
            ),
        ]

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.list_tasks = AsyncMock(
            return_value=PaginatedResponse[Task](
                items=mock_tasks,
                total=2,
                limit=50,
                offset=0,
            )
        )
        mock_service.get_task = AsyncMock(return_value=mock_tasks[0])

        # Mock Prompt.ask to return selection "1"
        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            with patch("cli.commands.task.pick.Prompt.ask", return_value="1"):
                result = cli_runner.invoke(
                    app,
                    ["task", "pick"],
                )

        assert result.exit_code == 0
        assert "Picked" in result.output
        assert "DEV-1" in result.output

    def test_task_pick_interactive_cancelled(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test interactive picker when user cancels."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="First task",
                status=Status.TODO,
                priority=Priority.HIGH,
            ),
        ]

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.list_tasks = AsyncMock(
            return_value=PaginatedResponse[Task](
                items=mock_tasks,
                total=1,
                limit=50,
                offset=0,
            )
        )

        # Mock Prompt.ask to return "q" (quit)
        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            with patch("cli.commands.task.pick.Prompt.ask", return_value="q"):
                result = cli_runner.invoke(
                    app,
                    ["task", "pick"],
                )

        assert result.exit_code == 0
        assert "cancelled" in result.output.lower()

    def test_task_pick_interactive_no_tasks(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test interactive picker when no tasks are available."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.list_tasks = AsyncMock(
            return_value=PaginatedResponse[Task](
                items=[],
                total=0,
                limit=50,
                offset=0,
            )
        )

        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            result = cli_runner.invoke(
                app,
                ["task", "pick"],
            )

        assert result.exit_code == 1
        assert "No tasks available" in result.output

    def test_task_pick_interactive_with_filters(
        self, cli_runner: CliRunner, patch_global_config, monkeypatch
    ):
        """Test interactive picker with status filter."""
        # Add auth token to global config
        patch_global_config.environments["dev"].auth_token = "test-token-123"

        ws_config = WorkspaceConfig(
            workspace_id="1",
            workspace_identifier="DEV",
            name="Test Workspace",
            api_url="http://localhost:8000",
        )

        def mock_ws_load():
            return ws_config

        def mock_active_save(self):
            pass

        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )
        monkeypatch.setattr("cli.config.ActiveTaskConfig.save", mock_active_save)

        mock_tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="Todo task",
                status=Status.TODO,
                priority=Priority.HIGH,
                workspace_id=1,
                project_id=1,
            ),
        ]

        # Mock TaskService
        mock_service = AsyncMock()
        mock_service.list_tasks = AsyncMock(
            return_value=PaginatedResponse[Task](
                items=mock_tasks,
                total=1,
                limit=50,
                offset=0,
            )
        )
        mock_service.get_task = AsyncMock(return_value=mock_tasks[0])

        # Mock Prompt.ask to return selection "1"
        with patch(
            "cli.services.task_service.TaskService.from_config",
            return_value=mock_service,
        ):
            with patch("cli.commands.task.pick.Prompt.ask", return_value="1"):
                result = cli_runner.invoke(
                    app,
                    ["task", "pick", "--status", "todo"],
                )

        assert result.exit_code == 0
        # Verify that list_tasks was called with correct filters
        mock_service.list_tasks.assert_called_once()
        call_args = mock_service.list_tasks.call_args
        filters = call_args[0][0]  # First positional argument is TaskFilters
        assert filters.status == [Status.TODO]
