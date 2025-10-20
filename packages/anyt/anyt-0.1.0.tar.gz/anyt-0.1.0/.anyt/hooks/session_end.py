#!/usr/bin/env python3
"""
SessionEnd hook for Claude Code.
This script is called when a Claude Code session ends.
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
        logger = get_logger("SessionEnd")

        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())
        logger.log_hook_input(hook_input)

        # Log session end details
        session_info = {
            "event": "session_end",
            "timestamp": hook_input.get("timestamp", "unknown"),
            "duration": hook_input.get("duration", "unknown"),
        }
        logger.log_event(session_info)
        logger.info("=" * 80)
        logger.info("SESSION ENDED")
        logger.info("=" * 80)

        # Prepare output
        output = {}
        logger.log_hook_output(output)

        # Return output
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        logger = get_logger("SessionEnd")
        logger.log_error("Error in SessionEnd hook", e)
        print(json.dumps({}))
        sys.exit(1)


if __name__ == "__main__":
    main()
