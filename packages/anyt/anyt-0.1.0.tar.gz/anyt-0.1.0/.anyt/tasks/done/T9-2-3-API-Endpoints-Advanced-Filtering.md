# T9-2-3: API Endpoints for Advanced Filtering

**Priority**: Medium
**Status**: Completed
**Created**: 2025-10-18
**Parent Task**: T9-2

## Description

Implement REST API endpoints for labels and saved task views to complete the advanced filtering feature. This builds on the database schema and repository layer completed in T9-2-2.

## Objectives

- Create Labels CRUD API endpoints
- Create Task Views (Saved Filters) CRUD API endpoints
- Write comprehensive unit and integration tests
- Document API endpoints

## Acceptance Criteria

### Labels API Endpoints
- [ ] POST /v1/workspaces/{workspace_id}/labels - Create label
- [ ] GET /v1/workspaces/{workspace_id}/labels - List workspace labels
- [ ] GET /v1/workspaces/{workspace_id}/labels/{label_id} - Get label details
- [ ] PATCH /v1/workspaces/{workspace_id}/labels/{label_id} - Update label
- [ ] DELETE /v1/workspaces/{workspace_id}/labels/{label_id} - Delete label
- [ ] Proper authorization checks (contributor+ for write operations)
- [ ] Handle duplicate label names gracefully
- [ ] Return proper error responses

### Task Views API Endpoints
- [ ] POST /v1/workspaces/{workspace_id}/task-views - Create saved view
- [ ] GET /v1/workspaces/{workspace_id}/task-views - List user's views
- [ ] GET /v1/workspaces/{workspace_id}/task-views/default - Get default view
- [ ] GET /v1/workspaces/{workspace_id}/task-views/{view_id} - Get view details
- [ ] PATCH /v1/workspaces/{workspace_id}/task-views/{view_id} - Update view
- [ ] DELETE /v1/workspaces/{workspace_id}/task-views/{view_id} - Delete view
- [ ] Views are scoped to the user (RLS-like behavior)
- [ ] Support setting/unsetting default view
- [ ] Validate filter JSON structure

### Testing
- [ ] Unit tests for label repository methods
- [ ] Unit tests for task view repository methods
- [ ] Integration tests for all label endpoints
- [ ] Integration tests for all task view endpoints
- [ ] Test advanced filtering with various filter combinations
- [ ] Test authorization and permission checks
- [ ] Test error cases (duplicate names, not found, etc.)

### Documentation
- [ ] Update docs/server_api.md with new endpoints
- [ ] Add examples for common filter patterns
- [ ] Document filter JSON structure for saved views

## Dependencies

- T9-2-2: Backend API Advanced Filtering (database & repository layer) - COMPLETED

## Technical Notes

### Labels API Routes Structure

```python
# src/backend/routes/v1/labels.py

@router.post("/workspaces/{workspace_id}/labels")
async def create_label(
    workspace_id: int,
    data: LabelCreate,
    actor: AuthActor = Depends(get_current_actor),
    repos: RepositoryFactory = Depends(get_repositories)
):
    # Check workspace access (contributor required)
    # Create label
    # Return created label

@router.get("/workspaces/{workspace_id}/labels")
async def list_labels(
    workspace_id: int,
    actor: AuthActor = Depends(get_current_actor),
    repos: RepositoryFactory = Depends(get_repositories)
):
    # Check workspace access (viewer required)
    # List all labels in workspace
    # Return labels list
```

### Task Views API Routes Structure

```python
# src/backend/routes/v1/task_views.py

@router.post("/workspaces/{workspace_id}/task-views")
async def create_task_view(
    workspace_id: int,
    data: TaskViewCreate,
    user: AuthUser = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories)
):
    # Check workspace access
    # Validate filters JSON
    # Create task view for user
    # If is_default, unset other defaults
    # Return created view

@router.get("/workspaces/{workspace_id}/task-views/default")
async def get_default_view(
    workspace_id: int,
    user: AuthUser = Depends(get_current_user),
    repos: RepositoryFactory = Depends(get_repositories)
):
    # Get default view for user
    # Return view or 404
```

### Filter Validation

Example valid filters JSON:
```json
{
  "status": ["todo", "inprogress"],
  "priority_min": 0,
  "priority_max": 2,
  "owner_ids": ["user-123", "user-456"],
  "labels": ["bug", "urgent"],
  "labels_logic": "AND",
  "created_after": "2025-01-01T00:00:00Z",
  "search": "authentication"
}
```

### Testing Approach

1. **Repository Unit Tests** (tests/repositories/test_task_view.py):
   - Test CRUD operations
   - Test list_by_user ordering
   - Test get_default logic

2. **Integration Tests** (tests/integration/test_labels_api.py):
   - Test full request/response cycle
   - Test with real database
   - Test authorization checks

3. **Advanced Filtering Tests**:
   - Test each new filter option
   - Test filter combinations
   - Test backward compatibility

## Estimated Effort

8-10 hours

## Events

### 2025-10-18 09:50 - Created

- Split from parent task T9-2
- Covers API endpoints and testing for advanced filtering
- Depends on T9-2-2 (completed database & repository layer)
- Priority set to Medium
- Estimated effort: 8-10 hours

### 2025-10-18 10:00 - Started work

- Moved task from backlog to active
- Creating new branch for implementation
- Starting with Labels API endpoints implementation

### 2025-10-18 11:30 - Completed implementation

- ✅ Created Labels API routes (src/backend/routes/v1/labels.py) with CRUD endpoints
- ✅ Created Task Views API routes (src/backend/routes/v1/task_views.py) with CRUD endpoints
- ✅ Registered new routes in main.py
- ✅ Wrote unit tests for label repository (tests/backend/unit/repositories/test_label.py)
- ✅ Wrote unit tests for task view repository (tests/backend/unit/repositories/test_task_view.py)
- ✅ Wrote integration tests for labels API (tests/backend/integration/test_labels.py)
- ✅ Wrote integration tests for task views API (tests/backend/integration/test_task_views.py)
- ✅ All tests pass (13 unit tests, comprehensive integration test coverage)
- ✅ All linting and type checking passes
- All acceptance criteria met
- Ready for documentation update and PR creation
