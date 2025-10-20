# T7-6: Update CLI to Use .anyt/anyt.json Config Path

**Priority**: Low
**Status**: Completed
**Created**: 2025-10-18

## Description

Modify the CLI codebase to read and write the workspace configuration file from `.anyt/anyt.json` instead of the project root `anyt.json`. This improves project organization by consolidating all AnyTask metadata (tasks, config, active_task.json) in a single `.anyt/` folder.

This is a **CLI code modification task** that requires updating the configuration path logic and ensuring the CLI creates the `.anyt/` directory when needed.

## Objectives

- Update CLI configuration path from `anyt.json` → `.anyt/anyt.json`
- Modify `WorkspaceConfig.get_config_path()` to return new path
- Ensure `WorkspaceConfig.save()` creates `.anyt/` directory if needed
- Update test fixtures to use new path
- Move existing `anyt.json` file to new location
- Update documentation to reflect new path

## Acceptance Criteria

- [x] `src/cli/config.py:194` updated to return `.anyt/anyt.json` path
- [x] `WorkspaceConfig.save()` creates `.anyt/` directory before writing
- [x] `tests/cli/unit/conftest.py` test fixtures updated for new path
- [x] All CLI unit tests pass: `make test`
- [x] Existing `anyt.json` moved to `.anyt/anyt.json` using `git mv`
- [x] CLI commands work correctly with new path (tested with `anyt workspace list`)
- [x] Documentation updated (`docs/CLI_USAGE.md`, `CHANGELOG.md`)
- [x] Code linting passes: `make lint`
- [x] Type checking passes: `make typecheck`
- [ ] Code reviewed and merged

## Dependencies

None - this is an internal CLI refactoring

## Estimated Effort

1-2 hours

## Technical Notes

### CLI Architecture Analysis

**Key File**: `src/cli/config.py`
- **Line 194**: `get_config_path()` currently returns `directory / "anyt.json"`
- **Line 211-219**: `save()` writes config to disk using `get_config_path()`
- **Line 196-209**: `load()` reads config from disk using `get_config_path()`

**Centralized Design**: The path is hardcoded in **ONE location** (`config.py:194`). All other code uses `WorkspaceConfig.load()` and `WorkspaceConfig.save()`, making this change straightforward.

**Files That Use WorkspaceConfig**:
- `src/cli/commands/init.py` - Initializes workspace, saves config
- `src/cli/commands/workspace.py` - Manages workspace switching
- `src/cli/commands/task/helpers.py` - Helper to load workspace config
- `src/cli/main.py` - Loads config for active task display
- All task command files use `get_workspace_or_exit()` helper

### Current Structure
```
/Users/bsheng/work/AnyTaskBackend/
├── anyt.json                    # Current location (root)
└── .anyt/
    ├── active_task.json        # Already in .anyt/
    └── tasks/                   # Already in .anyt/
```

### Target Structure
```
/Users/bsheng/work/AnyTaskBackend/
└── .anyt/
    ├── anyt.json               # New location (consolidated)
    ├── active_task.json
    └── tasks/
```

### Implementation Steps

#### 1. Update Configuration Path (`src/cli/config.py`)

**Before** (Line 194):
```python
@classmethod
def get_config_path(cls, directory: Optional[Path] = None) -> Path:
    """Get the path to the workspace config file."""
    if directory is None:
        directory = Path.cwd()

    return directory / "anyt.json"  # OLD PATH
```

**After** (Line 194):
```python
@classmethod
def get_config_path(cls, directory: Optional[Path] = None) -> Path:
    """Get the path to the workspace config file."""
    if directory is None:
        directory = Path.cwd()

    return directory / ".anyt" / "anyt.json"  # NEW PATH
```

#### 2. Ensure Directory Creation (`src/cli/config.py`)

Check `save()` method (lines 211-219) to ensure it creates the `.anyt/` directory:

```python
def save(self, directory: Optional[Path] = None) -> None:
    """Save workspace config to anyt.json."""
    config_path = self.get_config_path(directory)

    # Ensure .anyt directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(self.model_dump(exclude_none=True), f, indent=2)
```

If this line doesn't exist, add it: `config_path.parent.mkdir(parents=True, exist_ok=True)`

#### 3. Update Test Fixtures (`tests/cli/unit/conftest.py`)

**Before** (Line 78):
```python
def mock_workspace_path():
    return tmp_path / "anyt.json"
```

**After** (Line 78):
```python
def mock_workspace_path():
    return tmp_path / ".anyt" / "anyt.json"
```

Ensure test setup creates the `.anyt/` directory in temporary test directories.

#### 4. Move Existing Config File

After code changes are complete, move the actual file:

```bash
# Move file using git to preserve history
git mv anyt.json .anyt/anyt.json

# Verify it worked
git status  # Should show as renamed, not deleted/added
```

#### 5. Update Documentation

**Files to update**:
- `docs/CLI_USAGE.md` (lines 251, 907) - Update references to anyt.json path
- `CHANGELOG.md` (line 43) - Add entry for this change
- `CLAUDE.md` - Update any references to config file location

**Changelog Entry**:
```markdown
### Changed
- CLI configuration file moved from `anyt.json` to `.anyt/anyt.json` for better organization
```

#### 6. Testing Checklist

```bash
# Run unit tests
make test

# Run CLI manually to verify
anyt workspace info    # Should read from .anyt/anyt.json
anyt task list         # Should work normally
anyt workspace set     # Should save to .anyt/anyt.json

# Check file was created in right location
ls -la .anyt/anyt.json

# Verify linting and type checking
make lint
make typecheck
```

### Migration Notes

**Previous Migration History**:
- **T5-6 (Completed)**: Moved from `.anyt/workspace.json` → `anyt.json` (root)
- **T7-6 (This task)**: Moving from `anyt.json` (root) → `.anyt/anyt.json`

**Why Move Again?**
The root location was temporary. Consolidating all AnyTask metadata in `.anyt/` improves project cleanliness and makes it clear what files belong to the CLI vs the backend server.

**Current Config Content** (`anyt.json`):
```json
{
  "workspace_id": "187",
  "name": "default",
  "api_url": "http://localhost:8000",
  "last_sync": "2025-10-18 11:29:01",
  "current_project_id": 134,
  "workspace_identifier": "DEFAULT"
}
```

### Edge Cases to Test

1. **Fresh initialization**: `anyt init` should create `.anyt/anyt.json` automatically
2. **Directory doesn't exist**: Save should create `.anyt/` directory
3. **Existing users**: Migration path - what happens to old `anyt.json`?
4. **Tests**: Ensure test fixtures create `.anyt/` in temp directories

### .gitignore Considerations

Currently, `anyt.json` is **NOT** in `.gitignore` (it's tracked by git).

**Decision needed**: Should `.anyt/anyt.json` be:
- **Tracked** (current behavior) - Allows sharing workspace config
- **Ignored** (add to .gitignore) - Keeps local config private

For now, maintain current behavior (tracked) unless there's a reason to change.

## Events

### 2025-10-18 11:45 - Created
- Task created based on user request to modify CLI configuration path
- Completed codebase exploration of CLI architecture
- Identified key files: `src/cli/config.py` (line 194), test fixtures, documentation
- This is a CLI code modification task, not just a file move

### 2025-10-18 11:50 - Task Updated
- Rewrote task to focus on CLI code changes
- Added comprehensive technical analysis
- Specified exact line numbers and code changes needed
- Added testing checklist and edge cases

### 2025-10-18 14:30 - Started Work
- Moved task from backlog to active
- Beginning implementation of CLI configuration path changes
- Will update src/cli/config.py, test fixtures, and documentation

### 2025-10-18 14:50 - Completed Implementation
- ✅ Updated `src/cli/config.py:194` to return `.anyt/anyt.json`
- ✅ Added directory creation in `WorkspaceConfig.save()` method
- ✅ Updated test fixtures in `tests/cli/unit/conftest.py`
- ✅ Moved `anyt.json` to `.anyt/anyt.json` using `git mv`
- ✅ Updated documentation in `CLI_USAGE.md` and `CHANGELOG.md`
- ✅ All CLI unit tests pass (139 passed, 2 skipped)
- ✅ Verified CLI works with new path using `anyt workspace list`
- ✅ Code linting passes: `make lint`
- ✅ Type checking passes: `make typecheck`
- Task completed successfully and ready for review

### 2025-10-18 15:00 - Fixed Output Messages
- 🔧 Updated success messages in `init.py` and `workspace.py` (4 locations)
- Changed "Initialized workspace config in {target_dir}/anyt.json" to show correct path
- Now displays: "Initialized workspace config in {target_dir}/.anyt/anyt.json"
- All tests still pass, lint and typecheck clean

### 2025-10-18 15:05 - Pull Request Created
- 🚀 Created PR #90: https://github.com/supercarl87/AnyTaskBackend/pull/90
- All quality checks passed before commit
- Pushed branch `t5-4-4-task-management-tests` to remote
- PR includes full task context and acceptance criteria
- Ready for code review
