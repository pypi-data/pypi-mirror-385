"""Workspace commands for AnyTask CLI."""

import asyncio
from datetime import datetime
from pathlib import Path

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from cli.config import GlobalConfig, WorkspaceConfig
from cli.client import APIClient

app = typer.Typer(help="Manage workspaces")
console = Console()


@app.command()
def init(
    create: Annotated[
        str | None,
        typer.Option("--create", help="Create a new workspace with the given name"),
    ] = None,
    identifier: Annotated[
        str | None,
        typer.Option(
            "--identifier", "-i", help="Workspace identifier (required when creating)"
        ),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option("--dir", "-d", help="Directory to initialize (default: current)"),
    ] = None,
):
    """Initialize a workspace in the current directory.

    Links an existing workspace or creates a new one.
    Creates anyt.json workspace configuration file.
    """
    try:
        config = GlobalConfig.load()
        effective_config = config.get_effective_config()

        # Check authentication
        if not effective_config.get("auth_token") and not effective_config.get(
            "agent_key"
        ):
            console.print("[red]Error:[/red] Not authenticated")
            console.print("Run [cyan]anyt auth login[/cyan] first")
            raise typer.Exit(1)

        # Initialize API client
        client = APIClient.from_config(config)

        # Determine target directory
        target_dir = directory or Path.cwd()
        target_dir = target_dir.resolve()

        # Check if already initialized
        existing_config = WorkspaceConfig.load(target_dir)
        if existing_config:
            console.print(
                f"[yellow]Warning:[/yellow] Workspace config already exists: {existing_config.name}"
            )
            console.print(f"Workspace ID: {existing_config.workspace_id}")
            if existing_config.workspace_identifier:
                console.print(f"Identifier: {existing_config.workspace_identifier}")

            reset = Prompt.ask(
                "Do you want to reset it?", choices=["y", "N"], default="N"
            )

            if reset.lower() != "y":
                console.print("[green]✓[/green] Using existing workspace configuration")
                raise typer.Exit(0)

            # If reset (y), continue with initialization

        async def init_workspace():
            if create:
                # Create new workspace
                if not identifier:
                    console.print(
                        "[red]Error:[/red] --identifier is required when creating a workspace"
                    )
                    raise typer.Exit(1)

                console.print(
                    f"Creating workspace: [cyan]{create}[/cyan] ({identifier})..."
                )

                try:
                    workspace = await client.create_workspace(
                        name=create,
                        identifier=identifier.upper(),
                    )

                    console.print(
                        f"[green]✓[/green] Created workspace: {workspace['name']} ({workspace['identifier']})"
                    )

                    # Fetch current project for the workspace
                    console.print("Fetching current project...")
                    try:
                        current_project = await client.get_current_project(
                            workspace["id"]
                        )
                        current_project_id = current_project.get("id")
                    except Exception as e:
                        console.print(
                            f"[yellow]Warning:[/yellow] Could not fetch current project: {e}"
                        )
                        current_project_id = None

                    # Save workspace config
                    ws_config = WorkspaceConfig(
                        workspace_id=str(workspace["id"]),
                        name=workspace["name"],
                        api_url=effective_config["api_url"],
                        workspace_identifier=workspace.get("identifier"),
                        current_project_id=current_project_id,
                        last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    ws_config.save(target_dir)

                    console.print(
                        f"[green]✓[/green] Initialized workspace config in {target_dir}/.anyt/anyt.json"
                    )

                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to create workspace: {e}")
                    raise typer.Exit(1)

            else:
                # Get or create current workspace
                console.print("Setting up workspace...")

                try:
                    # Use the current workspace endpoint which auto-creates if needed
                    selected_ws = await client.get_current_workspace()
                    console.print(
                        f"[green]✓[/green] Using workspace: {selected_ws['name']} ({selected_ws['identifier']})"
                    )

                    # Fetch current project for the workspace
                    console.print("Fetching current project...")
                    try:
                        current_project = await client.get_current_project(
                            selected_ws["id"]
                        )
                        current_project_id = current_project.get("id")
                    except Exception as e:
                        console.print(
                            f"[yellow]Warning:[/yellow] Could not fetch current project: {e}"
                        )
                        current_project_id = None

                    # Save workspace config
                    ws_config = WorkspaceConfig(
                        workspace_id=str(selected_ws["id"]),
                        name=selected_ws["name"],
                        api_url=effective_config["api_url"],
                        workspace_identifier=selected_ws.get("identifier"),
                        current_project_id=current_project_id,
                        last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    ws_config.save(target_dir)

                    console.print(
                        f"[green]✓[/green] Initialized workspace config in {target_dir}/.anyt/anyt.json"
                    )

                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to setup workspace: {e}")
                    console.print(
                        "\nAlternatively, create one with: [cyan]anyt workspace init --create 'Workspace Name' --identifier IDENT[/cyan]"
                    )
                    raise typer.Exit(1)

        asyncio.run(init_workspace())

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)


@app.command()
def list():
    """List all accessible workspaces."""
    try:
        config = GlobalConfig.load()
        effective_config = config.get_effective_config()

        # Check authentication
        if not effective_config.get("auth_token") and not effective_config.get(
            "agent_key"
        ):
            console.print("[red]Error:[/red] Not authenticated")
            console.print("Run [cyan]anyt auth login[/cyan] first")
            raise typer.Exit(1)

        # Initialize API client
        client = APIClient.from_config(config)

        async def fetch_workspaces():
            try:
                console.print("Fetching workspaces...")
                workspaces = await client.list_workspaces()

                if not workspaces:
                    console.print("[yellow]No workspaces found[/yellow]")
                    return

                # Check for local workspace
                local_ws = WorkspaceConfig.load()

                # Display workspaces as a table
                table = Table(title="Accessible Workspaces")
                table.add_column("Name", style="green")
                table.add_column("Identifier", style="yellow")
                table.add_column("ID", style="dim")
                table.add_column("Status", style="cyan")

                for ws in workspaces:
                    ws_id = str(ws.get("id", ""))
                    is_current = local_ws and local_ws.workspace_id == ws_id

                    status = "● active" if is_current else ""

                    table.add_row(
                        ws.get("name", ""),
                        ws.get("identifier", ""),
                        ws_id,
                        status,
                    )

                console.print(table)
                console.print(
                    f"\nEnvironment: [cyan]{effective_config['environment']}[/cyan] ({effective_config['api_url']})"
                )

            except Exception as e:
                console.print(f"[red]Error:[/red] Failed to fetch workspaces: {e}")
                raise typer.Exit(1)

        asyncio.run(fetch_workspaces())

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)


@app.command()
def switch(
    workspace_id: Annotated[
        str | None,
        typer.Argument(help="Workspace ID or identifier to switch to"),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option(
            "--dir", "-d", help="Directory to switch workspace in (default: current)"
        ),
    ] = None,
):
    """Switch the active workspace for the current directory.

    This updates the anyt.json file to point to a different workspace.
    """
    try:
        config = GlobalConfig.load()
        effective_config = config.get_effective_config()

        # Check authentication
        if not effective_config.get("auth_token") and not effective_config.get(
            "agent_key"
        ):
            console.print("[red]Error:[/red] Not authenticated")
            console.print("Run [cyan]anyt auth login[/cyan] first")
            raise typer.Exit(1)

        # Determine target directory
        target_dir = directory or Path.cwd()
        target_dir = target_dir.resolve()

        # Check if initialized
        existing_config = WorkspaceConfig.load(target_dir)
        if not existing_config:
            console.print(
                "[red]Error:[/red] Directory not initialized with a workspace"
            )
            console.print("Run [cyan]anyt workspace init[/cyan] first")
            raise typer.Exit(1)

        # Initialize API client
        client = APIClient.from_config(config)

        async def switch_workspace():
            try:
                console.print("Fetching available workspaces...")
                workspaces = await client.list_workspaces()

                if not workspaces:
                    console.print("[yellow]No workspaces found[/yellow]")
                    raise typer.Exit(0)

                # If workspace_id provided, find it
                target_ws = None
                if workspace_id:
                    for ws in workspaces:
                        if (
                            str(ws.get("id")) == workspace_id
                            or ws.get("identifier") == workspace_id.upper()
                        ):
                            target_ws = ws
                            break

                    if not target_ws:
                        console.print(
                            f"[red]Error:[/red] Workspace '{workspace_id}' not found"
                        )
                        raise typer.Exit(1)
                else:
                    # Show selection prompt
                    table = Table(title="Available Workspaces")
                    table.add_column("#", style="cyan", no_wrap=True)
                    table.add_column("Name", style="green")
                    table.add_column("Identifier", style="yellow")
                    table.add_column("Current", style="dim")

                    for idx, ws in enumerate(workspaces, 1):
                        ws_id = str(ws.get("id", ""))
                        is_current = existing_config.workspace_id == ws_id

                        table.add_row(
                            str(idx),
                            ws.get("name", ""),
                            ws.get("identifier", ""),
                            "●" if is_current else "",
                        )

                    console.print(table)

                    choice = Prompt.ask(
                        "Select workspace",
                        choices=[str(i) for i in range(1, len(workspaces) + 1)],
                        default="1",
                    )

                    target_ws = workspaces[int(choice) - 1]

                # Fetch current project for the workspace
                console.print("Fetching current project...")
                try:
                    current_project = await client.get_current_project(target_ws["id"])
                    current_project_id = current_project.get("id")
                except Exception as e:
                    console.print(
                        f"[yellow]Warning:[/yellow] Could not fetch current project: {e}"
                    )
                    current_project_id = None

                # Update workspace config
                ws_config = WorkspaceConfig(
                    workspace_id=str(target_ws["id"]),
                    name=target_ws["name"],
                    api_url=effective_config["api_url"],
                    workspace_identifier=target_ws.get("identifier"),
                    current_project_id=current_project_id,
                    last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                ws_config.save(target_dir)

                console.print(
                    f"[green]✓[/green] Switched to workspace: {target_ws['name']} ({target_ws['identifier']})"
                )

            except Exception as e:
                if not isinstance(e, typer.Exit):
                    console.print(f"[red]Error:[/red] {e}")
                    raise typer.Exit(1)

        asyncio.run(switch_workspace())

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)


@app.command()
def use(
    workspace: Annotated[
        str,
        typer.Argument(help="Workspace ID or identifier to set as current"),
    ],
):
    """Set the current workspace for the active environment.

    This sets the default workspace that will be used for all task operations
    when no explicit workspace is specified via --workspace flag.
    """
    try:
        config = GlobalConfig.load()
        effective_config = config.get_effective_config()

        # Check authentication
        if not effective_config.get("auth_token") and not effective_config.get(
            "agent_key"
        ):
            console.print("[red]Error:[/red] Not authenticated")
            console.print("Run [cyan]anyt auth login[/cyan] first")
            raise typer.Exit(1)

        # Initialize API client
        client = APIClient.from_config(config)

        async def set_current_workspace():
            try:
                console.print("Fetching available workspaces...")
                workspaces = await client.list_workspaces()

                if not workspaces:
                    console.print("[yellow]No workspaces found[/yellow]")
                    raise typer.Exit(0)

                # Find the target workspace
                target_ws = None
                for ws in workspaces:
                    if (
                        str(ws.get("id")) == workspace
                        or ws.get("identifier") == workspace.upper()
                    ):
                        target_ws = ws
                        break

                if not target_ws:
                    console.print(
                        f"[red]Error:[/red] Workspace '{workspace}' not found"
                    )
                    console.print("\nAvailable workspaces:")
                    for ws in workspaces:
                        console.print(
                            f"  {ws.get('identifier', '')} - {ws.get('name', '')} (ID: {ws.get('id', '')})"
                        )
                    raise typer.Exit(1)

                # Update the current environment's default workspace
                env_name = config.current_environment
                env_config = config.get_current_env()
                env_config.default_workspace = target_ws.get("identifier")
                config.environments[env_name] = env_config
                config.save()

                console.print(
                    f"[green]✓[/green] Set current workspace to: {target_ws['name']} ({target_ws['identifier']})"
                )
                console.print(f"[dim]Environment: {env_name}[/dim]")

            except Exception as e:
                if not isinstance(e, typer.Exit):
                    console.print(f"[red]Error:[/red] {e}")
                    raise typer.Exit(1)

        asyncio.run(set_current_workspace())

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)


@app.command()
def current():
    """Show the current workspace for the active environment."""
    try:
        config = GlobalConfig.load()
        effective_config = config.get_effective_config()
        env_name = config.current_environment
        env_config = config.get_current_env()

        console.print(f"Environment: [cyan]{env_name}[/cyan]")

        if env_config.default_workspace:
            # Check authentication to fetch workspace details
            if effective_config.get("auth_token") or effective_config.get("agent_key"):
                client = APIClient.from_config(config)

                async def fetch_workspace_details():
                    try:
                        workspaces = await client.list_workspaces()
                        current_ws = None
                        for ws in workspaces:
                            if ws.get("identifier") == env_config.default_workspace:
                                current_ws = ws
                                break

                        if current_ws:
                            console.print(
                                f"Current workspace: [green]{current_ws['name']}[/green] ([yellow]{current_ws['identifier']}[/yellow])"
                            )
                            console.print(f"Workspace ID: {current_ws['id']}")
                        else:
                            console.print(
                                f"Current workspace: [yellow]{env_config.default_workspace}[/yellow]"
                            )
                            console.print(
                                "[dim](Workspace not found in accessible workspaces)[/dim]"
                            )
                    except Exception:
                        console.print(
                            f"Current workspace: [yellow]{env_config.default_workspace}[/yellow]"
                        )

                asyncio.run(fetch_workspace_details())
            else:
                console.print(
                    f"Current workspace: [yellow]{env_config.default_workspace}[/yellow]"
                )
        else:
            console.print("[dim]No current workspace set[/dim]")
            console.print(
                "\nSet a workspace with: [cyan]anyt workspace use WORKSPACE[/cyan]"
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
