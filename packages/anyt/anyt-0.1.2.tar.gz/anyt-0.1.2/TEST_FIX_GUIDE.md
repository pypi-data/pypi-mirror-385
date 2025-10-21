# Test Fix Guide - Updating Mocks for Typed Clients

## Current Status

**Before fixes**: 80 failed, 129 passed  
**Current**: **53 failed, 155 passed, 1 skipped**

**Progress**: Fixed 27 tests (+26 passing tests)

## What Was Done

### 1. Infrastructure Setup ✅

Created helper functions in `tests/cli/unit/conftest.py`:
```python
def create_test_task(...) -> Task:
    """Create a test Task instance with sensible defaults."""
    
def create_test_project(...) -> Project:
    """Create a test Project instance with sensible defaults."""
```

### 2. Global Fixture ✅

Added autouse fixture to prevent workspace config interference:
```python
@pytest.fixture(autouse=True)
def auto_patch_workspace_config(monkeypatch):
    """Automatically patch WorkspaceConfig.load() for all tests."""
```

### 3. Updated API Client References ✅

Replaced all old `cli.client.APIClient` references with typed clients:
- `cli.client.ai.AIAPIClient`
- `cli.client.tasks.TasksAPIClient`  
- `cli.client.projects.ProjectsAPIClient`
- etc.

### 4. Fixed Files ✅

- `tests/cli/unit/test_ai_commands.py` - 13/14 passing (1 skipped)
- `tests/cli/unit/task_commands/test_task_list.py` - 4/4 passing ✅

## Remaining Work

### Files to Fix (53 tests)

1. **test_preference_commands.py** (6 tests) - Started
2. **test_task_dependencies.py** (7 tests)
3. **test_task_pick_interactive.py** (8 tests)
4. **test_project_commands.py** (9 tests)
5. **test_visualization_commands.py** (14 tests)
6. **test_task_crud.py** (17 tests) - Most complex

## Fixing Pattern

### Pattern 1: Simple Mock Updates

**OLD (returns dict):**
```python
mock_client.get_task = AsyncMock(
    return_value={
        "id": 1,
        "identifier": "DEV-1",
        "title": "Test Task",
        "status": "todo",
    }
)
```

**NEW (returns Pydantic model):**
```python
from tests.cli.unit.conftest import create_test_task
from cli.models.common import Status, Priority

mock_client.get_task = AsyncMock(
    return_value=create_test_task(
        id=1,
        identifier="DEV-1",
        title="Test Task",
        status=Status.TODO,
    )
)
```

### Pattern 2: list_tasks Returns PaginatedResponse

**OLD:**
```python
mock_client.list_tasks = AsyncMock(
    return_value={
        "items": [{"id": 1, "identifier": "DEV-1", ...}],
        "total": 1,
    }
)
```

**NEW:**
```python
from cli.schemas.pagination import PaginatedResponse
from cli.models.task import Task

mock_client.list_tasks = AsyncMock(
    return_value=PaginatedResponse[Task](
        items=[
            create_test_task(id=1, identifier="DEV-1", ...),
        ],
        total=1,
        limit=50,
        offset=0,
    )
)
```

### Pattern 3: Checking Call Arguments

**OLD (checking kwargs):**
```python
call_kwargs = mock_client.list_tasks.call_args.kwargs
assert call_kwargs["status"] == ["todo"]
```

**NEW (checking TaskFilters object):**
```python
call_args = mock_client.list_tasks.call_args
filters = call_args[0][0]  # First positional argument
assert filters.status == [Status.TODO]
```

### Pattern 4: Service Instead of Client

Some commands use services instead of clients directly:

**Preference commands:**
```python
# OLD
with patch("cli.commands.preference.APIClient.from_config"):
    ...

# NEW  
with patch("cli.services.preference_service.PreferenceService.from_config"):
    with patch("cli.services.workspace_service.WorkspaceService.from_config"):
        ...
```

## File-Specific Guidance

### test_task_crud.py (17 tests)

**Issues:**
- Mock return values are dicts instead of Task objects
- `list_tasks` needs `PaginatedResponse[Task]`
- `create_task` returns Task
- `update_task` returns Task
- `get_task` returns Task

**Imports needed:**
```python
from cli.models.common import Status, Priority
from cli.models.task import Task
from cli.schemas.pagination import PaginatedResponse
from tests.cli.unit.conftest import create_test_task
```

**Example fix:**
```python
# Line 38-46: Fix create_task mock
mock_client.create_task = AsyncMock(
    return_value=create_test_task(
        id=42,
        identifier="DEV-42",
        title="New Feature",
        status=Status.BACKLOG,
        priority=Priority.HIGH,
        labels=["feature", "urgent"],
    )
)
```

### test_task_pick_interactive.py (8 tests)

**Issues:**
- Task dicts need to be Task objects
- Tests access `.status`, `.title`, `.priority` attributes

**Imports needed:**
```python
from cli.models.common import Status, Priority
from tests.cli.unit.conftest import create_test_task
```

### test_task_dependencies.py (7 tests)

**Issues:**
- Similar to test_task_crud.py
- Dependency objects may need updating

### test_project_commands.py (9 tests)

**Issues:**
- Project dicts need to be Project objects
- May need `create_test_project()` helper

**Imports needed:**
```python
from cli.models.project import Project
from tests.cli.unit.conftest import create_test_project
```

### test_visualization_commands.py (14 tests)

**Issues:**
- Uses both tasks and projects
- Board/timeline views
- May have complex dict structures

## Quick Reference

### Required Enums

```python
from cli.models.common import Status, Priority

# Status values
Status.BACKLOG
Status.TODO
Status.IN_PROGRESS  
Status.DONE
Status.CANCELLED

# Priority values
Priority.LOWEST   # -2
Priority.LOW      # -1
Priority.NORMAL   # 0
Priority.HIGH     # 1
Priority.HIGHEST  # 2
```

### Task Required Fields

```python
create_test_task(
    id=1,                    # Required
    identifier="DEV-1",      # Required
    title="Task Title",      # Required
    description="...",       # Optional (has default)
    status=Status.TODO,      # Required
    priority=Priority.NORMAL,# Required
    project_id=1,            # Required
    workspace_id=1,          # Required
    # These have defaults in create_test_task:
    # created_at=datetime.now()
    # updated_at=datetime.now()
    # version=1
    # labels=[]
)
```

## Testing Strategy

1. **Fix one file at a time**
2. **Run tests after each fix**: `PYTHONPATH=src uv run pytest tests/cli/unit/path/to/test_file.py -v`
3. **Check for new errors**: They often reveal other needed fixes
4. **Run full suite periodically**: `make test`

## Common Errors & Solutions

### Error: 'dict' object has no attribute 'identifier'
**Solution:** Return `create_test_task()` instead of dict

### Error: 'dict' object has no attribute 'total'
**Solution:** Return `PaginatedResponse[Task]()` instead of dict

### Error: AttributeError: module 'cli.commands.X' has no attribute 'APIClient'
**Solution:** Patch the service instead (e.g., `XService.from_config`)

### Error: KeyError: 'status' (when checking call args)
**Solution:** Access TaskFilters object: `filters = call_args[0][0]`

## Final Checklist

After fixing all tests:

```bash
# 1. Format code
make format

# 2. Lint code
make lint

# 3. Type check
make typecheck

# 4. Run all tests
make test

# All should pass! Target: 209 passed, 0 failed
```

## Summary

The infrastructure is in place. The remaining work is mechanical:
1. Add imports
2. Replace dict mocks with `create_test_task()` / `create_test_project()`
3. Wrap list_tasks in `PaginatedResponse[Task]`
4. Update assertion patterns for TaskFilters

Good luck!
