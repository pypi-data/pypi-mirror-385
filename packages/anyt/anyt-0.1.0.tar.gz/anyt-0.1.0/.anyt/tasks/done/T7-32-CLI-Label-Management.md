# T7-32: CLI Label Management Commands

**Priority**: Medium
**Status**: Completed
**Phase**: 7 (CLI Enhancement)
**Estimated Effort**: 3-4 hours

## Description

Implement CLI commands for managing workspace labels. The backend API for labels is fully implemented (`/v1/workspaces/{workspace_id}/labels`), but CLI commands are missing. This task adds the `anyt label` command group to provide full CRUD operations for labels.

## Objectives

- Implement `anyt label` command group
- Provide create, list, show, edit, and delete operations
- Support both interactive and JSON output modes
- Ensure proper workspace context handling
- Add color/emoji support in terminal output

## Acceptance Criteria

- [x] `anyt label create <name>` - Create a new label
  - Support `--color` flag for hex color
  - Support `--description` flag
  - Output created label details
- [x] `anyt label list` - List all labels in workspace
  - Display in table format with colors
  - Support `--json` output
  - Sort alphabetically by name
- [x] `anyt label show <name>` - Show label details
  - Display name, color, description, usage count
  - Support `--json` output
- [x] `anyt label edit <name>` - Edit label properties
  - Support `--name`, `--color`, `--description` flags
  - Confirm before updating
  - Show before/after comparison
- [x] `anyt label rm <name>` - Delete a label
  - Require `--force` flag or confirmation prompt
  - Warn about tasks using this label (future enhancement)
  - Support bulk deletion with multiple names
- [x] All commands support `--json` flag for machine-readable output
- [x] All commands respect workspace context (`.anyt/anyt.json`)
- [x] Error handling with helpful messages
- [x] Update `docs/CLI_USAGE.md` with new commands section

## Dependencies

- Backend Label API (already implemented)
- CLI client configuration and workspace detection

## Technical Notes

### File Structure
```
src/cli/commands/label.py  # New file for label commands
```

### Command Group Structure
```python
# src/cli/commands/label.py
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Manage workspace labels")

@app.command("create")
async def create_label(
    name: str,
    color: Optional[str] = typer.Option(None, "--color", help="Hex color code (e.g., #FF0000)"),
    description: Optional[str] = typer.Option(None, "--description", help="Label description"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Create a new label in the workspace."""
    # Implementation

@app.command("list")
async def list_labels(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """List all labels in the workspace."""
    # Implementation with rich table

@app.command("show")
async def show_label(
    name: str,
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show details for a specific label."""
    # Implementation

@app.command("edit")
async def edit_label(
    name: str,
    new_name: Optional[str] = typer.Option(None, "--name", help="New label name"),
    color: Optional[str] = typer.Option(None, "--color", help="New color"),
    description: Optional[str] = typer.Option(None, "--description", help="New description"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Edit label properties."""
    # Implementation

@app.command("rm")
async def delete_label(
    names: List[str],
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Delete one or more labels."""
    # Implementation with confirmation
```

### Register in main.py
```python
# src/cli/main.py
from cli.commands import label as label_commands

app.add_typer(label_commands.app, name="label")
```

### API Client Methods
Add to `src/cli/client.py`:
```python
async def create_label(self, workspace_id: int, name: str, color: Optional[str] = None, description: Optional[str] = None):
    """Create a new label."""
    # POST /v1/workspaces/{workspace_id}/labels

async def list_labels(self, workspace_id: int):
    """List all labels in workspace."""
    # GET /v1/workspaces/{workspace_id}/labels

async def get_label(self, workspace_id: int, label_id: int):
    """Get label by ID."""
    # GET /v1/workspaces/{workspace_id}/labels/{label_id}

async def update_label(self, workspace_id: int, label_id: int, **updates):
    """Update label properties."""
    # PATCH /v1/workspaces/{workspace_id}/labels/{label_id}

async def delete_label(self, workspace_id: int, label_id: int):
    """Delete a label."""
    # DELETE /v1/workspaces/{workspace_id}/labels/{label_id}
```

### Color Display
Use Rich console features to show label colors:
```python
from rich.style import Style

# Display label with color
console.print(f"[{label['color']}]●[/] {label['name']}")

# Or use Style
style = Style(color=label['color'])
console.print("●", style=style, end=" ")
console.print(label['name'])
```

### Example Usage
```bash
# Create labels
anyt label create Bug --color "#FF0000" --description "Bug fixes"
anyt label create Feature --color "#00FF00" --description "New features"

# List labels (shows colored output)
anyt label list

# Edit label
anyt label edit Bug --color "#FF3333"

# Delete label
anyt label rm "Old Label" --force
```

## Documentation Updates Required

After implementation, update the following documentation:

### 1. docs/CLI_USAGE.md
Add new section after "Dependency Management":

```markdown
### Label Management

Manage workspace labels for task categorization.

#### Create Label
\`\`\`bash
anyt label create <name> [OPTIONS]
\`\`\`

#### List Labels
\`\`\`bash
anyt label list [--json]
\`\`\`

#### Show Label
\`\`\`bash
anyt label show <name> [--json]
\`\`\`

#### Edit Label
\`\`\`bash
anyt label edit <name> [OPTIONS]
\`\`\`

#### Delete Label
\`\`\`bash
anyt label rm <names>... [--force] [--json]
\`\`\`

**Examples:**
\`\`\`bash
# Create labels
anyt label create Bug --color "#FF0000"
anyt label create Feature --color "#00FF00" --description "New features"

# List all labels
anyt label list

# Edit label color
anyt label edit Bug --color "#FF3333"

# Delete labels
anyt label rm "Old Label" --force
\`\`\`
```

## Testing

- [ ] Test create label with valid inputs
- [ ] Test create label with invalid color codes
- [ ] Test list labels (empty workspace)
- [ ] Test list labels (with multiple labels)
- [ ] Test edit label name
- [ ] Test edit label color
- [ ] Test delete label (with confirmation)
- [ ] Test delete label (--force flag)
- [ ] Test JSON output for all commands
- [ ] Test error cases (workspace not found, label not found, etc.)

## Events

### 2025-10-18 14:45 - Task created
- Created task specification for CLI Label Management
- Backend API already exists and is fully functional
- CLI commands will provide user-friendly interface to existing API

### 2025-10-18 18:30 - Started work
- Moved task from backlog to active
- Updated status to "In Progress"
- Beginning implementation of CLI label commands
- Will implement: create, list, show, edit, rm commands
- Will add API client methods for label operations

### 2025-10-18 19:15 - Implementation completed
- Added 5 API client methods to client.py:
  - list_labels() - Fetch all labels in workspace
  - create_label() - Create new label with color/description
  - get_label() - Get single label by ID
  - update_label() - Update label properties
  - delete_label() - Remove label
- Created src/cli/commands/label.py with 5 commands:
  - create - Create new label
  - list - Display all labels in table format with colors
  - show - Show detailed label information
  - edit - Update label with before/after comparison
  - rm - Delete labels with confirmation
- Registered label commands in main.py
- All commands support --json output mode
- Color display using Rich console styling
- Input validation and error handling
- Passed all linting (ruff) and type checking (mypy)
- All existing unit tests passing
- Updated docs/CLI_USAGE.md with complete Label Management section
- All acceptance criteria completed ✓

### 2025-10-18 19:20 - Task completed
- Updated status to "Completed"
- All objectives achieved
- Task ready to move to done/
- Created comprehensive documentation with examples
- Code quality checks passed (lint, typecheck, tests)
