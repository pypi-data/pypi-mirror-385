# T7-49: Models and Schemas Foundation

**Priority**: High
**Status**: Completed
**Created**: 2025-10-20
**Completed**: 2025-10-20
**Parent**: T7-48 (CLI Architecture Improvements)
**PR**: https://github.com/supercarl87/AnyTaskCLI/pull/28

## Description

Create the foundational type layer for the CLI by defining Pydantic models for all domain entities and API response schemas. This establishes the type system that subsequent refactoring tasks will use.

This task creates new modules alongside existing code without breaking anything - it's purely additive.

## Objectives

- Define Pydantic models for all domain entities
- Create API response wrapper schemas
- Establish enums for common types (Status, Priority)
- Provide strong typing for all API interactions

## Acceptance Criteria

- [ ] Create `src/cli/models/` directory structure:
  - [ ] `models/__init__.py` - Export all models
  - [ ] `models/common.py` - Status, Priority enums, shared types
  - [ ] `models/task.py` - Task, TaskCreate, TaskUpdate, TaskFilters
  - [ ] `models/workspace.py` - Workspace, WorkspaceCreate
  - [ ] `models/project.py` - Project, ProjectCreate
  - [ ] `models/label.py` - Label, LabelCreate, LabelUpdate
  - [ ] `models/user.py` - User, UserPreferences
  - [ ] `models/goal.py` - Goal, GoalDecomposition
  - [ ] `models/view.py` - TaskView, TaskViewCreate, TaskViewUpdate
  - [ ] `models/dependency.py` - TaskDependency
- [ ] Create `src/cli/schemas/` directory structure:
  - [ ] `schemas/__init__.py` - Export all schemas
  - [ ] `schemas/responses.py` - SuccessResponse[T], ErrorResponse
  - [ ] `schemas/pagination.py` - PaginatedResponse[T], PaginationParams
  - [ ] `schemas/filters.py` - Common filter types
- [ ] All models have proper type hints
- [ ] All models include docstrings
- [ ] Models match current API contract from backend
- [ ] Enums cover all valid values (status, priority, etc.)
- [ ] Models support JSON serialization/deserialization
- [ ] Type checking passes: `make typecheck`
- [ ] Code formatted: `make format`
- [ ] No breaking changes to existing code

## Dependencies

None - this is the foundation task

## Estimated Effort

3-4 hours

## Technical Notes

### Directory Structure
```
src/cli/
├── models/
│   ├── __init__.py
│   ├── common.py          # Enums and shared types
│   ├── task.py
│   ├── workspace.py
│   ├── project.py
│   ├── label.py
│   ├── user.py
│   ├── goal.py
│   ├── view.py
│   └── dependency.py
└── schemas/
    ├── __init__.py
    ├── responses.py       # API response wrappers
    ├── pagination.py      # Pagination types
    └── filters.py         # Common filter types
```

### Key Models to Implement

**Common Enums** (`models/common.py`):
```python
from enum import Enum

class Status(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"

class Priority(int, Enum):
    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    HIGHEST = 2
```

**Task Models** (`models/task.py`):
- `Task` - Full task with all fields
- `TaskCreate` - Payload for creating tasks
- `TaskUpdate` - Payload for updating tasks
- `TaskFilters` - Query filters for listing tasks

**Response Schemas** (`schemas/responses.py`):
- `SuccessResponse[T]` - Generic success wrapper
- `ErrorResponse` - Error response structure
- `PaginatedResponse[T]` - Paginated list response

### Validation Rules

- Match exact field names from backend API
- Use Optional[] for nullable fields
- Use Field(default_factory=list) for empty lists
- Include Field(description="...") for documentation
- Datetime fields should use datetime type
- IDs should be int, identifiers should be str

### Testing Strategy

- Create simple test file to validate models can be instantiated
- Test JSON serialization/deserialization
- Validate enum values match backend
- No integration tests needed - just unit tests for models

### Next Steps After This Task

After merging this PR:
- T7-50 will refactor APIClient to use these models
- Commands will gradually migrate to use typed models
- Old dict[str, Any] code remains working in parallel

## Events

### 2025-10-20 15:45 - Created
- Broken out from T7-48 as first implementation task
- Foundation for all subsequent type safety improvements

### 2025-10-20 16:30 - Started work
- Moved task from backlog to active
- Updated status to "In Progress"
- Creating new branch for this work
- Beginning implementation of models and schemas

### 2025-10-20 16:35 - Completed models and schemas implementation
- Created `src/cli/models/` directory with all domain models:
  - `common.py` - Status and Priority enums
  - `task.py` - Task, TaskCreate, TaskUpdate, TaskFilters
  - `workspace.py` - Workspace, WorkspaceCreate
  - `project.py` - Project, ProjectCreate
  - `label.py` - Label, LabelCreate, LabelUpdate
  - `user.py` - User, UserPreferences
  - `view.py` - TaskView, TaskViewCreate, TaskViewUpdate
  - `goal.py` - Goal, GoalDecomposition
  - `dependency.py` - TaskDependency
  - `__init__.py` - Export all models
- Created `src/cli/schemas/` directory with API schemas:
  - `responses.py` - SuccessResponse[T], ErrorResponse
  - `pagination.py` - PaginatedResponse[T], PaginationParams
  - `filters.py` - BaseFilters, DateRangeFilter
  - `__init__.py` - Export all schemas
- All models include proper type hints and docstrings
- All models use Pydantic Field() with descriptions
- Enums configured to convert values for API serialization
- Type checking passes: `make typecheck`
- Code formatted: `make format`
- Linting passes: `make lint`
- No breaking changes to existing code

### 2025-10-20 16:40 - Task completed
- All acceptance criteria met
- All 156 unit tests pass
- Committed changes and pushed to branch
- Created PR #28: https://github.com/supercarl87/AnyTaskCLI/pull/28
- PR includes:
  - 9 model files with domain entities
  - 3 schema files with API response wrappers
  - 2 __init__.py files with exports
  - 485+ lines of type-safe, documented code
- Task moved to done/
- Ready for code review and merge
