"""User domain models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """User model."""

    id: str = Field(description="User ID")
    email: str = Field(description="User email")
    name: Optional[str] = Field(default=None, description="User display name")
    created_at: datetime = Field(description="Creation timestamp")


class UserPreferences(BaseModel):
    """User preferences model."""

    user_id: str = Field(description="User ID")
    current_workspace_id: Optional[int] = Field(
        default=None, description="Current workspace ID"
    )
    current_project_id: Optional[int] = Field(
        default=None, description="Current project ID"
    )
    updated_at: datetime = Field(description="Last update timestamp")
