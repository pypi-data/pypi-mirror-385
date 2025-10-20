# T4-5: User Setup Route

**Priority**: Medium
**Status**: Completed
**Created**: 2025-10-16

## Description

Implement a user setup route that automatically creates default resources for new users on their first login or setup. The route should create:
1. A personal workspace with the user's identifier
2. A default project within that workspace
3. Proper workspace membership for the user

The route must be idempotent - if the user has already been set up (workspace and project exist), it should have no effect and return success.

## Objectives

- Create a `/v1/users/setup` endpoint for user onboarding
- Automatically create a personal workspace for the user (e.g., "USER123" or based on username)
- Create a default project within the workspace (e.g., "Personal Tasks" or "Default Project")
- Add the user as an admin member of the workspace
- Ensure idempotency - repeated calls should not create duplicates
- Return information about the created or existing workspace and project

## Acceptance Criteria

- [ ] POST `/v1/users/setup` endpoint implemented in `src/backend/routes/v1/`
- [ ] Endpoint requires user authentication (JWT token)
- [ ] Endpoint checks if user already has a personal workspace
- [ ] If workspace doesn't exist:
  - [ ] Creates workspace with unique identifier (e.g., user ID or username-based)
  - [ ] Creates default project within workspace
  - [ ] Adds user as workspace admin member
- [ ] If workspace exists, returns existing workspace and project info
- [ ] Response includes workspace ID, workspace identifier, project ID, and project name
- [ ] Proper error handling for database failures
- [ ] Transaction ensures atomicity (workspace + project + membership created together or not at all)
- [ ] Unit tests for setup logic
- [ ] Integration tests for endpoint
- [ ] Tests cover idempotency (calling setup multiple times)
- [ ] Code passes `make lint`, `make format`, `make typecheck`
- [ ] Documentation updated in API docs

## Dependencies

- T2-6: Project Repository Implementation (completed)
- T2-8: Workspace Repository Implementation (completed)
- T2-9: Complete Repository Migration (completed)

## Estimated Effort

4-6 hours

## Technical Notes

### Implementation Approach

1. **Route Location**: `src/backend/routes/v1/users.py` (create new file)
   - Or add to existing users route file if it exists

2. **Repository Usage**:
   - Use `repos.workspaces` to check/create workspace
   - Use `repos.projects` to create default project
   - Use `repos.workspace_members` to add user membership

3. **Workspace Naming Strategy**:
   - Option 1: Use user ID as workspace identifier (e.g., "USER-{user_id}")
   - Option 2: Use username/email prefix if available
   - Option 3: Generate unique identifier like "personal-{uuid}"
   - Ensure uniqueness and handle collisions

4. **Idempotency Check**:
   ```python
   # Check if user already has a personal workspace
   existing_workspaces = await repos.workspaces.get_by_user_id(user_id)
   personal_workspace = find_personal_workspace(existing_workspaces)

   if personal_workspace:
       # Return existing setup
       return SuccessResponse(...)
   ```

5. **Transaction Pattern**:
   ```python
   async with db.begin():
       workspace = await repos.workspaces.create(...)
       project = await repos.projects.create(...)
       membership = await repos.workspace_members.create(...)
   ```

6. **Response Format**:
   ```json
   {
     "success": true,
     "data": {
       "workspace": {
         "id": 1,
         "identifier": "USER-123",
         "name": "Personal Workspace"
       },
       "project": {
         "id": 1,
         "name": "Default Project",
         "identifier": "USER-1"
       },
       "is_new_setup": true
     }
   }
   ```

### Testing Considerations

- Test first-time setup (creates resources)
- Test repeated setup calls (idempotent behavior)
- Test concurrent setup calls (race conditions)
- Test with different user IDs
- Test database transaction rollback on failure
- Test with missing authentication

### Edge Cases

- User with existing workspaces (identify which is "personal")
- Workspace identifier collision (handle gracefully)
- Database connection failures during setup
- Partial creation (workspace created but project fails)

## Events

### 2025-10-16 09:00 - Created
- Task created based on user request for user setup route
- Placed in backlog for Phase 4 (Agent Integration)

### 2025-10-16 09:05 - Started work
- Moved task from backlog to active
- Beginning implementation of user setup route
- Plan: Create endpoint, implement idempotency checks, add tests

### 2025-10-16 10:30 - Completed
- ✅ POST `/v1/users/setup` endpoint implemented in `src/backend/routes/v1/users.py`
- ✅ Endpoint requires user authentication (JWT token)
- ✅ Idempotency check: returns existing workspace if user already has one
- ✅ Creates workspace with unique identifier using hash-based approach (only letters A-Z)
- ✅ Creates default project within workspace
- ✅ Adds user as workspace admin member
- ✅ Proper error handling and transaction support
- ✅ UserSetupResponse model added to API models
- ✅ Router registered in v1 routes
- ✅ 7 comprehensive unit tests written covering:
  - First-time setup
  - Idempotency (repeated calls)
  - Existing workspace handling
  - Authentication requirement
  - Membership creation
  - Unique identifier generation
  - Edge case: workspace without project
- ✅ All tests passing (7/7)
- ✅ Code passes make lint, make format, make typecheck
- Task moved to done/

### 2025-10-16 10:35 - Pull Request Created
- PR #32: https://github.com/supercarl87/AnyTaskBackend/pull/32
- All quality checks passing
- Ready for review
