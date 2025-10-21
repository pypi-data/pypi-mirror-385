"""Common types and enums used across the CLI."""

from enum import Enum


class Status(str, Enum):
    """Task status values."""

    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class Priority(int, Enum):
    """Task priority values."""

    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    HIGHEST = 2
