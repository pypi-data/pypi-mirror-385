"""Client module for API communication.

This module provides typed API clients for communicating with the AnyTask backend.
"""

# Import typed client classes
from cli.client.ai import AIAPIClient
from cli.client.base import BaseAPIClient
from cli.client.exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from cli.client.labels import LabelsAPIClient
from cli.client.preferences import PreferencesAPIClient
from cli.client.projects import ProjectsAPIClient
from cli.client.tasks import TasksAPIClient
from cli.client.views import ViewsAPIClient
from cli.client.workspaces import WorkspacesAPIClient

__all__ = [
    "BaseAPIClient",
    "TasksAPIClient",
    "WorkspacesAPIClient",
    "ProjectsAPIClient",
    "PreferencesAPIClient",
    "LabelsAPIClient",
    "ViewsAPIClient",
    "AIAPIClient",
    "APIError",
    "AuthenticationError",
    "ConflictError",
    "NotFoundError",
    "ValidationError",
]
