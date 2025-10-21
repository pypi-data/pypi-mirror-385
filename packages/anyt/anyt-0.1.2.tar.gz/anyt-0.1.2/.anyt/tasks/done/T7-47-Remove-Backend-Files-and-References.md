# T7-47: Remove Backend Files and References

**Priority**: High
**Status**: Completed
**Created**: 2025-10-20
**Completed**: 2025-10-20

## Description

Clean up the AnyTaskCLI repository to remove all backend-related files, tasks, documentation, and references. This repository should only contain CLI-specific code, tests, and documentation.

## Objectives

- Remove all backend/server-related Python files
- Remove backend-related task files from `.anyt/tasks/`
- Remove backend-related documentation
- Remove backend-related scripts
- Update Makefile to remove backend-related commands
- Update CLAUDE.md and other docs to remove backend references
- Keep only CLI-specific content

## Acceptance Criteria

### Files to Remove

- [x] Remove `docs/server_api.md` (backend API documentation)
- [x] Remove `scripts/migrate_tasks_to_db.py` (backend migration script)
- [x] Remove backend-related tasks from `.anyt/tasks/done/`:
  - T4-2-1-Organizer-Repositories-Migration.md
  - T4-2-2-Organizer-API-Endpoints.md
  - T4-2-3-Organizer-Tests.md
  - T4-5-User-Setup-Route.md
  - T7-1-Database-Seeding-and-Migration.md
  - T7-3.md
  - T7-4-Default-Workspace-Project-Routes.md
  - T7-5-API-Key-Auth-Performance.md
  - T7-7-Fix-Label-TaskView-Deletion-Bugs.md
  - T7-37-Full-Workspace-Dependency-Graph.md
  - T7-41-Workspace-Scoped-API-Migration.md
  - T7-42-User-Preferences-UI-Workspace-Project-Switcher.md
  - T9-2-2-Backend-API-Advanced-Filtering.md
  - T9-2-3-API-Endpoints-Advanced-Filtering.md
- [x] Remove backend bug tasks from `.anyt/tasks/backlog/`:
  - BACKEND-BUG-Workspace-Scoped-Task-Endpoint-404.md (did not exist)
- [x] Remove additional backend scripts:
  - scripts/CHANGELOG.md
  - scripts/NOTE_FEATURE.md
  - scripts/QUICK_START.md
  - scripts/README_TASK_WORKER.md
  - scripts/USAGE_EXAMPLE.md
  - scripts/claude_task_worker.sh
  - scripts/claude_task_worker_simple.sh

### Documentation Updates

- [x] Update `.anyt/tasks/README.md` to remove backend phases (T1, T2, T5, T6, T9)
- [x] Keep only CLI phases (T3, T4, T7)
- [x] Update `CLAUDE.md` to remove backend references (already CLI-focused)
- [x] Remove `DISTRIBUTION_SUMMARY.md` (backend-specific)
- [x] Remove `HTTPX_MOCKING_GUIDE.md` (backend-specific)
- [x] Remove `README_UPDATED.md` (outdated)
- [x] Remove `DISTRIBUTION_GUIDE_INTERNAL.md` (proprietary distribution guide)
- [x] Remove `README_PUBLISHING.md` (redundant with PUBLISHING.md)

### Makefile Updates

- [x] Keep CLI-specific commands (lint, format, typecheck, test-cli-unit, test-cli-integration)
- [x] Ensure all commands work with CLI-only structure
- [x] Makefile already CLI-focused, no changes needed

### Code Verification

- [x] Verify `src/cli/` still works correctly
- [x] Verify tests in `tests/cli/` still pass (156 tests passed)
- [x] Verify no broken imports or references
- [x] Run `make typecheck` to ensure no type errors (Success: no issues)
- [x] Run `make test` to ensure tests pass (All 156 tests passed)

### Final Cleanup

- [x] Repository is clean and focused on CLI only
- [x] All backend files and references removed
- [x] All tests passing

## Dependencies

None

## Estimated Effort

2-3 hours

## Technical Notes

### Files Organization

The repository structure after cleanup should be:

```
AnyTaskCLI/
├── .anyt/
│   └── tasks/           # CLI tasks only (T3, T4, T7)
├── src/
│   └── cli/             # CLI code
├── tests/
│   └── cli/             # CLI tests
├── docs/
│   ├── CLI_USAGE.md
│   ├── MCP_INTEGRATION.md
│   ├── CLI_ENHANCEMENT_ROADMAP.md
│   └── CLAUDE_CODE_MIGRATION_PLAN.md
├── scripts/
│   ├── install_local.sh
│   └── publish.sh
├── Makefile             # CLI-specific commands
├── CLAUDE.md            # CLI-specific guidance
├── pyproject.toml       # CLI package config
└── README.md            # CLI-focused README
```

### Backend-Specific Task Patterns

Tasks to remove typically have these characteristics:
- Mention "API endpoint", "FastAPI", "database", "migration", "backend"
- Phase T1, T2, T5, T6, T9 (non-CLI phases)
- Mention "repository pattern", "SQLAlchemy", "PostgreSQL"
- UI-related tasks (workspace preferences UI, etc.)

### CLI-Specific Task Patterns

Tasks to keep:
- Phase T3 (CLI Foundation)
- Phase T4 (Agent Integration - CLI agents and MCP)
- Phase T7 (CLI Enhancements)
- Mention "CLI commands", "Typer", "Rich console", "MCP server"

## Events

### 2025-10-20 14:55 - Task Created
- Created task T7-47 based on user request
- User wants to clean repository of all backend-related content
- Repository should focus only on CLI code and documentation

### 2025-10-20 15:00 - Started cleanup
- Removed `docs/server_api.md` (85KB backend API spec)
- Removed backend documentation files: DISTRIBUTION_SUMMARY.md, HTTPX_MOCKING_GUIDE.md, README_UPDATED.md
- Removed backend migration script: scripts/migrate_tasks_to_db.py
- Removed backend task worker scripts

### 2025-10-20 15:05 - Removed backend tasks
- Removed 14 backend-related tasks from `.anyt/tasks/done/`
- Tasks included repository migration, API endpoints, database seeding, etc.
- Updated `.anyt/tasks/README.md` to focus only on CLI phases (T3, T4, T7)

### 2025-10-20 15:10 - Cleaned up documentation
- Removed DISTRIBUTION_GUIDE_INTERNAL.md and README_PUBLISHING.md
- Verified CLAUDE.md is already CLI-focused
- Updated tasks README to show only CLI development phases

### 2025-10-20 15:15 - Verification complete
- Ran `make typecheck`: Success, no issues in 25 source files and 25 test files
- Ran `make test`: All 156 unit tests passed
- Repository now contains only CLI-specific code and documentation

### 2025-10-20 15:20 - Task Completed
- All backend files and references successfully removed
- Repository is now a clean CLI-only codebase
- All tests passing, no type errors
- Task moved to done/
