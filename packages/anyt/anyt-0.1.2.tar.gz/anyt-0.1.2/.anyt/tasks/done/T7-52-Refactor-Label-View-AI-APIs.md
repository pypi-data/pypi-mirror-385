# T7-52: Refactor Label, View, and AI APIs

**Priority**: Medium
**Status**: Completed
**Created**: 2025-10-20
**Parent**: T7-48 (CLI Architecture Improvements)
**PR**: https://github.com/supercarl87/AnyTaskCLI/pull/32

## Description

Create `LabelsAPIClient`, `ViewsAPIClient`, and `AIAPIClient` to complete the client refactoring. After this task, all API operations will have typed clients available.

## Objectives

- Implement LabelsAPIClient for label management
- Implement ViewsAPIClient for task view management
- Implement AIAPIClient for AI-powered operations
- Complete the client layer refactoring

## Acceptance Criteria

- [x] Create `src/cli/client/labels.py`:
  - [x] `list_labels(workspace_id: int) -> list[Label]`
  - [x] `create_label(workspace_id: int, label: LabelCreate) -> Label`
  - [x] `get_label(workspace_id: int, label_id: int) -> Label`
  - [x] `update_label(workspace_id: int, label_id: int, updates: LabelUpdate) -> Label`
  - [x] `delete_label(workspace_id: int, label_id: int) -> None`
- [x] Create `src/cli/client/views.py`:
  - [x] `list_task_views(workspace_id: int) -> list[TaskView]`
  - [x] `create_task_view(workspace_id: int, view: TaskViewCreate) -> TaskView`
  - [x] `get_task_view(workspace_id: int, view_id: int) -> TaskView`
  - [x] `get_task_view_by_name(workspace_id: int, name: str) -> TaskView | None`
  - [x] `get_default_task_view(workspace_id: int) -> TaskView | None`
  - [x] `update_task_view(workspace_id: int, view_id: int, updates: TaskViewUpdate) -> TaskView`
  - [x] `delete_task_view(workspace_id: int, view_id: int) -> None`
- [x] Create `src/cli/client/ai.py`:
  - [x] `decompose_goal(goal: str, workspace_id: int, ...) -> GoalDecomposition`
  - [x] `organize_workspace(workspace_id: int, actions: list[str], ...) -> OrganizationResult`
  - [x] `fill_task_details(identifier: str, fields: list[str]) -> TaskAutoFill`
  - [x] `get_ai_suggestions(workspace_id: int) -> AISuggestions`
  - [x] `review_task(identifier: str) -> TaskReview`
  - [x] `generate_summary(workspace_id: int, period: str) -> WorkspaceSummary`
  - [x] `get_ai_usage(workspace_id: int | None) -> AIUsage`
- [x] All methods return typed models
- [x] Type checking passes: `make typecheck`
- [x] Unit tests for all three clients
- [x] Old client.py remains untouched

## Dependencies

- T7-49: Models and Schemas Foundation
- T7-50: Refactor BaseClient and Tasks API

## Estimated Effort

3-4 hours

## Technical Notes

### Client Implementations

Follow the established BaseAPIClient pattern for all three clients.

### AI Models

Need to define additional models for AI responses:
- `GoalDecomposition` - result of goal decomposition
- `OrganizationResult` - result of workspace organization
- `TaskAutoFill` - auto-filled task details
- `AISuggestions` - AI task suggestions
- `TaskReview` - AI task review
- `WorkspaceSummary` - workspace summary
- `AIUsage` - AI usage statistics

These should be added to `models/ai.py` or similar.

### Testing Strategy

- Mock all AI endpoints
- Validate response parsing
- Test timeout handling (AI endpoints may be slow)

## Events

### 2025-10-20 16:00 - Created
- Broken out from T7-48
- Completes client layer refactoring

### 2025-10-20 16:10 - Started work
- Moved task from backlog to active
- Created new branch: T7-52-refactor-label-view-ai-apis
- Dependencies T7-49 and T7-50 confirmed completed
- Beginning implementation with Labels API client

### 2025-10-20 16:45 - Completed
- Implemented LabelsAPIClient with all CRUD operations
- Implemented ViewsAPIClient with all operations including get_by_name and get_default
- Created AI response models in src/cli/models/ai.py:
  - OrganizationResult, TaskAutoFill, AISuggestions, TaskReview, WorkspaceSummary, AIUsage
- Implemented AIAPIClient with all 7 AI operations
- Updated src/cli/client/__init__.py to export new clients
- Updated src/cli/models/__init__.py to export AI models
- All type checking passes (make typecheck)
- Created comprehensive unit tests:
  - test_labels_client.py (6 tests)
  - test_views_client.py (10 tests)
  - test_ai_client.py (8 tests)
- All 232 unit tests pass
- Old client.py remains untouched as old_client.py
- Task moved to done/
