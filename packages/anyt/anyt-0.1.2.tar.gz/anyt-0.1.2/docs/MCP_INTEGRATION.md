# MCP Integration with Claude Code

This document describes how to integrate AnyTask with Claude Code using the Model Context Protocol (MCP).

## Overview

The AnyTask MCP server exposes task management tools and resources to Claude Code, enabling seamless AI agent integration. Claude Code can:

- List and query tasks
- Create and update tasks
- Start and finish work attempts
- Upload artifacts (diffs, logs, files)
- Access task details, dependencies, and history
- Track active tasks across sessions

## Prerequisites

1. **AnyTask Backend Running**: Ensure the backend API is running (default: http://0.0.0.0:8000)
2. **Agent API Key**: Create an agent API key for authentication
3. **Workspace**: Have a workspace set up in AnyTask

## Setup Instructions

### Step 1: Create Agent API Key

```bash
# Login to AnyTask CLI first
anyt auth login

# Create an agent API key
anyt auth agent-key create --name "claude-code" --permissions read,write,execute

# Save the generated key (starts with anyt_agent_)
```

### Step 2: Get Workspace ID

```bash
# List your workspaces
anyt workspace list

# Note your workspace ID (e.g., 1)
```

### Step 3: Configure Claude Code

Add the MCP server to Claude Code's configuration file:

**macOS/Linux**: `~/.config/claude/mcp.json`
**Windows**: `%APPDATA%\Claude\mcp.json`

```json
{
  "mcpServers": {
    "anytask": {
      "command": "anyt",
      "args": ["mcp", "serve"],
      "env": {
        "ANYTASK_API_URL": "http://0.0.0.0:8000",
        "ANYTASK_API_KEY": "anyt_agent_xxx",
        "ANYTASK_WORKSPACE_ID": "1"
      }
    }
  }
}
```

Replace:
- `anyt_agent_xxx` with your actual agent API key
- `1` with your workspace ID
- `http://0.0.0.0:8000` with your backend URL if different

### Step 4: Generate Configuration

Alternatively, use the CLI to generate the configuration:

```bash
anyt mcp config
```

This will output the configuration snippet with your current settings.

### Step 5: Test Connection

Verify the MCP server can connect to AnyTask:

```bash
export ANYTASK_API_KEY=anyt_agent_xxx
export ANYTASK_WORKSPACE_ID=1
anyt mcp test
```

Expected output:
```
Testing MCP server connection...
✓ API client initialized
✓ Connected to workspace: DEV
✓ Connected to project: default
✓ 8 tools available:
  - list_tasks
  - select_task
  - create_task
  - update_task
  - start_attempt
  - finish_attempt
  - add_artifact
  - get_board
✓ 1 resources + 3 templates available

✓ All tests passed!
```

### Step 6: Restart Claude Code

Restart Claude Code to load the MCP configuration.

## Available Tools

### list_tasks

List tasks with optional filtering.

**Arguments**:
- `status` (optional): Filter by status (backlog, todo, inprogress, done, canceled)
- `assignee_id` (optional): Filter by assignee ID
- `limit` (optional): Maximum number of tasks (default: 20)

**Example**:
```
List all tasks in progress
```

### select_task

Select a task as the active task for the current workspace.

**Arguments**:
- `task_id` (required): Task identifier (e.g., "DEV-123")

**Example**:
```
Select task DEV-123
```

### create_task

Create a new task.

**Arguments**:
- `title` (required): Task title
- `description` (optional): Task description
- `priority` (optional): Priority (-2 to 2)

**Example**:
```
Create a task "Implement user authentication" with priority 1
```

### update_task

Update task fields.

**Arguments**:
- `task_id` (required): Task identifier
- `version` (required): Current version for optimistic locking
- `title` (optional): New title
- `description` (optional): New description
- `status` (optional): New status

**Example**:
```
Update DEV-123 status to "done" with version 5
```

### start_attempt

Start a work attempt on a task.

**Arguments**:
- `task_id` (required): Task identifier
- `notes` (optional): Notes about the attempt

**Example**:
```
Start an attempt on DEV-123
```

### finish_attempt

Mark an attempt as finished.

**Arguments**:
- `attempt_id` (required): Attempt ID
- `status` (required): Outcome (success, failed, aborted)
- `failure_class` (optional): Failure classification if failed
- `cost_tokens` (optional): Token cost
- `wall_clock_ms` (optional): Duration in milliseconds
- `notes` (optional): Notes about the outcome

**Example**:
```
Finish attempt 42 with status success
```

### add_artifact

Upload an artifact for an attempt.

**Arguments**:
- `attempt_id` (required): Attempt ID
- `type` (required): Artifact type (diff, file, log, benchmark, screenshot)
- `content` (required): Artifact content
- `metadata` (optional): Additional metadata

**Example**:
```
Add a diff artifact to attempt 42 with the git diff output
```

### get_board

Get Kanban board view of tasks organized by status.

**Arguments**: None

**Example**:
```
Show me the board
```

## Available Resources

### task://{task_id}/spec

Full task specification including title, description, status, and metadata.

**Example URI**: `task://DEV-123/spec`

### task://{task_id}/deps

Task dependencies and dependents.

**Example URI**: `task://DEV-123/deps`

### task://{task_id}/history

Event history and timeline for the task.

**Example URI**: `task://DEV-123/history`

### workspace://current/active_task

Currently selected active task for the workspace.

**Example URI**: `workspace://current/active_task`

## Usage Patterns

### Working on a Task

1. **Select task**:
   ```
   Select task DEV-123
   ```

2. **Start attempt**:
   ```
   Start an attempt on DEV-123 with notes "Implementing authentication"
   ```

3. **Work on implementation** (Claude Code writes code)

4. **Add artifacts**:
   ```
   Add a diff artifact to attempt 42 with this git diff:
   [paste diff]
   ```

5. **Finish attempt**:
   ```
   Finish attempt 42 with status success
   ```

### Creating and Organizing Tasks

1. **Create task**:
   ```
   Create a task "Add rate limiting" with description "Implement rate limiting middleware" and priority 1
   ```

2. **View board**:
   ```
   Show me the Kanban board
   ```

3. **Update task**:
   ```
   Update DEV-124 status to "inprogress" with version 1
   ```

### Exploring Task Context

Claude Code can automatically fetch task context using resources:

- Task specification provides full details
- Task dependencies show relationships
- Task history reveals past changes and attempts

## Active Task Management

The MCP server maintains an active task in `.anyt/active_task.json`:

```json
{
  "task_id": "DEV-123",
  "version": 5,
  "title": "Implement user authentication",
  "status": "inprogress",
  "workspace_id": 1,
  "last_sync": "2024-01-15T10:00:00Z"
}
```

This file:
- Persists the active task across sessions
- Tracks version for optimistic locking
- Syncs with the backend on updates

## Troubleshooting

### "Error: No workspace configured"

Ensure `ANYTASK_WORKSPACE_ID` is set in the MCP configuration.

### "Error: API key is required"

Set `ANYTASK_API_KEY` in the MCP configuration with a valid agent API key.

### "Authentication failed"

Verify:
1. API key is valid (starts with `anyt_agent_`)
2. API key has not been revoked
3. Agent has access to the workspace

### "Connection refused"

Ensure:
1. AnyTask backend is running at the configured URL
2. No firewall blocking the connection
3. URL is correct (include http:// or https://)

### Test the connection

```bash
export ANYTASK_API_KEY=your_key
export ANYTASK_WORKSPACE_ID=1
anyt mcp test
```

## Security Considerations

1. **API Key Storage**: Store API keys securely in environment variables, not in code
2. **Workspace Isolation**: Each agent API key is scoped to specific workspaces
3. **Permissions**: Agent keys support granular permissions (read, write, execute)
4. **Audit Trail**: All agent actions are logged in the event history

## Advanced Configuration

### Custom Workspace Directory

By default, the MCP server uses the current working directory for `.anyt/` files. To use a different directory:

```bash
cd /path/to/your/project
anyt mcp serve
```

### Multiple Workspaces

To work with multiple workspaces, create separate MCP server configurations:

```json
{
  "mcpServers": {
    "anytask-dev": {
      "command": "anyt",
      "args": ["mcp", "serve"],
      "env": {
        "ANYTASK_WORKSPACE_ID": "1",
        "ANYTASK_API_KEY": "anyt_agent_dev_xxx"
      }
    },
    "anytask-prod": {
      "command": "anyt",
      "args": ["mcp", "serve"],
      "env": {
        "ANYTASK_WORKSPACE_ID": "2",
        "ANYTASK_API_KEY": "anyt_agent_prod_xxx"
      }
    }
  }
}
```

## Next Steps

- Explore [CLI documentation](CLI_USAGE.md) for more AnyTask features
- Review [API documentation](server_api.md) for endpoint details
- Check [architecture overview](CLAUDE.md) for system design

## Support

For issues or questions:
1. Check the [troubleshooting](#troubleshooting) section
2. Run `anyt mcp test` to diagnose connection issues
3. Review logs in Claude Code's output panel
4. File an issue on GitHub with reproduction steps
