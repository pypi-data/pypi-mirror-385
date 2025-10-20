"""Initialize AnyTask workspace in current directory."""

import asyncio
from datetime import datetime
from pathlib import Path

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.prompt import Prompt

from cli.config import GlobalConfig, WorkspaceConfig
from cli.client import APIClient

console = Console()


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
    """Initialize AnyTask in the current directory.

    Creates .anyt/ directory and sets up workspace configuration.
    Links an existing workspace or creates a new one.
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

        # Create .anyt directory if it doesn't exist
        anyt_dir = target_dir / ".anyt"
        if not anyt_dir.exists():
            anyt_dir.mkdir(parents=True)
            console.print("[green]✓[/green] Created .anyt/ directory")
        else:
            console.print("[dim].anyt/ directory already exists[/dim]")

        # Check if workspace config already exists
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
                        "\nAlternatively, create one with: [cyan]anyt init --create 'Workspace Name' --identifier IDENT[/cyan]"
                    )
                    raise typer.Exit(1)

        asyncio.run(init_workspace())

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
