"""Project domain models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Project(BaseModel):
    """Full project model."""

    id: int = Field(description="Project ID")
    name: str = Field(description="Project name")
    identifier: str = Field(description="Project identifier (e.g., API)")
    description: Optional[str] = Field(default=None, description="Project description")
    workspace_id: int = Field(description="Workspace ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class ProjectCreate(BaseModel):
    """Project creation payload."""

    name: str = Field(description="Project name")
    identifier: str = Field(description="Project identifier")
    description: Optional[str] = Field(default=None, description="Project description")
