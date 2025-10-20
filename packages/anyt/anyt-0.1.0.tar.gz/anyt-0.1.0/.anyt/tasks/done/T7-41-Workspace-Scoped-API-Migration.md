# T7-41: Workspace-Scoped API Migration

**Priority**: Medium
**Status**: Completed
**Created**: 2025-10-18

## Description

Update CLI to use workspace-scoped API endpoints when the backend is ready. Currently, there's a TODO comment in `task/crud.py` indicating the CLI needs to be updated to support workspace-scoped task operations.

## Objectives

- Update `anyt task show` to use workspace-scoped API when `--workspace` flag is provided
- Ensure proper workspace context resolution
- Support cross-workspace task queries
- Maintain backward compatibility with current workspace

## Acceptance Criteria

- [x] `anyt task show DEV-42 --workspace PROJ` queries correct workspace
- [x] Backend API endpoint supports workspace-scoped queries (GET /v1/workspaces/{workspace_id}/tasks/{identifier})
- [x] CLI resolves workspace identifier to workspace ID (via resolve_workspace_context)
- [x] Error handling for invalid workspace identifiers (implemented in resolve_workspace_context)
- [x] Cache workspace resolution to avoid repeated API calls (5-minute TTL implemented)
- [x] Tests written for workspace resolution logic (2 new tests added)
- [x] Documentation updated with workspace flag usage (docs/CLI_USAGE.md:399-415)
- [x] Backward compatibility maintained (no --workspace uses current workspace via Priority 3 fallback)

## Dependencies

- T7-35: Workspace-Scoped Task Identifiers (completed ✅)
- Backend API must support workspace-scoped task queries

## Estimated Effort

3-4 hours

## Technical Notes

### Current TODO to Address

From `src/cli/commands/task/crud.py`:
```python
# Line ~250: TODO: Update to use workspace-scoped API when backend is ready
```

### Implementation Steps

1. **Update `show_task` function**:
   ```python
   async def fetch_task(client, identifier, workspace_id=None):
       if workspace_id:
           # Use workspace-scoped endpoint
           return await client.get_task_by_workspace(
               identifier=identifier,
               workspace_id=workspace_id
           )
       else:
           # Use current workspace
           return await client.get_task(identifier)
   ```

2. **Workspace Resolution**:
   ```python
   async def resolve_workspace_id(client, workspace_identifier: str) -> int:
       """Resolve workspace identifier/ID to workspace ID."""
       # Check if it's already a numeric ID
       if workspace_identifier.isdigit():
           return int(workspace_identifier)

       # Otherwise treat as identifier and fetch workspace
       workspaces = await client.list_workspaces()
       for ws in workspaces:
           if ws.get("identifier") == workspace_identifier.upper():
               return ws["id"]

       raise ValueError(f"Workspace '{workspace_identifier}' not found")
   ```

3. **Add Caching**:
   - Cache workspace ID lookups in memory
   - Expire cache after 5 minutes
   - Clear cache on workspace switch

4. **Backend API Endpoint** (verify this exists):
   ```
   GET /v1/workspaces/{workspace_id}/tasks/{identifier}
   ```

5. **Update Other Commands**:
   - Check if `task edit`, `task done`, `task rm` also need workspace flag
   - Apply same pattern consistently

### Error Handling

```python
try:
    workspace_id = await resolve_workspace_id(client, workspace)
except ValueError as e:
    console.print(f"[red]Error:[/red] {e}")
    console.print("\nAvailable workspaces:")
    # Show list of workspaces
    raise typer.Exit(1)
```

### Testing Strategy

- Unit tests for workspace resolution
- Test with numeric ID vs identifier
- Test error cases (invalid workspace)
- Integration test with actual backend
- Test caching behavior

## Events

### 2025-10-18 16:10 - Created
- Task created based on TODO in `src/cli/commands/task/crud.py`
- Depends on T7-35 (already completed)
- Prioritized as Medium (useful for multi-workspace workflows)

### 2025-10-18 22:25 - Started work
- Moved task from backlog to active
- Updated status to "In Progress"
- Beginning implementation of workspace-scoped API migration
- Will start by examining current implementation and backend API status

### 2025-10-18 22:45 - Implementation completed
- Added new `get_task_by_workspace(workspace_id, identifier)` method to APIClient (src/cli/client.py:354-384)
- Updated `show_task` command to use workspace-scoped API endpoint (src/cli/commands/task/crud.py:247-249)
- Implemented workspace resolution caching with 5-minute TTL (src/cli/commands/task/helpers.py:14-27)
- Added `clear_workspace_cache()` utility function for cache management
- Updated `resolve_workspace_context` to use cache for workspace lookups
- Wrote comprehensive unit tests for workspace-scoped API (tests/cli/unit/api_client/test_tasks.py:99-146)
- All tests passing (15/15 in test_tasks.py)
- Linting passed with ruff
- Ready for final acceptance criteria verification

### 2025-10-18 23:00 - Task completed
- All acceptance criteria verified and marked complete
- Updated documentation with workspace resolution details (docs/CLI_USAGE.md:399-415)
- Added examples for workspace-scoped queries
- Documented workspace resolution priority order and caching behavior
- Task status updated to "Completed"
- Ready to move to done/ directory
