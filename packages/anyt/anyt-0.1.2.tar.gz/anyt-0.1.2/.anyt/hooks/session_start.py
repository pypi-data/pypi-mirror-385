#!/usr/bin/env python3
"""
SessionStart hook for Claude Code.
This script is called when a Claude Code session starts.
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
        logger = get_logger("SessionStart")
        logger.info("=" * 80)
        logger.info("NEW SESSION STARTED")
        logger.info("=" * 80)

        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())
        logger.log_hook_input(hook_input)

        # Log session start details
        session_info = {
            "event": "session_start",
            "timestamp": hook_input.get("timestamp", "unknown"),
            "working_directory": hook_input.get("workingDirectory", "unknown"),
        }
        logger.log_event(session_info)

        # Prepare output (no additional context needed for session start)
        output = {}
        logger.log_hook_output(output)

        # Return output
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        logger = get_logger("SessionStart")
        logger.log_error("Error in SessionStart hook", e)
        # Return empty output on error
        print(json.dumps({}))
        sys.exit(1)


if __name__ == "__main__":
    main()
