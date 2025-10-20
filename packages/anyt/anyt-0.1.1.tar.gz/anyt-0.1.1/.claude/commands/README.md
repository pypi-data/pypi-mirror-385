# Claude Code Slash Commands for AnyTask

This directory contains slash commands for integrating AnyTask with Claude Code.

## Available Commands

### `/anyt-next` - Select Next Task ⭐ Most Used
Select and work on the next highest-priority task.

**Usage:** Just type `/anyt-next` in Claude Code

**What it does:**
1. Lists available tasks
2. Suggests best task based on priority/dependencies
3. Helps you pick and start working on it

---

### `/anyt-active` - Show Active Task
Display details about the currently active task.

**Usage:** `/anyt-active`

**What it does:**
- Shows current task details
- Offers to help with the task

---

### `/anyt-create` - Create New Task
Create a new task interactively.

**Usage:** `/anyt-create`

**What it does:**
- Guides you through task creation
- Sets title, priority, labels, etc.
- Offers to start working on it

---

### `/anyt-board` - Show Kanban Board
Display the task board with all tasks by status.

**Usage:** `/anyt-board`

**What it does:**
- Shows Kanban board view
- Summarizes tasks by status
- Provides overview of work

---

## How to Use

1. **Start your day:**
   ```
   User: /anyt-board
   → See what's in progress

   User: /anyt-next
   → Get suggestion for what to work on
   ```

2. **During work:**
   ```
   User: /anyt-active
   → Check current task

   User: "I'm done"
   → Claude marks task complete
   ```

3. **Quick task creation:**
   ```
   User: /anyt-create
   → Create task interactively
   ```

## Requirements

- Backend must be running: `make dev`
- CLI must be configured: `uv run src/cli/main.py init`
- Must be in workspace directory

## Behind the Scenes

These commands run CLI commands via bash:
- `uv run src/cli/main.py task list --json`
- `uv run src/cli/main.py task suggest --json`
- `uv run src/cli/main.py task pick <ID>`
- etc.

Claude parses the JSON output and presents it nicely!

## Troubleshooting

**Slash command not found:**
- Check this directory exists: `.claude/commands/`
- Files must be `.md` format
- Try restarting Claude Code

**Commands fail:**
- Make sure backend is running: `make dev`
- Check CLI is configured: `uv run src/cli/main.py health`
- Verify you're in workspace directory

**No tasks shown:**
- Create some tasks first: `/anyt-create`
- Or migrate existing tasks: `python scripts/migrate_tasks_to_db.py`

## Learn More

- [Integration Plan](../docs/CLAUDE_CODE_MIGRATION_PLAN.md)
- [Ticket Summary](../.anyt/tasks/CLAUDE_CODE_INTEGRATION_TICKETS_CLI.md)
- [CLI Usage Guide](../docs/CLI_USAGE.md)
