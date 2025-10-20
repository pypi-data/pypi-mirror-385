# T7-31: Migration Script - Folder to Database

## Priority
Medium

## Status
Completed

## Description
Create a migration script to import existing tasks from `.anyt/tasks/` markdown files into the database via the AnyTask CLI. This enables switching from folder-based to database-backed task management while preserving all existing task data.

## Objectives
1. Parse markdown task files
2. Extract task metadata (title, status, priority, etc.)
3. Import tasks via CLI commands
4. Preserve task relationships (dependencies)
5. Create backup before migration

## Acceptance Criteria
- [x] Script `scripts/migrate_tasks_to_db.py` created
- [x] Parses all `.md` files in `.anyt/tasks/`
- [x] Extracts: title, status, priority, description, dependencies
- [x] Maps folder location to status (done/ → done, active/ → inprogress, backlog/ → backlog)
- [x] Creates tasks via `anyt task add` CLI commands
- [x] Sets up dependencies via `anyt task dep add`
- [x] Preserves task IDs where possible (T7-19 → include in title/description)
- [x] Creates backup of `.anyt/tasks/` before migration
- [x] Generates migration report (tasks created, errors, warnings)
- [x] Dry-run mode to preview changes

## Dependencies
- T7-27 (JSON output for CLI)

## Estimated Effort
4-5 hours

## Technical Notes

### Script Structure

```python
#!/usr/bin/env python3
"""Migrate tasks from .anyt/tasks/ markdown files to AnyTask database."""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List

def parse_task_file(file_path: Path) -> Dict:
    """Parse a markdown task file."""
    content = file_path.read_text()

    # Extract metadata
    task_id = extract_task_id(file_path.name)  # e.g., T7-19
    title = extract_title(content)
    priority = extract_priority(content)
    status = infer_status(file_path)
    description = extract_description(content)
    dependencies = extract_dependencies(content)

    return {
        "task_id": task_id,
        "title": title,
        "priority": priority,
        "status": status,
        "description": description,
        "dependencies": dependencies,
        "file_path": str(file_path)
    }

def extract_task_id(filename: str) -> str:
    """Extract task ID from filename (e.g., T7-19-Tool-Name.md → T7-19)."""
    match = re.match(r'(T\d+-\d+)', filename)
    return match.group(1) if match else None

def extract_title(content: str) -> str:
    """Extract title from markdown (first # heading)."""
    match = re.search(r'^# (.+)$', content, re.MULTILINE)
    return match.group(1) if match else "Untitled Task"

def extract_priority(content: str) -> int:
    """Extract priority from metadata section."""
    # Look for "## Priority\nHigh/Medium/Low"
    match = re.search(r'## Priority\s+(High|Medium|Low)', content, re.IGNORECASE)
    if match:
        priority_map = {"high": 1, "medium": 0, "low": -1}
        return priority_map.get(match.group(1).lower(), 0)
    return 0

def infer_status(file_path: Path) -> str:
    """Infer status from folder location."""
    if "done/" in str(file_path):
        return "done"
    elif "active/" in str(file_path):
        return "inprogress"
    elif "cancelled/" in str(file_path):
        return "canceled"
    else:
        return "backlog"

def extract_description(content: str) -> str:
    """Extract description section."""
    # Get content between ## Description and next ##
    match = re.search(r'## Description\s+(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if match:
        desc = match.group(1).strip()
        # Include original task ID in description
        return desc
    return ""

def extract_dependencies(content: str) -> List[str]:
    """Extract dependencies from Dependencies section."""
    # Look for "## Dependencies\n- T7-19: ..."
    deps = []
    match = re.search(r'## Dependencies\s+(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if match:
        dep_text = match.group(1)
        # Find all T#-# patterns
        deps = re.findall(r'(T\d+-\d+)', dep_text)
    return deps

def create_task_via_cli(task: Dict, project_id: int, dry_run: bool = False) -> str:
    """Create task using CLI."""
    cmd = [
        "uv", "run", "src/cli/main.py", "task", "add",
        task["title"],
        "--description", f"[Migrated from {task['task_id']}]\n\n{task['description']}",
        "--priority", str(task["priority"]),
        "--status", task["status"],
        "--project", str(project_id),
        "--json"
    ]

    if dry_run:
        print(f"[DRY RUN] Would run: {' '.join(cmd)}")
        return "DEV-DRY-RUN"

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Failed to create task: {result.stderr}")

    response = json.loads(result.stdout)
    return response["data"]["identifier"]

def add_dependency_via_cli(task_id: str, depends_on: str, dry_run: bool = False):
    """Add dependency using CLI."""
    cmd = [
        "uv", "run", "src/cli/main.py", "task", "dep", "add",
        task_id,
        "--on", depends_on
    ]

    if dry_run:
        print(f"[DRY RUN] Would run: {' '.join(cmd)}")
        return

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Warning: Failed to add dependency {task_id} → {depends_on}: {result.stderr}")

def migrate_tasks(dry_run: bool = False):
    """Main migration function."""
    tasks_dir = Path(".anyt/tasks")

    # Backup
    if not dry_run:
        import shutil
        backup_dir = Path(".anyt/tasks.backup")
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(tasks_dir, backup_dir)
        print(f"✓ Created backup at {backup_dir}")

    # Find all task files
    task_files = list(tasks_dir.rglob("T*.md"))
    print(f"Found {len(task_files)} task files")

    # Parse all tasks
    parsed_tasks = []
    for file_path in task_files:
        try:
            task = parse_task_file(file_path)
            parsed_tasks.append(task)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    # Sort by task ID to maintain order
    parsed_tasks.sort(key=lambda t: t.get("task_id", ""))

    # Get project ID
    if not dry_run:
        result = subprocess.run(
            ["uv", "run", "src/cli/main.py", "workspace", "show", "--json"],
            capture_output=True,
            text=True
        )
        workspace = json.loads(result.stdout)["data"]
        # Assume first project for now
        project_id = 1  # Or get from config
    else:
        project_id = 1

    # Create tasks
    task_id_map = {}  # old_id → new_id
    created = []
    errors = []

    for task in parsed_tasks:
        try:
            new_id = create_task_via_cli(task, project_id, dry_run)
            task_id_map[task["task_id"]] = new_id
            created.append((task["task_id"], new_id, task["title"]))
            print(f"✓ Created {task['task_id']} → {new_id}: {task['title']}")
        except Exception as e:
            errors.append((task["task_id"], str(e)))
            print(f"✗ Failed {task['task_id']}: {e}")

    # Add dependencies (second pass)
    for task in parsed_tasks:
        old_id = task["task_id"]
        if old_id not in task_id_map:
            continue  # Task creation failed

        new_id = task_id_map[old_id]

        for dep_old_id in task["dependencies"]:
            if dep_old_id in task_id_map:
                dep_new_id = task_id_map[dep_old_id]
                add_dependency_via_cli(new_id, dep_new_id, dry_run)
                print(f"  Added dependency: {new_id} → {dep_new_id}")

    # Summary
    print(f"\n{'='*50}")
    print(f"Migration {'Preview' if dry_run else 'Complete'}!")
    print(f"Tasks created: {len(created)}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for task_id, error in errors:
            print(f"  {task_id}: {error}")

if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("Running in DRY RUN mode (no changes will be made)\n")

    migrate_tasks(dry_run=dry_run)
```

### Usage

```bash
# Preview migration
python scripts/migrate_tasks_to_db.py --dry-run

# Run migration
python scripts/migrate_tasks_to_db.py

# After migration, rename old folder
mv .anyt/tasks .anyt/tasks.old
```

### Post-Migration Validation

```bash
# Check migrated tasks
uv run src/cli/main.py task list

# Check dependencies
uv run src/cli/main.py graph --full
```

## Events

### 2025-10-18 19:15 - Started work
- Moved task from backlog to active
- Verified dependency T7-27 (JSON output) is complete
- Beginning implementation of migration script

### 2025-10-18 19:25 - Completed implementation
- Created `scripts/migrate_tasks_to_db.py` with full functionality
- Implemented all parsing functions (task ID, title, priority, status, description, dependencies)
- Implemented CLI integration using `uv run anyt` commands with JSON output
- Added backup functionality before migration
- Implemented comprehensive error handling and reporting
- Added dry-run mode for safe testing
- Tested dry-run mode successfully: parsed 35 tasks, would create 35 tasks and 28 dependencies with 0 errors
- All acceptance criteria met
- Task moved to done/

## Related Files
- `scripts/migrate_tasks_to_db.py` - New migration script
- `.anyt/tasks/` - Source folder
- `.anyt/tasks.backup/` - Backup created by script
