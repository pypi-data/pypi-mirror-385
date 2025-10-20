#!/usr/bin/env python3
"""
PreToolUse hook for Claude Code.
This script is called before Claude uses a tool.
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
        logger = get_logger("PreToolUse")

        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())
        logger.log_hook_input(hook_input)

        # Extract tool information
        tool_name = hook_input.get("toolName", "unknown")
        tool_input = hook_input.get("toolInput", {})

        # Log pre-tool use details
        tool_info = {
            "event": "pre_tool_use",
            "tool_name": tool_name,
            "timestamp": hook_input.get("timestamp", "unknown"),
            "has_input": bool(tool_input),
        }
        logger.log_event(tool_info)
        logger.debug(
            f"Pre-tool use: '{tool_name}' about to be invoked with input: {json.dumps(tool_input, indent=2)}"
        )

        # Prepare output (no additional context needed)
        output = {}
        logger.log_hook_output(output)

        # Return output
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        logger = get_logger("PreToolUse")
        logger.log_error("Error in PreToolUse hook", e)
        print(json.dumps({}))
        sys.exit(1)


if __name__ == "__main__":
    main()
