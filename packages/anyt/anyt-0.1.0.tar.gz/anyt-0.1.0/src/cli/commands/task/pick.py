"""Pick command for setting the active task."""

import asyncio
import json
from collections import defaultdict
from datetime import UTC, datetime
from typing import Optional

import typer
from rich.prompt import Prompt
from rich.table import Table
from typing_extensions import Annotated

from cli.client import APIClient
from cli.config import ActiveTaskConfig

from .helpers import console, get_workspace_or_exit


def display_interactive_picker(
    tasks: list[dict], group_by_status: bool = True
) -> str | None:
    """Display interactive task picker and return selected task identifier.

    Args:
        tasks: List of task dictionaries
        group_by_status: If True, group tasks by status

    Returns:
        Selected task identifier or None if cancelled
    """
    if not tasks:
        console.print("[yellow]No tasks available to pick[/yellow]")
        return None

    # Group tasks by status if requested
    if group_by_status:
        groups = defaultdict(list)
        for task in tasks:
            status = task.get("status", "unknown")
            groups[status].append(task)

        # Display tasks grouped by status
        task_index = 1
        task_map = {}

        for status in ["backlog", "todo", "inprogress", "blocked", "done"]:
            if status not in groups:
                continue

            status_tasks = groups[status]
            console.print(
                f"\n[bold cyan]{status.upper()}[/bold cyan] ({len(status_tasks)} tasks)"
            )

            table = Table(show_header=True, header_style="bold magenta", box=None)
            table.add_column("#", style="cyan", width=4)
            table.add_column("ID", style="yellow", width=12)
            table.add_column("Title", style="white")
            table.add_column("Priority", style="blue", width=8)

            for task in status_tasks:
                task_id = task.get("identifier", str(task.get("id", "")))
                title = task.get("title", "")
                priority = task.get("priority", 0)

                # Format priority display
                priority_display = {
                    2: "↑↑ (2)",
                    1: "↑ (1)",
                    0: "- (0)",
                    -1: "↓ (-1)",
                    -2: "↓↓ (-2)",
                }.get(priority, str(priority))

                # Truncate title if too long
                if len(title) > 60:
                    title = title[:57] + "..."

                table.add_row(str(task_index), task_id, title, priority_display)
                task_map[task_index] = task_id
                task_index += 1

            console.print(table)

    else:
        # Simple list without grouping
        table = Table(
            title="Available Tasks", show_header=True, header_style="bold magenta"
        )
        table.add_column("#", style="cyan", width=4)
        table.add_column("ID", style="yellow", width=12)
        table.add_column("Title", style="white")
        table.add_column("Status", style="blue", width=12)
        table.add_column("Priority", style="green", width=8)

        task_map = {}
        for idx, task in enumerate(tasks, 1):
            task_id = task.get("identifier", str(task.get("id", "")))
            title = task.get("title", "")
            status = task.get("status", "unknown")
            priority = task.get("priority", 0)

            # Format priority display
            priority_display = {
                2: "↑↑ (2)",
                1: "↑ (1)",
                0: "- (0)",
                -1: "↓ (-1)",
                -2: "↓↓ (-2)",
            }.get(priority, str(priority))

            # Truncate title if too long
            if len(title) > 50:
                title = title[:47] + "..."

            table.add_row(str(idx), task_id, title, status, priority_display)
            task_map[idx] = task_id

        console.print(table)

    # Prompt user for selection
    console.print()
    choice = Prompt.ask("[bold]Select task number[/bold] (or 'q' to quit)", default="q")

    if choice.lower() == "q":
        console.print("[yellow]Selection cancelled[/yellow]")
        return None

    try:
        idx = int(choice)
        if idx in task_map:
            return task_map[idx]
        else:
            console.print(f"[red]Invalid selection: {idx}[/red]")
            console.print(f"Please choose a number between 1 and {len(task_map)}")
            return None
    except ValueError:
        console.print(f"[red]Invalid input: '{choice}'[/red]")
        console.print("Please enter a number or 'q' to quit")
        return None


def pick_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42) or ID. Leave empty for interactive picker."
        ),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="Filter by status (comma-separated)"),
    ] = None,
    project: Annotated[
        Optional[int],
        typer.Option("--project", help="Filter by project ID"),
    ] = None,
    mine: Annotated[
        bool,
        typer.Option("--mine", help="Show only tasks assigned to you"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
):
    """Pick a task to work on (sets as active task).

    If identifier is provided, picks that specific task.
    Otherwise, shows an interactive picker to select a task.
    """
    ws_config, global_config = get_workspace_or_exit()
    client = APIClient.from_config(global_config)

    async def pick():
        try:
            # If identifier is provided, pick that task directly
            if identifier:
                # Fetch task details
                task = await client.get_task(identifier)
                task_id = task.get("identifier", str(task.get("id", "")))
                title = task.get("title", "")
                workspace_id = task.get("workspace_id")
                project_id = task.get("project_id")

                # Save as active task
                active_task = ActiveTaskConfig(
                    identifier=task_id,
                    title=title,
                    picked_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    workspace_id=workspace_id,
                    project_id=project_id,
                )
                active_task.save()

                if json_output:
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "data": {
                                    "identifier": task_id,
                                    "title": title,
                                    "workspace_id": workspace_id,
                                    "project_id": project_id,
                                    "picked_at": active_task.picked_at,
                                },
                                "message": "Task picked successfully",
                            }
                        )
                    )
                else:
                    console.print(
                        f"[green]✓[/green] Picked [cyan]{task_id}[/cyan] ({title})"
                    )
                    console.print("  Saved to .anyt/active_task.json")

            else:
                # Interactive picker - fetch tasks and display
                # Build filters
                filters = {
                    "workspace_id": int(ws_config.workspace_id),
                }
                if status:
                    filters["status"] = [s.strip() for s in status.split(",")]
                if project:
                    filters["project_id"] = project
                if mine:
                    filters["owner"] = "me"

                # Fetch tasks
                result = await client.list_tasks(**filters)
                tasks = result.get("items", [])

                if not tasks:
                    if json_output:
                        print(
                            json.dumps(
                                {
                                    "success": False,
                                    "error": "No tasks available",
                                    "message": "No tasks found matching the filters",
                                }
                            )
                        )
                    else:
                        console.print("[yellow]No tasks available to pick[/yellow]")
                        console.print("Try adjusting your filters or create a new task")
                    raise typer.Exit(1)

                # Display interactive picker
                selected_identifier = display_interactive_picker(
                    tasks, group_by_status=True
                )

                if not selected_identifier:
                    # User cancelled
                    if json_output:
                        print(
                            json.dumps(
                                {
                                    "success": False,
                                    "error": "Selection cancelled",
                                    "message": "No task was picked",
                                }
                            )
                        )
                    raise typer.Exit(0)

                # Fetch the selected task details
                task = await client.get_task(selected_identifier)
                task_id = task.get("identifier", str(task.get("id", "")))
                title = task.get("title", "")
                workspace_id = task.get("workspace_id")
                project_id = task.get("project_id")

                # Save as active task
                active_task = ActiveTaskConfig(
                    identifier=task_id,
                    title=title,
                    picked_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    workspace_id=workspace_id,
                    project_id=project_id,
                )
                active_task.save()

                if json_output:
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "data": {
                                    "identifier": task_id,
                                    "title": title,
                                    "workspace_id": workspace_id,
                                    "project_id": project_id,
                                    "picked_at": active_task.picked_at,
                                },
                                "message": "Task picked successfully",
                            }
                        )
                    )
                else:
                    console.print(
                        f"[green]✓[/green] Picked [cyan]{task_id}[/cyan] ({title})"
                    )
                    console.print("  Saved to .anyt/active_task.json")

        except typer.Exit:
            raise
        except Exception as e:
            error_msg = str(e)
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "Task not found"
                            if "404" in error_msg
                            else f"Failed to pick task: {error_msg}",
                            "message": error_msg,
                        }
                    )
                )
            else:
                if "404" in error_msg:
                    console.print(f"[red]Error:[/red] Task '{identifier}' not found")
                else:
                    console.print(f"[red]Error:[/red] Failed to pick task: {e}")
            raise typer.Exit(1)

    asyncio.run(pick())
