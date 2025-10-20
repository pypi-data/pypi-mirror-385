# AnyTask Development Tickets

This directory contains detailed specifications for all development tickets organized by phase.

## Ticket Structure

Each ticket follows this format:
- **Priority**: High/Medium/Low
- **Status**: Pending/In Progress/Completed
- **Description**: What needs to be built
- **Objectives**: Specific goals
- **Acceptance Criteria**: Checklist of requirements
- **Dependencies**: Required tickets
- **Estimated Effort**: Time estimate
- **Technical Notes**: Implementation guidance

## All Tickets by Phase

### Phase 1: Foundation & Setup (T1)
Foundation for backend, database, and authentication.

- [T1-1: Database Schema Design & Implementation](./T1-1-Database-Schema.md) - 6-8h
- [T1-2: API Foundation & Error Handling](./T1-2-API-Foundation.md) - 4-6h
- [T1-3: Authentication & Authorization Enhancement](./T1-3-Auth-Enhancement.md) - 5-7h

**Total Effort**: 15-21 hours

---

### Phase 2: Core Task Management API (T2)
Complete task management with repository pattern, dependencies, and audit trail.

**Core API Implementation (Completed):**
- [T2-1: Task CRUD API Implementation](./done/T2-1-Task-CRUD-API.md) - ✅ 8-10h
- [T2-1.5: Fix Test Infrastructure](./done/T2-1.5-Fix-Test-Infrastructure.md) - ✅ 3-4h
- [T2-1.6: Fix Deprecation Warnings](./done/T2-1.6-Fix-Deprecation-Warnings.md) - ✅ 2h
- [T2-1.7: Fix Type Checking](./done/T2-1.7-Fix-Type-Checking.md) - ✅ 2-3h

**Repository Pattern Migration (Completed):**
- [T2-5: Repository Pattern Foundation](./done/T2-5-Repository-Pattern-Foundation.md) - ✅ 4-6h
- [T2-6: Project Repository Implementation](./done/T2-6-Project-Repository-Implementation.md) - ✅ 6-8h
- [T2-7: Task Repository Implementation](./done/T2-7-Task-Repository-Implementation.md) - ✅ 12-16h
- [T2-8: Workspace Repository Implementation](./done/T2-8-Workspace-Repository-Implementation.md) - ✅ 8-10h
- [T2-9: Complete Repository Migration](./done/T2-9-Complete-Repository-Migration.md) - ✅ 12-16h

**Feature Extensions (After Repository Migration):**
- [T2-2: Task Dependencies & Relationship Management](./backlog/T2-2-Task-Dependencies.md) - 6-8h
- [T2-3: Attempts & Artifacts Tracking](./backlog/T2-3-Attempts-Artifacts.md) - 7-9h
- [T2-4: Event History & Audit Trail](./backlog/T2-4-Event-History.md) - 5-7h

**Total Effort**: 75-105 hours (includes repository refactoring)

---

### Phase 3: CLI Development (T3)
Full-featured command-line interface with multi-environment support.

- [T3-1: CLI Foundation & Setup](./backlog/T3-1-CLI-Foundation.md) - 10-12h
- [T3-2: CLI Task Commands](./backlog/T3-2-CLI-Task-Commands.md) - 10-12h
- [T3-3: CLI Board & Timeline Views](./backlog/T3-3-CLI-Board-Timeline.md) - 8-10h
- [T3-4: CLI AI Commands](./backlog/T3-4-CLI-AI-Commands.md) - 7-9h

**Total Effort**: 35-43 hours

---

### Phase 4: Agent Integration (T4)
AI agents for task decomposition, organization, and Claude Code integration.

- [T4-1: AI Task Decomposer Agent](./backlog/T4-1-AI-Decomposer.md) - 6-8h
- [T4-2: AI Organizer & Summarizer Agent](./backlog/T4-2-AI-Organizer.md) - 6-8h
- [T4-3: MCP Server for Claude Code Integration](./backlog/T4-3-MCP-Server.md) - 8-10h

**Total Effort**: 20-26 hours

---

### Phase 5: Web Dashboard (T5)
Modern web interface with drag-and-drop Kanban board.

- [T5-1: Web Dashboard Foundation](./T5-1-Web-Foundation.md) - 12-14h
- [T5-2: Web Board (Kanban) View](./T5-2-Web-Board-View.md) - 10-12h
- [T5-3: Web Task Detail View](./T5-3-Web-Task-Detail.md) - 12-14h

**Total Effort**: 34-40 hours

---

### Phase 6: Advanced Features (T6)
Production features: real-time collaboration, analytics, integrations.

- [T6-1: Real-time Sync & Collaboration](./T6-1-Realtime-Sync.md) - 10-12h
- [T6-2: Analytics & Reporting](./T6-2-Analytics-Reporting.md) - 14-16h
- [T6-3: External Integrations](./T6-3-Integrations.md) - 16-20h

**Total Effort**: 40-48 hours

---

## Total Project Effort

**Sum**: 219-279 hours (includes repository pattern migration)
**Average**: ~249 hours
**Estimated Duration**: 24-30 weeks (with parallelization)

**Note**: Repository pattern migration (T2-5 through T2-9) adds ~42-58 hours but provides significant long-term benefits:
- Type-safe codebase (no type: ignore in business logic)
- Better testability and maintainability
- Cleaner separation of concerns
- Foundation for caching and optimization

---

## Dependency Graph

```
T1-1 (Database) ✅
  ├─→ T1-2 (API Foundation) ✅
  │     └─→ T1-3 (Auth) ✅
  │           └─→ T2-1 (Task CRUD) ✅
  │                 ├─→ T2-1.5 (Fix Tests) ✅
  │                 ├─→ T2-1.6 (Fix Warnings) ✅
  │                 └─→ T2-1.7 (Fix Type Checking) ✅
  │                       └─→ T2-5 (Repository Foundation) ✅
  │                             └─→ T2-6 (Project Repository) ✅
  │                                   └─→ T2-7 (Task Repository) ✅
  │                                         └─→ T2-8 (Workspace Repository) ✅
  │                                               └─→ T2-9 (Complete Migration) ✅
  │                                                     ├─→ T2-2 (Dependencies) 🟡 NEXT
  │                                                     │     ├─→ T2-3 (Attempts)
  │                                                     │     │     └─→ T2-4 (Events)
  │                                                     │     │           ├─→ T3-1 (CLI Foundation)
  │                                                     │     │           │     ├─→ T3-2 (CLI Tasks)
  │                                                     │     │           │     │     ├─→ T3-3 (CLI Board)
  │                                                     │     │           │     │     └─→ T3-4 (CLI AI)
  │                                                     │     │           │           │     └─→ T4-1 (AI Decomposer)
  │                                                     │     │           │           │           ├─→ T4-2 (AI Organizer)
  │                                                     │     │           │           │           └─→ T4-3 (MCP Server)
  │                                                     │     │           │           └─→ T5-1 (Web Foundation)
  │                                                     │     │           │                 ├─→ T5-2 (Web Board)
  │                                                     │     │           │                 └─→ T5-3 (Web Detail)
  │                                                     │     │           │                       ├─→ T6-1 (Realtime)
  │                                                     │     │           │                       ├─→ T6-2 (Analytics)
  │                                                     │     │           │                       └─→ T6-3 (Integrations)
```

**Legend:**
- ✅ Completed
- 🟡 Next in sequence
- ⚪ Pending

---

## Critical Path

The critical path (longest dependency chain) is:

1. T1-1 → T1-2 → T1-3 → T2-1 → T2-1.7 → T2-5 → T2-6 → T2-7 → T2-8 → T2-9 → T2-2 → T2-3 → T2-4 → T3-1 → T3-2 → T3-4 → T4-3 → T5-1 → T5-3 → T6-2

**Critical Path Duration**: ~117-153 hours

**Note**: CLI development (T3-x) now comes before AI integration (T4-x) to enable direct backend access and testing first. Repository migration (T2-5 through T2-9) is complete ✅.

---

## Parallelization Opportunities

### Repository Migration Phase (T2-5 to T2-9) - COMPLETED ✅
**Sequential**: These were done in order to validate the pattern incrementally:
1. T2-5 (Foundation) ✅ - Set up infrastructure
2. T2-6 (Projects) ✅ - Proof of concept
3. T2-7 (Tasks) ✅ - Complex entity validation
4. T2-8 (Workspaces) ✅ - Complete core entities
5. T2-9 (Remaining) ✅ - Finish migration

### Can Work in Parallel (After Repository Migration)
- T2-2 (Dependencies) + T2-3 (Attempts) + T2-4 (Events)
- T3-2 (CLI Tasks) + T3-3 (CLI Board) (both depend on T3-1)
- T4-1 (AI Decomposer) + T4-2 (AI Organizer) (after T3-4)
- T5-2 (Web Board) + T5-3 (Web Detail)
- T6-1 (Realtime) + T6-2 (Analytics) + T6-3 (Integrations)

---

## Quick Start Guide

### For Contributors

1. **Pick a ticket**: Choose from available tickets in the current phase
2. **Check dependencies**: Ensure prerequisite tickets are completed
3. **Review the spec**: Read the full ticket document
4. **Create a branch**: `git checkout -b ticket/T1-1-database-schema`
5. **Implement**: Follow acceptance criteria
6. **Test**: Ensure all criteria met
7. **Submit PR**: Reference ticket number in PR title

### For Project Managers

1. **Track progress**: Use GitHub Projects or Linear
2. **Assign tickets**: Based on expertise and availability
3. **Monitor dependencies**: Ensure blockers are resolved
4. **Review milestones**: Check progress against roadmap
5. **Adjust priorities**: Based on feedback and requirements

---

## Status Legend

- 🟢 **Completed**: Ticket implemented, tested, and merged
- 🟡 **In Progress**: Currently being worked on
- 🔴 **Blocked**: Waiting on dependencies
- ⚪ **Pending**: Not started yet

---

## Related Documents

- [Project Roadmap](../ROADMAP.md)
- [Design Document](../design.md)
- [Project Pitch](../pitch.md)
- [Claude Code Usage Guide](../claude_code_usage.md)

---

**Last Updated**: 2025-10-15

---

## Recent Changes

### 2025-10-15: Task Restructuring - CLI Before AI
- **Phase reordering**: CLI development (T3) now comes before AI integration (T4)
- Rationale: CLI enables direct backend testing and user workflows first
- CLI enhanced with multi-environment support (dev, staging, prod)
- CLI supports remote server configuration and user directory settings
- Repository pattern migration (T2-5 through T2-9) completed ✅
- Repository pattern provides type-safe data access layer
- Next priority: T2-2 (Task Dependencies) to enable more complex workflows
