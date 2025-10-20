# Show Task Board

Display the current Kanban board with all tasks organized by status.

## Steps

1. Run: `uv run src/cli/main.py board --json`

2. Parse the JSON output to extract task counts by status:
   - backlog
   - todo
   - inprogress
   - blocked
   - done
   - canceled

3. Also run: `uv run src/cli/main.py board` (without --json) to get the visual board

4. Show the visual board output to the user

5. Provide a summary analysis:
   - Total tasks in progress
   - Tasks ready to work on (todo status)
   - Tasks in backlog
   - Recent completions (done status)
   - Any blocked tasks (highlight these as they need attention)

6. Optionally, identify high-priority tasks that are ready to work on:
   ```bash
   uv run src/cli/main.py task list --status todo --sort priority --order desc --limit 5 --json
   ```

7. Provide actionable insights:
   - If there are too many in-progress tasks, suggest focusing on completion
   - If there are blocked tasks, suggest reviewing dependencies
   - If todo list is empty, suggest picking from backlog
   - Highlight high-priority items that need attention

## Example Output

**Visual Board:**
```
(Shows the board output from CLI)
```

**Summary:**

Current Status:
- 🔵 In Progress: 5 tasks
- ✅ Todo (Ready): 12 tasks
- 📋 Backlog: 23 tasks
- ⚠️ Blocked: 2 tasks
- ✓ Done (Today): 3 tasks

Key Insights:
- You have 2 blocked tasks that need attention:
  - DEV-35: Blocked by DEV-40 (still in progress)
  - DEV-47: Waiting on external API access

- Top priority tasks ready to work on:
  1. DEV-42 - Implement OAuth callback (Priority: 2)
  2. DEV-45 - Add Redis caching (Priority: 1)
  3. DEV-48 - Update documentation (Priority: 1)

Recommendation: You have 5 tasks in progress. Consider completing some before starting new ones, or run /anyt-next to see what to prioritize.

## Notes

- Use `--json` for data analysis but show the regular visual board for better readability
- Provide both the visual representation AND analytical insights
- Focus on actionable recommendations
- Highlight blocked tasks as they may need dependency resolution
