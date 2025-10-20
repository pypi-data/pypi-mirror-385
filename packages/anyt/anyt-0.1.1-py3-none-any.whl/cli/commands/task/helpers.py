"""Helper functions for task commands."""

from datetime import datetime, timedelta
from typing import Optional

from cli.config import ActiveTaskConfig, GlobalConfig, WorkspaceConfig
from cli.client import APIClient
from rich.console import Console

import typer

console = Console()

# Workspace resolution cache
# Maps (workspace_identifier_or_id) -> (workspace_id, workspace_identifier, timestamp)
_workspace_cache: dict[str, tuple[int, str, datetime]] = {}
_CACHE_TTL = timedelta(minutes=5)


def clear_workspace_cache():
    """Clear the workspace resolution cache.

    Call this when switching workspaces or when you want to force
    a fresh lookup from the API.
    """
    global _workspace_cache
    _workspace_cache.clear()


def get_workspace_or_exit() -> tuple[WorkspaceConfig, GlobalConfig]:
    """Load workspace config and global config or exit with error.

    Returns:
        Tuple of (workspace_config, global_config)

    Raises:
        typer.Exit: If workspace is not initialized or config cannot be loaded
    """
    # Check if workspace is initialized
    ws_config = WorkspaceConfig.load()
    if not ws_config:
        console.print("[red]Error:[/red] Not in a workspace directory")
        console.print("Run [cyan]anyt workspace init[/cyan] first")
        raise typer.Exit(1)

    # Load global config
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

    return ws_config, global_config


async def resolve_workspace_context(
    workspace_arg: Optional[str], global_config: GlobalConfig, client: APIClient
) -> tuple[int, str]:
    """Resolve workspace context from --workspace flag, config, or local workspace.

    Uses a cache to avoid repeated API calls for workspace resolution.
    Cache expires after 5 minutes.

    Priority order:
    1. --workspace flag (if provided)
    2. Environment's default_workspace (from config)
    3. Local .anyt/anyt.json workspace

    Args:
        workspace_arg: Workspace identifier or ID from --workspace flag
        global_config: Global configuration
        client: API client for fetching workspace details

    Returns:
        Tuple of (workspace_id, workspace_identifier)

    Raises:
        typer.Exit: If workspace cannot be resolved or is invalid
    """
    # Priority 1: Explicit --workspace flag
    if workspace_arg:
        # Check cache first
        cache_key = workspace_arg.upper()
        if cache_key in _workspace_cache:
            cached_id, cached_identifier, cached_time = _workspace_cache[cache_key]
            if datetime.now() - cached_time < _CACHE_TTL:
                return cached_id, cached_identifier

        # Fetch all workspaces to resolve identifier or ID
        workspaces = await client.list_workspaces()
        for ws in workspaces:
            if (
                str(ws.get("id")) == workspace_arg
                or ws.get("identifier") == workspace_arg.upper()
            ):
                workspace_id = int(ws["id"])
                workspace_identifier = ws["identifier"]
                # Update cache
                _workspace_cache[cache_key] = (
                    workspace_id,
                    workspace_identifier,
                    datetime.now(),
                )
                return workspace_id, workspace_identifier

        console.print(f"[red]Error:[/red] Workspace '{workspace_arg}' not found")
        console.print("\nAvailable workspaces:")
        for ws in workspaces:
            console.print(
                f"  {ws.get('identifier', '')} - {ws.get('name', '')} (ID: {ws.get('id', '')})"
            )
        raise typer.Exit(1)

    # Priority 2: Environment's default workspace
    env_config = global_config.get_current_env()
    if env_config.default_workspace:
        # Fetch workspace by identifier
        workspaces = await client.list_workspaces()
        for ws in workspaces:
            if ws.get("identifier") == env_config.default_workspace:
                return int(ws["id"]), ws["identifier"]

        console.print(
            f"[yellow]Warning:[/yellow] Default workspace '{env_config.default_workspace}' not found"
        )
        console.print(
            "Falling back to local workspace or provide --workspace flag explicitly"
        )

    # Priority 3: Local .anyt/anyt.json workspace
    ws_config = WorkspaceConfig.load()
    if ws_config:
        workspace_id = int(ws_config.workspace_id)
        workspace_identifier = ws_config.workspace_identifier or "UNKNOWN"
        return workspace_id, workspace_identifier

    # No workspace found
    console.print("[red]Error:[/red] No workspace context available")
    console.print("\nOptions:")
    console.print("  1. Initialize workspace: [cyan]anyt workspace init[/cyan]")
    console.print(
        "  2. Set default workspace: [cyan]anyt workspace use WORKSPACE[/cyan]"
    )
    console.print("  3. Use --workspace flag: [cyan]--workspace DEV[/cyan]")
    raise typer.Exit(1)


def format_priority(priority: int) -> str:
    """Format priority as visual dots.

    Priority scale: -2 (lowest) to 2 (highest)
    """
    if priority >= 2:
        return "●●●"
    elif priority == 1:
        return "●●○"
    elif priority == 0:
        return "●○○"
    elif priority == -1:
        return "○○○"
    else:  # -2 or lower
        return "○○○"


def format_relative_time(dt_str: Optional[str]) -> str:
    """Format datetime string as relative time (e.g., '2h ago')."""
    if not dt_str:
        return "—"

    try:
        # Parse ISO format datetime
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        delta = now - dt

        seconds = int(delta.total_seconds())

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h ago"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days}d ago"
        else:
            weeks = seconds // 604800
            return f"{weeks}w ago"
    except Exception:
        return dt_str


def truncate_text(text: str, max_length: int = 40) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"


def get_active_task_id() -> Optional[str]:
    """Get the active task identifier from .anyt/active_task.json.

    Returns:
        Task identifier if an active task is set, None otherwise.
    """
    active_task = ActiveTaskConfig.load()
    return active_task.identifier if active_task else None


def normalize_identifier(task_id: str, workspace_prefix: Optional[str] = None) -> str:
    """Normalize task identifier for fuzzy matching.

    Handles variations like:
    - DEV-42 → DEV-42 (full identifier)
    - dev42 → DEV-42 (case insensitive, no dash)
    - 42 → 42 (just number)
    - DEV 42 → DEV-42 (with space)

    Args:
        task_id: The task identifier to normalize
        workspace_prefix: Workspace prefix (e.g., "DEV") to use if identifier is just a number

    Returns:
        Normalized task identifier
    """
    task_id = task_id.strip()

    # If it's just a number, prepend workspace prefix if provided
    if task_id.isdigit():
        if workspace_prefix:
            return f"{workspace_prefix}-{task_id}"
        return task_id

    # If it contains a dash already (DEV-42), normalize case
    if "-" in task_id:
        parts = task_id.split("-", 1)
        return f"{parts[0].upper()}-{parts[1]}"

    # If it contains a space (DEV 42), replace with dash
    if " " in task_id:
        parts = task_id.split(" ", 1)
        return f"{parts[0].upper()}-{parts[1]}"

    # Try to split alphanumeric (dev42 → DEV-42)
    # Find where digits start
    for i, char in enumerate(task_id):
        if char.isdigit():
            if i > 0:
                prefix = task_id[:i].upper()
                number = task_id[i:]
                return f"{prefix}-{number}"
            break

    # If nothing matched, return as uppercase
    return task_id.upper()


def output_json(data: dict, success: bool = True) -> None:
    """Output data as JSON to stdout.

    Args:
        data: The data to output as JSON
        success: Whether this is a success response (affects structure)
    """
    import json

    if success:
        output = {"success": True, "data": data}
    else:
        output = {"success": False, **data}

    print(json.dumps(output, indent=2))


async def find_similar_tasks(
    client: APIClient, workspace_id: int, identifier: str, limit: int = 3
) -> list[dict]:
    """Find tasks with similar identifiers using fuzzy matching.

    Args:
        client: API client
        workspace_id: Workspace ID to search in
        identifier: The identifier that wasn't found
        limit: Maximum number of suggestions to return

    Returns:
        List of similar tasks
    """
    import difflib

    try:
        # Fetch recent tasks from workspace
        result = await client.list_tasks(
            workspace_id=workspace_id, limit=50, sort_by="updated_at", order="desc"
        )

        tasks = result.get("items", [])

        if not tasks:
            return []

        # Get all task identifiers
        identifiers = [t.get("identifier", str(t.get("id", ""))) for t in tasks]

        # Use difflib to find similar matches
        matches = difflib.get_close_matches(
            identifier.upper(),
            [id.upper() for id in identifiers],
            n=limit,
            cutoff=0.4,  # Lower cutoff for more suggestions
        )

        # Return the corresponding tasks
        similar_tasks = []
        for match in matches:
            for task in tasks:
                task_id = task.get("identifier", str(task.get("id", "")))
                if task_id.upper() == match:
                    similar_tasks.append(task)
                    break

        return similar_tasks

    except Exception:
        return []
