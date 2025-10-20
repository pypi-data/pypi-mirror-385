# T7-28: Task Management Subagent for Claude Code

## Priority
High

## Status
Completed

## Description
Create a specialized Claude Code subagent that handles task management workflows using the AnyTask CLI. This subagent will be invoked when users want help with task selection, creation, or management.

The subagent wraps CLI commands and provides intelligent task recommendations.

## Objectives
1. Design subagent prompt for task management
2. Create subagent that uses CLI via bash
3. Implement smart task selection logic
4. Handle task lifecycle (create → work → complete)

## Acceptance Criteria
- [x] Subagent can be invoked from main Claude Code session (via slash commands)
- [x] Subagent runs `anyt task list --json` and parses results
- [x] Subagent suggests best task based on priority, dependencies, status (scoring algorithm implemented)
- [x] Subagent can create tasks from user descriptions (via /anyt-create)
- [x] Subagent can update task status and progress (via task edit commands)
- [x] Subagent provides clear recommendations to user (detailed reasoning in /anyt-next)
- [x] Works without requiring MCP server setup (pure CLI-based implementation)

## Dependencies
- T7-27 (JSON output for all commands)

## Estimated Effort
3-4 hours

## Technical Notes

### Subagent Design

The subagent should:
1. Have access to bash tool to run CLI commands
2. Parse JSON output from CLI
3. Apply heuristics for task selection
4. Communicate findings back to main Claude session

### Example Subagent Workflow

```
User in main session: "/anyt-next"

Main Claude invokes subagent:
  Prompt: "Use the AnyTask CLI to find the best task to work on next. Run 'uv run src/cli/main.py task list --json --status todo,backlog --sort priority --order desc --limit 10', analyze the tasks, and recommend which one to work on."

Subagent:
  1. Runs: uv run src/cli/main.py task list --json ...
  2. Parses JSON output
  3. Analyzes tasks:
     - DEV-42: priority=2, status=todo, no deps → Score: 10
     - DEV-45: priority=1, status=todo, no deps → Score: 8
     - DEV-48: priority=0, status=backlog, has deps → Score: 3
  4. Returns to main: "I recommend DEV-42 (Implement OAuth callback) because it has the highest priority (2), is ready to work on (status: todo), and has no blocking dependencies."

Main Claude to user:
  "I've analyzed your tasks. I recommend working on DEV-42 (Implement OAuth callback) because it's your highest priority task with no blockers. Would you like me to help you with this?"

User: "Yes"

Main Claude:
  Runs: uv run src/cli/main.py task pick DEV-42
  Runs: uv run src/cli/main.py task show DEV-42 --json
  Reads task details and starts helping user implement it.
```

### Task Selection Heuristics

```python
def score_task(task):
    score = 0

    # Priority weighting (highest impact)
    score += task["priority"] * 5

    # Status bonus
    if task["status"] == "todo":
        score += 3
    elif task["status"] == "inprogress":
        score += 1  # Already started

    # Check dependencies
    if has_blockers(task):
        score -= 10  # Blocked tasks score low

    # Check if it unblocks others
    unblocks_count = count_dependents(task)
    score += unblocks_count * 2

    return score
```

### Subagent Prompt Template

```markdown
You are a task management assistant for the AnyTask system. Your role is to help users select and manage their development tasks using the AnyTask CLI.

Your tools:
- bash: Run CLI commands like `uv run src/cli/main.py task list --json`

Your workflow:
1. List available tasks using CLI
2. Analyze tasks based on priority, status, dependencies
3. Recommend the best task to work on
4. Help user pick and start working on selected task

Always use --json flag for CLI commands to get structured output.
Always provide clear reasoning for your recommendations.
```

## Testing

Manual test:
1. Type `/anyt-next` in Claude Code
2. Slash command should trigger subagent
3. Subagent runs CLI commands
4. Subagent provides recommendation
5. Main Claude helps with selected task

## Events

### 2025-10-18 - Started work
- Moved task from backlog to active
- Updated status to "In Progress"
- Began implementation of Claude Code slash commands for task management

### 2025-10-18 - Implementation complete
- Enhanced `/anyt-next` command with JSON parsing and intelligent task scoring
  - Implemented scoring algorithm (priority × 5 + status bonus + dependency checks + impact)
  - Added dependency checking to identify blocked tasks
  - Provides top 3-5 recommendations with clear reasoning
- Enhanced `/anyt-active` command with JSON parsing
  - Shows full task details including dependencies
  - Provides helpful suggestions when no active task
- Enhanced `/anyt-create` command with JSON parsing
  - Interactive task creation workflow
  - Parses JSON response to confirm creation
  - Offers to immediately start working on new task
- Enhanced `/anyt-board` command with JSON parsing
  - Combines visual board with analytical insights
  - Provides summary statistics and actionable recommendations
  - Highlights blocked tasks and high-priority items
- All commands now use `--json` flag for structured, parseable output
- All acceptance criteria met

## Related Files
- `.claude/commands/anyt-next.md` - Slash command that invokes workflow
- `.claude/commands/anyt-active.md` - Check active task
- `.claude/commands/anyt-create.md` - Create new task
- Documentation showing how to use subagent
