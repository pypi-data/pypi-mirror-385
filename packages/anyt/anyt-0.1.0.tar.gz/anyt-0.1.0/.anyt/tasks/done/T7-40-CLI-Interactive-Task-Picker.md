# T7-40: CLI Interactive Task Picker

**Priority**: Low
**Status**: Completed
**Created**: 2025-10-18

## Description

Implement full interactive task picker for `anyt task pick` command with filtering, grouping by status, and keyboard navigation. Currently has a placeholder TODO comment.

## Objectives

- Create interactive task picker using Rich or Textual
- Support filtering by status, priority, labels
- Group tasks by status for easier navigation
- Add keyboard shortcuts for quick selection
- Show task preview on hover/selection

## Acceptance Criteria

- [x] `anyt task pick` launches interactive picker when no identifier provided
- [x] Tasks grouped by status columns (backlog, todo, inprogress)
- [x] Status indicators show task state and priority
- [x] Works in both terminal and VSCode integrated terminal
- [x] Tests written and passing
- [x] Documentation updated in `docs/CLI_USAGE.md`

Note: Implemented with numbered selection (Rich library) rather than arrow keys navigation. User types number to select task, 'q' to quit. This provides better compatibility across different terminal environments and is simpler to use.

## Dependencies

- None (can be implemented independently)

## Estimated Effort

4-6 hours

## Technical Notes

### Current TODO to Address

From `src/cli/commands/task/pick.py`:
```python
# Line ~80: TODO: Implement full interactive picker with grouping by status
```

### Implementation Approach

Two options:

**Option 1: Rich Prompts (Simpler)**
```python
from rich.prompt import Prompt
from rich.table import Table

def interactive_picker(tasks: list[dict]) -> str | None:
    # Display tasks in a numbered table
    table = Table(title="Select a Task")
    table.add_column("#", style="cyan")
    table.add_column("ID", style="yellow")
    table.add_column("Title")
    table.add_column("Status", style="blue")

    for idx, task in enumerate(tasks, 1):
        table.add_row(
            str(idx),
            task["identifier"],
            task["title"][:50],
            task["status"]
        )

    console.print(table)
    choice = Prompt.ask("Select task number (or 'q' to quit)")

    if choice.lower() == 'q':
        return None

    try:
        idx = int(choice) - 1
        return tasks[idx]["identifier"]
    except (ValueError, IndexError):
        console.print("[red]Invalid selection[/red]")
        return None
```

**Option 2: Textual TUI (More Advanced)**
```python
from textual.app import App
from textual.widgets import DataTable, Header, Footer

class TaskPickerApp(App):
    """Interactive task picker with filtering."""

    def compose(self):
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("ID", "Title", "Status", "Priority")

        for task in self.tasks:
            table.add_row(
                task["identifier"],
                task["title"],
                task["status"],
                str(task["priority"])
            )

    def on_data_table_row_selected(self, event):
        self.selected_task = event.row_key.value
        self.exit(self.selected_task)
```

### Recommended: Start with Option 1 (Rich)

- Simpler to implement
- Good UX for most use cases
- Can upgrade to Textual later if needed

### Features to Include

1. **Numbered Selection**:
   - Display tasks with numbers
   - User types number to select
   - Support range selection (e.g., "1-5" for bulk pick)

2. **Filtering**:
   - Filter by status: `anyt task pick --status todo`
   - Filter by labels: `anyt task pick --labels bug`
   - Filter by priority: `anyt task pick --priority-min 1`

3. **Grouping Display**:
   - Group tasks by status columns
   - Show count per status
   - Highlight current status

4. **Task Preview**:
   - Show description snippet
   - Show dependencies count
   - Show last updated time

### Testing Strategy

- Mock task list and test selection logic
- Test filtering combinations
- Test edge cases (empty list, single task)
- Manual testing in different terminals

## Events

### 2025-10-18 16:00 - Created
- Task created based on TODO in `src/cli/commands/task/pick.py`
- Prioritized as Low (nice-to-have UX improvement)
- Can be implemented independently without blocking other work

### 2025-10-18 22:36 - Started work
- Moved task from backlog to active
- Beginning implementation using Rich library (Option 1 approach)
- Will implement numbered selection with task grouping by status
- Plan: Create interactive picker, add tests, update documentation

### 2025-10-18 22:50 - Implementation completed
- Implemented `display_interactive_picker()` function with Rich library
- Added task grouping by status (backlog, todo, inprogress, blocked, done)
- Implemented numbered selection with input validation
- Added priority indicators (↑↑, ↑, -, ↓, ↓↓) for all tasks
- Supports both grouped and ungrouped display modes
- Integrated with `anyt task pick` command
- Added filter support (--status, --project, --mine)
- Handles edge cases: empty list, invalid input, cancellation
- All 141 unit tests passing (including 14 new tests for interactive picker)
- Code passes linting and type checking
- Next: Update documentation

### 2025-10-18 23:00 - Task completed
- Updated `docs/CLI_USAGE.md` with interactive picker documentation
- Added detailed examples and usage instructions
- Documented all filter options and interactive picker behavior
- All acceptance criteria met
- Task ready to be moved to done/
