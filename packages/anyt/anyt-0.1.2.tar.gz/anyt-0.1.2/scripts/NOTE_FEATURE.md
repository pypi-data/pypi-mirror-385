# Automatic Task Notes Feature

## Overview

The Claude Task Worker scripts now automatically add timestamped notes to tasks, creating a complete audit trail of Claude's work. This uses the `uv run anyt task note` command to track:

- ✅ When Claude started working
- ✅ What Claude accomplished
- ✅ When Claude finished
- ✅ Any errors encountered

## How It Works

### 1. Start Note (When Claude Begins)

```bash
uv run anyt task note DE-3 --message "🤖 Claude started working on this task"
```

**Added to task:**
```
Events:
[2025-10-19 14:30:17] 🤖 Claude started working on this task
```

### 2. Completion Note (When Claude Finishes)

```bash
uv run anyt task note DE-3 --message "✅ Claude completed work: Added subtitle 'AI-native task management' to landing page..."
```

**Added to task:**
```
Events:
[2025-10-19 14:30:17] 🤖 Claude started working on this task
[2025-10-19 14:30:45] ✅ Claude completed work: Added subtitle "AI-native task management" to landing page, styled with proper typography, tested responsive design, verified all changes work correctly
```

### 3. Error Note (If Claude Encounters an Error)

```bash
uv run anyt task note DE-3 --message "❌ Claude encountered an error during execution"
```

**Added to task:**
```
Events:
[2025-10-19 14:30:17] 🤖 Claude started working on this task
[2025-10-19 14:30:30] ❌ Claude encountered an error during execution
```

## Viewing Task History

### After Task Completion

```bash
$ uv run anyt task show DE-3
```

**Output:**
```
┌─────────────────────────────────────────────────────────────┐
│ Task Details: DE-3                                          │
├─────────────────────────────────────────────────────────────┤
│ Title:       Subtitle AnyT in landing page                  │
│ Status:      done                                           │
│ Priority:    0                                              │
│ Project:     Development                                    │
│ Created:     2025-10-19 14:00:00                           │
│ Updated:     2025-10-19 14:30:50                           │
└─────────────────────────────────────────────────────────────┘

Description:
Add a descriptive subtitle below the main AnyT heading on the
landing page to better explain what the product does.

Events:
[2025-10-19 14:30:17] 🤖 Claude started working on this task
[2025-10-19 14:30:45] ✅ Claude completed work: I'll help you add a subtitle to the AnyT landing page. Let me first locate the landing page component... Added subtitle "AI-native task management for teams" below the main heading, Styled with proper typography and spacing, Verified responsive design, Changes committed
```

## Benefits

### 📋 Complete Audit Trail
Every task has a full history of Claude's work:
- Start time
- What was changed
- Completion time
- Any issues encountered

### 🔍 Easy Debugging
If something goes wrong, you can see exactly what Claude did:
```bash
uv run anyt task show DE-3
# Review Events section to see what happened
```

### 📊 Progress Tracking
Team members can see when Claude worked on tasks:
```bash
uv run anyt task list --status done
# Each task shows completion notes
```

### 🕐 Timeline Analysis
Understand how long tasks take:
```
[14:30:17] Started
[14:30:45] Completed
Duration: ~28 seconds
```

## Example Session

### Simple Interactive Mode

```bash
$ ./scripts/claude_task_worker_simple.sh

=== Claude Task Worker (Simple Mode) ===

Checking for available tasks...
Found task: DE-3

=== Task Details ===
Task: DE-3
Title: Subtitle AnyT in landing page
Status: todo

Do you want to work on this task? (y/n): y

Updating task status to 'inprogress'...
✓ Task marked as in progress
Adding start note to task...

=== Calling Claude AI to work on task ===

Executing task with Claude...
[Claude's output here...]

Adding completion note to task...

===========================

Mark task as done? (y/n): y
✓ Task DE-3 marked as done!
```

### Automated Mode

```bash
$ ./scripts/claude_task_worker.sh

[2025-10-19 14:30:15] Claude Task Worker started
[2025-10-19 14:30:16] ✓ Found task: DE-3
[2025-10-19 14:30:16] Processing task: DE-3
[2025-10-19 14:30:17] ✓ Task DE-3 marked as in progress
[2025-10-19 14:30:17] Adding start note to task...
[2025-10-19 14:30:17] Start note added
[2025-10-19 14:30:17] Executing task with Claude CLI...
[2025-10-19 14:30:45] Adding completion note to task...
[2025-10-19 14:30:45] Completion note added
[2025-10-19 14:30:45] ✓ Task DE-3 completed and marked as done!
```

## Checking Notes

### View Single Task
```bash
uv run anyt task show DE-3
```

### View All Recent Activity
```bash
# List recently completed tasks
uv run anyt task list --status done --sort updated_at --limit 10

# Show details of each
for task in DE-3 DE-4 DE-5; do
  echo "=== $task ==="
  uv run anyt task show $task | grep -A 10 "Events:"
done
```

### Search Task Notes
```bash
# Find all tasks Claude worked on
uv run anyt task list --status done --json | \
  jq -r '.data[] | select(.description | contains("Claude completed work"))'
```

## Script Implementation

### In `claude_task_worker_simple.sh`

```bash
# Start note
uv run anyt task note "$TASK_ID" --message "🤖 Claude started working on this task"

# Work with Claude
CLAUDE_OUTPUT=$(claude -p "$PROMPT" --dangerously-skip-permissions 2>&1)
CLAUDE_EXIT_CODE=$?

# Completion note
if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
    SUMMARY=$(echo "$CLAUDE_OUTPUT" | head -c 500)
    uv run anyt task note "$TASK_ID" --message "✅ Claude completed work: $SUMMARY"
else
    uv run anyt task note "$TASK_ID" --message "❌ Claude encountered an error during execution"
fi
```

### In `claude_task_worker.sh`

```bash
# Start note
uv run anyt task note "$task_id" --message "🤖 Claude started working on this task (automated worker)"

# Work with Claude
claude_response=$(work_on_task_with_claude "$task_id" "$task_details")
claude_exit_code=$?

# Completion note
if [ $claude_exit_code -eq 0 ]; then
    summary=$(echo "$claude_response" | head -c 500)
    uv run anyt task note "$task_id" --message "✅ Claude completed work: $summary"
else
    uv run anyt task note "$task_id" --message "❌ Claude encountered an error during execution"
fi
```

## Note Format

### Task Note Command
```bash
uv run anyt task note [IDENTIFIER] --message "Your message here"
```

### Arguments
- `IDENTIFIER`: Task identifier (e.g., DE-3) or use active task
- `--message, -m`: Note message to append

### Where Notes Appear
Notes are appended to the task's **Events** section with automatic timestamps:
```
Events:
[2025-10-19 14:30:17] Your message here
```

## Customization

### Change Note Messages

Edit the scripts to customize the note messages:

```bash
# Start note (simple script)
uv run anyt task note "$TASK_ID" --message "🚀 Starting work with Claude"

# Completion note (automated script)
uv run anyt task note "$task_id" --message "✨ Claude finished: $summary"

# Error note
uv run anyt task note "$task_id" --message "🔴 Error occurred during Claude execution"
```

### Adjust Summary Length

Change the number of characters captured from Claude's output:

```bash
# Currently: first 500 characters
summary=$(echo "$claude_response" | head -c 500)

# Increase to 1000 characters for more detail
summary=$(echo "$claude_response" | head -c 1000)

# Or capture first 5 lines instead
summary=$(echo "$claude_response" | head -n 5)
```

## Integration with Other Commands

### Use with Task Suggest
```bash
# Get suggestions, work on them, notes added automatically
uv run anyt task suggest --status todo
./scripts/claude_task_worker_simple.sh
uv run anyt task show DE-3  # See notes
```

### Use with Board View
```bash
# After Claude works on tasks, review on the board
uv run anyt board --status done

# Then check individual task notes
uv run anyt task show DE-3
```

### Use with Timeline
```bash
# View chronological timeline with notes
uv run anyt timeline DE-3

# Shows events including Claude's work notes
```

## Best Practices

1. **Review Notes Regularly**: Check what Claude did on each task
   ```bash
   uv run anyt task list --status done --sort updated_at
   ```

2. **Use Notes for Debugging**: If a task has issues, check the notes
   ```bash
   uv run anyt task show PROBLEMATIC-TASK
   ```

3. **Track Time**: Use timestamps to see how long tasks take
   ```bash
   # Start time in first note
   # Completion time in second note
   # Calculate duration
   ```

4. **Archive Important Notes**: Export task details for record-keeping
   ```bash
   uv run anyt task show DE-3 --json > task-de-3-archive.json
   ```

5. **Share Progress**: Use notes to communicate with team
   ```bash
   # Team members can see what Claude did
   uv run anyt task show DE-3
   ```

## Troubleshooting

### Notes Not Appearing

**Check if command succeeded:**
```bash
uv run anyt task note DE-3 --message "Test note"
# Should output success message
```

**View task to verify:**
```bash
uv run anyt task show DE-3
# Check Events section
```

### Notes Too Long

**Adjust summary length in script:**
```bash
# Reduce from 500 to 200 characters
summary=$(echo "$claude_response" | head -c 200)
```

### Missing Timestamps

Notes are automatically timestamped by the `task note` command. If timestamps are missing, check your AnyTask CLI version:
```bash
uv run anyt --version
```

## Future Enhancements

- [ ] Add tags to notes (e.g., `#claude #automated`)
- [ ] Support for note categories (start, progress, completion, error)
- [ ] Export notes to external systems (Slack, Discord)
- [ ] Aggregate notes across multiple tasks
- [ ] Search and filter by note content
- [ ] Generate reports from task notes

---

**This automatic note-taking feature provides complete transparency and accountability for Claude's automated task work!** 📝✨
