# Create New Task

Help the user create a new task interactively.

## Steps

1. Ask the user for task details:
   - **Title** (required)
   - **Description** (optional, but recommended)
   - **Priority** (-2 to 2, default 0)
     - -2: Very Low
     - -1: Low
     - 0: Normal (default)
     - 1: High
     - 2: Urgent
   - **Labels** (optional, comma-separated)
   - **Status** (backlog, todo, inprogress - default: backlog)
   - **Project ID** (optional, will use default if not specified)

2. Once you have the details, run:
   ```bash
   uv run src/cli/main.py task add "<TITLE>" \
     --description "<DESCRIPTION>" \
     --priority <PRIORITY> \
     --labels <LABELS> \
     --status <STATUS> \
     --json
   ```

3. Parse the JSON response to get the task identifier

4. Show a confirmation message with the created task details:
   - Task identifier
   - Title
   - Priority
   - Status
   - Labels (if any)

5. Ask: "Would you like to start working on this task now?"
   - If yes, run: `uv run src/cli/main.py task pick <TASK_ID>`
   - Then offer to help with implementation

## Example Workflow

**User:** "I need to add Redis caching to the API"

**Claude:** "I'll help you create a task for adding Redis caching. Let me gather some details:

Title: Add Redis caching to API

What priority should this be?
- 0: Normal
- 1: High
- 2: Urgent"

**User:** "1 - it's high priority"

**Claude:** "Great. Any labels to add? (e.g., backend, performance, cache)"

**User:** "backend, cache, performance"

**Claude:** "Should this be in 'backlog' or ready to work on in 'todo'?"

**User:** "todo"

**Claude runs:**
```bash
uv run src/cli/main.py task add "Add Redis caching to API" \
  --description "Implement Redis caching layer to improve API performance and reduce database load" \
  --priority 1 \
  --labels backend,cache,performance \
  --status todo \
  --json
```

**Claude parses JSON response:**
```json
{
  "success": true,
  "data": {
    "identifier": "DEV-48",
    "title": "Add Redis caching to API",
    "priority": 1,
    "status": "todo",
    "labels": ["backend", "cache", "performance"]
  }
}
```

**Claude:** "✓ Created DEV-48: Add Redis caching to API

Priority: 1 (High)
Status: todo
Labels: backend, cache, performance

Would you like to start working on this task now?"

**User:** "Yes"

**Claude:** "Great! Let me pick this task for you."
```bash
uv run src/cli/main.py task pick DEV-48
```

"Now, let me help you implement Redis caching. First, let me check what you already have..."

## Notes

- Always use `--json` flag to get structured output
- Parse the JSON response to extract task details
- Provide helpful default suggestions based on the user's description
- If the user's initial message includes enough context, you can pre-fill some fields
- Always confirm before creating the task
- After creation, offer to help implement the task immediately
