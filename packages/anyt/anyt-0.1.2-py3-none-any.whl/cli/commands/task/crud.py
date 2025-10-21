"""CRUD commands for tasks (add, show, edit, done, rm)."""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional

import pyperclip  # type: ignore[import-untyped]
import typer
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt
from typing_extensions import Annotated

from cli.client.projects import ProjectsAPIClient
from cli.config import ActiveTaskConfig, GlobalConfig
from cli.models.common import Priority, Status
from cli.models.task import TaskCreate, TaskUpdate
from cli.services.task_service import TaskService
from cli.services.workspace_service import WorkspaceService

from .helpers import (
    console,
    find_similar_tasks,
    format_priority,
    format_relative_time,
    get_active_task_id,
    get_workspace_or_exit,
    normalize_identifier,
    output_json,
    resolve_workspace_context,
    truncate_text,
)


def add_task(
    title: Annotated[str, typer.Argument(help="Task title")],
    description: Annotated[
        Optional[str],
        typer.Option("-d", "--description", help="Task description"),
    ] = None,
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Phase/milestone identifier (e.g., T3, Phase 1)"),
    ] = None,
    priority: Annotated[
        int,
        typer.Option("-p", "--priority", help="Priority (-2 to 2, default: 0)"),
    ] = 0,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Comma-separated labels"),
    ] = None,
    status: Annotated[
        str,
        typer.Option("--status", help="Task status (default: backlog)"),
    ] = "backlog",
    owner: Annotated[
        Optional[str],
        typer.Option("--owner", help="Assign to user or agent ID"),
    ] = None,
    estimate: Annotated[
        Optional[int],
        typer.Option("--estimate", help="Time estimate in hours"),
    ] = None,
    project: Annotated[
        Optional[int],
        typer.Option(
            "--project",
            help="Project ID (uses current/default project if not specified)",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Create a new task."""
    ws_config, global_config = get_workspace_or_exit()
    service: TaskService = TaskService.from_config(global_config)  # type: ignore[assignment]
    projects_client: ProjectsAPIClient = ProjectsAPIClient.from_config(global_config)  # type: ignore[assignment]

    async def create() -> None:
        try:
            # Validate priority range
            if priority < -2 or priority > 2:
                if json_output:
                    output_json(
                        {
                            "error": "ValidationError",
                            "message": "Invalid priority value",
                            "details": "Priority must be between -2 and 2\n  -2: Lowest\n  -1: Low\n   0: Normal (default)\n   1: High\n   2: Highest",
                        },
                        success=False,
                    )
                else:
                    console.print("[red]✗ Error:[/red] Invalid priority value")
                    console.print()
                    console.print("  Priority must be between -2 and 2")
                    console.print("    -2: Lowest")
                    console.print("    -1: Low")
                    console.print("     0: Normal (default)")
                    console.print("     1: High")
                    console.print("     2: Highest")
                raise typer.Exit(1)

            # If project not specified, use the current project from the API
            project_id = project
            if not project_id:
                try:
                    # Fetch the current/default project for this workspace
                    current_project = await projects_client.get_current_project(
                        int(ws_config.workspace_id)
                    )
                    project_id = current_project.id

                    if not json_output:
                        console.print(
                            f"[dim]Using project: {current_project.name} (ID: {project_id})[/dim]"
                        )
                except Exception as e:
                    if json_output:
                        output_json(
                            {
                                "error": "ProjectError",
                                "message": f"Failed to get current project: {str(e)}",
                                "hint": "Specify --project ID explicitly",
                            },
                            success=False,
                        )
                    else:
                        console.print(
                            f"[red]Error:[/red] Failed to get current project: {e}"
                        )
                        console.print(
                            "Specify the project ID explicitly with --project <ID>"
                        )
                    raise typer.Exit(1)

            # Parse labels
            label_list = []
            if labels:
                label_list = [label.strip() for label in labels.split(",")]

            # Ensure project_id is set
            if project_id is None:
                raise ValueError("Project ID is required but not set")

            # Convert priority to enum
            priority_enum = Priority(priority)
            # Convert status to enum
            status_enum = Status(status)

            # Create task using typed model
            task_create = TaskCreate(
                title=title,
                description=description,
                phase=phase,
                status=status_enum,
                priority=priority_enum,
                owner_id=owner,
                labels=label_list,
                estimate=estimate,
            )

            # Create task via service
            task = await service.create_task_with_validation(
                project_id=project_id,
                task=task_create,
            )

            # Display success
            if json_output:
                output_json(task.model_dump(mode="json"))
            else:
                console.print(
                    f"[green]✓[/green] Created: [cyan]{task.identifier}[/cyan] ({task.title})"
                )

        except typer.Exit:
            raise
        except ValueError as e:
            # Handle enum conversion errors
            if json_output:
                output_json(
                    {"error": "ValidationError", "message": str(e)}, success=False
                )
            else:
                console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:
            if json_output:
                output_json({"error": "CreateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to create task: {e}")
            raise typer.Exit(1)

    asyncio.run(create())


def show_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42, 123456789 for public ID). Uses active task if not specified."
        ),
    ] = None,
    workspace: Annotated[
        Optional[str],
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace identifier or ID (uses current workspace if not specified)",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Show detailed information about a task.

    Supports both workspace-scoped identifiers (DEV-42) and public IDs (123456789).
    """
    # Load global config first (don't require workspace directory yet)
    try:
        global_config = GlobalConfig.load()
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load config: {e}")
        raise typer.Exit(1)

    # Check authentication
    effective_config = global_config.get_effective_config()
    if not effective_config.get("auth_token") and not effective_config.get("agent_key"):
        console.print("[red]Error:[/red] Not authenticated")
        console.print("Run [cyan]anyt auth login[/cyan] first")
        raise typer.Exit(1)

    service: TaskService = TaskService.from_config(global_config)  # type: ignore[assignment]
    workspace_service: WorkspaceService = WorkspaceService.from_config(global_config)  # type: ignore[assignment]

    # Use active task if no identifier provided
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task show DEV-42",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print("Specify a task: [cyan]anyt task show DEV-42[/cyan]")
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)

    async def fetch() -> None:
        try:
            # Check if identifier is a 9-digit public ID
            if identifier.isdigit() and len(identifier) == 9:
                # Use public ID endpoint (no workspace context needed)
                task = await service.get_task_by_public_id(int(identifier))
            else:
                # Resolve workspace context for workspace-scoped identifiers
                workspace_id, workspace_identifier = await resolve_workspace_context(
                    workspace, global_config, workspace_service
                )

                # Normalize identifier for fuzzy matching with workspace prefix
                normalized_id = normalize_identifier(identifier, workspace_identifier)

                # Fetch task using service
                task = await service.get_task(normalized_id)

            # JSON output mode
            if json_output:
                output_json(task.model_dump(mode="json"))
                return

            # Rich console output mode
            console.print()
            console.print(f"[cyan bold]{task.identifier}:[/cyan bold] {task.title}")
            console.print(f"[dim]Public ID: {task.public_id}[/dim]")
            console.print("━" * 60)

            # Status and priority line
            priority_str = format_priority(
                task.priority.value
                if isinstance(task.priority, Priority)
                else task.priority
            )
            console.print(
                f"Status: [yellow]{task.status.value if isinstance(task.status, Status) else task.status}[/yellow]    "
                f"Priority: {priority_str} ({task.priority.value if isinstance(task.priority, Priority) else task.priority})"
            )

            # Owner and labels
            if task.owner_id:
                console.print(f"Owner: {task.owner_id}")
            else:
                console.print("Owner: [dim]unassigned[/dim]")

            if task.labels:
                labels_str = ", ".join(task.labels)
                console.print(f"Labels: [blue]{labels_str}[/blue]")

            # Project
            console.print(f"Project: {task.project_id}")

            # Estimate
            if task.estimate:
                console.print(f"Estimate: {task.estimate}h")

            # Description
            if task.description:
                console.print()
                console.print("[bold]Description:[/bold]")
                console.print()
                # Render description as markdown
                markdown = Markdown(task.description)
                console.print(markdown)

            # Metadata
            console.print()
            created = format_relative_time(task.created_at.isoformat())
            updated = format_relative_time(task.updated_at.isoformat())
            console.print(f"Created: {created}")
            console.print(f"Updated: {updated}")
            console.print(f"Version: {task.version}")
            console.print()

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                # Resolve workspace for error messages
                try:
                    workspace_id, _ = await resolve_workspace_context(
                        workspace, global_config, workspace_service
                    )
                except Exception:
                    workspace_id = None

                # Try to find similar tasks for suggestions
                similar_tasks = []
                if workspace_id:
                    similar_tasks = await find_similar_tasks(
                        service, workspace_id, normalized_id
                    )

                if json_output:
                    output_json(
                        {
                            "error": "NotFoundError",
                            "message": f"Task '{normalized_id}' not found"
                            + (f" in workspace {workspace_id}" if workspace_id else ""),
                            "suggestions": [
                                {
                                    "identifier": t.get("identifier"),
                                    "title": t.get("title"),
                                }
                                for t in similar_tasks
                            ],
                        },
                        success=False,
                    )
                else:
                    workspace_info = (
                        f" in workspace {workspace_id}" if workspace_id else ""
                    )
                    console.print(
                        f"[red]✗ Error:[/red] Task '{normalized_id}' not found{workspace_info}"
                    )

                    if similar_tasks:
                        console.print()
                        console.print("  Did you mean:")
                        for task_dict in similar_tasks:
                            task_id = task_dict.get(
                                "identifier", str(task_dict.get("id", ""))
                            )
                            title = truncate_text(task_dict.get("title", ""), 40)
                            console.print(f"    [cyan]{task_id}[/cyan]  {title}")

                    console.print()
                    console.print("  List all tasks: [cyan]anyt task list[/cyan]")
            else:
                if json_output:
                    output_json(
                        {"error": "FetchError", "message": str(e)}, success=False
                    )
                else:
                    console.print(f"[red]Error:[/red] Failed to fetch task: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch())


def share_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42, 123456789 for public ID). Uses active task if not specified."
        ),
    ] = None,
    copy: Annotated[
        bool,
        typer.Option("--copy", "-c", help="Copy link to clipboard"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Generate a shareable link for a task.

    Creates a public URL that can be shared with anyone who has access to the task.
    The link uses the task's public ID for global accessibility.
    """
    # Load global config
    try:
        global_config = GlobalConfig.load()
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load config: {e}")
        raise typer.Exit(1)

    # Check authentication
    effective_config = global_config.get_effective_config()
    if not effective_config.get("auth_token") and not effective_config.get("agent_key"):
        console.print("[red]Error:[/red] Not authenticated")
        console.print("Run [cyan]anyt auth login[/cyan] first")
        raise typer.Exit(1)

    service: TaskService = TaskService.from_config(global_config)  # type: ignore[assignment]
    workspace_service: WorkspaceService = WorkspaceService.from_config(global_config)  # type: ignore[assignment]

    # Use active task if no identifier provided
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task share DEV-42",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print("Specify a task: [cyan]anyt task share DEV-42[/cyan]")
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)

    async def share() -> None:
        try:
            # Check if identifier is a 9-digit public ID
            if identifier.isdigit() and len(identifier) == 9:
                # Use public ID endpoint (no workspace context needed)
                task = await service.get_task_by_public_id(int(identifier))
            else:
                # Resolve workspace context for workspace-scoped identifiers
                workspace_id, workspace_identifier = await resolve_workspace_context(
                    None, global_config, workspace_service
                )

                # Normalize identifier for fuzzy matching with workspace prefix
                normalized_id = normalize_identifier(identifier, workspace_identifier)

                # Fetch task using service
                task = await service.get_task(normalized_id)

            # Generate shareable URL using public_id
            share_url = f"https://anyt.dev/t/{task.public_id}"

            # Copy to clipboard if requested
            if copy:
                try:
                    pyperclip.copy(share_url)
                    copied = True
                except Exception:
                    # Clipboard may not be available in all environments
                    copied = False

            # Output result
            if json_output:
                output_json(
                    {
                        "task_id": task.identifier,
                        "public_id": task.public_id,
                        "share_url": share_url,
                        "copied": copied if copy else False,
                    }
                )
            else:
                console.print()
                console.print(f"[cyan bold]{task.identifier}:[/cyan bold] {task.title}")
                console.print()
                console.print(f"[green]Shareable link:[/green] {share_url}")
                if copy:
                    if copied:
                        console.print("[green]✓[/green] Link copied to clipboard")
                    else:
                        console.print(
                            "[yellow]⚠[/yellow] Could not copy to clipboard (not available in this environment)"
                        )
                console.print()

        except Exception as e:
            error_msg = str(e)
            if json_output:
                output_json(
                    {"error": "ShareError", "message": error_msg}, success=False
                )
            else:
                console.print(f"[red]Error:[/red] Failed to generate share link: {e}")
            raise typer.Exit(1)

    asyncio.run(share())


def edit_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42) or ID. Uses active task if not specified."
        ),
    ] = None,
    title: Annotated[
        Optional[str],
        typer.Option("--title", help="New title"),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option("-d", "--description", help="New description"),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="New status"),
    ] = None,
    priority: Annotated[
        Optional[int],
        typer.Option("-p", "--priority", help="New priority (-2 to 2)"),
    ] = None,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Comma-separated labels (replaces all labels)"),
    ] = None,
    owner: Annotated[
        Optional[str],
        typer.Option("--owner", help="New owner ID"),
    ] = None,
    estimate: Annotated[
        Optional[int],
        typer.Option("--estimate", help="New time estimate in hours"),
    ] = None,
    ids: Annotated[
        Optional[str],
        typer.Option("--ids", help="Multiple task IDs to edit (comma-separated)"),
    ] = None,
    if_match: Annotated[
        Optional[int],
        typer.Option(
            "--if-match", help="Expected version for optimistic concurrency control"
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview changes without applying"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Edit a task's fields."""
    ws_config, global_config = get_workspace_or_exit()
    service: TaskService = TaskService.from_config(global_config)  # type: ignore[assignment]

    # Get workspace identifier for task ID normalization
    workspace_identifier = ws_config.workspace_identifier

    # Determine task IDs to edit (bulk or single)
    task_ids = []
    if ids:
        # Bulk edit mode
        task_ids = [
            normalize_identifier(tid.strip(), workspace_identifier)
            for tid in ids.split(",")
        ]
    elif identifier:
        # Single task by identifier
        task_ids = [normalize_identifier(identifier, workspace_identifier)]
    else:
        # Use active task
        active_id = get_active_task_id()
        if not active_id:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task edit DEV-42 --status done",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print(
                    "Specify a task: [cyan]anyt task edit DEV-42 --status done[/cyan]"
                )
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)
        task_ids = [normalize_identifier(active_id, workspace_identifier)]

    # Validate priority if provided
    if priority is not None and (priority < -2 or priority > 2):
        if json_output:
            output_json(
                {
                    "error": "ValidationError",
                    "message": "Invalid priority value",
                    "details": "Priority must be between -2 and 2",
                },
                success=False,
            )
        else:
            console.print("[red]✗ Error:[/red] Invalid priority value")
            console.print("  Priority must be between -2 and 2")
        raise typer.Exit(1)

    async def update() -> None:
        try:
            # Parse labels
            label_list = None
            if labels is not None:
                label_list = [label.strip() for label in labels.split(",")]

            # Convert priority and status to enums if provided
            priority_enum = None
            if priority is not None:
                priority_enum = Priority(priority)

            status_enum = None
            if status is not None:
                status_enum = Status(status)

            # Track results for bulk operations
            updated_tasks = []
            errors = []

            # Update each task
            for task_id in task_ids:
                try:
                    # Fetch current task for dry-run or version checking
                    current_task = await service.get_task(task_id)

                    # Check version if --if-match provided
                    if if_match is not None:
                        if current_task.version != if_match:
                            if json_output:
                                errors.append(
                                    {
                                        "task_id": task_id,
                                        "error": "VersionConflict",
                                        "message": "Task was modified by another user",
                                        "current_version": current_task.version,
                                        "provided_version": if_match,
                                    }
                                )
                            else:
                                console.print(
                                    f"[red]✗ Error:[/red] Task {task_id} was modified by another user"
                                )
                                console.print(
                                    f"  Current version: {current_task.version}"
                                )
                                console.print(f"  Your version: {if_match}")
                                console.print()
                                console.print(
                                    f"  Fetch latest with: [cyan]anyt task show {task_id}[/cyan]"
                                )
                            continue

                    # Dry-run mode: show preview
                    if dry_run:
                        if not json_output:
                            console.print(
                                f"[yellow][Preview][/yellow] Would update {task_id}:"
                            )
                            if title is not None:
                                console.print(
                                    f"  title: {current_task.title} → {title}"
                                )
                            if description is not None:
                                console.print("  description: <updated>")
                            if status is not None:
                                console.print(
                                    f"  status: {current_task.status.value if isinstance(current_task.status, Status) else current_task.status} → {status}"
                                )
                            if priority is not None:
                                console.print(
                                    f"  priority: {current_task.priority.value if isinstance(current_task.priority, Priority) else current_task.priority} → {priority}"
                                )
                            if labels is not None:
                                console.print(
                                    f"  labels: {current_task.labels} → {label_list}"
                                )
                            if owner is not None:
                                console.print(
                                    f"  owner: {current_task.owner_id} → {owner}"
                                )
                            if estimate is not None:
                                console.print(
                                    f"  estimate: {current_task.estimate} → {estimate}"
                                )
                            console.print(
                                f"  updated_at: {current_task.updated_at} → <now>"
                            )
                            console.print()
                        continue

                    # Create update model
                    task_update = TaskUpdate(
                        title=title,
                        description=description,
                        status=status_enum,
                        priority=priority_enum,
                        owner_id=owner,
                        labels=label_list,
                        estimate=estimate,
                    )

                    # Actually update the task
                    updated_task = await service.update_task(task_id, task_update)
                    updated_tasks.append(updated_task)

                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "NotFound",
                                "message": f"Task '{task_id}' not found",
                            }
                        )
                    elif "409" in error_msg:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "Conflict",
                                "message": "Version conflict - task was modified by someone else",
                            }
                        )
                    else:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "UpdateError",
                                "message": str(e),
                            }
                        )

            # Output results
            if json_output:
                if dry_run:
                    output_json(
                        {
                            "dry_run": True,
                            "task_ids": task_ids,
                            "changes": {
                                k: v
                                for k, v in {
                                    "title": title,
                                    "description": description,
                                    "status": status,
                                    "priority": priority,
                                    "labels": label_list,
                                    "owner_id": owner,
                                    "estimate": estimate,
                                }.items()
                                if v is not None
                            },
                        }
                    )
                else:
                    output_json(
                        {
                            "updated": [
                                t.model_dump(mode="json") for t in updated_tasks
                            ],
                            "errors": errors,
                        }
                    )
            else:
                if dry_run:
                    console.print()
                    console.print("Run without --dry-run to apply changes")
                else:
                    # Show success for updated tasks
                    if len(updated_tasks) == 1:
                        console.print(
                            f"[green]✓[/green] Updated {updated_tasks[0].identifier}"
                        )
                    elif len(updated_tasks) > 1:
                        console.print(
                            f"[green]✓[/green] Updated {len(updated_tasks)} tasks"
                        )

                    # Show errors
                    if errors:
                        console.print()
                        for error in errors:
                            console.print(
                                f"[red]✗[/red] {error['task_id']}: {error['message']}"
                            )

            # Exit with error if all failed
            if not dry_run and len(updated_tasks) == 0 and len(errors) > 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to update task: {e}")
            raise typer.Exit(1)

    asyncio.run(update())


def mark_done(
    identifiers: Annotated[
        Optional[list[str]],
        typer.Argument(
            help="Task identifier(s) (e.g., DEV-42 DEV-43). Uses active task if not specified."
        ),
    ] = None,
    note: Annotated[
        Optional[str],
        typer.Option("--note", "-n", help="Add a completion note to the task"),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Mark one or more tasks as done.

    Optionally add a completion note to the task's Events section.
    """
    ws_config, global_config = get_workspace_or_exit()
    service: TaskService = TaskService.from_config(global_config)  # type: ignore[assignment]

    # Get workspace identifier for task ID normalization
    workspace_identifier = ws_config.workspace_identifier

    # Determine task IDs
    task_ids = []
    clear_active = False

    if identifiers:
        # Normalize each identifier
        task_ids = [
            normalize_identifier(tid, workspace_identifier) for tid in identifiers
        ]
    else:
        # Use active task
        active_id = get_active_task_id()
        if not active_id:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task done DEV-42",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print("Specify a task: [cyan]anyt task done DEV-42[/cyan]")
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)
        task_ids = [normalize_identifier(active_id, workspace_identifier)]
        clear_active = True

    async def update() -> None:
        try:
            updated_tasks = []
            errors = []

            # Mark each task as done
            for task_id in task_ids:
                try:
                    # If note is provided, fetch task to append note to description
                    description_update = None
                    if note:
                        from datetime import datetime

                        task_data = await service.get_task(task_id)
                        current_description = task_data.description or ""
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                        note_text = f"\n### {timestamp} - Completed\n- {note}\n"

                        if "## Events" in current_description:
                            description_update = current_description + note_text
                        else:
                            description_update = (
                                current_description + f"\n## Events\n{note_text}"
                            )

                    # Update task status and description using typed model
                    if description_update:
                        task_update = TaskUpdate(
                            status=Status.DONE,
                            description=description_update,
                        )
                        task = await service.update_task(task_id, task_update)
                    else:
                        task_update = TaskUpdate(status=Status.DONE)
                        task = await service.update_task(task_id, task_update)

                    updated_tasks.append(task)
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "NotFound",
                                "message": f"Task '{task_id}' not found",
                            }
                        )
                    else:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "UpdateError",
                                "message": str(e),
                            }
                        )

            # Output results
            if json_output:
                output_json(
                    {
                        "updated": [t.model_dump(mode="json") for t in updated_tasks],
                        "errors": errors,
                    }
                )
            else:
                # Show success
                if len(updated_tasks) == 1:
                    console.print(
                        f"[green]✓[/green] Marked {updated_tasks[0].identifier} as done"
                    )
                elif len(updated_tasks) > 1:
                    console.print(
                        f"[green]✓[/green] Marked {len(updated_tasks)} tasks as done"
                    )

                # Clear active task if applicable
                if clear_active and len(updated_tasks) > 0:
                    ActiveTaskConfig.clear()
                    console.print("[dim]Cleared active task[/dim]")

                # Show errors
                if errors:
                    console.print()
                    for error in errors:
                        console.print(
                            f"[red]✗[/red] {error['task_id']}: {error['message']}"
                        )

            # Exit with error if all failed
            if len(updated_tasks) == 0 and len(errors) > 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to mark task(s) as done: {e}")
            raise typer.Exit(1)

    asyncio.run(update())


def remove_task(
    identifiers: Annotated[
        Optional[list[str]],
        typer.Argument(
            help="Task identifier(s) (e.g., DEV-42 DEV-43). Uses active task if not specified."
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompt"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Delete one or more tasks (soft delete)."""
    ws_config, global_config = get_workspace_or_exit()
    service: TaskService = TaskService.from_config(global_config)  # type: ignore[assignment]

    # Get workspace identifier for task ID normalization
    workspace_identifier = ws_config.workspace_identifier

    # Determine task IDs
    task_ids = []
    clear_active = False

    if identifiers:
        # Normalize each identifier
        task_ids = [
            normalize_identifier(tid, workspace_identifier) for tid in identifiers
        ]
    else:
        # Use active task
        active_id = get_active_task_id()
        if not active_id:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task rm DEV-42",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print("Specify a task: [cyan]anyt task rm DEV-42[/cyan]")
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)
        task_ids = [normalize_identifier(active_id, workspace_identifier)]
        clear_active = True

    async def delete() -> None:
        try:
            # Fetch tasks for confirmation if not forced
            tasks_to_delete = []
            if not force and not json_output:
                for task_id in task_ids:
                    try:
                        task = await service.get_task(task_id)
                        tasks_to_delete.append(task)
                    except Exception:
                        pass  # Will handle errors during actual deletion

                # Confirm deletion
                if len(tasks_to_delete) == 1:
                    task = tasks_to_delete[0]
                    if not Confirm.ask(
                        f"Delete task {task.identifier} ({task.title})?", default=False
                    ):
                        raise typer.Exit(0)
                elif len(tasks_to_delete) > 1:
                    console.print(f"About to delete {len(tasks_to_delete)} tasks:")
                    for task in tasks_to_delete:
                        title = truncate_text(task.title, 40)
                        console.print(f"  - {task.identifier}: {title}")
                    console.print()
                    if not Confirm.ask(
                        f"Delete these {len(tasks_to_delete)} tasks?", default=False
                    ):
                        raise typer.Exit(0)

            deleted_tasks = []
            errors = []

            # Delete each task
            for task_id in task_ids:
                try:
                    await service.delete_task(task_id)
                    deleted_tasks.append({"identifier": task_id})
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "NotFound",
                                "message": f"Task '{task_id}' not found",
                            }
                        )
                    else:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "DeleteError",
                                "message": str(e),
                            }
                        )

            # Output results
            if json_output:
                output_json({"deleted": deleted_tasks, "errors": errors})
            else:
                # Show success
                if len(deleted_tasks) == 1:
                    console.print(
                        f"[green]✓[/green] Deleted {deleted_tasks[0]['identifier']}"
                    )
                elif len(deleted_tasks) > 1:
                    console.print(
                        f"[green]✓[/green] Deleted {len(deleted_tasks)} tasks"
                    )

                # Clear active task if applicable
                if clear_active and len(deleted_tasks) > 0:
                    ActiveTaskConfig.clear()
                    console.print("[dim]Cleared active task[/dim]")

                # Show errors
                if errors:
                    console.print()
                    for error in errors:
                        console.print(
                            f"[red]✗[/red] {error['task_id']}: {error['message']}"
                        )

            # Exit with error if all failed
            if len(deleted_tasks) == 0 and len(errors) > 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "DeleteError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to delete task(s): {e}")
            raise typer.Exit(1)

    asyncio.run(delete())


def create_task_from_template(
    title: Annotated[str, typer.Argument(help="Task title")],
    template: Annotated[
        str,
        typer.Option(
            "--template", "-t", help="Template name to use (default: default)"
        ),
    ] = "default",
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Phase/milestone identifier (e.g., T3, Phase 1)"),
    ] = None,
    priority: Annotated[
        int,
        typer.Option("-p", "--priority", help="Priority (-2 to 2, default: 0)"),
    ] = 0,
    project: Annotated[
        Optional[int],
        typer.Option(
            "--project",
            help="Project ID (uses current/default project if not specified)",
        ),
    ] = None,
    no_edit: Annotated[
        bool,
        typer.Option("--no-edit", help="Skip opening editor, use template as-is"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Create a new task from a template.

    Opens the template in your editor ($EDITOR) for customization before creating the task.
    The template content will be stored in the task's description field.
    """
    # Import template loading function
    try:
        from cli.commands.template import load_template
    except ImportError:
        console.print("[red]Error:[/red] Template module not available")
        raise typer.Exit(1)

    ws_config, global_config = get_workspace_or_exit()
    task_service: TaskService = TaskService.from_config(global_config)  # type: ignore[assignment]
    projects_client: ProjectsAPIClient = ProjectsAPIClient.from_config(global_config)  # type: ignore[assignment]

    async def create() -> None:
        try:
            # Validate priority range
            if priority < -2 or priority > 2:
                if json_output:
                    output_json(
                        {
                            "error": "ValidationError",
                            "message": "Invalid priority value",
                            "details": "Priority must be between -2 and 2",
                        },
                        success=False,
                    )
                else:
                    console.print("[red]✗ Error:[/red] Invalid priority value")
                    console.print("  Priority must be between -2 and 2")
                raise typer.Exit(1)

            # Load template
            try:
                template_content = load_template(template)
            except Exception as e:
                if json_output:
                    output_json(
                        {
                            "error": "TemplateError",
                            "message": f"Failed to load template: {e}",
                        },
                        success=False,
                    )
                else:
                    console.print(f"[red]Error:[/red] Failed to load template: {e}")
                    console.print(
                        "Run [cyan]anyt template init[/cyan] to create templates"
                    )
                raise typer.Exit(1)

            # If no-edit is set, use template as-is
            description = template_content
            if not no_edit:
                # Open editor with template
                editor = os.environ.get("EDITOR", "nano")

                # Create temp file with template content
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False
                ) as tmp:
                    tmp.write(template_content)
                    tmp_path = tmp.name

                try:
                    # Open editor
                    import subprocess

                    result = subprocess.run([editor, tmp_path])

                    if result.returncode != 0:
                        if not json_output:
                            console.print(
                                "[yellow]Editor exited with error, using template as-is[/yellow]"
                            )

                    # Read edited content
                    with open(tmp_path, "r") as f:
                        description = f.read()

                finally:
                    # Clean up temp file
                    Path(tmp_path).unlink(missing_ok=True)

            # Get project ID
            project_id = project
            if not project_id:
                try:
                    current_project = await projects_client.get_current_project(
                        int(ws_config.workspace_id)
                    )
                    project_id = current_project.id

                    if not json_output:
                        console.print(
                            f"[dim]Using project: {current_project.name} (ID: {project_id})[/dim]"
                        )
                except Exception as e:
                    if json_output:
                        output_json(
                            {
                                "error": "ProjectError",
                                "message": f"Failed to get current project: {str(e)}",
                                "hint": "Specify --project ID explicitly",
                            },
                            success=False,
                        )
                    else:
                        console.print(
                            f"[red]Error:[/red] Failed to get current project: {e}"
                        )
                        console.print(
                            "Specify the project ID explicitly with --project <ID>"
                        )
                    raise typer.Exit(1)

            # Ensure project_id is set
            if project_id is None:
                raise ValueError("Project ID is required but not set")

            # Create task
            task_create = TaskCreate(
                title=title,
                description=description,
                phase=phase,
                status=Status.BACKLOG,
                priority=Priority(priority),
            )
            task = await task_service.create_task_with_validation(
                project_id=project_id, task=task_create
            )

            # Display success
            if json_output:
                output_json(task.model_dump(mode="json"))
            else:
                console.print(
                    f"[green]✓[/green] Created: [cyan]{task.identifier}[/cyan] ({task.title})"
                )

                if phase:
                    console.print(f"  Phase: {phase}")

                console.print(f"  Priority: {format_priority(priority)}")
                console.print(f"  Template: {template}")

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "CreateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to create task: {e}")
            raise typer.Exit(1)

    asyncio.run(create())


def add_note_to_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(help="Task identifier (e.g., DEV-42) or use active task"),
    ] = None,
    message: Annotated[
        str,
        typer.Option("--message", "-m", help="Note message to append"),
    ] = "",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Add a timestamped note/event to a task's description.

    The note will be appended to the Events section of the task description
    with a timestamp.
    """
    from datetime import datetime

    ws_config, global_config = get_workspace_or_exit()
    task_service: TaskService = TaskService.from_config(global_config)  # type: ignore[assignment]

    async def add_note() -> None:
        try:
            # Get task identifier
            task_id = identifier
            if not task_id:
                task_id = get_active_task_id()
                if not task_id:
                    if json_output:
                        output_json(
                            {
                                "error": "NoActiveTask",
                                "message": "No active task set",
                                "hint": "Specify task identifier or run 'anyt task pick'",
                            },
                            success=False,
                        )
                    else:
                        console.print("[red]Error:[/red] No active task set")
                        console.print(
                            "Specify task identifier or run [cyan]anyt task pick[/cyan]"
                        )
                    raise typer.Exit(1)

            # Normalize identifier
            task_id = normalize_identifier(task_id, ws_config.workspace_identifier)

            # Get current task to retrieve description
            task = await task_service.get_task(task_id)
            current_description = task.description or ""

            # Get message from parameter or prompt
            note_message = message
            if not note_message:
                if json_output:
                    console.print("[red]Error:[/red] Message is required")
                    raise typer.Exit(1)
                note_message = Prompt.ask("[cyan]Note message[/cyan]")
                if not note_message:
                    console.print("[yellow]Cancelled[/yellow]")
                    raise typer.Exit(0)

            # Create timestamped note
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            note = f"\n### {timestamp} - Note\n- {note_message}\n"

            # Append note to description
            # If description has an Events section, append there
            # Otherwise, create Events section and append
            if "## Events" in current_description:
                new_description = current_description + note
            else:
                new_description = current_description + f"\n## Events\n{note}"

            # Update task with new description
            updates = TaskUpdate(description=new_description)
            updated_task = await task_service.update_task(
                identifier=task_id,
                updates=updates,
            )

            # Display success
            if json_output:
                output_json(updated_task.model_dump(mode="json"))
            else:
                console.print(
                    f"[green]✓[/green] Note added to [cyan]{updated_task.identifier}[/cyan]"
                )
                console.print(f"  {note_message}")

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to add note: {e}")
            raise typer.Exit(1)

    asyncio.run(add_note())
