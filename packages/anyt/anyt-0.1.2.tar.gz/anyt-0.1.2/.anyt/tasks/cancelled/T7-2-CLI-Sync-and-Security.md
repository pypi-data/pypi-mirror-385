# T7-2: CLI Sync & Security Enhancement

## Priority
Low

## Status
Pending

## Description
Enhance the AnyTask CLI with offline sync capabilities and secure credential storage. Implements SQLite-based local cache for tasks, bi-directional sync with conflict resolution, and keyring-based secure credential storage.

## Objectives
- Implement local SQLite cache for offline access to tasks/workspaces
- Build bi-directional sync system (local ↔ remote)
- Add conflict resolution for concurrent edits
- Secure credential storage using keyring library
- Support offline task creation and editing
- Queue operations when offline, sync when online

## Features

### Local Cache (SQLite)
Store local copies of remote data for offline access:
- Tasks, projects, workspaces
- Task dependencies
- Attempts and artifacts
- Workspace members
- Labels

### Sync Functionality
Bi-directional synchronization between local cache and remote API:
- **Pull**: Fetch remote changes and update local cache
- **Push**: Send local changes to remote server
- **Conflict Resolution**: Handle concurrent edits with user prompts
- **Sync Queue**: Track pending operations when offline

### Secure Credential Storage
Replace plaintext token storage with encrypted keyring:
- Use `keyring` library for OS-level credential storage
- macOS: Keychain
- Linux: Secret Service / libsecret
- Windows: Windows Credential Locker
- Fallback to encrypted file if keyring unavailable

## Commands

### anyt sync
```bash
# Sync all changes (pull then push)
$ anyt sync
↓ Fetching remote changes...
  - Pulled 5 updated tasks
  - Pulled 2 new tasks
↑ Pushing local changes...
  - Created: DEV-42
  - Updated: DEV-43
✓ Synced 9 tasks

# Pull only (fetch remote changes)
$ anyt sync --pull
↓ Fetching remote changes...
✓ Pulled 7 changes

# Push only (send local changes)
$ anyt sync --push
↑ Pushing local changes...
✓ Pushed 3 changes

# Force sync (overwrite local with remote)
$ anyt sync --force
⚠ This will overwrite local changes
Continue? [y/N]: y
↓ Fetching remote changes...
✓ Force synced 15 tasks
```

### Conflict Resolution
```bash
$ anyt sync
↓ Fetching remote changes...
⚠ Conflict detected for DEV-42:
  Local version: 5
  Remote version: 6

  Choose resolution:
  1. Keep local changes (overwrite remote)
  2. Accept remote changes (overwrite local)
  3. Edit manually

  Choice [1-3]: 2
✓ Resolved conflict (accepted remote)
✓ Synced 1 task
```

### Offline Operations
```bash
# Create task offline
$ anyt task create "Fix bug" --offline
✓ Created DEV-43 (queued for sync)

# Edit task offline
$ anyt task update DEV-43 --status done --offline
✓ Updated DEV-43 (queued for sync)

# View sync queue
$ anyt sync status
Pending operations: 2
  - Create: DEV-43
  - Update: DEV-43 (status)

Last sync: 2 hours ago
Connection: Offline ✗

# Sync when back online
$ anyt sync
↑ Pushing local changes...
  - Created: DEV-43
  - Updated: DEV-43
✓ Synced 2 operations
```

## Cache Schema

SQLite database stored at `~/.cache/anyt/<env>/cache.db`:

```sql
-- Core entities (mirror of remote)
CREATE TABLE workspaces (
  id INTEGER PRIMARY KEY,
  identifier TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  synced_at TEXT NOT NULL
);

CREATE TABLE projects (
  id INTEGER PRIMARY KEY,
  workspace_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  synced_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

CREATE TABLE tasks (
  id INTEGER PRIMARY KEY,
  project_id INTEGER NOT NULL,
  workspace_id INTEGER NOT NULL,
  identifier TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL,
  priority INTEGER NOT NULL,
  assignee_id TEXT,
  version INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  synced_at TEXT NOT NULL,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

CREATE TABLE task_dependencies (
  id INTEGER PRIMARY KEY,
  task_id INTEGER NOT NULL,
  depends_on_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  synced_at TEXT NOT NULL,
  FOREIGN KEY (task_id) REFERENCES tasks(id),
  FOREIGN KEY (depends_on_id) REFERENCES tasks(id)
);

CREATE TABLE attempts (
  id INTEGER PRIMARY KEY,
  task_id INTEGER NOT NULL,
  status TEXT NOT NULL,
  failure_type TEXT,
  cost_tokens INTEGER,
  wall_clock_ms INTEGER,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  synced_at TEXT NOT NULL,
  FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Sync tracking
CREATE TABLE sync_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  operation TEXT NOT NULL,        -- 'create', 'update', 'delete'
  entity_type TEXT NOT NULL,      -- 'task', 'project', 'attempt', etc.
  entity_id TEXT,                 -- Local ID (may be temp for creates)
  remote_id INTEGER,              -- Remote ID after sync
  payload TEXT NOT NULL,          -- JSON payload
  created_at TEXT NOT NULL,
  synced INTEGER DEFAULT 0,       -- 0 = pending, 1 = synced
  synced_at TEXT,
  error TEXT                      -- Error message if sync failed
);

CREATE TABLE sync_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  direction TEXT NOT NULL,        -- 'pull', 'push'
  synced_at TEXT NOT NULL,
  changes INTEGER NOT NULL,       -- Number of changes synced
  conflicts INTEGER DEFAULT 0,    -- Number of conflicts resolved
  errors INTEGER DEFAULT 0        -- Number of errors encountered
);

-- Metadata
CREATE TABLE sync_metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- Store last sync timestamp
INSERT INTO sync_metadata (key, value) VALUES ('last_sync', '');
```

## Sync Strategy

### Pull (Remote → Local)
1. Get `last_sync` timestamp from metadata
2. Fetch all changes from remote API since `last_sync`
3. For each remote entity:
   - If exists in local cache with same version: skip
   - If exists in local cache with different version: check for conflict
   - If conflict and local has pending changes: prompt user
   - If no conflict or user chose remote: update local cache
4. Update `last_sync` timestamp
5. Log sync operation

### Push (Local → Remote)
1. Read unsynced operations from `sync_queue`
2. For each operation:
   - Send to remote API
   - If 409 Conflict: prompt user for resolution
   - If success: mark as synced, store remote ID
   - If error: log error, keep in queue
3. Update sync log

### Conflict Resolution
When local and remote versions differ:
1. Show both versions to user
2. Prompt for choice:
   - Accept local (push to remote, increment version)
   - Accept remote (update local, discard changes)
   - Manual edit (open editor with both versions)
3. Apply choice and continue sync

## Secure Credential Storage

### Using Keyring
Replace current plaintext storage in config.json:

**Before** (config.json):
```json
{
  "environments": {
    "dev": {
      "api_url": "http://localhost:8000",
      "auth_token": "plaintext_token_here"
    }
  }
}
```

**After** (config.json + keyring):
```json
{
  "environments": {
    "dev": {
      "api_url": "http://localhost:8000",
      "auth_token_stored": true
    }
  }
}
```

**Keyring storage**:
```python
import keyring

# Store
keyring.set_password("anyt-cli", "dev:auth_token", "secret_token")

# Retrieve
token = keyring.get_password("anyt-cli", "dev:auth_token")

# Delete
keyring.delete_password("anyt-cli", "dev:auth_token")
```

### Migration
On first run with new version:
1. Detect plaintext tokens in config.json
2. Migrate to keyring
3. Remove plaintext tokens from config
4. Mark as migrated

## Acceptance Criteria
- [ ] SQLite cache database created at `~/.cache/anyt/<env>/cache.db`
- [ ] Cache schema includes all core entities (tasks, projects, workspaces, etc.)
- [ ] `anyt sync` performs bi-directional sync
- [ ] `anyt sync --pull` fetches remote changes only
- [ ] `anyt sync --push` sends local changes only
- [ ] Sync queue tracks pending operations
- [ ] Conflict resolution prompts user with options
- [ ] Offline task creation queued for later sync
- [ ] Sync log records all sync operations
- [ ] Keyring library integrated for secure credential storage
- [ ] Credentials migrated from plaintext to keyring
- [ ] Fallback to encrypted file if keyring unavailable
- [ ] Sync works across multiple environments (separate caches)
- [ ] Error handling for network failures during sync
- [ ] Sync status command shows pending operations and last sync time

## Dependencies
- T3-1: CLI Foundation & Setup (completed)
- T3-2.1: CLI Task Commands - Core (core commands for offline sync)
- Backend task CRUD endpoints (for syncing tasks)

## Estimated Effort
8-10 hours

## Technical Notes
- Use `sqlalchemy` or `sqlite3` for database operations
- Use `keyring` library for OS-level credential storage
- Implement exponential backoff for sync retries on network errors
- Cache database is environment-specific: `~/.cache/anyt/dev/cache.db`
- Sync should be atomic: either all operations succeed or rollback
- Consider using `filelock` to prevent concurrent cache access
- Add `--offline` flag to all write commands to queue operations
- Device code flow can be added later when backend supports it

## Out of Scope (Future Tasks)
- Device code authentication flow (requires backend implementation)
- Real-time sync with websockets
- Optimistic locking with CRDTs
- Sync preferences per entity type

## Events

### 2025-10-16 00:45 - Task Created
- Split from T3-1 CLI Foundation & Setup
- Status: Pending in backlog
- Includes remaining items from T3-1 acceptance criteria
- Ready to implement once task commands (T3-2) are available
