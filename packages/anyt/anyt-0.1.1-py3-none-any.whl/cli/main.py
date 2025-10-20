"""Main entry point for the AnyTask CLI."""

import asyncio
import typer
from typing_extensions import Annotated
from rich.console import Console

from cli.commands import env as env_commands
from cli.commands import auth as auth_commands
from cli.commands import workspace as workspace_commands
from cli.commands import project as project_commands
from cli.commands import task as task_commands
from cli.commands import board as board_commands
from cli.commands import ai as ai_commands
from cli.commands import mcp as mcp_commands
from cli.commands import init as init_command
from cli.commands import template as template_commands
from cli.commands import label as label_commands
from cli.commands import view as view_commands
from cli.commands import preference as preference_commands
from cli.config import ActiveTaskConfig, GlobalConfig, WorkspaceConfig
from cli.client import APIClient

app = typer.Typer(
    name="anyt",
    help="AnyTask - AI-native task management from the command line",
)

# Register command groups
app.add_typer(env_commands.app, name="env")
app.add_typer(auth_commands.app, name="auth")
app.add_typer(workspace_commands.app, name="workspace")
app.add_typer(project_commands.app, name="project")
app.add_typer(task_commands.app, name="task")
app.add_typer(template_commands.app, name="template")
app.add_typer(label_commands.app, name="label")
app.add_typer(view_commands.app, name="view")
app.add_typer(preference_commands.app, name="preference")
app.add_typer(ai_commands.app, name="ai")
app.add_typer(mcp_commands.app, name="mcp")

# Register board visualization commands as top-level commands
app.command("board")(board_commands.show_board)
app.command("timeline")(board_commands.show_timeline)
app.command("summary")(board_commands.show_summary)
app.command("graph")(board_commands.show_graph)

# Register init command as top-level command
app.command("init")(init_command.init)

console = Console()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-v", help="Show version and exit"),
    ] = False,
):
    """AnyTask CLI - Manage tasks, projects, and workflows."""
    if version:
        from cli import __version__

        typer.echo(f"anyt version {__version__}")
        raise typer.Exit()

    # If no command and no version flag, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("health")
def health_check():
    """Check if the API server is reachable."""
    try:
        global_config = GlobalConfig.load()
        effective_config = global_config.get_effective_config()
        api_url = effective_config["api_url"]

        if not api_url:
            console.print("[red]Error:[/red] No environment configured")
            console.print("Run [cyan]anyt env add <name> <url>[/cyan] first")
            raise typer.Exit(1)

        env_name = effective_config["environment"]
        console.print(f"Environment: [cyan]{env_name}[/cyan]")
        console.print(f"API URL: {api_url}")

        # Check health endpoint
        client = APIClient.from_config(global_config)

        async def check():
            try:
                await client.health_check()
                return True
            except Exception as e:
                console.print(f"\n[red]Health check failed:[/red] {e}")
                return False

        if asyncio.run(check()):
            console.print("\n[green]✓ Server is healthy[/green]")
        else:
            raise typer.Exit(1)

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("active")
def show_active():
    """Show the currently active task."""
    # Check if workspace is initialized
    ws_config = WorkspaceConfig.load()
    if not ws_config:
        console.print("[red]Error:[/red] Not in a workspace directory")
        console.print("Run [cyan]anyt workspace init[/cyan] first")
        raise typer.Exit(1)

    # Load active task
    active_task = ActiveTaskConfig.load()
    if not active_task:
        console.print("[yellow]No active task[/yellow]")
        console.print("Pick one with: [cyan]anyt task pick[/cyan]")
        raise typer.Exit(0)

    # Load global config for API client
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

    client = APIClient.from_config(global_config)

    async def fetch_and_display():
        try:
            # Fetch full task details
            task = await client.get_task(active_task.identifier)

            # Display task details
            from cli.commands.task import (
                format_priority,
                format_relative_time,
            )

            task_id = task.get("identifier", str(task.get("id", "")))
            title = task.get("title", "")

            console.print()
            console.print(f"[cyan bold]{task_id}:[/cyan bold] {title}")
            console.print("━" * 60)

            # Status and priority
            status = task.get("status", "")
            priority_val = task.get("priority", 0)
            priority_str = format_priority(priority_val)
            console.print(
                f"Status: [yellow]{status}[/yellow]    Priority: {priority_str} ({priority_val})"
            )

            # Owner and labels
            owner_id = task.get("owner_id")
            if owner_id:
                console.print(f"Owner: {owner_id}")
            else:
                console.print("Owner: [dim]unassigned[/dim]")

            labels_list = task.get("labels", [])
            if labels_list:
                labels_str = ", ".join(labels_list)
                console.print(f"Labels: [blue]{labels_str}[/blue]")

            # Dependencies status (simplified)
            console.print()
            console.print("[dim]Dependencies: (use 'anyt dep list' for details)[/dim]")

            # Timestamps
            console.print()
            updated = format_relative_time(task.get("updated_at"))
            console.print(f"Last updated: {updated}")

            # Show when task was picked
            picked_time = format_relative_time(active_task.picked_at)
            console.print(f"Picked: {picked_time}")

            console.print()

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                console.print(
                    f"[red]Error:[/red] Active task '{active_task.identifier}' not found"
                )
                console.print(
                    "It may have been deleted. Clear with: [cyan]rm .anyt/active_task.json[/cyan]"
                )
            else:
                console.print(f"[red]Error:[/red] Failed to fetch task: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch_and_display())


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
