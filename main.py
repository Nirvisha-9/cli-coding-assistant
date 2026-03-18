# main.py
# ─────────────────────────────────────────────────────────────
# Entry point — this is the file you run.
# All it does is define the CLI interface and call into agent/.
# Keeping CLI logic here means agent/ stays clean and testable.
# ─────────────────────────────────────────────────────────────

import click
from agent.loop import run_agent
from agent.core import generate_code, extract_code
from agent.prompts import SYSTEM_PROMPT, user_task_prompt
from agent.utils import save_code, auto_filename, print_header, print_footer


@click.command()
@click.argument("task")
@click.option(
    "--output", "-o",
    default=None,
    help="Save generated code to this file path (e.g. scripts/sorter.py)"
)
@click.option(
    "--retries", "-r",
    default=3,
    show_default=True,
    help="Max number of fix attempts if code fails"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Generate code but do NOT run it — just print it"
)
@click.option(
    "--save",
    is_flag=True,
    help="Auto-save code to a file named after the task"
)
def main(task, output, retries, dry_run, save):
    """
    \b
    CLI Coding Assistant — describe a task, get working Python code.

    \b
    The agent will:
      1. Generate Python code for your task
      2. Run it automatically
      3. If it fails, read the error and fix itself
      4. Retry up to --retries times

    \b
    Examples:
      python main.py "print the first 10 fibonacci numbers"
      python main.py "read a csv and print column names" --output reader.py
      python main.py "build a number guessing game" --dry-run
      python main.py "sort a list of dicts by age key" --save --retries 5
    """

    print_header(task)
    success = False
    attempt_count = 1

    # ── Dry run mode ───────────────────────────────────────────
    # Just generate and print — don't execute anything.
    # Useful when you want to review code before running it.
    if dry_run:
        click.echo(click.style(
            "\n[Dry run mode — code will not be executed]\n",
            fg="yellow"
        ))
        conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_task_prompt(task)}
        ]
        raw = generate_code(conversation)
        code = extract_code(raw)
        click.echo(code)

        # Still save if requested
        path = output or (auto_filename(task) if save else None)
        if path:
            save_code(code, path)

        print_footer(1, success=True)
        return

    # ── Normal mode — generate, run, fix loop ──────────────────
    code = run_agent(task, max_retries=retries)

    # Determine if it succeeded by checking if last run passed.
    # run_agent returns early on success, so if we got code back
    # we count it as done (even if it needed retries).
    success = True

    # ── Save output ────────────────────────────────────────────
    # Priority: --output path > --save (auto name) > don't save
    path = output or (auto_filename(task) if save else None)
    if path:
        save_code(code, path)

    print_footer(attempt_count, success=success)


if __name__ == "__main__":
    main()