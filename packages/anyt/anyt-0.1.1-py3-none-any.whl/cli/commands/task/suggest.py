"""Task suggestion command - recommends tasks to work on next."""

import asyncio

import typer
from typing_extensions import Annotated

from cli.client import APIClient

from .helpers import console, get_workspace_or_exit, output_json


async def score_task(task: dict, client: APIClient) -> tuple[int, str, dict]:
    """Calculate a score for task suggestion priority.

    Args:
        task: Task dictionary
        client: API client for fetching dependencies

    Returns:
        Tuple of (score, reason, metadata)
    """
    score = 0
    reasons = []

    # Priority weighting (most important factor)
    priority = task.get("priority", 0)
    score += priority * 5
    if priority >= 1:
        reasons.append(f"Priority {priority}")

    # Status bonus
    status = task.get("status", "")
    if status == "todo":
        score += 3
        reasons.append("Ready to work on")
    elif status == "inprogress":
        score += 1  # Already started, moderate bonus
        reasons.append("In progress")

    # Check dependencies
    try:
        identifier = task.get("identifier", str(task.get("id", "")))
        deps = await client.get_task_dependencies(identifier)
        incomplete_deps = [d for d in deps if d.get("status") != "done"]

        if incomplete_deps:
            score -= 10  # Heavily penalize blocked tasks
            # Don't add to reasons - we'll filter these out anyway
        elif deps:
            score += 2  # Bonus for having completed dependencies
            reasons.append("All dependencies complete")
        else:
            reasons.append("No dependencies")
    except Exception:
        # If we can't fetch dependencies, assume none
        pass

    # Check impact (how many tasks this unblocks)
    try:
        dependents = await client.get_task_dependents(identifier)
        unblocks_count = len(dependents)
        if unblocks_count > 0:
            score += unblocks_count * 2
            reasons.append(
                f"Unblocks {unblocks_count} task{'s' if unblocks_count > 1 else ''}"
            )
    except Exception:
        dependents = []
        unblocks_count = 0

    # Build metadata
    metadata = {
        "has_blockers": len(incomplete_deps) > 0
        if "incomplete_deps" in locals()
        else False,
        "unblocks_count": unblocks_count,
        "is_ready": len(incomplete_deps) == 0
        if "incomplete_deps" in locals()
        else True,
    }

    # Generate reason string
    reason = ", ".join(reasons) if reasons else "Available to work on"

    return score, reason, metadata


async def generate_suggestions(
    workspace_id: int,
    client: APIClient,
    limit: int = 3,
    status_filter: str = "todo,backlog",
) -> list[dict]:
    """Generate task suggestions.

    Args:
        workspace_id: Workspace ID
        client: API client
        limit: Number of suggestions to return
        status_filter: Comma-separated status values

    Returns:
        List of suggestion dictionaries
    """
    # Get candidate tasks
    # Convert comma-separated status string to list
    status_list = (
        [s.strip() for s in status_filter.split(",")] if status_filter else None
    )

    tasks = await client.list_tasks(
        workspace_id=workspace_id,
        status=status_list,
        limit=50,  # Get more candidates than we need
    )

    # Handle SuccessResponse wrapper
    if isinstance(tasks, dict) and "data" in tasks:
        task_list = tasks["data"].get("items", [])
    elif isinstance(tasks, dict) and "items" in tasks:
        task_list = tasks["items"]
    else:
        task_list = tasks if isinstance(tasks, list) else []

    # Score each task
    scored_tasks = []
    for task in task_list:
        score, reason, metadata = await score_task(task, client)

        # Filter out blocked tasks
        if metadata["has_blockers"]:
            continue

        scored_tasks.append(
            {"task": task, "score": score, "reason": reason, "metadata": metadata}
        )

    # Sort by score (descending)
    scored_tasks.sort(key=lambda x: x["score"], reverse=True)

    # Return top N
    return scored_tasks[:limit]


def suggest_tasks(
    limit: Annotated[
        int,
        typer.Option("--limit", help="Number of suggestions to return"),
    ] = 3,
    status: Annotated[
        str,
        typer.Option("--status", help="Filter by status (comma-separated)"),
    ] = "todo,backlog",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
):
    """Suggest tasks to work on next based on priority, dependencies, and impact.

    Analyzes available tasks and recommends the best ones to work on.
    Considers:
    - Priority (higher priority scores better)
    - Status (todo/backlog preferred)
    - Dependencies (filters out blocked tasks, prefers ready tasks)
    - Impact (prefers tasks that unblock others)
    """
    ws_config, global_config = get_workspace_or_exit()
    client = APIClient.from_config(global_config)

    async def run_suggestions():
        try:
            suggestions = await generate_suggestions(
                workspace_id=int(ws_config.workspace_id),
                client=client,
                limit=limit,
                status_filter=status,
            )

            if json_output:
                # JSON output
                output_data = {
                    "suggestions": [
                        {
                            "identifier": s["task"].get(
                                "identifier", str(s["task"].get("id", ""))
                            ),
                            "title": s["task"].get("title", ""),
                            "priority": s["task"].get("priority", 0),
                            "status": s["task"].get("status", ""),
                            "score": s["score"],
                            "reason": s["reason"],
                            "metadata": s["metadata"],
                        }
                        for s in suggestions
                    ]
                }
                output_json(output_data)
            else:
                # Pretty console output
                if not suggestions:
                    console.print("\n[yellow]No task suggestions available.[/yellow]")
                    console.print(
                        "Try adjusting filters with --status or create new tasks.\n"
                    )
                    return

                console.print(
                    f"\n[cyan bold]Top {len(suggestions)} Recommended Task{'s' if len(suggestions) > 1 else ''}:[/cyan bold]\n"
                )

                for i, s in enumerate(suggestions, 1):
                    task = s["task"]
                    task_id = task.get("identifier", str(task.get("id", "")))
                    title = task.get("title", "")
                    priority_val = task.get("priority", 0)
                    status_val = task.get("status", "")

                    console.print(
                        f"{i}. [bold cyan]{task_id}[/bold cyan] - {title} [dim][Priority: {priority_val}][/dim]"
                    )
                    console.print(f"   Reason: {s['reason']}")
                    console.print(f"   Status: [yellow]{status_val}[/yellow]\n")

                console.print(
                    "[dim]Run: anyt task pick <ID> to start working on a task[/dim]\n"
                )

        except Exception as e:
            if json_output:
                output_json({"error": "SuggestError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to generate suggestions: {e}")
            raise typer.Exit(1)

    asyncio.run(run_suggestions())
