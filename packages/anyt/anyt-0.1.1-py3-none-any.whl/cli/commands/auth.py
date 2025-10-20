"""Authentication commands for AnyTask CLI."""

import asyncio
import os
import typer
from typing_extensions import Annotated
from rich.console import Console

from cli.config import GlobalConfig
from cli.client import APIClient

app = typer.Typer(help="Manage authentication")
console = Console()


@app.command()
def login(
    env: Annotated[
        str | None,
        typer.Option("--env", "-e", help="Environment to login to"),
    ] = None,
    token: Annotated[
        bool,
        typer.Option(
            "--token", help="Login with Personal Access Token (prompts for value)"
        ),
    ] = False,
    agent_key: Annotated[
        bool,
        typer.Option(
            "--agent-key", help="Login with agent API key (prompts for value)"
        ),
    ] = False,
    token_value: Annotated[
        str | None,
        typer.Option(
            "--token-value", help="Personal Access Token value (skips prompt)"
        ),
    ] = None,
    agent_key_value: Annotated[
        str | None,
        typer.Option("--agent-key-value", help="Agent API key value (skips prompt)"),
    ] = None,
):
    """Login to AnyTask API.

    Supports multiple authentication flows:
    - Agent API key (--agent-key with value or from ANYT_AGENT_KEY env var)
    - Personal Access Token (--token with value)
    - Interactive prompt if flags provided without values

    Examples:
        anyt auth login --agent-key anyt_agent_...
        anyt auth login --token anyt_...
        anyt auth login  # Uses ANYT_AGENT_KEY if set
    """
    try:
        config = GlobalConfig.load()

        # Use specified environment or current one
        if env:
            if env not in config.environments:
                console.print(f"[red]Error:[/red] Environment '{env}' not found")
                console.print("\nAvailable environments:")
                for env_name in config.environments.keys():
                    console.print(f"  - {env_name}")
                raise typer.Exit(1)
            target_env = env
        else:
            target_env = config.current_environment

        env_config = config.environments[target_env]
        console.print(f"Environment: [cyan]{target_env}[/cyan] ({env_config.api_url})")

        # Determine which authentication method to use
        # Priority: explicit values > flags (with prompt) > environment variable > error
        if agent_key_value:
            # Agent API key provided directly
            key = agent_key_value

            # Validate format (but allow TEST_API_KEY for development)
            if not key.startswith("anyt_agent_") and len(key) < 30:
                console.print(
                    "[yellow]Warning:[/yellow] API key doesn't match expected format 'anyt_agent_...'"
                )
                console.print("Attempting to authenticate anyway...")

            # Verify the key works by making a test API call
            client = APIClient(base_url=env_config.api_url, agent_key=key)

            async def verify_key():
                try:
                    await client.health_check()
                    return True
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to authenticate: {e}")
                    return False

            if not asyncio.run(verify_key()):
                raise typer.Exit(1)

            # Store the agent key
            env_config.auth_token = key
            config.environments[target_env] = env_config
            config.save()

            console.print("[green]✓[/green] Authenticated as agent")

        elif agent_key:
            # Agent API key flag - prompt for value
            key = typer.prompt("Enter agent key", hide_input=True)

            # Validate format (but allow TEST_API_KEY for development)
            if not key.startswith("anyt_agent_") and len(key) < 30:
                console.print(
                    "[yellow]Warning:[/yellow] API key doesn't match expected format 'anyt_agent_...'"
                )
                console.print("Attempting to authenticate anyway...")

            # Verify the key works by making a test API call
            client = APIClient(base_url=env_config.api_url, agent_key=key)

            async def verify_key():
                try:
                    await client.health_check()
                    return True
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to authenticate: {e}")
                    return False

            if not asyncio.run(verify_key()):
                raise typer.Exit(1)

            # Store the agent key
            env_config.auth_token = key
            config.environments[target_env] = env_config
            config.save()

            console.print("[green]✓[/green] Authenticated as agent")

        elif token_value:
            # PAT provided directly
            pat = token_value

            if not pat.startswith("anyt_"):
                console.print(
                    "[yellow]Warning:[/yellow] Token doesn't start with 'anyt_'. This may be invalid."
                )

            # Verify the token works
            client = APIClient(base_url=env_config.api_url, auth_token=pat)

            async def verify_token():
                try:
                    await client.health_check()
                    return True
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to authenticate: {e}")
                    return False

            if not asyncio.run(verify_token()):
                raise typer.Exit(1)

            # Store the token
            env_config.auth_token = pat
            config.environments[target_env] = env_config
            config.save()

            console.print("[green]✓[/green] Logged in successfully")

        elif token:
            # PAT flag - prompt for value
            pat = typer.prompt("Enter PAT", hide_input=True)

            if not pat.startswith("anyt_"):
                console.print(
                    "[yellow]Warning:[/yellow] Token doesn't start with 'anyt_'. This may be invalid."
                )

            # Verify the token works
            client = APIClient(base_url=env_config.api_url, auth_token=pat)

            async def verify_token():
                try:
                    await client.health_check()
                    return True
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to authenticate: {e}")
                    return False

            if not asyncio.run(verify_token()):
                raise typer.Exit(1)

            # Store the token
            env_config.auth_token = pat
            config.environments[target_env] = env_config
            config.save()

            console.print("[green]✓[/green] Logged in successfully")

        else:
            # No explicit flags - check for ANYT_AGENT_KEY environment variable
            env_agent_key = os.getenv("ANYT_AGENT_KEY")
            if env_agent_key:
                console.print("[cyan]Using ANYT_AGENT_KEY from environment[/cyan]")

                # Validate format (but allow TEST_API_KEY for development)
                if (
                    not env_agent_key.startswith("anyt_agent_")
                    and len(env_agent_key) < 30
                ):
                    console.print(
                        "[yellow]Warning:[/yellow] API key doesn't match expected format 'anyt_agent_...'"
                    )
                    console.print("Attempting to authenticate anyway...")

                # Verify the key works
                client = APIClient(base_url=env_config.api_url, agent_key=env_agent_key)

                async def verify_key():
                    try:
                        await client.health_check()
                        return True
                    except Exception as e:
                        console.print(f"[red]Error:[/red] Failed to authenticate: {e}")
                        return False

                if not asyncio.run(verify_key()):
                    raise typer.Exit(1)

                # Store the agent key
                env_config.auth_token = env_agent_key
                config.environments[target_env] = env_config
                config.save()

                console.print("[green]✓[/green] Authenticated as agent")
            else:
                # No authentication method specified
                console.print("[yellow]No authentication method specified[/yellow]")
                console.print("\nOptions:")
                console.print("  1. Set ANYT_AGENT_KEY environment variable")
                console.print(
                    "  2. Use [cyan]--agent-key[/cyan] flag with value or for prompt"
                )
                console.print(
                    "  3. Use [cyan]--token[/cyan] flag with value or for prompt"
                )
                console.print("\nExamples:")
                console.print("  anyt auth login --agent-key anyt_agent_...")
                console.print("  anyt auth login --token anyt_...")
                console.print("  ANYT_AGENT_KEY=anyt_agent_... anyt auth login")
                raise typer.Exit(1)

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        else:
            # Re-raise typer.Exit to preserve exit code
            raise


@app.command()
def logout(
    env: Annotated[
        str | None,
        typer.Option("--env", "-e", help="Environment to logout from"),
    ] = None,
    all_envs: Annotated[
        bool,
        typer.Option("--all", help="Logout from all environments"),
    ] = False,
):
    """Logout from AnyTask API.

    Clears stored authentication credentials for the specified environment
    or all environments.
    """
    try:
        config = GlobalConfig.load()

        if all_envs:
            # Clear all environment credentials
            for env_name in config.environments:
                config.environments[env_name].auth_token = None
            config.save()
            console.print("[green]✓[/green] Logged out from all environments")

        else:
            # Logout from specific environment
            if env:
                if env not in config.environments:
                    console.print(f"[red]Error:[/red] Environment '{env}' not found")
                    raise typer.Exit(1)
                target_env = env
            else:
                target_env = config.current_environment

            # Clear credentials
            config.environments[target_env].auth_token = None
            config.save()

            console.print(f"[green]✓[/green] Logged out from {target_env}")

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        else:
            # Re-raise typer.Exit to preserve exit code
            raise


@app.command()
def whoami():
    """Show information about the currently authenticated user or agent."""
    try:
        config = GlobalConfig.load()
        effective_config = config.get_effective_config()

        env_name = effective_config["environment"]
        api_url = effective_config["api_url"]

        console.print(f"Environment: [cyan]{env_name}[/cyan]")
        console.print(f"API URL: {api_url}")

        # Check if authenticated
        # Check for agent key from env var first, then check if stored token is an agent key
        auth_token = effective_config.get("auth_token")
        agent_key = effective_config.get("agent_key")

        # Determine if we're using an agent key
        is_agent_key = False
        credential = None

        if agent_key:
            is_agent_key = True
            credential = agent_key
        elif auth_token:
            # Check if the stored token is actually an agent key
            # Detect agent keys: starts with anyt_agent_ OR is a long string without @ (email indicator)
            if auth_token.startswith("anyt_agent_") or (
                len(auth_token) > 30 and "@" not in auth_token
            ):
                is_agent_key = True
                credential = auth_token
            else:
                credential = auth_token

        if credential:
            if is_agent_key:
                console.print("Authentication: [green]Agent Key[/green]")
                client = APIClient(base_url=api_url, agent_key=credential)
            else:
                console.print("Authentication: [green]User Token[/green]")
                client = APIClient(base_url=api_url, auth_token=credential)

            async def get_info():
                try:
                    await client.health_check()
                    workspaces = await client.list_workspaces()
                    return workspaces
                except Exception:
                    return None

            workspaces = asyncio.run(get_info())

            if workspaces:
                console.print("Status: [green]Connected ✓[/green]")
                if workspaces:
                    console.print("\nAccessible workspaces:")
                    for ws in workspaces:
                        console.print(f"  - {ws.get('name')} ({ws.get('identifier')})")
            else:
                console.print("Status: [red]Not connected ✗[/red]")

        else:
            console.print("Authentication: [yellow]Not logged in[/yellow]")
            console.print("\nUse [cyan]anyt auth login[/cyan] to authenticate")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
