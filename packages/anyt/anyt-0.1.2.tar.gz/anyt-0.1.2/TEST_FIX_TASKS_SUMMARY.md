# Test Fix Tasks - Summary

## Overview

Created 4 new tasks to fix the remaining 53 failing tests after T7-56 (Remove Old Client). Each task is organized for a separate PR.

## Current Test Status

**Before fixes**: 80 failed, 129 passed  
**Current**: **53 failed, 155 passed, 1 skipped**  
**Progress**: Fixed 27 tests (+26 passing tests)

## Created Tasks

### T7-59: Fix Task CRUD Tests (17 tests) - High Priority
**File**: `.anyt/tasks/backlog/T7-59-Fix-Task-CRUD-Tests.md`

- **Tests**: `tests/cli/unit/task_commands/test_task_crud.py` (17 tests)
- **Effort**: 2-3 hours
- **Complexity**: High (most complex test file)
- **Focus**: Task CRUD operations (add, show, edit, done, remove, pick)

**Key Changes Needed**:
- Fix `get_task()`, `create_task()`, `update_task()` mocks
- Fix `list_tasks()` to return `PaginatedResponse[Task]`
- Update test assertions to check `TaskFilters` objects

**Test Classes**:
- TestTaskAddCommand (3 tests)
- TestTaskShowCommand (2 tests)
- TestTaskEditCommand (1 test)
- TestTaskDoneCommand (1 test)
- TestTaskPickCommand (4 tests)

---

### T7-60: Fix Visualization Tests (14 tests) - High Priority
**File**: `.anyt/tasks/backlog/T7-60-Fix-Visualization-Tests.md`

- **Tests**: `tests/cli/unit/test_visualization_commands.py` (14 tests)
- **Effort**: 2-3 hours
- **Complexity**: Medium-High
- **Focus**: Board, timeline, summary, graph visualization commands

**Key Changes Needed**:
- Fix task mocks to use `create_test_task()`
- Fix project mocks to use `create_test_project()`
- Fix `list_tasks()` to return `PaginatedResponse[Task]`
- Fix any import errors for old APIClient references

**Test Classes**:
- TestBoardCommand (6 tests) - Critical user-facing feature
- TestTimelineCommand (1 test)
- TestSummaryCommand (3 tests)
- TestGraphCommand (4 tests)

---

### T7-61: Fix Project and Dependency Tests (16 tests) - High Priority
**File**: `.anyt/tasks/backlog/T7-61-Fix-Project-and-Dependency-Tests.md`

- **Tests**: 
  - `tests/cli/unit/test_project_commands.py` (9 tests)
  - `tests/cli/unit/task_commands/test_task_dependencies.py` (7 tests)
- **Effort**: 2-3 hours
- **Complexity**: Medium
- **Focus**: Project management and task dependency features

**Key Changes Needed**:
- Fix project mocks to use `create_test_project()`
- Fix `list_projects()` to return `PaginatedResponse[Project]`
- Fix task dependency mocks (may need `TaskDependency` model)
- Fix task mocks to use `create_test_task()`

**Test Classes**:
- TestProjectCreateCommand
- TestProjectListCommand
- TestProjectUseCommand
- TestProjectCurrentCommand
- TestProjectSwitchCommand
- TestDependencyAddCommand
- TestDependencyListCommand
- TestDependencyRemoveCommand

---

### T7-62: Fix Interactive and Preference Tests (14 tests) - Medium Priority
**File**: `.anyt/tasks/backlog/T7-62-Fix-Interactive-and-Preference-Tests.md`

- **Tests**:
  - `tests/cli/unit/task_commands/test_task_pick_interactive.py` (8 tests)
  - `tests/cli/unit/test_preference_commands.py` (6 tests)
- **Effort**: 1-2 hours
- **Complexity**: Low-Medium (smaller files)
- **Focus**: Interactive picker UI and user preferences

**Key Changes Needed**:
- Fix task mocks in picker tests to use `create_test_task()`
- Fix preference tests to use `PreferenceService` instead of old `APIClient`
- Complete partially started fixes in preference tests

**Test Classes**:
- TestDisplayInteractivePicker (8 tests)
- TestPreferenceCommands (6 tests)

---

## Infrastructure Already Created

✅ **Helper Functions** (`tests/cli/unit/conftest.py`):
```python
def create_test_task(...) -> Task
def create_test_project(...) -> Project
```

✅ **Global Fixture**:
```python
@pytest.fixture(autouse=True)
def auto_patch_workspace_config(monkeypatch)
```

✅ **API Client References Updated**:
- All old `cli.client.APIClient` → typed clients

✅ **Documentation Created**:
- `TEST_FIX_GUIDE.md` - Comprehensive guide with patterns and examples

## Recommended Order

1. **T7-59** (Task CRUD) - Highest impact, most used features
2. **T7-60** (Visualizations) - User-facing board/timeline views
3. **T7-61** (Projects/Dependencies) - Entity management features
4. **T7-62** (Interactive/Preferences) - Smaller files, quickest wins

Each task is independent and can be worked on in parallel if needed.

## Success Criteria

After completing all 4 tasks:
- ✅ All 209 tests passing (currently 155 passing)
- ✅ `make test` shows 0 failures
- ✅ `make typecheck` passes
- ✅ `make lint` passes
- ✅ `make format` passes

## Quick Reference

### Common Fix Patterns

**Pattern 1: Simple mocks**
```python
# OLD: return_value={"id": 1, "status": "todo"}
# NEW: return_value=create_test_task(id=1, status=Status.TODO)
```

**Pattern 2: list_tasks**
```python
# OLD: return_value={"items": [...], "total": 1}
# NEW: return_value=PaginatedResponse[Task](items=[...], total=1, limit=50, offset=0)
```

**Pattern 3: Services**
```python
# OLD: patch("cli.commands.X.APIClient.from_config")
# NEW: patch("cli.services.x_service.XService.from_config")
```

### Enum Mappings

```python
# Status
"backlog" -> Status.BACKLOG
"todo" -> Status.TODO
"inprogress" -> Status.IN_PROGRESS
"done" -> Status.DONE

# Priority
-2 -> Priority.LOWEST
-1 -> Priority.LOW
0  -> Priority.NORMAL
1  -> Priority.HIGH
2  -> Priority.HIGHEST
```

## Files Created

- `.anyt/tasks/backlog/T7-59-Fix-Task-CRUD-Tests.md`
- `.anyt/tasks/backlog/T7-60-Fix-Visualization-Tests.md`
- `.anyt/tasks/backlog/T7-61-Fix-Project-and-Dependency-Tests.md`
- `.anyt/tasks/backlog/T7-62-Fix-Interactive-and-Preference-Tests.md`
- `.anyt/tasks/README.md` (updated with test fix sprint)
- `TEST_FIX_GUIDE.md` (comprehensive fixing guide)
- `TEST_FIX_TASKS_SUMMARY.md` (this file)

## Next Steps

1. Choose a task from the backlog (recommend T7-59 first)
2. Move task from `backlog/` to `active/`
3. Update Status to "In Progress"
4. Create new branch: `git checkout -b anyt{task-number}`
5. Follow the patterns in `TEST_FIX_GUIDE.md`
6. Run tests frequently: `PYTHONPATH=src uv run pytest path/to/test_file.py -v`
7. When done, run `make format && make lint && make typecheck && make test`
8. Commit changes and create PR with task ID in title
9. Move task to `done/` and update Status to "Completed"

Good luck! 🚀
