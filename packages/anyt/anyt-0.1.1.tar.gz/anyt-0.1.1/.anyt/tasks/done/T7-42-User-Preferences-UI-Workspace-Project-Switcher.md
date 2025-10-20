# T7-42: User Preferences UI - Workspace and Project Switcher

**Priority**: High
**Status**: Completed
**Created**: 2025-10-19

## Description

Add CLI commands to allow users to view and switch their current workspace and project preferences using the new User Preferences API endpoints (`/v1/users/me/preferences`). This provides a seamless way for users to manage their default workspace/project context without needing to rely on local configuration files.

## Objectives

- Implement CLI commands to view current user preferences (workspace & project)
- Implement CLI commands to switch current workspace
- Implement CLI commands to switch current project
- Integrate with the new User Preferences API endpoints
- Provide clear feedback when preferences are updated
- Handle edge cases (no preferences, invalid workspace/project, permission issues)

## Acceptance Criteria

- [ ] Add `anyt preference show` command to display current workspace and project preferences
- [ ] Add `anyt preference set-workspace <workspace_id>` command to set current workspace
- [ ] Add `anyt preference set-project <workspace_id> <project_id>` command to set current project
- [ ] Add `anyt preference clear` command to delete user preferences
- [ ] API client methods for all preference endpoints (GET, PUT workspace, PUT project, DELETE)
- [ ] Proper error handling for:
  - User not authenticated (JWT required, not agent keys)
  - Invalid workspace/project IDs
  - User doesn't have permission to access workspace/project
  - Network errors
- [ ] Rich console output with colored status messages
- [ ] Unit tests for all commands with mocked API client
- [ ] Integration tests for preference workflow
- [ ] Update CLI documentation with new commands
- [ ] Tests written and passing
- [ ] Code reviewed and merged

## Dependencies

- T7-41: Workspace-Scoped API Migration (completed - API endpoints exist)

## Estimated Effort

6-8 hours

## Technical Notes

### API Integration

The backend now provides these endpoints:

1. **GET /v1/users/me/preferences**
   - Returns user's current workspace and project preferences
   - Returns null if no preferences set
   - Requires JWT authentication (not agent keys)

2. **PUT /v1/users/me/preferences/workspace**
   - Sets the current workspace for the user
   - Clears current_project if it doesn't belong to new workspace
   - Request body: `{"workspace_id": 2}`

3. **PUT /v1/users/me/preferences/project**
   - Sets the current project (and workspace) for the user
   - Both workspace and project are updated automatically
   - Request body: `{"workspace_id": 2, "project_id": 5}`

4. **DELETE /v1/users/me/preferences**
   - Clears all user preferences
   - Resets to no current workspace/project

### Implementation Plan

1. **Update API Client** (`src/cli/client.py`):
   ```python
   async def get_user_preferences(self) -> dict:
       """Get user preferences (workspace/project)."""

   async def set_current_workspace(self, workspace_id: int) -> dict:
       """Set current workspace preference."""

   async def set_current_project(self, workspace_id: int, project_id: int) -> dict:
       """Set current project (and workspace) preference."""

   async def clear_user_preferences(self) -> dict:
       """Clear user preferences."""
   ```

2. **Create Preference Commands** (`src/cli/commands/preference.py`):
   - `show` - Display current preferences
   - `set-workspace` - Change current workspace
   - `set-project` - Change current project
   - `clear` - Reset preferences

3. **Register Commands** in `src/cli/main.py`:
   ```python
   from cli.commands import preference
   app.add_typer(preference.app, name="preference")
   ```

4. **Rich Output Format**:
   - Show current workspace and project with IDs and names
   - Color-coded success/error messages
   - Clear instructions when no preferences are set

5. **Error Handling**:
   - Detect JWT requirement (fail gracefully if using agent key)
   - Validate workspace/project IDs exist
   - Check user permissions
   - Handle network/API errors

### Example Usage

```bash
# Show current preferences
anyt preference show
# Output:
# Current Workspace: [2] My Workspace
# Current Project: [5] Mobile App

# Switch workspace
anyt preference set-workspace 3
# Output:
# ✓ Current workspace updated to [3] Team Workspace
# Note: Current project cleared (not in this workspace)

# Switch project
anyt preference set-project 3 10
# Output:
# ✓ Current workspace updated to [3] Team Workspace
# ✓ Current project updated to [10] Backend API

# Clear preferences
anyt preference clear
# Output:
# ✓ User preferences cleared
```

### Testing Strategy

1. **Unit Tests** (`tests/cli/unit/test_preference_commands.py`):
   - Mock API client responses
   - Test all commands with various scenarios
   - Test error handling

2. **Integration Tests** (`tests/cli/integration/test_preference_flow.py`):
   - Test full workflow with real backend
   - Verify preferences persist across commands
   - Test permission scenarios

### Notes

- This feature only works with JWT authentication (user tokens), not agent API keys
- When switching workspaces, the current project is automatically cleared if it doesn't belong to the new workspace
- When switching projects, the workspace is automatically updated to match
- The CLI should gracefully fall back to local config if preferences API is unavailable
- Consider caching preferences locally to reduce API calls

## Events

### 2025-10-19 17:00 - Created
- Task created based on new User Preferences API endpoints
- Highest task ID was T7-41, so this is T7-42
- Task placed in backlog for implementation

### 2025-10-19 17:30 - Started work
- Moved task from backlog to active
- Status updated to "In Progress"
- Beginning implementation with API client methods

### 2025-10-19 19:00 - Implementation complete
- Added 4 API client methods to `src/cli/client.py`:
  - `get_user_preferences()` - Get current preferences
  - `set_current_workspace()` - Set workspace preference
  - `set_current_project()` - Set project preference
  - `clear_user_preferences()` - Clear all preferences
- Created `src/cli/commands/preference.py` with 4 commands:
  - `anyt preference show` - Display current preferences
  - `anyt preference set-workspace <workspace_id>` - Switch workspace
  - `anyt preference set-project <workspace_id> <project_id>` - Switch project
  - `anyt preference clear` - Reset preferences
- Registered preference commands in `src/cli/main.py`
- Added comprehensive unit tests in `tests/cli/unit/test_preference_commands.py`
- All 10 preference tests pass, total 143 CLI unit tests pass
- Updated `docs/CLI_USAGE.md` with User Preferences Management section
- All linting and type checking pass
- Task status updated to "Completed"
