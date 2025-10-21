# Claude Task Worker

Automated task processing scripts that continuously poll AnyTask for TODO tasks, use Claude AI to work on them, commit changes, and mark tasks complete.

## Available Scripts

### 1. `claude_task_worker_enhanced.sh` (Recommended)
Full-featured worker with git commits, follow-up tasks, and dependency management.

### 2. `claude_task_worker.sh`
Standard worker with git auto-commit functionality.

### 3. `claude_task_worker_simple.sh`
Interactive mode with manual approval and commit prompts.

## Features

### Core Features (All Scripts)
- 🔄 Continuous polling for available tasks (configurable interval)
- 🤖 Claude AI integration for task execution
- 📊 Automatic task status management (todo → inprogress → done)
- 📝 Comprehensive logging with timestamped task notes
- 🎯 Smart task selection using `anyt task suggest`
- ⚡ Immediate continuation after task completion
- 📋 Automatic task notes tracking what Claude did
- 🕐 Full audit trail of Claude's work on each task

### Enhanced Features (claude_task_worker_enhanced.sh)
- 🔀 **Git Auto-Commit**: Automatically commits code changes with structured commit messages
- 📌 **Follow-up Tasks**: Creates related tasks that depend on completed work
- 🚧 **Blocking Tasks**: Identifies and creates prerequisite tasks
- 🔗 **Dependency Management**: Automatically links tasks with dependencies
- ⚙️ **Configurable**: Environment variables for customization

### Standard Features (claude_task_worker.sh)
- 🔀 **Git Auto-Commit**: Automatically commits code changes with structured commit messages

### Interactive Features (claude_task_worker_simple.sh)
- 🔀 **Git Commit Prompt**: Interactive prompt for committing changes

## Prerequisites

1. **uv** - Python package manager
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **AnyTask CLI** installed and configured
   ```bash
   uv run anyt --version
   uv run anyt auth login
   uv run anyt init
   ```

3. **Claude Code CLI** (required)

   ```bash
   # Install Claude Code CLI
   npm install -g @anthropic-ai/claude-code

   # Verify installation
   claude --version
   ```

   **Note**: The script uses Claude CLI in non-interactive mode with the `-p` flag and `--dangerously-skip-permissions` to automatically execute tasks and make code changes.

## Usage

### Enhanced Worker (Recommended)

```bash
# Start the enhanced task worker with all features
./scripts/claude_task_worker_enhanced.sh

# With custom configuration
POLL_INTERVAL=10 AUTO_COMMIT=true CREATE_FOLLOWUP_TASKS=true ./scripts/claude_task_worker_enhanced.sh
```

The enhanced script will:
1. Check for tasks every 5 seconds (configurable)
2. Pick the first task from suggestions
3. Show task details
4. Update status to "inprogress"
5. Send task to Claude for processing
6. Display Claude's response
7. **Automatically commit code changes to git**
8. **Parse and create follow-up/blocking tasks**
9. **Add task dependencies**
10. Mark task as done
11. Repeat

### Standard Worker

```bash
# Start the standard worker with git auto-commit
./scripts/claude_task_worker.sh
```

Same as enhanced but without follow-up task creation.

### Simple Interactive Worker

```bash
# Start the interactive worker
./scripts/claude_task_worker_simple.sh
```

Interactive mode - prompts for each action.

### Configuration

#### Enhanced Worker Environment Variables

```bash
# Poll interval in seconds (default: 5)
export POLL_INTERVAL=10

# Log file location (default: claude_task_worker.log)
export LOG_FILE="worker.log"

# Enable/disable auto-commit (default: true)
export AUTO_COMMIT=true

# Git commit type prefix (default: feat)
# Options: feat, fix, docs, style, refactor, test, chore
export COMMIT_PREFIX=feat

# Enable/disable follow-up task creation (default: true)
export CREATE_FOLLOWUP_TASKS=true
```

#### Standard Worker Configuration

Edit the script to customize:

```bash
# Poll interval in seconds (default: 5)
POLL_INTERVAL=5

# Log file location (default: claude_task_worker.log)
LOG_FILE="claude_task_worker.log"
```

### Environment Variables

```bash
# AnyTask configuration (optional overrides)
export ANYT_ENV="dev"
export ANYT_API_URL="http://localhost:8000"
```

**Note**: Claude Code CLI uses your configured authentication automatically. No need to set API keys in environment variables.

### Example Output

```
[2025-10-19 14:30:15] Claude Task Worker started
[2025-10-19 14:30:15] Polling interval: 5s
[2025-10-19 14:30:15] Log file: claude_task_worker.log

[2025-10-19 14:30:15] Checking for available tasks...
[2025-10-19 14:30:16] ✓ Found task: DE-3
[2025-10-19 14:30:16] Processing task: DE-3
[2025-10-19 14:30:16] Fetching task details...
[2025-10-19 14:30:17] Updating task status to 'inprogress'...
[2025-10-19 14:30:17] ✓ Task DE-3 marked as in progress
[2025-10-19 14:30:17] Working on task with Claude...

=== Claude's Response ===
I'll help you add a subtitle to the AnyT landing page.

Summary:
- Add a descriptive subtitle below the main heading
- Ensure proper styling and responsiveness
- Update landing page component

Steps to complete:
1. Identify landing page component location
2. Add subtitle text element
3. Style the subtitle appropriately
4. Test responsiveness

The task is now complete!
=========================

[2025-10-19 14:30:25] Marking task as done...
[2025-10-19 14:30:25] ✓ Task DE-3 completed and marked as done!
[2025-10-19 14:30:25] ✓ Successfully completed task DE-3
[2025-10-19 14:30:25] Checking for available tasks...
```

## How It Works

### Task Selection

The script uses `uv run anyt task suggest --status todo` to get intelligent task recommendations based on:
- Priority weighting
- Dependencies
- Impact on other tasks
- Current status

### Task Processing Flow

```
┌─────────────────────────────────────┐
│  Poll for tasks (every 5s)          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Get suggestions:                   │
│  uv run anyt task suggest --status  │
│  todo                               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Extract first task ID (e.g., DE-3) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Get task details:                  │
│  uv run anyt task show DE-3         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Update status to inprogress:       │
│  uv run anyt task edit --status     │
│  inprogress DE-3                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Send to Claude AI for processing   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Display Claude's response          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Mark as done:                      │
│  uv run anyt task done DE-3         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Continue to next task              │
│  (or wait if no tasks)              │
└─────────────────────────────────────┘
```

### Claude Integration

The script uses **Claude Code CLI in non-interactive mode** to actually execute tasks:

```bash
claude -p "task description and instructions" --dangerously-skip-permissions
```

**Features**:
- 🚀 Non-interactive execution with `-p` flag
- ⚡ Automatic code changes and task completion
- 🔓 `--dangerously-skip-permissions` skips approval prompts
- 🤖 Claude actually performs the work, not just suggests it

**How it works**:
1. Script formats task details into a detailed prompt
2. Calls `claude -p "$prompt" --dangerously-skip-permissions`
3. Claude analyzes the task, makes code changes, and completes the work
4. Script captures output and marks task as done

## Automatic Task Notes

The script automatically adds timestamped notes to tasks using `uv run anyt task note`, creating a complete audit trail of Claude's work:

### Start Note
When Claude begins working on a task:
```bash
uv run anyt task note DE-3 --message "🤖 Claude started working on this task"
```

This adds a timestamped event to the task:
```
[2025-10-19 14:30:17] 🤖 Claude started working on this task
```

### Completion Note
When Claude finishes working on a task:
```bash
uv run anyt task note DE-3 --message "✅ Claude completed work: [summary of changes...]"
```

This adds a completion event with Claude's work summary:
```
[2025-10-19 14:30:45] ✅ Claude completed work: Added subtitle "AI-native task management" to landing page, styled with proper typography, tested responsive design...
```

### Error Note
If Claude encounters an error:
```bash
uv run anyt task note DE-3 --message "❌ Claude encountered an error during execution"
```

### View Task History
After the task is complete, you can view the full timeline:
```bash
$ uv run anyt task show DE-3

Task: DE-3
Title: Subtitle AnyT in landing page
Status: done

Events:
[2025-10-19 14:30:17] 🤖 Claude started working on this task
[2025-10-19 14:30:45] ✅ Claude completed work: I'll help you add a subtitle...
```

This creates a permanent record of:
- When Claude started working
- What Claude did
- When Claude finished
- Any errors encountered

## Logging

All activity is logged to `claude_task_worker.log`:

```bash
# View logs in real-time
tail -f claude_task_worker.log

# Search for errors
grep "✗" claude_task_worker.log

# View completed tasks
grep "completed and marked as done" claude_task_worker.log
```

## Stopping the Worker

Press `Ctrl+C` to gracefully shut down:

```
^C
[2025-10-19 14:35:42] Shutting down Claude Task Worker...
```

## Troubleshooting

### No tasks available

```
[2025-10-19 14:30:15] ⚠ No tasks available. Waiting 5s...
```

**Solution**: Create tasks or check task status filters
```bash
uv run anyt task list --status todo
uv run anyt task add "New task" --status todo --project 1
```

### Claude CLI not found

```
[2025-10-19 14:30:15] ✗ Claude CLI not found
```

**Solution**: Install Claude Code CLI
```bash
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

### Failed to update task status

```
[2025-10-19 14:30:17] ✗ Failed to update task status to inprogress
```

**Solution**: Check authentication and task permissions
```bash
uv run anyt auth whoami
uv run anyt task show DE-3
```

## Advanced Usage

### Run as Background Service

```bash
# Start in background
nohup ./scripts/claude_task_worker.sh > worker.out 2>&1 &

# Check if running
ps aux | grep claude_task_worker

# Stop background worker
pkill -f claude_task_worker.sh
```

### Custom Poll Interval

```bash
# Edit script to change POLL_INTERVAL
sed -i 's/POLL_INTERVAL=5/POLL_INTERVAL=10/' scripts/claude_task_worker.sh
```

### Filter by Project

Modify the script's `uv run anyt task suggest` command:

```bash
# Edit the get task suggestions line
uv run anyt task suggest --status todo --project 1
```

## Integration with Other Tools

### Use with tmux

```bash
# Create new tmux session
tmux new -s claude-worker

# Run worker
./scripts/claude_task_worker.sh

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t claude-worker
```

### Use with systemd (Linux)

Create `/etc/systemd/system/claude-task-worker.service`:

```ini
[Unit]
Description=Claude Task Worker
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/AnyTaskCLI
Environment="ANTHROPIC_API_KEY=sk-ant-..."
ExecStart=/path/to/AnyTaskCLI/scripts/claude_task_worker.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable claude-task-worker
sudo systemctl start claude-task-worker
sudo systemctl status claude-task-worker
```

## Security Notes

- **Never commit API keys** to version control
- Store `ANTHROPIC_API_KEY` in environment variables or secure vault
- Review Claude's responses before marking tasks complete
- Use read-only workspace mode for testing

## Git Commit Integration

All worker scripts now support git commit integration to track code changes.

### Commit Message Format

```
feat: TASK-ID - Task Title

Completed by Claude Task Worker
Task ID: TASK-ID

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Example

```
feat: DE-42 - Add user authentication

Completed by Claude Task Worker
Task ID: DE-42

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit Hash Tracking

After committing, the worker adds a note to the task:
```
📝 Committed changes: a1b2c3d
```

This creates a permanent link between the task and the git commit.

## Follow-up and Blocking Tasks (Enhanced Worker Only)

The enhanced worker can automatically create related tasks based on Claude's analysis.

### Follow-up Tasks

Claude can identify tasks that should be done AFTER the current task completes.

**Format in Claude's response:**
```
FOLLOW_UP_TASK: Add tests for authentication flow
FOLLOW_UP_TASK: Update documentation for auth API
```

**What happens:**
1. Worker creates new tasks with these titles
2. Sets status to "todo"
3. Adds dependency: new task depends on current task
4. Adds note to original task

**Example:**
```
Task DE-42 (Add user authentication) completed
  ↓ Created follow-up tasks:
  - DE-43 (Add tests for authentication flow) depends on DE-42
  - DE-44 (Update documentation for auth API) depends on DE-42
```

### Blocking Tasks

Claude can identify tasks that SHOULD HAVE been completed first.

**Format in Claude's response:**
```
BLOCKING_TASK: Set up database schema for users
BLOCKING_TASK: Configure auth middleware
```

**What happens:**
1. Worker creates new tasks with these titles
2. Sets status to "todo" with high priority
3. Adds note to original task about blocking dependency

**Example:**
```
Task DE-42 (Add user authentication) completed
  ↓ Created blocking tasks (manual review needed):
  - DE-43 (Set up database schema for users) should have been done first
  - DE-44 (Configure auth middleware) should have been done first
```

### Dependency Management

Dependencies are automatically managed using `anyt task dep add`:

```bash
# Follow-up task depends on current task
anyt task dep add DE-43 --on DE-42

# View dependencies
anyt task dep list DE-43
```

## Claude Response Format

To enable follow-up/blocking task creation, Claude should include these markers:

```
I've completed the task by implementing user authentication.

Changes made:
- Added login endpoint
- Implemented JWT token generation
- Created user session management

FOLLOW_UP_TASK: Add tests for authentication flow
FOLLOW_UP_TASK: Update documentation for auth API

BLOCKING_TASK: Set up database schema for users

Task completed successfully!
```

## Limitations

- Enhanced worker creates tasks sequentially (no parallel processing)
- Blocking tasks don't automatically reopen the current task
- Manual review recommended for blocking task dependencies
- Git auto-commit commits ALL changes (use .gitignore appropriately)

## Future Enhancements

- [ ] Parallel task processing
- [ ] Automatic re-ordering of tasks based on dependencies
- [ ] Smart commit message generation from Claude's work summary
- [ ] Web dashboard for monitoring
- [ ] Slack/Discord notifications
- [ ] Task retry logic with exponential backoff
- [ ] Git branch creation per task
- [ ] Pull request creation after task completion

## Contributing

To improve the task worker script:

1. Test changes locally
2. Update this README
3. Submit pull request

## Support

For issues or questions:
- Check logs: `cat claude_task_worker.log`
- Verify CLI: `uv run anyt --version`
- Test Claude: `echo "Hello" | claude`
- Open issue on GitHub

## License

Same as AnyTask CLI project license.
