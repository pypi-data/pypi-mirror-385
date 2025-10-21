# T7-64: Fix Whoami Test

**Priority**: High
**Status**: Completed
**Phase**: 7
**PR**: https://github.com/supercarl87/AnyTaskCLI/pull/47

## Description

Fix failing `test_auth_token_validation_on_whoami` test by updating it to use Pydantic Workspace models instead of raw dictionaries.

## Objectives

- Fix test to use `create_test_workspace()` helper instead of dict mocks
- Ensure test passes with typed API clients
- Maintain test coverage for whoami command authentication status display

## Acceptance Criteria

- [x] Test uses `create_test_workspace()` helper from conftest
- [x] Test passes successfully
- [x] All other unit tests still pass
- [x] Code follows project style guidelines

## Dependencies

None

## Estimated Effort

15 minutes

## Technical Notes

The test was failing because it was mocking `list_workspaces()` to return a list of dicts:
```python
mock_list.return_value = [
    {"id": 1, "identifier": "DEV", "name": "Development"}
]
```

But the actual `WorkspacesAPIClient.list_workspaces()` returns `list[Workspace]`, and the whoami command expects Workspace objects with `.name` and `.identifier` attributes.

**Fix Applied:**
```python
from tests.cli.unit.conftest import create_test_workspace

# In test:
mock_list.return_value = [
    create_test_workspace(id=1, identifier="DEV", name="Development")
]
```

This aligns with the architecture migration completed in T7-56 where we moved from dict-based responses to typed Pydantic models.

## Files Modified

- `tests/cli/unit/test_core_commands.py`
  - Added import for `create_test_workspace`
  - Updated mock return value to use Workspace object

## Events

### 2025-10-20 22:50 - Task started
- Created task and began investigation
- Identified root cause: test using dict instead of Pydantic model
- Applied fix using `create_test_workspace()` helper
- Test now passes successfully

### 2025-10-20 23:00 - Task completed
- All unit tests passing (214 tests)
- Code quality checks passed (format, lint, typecheck)
- Committed changes and created PR #47
- Task moved to done/
