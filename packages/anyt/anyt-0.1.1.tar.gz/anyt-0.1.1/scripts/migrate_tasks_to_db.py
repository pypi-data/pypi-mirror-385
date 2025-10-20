#!/usr/bin/env python3
"""Migrate tasks from .anyt/tasks/ markdown files to AnyTask database."""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


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
        "file_path": str(file_path),
    }


def extract_task_id(filename: str) -> Optional[str]:
    """Extract task ID from filename (e.g., T7-19-Tool-Name.md → T7-19)."""
    match = re.match(r"(T\d+-\d+)", filename)
    return match.group(1) if match else None


def extract_title(content: str) -> str:
    """Extract title from markdown (first # heading)."""
    match = re.search(r"^# (.+)$", content, re.MULTILINE)
    if match:
        # Remove task ID prefix if present (e.g., "T7-19: Title" → "Title")
        title = match.group(1)
        title = re.sub(r"^T\d+-\d+:\s*", "", title)
        return title
    return "Untitled Task"


def extract_priority(content: str) -> int:
    """Extract priority from metadata section."""
    # Look for "## Priority\nHigh/Medium/Low"
    match = re.search(r"## Priority\s+(High|Medium|Low)", content, re.IGNORECASE)
    if match:
        priority_map = {"high": 1, "medium": 0, "low": -1}
        return priority_map.get(match.group(1).lower(), 0)
    return 0


def infer_status(file_path: Path) -> str:
    """Infer status from folder location."""
    path_str = str(file_path)
    if "done/" in path_str:
        return "done"
    elif "active/" in path_str:
        return "inprogress"
    elif "cancelled/" in path_str:
        return "canceled"
    else:
        return "backlog"


def extract_description(content: str) -> str:
    """Extract description section."""
    # Get content between ## Description and next ##
    match = re.search(r"## Description\s+(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if match:
        desc = match.group(1).strip()
        return desc
    return ""


def extract_dependencies(content: str) -> List[str]:
    """Extract dependencies from Dependencies section."""
    # Look for "## Dependencies\n- T7-19: ..."
    deps = []
    match = re.search(r"## Dependencies\s+(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if match:
        dep_text = match.group(1)
        # Find all T#-# patterns
        deps = re.findall(r"(T\d+-\d+)", dep_text)
    return deps


def create_task_via_cli(task: Dict, dry_run: bool = False) -> str:
    """Create task using CLI."""
    # Build description with original task ID
    full_description = f"[Migrated from {task['task_id']}]\n\n{task['description']}"

    cmd = [
        "uv",
        "run",
        "anyt",
        "task",
        "add",
        task["title"],
        "--description",
        full_description,
        "--priority",
        str(task["priority"]),
        "--status",
        task["status"],
        "--json",
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
    cmd = ["uv", "run", "anyt", "task", "dep", "add", task_id, "--on", depends_on]

    if dry_run:
        print(f"[DRY RUN] Would run: {' '.join(cmd)}")
        return

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"Warning: Failed to add dependency {task_id} → {depends_on}: {result.stderr}"
        )


def migrate_tasks(dry_run: bool = False):
    """Main migration function."""
    tasks_dir = Path(".anyt/tasks")

    if not tasks_dir.exists():
        print(f"Error: Tasks directory not found at {tasks_dir}")
        sys.exit(1)

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

    if len(task_files) == 0:
        print("No task files found. Nothing to migrate.")
        return

    # Parse all tasks
    parsed_tasks = []
    parse_errors = []

    for file_path in task_files:
        try:
            task = parse_task_file(file_path)
            if task["task_id"]:
                parsed_tasks.append(task)
            else:
                parse_errors.append((file_path, "Could not extract task ID"))
        except Exception as e:
            parse_errors.append((file_path, str(e)))
            print(f"Error parsing {file_path}: {e}")

    # Sort by task ID to maintain order
    parsed_tasks.sort(key=lambda t: t.get("task_id", ""))

    print(f"\nSuccessfully parsed: {len(parsed_tasks)} tasks")
    if parse_errors:
        print(f"Parse errors: {len(parse_errors)}")
        for file_path, error in parse_errors:
            print(f"  {file_path}: {error}")

    # Create tasks
    task_id_map = {}  # old_id → new_id
    created = []
    errors = []

    print("\nCreating tasks...")
    for task in parsed_tasks:
        try:
            new_id = create_task_via_cli(task, dry_run)
            task_id_map[task["task_id"]] = new_id
            created.append((task["task_id"], new_id, task["title"]))
            print(f"✓ Created {task['task_id']} → {new_id}: {task['title']}")
        except Exception as e:
            errors.append((task["task_id"], str(e)))
            print(f"✗ Failed {task['task_id']}: {e}")

    # Add dependencies (second pass)
    print("\nAdding dependencies...")
    dep_count = 0

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
                dep_count += 1
            else:
                print(f"  Warning: Dependency {dep_old_id} not found for task {old_id}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Migration {'Preview' if dry_run else 'Complete'}!")
    print(f"{'=' * 60}")
    print(f"Tasks parsed:     {len(parsed_tasks)}")
    print(f"Tasks created:    {len(created)}")
    print(f"Dependencies:     {dep_count}")
    print(f"Errors:           {len(errors)}")

    if errors:
        print("\nErrors:")
        for task_id, error in errors:
            print(f"  {task_id}: {error}")

    if not dry_run and len(created) > 0:
        print("\n✓ Migration completed successfully!")
        print("✓ Backup saved to: .anyt/tasks.backup/")
        print("\nNext steps:")
        print("  1. Verify migrated tasks: uv run anyt task list")
        print("  2. Check dependencies: uv run anyt task dep list <task-id>")
        print("  3. If everything looks good, you can rename the old folder:")
        print("     mv .anyt/tasks .anyt/tasks.old")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=" * 60)
        print("Running in DRY RUN mode (no changes will be made)")
        print("=" * 60)
        print()

    migrate_tasks(dry_run=dry_run)
