"""API client for AI-powered operations."""

from cli.client.base import BaseAPIClient
from cli.models.ai import (
    AIUsage,
    AISuggestions,
    OrganizationResult,
    TaskAutoFill,
    TaskReview,
    WorkspaceSummary,
)
from cli.models.goal import GoalDecomposition


class AIAPIClient(BaseAPIClient):
    """API client for AI-powered operations with strongly-typed responses."""

    async def decompose_goal(
        self,
        goal: str,
        workspace_id: int,
        max_tasks: int = 10,
        task_size: int = 4,
    ) -> GoalDecomposition:
        """Decompose a goal into actionable tasks using AI.

        Args:
            goal: The goal description
            workspace_id: The workspace ID
            max_tasks: Maximum number of tasks to generate
            task_size: Preferred task size in hours

        Returns:
            GoalDecomposition object with tasks and dependencies

        Raises:
            APIError: On HTTP errors
        """
        # First create a goal
        create_response = await self.post(
            "/v1/goals",
            json={
                "title": goal,
                "description": goal,
                "workspace_id": workspace_id,
            },
        )
        goal_data = self._unwrap_response(create_response)

        # Extract goal ID
        if isinstance(goal_data, dict):
            goal_id = goal_data.get("id")
        else:
            raise ValueError("Invalid goal creation response")

        # Then decompose it with longer timeout for AI operations
        # Note: We'll need to handle timeout in the base client
        decompose_response = await self.post(
            f"/v1/goals/{goal_id}/decompose",
            json={
                "max_tasks": max_tasks,
                "max_depth": 2,
                "task_size_hours": task_size,
            },
        )
        data = self._unwrap_response(decompose_response)
        return GoalDecomposition(**data)

    async def organize_workspace(
        self, workspace_id: int, actions: list[str], dry_run: bool = False
    ) -> OrganizationResult:
        """Organize workspace tasks using AI.

        Args:
            workspace_id: The workspace ID
            actions: List of actions to perform (e.g., ["normalize_titles", "suggest_labels"])
            dry_run: If True, preview changes without applying them

        Returns:
            OrganizationResult with changes and suggestions

        Raises:
            APIError: On HTTP errors
        """
        response = await self.post(
            f"/v1/workspaces/{workspace_id}/organize",
            json={"actions": actions, "dry_run": dry_run},
        )
        data = self._unwrap_response(response)
        return OrganizationResult(**data)

    async def fill_task_details(
        self, identifier: str, fields: list[str] | None = None
    ) -> TaskAutoFill:
        """Auto-fill missing details for a task using AI.

        Args:
            identifier: Task identifier (e.g., DEV-42)
            fields: List of fields to fill (e.g., ["description", "acceptance", "labels"])

        Returns:
            TaskAutoFill object with generated content

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        response = await self.post(
            f"/v1/tasks/{identifier}/auto-fill",
            json={"fields": fields or []},
        )
        data = self._unwrap_response(response)
        return TaskAutoFill(**data)

    async def get_ai_suggestions(self, workspace_id: int) -> AISuggestions:
        """Get AI-powered suggestions for next tasks to work on.

        Args:
            workspace_id: The workspace ID

        Returns:
            AISuggestions with recommended tasks and reasoning

        Raises:
            APIError: On HTTP errors
        """
        response = await self.get(f"/v1/workspaces/{workspace_id}/suggestions")
        data = self._unwrap_response(response)
        return AISuggestions(**data)

    async def review_task(self, identifier: str) -> TaskReview:
        """Get AI review of a task before marking done.

        Args:
            identifier: Task identifier (e.g., DEV-42)

        Returns:
            TaskReview with checks, warnings, and readiness status

        Raises:
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        response = await self.post(f"/v1/tasks/{identifier}/review")
        data = self._unwrap_response(response)
        return TaskReview(**data)

    async def generate_summary(
        self, workspace_id: int, period: str = "today"
    ) -> WorkspaceSummary:
        """Generate workspace progress summary.

        Args:
            workspace_id: The workspace ID
            period: Summary period (today, weekly, monthly)

        Returns:
            WorkspaceSummary with activity breakdown and insights

        Raises:
            APIError: On HTTP errors
        """
        response = await self.post(
            f"/v1/workspaces/{workspace_id}/summaries",
            json={"period": period, "include_sections": ["all"]},
        )
        data = self._unwrap_response(response)
        return WorkspaceSummary(**data)

    async def get_ai_usage(self, workspace_id: int | None = None) -> AIUsage:
        """Get AI usage statistics and costs.

        Args:
            workspace_id: Optional workspace ID for workspace-level stats

        Returns:
            AIUsage statistics with token counts and costs

        Raises:
            APIError: On HTTP errors
        """
        if workspace_id:
            url = f"/v1/workspaces/{workspace_id}/ai-usage"
        else:
            url = "/v1/ai-usage"

        response = await self.get(url)
        data = self._unwrap_response(response)
        return AIUsage(**data)
