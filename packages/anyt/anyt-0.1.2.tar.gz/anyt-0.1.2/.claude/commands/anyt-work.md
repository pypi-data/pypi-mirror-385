Work on a specific task by its ID: [task-id]

**Expected input:** Task ID in format `T{stage}-{id}` (e.g., T2-5, T3-1)

**Workflow:**

1. **Find the task:**
   - Search for task file matching the ID in `.anyt/tasks/backlog/`, `.anyt/tasks/active/`, or `.anyt/tasks/done/`
   - The filename will be like `T2-5-Repository-Pattern-Foundation.md`

2. **Handle task state:**
   - **If task is in `done/`:**
     - Inform user that task is already completed
     - Ask if they want to review it or reopen it

   - **If task is in `backlog/`:**
     - Move task file from `backlog/` to `active/`
     - Check if there's already an active task:
       - If yes, ask user if they want to pause the current task
       - Move current active task back to backlog if confirmed
     - Update Status field to "In Progress"
     - Add event entry: "Started work on task"

   - **If task is in `active/`:**
     - Read the current task state
     - Review latest event to see progress

3. **Begin work:**
   - Read the full task specification
   - Review objectives and acceptance criteria
   - Check dependencies are met
   - Start implementing following the technical notes
   - Add event entries as you make progress

4. **Task completion:**
   - Verify all acceptance criteria are met
   - Update Status to "Completed"
   - Add completion event with summary
   - Move task file from `active/` to `done/`

**Important:**
- Only one task should be active at a time
- Always check dependencies before starting
- Document progress with event entries
- Follow acceptance criteria strictly

Begin working on the task now.
