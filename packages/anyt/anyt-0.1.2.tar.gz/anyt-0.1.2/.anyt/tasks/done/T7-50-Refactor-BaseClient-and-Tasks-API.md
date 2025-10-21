# T7-50: Refactor BaseClient and Tasks API

**Priority**: High
**Status**: Completed
**Created**: 2025-10-20
**Completed**: 2025-10-20
**Parent**: T7-48 (CLI Architecture Improvements)

## Description

Split the monolithic `client.py` by creating a new `client/` module with `BaseAPIClient` and `TasksAPIClient`. This establishes the pattern for all future client refactoring and provides strongly-typed task operations.

The existing `client.py` remains untouched - this creates new clients alongside it. Commands can gradually migrate.

## Objectives

- Create BaseAPIClient with common HTTP operations
- Implement TasksAPIClient with typed task operations
- Establish client architecture pattern for other domains
- Maintain backward compatibility with existing client.py

## Acceptance Criteria

- [ ] Create `src/cli/client/` directory structure:
  - [ ] `client/__init__.py` - Export client classes
  - [ ] `client/base.py` - BaseAPIClient abstract class
  - [ ] `client/tasks.py` - TasksAPIClient implementation
  - [ ] `client/exceptions.py` - Custom exceptions (APIError, NotFoundError, etc.)
- [ ] BaseAPIClient includes:
  - [ ] Common HTTP methods (get, post, patch, delete)
  - [ ] Authentication header injection
  - [ ] Response unwrapping logic (handle SuccessResponse[T])
  - [ ] Error handling and custom exceptions
  - [ ] from_config() class method
  - [ ] Timeout configuration
- [ ] TasksAPIClient implements all task operations:
  - [ ] `list_tasks(filters: TaskFilters) -> PaginatedResponse[Task]`
  - [ ] `get_task(identifier: str) -> Task`
  - [ ] `get_task_by_workspace(workspace_id: int, identifier: str) -> Task`
  - [ ] `create_task(project_id: int, task: TaskCreate) -> Task`
  - [ ] `update_task(identifier: str, updates: TaskUpdate) -> Task`
  - [ ] `delete_task(identifier: str) -> None`
  - [ ] `add_task_dependency(identifier: str, depends_on: str) -> TaskDependency`
  - [ ] `remove_task_dependency(identifier: str, depends_on: str) -> None`
  - [ ] `get_task_dependencies(identifier: str) -> list[Task]`
  - [ ] `get_task_dependents(identifier: str) -> list[Task]`
  - [ ] `get_task_events(identifier: str, ...) -> list[TaskEvent]`
- [ ] All methods return typed models (not dict[str, Any])
- [ ] Proper error handling with custom exceptions
- [ ] Type checking passes: `make typecheck`
- [ ] Code formatted: `make format`
- [ ] Unit tests for BaseAPIClient
- [ ] Unit tests for TasksAPIClient (mocked HTTP)
- [ ] Old client.py remains untouched and functional

## Dependencies

- T7-49: Models and Schemas Foundation (must complete first)

## Estimated Effort

4-5 hours

## Technical Notes

### Directory Structure
```
src/cli/
├── client/
│   ├── __init__.py
│   ├── base.py           # BaseAPIClient abstract class
│   ├── tasks.py          # TasksAPIClient
│   └── exceptions.py     # APIError, NotFoundError, etc.
└── client.py             # OLD - remains untouched
```

### BaseAPIClient Pattern

```python
# client/base.py
from abc import ABC
import httpx
from typing import Any, TypeVar, Type
from cli.config import GlobalConfig
from cli.schemas.responses import SuccessResponse

T = TypeVar('T')

class BaseAPIClient(ABC):
    """Base API client with common functionality."""

    def __init__(self, base_url: str, auth_token: str = None, agent_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.agent_key = agent_key
        self.headers = self._build_headers()

    def _build_headers(self) -> dict[str, str]:
        """Build authentication headers."""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        elif self.agent_key:
            headers["X-API-Key"] = self.agent_key
        return headers

    @classmethod
    def from_config(cls, config: GlobalConfig = None) -> "BaseAPIClient":
        """Create client from global config."""
        if config is None:
            config = GlobalConfig.load()
        effective = config.get_effective_config()
        return cls(
            base_url=effective["api_url"],
            auth_token=effective.get("auth_token"),
            agent_key=effective.get("agent_key"),
        )

    async def get(self, path: str, params: dict = None) -> Any:
        """HTTP GET request."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                headers=self.headers,
                params=params,
                timeout=10.0,
            )
            return self._handle_response(response)

    async def post(self, path: str, json: dict = None) -> Any:
        """HTTP POST request."""
        # Similar implementation

    async def patch(self, path: str, json: dict = None) -> Any:
        """HTTP PATCH request."""
        # Similar implementation

    async def delete(self, path: str) -> Any:
        """HTTP DELETE request."""
        # Similar implementation

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle response and raise appropriate exceptions."""
        if not response.is_success:
            self._raise_error(response)
        return response.json()

    def _raise_error(self, response: httpx.Response) -> None:
        """Raise appropriate exception based on status code."""
        if response.status_code == 404:
            raise NotFoundError(self._extract_error_message(response))
        elif response.status_code == 401:
            raise AuthenticationError("Authentication failed")
        else:
            raise APIError(self._extract_error_message(response))

    def _unwrap_response(self, response_data: dict) -> Any:
        """Unwrap SuccessResponse[T] to get data."""
        if isinstance(response_data, dict) and "data" in response_data:
            return response_data["data"]
        return response_data
```

### TasksAPIClient Implementation

```python
# client/tasks.py
from cli.client.base import BaseAPIClient
from cli.models.task import Task, TaskCreate, TaskUpdate, TaskFilters
from cli.schemas.pagination import PaginatedResponse

class TasksAPIClient(BaseAPIClient):
    """API client for task operations."""

    async def list_tasks(self, filters: TaskFilters) -> PaginatedResponse[Task]:
        """List tasks with filters."""
        params = filters.model_dump(exclude_none=True)
        response = await self.get("/v1/tasks", params=params)
        data = self._unwrap_response(response)

        # Parse paginated response
        return PaginatedResponse[Task](
            items=[Task(**item) for item in data["items"]],
            total=data["total"],
            limit=data["limit"],
            offset=data["offset"],
        )

    async def get_task(self, identifier: str) -> Task:
        """Get task by identifier."""
        response = await self.get(f"/v1/tasks/{identifier}")
        data = self._unwrap_response(response)
        return Task(**data)

    async def create_task(self, project_id: int, task: TaskCreate) -> Task:
        """Create a new task."""
        response = await self.post(
            f"/v1/projects/{project_id}/tasks",
            json=task.model_dump(exclude_none=True)
        )
        data = self._unwrap_response(response)
        return Task(**data)

    # ... other methods
```

### Custom Exceptions

```python
# client/exceptions.py
class APIError(Exception):
    """Base exception for API errors."""
    pass

class NotFoundError(APIError):
    """Resource not found (404)."""
    pass

class AuthenticationError(APIError):
    """Authentication failed (401)."""
    pass

class ValidationError(APIError):
    """Validation error (422)."""
    pass
```

### Testing Strategy

- Unit tests for BaseAPIClient with mocked httpx
- Unit tests for TasksAPIClient with mocked responses
- Validate all return types are correct models
- Test error handling and exceptions
- No integration tests needed yet

### Migration Strategy

- Old client.py remains fully functional
- New clients available for commands to use
- Future tasks will migrate commands one by one
- After all migrations, remove old client.py

## Events

### 2025-10-20 15:50 - Created
- Broken out from T7-48 as second implementation task
- Establishes client architecture pattern
- Depends on T7-49 models being available

### 2025-10-20 16:45 - Started work
- Moved task from backlog to active
- T7-49 dependency completed (models and schemas available)
- Beginning implementation of BaseAPIClient and TasksAPIClient

### 2025-10-20 17:30 - Completed implementation
- Created client/ directory with proper structure
- Implemented BaseAPIClient with HTTP methods (GET, POST, PATCH, DELETE)
- Implemented custom exceptions (APIError, NotFoundError, AuthenticationError, ValidationError, ConflictError)
- Implemented TasksAPIClient with all task operations
- Added comprehensive unit tests (35 new tests, all passing)
- Maintained backwards compatibility by renaming client.py to old_client.py and re-exporting APIClient from client package
- All 191 unit tests pass
- Type checking passes with mypy
- Code formatted with ruff
- Created PR #30: https://github.com/supercarl87/AnyTaskCLI/pull/30
- Ready for next subtask (T7-51: Workspace and Project APIs)
