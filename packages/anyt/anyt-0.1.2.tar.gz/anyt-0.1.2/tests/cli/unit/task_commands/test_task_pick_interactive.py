"""Tests for interactive task picker functionality."""

from unittest.mock import patch

from cli.commands.task.pick import display_interactive_picker
from cli.models.common import Priority, Status
from tests.cli.unit.conftest import create_test_task


class TestDisplayInteractivePicker:
    """Tests for display_interactive_picker function."""

    def test_picker_empty_tasks(self):
        """Test picker with empty task list."""
        result = display_interactive_picker([])
        assert result is None

    def test_picker_with_grouping(self):
        """Test picker groups tasks by status correctly."""
        tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="Backlog task",
                status=Status.BACKLOG,
                priority=Priority.NORMAL,
            ),
            create_test_task(
                id=2,
                identifier="DEV-2",
                title="Todo task",
                status=Status.TODO,
                priority=Priority.HIGH,
            ),
            create_test_task(
                id=3,
                identifier="DEV-3",
                title="In progress task",
                status=Status.IN_PROGRESS,
                priority=Priority.HIGHEST,
            ),
        ]

        # Mock Prompt.ask to return "1" (first task)
        with patch("cli.commands.task.pick.Prompt.ask", return_value="1"):
            result = display_interactive_picker(tasks, group_by_status=True)

        assert result == "DEV-1"

    def test_picker_without_grouping(self):
        """Test picker without grouping."""
        tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="First task",
                status=Status.TODO,
                priority=Priority.NORMAL,
            ),
            create_test_task(
                id=2,
                identifier="DEV-2",
                title="Second task",
                status=Status.IN_PROGRESS,
                priority=Priority.HIGH,
            ),
        ]

        # Mock Prompt.ask to return "2" (second task)
        with patch("cli.commands.task.pick.Prompt.ask", return_value="2"):
            result = display_interactive_picker(tasks, group_by_status=False)

        assert result == "DEV-2"

    def test_picker_cancelled(self):
        """Test picker when user cancels with 'q'."""
        tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="Task",
                status=Status.TODO,
                priority=Priority.NORMAL,
            ),
        ]

        # Mock Prompt.ask to return "q" (quit)
        with patch("cli.commands.task.pick.Prompt.ask", return_value="q"):
            result = display_interactive_picker(tasks)

        assert result is None

    def test_picker_invalid_number(self):
        """Test picker with invalid selection number."""
        tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="Task",
                status=Status.TODO,
                priority=Priority.NORMAL,
            ),
        ]

        # Mock Prompt.ask to return invalid number "999"
        with patch("cli.commands.task.pick.Prompt.ask", return_value="999"):
            result = display_interactive_picker(tasks)

        assert result is None

    def test_picker_invalid_input(self):
        """Test picker with invalid non-numeric input."""
        tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="Task",
                status=Status.TODO,
                priority=Priority.NORMAL,
            ),
        ]

        # Mock Prompt.ask to return invalid input "abc"
        with patch("cli.commands.task.pick.Prompt.ask", return_value="abc"):
            result = display_interactive_picker(tasks)

        assert result is None

    def test_picker_handles_long_titles(self):
        """Test picker truncates long task titles."""
        tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="A" * 100,  # Very long title
                status=Status.TODO,
                priority=Priority.NORMAL,
            ),
        ]

        # Mock Prompt.ask to return "1"
        with patch("cli.commands.task.pick.Prompt.ask", return_value="1"):
            result = display_interactive_picker(tasks, group_by_status=False)

        assert result == "DEV-1"

    def test_picker_handles_all_priority_levels(self):
        """Test picker displays all priority levels correctly."""
        tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="P2",
                status=Status.TODO,
                priority=Priority.HIGHEST,
            ),
            create_test_task(
                id=2,
                identifier="DEV-2",
                title="P1",
                status=Status.TODO,
                priority=Priority.HIGH,
            ),
            create_test_task(
                id=3,
                identifier="DEV-3",
                title="P0",
                status=Status.TODO,
                priority=Priority.NORMAL,
            ),
            create_test_task(
                id=4,
                identifier="DEV-4",
                title="P-1",
                status=Status.TODO,
                priority=Priority.LOW,
            ),
            create_test_task(
                id=5,
                identifier="DEV-5",
                title="P-2",
                status=Status.TODO,
                priority=Priority.LOWEST,
            ),
        ]

        # Mock Prompt.ask to return "3" (middle priority)
        with patch("cli.commands.task.pick.Prompt.ask", return_value="3"):
            result = display_interactive_picker(tasks, group_by_status=False)

        assert result == "DEV-3"

    def test_picker_groups_multiple_statuses(self):
        """Test picker correctly groups tasks across multiple statuses."""
        tasks = [
            create_test_task(
                id=1,
                identifier="DEV-1",
                title="T1",
                status=Status.BACKLOG,
                priority=Priority.NORMAL,
            ),
            create_test_task(
                id=2,
                identifier="DEV-2",
                title="T2",
                status=Status.BACKLOG,
                priority=Priority.NORMAL,
            ),
            create_test_task(
                id=3,
                identifier="DEV-3",
                title="T3",
                status=Status.TODO,
                priority=Priority.NORMAL,
            ),
            create_test_task(
                id=4,
                identifier="DEV-4",
                title="T4",
                status=Status.IN_PROGRESS,
                priority=Priority.NORMAL,
            ),
            create_test_task(
                id=5,
                identifier="DEV-5",
                title="T5",
                status=Status.IN_PROGRESS,
                priority=Priority.NORMAL,
            ),
            create_test_task(
                id=6,
                identifier="DEV-6",
                title="T6",
                status=Status.DONE,
                priority=Priority.NORMAL,
            ),
        ]

        # Mock Prompt.ask to return "5" (second inprogress task)
        with patch("cli.commands.task.pick.Prompt.ask", return_value="5"):
            result = display_interactive_picker(tasks, group_by_status=True)

        assert result == "DEV-5"
