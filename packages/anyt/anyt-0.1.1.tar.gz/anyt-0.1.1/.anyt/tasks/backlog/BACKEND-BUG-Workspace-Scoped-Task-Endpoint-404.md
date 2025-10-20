# BACKEND BUG: Workspace-Scoped Task Endpoint Returns 404 for Valid Tasks

**Priority**: High
**Status**: Pending
**Component**: Backend API
**Created**: 2025-10-19

## Description

The workspace-scoped task retrieval endpoint `/v1/workspaces/{workspace_id}/tasks/{identifier}` returns a 404 error even when the task exists and is visible in the workspace.

## Environment

- **Backend API**: http://localhost:8000
- **Workspace ID**: 737
- **Workspace Identifier**: DE
- **Task Identifier**: DE-1

## Steps to Reproduce

1. Create a task in workspace with ID 737 (identifier: DE)
   - Task identifier: DE-1
   - Task title: "test"

2. Verify task exists using list endpoint:
   ```bash
   GET /v1/tasks?workspace_id=737
   ```
   **Result**: ✅ Task DE-1 appears in the list

3. Try to fetch task using workspace-scoped endpoint:
   ```bash
   GET /v1/workspaces/737/tasks/DE-1
   ```
   **Result**: ❌ 404 Not Found

4. Try to fetch task using non-workspace-scoped endpoint:
   ```bash
   GET /v1/tasks/DE-1
   ```
   **Result**: ✅ Task details returned successfully

## Expected Behavior

The workspace-scoped endpoint `/v1/workspaces/{workspace_id}/tasks/{identifier}` should return the task details when:
- The task exists
- The task belongs to the specified workspace
- The user has access to that workspace

## Actual Behavior

The endpoint returns a 404 error with the message:
```
Task 'DE-1' not found in workspace 737

Did you mean:
  DE-1  test
```

**Note**: The error message itself suggests "DE-1" as a match, which proves the task exists and the backend can find it - but the endpoint logic is failing to return it.

## Impact

- **CLI Workaround**: Changed `anyt task show` to use `/v1/tasks/{identifier}` instead
- **API Inconsistency**: Workspace-scoped endpoints should work for workspace isolation
- **Future Issues**: Other workspace-scoped operations may have similar bugs

## Technical Analysis

### Possible Root Causes

1. **Query/Filter Issue**: The endpoint might be using incorrect SQL query or ORM filters when looking up tasks within a workspace

2. **Identifier vs ID Confusion**: The backend might be expecting a numeric ID instead of the string identifier (e.g., expecting `1` instead of `DE-1`)

3. **Authorization/Scope Issue**: The workspace context might not be properly applied to the task lookup query

4. **Workspace Relationship**: The task-to-workspace relationship might not be properly joined in the query

### Suggested Investigation

1. Check the backend route handler for `/v1/workspaces/{workspace_id}/tasks/{identifier}`
2. Verify the ORM query is correctly joining tasks with workspace
3. Check if the identifier parameter is being parsed correctly (string vs int)
4. Compare with the working `/v1/tasks/{identifier}` endpoint to see the difference

## Acceptance Criteria

- [ ] `GET /v1/workspaces/737/tasks/DE-1` returns task details (not 404)
- [ ] Workspace-scoped endpoint properly validates task belongs to workspace
- [ ] Both numeric IDs and string identifiers work (e.g., `DE-1` and `1`)
- [ ] Error messages are accurate (don't suggest the task exists if returning 404)
- [ ] Existing `/v1/tasks/{identifier}` endpoint continues to work

## Code Reference (CLI Side)

**File**: `src/cli/client.py`
```python
async def get_task_by_workspace(
    self, workspace_id: int, identifier: str
) -> dict[str, Any]:
    """Get a task by identifier or ID within a specific workspace.

    This is the workspace-scoped version of get_task that explicitly
    specifies which workspace to query.

    Args:
        workspace_id: The workspace ID to query
        identifier: Task identifier (DEV-42) or ID

    Returns:
        Task details

    Raises:
        httpx.HTTPError: If the request fails.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            f"{self.base_url}/v1/workspaces/{workspace_id}/tasks/{identifier}",
            headers=self.headers,
            timeout=10.0,
        )
        response.raise_for_status()  # <-- This raises 404 for valid tasks
        data = response.json()

        # Handle SuccessResponse format
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
```

## Related Issues

- CLI Issue T7-44: Fixed by using `/v1/tasks/{identifier}` as workaround
- This affects any CLI command that needs workspace-scoped task access
- May affect web dashboard if it uses workspace-scoped endpoints

## Priority Justification

**High Priority** because:
- Breaks fundamental workspace isolation feature
- Forces CLI to use non-workspace-scoped endpoints
- Confusing error messages (suggests task exists but returns 404)
- Indicates potential architectural issue with workspace-scoped resources

## Workaround (CLI Side)

Currently using `/v1/tasks/{identifier}` instead of workspace-scoped endpoint.
This works but loses workspace validation benefits.
