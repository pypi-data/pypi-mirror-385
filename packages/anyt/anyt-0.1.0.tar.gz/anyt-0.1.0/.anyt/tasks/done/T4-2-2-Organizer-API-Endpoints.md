# T4-2-2: Organizer API Endpoints

## Priority
Medium

## Status
Completed

## Description
Implement REST API endpoints for workspace organization, summary generation, task auto-fill, and duplicate detection. This exposes the OrganizerService functionality through the API.

## Objectives
- Implement POST /v1/workspaces/:id/organize endpoint
- Implement POST /v1/workspaces/:id/summaries endpoint
- Implement GET /v1/workspaces/:id/summaries (list endpoint)
- Implement POST /v1/tasks/:id/auto-fill endpoint
- Implement GET /v1/workspaces/:id/duplicates endpoint
- Add proper authentication and authorization
- Return standardized API responses

## Acceptance Criteria
- [ ] POST /v1/workspaces/:id/organize endpoint
  - [ ] Accepts OrganizeRequest (actions, dry_run)
  - [ ] Returns OrganizeResponse with changes and duplicates
  - [ ] Dry-run mode previews without applying changes
  - [ ] Non-dry-run applies changes and creates OrganizationSuggestion records
- [ ] POST /v1/workspaces/:id/summaries endpoint
  - [ ] Accepts SummaryRequest (period, include_sections)
  - [ ] Generates summary using OrganizerService
  - [ ] Stores summary in database
  - [ ] Returns SummaryResponse with all sections
- [ ] GET /v1/workspaces/:id/summaries endpoint
  - [ ] Lists summaries for workspace
  - [ ] Filter by period (daily, weekly, monthly)
  - [ ] Pagination support
- [ ] POST /v1/tasks/:id/auto-fill endpoint
  - [ ] Accepts AutoFillRequest (fields)
  - [ ] Returns AutoFillResponse with filled fields
  - [ ] Does not modify task unless explicitly requested
- [ ] GET /v1/workspaces/:id/duplicates endpoint
  - [ ] Returns list of duplicate task groups
  - [ ] Includes similarity scores and merge suggestions
- [ ] All endpoints require authentication
- [ ] Workspace access verified for all endpoints
- [ ] Events logged for organization actions

## Dependencies
- T4-2-1: Organizer Repositories & Migration

## Estimated Effort
3-4 hours

## Technical Notes
- Create routes/v1/organizer.py for new endpoints
- Use RepositoryFactory dependency injection
- Instantiate OrganizerService in route handlers
- Follow pattern from routes/v1/goals.py
- Use require_workspace_access for authorization
- Log events for title_normalized, labels_added, summary_generated
- Return SuccessResponse for all successful operations

## Events

### 2025-10-16 - Started work
- Moved task from backlog to active
- Created new branch T4-2-2-organizer-api-endpoints
- Beginning implementation of Organizer API endpoints

### 2025-10-16 - Completed implementation
- Created src/backend/routes/v1/organizer.py with all 5 endpoints
- Implemented POST /v1/workspaces/:id/organize with dry-run support
- Implemented POST /v1/workspaces/:id/summaries for summary generation
- Implemented GET /v1/workspaces/:id/summaries with period filtering
- Implemented POST /v1/tasks/:id/auto-fill for AI-powered field completion
- Implemented GET /v1/workspaces/:id/duplicates for duplicate detection
- Registered workspace_router and task_router in routes/v1/__init__.py
- All endpoints use proper authentication and authorization
- All endpoints return standardized SuccessResponse
- Fixed type checking issues with mypy
- All linting and formatting checks pass
- Committed changes and pushed to branch T4-2-2-organizer-api-endpoints
- Created PR #31: https://github.com/supercarl87/AnyTaskBackend/pull/31
- Task completed successfully
