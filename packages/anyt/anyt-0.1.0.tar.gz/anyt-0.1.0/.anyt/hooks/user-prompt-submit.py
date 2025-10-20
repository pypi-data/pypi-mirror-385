#!/usr/bin/env python3
"""
UserPromptSubmit hook for task management.
This script is called when a user submits a prompt.
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
        logger = get_logger("UserPromptSubmit")

        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())
        logger.log_hook_input(hook_input)

        user_prompt = hook_input.get("prompt", "")

        # Define paths
        project_root = Path("/Users/bsheng/work/AnyTaskBackend")
        tasks_dir = project_root / ".anyt" / "tasks"
        active_dir = tasks_dir / "active"
        tasks_dir / "backlog"

        # Get current active tasks
        active_tasks = list(active_dir.glob("*.md")) if active_dir.exists() else []

        # Log prompt details
        prompt_info = {
            "event": "user_prompt_submit",
            "prompt_length": len(user_prompt),
            "prompt_preview": user_prompt[:100] + "..."
            if len(user_prompt) > 100
            else user_prompt,
            "active_tasks_count": len(active_tasks),
            "timestamp": hook_input.get("timestamp", "unknown"),
        }
        logger.log_event(prompt_info)
        logger.info(f"User submitted prompt: {user_prompt[:100]}...")

        # Prepare additional context for Claude
        additional_context = f"""

TASK MANAGEMENT CONTEXT:
- Current active tasks: {len(active_tasks)}
- Task directory: {tasks_dir}

INSTRUCTIONS FOR CLAUDE:
When you receive this user instruction, please:
1. Check if it belongs to one of the active tasks in {active_dir}
2. If yes: Update that task's status and add a timestamped entry
3. If no: Move current active task(s) to backlog and create a new task
4. Task ID format: section_id-ticket_num (e.g., T2-4)

User's prompt: {user_prompt}
"""

        # Return additional context to Claude
        output = {"additionalContext": additional_context}
        logger.log_hook_output(output)

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        logger = get_logger("UserPromptSubmit")
        logger.log_error("Error in UserPromptSubmit hook", e)
        print(json.dumps({}))
        sys.exit(1)


if __name__ == "__main__":
    main()
