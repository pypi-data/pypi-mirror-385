# Workspace-Scoped Task Identifiers (CLI Implementation)

This document describes the CLI-side implementation of workspace-scoped task identifiers for T7-35.

## Overview

This implementation prepares the AnyTask CLI for workspace-scoped task identifiers. The changes allow users to specify workspace context for task operations while maintaining backward compatibility until the backend API is updated.

## What's Implemented

### 1. Workspace Selection Commands

#### `anyt workspace use WORKSPACE`
Set the current workspace for the active environment. This workspace will be used as the default for all task operations when no explicit `--workspace` flag is provided.

```bash
# Set DEV as the current workspace
anyt workspace use DEV

# Set workspace by ID
anyt workspace use 1
```

The current workspace is stored in `~/.config/anyt/config.json` under the environment's `default_workspace` field.

#### `anyt workspace current`
Show the current workspace for the active environment.

```bash
anyt workspace current
# Output:
# Environment: prod
# Current workspace: Development (DEV)
# Workspace ID: 1
```

### 2. Workspace Context Resolution

Added `resolve_workspace_context()` helper function that resolves workspace context with the following priority:

1. **Explicit `--workspace` flag** (highest priority)
   ```bash
   anyt task show DEV-123 --workspace STAGING
   ```

2. **Environment's default workspace** (from config)
   ```bash
   # If you've run: anyt workspace use DEV
   anyt task show DEV-123  # Uses DEV workspace
   ```

3. **Local `.anyt/anyt.json` workspace** (lowest priority)
   ```bash
   # If current directory has .anyt/anyt.json
   anyt task show DEV-123  # Uses workspace from anyt.json
   ```

### 3. Task Commands with Workspace Support

#### `anyt task show`
Updated to accept `--workspace/-w` flag:

```bash
# Use current workspace
anyt task show DEV-123

# Specify workspace explicitly
anyt task show DEV-123 --workspace STAGING
anyt task show DEV-123 -w STAGING
```

**Pattern for other commands**: The same pattern can be applied to other task commands (`add`, `edit`, `done`, `list`, etc.) by:
1. Adding `--workspace/-w` parameter
2. Using `resolve_workspace_context()` to get workspace ID
3. Passing workspace context to API client (when backend is ready)

## Configuration Changes

### Environment Configuration
The `EnvironmentConfig` in `config.py` already had a `default_workspace` field that was previously unused. It's now utilized to store the user's workspace preference per environment:

```json
{
  "environments": {
    "prod": {
      "api_url": "http://anyt.up.railway.app",
      "auth_token": "...",
      "default_workspace": "DEV"
    }
  },
  "current_environment": "prod"
}
```

## What's NOT Yet Implemented

### Backend API Changes Required

The following backend changes are **prerequisites** before this feature is fully functional:

1. **Database Schema Migration** (Backend Repository)
   - Remove unique constraint on `workspaces.identifier`
   - Add composite unique constraint `(workspace_id, identifier)` on tasks table
   - Update indexes

2. **API Route Updates** (Backend Repository)
   - Change task lookup endpoints to require workspace context:
     - Old: `GET /v1/tasks/{identifier}`
     - New: `GET /v1/workspaces/{workspace_id}/tasks/{identifier}`
     - Or: `GET /v1/tasks/{identifier}?workspace_id={id}`
   - Update all task CRUD endpoints
   - Add backward compatibility layer with deprecation warnings

3. **API Client Updates** (This Repository - After Backend Changes)
   - Update `client.get_task()` to accept workspace_id parameter
   - Update all task operation methods to include workspace context
   - Update request URLs to use new workspace-scoped endpoints

### Other Task Commands

Only `anyt task show` has been updated with `--workspace` support as a reference implementation. The following commands should be updated using the same pattern:

- `anyt task add`
- `anyt task edit`
- `anyt task done`
- `anyt task rm`
- `anyt task list`
- `anyt task dep add/rm/list`
- `anyt task pick`

### Tests

Test coverage needs to be added for:
- Workspace use/current commands
- Workspace context resolution logic
- Task commands with --workspace flag
- Error handling when workspace not found

## Migration Path for Users

### Before Backend Changes

Users can start using the new workspace commands now:

```bash
# Set your preferred workspace
anyt workspace use DEV

# View current workspace
anyt workspace current

# Task commands work as before (no breaking changes)
anyt task show DEV-123
```

### After Backend Changes

Once the backend API is updated, the CLI will automatically use workspace-scoped endpoints. Users can:

```bash
# Continue using current workspace
anyt task show DEV-123

# Or specify different workspace
anyt task show DEV-123 --workspace STAGING

# Multiple workspaces can now have the same identifier
# (e.g., both "Personal DEV" and "Work DEV" can use identifier "DEV")
```

## Implementation Notes

### Code Locations

- **Workspace commands**: `src/cli/commands/workspace.py`
  - Added: `use()` and `current()` commands

- **Workspace resolver**: `src/cli/commands/task/helpers.py`
  - Added: `resolve_workspace_context()` function

- **Task command example**: `src/cli/commands/task/crud.py`
  - Updated: `show_task()` to use `--workspace` flag

- **Config**: `src/cli/config.py`
  - Existing: `EnvironmentConfig.default_workspace` field (now utilized)

### TODO Comments

Look for `TODO` comments in the code that indicate where API client calls need to be updated once the backend supports workspace-scoped endpoints:

```python
# TODO: Update to use workspace-scoped API when backend is ready
#       e.g., GET /v1/workspaces/{workspace_id}/tasks/{identifier}
task = await client.get_task(normalized_id)
```

## Related Tasks

- **T7-35**: Make Workspace Identifiers Non-Unique with Workspace-Scoped Task Identifiers
- **Backend Repository**: Database migration and API route updates (separate PR required)

## Questions?

For questions or issues related to this implementation, please refer to:
- Task specification: `.anyt/tasks/active/T7-35-Workspace-Scoped-Task-Identifiers.md`
- Main documentation: `CLAUDE.md`
- CLI usage: `docs/CLI_USAGE.md`
