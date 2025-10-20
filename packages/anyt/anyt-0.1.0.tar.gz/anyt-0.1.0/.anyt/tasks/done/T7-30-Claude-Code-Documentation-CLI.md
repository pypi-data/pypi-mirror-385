# T7-30: Claude Code Integration Documentation (CLI-Based)

## Priority
Medium

## Status
Completed

## Description
Create comprehensive documentation for Claude Code integration using slash commands and the AnyTask CLI (NOT MCP server). This enables developers to quickly get started with task management from within Claude Code using simple commands.

## Objectives
1. Create integration guide in `docs/CLAUDE_CODE_INTEGRATION.md`
2. Document all slash commands
3. Provide workflow examples
4. Add troubleshooting section

## Acceptance Criteria
- [x] New file `docs/CLAUDE_CODE_INTEGRATION.md` created
- [x] Setup instructions (backend + CLI)
- [x] List of all slash commands with descriptions
- [x] Workflow examples (select task, create task, complete task)
- [x] Troubleshooting section
- [x] Update main README.md with Claude Code integration section

## Dependencies
- T7-27 (JSON output)
- T7-29 (Suggest command)

## Estimated Effort
2-3 hours

## Technical Notes

### Documentation Outline

```markdown
# Claude Code Integration Guide (CLI-Based)

## Overview
AnyTask integrates with Claude Code via slash commands and CLI tools, allowing Claude to help you manage tasks, select priorities, and track progress.

**No MCP server required!** Just use the CLI.

## Setup

### 1. Install and Configure AnyTask

```bash
# Install dependencies
make install

# Start backend
make dev

# In another terminal, configure CLI
uv run src/cli/main.py env add dev http://localhost:8000
uv run src/cli/main.py auth login --token
uv run src/cli/main.py init
```

### 2. Verify Setup

```bash
# Check health
uv run src/cli/main.py health

# View board
uv run src/cli/main.py board
```

That's it! No additional configuration needed.

## Available Slash Commands

Claude Code comes with several slash commands in `.claude/commands/`:

### `/anyt-next`
Select and work on the next task.

**What it does:**
1. Lists available tasks
2. Suggests best task based on priority/dependencies
3. Helps you pick and start working on it

**Usage:**
```
User: /anyt-next

Claude: "Let me check your tasks...

I recommend DEV-42 (Implement OAuth callback) because:
- Highest priority (2)
- Status: todo (ready to work on)
- No blocking dependencies
- Unblocks 2 other tasks

Would you like to work on this?"
```

### `/anyt-active`
Show the currently active task.

**Usage:**
```
User: /anyt-active

Claude: "You're currently working on DEV-42 (Implement OAuth callback).
What would you like me to help with?"
```

### `/anyt-create`
Create a new task interactively.

**Usage:**
```
User: /anyt-create

Claude: "I'll help you create a task. What's the title?"
User: "Add Redis caching"
Claude: "What priority? (0=normal, 1=high, 2=urgent)"
...
Claude creates task and offers to start working on it.
```

### `/anyt-board`
Show the Kanban board.

**Usage:**
```
User: /anyt-board

Claude: Shows board and summarizes:
"You have 5 tasks in progress, 12 in backlog, 3 done today."
```

## Workflow Examples

### Example 1: Daily Standup

```
User: /anyt-board

Claude: Shows board overview

User: /anyt-next

Claude: Suggests top priority task

User: "Let's do it"

Claude: Picks task and starts helping implement it
```

### Example 2: User Has an Idea

```
User: "I want to add rate limiting to the API"

Claude: "That's a great idea! Let me create a task for that."

Runs: /anyt-create internally or asks:
"Should I create a task for this? What priority?"

User: "Yes, high priority"

Claude creates task, picks it, and starts implementing.
```

### Example 3: Checking Progress

```
User: "What am I working on?"

Claude runs: /anyt-active

Shows current task details and offers help.
```

### Example 4: Marking Tasks Complete

When you're done with a task:

```
User: "I'm done with this task"

Claude: "Great! Let me mark it as complete."

Runs: uv run src/cli/main.py task done

Claude: "✓ Marked DEV-42 as done. Run /anyt-next to see what's next!"
```

## Advanced: Using CLI Directly

You can also use Claude Code's bash tool to run any CLI command:

```
User: "Show me all high priority tasks"

Claude runs:
uv run src/cli/main.py task list --priority-gte 1 --json

Parses output and presents nicely formatted results.
```

## Troubleshooting

### Backend Not Running
```
Error: Connection refused

Fix: Start backend: make dev
```

### No Workspace Configured
```
Error: Not in a workspace directory

Fix: Run: uv run src/cli/main.py init
```

### Slash Command Not Found
```
Fix: Make sure .claude/commands/ directory exists
Check files are .md format
Restart Claude Code if needed
```

## Tips & Best Practices

1. **Use `/anyt-next` daily** - Start each session by seeing what to work on
2. **Create tasks as you go** - When you think of something, use `/anyt-create`
3. **Update progress** - Ask Claude to update task descriptions as you work
4. **Mark done promptly** - Don't forget to mark tasks complete
5. **Check the board** - Use `/anyt-board` to see overall progress

## vs. MCP Integration

This CLI-based approach is simpler and requires no MCP server setup. For more advanced integration (real-time updates, auto-task creation), see MCP integration guide (coming in Phase 2).

**Advantages of CLI approach:**
- ✅ Simple setup (no MCP configuration)
- ✅ Works immediately
- ✅ Easy to debug (just run CLI commands manually)
- ✅ Portable (works anywhere uv/CLI is installed)

**When to use MCP:**
- You want automatic task creation as Claude works
- You need real-time resource updates
- You want Claude to proactively track progress
```

## Events

### 2025-10-18 - Started work
- Moved task from backlog to active
- Updated status to "In Progress"
- All dependencies (T7-27, T7-29) are completed
- Creating new git branch for this task
- Beginning documentation creation

### 2025-10-18 - Documentation completed
- Created comprehensive `docs/CLAUDE_CODE_INTEGRATION.md` guide (500+ lines)
- Documented all 4 main slash commands: /anyt-next, /anyt-active, /anyt-create, /anyt-board
- Added setup instructions for backend + CLI configuration
- Included 9 workflow examples covering daily standup, task creation, completion, etc.
- Added comprehensive troubleshooting section with 6 common issues
- Included tips & best practices section (10 tips)
- Compared CLI-based vs MCP integration approaches
- Updated README.md with new "Claude Code Integration" section
- Updated documentation links in README.md
- All acceptance criteria met ✓
- Task status updated to "Completed"

## Related Files
- `docs/CLAUDE_CODE_INTEGRATION.md` - New documentation file
- `.claude/commands/*.md` - Slash command files
- `README.md` - Update with integration section
