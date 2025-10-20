Create a new task based on user description: [description]

**Expected input:** A description or prompt for what needs to be built (e.g., "Add API endpoint for task comments")

**Workflow:**

1. **Determine task ID:**
   - Check `.anyt/tasks/README.md` to see current phase
   - Look at existing tasks in `active/`, `backlog/`, and `done/`
   - Find the highest task ID in the current phase
   - Increment the ID for the new task
   - If starting a new phase, use next phase number with ID 1
   - Format: `T{stage}-{id}` (e.g., T2-10, T3-1)

2. **Analyze the description:**
   - Break down what needs to be implemented
   - Identify technical requirements
   - Determine if this depends on other tasks
   - Estimate complexity (Low/Medium/High priority, hours estimate)

3. **Create task file:**
   - Create file in `.anyt/tasks/backlog/`
   - Filename format: `T{stage}-{id}-{Title}.md` (e.g., `T2-10-Task-Comments-API.md`)
   - Use the standard task template with these sections:
     ```markdown
     # T{stage}-{id}: {Title}

     **Priority**: [High/Medium/Low]
     **Status**: Pending
     **Created**: {date}

     ## Description
     [What needs to be built]

     ## Objectives
     - [Specific goal 1]
     - [Specific goal 2]

     ## Acceptance Criteria
     - [ ] [Criterion 1]
     - [ ] [Criterion 2]
     - [ ] Tests written and passing
     - [ ] Code reviewed and merged

     ## Dependencies
     - T{x}-{y}: [Task name]

     ## Estimated Effort
     {hours estimate}

     ## Technical Notes
     [Implementation guidance]

     ## Events

     ### {date} {time} - Created
     - Task created based on user request
     ```

4. **Ask user:**
   - Show the created task summary
   - Ask if they want to start working on it now (use `/anyt-work {task-id}`)
   - Or if they want to keep it in backlog for later

**Important:**
- Only create tasks for actual code implementation work
- Don't create tasks for linting, formatting, or docs
- Ensure task ID is unique and sequential
- Include proper dependencies
- Be specific in acceptance criteria

Create the task now.
