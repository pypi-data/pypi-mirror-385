# T7-61: Fix Project and Dependency Tests - Update Mocks to Use Pydantic Models

**Priority**: High
**Status**: Completed
**Created**: 2025-10-20
**Completed**: 2025-10-20

## Description

Fix 16 failing tests across two test files by updating mock return values to use Pydantic models:
- `tests/cli/unit/test_project_commands.py` (9 tests)
- `tests/cli/unit/task_commands/test_task_dependencies.py` (7 tests)

Both files are related to entity management (projects and task dependencies) and can be fixed together in one PR.

## Objectives

- Update project mocks to use `create_test_project()` helper
- Update task mocks to use `create_test_task()` helper
- Fix dependency-related mocks to return proper Pydantic models
- Ensure all 16 tests pass

## Acceptance Criteria

- [x] All 13 tests in `test_project_commands.py` pass
- [x] All 7 tests in `test_task_dependencies.py` pass
- [x] All mock project objects use `create_test_project()`
- [x] All mock task objects use `create_test_task()`
- [x] Dependency mocks return proper Task models
- [x] Type checking passes (`make typecheck`)
- [x] Linting passes (`make lint`)
- [x] Tests pass for both files

## Dependencies

None (infrastructure already created)

## Estimated Effort

2-3 hours

## Technical Notes

### Files to Modify

1. **`tests/cli/unit/test_project_commands.py`** (9 tests)
2. **`tests/cli/unit/task_commands/test_task_dependencies.py`** (7 tests)

### Required Imports

**For test_project_commands.py:**
```python
from cli.models.project import Project
from cli.schemas.pagination import PaginatedResponse
from tests.cli.unit.conftest import create_test_project
```

**For test_task_dependencies.py:**
```python
from cli.models.common import Status, Priority
from cli.models.task import Task
from cli.models.dependency import TaskDependency
from tests.cli.unit.conftest import create_test_task
```

### test_project_commands.py Fix Patterns

**Project creation:**
```python
# OLD
mock_client.create_project = AsyncMock(
    return_value={
        "id": 1,
        "name": "New Project",
        "identifier": "NEW",
        "workspace_id": 123,
    }
)

# NEW
mock_client.create_project = AsyncMock(
    return_value=create_test_project(
        id=1,
        name="New Project",
        identifier="NEW",
        workspace_id=123,
    )
)
```

**Project listing:**
```python
# OLD
mock_client.list_projects = AsyncMock(
    return_value={
        "items": [{"id": 1, "name": "Project 1", ...}],
        "total": 1,
    }
)

# NEW
mock_client.list_projects = AsyncMock(
    return_value=PaginatedResponse[Project](
        items=[create_test_project(id=1, name="Project 1", ...)],
        total=1,
        limit=50,
        offset=0,
    )
)
```

### test_task_dependencies.py Fix Patterns

**Task with dependencies:**
```python
# OLD
mock_client.get_task = AsyncMock(
    return_value={
        "id": 1,
        "identifier": "DEV-1",
        "title": "Task with deps",
        "dependencies": [2, 3],
    }
)

# NEW
mock_client.get_task = AsyncMock(
    return_value=create_test_task(
        id=1,
        identifier="DEV-1",
        title="Task with deps",
        # Note: dependencies may need special handling
    )
)
```

**Dependency objects:**
```python
# May need to return TaskDependency objects
from cli.models.dependency import TaskDependency

mock_client.get_dependencies = AsyncMock(
    return_value=[
        TaskDependency(
            task_id=1,
            depends_on_id=2,
            dependency_type="blocks",
        ),
    ]
)
```

### Test Classes

**test_project_commands.py:**
- `TestProjectCreateCommand`
- `TestProjectListCommand`
- `TestProjectUseCommand`
- `TestProjectCurrentCommand`
- `TestProjectSwitchCommand`

**test_task_dependencies.py:**
- `TestDependencyAddCommand`
- `TestDependencyListCommand`
- `TestDependencyRemoveCommand`

### Implementation Strategy

1. **Fix test_project_commands.py first** (9 tests):
   - Add imports
   - Fix `create_project` mocks
   - Fix `list_projects` mocks to return `PaginatedResponse[Project]`
   - Fix `get_project` mocks
   - Run tests: `PYTHONPATH=src uv run pytest tests/cli/unit/test_project_commands.py -v`

2. **Fix test_task_dependencies.py** (7 tests):
   - Add imports
   - Fix task mocks to use `create_test_task()`
   - Fix dependency mocks (may need TaskDependency model)
   - Handle cases where tasks have dependency relationships
   - Run tests: `PYTHONPATH=src uv run pytest tests/cli/unit/task_commands/test_task_dependencies.py -v`

3. **Run both test files together** to ensure no conflicts

### Test After Fixing

```bash
# Test project commands
PYTHONPATH=src uv run pytest tests/cli/unit/test_project_commands.py -v

# Test dependency commands
PYTHONPATH=src uv run pytest tests/cli/unit/task_commands/test_task_dependencies.py -v

# Test both together
PYTHONPATH=src uv run pytest tests/cli/unit/test_project_commands.py tests/cli/unit/task_commands/test_task_dependencies.py -v
```

## Events

### 2025-10-20 20:25 - Created
- Task created to fix 16 failing tests across 2 files
- Grouped together as both relate to entity management (projects and dependencies)
- Part of test migration work after T7-56
- Ready for implementation

### 2025-10-20 21:55 - Started work
- Moved task from backlog to active
- Beginning implementation following the strategy outlined in technical notes
- Will fix test_project_commands.py first (13 tests), then test_task_dependencies.py (7 tests)

### 2025-10-20 22:30 - Completed implementation
- Fixed test_project_commands.py: Refactored all 13 tests to mock services (WorkspaceService, ProjectService, PreferenceService) instead of API clients
- Added helper functions to conftest.py: create_test_workspace() and create_test_user_preferences()
- Fixed test_task_dependencies.py: Updated mocks to return Pydantic Task models instead of dicts
- All 20 tests pass (13 + 7)
- Pre-merge checks pass: format ✅, lint ✅, typecheck ✅
- Task completed successfully
- Created PR: https://github.com/supercarl87/AnyTaskCLI/pull/45
