"""Workspace domain models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Workspace(BaseModel):
    """Full workspace model."""

    id: int = Field(description="Workspace ID")
    name: str = Field(description="Workspace name")
    identifier: str = Field(description="Workspace identifier (e.g., DEV)")
    description: Optional[str] = Field(
        default=None, description="Workspace description"
    )
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class WorkspaceCreate(BaseModel):
    """Workspace creation payload."""

    name: str = Field(description="Workspace name")
    identifier: str = Field(description="Workspace identifier (3+ chars)")
    description: Optional[str] = Field(
        default=None, description="Workspace description"
    )
