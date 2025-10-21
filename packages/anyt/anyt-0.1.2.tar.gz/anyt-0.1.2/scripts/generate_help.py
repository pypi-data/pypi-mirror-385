#!/usr/bin/env python3
"""Generate comprehensive help documentation for all CLI commands."""

import subprocess
import sys
from pathlib import Path


def get_help_output(command: list[str]) -> str:
    """Run command with --help and capture output."""
    try:
        result = subprocess.run(
            ["uv", "run", "anyt"] + command + ["--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting help for {' '.join(command)}: {e}"


def generate_help_docs() -> str:
    """Generate comprehensive help documentation."""

    # Define all commands and subcommands
    commands = [
        # Top-level
        [],
        ["active"],
        ["board"],
        ["timeline"],
        ["summary"],
        ["graph"],
        ["init"],
        # Environment
        ["env"],
        ["env", "list"],
        ["env", "add"],
        ["env", "remove"],
        ["env", "switch"],
        ["env", "show"],
        # Auth
        ["auth"],
        ["auth", "login"],
        ["auth", "logout"],
        ["auth", "whoami"],
        # Workspace
        ["workspace"],
        ["workspace", "init"],
        ["workspace", "list"],
        ["workspace", "switch"],
        ["workspace", "use"],
        ["workspace", "current"],
        # Project
        ["project"],
        ["project", "create"],
        ["project", "list"],
        ["project", "use"],
        ["project", "current"],
        ["project", "switch"],
        # Task
        ["task"],
        ["task", "add"],
        ["task", "create"],
        ["task", "list"],
        ["task", "show"],
        ["task", "edit"],
        ["task", "done"],
        ["task", "note"],
        ["task", "rm"],
        ["task", "pick"],
        ["task", "suggest"],
        ["task", "dep"],
        ["task", "dep", "add"],
        ["task", "dep", "rm"],
        ["task", "dep", "list"],
        # Label
        ["label"],
        ["label", "create"],
        ["label", "list"],
        ["label", "show"],
        ["label", "edit"],
        ["label", "rm"],
        # View
        ["view"],
        ["view", "create"],
        ["view", "list"],
        ["view", "show"],
        ["view", "apply"],
        ["view", "edit"],
        ["view", "rm"],
        ["view", "default"],
        # AI
        ["ai"],
        ["ai", "decompose"],
        ["ai", "organize"],
        ["ai", "fill"],
        ["ai", "suggest"],
        ["ai", "review"],
        ["ai", "summary"],
        ["ai", "config"],
        ["ai", "test"],
        ["ai", "usage"],
        # Template
        ["template"],
        ["template", "init"],
        ["template", "list"],
        ["template", "show"],
        ["template", "edit"],
        # Preference
        ["preference"],
        ["preference", "show"],
        ["preference", "set-workspace"],
        ["preference", "set-project"],
        ["preference", "clear"],
        # Health
        ["health"],
        ["health", "check"],
    ]

    output = []
    output.append("# AnyTask CLI - Complete Command Reference\n")
    output.append(
        "Auto-generated comprehensive help for all commands and subcommands.\n"
    )
    output.append("=" * 80 + "\n\n")

    for cmd in commands:
        # Create section header
        cmd_str = " ".join(cmd) if cmd else "anyt (top-level)"
        output.append(f"\n{'#' * (len(cmd) + 2)} {cmd_str}\n")
        output.append("-" * 80 + "\n")

        # Get help output
        help_text = get_help_output(cmd)
        output.append(help_text)
        output.append("\n" + "=" * 80 + "\n")

    return "\n".join(output)


def main():
    """Main entry point."""
    print("Generating comprehensive help documentation...", file=sys.stderr)

    docs = generate_help_docs()

    # Write to file
    output_file = Path("docs/CLI_COMPLETE_REFERENCE.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(docs)

    print(f"✓ Documentation generated: {output_file}", file=sys.stderr)
    print(f"  Total size: {len(docs):,} bytes", file=sys.stderr)


if __name__ == "__main__":
    main()
