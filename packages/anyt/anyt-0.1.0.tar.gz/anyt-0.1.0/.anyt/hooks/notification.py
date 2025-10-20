#!/usr/bin/env python3
"""
Notification hook for task status updates.
This script is called when Claude is about to send a notification.
"""

import sys
import json
from pathlib import Path

# Add hooks directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from hook_logger import get_logger


def main():
    """Main hook execution."""
    try:
        # Initialize logger
        logger = get_logger("Notification")

        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())
        logger.log_hook_input(hook_input)

        # Define paths
        project_root = Path("/Users/bsheng/work/AnyTaskBackend")
        tasks_dir = project_root / ".anyt" / "tasks"
        active_dir = tasks_dir / "active"
        tasks_dir / "backlog"

        # Get current active tasks
        active_tasks = list(active_dir.glob("*.md")) if active_dir.exists() else []

        # Log notification details
        notification_info = {
            "event": "notification",
            "notification_type": hook_input.get("type", "unknown"),
            "active_tasks_count": len(active_tasks),
            "timestamp": hook_input.get("timestamp", "unknown"),
        }
        logger.log_event(notification_info)
        logger.info(f"Notification triggered: {hook_input.get('type', 'unknown')}")

        # Prepare additional context for Claude
        additional_context = f"""

TASK STATUS UPDATE REQUIRED:
Before sending this notification, please update task status:

1. Check tasks in {active_dir}
2. Add timestamped update (YYYY-MM-DD HH:MM format) to the task file
3. If task is completed: move to .anyt/tasks/done
4. If task is blocked: update status to "blocked" in the file
5. If still active: update status to "active"
6. If no active tasks: create new task based on backlog schema

Current active tasks: {[t.name for t in active_tasks]}
"""

        # Return additional context to Claude
        output = {"additionalContext": additional_context}
        logger.log_hook_output(output)

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        logger = get_logger("Notification")
        logger.log_error("Error in Notification hook", e)
        print(json.dumps({}))
        sys.exit(1)


if __name__ == "__main__":
    main()
