"""Domain models for the AnyTask CLI."""

from cli.models.ai import (
    AIUsage,
    AISuggestions,
    OrganizationResult,
    TaskAutoFill,
    TaskReview,
    WorkspaceSummary,
)
from cli.models.common import Priority, Status
from cli.models.dependency import TaskDependency
from cli.models.goal import Goal, GoalDecomposition
from cli.models.label import Label, LabelCreate, LabelUpdate
from cli.models.project import Project, ProjectCreate
from cli.models.task import Task, TaskCreate, TaskFilters, TaskUpdate
from cli.models.user import User, UserPreferences
from cli.models.view import TaskView, TaskViewCreate, TaskViewUpdate
from cli.models.workspace import Workspace, WorkspaceCreate

__all__ = [
    # Common
    "Status",
    "Priority",
    # Task
    "Task",
    "TaskCreate",
    "TaskUpdate",
    "TaskFilters",
    # Workspace
    "Workspace",
    "WorkspaceCreate",
    # Project
    "Project",
    "ProjectCreate",
    # Label
    "Label",
    "LabelCreate",
    "LabelUpdate",
    # User
    "User",
    "UserPreferences",
    # View
    "TaskView",
    "TaskViewCreate",
    "TaskViewUpdate",
    # Goal
    "Goal",
    "GoalDecomposition",
    # Dependency
    "TaskDependency",
    # AI
    "AIUsage",
    "AISuggestions",
    "OrganizationResult",
    "TaskAutoFill",
    "TaskReview",
    "WorkspaceSummary",
]
