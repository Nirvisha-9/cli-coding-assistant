# agent/utils.py
# ─────────────────────────────────────────────────────────────
# Helper functions — file saving, formatting, small utilities.
# Anything that doesn't belong in core.py or loop.py lives here.
# ─────────────────────────────────────────────────────────────

import os
import click
from datetime import datetime


def save_code(code: str, output_path: str) -> None:
    """
    Save generated code to a file.
    Creates parent directories if they don't exist.
    """
    # Create parent dirs if needed (e.g. output/scripts/task.py)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w") as f:
        f.write(code)

    click.echo(click.style(f"\n💾 Saved to: {output_path}", fg="green"))


def auto_filename(task: str) -> str:
    """
    Generate a filename from the task description if user didn't specify one.
    Example: "sort a list of dicts" → "sort_a_list_of_dicts.py"
    """
    # Take first 5 words, lowercase, replace spaces with underscores
    words = task.lower().split()[:5]
    base = "_".join(words)
    # Remove special characters
    base = "".join(c for c in base if c.isalnum() or c == "_")
    return f"{base}.py"


def print_header(task: str) -> None:
    """Print the opening banner when the agent starts."""
    click.echo(click.style("\n🤖  CLI Coding Assistant", fg="bright_cyan", bold=True))
    click.echo(click.style("─" * 44, fg="bright_black"))
    click.echo(click.style(f"Task: ", fg="bright_black") + click.style(task, fg="white"))
    click.echo(click.style(f"Time: {datetime.now().strftime('%H:%M:%S')}", fg="bright_black"))


def print_footer(attempt_count: int, success: bool) -> None:
    """Print the closing summary when the agent finishes."""
    click.echo(click.style("\n" + "─" * 44, fg="bright_black"))
    if success:
        click.echo(click.style(
            f"✨ Done in {attempt_count} attempt(s).",
            fg="bright_cyan", bold=True
        ))
    else:
        click.echo(click.style(
            f"⚠️  Finished after {attempt_count} attempt(s) — check output manually.",
            fg="yellow"
        ))
    click.echo("")