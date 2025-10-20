"""Tests for task CRUD operations and dependencies."""

import pytest
from unittest.mock import patch

from cli.client import APIClient
from .conftest import create_mock_response, create_mock_async_client


@pytest.mark.asyncio
class TestTaskOperations:
    """Test task CRUD operations."""

    async def test_list_tasks_with_pagination(self):
        """Test list_tasks() with pagination."""
        client = APIClient(base_url="http://localhost:8000")

        response_data = {
            "items": [
                {"id": 1, "identifier": "DEV-1", "title": "Task 1", "status": "todo"},
                {
                    "id": 2,
                    "identifier": "DEV-2",
                    "title": "Task 2",
                    "status": "inprogress",
                },
            ],
            "pagination": {"total": 2, "limit": 50, "offset": 0},
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": response_data})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.list_tasks(limit=50, offset=0)

            assert result == response_data
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["limit"] == 50
            assert call_args[1]["params"]["offset"] == 0

    async def test_list_tasks_with_filters(self):
        """Test list_tasks() with various filters."""
        client = APIClient(base_url="http://localhost:8000")

        response_data = {"items": [], "pagination": {"total": 0}}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": response_data})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            await client.list_tasks(
                workspace_id=1,
                project_id=2,
                status=["todo", "inprogress"],
                owner="me",
                priority_gte=0,
                priority_lte=2,
            )

            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["workspace_id"] == 1
            assert params["project"] == 2
            assert params["status"] == "todo,inprogress"
            assert params["owner"] == "me"
            assert params["priority_gte"] == 0
            assert params["priority_lte"] == 2

    async def test_get_task_by_identifier(self):
        """Test get_task() by task identifier."""
        client = APIClient(base_url="http://localhost:8000")

        task = {
            "id": 1,
            "identifier": "DEV-1",
            "title": "Test Task",
            "description": "A test task",
            "status": "todo",
            "priority": 1,
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": task})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_task("DEV-1")

            assert result == task
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/tasks/DEV-1",
                headers={},
                timeout=10.0,
            )

    async def test_get_task_by_workspace_identifier(self):
        """Test get_task_by_workspace() by workspace ID and task identifier."""
        client = APIClient(base_url="http://localhost:8000")

        task = {
            "id": 1,
            "identifier": "DEV-1",
            "title": "Test Task",
            "description": "A test task",
            "status": "todo",
            "priority": 1,
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": task})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_task_by_workspace(
                workspace_id=42, identifier="DEV-1"
            )

            assert result == task
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/workspaces/42/tasks/DEV-1",
                headers={},
                timeout=10.0,
            )

    async def test_get_task_by_workspace_id_only(self):
        """Test get_task_by_workspace() by workspace ID and numeric task ID."""
        client = APIClient(base_url="http://localhost:8000")

        task = {"id": 1, "identifier": "DEV-1", "title": "Test Task"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": task})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_task_by_workspace(workspace_id=42, identifier="1")

            assert result == task
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/workspaces/42/tasks/1",
                headers={},
                timeout=10.0,
            )

    async def test_get_task_by_id(self):
        """Test get_task() by numeric ID."""
        client = APIClient(base_url="http://localhost:8000")

        task = {"id": 1, "identifier": "DEV-1", "title": "Test Task"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": task})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_task("1")

            assert result == task
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/tasks/1",
                headers={},
                timeout=10.0,
            )

    async def test_create_task_minimal(self):
        """Test create_task() with required fields."""
        client = APIClient(base_url="http://localhost:8000")

        created_task = {
            "id": 2,
            "identifier": "DEV-2",
            "title": "New Task",
            "status": "backlog",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": created_task})
            mock_client = create_mock_async_client(mock_response, method="post")
            mock_client_class.return_value = mock_client

            result = await client.create_task(project_id=1, title="New Task")

            assert result == created_task
            call_args = mock_client.post.call_args
            assert call_args[1]["json"]["title"] == "New Task"
            assert call_args[1]["json"]["status"] == "backlog"
            assert call_args[1]["json"]["priority"] == 0

    async def test_create_task_with_all_options(self):
        """Test create_task() with all optional fields."""
        client = APIClient(base_url="http://localhost:8000")

        created_task = {
            "id": 2,
            "identifier": "DEV-2",
            "title": "New Task",
            "description": "Task description",
            "status": "todo",
            "priority": 2,
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": created_task})
            mock_client = create_mock_async_client(mock_response, method="post")
            mock_client_class.return_value = mock_client

            result = await client.create_task(
                project_id=1,
                title="New Task",
                description="Task description",
                status="todo",
                priority=2,
                owner_id="user-123",
                labels=["bug", "urgent"],
                estimate=5,
                parent_id=1,
            )

            assert result == created_task
            call_args = mock_client.post.call_args
            payload = call_args[1]["json"]
            assert payload["title"] == "New Task"
            assert payload["description"] == "Task description"
            assert payload["status"] == "todo"
            assert payload["priority"] == 2
            assert payload["owner_id"] == "user-123"
            assert payload["labels"] == ["bug", "urgent"]
            assert payload["estimate"] == 5
            assert payload["parent_id"] == 1

    async def test_update_task_minimal(self):
        """Test update_task() with single field update."""
        client = APIClient(base_url="http://localhost:8000")

        updated_task = {
            "id": 1,
            "identifier": "DEV-1",
            "title": "Updated Task",
            "status": "inprogress",
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": updated_task})
            mock_client = create_mock_async_client(mock_response, method="patch")
            mock_client_class.return_value = mock_client

            result = await client.update_task("DEV-1", status="inprogress")

            assert result == updated_task
            call_args = mock_client.patch.call_args
            assert call_args[1]["json"] == {"status": "inprogress"}

    async def test_update_task_with_optimistic_locking(self):
        """Test update_task() with optimistic locking (If-Match header)."""
        client = APIClient(base_url="http://localhost:8000")

        updated_task = {"id": 1, "identifier": "DEV-1", "version": 2}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": updated_task})
            mock_client = create_mock_async_client(mock_response, method="patch")
            mock_client_class.return_value = mock_client

            result = await client.update_task("DEV-1", title="New Title", if_match=1)

            assert result == updated_task
            call_args = mock_client.patch.call_args
            headers = call_args[1]["headers"]
            assert headers["If-Match"] == "1"

    async def test_delete_task(self):
        """Test delete_task()."""
        client = APIClient(base_url="http://localhost:8000")

        deletion_response = {"deleted": True}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": deletion_response})
            mock_client = create_mock_async_client(mock_response, method="delete")
            mock_client_class.return_value = mock_client

            result = await client.delete_task("DEV-1")

            assert result == deletion_response
            mock_client.delete.assert_called_once_with(
                "http://localhost:8000/v1/tasks/DEV-1",
                headers={},
                timeout=10.0,
            )


@pytest.mark.asyncio
class TestTaskDependencies:
    """Test task dependency operations."""

    async def test_add_task_dependency(self):
        """Test add_task_dependency()."""
        client = APIClient(base_url="http://localhost:8000")

        dependency = {"id": 1, "task_id": 1, "depends_on_id": 2}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": dependency})
            mock_client = create_mock_async_client(mock_response, method="post")
            mock_client_class.return_value = mock_client

            result = await client.add_task_dependency("DEV-1", "DEV-2")

            assert result == dependency
            call_args = mock_client.post.call_args
            assert (
                call_args[0][0] == "http://localhost:8000/v1/tasks/DEV-1/dependencies"
            )
            assert call_args[1]["json"] == {"depends_on": "DEV-2"}

    async def test_remove_task_dependency(self):
        """Test remove_task_dependency()."""
        client = APIClient(base_url="http://localhost:8000")

        deletion_response = {"deleted": True}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": deletion_response})
            mock_client = create_mock_async_client(mock_response, method="delete")
            mock_client_class.return_value = mock_client

            result = await client.remove_task_dependency("DEV-1", "DEV-2")

            assert result == deletion_response
            mock_client.delete.assert_called_once_with(
                "http://localhost:8000/v1/tasks/DEV-1/dependencies/DEV-2",
                headers={},
                timeout=10.0,
            )

    async def test_get_task_dependencies(self):
        """Test get_task_dependencies()."""
        client = APIClient(base_url="http://localhost:8000")

        dependencies = [
            {"id": 1, "identifier": "DEV-2", "title": "Dependency 1"},
            {"id": 2, "identifier": "DEV-3", "title": "Dependency 2"},
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": dependencies})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_task_dependencies("DEV-1")

            assert result == dependencies
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/tasks/DEV-1/dependencies",
                headers={},
                timeout=10.0,
            )

    async def test_get_task_dependents(self):
        """Test get_task_dependents()."""
        client = APIClient(base_url="http://localhost:8000")

        dependents = [
            {"id": 3, "identifier": "DEV-4", "title": "Dependent Task 1"},
            {"id": 4, "identifier": "DEV-5", "title": "Dependent Task 2"},
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = create_mock_response({"data": dependents})
            mock_client = create_mock_async_client(mock_response, method="get")
            mock_client_class.return_value = mock_client

            result = await client.get_task_dependents("DEV-1")

            assert result == dependents
            mock_client.get.assert_called_once_with(
                "http://localhost:8000/v1/tasks/DEV-1/dependents",
                headers={},
                timeout=10.0,
            )
