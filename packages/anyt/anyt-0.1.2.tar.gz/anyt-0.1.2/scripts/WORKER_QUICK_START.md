# Claude Task Worker - Quick Start Guide

Get started with the Claude Task Worker scripts in 5 minutes.

## Prerequisites

Install required tools:

```bash
# 1. Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 3. Verify installations
uv --version
claude --version
```

## Setup

### 1. Configure AnyTask CLI

```bash
# Login to AnyTask
uv run anyt auth login --agent-key

# Initialize workspace in your project
cd /path/to/your/project
uv run anyt init

# Verify configuration
uv run anyt auth whoami
```

### 2. Create Test Tasks

```bash
# Create a few test tasks
uv run anyt task add "Update README" --status todo --priority 0
uv run anyt task add "Fix typo in config" --status todo --priority 1
uv run anyt task add "Add unit tests" --status todo --priority 0

# Verify tasks
uv run anyt task list --status todo
```

## Running the Worker

### Option 1: Enhanced Worker (Recommended)

Full-featured with git commits and task dependencies:

```bash
# Run with defaults
./scripts/claude_task_worker_enhanced.sh

# Run with custom settings
AUTO_COMMIT=true \
CREATE_FOLLOWUP_TASKS=true \
POLL_INTERVAL=10 \
./scripts/claude_task_worker_enhanced.sh
```

**Features:**
- ✅ Auto-commits code changes
- ✅ Creates follow-up tasks
- ✅ Creates blocking tasks
- ✅ Manages dependencies
- ✅ Comprehensive logging

### Option 2: Standard Worker

Auto-commit without follow-up task creation:

```bash
./scripts/claude_task_worker.sh
```

**Features:**
- ✅ Auto-commits code changes
- ✅ Continuous task processing
- ✅ Task status management

### Option 3: Interactive Worker

Manual approval for each step:

```bash
./scripts/claude_task_worker_simple.sh
```

**Features:**
- ✅ Interactive prompts
- ✅ Manual commit approval
- ✅ Single task processing

## Example Workflow

### 1. Start the Enhanced Worker

```bash
# In your project directory
cd /path/to/your/project

# Start the worker
./scripts/claude_task_worker_enhanced.sh
```

### 2. Worker Output

```
[2025-10-20 15:30:00] Claude Task Worker (Enhanced) started
[2025-10-20 15:30:00] Configuration:
[2025-10-20 15:30:00]   - Poll interval: 5s
[2025-10-20 15:30:00]   - Log file: claude_task_worker.log
[2025-10-20 15:30:00]   - Auto-commit: true
[2025-10-20 15:30:00]   - Commit prefix: feat
[2025-10-20 15:30:00]   - Create follow-up tasks: true

[2025-10-20 15:30:01] Checking for available tasks...
[2025-10-20 15:30:02] ✓ Found task: DEV-42
[2025-10-20 15:30:02] Processing task: DEV-42
[2025-10-20 15:30:02] Fetching task details...
[2025-10-20 15:30:03] Updating task status to 'inprogress'...
[2025-10-20 15:30:03] ✓ Task DEV-42 marked as in progress
[2025-10-20 15:30:03] Working on task with Claude...

=== Claude's Response ===
I've completed the README update by adding installation instructions
and usage examples.

Changes made:
- Added installation section
- Added usage examples
- Fixed formatting issues

FOLLOW_UP_TASK: Add screenshots to README
FOLLOW_UP_TASK: Update CHANGELOG.md with new features

Task completed successfully!
=========================

[2025-10-20 15:30:25] Checking for code changes to commit...
[2025-10-20 15:30:25] Committing changes for task DEV-42...
[2025-10-20 15:30:25] Staged all changes
[2025-10-20 15:30:26] ✓ Committed changes
[2025-10-20 15:30:26] Commit hash: a1b2c3d
[2025-10-20 15:30:26] ℹ Checking for follow-up or blocking tasks...
[2025-10-20 15:30:26] ℹ Creating follow-up task: Add screenshots to README
[2025-10-20 15:30:27] ✓ Created follow-up task: DEV-43 - Add screenshots to README
[2025-10-20 15:30:27] ✓ Added dependency: DEV-43 depends on DEV-42
[2025-10-20 15:30:27] ℹ Creating follow-up task: Update CHANGELOG.md with new features
[2025-10-20 15:30:28] ✓ Created follow-up task: DEV-44 - Update CHANGELOG.md with new features
[2025-10-20 15:30:28] ✓ Added dependency: DEV-44 depends on DEV-42
[2025-10-20 15:30:28] Marking task as done...
[2025-10-20 15:30:29] ✓ Task DEV-42 completed and marked as done!
[2025-10-20 15:30:29] ✓ Successfully completed task DEV-42
[2025-10-20 15:30:29] Checking for available tasks...
```

### 3. Verify Results

```bash
# Check git commits
git log --oneline -5

# Output:
# a1b2c3d feat: DEV-42 - Update README
# ...

# Check created tasks
uv run anyt task list --status todo

# Output:
# DEV-43 - Add screenshots to README [depends on DEV-42]
# DEV-44 - Update CHANGELOG.md [depends on DEV-42]

# Check task history
uv run anyt task show DEV-42

# Output shows:
# - 🤖 Claude Task Worker started working on this task
# - ✅ Claude completed work: I've completed the README...
# - 📝 Committed changes: a1b2c3d
# - 📌 Created follow-up task: DEV-43
# - 📌 Created follow-up task: DEV-44
```

## Configuration Options

### Enhanced Worker

```bash
# Customize behavior with environment variables

# Poll every 10 seconds instead of 5
export POLL_INTERVAL=10

# Use different log file
export LOG_FILE="my_worker.log"

# Disable auto-commit
export AUTO_COMMIT=false

# Use different commit prefix
export COMMIT_PREFIX=fix  # or docs, refactor, etc.

# Disable follow-up task creation
export CREATE_FOLLOWUP_TASKS=false

# Run worker with config
./scripts/claude_task_worker_enhanced.sh
```

### Standard Worker

Edit the script directly:

```bash
# Edit configuration at top of script
vim scripts/claude_task_worker.sh

# Change these lines:
POLL_INTERVAL=10
LOG_FILE="custom_worker.log"
```

## Claude Response Format

To leverage follow-up/blocking task features, Claude should format responses like this:

```
I've completed the task successfully.

Summary of changes:
- Implemented feature X
- Updated documentation
- Added tests

FOLLOW_UP_TASK: Add integration tests for feature X
FOLLOW_UP_TASK: Update API documentation

BLOCKING_TASK: Database migration needs to run first

All done!
```

## Monitoring

### View Logs in Real-Time

```bash
# Watch worker logs
tail -f claude_task_worker.log

# Filter for errors
grep "✗" claude_task_worker.log

# See completed tasks
grep "completed and marked as done" claude_task_worker.log
```

### Check Task Progress

```bash
# List all tasks
uv run anyt task list

# Show task board
uv run anyt board

# View task dependencies
uv run anyt graph --full
```

## Stopping the Worker

Press `Ctrl+C` to gracefully stop:

```
^C
[2025-10-20 15:45:00] Shutting down Claude Task Worker...
```

## Common Issues

### "Claude CLI not found"

```bash
# Install Claude CLI
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

### "No tasks available"

```bash
# Check task status
uv run anyt task list --status todo

# Create new task
uv run anyt task add "Test task" --status todo
```

### "Not in a git repository"

```bash
# Initialize git repo
git init
git add .
git commit -m "Initial commit"

# Then run worker again
```

### "Failed to update task status"

```bash
# Verify authentication
uv run anyt auth whoami

# Re-login if needed
uv run anyt auth login --agent-key
```

## Advanced Usage

### Run as Background Service

```bash
# Start in background
nohup ./scripts/claude_task_worker_enhanced.sh > worker.out 2>&1 &

# Get process ID
ps aux | grep claude_task_worker

# Stop background worker
pkill -f claude_task_worker_enhanced.sh
```

### Filter Tasks by Project

Modify the script to filter by project:

```bash
# Edit line ~184 in claude_task_worker_enhanced.sh
# Change:
local suggest_output=$(uv run anyt task suggest --status todo 2>&1)

# To:
local suggest_output=$(uv run anyt task suggest --status todo --project 1 2>&1)
```

### Use with tmux

```bash
# Create tmux session
tmux new -s claude-worker

# Run worker
./scripts/claude_task_worker_enhanced.sh

# Detach: Ctrl+B then D
# Reattach: tmux attach -t claude-worker
```

## Next Steps

1. **Customize prompts**: Edit the prompt in `work_on_task_with_claude()` function
2. **Add filters**: Modify task selection logic to filter by labels, priority, etc.
3. **Integrate CI/CD**: Use worker in CI pipeline for automated task processing
4. **Monitor metrics**: Track completion rates, time per task, etc.
5. **Scale up**: Run multiple workers for different projects

## Support

- **Full documentation**: See `README_TASK_WORKER.md`
- **CLI reference**: See `CLI_COMPLETE_REFERENCE.md`
- **Issues**: Check worker logs at `claude_task_worker.log`
- **Questions**: Open GitHub issue

## Quick Reference

```bash
# Enhanced worker (full features)
./scripts/claude_task_worker_enhanced.sh

# Standard worker (auto-commit only)
./scripts/claude_task_worker.sh

# Interactive worker
./scripts/claude_task_worker_simple.sh

# View logs
tail -f claude_task_worker.log

# List tasks
uv run anyt task list --status todo

# Stop worker
Ctrl+C
```

Happy task processing! 🤖
