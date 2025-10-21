"""Tests for anyt init command with agent_key support."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.config import GlobalConfig, EnvironmentConfig, WorkspaceConfig
from cli.models.workspace import Workspace
from cli.models.project import Project


def create_mock_workspace_and_project(ws_id: int = 1) -> tuple[Workspace, Project]:
    """Helper to create mock workspace and project."""
    mock_workspace = Workspace(
        id=ws_id,
        name="Test Workspace",
        identifier="TEST",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_project = Project(
        id=ws_id,
        workspace_id=ws_id,
        name="Default Project",
        identifier="DEF",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return mock_workspace, mock_project


@pytest.mark.cli
class TestInitCommandAgentKey:
    """Tests for anyt init command agent_key functionality."""

    def test_init_saves_agent_key_from_env_var(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ):
        """Test that init saves agent_key from environment variable to workspace config."""
        # Setup config directory
        config_dir = tmp_path / ".config" / "anyt"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("ANYT_CONFIG_DIR", str(config_dir))

        # Setup workspace directory
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        # Create global config with environment
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(api_url="http://localhost:8000")
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        # Set agent key via environment variable
        agent_key = "anyt_agent_test123"
        monkeypatch.setenv("ANYT_AGENT_KEY", agent_key)

        mock_workspace, mock_project = create_mock_workspace_and_project(1)

        # Track what WorkspaceConfig.save was called with
        saved_config = None

        def capture_save(self, directory=None):
            nonlocal saved_config
            saved_config = self

        with (
            patch("cli.commands.init.WorkspaceService.from_config") as mock_ws_service,
            patch("cli.commands.init.ProjectService.from_config") as mock_proj_service,
            patch("cli.config.WorkspaceConfig.save", capture_save),
        ):
            mock_ws_instance = MagicMock()
            mock_ws_instance.get_or_create_default_workspace = AsyncMock(
                return_value=mock_workspace
            )
            mock_ws_service.return_value = mock_ws_instance

            mock_proj_instance = MagicMock()
            mock_proj_instance.get_current_project = AsyncMock(
                return_value=mock_project
            )
            mock_proj_service.return_value = mock_proj_instance

            # Change to workspace directory
            monkeypatch.chdir(workspace_dir)
            result = cli_runner.invoke(app, ["init"])

        # Verify command succeeded
        assert result.exit_code == 0

        # Verify workspace config was saved with agent_key
        assert saved_config is not None
        assert saved_config.agent_key == agent_key
        assert saved_config.workspace_id == "1"
        assert saved_config.name == "Test Workspace"

    def test_init_saves_agent_key_from_global_config(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ):
        """Test that init saves agent_key from global config to workspace config."""
        # Setup config directory
        config_dir = tmp_path / ".config" / "anyt"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("ANYT_CONFIG_DIR", str(config_dir))

        # Clear environment variables
        monkeypatch.delenv("ANYT_AGENT_KEY", raising=False)
        monkeypatch.delenv("ANYT_AUTH_TOKEN", raising=False)

        # Setup workspace directory
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        # Create global config with agent_key in environment
        agent_key = "anyt_agent_fromconfig456"
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", agent_key=agent_key
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        mock_workspace, mock_project = create_mock_workspace_and_project(2)

        # Track what WorkspaceConfig.save was called with
        saved_config = None

        def capture_save(self, directory=None):
            nonlocal saved_config
            saved_config = self

        with (
            patch("cli.commands.init.WorkspaceService.from_config") as mock_ws_service,
            patch("cli.commands.init.ProjectService.from_config") as mock_proj_service,
            patch("cli.config.WorkspaceConfig.save", capture_save),
        ):
            mock_ws_instance = MagicMock()
            mock_ws_instance.get_or_create_default_workspace = AsyncMock(
                return_value=mock_workspace
            )
            mock_ws_service.return_value = mock_ws_instance

            mock_proj_instance = MagicMock()
            mock_proj_instance.get_current_project = AsyncMock(
                return_value=mock_project
            )
            mock_proj_service.return_value = mock_proj_instance

            # Change to workspace directory
            monkeypatch.chdir(workspace_dir)
            result = cli_runner.invoke(app, ["init"])

        # Verify command succeeded
        assert result.exit_code == 0

        # Verify workspace config was saved with agent_key
        assert saved_config is not None
        assert saved_config.agent_key == agent_key

    def test_init_no_agent_key_backward_compatible(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ):
        """Test that init works without agent_key (backward compatibility)."""
        # Setup config directory
        config_dir = tmp_path / ".config" / "anyt"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("ANYT_CONFIG_DIR", str(config_dir))

        # Clear agent key
        monkeypatch.delenv("ANYT_AGENT_KEY", raising=False)

        # Setup workspace directory
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        # Create global config with auth_token but no agent_key
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", auth_token="user_token_123"
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        mock_workspace, mock_project = create_mock_workspace_and_project(3)

        # Track what WorkspaceConfig.save was called with
        saved_config = None

        def capture_save(self, directory=None):
            nonlocal saved_config
            saved_config = self

        with (
            patch("cli.commands.init.WorkspaceService.from_config") as mock_ws_service,
            patch("cli.commands.init.ProjectService.from_config") as mock_proj_service,
            patch("cli.config.WorkspaceConfig.save", capture_save),
        ):
            mock_ws_instance = MagicMock()
            mock_ws_instance.get_or_create_default_workspace = AsyncMock(
                return_value=mock_workspace
            )
            mock_ws_service.return_value = mock_ws_instance

            mock_proj_instance = MagicMock()
            mock_proj_instance.get_current_project = AsyncMock(
                return_value=mock_project
            )
            mock_proj_service.return_value = mock_proj_instance

            # Change to workspace directory
            monkeypatch.chdir(workspace_dir)
            result = cli_runner.invoke(app, ["init"])

        # Verify command succeeded
        assert result.exit_code == 0

        # Verify workspace config was saved without agent_key
        assert saved_config is not None
        assert saved_config.agent_key is None  # Should be None when not provided

    def test_init_create_new_workspace_with_agent_key(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ):
        """Test creating a new workspace saves agent_key."""
        # Setup config directory
        config_dir = tmp_path / ".config" / "anyt"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("ANYT_CONFIG_DIR", str(config_dir))

        # Clear environment variables to isolate test
        monkeypatch.delenv("ANYT_AGENT_KEY", raising=False)
        monkeypatch.delenv("ANYT_AUTH_TOKEN", raising=False)

        # Setup workspace directory
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()

        # Create global config with agent_key
        agent_key = "anyt_agent_create789"
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", agent_key=agent_key
            )
        }
        config.current_environment = "dev"

        def mock_load():
            return config

        monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))

        # Mock workspace service
        mock_workspace = Workspace(
            id=4,
            name="New Workspace",
            identifier="NEW",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        mock_project = Project(
            id=4,
            workspace_id=4,
            name="Default Project",
            identifier="DEF",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Track what WorkspaceConfig.save was called with
        saved_config = None

        def capture_save(self, directory=None):
            nonlocal saved_config
            saved_config = self

        with (
            patch("cli.commands.init.WorkspaceService.from_config") as mock_ws_service,
            patch("cli.commands.init.ProjectService.from_config") as mock_proj_service,
            patch("cli.config.WorkspaceConfig.save", capture_save),
        ):
            mock_ws_instance = MagicMock()
            mock_ws_instance.create_workspace = AsyncMock(return_value=mock_workspace)
            mock_ws_service.return_value = mock_ws_instance

            mock_proj_instance = MagicMock()
            mock_proj_instance.get_current_project = AsyncMock(
                return_value=mock_project
            )
            mock_proj_service.return_value = mock_proj_instance

            # Change to workspace directory
            monkeypatch.chdir(workspace_dir)
            result = cli_runner.invoke(
                app,
                ["init", "--create", "New Workspace", "--identifier", "NEW"],
            )

        # Verify command succeeded
        assert result.exit_code == 0

        # Verify workspace config was saved with agent_key
        assert saved_config is not None
        assert saved_config.agent_key == agent_key
        assert saved_config.workspace_id == "4"
        assert saved_config.name == "New Workspace"

    def test_workspace_config_model_agent_key_field(self):
        """Test that WorkspaceConfig model supports agent_key field."""
        # Test with agent_key
        config_with_key = WorkspaceConfig(
            workspace_id="123",
            name="Test",
            api_url="http://localhost:8000",
            agent_key="test_key_abc",
        )
        assert config_with_key.agent_key == "test_key_abc"

        # Test without agent_key (backward compatibility)
        config_without_key = WorkspaceConfig(
            workspace_id="123",
            name="Test",
            api_url="http://localhost:8000",
        )
        assert config_without_key.agent_key is None

        # Test serialization
        config_dict = config_with_key.model_dump()
        assert config_dict["agent_key"] == "test_key_abc"

        # Test deserialization
        loaded_config = WorkspaceConfig(**config_dict)
        assert loaded_config.agent_key == "test_key_abc"


@pytest.mark.cli
class TestWorkspaceConfigAgentKeyPriority:
    """Tests for agent_key resolution priority (env var > workspace config > global config)."""

    def test_effective_config_prioritizes_env_var(self, tmp_path: Path, monkeypatch):
        """Test that environment variable takes precedence over workspace config."""
        # Setup config directory
        config_dir = tmp_path / ".config" / "anyt"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("ANYT_CONFIG_DIR", str(config_dir))

        # Setup workspace directory
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        anyt_dir = workspace_dir / ".anyt"
        anyt_dir.mkdir()

        # Create workspace config with agent_key
        ws_config = WorkspaceConfig(
            workspace_id="1",
            name="Test",
            api_url="http://localhost:8000",
            agent_key="workspace_key",
        )
        ws_config.save(workspace_dir)

        # Create global config
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", agent_key="global_key"
            )
        }
        config.current_environment = "dev"

        # Set environment variable (should have highest priority)
        monkeypatch.setenv("ANYT_AGENT_KEY", "env_key")

        # Change to workspace directory
        monkeypatch.chdir(workspace_dir)

        # Get effective config
        effective = config.get_effective_config()

        # Environment variable should take precedence
        assert effective["agent_key"] == "env_key"

    def test_effective_config_uses_workspace_config_when_no_env_var(
        self, tmp_path: Path, monkeypatch
    ):
        """Test that workspace config is used when env var is not set."""
        # Setup config directory
        config_dir = tmp_path / ".config" / "anyt"
        config_dir.mkdir(parents=True)
        monkeypatch.setenv("ANYT_CONFIG_DIR", str(config_dir))

        # Undo the autouse fixture that mocks WorkspaceConfig.load() to return None
        # We need the real implementation for this test
        # IMPORTANT: Must undo before delenv to avoid clearing the undo
        monkeypatch.undo()

        # Clear env vars AFTER undo to ensure they're actually cleared
        monkeypatch.delenv("ANYT_AGENT_KEY", raising=False)
        monkeypatch.delenv("ANYT_ENV", raising=False)
        monkeypatch.delenv("ANYT_AUTH_TOKEN", raising=False)

        # Setup workspace directory
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        anyt_dir = workspace_dir / ".anyt"
        anyt_dir.mkdir()

        # Create workspace config with agent_key
        ws_config = WorkspaceConfig(
            workspace_id="1",
            name="Test",
            api_url="http://localhost:8000",
            agent_key="workspace_key",
        )
        ws_config.save(workspace_dir)

        # Create global config with different agent_key
        config = GlobalConfig()
        config.environments = {
            "dev": EnvironmentConfig(
                api_url="http://localhost:8000", agent_key="global_key"
            )
        }
        config.current_environment = "dev"

        # Change current working directory to workspace directory
        # This is needed so WorkspaceConfig.load() can find the config file
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(workspace_dir)

            # Get effective config
            effective = config.get_effective_config()

            # Workspace config should take precedence over global config
            assert effective["agent_key"] == "workspace_key"
        finally:
            os.chdir(original_cwd)
