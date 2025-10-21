# T7-53: Service Layer Foundation

**Priority**: High
**Status**: Completed
**Created**: 2025-10-20
**Parent**: T7-48 (CLI Architecture Improvements)
**PR**: https://github.com/supercarl87/AnyTaskCLI/pull/33

## Description

Create the service layer to encapsulate business logic. Services sit between commands and API clients, providing a clean interface for common operations and business rules.

This task creates `BaseService`, `TaskService`, and `WorkspaceService` as examples. Future tasks will migrate commands to use services.

## Objectives

- Create base service class with common patterns
- Implement TaskService with business logic for task operations
- Implement WorkspaceService with workspace management logic
- Establish service layer architecture for other domains

## Acceptance Criteria

- [ ] Create `src/cli/services/` directory structure:
  - [ ] `services/__init__.py` - Export all services
  - [ ] `services/base.py` - BaseService abstract class
  - [ ] `services/task_service.py` - TaskService implementation
  - [ ] `services/workspace_service.py` - WorkspaceService implementation
  - [ ] `services/context.py` - Service context helpers
- [ ] BaseService includes:
  - [ ] Configuration management
  - [ ] Client initialization
  - [ ] Common error handling patterns
  - [ ] from_config() class method
- [ ] TaskService implements high-level operations:
  - [ ] `create_task_with_validation()` - Create with business rules
  - [ ] `update_task_status()` - Update status with validation
  - [ ] `find_similar_tasks()` - Find similar task titles
  - [ ] `get_task_with_context()` - Get task with dependencies/parent
  - [ ] `complete_task()` - Mark done with validation checks
  - [ ] `suggest_next_tasks()` - Get suggestions based on current state
- [ ] WorkspaceService implements:
  - [ ] `get_or_create_default_workspace()` - Ensure workspace exists
  - [ ] `switch_workspace()` - Switch with validation
  - [ ] `get_workspace_summary()` - Get workspace overview
  - [ ] `resolve_workspace_context()` - Resolve from config/params
- [ ] All services use typed clients (not old client.py)
- [ ] Type checking passes: `make typecheck`
- [ ] Unit tests for BaseService
- [ ] Unit tests for TaskService (mocked clients)
  - Unit tests for WorkspaceService (mocked clients)

## Dependencies

- T7-49: Models and Schemas Foundation
- T7-50: Refactor BaseClient and Tasks API
- T7-51: Refactor Workspace Project APIs

## Estimated Effort

4-5 hours

## Technical Notes

### Directory Structure
```
src/cli/
└── services/
    ├── __init__.py
    ├── base.py              # BaseService
    ├── task_service.py      # TaskService
    ├── workspace_service.py # WorkspaceService
    └── context.py           # Context helpers
```

### BaseService Pattern

```python
# services/base.py
from abc import ABC
from cli.config import GlobalConfig

class BaseService(ABC):
    """Base service with common functionality."""

    def __init__(self, config: GlobalConfig):
        self.config = config
        self._init_clients()

    def _init_clients(self):
        """Initialize API clients. Override in subclasses."""
        pass

    @classmethod
    def from_config(cls, config: GlobalConfig = None):
        """Create service from config."""
        if config is None:
            config = GlobalConfig.load()
        return cls(config)

    def _get_effective_workspace_id(self) -> int:
        """Get workspace ID from config/context."""
        # Helper to resolve workspace context
        pass
```

### TaskService Implementation

```python
# services/task_service.py
from cli.services.base import BaseService
from cli.client.tasks import TasksAPIClient
from cli.models.task import Task, TaskCreate, TaskUpdate, TaskFilters

class TaskService(BaseService):
    """Business logic for task operations."""

    def _init_clients(self):
        self.tasks = TasksAPIClient.from_config(self.config)

    async def create_task_with_validation(
        self,
        project_id: int,
        task: TaskCreate
    ) -> Task:
        """Create task with validation."""
        # Business rule: validate priority range
        if task.priority < -2 or task.priority > 2:
            raise ValueError("Priority must be between -2 and 2")

        # Business rule: check for similar titles
        similar = await self.find_similar_tasks(task.title, project_id)
        if similar:
            # Could prompt user or return warning
            pass

        return await self.tasks.create_task(project_id, task)

    async def find_similar_tasks(
        self,
        title: str,
        workspace_id: int
    ) -> list[Task]:
        """Find tasks with similar titles (fuzzy match)."""
        filters = TaskFilters(workspace_id=workspace_id)
        result = await self.tasks.list_tasks(filters)

        # Fuzzy matching logic
        similar = []
        title_lower = title.lower()
        for task in result.items:
            if self._is_similar(title_lower, task.title.lower()):
                similar.append(task)

        return similar

    def _is_similar(self, a: str, b: str) -> bool:
        """Check if two strings are similar."""
        # Simple similarity check - could use Levenshtein distance
        return a in b or b in a

    async def complete_task(self, identifier: str) -> Task:
        """Mark task as done with validation."""
        # Get task
        task = await self.tasks.get_task(identifier)

        # Business rule: check dependencies
        dependencies = await self.tasks.get_task_dependencies(identifier)
        incomplete_deps = [d for d in dependencies if d.status != "done"]
        if incomplete_deps:
            raise ValueError(
                f"Cannot complete task. {len(incomplete_deps)} dependencies "
                "are not done yet."
            )

        # Update status
        updates = TaskUpdate(status="done")
        return await self.tasks.update_task(identifier, updates)

    async def suggest_next_tasks(
        self,
        workspace_id: int,
        current_task_id: str | None = None
    ) -> list[Task]:
        """Suggest next tasks to work on."""
        # Business logic for task suggestions
        filters = TaskFilters(
            workspace_id=workspace_id,
            status=["todo", "backlog"],
        )
        result = await self.tasks.list_tasks(filters)

        # Sort by priority and return top suggestions
        sorted_tasks = sorted(
            result.items,
            key=lambda t: (t.priority, -t.id),
            reverse=True
        )
        return sorted_tasks[:5]
```

### WorkspaceService Implementation

```python
# services/workspace_service.py
from cli.services.base import BaseService
from cli.client.workspaces import WorkspacesAPIClient
from cli.models.workspace import Workspace, WorkspaceCreate

class WorkspaceService(BaseService):
    """Business logic for workspace operations."""

    def _init_clients(self):
        self.workspaces = WorkspacesAPIClient.from_config(self.config)

    async def get_or_create_default_workspace(self) -> Workspace:
        """Get current workspace or create default if none exists."""
        try:
            return await self.workspaces.get_current_workspace()
        except NotFoundError:
            # Create default workspace
            workspace = WorkspaceCreate(
                name="Personal",
                identifier="PER",
                description="Default workspace"
            )
            return await self.workspaces.create_workspace(workspace)

    async def resolve_workspace_context(
        self,
        workspace_id: int | None = None
    ) -> Workspace:
        """Resolve workspace from context."""
        if workspace_id:
            return await self.workspaces.get_workspace(str(workspace_id))

        # Try to get from config
        # Fall back to current workspace
        return await self.get_or_create_default_workspace()
```

### Testing Strategy

- Mock all API clients in service tests
- Test business logic in isolation
- Validate error handling
- Test edge cases (empty lists, missing data, etc.)

### Benefits of Service Layer

- **Separation of Concerns**: Commands focus on CLI, services on business logic
- **Reusability**: Services can be used by commands, MCP server, future APIs
- **Testability**: Business logic tested independently of CLI
- **Maintainability**: Logic changes in one place, not scattered across commands

## Events

### 2025-10-20 16:05 - Created
- Broken out from T7-48
- Establishes service layer architecture

### 2025-10-20 16:25 - Started work
- Moved task from backlog to active
- All dependencies (T7-49, T7-50, T7-51) are completed
- Beginning implementation of service layer foundation
- Will create BaseService, TaskService, and WorkspaceService

### 2025-10-20 17:30 - Implementation completed
- ✅ Created `src/cli/services/` directory structure
- ✅ Implemented `BaseService` abstract class with:
  - Configuration management
  - Client initialization pattern
  - `from_config()` class method
  - `_get_effective_workspace_id()` helper
- ✅ Implemented `TaskService` with business logic:
  - `create_task_with_validation()` - Task creation
  - `update_task_status()` - Status updates
  - `find_similar_tasks()` - Fuzzy matching for duplicates
  - `get_task_with_context()` - Task with dependencies
  - `complete_task()` - Validation of dependencies before completion
  - `suggest_next_tasks()` - Smart task suggestions
  - Full CRUD operations and dependency management
- ✅ Implemented `WorkspaceService` with:
  - `get_or_create_default_workspace()` - Auto-creation
  - `switch_workspace()` - With config update
  - `get_workspace_summary()` - Overview with stats
  - `resolve_workspace_context()` - Smart context resolution
  - Workspace validation (identifier length, name)
- ✅ Implemented `ServiceContext` helper for context resolution
- ✅ Type checking passes (`make typecheck`)
- ✅ Comprehensive unit tests:
  - 6 tests for BaseService
  - 20 tests for TaskService
  - 12 tests for WorkspaceService
  - All 264 unit tests pass
- ✅ All acceptance criteria met

**Files created:**
- `src/cli/services/__init__.py`
- `src/cli/services/base.py`
- `src/cli/services/task_service.py`
- `src/cli/services/workspace_service.py`
- `src/cli/services/context.py`
- `tests/cli/unit/services/__init__.py`
- `tests/cli/unit/services/test_base_service.py`
- `tests/cli/unit/services/test_task_service.py`
- `tests/cli/unit/services/test_workspace_service.py`

Ready for next task (T7-54: Migrate Task Commands to Services)
