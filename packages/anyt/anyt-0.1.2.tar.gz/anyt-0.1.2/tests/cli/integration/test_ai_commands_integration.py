"""Tests for CLI AI-powered commands."""

from unittest.mock import AsyncMock, patch
import json

import pytest
from typer.testing import CliRunner

from cli.main import app


# ============================================================================
# AI Decompose Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIDecomposeCommand:
    """Tests for anyt ai decompose command."""

    def test_decompose_basic(self, cli_runner: CliRunner, mock_config_load):
        """Test basic goal decomposition."""
        result = cli_runner.invoke(app, ["ai", "decompose", "Add user authentication"])

        assert result.exit_code == 0
        assert "Decomposing goal" in result.output or "Goal" in result.output

    def test_decompose_with_max_tasks(self, cli_runner: CliRunner, mock_config_load):
        """Test decompose with max tasks limit."""
        result = cli_runner.invoke(
            app, ["ai", "decompose", "Add user authentication", "--max-tasks", "5"]
        )

        assert result.exit_code == 0

    def test_decompose_dry_run(self, cli_runner: CliRunner, mock_config_load):
        """Test decompose in dry-run mode."""
        result = cli_runner.invoke(
            app, ["ai", "decompose", "Add user authentication", "--dry-run"]
        )

        assert result.exit_code == 0

    def test_decompose_json_output(self, cli_runner: CliRunner, mock_config_load):
        """Test decompose with JSON output format."""
        result = cli_runner.invoke(
            app, ["ai", "decompose", "Add user authentication", "--json"]
        )

        assert result.exit_code == 0
        # Should be valid JSON
        try:
            output_data = json.loads(result.output)
            assert "goal" in output_data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


# ============================================================================
# AI Organize Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIOrganizeCommand:
    """Tests for anyt ai organize command."""

    def test_organize_basic(self, cli_runner: CliRunner, mock_config_load):
        """Test basic workspace organization."""
        result = cli_runner.invoke(app, ["ai", "organize"])

        assert result.exit_code == 0
        assert (
            "Organizing workspace" in result.output
            or "Organization complete" in result.output
        )

    def test_organize_dry_run(self, cli_runner: CliRunner, mock_config_load):
        """Test organize in dry-run mode."""
        result = cli_runner.invoke(app, ["ai", "organize", "--dry-run"])

        assert result.exit_code == 0

    def test_organize_titles_only(self, cli_runner: CliRunner, mock_config_load):
        """Test organize with titles-only flag."""
        result = cli_runner.invoke(app, ["ai", "organize", "--titles-only"])

        assert result.exit_code == 0


# ============================================================================
# AI Config Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIConfigCommand:
    """Tests for anyt ai config command."""

    def test_config_show(self, cli_runner: CliRunner, mock_config_load):
        """Test showing AI configuration."""
        result = cli_runner.invoke(app, ["ai", "config"])

        assert result.exit_code == 0
        assert "Configuration" in result.output or "config" in result.output
        assert "model" in result.output.lower() or "provider" in result.output.lower()

    def test_config_set_model(self, cli_runner: CliRunner, mock_config_load):
        """Test setting AI model."""
        result = cli_runner.invoke(
            app, ["ai", "config", "--model", "claude-3-5-sonnet-20241022"]
        )

        assert result.exit_code == 0
        assert "updated" in result.output.lower() or "Configuration" in result.output

    def test_config_set_max_tokens(self, cli_runner: CliRunner, mock_config_load):
        """Test setting max tokens."""
        result = cli_runner.invoke(app, ["ai", "config", "--max-tokens", "8192"])

        assert result.exit_code == 0


# ============================================================================
# AI Test Command Tests
# ============================================================================


@pytest.mark.cli
class TestAITestCommand:
    """Tests for anyt ai test command."""

    def test_ai_test_connection(self, cli_runner: CliRunner, mock_config_load):
        """Test AI connection test."""
        result = cli_runner.invoke(app, ["ai", "test"])

        assert result.exit_code == 0
        assert "Testing" in result.output or "Connected" in result.output


# ============================================================================
# AI Usage Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIUsageCommand:
    """Tests for anyt ai usage command."""

    def test_usage_basic(self, cli_runner: CliRunner, mock_config_load):
        """Test showing AI usage statistics."""
        result = cli_runner.invoke(app, ["ai", "usage"])

        assert result.exit_code == 0
        assert "Usage" in result.output or "tokens" in result.output.lower()

    def test_usage_json_output(self, cli_runner: CliRunner, mock_config_load):
        """Test usage with JSON output."""
        result = cli_runner.invoke(app, ["ai", "usage", "--json"])

        assert result.exit_code == 0
        # Should be valid JSON
        try:
            output_data = json.loads(result.output)
            assert "total_tokens" in output_data or "operations" in output_data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


# ============================================================================
# AI Review Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIReviewCommand:
    """Tests for anyt ai review command."""

    def test_review_task(self, cli_runner: CliRunner, mock_config_load):
        """Test AI task review."""
        with patch("cli.client.APIClient.get_task", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "id": 1,
                "identifier": "DEV-42",
                "title": "Test Task",
                "description": "Test description",
                "status": "inprogress",
                "priority": 1,
            }

            result = cli_runner.invoke(app, ["ai", "review", "DEV-42"])

        assert result.exit_code == 0
        assert "Review" in result.output or "Reviewing" in result.output

    def test_review_json_output(self, cli_runner: CliRunner, mock_config_load):
        """Test review with JSON output."""
        with patch("cli.client.APIClient.get_task", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "id": 1,
                "identifier": "DEV-42",
                "title": "Test Task",
                "description": "Test description",
                "status": "inprogress",
                "priority": 1,
            }

            result = cli_runner.invoke(app, ["ai", "review", "DEV-42", "--json"])

        assert result.exit_code == 0
        # Should be valid JSON
        try:
            output_data = json.loads(result.output)
            assert "task_id" in output_data or "checks" in output_data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


# ============================================================================
# AI Fill Command Tests
# ============================================================================


@pytest.mark.cli
class TestAIFillCommand:
    """Tests for anyt ai fill command."""

    def test_fill_task(self, cli_runner: CliRunner, mock_config_load):
        """Test AI task auto-fill."""
        result = cli_runner.invoke(app, ["ai", "fill", "DEV-42"])

        assert result.exit_code == 0
        assert "Analyzing" in result.output or "generated" in result.output.lower()

    def test_fill_with_specific_fields(self, cli_runner: CliRunner, mock_config_load):
        """Test fill with specific fields."""
        result = cli_runner.invoke(
            app, ["ai", "fill", "DEV-42", "--fields", "description,labels"]
        )

        assert result.exit_code == 0


# ============================================================================
# AI Suggest Command Tests
# ============================================================================


@pytest.mark.cli
class TestAISuggestCommand:
    """Tests for anyt ai suggest command."""

    def test_suggest_tasks(self, cli_runner: CliRunner, mock_config_load):
        """Test AI task suggestions."""
        result = cli_runner.invoke(app, ["ai", "suggest"])

        assert result.exit_code == 0
        assert "Analyzing" in result.output or "Recommended" in result.output

    def test_suggest_json_output(self, cli_runner: CliRunner, mock_config_load):
        """Test suggest with JSON output."""
        result = cli_runner.invoke(app, ["ai", "suggest", "--json"])

        assert result.exit_code == 0
        # Should be valid JSON
        try:
            output_data = json.loads(result.output)
            assert "recommendations" in output_data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


# ============================================================================
# AI Summary Command Tests
# ============================================================================


@pytest.mark.cli
class TestAISummaryCommand:
    """Tests for anyt ai summary command."""

    def test_summary_basic(self, cli_runner: CliRunner, mock_config_load):
        """Test AI workspace summary generation."""
        result = cli_runner.invoke(app, ["ai", "summary"])

        assert result.exit_code == 0
        assert "Generating" in result.output or "Summary" in result.output

    def test_summary_with_period(self, cli_runner: CliRunner, mock_config_load):
        """Test summary with period filter."""
        result = cli_runner.invoke(app, ["ai", "summary", "--period", "weekly"])

        assert result.exit_code == 0
        assert "weekly" in result.output.lower() or "Weekly" in result.output

    def test_summary_markdown_format(self, cli_runner: CliRunner, mock_config_load):
        """Test summary with markdown output format."""
        result = cli_runner.invoke(app, ["ai", "summary", "--format", "markdown"])

        assert result.exit_code == 0
        # Markdown format should have # headers
        assert "#" in result.output or "Workspace Summary" in result.output
