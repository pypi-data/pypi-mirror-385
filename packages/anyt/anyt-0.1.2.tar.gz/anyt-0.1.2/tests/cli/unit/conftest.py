"""Fixtures and utilities for CLI unit tests."""

from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock

import httpx
import pytest
from typer.testing import CliRunner

from cli.config import (
    ActiveTaskConfig,
    GlobalConfig,
    WorkspaceConfig,
    EnvironmentConfig,
)
from cli.models.task import Task
from cli.models.project import Project
from cli.models.common import Status, Priority
from datetime import datetime


# ============================================================================
# CLI Runner Fixtures
# ============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Typer CLI test runner."""
    return CliRunner()


# ============================================================================
# Temporary Configuration Fixtures
# ============================================================================


@pytest.fixture
def temp_config_dir(tmp_path: Path, monkeypatch) -> Generator[Path, None, None]:
    """Create temporary CLI config directory (~/.config/anyt/).

    Clears auth-related environment variables to prevent leakage between tests.
    """
    config_dir = tmp_path / ".config" / "anyt"
    config_dir.mkdir(parents=True)

    # Clear auth-related environment variables
    monkeypatch.delenv("ANYT_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANYT_AGENT_KEY", raising=False)
    monkeypatch.delenv("ANYT_ENV", raising=False)
    monkeypatch.setenv("ANYT_CONFIG_DIR", str(config_dir))

    yield config_dir


@pytest.fixture
def temp_workspace_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create temporary workspace directory for anyt.json."""
    # anyt.json is in .anyt/ directory along with active_task.json
    anyt_dir = tmp_path / ".anyt"
    anyt_dir.mkdir()
    yield tmp_path


@pytest.fixture
def mock_config_dirs(
    tmp_path: Path, monkeypatch
) -> Generator[dict[str, Any], None, None]:
    """Mock config directories and return paths."""
    config_dir = tmp_path / ".config" / "anyt"
    workspace_dir = tmp_path / ".anyt"
    config_dir.mkdir(parents=True)
    workspace_dir.mkdir()

    # Mock config loading to use temp directories
    def mock_config_path() -> Path:
        return config_dir / "config.json"

    def mock_workspace_path() -> Path:
        # anyt.json is now in .anyt/ directory
        return tmp_path / ".anyt" / "anyt.json"

    def mock_active_task_path() -> Path:
        return workspace_dir / "active_task.json"

    monkeypatch.setattr(
        "cli.config.GlobalConfig.config_file", property(lambda self: mock_config_path())
    )
    monkeypatch.setattr(
        "cli.config.WorkspaceConfig.config_file",
        property(lambda self: mock_workspace_path()),
    )
    monkeypatch.setattr(
        "cli.config.ActiveTaskConfig.config_file",
        property(lambda self: mock_active_task_path()),
    )

    yield {
        "config_dir": config_dir,
        "workspace_dir": workspace_dir,
    }


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def global_config(temp_config_dir: Path) -> GlobalConfig:
    """Create a GlobalConfig instance with default test environment."""
    config = GlobalConfig()
    config.environments = {
        "dev": EnvironmentConfig(
            api_url="http://localhost:8000",
            auth_token=None,
            default_workspace=None,
        )
    }
    config.current_environment = "dev"
    return config


@pytest.fixture
def global_config_with_token(global_config: GlobalConfig) -> GlobalConfig:
    """GlobalConfig with test user token."""
    global_config.environments["dev"].auth_token = "test-user-token-12345"
    return global_config


@pytest.fixture
def global_config_with_agent_key(global_config: GlobalConfig) -> GlobalConfig:
    """GlobalConfig with test agent key."""
    global_config.environments[
        "dev"
    ].auth_token = "anyt_agent_abcdef123456789012345678901234"
    return global_config


@pytest.fixture
def workspace_config(temp_workspace_dir: Path) -> WorkspaceConfig:
    """Create a WorkspaceConfig instance."""
    config = WorkspaceConfig(
        workspace_id="1",
        name="Test Workspace",
        api_url="http://localhost:8000",
        last_sync=None,
    )
    return config


@pytest.fixture
def active_task_config(temp_workspace_dir: Path) -> ActiveTaskConfig:
    """Create an ActiveTaskConfig instance."""
    config = ActiveTaskConfig(
        identifier="DEV-42",
        title="Test Task",
        picked_at="2025-10-16T12:00:00Z",
        workspace_id=1,
        project_id=1,
    )
    return config


# ============================================================================
# Mock API Client Fixtures
# ============================================================================


@pytest.fixture
def mock_httpx_client() -> MagicMock:
    """Mock httpx.AsyncClient for API calls."""
    return MagicMock(spec=httpx.AsyncClient)


# ============================================================================
# Mocked Response Fixtures
# ============================================================================


@pytest.fixture
def mock_task_response() -> dict[str, Any]:
    """Mock task response from API."""
    return {
        "success": True,
        "data": {
            "id": 1,
            "identifier": "DEV-1",
            "title": "Test Task",
            "description": "A test task",
            "status": "todo",
            "priority": 1,
            "created_at": "2025-10-16T10:00:00Z",
            "updated_at": "2025-10-16T10:00:00Z",
            "project": {"id": 1, "name": "Test Project"},
        },
        "request_id": "req-123",
    }


@pytest.fixture
def mock_workspace_response() -> dict[str, Any]:
    """Mock workspace response from API."""
    return {
        "success": True,
        "data": {
            "id": 1,
            "identifier": "DEV",
            "name": "Development",
            "description": "Development workspace",
            "created_at": "2025-10-01T00:00:00Z",
        },
        "request_id": "req-123",
    }


@pytest.fixture
def mock_tasks_list_response() -> dict[str, Any]:
    """Mock tasks list response from API."""
    return {
        "success": True,
        "data": {
            "items": [
                {
                    "id": 1,
                    "identifier": "DEV-1",
                    "title": "First Task",
                    "status": "todo",
                    "priority": 1,
                },
                {
                    "id": 2,
                    "identifier": "DEV-2",
                    "title": "Second Task",
                    "status": "inprogress",
                    "priority": 2,
                },
            ],
            "pagination": {"total": 2, "limit": 50, "offset": 0},
        },
        "request_id": "req-123",
    }


@pytest.fixture
def mock_error_response() -> dict[str, Any]:
    """Mock error response from API."""
    return {
        "error": "NotFoundError",
        "message": "Task DEV-999 not found",
        "code": "TASK_NOT_FOUND",
        "request_id": "req-123",
        "timestamp": "2025-10-16T12:00:00Z",
    }


# ============================================================================
# Patched Fixtures
# ============================================================================


@pytest.fixture
def patch_global_config(monkeypatch, global_config: GlobalConfig):
    """Patch GlobalConfig.load() to return test config."""

    def mock_load():
        return global_config

    monkeypatch.setattr("cli.config.GlobalConfig.load", staticmethod(mock_load))
    return global_config


@pytest.fixture
def patch_console(monkeypatch):
    """Patch rich Console to capture output."""
    mock_console = MagicMock()
    monkeypatch.setattr("cli.main.console", mock_console)
    return mock_console


@pytest.fixture
def patch_workspace_config(monkeypatch):
    """Patch WorkspaceConfig.load() to return None to prevent loading real workspace config."""

    def mock_load(directory=None):
        return None

    monkeypatch.setattr("cli.config.WorkspaceConfig.load", staticmethod(mock_load))
    return None


@pytest.fixture(autouse=True)
def auto_patch_workspace_config(monkeypatch):
    """Automatically patch WorkspaceConfig.load() for all tests to prevent loading real workspace config.

    This is an autouse fixture that runs for every test, preventing the real workspace config
    from interfering with test isolation.
    """

    def mock_load(directory=None):
        return None

    monkeypatch.setattr("cli.config.WorkspaceConfig.load", staticmethod(mock_load))


# ============================================================================
# Helper Fixtures
# ============================================================================


@pytest.fixture
def sample_tasks() -> list[Task]:
    """Sample task data for testing."""
    return [
        create_test_task(
            id=1,
            identifier="DEV-1",
            title="Setup project",
            description="Initial project setup",
            status=Status.DONE,
            priority=Priority.HIGH,
            created_at="2025-10-01T10:00:00Z",
            updated_at="2025-10-01T15:00:00Z",
        ),
        create_test_task(
            id=2,
            identifier="DEV-2",
            title="Design architecture",
            description="Design system architecture",
            status=Status.DONE,
            priority=Priority.HIGH,
            created_at="2025-10-02T10:00:00Z",
            updated_at="2025-10-05T12:00:00Z",
        ),
        create_test_task(
            id=3,
            identifier="DEV-3",
            title="Implement API",
            description="Implement REST API endpoints",
            status=Status.IN_PROGRESS,
            priority=Priority.NORMAL,
            created_at="2025-10-06T10:00:00Z",
            updated_at="2025-10-16T10:00:00Z",
        ),
        create_test_task(
            id=4,
            identifier="DEV-4",
            title="Write tests",
            description="Write unit and integration tests",
            status=Status.BACKLOG,
            priority=Priority.NORMAL,
            created_at="2025-10-10T10:00:00Z",
            updated_at="2025-10-10T10:00:00Z",
        ),
        create_test_task(
            id=5,
            identifier="DEV-5",
            title="Deploy to production",
            description="Deploy to production environment",
            status=Status.BACKLOG,
            priority=Priority.LOW,
            created_at="2025-10-15T10:00:00Z",
            updated_at="2025-10-15T10:00:00Z",
        ),
    ]


@pytest.fixture
def sample_workspaces() -> list[dict[str, Any]]:
    """Sample workspace data for testing."""
    return [
        {
            "id": 1,
            "identifier": "DEV",
            "name": "Development",
            "description": "Development workspace",
        },
        {
            "id": 2,
            "identifier": "PROD",
            "name": "Production",
            "description": "Production workspace",
        },
    ]


@pytest.fixture
def sample_environments() -> dict[str, Any]:
    """Sample environment configuration."""
    return {
        "dev": {
            "api_url": "http://localhost:8000",
            "auth_token": "test-token-dev",
            "default_workspace": None,
        },
        "staging": {
            "api_url": "https://staging-api.example.com",
            "auth_token": "test-token-staging",
            "default_workspace": None,
        },
        "prod": {
            "api_url": "https://api.example.com",
            "auth_token": "test-token-prod",
            "default_workspace": 2,
        },
    }


# ============================================================================
# Pydantic Model Test Helpers
# ============================================================================


def create_test_task(
    id: int = 1,
    identifier: str = "DEV-1",
    title: str = "Test Task",
    description: str | None = "Test description",
    status: Status = Status.TODO,
    priority: Priority = Priority.NORMAL,
    project_id: int = 1,
    workspace_id: int = 1,
    labels: list[str] | None = None,
    **kwargs: Any,
) -> Task:
    """Create a test Task instance with sensible defaults.

    Args:
        id: Task ID
        identifier: Task identifier (e.g., DEV-1)
        title: Task title
        description: Task description
        status: Task status
        priority: Task priority
        project_id: Project ID
        workspace_id: Workspace ID
        labels: Task labels
        **kwargs: Additional fields to override

    Returns:
        Task instance
    """
    defaults = {
        "id": id,
        "public_id": 100000000 + id,  # Generate a 9-digit public ID
        "identifier": identifier,
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "project_id": project_id,
        "workspace_id": workspace_id,
        "labels": labels or [],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "version": 1,
    }
    defaults.update(kwargs)
    return Task(**defaults)  # type: ignore[arg-type]


def create_test_project(
    id: int = 1,
    name: str = "Test Project",
    identifier: str = "TEST",
    workspace_id: int = 1,
    **kwargs: Any,
) -> Project:
    """Create a test Project instance with sensible defaults.

    Args:
        id: Project ID
        name: Project name
        identifier: Project identifier
        workspace_id: Workspace ID
        **kwargs: Additional fields to override

    Returns:
        Project instance
    """
    defaults = {
        "id": id,
        "name": name,
        "identifier": identifier,
        "workspace_id": workspace_id,
        "description": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "version": 1,
    }
    defaults.update(kwargs)
    return Project(**defaults)  # type: ignore[arg-type]


def create_test_workspace(
    id: int = 1,
    name: str = "Test Workspace",
    identifier: str = "TEST",
    description: str | None = None,
    **kwargs: Any,
):
    """Create a test Workspace instance with sensible defaults.

    Args:
        id: Workspace ID
        name: Workspace name
        identifier: Workspace identifier
        description: Workspace description
        **kwargs: Additional fields to override

    Returns:
        Workspace instance
    """
    from cli.models.workspace import Workspace

    defaults = {
        "id": id,
        "name": name,
        "identifier": identifier,
        "description": description,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    defaults.update(kwargs)
    return Workspace(**defaults)  # type: ignore[arg-type]


def create_test_user_preferences(
    user_id: str = "test-user-123",
    current_workspace_id: int | None = None,
    current_project_id: int | None = None,
    **kwargs: Any,
):
    """Create a test UserPreferences instance with sensible defaults.

    Args:
        user_id: User ID
        current_workspace_id: Current workspace ID
        current_project_id: Current project ID
        **kwargs: Additional fields to override

    Returns:
        UserPreferences instance
    """
    from cli.models.user import UserPreferences

    defaults = {
        "user_id": user_id,
        "current_workspace_id": current_workspace_id,
        "current_project_id": current_project_id,
        "updated_at": datetime.now(),
    }
    defaults.update(kwargs)
    return UserPreferences(**defaults)  # type: ignore[arg-type]


# ============================================================================
# Marker Registration
# ============================================================================


def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "cli: CLI command tests")
    config.addinivalue_line("markers", "config: Configuration tests")
    config.addinivalue_line("markers", "client: API client tests")
    config.addinivalue_line("markers", "unit: Unit tests")
