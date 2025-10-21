"""Common types and enums used across the CLI."""

from enum import Enum


class Status(str, Enum):
    """Task status values.

    Note: Values must match backend API exactly.
    Backend uses: backlog, todo, inprogress, canceled, done
    """

    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "inprogress"  # Backend uses no underscore
    CANCELED = "canceled"  # Backend uses single 'l'
    DONE = "done"


class Priority(int, Enum):
    """Task priority values."""

    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    HIGHEST = 2
