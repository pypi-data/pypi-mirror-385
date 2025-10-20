# AnyTask CLI Usage Guide

The `anyt` CLI is an AI-native task management tool built for Linear-style workflows. It supports both human users and AI agents as first-class citizens.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Global Options](#global-options)
- [Environment Management](#environment-management)
- [Authentication](#authentication)
- [User Preferences Management](#user-preferences-management)
- [Workspace Management](#workspace-management)
- [Project Management](#project-management)
- [Task Management](#task-management)
- [Dependency Management](#dependency-management)
- [Label Management](#label-management)
- [Task Views (Saved Filters)](#task-views-saved-filters)
- [Template Management](#template-management)
- [Board & Visualization](#board--visualization)
- [AI Commands](#ai-commands)
- [Upcoming CLI Features](#upcoming-cli-features)
- [MCP Integration](#mcp-integration)
- [Configuration](#configuration)

---

## Installation

The CLI is installed as part of the backend package:

```bash
# Install dependencies
make install

# Verify installation
anyt --version
```

---

## Quick Start

```bash
# 1. Add an environment
anyt env add dev http://localhost:8000

# 2. Login with a token or agent key
anyt auth login --token                                    # Interactive prompt
# OR
anyt auth login --agent-key-value anyt_agent_...           # Direct agent key
# OR
export ANYT_AGENT_KEY=anyt_agent_... && anyt auth login   # Environment variable

# 3. Initialize a workspace
anyt init

# 4. View tasks on the board
anyt board

# 5. Create a task
anyt task add "Implement user authentication" --priority 1

# 6. Pick a task to work on
anyt task pick DEV-1

# 7. Show active task details
anyt active

# 8. Mark task as done
anyt task done
```

---

## Global Options

```bash
anyt --version, -v    # Show version and exit
anyt --help          # Show help message
```

### Health Check

```bash
anyt health
```

Check if the API server is reachable. Displays:
- Current environment name
- API URL
- Server connectivity status

**Example:**
```bash
$ anyt health
Environment: dev
API URL: http://localhost:8000

✓ Server is healthy
```

---

## Environment Management

Manage CLI environments (development, staging, production).

### List Environments

```bash
anyt env list
```

Shows all configured environments with connectivity status. The current environment is marked with `*`.

### Add Environment

```bash
anyt env add <name> <api-url> [--active]
```

**Arguments:**
- `name`: Environment name (e.g., `dev`, `staging`, `prod`)
- `api-url`: API base URL (must start with `http://` or `https://`)

**Options:**
- `--active`: Make this the active environment immediately

**Examples:**
```bash
anyt env add dev http://localhost:8000
anyt env add prod https://api.anytask.com --active
```

### Switch Environment

```bash
anyt env switch <name>
```

**Arguments:**
- `name`: Environment name to switch to

**Examples:**
```bash
anyt env switch prod
```

### Show Current Environment

```bash
anyt env show
```

Displays:
- Current environment name
- API URL
- Authentication status
- Default workspace (if set)
- Connection status

**Note:** Environment can be overridden with `ANYT_ENV` and `ANYT_API_URL` environment variables.

---

## Authentication

Manage authentication credentials for accessing the AnyTask API.

### Login

```bash
anyt auth login [--env ENV] [--token] [--agent-key] [--token-value VALUE] [--agent-key-value VALUE]
```

**Options:**
- `--env, -e`: Environment to login to (defaults to current)
- `--token`: Use Personal Access Token (PAT) - prompts for value
- `--token-value`: Personal Access Token value (skips prompt)
- `--agent-key`: Use agent API key - prompts for value
- `--agent-key-value`: Agent API key value (skips prompt)

**Authentication Flows:**

1. **Personal Access Token (PAT):**
   ```bash
   # Interactive prompt
   anyt auth login --token
   # Enter: anyt_...

   # Direct value
   anyt auth login --token-value anyt_user_token_abc123
   ```

2. **Agent API Key:**
   ```bash
   # Interactive prompt
   anyt auth login --agent-key
   # Enter: anyt_agent_...

   # Direct value (recommended for scripts/automation)
   anyt auth login --agent-key-value anyt_agent_O1HFI42vTa442u6XSCAZISxLVoW8Xd7j
   ```

3. **Environment Variable (Agent Key):**
   ```bash
   # Set environment variable
   export ANYT_AGENT_KEY=anyt_agent_O1HFI42vTa442u6XSCAZISxLVoW8Xd7j

   # Login automatically uses ANYT_AGENT_KEY if set
   anyt auth login
   ```

4. **Device Code Flow (coming soon):**
   ```bash
   anyt auth login
   # Interactive browser-based authentication (when ANYT_AGENT_KEY not set)
   ```

### Logout

```bash
anyt auth logout [--env ENV] [--all]
```

**Options:**
- `--env, -e`: Environment to logout from (defaults to current)
- `--all`: Logout from all environments

**Examples:**
```bash
anyt auth logout              # Logout from current environment
anyt auth logout --env prod   # Logout from specific environment
anyt auth logout --all        # Logout from all environments
```

### Who Am I

```bash
anyt auth whoami
```

Shows information about the currently authenticated user or agent:
- Environment name and API URL
- Authentication type (User Token or Agent Key)
- Connection status
- Accessible workspaces

---

## User Preferences Management

Manage your user preferences for current workspace and project. These preferences are stored on the server and provide a seamless experience across different CLI sessions and machines.

**Note:** User preferences require JWT authentication (user tokens). They are not supported with agent API keys.

### Show Current Preferences

```bash
anyt preference show
```

Display your current workspace and project preferences. Shows:
- Current workspace ID and name
- Current project ID (if set)

**Example:**
```bash
$ anyt preference show
╭─────────────────────────────────────────╮
│          User Preferences               │
├────────────────────┬────────────────────┤
│ Setting            │ Value              │
├────────────────────┼────────────────────┤
│ Current Workspace  │ [2] Team Workspace │
│ Current Project    │ [10]               │
╰────────────────────┴────────────────────╯
```

### Set Current Workspace

```bash
anyt preference set-workspace <workspace_id>
```

Set your current workspace preference. If you have a current project set and it doesn't belong to the new workspace, the project preference will be automatically cleared.

**Arguments:**
- `workspace_id`: The workspace ID to set as current

**Examples:**
```bash
# Set workspace 2 as current
anyt preference set-workspace 2

# Output:
# ✓ Current workspace updated to [2] Team Workspace
```

**Note:** When switching workspaces, your current project preference may be cleared if it doesn't belong to the new workspace.

### Set Current Project

```bash
anyt preference set-project <workspace_id> <project_id>
```

Set your current project (and workspace) preference. Both the workspace and project preferences are updated together.

**Arguments:**
- `workspace_id`: The workspace ID containing the project
- `project_id`: The project ID to set as current

**Examples:**
```bash
# Set project 10 in workspace 2 as current
anyt preference set-project 2 10

# Output:
# ✓ Current workspace updated to [2] Team Workspace
# ✓ Current project updated to [10]
```

### Clear Preferences

```bash
anyt preference clear
```

Clear all your user preferences, resetting both workspace and project selections. After clearing, you'll use the default behavior (first workspace/project by creation date).

**Example:**
```bash
$ anyt preference clear
✓ User preferences cleared
Your workspace and project selections have been reset
```

### How Preferences Work

User preferences provide a consistent experience across CLI sessions:

1. **Persistent Storage**: Preferences are stored on the server, not locally
2. **Cross-Device Sync**: Your preferences follow you across different machines
3. **Default Fallback**: If no preferences are set, the CLI uses the first workspace/project by creation date
4. **Smart Clearing**: When switching workspaces, projects that don't belong to the new workspace are automatically cleared
5. **API Integration**: The `/v1/workspaces/current` and `/v1/workspaces/{id}/projects/current` endpoints check preferences first

**Use Cases:**
- Set a default workspace when you work across multiple teams
- Keep your active project context consistent across CLI sessions
- Reset preferences when switching to a different workflow

**Authentication Requirement:**
- User preferences require JWT authentication (user login tokens)
- Agent API keys do not support user preferences
- Run `anyt auth login --token` to authenticate with a user token

---

## Workspace Management

Manage workspaces - the top-level container for projects and tasks.

### Initialize Workspace

```bash
anyt init [--create NAME] [--identifier ID] [--dir DIR]
```

**Options:**
- `--create`: Create a new workspace with the given name
- `--identifier, -i`: Workspace identifier (required when creating, e.g., "DEV")
- `--dir, -d`: Directory to initialize (default: current directory)

**Modes:**

1. **Link Existing/Auto-Create Workspace:**
   ```bash
   anyt init
   # Uses or creates current workspace automatically
   ```

2. **Create New Workspace:**
   ```bash
   anyt init --create "Development" --identifier DEV
   ```

Creates a `.anyt/anyt.json` workspace configuration file.

**Note:** The `anyt init` command replaces `anyt workspace init` as a top-level command for convenience.

### List Workspaces

```bash
anyt workspace list
```

Shows all accessible workspaces with:
- Name
- Identifier
- ID
- Current workspace indicator (●)

### Switch Workspace

```bash
anyt workspace switch [WORKSPACE_ID] [--dir DIR]
```

**Arguments:**
- `WORKSPACE_ID`: Workspace ID or identifier to switch to (optional - shows picker if not provided)

**Options:**
- `--dir, -d`: Directory to switch workspace in (default: current)

**Examples:**
```bash
anyt workspace switch DEV
anyt workspace switch 123
anyt workspace switch  # Interactive picker
```

---

## Project Management

Manage projects within workspaces. Projects organize tasks into logical groups.

### Create Project

```bash
anyt project create --name <NAME> --identifier <ID> [OPTIONS]
```

**Options:**
- `--name, -n`: Project name (required)
- `--identifier, -i`: Project identifier (required, e.g., "API", "WEB")
- `--description, -d`: Project description (optional)
- `--workspace, -w`: Workspace ID or identifier (default: current workspace from anyt.json)
- `--dir`: Directory with workspace config (default: current directory)

**Examples:**
```bash
# Create project in current workspace
anyt project create --name "Backend API" --identifier API

# Create project with description
anyt project create --name "Frontend" --identifier WEB --description "React application"

# Create project in specific workspace
anyt project create --name "Mobile App" --identifier MOB --workspace DEV
```

### List Projects

```bash
anyt project list [OPTIONS]
```

**Options:**
- `--workspace, -w`: Workspace ID or identifier (default: current workspace from anyt.json)
- `--dir`: Directory with workspace config (default: current directory)

**Examples:**
```bash
# List projects in current workspace
anyt project list

# List projects in specific workspace
anyt project list --workspace PROD
```

**Output:**
```
Projects in Development

Name          Identifier  ID  Status
Backend API   API         1   ● current
Frontend      WEB         2
Mobile App    MOB         3

Total: 3 projects
```

### Set Current Project

```bash
anyt project use <PROJECT_ID_OR_IDENTIFIER> [OPTIONS]
```

**Arguments:**
- `PROJECT_ID_OR_IDENTIFIER`: Project ID or identifier to set as current (required)

**Options:**
- `--workspace, -w`: Workspace ID or identifier (default: current workspace from anyt.json)
- `--dir`: Directory with workspace config (default: current directory)

**Examples:**
```bash
# Set current project by identifier
anyt project use API

# Set current project by ID
anyt project use 1

# Set current project in specific workspace
anyt project use WEB --workspace DEV
```

This updates your user preferences to make the selected project your default.

### Show Current Project

```bash
anyt project current [OPTIONS]
```

**Options:**
- `--workspace, -w`: Workspace ID or identifier (default: current workspace from anyt.json)
- `--dir`: Directory with workspace config (default: current directory)

**Examples:**
```bash
# Show current project
anyt project current

# Output:
# Workspace: Development
# Current project: Backend API (API)
# Project ID: 1
```

### Switch Project (Interactive)

```bash
anyt project switch [OPTIONS]
```

**Options:**
- `--workspace, -w`: Workspace ID or identifier (default: current workspace from anyt.json)
- `--dir`: Directory with workspace config (default: current directory)

**Examples:**
```bash
# Interactive project switcher
anyt project switch
```

Displays an interactive table of projects and prompts you to select one. The selected project becomes your current project.

**Output:**
```
Projects in Development

#  Name          Identifier  Current
1  Backend API   API         ●
2  Frontend      WEB
3  Mobile App    MOB

Select project [1]: 2
✓ Switched to project: Frontend (WEB)
```

---

## Task Management

Create, view, edit, and manage tasks.

### Create Task

```bash
anyt task add <title> [OPTIONS]
```

**Arguments:**
- `title`: Task title (required)

**Options:**
- `-d, --description`: Task description
- `--phase`: Phase/milestone identifier (e.g., T3, Phase 1)
- `-p, --priority`: Priority (-2 to 2, default: 0)
  - `-2`: Lowest
  - `-1`: Low
  - `0`: Normal (default)
  - `1`: High
  - `2`: Highest
- `--labels`: Comma-separated labels
- `--status`: Task status (default: `backlog`)
  - Values: `backlog`, `todo`, `inprogress`, `done`, `canceled`
- `--owner`: Assign to user or agent ID
- `--estimate`: Time estimate in hours
- `--project`: Project ID (uses current/default project if not specified)
- `--json`: Output in JSON format

**Examples:**
```bash
anyt task add "Implement OAuth" --priority 1 --project 1
anyt task add "Fix login bug" -p 2 --labels bug,auth --project 1
anyt task add "Update docs" -d "Add API documentation" --estimate 3 --project 1
anyt task add "Phase 3 task" --phase "T3" --priority 2
```

### List Tasks

```bash
anyt task list [OPTIONS]
```

**Options:**
- `--status`: Filter by status (comma-separated)
- `--mine`: Show only tasks assigned to you
- `--labels`: Filter by labels (comma-separated)
- `--sort`: Sort field (`priority`, `updated_at`, `created_at`, `status`)
- `--order`: Sort order (`asc`, `desc`)
- `--limit`: Max number of tasks to show (default: 50)
- `--offset`: Pagination offset (default: 0)
- `--json`: Output in JSON format

**Examples:**
```bash
anyt task list
anyt task list --status inprogress,done
anyt task list --mine --sort priority
anyt task list --labels bug --limit 10
```

### Show Task Details

```bash
anyt task show [IDENTIFIER] [OPTIONS]
```

**Arguments:**
- `IDENTIFIER`: Task identifier (e.g., `DEV-42`) or ID (uses active task if not specified)

**Options:**
- `--workspace, -w`: Workspace identifier or ID (uses current workspace if not specified)
- `--json`: Output in JSON format

**Examples:**
```bash
anyt task show DEV-42
anyt task show       # Uses active task
anyt task show 123   # By numeric ID
anyt task show DEV-42 --workspace PROJ  # Show task from different workspace
anyt task show DEV-42 --workspace 5     # Show task by workspace ID
```

**Workspace Resolution:**

The `--workspace` flag uses workspace-scoped API endpoints to fetch tasks from specific workspaces. Workspace lookups are cached for 5 minutes to improve performance.

Priority order for workspace resolution:
1. Explicit `--workspace` flag (if provided)
2. Environment's default workspace (from config)
3. Local `.anyt/anyt.json` workspace

Example workflow:
```bash
# Query task from production workspace while in dev directory
anyt task show PROD-123 --workspace PROD

# Query task from workspace ID 5
anyt task show DEV-42 --workspace 5
```

**Fuzzy Matching:**
- `DEV-42` → `DEV-42` (exact)
- `dev42` → `DEV-42` (case insensitive, no dash)
- `42` → `42` (just number)
- `DEV 42` → `DEV-42` (with space)

### Edit Task

```bash
anyt task edit [IDENTIFIER] [OPTIONS]
```

**Arguments:**
- `IDENTIFIER`: Task identifier (uses active task if not specified)

**Options:**
- `--title`: New title
- `-d, --description`: New description
- `--status`: New status
- `-p, --priority`: New priority (-2 to 2)
- `--labels`: Comma-separated labels (replaces all labels)
- `--owner`: New owner ID
- `--estimate`: New time estimate in hours
- `--ids`: Multiple task IDs to edit (comma-separated, for bulk operations)
- `--if-match`: Expected version for optimistic concurrency control
- `--dry-run`: Preview changes without applying
- `--json`: Output in JSON format

**Examples:**
```bash
# Edit single task
anyt task edit DEV-42 --status inprogress

# Bulk edit
anyt task edit --ids DEV-42,DEV-43,DEV-44 --status done

# Optimistic locking
anyt task edit DEV-42 --status done --if-match 5

# Preview changes
anyt task edit DEV-42 --priority 2 --dry-run
```

### Mark Task as Done

```bash
anyt task done [IDENTIFIERS...] [--json]
```

**Arguments:**
- `IDENTIFIERS`: Task identifier(s) (uses active task if not specified)

**Options:**
- `--json`: Output in JSON format

**Examples:**
```bash
anyt task done DEV-42
anyt task done DEV-42 DEV-43 DEV-44
anyt task done  # Marks active task as done
```

If the active task is marked done, it's automatically cleared.

### Delete Task

```bash
anyt task rm [IDENTIFIERS...] [--force] [--json]
```

**Arguments:**
- `IDENTIFIERS`: Task identifier(s) (uses active task if not specified)

**Options:**
- `--force, -f`: Skip confirmation prompt
- `--json`: Output in JSON format

**Examples:**
```bash
anyt task rm DEV-42
anyt task rm DEV-42 DEV-43 --force
anyt task rm  # Deletes active task (with confirmation)
```

Performs soft delete (sets `deleted_at` timestamp).

### Add Note to Task

```bash
anyt task note [IDENTIFIER] <note_text>
```

**Arguments:**
- `IDENTIFIER`: Task identifier (uses active task if not specified)
- `note_text`: Note content to add

**Examples:**
```bash
anyt task note DEV-42 "Implemented OAuth callback handler"
anyt task note "Fixed edge case with empty tokens"  # Uses active task
```

Adds a timestamped note to the task's description. The note is appended with a timestamp in the format:
```
---
[2025-10-18 14:30] Implemented OAuth callback handler
```

This is useful for tracking progress and adding context without formal commits.

### Pick Active Task

```bash
anyt task pick [IDENTIFIER] [OPTIONS]
```

**Arguments:**
- `IDENTIFIER`: Task identifier (optional - shows interactive picker if not specified)

**Options:**
- `--status`: Filter by status (comma-separated) - applies to interactive picker
- `--project`: Filter by project ID - applies to interactive picker
- `--mine`: Show only tasks assigned to you - applies to interactive picker
- `--json`: Output in JSON format

**Examples:**
```bash
# Pick a specific task by identifier
anyt task pick DEV-42

# Launch interactive picker to browse and select tasks
anyt task pick

# Interactive picker with filters
anyt task pick --status todo,backlog
anyt task pick --mine
anyt task pick --status inprogress --project 1
```

**Interactive Picker:**

When no identifier is provided, an interactive picker displays all available tasks:
- Tasks are grouped by status (backlog, todo, inprogress, blocked, done)
- Each task shows: number, identifier, title, and priority indicator
- Priority indicators: ↑↑ (2), ↑ (1), - (0), ↓ (-1), ↓↓ (-2)
- Type the task number to select it
- Type 'q' to quit without selecting

The picked task is saved to `.anyt/active_task.json` for use as default in other commands.

### Suggest Tasks

```bash
anyt task suggest [OPTIONS]
```

Get intelligent task recommendations based on priority, dependencies, and impact.

**Options:**
- `--limit INTEGER`: Number of suggestions to return (default: 3)
- `--status TEXT`: Filter by status, comma-separated (default: todo,backlog)
- `--json`: Output in JSON format

**Examples:**
```bash
# Get top 3 recommended tasks
anyt task suggest

# Get top 5 suggestions
anyt task suggest --limit 5

# Filter for only TODO tasks
anyt task suggest --status todo

# Get JSON output for programmatic use
anyt task suggest --json
```

**How it works:**

The suggest command implements intelligent scoring based on:
- **Priority weighting** (5x) - Higher priority tasks score better
- **Status bonus** (+3 for todo, +1 for inprogress)
- **Dependencies** (-10 penalty if blocked, +2 bonus if all deps complete)
- **Impact** (+2 per task that this unblocks)

Tasks with incomplete dependencies are automatically filtered out.

**Example output:**
```
Top 3 Recommended Tasks:

1. DEV-42 - Implement OAuth callback [Priority: 2]
   Reason: Priority 2, No dependencies, Unblocks 2 tasks, Ready to work on
   Status: todo

2. DEV-45 - Add Redis caching [Priority: 1]
   Reason: Priority 1, No dependencies, Ready to work on
   Status: todo

3. DEV-48 - Update API documentation [Priority: 0]
   Reason: All dependencies complete, Ready to work on
   Status: backlog

Run: anyt task pick <ID> to start working on a task
```

---

## Dependency Management

Manage task dependencies (prerequisite relationships).

### Add Dependency

```bash
anyt task dep add [IDENTIFIER] --on <DEPENDENCIES>
```

**Arguments:**
- `IDENTIFIER`: Task identifier (uses active task if not specified)

**Options:**
- `--on`: Task(s) this depends on (comma-separated identifiers, required)

**Examples:**
```bash
# DEV-43 depends on DEV-42
anyt task dep add DEV-43 --on DEV-42

# DEV-50 depends on multiple tasks
anyt task dep add DEV-50 --on DEV-42,DEV-43,DEV-44

# Use active task
anyt task pick DEV-43
anyt task dep add --on DEV-42
```

**Validation:**
- Prevents circular dependencies
- Prevents self-dependencies
- Shows warnings for already-existing dependencies

### Remove Dependency

```bash
anyt task dep rm [IDENTIFIER] --on <DEPENDENCIES>
```

**Arguments:**
- `IDENTIFIER`: Task identifier (uses active task if not specified)

**Options:**
- `--on`: Task(s) to remove dependency on (comma-separated identifiers, required)

**Examples:**
```bash
anyt task dep rm DEV-43 --on DEV-42
anyt task dep rm DEV-50 --on DEV-42,DEV-43
```

### List Dependencies

```bash
anyt task dep list [IDENTIFIER]
```

**Arguments:**
- `IDENTIFIER`: Task identifier (uses active task if not specified)

Shows:
- **Dependencies** (tasks this depends on) with status indicators
- **Blocks** (tasks that depend on this) with status indicators

**Status Indicators:**
- ✓ done
- ⬤ inprogress
- ⬜ backlog

**Example:**
```bash
anyt task dep list DEV-43
```

---

## Label Management

Manage workspace labels for task categorization and organization.

### Create Label

```bash
anyt label create <name> [OPTIONS]
```

**Arguments:**
- `name`: Label name (required)

**Options:**
- `--color`: Hex color code (e.g., #FF0000)
- `--description`: Label description
- `--json`: Output in JSON format

**Examples:**
```bash
# Create a simple label
anyt label create "Bug"

# Create with color and description
anyt label create "Feature" --color "#00FF00" --description "New features"
anyt label create "Urgent" --color "#FF0000" --description "High priority items"
```

### List Labels

```bash
anyt label list [--json]
```

Lists all labels in the workspace with:
- Colored indicators (if color is set)
- Description
- Alphabetically sorted

**Example:**
```bash
anyt label list
```

**Output:**
```
                Labels in My Workspace
┌─────────┬──────────────────┬────────────────────┐
│ Name    │ Color            │ Description        │
├─────────┼──────────────────┼────────────────────┤
│ Bug     │ ● #FF0000        │ Bug fixes          │
│ Feature │ ● #00FF00        │ New features       │
│ Urgent  │ ● #FFAA00        │ High priority      │
└─────────┴──────────────────┴────────────────────┘

Total: 3 label(s)
```

### Show Label

```bash
anyt label show <name> [--json]
```

**Arguments:**
- `name`: Label name (required)

Shows detailed information about a specific label including:
- Name
- Color (with colored indicator)
- Description
- ID

**Example:**
```bash
anyt label show "Bug"
```

### Edit Label

```bash
anyt label edit <name> [OPTIONS]
```

**Arguments:**
- `name`: Current label name (required)

**Options:**
- `--name`: New label name
- `--color`: New hex color code
- `--description`: New description
- `--json`: Output in JSON format

Shows before/after comparison and requires confirmation (unless using `--json`).

**Examples:**
```bash
# Rename label
anyt label edit "Bug" --name "Bugfix"

# Update color
anyt label edit "Feature" --color "#00AA00"

# Update multiple properties
anyt label edit "Urgent" --color "#FF3333" --description "Critical priority items"
```

### Delete Label

```bash
anyt label rm <names>... [OPTIONS]
```

**Arguments:**
- `names`: One or more label names to delete

**Options:**
- `--force`, `-f`: Skip confirmation prompt
- `--json`: Output in JSON format

**Examples:**
```bash
# Delete single label (with confirmation)
anyt label rm "Old Label"

# Delete multiple labels
anyt label rm "Label1" "Label2" "Label3" --force

# Delete with JSON output
anyt label rm "Bug" --json
```

---

## Task Views (Saved Filters)

Manage saved task views for quick access to commonly used filters. Task views are user-specific and require user authentication (not available for agents).

### Create View

```bash
anyt view create <name> [OPTIONS]
```

**Arguments:**
- `name`: View name (required)

**Options:**
- `--status`: Filter by status (comma-separated, e.g., "todo,inprogress")
- `--priority-min`: Minimum priority value
- `--priority-max`: Maximum priority value
- `--owner`: Filter by owner
- `--labels`: Filter by labels (comma-separated)
- `--default`: Set as default view
- `--json`: Output in JSON format

**Examples:**
```bash
# Create a high priority view
anyt view create "High Priority" --status "todo,inprogress" --priority-min 1 --default

# Create a bugs view
anyt view create "Bugs Only" --labels "bug"

# Create a personal tasks view
anyt view create "My Tasks" --owner "me" --status "inprogress"
```

### List Views

```bash
anyt view list [--json]
```

Lists all saved views with:
- View names
- Filter summary
- Default view indicator (⭐)

**Example:**
```bash
anyt view list
```

**Output:**
```
           Task Views in My Workspace
┌─────────────────┬─────────────────────────┬─────────┐
│ Name            │ Filters                 │ Default │
├─────────────────┼─────────────────────────┼─────────┤
│ Bugs Only       │ labels=bug              │         │
│ High Priority   │ status=todo,inprogress, │ ⭐      │
│                 │ priority≥1              │         │
│ My Tasks        │ status=inprogress,      │         │
│                 │ owner=me                │         │
└─────────────────┴─────────────────────────┴─────────┘

Total: 3 view(s)
```

### Show View

```bash
anyt view show <name> [--json]
```

**Arguments:**
- `name`: View name (required)

Shows detailed view configuration including all filters.

**Example:**
```bash
anyt view show "High Priority"
```

**Output:**
```
High Priority (default)

Filters:
  • status: todo, inprogress
  • priority_min: 1
```

### Apply View

```bash
anyt view apply <name> [OPTIONS]
```

**Arguments:**
- `name`: View name (required)

**Options:**
- `--limit`: Maximum tasks to show (default: 50)
- `--json`: Output in JSON format

Applies the saved view filters and displays matching tasks in table format.

**Example:**
```bash
anyt view apply "High Priority"
```

**Output:**
```
View: High Priority
Filters: status=todo,inprogress, priority≥1

┌────────┬─────────────────────────────┬────────────┬──────────┐
│ ID     │ Title                       │ Status     │ Priority │
├────────┼─────────────────────────────┼────────────┼──────────┤
│ DEV-42 │ Implement OAuth callback    │ todo       │ 2        │
│ DEV-38 │ Add Redis caching           │ inprogress │ 1        │
└────────┴─────────────────────────────┴────────────┴──────────┘

Showing 2 task(s)
```

### Edit View

```bash
anyt view edit <name> [OPTIONS]
```

**Arguments:**
- `name`: Current view name (required)

**Options:**
- `--name`: New view name
- `--status`: Update status filter
- `--priority-min`: Update minimum priority
- `--priority-max`: Update maximum priority
- `--owner`: Update owner filter
- `--labels`: Update labels filter
- `--default/--no-default`: Set/unset as default
- `--json`: Output in JSON format

**Examples:**
```bash
# Rename view
anyt view edit "High Priority" --name "Critical Tasks"

# Update filters
anyt view edit "High Priority" --priority-min 2

# Set as default
anyt view edit "My Tasks" --default

# Remove from default
anyt view edit "My Tasks" --no-default
```

### Delete View

```bash
anyt view rm <names>... [OPTIONS]
```

**Arguments:**
- `names`: One or more view names to delete

**Options:**
- `--force`, `-f`: Skip confirmation prompt
- `--json`: Output in JSON format

Shows extra warning when deleting default view. Requires confirmation unless `--force` is used.

**Examples:**
```bash
# Delete single view (with confirmation)
anyt view rm "Old View"

# Delete multiple views
anyt view rm "View1" "View2" --force

# Delete with JSON output
anyt view rm "Unused View" --json
```

### Set Default View

```bash
anyt view default <name>
anyt view default --clear
```

**Arguments:**
- `name`: View name to set as default (optional)

**Options:**
- `--clear`: Clear the current default view
- `--json`: Output in JSON format

**Examples:**
```bash
# Set default view
anyt view default "High Priority"

# Clear default view
anyt view default --clear
```

**Note:** Only one view can be set as default at a time. Setting a new default automatically clears the previous one.

---

## Template Management

Manage reusable task templates stored as markdown files. Templates help standardize task creation with predefined structure.

### Initialize Templates

```bash
anyt template init
```

Creates the template directory at `~/.config/anyt/templates/` and generates a default template with standard sections (Objectives, Acceptance Criteria, Technical Notes, etc.).

**Example:**
```bash
anyt template init
# Output: ✓ Template directory created
#         ✓ Default template created
```

### List Templates

```bash
anyt template list
```

Shows all available templates (`.md` files in the template directory) with size and last modified date.

**Example:**
```bash
anyt template list
# Output: Available Templates table with Name, Size, Modified columns
```

### Show Template

```bash
anyt template show [NAME]
```

**Arguments:**
- `NAME`: Template name to display (default: "default")

Displays the template content rendered as markdown.

**Examples:**
```bash
anyt template show default
anyt template show feature-template
```

### Edit Template

```bash
anyt template edit [NAME]
```

**Arguments:**
- `NAME`: Template name to edit (default: "default")

Opens the template file in your system's default editor (respects `$EDITOR` environment variable).

**Examples:**
```bash
anyt template edit default
export EDITOR=vim && anyt template edit feature-template
```

### Create Task from Template

```bash
anyt task create <title> [OPTIONS]
```

**Arguments:**
- `title`: Task title (required)

**Options:**
- `--template, -t`: Template name to use (default: "default")
- `--project`: Project ID (required)
- `--priority, -p`: Task priority (-2 to 2)
- `--owner`: Assign to user or agent ID
- `--json`: Output in JSON format

**Examples:**
```bash
anyt task create "Implement OAuth" --template feature-template --project 1 --priority 1
anyt task create "Fix login bug" -t bugfix --project 1 -p 2
```

The template content is loaded and used as the task's description, with placeholder variables replaced:
- `{datetime}` → Current timestamp (e.g., "2025-10-18 14:30")

**Template Location:** `~/.config/anyt/templates/`

---

## Board & Visualization

Visualize tasks and workspace in different views.

### Show Active Task

```bash
anyt active
```

Displays detailed information about the currently active task (set via `anyt task pick`).

### Kanban Board

```bash
anyt board [OPTIONS]
```

Display tasks in a Kanban board view with columns:
- Backlog
- Active
- Blocked (coming soon)
- Done

**Options:**
- `--mine`: Show only tasks assigned to you
- `--labels`: Filter by labels (comma-separated)
- `--status`: Filter by status (comma-separated)
- `--group-by`: Group by (`status`, `priority`, `owner`, `labels`) - default: `status`
- `--sort`: Sort within groups (`priority`, `updated_at`) - default: `priority`
- `--compact`: Compact display mode
- `--limit`: Max tasks per lane (default: 20)

**Examples:**
```bash
anyt board
anyt board --mine
anyt board --labels bug,auth
anyt board --compact
anyt board --group-by priority --sort updated_at
```

### Timeline View

```bash
anyt timeline <identifier> [OPTIONS]
```

Show chronological timeline of task events, attempts, and artifacts.

**Arguments:**
- `identifier`: Task identifier (e.g., `DEV-42`)

**Options:**
- `--events-only`: Show only events
- `--attempts-only`: Show only attempts
- `--since`: Show events since date (`YYYY-MM-DD`)
- `--last`: Show events from last N hours/days (e.g., `24h`, `7d`)
- `--show-artifacts`: Include artifact previews
- `--compact`: Compact format

**Examples:**
```bash
anyt timeline DEV-42
anyt timeline DEV-42 --last 24h
anyt timeline DEV-42 --events-only
```

**Note:** Full timeline API integration is pending.

### Workspace Summary

```bash
anyt summary [OPTIONS]
```

Generate workspace summary with done, active, blocked, and next priorities.

**Options:**
- `--period`: Summary period (`today`, `weekly`, `monthly`) - default: `today`
- `--format`: Output format (`text`, `markdown`, `json`) - default: `text`

**Examples:**
```bash
anyt summary
anyt summary --period weekly
anyt summary --format markdown > summary.md
```

Shows:
- ✅ Done tasks (top 5)
- 🔄 Active tasks (with owners and update times)
- 🚫 Blocked tasks
- 📅 Next priorities (top 3 by priority)
- Progress percentage

### Dependency Graph

```bash
anyt graph [IDENTIFIER] [OPTIONS]
```

Visualize task dependencies as ASCII art, DOT format, or JSON.

**Arguments:**
- `IDENTIFIER`: Task identifier to show dependencies for (optional - shows full workspace graph if omitted)

**Options:**
- `--format <format>`: Output format: `ascii` (default), `dot`, `json`
- `--status <statuses>`: Filter by status (comma-separated)
- `--priority-min <N>`: Filter by minimum priority
- `--labels <labels>`: Filter by labels (comma-separated)
- `--phase <phase>`: Filter by phase/milestone
- `--mine`: Show only tasks assigned to you
- `--depth <N>`: Max dependency depth to show
- `--compact`: Compact display mode
- `--json`: JSON output (same as `--format json`)

**Single Task Graph:**
```bash
# Show dependencies for specific task
anyt graph DEV-42

# Export single task graph as DOT format for Graphviz
anyt graph DEV-42 --format dot | dot -Tpng > task-graph.png
```

**Full Workspace Graph:**
```bash
# Show all tasks in workspace with dependencies
anyt graph

# Filter by status
anyt graph --status "inprogress,backlog"

# Show only high-priority tasks
anyt graph --priority-min 1

# Show my tasks with dependencies
anyt graph --mine

# Export workspace graph as PNG using Graphviz
anyt graph --format dot | dot -Tpng > workspace-graph.png

# Compact view
anyt graph --compact

# Limit dependency depth
anyt graph --depth 2

# JSON output for programmatic use
anyt graph --json

# Filter by phase
anyt graph --phase "Phase 1"
```

**Graph Features:**
- Displays dependency tree starting from root tasks (tasks with no dependencies)
- Shows task identifier, truncated title, and status symbol
- Detects and warns about circular dependencies
- Identifies orphaned tasks (tasks with no dependencies or dependents)
- Supports multiple output formats (ASCII, DOT for Graphviz, JSON)

**Status Indicators:**
- ✓ done
- • active/inprogress
- ○ backlog/todo
- ⚠ blocked

**Output Formats:**
- **ascii**: Tree-like ASCII art visualization (default)
- **dot**: Graphviz DOT format - pipe to `dot` command to generate images
- **json**: Structured JSON with nodes, edges, and metadata

**Single Task Display:**
When viewing a single task's dependencies, shows:
- Tasks this depends on (upstream dependencies)
- Current task
- Tasks that depend on this (downstream dependents)

**Full Workspace Display:**
When viewing the full workspace graph (no identifier), shows:
- Complete dependency tree for all tasks
- Root tasks (no dependencies) at the top
- Hierarchical dependency structure
- Orphaned tasks separately
- Total task and dependency counts
- Circular dependency warnings (if any)

---

## AI Commands

AI-powered task management features.

### Decompose Goal

```bash
anyt ai decompose <goal> [OPTIONS]
```

Decompose a goal into actionable tasks using AI.

**Arguments:**
- `goal`: Goal description or goal ID

**Options:**
- `--max-tasks`: Maximum number of tasks to generate (default: 10)
- `--task-size`: Preferred task size in hours (default: 4)
- `--dry-run`: Preview tasks without creating them
- `--json`: Output in JSON format

**Examples:**
```bash
anyt ai decompose "Add social login"
anyt ai decompose "Add social login" --dry-run
anyt ai decompose "Add social login" --max-tasks 10 --task-size 3
```

**Note:** API integration pending.

### Organize Workspace

```bash
anyt ai organize [OPTIONS]
```

Organize workspace tasks using AI:
- Normalize task titles to follow conventions
- Suggest appropriate labels for tasks
- Detect potential duplicate tasks

**Options:**
- `--dry-run`: Preview changes without applying them
- `--auto`: Apply all changes without confirmation
- `--titles-only`: Only normalize task titles
- `--json`: Output in JSON format

**Examples:**
```bash
anyt ai organize --dry-run
anyt ai organize --auto
anyt ai organize --titles-only
```

**Note:** API integration pending.

### Fill Task Details

```bash
anyt ai fill <identifier> [OPTIONS]
```

Fill in missing details for a task using AI.

**Arguments:**
- `identifier`: Task identifier (e.g., `DEV-42`)

**Options:**
- `--fields`: Comma-separated fields to fill (`description`, `acceptance`, `labels`)
- `--json`: Output in JSON format

**Examples:**
```bash
anyt ai fill DEV-42
anyt ai fill DEV-42 --fields description,acceptance
anyt ai fill DEV-42 --fields labels
```

**Note:** API integration pending.

### Suggest Tasks

```bash
anyt ai suggest [--json]
```

Get AI suggestions for next task to work on based on:
- Priority and dependencies
- Unblocking downstream tasks
- Quick wins and impact

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
anyt ai suggest
```

**Note:** API integration pending.

### Review Task

```bash
anyt ai review <identifier> [--json]
```

Get AI review of a task before marking done. Validates:
- Title follows naming convention
- Description is clear and complete
- All acceptance criteria met
- Dependencies satisfied
- Tests exist and pass

**Arguments:**
- `identifier`: Task identifier (e.g., `DEV-42`)

**Options:**
- `--json`: Output in JSON format

**Example:**
```bash
anyt ai review DEV-42
```

**Note:** API integration pending.

### Generate Summary

```bash
anyt ai summary [OPTIONS]
```

Generate workspace progress summary.

**Options:**
- `--period`: Summary period (`today`, `weekly`, `monthly`) - default: `today`
- `--format`: Output format (`text`, `markdown`, `slack`) - default: `text`

**Examples:**
```bash
anyt ai summary
anyt ai summary --period weekly
anyt ai summary --format markdown > summary.md
```

**Note:** API integration pending.

### AI Configuration

```bash
anyt ai config [OPTIONS]
```

Manage AI provider settings.

**Options:**
- `--show`: Show current AI configuration (default: true)
- `--model`: Set AI model
- `--max-tokens`: Set max tokens
- `--cache`: Enable/disable cache (`on`/`off`)

**Examples:**
```bash
anyt ai config
anyt ai config --model claude-3-5-sonnet-20241022
anyt ai config --max-tokens 8192
anyt ai config --cache on
```

**Default Configuration:**
- Provider: `anthropic`
- Model: `claude-3-5-sonnet-20241022`
- Max tokens: `4096`
- Temperature: `0.0`
- Cache enabled: `true`

### Test AI Connection

```bash
anyt ai test
```

Test AI connection and settings. Validates:
- API connectivity
- Model availability
- Prompt caching status

### AI Usage Tracking

```bash
anyt ai usage [OPTIONS]
```

Track AI token usage and costs.

**Options:**
- `--workspace`: Show workspace-level usage
- `--json`: Output in JSON format

**Examples:**
```bash
anyt ai usage
anyt ai usage --workspace
anyt ai usage --json
```

Shows:
- Operations breakdown (decompose, organize, fill, summary)
- Total calls, tokens, and costs
- Cache hit rate and savings

**Note:** Usage tracking implementation pending.

---

## Upcoming CLI Features

### Enhanced AI Commands (Coming Soon)

Several AI-powered commands have backend API support but are pending full CLI integration:

- `anyt ai decompose` - Decompose goals into tasks
- `anyt ai organize` - Normalize titles, suggest labels, detect duplicates
- `anyt ai fill` - Fill in missing task details
- `anyt ai suggest` - Get AI-powered task suggestions
- `anyt ai review` - Review task before marking done
- `anyt ai summary` - Generate progress summary

**Note:** Basic `anyt task suggest` (non-AI, score-based) is already implemented and available.

---

## MCP Integration

The AnyTask CLI provides Model Context Protocol (MCP) integration for Claude Code, allowing AI agents to interact with the task management system directly.

### Start MCP Server

```bash
anyt mcp serve
```

Starts an MCP server for Claude Code integration. The server runs in the foreground and communicates via stdio.

**Required Environment Variables:**
- `ANYTASK_API_KEY`: Agent API key for authentication
- `ANYTASK_API_URL`: Backend URL (default: http://0.0.0.0:8000)
- `ANYTASK_WORKSPACE_ID`: Workspace ID to operate in

**Example:**
```bash
export ANYTASK_API_KEY=anyt_agent_xxx
export ANYTASK_WORKSPACE_ID=1
anyt mcp serve
```

### Show MCP Configuration

```bash
anyt mcp config
```

Displays the configuration snippet to add to Claude Code's MCP settings file (`~/.config/claude/mcp.json`).

**Example Output:**
```json
{
  "mcpServers": {
    "anytask": {
      "command": "/path/to/anyt",
      "args": ["mcp", "serve"],
      "env": {
        "ANYTASK_API_URL": "http://0.0.0.0:8000",
        "ANYTASK_API_KEY": "YOUR_API_KEY_HERE",
        "ANYTASK_WORKSPACE_ID": "YOUR_WORKSPACE_ID"
      }
    }
  }
}
```

**Setup Steps:**
1. Replace `YOUR_API_KEY_HERE` with your agent API key
2. Replace `YOUR_WORKSPACE_ID` with your workspace ID
3. Get an agent key with: `anyt auth agent-key create`
4. Get your workspace ID with: `anyt workspace list`

### Test MCP Connection

```bash
anyt mcp test
```

Tests the MCP server connection to verify:
- API client initialization
- Workspace access
- Project access
- Available tools (8 tools: list_tasks, select_task, create_task, update_task, start_attempt, finish_attempt, add_artifact, get_board)
- Available resources (4 resource templates)

**Example:**
```bash
$ anyt mcp test
Testing MCP server connection...
✓ API client initialized
✓ Connected to workspace: DEV
✓ Connected to project: PROJ-1
✓ 8 tools available:
  - list_tasks
  - select_task
  - create_task
  - update_task
  - start_attempt
  - finish_attempt
  - add_artifact
  - get_board
✓ 4 resource templates available

✓ All tests passed!
```

---

## Configuration

### Configuration Files

The CLI stores configuration in:
- **Global config**: `~/.config/anyt/config.json`
  - Environments
  - Current environment
  - Authentication tokens
- **Workspace config**: `.anyt/anyt.json`
  - Workspace ID
  - Workspace name
  - API URL
- **Active task**: `.anyt/active_task.json`
  - Current active task
  - Pick timestamp

### Environment Variables

Override configuration with environment variables:
- `ANYT_ENV`: Override current environment
- `ANYT_API_URL`: Override API URL
- `ANYT_AUTH_TOKEN`: Override auth token
- `ANYT_AGENT_KEY`: Agent API key (also used as default for `anyt auth login`)

**Examples:**
```bash
# Override environment
ANYT_ENV=prod anyt task list

# Override API URL
ANYT_API_URL=http://localhost:8000 anyt board

# Use agent key from environment (most common for CI/CD)
export ANYT_AGENT_KEY=anyt_agent_O1HFI42vTa442u6XSCAZISxLVoW8Xd7j
anyt auth login  # Automatically uses ANYT_AGENT_KEY
anyt task list

# Override auth token
ANYT_AUTH_TOKEN=anyt_token_... anyt task list
```

### JSON Output Mode

Most commands support `--json` flag for machine-readable output:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "ErrorType",
  "message": "Error description",
  "suggestions": [ ... ]
}
```

---

## Tips & Best Practices

### Task Identifiers

The CLI supports flexible task identifier formats:
- `DEV-42` - Full identifier (workspace prefix + number)
- `dev42` - Case insensitive, no dash
- `42` - Just the number
- `DEV 42` - With space

All are automatically normalized.

### Active Task Workflow

Pick a task to make it the default for subsequent commands:

```bash
anyt task pick DEV-42
anyt task show        # Shows DEV-42
anyt task edit --status inprogress
anyt task dep list
anyt task done        # Marks DEV-42 as done and clears active
```

### Bulk Operations

Edit multiple tasks at once:

```bash
# Mark multiple tasks as done
anyt task done DEV-42 DEV-43 DEV-44

# Bulk edit status
anyt task edit --ids DEV-42,DEV-43,DEV-44 --status inprogress

# Delete multiple tasks
anyt task rm DEV-42 DEV-43 --force
```

### Optimistic Locking

Prevent lost updates with version checking:

```bash
# Get current version
anyt task show DEV-42 --json | jq '.data.version'
# Output: 5

# Update with version check
anyt task edit DEV-42 --status done --if-match 5
```

If another user modifies the task in the meantime, the edit will fail with a version conflict error.

### Dependency Management

Build complex task graphs:

```bash
# Create tasks
anyt task add "Setup database" --project 1 --priority 2
anyt task add "Create models" --project 1 --priority 1
anyt task add "Build API" --project 1 --priority 1

# Link dependencies
anyt task dep add DEV-2 --on DEV-1  # Models depend on database
anyt task dep add DEV-3 --on DEV-2  # API depends on models

# Visualize
anyt graph DEV-3
```

### Board Filters

Focus on what matters:

```bash
# My high-priority bugs
anyt board --mine --labels bug --sort priority

# All in-progress tasks
anyt board --status inprogress

# Compact view for quick overview
anyt board --compact
```

---

## Troubleshooting

### Not authenticated

```
Error: Not authenticated
```

**Solution:** Login first
```bash
anyt auth login --token
```

### Not in a workspace directory

```
Error: Not in a workspace directory
```

**Solution:** Initialize workspace
```bash
anyt workspace init
```

### Task not found

```
Error: Task 'DEV-42' not found
```

**Solution:** Check task list
```bash
anyt task list
anyt task show DEV-42  # Shows suggestions for similar tasks
```

### Connection failed

```
Error: Connection failed
```

**Solution:** Check environment configuration
```bash
anyt env show
anyt env list  # Verify API URL and connectivity
```

---

## Examples

### Complete Workflow Example

```bash
# 1. Setup
anyt env add dev http://localhost:8000
anyt auth login --token
anyt init

# 2. Verify connection
anyt health

# 3. Create tasks
anyt task add "Design authentication system" --project 1 --priority 2
anyt task add "Implement JWT tokens" --project 1 --priority 1
anyt task add "Add login endpoint" --project 1 --priority 1

# 4. Link dependencies
anyt task dep add DEV-2 --on DEV-1
anyt task dep add DEV-3 --on DEV-2

# 5. Work on tasks
anyt board
anyt task pick DEV-1
anyt task edit --status inprogress
anyt task done

# 6. Continue with next task
anyt task pick DEV-2
anyt task edit --status inprogress
anyt task done

# 7. View progress
anyt summary
anyt graph DEV-3
```

### Agent Integration Example

```bash
# 1. Login as agent (multiple methods)

# Method A: Direct value (best for scripts/automation)
anyt auth login --agent-key-value anyt_agent_O1HFI42vTa442u6XSCAZISxLVoW8Xd7j

# Method B: Environment variable (best for CI/CD)
export ANYT_AGENT_KEY=anyt_agent_O1HFI42vTa442u6XSCAZISxLVoW8Xd7j
anyt auth login

# Method C: Interactive prompt
anyt auth login --agent-key
# Enter: anyt_agent_xxxxxxxxxxxxxxxxxxxxx

# 2. Initialize workspace
anyt init

# 3. Agent creates tasks
anyt task add "Automated test run" --owner agent-001 --project 1

# 4. Agent reports progress
anyt task edit DEV-42 --status inprogress
anyt task done DEV-42

# 5. Human reviews agent's work
anyt board --status done
anyt timeline DEV-42
```

---

## Version

CLI Version: `0.1.0`

For bug reports and feature requests, visit: https://github.com/supercarl87/AnyTaskBackend

---

## See Also

- [Repository Pattern Documentation](REPOSITORY_PATTERN.md)
- [API Documentation](server_api.md)
- [CLAUDE.md](../CLAUDE.md) - Project overview and development guide
