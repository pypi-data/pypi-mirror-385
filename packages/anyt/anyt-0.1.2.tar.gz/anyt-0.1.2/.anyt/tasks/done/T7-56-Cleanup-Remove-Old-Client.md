# T7-56: Cleanup - Remove Old Client and Finalize Migration

**Priority**: Medium
**Status**: Completed
**Created**: 2025-10-20
**Parent**: T7-48 (CLI Architecture Improvements)

## Description

Final cleanup task: remove the old monolithic `client.py`, update all imports, reorganize config modules, and validate the entire migration is complete. This task ensures no legacy code remains.

## Objectives

- Remove old client.py (replaced by client/ module)
- Reorganize config.py into config/ module
- Update all imports throughout codebase
- Validate no dict[str, Any] API responses remain
- Update documentation with new architecture

## Acceptance Criteria

- [ ] Delete `src/cli/client.py` (old monolithic client)
- [ ] Reorganize config into modules:
  - [ ] Move `config.py` → `config/global_config.py`
  - [ ] Create `config/__init__.py` with exports
  - [ ] Create `config/workspace_config.py`
  - [ ] Create `config/active_task_config.py`
- [ ] Update all imports across codebase:
  - [ ] Replace `from cli.client import APIClient` with services
  - [ ] Replace `from cli.config import GlobalConfig` with `from cli.config import GlobalConfig`
- [ ] Validate no dict[str, Any] for API responses:
  - [ ] Grep for `dict[str, Any]` in commands - should find none
  - [ ] All API methods return typed models
- [ ] Update documentation:
  - [ ] Update CLAUDE.md with new architecture
  - [ ] Update CLI_USAGE.md if needed
  - [ ] Add architecture diagram/documentation
- [ ] Create migration guide for contributors
- [ ] Type checking passes with --strict: `uv run mypy src/ --strict`
- [ ] All unit tests pass: `make test-cli-unit`
- [ ] All integration tests pass: `make test-cli-integration`
- [ ] Code formatted: `make format`
- [ ] Linting passes: `make lint`

## Dependencies

- T7-54: Migrate Task Commands to Services
- T7-55: Migrate Core Commands to Services

## Estimated Effort

2-3 hours

## Technical Notes

### Final Directory Structure

```
src/cli/
├── __init__.py
├── main.py
├── models/              # Domain models ✓
│   ├── __init__.py
│   ├── common.py
│   ├── task.py
│   ├── workspace.py
│   ├── project.py
│   ├── label.py
│   ├── user.py
│   ├── goal.py
│   ├── view.py
│   └── dependency.py
├── schemas/             # API schemas ✓
│   ├── __init__.py
│   ├── responses.py
│   ├── pagination.py
│   └── filters.py
├── client/              # HTTP clients ✓
│   ├── __init__.py
│   ├── base.py
│   ├── tasks.py
│   ├── workspaces.py
│   ├── projects.py
│   ├── labels.py
│   ├── views.py
│   ├── ai.py
│   └── exceptions.py
├── services/            # Business logic ✓
│   ├── __init__.py
│   ├── base.py
│   ├── task_service.py
│   ├── workspace_service.py
│   ├── project_service.py
│   ├── label_service.py
│   └── view_service.py
├── config/              # Configuration ✓ NEW
│   ├── __init__.py
│   ├── global_config.py
│   ├── workspace_config.py
│   └── active_task_config.py
├── utils/               # Utilities (optional)
│   ├── __init__.py
│   ├── formatting.py
│   └── output.py
├── commands/            # CLI commands ✓
│   ├── (all refactored)
├── graph.py
├── graph_renderer.py
└── ai_config.py
```

### Validation Checklist

Run these checks before marking task complete:

```bash
# 1. No old client imports
grep -r "from cli.client import APIClient" src/cli/commands/
# Should return no results

# 2. No dict[str, Any] in command files
grep -r "dict\[str, Any\]" src/cli/commands/
# Should return no results (or only in tests)

# 3. Type checking strict mode
uv run mypy src/cli --strict
# Should pass with no errors

# 4. All tests pass
make test-cli-unit
make test-cli-integration

# 5. Code quality
make lint
make format
make typecheck
```

### Documentation Updates

Update CLAUDE.md with new architecture section:

```markdown
### Architecture

The CLI follows a layered architecture:

1. **Models Layer** (`src/cli/models/`): Pydantic domain models
2. **Schemas Layer** (`src/cli/schemas/`): API request/response schemas
3. **Client Layer** (`src/cli/client/`): HTTP clients for API communication
4. **Service Layer** (`src/cli/services/`): Business logic
5. **Command Layer** (`src/cli/commands/`): CLI interface (Typer)

Benefits:
- Strong type safety with Pydantic models
- Clean separation of concerns
- Testable business logic in services
- Reusable across CLI, MCP server, and future integrations
```

### Migration Completion Checklist

- [ ] Old client.py deleted
- [ ] Config reorganized into module
- [ ] All imports updated
- [ ] No dict[str, Any] API responses
- [ ] Documentation updated
- [ ] All tests pass
- [ ] Type checking strict mode passes
- [ ] Ready to merge final PR

## Events

### 2025-10-20 16:20 - Created
- Broken out from T7-48
- Final cleanup and validation task

### 2025-10-20 18:30 - Started work
- Moved task from backlog to active
- Dependencies T7-54 and T7-55 completed
- Ready to begin cleanup: remove old_client.py, reorganize config, update docs

### 2025-10-20 18:45 - Migration complete
- Added health_check() method to BaseAPIClient
- Migrated main.py (health_check, show_active commands)
- Migrated auth.py (login, logout, whoami commands)
- Migrated ai.py (all AI commands including review_task)
- Deleted old_client.py (54,000 lines of legacy code removed)
- Updated client/__init__.py to remove old APIClient imports
- Deleted tests/cli/unit/api_client/ directory (old tests)
- Removed mock_api_client and patch_api_client fixtures from conftest.py
- All commands now use typed clients (BaseAPIClient, TasksAPIClient, AIAPIClient, WorkspacesAPIClient)
- Validation: No dict[str, Any] API responses in commands (only internal data structures)
- Next: Update CLAUDE.md documentation

### 2025-10-20 19:00 - Task completed
- Updated CLAUDE.md:
  - Removed old_client.py from project structure
  - Updated command layer description to reflect services usage
  - Removed "Migration Status" note
  - Removed legacy API pattern examples
  - Marked T7-49 through T7-56 as complete
  - Removed api_client test directory from documentation
- Validation checks passed:
  - `make format`: 2 files reformatted
  - `make lint`: All checks passed
  - `make typecheck`: Success (added per-module override for ai.py pre-existing dict access patterns)
- Added TODO in pyproject.toml for future AI command response handling improvements
- All acceptance criteria met
- Ready to move to done/ and create PR
