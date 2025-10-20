"""MCP server for AnyTask."""

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from anytask_mcp.client import AnyTaskClient
from anytask_mcp.context import WorkspaceContext
from anytask_mcp.tools import ToolHandler
from anytask_mcp.resources import ResourceHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("AnyTask")

# Initialize client and context (will be set on server start)
_client: AnyTaskClient | None = None
_context: WorkspaceContext | None = None
_tool_handler: ToolHandler | None = None
_resource_handler: ResourceHandler | None = None


def _ensure_initialized():
    """Ensure server components are initialized."""
    global _client, _context, _tool_handler, _resource_handler
    if _client is None:
        _context = WorkspaceContext()
        _client = AnyTaskClient()
        _tool_handler = ToolHandler(_client, _context)
        _resource_handler = ResourceHandler(_client, _context)


# Tool implementations
@mcp.tool()
async def list_tasks(
    status: str | None = None,
    assignee_id: str | None = None,
    limit: int = 20,
) -> str:
    """List tasks with optional filtering.

    Args:
        status: Filter by status (backlog, todo, inprogress, done, canceled)
        assignee_id: Filter by assignee ID
        limit: Maximum number of tasks (default: 20)
    """
    _ensure_initialized()
    result = await _tool_handler.handle_list_tasks(status, assignee_id, limit)  # type: ignore
    return result[0].text


@mcp.tool()
async def select_task(task_id: str) -> str:
    """Select a task as active for the current workspace.

    Args:
        task_id: Task identifier (e.g., 'DEV-123')
    """
    _ensure_initialized()
    result = await _tool_handler.handle_select_task(task_id)  # type: ignore
    return result[0].text


@mcp.tool()
async def create_task(
    title: str,
    description: str | None = None,
    priority: int | None = None,
) -> str:
    """Create a new task.

    Args:
        title: Task title
        description: Task description
        priority: Task priority (-2 to 2)
    """
    _ensure_initialized()
    result = await _tool_handler.handle_create_task(title, description, priority)  # type: ignore
    return result[0].text


@mcp.tool()
async def update_task(
    task_id: str,
    version: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
) -> str:
    """Update task fields.

    Args:
        task_id: Task identifier (e.g., 'DEV-123')
        version: Current version for optimistic locking
        title: New task title
        description: New task description
        status: New task status
    """
    _ensure_initialized()
    assert _tool_handler is not None
    result = await _tool_handler.handle_update_task(
        task_id, version, title, description, status
    )
    return result[0].text


@mcp.tool()
async def start_attempt(task_id: str, notes: str | None = None) -> str:
    """Start a work attempt on a task.

    Args:
        task_id: Task identifier (e.g., 'DEV-123')
        notes: Optional notes about the attempt
    """
    _ensure_initialized()
    result = await _tool_handler.handle_start_attempt(task_id, notes)  # type: ignore
    return result[0].text


@mcp.tool()
async def finish_attempt(
    attempt_id: int,
    status: str,
    failure_class: str | None = None,
    cost_tokens: int | None = None,
    wall_clock_ms: int | None = None,
    notes: str | None = None,
) -> str:
    """Mark an attempt as finished.

    Args:
        attempt_id: Attempt ID
        status: Attempt outcome (success, failed, aborted)
        failure_class: Failure classification (required if status=failed)
        cost_tokens: Token cost of the attempt
        wall_clock_ms: Wall clock time in milliseconds
        notes: Optional notes about the outcome
    """
    _ensure_initialized()
    result = await _tool_handler.handle_finish_attempt(  # type: ignore
        attempt_id, status, failure_class, cost_tokens, wall_clock_ms, notes
    )
    return result[0].text


@mcp.tool()
async def add_artifact(
    attempt_id: int,
    type: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Upload an artifact (diff, log, file) for an attempt.

    Args:
        attempt_id: Attempt ID
        type: Artifact type (diff, file, log, benchmark, screenshot)
        content: Artifact content
        metadata: Optional metadata (filename, language, etc.)
    """
    _ensure_initialized()
    assert _tool_handler is not None
    result = await _tool_handler.handle_add_artifact(
        attempt_id, type, content, metadata
    )
    return result[0].text


@mcp.tool()
async def get_board() -> str:
    """Get Kanban board view of tasks organized by status."""
    _ensure_initialized()
    result = await _tool_handler.handle_get_board()  # type: ignore
    return result[0].text


# Resource implementations
@mcp.resource("task://{task_id}/spec")
async def get_task_spec(task_id: str) -> str:
    """Get full task specification including title, description, and metadata."""
    _ensure_initialized()
    result = await _resource_handler.read_task_spec(task_id)  # type: ignore
    return result[0].text


@mcp.resource("task://{task_id}/deps")
async def get_task_deps(task_id: str) -> str:
    """Get task dependencies and dependents."""
    _ensure_initialized()
    result = await _resource_handler.read_task_deps(task_id)  # type: ignore
    return result[0].text


@mcp.resource("task://{task_id}/history")
async def get_task_history(task_id: str) -> str:
    """Get event history and timeline for the task."""
    _ensure_initialized()
    result = await _resource_handler.read_task_history(task_id)  # type: ignore
    return result[0].text


@mcp.resource("workspace://current/active_task")
async def get_active_task() -> str:
    """Get the currently selected task for this workspace."""
    _ensure_initialized()
    result = await _resource_handler.read_active_task()  # type: ignore
    return result[0].text


def main():
    """Entry point for MCP server."""
    logger.info("Starting AnyTask MCP server")
    _ensure_initialized()
    logger.info(f"Workspace directory: {_context.workspace_dir}")  # type: ignore
    logger.info(f"API URL: {_client.base_url}")  # type: ignore
    logger.info(f"Workspace ID: {_client.workspace_id}")  # type: ignore
    mcp.run()


if __name__ == "__main__":
    main()
