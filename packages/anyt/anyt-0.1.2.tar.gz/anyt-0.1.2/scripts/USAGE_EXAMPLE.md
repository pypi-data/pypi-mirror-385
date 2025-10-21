# Claude Task Worker - Usage Example

## Updated Implementation

The scripts now use **Claude Code CLI in non-interactive mode** to actually execute tasks, not just provide suggestions.

## Command Used

```bash
claude -p "detailed task prompt" --dangerously-skip-permissions
```

This allows Claude to:
- ✅ Actually make code changes
- ✅ Run commands and tests
- ✅ Complete tasks fully automatically
- ✅ Skip permission prompts for automation

## Example Workflow

### Step 1: Check for tasks
```bash
$ uv run anyt task suggest --status todo

Top 1 Recommended Task:

1. DE-3 - Subtitle AnyT in landing page [Priority: 0]
   Reason: Ready to work on, No dependencies
   Status: todo
```

### Step 2: Run the simple worker
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
Description: Add a descriptive subtitle below the main AnyT heading on the landing page
```

### Step 3: Confirm work on task
```
Do you want to work on this task? (y/n): y

Updating task status to 'inprogress'...
✓ Task marked as in progress
Adding start note to task...
```

**Note**: A timestamped note is added to the task:
```
🤖 Claude started working on this task
```

### Step 4: Claude executes the task
```
=== Calling Claude AI to work on task ===

Executing task with Claude...

[Claude Code output:]
I'll help you add a subtitle to the AnyT landing page.

Let me first locate the landing page component...
[Reading files...]
[Making changes to src/pages/Landing.tsx...]
[Testing the changes...]

✓ Added subtitle "AI-native task management for teams" below the main heading
✓ Styled with proper typography and spacing
✓ Verified responsive design
✓ Changes committed

Task completed successfully!

Adding completion note to task...
```

**Note**: Another timestamped note is added to the task with Claude's work summary:
```
✅ Claude completed work: I'll help you add a subtitle to the AnyT landing page...
```

### Step 5: Mark as done
```
=========================

Mark task as done? (y/n): y
✓ Task DE-3 marked as done!
```

### Step 6: View task timeline
```bash
# You can now view the complete task history with notes
$ uv run anyt task show DE-3

Task: DE-3
Title: Subtitle AnyT in landing page
Status: done

Events:
[2025-10-19 14:30:17] 🤖 Claude started working on this task
[2025-10-19 14:30:45] ✅ Claude completed work: I'll help you add a subtitle to the AnyT landing page. Let me first locate the landing page component... [Added subtitle "AI-native task management for teams" below the main heading, Styled with proper typography and spacing, Verified responsive design, Changes committed]
```

## Automated Mode

For continuous operation:

```bash
$ ./scripts/claude_task_worker.sh

[2025-10-19 14:30:15] Claude Task Worker started
[2025-10-19 14:30:15] Polling interval: 5s
[2025-10-19 14:30:15] Log file: claude_task_worker.log

[2025-10-19 14:30:15] Checking for available tasks...
[2025-10-19 14:30:16] ✓ Found task: DE-3
[2025-10-19 14:30:16] Processing task: DE-3
[2025-10-19 14:30:17] ✓ Task DE-3 marked as in progress
[2025-10-19 14:30:17] Executing task with Claude CLI (non-interactive mode)...

[Claude makes changes automatically...]

[2025-10-19 14:30:45] ✓ Task DE-3 completed and marked as done!
[2025-10-19 14:30:45] Checking for available tasks...
[2025-10-19 14:30:46] ✓ Found task: DE-4
[2025-10-19 14:30:47] Processing task: DE-4
...
```

## Installation

### 1. Install Claude Code CLI
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Verify installation
```bash
claude --version
```

### 3. Setup AnyTask CLI
```bash
uv run anyt --version
uv run anyt auth login --token
uv run anyt init
```

### 4. Run the worker
```bash
# Interactive mode (recommended for first time)
./scripts/claude_task_worker_simple.sh

# Automated mode
./scripts/claude_task_worker.sh
```

## How It's Different Now

### Before (API-based suggestions)
```bash
# Old approach: Claude just provided suggestions via API
curl -X POST https://api.anthropic.com/v1/messages \
  -d '{"model": "claude-3-5-sonnet", "messages": [...]}'

# Output: Just text suggestions, no actual work done
{
  "content": "To complete this task, you should:
  1. Edit the Landing.tsx file
  2. Add a subtitle element
  3. Style it appropriately..."
}
```

### After (CLI-based execution)
```bash
# New approach: Claude actually does the work
claude -p "Complete this task: Add subtitle to landing page" \
  --dangerously-skip-permissions

# Claude:
# - Reads the codebase
# - Makes actual code changes
# - Tests the changes
# - Completes the task fully
```

## Security Note

⚠️ **Important**: The `--dangerously-skip-permissions` flag allows Claude to make changes without asking for approval. This is designed for automation but should be used carefully.

**Recommendations**:
1. Start with the **simple interactive mode** to review Claude's work
2. Use **automated mode** only in controlled environments
3. Monitor the logs regularly
4. Review commits made by Claude
5. Use in a development environment first

## Task Flow Diagram

```
┌─────────────────────────────────────────┐
│  anyt task suggest --status todo       │
│  → Get task DE-3                        │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  anyt task show DE-3                    │
│  → Fetch detailed task description      │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  anyt task edit --status inprogress DE-3│
│  → Mark task as being worked on         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  claude -p "$task_prompt" \             │
│    --dangerously-skip-permissions       │
│  → Claude executes the task             │
│  → Makes code changes                   │
│  → Runs tests                           │
│  → Completes work                       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  anyt task done DE-3                    │
│  → Mark task as complete                │
└─────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Loop: Continue to next task            │
└─────────────────────────────────────────┘
```

## Logs

The automated worker creates detailed logs:

```bash
# View live logs
tail -f claude_task_worker.log

# Example log output:
[2025-10-19 14:30:15] Claude Task Worker started
[2025-10-19 14:30:16] ✓ Found task: DE-3
[2025-10-19 14:30:17] Fetching task details...
[2025-10-19 14:30:17] ✓ Task DE-3 marked as in progress
[2025-10-19 14:30:17] Executing task with Claude CLI (non-interactive mode)...
[2025-10-19 14:30:45] ✓ Task DE-3 completed and marked as done!
[2025-10-19 14:30:45] ✓ Successfully completed task DE-3
```

## Troubleshooting

### Claude command not found
```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# If you already have it, update it
npm update -g @anthropic-ai/claude-code
```

### Raw mode error
This has been fixed! The script now uses `-p` flag instead of piping to stdin.

### No tasks available
```bash
# Create a test task
uv run anyt task add "Test task for Claude" --status todo --project 1

# Verify task exists
uv run anyt task list --status todo
```

## Next Steps

1. **Test with simple mode**: Run `./scripts/claude_task_worker_simple.sh` first
2. **Review Claude's work**: Check the code changes Claude makes
3. **Monitor logs**: Watch `claude_task_worker.log` for issues
4. **Scale up**: Once comfortable, use automated mode for continuous operation
5. **Integrate with CI/CD**: Set up as a background service for automated task completion

---

**Note**: This is a powerful automation tool. Start small, monitor closely, and scale gradually!
