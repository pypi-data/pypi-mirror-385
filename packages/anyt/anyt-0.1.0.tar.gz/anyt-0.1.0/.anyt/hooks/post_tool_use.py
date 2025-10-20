#!/usr/bin/env python3
"""
PostToolUse hook for Claude Code.
This script is called after Claude uses a tool.
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
        logger = get_logger("PostToolUse")

        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())
        logger.log_hook_input(hook_input)

        # Extract tool information
        tool_name = hook_input.get("toolName", "unknown")
        tool_result = hook_input.get("toolResult", {})
        success = hook_input.get("success", True)

        # Log post-tool use details
        tool_info = {
            "event": "post_tool_use",
            "tool_name": tool_name,
            "success": success,
            "timestamp": hook_input.get("timestamp", "unknown"),
            "has_result": bool(tool_result),
        }
        logger.log_event(tool_info)

        if success:
            logger.debug(f"Post-tool use: '{tool_name}' completed successfully")
        else:
            logger.warning(f"Post-tool use: '{tool_name}' failed")

        # Prepare output (no additional context needed)
        output = {}
        logger.log_hook_output(output)

        # Return output
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        logger = get_logger("PostToolUse")
        logger.log_error("Error in PostToolUse hook", e)
        print(json.dumps({}))
        sys.exit(1)


if __name__ == "__main__":
    main()
