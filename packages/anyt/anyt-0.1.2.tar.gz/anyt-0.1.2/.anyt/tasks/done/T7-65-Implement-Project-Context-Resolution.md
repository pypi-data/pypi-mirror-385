# T7-65: Implement Project Context Resolution

**Priority**: Medium
**Status**: Completed
**Phase**: 7
**PR**: https://github.com/supercarl87/AnyTaskCLI/pull/48

## Description

Implement the `get_project_id()` method in `ServiceContext` class to resolve the current project ID from workspace configuration. The `.anyt/anyt.json` file already contains a `current_project_id` field, but the ServiceContext is not reading it (returns None instead).

## Objectives

- Read `current_project_id` from `.anyt/anyt.json` workspace config
- Implement proper fallback logic if workspace config doesn't exist
- Maintain compatibility with existing code
- Add proper error handling

## Acceptance Criteria

- [ ] `ServiceContext.get_project_id()` reads from `.anyt/anyt.json`
- [ ] Method returns `current_project_id` as int if available
- [ ] Method returns None if workspace config doesn't exist
- [ ] Method returns None if `current_project_id` is not set
- [ ] Remove TODO comment from context.py:78
- [ ] Add unit tests for project context resolution
- [ ] Code passes linting and type checking
- [ ] All existing tests still pass

## Dependencies

None

## Estimated Effort

1-2 hours

## Technical Notes

**Current Implementation** (src/cli/services/context.py:67-80):
```python
def get_project_id(self) -> int | None:
    """Get project ID from config/context.

    Future implementation will check:
    1. .anyt/anyt.json workspace config for default project
    2. Global config for default project
    3. None if not configured

    Returns:
        Project ID if available, None otherwise
    """
    # TODO: Implement project context resolution
    # For now, return None
    return None
```

**Workspace Config Format** (.anyt/anyt.json):
```json
{
  "workspace_id": "2083",
  "name": "Development Workspace",
  "api_url": "http://localhost:8000",
  "last_sync": "2025-10-20 20:05:49",
  "current_project_id": 1361,
  "workspace_identifier": "DEV",
  "agent_key": "anyt_agent_..."
}
```

**Implementation Plan:**

1. Check if workspace config exists (use GlobalConfig or WorkspaceConfig model)
2. Read `current_project_id` from workspace config
3. Return as int if available, None otherwise
4. Handle file not found, JSON parsing errors gracefully

**Example Implementation:**
```python
def get_project_id(self) -> int | None:
    """Get project ID from config/context.

    Resolution order:
    1. .anyt/anyt.json workspace config for current_project_id
    2. Global config for default project (future)
    3. None if not configured

    Returns:
        Project ID if available, None otherwise
    """
    from pathlib import Path
    import json

    # Try to read from workspace config
    workspace_config_path = Path.cwd() / ".anyt" / "anyt.json"
    if workspace_config_path.exists():
        try:
            with open(workspace_config_path) as f:
                config = json.load(f)
                project_id = config.get("current_project_id")
                if project_id:
                    return int(project_id)
        except (json.JSONDecodeError, ValueError, OSError):
            pass

    # Future: Check global config for default project

    return None
```

**Files to Modify:**
- `src/cli/services/context.py` - Implement get_project_id()
- `tests/cli/unit/services/test_context_service.py` - Add tests (create if doesn't exist)

**Testing Plan:**
- Test with valid workspace config containing current_project_id
- Test with workspace config missing current_project_id
- Test with no workspace config file
- Test with invalid JSON in workspace config
- Test with non-integer current_project_id value

## Events

### 2025-10-20 23:00 - Task created and started
- Identified TODO at context.py:78 that needs implementation
- Found that .anyt/anyt.json already has current_project_id field
- Created task T7-65 in active/ directory
- Ready to begin implementation

### 2025-10-20 23:30 - Implementation completed
- Implemented `get_project_id()` method in ServiceContext
- Added 13 comprehensive unit tests for ServiceContext
- All tests passing (224 passed, 2 skipped)
- Code passes linting, formatting, and type checking
- Created PR #48
- Task completed successfully
