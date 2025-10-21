"""Tests for ViewsAPIClient."""

from unittest.mock import AsyncMock, patch

import pytest

from cli.client.views import ViewsAPIClient
from cli.models.view import TaskView, TaskViewCreate, TaskViewUpdate


@pytest.fixture
def client():
    """Create a ViewsAPIClient instance for testing."""
    return ViewsAPIClient(
        base_url="http://test.example.com",
        auth_token="test_token",
    )


@pytest.fixture
def sample_view_data():
    """Sample task view data for testing."""
    return {
        "id": 1,
        "name": "My Active Tasks",
        "workspace_id": 1,
        "user_id": "user123",
        "filters": {"status": ["todo", "in_progress"]},
        "is_default": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


class TestListTaskViews:
    """Test list_task_views method."""

    @pytest.mark.asyncio
    async def test_list_task_views_success(self, client, sample_view_data):
        """Test successful task view listing."""
        mock_response = {"data": [sample_view_data]}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.list_task_views(workspace_id=1)

            mock_get.assert_called_once_with("/v1/workspaces/1/views")
            assert len(result) == 1
            assert isinstance(result[0], TaskView)
            assert result[0].name == "My Active Tasks"

    @pytest.mark.asyncio
    async def test_list_task_views_empty(self, client):
        """Test listing task views with empty result."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}

            result = await client.list_task_views(workspace_id=1)

            assert result == []


class TestCreateTaskView:
    """Test create_task_view method."""

    @pytest.mark.asyncio
    async def test_create_task_view_success(self, client, sample_view_data):
        """Test successful task view creation."""
        view_create = TaskViewCreate(
            name="My Active Tasks",
            filters={"status": ["todo", "in_progress"]},
            is_default=False,
        )

        mock_response = {"data": sample_view_data}

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.create_task_view(workspace_id=1, view=view_create)

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "/v1/workspaces/1/views"
            assert isinstance(result, TaskView)
            assert result.id == 1


class TestGetTaskView:
    """Test get_task_view method."""

    @pytest.mark.asyncio
    async def test_get_task_view_success(self, client, sample_view_data):
        """Test successful task view retrieval."""
        mock_response = {"data": sample_view_data}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_task_view(workspace_id=1, view_id=1)

            mock_get.assert_called_once_with("/v1/workspaces/1/views/1")
            assert isinstance(result, TaskView)
            assert result.id == 1


class TestGetTaskViewByName:
    """Test get_task_view_by_name method."""

    @pytest.mark.asyncio
    async def test_get_task_view_by_name_found(self, client, sample_view_data):
        """Test successful task view retrieval by name."""
        mock_response = {"data": [sample_view_data]}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_task_view_by_name(
                workspace_id=1, name="My Active Tasks"
            )

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/v1/workspaces/1/views"
            assert call_args[1]["params"]["name"] == "My Active Tasks"
            assert isinstance(result, TaskView)
            assert result.name == "My Active Tasks"

    @pytest.mark.asyncio
    async def test_get_task_view_by_name_not_found(self, client):
        """Test task view not found by name."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}

            result = await client.get_task_view_by_name(
                workspace_id=1, name="Nonexistent"
            )

            assert result is None


class TestGetDefaultTaskView:
    """Test get_default_task_view method."""

    @pytest.mark.asyncio
    async def test_get_default_task_view_found(self, client, sample_view_data):
        """Test successful default task view retrieval."""
        default_view = {**sample_view_data, "is_default": True}
        mock_response = {"data": default_view}

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_default_task_view(workspace_id=1)

            mock_get.assert_called_once_with("/v1/workspaces/1/views/default")
            assert isinstance(result, TaskView)
            assert result.is_default is True

    @pytest.mark.asyncio
    async def test_get_default_task_view_not_found(self, client):
        """Test default task view not found."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Not found")

            result = await client.get_default_task_view(workspace_id=1)

            assert result is None


class TestUpdateTaskView:
    """Test update_task_view method."""

    @pytest.mark.asyncio
    async def test_update_task_view_success(self, client, sample_view_data):
        """Test successful task view update."""
        view_update = TaskViewUpdate(
            name="Updated View Name",
            filters={"status": ["in_progress"]},
        )

        updated_data = {**sample_view_data, "name": "Updated View Name"}
        mock_response = {"data": updated_data}

        with patch.object(client, "patch", new_callable=AsyncMock) as mock_patch:
            mock_patch.return_value = mock_response

            result = await client.update_task_view(
                workspace_id=1, view_id=1, updates=view_update
            )

            mock_patch.assert_called_once()
            call_args = mock_patch.call_args
            assert call_args[0][0] == "/v1/workspaces/1/views/1"
            assert isinstance(result, TaskView)
            assert result.name == "Updated View Name"


class TestDeleteTaskView:
    """Test delete_task_view method."""

    @pytest.mark.asyncio
    async def test_delete_task_view_success(self, client):
        """Test successful task view deletion."""
        with patch.object(client, "delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {}

            await client.delete_task_view(workspace_id=1, view_id=1)

            mock_delete.assert_called_once_with("/v1/workspaces/1/views/1")
