# AnyTask CLI Development Tasks

This directory contains task specifications for the AnyTask CLI project organized by phase and status.

## Task Structure

Each task follows this format:
- **Priority**: High/Medium/Low
- **Status**: Pending/In Progress/Completed
- **Description**: What needs to be built
- **Objectives**: Specific goals
- **Acceptance Criteria**: Checklist of requirements
- **Dependencies**: Required tasks
- **Estimated Effort**: Time estimate
- **Technical Notes**: Implementation guidance

## Directory Structure

```
.anyt/tasks/
├── README.md        # This file
├── active/          # Currently active task (max 1)
├── backlog/         # Tasks pending work
├── done/            # Completed tasks
└── cancelled/       # Cancelled tasks
```

## CLI Development Phases

### Phase 3: CLI Development (T3)
Full-featured command-line interface with multi-environment support.

**Completed Tasks:**
- [T3-1: CLI Foundation & Setup](./done/T3-1-CLI-Foundation.md) - ✅ 10-12h
- [T3-2: CLI Task Commands](./done/T3-2-CLI-Task-Commands.md) - ✅ 10-12h
  - [T3-2.1: CLI Task Commands Core](./done/T3-2.1-CLI-Task-Commands-Core.md) - ✅
  - [T3-2.2: Task Dependency Commands](./done/T3-2.2-Task-Dependency-Commands.md) - ✅
  - [T3-2.3: Task Picker Active Task](./done/T3-2.3-Task-Picker-Active-Task.md) - ✅
  - [T3-2.4: Advanced Task Features](./done/T3-2.4-Advanced-Task-Features.md) - ✅
- [T3-3: CLI Board & Timeline Views](./done/T3-3-CLI-Board-Timeline.md) - ✅ 8-10h
- [T3-4: CLI AI Commands](./done/T3-4-CLI-AI-Commands.md) - ✅ 7-9h

**Total Effort**: 35-43 hours ✅

---

### Phase 4: Agent Integration (T4)
AI agents for task decomposition, organization, and Claude Code integration.

**Completed Tasks:**
- [T4-1: AI Task Decomposer Agent](./done/T4-1-AI-Decomposer.md) - ✅ 6-8h
- [T4-2: AI Organizer & Summarizer Agent](./done/T4-2-AI-Organizer.md) - ✅ 6-8h
- [T4-4: Goal Decomposer Enhancements](./done/T4-4-Goal-Decomposer-Enhancements.md) - ✅

**Pending Tasks:**
- T4-3: MCP Server for Claude Code Integration - 8-10h

**Total Effort**: 20-26 hours

---

### Phase 7: CLI Enhancements (T7)
Advanced CLI features, performance improvements, and bug fixes.

**Completed Tasks:**
- [T7-6: Move Config to Anyt Folder](./done/T7-6-Move-Config-to-Anyt-Folder.md) - ✅
- [T7-16: CLI Workflow MVP](./done/T7-16-CLI-Workflow-MVP.md) - ✅
- [T7-27: CLI JSON Output Enhancement](./done/T7-27-CLI-JSON-Output-Enhancement.md) - ✅
- [T7-29: CLI Smart Task Suggest](./done/T7-29-CLI-Smart-Task-Suggest.md) - ✅
- [T7-30: Claude Code Documentation CLI](./done/T7-30-Claude-Code-Documentation-CLI.md) - ✅
- [T7-31: Migration Script CLI](./done/T7-31-Migration-Script-CLI.md) - ✅
- [T7-32: CLI Label Management](./done/T7-32-CLI-Label-Management.md) - ✅
- [T7-33: CLI TaskView Management](./done/T7-33-CLI-TaskView-Management.md) - ✅
- [T7-34: Workspace Identifier 3 Char Limit](./done/T7-34-Workspace-Identifier-3-Char-Limit.md) - ✅
- [T7-35: Workspace Scoped Task Identifiers](./done/T7-35-Workspace-Scoped-Task-Identifiers.md) - ✅
- [T7-36: Fix E2E Test Identifier Generation](./done/T7-36-Fix-E2E-Test-Identifier-Generation.md) - ✅
- [T7-38: CLI AI Commands Backend Integration](./done/T7-38-CLI-AI-Commands-Backend-Integration.md) - ✅
- [T7-39: CLI Board View Enhancements](./done/T7-39-CLI-Board-View-Enhancements.md) - ✅
- [T7-40: CLI Interactive Task Picker](./done/T7-40-CLI-Interactive-Task-Picker.md) - ✅
- [T7-43: CLI Project Creation Management](./done/T7-43-CLI-Project-Creation-Management.md) - ✅
- [T7-44: Fix Task Show Identifier Resolution](./done/T7-44-Fix-Task-Show-Identifier-Resolution.md) - ✅
- [T7-45: Fix Makefile Typecheck Verbosity](./done/T7-45-Fix-Makefile-Typecheck-Verbosity.md) - ✅
- [T7-46: Fix MyPy Type Checking Errors](./done/T7-46-Fix-MyPy-Type-Checking-Errors.md) - ✅

**Completed T7 Tasks (Recent)**:
- [T7-47 through T7-56]: Architecture Migration (typed clients, services, models)
- [T7-57: Agent Key in Workspace Configuration](./done/T7-57-Agent-Key-Workspace-Config.md) - ✅ Oct 20, 2025

**Active Tasks:**
- None currently

---

## Task ID Convention

Task IDs follow the format: `T{stage}-{id}`

- **T3-x**: CLI Foundation tasks
- **T4-x**: Agent Integration tasks
- **T7-x**: CLI Enhancement tasks

When creating a new task:
1. Check the highest ID in the current phase
2. Increment by 1 for new tasks in the same phase
3. For new phases, start at ID 1

Example: After T7-63, the next CLI enhancement task would be T7-64.

---

## Workflow

### Starting a Task
1. Check `backlog/` for pending tasks
2. Move task file to `active/`
3. Update status to "In Progress"
4. Add event entry marking start of work

### Completing a Task
1. Verify all acceptance criteria are met
2. Update status to "Completed"
3. Add completion event entry
4. Move task file from `active/` to `done/`

### Cancelling a Task
1. Update status to "Cancelled"
2. Add cancellation event with reason
3. Move task file from `active/` or `backlog/` to `cancelled/`

---

## Current Status

**CLI Development**: Complete ✅
- Full command structure implemented
- Multi-environment support
- Task CRUD operations
- Board and timeline views
- AI-powered commands
- MCP server integration
- **Architecture Migration Complete** (T7-47 through T7-57)
  - Typed API clients with Pydantic models
  - Service layer for business logic
  - Clean separation of concerns
  - Agent key in workspace config

**Active Work**: Test suite fixes

**Next Steps**: Fix remaining 61 unit tests, then new features

---

**Last Updated**: 2025-10-20 21:30

---

## Current Sprint: Test Migration After T7-56

After completing T7-56 (Remove Old Client), we migrated to typed API clients. This requires updating all unit tests to use Pydantic models instead of dicts.

**Progress**: 61 tests remaining to fix (down from 80)

### Completed in This Sprint

✅ **T7-57: Agent Key in Workspace Configuration** (Oct 20, 2025)
- Added `agent_key` field to `WorkspaceConfig`
- Fixed bug in `get_effective_config()` priority logic
- Created comprehensive test suite (7 tests)
- PR #42: https://github.com/supercarl87/AnyTaskCLI/pull/42

### Backlog: Prioritized Development Roadmap

#### **Phase 1: Test Suite Completion** (IMMEDIATE PRIORITY)

Fix remaining 61 unit tests to ensure codebase stability. Each task is a separate PR.

1. **[T7-59: Fix Task CRUD Tests](./backlog/T7-59-Fix-Task-CRUD-Tests.md)** - 🔴 HIGH PRIORITY
   - Fix 17 tests in `test_task_crud.py`
   - Most critical test file (core CRUD operations)
   - Effort: 2-3h
   - **Recommended: Start with this**

2. **[T7-60: Fix Visualization Tests](./backlog/T7-60-Fix-Visualization-Tests.md)** - 🔴 HIGH PRIORITY
   - Fix 14 tests in `test_visualization_commands.py`
   - Board, timeline, summary, graph commands
   - User-facing features
   - Effort: 2-3h

3. **[T7-61: Fix Project and Dependency Tests](./backlog/T7-61-Fix-Project-and-Dependency-Tests.md)** - 🔴 HIGH PRIORITY
   - Fix 9 tests in `test_project_commands.py`
   - Fix 7 tests in `test_task_dependencies.py`
   - Total: 16 tests
   - Entity management features
   - Effort: 2-3h

4. **[T7-62: Fix Interactive and Preference Tests](./backlog/T7-62-Fix-Interactive-and-Preference-Tests.md)** - 🟡 MEDIUM PRIORITY
   - Fix 8 tests in `test_task_pick_interactive.py`
   - Fix 6 tests in `test_preference_commands.py`
   - Total: 14 tests (smaller, less critical files)
   - Effort: 1-2h

**Phase 1 Total**: 61 tests across 4 tasks (~8-12 hours)

#### **Phase 2: New Features** (AFTER TEST FIXES)

5. **[T7-63: Public Task ID CLI Support](./backlog/T7-63-Public-Task-ID-CLI-Support.md)** - 🔴 HIGH PRIORITY
   - Add support for 9-digit public IDs in CLI
   - Add `anyt task share <id>` command
   - Support both identifier formats (DEV-123 and 123456789)
   - Effort: 3-4h
   - **Status**: ⏸️ Blocked by backend T11-31 (Public Task ID System)
   - **Action**: Wait for backend API deployment

#### **Phase 3: Backend Issues** (TRACK BUT DON'T BLOCK)

- **[BACKEND-BUG: Workspace-Scoped Task Endpoint 404](./backlog/BACKEND-BUG-Workspace-Scoped-Task-Endpoint-404.md)**
  - Backend team issue
  - CLI has workaround in place
  - Track for backend resolution

### Infrastructure Completed

✅ Created helper functions in `tests/cli/unit/conftest.py`:
- `create_test_task()` - Creates Task instances with defaults
- `create_test_project()` - Creates Project instances with defaults
- `auto_patch_workspace_config()` - Global fixture for test isolation

✅ Updated all API client references from old `APIClient` to typed clients

✅ Fixed 27 tests (test_ai_commands.py, test_task_list.py)

✅ Created comprehensive `TEST_FIX_GUIDE.md` documentation

### Quick Start for Test Fixes

Each task follows the same pattern:

1. **Add imports**:
   ```python
   from cli.models.common import Status, Priority
   from cli.models.task import Task
   from cli.schemas.pagination import PaginatedResponse
   from tests.cli.unit.conftest import create_test_task
   ```

2. **Replace dict mocks with Pydantic models**:
   ```python
   # OLD: return_value={"id": 1, "title": "Task", "status": "todo"}
   # NEW: return_value=create_test_task(id=1, title="Task", status=Status.TODO)
   ```

3. **Wrap list_tasks in PaginatedResponse**:
   ```python
   # OLD: return_value={"items": [...], "total": 1}
   # NEW: return_value=PaginatedResponse[Task](items=[...], total=1, limit=50, offset=0)
   ```

See `TEST_FIX_GUIDE.md` for complete patterns and examples.

---

## Development Roadmap Summary

### ✅ Completed Recently
- T7-57: Agent Key in Workspace Configuration (Oct 20, 2025)
  - 7 comprehensive tests added
  - PR #42 ready for review

### 🎯 Current Focus: Test Suite Completion
**Goal**: Fix 61 remaining unit tests from architecture migration

**Recommended Order**:
1. T7-59 (Task CRUD) - 17 tests - **START HERE**
2. T7-60 (Visualization) - 14 tests
3. T7-61 (Project & Dependencies) - 16 tests
4. T7-62 (Interactive & Preferences) - 14 tests

**Why This Order?**
- T7-59 contains the most critical tests (core CRUD operations)
- Each task is independent and can be a separate PR
- Builds confidence incrementally
- Most important features tested first

### 🚀 Next Up: New Features
- T7-63: Public Task ID CLI Support (blocked by backend T11-31)
  - Wait for backend API deployment
  - Ready to implement once backend is available

### 📊 Progress Tracking
- **Architecture Migration**: ✅ Complete (T7-47 through T7-57)
- **Test Suite Health**: 🟡 In Progress (61 tests to fix)
- **New Features**: ⏸️ On Hold (waiting for backend)

**Estimated Time to Green Tests**: 8-12 hours across 4 PRs

---

## Quick Start Guide

### To Start Next Task:

```bash
# 1. Sync with latest
git fetch origin
git checkout main
git pull

# 2. Create new branch
git checkout -b anyt-next-task-id

# 3. Move task from backlog to active
mv .anyt/tasks/backlog/T7-XX-Task-Name.md .anyt/tasks/active/

# 4. Update task status to "In Progress"
# Edit .anyt/tasks/active/T7-XX-Task-Name.md

# 5. Add event entry documenting start

# 6. Begin implementation!
```

### After Completing Task:

```bash
# 1. Run quality checks
make format && make lint && make typecheck

# 2. Commit changes
git add -A
git commit -m "feat(T7-XX): Task title"

# 3. Push and create PR
git push -u origin anyt-next-task-id
gh pr create --title "T7-XX: Task title" --body "..."

# 4. Move task to done
mv .anyt/tasks/active/T7-XX-Task-Name.md .anyt/tasks/done/

# 5. Update task status to "Completed"
```

---

**Need Help?** Check `TEST_FIX_GUIDE.md` for detailed patterns and examples.

