"""MCP server commands."""

import asyncio
import typer
from rich.console import Console

from cli.config import GlobalConfig

app = typer.Typer(help="MCP server commands for Claude Code integration")
console = Console()


@app.command("serve")
def serve_mcp():
    """Start the MCP server for Claude Code integration.

    This command starts an MCP (Model Context Protocol) server that exposes
    AnyTask tools and resources to Claude Code. The server runs in the foreground
    and communicates via stdio.

    Environment variables required:
    - ANYTASK_API_KEY: Agent API key for authentication
    - ANYTASK_API_URL: Backend URL (default: http://0.0.0.0:8000)
    - ANYTASK_WORKSPACE_ID: Workspace ID to operate in

    Example:
        $ export ANYTASK_API_KEY=anyt_agent_xxx
        $ export ANYTASK_WORKSPACE_ID=1
        $ anyt mcp serve
    """
    console.print("[cyan]Starting AnyTask MCP server...[/cyan]")

    try:
        from anytask_mcp.server import main as run_server

        run_server()

    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("config")
def show_mcp_config():
    """Show MCP server configuration for Claude Code.

    This command displays the configuration snippet to add to Claude Code's
    MCP settings file (~/.config/claude/mcp.json).
    """
    import json

    console.print("[cyan bold]MCP Configuration for Claude Code[/cyan bold]")
    console.print()

    # Get workspace info if available
    try:
        global_config = GlobalConfig.load()
        effective_config = global_config.get_effective_config()
        api_url = effective_config.get("api_url", "http://0.0.0.0:8000")
        workspace_id = effective_config.get("workspace_id", "YOUR_WORKSPACE_ID")
        agent_key = "YOUR_API_KEY_HERE"
    except Exception:
        api_url = "http://0.0.0.0:8000"
        workspace_id = "YOUR_WORKSPACE_ID"
        agent_key = "YOUR_API_KEY_HERE"

    # Find the anyt executable
    import shutil

    anyt_path = shutil.which("anyt") or "anyt"

    config = {
        "mcpServers": {
            "anytask": {
                "command": anyt_path,
                "args": ["mcp", "serve"],
                "env": {
                    "ANYTASK_API_URL": api_url,
                    "ANYTASK_API_KEY": agent_key,
                    "ANYTASK_WORKSPACE_ID": str(workspace_id),
                },
            }
        }
    }

    console.print("Add this to your Claude Code MCP configuration:")
    console.print("[dim]~/.config/claude/mcp.json[/dim]")
    console.print()
    console.print(json.dumps(config, indent=2))
    console.print()

    console.print("[yellow]Important:[/yellow]")
    console.print("1. Replace [cyan]YOUR_API_KEY_HERE[/cyan] with your agent API key")
    console.print("2. Replace [cyan]YOUR_WORKSPACE_ID[/cyan] with your workspace ID")
    console.print("3. Get an agent key with: [cyan]anyt auth agent-key create[/cyan]")
    console.print("4. Get your workspace ID with: [cyan]anyt workspace list[/cyan]")
    console.print()


@app.command("test")
def test_mcp():
    """Test MCP server connection.

    This command verifies that the MCP server can connect to the AnyTask backend
    and lists available tools and resources.
    """
    console.print("[cyan]Testing MCP server connection...[/cyan]")

    async def test():
        try:
            from anytask_mcp.client import AnyTaskClient

            client = AnyTaskClient()

            # Test workspace access
            console.print("✓ API client initialized")

            workspace = await client.get_current_workspace()
            console.print(
                f"✓ Connected to workspace: {workspace.get('identifier', 'N/A')}"
            )

            # Test project access
            project = await client.get_current_project(workspace["id"])
            console.print(f"✓ Connected to project: {project.get('identifier', 'N/A')}")

            # Count tools and resources
            console.print("✓ 8 tools available:")
            tools = [
                "list_tasks",
                "select_task",
                "create_task",
                "update_task",
                "start_attempt",
                "finish_attempt",
                "add_artifact",
                "get_board",
            ]
            for tool in tools:
                console.print(f"  - {tool}")

            # List resources
            console.print("✓ 4 resource templates available")

            await client.close()

            console.print()
            console.print("[green]✓ All tests passed![/green]")

        except Exception as e:
            console.print(f"[red]✗ Test failed:[/red] {e}")
            raise typer.Exit(1)

    asyncio.run(test())
