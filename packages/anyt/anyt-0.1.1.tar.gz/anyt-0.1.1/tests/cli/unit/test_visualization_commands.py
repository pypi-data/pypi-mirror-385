"""Tests for CLI visualization commands: board, timeline, summary, graph."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import GlobalConfig, EnvironmentConfig


# ============================================================================
# Board Command Tests
# ============================================================================


@pytest.mark.cli
class TestBoardCommand:
    """Tests for anyt board command."""

    def test_board_basic_display(
        self, cli_runner: CliRunner, monkeypatch, sample_tasks
    ):
        """Test basic board rendering with tasks grouped by status."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch(
            "cli.client.APIClient.list_tasks", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "items": sample_tasks,
                "pagination": {"total": len(sample_tasks), "limit": 200, "offset": 0},
            }

            result = cli_runner.invoke(app, ["board"])

        assert result.exit_code == 0
        # Board should show workspace name
        assert "DEV" in result.output or "Board" in result.output

    def test_board_empty_workspace(self, cli_runner: CliRunner, monkeypatch):
        """Test board display when workspace has no tasks."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch(
            "cli.client.APIClient.list_tasks", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "items": [],
                "pagination": {"total": 0, "limit": 200, "offset": 0},
            }

            result = cli_runner.invoke(app, ["board"])

        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_board_with_mine_filter(
        self, cli_runner: CliRunner, monkeypatch, sample_tasks
    ):
        """Test board with --mine filter to show only user's tasks."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch(
            "cli.client.APIClient.list_tasks", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "items": sample_tasks[:2],  # Subset of tasks
                "pagination": {"total": 2, "limit": 200, "offset": 0},
            }

            result = cli_runner.invoke(app, ["board", "--mine"])

        assert result.exit_code == 0
        # Verify the filter was passed to API
        mock_list.assert_called_once()
        call_kwargs = mock_list.call_args.kwargs
        assert call_kwargs.get("owner") == "me"

    def test_board_with_status_filter(
        self, cli_runner: CliRunner, monkeypatch, sample_tasks
    ):
        """Test board with status filter."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch(
            "cli.client.APIClient.list_tasks", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "items": [t for t in sample_tasks if t["status"] == "inprogress"],
                "pagination": {"total": 1, "limit": 200, "offset": 0},
            }

            result = cli_runner.invoke(app, ["board", "--status", "inprogress"])

        assert result.exit_code == 0
        mock_list.assert_called_once()
        call_kwargs = mock_list.call_args.kwargs
        assert call_kwargs.get("status") == ["inprogress"]

    def test_board_compact_mode(self, cli_runner: CliRunner, monkeypatch, sample_tasks):
        """Test board compact display mode."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch(
            "cli.client.APIClient.list_tasks", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "items": sample_tasks,
                "pagination": {"total": len(sample_tasks), "limit": 200, "offset": 0},
            }

            result = cli_runner.invoke(app, ["board", "--compact"])

        assert result.exit_code == 0
        # Compact mode should show counts
        assert "(" in result.output  # Status counts like "Backlog(2)"

    def test_board_with_limit(self, cli_runner: CliRunner, monkeypatch, sample_tasks):
        """Test board with limit parameter."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch(
            "cli.client.APIClient.list_tasks", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "items": sample_tasks,
                "pagination": {"total": len(sample_tasks), "limit": 200, "offset": 0},
            }

            result = cli_runner.invoke(app, ["board", "--limit", "5"])

        assert result.exit_code == 0

    def test_board_not_in_workspace(self, cli_runner: CliRunner, monkeypatch):
        """Test board command when not in a workspace directory."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return None

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        result = cli_runner.invoke(app, ["board"])

        assert result.exit_code == 1
        assert (
            "Not in a workspace" in result.output or "workspace init" in result.output
        )


# ============================================================================
# Timeline Command Tests
# ============================================================================


@pytest.mark.cli
class TestTimelineCommand:
    """Tests for anyt timeline command."""

    def test_timeline_basic_display(self, cli_runner: CliRunner, monkeypatch):
        """Test basic timeline display for a task."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch("cli.client.APIClient.get_task", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "id": 1,
                "identifier": "DEV-42",
                "title": "Test Task",
                "status": "todo",
                "priority": 1,
                "created_at": "2025-10-01T10:00:00Z",
                "updated_at": "2025-10-16T10:00:00Z",
            }

            result = cli_runner.invoke(app, ["timeline", "DEV-42"])

        assert result.exit_code == 0
        assert "DEV-42" in result.output
        assert "Timeline" in result.output

    def test_timeline_task_not_found(self, cli_runner: CliRunner, monkeypatch):
        """Test timeline when task is not found."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch("cli.client.APIClient.get_task", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("404 Not Found")

            result = cli_runner.invoke(app, ["timeline", "DEV-999"])

        assert result.exit_code == 1
        assert "not found" in result.output


# ============================================================================
# Summary Command Tests
# ============================================================================


@pytest.mark.cli
class TestSummaryCommand:
    """Tests for anyt summary command."""

    def test_summary_basic_display(
        self, cli_runner: CliRunner, monkeypatch, sample_tasks
    ):
        """Test basic workspace summary display."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch(
            "cli.client.APIClient.list_tasks", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "items": sample_tasks,
                "pagination": {"total": len(sample_tasks), "limit": 500, "offset": 0},
                "total": len(sample_tasks),
            }

            result = cli_runner.invoke(app, ["summary"])

        assert result.exit_code == 0
        assert "Summary" in result.output
        # Should show done, active, and next priorities
        assert "Done" in result.output or "done" in result.output

    def test_summary_with_period_filter(
        self, cli_runner: CliRunner, monkeypatch, sample_tasks
    ):
        """Test summary with period filter."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch(
            "cli.client.APIClient.list_tasks", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "items": sample_tasks,
                "pagination": {"total": len(sample_tasks), "limit": 500, "offset": 0},
                "total": len(sample_tasks),
            }

            result = cli_runner.invoke(app, ["summary", "--period", "weekly"])

        assert result.exit_code == 0
        assert "Weekly" in result.output or "weekly" in result.output

    def test_summary_empty_workspace(self, cli_runner: CliRunner, monkeypatch):
        """Test summary when workspace has no tasks."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch(
            "cli.client.APIClient.list_tasks", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "items": [],
                "pagination": {"total": 0, "limit": 500, "offset": 0},
                "total": 0,
            }

            result = cli_runner.invoke(app, ["summary"])

        assert result.exit_code == 0
        assert "No tasks" in result.output


# ============================================================================
# Graph Command Tests
# ============================================================================


@pytest.mark.cli
class TestGraphCommand:
    """Tests for anyt graph command."""

    def test_graph_for_specific_task(self, cli_runner: CliRunner, monkeypatch):
        """Test dependency graph for a specific task."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch("cli.client.APIClient.get_task", new_callable=AsyncMock) as mock_get:
            with patch(
                "cli.client.APIClient.get_task_dependencies", new_callable=AsyncMock
            ) as mock_deps:
                with patch(
                    "cli.client.APIClient.get_task_dependents", new_callable=AsyncMock
                ) as mock_depts:
                    mock_get.return_value = {
                        "id": 2,
                        "identifier": "DEV-2",
                        "title": "Middle Task",
                        "status": "inprogress",
                    }
                    mock_deps.return_value = [
                        {"identifier": "DEV-1", "title": "First Task", "status": "done"}
                    ]
                    mock_depts.return_value = [
                        {
                            "identifier": "DEV-3",
                            "title": "Last Task",
                            "status": "backlog",
                        }
                    ]

                    result = cli_runner.invoke(app, ["graph", "DEV-2"])

        assert result.exit_code == 0
        assert "DEV-2" in result.output

    def test_graph_without_task_shows_workspace_graph(
        self, cli_runner: CliRunner, monkeypatch
    ):
        """Test graph command without task identifier shows full workspace graph."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        # Mock APIClient to return empty task list
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.list_tasks = AsyncMock(return_value={"items": [], "total": 0})

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )
        monkeypatch.setattr(
            "cli.commands.board.APIClient.from_config", lambda _: mock_client
        )

        result = cli_runner.invoke(app, ["graph"])

        assert result.exit_code == 0
        assert "No tasks found in workspace" in result.output

    def test_graph_task_not_found(self, cli_runner: CliRunner, monkeypatch):
        """Test graph when task is not found."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        }
        config.current_environment = "dev"

        ws_config = MagicMock()
        ws_config.workspace_id = "1"
        ws_config.workspace_identifier = "DEV"
        ws_config.name = "Test Workspace"
        ws_config.api_url = "http://localhost:8000"

        def mock_global_load():
            return config

        def mock_workspace_load():
            return ws_config

        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", staticmethod(mock_global_load)
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_workspace_load)
        )

        with patch("cli.client.APIClient.get_task", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("404 Not Found")

            result = cli_runner.invoke(app, ["graph", "DEV-999"])

        assert result.exit_code == 1
        assert "not found" in result.output
