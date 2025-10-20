# CLI Enhancement Roadmap

**Current Version**: MVP (Phase/Template Support)
**Last Updated**: 2025-01-18

This document outlines planned enhancements to the AnyTask CLI tool beyond the MVP.

---

## MVP Features (Completed)

- ✅ Task creation from universal template
- ✅ Phase field for task organization
- ✅ Note/event appending to task description
- ✅ Template management (init, list, show)
- ✅ Phase-based filtering and board views
- ✅ Markdown-formatted task descriptions
- ✅ Editor integration for task creation

**Philosophy**: Use description field for all task content in markdown format. Keep it simple and flexible.

---

## Phase 1: Structured Task Metadata (4-6 weeks)

**Goal**: Add database fields for objectives, acceptance criteria, and technical notes instead of parsing markdown.

### Features
- **Backend**: Add `objectives`, `acceptance_criteria`, `technical_notes` JSONB fields to Task model
- **API**: Endpoints to manage these fields separately
- **CLI**:
  ```bash
  anyt task add "Title" \
    --objectives "Obj 1" "Obj 2" \
    --acceptance "Criterion 1" "Criterion 2"

  anyt task check DEV-42 1  # Mark acceptance criterion #1 as done
  anyt task check DEV-42 --all  # Mark all criteria as done

  # Show progress
  anyt task show DEV-42
  # Acceptance Criteria: 3/5 completed (60%)
  ```

**Benefits**:
- Queryable acceptance criteria completion
- Better progress tracking
- Structured data for reporting

**Estimated Effort**: 8-10 hours

---

## Phase 2: Milestone Management (3-4 weeks)

**Goal**: Replace string `phase` field with proper Milestone entity.

### Features
- **Backend**: Create `milestones` table linked to workspace
- **API**: CRUD endpoints for milestones
- **CLI**:
  ```bash
  anyt milestone create "Phase 3: CLI Development" --identifier T3
  anyt milestone list
  anyt milestone progress T3

  anyt task add "CLI Foundation" --milestone T3
  anyt board --milestone T3
  ```

**Benefits**:
- Structured milestone tracking
- Milestone-level progress reporting
- Better organization for large projects

**Estimated Effort**: 10-12 hours

---

## Phase 3: Advanced Templates (2-3 weeks)

**Goal**: Support multiple template types and custom fields.

### Features
- **Template Types**:
  - Feature template (current default)
  - Bug fix template
  - Research/spike template
  - Documentation template
- **Custom Fields**: User-defined fields in templates
- **CLI**:
  ```bash
  anyt template create "Bug Fix" --based-on default
  anyt template edit "Bug Fix"

  anyt task add "Fix auth bug" --template "Bug Fix"
  ```

**Benefits**:
- Tailored workflows for different task types
- Team-specific templates
- Consistency across projects

**Estimated Effort**: 6-8 hours

---

## Phase 4: Offline Sync & Conflict Resolution (6-8 weeks)

**Goal**: Work offline with local SQLite cache and sync when online.

### Features
- **Local Cache**: SQLite database mirrors server state
- **Sync Queue**: Track offline changes
- **Conflict Resolution**: 3-way merge for conflicts
- **CLI**:
  ```bash
  anyt sync  # Bi-directional sync
  anyt sync status  # Show pending changes
  anyt sync push  # Upload local changes
  anyt sync pull  # Download remote changes

  # Work offline
  anyt task add "Offline task" --offline
  anyt task done DEV-42 --offline
  ```

**Benefits**:
- Work without internet connection
- Faster operations (read from cache)
- Conflict-aware collaboration

**Estimated Effort**: 16-20 hours

**Note**: Referenced as T7-2 and T7-15 in task system.

---

## Phase 5: Subtasks & Hierarchies (3-4 weeks)

**Goal**: Support parent-child task relationships with progress rollup.

### Features
- **Backend**: Enhanced parent_id support with progress calculation
- **API**: Subtask management endpoints
- **CLI**:
  ```bash
  anyt task add-subtask DEV-42 "Write tests"
  anyt task add-subtask DEV-42 "Update docs"

  anyt task show DEV-42 --show-subtasks
  # Subtasks: 2/5 completed (40%)

  anyt task tree DEV-42  # Show task hierarchy
  ```

**Benefits**:
- Break down large tasks
- Track progress on complex work
- Better project planning

**Estimated Effort**: 8-10 hours

---

## Phase 6: Advanced Querying & Saved Views (2-3 weeks)

**Goal**: Complex filtering with saved views using backend TaskView entity.

### Features
- **Backend**: Already has TaskView table
- **CLI**:
  ```bash
  # Complex queries
  anyt task list \
    --phase T7 \
    --priority 1,2 \
    --labels bug,urgent \
    --assigned me

  # Full-text search
  anyt task search "authentication"
  anyt task search "OAuth" --in title,description

  # Saved views (uses backend TaskView)
  anyt view create "My Urgent" \
    --status inprogress,todo \
    --priority-min 1 \
    --assigned me

  anyt view list
  anyt task list --view "My Urgent"
  anyt board --view "My Urgent"
  ```

**Benefits**:
- Quick access to relevant tasks
- Personalized workflows
- Reduced cognitive load

**Estimated Effort**: 6-8 hours

---

## Phase 7: Task Import & Export (1-2 weeks)

**Goal**: Import existing tasks from markdown and export for backup.

### Features
- **Import**:
  ```bash
  anyt import markdown .anyt/tasks/ --dry-run
  anyt import markdown .anyt/tasks/done/ --status done
  ```
- **Export**:
  ```bash
  anyt export markdown ./backup/
  anyt export csv tasks.csv
  anyt export json tasks.json
  ```

**Benefits**:
- Migrate from file-based system
- Backup task data
- Integration with other tools

**Estimated Effort**: 10-12 hours

---

## Phase 8: Workflow Automation (2-3 weeks)

**Goal**: Automate common workflows and task transitions.

### Features
- **Smart Suggestions**:
  ```bash
  anyt task next  # Suggest next task based on priority/dependencies
  anyt task pick-next  # Auto-pick suggested task
  ```

- **Hooks**:
  ```bash
  anyt hook create on-task-done "anyt sync"
  anyt hook create on-status-change "git commit -m 'Update task status'"
  ```

- **Auto-transitions**:
  ```bash
  anyt task done DEV-42
  # Automatically:
  # - Marks as done
  # - Clears from active
  # - Suggests next task
  # - Triggers hooks
  ```

**Benefits**:
- Reduced manual work
- Consistent workflows
- Better integration with dev tools

**Estimated Effort**: 8-10 hours

---

## Phase 9: Enhanced Visualization (3-4 weeks)

**Goal**: Rich terminal UI with charts and graphs.

### Features
- **Burndown Charts**:
  ```bash
  anyt chart burndown --phase T7
  anyt chart velocity --last 4-weeks
  ```

- **Interactive Board** (using textual):
  ```bash
  anyt board --interactive
  # Drag-and-drop tasks between columns
  # Keyboard shortcuts for quick actions
  ```

- **Dependency Graph**:
  ```bash
  anyt graph DEV-42 --format ascii
  anyt graph --all --format dot | dot -Tpng > graph.png
  ```

**Benefits**:
- Visual progress tracking
- Better planning insights
- Identify bottlenecks

**Estimated Effort**: 12-16 hours

---

## Phase 10: Team Collaboration Features (4-6 weeks)

**Goal**: Better support for team workflows.

### Features
- **Team Views**:
  ```bash
  anyt team list  # List team members
  anyt team tasks @john  # Show John's tasks
  anyt team board  # Board for entire team
  ```

- **Notifications**:
  ```bash
  anyt notify  # Show mentions and updates
  anyt watch DEV-42  # Watch task for changes
  ```

- **Comments** (when backend supports):
  ```bash
  anyt comment DEV-42 "Great work!"
  anyt comments DEV-42  # List comments
  ```

**Benefits**:
- Better team coordination
- Reduced context switching
- Improved communication

**Estimated Effort**: 10-12 hours

---

## Long-term Vision (6-12 months)

### Integration Features
- **GitHub Integration**: Link PRs, sync issues
- **Linear Integration**: Import/sync with Linear
- **Jira Import**: Migration tool from Jira
- **Slack Integration**: Task notifications and updates
- **Calendar Integration**: Due dates in calendar

### AI Features
- **Task Suggestions**: AI-suggested task breakdowns
- **Smart Scheduling**: Optimal task ordering
- **Automated Categorization**: Auto-label and prioritize
- **Progress Predictions**: Estimate completion dates

### Mobile Support
- **CLI Web UI**: Access CLI features via web interface
- **Mobile App**: iOS/Android native apps
- **REST API**: Full REST API for custom integrations

---

## Contributing

Have ideas for CLI enhancements?

1. Add suggestions to this document
2. Create issues with `enhancement` label
3. Discuss in team meetings

---

## Version History

- **v0.1.0** (2025-01-18): MVP - Phase support, templates, notes
- **v0.2.0** (Planned): Structured metadata (objectives, acceptance criteria)
- **v0.3.0** (Planned): Milestone management
- **v0.4.0** (Planned): Offline sync
- **v1.0.0** (Planned): Full feature parity with file-based system
