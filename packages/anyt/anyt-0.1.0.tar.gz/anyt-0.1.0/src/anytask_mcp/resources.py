"""MCP resource implementations."""

import json
from typing import Any

from mcp.types import TextContent, ResourceTemplate

from anytask_mcp.client import AnyTaskClient
from anytask_mcp.context import WorkspaceContext


# Resource templates
TASK_SPEC_RESOURCE = ResourceTemplate(
    uriTemplate="task://{task_id}/spec",
    name="Task Specification",
    mimeType="application/json",
    description="Full task details including title, description, and metadata",
)

TASK_DEPS_RESOURCE = ResourceTemplate(
    uriTemplate="task://{task_id}/deps",
    name="Task Dependencies",
    mimeType="application/json",
    description="Dependencies and dependents for this task",
)

TASK_HISTORY_RESOURCE = ResourceTemplate(
    uriTemplate="task://{task_id}/history",
    name="Task History",
    mimeType="application/json",
    description="Event history and timeline for this task",
)

# Note: Since Resource requires AnyUrl, we'll skip defining static resources
# and rely on resource templates instead


class ResourceHandler:
    """Handles MCP resource reads."""

    def __init__(self, client: AnyTaskClient, context: WorkspaceContext):
        """Initialize resource handler.

        Args:
            client: AnyTask API client
            context: Workspace context manager
        """
        self.client = client
        self.context = context

    async def read_task_spec(self, task_id: str) -> list[TextContent]:
        """Read task specification resource.

        Args:
            task_id: Task identifier (e.g., 'DEV-123')

        Returns:
            Task details as JSON
        """
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

            # Format task specification
            spec = {
                "identifier": task["identifier"],
                "title": task["title"],
                "description": task.get("description", ""),
                "status": task["status"],
                "priority": task["priority"],
                "version": task["version"],
                "created_at": task["created_at"],
                "updated_at": task["updated_at"],
                "assignee": task.get("assignee_id"),
                "project_id": task.get("project_id"),
            }

            return [TextContent(type="text", text=json.dumps(spec, indent=2))]

        except Exception as e:
            return [TextContent(type="text", text=f"Error reading task spec: {e}")]

    async def read_task_deps(self, task_id: str) -> list[TextContent]:
        """Read task dependencies resource.

        Args:
            task_id: Task identifier (e.g., 'DEV-123')

        Returns:
            Dependencies and dependents as JSON
        """
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        try:
            deps = await self.client.get_dependencies(
                workspace_id=workspace_id, task_identifier=task_id
            )

            return [TextContent(type="text", text=json.dumps(deps, indent=2))]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error reading task dependencies: {e}")
            ]

    async def read_task_history(self, task_id: str) -> list[TextContent]:
        """Read task history resource.

        Args:
            task_id: Task identifier (e.g., 'DEV-123')

        Returns:
            Event history as JSON
        """
        workspace_id = self.client.workspace_id
        if not workspace_id:
            return [
                TextContent(
                    type="text",
                    text="Error: No workspace configured. Set ANYTASK_WORKSPACE_ID.",
                )
            ]

        try:
            result = await self.client.get_events(
                workspace_id=workspace_id, task_identifier=task_id
            )
            events: list[dict[str, Any]] = result if isinstance(result, list) else []

            # Format event history
            history = []
            for event in events:
                history.append(
                    {
                        "id": event["id"],
                        "event_type": event["event_type"],
                        "description": event["description"],
                        "actor": event.get("actor_id"),
                        "created_at": event["created_at"],
                        "metadata": event.get("metadata", {}),
                    }
                )

            return [TextContent(type="text", text=json.dumps(history, indent=2))]

        except Exception as e:
            return [TextContent(type="text", text=f"Error reading task history: {e}")]

    async def read_active_task(self) -> list[TextContent]:
        """Read active task resource.

        Returns:
            Active task details as JSON
        """
        active_task = self.context.get_active_task()
        if not active_task:
            return [
                TextContent(
                    type="text", text=json.dumps({"active_task": None}, indent=2)
                )
            ]

        return [
            TextContent(
                type="text",
                text=json.dumps(active_task.model_dump(), indent=2),
            )
        ]

    async def read_resource(self, uri: str) -> list[TextContent]:
        """Dispatch resource read to appropriate handler.

        Args:
            uri: Resource URI

        Returns:
            Resource content as TextContent list
        """
        if uri.startswith("task://"):
            # Parse URI: task://{task_id}/{resource_type}
            parts = uri[7:].split("/")
            if len(parts) != 2:
                return [TextContent(type="text", text=f"Invalid task URI: {uri}")]

            task_id, resource_type = parts

            if resource_type == "spec":
                return await self.read_task_spec(task_id)
            elif resource_type == "deps":
                return await self.read_task_deps(task_id)
            elif resource_type == "history":
                return await self.read_task_history(task_id)
            else:
                return [
                    TextContent(
                        type="text", text=f"Unknown resource type: {resource_type}"
                    )
                ]

        elif uri == "workspace://current/active_task":
            return await self.read_active_task()

        else:
            return [TextContent(type="text", text=f"Unknown resource URI: {uri}")]


def get_all_resource_templates() -> list[ResourceTemplate]:
    """Get list of all available resource templates."""
    return [
        TASK_SPEC_RESOURCE,
        TASK_DEPS_RESOURCE,
        TASK_HISTORY_RESOURCE,
    ]
