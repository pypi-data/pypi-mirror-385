"""Task commands for AnyTask CLI."""

import typer

from .crud import (
    add_note_to_task,
    add_task,
    create_task_from_template,
    edit_task,
    mark_done,
    remove_task,
    show_task,
)
from .dependencies import add_dependency, list_dependencies, remove_dependency
from .helpers import (
    format_priority,
    format_relative_time,
    get_active_task_id,
    get_workspace_or_exit,
    normalize_identifier,
    resolve_workspace_context,
    truncate_text,
)
from .list import list_tasks
from .pick import pick_task
from .suggest import suggest_tasks

# Main task command app
app = typer.Typer(help="Manage tasks")

# Register CRUD commands
app.command("add")(add_task)
app.command("create")(create_task_from_template)
app.command("list")(list_tasks)
app.command("show")(show_task)
app.command("edit")(edit_task)
app.command("done")(mark_done)
app.command("note")(add_note_to_task)
app.command("rm")(remove_task)
app.command("pick")(pick_task)
app.command("suggest")(suggest_tasks)

# Dependency management subcommands
dep_app = typer.Typer(help="Manage task dependencies")
dep_app.command("add")(add_dependency)
dep_app.command("rm")(remove_dependency)
dep_app.command("list")(list_dependencies)

# Add dependency subcommand to main app
app.add_typer(dep_app, name="dep")

# Export the app and helper functions for use by other modules
__all__ = [
    "app",
    "format_priority",
    "format_relative_time",
    "get_active_task_id",
    "get_workspace_or_exit",
    "normalize_identifier",
    "resolve_workspace_context",
    "truncate_text",
]
