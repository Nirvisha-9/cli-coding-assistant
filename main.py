# main.py
# ─────────────────────────────────────────────────────────────
# Entry point — natural language input, no flags needed.
# User just describes what they want in plain English.
# ─────────────────────────────────────────────────────────────

import os
import click
from agent.loop import run_agent
from agent.core import generate_code, extract_code
from agent.prompts import SYSTEM_PROMPT, user_task_prompt
from agent.utils import save_code, print_header, print_footer
from agent.parser import parse_intent


@click.command()
@click.argument("request", nargs=-1, required=True)
@click.option("--retries", "-r", default=3, show_default=True,
              help="Max fix attempts")
@click.option("--dry-run", is_flag=True,
              help="Show code without running it")
def main(request, retries, dry_run):
    """
    \b
    CLI Coding Assistant — just describe what you want in plain English.

    \b
    Examples:
      code "print fibonacci numbers"
      code "build a calculator and save it to my documents"
      code "create a snake game on my desktop"
      code "write a todo app and put it in ~/Projects as todo.py"
      code "make a password generator and save to documents as passwords.py"
      code "build a web scraper" --dry-run
    """

    # Join all words into one string
    # Lets user skip quotes if they want:
    # code build a calculator and save to desktop
    user_input = " ".join(request)

    # ── Parse natural language ─────────────────────────────────
    click.echo(click.style("\n🧠 Understanding your request...", fg="bright_black"))
    intent = parse_intent(user_input)

    task      = intent["task"]
    full_path = intent["full_path"]

    # Show what the agent understood
    click.echo(click.style(f"   Task:    ", fg="bright_black") +
               click.style(task, fg="white"))

    if full_path:
        click.echo(click.style(f"   Save to: ", fg="bright_black") +
                   click.style(full_path, fg="cyan"))
    else:
        click.echo(click.style(
            "   Save to: not saving — add 'save to documents' or similar to save a file",
            fg="bright_black"
        ))

    # Create parent directories if needed
    if full_path:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

    print_header(task)

    # ── Dry run ────────────────────────────────────────────────
    if dry_run:
        click.echo(click.style("\n[Dry run — will not execute]\n", fg="yellow"))
        conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_task_prompt(task, full_path)}
        ]
        raw  = generate_code(conversation)
        code = extract_code(raw)
        click.echo(code)
        if full_path:
            save_code(code, full_path)
        print_footer(1, success=True)
        return

    # ── Normal run ─────────────────────────────────────────────
    code = run_agent(task, max_retries=retries, save_path=full_path)

    # Save final code if path was given
    if full_path and code:
        save_code(code, full_path)

    print_footer(1, success=True)


if __name__ == "__main__":
    main()