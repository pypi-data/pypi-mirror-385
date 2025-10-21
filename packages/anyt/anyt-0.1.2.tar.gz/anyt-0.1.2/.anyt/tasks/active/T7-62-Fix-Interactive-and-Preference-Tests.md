# T7-62: Fix Interactive Picker and Preference Tests - Update Mocks to Use Pydantic Models

**Priority**: Medium
**Status**: In Progress
**Created**: 2025-10-20

## Description

Fix 14 failing tests across two smaller test files:
- `tests/cli/unit/task_commands/test_task_pick_interactive.py` (8 tests)
- `tests/cli/unit/test_preference_commands.py` (6 tests)

These are smaller test files that can be fixed together in one PR. The pick interactive tests are for the task picker UI, and preference tests are for user preference management.

## Objectives

- Update task mocks in interactive picker tests to use `create_test_task()`
- Update preference service mocks to use proper service patterns
- Ensure all 14 tests pass

## Acceptance Criteria

- [x] All 8 tests in `test_task_pick_interactive.py` pass
- [x] All 6 tests in `test_preference_commands.py` pass
- [x] Task mocks use `create_test_task()` helper
- [x] Preference service mocks use `PreferenceService` instead of old APIClient
- [x] Type checking passes (`make typecheck`)
- [x] Linting passes (`make lint`)
- [x] Tests pass for both files

## Dependencies

None (infrastructure already created)

## Estimated Effort

1-2 hours

## Technical Notes

### Files to Modify

1. **`tests/cli/unit/task_commands/test_task_pick_interactive.py`** (8 tests)
2. **`tests/cli/unit/test_preference_commands.py`** (6 tests)

### Required Imports

**For test_task_pick_interactive.py:**
```python
from cli.models.common import Status, Priority
from cli.models.task import Task
from tests.cli.unit.conftest import create_test_task
```

**For test_preference_commands.py:**
```python
# Already has most imports, may need:
from cli.services.preference_service import PreferenceService
from cli.services.workspace_service import WorkspaceService
```

### test_task_pick_interactive.py Fix Patterns

The interactive picker tests access task attributes like `.status`, `.title`, `.priority`, so task dicts must be converted to Task objects.

**Task lists for picker:**
```python
# OLD
mock_tasks = [
    {
        "id": 1,
        "identifier": "DEV-1",
        "title": "First task",
        "status": "todo",
        "priority": 1,
    },
    {
        "id": 2,
        "identifier": "DEV-2",
        "title": "Second task",
        "status": "inprogress",
        "priority": 0,
    },
]

# NEW
mock_tasks = [
    create_test_task(
        id=1,
        identifier="DEV-1",
        title="First task",
        status=Status.TODO,
        priority=Priority.HIGH,
    ),
    create_test_task(
        id=2,
        identifier="DEV-2",
        title="Second task",
        status=Status.IN_PROGRESS,
        priority=Priority.NORMAL,
    ),
]
```

**Common pattern in picker tests:**
```python
# Tests will group by status, access .status attribute
# Tests will display title, access .title attribute
# Tests will show priority, access .priority attribute
```

### test_preference_commands.py Fix Patterns

Preference commands use **services** not direct API clients.

**Service mocking pattern (PARTIALLY STARTED):**
```python
# OLD (incorrect - APIClient doesn't exist in preference commands)
with patch("cli.commands.preference.APIClient.from_config") as mock_client_factory:
    ...

# NEW (correct - use services)
with patch("cli.services.preference_service.PreferenceService.from_config") as mock_service_factory:
    with patch("cli.services.workspace_service.WorkspaceService.from_config") as mock_ws_service_factory:
        mock_service = AsyncMock()
        mock_service.get_user_preferences = AsyncMock(return_value=None)
        mock_service_factory.return_value = mock_service

        mock_ws_service = AsyncMock()
        mock_ws_service_factory.return_value = mock_ws_service

        result = cli_runner.invoke(app, ["preference", "show"])
```

**Preference data structure:**
```python
# Preferences are returned as dicts (not Pydantic models in current implementation)
prefs = {
    "user_id": "test-user",
    "current_workspace_id": 1,
    "current_project_id": 5,
}
```

### Test Classes

**test_task_pick_interactive.py:**
- `TestDisplayInteractivePicker` (8 tests):
  - Tests for picker with grouping
  - Tests for picker without grouping
  - Tests for cancelled selection
  - Tests for invalid input handling
  - Tests for long titles
  - Tests for all priority levels
  - Tests for multiple status groups

**test_preference_commands.py:**
- `TestPreferenceCommands` (6 tests):
  - `test_preference_show_no_auth_token`
  - `test_preference_show_no_preferences_set` (partially fixed)
  - `test_preference_show_with_preferences`
  - `test_preference_set_workspace_success`
  - `test_preference_set_project_success`
  - `test_preference_clear_success`

### Implementation Strategy

1. **Fix test_task_pick_interactive.py first** (8 tests):
   - Add imports
   - Convert all task dict lists to use `create_test_task()`
   - Ensure Status and Priority enums are used
   - Run tests: `PYTHONPATH=src uv run pytest tests/cli/unit/task_commands/test_task_pick_interactive.py -v`

2. **Fix test_preference_commands.py** (6 tests):
   - Review partially started fix for `test_preference_show_no_preferences_set`
   - Apply service mocking pattern to all remaining tests
   - Replace `APIClient` patches with `PreferenceService` and `WorkspaceService` patches
   - Run tests: `PYTHONPATH=src uv run pytest tests/cli/unit/test_preference_commands.py -v`

3. **Run both test files together** to ensure no conflicts

### Test After Fixing

```bash
# Test picker commands
PYTHONPATH=src uv run pytest tests/cli/unit/task_commands/test_task_pick_interactive.py -v

# Test preference commands
PYTHONPATH=src uv run pytest tests/cli/unit/test_preference_commands.py -v

# Test both together
PYTHONPATH=src uv run pytest tests/cli/unit/task_commands/test_task_pick_interactive.py tests/cli/unit/test_preference_commands.py -v
```

## Events

### 2025-10-20 20:30 - Created
- Task created to fix 14 failing tests across 2 smaller files
- Pick interactive tests are for task picker UI
- Preference tests need service mocking pattern (partially started)
- Part of test migration work after T7-56
- Ready for implementation

### 2025-10-20 22:15 - Started work
- Moved task from backlog to active
- Updated status to "In Progress"
- Beginning implementation of test fixes
- Will start with test_task_pick_interactive.py (8 tests) then test_preference_commands.py (6 tests)

### 2025-10-20 23:00 - Completed
- Fixed all 8 tests in `test_task_pick_interactive.py`:
  - Updated imports to include `Status`, `Priority`, and `create_test_task`
  - Converted all task dictionaries to use `create_test_task()` with proper enums
  - Fixed priority mapping: 2→HIGHEST, 1→HIGH, 0→NORMAL, -1→LOW, -2→LOWEST
  - All tests now pass successfully
- Fixed all 10 tests in `test_preference_commands.py`:
  - Updated service mocks from `APIClient` to `PreferenceService` and `WorkspaceService`
  - Fixed model imports: `UserPreferences` from `cli.models.user` (not `cli.models.preference`)
  - Added required fields to models: `updated_at` for UserPreferences, `created_at`/`updated_at` for Workspace
  - Updated all async mock patterns to use `AsyncMock(return_value=...)`
  - All tests now pass successfully
- All acceptance criteria met:
  - ✅ All 8 tests in `test_task_pick_interactive.py` pass
  - ✅ All 10 tests in `test_preference_commands.py` pass (originally estimated 6, but 10 total in file)
  - ✅ Task mocks use `create_test_task()` helper
  - ✅ Preference service mocks use `PreferenceService` and `WorkspaceService`
  - ✅ Type checking passes (`make typecheck`)
  - ✅ Linting passes (`make lint`)
  - ✅ Format passes (`make format`)
- Total: 19 tests now passing (9 in picker + 10 in preferences)
- Ready to commit and create PR
