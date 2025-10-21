# T7-51: Refactor Workspace and Project APIs

**Priority**: High
**Status**: Completed
**Created**: 2025-10-20
**Parent**: T7-48 (CLI Architecture Improvements)

## Description

Create `WorkspacesAPIClient` and `ProjectsAPIClient` following the pattern established in T7-50. These clients provide strongly-typed operations for workspace and project management.

## Objectives

- Implement WorkspacesAPIClient with all workspace operations
- Implement ProjectsAPIClient with all project operations
- Follow BaseAPIClient pattern established in T7-50
- Maintain backward compatibility

## Acceptance Criteria

- [x] Create `src/cli/client/workspaces.py`:
  - [x] `list_workspaces() -> list[Workspace]`
  - [x] `get_workspace(workspace_id: str) -> Workspace`
  - [x] `get_current_workspace() -> Workspace`
  - [x] `create_workspace(workspace: WorkspaceCreate) -> Workspace`
- [x] Create `src/cli/client/projects.py`:
  - [x] `list_projects(workspace_id: int) -> list[Project]`
  - [x] `create_project(workspace_id: int, project: ProjectCreate) -> Project`
  - [x] `get_current_project(workspace_id: int) -> Project`
- [x] Create `src/cli/client/preferences.py`:
  - [x] `get_user_preferences() -> UserPreferences`
  - [x] `set_current_workspace(workspace_id: int) -> UserPreferences`
  - [x] `set_current_project(workspace_id: int, project_id: int) -> UserPreferences`
  - [x] `clear_user_preferences() -> None`
- [x] All methods return typed models
- [x] Type checking passes: `make typecheck`
- [x] Unit tests for WorkspacesAPIClient
- [x] Unit tests for ProjectsAPIClient
- [x] Unit tests for PreferencesAPIClient
- [x] Old client.py remains untouched

## Dependencies

- T7-49: Models and Schemas Foundation
- T7-50: Refactor BaseClient and Tasks API

## Estimated Effort

3-4 hours

## Technical Notes

### Implementation Pattern

Follow the same pattern as TasksAPIClient:

```python
# client/workspaces.py
from cli.client.base import BaseAPIClient
from cli.models.workspace import Workspace, WorkspaceCreate

class WorkspacesAPIClient(BaseAPIClient):
    """API client for workspace operations."""

    async def list_workspaces(self) -> list[Workspace]:
        """List accessible workspaces."""
        response = await self.get("/v1/workspaces")
        data = self._unwrap_response(response)
        return [Workspace(**ws) for ws in data]

    async def get_workspace(self, workspace_id: str) -> Workspace:
        """Get workspace by ID."""
        response = await self.get(f"/v1/workspaces/{workspace_id}")
        data = self._unwrap_response(response)
        return Workspace(**data)

    # ... other methods
```

### Testing Strategy

- Mock HTTP responses for all methods
- Validate model instantiation
- Test error cases (not found, unauthorized)
- No integration tests needed

## Events

### 2025-10-20 15:55 - Created
- Broken out from T7-48
- Continues client refactoring pattern

### 2025-10-20 16:30 - Started work
- Moved task from backlog to active
- Updated status to In Progress
- Dependencies satisfied: T7-49 ✅, T7-50 ✅
- Beginning implementation of WorkspacesAPIClient, ProjectsAPIClient, and PreferencesAPIClient

### 2025-10-20 17:15 - Implementation completed
- ✅ Created WorkspacesAPIClient with 4 methods (list, get, get_current, create)
- ✅ Created ProjectsAPIClient with 3 methods (list, create, get_current)
- ✅ Created PreferencesAPIClient with 4 methods (get, set_workspace, set_project, clear)
- ✅ Updated client/__init__.py to export new clients
- ✅ Created comprehensive unit tests for all 3 clients
  - test_workspaces.py: 6 tests
  - test_projects.py: 5 tests
  - test_preferences.py: 6 tests
- ✅ Type checking passes (mypy --strict)
- ✅ All 208 unit tests pass
- ✅ Backward compatibility maintained (old_client.py untouched)
- Task completed successfully

### 2025-10-20 17:20 - PR created
- Created pull request: https://github.com/supercarl87/AnyTaskCLI/pull/31
- PR title: [T7-51] Refactor Workspace and Project APIs
- Ready for review
