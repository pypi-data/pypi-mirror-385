#!/usr/bin/env python3
"""Generate comprehensive help documentation using Typer introspection."""

import sys
from pathlib import Path
from typing import Any

import typer
import typer.core
from click import Command, Group


def format_params(params: list[Any]) -> str:
    """Format command parameters."""
    if not params:
        return ""

    lines = []
    for param in params:
        param_type = "Option" if param.param_type_name == "option" else "Argument"
        param_names = " / ".join(param.opts) if hasattr(param, "opts") else param.name
        help_text = param.help or "(no help text)"
        lines.append(f"  **{param_names}** [{param_type}]")
        lines.append(f"    {help_text}")

    return "\n".join(lines)


def extract_command_help(cmd: Command, prefix: str = "") -> list[str]:
    """Recursively extract help from a Typer/Click command."""
    lines = []

    # Command header
    cmd_name = f"{prefix} {cmd.name}" if prefix else cmd.name or "anyt"
    level = len(cmd_name.split())
    header = "#" * (level + 1)

    lines.append(f"\n{header} {cmd_name}\n")
    lines.append("-" * 80)

    # Command help
    if cmd.help:
        lines.append(f"\n{cmd.help}\n")

    # Usage
    ctx = typer.Context(cmd)
    lines.append("**Usage:**")
    lines.append(f"```\n{cmd.get_usage(ctx)}\n```\n")

    # Parameters
    if cmd.params:
        lines.append("**Parameters:**\n")
        lines.append(format_params(cmd.params))
        lines.append("")

    # Recurse into subcommands if this is a group
    if isinstance(cmd, Group):
        subcommands = sorted(cmd.commands.items())
        if subcommands:
            lines.append("\n**Subcommands:**\n")
            for sub_name, _ in subcommands:
                lines.append(f"- `{sub_name}`")
            lines.append("")

            # Recursively document subcommands
            for sub_name, sub_cmd in subcommands:
                lines.extend(extract_command_help(sub_cmd, cmd_name))

    lines.append("\n" + "=" * 80 + "\n")
    return lines


def generate_help_docs() -> str:
    """Generate comprehensive help documentation using introspection."""
    # Import the main app
    from cli.main import app

    output = []
    output.append("# AnyTask CLI - Complete Command Reference\n")
    output.append("Auto-generated from Typer app introspection.\n")
    output.append("=" * 80 + "\n")

    # Get the Click command from Typer app
    click_cmd = typer.main.get_command(app)

    # Extract help recursively
    output.extend(extract_command_help(click_cmd))

    return "\n".join(output)


def main():
    """Main entry point."""
    print("Generating help documentation using Typer introspection...", file=sys.stderr)

    try:
        docs = generate_help_docs()

        # Write to file
        output_file = Path("docs/CLI_COMPLETE_REFERENCE.md")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(docs)

        print(f"✓ Documentation generated: {output_file}", file=sys.stderr)
        print(f"  Total size: {len(docs):,} bytes", file=sys.stderr)
        print(f"\nTo view: cat {output_file}", file=sys.stderr)

    except Exception as e:
        print(f"✗ Error generating documentation: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
