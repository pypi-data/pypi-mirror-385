"""Unit tests for WorkspaceService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cli.client.exceptions import NotFoundError
from cli.client.workspaces import WorkspacesAPIClient
from cli.config import EnvironmentConfig, GlobalConfig
from cli.models.workspace import Workspace, WorkspaceCreate
from cli.services.workspace_service import WorkspaceService


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    return GlobalConfig(
        current_environment="test",
        environments={
            "test": EnvironmentConfig(
                api_url="http://localhost:8000",
                auth_token="test-token",
            )
        },
    )


@pytest.fixture
def workspace_service(mock_config):
    """Create WorkspaceService with mocked client."""
    with patch.object(WorkspacesAPIClient, "from_config") as mock_from_config:
        mock_client = MagicMock(spec=WorkspacesAPIClient)
        mock_from_config.return_value = mock_client

        service = WorkspaceService(mock_config)
        service.workspaces = mock_client  # Ensure it's set

        yield service


@pytest.fixture
def sample_workspace():
    """Create a sample workspace for testing."""
    return Workspace(
        id=1,
        name="Test Workspace",
        identifier="TEST",
        description="A test workspace",
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00",
    )


@pytest.mark.asyncio
async def test_list_workspaces(workspace_service, sample_workspace):
    """Test list_workspaces passes through to client."""
    # Setup
    expected_workspaces = [sample_workspace]
    workspace_service.workspaces.list_workspaces = AsyncMock(
        return_value=expected_workspaces
    )

    # Execute
    result = await workspace_service.list_workspaces()

    # Verify
    assert result == expected_workspaces
    workspace_service.workspaces.list_workspaces.assert_called_once()


@pytest.mark.asyncio
async def test_get_workspace(workspace_service, sample_workspace):
    """Test get_workspace passes through to client."""
    # Setup
    workspace_service.workspaces.get_workspace = AsyncMock(
        return_value=sample_workspace
    )

    # Execute
    result = await workspace_service.get_workspace(1)

    # Verify
    assert result == sample_workspace
    workspace_service.workspaces.get_workspace.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_get_or_create_default_workspace_exists(
    workspace_service, sample_workspace
):
    """Test get_or_create_default_workspace when workspace exists."""
    # Setup
    workspace_service.workspaces.get_current_workspace = AsyncMock(
        return_value=sample_workspace
    )

    # Execute
    result = await workspace_service.get_or_create_default_workspace()

    # Verify
    assert result == sample_workspace
    workspace_service.workspaces.get_current_workspace.assert_called_once()
    workspace_service.workspaces.create_workspace.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_default_workspace_creates(
    workspace_service, sample_workspace
):
    """Test get_or_create_default_workspace creates when none exists."""
    # Setup
    workspace_service.workspaces.get_current_workspace = AsyncMock(
        side_effect=NotFoundError("No workspace found")
    )
    workspace_service.workspaces.create_workspace = AsyncMock(
        return_value=sample_workspace
    )

    # Execute
    result = await workspace_service.get_or_create_default_workspace()

    # Verify
    assert result == sample_workspace
    workspace_service.workspaces.get_current_workspace.assert_called_once()
    workspace_service.workspaces.create_workspace.assert_called_once()

    # Verify the created workspace has correct defaults
    call_args = workspace_service.workspaces.create_workspace.call_args
    created_workspace = call_args[0][0]
    assert created_workspace.name == "Personal"
    assert created_workspace.identifier == "PER"


@pytest.mark.asyncio
async def test_create_workspace_success(workspace_service, sample_workspace):
    """Test create_workspace with valid data."""
    # Setup
    workspace_create = WorkspaceCreate(
        name="New Workspace", identifier="NEW", description="Description"
    )
    workspace_service.workspaces.create_workspace = AsyncMock(
        return_value=sample_workspace
    )

    # Execute
    result = await workspace_service.create_workspace(workspace_create)

    # Verify
    assert result == sample_workspace
    workspace_service.workspaces.create_workspace.assert_called_once_with(
        workspace_create
    )


@pytest.mark.asyncio
async def test_create_workspace_identifier_too_short(workspace_service):
    """Test create_workspace rejects identifier < 3 chars."""
    # Setup
    workspace_create = WorkspaceCreate(
        name="Test",
        identifier="AB",  # Only 2 chars
    )

    # Execute & Verify
    with pytest.raises(
        ValueError, match="Workspace identifier must be at least 3 characters"
    ):
        await workspace_service.create_workspace(workspace_create)


@pytest.mark.asyncio
async def test_create_workspace_empty_name(workspace_service):
    """Test create_workspace rejects empty name."""
    # Setup
    workspace_create = WorkspaceCreate(
        name="   ",  # Empty after strip
        identifier="TEST",
    )

    # Execute & Verify
    with pytest.raises(ValueError, match="Workspace name cannot be empty"):
        await workspace_service.create_workspace(workspace_create)


@pytest.mark.asyncio
async def test_switch_workspace_success(
    workspace_service, sample_workspace, mock_config
):
    """Test switch_workspace updates config."""
    # Setup
    workspace_service.workspaces.get_workspace = AsyncMock(
        return_value=sample_workspace
    )

    # Execute
    result = await workspace_service.switch_workspace(1)

    # Verify
    assert result == sample_workspace
    assert mock_config.get_current_env().default_workspace == "1"


@pytest.mark.asyncio
async def test_resolve_workspace_context_explicit_id(
    workspace_service, sample_workspace
):
    """Test resolve_workspace_context with explicit workspace_id."""
    # Setup
    workspace_service.workspaces.get_workspace = AsyncMock(
        return_value=sample_workspace
    )

    # Execute
    result = await workspace_service.resolve_workspace_context(workspace_id=1)

    # Verify
    assert result == sample_workspace
    workspace_service.workspaces.get_workspace.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_resolve_workspace_context_from_config(
    workspace_service, sample_workspace, mock_config
):
    """Test resolve_workspace_context uses config default."""
    # Setup
    mock_config.get_current_env().default_workspace = "1"
    workspace_service.workspaces.get_workspace = AsyncMock(
        return_value=sample_workspace
    )

    # Execute
    result = await workspace_service.resolve_workspace_context()

    # Verify
    assert result == sample_workspace
    workspace_service.workspaces.get_workspace.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_resolve_workspace_context_fallback_to_default(
    workspace_service, sample_workspace
):
    """Test resolve_workspace_context falls back to default when config not set."""
    # Setup - no default_workspace in config
    workspace_service.workspaces.get_current_workspace = AsyncMock(
        return_value=sample_workspace
    )

    # Execute
    result = await workspace_service.resolve_workspace_context()

    # Verify
    assert result == sample_workspace
    workspace_service.workspaces.get_current_workspace.assert_called_once()


@pytest.mark.asyncio
async def test_get_workspace_summary(workspace_service, sample_workspace):
    """Test get_workspace_summary returns workspace with stats."""
    # Setup
    workspace_service.workspaces.get_current_workspace = AsyncMock(
        return_value=sample_workspace
    )

    # Execute
    result = await workspace_service.get_workspace_summary()

    # Verify
    assert result["workspace"] == sample_workspace
    assert "stats" in result
    assert result["stats"]["tasks_total"] == 0  # Placeholder stats
