# T7-60: Fix Visualization Command Tests - Update Mocks to Use Pydantic Models

**Priority**: High
**Status**: Completed
**Created**: 2025-10-20

## Description

Fix 14 failing tests in `tests/cli/unit/test_visualization_commands.py` by updating mock return values to use Pydantic models instead of dicts. This is part of the cleanup after T7-56 (Remove Old Client) which migrated to typed API clients.

The visualization commands (board, timeline, summary, graph) use tasks and projects but the tests return dict objects instead of Pydantic models.

## Objectives

- Update all task mocks to use `create_test_task()` helper
- Update all project mocks to use `create_test_project()` helper
- Fix `list_tasks` mocks to return `PaginatedResponse[Task]`
- Ensure all 14 tests in test_visualization_commands.py pass

## Acceptance Criteria

- [x] All mock task objects use `create_test_task()`
- [x] All mock project objects use `create_test_project()`
- [x] All mock `list_tasks()` calls return `PaginatedResponse[Task]`
- [x] All 15 tests in `test_visualization_commands.py` pass
- [x] Type checking passes (`make typecheck`)
- [x] Linting passes (`make lint`)
- [x] Tests pass: `PYTHONPATH=src uv run pytest tests/cli/unit/test_visualization_commands.py -v`

## Dependencies

None (infrastructure already created)

## Estimated Effort

2-3 hours

## Technical Notes

### Files to Modify

**`tests/cli/unit/test_visualization_commands.py`**

### Required Imports

Add these imports:
```python
from cli.models.common import Status, Priority
from cli.models.task import Task
from cli.models.project import Project
from cli.schemas.pagination import PaginatedResponse
from tests.cli.unit.conftest import create_test_task, create_test_project
```

### Test Classes to Fix

1. **TestBoardCommand** (6 tests):
   - `test_board_basic_display`
   - `test_board_empty_workspace`
   - `test_board_with_mine_filter`
   - `test_board_with_status_filter`
   - `test_board_compact_mode`
   - `test_board_with_limit`

2. **TestTimelineCommand** (1 test):
   - `test_timeline_basic_display`

3. **TestSummaryCommand** (3 tests):
   - `test_summary_basic_display`
   - `test_summary_with_period_filter`
   - `test_summary_empty_workspace`

4. **TestGraphCommand** (4 tests):
   - `test_graph_for_specific_task`
   - `test_graph_without_task_shows_workspace_graph`
   - May have import errors to fix

### Common Fix Patterns

**Task lists in board/timeline views:**
```python
# OLD
mock_client.list_tasks = AsyncMock(
    return_value={
        "items": [
            {"id": 1, "identifier": "DEV-1", "status": "todo", ...},
            {"id": 2, "identifier": "DEV-2", "status": "inprogress", ...},
        ],
        "total": 2,
    }
)

# NEW
mock_client.list_tasks = AsyncMock(
    return_value=PaginatedResponse[Task](
        items=[
            create_test_task(id=1, identifier="DEV-1", status=Status.TODO, ...),
            create_test_task(id=2, identifier="DEV-2", status=Status.IN_PROGRESS, ...),
        ],
        total=2,
        limit=50,
        offset=0,
    )
)
```

**Project mocks (if used):**
```python
# OLD
mock_client.get_project = AsyncMock(
    return_value={
        "id": 1,
        "name": "Test Project",
        "identifier": "TEST",
    }
)

# NEW
mock_client.get_project = AsyncMock(
    return_value=create_test_project(
        id=1,
        name="Test Project",
        identifier="TEST",
    )
)
```

### Special Considerations

- **Board commands** group tasks by status, ensure Status enums are used
- **Timeline commands** may use date filtering, ensure datetime fields are present
- **Graph commands** may have import errors related to old APIClient

### Implementation Strategy

1. Add imports to the test file
2. Fix TestBoardCommand tests (6 tests) - Most critical for visualization
3. Fix TestTimelineCommand tests (1 test)
4. Fix TestSummaryCommand tests (3 tests)
5. Fix TestGraphCommand tests (4 tests) - May need client reference fixes
6. Run tests after each test class to catch issues early

### Test After Fixing

```bash
# Run just this file
PYTHONPATH=src uv run pytest tests/cli/unit/test_visualization_commands.py -v

# Run specific test class
PYTHONPATH=src uv run pytest tests/cli/unit/test_visualization_commands.py::TestBoardCommand -v
```

## Events

### 2025-10-20 20:20 - Created
- Task created to fix 14 failing tests in test_visualization_commands.py
- Part of test migration work after T7-56
- Visualization commands are important user-facing features
- Ready for implementation

### 2025-10-20 21:50 - Started work
- Moved task from backlog to active
- Starting with adding required imports
- Will fix tests class by class: Board → Timeline → Summary → Graph
- Plan to run tests after each class to catch issues early

### 2025-10-20 22:10 - Completed
- Updated `sample_tasks` fixture in conftest.py to return Task objects instead of dicts
- Added required imports to test_visualization_commands.py
- Fixed all TestBoardCommand tests (7 tests) to use PaginatedResponse[Task]
- Fixed all TestTimelineCommand tests (2 tests) to use create_test_task()
- Fixed all TestSummaryCommand tests (3 tests) to use PaginatedResponse[Task]
- Fixed all TestGraphCommand tests (3 tests) to use create_test_task()
- Fixed test assertions to check TaskFilters object instead of kwargs
- Fixed status value from "inprogress" to "in_progress" to match Status enum
- Removed unused imports (Project, create_test_project)
- All 15 tests passing
- Linting passes (make lint)
- Type checking passes (make typecheck)
- Task completed successfully
- PR created: https://github.com/supercarl87/AnyTaskCLI/pull/44
