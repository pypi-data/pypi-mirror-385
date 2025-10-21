"""Unit tests for TaskService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cli.client.tasks import TasksAPIClient
from cli.config import EnvironmentConfig, GlobalConfig
from cli.models.common import Priority, Status
from cli.models.task import Task, TaskCreate, TaskFilters, TaskUpdate
from cli.schemas.pagination import PaginatedResponse
from cli.services.task_service import TaskService


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
def task_service(mock_config):
    """Create TaskService with mocked client."""
    with patch.object(TasksAPIClient, "from_config") as mock_from_config:
        mock_client = MagicMock(spec=TasksAPIClient)
        mock_from_config.return_value = mock_client

        service = TaskService(mock_config)
        service.tasks = mock_client  # Ensure it's set

        yield service


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        id=1,
        public_id=100000001,
        identifier="TEST-1",
        title="Test Task",
        description="A test task",
        status=Status.TODO,
        priority=Priority.NORMAL,
        project_id=10,
        workspace_id=100,
        labels=[],
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00",
        version=1,
    )


@pytest.mark.asyncio
async def test_list_tasks(task_service, sample_task):
    """Test list_tasks passes through to client."""
    # Setup
    filters = TaskFilters(workspace_id=100)
    expected_response = PaginatedResponse[Task](
        items=[sample_task], total=1, limit=10, offset=0
    )
    task_service.tasks.list_tasks = AsyncMock(return_value=expected_response)

    # Execute
    result = await task_service.list_tasks(filters)

    # Verify
    assert result == expected_response
    task_service.tasks.list_tasks.assert_called_once_with(filters)


@pytest.mark.asyncio
async def test_get_task(task_service, sample_task):
    """Test get_task passes through to client."""
    # Setup
    task_service.tasks.get_task = AsyncMock(return_value=sample_task)

    # Execute
    result = await task_service.get_task("TEST-1")

    # Verify
    assert result == sample_task
    task_service.tasks.get_task.assert_called_once_with("TEST-1")


@pytest.mark.asyncio
async def test_create_task_with_validation_success(task_service, sample_task):
    """Test create_task_with_validation with valid data."""
    # Setup
    task_create = TaskCreate(
        title="New Task", description="Description", priority=Priority.HIGH
    )
    task_service.tasks.create_task = AsyncMock(return_value=sample_task)

    # Execute
    result = await task_service.create_task_with_validation(10, task_create)

    # Verify
    assert result == sample_task
    task_service.tasks.create_task.assert_called_once_with(10, task_create)


@pytest.mark.asyncio
async def test_create_task_with_validation_priority_within_range(
    task_service, sample_task
):
    """Test create_task_with_validation accepts valid priority range."""
    # Priority validation is already done by Pydantic, service should accept valid enums
    task_create = TaskCreate(title="Task", priority=Priority.HIGHEST)  # Valid: 2
    task_service.tasks.create_task = AsyncMock(return_value=sample_task)

    # Execute
    result = await task_service.create_task_with_validation(10, task_create)

    # Verify - should succeed
    assert result == sample_task


@pytest.mark.asyncio
async def test_update_task(task_service, sample_task):
    """Test update_task passes through to client."""
    # Setup
    updates = TaskUpdate(title="Updated Title")
    task_service.tasks.update_task = AsyncMock(return_value=sample_task)

    # Execute
    result = await task_service.update_task("TEST-1", updates)

    # Verify
    assert result == sample_task
    task_service.tasks.update_task.assert_called_once_with("TEST-1", updates)


@pytest.mark.asyncio
async def test_update_task_status(task_service, sample_task):
    """Test update_task_status convenience method."""
    # Setup
    task_service.tasks.update_task = AsyncMock(return_value=sample_task)

    # Execute
    result = await task_service.update_task_status("TEST-1", Status.IN_PROGRESS)

    # Verify
    assert result == sample_task
    task_service.tasks.update_task.assert_called_once()
    call_args = task_service.tasks.update_task.call_args
    assert call_args[0][0] == "TEST-1"
    assert call_args[0][1].status == Status.IN_PROGRESS


@pytest.mark.asyncio
async def test_delete_task(task_service):
    """Test delete_task passes through to client."""
    # Setup
    task_service.tasks.delete_task = AsyncMock()

    # Execute
    await task_service.delete_task("TEST-1")

    # Verify
    task_service.tasks.delete_task.assert_called_once_with("TEST-1")


@pytest.mark.asyncio
async def test_complete_task_success(task_service, sample_task):
    """Test complete_task with no blocking dependencies."""
    # Setup
    task_service.tasks.get_task = AsyncMock(return_value=sample_task)
    task_service.tasks.get_task_dependencies = AsyncMock(return_value=[])
    completed_task = Task(**sample_task.model_dump())
    completed_task.status = Status.DONE
    task_service.tasks.update_task = AsyncMock(return_value=completed_task)

    # Execute
    result = await task_service.complete_task("TEST-1")

    # Verify
    assert result.status == Status.DONE
    task_service.tasks.get_task.assert_called_once_with("TEST-1")
    task_service.tasks.get_task_dependencies.assert_called_once_with("TEST-1")
    task_service.tasks.update_task.assert_called_once()


@pytest.mark.asyncio
async def test_complete_task_with_incomplete_dependencies(task_service, sample_task):
    """Test complete_task fails when dependencies are not done."""
    # Setup
    dependency = Task(**sample_task.model_dump())
    dependency.identifier = "TEST-2"
    dependency.status = Status.IN_PROGRESS  # Not done
    task_service.tasks.get_task = AsyncMock(return_value=sample_task)
    task_service.tasks.get_task_dependencies = AsyncMock(return_value=[dependency])

    # Execute & Verify
    with pytest.raises(
        ValueError, match="Cannot complete task. 1 dependencies are not done yet"
    ):
        await task_service.complete_task("TEST-1")


@pytest.mark.asyncio
async def test_suggest_next_tasks(task_service, sample_task):
    """Test suggest_next_tasks returns sorted tasks."""
    # Setup
    task1 = Task(**sample_task.model_dump())
    task1.id = 1
    task1.priority = Priority.HIGH

    task2 = Task(**sample_task.model_dump())
    task2.id = 2
    task2.priority = Priority.LOW

    task3 = Task(**sample_task.model_dump())
    task3.id = 3
    task3.priority = Priority.HIGH

    paginated = PaginatedResponse[Task](
        items=[task2, task1, task3],  # Unsorted
        total=3,
        limit=10,
        offset=0,
    )
    task_service.tasks.list_tasks = AsyncMock(return_value=paginated)

    # Execute
    result = await task_service.suggest_next_tasks(workspace_id=100, limit=2)

    # Verify - should be sorted by priority (high first)
    assert len(result) == 2
    assert result[0].priority == Priority.HIGH
    assert result[1].priority == Priority.HIGH


@pytest.mark.asyncio
async def test_add_dependency(task_service):
    """Test add_dependency passes through to client."""
    # Setup
    task_service.tasks.add_task_dependency = AsyncMock()

    # Execute
    await task_service.add_dependency("TEST-1", "TEST-2")

    # Verify
    task_service.tasks.add_task_dependency.assert_called_once_with("TEST-1", "TEST-2")


@pytest.mark.asyncio
async def test_remove_dependency(task_service):
    """Test remove_dependency passes through to client."""
    # Setup
    task_service.tasks.remove_task_dependency = AsyncMock()

    # Execute
    await task_service.remove_dependency("TEST-1", "TEST-2")

    # Verify
    task_service.tasks.remove_task_dependency.assert_called_once_with(
        "TEST-1", "TEST-2"
    )


@pytest.mark.asyncio
async def test_get_task_with_context(task_service, sample_task):
    """Test get_task_with_context returns task with dependencies."""
    # Setup
    dep_task = Task(**sample_task.model_dump())
    dep_task.identifier = "TEST-2"

    dependent_task = Task(**sample_task.model_dump())
    dependent_task.identifier = "TEST-3"

    task_service.tasks.get_task = AsyncMock(return_value=sample_task)
    task_service.tasks.get_task_dependencies = AsyncMock(return_value=[dep_task])
    task_service.tasks.get_task_dependents = AsyncMock(return_value=[dependent_task])

    # Execute
    result = await task_service.get_task_with_context("TEST-1")

    # Verify
    assert result["task"] == sample_task
    assert result["dependencies"] == [dep_task]
    assert result["dependents"] == [dependent_task]


def test_is_similar():
    """Test _is_similar helper method."""
    config = GlobalConfig(
        current_environment="test",
        environments={"test": EnvironmentConfig(api_url="http://localhost:8000")},
    )
    service = TaskService(config)

    # Substring matches
    assert service._is_similar("fix bug", "fix bug in auth")
    assert service._is_similar("fix bug in auth", "fix bug")

    # No match
    assert not service._is_similar("fix bug", "add feature")
