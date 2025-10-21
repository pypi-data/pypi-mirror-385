"""Task domain models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from cli.models.common import Priority, Status


class Task(BaseModel):
    """Full task model with all fields."""

    id: int = Field(description="Task ID")
    public_id: int = Field(description="9-digit globally unique public ID")
    identifier: str = Field(description="Task identifier (e.g., DEV-42)")
    title: str = Field(description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: Status = Field(description="Task status")
    priority: Priority = Field(description="Task priority")
    phase: Optional[str] = Field(default=None, description="Phase/milestone identifier")
    owner_id: Optional[str] = Field(default=None, description="Owner user ID")
    project_id: int = Field(description="Project ID")
    workspace_id: int = Field(description="Workspace ID")
    labels: list[str] = Field(default_factory=list, description="Task labels")
    estimate: Optional[int] = Field(default=None, description="Time estimate in hours")
    parent_id: Optional[int] = Field(default=None, description="Parent task ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    version: int = Field(description="Version for optimistic locking")

    model_config = ConfigDict(
        use_enum_values=False  # Keep enum instances, don't convert to values
    )


class TaskCreate(BaseModel):
    """Task creation payload."""

    title: str = Field(description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: Status = Field(default=Status.BACKLOG, description="Task status")
    priority: Priority = Field(default=Priority.NORMAL, description="Task priority")
    phase: Optional[str] = Field(default=None, description="Phase/milestone identifier")
    owner_id: Optional[str] = Field(default=None, description="Owner user ID")
    labels: list[str] = Field(default_factory=list, description="Task labels")
    estimate: Optional[int] = Field(default=None, description="Time estimate in hours")
    parent_id: Optional[int] = Field(default=None, description="Parent task ID")

    model_config = ConfigDict(
        use_enum_values=True  # Convert enums to values for API
    )


class TaskUpdate(BaseModel):
    """Task update payload."""

    title: Optional[str] = Field(default=None, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: Optional[Status] = Field(default=None, description="Task status")
    priority: Optional[Priority] = Field(default=None, description="Task priority")
    phase: Optional[str] = Field(default=None, description="Phase/milestone identifier")
    owner_id: Optional[str] = Field(default=None, description="Owner user ID")
    project_id: Optional[int] = Field(default=None, description="Project ID")
    labels: Optional[list[str]] = Field(default=None, description="Task labels")
    estimate: Optional[int] = Field(default=None, description="Time estimate in hours")
    parent_id: Optional[int] = Field(default=None, description="Parent task ID")

    model_config = ConfigDict(
        use_enum_values=True  # Convert enums to values for API
    )


class TaskFilters(BaseModel):
    """Task list query filters."""

    workspace_id: Optional[int] = Field(
        default=None, description="Filter by workspace ID"
    )
    project_id: Optional[int] = Field(default=None, description="Filter by project ID")
    status: Optional[list[Status]] = Field(
        default=None, description="Filter by status values"
    )
    phase: Optional[str] = Field(default=None, description="Filter by phase/milestone")
    owner: Optional[str] = Field(default=None, description="Filter by owner ID or 'me'")
    labels: Optional[list[str]] = Field(
        default=None, description="Filter by labels (AND logic)"
    )
    priority_gte: Optional[int] = Field(default=None, description="Minimum priority")
    priority_lte: Optional[int] = Field(default=None, description="Maximum priority")
    limit: int = Field(default=50, description="Items per page")
    offset: int = Field(default=0, description="Pagination offset")
    sort_by: str = Field(default="priority", description="Sort field")
    order: str = Field(default="desc", description="Sort order (asc/desc)")

    model_config = ConfigDict(
        use_enum_values=True  # Convert enums to values for API params
    )
