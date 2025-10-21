# T7-45: Fix Makefile Typecheck Verbosity

**Priority**: Low
**Status**: Completed
**Created**: 2025-10-20

## Description

The `make typecheck` command currently shows verbose package install/uninstall messages from `uv run` that clutter the output. Each time mypy runs, uv rebuilds and reinstalls the local package, displaying "Built anyt", "Uninstalled 1 package", and "Installed 1 package" messages. This is expected behavior from `uv run` but creates unnecessary noise during type checking.

## Objectives

- Reduce verbosity of `make typecheck` output
- Keep the automatic rebuild behavior (ensures type checking against latest code)
- Maintain type checking correctness
- Make output cleaner and more focused on mypy results

## Acceptance Criteria

- [x] `make typecheck` output does not show package install/uninstall messages
- [x] Type checking still runs against the latest version of the code
- [x] Mypy output is still visible and clear
- [x] No breaking changes to the typecheck workflow
- [x] Documentation updated if behavior changes (no doc updates needed - internal change only)

## Dependencies

None

## Estimated Effort

0.5-1 hour

## Technical Notes

### Current Implementation
The Makefile currently uses:
```makefile
typecheck:
	@echo "Type checking src/..."
	@uv run mypy src
	@echo "Type checking tests/..."
	@uv run mypy tests
```

### Proposed Solutions

**Option 1: Use `--frozen` flag** (Recommended)
```makefile
typecheck:
	@echo "Type checking src/..."
	@uv run --frozen mypy src
	@echo "Type checking tests/..."
	@uv run --frozen mypy tests
```
- Prevents any environment changes during run
- Still ensures environment is correct
- Cleanest output

**Option 2: Use `--no-sync` flag**
```makefile
typecheck:
	@echo "Type checking src/..."
	@uv run --no-sync mypy src
	@echo "Type checking tests/..."
	@uv run --no-sync mypy tests
```
- Skips sync entirely
- Potential risk if code has changed since last sync

**Option 3: Use `--quiet` flag**
```makefile
typecheck:
	@echo "Type checking src/..."
	@uv run --quiet mypy src
	@echo "Type checking tests/..."
	@uv run --quiet mypy tests
```
- Suppresses uv output
- May suppress too much

### Recommendation
Use `--frozen` flag as it provides the best balance of correctness and clean output.

### Files to Modify
- `Makefile` (lines 33-37)

## Events

### 2025-10-20 - Created
- Task created based on user request to fix typecheck verbosity
- Issue: `uv run` shows package install/uninstall messages
- Solution: Add `--frozen` flag to suppress rebuild messages

### 2025-10-20 14:05 - Started work
- Moved task from backlog to active
- Status updated to "In Progress"
- Creating new git branch for implementation

### 2025-10-20 14:07 - Implementation completed
- Created git branch: T7-45-fix-makefile-typecheck-verbosity
- Updated Makefile line 35 and 37: Added `--frozen` flag to `uv run` commands
- Tested the fix: Confirmed verbose output is suppressed
- All acceptance criteria met
- Ready for commit and PR

### 2025-10-20 14:08 - Task completed and PR created
- Committed changes to branch
- Created PR: https://github.com/supercarl87/AnyTaskCLI/pull/24
- Task moved to done/
- All work completed successfully
