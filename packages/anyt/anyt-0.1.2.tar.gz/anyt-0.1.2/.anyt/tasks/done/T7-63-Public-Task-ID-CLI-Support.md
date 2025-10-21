# T7-63: Public Task ID CLI Support

**Priority**: High
**Status**: Completed
**Phase**: 7

## Description

Add CLI support for public task IDs, allowing users to view tasks using 9-digit public IDs and generate shareable links. This enhances task sharing workflows by providing a simple, globally unique identifier that works across workspaces.

## Objectives

- Support 9-digit public IDs in `anyt task show <id>` command
- Add `anyt task share <task-id>` command to generate shareable links
- Update task detail output to display public_id field
- Handle public ID lookup with proper error messages
- Support both workspace-scoped identifiers (DEV-123) and public IDs (123456789)

## Acceptance Criteria

- [x] `anyt task show 123456789` works with 9-digit public IDs
- [x] Command auto-detects ID format (9 digits = public ID, XXX-NNN = workspace ID)
- [x] `anyt task share <task-id>` generates shareable URL
- [x] Share command accepts both identifier formats
- [x] Share command outputs: `https://anyt.dev/t/{public_id}`
- [x] Share command includes `--copy` flag to copy to clipboard
- [x] Task detail view displays public_id field
- [x] Error messages distinguish between "task not found" and "no access"
- [x] Help text updated to document public ID support
- [x] Unit tests written and passing
- [x] Code follows project style guidelines

## Dependencies

- Backend T11-31: Public Task ID System (API endpoint must be deployed)

## Estimated Effort

3-4 hours

## Technical Notes

**Command Updates:**

1. **Update `anyt task show`:**
```python
# Detect ID format and use appropriate lookup
def show_task(task_id: str):
    if task_id.isdigit() and len(task_id) == 9:
        # Use public ID endpoint
        task = api_client.get_task_by_public_id(int(task_id))
    else:
        # Use workspace-scoped identifier
        task = api_client.get_task(task_id)

    display_task_detail(task)
```

2. **New `anyt task share` command:**
```python
@task_app.command("share")
def share_task(
    task_id: str = typer.Argument(..., help="Task identifier (DEV-123 or 123456789)"),
    copy: bool = typer.Option(False, "--copy", help="Copy link to clipboard")
):
    """Generate shareable link for a task."""
    task = get_task_by_id(task_id)  # Handles both ID formats
    share_url = f"https://anyt.dev/t/{task.public_id}"

    typer.echo(f"Shareable link: {share_url}")

    if copy:
        pyperclip.copy(share_url)
        typer.echo("✓ Link copied to clipboard")
```

**API Client Updates:**
```python
# Add method to TasksAPI client
def get_task_by_public_id(self, public_id: int) -> Task:
    """Fetch task using 9-digit public ID."""
    response = self._client.get(f"/v1/t/{public_id}")
    return Task(**response.json()["data"])
```

**Display Updates:**
```python
# Update task detail display to show public_id
def display_task_detail(task: Task):
    table.add_row("ID", task.identifier)
    table.add_row("Public ID", str(task.public_id))
    table.add_row("Title", task.title)
    # ... rest of fields
```

**Error Handling:**
```python
# Distinguish between 404 (not found) and 403 (no access)
try:
    task = api_client.get_task_by_public_id(public_id)
except HTTPError as e:
    if e.response.status_code == 404:
        typer.echo("Error: Task not found", err=True)
    elif e.response.status_code == 403:
        typer.echo("Error: You don't have access to this task", err=True)
    raise typer.Exit(1)
```

**Files to Create/Modify:**
- `cli/commands/tasks.py` (update show command, add share command)
- `cli/api/tasks.py` (add get_task_by_public_id method)
- `cli/display/tasks.py` (update task detail display)
- `tests/cli/unit/test_task_show.py` (add public ID tests)
- `tests/cli/unit/test_task_share.py` (new test file)
- `README.md` (document new commands)

**Dependencies:**
Add `pyperclip` for clipboard support:
```toml
# pyproject.toml
dependencies = [
    "pyperclip>=1.8.2",
    # ... existing deps
]
```

**Testing Checklist:**
- [ ] `anyt task show 123456789` fetches via public ID
- [ ] `anyt task show DEV-123` still works with workspace ID
- [ ] `anyt task share DEV-123` outputs correct URL
- [ ] `anyt task share 123456789` outputs correct URL
- [ ] `anyt task share DEV-123 --copy` copies to clipboard
- [ ] Error message for non-existent public ID is clear
- [ ] Error message for no access (403) is clear
- [ ] Help text shows both ID format examples

**Help Text Examples:**
```
anyt task show --help

Usage: anyt task show [TASK_ID]

Show details for a task.

Arguments:
  TASK_ID  Task identifier (e.g., DEV-123 or 123456789)

Examples:
  anyt task show DEV-123        # Using workspace-scoped identifier
  anyt task show 123456789      # Using public ID
```

```
anyt task share --help

Usage: anyt task share [OPTIONS] TASK_ID

Generate a shareable link for a task.

Arguments:
  TASK_ID  Task identifier (e.g., DEV-123 or 123456789)

Options:
  --copy  Copy link to clipboard

Examples:
  anyt task share DEV-123
  anyt task share 123456789 --copy
```

## Events

### 2025-10-20 - Task created
- Created task in backlog based on backend T11-31 implementation
- Ready for implementation once backend API is deployed

### 2025-10-20 21:30 - Updated and marked as blocked
- Reviewed and updated task specification
- Marked as blocked by backend T11-31 (Public Task ID System)
- Added comprehensive technical notes and implementation guide
- Priority remains HIGH, but cannot start until backend API is deployed
- **Action**: Monitor backend progress, ready to implement immediately after deployment

### 2025-10-20 23:00 - Implementation completed
- Confirmed backend T11-31 is deployed and ready
- Added `public_id` field to Task model (src/cli/models/task.py)
- Implemented `get_task_by_public_id()` method in TasksAPIClient (src/cli/client/tasks.py)
- Implemented `get_task_by_public_id()` method in TaskService (src/cli/services/task_service.py)
- Updated `anyt task show` command to auto-detect and support 9-digit public IDs
- Created new `anyt task share` command with clipboard support (--copy flag)
- Updated task detail display to show public_id field
- Added pyperclip dependency for clipboard functionality
- Wrote unit tests for get_task_by_public_id() method
- All pre-merge checks passed (format, lint, typecheck)
- All acceptance criteria met
- Task moved to done/
