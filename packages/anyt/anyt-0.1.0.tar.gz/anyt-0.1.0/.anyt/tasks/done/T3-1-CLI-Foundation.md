# T3-1: CLI Foundation & Setup

## Priority
High

## Status
Completed

## Description
Build the foundational CLI tool (`anyt`) that works with the current AnyTask backend. Supports multiple environments (dev, staging, production), remote server configuration, and user directory-based settings. Includes authentication, configuration management, and basic command structure.

## Objectives
- Create CLI package with clean command structure
- Implement authentication (device code flow and PAT) for the current backend
- Support multiple environments with configurable server URLs
- Set up user directory configuration (`~/.config/anyt/`)
- Add local workspace configuration (`.anyt/`)
- Add sync mechanism for offline/online operations
- Create local cache database (SQLite)
- Support both local development and remote production servers

## CLI Structure

```bash
anyt
├── auth
│   ├── login              # Device code or PAT login
│   ├── logout             # Clear local credentials
│   └── whoami             # Show current user
├── workspace
│   ├── init               # Initialize/link workspace
│   ├── list               # List accessible workspaces
│   └── switch             # Switch active workspace
├── env                    # Environment management
│   ├── list               # List configured environments
│   ├── add                # Add new environment
│   ├── switch             # Switch active environment
│   └── show               # Show current environment
├── sync                   # Bi-directional sync
├── task (T3-2)
├── board (T3-3)
├── goal (T3-4)
└── config                 # Manage CLI configuration
```

## Commands

### anyt env commands
```bash
# List environments
$ anyt env list
* dev        http://localhost:8000 (active)
  staging    https://staging.anytask.dev
  prod       https://api.anytask.dev

# Add new environment
$ anyt env add local http://localhost:8000
✓ Added environment: local

# Switch environment
$ anyt env switch staging
✓ Switched to staging (https://staging.anytask.dev)

# Show current environment
$ anyt env show
Environment: dev
API URL: http://localhost:8000
Status: Connected ✓
```

### anyt auth login
```bash
# Login to current environment
$ anyt auth login
Environment: dev (http://localhost:8000)
Visit: http://localhost:8000/device
Enter code: ABCD-1234
Waiting for authorization...
✓ Logged in as user@example.com

# Login to specific environment
$ anyt auth login --env prod
Environment: prod (https://api.anytask.dev)
Visit: https://app.anytask.dev/device
Enter code: ABCD-1234
Waiting for authorization...
✓ Logged in as user@example.com

# PAT flow (for agents or CI/CD)
$ anyt auth login --token
Enter PAT: anyt_...
✓ Logged in as user@example.com

# Agent API key flow
$ anyt auth login --agent-key
Enter agent key: anyt_agent_...
✓ Authenticated as agent (workspace: DEV)
```

### anyt auth whoami
```bash
$ anyt auth whoami
User: user@example.com
Workspace: my-project (ws-123)
Environment: dev
API: http://localhost:8000
Status: Connected ✓
```

### anyt workspace init
```bash
# Link existing workspace
$ anyt workspace init
? Select workspace: my-project (ws-123)
✓ Initialized .anyt/ in /path/to/project

# Create new workspace
$ anyt workspace init --create "New Project"
✓ Created workspace: New Project (ws-456)
✓ Initialized .anyt/ in /path/to/project
```

### anyt sync
```bash
$ anyt sync
↓ Fetching remote changes...
↑ Pushing local changes...
  - Created: T-42
  - Updated: T-43 (resolved conflict)
✓ Synced 15 tasks
```

## Local Storage

### Directory Structure
```
.anyt/
├── workspace.json         # Workspace metadata
├── active_task.json       # Currently selected task
├── cache.db              # SQLite cache of tasks/deps/attempts
└── config.json           # Local overrides
```

### workspace.json
```json
{
  "workspace_id": "ws-123",
  "name": "my-project",
  "api_url": "https://api.anytask.dev",
  "last_sync": "2024-01-15T10:00:00Z"
}
```

### active_task.json
```json
{
  "task_id": "T-12",
  "version": 7,
  "title": "Implement OAuth callback",
  "status": "active",
  "selected_at": "2024-01-15T09:00:00Z"
}
```

### Global Config
`~/.config/anyt/config.json`:
```json
{
  "current_environment": "dev",
  "environments": {
    "dev": {
      "api_url": "http://localhost:8000",
      "auth_token": "<encrypted>",
      "default_workspace": "DEV"
    },
    "staging": {
      "api_url": "https://staging.anytask.dev",
      "auth_token": "<encrypted>",
      "default_workspace": null
    },
    "prod": {
      "api_url": "https://api.anytask.dev",
      "auth_token": "<encrypted>",
      "default_workspace": "PROD"
    }
  },
  "sync_interval": 15,
  "editor": "code",
  "color_scheme": "auto"
}
```

### Environment Variables
Override config with environment variables:
```bash
# Override API URL
export ANYT_API_URL=http://localhost:8000

# Override auth token
export ANYT_AUTH_TOKEN=anyt_...

# Override environment
export ANYT_ENV=dev

# Use agent key instead of user token
export ANYT_AGENT_KEY=anyt_agent_...
```

### cache.db Schema
```sql
-- Mirror of remote tables
CREATE TABLE tasks (...);
CREATE TABLE task_dependencies (...);
CREATE TABLE attempts (...);

-- Sync tracking
CREATE TABLE sync_queue (
  id INTEGER PRIMARY KEY,
  operation TEXT, -- create, update, delete
  entity TEXT,    -- task, dependency, attempt
  entity_id TEXT,
  payload JSON,
  created_at TEXT,
  synced INTEGER DEFAULT 0
);

CREATE TABLE sync_log (
  id INTEGER PRIMARY KEY,
  synced_at TEXT,
  direction TEXT, -- push, pull
  changes INTEGER
);
```

## Sync Strategy

### Push (Local → Remote)
1. Read sync_queue for unsynced operations
2. Apply operations to remote API
3. Handle conflicts (409 responses)
4. Mark operations as synced
5. Update local cache with remote versions

### Pull (Remote → Local)
1. Fetch latest changes since last_sync
2. Apply to local cache.db
3. Resolve conflicts with local edits
4. Update last_sync timestamp

### Conflict Resolution
- For 409 Conflict: prompt user with 3-way merge
- Options: accept theirs, accept mine, edit manually
- Store resolution preference for future conflicts

## Output Formatting

### Tables
Use rich formatting for terminal tables:
```
ID    Title                       Status  Owner    Updated
T-12  Implement OAuth callback    active  you      2h ago
T-15  Add email templates         done    agent    5m ago
```

### Colors
- Green: success, done tasks
- Yellow: active, warnings
- Red: errors, blocked tasks
- Blue: info, backlog tasks
- Gray: metadata

### Progress Indicators
- Spinners for async operations
- Progress bars for sync
- Checkmarks for completed operations

## Acceptance Criteria
- [x] CLI installable via pip/uvx
- [x] Multiple environment support (dev, staging, prod)
- [x] `anyt env` commands for managing environments
- [x] Environment configuration stored in `~/.config/anyt/config.json`
- [x] Support for environment variables (ANYT_API_URL, ANYT_ENV, etc.)
- [x] `anyt auth login` supports PAT and agent key flows (device code pending backend)
- [x] `anyt auth login --env <env>` to login to specific environment
- [x] `anyt auth whoami` shows current user, workspace, and environment
- [x] `anyt workspace init` creates `.anyt/` directory with config
- [ ] `anyt sync` performs bi-directional sync with conflict resolution (moved to T3-1-2)
- [x] Works with current backend (http://localhost:8000 in dev)
- [x] Works with remote servers (https://api.anytask.dev in prod)
- [ ] Local cache (SQLite) mirrors remote state per environment (moved to T3-1-2)
- [ ] Sync queue handles offline operations (moved to T3-1-2)
- [x] Global config stored in `~/.config/anyt/`
- [ ] Auth tokens stored securely per environment with keyring (moved to T3-1-2)
- [x] Output formatted with colors and tables (using rich)
- [x] Error messages are clear and actionable
- [x] Help text for all commands (--help)
- [x] Connection health check for each environment

## Dependencies
- T2-9: Complete Repository Migration (ensures backend APIs are stable)
- T1-2: API Foundation (for API client)
- T1-3: Auth Enhancement (for auth endpoints and agent keys)

## Estimated Effort
10-12 hours

## Technical Notes
- Use Typer for CLI framework (Python, matches backend stack)
- Use rich for terminal formatting and tables
- Use keyring for secure credential storage per environment
- Use SQLModel for cache.db ORM (matches backend)
- Implement exponential backoff for API retries
- Add verbose mode (-v) for debugging
- Support --json flag for machine-readable output
- Use httpx for async API calls (matches FastAPI ecosystem)
- Environment config priority: CLI flags > Environment variables > Config file
- Store separate SQLite cache per environment in `~/.cache/anyt/<env>/cache.db`
- Support health check endpoint (`GET /v1/health`) to verify connectivity
- Default to current backend API structure (`/v1/` prefix)
- Consider using textual for TUI components later

## Environment Setup Examples

### Development (Local Backend)
```bash
# First time setup
anyt env add dev http://localhost:8000
anyt env switch dev
anyt auth login --agent-key
# Enter: anyt_agent_<key>

# Verify connection
anyt env show
```

### Production (Remote Server)
```bash
# Add production environment
anyt env add prod https://api.anytask.dev
anyt env switch prod
anyt auth login
# Follow device code flow

# Verify connection
anyt env show
```

### CI/CD Usage
```bash
# Use environment variables
export ANYT_ENV=prod
export ANYT_API_URL=https://api.anytask.dev
export ANYT_AGENT_KEY=anyt_agent_<key>

# CLI will use environment variables
anyt task list --status active
```

## Events

### 2025-10-15 17:30 - Started work
- Moved task from backlog to active
- Status changed to "In Progress"
- Creating new branch for CLI implementation
- All dependencies met (T2-9 complete, backend APIs stable)

### 2025-10-15 18:00 - CLI foundation implemented
- Created CLI package structure in `src/cli/`
- Implemented configuration management (`cli/config.py`)
  - GlobalConfig with multi-environment support
  - WorkspaceConfig for local `.anyt/` directories
  - Environment variable override support
- Implemented environment management commands (`cli/commands/env.py`)
  - `anyt env list` - List all environments with status
  - `anyt env add` - Add new environment
  - `anyt env switch` - Switch active environment
  - `anyt env show` - Show current environment details
- Added CLI dependencies (typer, rich, httpx, keyring)
- Configured entry point in pyproject.toml
- Tested CLI commands successfully

Next steps:
- Implement authentication commands (auth login/logout/whoami)
- Implement workspace commands (workspace init/list/switch)
- Add API client module
- Implement sync functionality

### 2025-10-15 18:15 - PR Created
- Created PR #17: https://github.com/supercarl87/AnyTaskBackend/pull/17
- Title: [T3-1] CLI Foundation & Setup - Environment Management
- Status: Ready for review
- Progress: ~40% complete (environment management done)

### 2025-10-16 00:35 - Authentication and Workspace Commands Implemented
- Implemented API client module (`src/cli/client.py`)
  - HTTP client with support for user tokens and agent keys
  - Methods: health_check, list_workspaces, get_workspace, create_workspace
  - Added redirect following for all API calls
- Implemented authentication commands (`src/cli/commands/auth.py`)
  - `anyt auth login` - Login with PAT or agent key (device code flow pending backend support)
  - `anyt auth login --env <env>` - Login to specific environment
  - `anyt auth logout` - Clear credentials for environment or all environments
  - `anyt auth whoami` - Show current authentication status and workspaces
- Implemented workspace commands (`src/cli/commands/workspace.py`)
  - `anyt workspace init` - Initialize/link workspace with interactive selection
  - `anyt workspace init --create <name> --identifier <id>` - Create new workspace
  - `anyt workspace list` - List all accessible workspaces with current indicator
  - `anyt workspace switch` - Switch active workspace interactively or by ID
- Registered new command groups in main.py
- Tested CLI commands successfully with dev server
- All core CLI commands now functional (env, auth, workspace)

Progress: ~75% complete
Remaining work:
- Implement sync functionality (SQLite cache + bi-directional sync)
- Add secure credential storage using keyring
- Implement task commands (T3-2)
- Add board and goal commands (T3-3, T3-4)

### 2025-10-16 00:45 - Task Completed
- Updated acceptance criteria: 16/20 items completed
- Core CLI functionality complete (env, auth, workspace commands)
- Remaining work split into new task T3-1-2
- Task moved to done/
- All code committed and pushed to PR #17

Completed items:
- ✅ CLI package structure with Typer and Rich
- ✅ Multi-environment support (dev, staging, prod)
- ✅ Environment management commands (env list/add/switch/show)
- ✅ Authentication commands (auth login/logout/whoami)
- ✅ Workspace commands (workspace init/list/switch)
- ✅ API client with HTTP support
- ✅ Configuration management (~/.config/anyt/)
- ✅ Local workspace config (.anyt/workspace.json)
- ✅ Environment variable overrides
- ✅ Rich terminal output with colors and tables
- ✅ Error handling and help text

Deferred to T3-1-2:
- Sync functionality (SQLite cache + bi-directional sync)
- Secure credential storage with keyring
- Device code flow (requires backend support)
