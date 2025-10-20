# Select and Work on Next Task

Run the AnyTask CLI to get task suggestions and help implement the recommended task.

## Steps

1. Run: `uv run src/cli/main.py task suggest --json --limit 5`

   The CLI will analyze available tasks and return pre-ranked suggestions with:
   - Computed scores based on priority, status, dependencies, and impact
   - Reasoning for each recommendation
   - Metadata about blockers and impact

2. Parse the JSON output and present the top 3-5 recommendations to the user

3. Present recommendations with clear reasoning:
   - Show why each task is recommended
   - Highlight the priority and status
   - Explain the impact of working on this task

4. Ask the user which task they'd like to work on

5. Once selected, run: `uv run src/cli/main.py task pick <TASK_ID>`

6. Run: `uv run src/cli/main.py task show <TASK_ID> --json` to get full details

7. Help the user implement the task based on its description and requirements

8. As you make progress, update the task description:
   ```bash
   uv run src/cli/main.py task edit <TASK_ID> --description "Progress: [your updates]"
   ```

9. When complete, mark the task done:
   ```bash
   uv run src/cli/main.py task done
   ```

## How the Suggest Command Works

The `task suggest` command implements intelligent scoring:

- **Priority weighting** (5x) - Higher priority tasks score better
- **Status bonus** (+3 for todo, +1 for inprogress)
- **Dependencies** (-10 penalty if blocked, +2 bonus if all deps complete)
- **Impact** (+2 per task that this unblocks)

Blocked tasks (with incomplete dependencies) are automatically filtered out.

## Example Interaction

```
User: /anyt-next