# AnyTask CLI - Complete Command Reference

Auto-generated from Typer app introspection.

================================================================================


## anyt

--------------------------------------------------------------------------------

AnyTask - AI-native task management from the command line

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```

**Parameters:**

  **--version / -v** [Option]
    Show version and exit
  **--install-completion** [Option]
    Install completion for the current shell.
  **--show-completion** [Option]
    Show completion for the current shell, to copy it or customize the installation.


**Subcommands:**

- `active`
- `ai`
- `auth`
- `board`
- `env`
- `graph`
- `health`
- `init`
- `label`
- `preference`
- `project`
- `summary`
- `task`
- `template`
- `timeline`
- `view`
- `workspace`


### anyt active

--------------------------------------------------------------------------------

Show the currently active task.

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


### anyt ai

--------------------------------------------------------------------------------

AI-powered task management

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `config`
- `decompose`
- `fill`
- `organize`
- `review`
- `suggest`
- `summary`
- `test`
- `usage`


#### anyt ai config

--------------------------------------------------------------------------------

Manage AI provider settings.

Examples:
    anyt ai config
    anyt ai config --model claude-3-5-sonnet-20241022
    anyt ai config --max-tokens 8192
    anyt ai config --cache on

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--show** [Option]
    Show current AI configuration
  **--model** [Option]
    Set AI model
  **--max-tokens** [Option]
    Set max tokens
  **--cache** [Option]
    Enable/disable cache (on/off)


================================================================================


#### anyt ai decompose

--------------------------------------------------------------------------------

Decompose a goal into actionable tasks using AI.

Examples:
    anyt ai decompose "Add social login"
    anyt ai decompose "Add social login" --dry-run
    anyt ai decompose "Add social login" --max-tasks 10 --task-size 3

**Usage:**
```
Usage:  [OPTIONS] GOAL
```

**Parameters:**

  **goal** [Argument]
    Goal description or goal ID
  **--max-tasks** [Option]
    Maximum number of tasks to generate
  **--task-size** [Option]
    Preferred task size in hours
  **--dry-run** [Option]
    Preview tasks without creating them
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt ai fill

--------------------------------------------------------------------------------

Fill in missing details for a task using AI.

Examples:
    anyt ai fill DEV-42
    anyt ai fill DEV-42 --fields description,acceptance
    anyt ai fill DEV-42 --fields labels

**Usage:**
```
Usage:  [OPTIONS] IDENTIFIER
```

**Parameters:**

  **identifier** [Argument]
    Task identifier (e.g., DEV-42)
  **--fields** [Option]
    Comma-separated fields to fill (description,acceptance,labels)
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt ai organize

--------------------------------------------------------------------------------

Organize workspace tasks using AI.

This command analyzes your workspace and suggests improvements:
- Normalize task titles to follow conventions
- Suggest appropriate labels for tasks
- Detect potential duplicate tasks

Examples:
    anyt ai organize --dry-run
    anyt ai organize --auto
    anyt ai organize --titles-only

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--dry-run** [Option]
    Preview changes without applying them
  **--auto** [Option]
    Apply all changes without confirmation
  **--titles-only** [Option]
    Only normalize task titles
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt ai review

--------------------------------------------------------------------------------

Get AI review of a task before marking done.

Validates:
- Title follows naming convention
- Description is clear and complete
- All acceptance criteria met
- Dependencies satisfied
- Tests exist and pass

**Usage:**
```
Usage:  [OPTIONS] IDENTIFIER
```

**Parameters:**

  **identifier** [Argument]
    Task identifier (e.g., DEV-42)
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt ai suggest

--------------------------------------------------------------------------------

Get AI suggestions for next task to work on.

Analyzes the workspace and recommends tasks based on:
- Priority and dependencies
- Unblocking downstream tasks
- Quick wins and impact

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt ai summary

--------------------------------------------------------------------------------

Generate workspace progress summary.

Examples:
    anyt ai summary
    anyt ai summary --period weekly
    anyt ai summary --format markdown > summary.md

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--period** [Option]
    Summary period (today, weekly, monthly)
  **--format** [Option]
    Output format (text, markdown, slack)


================================================================================


#### anyt ai test

--------------------------------------------------------------------------------

Test AI connection and settings.

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


#### anyt ai usage

--------------------------------------------------------------------------------

Track AI token usage and costs.

Examples:
    anyt ai usage
    anyt ai usage --workspace
    anyt ai usage --json

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--workspace** [Option]
    Show workspace-level usage
  **--json** [Option]
    Output in JSON format


================================================================================


================================================================================


### anyt auth

--------------------------------------------------------------------------------

Manage authentication

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `login`
- `logout`
- `whoami`


#### anyt auth login

--------------------------------------------------------------------------------

Login to AnyTask API.

Supports multiple authentication flows:
- Agent API key (--agent-key with value or from ANYT_AGENT_KEY env var)
- Personal Access Token (--token with value)
- Interactive prompt if flags provided without values

Examples:
    anyt auth login --agent-key anyt_agent_...
    anyt auth login --token anyt_...
    anyt auth login  # Uses ANYT_AGENT_KEY if set

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--env / -e** [Option]
    Environment to login to
  **--token** [Option]
    Login with Personal Access Token (prompts for value)
  **--agent-key** [Option]
    Login with agent API key (prompts for value)
  **--token-value** [Option]
    Personal Access Token value (skips prompt)
  **--agent-key-value** [Option]
    Agent API key value (skips prompt)


================================================================================


#### anyt auth logout

--------------------------------------------------------------------------------

Logout from AnyTask API.

Clears stored authentication credentials for the specified environment
or all environments.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--env / -e** [Option]
    Environment to logout from
  **--all** [Option]
    Logout from all environments


================================================================================


#### anyt auth whoami

--------------------------------------------------------------------------------

Show information about the currently authenticated user or agent.

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


================================================================================


### anyt board

--------------------------------------------------------------------------------

Display tasks in a Kanban board view.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--mine** [Option]
    Show only tasks assigned to you
  **--labels** [Option]
    Filter by labels (comma-separated)
  **--status** [Option]
    Filter by status (comma-separated)
  **--phase** [Option]
    Filter by phase/milestone
  **--group-by** [Option]
    Group by: status, priority, owner, labels
  **--sort** [Option]
    Sort within groups: priority, updated_at
  **--compact** [Option]
    Compact display mode
  **--limit** [Option]
    Max tasks per lane
  **--json** [Option]
    Output in JSON format


================================================================================


### anyt env

--------------------------------------------------------------------------------

Manage CLI environments

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `add`
- `list`
- `remove`
- `show`
- `switch`
- `use`


#### anyt env add

--------------------------------------------------------------------------------

Add a new environment.

**Usage:**
```
Usage:  [OPTIONS] NAME API_URL
```

**Parameters:**

  **name** [Argument]
    Environment name (e.g., 'dev', 'prod')
  **api_url** [Argument]
    API base URL
  **--active** [Option]
    Make this the active environment


================================================================================


#### anyt env list

--------------------------------------------------------------------------------

List all configured environments.

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


#### anyt env remove

--------------------------------------------------------------------------------

Remove an environment.

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    Environment name to remove
  **--force / -f** [Option]
    Skip confirmation prompt


================================================================================


#### anyt env show

--------------------------------------------------------------------------------

Show the current environment configuration.

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


#### anyt env switch

--------------------------------------------------------------------------------

Switch to a different environment.

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    Environment name to switch to


================================================================================


#### anyt env use

--------------------------------------------------------------------------------

Switch to a different environment (alias for 'switch').

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    Environment name to switch to


================================================================================


================================================================================


### anyt graph

--------------------------------------------------------------------------------

Visualize task dependencies as ASCII art or DOT format.

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIER]
```

**Parameters:**

  **identifier** [Argument]
    Task identifier to show dependencies for (shows all if not specified)
  **--full** [Option]
    Show all tasks in workspace
  **--format** [Option]
    Output format: ascii, dot, json
  **--status** [Option]
    Filter by status (comma-separated)
  **--priority-min** [Option]
    Filter by minimum priority
  **--labels** [Option]
    Filter by labels (comma-separated)
  **--phase** [Option]
    Filter by phase/milestone
  **--mine** [Option]
    Show only tasks assigned to you
  **--depth** [Option]
    Max dependency depth to show
  **--compact** [Option]
    Compact display mode
  **--json** [Option]
    Output in JSON format


================================================================================


### anyt health

--------------------------------------------------------------------------------

Check backend server health

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `check`


#### anyt health check

--------------------------------------------------------------------------------

Check if the AnyTask backend server is healthy.

Calls the /health endpoint on the configured API server
and displays the server status.

Examples:
    anyt health          # Check current environment
    anyt health check    # Explicit check command

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


================================================================================


### anyt init

--------------------------------------------------------------------------------

Initialize AnyTask in the current directory.

Creates .anyt/ directory and sets up workspace configuration.
Links an existing workspace or creates a new one.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--create** [Option]
    Create a new workspace with the given name
  **--identifier / -i** [Option]
    Workspace identifier (required when creating)
  **--dir / -d** [Option]
    Directory to initialize (default: current)


================================================================================


### anyt label

--------------------------------------------------------------------------------

Manage workspace labels

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `create`
- `edit`
- `list`
- `rm`
- `show`


#### anyt label create

--------------------------------------------------------------------------------

Create a new label in the workspace.

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    Label name
  **--color** [Option]
    Hex color code (e.g., #FF0000)
  **--description** [Option]
    Label description
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt label edit

--------------------------------------------------------------------------------

Edit label properties.

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    Label name
  **--name** [Option]
    New label name
  **--color** [Option]
    New color (hex code)
  **--description** [Option]
    New description
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt label list

--------------------------------------------------------------------------------

List all labels in the workspace.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt label rm

--------------------------------------------------------------------------------

Delete one or more labels.

**Usage:**
```
Usage:  [OPTIONS] NAMES...
```

**Parameters:**

  **names** [Argument]
    Label name(s) to delete
  **--force / -f** [Option]
    Skip confirmation
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt label show

--------------------------------------------------------------------------------

Show details for a specific label.

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    Label name
  **--json** [Option]
    Output in JSON format


================================================================================


================================================================================


### anyt preference

--------------------------------------------------------------------------------

Manage user preferences for workspace and project

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `clear`
- `set-project`
- `set-workspace`
- `show`


#### anyt preference clear

--------------------------------------------------------------------------------

Clear user preferences (reset workspace and project).

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


#### anyt preference set-project

--------------------------------------------------------------------------------

Set the current project (and workspace) preference.

**Usage:**
```
Usage:  [OPTIONS] WORKSPACE_ID PROJECT_ID
```

**Parameters:**

  **workspace_id** [Argument]
    Workspace ID containing the project
  **project_id** [Argument]
    Project ID to set as current


================================================================================


#### anyt preference set-workspace

--------------------------------------------------------------------------------

Set the current workspace preference.

**Usage:**
```
Usage:  [OPTIONS] WORKSPACE_ID
```

**Parameters:**

  **workspace_id** [Argument]
    Workspace ID to set as current


================================================================================


#### anyt preference show

--------------------------------------------------------------------------------

Show current user preferences (workspace and project).

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


================================================================================


### anyt project

--------------------------------------------------------------------------------

Manage projects

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `create`
- `current`
- `list`
- `switch`
- `use`


#### anyt project create

--------------------------------------------------------------------------------

Create a new project in a workspace.

Creates a project with the given name and identifier.
By default, uses the workspace from the current directory's anyt.json.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--name / -n** [Option]
    Project name
  **--identifier / -i** [Option]
    Project identifier (e.g., API)
  **--description / -d** [Option]
    Project description
  **--workspace / -w** [Option]
    Workspace ID or identifier (default: current workspace)
  **--dir** [Option]
    Directory with workspace config (default: current)


================================================================================


#### anyt project current

--------------------------------------------------------------------------------

Show the current project for a workspace.

Displays the current project based on user preferences.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--workspace / -w** [Option]
    Workspace ID or identifier (default: current workspace)
  **--dir** [Option]
    Directory with workspace config (default: current)


================================================================================


#### anyt project list

--------------------------------------------------------------------------------

List all projects in a workspace.

By default, lists projects in the workspace from the current directory's anyt.json.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--workspace / -w** [Option]
    Workspace ID or identifier (default: current workspace)
  **--dir** [Option]
    Directory with workspace config (default: current)


================================================================================


#### anyt project switch

--------------------------------------------------------------------------------

Interactively switch the current project.

Displays a list of projects and allows you to select one.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--workspace / -w** [Option]
    Workspace ID or identifier (default: current workspace)
  **--dir** [Option]
    Directory with workspace config (default: current)


================================================================================


#### anyt project use

--------------------------------------------------------------------------------

Set the current project for a workspace.

Updates user preferences to make this the default project.

**Usage:**
```
Usage:  [OPTIONS] PROJECT
```

**Parameters:**

  **project** [Argument]
    Project ID or identifier to set as current
  **--workspace / -w** [Option]
    Workspace ID or identifier (default: current workspace)
  **--dir** [Option]
    Directory with workspace config (default: current)


================================================================================


================================================================================


### anyt summary

--------------------------------------------------------------------------------

Generate workspace summary with done, active, blocked, and next priorities.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--period** [Option]
    Summary period: today, weekly, monthly
  **--phase** [Option]
    Filter by phase/milestone
  **--format** [Option]
    Output format: text, markdown, json
  **--json** [Option]
    Output in JSON format


================================================================================


### anyt task

--------------------------------------------------------------------------------

Manage tasks

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `add`
- `create`
- `dep`
- `done`
- `edit`
- `list`
- `note`
- `pick`
- `rm`
- `share`
- `show`
- `suggest`


#### anyt task add

--------------------------------------------------------------------------------

Create a new task.

**Usage:**
```
Usage:  [OPTIONS] TITLE
```

**Parameters:**

  **title** [Argument]
    Task title
  **-d / --description** [Option]
    Task description
  **--phase** [Option]
    Phase/milestone identifier (e.g., T3, Phase 1)
  **-p / --priority** [Option]
    Priority (-2 to 2, default: 0)
  **--labels** [Option]
    Comma-separated labels
  **--status** [Option]
    Task status (default: backlog)
  **--owner** [Option]
    Assign to user or agent ID
  **--estimate** [Option]
    Time estimate in hours
  **--project** [Option]
    Project ID (uses current/default project if not specified)
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task create

--------------------------------------------------------------------------------

Create a new task from a template.

Opens the template in your editor ($EDITOR) for customization before creating the task.
The template content will be stored in the task's description field.

**Usage:**
```
Usage:  [OPTIONS] TITLE
```

**Parameters:**

  **title** [Argument]
    Task title
  **--template / -t** [Option]
    Template name to use (default: default)
  **--phase** [Option]
    Phase/milestone identifier (e.g., T3, Phase 1)
  **-p / --priority** [Option]
    Priority (-2 to 2, default: 0)
  **--project** [Option]
    Project ID (uses current/default project if not specified)
  **--no-edit** [Option]
    Skip opening editor, use template as-is
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task dep

--------------------------------------------------------------------------------

Manage task dependencies

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `add`
- `list`
- `rm`


##### anyt task dep add

--------------------------------------------------------------------------------

Add dependency/dependencies to a task.

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIER]
```

**Parameters:**

  **--on** [Option]
    Task(s) this depends on (comma-separated identifiers)
  **identifier** [Argument]
    Task identifier (e.g., DEV-43) or ID. Uses active task if not specified.
  **--json** [Option]
    Output in JSON format


================================================================================


##### anyt task dep list

--------------------------------------------------------------------------------

List task dependencies and dependents.

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIER]
```

**Parameters:**

  **identifier** [Argument]
    Task identifier (e.g., DEV-43) or ID. Uses active task if not specified.
  **--json** [Option]
    Output in JSON format


================================================================================


##### anyt task dep rm

--------------------------------------------------------------------------------

Remove dependency/dependencies from a task.

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIER]
```

**Parameters:**

  **--on** [Option]
    Task(s) to remove dependency on (comma-separated identifiers)
  **identifier** [Argument]
    Task identifier (e.g., DEV-43) or ID. Uses active task if not specified.
  **--json** [Option]
    Output in JSON format


================================================================================


================================================================================


#### anyt task done

--------------------------------------------------------------------------------

Mark one or more tasks as done.

Optionally add a completion note to the task's Events section.

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIERS]...
```

**Parameters:**

  **identifiers** [Argument]
    Task identifier(s) (e.g., DEV-42 DEV-43). Uses active task if not specified.
  **--note / -n** [Option]
    Add a completion note to the task
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task edit

--------------------------------------------------------------------------------

Edit a task's fields.

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIER]
```

**Parameters:**

  **identifier** [Argument]
    Task identifier (e.g., DEV-42) or ID. Uses active task if not specified.
  **--title** [Option]
    New title
  **-d / --description** [Option]
    New description
  **--status** [Option]
    New status
  **-p / --priority** [Option]
    New priority (-2 to 2)
  **--labels** [Option]
    Comma-separated labels (replaces all labels)
  **--owner** [Option]
    New owner ID
  **--estimate** [Option]
    New time estimate in hours
  **--ids** [Option]
    Multiple task IDs to edit (comma-separated)
  **--if-match** [Option]
    Expected version for optimistic concurrency control
  **--dry-run** [Option]
    Preview changes without applying
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task list

--------------------------------------------------------------------------------

List tasks with filtering.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--status** [Option]
    Filter by status (comma-separated)
  **--phase** [Option]
    Filter by phase/milestone
  **--mine** [Option]
    Show only tasks assigned to you
  **--labels** [Option]
    Filter by labels (comma-separated)
  **--sort** [Option]
    Sort field (priority, updated_at, created_at, status)
  **--order** [Option]
    Sort order (asc/desc)
  **--limit** [Option]
    Max number of tasks to show
  **--offset** [Option]
    Pagination offset
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task note

--------------------------------------------------------------------------------

Add a timestamped note/event to a task's description.

The note will be appended to the Events section of the task description
with a timestamp.

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIER]
```

**Parameters:**

  **identifier** [Argument]
    Task identifier (e.g., DEV-42) or use active task
  **--message / -m** [Option]
    Note message to append
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task pick

--------------------------------------------------------------------------------

Pick a task to work on (sets as active task).

If identifier is provided, picks that specific task.
Otherwise, shows an interactive picker to select a task.

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIER]
```

**Parameters:**

  **identifier** [Argument]
    Task identifier (e.g., DEV-42) or ID. Leave empty for interactive picker.
  **--status** [Option]
    Filter by status (comma-separated)
  **--project** [Option]
    Filter by project ID
  **--mine** [Option]
    Show only tasks assigned to you
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task rm

--------------------------------------------------------------------------------

Delete one or more tasks (soft delete).

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIERS]...
```

**Parameters:**

  **identifiers** [Argument]
    Task identifier(s) (e.g., DEV-42 DEV-43). Uses active task if not specified.
  **--force / -f** [Option]
    Skip confirmation prompt
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task share

--------------------------------------------------------------------------------

Generate a shareable link for a task.

Creates a public URL that can be shared with anyone who has access to the task.
The link uses the task's public ID for global accessibility.

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIER]
```

**Parameters:**

  **identifier** [Argument]
    Task identifier (e.g., DEV-42, 123456789 for public ID). Uses active task if not specified.
  **--copy / -c** [Option]
    Copy link to clipboard
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task show

--------------------------------------------------------------------------------

Show detailed information about a task.

Supports both workspace-scoped identifiers (DEV-42) and public IDs (123456789).

**Usage:**
```
Usage:  [OPTIONS] [IDENTIFIER]
```

**Parameters:**

  **identifier** [Argument]
    Task identifier (e.g., DEV-42, 123456789 for public ID). Uses active task if not specified.
  **--workspace / -w** [Option]
    Workspace identifier or ID (uses current workspace if not specified)
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt task suggest

--------------------------------------------------------------------------------

Suggest tasks to work on next based on priority, dependencies, and impact.

Analyzes available tasks and recommends the best ones to work on.
Considers:
- Priority (higher priority scores better)
- Status (todo/backlog preferred)
- Dependencies (filters out blocked tasks, prefers ready tasks)
- Impact (prefers tasks that unblock others)

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--limit** [Option]
    Number of suggestions to return
  **--status** [Option]
    Filter by status (comma-separated)
  **--json** [Option]
    Output in JSON format


================================================================================


================================================================================


### anyt template

--------------------------------------------------------------------------------

Manage task templates

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `edit`
- `init`
- `list`
- `show`


#### anyt template edit

--------------------------------------------------------------------------------

Open template in editor.

Opens the template file in the system's default editor
(respects $EDITOR environment variable).

Args:
    name: Name of the template to edit (default: "default")

**Usage:**
```
Usage:  [OPTIONS] [NAME]
```

**Parameters:**

  **name** [Argument]
    Template name to edit


================================================================================


#### anyt template init

--------------------------------------------------------------------------------

Initialize template directory with default template.

Creates the template directory at ~/.config/anyt/templates/
and creates a default.md template if it doesn't exist.

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


#### anyt template list

--------------------------------------------------------------------------------

List available templates.

Shows all .md files in the template directory.

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


#### anyt template show

--------------------------------------------------------------------------------

Display template content.

Args:
    name: Name of the template to display (default: "default")

**Usage:**
```
Usage:  [OPTIONS] [NAME]
```

**Parameters:**

  **name** [Argument]
    Template name to display


================================================================================


================================================================================


### anyt timeline

--------------------------------------------------------------------------------

Show chronological timeline of task events, attempts, and artifacts.

**Usage:**
```
Usage:  [OPTIONS] IDENTIFIER
```

**Parameters:**

  **identifier** [Argument]
    Task identifier (e.g., DEV-42)
  **--events-only** [Option]
    Show only events
  **--attempts-only** [Option]
    Show only attempts
  **--since** [Option]
    Show events since date (YYYY-MM-DD)
  **--last** [Option]
    Show events from last N hours/days (e.g., 24h, 7d)
  **--show-artifacts** [Option]
    Include artifact previews
  **--compact** [Option]
    Compact format
  **--json** [Option]
    Output in JSON format


================================================================================


### anyt view

--------------------------------------------------------------------------------

Manage saved task views (filters)

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `apply`
- `create`
- `default`
- `edit`
- `list`
- `rm`
- `show`


#### anyt view apply

--------------------------------------------------------------------------------

Apply a saved view and display matching tasks.

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    View name
  **--limit** [Option]
    Max tasks to show
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt view create

--------------------------------------------------------------------------------

Create a new saved task view (filter).

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    View name
  **--status** [Option]
    Filter by status (comma-separated)
  **--priority-min** [Option]
    Minimum priority
  **--priority-max** [Option]
    Maximum priority
  **--owner** [Option]
    Filter by owner
  **--labels** [Option]
    Filter by labels (comma-separated)
  **--default** [Option]
    Set as default view
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt view default

--------------------------------------------------------------------------------

Set or clear the default task view.

**Usage:**
```
Usage:  [OPTIONS] [NAME]
```

**Parameters:**

  **name** [Argument]
    View name to set as default
  **--clear** [Option]
    Clear default view
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt view edit

--------------------------------------------------------------------------------

Edit a saved view.

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    View name
  **--name** [Option]
    New view name
  **--status** [Option]
    Update status filter (comma-separated)
  **--priority-min** [Option]
    Update min priority
  **--priority-max** [Option]
    Update max priority
  **--owner** [Option]
    Update owner filter
  **--labels** [Option]
    Update labels filter (comma-separated)
  **--default** [Option]
    Set/unset as default
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt view list

--------------------------------------------------------------------------------

List all saved task views.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt view rm

--------------------------------------------------------------------------------

Delete one or more saved views.

**Usage:**
```
Usage:  [OPTIONS] NAMES...
```

**Parameters:**

  **names** [Argument]
    View name(s) to delete
  **--force / -f** [Option]
    Skip confirmation
  **--json** [Option]
    Output in JSON format


================================================================================


#### anyt view show

--------------------------------------------------------------------------------

Show details for a specific view.

**Usage:**
```
Usage:  [OPTIONS] NAME
```

**Parameters:**

  **name** [Argument]
    View name
  **--json** [Option]
    Output in JSON format


================================================================================


================================================================================


### anyt workspace

--------------------------------------------------------------------------------

Manage workspaces

**Usage:**
```
Usage:  [OPTIONS] COMMAND [ARGS]...
```


**Subcommands:**

- `current`
- `init`
- `list`
- `switch`
- `use`


#### anyt workspace current

--------------------------------------------------------------------------------

Show the current workspace for the active environment.

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


#### anyt workspace init

--------------------------------------------------------------------------------

Initialize a workspace in the current directory.

Links an existing workspace or creates a new one.
Creates anyt.json workspace configuration file.

**Usage:**
```
Usage:  [OPTIONS]
```

**Parameters:**

  **--create** [Option]
    Create a new workspace with the given name
  **--identifier / -i** [Option]
    Workspace identifier (required when creating)
  **--dir / -d** [Option]
    Directory to initialize (default: current)


================================================================================


#### anyt workspace list

--------------------------------------------------------------------------------

List all accessible workspaces.

**Usage:**
```
Usage:  [OPTIONS]
```


================================================================================


#### anyt workspace switch

--------------------------------------------------------------------------------

Switch the active workspace for the current directory.

This updates the anyt.json file to point to a different workspace.

**Usage:**
```
Usage:  [OPTIONS] [WORKSPACE_ID]
```

**Parameters:**

  **workspace_id** [Argument]
    Workspace ID or identifier to switch to
  **--dir / -d** [Option]
    Directory to switch workspace in (default: current)


================================================================================


#### anyt workspace use

--------------------------------------------------------------------------------

Set the current workspace for the active environment.

This sets the default workspace that will be used for all task operations
when no explicit workspace is specified via --workspace flag.

**Usage:**
```
Usage:  [OPTIONS] WORKSPACE
```

**Parameters:**

  **workspace** [Argument]
    Workspace ID or identifier to set as current


================================================================================


================================================================================


================================================================================
