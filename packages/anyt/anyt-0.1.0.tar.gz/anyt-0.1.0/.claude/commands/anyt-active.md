# Show Active Task

Display details about the currently active task.

## Steps

1. Run: `uv run src/cli/main.py active --json`

2. Parse the JSON response to check if there's an active task

3. If there's an active task:
   - Show the task identifier, title, priority, and status
   - Display the description
   - Show any labels or metadata
   - Run: `uv run src/cli/main.py task dep list <TASK_ID> --json` to check dependencies
   - Display dependency information if any
   - Ask: "What would you like me to help with on this task?"

4. If there's no active task (empty response or null):
   - Inform the user: "You don't have an active task picked right now."
   - Suggest: "Would you like me to run /anyt-next to help you select a task to work on?"

## Example Output (Active Task)

```
Active Task: DEV-42 - Implement OAuth callback

Priority: 2 (Urgent)
Status: inprogress
Labels: backend, auth

Description:
Implement the OAuth callback endpoint to handle authentication
responses from third-party providers.

Dependencies:
✓ DEV-40 - Set up OAuth provider config (done)
✓ DEV-41 - Create user model (done)

What would you like me to help with on this task?
```

## Example Output (No Active Task)

```
You don't have an active task picked right now.

Would you like me to run /anyt-next to help you select a task to work on?
```

## Notes

- Always use `--json` flag to get structured output
- Present information in a clear, readable format
- Check dependencies to give context about the task
