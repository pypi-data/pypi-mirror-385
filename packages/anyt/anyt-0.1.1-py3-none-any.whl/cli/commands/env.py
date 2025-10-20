"""Environment management commands."""

import os

import httpx
import typer
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from cli.config import GlobalConfig

app = typer.Typer(name="env", help="Manage CLI environments")
console = Console()


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """Environment management callback - defaults to list."""
    if ctx.invoked_subcommand is None:
        # No subcommand provided, show list
        list_environments()


@app.command("list")
def list_environments():
    """List all configured environments."""
    config = GlobalConfig.load()

    if not config.environments:
        console.print("[yellow]No environments configured.[/yellow]")
        console.print(
            "\nAdd an environment with: [cyan]anyt env add <name> <api-url>[/cyan]"
        )
        return

    table = Table(title="Configured Environments")
    table.add_column("", width=2)
    table.add_column("Name", style="cyan")
    table.add_column("API URL", style="blue")
    table.add_column("Status", style="green")

    for name, env_config in config.environments.items():
        is_current = name == config.current_environment
        marker = "*" if is_current else ""
        style = "bold" if is_current else ""

        # Try to check connectivity
        status = _check_connection(env_config.api_url)

        table.add_row(
            marker,
            f"[{style}]{name}[/]" if style else name,
            f"[{style}]{env_config.api_url}[/]" if style else env_config.api_url,
            status,
        )

    console.print(table)


@app.command("add")
def add_environment(
    name: Annotated[str, typer.Argument(help="Environment name (e.g., 'dev', 'prod')")],
    api_url: Annotated[str, typer.Argument(help="API base URL")],
    make_active: Annotated[
        bool, typer.Option("--active", help="Make this the active environment")
    ] = False,
):
    """Add a new environment."""
    config = GlobalConfig.load()

    # Validate URL format
    if not api_url.startswith(("http://", "https://")):
        console.print("[red]Error:[/red] API URL must start with http:// or https://")
        raise typer.Exit(1)

    # Check if environment already exists
    if name in config.environments:
        console.print(f"[yellow]Environment '{name}' already exists.[/yellow]")
        overwrite = typer.confirm("Do you want to overwrite it?")
        if not overwrite:
            raise typer.Exit(0)

    try:
        config.add_environment(name, api_url, make_active=make_active)
        console.print(f"[green]✓[/green] Added environment: [cyan]{name}[/cyan]")
        console.print(f"API URL: [blue]{api_url}[/blue]")

        if make_active:
            console.print(
                f"[green]✓[/green] Switched to environment: [cyan]{name}[/cyan]"
            )

        # Try to check connectivity
        status = _check_connection(api_url)
        console.print(f"Connection status: {status}")

    except Exception as e:
        console.print(f"[red]Error adding environment:[/red] {e}")
        raise typer.Exit(1)


@app.command("remove")
def remove_environment(
    name: Annotated[str, typer.Argument(help="Environment name to remove")],
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation prompt")
    ] = False,
):
    """Remove an environment."""
    config = GlobalConfig.load()

    if name not in config.environments:
        console.print(f"[red]Error:[/red] Environment '{name}' not found")
        console.print("\nAvailable environments:")
        for env_name in config.environments.keys():
            console.print(f"  - [cyan]{env_name}[/cyan]")
        raise typer.Exit(1)

    # Check if this is the current environment
    if name == config.current_environment:
        console.print(f"[red]Error:[/red] Cannot remove current environment '{name}'")
        console.print("Switch to a different environment first:")
        console.print("  [cyan]anyt env use <environment>[/cyan]")
        raise typer.Exit(1)

    # Confirm removal
    if not force:
        env_config = config.environments[name]
        console.print(f"Remove environment: [cyan]{name}[/cyan]")
        console.print(f"API URL: {env_config.api_url}")
        if env_config.auth_token:
            console.print("Auth: [yellow]Configured (will be lost)[/yellow]")

        if not typer.confirm("\nAre you sure?"):
            console.print("Cancelled")
            raise typer.Exit(0)

    try:
        config.remove_environment(name)
        console.print(f"[green]✓[/green] Removed environment: [cyan]{name}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error removing environment:[/red] {e}")
        raise typer.Exit(1)


@app.command("switch")
def switch_environment(
    name: Annotated[str, typer.Argument(help="Environment name to switch to")],
):
    """Switch to a different environment."""
    config = GlobalConfig.load()

    if name not in config.environments:
        console.print(f"[red]Error:[/red] Environment '{name}' not found")
        console.print("\nAvailable environments:")
        for env_name in config.environments.keys():
            console.print(f"  - [cyan]{env_name}[/cyan]")
        raise typer.Exit(1)

    try:
        config.switch_environment(name)
        env_config = config.get_current_env()
        console.print(f"[green]✓[/green] Switched to environment: [cyan]{name}[/cyan]")
        console.print(f"API URL: [blue]{env_config.api_url}[/blue]")

        # Check connectivity
        status = _check_connection(env_config.api_url)
        console.print(f"Status: {status}")

    except Exception as e:
        console.print(f"[red]Error switching environment:[/red] {e}")
        raise typer.Exit(1)


# Alias for switch command
@app.command("use")
def use_environment(
    name: Annotated[str, typer.Argument(help="Environment name to switch to")],
):
    """Switch to a different environment (alias for 'switch')."""
    switch_environment(name)


@app.command("show")
def show_current_environment():
    """Show the current environment configuration."""
    config = GlobalConfig.load()

    try:
        env_config = config.get_current_env()
        effective = config.get_effective_config()

        console.print("[bold]Current Environment[/bold]")
        console.print(f"Name: [cyan]{config.current_environment}[/cyan]")
        console.print(f"API URL: [blue]{effective['api_url']}[/blue]")

        if effective["auth_token"]:
            console.print("Auth Token: [green]✓ Configured[/green]")
        elif effective["agent_key"]:
            console.print("Agent Key: [green]✓ Configured[/green]")
        else:
            console.print("Auth: [yellow]Not configured[/yellow]")

        if env_config.default_workspace:
            console.print(
                f"Default Workspace: [cyan]{env_config.default_workspace}[/cyan]"
            )

        # Check connectivity
        status = _check_connection(effective["api_url"])
        console.print(f"\nConnection: {status}")

        # Show if environment variables are overriding config
        if os_env := os.getenv("ANYT_ENV"):
            console.print(
                f"\n[yellow]Note:[/yellow] Environment overridden by ANYT_ENV={os_env}"
            )
        if os_url := os.getenv("ANYT_API_URL"):
            console.print(
                f"[yellow]Note:[/yellow] API URL overridden by ANYT_API_URL={os_url}"
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _check_connection(api_url: str) -> str:
    """Check if the API is reachable."""
    try:
        response = httpx.get(f"{api_url}/v1/health", timeout=5.0)
        if response.status_code == 200:
            return "[green]Connected ✓[/green]"
        else:
            return f"[yellow]Responded with {response.status_code}[/yellow]"
    except httpx.ConnectError:
        return "[red]Connection failed[/red]"
    except httpx.TimeoutException:
        return "[yellow]Connection timeout[/yellow]"
    except Exception:
        return "[red]Error checking connection[/red]"
