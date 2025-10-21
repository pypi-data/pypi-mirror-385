# Claude Task Worker - Quick Start Guide

## What You Got

I've created two versions of the Claude Task Worker script:

### 1. **Automated Worker** (`claude_task_worker.sh`)
- 🤖 Fully automated
- 🔄 Runs continuously
- ⏱️ Polls every 5 seconds
- 📝 Comprehensive logging
- **Best for**: Unattended task processing

### 2. **Simple Interactive** (`claude_task_worker_simple.sh`)
- 👤 Interactive mode
- ✅ Manual approval required
- 🎯 Processes one task at a time
- **Best for**: Testing and manual oversight

## Quick Setup

### 1. Install Prerequisites

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install jq (for JSON parsing)
brew install jq  # macOS
# or
sudo apt-get install jq  # Linux
```

### 2. Setup AnyTask CLI

```bash
# Verify installation
uv run anyt --version

# Login
uv run anyt auth login --token

# Initialize workspace
cd /path/to/your/project
uv run anyt init
```

### 3. Setup Claude CLI

**Install Claude Code CLI** (Required)
```bash
npm install -g @anthropic-ai/claude-code
```

**Verify installation**
```bash
claude --version
```

**Note**: The script uses Claude in non-interactive mode with `--dangerously-skip-permissions` to automatically execute tasks.

## Usage Examples

### Run Simple Interactive Mode

Perfect for first-time use or when you want control:

```bash
./scripts/claude_task_worker_simple.sh
```

**What happens:**
1. Shows you the next suggested task
2. Asks if you want to work on it
3. Marks it as "in progress"
4. Calls Claude to analyze the task
5. Shows Claude's recommendations
6. Asks if you want to mark it done

### Run Automated Mode

For continuous task processing:

```bash
./scripts/claude_task_worker.sh
```

**What happens:**
1. Continuously polls for tasks (every 5 seconds)
2. Automatically picks and processes tasks
3. Sends each task to Claude
4. Marks tasks as done automatically
5. Logs everything to `claude_task_worker.log`

**To stop:** Press `Ctrl+C`

### Run in Background

```bash
# Start in background
nohup ./scripts/claude_task_worker.sh > worker.out 2>&1 &

# View logs
tail -f claude_task_worker.log

# Stop it
pkill -f claude_task_worker.sh
```

## Workflow Overview

```
┌─────────────────────────────────────────────────────┐
│ Your AnyTask Board                                  │
│                                                     │
│ TODO:                                               │
│ - DE-3: Subtitle AnyT in landing page              │
│ - DE-4: Add contact form                           │
│ - DE-5: Update footer links                        │
└─────────────────────────────────────────────────────┘
                      │
                      │ uv run anyt task suggest --status todo
                      ▼
┌─────────────────────────────────────────────────────┐
│ Script picks: DE-3                                  │
└─────────────────────────────────────────────────────┘
                      │
                      │ uv run anyt task show DE-3
                      ▼
┌─────────────────────────────────────────────────────┐
│ Get task details                                    │
└─────────────────────────────────────────────────────┘
                      │
                      │ uv run anyt task edit --status inprogress DE-3
                      ▼
┌─────────────────────────────────────────────────────┐
│ Mark as IN PROGRESS                                 │
└─────────────────────────────────────────────────────┘
                      │
                      │ Send to Claude AI
                      ▼
┌─────────────────────────────────────────────────────┐
│ Claude analyzes and provides:                       │
│ - Summary of what needs to be done                  │
│ - Step-by-step approach                            │
│ - Code changes required                             │
└─────────────────────────────────────────────────────┘
                      │
                      │ uv run anyt task done DE-3
                      ▼
┌─────────────────────────────────────────────────────┐
│ Mark as DONE ✓                                      │
└─────────────────────────────────────────────────────┘
                      │
                      │ Continue to next task...
                      ▼
```

## Configuration

### Change Poll Interval

Edit `claude_task_worker.sh`:

```bash
# Change from 5 seconds to 10 seconds
POLL_INTERVAL=10
```

### Change Claude Model

Edit the API call in the script:

```bash
# From:
"model": "claude-3-5-sonnet-20241022"

# To:
"model": "claude-3-opus-20240229"
```

### Filter Tasks by Project

Modify the suggest command:

```bash
# From:
uv run anyt task suggest --status todo

# To:
uv run anyt task suggest --status todo --project 1
```

## Commands Reference

### Essential AnyTask Commands

```bash
# View available tasks
uv run anyt task list --status todo

# Get task suggestions (sorted by priority)
uv run anyt task suggest --status todo

# Show task details
uv run anyt task show DE-3

# Update task status
uv run anyt task edit --status inprogress DE-3

# Mark task as done
uv run anyt task done DE-3

# View board
uv run anyt board
```

### Monitoring

```bash
# Watch logs in real-time
tail -f claude_task_worker.log

# Count completed tasks
grep "marked as done" claude_task_worker.log | wc -l

# View errors
grep "✗" claude_task_worker.log

# View current tasks
uv run anyt task list --status inprogress
```

## Troubleshooting

### "No tasks available"

```bash
# Check if there are tasks
uv run anyt task list --status todo

# Create a test task
uv run anyt task add "Test task" --status todo --project 1
```

### "Claude CLI not found"

```bash
# Install claude CLI
pip install claude-cli

# Or set API key
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Failed to update task status"

```bash
# Check authentication
uv run anyt auth whoami

# Verify task exists
uv run anyt task show DE-3

# Check workspace
uv run anyt workspace list
```

### Script won't start

```bash
# Make executable
chmod +x scripts/claude_task_worker.sh

# Check uv is installed
which uv

# Run with bash explicitly
bash scripts/claude_task_worker.sh
```

## Tips

1. **Start with simple mode** to understand the workflow
2. **Review Claude's output** before marking tasks done
3. **Monitor logs** when running automated mode
4. **Use filters** to focus on specific project tasks
5. **Stop and restart** the worker when updating task priorities

## Example Session

```bash
$ ./scripts/claude_task_worker_simple.sh

=== Claude Task Worker (Simple Mode) ===

Checking for available tasks...
Found task: DE-3

=== Task Details ===
Task: DE-3
Title: Subtitle AnyT in landing page
Status: todo
Priority: 0
Description: Add a descriptive subtitle below the main AnyT heading

Do you want to work on this task? (y/n): y

Updating task status to 'inprogress'...
✓ Task marked as in progress

=== Calling Claude AI ===

Summary:
Add a subtitle element to the landing page that describes AnyT's purpose.

Steps:
1. Locate the landing page component (likely in src/pages/Landing.tsx)
2. Add a subtitle element below the main heading
3. Style appropriately with existing design system
4. Ensure responsive design

Code changes:
- Update Landing.tsx with subtitle text
- Add CSS/Tailwind classes for styling
- Test on mobile and desktop views

=========================

Mark task as done? (y/n): y
✓ Task DE-3 marked as done!
```

## Next Steps

1. Try the simple mode first: `./scripts/claude_task_worker_simple.sh`
2. Review the output and Claude's suggestions
3. When comfortable, try automated mode: `./scripts/claude_task_worker.sh`
4. Customize for your workflow
5. Monitor and iterate!

## Documentation

- Full documentation: `scripts/README_TASK_WORKER.md`
- AnyTask CLI usage: `docs/CLI_USAGE.md`
- Questions? Check the main README or open an issue

---

**Happy task automation! 🤖✨**
