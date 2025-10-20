# Claude Code Integration & Migration Plan (CLI-Based)

**Last Updated**: 2025-10-18
**Status**: Planning
**Approach**: CLI + Slash Commands (MCP in Phase 2)
**Goal**: Replace folder-based `.anyt/tasks/` workflow with database-backed task management integrated with Claude Code

---

## 📋 Executive Summary

This document outlines the plan to integrate AnyTask with Claude Code using **slash commands and CLI tools** (NOT MCP server). This approach is simpler, faster to implement, and requires no additional server setup.

### Current State
- ✅ Backend API complete with 50+ endpoints
- ✅ CLI tool with comprehensive task management
- ✅ Active task tracking (`.anyt/active_task.json`)
- ⚠️ Tasks managed in `.anyt/tasks/` markdown files
- ⚠️ No Claude Code integration
- ⚠️ Manual task selection and updates

### Target State (CLI-Based Approach)
- ✅ All tasks in database via AnyTask backend
- ✅ Claude Code slash commands (`/anyt-next`, `/anyt-create`, etc.)
- ✅ CLI provides JSON output for easy parsing
- ✅ Smart task suggestions via `anyt task suggest`
- ✅ Seamless workflow: `/anyt-next` → Claude suggests → implement → mark done
- 📅 MCP integration as Phase 2 enhancement (future)

---

## 🎯 Why CLI-Based Approach?

### Advantages
1. **No MCP Setup Required** - Works immediately, no server configuration
2. **Simpler Architecture** - Just CLI commands via bash tool
3. **Easy to Debug** - Run commands manually to test
4. **Portable** - Works anywhere CLI is installed
5. **Faster to Implement** - 10-15 hours vs 20-30 for MCP
6. **Transparent** - User can see exact CLI commands running

### MCP Can Come Later
We can add MCP in Phase 2 for:
- Auto task creation as Claude works
- Real-time resource updates
- Proactive progress tracking
- More sophisticated integrations

But CLI-based approach gets us 80% of the value in 20% of the time!

---

## 🎯 Phase 1: CLI Enhancement (Week 1)

**Goal**: Make CLI output Claude-friendly and add smart features

### Tasks (7-10 hours total)

| ID | Task | Priority | Effort | Status |
|----|------|----------|--------|--------|
| T7-27 | CLI - JSON Output Enhancement | High | 2-3h | Pending |
| T7-29 | CLI - Smart Task Suggestion | High | 2-3h | Pending |
| T7-28 | Task Management Patterns Documentation | Medium | 3-4h | Pending |

### Critical Path
T7-27 (JSON Output) → T7-29 (Smart Suggestions)

These enable Claude Code to:
1. Run CLI commands via bash
2. Parse JSON output easily
3. Get intelligent task suggestions
4. Present recommendations to user

### Deliverables
- [ ] All CLI commands support `--json` flag
- [ ] New `anyt task suggest` command with smart scoring
- [ ] Documentation on using CLI from Claude Code

---

## 🎯 Phase 2: Slash Commands (Week 1-2)

**Goal**: Create slash commands for common workflows

### Slash Commands (Already Created! ✅)

Located in `.claude/commands/`:

1. **`/anyt-next`** - Select and work on next task
   - Lists tasks, suggests best one, helps implement

2. **`/anyt-active`** - Show currently active task
   - Displays active task details, offers help

3. **`/anyt-create`** - Create new task interactively
   - Guides user through task creation

4. **`/anyt-board`** - Show Kanban board
   - Displays board and summarizes status

### How They Work

```markdown
# Example: /anyt-next

User types: /anyt-next

Claude:
1. Runs: uv run src/cli/main.py task suggest --json --limit 5
2. Parses JSON output
3. Presents: "I recommend DEV-42 (high priority, no blockers)"
4. User confirms
5. Runs: uv run src/cli/main.py task pick DEV-42
6. Starts helping implement
```

### Deliverables
- [x] Slash command files created
- [ ] Commands tested and working
- [ ] User documentation added

---

## 🎯 Phase 3: Documentation (Week 2)

**Goal**: Document the integration for developers

### Tasks (2-3 hours)

| ID | Task | Priority | Effort | Status |
|----|------|----------|--------|--------|
| T7-30 | Claude Code Documentation (CLI) | Medium | 2-3h | Pending |

### Deliverables
- [ ] `docs/CLAUDE_CODE_INTEGRATION.md` created
- [ ] Setup instructions validated
- [ ] Workflow examples documented
- [ ] Troubleshooting guide added
- [ ] README.md updated

---

## 🎯 Phase 4: Migration (Week 2-3)

**Goal**: Migrate existing tasks from files to database

### Tasks (4-5 hours)

| ID | Task | Priority | Effort | Status |
|----|------|----------|--------|--------|
| T7-31 | Migration Script - Folder to Database | Medium | 4-5h | Pending |

### Migration Process

1. **Create Backup**
   ```bash
   cp -r .anyt/tasks .anyt/tasks.backup
   ```

2. **Run Migration (Dry Run)**
   ```bash
   python scripts/migrate_tasks_to_db.py --dry-run
   ```

3. **Run Migration**
   ```bash
   python scripts/migrate_tasks_to_db.py
   ```

4. **Validate**
   ```bash
   uv run src/cli/main.py task list
   uv run src/cli/main.py board
   ```

5. **Archive Old Files**
   ```bash
   mv .anyt/tasks .anyt/tasks.old
   ```

### Deliverables
- [ ] Migration script complete
- [ ] All existing tasks in database
- [ ] Validation passed
- [ ] Old folder archived

---

## 📊 Total Effort Estimate

| Phase | Tasks | Effort | Dependencies |
|-------|-------|--------|--------------|
| 1. CLI Enhancement | T7-27, T7-29 | 4-6h | None |
| 2. Slash Commands | Already done! | 0h | ✅ Complete |
| 3. Documentation | T7-30 | 2-3h | Phase 1 |
| 4. Migration | T7-31 | 4-5h | Phase 3 |
| **Total** | | **10-14h** | |

**Timeline**: 1-2 weeks (much faster than MCP approach!)

---

## ✅ Success Criteria

### Must Have (Required for Migration)
- [ ] CLI supports JSON output for all commands
- [ ] `anyt task suggest` provides smart recommendations
- [ ] Slash commands work in Claude Code
- [ ] Documentation complete
- [ ] Migration script validated
- [ ] All existing tasks in database

### Nice to Have (Future Enhancements)
- [ ] MCP server integration (Phase 2)
- [ ] Auto task creation as Claude works
- [ ] Git commit linking
- [ ] Real-time progress tracking

---

## 🚀 Quick Start (After Implementation)

### 1. Setup Backend and CLI

```bash
# Start backend
make dev

# Configure CLI (in another terminal)
uv run src/cli/main.py env add dev http://localhost:8000
uv run src/cli/main.py auth login --token
uv run src/cli/main.py init
```

### 2. Use Slash Commands in Claude Code

```
User: /anyt-next

Claude: "Let me check your tasks...

I recommend DEV-42 (Implement OAuth callback) because:
- Highest priority (2)
- Status: todo
- No blockers
- Unblocks 2 tasks

Would you like to work on this?"

User: "Yes"

Claude: [Picks task and starts helping implement it]
```

### 3. Complete Tasks

```
User: "I'm done"

Claude: "Great! Marking DEV-42 as complete."
Runs: uv run src/cli/main.py task done
```

---

## 📝 Workflow Examples

### Example 1: Morning Standup

```
User: /anyt-board
→ Claude shows board overview

User: /anyt-next
→ Claude suggests top priority task

User: "Let's do it"
→ Claude picks task and helps implement
```

### Example 2: User Has Idea

```
User: "I want to add rate limiting"

Claude: "Great idea! Let me create a task."

User: Confirms

Claude runs: /anyt-create
Creates task interactively and offers to start working
```

### Example 3: Check Progress

```
User: /anyt-active
→ Claude shows current task
→ Offers to continue helping
```

---

## 🐛 Known Limitations

### Current Limitations
1. **Manual Invocation** - User must type slash commands (vs automatic)
2. **No Real-Time Updates** - Must refresh via commands
3. **Single Session** - Active task is session-local

### Workarounds
1. Users quickly learn to use `/anyt-next` habitually
2. Slash commands run very fast (< 1s)
3. Active task saved in `.anyt/active_task.json` for persistence

### Future: MCP Will Fix These
When we add MCP in Phase 2, we'll get:
- Auto task creation
- Real-time resource updates
- Proactive assistance

---

## 🎉 Benefits After Migration

1. **Database-Backed** - Full querying power
2. **Claude Integration** - Slash commands for workflow
3. **Smart Suggestions** - AI-powered task prioritization
4. **Audit Trail** - Complete event history
5. **Easy to Use** - Simple commands, no complex setup
6. **Team Ready** - Multi-user capable
7. **Scalable** - Handles thousands of tasks

---

## 📚 Related Documentation

- [CLI Usage Guide](./CLI_USAGE.md) - Complete CLI reference
- [Server API](./server_api.md) - Backend API docs
- [Claude Code Integration](./CLAUDE_CODE_INTEGRATION.md) - Setup guide (T7-30)

---

## 🔄 Phase 2: MCP Enhancement (Future)

After CLI integration is stable, we can add MCP for:

1. **Auto Task Creation** - Claude creates tasks as it works
2. **Progress Resources** - Real-time active task context
3. **Workspace Awareness** - Claude knows workspace state
4. **Git Integration** - Auto-link commits to tasks

Estimated effort: 10-15 hours (in addition to CLI work)

Benefits:
- More seamless experience
- Less manual slash command invocation
- Richer integration

Trade-off:
- More complex setup (MCP server config)
- Additional infrastructure to maintain

---

**Next Steps**: Start with T7-27 (JSON Output Enhancement)!

This gets basic integration working in just 4-6 hours of work.
