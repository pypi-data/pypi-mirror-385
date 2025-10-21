"""Tests for AIAPIClient."""

from unittest.mock import AsyncMock, patch

import pytest

from cli.client.ai import AIAPIClient
from cli.models.ai import (
    AIUsage,
    AISuggestions,
    OrganizationResult,
    TaskAutoFill,
    TaskReview,
    WorkspaceSummary,
)
from cli.models.goal import GoalDecomposition


@pytest.fixture
def client():
    """Create an AIAPIClient instance for testing."""
    return AIAPIClient(
        base_url="http://test.example.com",
        auth_token="test_token",
    )


class TestDecomposeGoal:
    """Test decompose_goal method."""

    @pytest.mark.asyncio
    async def test_decompose_goal_success(self, client):
        """Test successful goal decomposition."""
        goal_create_response = {"data": {"id": 1, "title": "Build feature"}}
        decompose_response = {
            "data": {
                "goal_id": 1,
                "tasks": [
                    {"title": "Task 1", "description": "First task"},
                    {"title": "Task 2", "description": "Second task"},
                ],
                "dependencies": [],
                "reasoning": "AI reasoning",
            }
        }

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [goal_create_response, decompose_response]

            result = await client.decompose_goal(
                goal="Build feature", workspace_id=1, max_tasks=5, task_size=4
            )

            assert mock_post.call_count == 2
            assert isinstance(result, GoalDecomposition)
            assert result.goal_id == 1
            assert len(result.tasks) == 2


class TestOrganizeWorkspace:
    """Test organize_workspace method."""

    @pytest.mark.asyncio
    async def test_organize_workspace_success(self, client):
        """Test successful workspace organization."""
        mock_response = {
            "data": {
                "changes": [{"type": "rename", "task_id": 1}],
                "summary": "Renamed 1 task",
            }
        }

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.organize_workspace(
                workspace_id=1, actions=["normalize_titles"], dry_run=True
            )

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "/v1/workspaces/1/organize"
            assert isinstance(result, OrganizationResult)
            assert len(result.changes) == 1


class TestFillTaskDetails:
    """Test fill_task_details method."""

    @pytest.mark.asyncio
    async def test_fill_task_details_success(self, client):
        """Test successful task detail filling."""
        mock_response = {
            "data": {
                "identifier": "DEV-42",
                "filled_fields": {"description": "Auto-filled description"},
                "reasoning": "AI reasoning",
            }
        }

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.fill_task_details(
                identifier="DEV-42", fields=["description"]
            )

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "/v1/tasks/DEV-42/auto-fill"
            assert isinstance(result, TaskAutoFill)
            assert result.identifier == "DEV-42"


class TestGetAISuggestions:
    """Test get_ai_suggestions method."""

    @pytest.mark.asyncio
    async def test_get_ai_suggestions_success(self, client):
        """Test successful AI suggestions retrieval."""
        mock_response = {
            "data": {
                "recommended_tasks": [{"identifier": "DEV-1", "score": 0.9}],
                "reasoning": "Based on current priorities",
            }
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_ai_suggestions(workspace_id=1)

            mock_get.assert_called_once_with("/v1/workspaces/1/suggestions")
            assert isinstance(result, AISuggestions)
            assert len(result.recommended_tasks) == 1


class TestReviewTask:
    """Test review_task method."""

    @pytest.mark.asyncio
    async def test_review_task_success(self, client):
        """Test successful task review."""
        mock_response = {
            "data": {
                "identifier": "DEV-42",
                "checks": [{"name": "acceptance_criteria", "passed": True}],
                "warnings": [],
                "is_ready": True,
                "summary": "Task is ready",
            }
        }

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.review_task(identifier="DEV-42")

            mock_post.assert_called_once_with("/v1/tasks/DEV-42/review")
            assert isinstance(result, TaskReview)
            assert result.is_ready is True
            assert result.identifier == "DEV-42"


class TestGenerateSummary:
    """Test generate_summary method."""

    @pytest.mark.asyncio
    async def test_generate_summary_success(self, client):
        """Test successful summary generation."""
        mock_response = {
            "data": {
                "period": "today",
                "activity_breakdown": {"completed": 5, "created": 3},
                "insights": ["High productivity day"],
                "summary_text": "You completed 5 tasks today",
            }
        }

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client.generate_summary(workspace_id=1, period="today")

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "/v1/workspaces/1/summaries"
            assert isinstance(result, WorkspaceSummary)
            assert result.period == "today"


class TestGetAIUsage:
    """Test get_ai_usage method."""

    @pytest.mark.asyncio
    async def test_get_ai_usage_workspace(self, client):
        """Test AI usage retrieval for workspace."""
        mock_response = {
            "data": {
                "total_requests": 100,
                "total_tokens": 50000,
                "total_cost": 1.25,
                "breakdown": {},
            }
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_ai_usage(workspace_id=1)

            mock_get.assert_called_once_with("/v1/workspaces/1/ai-usage")
            assert isinstance(result, AIUsage)
            assert result.total_requests == 100

    @pytest.mark.asyncio
    async def test_get_ai_usage_global(self, client):
        """Test AI usage retrieval globally."""
        mock_response = {
            "data": {
                "total_requests": 500,
                "total_tokens": 250000,
                "total_cost": 6.25,
                "breakdown": {},
            }
        }

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client.get_ai_usage(workspace_id=None)

            mock_get.assert_called_once_with("/v1/ai-usage")
            assert isinstance(result, AIUsage)
            assert result.total_requests == 500
