# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- CLI configuration file moved from `anyt.json` to `.anyt/anyt.json` for better organization
- Renamed package from `backend` to `anyt` for clarity
- Updated project metadata for PyPI publishing
- Added comprehensive installation and publishing documentation

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

[Unreleased]: https://github.com/yourusername/AnyTaskBackend/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/AnyTaskBackend/releases/tag/v0.1.0

