"""MCP tool implementations."""

from typing import Any

from mcp.types import Tool, TextContent

from anytask_mcp.client import AnyTaskClient
from anytask_mcp.context import WorkspaceContext


# Tool schemas
LIST_TASKS_TOOL = Tool(
    name="list_tasks",
    description="List tasks with optional filtering",
    inputSchema={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["backlog", "todo", "inprogress", "done", "canceled"],
                "description": "Filter by task status",
            },
            "assignee_id": {
                "type": "string",
                "description": "Filter by assignee ID",
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of tasks to return",
                "default": 20,
            },
        },
    },
)

SELECT_TASK_TOOL = Tool(
    name="select_task",
    description="Select a task as active for the current workspace",
    inputSchema={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "Task identifier (e.g., 'DEV-123')",
            },
        },
        "required": ["task_id"],
    },
)

CREATE_TASK_TOOL = Tool(
    name="create_task",
    description="Create a new task",
    inputSchema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Task title",
            },
            "description": {
                "type": "string",
                "description": "Task description",
            },
            "priority": {
                "type": "number",
                "description": "Task priority (-2 to 2)",
            },
        },
        "required": ["title"],
    },
)

UPDATE_TASK_TOOL = Tool(
    name="update_task",
    description="Update task fields",
    inputSchema={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "Task identifier (e.g., 'DEV-123')",
            },
            "title": {
                "type": "string",
                "description": "New task title",
            },
            "description": {
                "type": "string",
                "description": "New task description",
            },
            "status": {
                "type": "string",
                "enum": ["backlog", "todo", "inprogress", "done", "canceled"],
                "description": "New task status",
            },
            "version": {
                "type": "number",
                "description": "Current version for optimistic locking",
            },
        },
        "required": ["task_id", "version"],
    },
)

START_ATTEMPT_TOOL = Tool(
    name="start_attempt",
    description="Start a work attempt on a task",
    inputSchema={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "Task identifier (e.g., 'DEV-123')",
            },
            "notes": {
                "type": "string",
                "description": "Optional notes about the attempt",
            },
        },
        "required": ["task_id"],
    },
)

FINISH_ATTEMPT_TOOL = Tool(
    name="finish_attempt",
    description="Mark an attempt as finished",
    inputSchema={
        "type": "object",
        "properties": {
            "attempt_id": {
                "type": "number",
                "description": "Attempt ID",
            },
            "status": {
                "type": "string",
                "enum": ["success", "failed", "aborted"],
                "description": "Attempt outcome",
            },
            "failure_class": {
                "type": "string",
                "enum": [
                    "test_fail",
                    "tool_error",
                    "context_limit",
                    "rate_limit",
                    "timeout",
                    "other",
                ],
                "description": "Failure classification (required if status=failed)",
            },
            "cost_tokens": {
                "type": "number",
                "description": "Token cost of the attempt",
            },
            "wall_clock_ms": {
                "type": "number",
                "description": "Wall clock time in milliseconds",
            },
            "notes": {
                "type": "string",
                "description": "Optional notes about the outcome",
            },
        },
        "required": ["attempt_id", "status"],
    },
)

ADD_ARTIFACT_TOOL = Tool(
    name="add_artifact",
    description="Upload an artifact (diff, log, file) for an attempt",
    inputSchema={
        "type": "object",
        "properties": {
            "attempt_id": {
                "type": "number",
                "description": "Attempt ID",
            },
            "type": {
                "type": "string",
                "enum": ["diff", "file", "log", "benchmark", "screenshot"],
                "description": "Artifact type",
            },
            "content": {
                "type": "string",
                "description": "Artifact content",
            },
            "metadata": {
                "type": "object",
                "description": "Optional metadata (filename, language, etc.)",
            },
        },
        "required": ["attempt_id", "type", "content"],
    },
)

GET_BOARD_TOOL = Tool(
    name="get_board",
    description="Get Kanban board view of tasks organized by status",
    inputSchema={
        "type": "object",
        "properties": {},
    },
)


class ToolHandler:
    """Handles MCP tool calls."""

    def __init__(self, client: AnyTaskClient, context: WorkspaceContext):
        """Initialize tool handler.

        Args:
            client: AnyTask API client
            context: Workspace context manager
        """
        self.client = client
        self.context = context

    async def handle_list_tasks(
        self,
        status: str | None = None,
        assignee_id: str | None = None,
        limit: int = 20,
    ) -> list[TextContent]:
        """Handle list_tasks tool call."""
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        try:
            result = await self.client.list_tasks(
                workspace_id=workspace_id,
                status=status,
                assignee_id=assignee_id,
                limit=limit,
            )

            # Handle both list and dict responses
            tasks: list[dict[str, Any]] = result if isinstance(result, list) else []

            if not tasks:
                return [TextContent(type="text", text="No tasks found.")]

            lines = ["Tasks:"]
            for task in tasks:
                lines.append(
                    f"- {task['identifier']}: {task['title']} [{task['status']}] (v{task['version']})"
                )

            return [TextContent(type="text", text="\n".join(lines))]

        except Exception as e:
            return [TextContent(type="text", text=f"Error listing tasks: {e}")]

    async def handle_select_task(self, task_id: str) -> list[TextContent]:
        """Handle select_task tool call."""
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        try:
            task = await self.client.get_task(
                workspace_id=workspace_id, task_identifier=task_id
            )
            self.context.set_active_task(task)

            return [
                TextContent(
                    type="text",
                    text=f"Selected task {task['identifier']}: {task['title']}\nStatus: {task['status']}\nVersion: {task['version']}",
                )
            ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error selecting task: {e}")]

    async def handle_create_task(
        self,
        title: str,
        description: str | None = None,
        priority: int | None = None,
    ) -> list[TextContent]:
        """Handle create_task tool call."""
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        try:
            task = await self.client.create_task(
                workspace_id=workspace_id,
                title=title,
                description=description,
                priority=priority,
            )

            return [
                TextContent(
                    type="text",
                    text=f"Created task {task['identifier']}: {task['title']}",
                )
            ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error creating task: {e}")]

    async def handle_update_task(
        self,
        task_id: str,
        version: int,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> list[TextContent]:
        """Handle update_task tool call."""
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        try:
            task = await self.client.update_task(
                workspace_id=workspace_id,
                task_identifier=task_id,
                version=version,
                title=title,
                description=description,
                status=status,
            )

            # Update active task if it's the one being updated
            active_task = self.context.get_active_task()
            if active_task and active_task.task_id == task_id:
                self.context.update_active_task_version(task["version"])

            return [
                TextContent(
                    type="text",
                    text=f"Updated task {task['identifier']} to version {task['version']}",
                )
            ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error updating task: {e}")]

    async def handle_start_attempt(
        self, task_id: str, notes: str | None = None
    ) -> list[TextContent]:
        """Handle start_attempt tool call."""
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        try:
            attempt = await self.client.start_attempt(
                workspace_id=workspace_id,
                task_identifier=task_id,
                notes=notes,
            )

            return [
                TextContent(
                    type="text",
                    text=f"Started attempt {attempt['id']} on task {task_id}",
                )
            ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error starting attempt: {e}")]

    async def handle_finish_attempt(
        self,
        attempt_id: int,
        status: str,
        failure_class: str | None = None,
        cost_tokens: int | None = None,
        wall_clock_ms: int | None = None,
        notes: str | None = None,
    ) -> list[TextContent]:
        """Handle finish_attempt tool call."""
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        # Get active task to get task identifier
        active_task = self.context.get_active_task()
        if not active_task:
            return [TextContent(type="text", text="Error: No active task selected.")]

        try:
            attempt = await self.client.finish_attempt(
                workspace_id=workspace_id,
                task_identifier=active_task.task_id,
                attempt_id=attempt_id,
                status=status,
                failure_class=failure_class,
                cost_tokens=cost_tokens,
                wall_clock_ms=wall_clock_ms,
                notes=notes,
            )

            return [
                TextContent(
                    type="text",
                    text=f"Finished attempt {attempt['id']} with status: {status}",
                )
            ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error finishing attempt: {e}")]

    async def handle_add_artifact(
        self,
        attempt_id: int,
        type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[TextContent]:
        """Handle add_artifact tool call."""
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        # Get active task to get task identifier
        active_task = self.context.get_active_task()
        if not active_task:
            return [TextContent(type="text", text="Error: No active task selected.")]

        try:
            artifact = await self.client.add_artifact(
                workspace_id=workspace_id,
                task_identifier=active_task.task_id,
                attempt_id=attempt_id,
                artifact_type=type,
                content=content,
                metadata=metadata,
            )

            return [
                TextContent(
                    type="text",
                    text=f"Added {type} artifact {artifact['id']} to attempt {attempt_id}",
                )
            ]

        except Exception as e:
            return [TextContent(type="text", text=f"Error adding artifact: {e}")]

    async def handle_get_board(self) -> list[TextContent]:
        """Handle get_board tool call."""
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        try:
            # Fetch all tasks
            result = await self.client.list_tasks(workspace_id=workspace_id, limit=100)
            all_tasks: list[dict[str, Any]] = result if isinstance(result, list) else []

            # Group by status
            board: dict[str, list[dict[str, Any]]] = {
                "backlog": [],
                "todo": [],
                "inprogress": [],
                "done": [],
                "canceled": [],
            }

            for task in all_tasks:
                status = task["status"]
                if status in board:
                    board[status].append(task)

            # Format board
            lines = ["Kanban Board:"]
            for status, tasks in board.items():
                lines.append(f"\n{status.upper()} ({len(tasks)}):")
                for task in tasks:
                    lines.append(f"  - {task['identifier']}: {task['title']}")

            return [TextContent(type="text", text="\n".join(lines))]

        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching board: {e}")]

    async def call_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Dispatch tool call to appropriate handler.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result as TextContent list
        """
        if name == "list_tasks":
            return await self.handle_list_tasks(**arguments)
        elif name == "select_task":
            return await self.handle_select_task(**arguments)
        elif name == "create_task":
            return await self.handle_create_task(**arguments)
        elif name == "update_task":
            return await self.handle_update_task(**arguments)
        elif name == "start_attempt":
            return await self.handle_start_attempt(**arguments)
        elif name == "finish_attempt":
            return await self.handle_finish_attempt(**arguments)
        elif name == "add_artifact":
            return await self.handle_add_artifact(**arguments)
        elif name == "get_board":
            return await self.handle_get_board(**arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]


def get_all_tools() -> list[Tool]:
    """Get list of all available tools."""
    return [
        LIST_TASKS_TOOL,
        SELECT_TASK_TOOL,
        CREATE_TASK_TOOL,
        UPDATE_TASK_TOOL,
        START_ATTEMPT_TOOL,
        FINISH_ATTEMPT_TOOL,
        ADD_ARTIFACT_TOOL,
        GET_BOARD_TOOL,
    ]
