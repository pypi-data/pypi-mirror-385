"""AI-related domain models."""

from typing import Any

from pydantic import BaseModel, Field


class OrganizationResult(BaseModel):
    """Result of workspace organization."""

    changes: list[dict[str, Any]] = Field(
        description="List of changes made or suggested"
    )
    summary: str = Field(description="Summary of organization actions")


class TaskAutoFill(BaseModel):
    """Auto-filled task details."""

    identifier: str = Field(description="Task identifier")
    filled_fields: dict[str, Any] = Field(description="Fields that were auto-filled")
    reasoning: str | None = Field(default=None, description="AI reasoning")


class AISuggestions(BaseModel):
    """AI-powered task suggestions."""

    recommended_tasks: list[dict[str, Any]] = Field(
        description="Recommended tasks to work on"
    )
    reasoning: str = Field(description="Reasoning for recommendations")


class TaskReview(BaseModel):
    """AI task review result."""

    identifier: str = Field(description="Task identifier")
    checks: list[dict[str, Any]] = Field(description="Review checks performed")
    warnings: list[str] = Field(default_factory=list, description="Review warnings")
    is_ready: bool = Field(description="Whether task is ready to be marked done")
    summary: str = Field(description="Review summary")


class WorkspaceSummary(BaseModel):
    """Workspace progress summary."""

    period: str = Field(description="Summary period (today, weekly, monthly)")
    activity_breakdown: dict[str, Any] = Field(description="Breakdown of activities")
    insights: list[str] = Field(description="Key insights from the period")
    summary_text: str = Field(description="Human-readable summary")


class AIUsage(BaseModel):
    """AI usage statistics."""

    total_requests: int = Field(description="Total number of AI requests")
    total_tokens: int = Field(description="Total tokens consumed")
    total_cost: float = Field(description="Total cost in USD")
    breakdown: dict[str, Any] = Field(
        default_factory=dict, description="Usage breakdown by operation"
    )
