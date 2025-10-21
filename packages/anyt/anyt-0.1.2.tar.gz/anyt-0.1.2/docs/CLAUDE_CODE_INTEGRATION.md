# Claude Code Integration Guide

## Overview

AnyTask provides seamless integration with Claude Code through slash commands and CLI tools. This enables Claude to help you manage tasks, prioritize work, track progress, and implement features - all from within your development environment.

**No MCP server required!** This guide covers the simpler CLI-based approach using slash commands.

## Quick Start

### Prerequisites

- Python 3.11+ installed
- `uv` package manager installed
- Claude Code (claude.ai/code) access

### Setup (5 minutes)

1. **Install and start AnyTask backend:**

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd AnyTaskCLI

# Install dependencies
make install

# Start the backend server
make dev
```

The backend will start at `http://localhost:8000`.

2. **Configure the CLI:**

Open a new terminal and configure the environment:

```bash
# Add development environment
uv run src/cli/main.py env add dev http://localhost:8000

# Login with authentication token
uv run src/cli/main.py auth login --token

# Initialize workspace in your project directory
cd /path/to/your/project
uv run src/cli/main.py init
```

3. **Verify the setup:**

```bash
# Check API health
uv run src/cli/main.py health

# View your task board
uv run src/cli/main.py board
```

That's it! You're ready to use AnyTask with Claude Code.

## Available Slash Commands

Claude Code includes several powerful slash commands located in `.claude/commands/`. These commands integrate with the AnyTask CLI to provide intelligent task management.

### `/anyt-next` - Select Next Task

**Purpose:** Intelligently suggests the best task to work on next based on priority, dependencies, and impact.

**What it does:**
1. Runs `task suggest` to analyze all available tasks
2. Presents top 3-5 recommendations with scoring and reasoning
3. Helps you pick a task and start working on it
4. Offers to help implement the selected task

**Example usage:**

```
User: /anyt-next

Claude: "Let me check your tasks...

📋 Top Task Recommendations:

1. DEV-42: Implement OAuth callback (Score: 15.0)
   • Priority: 2 (Urgent)
   • Status: todo
   • Impact: Unblocks 2 other tasks
   • All dependencies complete ✓
   • Reasoning: Highest priority task with no blockers

2. DEV-45: Add Redis caching layer (Score: 9.0)
   • Priority: 1 (High)
   • Status: todo
   • Impact: Performance improvement
   • Reasoning: High priority, ready to implement

3. DEV-48: Update API documentation (Score: 7.0)
   • Priority: 1 (High)
   • Status: todo
   • Reasoning: Documentation needed for recent changes

Which task would you like to work on?"

User: "Let's do DEV-42"

Claude: "Great choice! Let me pick that task for you."
[Runs: uv run src/cli/main.py task pick DEV-42]

"Now working on DEV-42: Implement OAuth callback

Let me help you implement this. First, let me check the existing auth setup..."
```

**How the scoring works:**
- Priority weighting (5x multiplier)
- Status bonus (+3 for todo, +1 for inprogress)
- Dependency analysis (-10 penalty if blocked)
- Impact score (+2 per task unblocked)
- Blocked tasks are automatically filtered out

### `/anyt-active` - Show Active Task

**Purpose:** Display details about your currently active (picked) task.

**What it does:**
1. Checks if you have an active task picked
2. Shows task details, dependencies, and status
3. Offers to help with implementation
4. If no active task, suggests running `/anyt-next`

**Example usage:**

```
User: /anyt-active

Claude: "📌 Active Task: DEV-42 - Implement OAuth callback

Priority: 2 (Urgent)
Status: inprogress
Labels: backend, auth

Description:
Implement the OAuth callback endpoint to handle authentication
responses from third-party providers.

Dependencies:
✓ DEV-40 - Set up OAuth provider config (done)
✓ DEV-41 - Create user model (done)

What would you like me to help with on this task?"
```

**When no task is active:**

```
User: /anyt-active

Claude: "You don't have an active task picked right now.

Would you like me to run /anyt-next to help you select a task to work on?"
```

### `/anyt-create` - Create New Task

**Purpose:** Interactively create a new task with all necessary details.

**What it does:**
1. Asks for task details (title, description, priority, labels, status)
2. Creates the task via CLI
3. Confirms creation with task identifier
4. Offers to pick the task and start working on it

**Priority levels:**
- `-2`: Very Low
- `-1`: Low
- `0`: Normal (default)
- `1`: High
- `2`: Urgent

**Example usage:**

```
User: "I need to add rate limiting to our API"

Claude: "Great idea! Let me help you create a task for that.

I'll create a task called 'Add rate limiting to API'.

What priority should this have?
- 0: Normal
- 1: High
- 2: Urgent"

User: "1 - it's high priority"

Claude: "Perfect. What labels would you like to add? (e.g., backend, security, api)"

User: "backend, security, api"

Claude: "Should this be in 'backlog' or ready to work on in 'todo'?"

User: "todo - I want to work on it soon"

Claude: [Runs: uv run src/cli/main.py task add "Add rate limiting to API" \
  --description "Implement rate limiting middleware to protect API endpoints from abuse" \
  --priority 1 \
  --labels backend,security,api \
  --status todo \
  --json]

"✓ Created DEV-50: Add rate limiting to API

Priority: 1 (High)
Status: todo
Labels: backend, security, api

Would you like to start working on this task now?"

User: "Yes"

Claude: [Runs: uv run src/cli/main.py task pick DEV-50]

"Excellent! Now working on DEV-50. Let me help you implement rate limiting.

First, I'll check what middleware framework you're using..."
```

### `/anyt-board` - Show Kanban Board

**Purpose:** Display the full Kanban board with tasks organized by status columns.

**What it does:**
1. Shows visual board representation
2. Provides summary statistics (tasks by status)
3. Identifies blocked tasks needing attention
4. Highlights high-priority items in todo
5. Gives actionable recommendations

**Example usage:**

```
User: /anyt-board

Claude: [Shows visual board output]

"📊 Task Board Summary:

Current Status:
• 🔵 In Progress: 5 tasks
• ✅ Todo (Ready): 12 tasks
• 📋 Backlog: 23 tasks
• ⚠️ Blocked: 2 tasks
• ✓ Done (Today): 3 tasks

⚠️ Blocked Tasks Needing Attention:
• DEV-35: Database migration - Blocked by DEV-40 (still in progress)
• DEV-47: Third-party API integration - Waiting on external API access

🎯 Top Priority Tasks Ready to Work On:
1. DEV-42 - Implement OAuth callback (Priority: 2, Urgent)
2. DEV-45 - Add Redis caching (Priority: 1, High)
3. DEV-48 - Update API documentation (Priority: 1, High)

💡 Recommendation: You have 5 tasks in progress. Consider completing some before starting new ones. Run /anyt-next to see what to prioritize."
```

## Common Workflows

### Daily Standup

Start your day by reviewing tasks and selecting what to work on:

```
User: /anyt-board

Claude: [Shows board with summary and insights]

User: /anyt-next

Claude: [Suggests best task based on priorities and dependencies]

User: "Let's go with option 1"

Claude: [Picks task and starts helping with implementation]
```

### Spontaneous Idea

When you think of something that needs to be done:

```
User: "We should add input validation to the user registration form"

Claude: "That's important for security! Should I create a task for this?"

User: "Yes, make it high priority"

Claude: [Creates task using /anyt-create workflow]
       [Offers to work on it immediately or add to backlog]
```

### Check What You're Working On

Quickly remind yourself of your current task:

```
User: "What am I working on?"
# or
User: /anyt-active

Claude: [Shows active task details, dependencies, and offers help]
```

### Complete a Task

Mark your work as done:

```
User: "I finished implementing the OAuth callback"

Claude: "Excellent work! Let me mark DEV-42 as complete."

[Runs: uv run src/cli/main.py task done]

"✓ Marked DEV-42 as done!

Great job completing this urgent task. It was blocking 2 other tasks which are now unblocked.

Would you like to run /anyt-next to see what to work on next?"
```

### Review Blocked Tasks

Address tasks that are stuck:

```
User: /anyt-board

Claude: [Shows board]
       "You have 2 blocked tasks:
       - DEV-35 is blocked by DEV-40
       - DEV-47 is waiting on external API access

       Would you like me to:
       1. Help complete DEV-40 to unblock DEV-35?
       2. Update DEV-47 with progress notes?
       3. Check if any other tasks can be worked on instead?"
```

## Advanced Usage: Direct CLI Access

While slash commands provide a guided experience, Claude can also run CLI commands directly for more specific queries:

### Filter by Priority

```
User: "Show me all urgent tasks"

Claude: [Runs: uv run src/cli/main.py task list --priority-gte 2 --json]

"🔴 Urgent Tasks (Priority 2):

1. DEV-42 - Implement OAuth callback (inprogress)
2. DEV-51 - Fix security vulnerability in auth module (todo)
3. DEV-54 - Database backup failure (blocked by DEV-53)

You're currently working on DEV-42. Would you like to focus on that, or should we look at DEV-51?"
```

### Search Tasks

```
User: "Find all tasks related to authentication"

Claude: [Runs: uv run src/cli/main.py task list --search auth --json]

"🔍 Tasks matching 'auth':

1. DEV-40 - Set up OAuth provider config (done)
2. DEV-41 - Create user authentication model (done)
3. DEV-42 - Implement OAuth callback (inprogress) ← Active
4. DEV-51 - Fix auth security vulnerability (todo, Priority 2)
5. DEV-56 - Add multi-factor authentication (backlog)

You're working on DEV-42. After that, DEV-51 is the next high-priority auth task."
```

### View Dependencies

```
User: "What's blocking task DEV-35?"

Claude: [Runs: uv run src/cli/main.py task dep list DEV-35 --json]

"📊 Dependencies for DEV-35 (Database migration):

Blocked by:
• DEV-40 - Set up OAuth provider config (done) ✓
• DEV-53 - Update database schema (inprogress) ⏳

DEV-35 is blocked because DEV-53 is still in progress. Once DEV-53 is complete, DEV-35 will be ready to work on.

Would you like to help complete DEV-53 first?"
```

### Update Task Details

```
User: "Update the description of DEV-42 to include progress notes"

Claude: [Runs: uv run src/cli/main.py task edit DEV-42 \
         --description "Implement OAuth callback endpoint.

         Progress:
         ✓ Created route handler
         ✓ Added token validation
         ⏳ Working on session management
         - Still need: error handling, tests"]

"✓ Updated DEV-42 description with progress notes."
```

## Troubleshooting

### Backend Not Running

**Error:**
```
Error: Connection refused at http://localhost:8000
```

**Solution:**
Start the backend server:
```bash
make dev
```

Verify it's running:
```bash
curl http://localhost:8000/api/v1/health
```

### No Workspace Configured

**Error:**
```
Error: Not in a workspace directory. No .anyt/anyt.json found.
```

**Solution:**
Initialize a workspace in your project directory:
```bash
cd /path/to/your/project
uv run src/cli/main.py init
```

### Authentication Failed

**Error:**
```
Error: Unauthorized. Invalid or missing authentication token.
```

**Solution:**
Login with a valid token:
```bash
uv run src/cli/main.py auth login --token
```

Get a token from your backend admin or user settings.

### Slash Command Not Found

**Error:**
Claude doesn't recognize `/anyt-next` or other commands.

**Solution:**
1. Verify `.claude/commands/` directory exists in your project
2. Check that command files are `.md` format (e.g., `anyt-next.md`)
3. Restart Claude Code to reload commands
4. Run `ls .claude/commands/` to verify files are present

### Task Identifier Not Found

**Error:**
```
Error: Task 'DEV-42' not found
```

**Solutions:**
1. Verify the task exists:
   ```bash
   uv run src/cli/main.py task list --json
   ```
2. Check if you're in the correct workspace
3. Ensure the identifier is correct (case-sensitive)

### CLI Command Times Out

**Error:**
Command hangs or takes too long.

**Solutions:**
1. Check backend is responsive:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
2. Check database connection
3. Look at backend logs for errors:
   ```bash
   # In the terminal running 'make dev'
   ```
4. Restart backend if needed:
   ```bash
   # Ctrl+C to stop, then 'make dev' again
   ```

## Tips & Best Practices

### 1. Start Every Session with `/anyt-board` or `/anyt-next`

Get oriented quickly by seeing what's on your plate:
- `/anyt-board` for a full overview
- `/anyt-next` to jump right into work

### 2. Create Tasks as You Go

When you think of something during development:
- Use `/anyt-create` immediately to capture it
- Add it to backlog if not urgent
- This prevents ideas from being forgotten

### 3. Keep Descriptions Updated

As you work, update task descriptions with progress:
- What's been completed
- Current blockers
- Next steps
- This helps when you return to a task later

### 4. Use Labels for Organization

Consistent labeling makes filtering easier:
- Technology: `backend`, `frontend`, `database`
- Type: `feature`, `bug`, `refactor`, `docs`
- Area: `auth`, `api`, `ui`, `tests`

Example:
```bash
uv run src/cli/main.py task add "Fix login timeout" \
  --labels backend,bug,auth \
  --priority 2
```

### 5. Mark Tasks Done Promptly

Don't let completed tasks linger in "inprogress":
- Keeping the board clean helps prioritization
- Unblocks dependent tasks
- Provides satisfaction of seeing progress

### 6. Review Blocked Tasks Regularly

Blocked tasks are opportunities to:
- Complete blockers first
- Reassess priorities
- Find alternative approaches

Use `/anyt-board` to spot blocked tasks quickly.

### 7. Limit Work-in-Progress

Too many inprogress tasks leads to context switching:
- Focus on completing 1-3 tasks before starting new ones
- `/anyt-board` will warn you if you have too many
- Higher completion rate > more started tasks

### 8. Use Priority Thoughtfully

Reserve urgent (priority 2) for true emergencies:
- Security vulnerabilities
- Production outages
- Blocking critical releases

Most tasks should be Normal (0) or High (1).

### 9. Leverage Dependency Tracking

For complex features with multiple subtasks:
```bash
# Create parent task
uv run src/cli/main.py task add "Implement user authentication"

# Create subtasks
uv run src/cli/main.py task add "Design auth database schema"
uv run src/cli/main.py task add "Create login API endpoint"
uv run src/cli/main.py task add "Add authentication middleware"

# Add dependencies
uv run src/cli/main.py task dep add DEV-43 --on DEV-42
```

This ensures subtasks are worked on in the right order.

### 10. Ask Claude for Help

Claude can help with more than just task management:
- "Help me implement DEV-42"
- "What's the best approach for this task?"
- "Review my code for DEV-45"
- "Suggest test cases for this feature"

## CLI-Based vs. MCP Integration

This guide covers the **CLI-based approach** using slash commands. There's also a more advanced **MCP (Model Context Protocol) integration** option.

### CLI-Based Approach (This Guide)

**Advantages:**
- ✅ Simple setup (no MCP configuration needed)
- ✅ Works immediately out of the box
- ✅ Easy to debug (run CLI commands manually to test)
- ✅ Portable (works anywhere uv/CLI is installed)
- ✅ Full control over when and how tasks are created

**Best for:**
- Getting started quickly
- Teams that prefer explicit task management
- Projects where you want manual control
- Debugging and testing scenarios

### MCP Integration

**Advantages:**
- ✅ Automatic task creation as Claude works
- ✅ Real-time resource updates (Claude sees tasks as resources)
- ✅ Proactive progress tracking
- ✅ Deeper integration with Claude Code environment

**Best for:**
- Advanced workflows
- Teams wanting automatic task tracking
- Projects with many small tasks
- When you want Claude to manage tasks autonomously

**Learn more:** See `docs/MCP_INTEGRATION.md` for MCP setup guide.

### Which Should You Use?

Start with the CLI-based approach (this guide):
1. It's simpler and faster to set up
2. You learn the core concepts
3. You can always add MCP later

Move to MCP integration when:
1. You're comfortable with CLI workflows
2. You want more automation
3. Your team is ready for autonomous task creation

## Next Steps

Now that you understand Claude Code integration:

1. **Try the workflows** - Run through the examples above
2. **Create your first task** - Use `/anyt-create`
3. **Pick a task** - Use `/anyt-next`
4. **Build something** - Let Claude help you implement it
5. **Explore the CLI** - See `docs/CLI_USAGE.md` for all commands
6. **Consider MCP** - Read `docs/MCP_INTEGRATION.md` if interested

## Getting Help

- **CLI Reference:** `docs/CLI_USAGE.md`
- **API Documentation:** `docs/server_api.md`
- **Project Guide:** `CLAUDE.md`
- **Issues:** Report bugs at GitHub issues
- **Command Help:** `uv run src/cli/main.py --help`

Happy task managing! 🚀
