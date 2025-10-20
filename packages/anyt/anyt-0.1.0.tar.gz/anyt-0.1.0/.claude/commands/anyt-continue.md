Continue working on the current task in the AnyTask task management system.

**Workflow:**

1. **Check for active task:**
   - Look in `.anyt/tasks/active/` directory
   - If an active task exists (a `.md` file in that directory):
     - Read the task file to understand what needs to be done
     - Review the acceptance criteria and objectives
     - Check the latest event entry to see what was done last
     - Update the task status if needed
     - Add a new event entry documenting that you're continuing work
     - Begin implementing the next acceptance criteria item
     - When making progress, add event entries to document what was accomplished

2. **If no active task found:**
   - Check `.anyt/tasks/backlog/` directory
   - Sort backlog tasks by priority and dependencies
   - Pick the latest task from backlog that has no unmet dependencies
   - Read the full task specification
   - Move the task file from `backlog/` to `active/`
   - Update the Status field from "Pending" to "In Progress"
   - Add an event entry: "Started work on task"
   - Begin implementing the task following the acceptance criteria

3. **Start new branch 
   -- `git fetch origin` to sync with origin 
   -- create new branch with on task id and description 
   -- work on the new task

4. **Task completion:**
   - Verify all acceptance criteria are met
   - Update Status to "Completed"
   - Add completion event entry with summary
   - Move task file from `active/` to `done/`
   - If the task is done Commit the current change, create PR for this change if PR already exists, update PR 
   - The PR description should have PR link  , PR title to include the Task id 

**Important:**
- Only track actual code implementation work as tasks
- Do not track linting, formatting, or minor doc updates
- Add event entries as you make significant progress
- Always check task dependencies before starting
- Follow the workflow exactly as documented in CLAUDE.md

Begin working on the task now.
