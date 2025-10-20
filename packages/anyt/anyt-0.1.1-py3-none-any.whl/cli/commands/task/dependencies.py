"""Dependency management commands for tasks."""

import asyncio
import json
from typing import Optional

import typer
from typing_extensions import Annotated

from cli.client import APIClient

from .helpers import (
    console,
    get_active_task_id,
    get_workspace_or_exit,
    truncate_text,
)


def add_dependency(
    on: Annotated[
        str,
        typer.Option(
            "--on", help="Task(s) this depends on (comma-separated identifiers)"
        ),
    ],
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-43) or ID. Uses active task if not specified."
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
):
    """Add dependency/dependencies to a task."""
    ws_config, global_config = get_workspace_or_exit()
    client = APIClient.from_config(global_config)

    # Use active task if no identifier provided
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "No task identifier provided and no active task set",
                            "message": "Specify a task or pick a task first",
                        }
                    )
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print(
                    "Specify a task: [cyan]anyt dep add DEV-43 --on DEV-42[/cyan]"
                )
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-43[/cyan]"
                )
            raise typer.Exit(1)

    async def add_deps():
        try:
            # Parse the dependencies - can be comma-separated
            depends_on_list = [dep.strip() for dep in on.split(",")]

            # Validate: task cannot depend on itself
            for dep_id in depends_on_list:
                if dep_id == identifier:
                    if json_output:
                        print(
                            json.dumps(
                                {
                                    "success": False,
                                    "error": "Task cannot depend on itself",
                                    "message": f"Task {identifier} cannot depend on itself",
                                }
                            )
                        )
                    else:
                        console.print(
                            "[red]✗ Error:[/red] Task cannot depend on itself"
                        )
                    raise typer.Exit(1)

            # Add each dependency
            added_count = 0
            errors = []

            for dep_id in depends_on_list:
                try:
                    await client.add_task_dependency(identifier, dep_id)
                    added_count += 1
                except Exception as e:
                    error_msg = str(e)
                    if "circular" in error_msg.lower():
                        errors.append(f"{dep_id}: Would create circular dependency")
                    elif "404" in error_msg:
                        errors.append(f"{dep_id}: Task not found")
                    elif "409" in error_msg:
                        errors.append(f"{dep_id}: Dependency already exists")
                    else:
                        errors.append(f"{dep_id}: {error_msg}")

            # Display results
            if json_output:
                result = {
                    "success": added_count > 0,
                    "data": {
                        "identifier": identifier,
                        "dependencies_added": depends_on_list[:added_count],
                        "added_count": added_count,
                        "total_count": len(depends_on_list),
                    },
                    "message": None,
                }
                if errors:
                    result["warnings"] = errors
                print(json.dumps(result))
            else:
                if added_count == 1 and len(depends_on_list) == 1:
                    console.print(
                        f"[green]✓[/green] {identifier} now depends on {depends_on_list[0]}"
                    )
                elif added_count > 0:
                    dep_str = ", ".join(depends_on_list[:added_count])
                    console.print(
                        f"[green]✓[/green] {identifier} now depends on {dep_str}"
                    )

                # Display errors
                if errors:
                    console.print()
                    console.print("[yellow]Warnings:[/yellow]")
                    for error in errors:
                        console.print(f"  [red]✗[/red] {error}")

            # Exit with error if all failed
            if added_count == 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:
            error_msg = str(e)
            if json_output:
                error_detail = (
                    "Task not found"
                    if "404" in error_msg
                    else (
                        "Would create circular dependency"
                        if "circular" in error_msg.lower()
                        else f"Failed to add dependency: {error_msg}"
                    )
                )
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": error_detail,
                            "message": error_msg,
                        }
                    )
                )
            else:
                if "404" in error_msg:
                    console.print(f"[red]✗ Error:[/red] Task '{identifier}' not found")
                elif "circular" in error_msg.lower():
                    console.print(
                        "[red]✗ Error:[/red] Adding this dependency would create a circular dependency"
                    )
                else:
                    console.print(f"[red]✗ Error:[/red] Failed to add dependency: {e}")
            raise typer.Exit(1)

    asyncio.run(add_deps())


def remove_dependency(
    on: Annotated[
        str,
        typer.Option(
            "--on", help="Task(s) to remove dependency on (comma-separated identifiers)"
        ),
    ],
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-43) or ID. Uses active task if not specified."
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
):
    """Remove dependency/dependencies from a task."""
    ws_config, global_config = get_workspace_or_exit()
    client = APIClient.from_config(global_config)

    # Use active task if no identifier provided
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "No task identifier provided and no active task set",
                            "message": "Specify a task or pick a task first",
                        }
                    )
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print(
                    "Specify a task: [cyan]anyt dep rm DEV-43 --on DEV-42[/cyan]"
                )
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-43[/cyan]"
                )
            raise typer.Exit(1)

    async def remove_deps():
        try:
            # Parse the dependencies - can be comma-separated
            depends_on_list = [dep.strip() for dep in on.split(",")]

            # Remove each dependency
            removed_count = 0
            errors = []

            for dep_id in depends_on_list:
                try:
                    await client.remove_task_dependency(identifier, dep_id)
                    removed_count += 1
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg:
                        errors.append(f"{dep_id}: Dependency not found")
                    else:
                        errors.append(f"{dep_id}: {error_msg}")

            # Display results
            if json_output:
                result = {
                    "success": removed_count > 0,
                    "data": {
                        "identifier": identifier,
                        "dependencies_removed": depends_on_list[:removed_count],
                        "removed_count": removed_count,
                        "total_count": len(depends_on_list),
                    },
                    "message": None,
                }
                if errors:
                    result["warnings"] = errors
                print(json.dumps(result))
            else:
                if removed_count == 1 and len(depends_on_list) == 1:
                    console.print(
                        f"[green]✓[/green] Removed dependency: {identifier} → {depends_on_list[0]}"
                    )
                elif removed_count > 0:
                    console.print(
                        f"[green]✓[/green] Removed {removed_count} dependencies from {identifier}"
                    )

                # Display errors
                if errors:
                    console.print()
                    console.print("[yellow]Warnings:[/yellow]")
                    for error in errors:
                        console.print(f"  [red]✗[/red] {error}")

            # Exit with error if all failed
            if removed_count == 0:
                raise typer.Exit(1)

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
                            else f"Failed to remove dependency: {error_msg}",
                            "message": error_msg,
                        }
                    )
                )
            else:
                if "404" in error_msg:
                    console.print(f"[red]✗ Error:[/red] Task '{identifier}' not found")
                else:
                    console.print(
                        f"[red]✗ Error:[/red] Failed to remove dependency: {e}"
                    )
            raise typer.Exit(1)

    asyncio.run(remove_deps())


def list_dependencies(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-43) or ID. Uses active task if not specified."
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
):
    """List task dependencies and dependents."""
    ws_config, global_config = get_workspace_or_exit()
    client = APIClient.from_config(global_config)

    # Use active task if no identifier provided
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "No task identifier provided and no active task set",
                            "message": "Specify a task or pick a task first",
                        }
                    )
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print("Specify a task: [cyan]anyt dep list DEV-43[/cyan]")
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-43[/cyan]"
                )
            raise typer.Exit(1)

    async def fetch_deps():
        try:
            # Fetch task details
            task = await client.get_task(identifier)
            task_id = task.get("identifier", str(task.get("id", "")))
            title = task.get("title", "")

            # Fetch dependencies (tasks this depends on)
            dependencies = await client.get_task_dependencies(identifier)

            # Fetch dependents (tasks that depend on this)
            dependents = await client.get_task_dependents(identifier)

            if json_output:
                # JSON output format
                print(
                    json.dumps(
                        {
                            "success": True,
                            "data": {
                                "task": {
                                    "identifier": task_id,
                                    "title": title,
                                },
                                "dependencies": dependencies,
                                "dependents": dependents,
                            },
                            "message": None,
                        }
                    )
                )
            else:
                # Display header
                console.print()
                console.print(f"[cyan bold]{task_id}:[/cyan bold] {title}")
                console.print("━" * 60)
                console.print()

                # Display dependencies
                console.print("[bold]Dependencies[/bold] (tasks this depends on):")
                if dependencies:
                    for dep in dependencies:
                        dep_id = dep.get("identifier", str(dep.get("id", "")))
                        dep_title = truncate_text(dep.get("title", ""), 50)
                        dep_status = dep.get("status", "")

                        # Status symbol
                        if dep_status == "done":
                            status_symbol = "[green]✓[/green]"
                        elif dep_status == "inprogress":
                            status_symbol = "[yellow]⬤[/yellow]"
                        elif dep_status == "backlog":
                            status_symbol = "[dim]⬜[/dim]"
                        else:
                            status_symbol = "[dim]○[/dim]"

                        console.print(
                            f"  → [cyan]{dep_id}[/cyan]  {dep_title}  {status_symbol} {dep_status}"
                        )
                else:
                    console.print("  [dim]No dependencies[/dim]")

                console.print()

                # Display dependents
                console.print("[bold]Blocks[/bold] (tasks that depend on this):")
                if dependents:
                    for dependent in dependents:
                        dept_id = dependent.get(
                            "identifier", str(dependent.get("id", ""))
                        )
                        dept_title = truncate_text(dependent.get("title", ""), 50)
                        dept_status = dependent.get("status", "")

                        # Status symbol
                        if dept_status == "done":
                            status_symbol = "[green]✓[/green]"
                        elif dept_status == "inprogress":
                            status_symbol = "[yellow]⬤[/yellow]"
                        elif dept_status == "backlog":
                            status_symbol = "[dim]⬜[/dim]"
                        else:
                            status_symbol = "[dim]○[/dim]"

                        console.print(
                            f"  ← [cyan]{dept_id}[/cyan]  {dept_title}  {status_symbol} {dept_status}"
                        )
                else:
                    console.print("  [dim]No dependents[/dim]")

                console.print()

        except Exception as e:
            error_msg = str(e)
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "Task not found"
                            if "404" in error_msg
                            else f"Failed to fetch dependencies: {error_msg}",
                            "message": error_msg,
                        }
                    )
                )
            else:
                if "404" in error_msg:
                    console.print(f"[red]✗ Error:[/red] Task '{identifier}' not found")
                else:
                    console.print(
                        f"[red]✗ Error:[/red] Failed to fetch dependencies: {e}"
                    )
            raise typer.Exit(1)

    asyncio.run(fetch_deps())
