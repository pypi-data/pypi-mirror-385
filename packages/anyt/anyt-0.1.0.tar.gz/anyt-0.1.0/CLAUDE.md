# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AnyTask CLI is an AI-native task management command-line interface built with Typer and Rich. It provides Linear-style task management with agent-aware features, MCP (Model Context Protocol) integration, and powerful AI-assisted commands for coding agents and human developers.

## Common Development Commands

### Package Management
- **Install dependencies**: `make install` (uses uv, not pip)
- **Clean Python cache**: `make clean`

### Code Quality
- **Lint code**: `make lint` (runs ruff check)
- **Format code**: `make format` (runs ruff format)
- **Type check**: `make typecheck` (runs mypy on src/ and tests/)

### Testing
- **Run all tests**: `make test` (runs unit tests only by default)
- **Run unit tests**: `make test-cli-unit` (no backend required, uses mocks)
- **Run integration tests**: `make test-cli-integration` (requires backend server + authentication)
  - Set `ANYT_TEST_TOKEN` environment variable with a valid JWT token
  - Optionally set `ANYT_TEST_API_URL` (default: http://localhost:8000)
  - Tests will be skipped if authentication is not configured
  - See `tests/cli/integration/README.md` for detailed setup instructions
- **Run specific test file**: `uv run pytest tests/cli/unit/test_core_commands.py -v`
- **Run specific test**: `uv run pytest tests/cli/unit/test_core_commands.py::test_env_add -v`

### Build & Distribution
- **Build package**: `make build` (creates wheel and sdist in dist/)
- **Install locally**: `make install-local` (installs from source for development)
- **Publish to PyPI**: `make publish` (requires credentials)

## Development Workflow & Task Management

This project uses a structured task management system in `.anyt/tasks/` to track development work. **IMPORTANT**: Only code edits and new features constitute tasks. Minor commits, linting, formatting, documentation updates, and design discussions are NOT tracked as tasks.

### Task Directory Structure

```
.anyt/tasks/
├── README.md        # Overview of all tasks and phases
├── active/          # Currently active task (max 1 task)
├── backlog/         # Pending tasks to be worked on
├── done/            # Completed tasks
└── cancelled/       # Cancelled tasks
```

### Task File Format

Tasks are markdown files named `T{stage}-{id}-Title.md` (e.g., `T3-2-CLI-Task-Commands.md`).

Task ID format follows:
- `T{stage}-{id}` where stage represents the project phase (3, 4, 7 for CLI)
- Sequential IDs within each stage: `T3-4` → `T3-5` (same phase)
- New phases start at 1: `T3-5` → `T4-1` (new phase)

Each task file contains:
- **Priority**: High/Medium/Low
- **Status**: Pending/In Progress/Completed
- **Description**: What needs to be built
- **Objectives**: Specific goals
- **Acceptance Criteria**: Checklist of requirements
- **Dependencies**: Required tasks (e.g., "T3-1: CLI Foundation")
- **Estimated Effort**: Time estimate
- **Technical Notes**: Implementation guidance

### Workflow Rules

When starting work on a feature or code edit:

1. **Check for active task**: Look in `.anyt/tasks/active/`
   - If there's an active task AND current work matches that task:
     - Update the task's **Status** field
     - Add an event entry at the bottom of the task file documenting progress
     - Continue working on the task

2. **Check backlog for matching task**: Look in `.anyt/tasks/backlog/`
   - If current work matches a backlog task:
     - Move the task file from `backlog/` to `active/`
     - Update status to "In Progress"
     - Add an event entry marking start of work
     - Begin implementation

3. **Create new task** (if no match found):
   - Determine appropriate task ID:
     - Check the highest ID in current phase (e.g., if T7-30 exists, next is T7-31)
     - CLI tasks use phases T3 (CLI Foundation), T4 (Agent Integration), T7 (CLI Enhancements)
   - Create task file in `.anyt/tasks/active/` with proper format
   - Include all required sections (Priority, Status, Description, Objectives, etc.)
   - Set Status to "In Progress"
   - Add initial event entry

4. **Complete task**:
   - Verify all acceptance criteria are met
   - Update Status to "Completed"
   - Add completion event entry
   - Move task file from `active/` to `done/`

5. **Cancel task**:
   - Update Status to "Cancelled"
   - Add cancellation event with reason
   - Move task file from `active/` or `backlog/` to `cancelled/`

### What Constitutes a Task

**Tasks (track these)**:
- Implementing new CLI commands
- Creating new features or functionality
- Adding new AI/agent capabilities
- Significant refactoring (architectural changes)
- Bug fixes that require code changes
- MCP server enhancements
- Integration with external services

**Not Tasks (don't track these)**:
- Running `make lint` or `make format`
- Fixing linting/formatting issues
- Minor documentation updates
- Code comments and docstrings
- Commit messages and git operations
- Design discussions
- Reading or exploring code
- Running tests
- Configuration tweaks

### Event Tracking

Add event entries to the task file to document progress. Events should be appended at the end of the file in this format:

```markdown
## Events

### 2025-10-15 10:30 - Started work
- Moved task from backlog to active
- Began implementing CLI command structure

### 2025-10-15 14:20 - Progress update
- Completed basic command implementation
- Added input validation
- Next: Add tests and error handling

### 2025-10-15 16:45 - Completed
- All commands implemented and tested
- Added comprehensive test coverage
- Updated documentation
- Task moved to done/
```

## Architecture Overview

### Technology Stack
- **CLI Framework**: Typer (FastAPI for CLIs)
- **UI/Rendering**: Rich (terminal formatting and tables)
- **HTTP Client**: httpx (async HTTP client)
- **Authentication**: keyring (secure credential storage)
- **Validation**: Pydantic v2
- **AI/Agent**: LangChain (Anthropic/OpenAI), LangGraph
- **MCP**: Model Context Protocol for Claude Code integration

### Project Structure

```
src/
├── cli/                          # CLI application
│   ├── main.py                   # Entry point and app setup
│   ├── client.py                 # API client for backend communication
│   ├── config.py                 # Configuration management
│   └── commands/                 # Command modules
│       ├── env.py                # Environment management
│       ├── auth.py               # Authentication
│       ├── workspace.py          # Workspace commands
│       ├── task.py               # Task CRUD and views
│       ├── dependency.py         # Task dependency management
│       ├── ai.py                 # AI-powered commands
│       ├── mcp.py                # MCP server commands
│       └── visualization.py      # Board and timeline views
└── anytask_mcp/                  # MCP server
    ├── __init__.py
    ├── server.py                 # MCP server implementation
    ├── client.py                 # AnyTask API client wrapper
    ├── tools.py                  # MCP tool definitions
    ├── resources.py              # MCP resource definitions
    └── context.py                # Server context management

tests/
└── cli/
    ├── unit/                     # Unit tests (mocked)
    │   ├── conftest.py           # Test fixtures
    │   ├── test_core_commands.py # env, auth, workspace tests
    │   ├── test_ai_commands.py   # AI command tests
    │   ├── test_visualization_commands.py
    │   ├── task_commands/        # Task command tests
    │   │   ├── test_task_crud.py
    │   │   ├── test_task_list.py
    │   │   └── test_task_dependencies.py
    │   └── api_client/           # API client tests
    │       ├── test_initialization.py
    │       ├── test_workspace.py
    │       ├── test_tasks.py
    │       └── test_errors.py
    └── integration/              # Integration tests (require server)
        ├── conftest.py
        ├── test_01_setup_flow.py
        └── helpers.py

docs/
├── CLI_USAGE.md                  # Complete CLI usage guide
├── MCP_INTEGRATION.md            # MCP server integration guide
├── CLI_ENHANCEMENT_ROADMAP.md    # Future CLI features
└── CLAUDE_CODE_MIGRATION_PLAN.md # Claude Code integration plan

scripts/
├── install_local.sh              # Local installation script
└── publish.sh                    # PyPI publishing script
```

### Core CLI Architecture

The CLI follows a layered architecture:

1. **Command Layer** (`src/cli/commands/`): Typer command definitions
2. **Client Layer** (`src/cli/client.py`): API communication with backend
3. **Config Layer** (`src/cli/config.py`): Configuration management
4. **Rendering Layer**: Rich console output and formatting

### Configuration System

The CLI uses three configuration files:

1. **Global Config** (`~/.config/anyt/config.json`):
   - Environment definitions (dev, staging, prod)
   - Current environment selection
   - Authentication tokens per environment

2. **Workspace Config** (`.anyt/anyt.json`):
   - Workspace ID and name
   - API URL
   - Last sync timestamp

3. **Active Task Config** (`.anyt/active_task.json`):
   - Currently picked task identifier
   - Task title and metadata
   - Picked timestamp

### API Client

The `APIClient` class (`src/cli/client.py`) handles all communication with the backend:
- Async HTTP requests using httpx
- Automatic authentication header injection
- Error handling and response parsing
- Retry logic with exponential backoff

Key methods:
- `health_check()` - Check API connectivity
- `list_workspaces()` - Get available workspaces
- `list_tasks()` - Get tasks with filters
- `get_task()` - Get task details
- `create_task()`, `update_task()`, `delete_task()` - Task CRUD
- `add_dependency()`, `remove_dependency()` - Dependency management
- `decompose_goal()` - AI task decomposition

### MCP Server

The MCP server (`src/anytask_mcp/`) provides Claude Code integration:

**Tools**:
- `anytask_list_tasks` - List tasks with filters
- `anytask_get_task` - Get task details
- `anytask_create_task` - Create new task
- `anytask_update_task` - Update existing task
- `anytask_list_workspaces` - List available workspaces

**Resources**:
- `task://{workspace}/{identifier}` - Task details as JSON
- `board://{workspace}` - Kanban board view as formatted text

## Configuration

Environment variables (loaded from `.env` or environment):
- `ANTHROPIC_API_KEY` - For AI commands
- `OPENAI_API_KEY` - For AI commands
- `ANYT_ENV` - Current environment (dev/staging/prod)
- `ANYT_AUTH_TOKEN` - Authentication token
- `ANYT_AGENT_KEY` - Agent API key
- `ANYT_CONFIG_DIR` - Override config directory (default: ~/.config/anyt)

## Testing Guidelines

### Test Structure

- **Unit tests** (`tests/cli/unit/`): Mock all API calls, test CLI logic in isolation
- **Integration tests** (`tests/cli/integration/`): Require running backend server

### Writing Tests

Use fixtures from `tests/cli/unit/conftest.py`:
- `cli_runner` - Typer CLI test runner
- `temp_config_dir` - Temporary config directory
- `mock_api_client` - Mocked API client
- `global_config` - Test global config
- `workspace_config` - Test workspace config

Example test structure:
```python
from typer.testing import CliRunner
from cli.main import app

def test_command(cli_runner: CliRunner, mock_api_client):
    result = cli_runner.invoke(app, ["command", "arg"])
    assert result.exit_code == 0
    assert "expected output" in result.output
```

### Running Tests
- `make test` - Run all CLI tests
- `make test-cli-unit` - Run unit tests only
- `make test-cli-integration` - Run integration tests (requires backend server)

## Common Patterns

### Adding a New CLI Command

1. **Create command module** in `src/cli/commands/<module>.py`
2. **Define Typer app**:
   ```python
   import typer
   from rich.console import Console

   app = typer.Typer()
   console = Console()

   @app.command()
   def my_command(arg: str):
       """Command description."""
       console.print(f"[green]Success:[/green] {arg}")
   ```

3. **Register command** in `src/cli/main.py`:
   ```python
   from cli.commands import my_module
   app.add_typer(my_module.app, name="my-command")
   ```

4. **Add tests** in `tests/cli/unit/test_my_command.py`

### API Client Usage Pattern

```python
from cli.client import APIClient
from cli.config import GlobalConfig

async def my_function():
    config = GlobalConfig.load()
    env_config = config.get_current_env()

    async with APIClient(
        base_url=env_config.api_url,
        auth_token=env_config.auth_token
    ) as client:
        result = await client.some_method()
        return result
```

### Rich Console Output

```python
from rich.console import Console
from rich.table import Table

console = Console()

# Print with color
console.print("[green]Success[/green]")

# Create table
table = Table(title="Tasks")
table.add_column("ID", style="cyan")
table.add_column("Title", style="white")
table.add_row("DEV-1", "Task title")
console.print(table)
```

## Development Notes

- **Use uv for Python**: All commands use `uv run`, not pip or direct python
- **Async everywhere**: API client uses async/await
- **Type hints**: MyPy enforces type safety on all source code
- **Rich output**: Use Rich console for all user-facing output
- **Error handling**: Catch and display user-friendly error messages
- **Config management**: Always use config classes, never hardcode paths/URLs

## Current Implementation Status

✅ Implemented:
- Complete CLI command structure
- Environment management (add, list, use, remove)
- Authentication (user tokens + agent keys)
- Workspace management
- Task CRUD operations
- Task list and board views
- Task dependency management
- Active task tracking (pick/drop)
- AI-powered goal decomposition
- MCP server for Claude Code integration
- Configuration management
- Error handling and user-friendly messages
- Comprehensive test suite (unit + integration)

🚧 In Progress:
- Enhanced AI commands
- Additional MCP tools and resources
- Advanced filtering and search

When implementing new features, follow the existing patterns in `src/cli/commands/` modules.
