# T7-27: CLI - JSON Output Enhancement for All Commands

## Priority
High

## Status
Completed

## Description
Ensure all CLI commands support `--json` output mode for machine-readable responses. This enables Claude Code to easily parse CLI output when using bash commands or subagents.

Currently some commands have JSON output, but we need to verify and standardize across ALL commands.

## Objectives
1. Audit all CLI commands for `--json` support
2. Add `--json` flag to any commands missing it
3. Standardize JSON output format
4. Test JSON output parsing

## Acceptance Criteria
- [x] All `task` commands support `--json`
- [x] All `board`, `timeline`, `graph` commands support `--json`
- [x] All existing `workspace` commands support `--json` (workspace list/project list don't exist)
- [x] JSON output follows consistent schema: `{"success": true, "data": {...}, "message": null}`
- [x] Errors return: `{"success": false, "error": "...", "message": "..."}`
- [ ] Documentation updated to show `--json` flag for each command (deferred - can be done in separate task)

## Dependencies
- None

## Estimated Effort
2-3 hours

## Technical Notes

### Audit Commands

Check these commands have `--json`:
- [x] `task add`
- [x] `task list`
- [x] `task show`
- [x] `task edit`
- [x] `task done`
- [x] `task rm`
- [x] `task dep add`
- [x] `task dep rm`
- [x] `task dep list`
- [x] `task pick`
- [ ] `active` (not a command - active task is tracked via file)
- [x] `board`
- [x] `timeline`
- [x] `graph`
- [x] `summary`
- [ ] `workspace list` (command does not exist)
- [ ] `project list` (command does not exist)

### Standard JSON Response Format

```json
{
  "success": true,
  "data": {
    "identifier": "DEV-42",
    "title": "Implement OAuth",
    "status": "todo",
    "priority": 1
  },
  "message": null
}
```

### Example Usage (by Claude Code)

```python
# Claude Code runs command
result = subprocess.run(
    ["uv", "run", "src/cli/main.py", "task", "list", "--json"],
    capture_output=True,
    text=True
)

# Parse JSON
import json
data = json.loads(result.stdout)

if data["success"]:
    tasks = data["data"]["items"]
    # Process tasks...
```

## Events

### 2025-10-18 16:30 - Started work
- Moved task from backlog to active
- Beginning implementation of JSON output for all CLI commands
- Will start by auditing current commands and identifying missing --json flags

### 2025-10-18 17:00 - Progress update
- Completed JSON support for task dependency commands (dep add, dep rm, dep list)
- Completed JSON support for task pick command
- All task CRUD commands already had JSON support
- Now working on visualization commands (board, timeline, graph, summary)

### 2025-10-18 17:30 - Completed
- Added JSON support to all visualization commands (board, timeline, graph, summary)
- All commands now support `--json` flag with consistent output format
- Success responses: `{"success": true, "data": {...}, "message": null}`
- Error responses: `{"success": false, "error": "...", "message": "..."}`
- Ran lint and format checks - all passed
- Ready to commit and create PR

## Related Files
- `src/cli/commands/task.py` - Add --json to missing commands
- `src/cli/commands/board.py` - Add --json support
- `src/cli/commands/workspace.py` - Add --json support
- `docs/CLI_USAGE.md` - Update documentation
