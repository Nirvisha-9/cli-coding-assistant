# main.py

import os
import click
from agent.loop import run_agent
from agent.core import generate_code, extract_code
from agent.prompts import SYSTEM_PROMPT, user_task_prompt
from agent.utils import save_code, print_header, print_footer
from agent.parser import parse_intent
from agent.chat import run_chat


@click.command()
@click.argument("request", nargs=-1, required=False)
@click.option("--chat", "-c", is_flag=True,
              help="Start an interactive chat session")
@click.option("--retries", "-r", default=3, show_default=True,
              help="Max fix attempts")
@click.option("--dry-run", is_flag=True,
              help="Show code without running it")
def main(request, chat, retries, dry_run):
    """
    \b
    CLI Coding Assistant — describe a task, get working Python code.

    \b
    Single task mode:
      code "print fibonacci numbers"
      code "build a calculator and save it to my documents"
      code "create a snake game on my desktop as snake.py"

    \b
    Chat mode — remembers everything across tasks:
      code --chat
    """

    # ── Chat mode ──────────────────────────────────────────────
    if chat:
        run_chat(max_retries=retries)
        return

    # ── Single task mode ───────────────────────────────────────
    if not request:
        click.echo(click.style(
            "\n❌ Please provide a task or use --chat for interactive mode.\n"
            "   Example: code \"build a calculator\"\n"
            "   Example: code --chat\n",
            fg="red"
        ))
        return

    user_input = " ".join(request)

    # Parse natural language
    click.echo(click.style("\n🧠 Understanding your request...", fg="bright_black"))
    intent    = parse_intent(user_input)
    task      = intent["task"]
    full_path = intent["full_path"]

    click.echo(click.style("   Task:    ", fg="bright_black") +
               click.style(task, fg="white"))

    if full_path:
        click.echo(click.style("   Save to: ", fg="bright_black") +
                   click.style(full_path, fg="cyan"))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    else:
        click.echo(click.style(
            "   Save to: not saving — add 'save to documents' to save a file",
            fg="bright_black"
        ))

    print_header(task)

    # Dry run
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

    # Normal run
    code = run_agent(task, max_retries=retries, save_path=full_path)
    if full_path and code:
        save_code(code, full_path)
    print_footer(1, success=True)


if __name__ == "__main__":
    main()