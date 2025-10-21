# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-10-20

### Added
- **Enhanced Claude Worker Scripts**: Comprehensive automation scripts for Claude AI task processing
  - `claude_task_worker_enhanced.sh`: Full-featured worker with git commits, follow-up tasks, and dependency management
  - `claude_task_worker.sh`: Standard worker with git auto-commit functionality
  - `claude_task_worker_simple.sh`: Interactive mode with manual approval
  - Git auto-commit with structured commit messages including Co-Authored-By attribution
  - Automatic follow-up task creation based on Claude's analysis (FOLLOW_UP_TASK markers)
  - Blocking task identification and creation (BLOCKING_TASK markers)
  - Automatic task dependency management using `anyt task dep add`
  - Configurable via environment variables (AUTO_COMMIT, CREATE_FOLLOWUP_TASKS, COMMIT_PREFIX, etc.)
  - Comprehensive logging with color-coded output and commit hash tracking
  - Quick start guide (WORKER_QUICK_START.md) with 5-minute setup instructions
- **Public Task ID Support** (T7-63): CLI now supports global public task IDs
  - `anyt task show` accepts public IDs (e.g., `123456789`) in addition to workspace identifiers
  - `anyt task share` generates shareable public URLs using public IDs
  - Public IDs work across workspaces for global task accessibility
- **Project Context Resolution** (T7-65): Intelligent workspace/project context handling
  - ServiceContext helper for resolving current workspace and project from config
  - Automatic project resolution based on user preferences
  - Improved context management across all commands
- **CLI Documentation Generator**: Auto-generate complete CLI reference documentation
  - `scripts/generate_help_introspect.py`: Uses Typer introspection to generate docs
  - Complete command reference with all parameters and examples
  - Outputs to `docs/CLI_COMPLETE_REFERENCE.md`
- **Health Check Command** (T7-58): Backend server health monitoring
  - `anyt health check`: Verify backend server status
  - Useful for troubleshooting connection issues

### Fixed
- **Pagination Response Parsing**: Updated to match backend API changes
  - Fixed total count parsing in paginated responses
  - Improved error handling for pagination edge cases
- **Test Suite Improvements**: Comprehensive test fixes for Pydantic migration
  - Fixed whoami test to use Pydantic Workspace model (T7-64)
  - Fixed interactive picker and preference tests (T7-62)
  - Fixed project and dependency tests with Pydantic models (T7-61)
  - Fixed visualization command tests (T7-60)
  - Refactored task CRUD tests to use service-based architecture (T7-59)
- **MyPy Configuration**: Reorganized to eliminate per-module section warnings

### Changed
- **CLI Architecture Completed** (T7-48): Finalized migration to 4-layer architecture
  - Removed legacy `old_client.py` (54,000 lines of code)
  - All commands now use typed services and clients
  - Improved type safety across entire codebase
- **Agent Key Configuration** (T7-57): Added agent_key support to workspace configuration
  - Workspaces can now store agent API keys
  - Improved authentication flow for agent-based workflows

### Documentation
- Updated `README_TASK_WORKER.md` with comprehensive worker script documentation
  - Git commit integration details
  - Follow-up and blocking task workflows
  - Dependency management examples
  - Configuration options reference
- New `WORKER_QUICK_START.md` for rapid onboarding
  - Step-by-step setup guide
  - Example workflows with actual output
  - Troubleshooting section
  - Advanced usage patterns

## [0.1.1] - 2025-10-19

### Fixed
- Fixed task identifier resolution bug where partial identifiers (e.g., "9") were not being properly resolved to full identifiers (e.g., "DEV-9")
- `anyt task show`, `anyt task edit`, `anyt task done`, and `anyt task rm` now correctly handle numeric task identifiers by prepending the workspace prefix
- Updated `normalize_identifier()` helper function to accept workspace prefix parameter for proper identifier resolution
- Fixed `anyt task show` using incompatible workspace-scoped API endpoint; now uses standard task endpoint for consistency with other commands

## [0.1.0] - 2025-10-17

### Added
- Initial release of AnyTask CLI
- Core CLI commands:
  - `anyt env` - Environment management
  - `anyt auth` - Authentication (user tokens and agent keys)
  - `anyt workspace` - Workspace operations
  - `anyt task` - Task CRUD operations
  - `anyt ai` - AI-powered features (decompose, summarize)
  - `anyt mcp` - MCP server integration
- Visualization commands:
  - `anyt board` - Kanban board view
  - `anyt timeline` - Task timeline
  - `anyt summary` - Workspace summary
  - `anyt graph` - Dependency visualization
- Task management features:
  - Create, update, delete tasks
  - Pick/unpick active tasks
  - Dependency management
  - Label management
  - Status and priority tracking
- Authentication methods:
  - JWT token authentication (users)
  - API key authentication (agents)
  - Secure credential storage with keyring
- Configuration system:
  - Global config (~/.config/anyt/config.json)
  - Workspace config (anyt.json)
  - Active task tracking (.anyt/active_task.json)
- Rich terminal UI with colors and formatting
- Error handling and user-friendly messages

### Dependencies
- typer>=0.15.3 - CLI framework
- rich>=14.0.0 - Terminal formatting
- httpx>=0.28.1 - HTTP client
- keyring>=25.0.0 - Secure credential storage
- pydantic>=2.11.9 - Data validation

[Unreleased]: https://github.com/yourusername/AnyTaskBackend/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/yourusername/AnyTaskBackend/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/yourusername/AnyTaskBackend/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yourusername/AnyTaskBackend/releases/tag/v0.1.0

