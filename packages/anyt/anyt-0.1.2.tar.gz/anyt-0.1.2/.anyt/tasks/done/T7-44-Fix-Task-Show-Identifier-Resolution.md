# T7-44: Fix Task Show Command Identifier Resolution

**Priority**: High
**Status**: Completed
**Created**: 2025-10-19
**Completed**: 2025-10-19

## Description

The `anyt task show` command is not working correctly when users provide partial task identifiers (e.g., just the numeric part like "9" instead of "DEV-9"). The command fails to resolve the task even though the task exists in the workspace.

### Current Behavior
```
uv run anyt task show 9
✗ Error: Task '9' not found in workspace 1
```

But when the user does `anyt task pick 9`, it works correctly:
```
uv run anyt task pick 9
✓ Picked DEV-9 (Create deployment guide)
```

Then trying to show it still fails:
```
uv run anyt task show
✗ Error: Task 'DEV-9' not found in workspace 1
```

## Root Cause

The `normalize_identifier` function in `src/cli/commands/task/helpers.py` has a `workspace_prefix` parameter that allows prepending the workspace identifier (e.g., "DEV-") to partial identifiers, but:

1. The `show_task` function in `src/cli/commands/task/crud.py` (line 238) calls `normalize_identifier(identifier)` without passing the `workspace_prefix` parameter
2. When a user provides just a number like "9", it returns "9" instead of "DEV-9"
3. The API endpoint `/v1/workspaces/{workspace_id}/tasks/{identifier}` then tries to look up task ID 9 (numeric) instead of identifier "DEV-9"

## Objectives

- Fix the `show_task` command to properly resolve partial identifiers by prepending the workspace prefix
- Ensure consistency across all task commands (show, edit, done, rm, etc.)
- Maintain backward compatibility with full identifiers like "DEV-9"

## Acceptance Criteria

- [x] `anyt task show 9` resolves to "DEV-9" when in workspace with identifier "DEV"
- [x] `anyt task show DEV-9` continues to work (full identifier)
- [x] `anyt task show` (without args) uses active task and resolves correctly
- [x] The fix is applied consistently to all task CRUD commands (show, edit, done, rm)
- [x] Tests are updated to cover partial identifier resolution
- [x] Bug is verified fixed with the provided test case

## Dependencies

None

## Estimated Effort

2-3 hours

## Technical Notes

### Files to Modify

1. **src/cli/commands/task/crud.py**
   - `show_task` function (line 238): Pass `workspace_prefix` to `normalize_identifier`
   - `edit_task` function: Same fix if needed
   - `mark_done` function: Same fix if needed
   - `remove_task` function: Same fix if needed
   - Need to extract workspace_identifier from config before calling normalize_identifier

2. **src/cli/commands/task/helpers.py**
   - Review `normalize_identifier` function logic
   - Ensure it correctly handles the case where just a number is provided with a workspace_prefix

### Implementation Strategy

1. In each CRUD function that calls `normalize_identifier`, get the workspace identifier first:
   ```python
   # After loading ws_config
   workspace_identifier = ws_config.workspace_identifier

   # When normalizing
   normalized_id = normalize_identifier(identifier, workspace_identifier)
   ```

2. Update the `normalize_identifier` function if needed to handle the case where:
   - `task_id` is just a number (e.g., "9")
   - `workspace_prefix` is provided (e.g., "DEV")
   - Should return "DEV-9"

   Current logic at line 239:
   ```python
   if task_id.isdigit():
       return task_id  # BUG: Should prepend workspace_prefix if provided
   ```

   Should be:
   ```python
   if task_id.isdigit():
       if workspace_prefix:
           return f"{workspace_prefix}-{task_id}"
       return task_id
   ```

3. Test the fix with the provided test cases

### Test Cases to Verify

```bash
# Setup
uv run anyt task pick 9  # Should work

# Test partial identifier
uv run anyt task show 9  # Should resolve to DEV-9 and display task

# Test full identifier
uv run anyt task show DEV-9  # Should continue to work

# Test active task
uv run anyt task show  # Should use active task and display

# Test other commands
uv run anyt task edit 9 --status "in progress"
uv run anyt task done 9
uv run anyt task rm 9 --force
```

## Events

### 2025-10-19 - Created
- Task created based on user-reported bug
- Bug identified: `normalize_identifier` not receiving workspace_prefix parameter
- Root cause: CRUD commands not passing workspace_identifier when normalizing

### 2025-10-19 - Implementation Completed
- Fixed `normalize_identifier` function in `src/cli/commands/task/helpers.py`:
  - Added logic to prepend workspace_prefix when task_id is numeric
  - Line 239-242: Added conditional check for workspace_prefix parameter
- Updated all CRUD commands in `src/cli/commands/task/crud.py`:
  - `show_task`: Moved normalization inside async function to access workspace_identifier
  - `edit_task`: Added workspace_identifier extraction and passed to normalize_identifier
  - `mark_done`: Added workspace_identifier extraction and passed to normalize_identifier
  - `remove_task`: Added workspace_identifier extraction and passed to normalize_identifier
- Updated CLI version to 0.1.1 in `pyproject.toml`
- Updated `CHANGELOG.md` with bug fix details
- All unit tests pass:
  - `normalize_identifier("9", "DEV")` → "DEV-9" ✓
  - `normalize_identifier("DEV-9", "DEV")` → "DEV-9" ✓
  - `normalize_identifier("dev-9", "DEV")` → "DEV-9" ✓
  - `normalize_identifier("dev42", "DEV")` → "DEV-42" ✓
- Linting and type checking pass successfully

### 2025-10-19 - Additional Fix: API Endpoint Compatibility
- Discovered `show_task` was using `client.get_task_by_workspace()` which calls `/v1/workspaces/{id}/tasks/{identifier}`
- This workspace-scoped endpoint has backend issues and returns 404 even for valid tasks
- Changed to use `client.get_task()` which calls `/v1/tasks/{identifier}` (consistent with other CRUD commands)
- Line 248 in `src/cli/commands/task/crud.py`: Changed from `get_task_by_workspace` to `get_task`
- Verified fix works:
  - `anyt task show DE-1` → Shows task details ✓
  - `anyt task show 1` → Resolves to DE-1 and shows details ✓
- Updated CHANGELOG.md with additional fix details
