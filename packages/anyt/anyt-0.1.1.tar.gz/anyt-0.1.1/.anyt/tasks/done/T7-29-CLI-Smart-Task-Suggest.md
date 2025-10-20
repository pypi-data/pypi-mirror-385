# T7-29: CLI Command - Smart Task Suggestion

## Priority
Medium

## Status
Completed

## Description
Add a new CLI command `anyt task suggest` that implements intelligent task suggestion logic. This makes it easy for both users and Claude Code to get recommendations on what to work on next.

Instead of requiring Claude to parse and analyze task lists, the CLI does the work and returns pre-ranked suggestions.

## Objectives
1. Add `anyt task suggest` command
2. Implement scoring algorithm for task prioritization
3. Return top 3-5 suggested tasks with reasoning
4. Support filtering options

## Acceptance Criteria
- [ ] New command `anyt task suggest` available
- [ ] Command returns top 3-5 tasks sorted by computed score
- [ ] Each suggestion includes reasoning (why it's recommended)
- [ ] Filters out blocked tasks (incomplete dependencies)
- [ ] Considers: priority, status, dependencies, impact
- [ ] Supports `--json` output
- [ ] Supports `--limit` parameter (default: 3)
- [ ] Works with current workspace context

## Dependencies
- None (can implement independently)

## Estimated Effort
2-3 hours

## Technical Notes

### Command Signature

```bash
$ anyt task suggest [OPTIONS]

Options:
  --limit INTEGER         Number of suggestions to return (default: 3)
  --status TEXT          Filter by status (default: todo,backlog)
  --json                 Output in JSON format

Examples:
  $ anyt task suggest
  $ anyt task suggest --limit 5
  $ anyt task suggest --json
```

### Command Output (Human-Readable)

```
$ anyt task suggest

Top 3 Recommended Tasks:

1. DEV-42 - Implement OAuth callback [Priority: 2]
   Reason: Highest priority, no blockers, unblocks 2 tasks
   Status: todo

2. DEV-45 - Add Redis caching [Priority: 1]
   Reason: High priority, no dependencies, quick win
   Status: todo

3. DEV-48 - Update API documentation [Priority: 0]
   Reason: Ready to work on, no blockers
   Status: backlog

Run: anyt task pick <ID> to start working on a task
```

### JSON Output

```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "identifier": "DEV-42",
        "title": "Implement OAuth callback",
        "priority": 2,
        "status": "todo",
        "score": 15,
        "reason": "Highest priority, no blockers, unblocks 2 tasks",
        "metadata": {
          "has_blockers": false,
          "unblocks_count": 2,
          "is_ready": true
        }
      },
      {
        "identifier": "DEV-45",
        "title": "Add Redis caching",
        "priority": 1,
        "status": "todo",
        "score": 10,
        "reason": "High priority, no dependencies, quick win",
        "metadata": {
          "has_blockers": false,
          "unblocks_count": 0,
          "is_ready": true
        }
      }
    ]
  },
  "message": null
}
```

### Scoring Algorithm

```python
async def score_task(task, client):
    """Calculate a score for task suggestion priority."""
    score = 0

    # Priority weighting (most important factor)
    score += task["priority"] * 5

    # Status bonus
    if task["status"] == "todo":
        score += 3
    elif task["status"] == "inprogress":
        score += 1  # Already started, moderate bonus

    # Check dependencies
    deps = await client.get_task_dependencies(task["identifier"])
    incomplete_deps = [d for d in deps if d["status"] != "done"]

    if incomplete_deps:
        score -= 10  # Heavily penalize blocked tasks
    elif deps:
        score += 2  # Bonus for having completed dependencies

    # Check impact (how many tasks this unblocks)
    dependents = await client.get_task_dependents(task["identifier"])
    unblocks_count = len(dependents)
    score += unblocks_count * 2

    # Age factor (older tasks get slight bonus)
    # ... could add created_at check ...

    return score

async def generate_suggestions(workspace_id, limit=3):
    """Generate task suggestions."""
    client = APIClient()

    # Get candidate tasks
    response = await client.list_tasks(
        workspace_id=workspace_id,
        status="todo,backlog",
        sort_by="priority",
        order="desc",
        limit=50
    )

    tasks = response["items"]

    # Score each task
    scored_tasks = []
    for task in tasks:
        score = await score_task(task, client)

        # Get metadata for reasoning
        deps = await client.get_task_dependencies(task["identifier"])
        dependents = await client.get_task_dependents(task["identifier"])
        incomplete_deps = [d for d in deps if d["status"] != "done"]

        # Generate reason
        reasons = []
        if task["priority"] >= 1:
            reasons.append(f"Priority {task['priority']}")
        if not incomplete_deps:
            if deps:
                reasons.append("All dependencies complete")
            else:
                reasons.append("No dependencies")
        if dependents:
            reasons.append(f"Unblocks {len(dependents)} task{'s' if len(dependents) > 1 else ''}")
        if task["status"] == "todo":
            reasons.append("Ready to work on")

        scored_tasks.append({
            "task": task,
            "score": score,
            "reason": ", ".join(reasons) if reasons else "Available to work on",
            "metadata": {
                "has_blockers": len(incomplete_deps) > 0,
                "unblocks_count": len(dependents),
                "is_ready": len(incomplete_deps) == 0
            }
        })

    # Sort by score
    scored_tasks.sort(key=lambda x: x["score"], reverse=True)

    # Return top N
    return scored_tasks[:limit]
```

### Implementation

```python
# src/cli/commands/task.py

@app.command("suggest")
def suggest_tasks(
    limit: int = typer.Option(3, help="Number of suggestions to return"),
    status: str = typer.Option("todo,backlog", help="Filter by status"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Suggest tasks to work on next based on priority, dependencies, and impact.

    Analyzes available tasks and recommends the best ones to work on.
    """
    asyncio.run(_suggest_tasks_async(limit, status, json_output))

async def _suggest_tasks_async(limit: int, status: str, json_output: bool):
    """Async implementation of task suggestion."""
    try:
        config = GlobalConfig.load()
        effective_config = config.get_effective_config()
        workspace_id = effective_config.get("workspace_id")

        suggestions = await generate_suggestions(workspace_id, limit)

        if json_output:
            output = {
                "success": True,
                "data": {
                    "suggestions": [
                        {
                            "identifier": s["task"]["identifier"],
                            "title": s["task"]["title"],
                            "priority": s["task"]["priority"],
                            "status": s["task"]["status"],
                            "score": s["score"],
                            "reason": s["reason"],
                            "metadata": s["metadata"]
                        }
                        for s in suggestions
                    ]
                },
                "message": None
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Pretty output
            console.print("\n[cyan bold]Top {} Recommended Tasks:[/cyan bold]\n".format(limit))

            for i, s in enumerate(suggestions, 1):
                task = s["task"]
                console.print(f"{i}. [bold]{task['identifier']}[/bold] - {task['title']} [dim][Priority: {task['priority']}][/dim]")
                console.print(f"   Reason: {s['reason']}")
                console.print(f"   Status: {task['status']}\n")

            console.print("[dim]Run: anyt task pick <ID> to start working on a task[/dim]")

    except Exception as e:
        handle_error(e, json_output)
```

### Usage in Slash Commands

Update `.claude/commands/anyt-next.md` to use this command:

```markdown
1. Run: `uv run src/cli/main.py task suggest --json --limit 5`

2. The CLI will return suggested tasks with scores and reasoning

3. Present the suggestions to the user and help them choose
```

## Events

### 2025-10-18 - Started work
- Moved task from backlog to active
- Reviewed task specification and acceptance criteria
- Beginning implementation of `anyt task suggest` command

### 2025-10-18 - Implementation complete
- Created `src/cli/commands/task/suggest.py` with full scoring algorithm
- Implemented async scoring function that considers priority, status, dependencies, and impact
- Added intelligent filtering to exclude blocked tasks
- Registered command in `task/__init__.py`
- Command supports `--limit`, `--status`, and `--json` flags
- Updated `.claude/commands/anyt-next.md` to use the new command
- Added comprehensive documentation to `docs/CLI_USAGE.md`
- All acceptance criteria met:
  ✓ Command returns top 3-5 tasks sorted by score
  ✓ Each suggestion includes reasoning
  ✓ Filters out blocked tasks
  ✓ Considers priority, status, dependencies, and impact
  ✓ Supports --json output
  ✓ Supports --limit parameter (default: 3)
  ✓ Works with current workspace context

## Related Files
- `src/cli/commands/task.py` - Add suggest subcommand
- `.claude/commands/anyt-next.md` - Update to use suggest command
- `docs/CLI_USAGE.md` - Document new command
