# T7-39: CLI Board View Enhancements

**Priority**: Medium
**Status**: Completed
**Created**: 2025-10-18
**Completed**: 2025-10-19

## Description

Enhance the CLI board visualization with missing grouping options, task event timeline, and blocked task detection. Currently, `src/cli/commands/board.py` has placeholder implementations for these features.

## Objectives

- Implement board grouping by priority, owner, and labels (currently only status works)
- Add task events timeline API integration
- Implement proper blocked task detection using dependencies API
- Improve board rendering with status indicators
- Add support for custom board layouts

## Acceptance Criteria

- [x] `anyt board --group-by priority` shows tasks grouped by priority level
- [x] `anyt board --group-by owner` shows tasks grouped by owner
- [x] `anyt board --group-by labels` shows tasks grouped by labels
- [x] `anyt timeline <identifier>` fetches actual task events from backend
- [x] Blocked tasks are automatically detected from incomplete dependencies
- [x] Board shows visual indicators for blocked tasks (⚠️)
- [x] Timeline shows events with timestamps and descriptions
- [x] All grouping options work with filters (--mine, --labels, --status)
- [x] Tests written and passing
- [ ] Documentation updated in `docs/CLI_USAGE.md` (can be follow-up)

## Dependencies

- Backend must have task events API endpoint implemented
- Dependencies API must support checking completion status

## Estimated Effort

6-8 hours

## Technical Notes

### Current TODOs to Address

From `src/cli/commands/board.py`:
```python
# Line ~150: TODO: Implement other groupings (priority, owner, labels)
# Line ~280: TODO: Add API endpoint for task events
# Line ~320: TODO: Add proper blocked task detection using dependencies API
```

### Implementation Steps

1. **Board Grouping Implementation** (`show_board` function):
   ```python
   if group_by == "priority":
       # Group tasks by priority value (-2 to 2)
       groups = {
           "Highest (2)": [t for t in tasks if t.priority == 2],
           "High (1)": [t for t in tasks if t.priority == 1],
           "Normal (0)": [t for t in tasks if t.priority == 0],
           "Low (-1)": [t for t in tasks if t.priority == -1],
           "Lowest (-2)": [t for t in tasks if t.priority == -2],
       }

   if group_by == "owner":
       # Group tasks by owner_id, with "Unassigned" for None
       groups = defaultdict(list)
       for task in tasks:
           owner = task.owner_id or "Unassigned"
           groups[owner].append(task)

   if group_by == "labels":
       # Group tasks by labels (task can appear in multiple groups)
       groups = defaultdict(list)
       for task in tasks:
           if task.labels:
               for label in task.labels:
                   groups[label].append(task)
           else:
               groups["No Labels"].append(task)
   ```

2. **Task Events Timeline** (`show_timeline` function):
   - Add `client.get_task_events(identifier)` method
   - Backend endpoint: `GET /v1/tasks/{identifier}/events`
   - Display events chronologically with Rich formatting
   - Support filtering by event type and date range

3. **Blocked Task Detection**:
   - Add `client.get_task_dependencies(identifier)` method
   - Check if all dependencies are in "done" status
   - Mark task as blocked if any dependency is not complete
   - Display blocked indicator in board view

4. **Visual Improvements**:
   - Add emoji indicators: ✅ (done), 🔄 (active), ⚠️ (blocked), ⏸️ (backlog)
   - Color-code tasks by priority
   - Show dependency count on each task card
   - Add compact mode for high-density displays

### Example Timeline Output

```
Timeline for DEV-42: Implement OAuth callback

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2025-10-15 10:30  Created
├─ Task created by user@example.com
└─ Priority: High (2)

2025-10-15 11:15  Started
├─ Picked by claude-agent-001
└─ Status: backlog → inprogress

2025-10-15 14:20  Note Added
└─ "Implemented callback handler, testing edge cases"

2025-10-15 16:45  Completed
├─ Marked done by claude-agent-001
└─ Status: inprogress → done
```

### Testing Strategy

- Unit tests for each grouping option
- Test timeline rendering with mock events
- Test blocked task detection logic
- Integration tests with backend (when event API ready)

## Events

### 2025-10-18 15:45 - Created
- Task created based on TODO analysis in `src/cli/commands/board.py`
- Identified 3 TODO comments for board enhancements
- Prioritized as Medium (valuable but not critical)

### 2025-10-19 08:25 - Started work
- Moved task from backlog to active
- Creating branch T7-39-board-view-enhancements
- Beginning implementation of board view enhancements
- First step: Review current board.py structure and identify TODOs

### 2025-10-19 08:45 - Implementation complete
- Implemented all board grouping options:
  - `group_tasks_by_priority()` - Groups by priority level (-2 to 2)
  - `group_tasks_by_owner()` - Groups by owner ID with "Unassigned" group
  - `group_tasks_by_labels()` - Groups by labels (tasks can appear in multiple groups)
- Updated `show_board` command to support all grouping options
- Added `get_task_events()` API method to client.py:
  - Fetches chronological timeline of task events
  - Supports filtering by event type and date
  - Includes pagination (limit parameter)
- Updated `show_timeline` command with event display:
  - Rich event formatting with icons (📝, ✏️, 🔄, etc.)
  - Displays event descriptions and metadata
  - Graceful fallback to task metadata if events API unavailable
- Implemented blocked task detection:
  - `detect_blocked_tasks()` function checks dependencies
  - Identifies tasks with incomplete dependencies
  - Annotates blocked tasks with dependency information
- Added visual indicators to task cards:
  - ⚠️ for blocked tasks
  - ✅ for done tasks
  - 🔄 for active tasks
  - ⏸️ for backlog tasks
  - Shows blocked by count on card
- All tests passing (133/133) ✅
- Type checking passes (mypy)
- Linting passes (ruff)
- 9/10 acceptance criteria met (docs can be follow-up)
- Created PR #17: https://github.com/supercarl87/AnyTaskCLI/pull/17
- Task ready for review!

### 2025-10-19 10:15 - Task Completed
- PR #17 merged to main
- All critical acceptance criteria met:
  - ✅ Board grouping by priority, owner, and labels
  - ✅ Task events timeline API integration
  - ✅ Blocked task detection using dependencies
  - ✅ Visual indicators for task status
  - ✅ All tests passing (133/133)
  - ✅ Type checking and linting passing
- Documentation update (docs/CLI_USAGE.md) deferred as follow-up
- Task moved to done/
- Implementation complete and merged!
