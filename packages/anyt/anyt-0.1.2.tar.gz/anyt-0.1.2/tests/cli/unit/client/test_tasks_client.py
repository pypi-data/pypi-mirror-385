"""Tests for TasksAPIClient."""

import pytest
from unittest.mock import AsyncMock, patch

from cli.client.tasks import TasksAPIClient
from cli.models.common import Priority, Status
from cli.models.task import Task, TaskCreate, TaskFilters, TaskUpdate


@pytest.fixture
def client():
    """Create a TasksAPIClient instance for testing."""
    return TasksAPIClient(
        base_url="http://test.example.com",
        auth_token="test_token",
    )


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "id": 1,
        "public_id": 123456789,
        "identifier": "DEV-42",
        "title": "Test task",
        "description": "Test description",
        "status": "in_progress",  # Status is string enum
        "priority": 2,  # Priority is int enum (HIGHEST)
        "phase": None,
        "owner_id": None,
        "project_id": 1,
        "workspace_id": 1,
        "labels": ["bug", "urgent"],
        "estimate": 5,
        "parent_id": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "version": 1,
    }


class TestListTasks:
    """Test list_tasks method."""

    @pytest.mark.asyncio
    async def test_list_tasks_success(self, client, sample_task_data):
        """Test successful task listing."""
        filters = TaskFilters(workspace_id=1, status=[Status.IN_PROGRESS])

        mock_response = {
            "data": {
                "items": [sample_task_data],
                "pagination": {
                    "total": 1,
                    "limit": 50,
                    "offset": 0,
                    "has_more": False,
                },
            }
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.list_tasks(filters)

            mock_get.assert_called_once()
            assert len(result.items) == 1
            assert isinstance(result.items[0], Task)
            assert result.items[0].identifier == "DEV-42"
            assert result.total == 1
            assert result.limit == 50
            assert result.offset == 0

    @pytest.mark.asyncio
    async def test_list_tasks_filters_params(self, client):
        """Test that filters are properly converted to params."""
        filters = TaskFilters(
            workspace_id=1,
            project_id=2,
            status=[Status.BACKLOG, Status.TODO],
            priority_gte=2,
            limit=25,
        )

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "data": {
                    "items": [],
                    "pagination": {
                        "total": 0,
                        "limit": 25,
                        "offset": 0,
                        "has_more": False,
                    },
                }
            }

            await client.list_tasks(filters)

            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["workspace_id"] == 1
            assert params["project_id"] == 2
            assert params["limit"] == 25


class TestGetTask:
    """Test get_task method."""

    @pytest.mark.asyncio
    async def test_get_task_by_identifier(self, client, sample_task_data):
        """Test getting task by identifier."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": sample_task_data}

            result = await client.get_task("DEV-42")

            mock_get.assert_called_once_with("/v1/tasks/DEV-42")
            assert isinstance(result, Task)
            assert result.identifier == "DEV-42"
            assert result.title == "Test task"

    @pytest.mark.asyncio
    async def test_get_task_by_workspace(self, client, sample_task_data):
        """Test getting task by workspace and identifier."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": sample_task_data}

            result = await client.get_task_by_workspace(1, "DEV-42")

            mock_get.assert_called_once_with("/v1/workspaces/1/tasks/DEV-42")
            assert isinstance(result, Task)
            assert result.identifier == "DEV-42"

    @pytest.mark.asyncio
    async def test_get_task_by_public_id(self, client, sample_task_data):
        """Test getting task by 9-digit public ID."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": sample_task_data}

            result = await client.get_task_by_public_id(123456789)

            mock_get.assert_called_once_with("/v1/t/123456789")
            assert isinstance(result, Task)
            assert result.public_id == 123456789
            assert result.identifier == "DEV-42"


class TestCreateTask:
    """Test create_task method."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, client, sample_task_data):
        """Test successful task creation."""
        task_create = TaskCreate(
            title="New task",
            description="New description",
            status=Status.TODO,
            priority=Priority.HIGH,
        )

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"data": sample_task_data}

            result = await client.create_task(1, task_create)

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "/v1/projects/1/tasks"
            assert call_args[1]["json"]["title"] == "New task"
            assert isinstance(result, Task)


class TestUpdateTask:
    """Test update_task method."""

    @pytest.mark.asyncio
    async def test_update_task_success(self, client, sample_task_data):
        """Test successful task update."""
        task_update = TaskUpdate(
            title="Updated title",
            status=Status.DONE,
        )

        updated_data = sample_task_data.copy()
        updated_data["title"] = "Updated title"
        updated_data["status"] = "done"  # Status is string enum

        with patch.object(client, "patch", new_callable=AsyncMock) as mock_patch:
            mock_patch.return_value = {"data": updated_data}

            result = await client.update_task("DEV-42", task_update)

            mock_patch.assert_called_once()
            call_args = mock_patch.call_args
            assert call_args[0][0] == "/v1/tasks/DEV-42"
            assert isinstance(result, Task)
            assert result.title == "Updated title"


class TestDeleteTask:
    """Test delete_task method."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self, client):
        """Test successful task deletion."""
        with patch.object(client, "delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {}

            result = await client.delete_task("DEV-42")

            mock_delete.assert_called_once_with("/v1/tasks/DEV-42")
            assert result is None


class TestTaskDependencies:
    """Test task dependency methods."""

    @pytest.mark.asyncio
    async def test_add_dependency(self, client):
        """Test adding a task dependency."""
        dependency_data = {
            "task_id": 1,
            "depends_on_id": 2,
            "created_at": "2024-01-01T00:00:00Z",
        }

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"data": dependency_data}

            await client.add_task_dependency("DEV-42", "DEV-41")

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "/v1/tasks/DEV-42/dependencies"
            assert call_args[1]["json"]["depends_on"] == "DEV-41"

    @pytest.mark.asyncio
    async def test_remove_dependency(self, client):
        """Test removing a task dependency."""
        with patch.object(client, "delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = {}

            await client.remove_task_dependency("DEV-42", "DEV-41")

            mock_delete.assert_called_once_with("/v1/tasks/DEV-42/dependencies/DEV-41")

    @pytest.mark.asyncio
    async def test_get_task_dependencies(self, client, sample_task_data):
        """Test getting task dependencies."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": [sample_task_data]}

            result = await client.get_task_dependencies("DEV-42")

            mock_get.assert_called_once_with("/v1/tasks/DEV-42/dependencies")
            assert len(result) == 1
            assert isinstance(result[0], Task)

    @pytest.mark.asyncio
    async def test_get_task_dependents(self, client, sample_task_data):
        """Test getting task dependents."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": [sample_task_data]}

            result = await client.get_task_dependents("DEV-42")

            mock_get.assert_called_once_with("/v1/tasks/DEV-42/dependents")
            assert len(result) == 1
            assert isinstance(result[0], Task)


class TestTaskEvents:
    """Test task events methods."""

    @pytest.mark.asyncio
    async def test_get_task_events_basic(self, client):
        """Test getting task events without filters."""
        events_data = [
            {
                "id": 1,
                "task_id": 1,
                "event_type": "created",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        ]

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": events_data}

            result = await client.get_task_events("DEV-42")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "/v1/tasks/DEV-42/events"
            assert result == events_data

    @pytest.mark.asyncio
    async def test_get_task_events_with_filters(self, client):
        """Test getting task events with filters."""
        events_data = [
            {
                "id": 1,
                "task_id": 1,
                "event_type": "status_changed",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        ]

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": events_data}

            await client.get_task_events(
                "DEV-42",
                event_type="status_changed",
                since="2024-01-01",
                limit=10,
            )

            call_args = mock_get.call_args
            params = call_args[1]["params"]
            assert params["event_type"] == "status_changed"
            assert params["since"] == "2024-01-01"
            assert params["limit"] == 10

    @pytest.mark.asyncio
    async def test_get_task_events_empty_list(self, client):
        """Test handling non-list response from events endpoint."""
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": {}}

            result = await client.get_task_events("DEV-42")

            assert result == []
