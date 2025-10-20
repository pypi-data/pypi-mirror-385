"""Label management commands for AnyTask CLI."""

import asyncio
import json
from typing import Optional

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

from cli.config import GlobalConfig, WorkspaceConfig
from cli.client import APIClient

app = typer.Typer(help="Manage workspace labels")
console = Console()


@app.command("create")
def create_label(
    name: Annotated[str, typer.Argument(help="Label name")],
    color: Annotated[
        Optional[str], typer.Option("--color", help="Hex color code (e.g., #FF0000)")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option("--description", help="Label description")
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
):
    """Create a new label in the workspace."""
    try:
        # Load configs
        global_config = GlobalConfig.load()
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Initialize API client
        client = APIClient.from_config(global_config)

        # Create label
        result = asyncio.run(
            client.create_label(
                workspace_id=int(workspace_config.workspace_id),
                name=name,
                color=color,
                description=description,
            )
        )

        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            console.print(f"[green]✓[/green] Created label: {result['name']}")
            if result.get("color"):
                console.print(f"  Color: {result['color']}")
            if result.get("description"):
                console.print(f"  Description: {result['description']}")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_labels(
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
):
    """List all labels in the workspace."""
    try:
        # Load configs
        global_config = GlobalConfig.load()
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Initialize API client
        client = APIClient.from_config(global_config)

        # List labels
        labels = asyncio.run(
            client.list_labels(workspace_id=int(workspace_config.workspace_id))
        )

        if json_output:
            console.print(json.dumps(labels, indent=2))
        else:
            if not labels:
                console.print("No labels found")
                return

            # Sort alphabetically
            labels.sort(key=lambda x: x.get("name", "").lower())

            # Create table
            table = Table(title=f"Labels in {workspace_config.name}")
            table.add_column("Name", style="cyan")
            table.add_column("Color", style="white")
            table.add_column("Description", style="dim")

            for label in labels:
                name = label.get("name", "")
                color = label.get("color", "")
                desc = label.get("description", "")

                # Display color indicator
                color_display = ""
                if color:
                    # Try to display colored circle
                    try:
                        color_display = f"[{color}]●[/] {color}"
                    except Exception:
                        color_display = color

                table.add_row(name, color_display, desc)

            console.print(table)
            console.print(f"\nTotal: {len(labels)} label(s)")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("show")
def show_label(
    name: Annotated[str, typer.Argument(help="Label name")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
):
    """Show details for a specific label."""
    try:
        # Load configs
        global_config = GlobalConfig.load()
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Initialize API client
        client = APIClient.from_config(global_config)

        # List labels to find the one by name
        labels = asyncio.run(
            client.list_labels(workspace_id=int(workspace_config.workspace_id))
        )

        # Find label by name
        label = next((lbl for lbl in labels if lbl.get("name") == name), None)

        if not label:
            if json_output:
                console.print(json.dumps({"error": f"Label '{name}' not found"}))
            else:
                console.print(f"[red]Error:[/red] Label '{name}' not found")
            raise typer.Exit(1)

        if json_output:
            console.print(json.dumps(label, indent=2))
        else:
            console.print(f"[cyan]{label['name']}[/cyan]")
            if label.get("color"):
                # Try to display colored circle
                try:
                    console.print(f"  Color: [{label['color']}]●[/] {label['color']}")
                except Exception:
                    console.print(f"  Color: {label['color']}")
            if label.get("description"):
                console.print(f"  Description: {label['description']}")
            if label.get("id"):
                console.print(f"  ID: {label['id']}")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("edit")
def edit_label(
    name: Annotated[str, typer.Argument(help="Label name")],
    new_name: Annotated[
        Optional[str], typer.Option("--name", help="New label name")
    ] = None,
    color: Annotated[
        Optional[str], typer.Option("--color", help="New color (hex code)")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option("--description", help="New description")
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
):
    """Edit label properties."""
    try:
        # Validate at least one field to update
        if not any([new_name, color, description is not None]):
            console.print(
                "[red]Error:[/red] At least one of --name, --color, or --description is required"
            )
            raise typer.Exit(1)

        # Load configs
        global_config = GlobalConfig.load()
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Initialize API client
        client = APIClient.from_config(global_config)

        # List labels to find the one by name
        labels = asyncio.run(
            client.list_labels(workspace_id=int(workspace_config.workspace_id))
        )

        # Find label by name
        label = next((lbl for lbl in labels if lbl.get("name") == name), None)

        if not label:
            if json_output:
                console.print(json.dumps({"error": f"Label '{name}' not found"}))
            else:
                console.print(f"[red]Error:[/red] Label '{name}' not found")
            raise typer.Exit(1)

        # Show before/after comparison if not JSON mode
        if not json_output:
            console.print(f"[cyan]Updating label '{name}'[/cyan]")
            console.print("\nBefore:")
            console.print(f"  Name: {label.get('name', '')}")
            console.print(f"  Color: {label.get('color', '')}")
            console.print(f"  Description: {label.get('description', '')}")
            console.print("\nAfter:")
            console.print(f"  Name: {new_name or label.get('name', '')}")
            console.print(f"  Color: {color or label.get('color', '')}")
            console.print(
                f"  Description: {description if description is not None else label.get('description', '')}"
            )

            if not Confirm.ask("\nProceed with update?"):
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        # Update label
        result = asyncio.run(
            client.update_label(
                workspace_id=int(workspace_config.workspace_id),
                label_id=label["id"],
                name=new_name,
                color=color,
                description=description,
            )
        )

        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            console.print(f"\n[green]✓[/green] Updated label: {result['name']}")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("rm")
def delete_label(
    names: Annotated[list[str], typer.Argument(help="Label name(s) to delete")],
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
):
    """Delete one or more labels."""
    try:
        # Load configs
        global_config = GlobalConfig.load()
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Initialize API client
        client = APIClient.from_config(global_config)

        # List labels to find them by name
        labels = asyncio.run(
            client.list_labels(workspace_id=int(workspace_config.workspace_id))
        )

        # Find labels to delete
        labels_to_delete = []
        not_found = []

        for name in names:
            label = next((lbl for lbl in labels if lbl.get("name") == name), None)
            if label:
                labels_to_delete.append(label)
            else:
                not_found.append(name)

        if not_found:
            if json_output:
                console.print(
                    json.dumps({"error": f"Labels not found: {', '.join(not_found)}"})
                )
            else:
                console.print(
                    f"[yellow]Warning:[/yellow] Labels not found: {', '.join(not_found)}"
                )

        if not labels_to_delete:
            if not json_output:
                console.print("[red]Error:[/red] No labels to delete")
            raise typer.Exit(1)

        # Confirm deletion unless --force
        if not force and not json_output:
            console.print(
                f"[yellow]About to delete {len(labels_to_delete)} label(s):[/yellow]"
            )
            for label in labels_to_delete:
                console.print(f"  - {label.get('name', '')}")

            if not Confirm.ask("\nAre you sure?"):
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        # Delete labels
        deleted = []
        errors = []

        for label in labels_to_delete:
            try:
                asyncio.run(
                    client.delete_label(
                        workspace_id=int(workspace_config.workspace_id),
                        label_id=label["id"],
                    )
                )
                deleted.append(label.get("name", ""))
            except Exception as e:
                errors.append({"name": label.get("name", ""), "error": str(e)})

        if json_output:
            console.print(json.dumps({"deleted": deleted, "errors": errors}, indent=2))
        else:
            if deleted:
                console.print(
                    f"[green]✓[/green] Deleted {len(deleted)} label(s): {', '.join(deleted)}"
                )
            if errors:
                console.print("[red]Errors:[/red]")
                for err in errors:
                    console.print(f"  - {err['name']}: {err['error']}")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
