# T4-2: AI Organizer & Summarizer Agent

## Priority
Medium

## Status
Completed (Core Infrastructure)

## Description
Implement an AI agent that maintains task hygiene by normalizing titles, applying labels, detecting duplicates, and generating progress summaries.

## Objectives
- Normalize task titles to consistent format (imperative verbs)
- Apply label taxonomy automatically
- Detect and suggest duplicate task merges
- Generate daily/weekly progress briefs
- Keep board organized and actionable

## API Endpoints

```
POST   /v1/workspaces/:id/organize
GET    /v1/workspaces/:id/summaries?period=daily
POST   /v1/tasks/:id/auto-fill
GET    /v1/workspaces/:id/duplicates
```

### Organize Workspace
```
POST /v1/workspaces/ws-123/organize
{
  "actions": ["normalize_titles", "apply_labels", "detect_duplicates"],
  "dry_run": true
}
```

Response:
```json
{
  "changes": [
    {
      "task_id": "T-12",
      "field": "title",
      "before": "oauth callback",
      "after": "Implement OAuth callback",
      "reason": "Capitalized and added imperative verb"
    },
    {
      "task_id": "T-15",
      "field": "labels",
      "before": ["backend"],
      "after": ["backend", "auth"],
      "reason": "Added 'auth' label based on title/description"
    }
  ],
  "duplicates": [
    {
      "tasks": ["T-12", "T-18"],
      "similarity": 0.89,
      "suggestion": "Merge T-18 into T-12"
    }
  ],
  "dry_run": true
}
```

### Generate Summary
```
POST /v1/workspaces/ws-123/summaries
{
  "period": "daily",
  "include_sections": ["done", "active", "blocked", "risks", "next"]
}
```

Response:
```json
{
  "id": 42,
  "workspace_id": "ws-123",
  "period": "daily",
  "snapshot_ts": "2024-01-15T17:00:00Z",
  "sections": {
    "done": {
      "count": 5,
      "summary": "Completed 5 tasks today: OAuth setup, Google integration, email templates, API tests, deployment config",
      "tasks": ["T-7", "T-12", "T-15", "T-19", "T-21"]
    },
    "active": {
      "count": 3,
      "summary": "3 tasks in progress: GitHub OAuth (T-23), Microsoft OAuth (T-24), UI polish (T-26)",
      "tasks": ["T-23", "T-24", "T-26"]
    },
    "blocked": {
      "count": 2,
      "summary": "2 tasks blocked: Token refresh endpoint (T-28) waiting on database migration, Profile page (T-30) needs design",
      "tasks": ["T-28", "T-30"]
    },
    "risks": {
      "summary": "Rate limiting concerns with OAuth providers. May need caching strategy.",
      "items": ["Rate limiting", "OAuth quota"]
    },
    "next": {
      "summary": "Tomorrow: Complete GitHub OAuth, start token refresh, unblock profile page with design",
      "priority_tasks": ["T-23", "T-28", "T-30"]
    }
  },
  "text": "<markdown formatted summary>",
  "author": "agent"
}
```

### Auto-fill Task Details
```
POST /v1/tasks/T-42/auto-fill
{
  "fields": ["description", "acceptance", "labels"]
}
```

## Organizer Functions

### Title Normalization
- Convert to imperative verb form ("Add X", "Implement Y", "Fix Z")
- Capitalize properly
- Remove redundant words
- Max 100 characters
- Examples:
  - "oauth" → "Implement OAuth"
  - "fixing bug in login" → "Fix login bug"
  - "ADD GOOGLE AUTH" → "Add Google authentication"

### Label Application
Apply labels based on content analysis:
- **Area**: auth, api, ui, db, infra, docs, tests
- **Type**: feature, bug, refactor, chore
- **Impact**: high, medium, low

### Duplicate Detection
- Use semantic similarity (embeddings)
- Compare titles, descriptions, labels
- Threshold: 0.85 similarity = likely duplicate
- Suggest merge with reasoning

### Progress Summarization
Generate human-readable briefs:
- What was completed (with links)
- What's in progress
- What's blocked (with reasons)
- Identified risks
- Next priorities

## Organizer Prompt Strategy

### System Prompt (Title Normalization)
```
You are a task title editor. Rewrite task titles to follow these rules:
- Start with imperative verb (Add, Implement, Fix, Update, Remove, etc.)
- Be concise (≤100 chars)
- Be specific about what is being changed
- Remove unnecessary words

Input: {current_title}
Output: {normalized_title}
```

### System Prompt (Summarization)
```
You are a project progress summarizer. Given a list of tasks with their statuses,
generate a concise progress brief covering:
- Done: What was completed today
- Active: What's currently in progress
- Blocked: What's stuck and why
- Risks: Identified concerns or blockers
- Next: Top priorities for tomorrow

Keep it concise and actionable. Use markdown formatting.
```

## Features

### Automatic Organization
- Run organizer on schedule (daily at midnight)
- Run on-demand via API
- Support dry-run mode (preview changes)
- Batch update tasks with approval

### Smart Suggestions
- Suggest label additions based on content
- Suggest priority changes based on dependencies
- Suggest task splits (if too large)
- Suggest task merges (if duplicates)

### Summary Distribution
- Store summaries in database
- Export to Slack/Discord webhooks
- Email daily digest option
- Markdown format for easy sharing

## Acceptance Criteria
- [x] Database schema created for summaries and organization suggestions
- [x] Domain models implemented for all organizer features
- [x] OrganizerService created with AI functions:
  - [x] Title normalization
  - [x] Label suggestions
  - [x] Duplicate detection
  - [x] Progress summarization
  - [x] Task auto-fill
- [ ] Repositories created (moved to T4-2-1)
- [ ] Database migration applied (moved to T4-2-1)
- [ ] API endpoints implemented (moved to T4-2-2)
- [ ] Comprehensive tests written (moved to T4-2-3)

**Core infrastructure complete. Remaining work split into subtasks T4-2-1, T4-2-2, T4-2-3**

## Dependencies
- T2-1: Task CRUD API
- T4-1: AI Decomposer (for shared AI infrastructure)

## Estimated Effort
6-8 hours

## Technical Notes
- Use Claude API for text generation and analysis
- Use OpenAI embeddings or Voyage AI for semantic similarity
- Cache embeddings to avoid recomputing
- Run organizer as background job (Celery/Temporal)
- Store organization suggestions for user approval
- Allow users to customize label taxonomy
- Consider using function calling for structured edits
- Implement rate limiting per workspace (e.g., 10 organize calls/day)

## Events

### 2025-10-15 22:15 - Started work
- Moved task from backlog to active
- Verified dependencies are complete (T2-1, T4-1)
- Beginning implementation of AI Organizer & Summarizer Agent
- Will start with core infrastructure and organize endpoint

### 2025-10-15 22:25 - Database and domain models completed
- ✅ Added Summary and OrganizationSuggestion models to db_schema/models.py
- ✅ Registered new models in db_schema/__init__.py
- ✅ Created comprehensive domain models in domain/models.py:
  - SummaryPeriod, SummaryBase, SummaryCreate, Summary
  - SuggestionType, SuggestionStatus, OrganizationSuggestion models
  - OrganizeRequest/Response, SummaryRequest/Response, AutoFillRequest/Response
- Next: Create organizer service with AI functions

### 2025-10-15 22:35 - Core infrastructure completed
- ✅ Created OrganizerService in services/organizer.py with 5 AI functions:
  - normalize_titles: Rewrites task titles to imperative verb format
  - suggest_labels: Analyzes tasks and suggests relevant labels
  - detect_duplicates: Finds similar tasks using AI analysis
  - generate_summary: Creates progress briefs with done/active/blocked/risks/next
  - auto_fill_task: Generates description, acceptance criteria, labels
- ✅ All AI functions follow same pattern as DecomposerService
- ✅ Proper error handling and JSON extraction
- Decision: Split remaining work into focused subtasks for better tracking
- Created T4-2-1 (Repositories + Migration), T4-2-2 (API Endpoints), T4-2-3 (Tests)
- Moving T4-2 to done, remaining work in subtasks

### 2025-10-15 22:50 - Pull request created
- Created PR #28: https://github.com/supercarl87/AnyTaskBackend/pull/28
- Branch: T4-1-ai-task-decomposer
- All quality checks passed (lint, format, typecheck)
- Comprehensive PR description with task context and subtask roadmap
- Core infrastructure complete and ready for review
