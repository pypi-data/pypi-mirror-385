"""Unit tests for CLI AI-powered commands with proper mocking."""

from unittest.mock import AsyncMock, MagicMock, patch
import json

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import GlobalConfig, EnvironmentConfig


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = GlobalConfig()
    config.environments = {
        "dev": EnvironmentConfig(
            api_url="http://localhost:8000",
            auth_token="test-token",
        )
    }
    config.current_environment = "dev"
    return config


@pytest.fixture
def mock_workspace_config():
    """Create mock workspace configuration."""
    ws_config = MagicMock()
    ws_config.workspace_id = "1"
    ws_config.workspace_identifier = "DEV"
    ws_config.name = "Test Workspace"
    ws_config.api_url = "http://localhost:8000"
    return ws_config


# ============================================================================
# AI Decompose Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIDecomposeCommand:
    """Tests for anyt ai decompose command."""

    def test_decompose_basic(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test basic goal decomposition."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.decompose_goal", new_callable=AsyncMock) as mock_decompose:
            mock_decompose.return_value = {
                "goal": "Add user authentication",
                "tasks": [{"title": "Task 1"}, {"title": "Task 2"}],
                "dependencies": [],
                "summary": "Created 2 tasks",
                "cost_tokens": 1000,
            }

            result = cli_runner.invoke(app, ["ai", "decompose", "Add user authentication"])

            assert result.exit_code == 0
            assert "Decomposition complete" in result.output or "Tasks created" in result.output
            mock_decompose.assert_called_once()

    def test_decompose_with_options(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test decompose with max tasks and task size options."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.decompose_goal", new_callable=AsyncMock) as mock_decompose:
            mock_decompose.return_value = {
                "goal": "Add user authentication",
                "tasks": [{"title": f"Task {i}"} for i in range(5)],
                "dependencies": [],
                "summary": "Created 5 tasks",
                "cost_tokens": 1500,
            }

            result = cli_runner.invoke(
                app, ["ai", "decompose", "Add user authentication", "--max-tasks", "5", "--task-size", "3"]
            )

            assert result.exit_code == 0
            assert "Decomposition complete" in result.output
            # Verify the API was called with correct parameters
            call_args = mock_decompose.call_args
            assert call_args.kwargs["max_tasks"] == 5
            assert call_args.kwargs["task_size"] == 3

    def test_decompose_json_output(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test decompose with JSON output format."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.decompose_goal", new_callable=AsyncMock) as mock_decompose:
            mock_decompose.return_value = {
                "goal": "Add user authentication",
                "tasks": [{"title": "Task 1"}],
                "dependencies": [],
                "summary": "Created 1 task",
            }

            result = cli_runner.invoke(
                app, ["ai", "decompose", "Add user authentication", "--json"]
            )

            assert result.exit_code == 0
            # Parse JSON output
            output_data = json.loads(result.output)
            assert output_data["goal"] == "Add user authentication"
            assert len(output_data["tasks"]) == 1


# ============================================================================
# AI Organize Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIOrganizeCommand:
    """Tests for anyt ai organize command."""

    def test_organize_basic(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test basic workspace organization."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.organize_workspace", new_callable=AsyncMock) as mock_organize:
            mock_organize.return_value = {
                "normalized_tasks": [{"id": 1, "title": "Updated title"}],
                "label_suggestions": [{"task_id": 1, "labels": ["backend"]}],
                "duplicates": [],
                "cost_tokens": 500,
            }

            result = cli_runner.invoke(app, ["ai", "organize"])

            assert result.exit_code == 0
            assert "Organization complete" in result.output
            mock_organize.assert_called_once()

    def test_organize_dry_run(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test organize in dry-run mode."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.organize_workspace", new_callable=AsyncMock) as mock_organize:
            mock_organize.return_value = {
                "normalized_tasks": [{"id": 1}],
                "label_suggestions": [],
                "duplicates": [],
            }

            result = cli_runner.invoke(app, ["ai", "organize", "--dry-run"])

            assert result.exit_code == 0
            assert "preview" in result.output.lower()
            # Verify dry_run was passed to API
            assert mock_organize.call_args.kwargs["dry_run"] is True


# ============================================================================
# AI Fill Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIFillCommand:
    """Tests for anyt ai fill command."""

    def test_fill_task(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test AI task auto-fill."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.fill_task_details", new_callable=AsyncMock) as mock_fill:
            mock_fill.return_value = {
                "task_id": "DEV-42",
                "generated": {"description": "Auto-generated description", "labels": ["backend"]},
                "cost_tokens": 300,
            }

            result = cli_runner.invoke(app, ["ai", "fill", "DEV-42"])

            assert result.exit_code == 0
            assert "Content generated" in result.output
            mock_fill.assert_called_once()


# ============================================================================
# AI Suggest Command Tests
# ============================================================================


@pytest.mark.cli
class TestAISuggestCommand:
    """Tests for anyt ai suggest command."""

    def test_suggest_tasks(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test AI task suggestions."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.get_ai_suggestions", new_callable=AsyncMock) as mock_suggest:
            mock_suggest.return_value = {
                "recommendations": [
                    {"task_id": "DEV-1", "reason": "High priority"},
                    {"task_id": "DEV-2", "reason": "Blocks others"},
                ],
                "cost_tokens": 200,
            }

            result = cli_runner.invoke(app, ["ai", "suggest"])

            assert result.exit_code == 0
            assert "Recommended tasks" in result.output
            assert "DEV-1" in result.output


# ============================================================================
# AI Review Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIReviewCommand:
    """Tests for anyt ai review command."""

    def test_review_task(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test AI task review."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.get_task", new_callable=AsyncMock) as mock_get:
            with patch("cli.client.APIClient.review_task", new_callable=AsyncMock) as mock_review:
                mock_get.return_value = {
                    "id": 1,
                    "identifier": "DEV-42",
                    "title": "Test Task",
                    "status": "inprogress",
                }
                mock_review.return_value = {
                    "task_id": "DEV-42",
                    "checks": [{"passed": True, "message": "Title follows convention"}],
                    "warnings": [],
                    "ready": True,
                    "cost_tokens": 200,
                }

                result = cli_runner.invoke(app, ["ai", "review", "DEV-42"])

                assert result.exit_code == 0
                assert "Review complete" in result.output
                assert "ready" in result.output.lower()


# ============================================================================
# AI Summary Command Tests
# ============================================================================


@pytest.mark.cli
class TestAISummaryCommand:
    """Tests for anyt ai summary command."""

    def test_summary_basic(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test AI workspace summary generation."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.generate_summary", new_callable=AsyncMock) as mock_summary:
            mock_summary.return_value = {
                "summary": "Completed 5 tasks this week",
                "period": "today",
                "cost_tokens": 400,
            }

            result = cli_runner.invoke(app, ["ai", "summary"])

            assert result.exit_code == 0
            assert "Workspace Summary" in result.output
            assert "Completed 5 tasks" in result.output


# ============================================================================
# AI Config Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIConfigCommand:
    """Tests for anyt ai config command."""

    def test_config_show(self, cli_runner: CliRunner, mock_config, monkeypatch):
        """Test showing AI configuration."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )

        result = cli_runner.invoke(app, ["ai", "config"])

        assert result.exit_code == 0
        assert "AI Configuration" in result.output
        assert "Provider:" in result.output
        assert "Model:" in result.output

    def test_config_set_model(self, cli_runner: CliRunner, mock_config, monkeypatch):
        """Test setting AI model."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )

        result = cli_runner.invoke(
            app, ["ai", "config", "--model", "claude-3-opus-20240229"]
        )

        assert result.exit_code == 0
        assert "configuration updated" in result.output or "Model:" in result.output


# ============================================================================
# AI Test Command Tests
# ============================================================================


@pytest.mark.cli
class TestAITestCommand:
    """Tests for anyt ai test command."""

    def test_ai_test_connection(self, cli_runner: CliRunner, mock_config, monkeypatch):
        """Test AI connection testing."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )

        # Mock environment variable for API key
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-1234")

        result = cli_runner.invoke(app, ["ai", "test"])

        assert result.exit_code == 0
        assert "API key configured" in result.output or "Provider:" in result.output


# ============================================================================
# AI Usage Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIUsageCommand:
    """Tests for anyt ai usage command."""

    def test_usage_basic(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test showing AI usage statistics."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.get_ai_usage", new_callable=AsyncMock) as mock_usage:
            mock_usage.return_value = {
                "period": "Last 30 Days",
                "operations": [
                    {"name": "Decompose", "calls": 10, "tokens": 10000, "cost": 0.10},
                ],
                "total_calls": 10,
                "total_tokens": 10000,
                "total_cost": 0.10,
                "cache_hits": 5,
                "cache_savings": 0.05,
            }

            result = cli_runner.invoke(app, ["ai", "usage"])

            assert result.exit_code == 0
            assert "AI Usage" in result.output
            assert "Decompose" in result.output

    def test_usage_json_output(self, cli_runner: CliRunner, mock_config, mock_workspace_config, monkeypatch):
        """Test usage with JSON output."""
        monkeypatch.setattr(
            "cli.config.GlobalConfig.load", lambda: mock_config
        )
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", lambda: mock_workspace_config
        )

        with patch("cli.client.APIClient.get_ai_usage", new_callable=AsyncMock) as mock_usage:
            mock_usage.return_value = {
                "period": "Last 30 Days",
                "operations": [],
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
            }

            result = cli_runner.invoke(app, ["ai", "usage", "--json"])

            assert result.exit_code == 0
            # Parse JSON output
            output_data = json.loads(result.output)
            assert "total_calls" in output_data
