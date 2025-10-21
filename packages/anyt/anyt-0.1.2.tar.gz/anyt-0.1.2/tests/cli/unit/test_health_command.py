"""Tests for health check command."""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import GlobalConfig, EnvironmentConfig


@pytest.mark.cli
class TestHealthCommand:
    """Tests for anyt health command."""

    def test_health_check_success(self, cli_runner: CliRunner, monkeypatch):
        """Test successful health check with valid response."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        with patch("cli.commands.health.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "healthy",
                "timestamp": "2025-10-20T19:41:25.992622",
            }
            mock_get.return_value = mock_response

            result = cli_runner.invoke(app, ["health"])

        assert result.exit_code == 0
        assert "Backend server is healthy" in result.output
        assert "healthy" in result.output
        assert "2025-10-20T19:41:25.992622" in result.output

    def test_health_check_explicit_command(self, cli_runner: CliRunner, monkeypatch):
        """Test health check with explicit 'check' subcommand."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        with patch("cli.commands.health.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "healthy",
                "timestamp": "2025-10-20T19:41:25.992622",
            }
            mock_get.return_value = mock_response

            result = cli_runner.invoke(app, ["health", "check"])

        assert result.exit_code == 0
        assert "Backend server is healthy" in result.output

    def test_health_check_no_environments(self, cli_runner: CliRunner, monkeypatch):
        """Test health check when no environments are configured."""
        config = GlobalConfig()
        config.environments = {}
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        result = cli_runner.invoke(app, ["health"])

        assert result.exit_code == 1
        assert "No environments configured" in result.output
        assert "anyt env add" in result.output

    def test_health_check_connection_refused(self, cli_runner: CliRunner, monkeypatch):
        """Test health check when server connection is refused."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        with patch("cli.commands.health.httpx.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection refused")

            result = cli_runner.invoke(app, ["health"])

        assert result.exit_code == 1
        assert "Backend server is unreachable" in result.output
        assert "Connection refused" in result.output
        assert "Is the server running?" in result.output

    def test_health_check_timeout(self, cli_runner: CliRunner, monkeypatch):
        """Test health check when request times out."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        with patch("cli.commands.health.httpx.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timed out")

            result = cli_runner.invoke(app, ["health"])

        assert result.exit_code == 1
        assert "Backend server did not respond in time" in result.output
        assert "Request timed out" in result.output
        assert "Server may be overloaded" in result.output

    def test_health_check_http_error(self, cli_runner: CliRunner, monkeypatch):
        """Test health check when server returns HTTP error."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        with patch("cli.commands.health.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error",
                request=MagicMock(),
                response=mock_response,
            )
            mock_get.return_value = mock_response

            result = cli_runner.invoke(app, ["health"])

        assert result.exit_code == 1
        assert "Backend server returned an error" in result.output
        assert "500" in result.output

    def test_health_check_invalid_response_format(
        self, cli_runner: CliRunner, monkeypatch
    ):
        """Test health check when server returns response without 'status' field."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        with patch("cli.commands.health.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "timestamp": "2025-10-20T19:41:25.992622"
            }
            mock_get.return_value = mock_response

            result = cli_runner.invoke(app, ["health"])

        assert result.exit_code == 1
        assert "Backend server returned invalid response" in result.output
        assert "Expected 'status' field" in result.output

    def test_health_check_invalid_json(self, cli_runner: CliRunner, monkeypatch):
        """Test health check when server returns invalid JSON."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        with patch("cli.commands.health.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response

            result = cli_runner.invoke(app, ["health"])

        assert result.exit_code == 1
        assert "Backend server returned invalid JSON" in result.output
        assert "Invalid JSON" in result.output

    def test_health_check_displays_environment_info(
        self, cli_runner: CliRunner, monkeypatch
    ):
        """Test that health check displays environment and API URL."""
        config = GlobalConfig()
        config.environments = {
            "staging": EnvironmentConfig(api_url="https://staging.example.com")
        }
        config.current_environment = "staging"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        with patch("cli.commands.health.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "healthy",
                "timestamp": "2025-10-20T19:41:25.992622",
            }
            mock_get.return_value = mock_response

            result = cli_runner.invoke(app, ["health"])

        assert result.exit_code == 0
        assert "staging" in result.output
        assert "staging.example.com" in result.output

    def test_health_check_calls_correct_endpoint(
        self, cli_runner: CliRunner, monkeypatch
    ):
        """Test that health check calls the /health endpoint."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        with patch("cli.commands.health.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "healthy",
                "timestamp": "2025-10-20T19:41:25.992622",
            }
            mock_get.return_value = mock_response

            result = cli_runner.invoke(app, ["health"])

            # Verify the correct endpoint was called
            mock_get.assert_called_once_with(
                "http://localhost:8000/health", timeout=5.0
            )

        assert result.exit_code == 0
