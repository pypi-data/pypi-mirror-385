"""Workspace context and active task management."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ActiveTask(BaseModel):
    """Active task stored in .anyt/active_task.json."""

    task_id: str = Field(..., description="Task identifier (e.g., 'DEV-123')")
    version: int = Field(..., description="Task version for optimistic locking")
    title: str = Field(..., description="Task title")
    status: str = Field(..., description="Task status")
    workspace_id: int = Field(..., description="Workspace ID")
    last_sync: str = Field(..., description="ISO timestamp of last sync")


class WorkspaceContext:
    """Manages workspace context and active task."""

    def __init__(self, workspace_dir: Path | None = None):
        """Initialize workspace context.

        Args:
            workspace_dir: Directory containing .anyt/ folder (defaults to cwd)
        """
        self.workspace_dir = workspace_dir or Path.cwd()
        self.anyt_dir = self.workspace_dir / ".anyt"
        self.active_task_file = self.anyt_dir / "active_task.json"

    def ensure_anyt_dir(self):
        """Ensure .anyt directory exists."""
        self.anyt_dir.mkdir(exist_ok=True)

    def get_active_task(self) -> ActiveTask | None:
        """Get active task from file."""
        if not self.active_task_file.exists():
            return None

        try:
            with open(self.active_task_file, "r") as f:
                data = json.load(f)
            return ActiveTask(**data)
        except (json.JSONDecodeError, ValueError):
            return None

    def set_active_task(self, task: dict[str, Any]) -> ActiveTask:
        """Set active task and save to file.

        Args:
            task: Task data from API

        Returns:
            ActiveTask model
        """
        self.ensure_anyt_dir()

        active_task = ActiveTask(
            task_id=task["identifier"],
            version=task["version"],
            title=task["title"],
            status=task["status"],
            workspace_id=task["workspace_id"],
            last_sync=datetime.utcnow().isoformat() + "Z",
        )

        with open(self.active_task_file, "w") as f:
            json.dump(active_task.model_dump(), f, indent=2)

        return active_task

    def clear_active_task(self):
        """Clear active task file."""
        if self.active_task_file.exists():
            self.active_task_file.unlink()

    def update_active_task_version(self, version: int):
        """Update version in active task file."""
        active_task = self.get_active_task()
        if not active_task:
            return

        active_task.version = version
        active_task.last_sync = datetime.utcnow().isoformat() + "Z"

        with open(self.active_task_file, "w") as f:
            json.dump(active_task.model_dump(), f, indent=2)
