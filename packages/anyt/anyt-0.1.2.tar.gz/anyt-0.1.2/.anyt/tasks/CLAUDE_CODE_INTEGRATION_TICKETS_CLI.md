# Claude Code Integration Tickets (CLI-Based Approach)

**Created**: 2025-10-18
**Approach**: Slash Commands + CLI (No MCP required!)
**Total Effort**: 10-14 hours over 1-2 weeks

---

## 🎯 Why CLI Instead of MCP?

**Advantages:**
- ✅ **No MCP server setup** - Works immediately
- ✅ **Simpler to implement** - 10-14h vs 20-30h for MCP
- ✅ **Easy to debug** - Just run CLI commands manually
- ✅ **Transparent** - User sees what's happening
- ✅ **Portable** - Works anywhere CLI is installed

**MCP can come later** as Phase 2 for advanced features!

---

## ✅ Slash Commands (Already Created!)

Located in `.claude/commands/`:

### `/anyt-next` - Select Next Task ⭐
**What**: Lists tasks, suggests best one, helps implement
**File**: `.claude/commands/anyt-next.md` ✅

```
User: /anyt-next

Claude:
1. Runs: uv run src/cli/main.py task suggest --json
2. Analyzes output
3. Suggests: "I recommend DEV-42 (high priority, no blockers)"
4. User confirms
5. Picks task and starts helping
```

### `/anyt-active` - Show Active Task
**What**: Displays currently active task details
**File**: `.claude/commands/anyt-active.md` ✅

### `/anyt-create` - Create New Task
**What**: Interactively creates a task
**File**: `.claude/commands/anyt-create.md` ✅

### `/anyt-board` - Show Board
**What**: Displays Kanban board and summary
**File**: `.claude/commands/anyt-board.md` ✅

---

## 📦 Phase 1: CLI Enhancement (4-6 hours)

### T7-27: CLI - JSON Output Enhancement ⭐ START HERE
- **Priority**: High
- **Effort**: 2-3 hours
- **What**: Ensure ALL CLI commands support `--json` flag
- **Why**: Claude Code needs machine-readable output to parse results
- **File**: `.anyt/tasks/backlog/T7-27-CLI-JSON-Output-Enhancement.md`

**Commands to check:**
- [x] task add, list, show, edit, done, rm
- [ ] task dep add, rm, list
- [ ] task pick, active
- [ ] board, timeline, graph, summary
- [ ] workspace/project commands

### T7-29: CLI - Smart Task Suggestion
- **Priority**: High
- **Effort**: 2-3 hours
- **What**: Add `anyt task suggest` command with intelligent scoring
- **Why**: Pre-computed suggestions instead of Claude parsing task lists
- **File**: `.anyt/tasks/backlog/T7-29-CLI-Smart-Task-Suggest.md`

**Example:**
```bash
$ anyt task suggest --json

{
  "suggestions": [
    {
      "identifier": "DEV-42",
      "title": "Implement OAuth",
      "priority": 2,
      "score": 15,
      "reason": "Highest priority, no blockers, unblocks 2 tasks"
    }
  ]
}
```

---

## 📚 Phase 2: Documentation (2-3 hours)

### T7-30: Claude Code Documentation (CLI)
- **Priority**: Medium
- **Effort**: 2-3 hours
- **What**: Create `docs/CLAUDE_CODE_INTEGRATION.md` with setup and workflows
- **Why**: Help developers get started quickly
- **File**: `.anyt/tasks/backlog/T7-30-Claude-Code-Documentation-CLI.md`

**Contents:**
- Setup instructions
- Slash command reference
- Workflow examples
- Troubleshooting guide

---

## 🔄 Phase 3: Migration (4-5 hours)

### T7-31: Migration Script - Folder to Database
- **Priority**: Medium
- **Effort**: 4-5 hours
- **What**: Script to import `.anyt/tasks/*.md` files into database
- **Why**: Migrate from folder-based to database-backed
- **File**: `.anyt/tasks/backlog/T7-31-Migration-Script-CLI.md`

**Features:**
- Parse markdown task files
- Extract metadata (title, priority, status, dependencies)
- Create tasks via CLI
- Preserve task IDs in description
- Generate migration report

**Usage:**
```bash
# Preview
python scripts/migrate_tasks_to_db.py --dry-run

# Migrate
python scripts/migrate_tasks_to_db.py

# Archive old files
mv .anyt/tasks .anyt/tasks.old
```

---

## 🎯 Critical Path (Minimum Viable)

For basic Claude Code integration, implement in this order:

```
1. T7-27 (JSON Output)       ← 2-3h - START HERE
   ↓
2. T7-29 (Smart Suggest)     ← 2-3h - Core feature
   ↓
3. T7-30 (Documentation)     ← 2-3h - Setup guide
   ↓
4. T7-31 (Migration)         ← 4-5h - Switch to database
```

**Total**: 10-14 hours

After these 4 tasks, you can:
- Type `/anyt-next` in Claude Code to get task suggestions
- Claude helps you implement the selected task
- All tasks tracked in database (not files)

---

## 📊 Task Summary

| ID | Task | Priority | Effort | Status |
|----|------|----------|--------|--------|
| T7-27 | CLI JSON Output | High | 2-3h | Pending |
| T7-29 | Smart Task Suggest | High | 2-3h | Pending |
| T7-30 | Documentation | Medium | 2-3h | Pending |
| T7-31 | Migration Script | Medium | 4-5h | Pending |

**All located in:** `.anyt/tasks/backlog/`

---

## 🚀 How It Works (After Implementation)

### User Experience

```
Morning:
  User: /anyt-board
  → Claude shows task board

  User: /anyt-next
  → Claude: "I suggest DEV-42 (Implement OAuth) - high priority, ready to work on"
  → User: "Let's do it"
  → Claude picks task and helps implement

During work:
  User: "I've implemented the OAuth callback"
  → Claude: "Great! Let me update the task."
  → Runs: uv run src/cli/main.py task edit DEV-42 --description "Progress: Implemented callback"

End of day:
  User: "I'm done with this task"
  → Claude: "Marking DEV-42 as complete."
  → Runs: uv run src/cli/main.py task done
  → Claude: "✓ DEV-42 complete! Run /anyt-next for next task."
```

### Behind the Scenes

Claude runs CLI commands via bash tool:
```bash
# Suggest task
uv run src/cli/main.py task suggest --json --limit 5

# Pick task
uv run src/cli/main.py task pick DEV-42

# Show details
uv run src/cli/main.py task show DEV-42 --json

# Update task
uv run src/cli/main.py task edit DEV-42 --description "..."

# Mark done
uv run src/cli/main.py task done
```

All commands return JSON for easy parsing!

---

## ✅ After Implementation Benefits

1. **No Manual File Editing** - Database handles everything
2. **Smart Suggestions** - AI-powered task prioritization
3. **Simple Workflow** - Just use slash commands
4. **Fast Setup** - No MCP server configuration
5. **Easy Debugging** - Run commands manually to test
6. **Database-Backed** - Full querying and filtering
7. **Team Ready** - Multi-user capable

---

## 📁 Created Files

### Slash Commands (Already done! ✅)
- `.claude/commands/anyt-next.md` ✅
- `.claude/commands/anyt-active.md` ✅
- `.claude/commands/anyt-create.md` ✅
- `.claude/commands/anyt-board.md` ✅

### Task Tickets
- `.anyt/tasks/backlog/T7-27-CLI-JSON-Output-Enhancement.md` ✅
- `.anyt/tasks/backlog/T7-29-CLI-Smart-Task-Suggest.md` ✅
- `.anyt/tasks/backlog/T7-30-Claude-Code-Documentation-CLI.md` ✅
- `.anyt/tasks/backlog/T7-31-Migration-Script-CLI.md` ✅

### Documentation
- `docs/CLAUDE_CODE_MIGRATION_PLAN.md` ✅ (Updated to CLI approach)

---

## 🔮 Future: Phase 2 (MCP Enhancement)

After CLI integration is stable, can optionally add MCP for:

- **Auto task creation** as Claude works
- **Real-time resources** (active task context)
- **Proactive updates** without slash commands
- **Git commit linking** automatically

Estimated: +10-15 hours

But CLI approach gets you 80% of value in 20% of time!

---

## 🎬 Next Steps

**Recommended order:**

1. **Start with T7-27** (JSON Output) - 2-3 hours
   - Make CLI output Claude-friendly
   - Test slash commands work

2. **Add T7-29** (Smart Suggest) - 2-3 hours
   - Implement intelligent task scoring
   - Test `/anyt-next` end-to-end

3. **Write T7-30** (Documentation) - 2-3 hours
   - Document setup and workflows
   - Create troubleshooting guide

4. **Run T7-31** (Migration) - 4-5 hours
   - Import existing tasks to database
   - Archive old folder system
   - **Start using Claude Code for task management!**

---

**Total Time**: 10-14 hours to complete integration 🎉

Then you can retire the `.anyt/tasks/` folder system and use Claude Code + database for everything!
