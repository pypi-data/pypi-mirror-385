"""Tests for project CLI commands."""

from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import GlobalConfig, EnvironmentConfig, WorkspaceConfig


@pytest.mark.cli
class TestProjectCreateCommand:
    """Tests for anyt project create command."""

    def test_project_create_not_authenticated(
        self, cli_runner: CliRunner, monkeypatch
    ):
        """Test creating project when not authenticated."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_global_load():
            return config

        def mock_ws_load(self=None):
            return None

        monkeypatch.setattr("cli.config.GlobalConfig.load", mock_global_load)
        monkeypatch.setattr("cli.config.WorkspaceConfig.load", mock_ws_load)

        result = cli_runner.invoke(
            app, ["project", "create", "--name", "Test Project", "--identifier", "TEST"]
        )

        assert result.exit_code == 1
        assert (
            "Not authenticated" in result.output
            or "Not in a workspace directory" in result.output
            or "No workspace configured" in result.output
        )

    def test_project_create_no_workspace_config(
        self, cli_runner: CliRunner, monkeypatch, tmp_path
    ):
        """Test creating project with no workspace configured."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return None

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(
            app, ["project", "create", "--name", "Test Project", "--identifier", "TEST"]
        )

        assert result.exit_code == 1
        assert "No workspace configured" in result.output

    def test_project_create_success_with_workspace_config(
        self, cli_runner: CliRunner, monkeypatch, tmp_path
    ):
        """Test successfully creating a project using workspace config."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        ws_config = WorkspaceConfig(
            workspace_id="123",
            name="Test Workspace",
            api_url="http://localhost:8000",
            workspace_identifier="TEST",
        )

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return ws_config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_create_project = AsyncMock(
            return_value={
                "id": 1,
                "name": "Test Project",
                "identifier": "PROJ",
                "workspace_id": 123,
            }
        )

        with patch("cli.client.APIClient.from_config") as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.create_project = mock_create_project
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(
                app,
                ["project", "create", "--name", "Test Project", "--identifier", "PROJ"],
            )

        assert result.exit_code == 0
        assert "Created project" in result.output
        assert "Test Project" in result.output
        mock_create_project.assert_called_once()


@pytest.mark.cli
class TestProjectListCommand:
    """Tests for anyt project list command."""

    def test_project_list_not_authenticated(self, cli_runner: CliRunner, monkeypatch):
        """Test listing projects when not authenticated."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_global_load():
            return config

        def mock_ws_load(self=None):
            return None

        monkeypatch.setattr("cli.config.GlobalConfig.load", mock_global_load)
        monkeypatch.setattr("cli.config.WorkspaceConfig.load", mock_ws_load)

        result = cli_runner.invoke(app, ["project", "list"])

        assert result.exit_code == 1
        assert (
            "Not authenticated" in result.output
            or "No workspace configured" in result.output
        )

    def test_project_list_no_projects(self, cli_runner: CliRunner, monkeypatch):
        """Test listing projects when workspace has none."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        ws_config = WorkspaceConfig(
            workspace_id="123",
            name="Test Workspace",
            api_url="http://localhost:8000",
            workspace_identifier="TEST",
        )

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return ws_config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_list_projects = AsyncMock(return_value=[])
        mock_get_prefs = AsyncMock(return_value=None)

        with patch("cli.client.APIClient.from_config") as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.list_projects = mock_list_projects
            mock_client.get_user_preferences = mock_get_prefs
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["project", "list"])

        assert result.exit_code == 0
        assert "No projects found" in result.output

    def test_project_list_with_projects(self, cli_runner: CliRunner, monkeypatch):
        """Test listing projects successfully."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        ws_config = WorkspaceConfig(
            workspace_id="123",
            name="Test Workspace",
            api_url="http://localhost:8000",
            workspace_identifier="TEST",
        )

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return ws_config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        projects = [
            {"id": 1, "name": "Project A", "identifier": "PROJA"},
            {"id": 2, "name": "Project B", "identifier": "PROJB"},
        ]

        mock_list_projects = AsyncMock(return_value=projects)
        mock_get_prefs = AsyncMock(
            return_value={"current_project_id": 1, "current_workspace_id": 123}
        )

        with patch("cli.client.APIClient.from_config") as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.list_projects = mock_list_projects
            mock_client.get_user_preferences = mock_get_prefs
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["project", "list"])

        assert result.exit_code == 0
        assert "Project A" in result.output
        assert "Project B" in result.output
        assert "Total: 2 projects" in result.output


@pytest.mark.cli
class TestProjectUseCommand:
    """Tests for anyt project use command."""

    def test_project_use_not_authenticated(self, cli_runner: CliRunner, monkeypatch):
        """Test using project when not authenticated."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_global_load():
            return config

        def mock_ws_load(self=None):
            return None

        monkeypatch.setattr("cli.config.GlobalConfig.load", mock_global_load)
        monkeypatch.setattr("cli.config.WorkspaceConfig.load", mock_ws_load)

        result = cli_runner.invoke(app, ["project", "use", "PROJ"])

        assert result.exit_code == 1
        assert (
            "Not authenticated" in result.output
            or "Missing authentication credentials" in result.output
            or "No workspace configured" in result.output
        )

    def test_project_use_project_not_found(self, cli_runner: CliRunner, monkeypatch):
        """Test using a project that doesn't exist."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        ws_config = WorkspaceConfig(
            workspace_id="123",
            name="Test Workspace",
            api_url="http://localhost:8000",
            workspace_identifier="TEST",
        )

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return ws_config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        projects = [
            {"id": 1, "name": "Project A", "identifier": "PROJA"},
        ]

        mock_list_projects = AsyncMock(return_value=projects)

        with patch("cli.client.APIClient.from_config") as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.list_projects = mock_list_projects
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["project", "use", "NONEXISTENT"])

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_project_use_success(self, cli_runner: CliRunner, monkeypatch):
        """Test successfully setting current project."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        ws_config = WorkspaceConfig(
            workspace_id="123",
            name="Test Workspace",
            api_url="http://localhost:8000",
            workspace_identifier="TEST",
        )

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return ws_config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        projects = [
            {"id": 1, "name": "Project A", "identifier": "PROJA"},
            {"id": 2, "name": "Project B", "identifier": "PROJB"},
        ]

        mock_list_projects = AsyncMock(return_value=projects)
        mock_set_current = AsyncMock(
            return_value={"current_project_id": 2, "current_workspace_id": 123}
        )

        with patch("cli.client.APIClient.from_config") as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.list_projects = mock_list_projects
            mock_client.set_current_project = mock_set_current
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["project", "use", "PROJB"])

        assert result.exit_code == 0
        assert "Set current project" in result.output
        assert "Project B" in result.output
        mock_set_current.assert_called_once_with(123, 2)


@pytest.mark.cli
class TestProjectCurrentCommand:
    """Tests for anyt project current command."""

    def test_project_current_no_project_set(self, cli_runner: CliRunner, monkeypatch):
        """Test showing current project when none is set."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        ws_config = WorkspaceConfig(
            workspace_id="123",
            name="Test Workspace",
            api_url="http://localhost:8000",
            workspace_identifier="TEST",
        )

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return ws_config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_get_prefs = AsyncMock(return_value=None)

        with patch("cli.client.APIClient.from_config") as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.get_user_preferences = mock_get_prefs
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["project", "current"])

        assert result.exit_code == 0
        assert "No current project set" in result.output

    def test_project_current_with_project_set(
        self, cli_runner: CliRunner, monkeypatch
    ):
        """Test showing current project when one is set."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        ws_config = WorkspaceConfig(
            workspace_id="123",
            name="Test Workspace",
            api_url="http://localhost:8000",
            workspace_identifier="TEST",
        )

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return ws_config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        projects = [
            {"id": 1, "name": "Project A", "identifier": "PROJA"},
        ]

        mock_get_prefs = AsyncMock(
            return_value={"current_project_id": 1, "current_workspace_id": 123}
        )
        mock_list_projects = AsyncMock(return_value=projects)

        with patch("cli.client.APIClient.from_config") as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.get_user_preferences = mock_get_prefs
            mock_client.list_projects = mock_list_projects
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["project", "current"])

        assert result.exit_code == 0
        assert "Current project" in result.output
        assert "Project A" in result.output


@pytest.mark.cli
class TestProjectSwitchCommand:
    """Tests for anyt project switch command."""

    def test_project_switch_no_projects(self, cli_runner: CliRunner, monkeypatch):
        """Test switching project when workspace has no projects."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        ws_config = WorkspaceConfig(
            workspace_id="123",
            name="Test Workspace",
            api_url="http://localhost:8000",
            workspace_identifier="TEST",
        )

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return ws_config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        mock_list_projects = AsyncMock(return_value=[])
        mock_get_prefs = AsyncMock(return_value=None)

        with patch("cli.client.APIClient.from_config") as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.list_projects = mock_list_projects
            mock_client.get_user_preferences = mock_get_prefs
            mock_client_factory.return_value = mock_client

            result = cli_runner.invoke(app, ["project", "switch"])

        assert result.exit_code == 0
        assert "No projects found" in result.output

    def test_project_switch_interactive(self, cli_runner: CliRunner, monkeypatch):
        """Test interactive project switching."""
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="test-token"
            )
        }
        config.current_environment = "dev"

        ws_config = WorkspaceConfig(
            workspace_id="123",
            name="Test Workspace",
            api_url="http://localhost:8000",
            workspace_identifier="TEST",
        )

        def mock_load():
            return config

        def mock_ws_load(path=None):
            return ws_config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
        monkeypatch.setattr(
            "cli.config.WorkspaceConfig.load", staticmethod(mock_ws_load)
        )

        projects = [
            {"id": 1, "name": "Project A", "identifier": "PROJA"},
            {"id": 2, "name": "Project B", "identifier": "PROJB"},
        ]

        mock_list_projects = AsyncMock(return_value=projects)
        mock_get_prefs = AsyncMock(
            return_value={"current_project_id": 1, "current_workspace_id": 123}
        )
        mock_set_current = AsyncMock(
            return_value={"current_project_id": 2, "current_workspace_id": 123}
        )

        with patch("cli.client.APIClient.from_config") as mock_client_factory:
            mock_client = AsyncMock()
            mock_client.list_projects = mock_list_projects
            mock_client.get_user_preferences = mock_get_prefs
            mock_client.set_current_project = mock_set_current
            mock_client_factory.return_value = mock_client

            # Simulate selecting the second project
            result = cli_runner.invoke(app, ["project", "switch"], input="2\n")

        assert result.exit_code == 0
        assert "Switched to project" in result.output or "Project B" in result.output
