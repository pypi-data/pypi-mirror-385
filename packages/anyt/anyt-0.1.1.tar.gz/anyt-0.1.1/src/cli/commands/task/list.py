"""List command for tasks."""

import asyncio
from typing import Optional

import typer
from rich.table import Table
from typing_extensions import Annotated

from cli.client import APIClient

from .helpers import (
    console,
    format_priority,
    format_relative_time,
    get_workspace_or_exit,
    output_json,
    truncate_text,
)


def list_tasks(
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="Filter by status (comma-separated)"),
    ] = None,
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Filter by phase/milestone"),
    ] = None,
    mine: Annotated[
        bool,
        typer.Option("--mine", help="Show only tasks assigned to you"),
    ] = False,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Filter by labels (comma-separated)"),
    ] = None,
    sort: Annotated[
        str,
        typer.Option(
            "--sort", help="Sort field (priority, updated_at, created_at, status)"
        ),
    ] = "priority",
    order: Annotated[
        str,
        typer.Option("--order", help="Sort order (asc/desc)"),
    ] = "desc",
    limit: Annotated[
        int,
        typer.Option("--limit", help="Max number of tasks to show"),
    ] = 50,
    offset: Annotated[
        int,
        typer.Option("--offset", help="Pagination offset"),
    ] = 0,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
):
    """List tasks with filtering."""
    ws_config, global_config = get_workspace_or_exit()
    client = APIClient.from_config(global_config)

    async def fetch():
        try:
            # Parse filters
            status_list = None
            if status:
                status_list = [s.strip() for s in status.split(",")]

            label_list = None
            if labels:
                label_list = [label.strip() for label in labels.split(",")]

            owner_filter = None
            if mine:
                owner_filter = "me"

            # Fetch tasks
            result = await client.list_tasks(
                workspace_id=int(ws_config.workspace_id),
                status=status_list,
                phase=phase,
                owner=owner_filter,
                labels=label_list,
                limit=limit,
                offset=offset,
                sort_by=sort,
                order=order,
            )

            tasks = result.get("items", [])
            total = result.get("total", len(tasks))

            # JSON output mode
            if json_output:
                output_json(
                    {
                        "items": tasks,
                        "pagination": {
                            "total": total,
                            "limit": limit,
                            "offset": offset,
                            "has_more": offset + len(tasks) < total,
                        },
                    }
                )
                return

            # Rich console output mode
            if not tasks:
                console.print("[yellow]No tasks found[/yellow]")
                return

            # Display tasks in table
            table = Table(show_header=True, header_style="bold")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white")
            table.add_column("Status", style="yellow", no_wrap=True)
            table.add_column("Priority", style="magenta", no_wrap=True)
            table.add_column("Updated", style="dim", no_wrap=True)

            for task in tasks:
                identifier = task.get("identifier", str(task.get("id", "")))
                title = truncate_text(task.get("title", ""))
                task_status = task.get("status", "")
                priority_val = task.get("priority", 0)
                priority_str = format_priority(priority_val)
                updated = format_relative_time(task.get("updated_at"))

                table.add_row(identifier, title, task_status, priority_str, updated)

            console.print(table)

            # Show count
            if offset > 0 or len(tasks) < total:
                console.print(
                    f"\nShowing {offset + 1}-{offset + len(tasks)} of {total} tasks"
                )
            else:
                count_text = "1 task" if total == 1 else f"{total} tasks"
                console.print(f"\n{count_text}")

        except Exception as e:
            if json_output:
                output_json({"error": "ListError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to list tasks: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch())
