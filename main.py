# main.py

import os
import click
from agent.loop import run_agent
from agent.core import generate_code, extract_code
from agent.prompts import SYSTEM_PROMPT, user_task_prompt
from agent.utils import save_code, print_header, print_footer
from agent.parser import parse_intent, is_explanation_request
from agent.chat import run_chat
from agent.explainer import explain_code, explain_topic, print_explanation


@click.command()
@click.argument("request", nargs=-1, required=False)
@click.option("--chat", "-c", is_flag=True,
              help="Start an interactive chat session")
@click.option("--explain", "-e", is_flag=True,
              help="Explain the generated code in plain English")
@click.option("--retries", "-r", default=3, show_default=True,
              help="Max fix attempts")
@click.option("--dry-run", is_flag=True,
              help="Show code without running it")
def main(request, chat, explain, retries, dry_run):
    """
    \b
    CLI Coding Assistant — describe a task, get working Python code.

    \b
    Single task mode:
      code "print fibonacci numbers"
      code "build a calculator and save it to my documents"
      code "implement binary search" --explain
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
        if explain:
            click.echo(click.style("\n🧠 Explaining...", fg="bright_black"))
            print_explanation(explain_code(code))
        print_footer(1, success=True)
        return

    # ── Detect explanation-style requests and handle them ────────
    # If the user asked for an explanation (e.g. "explain binary search")
    # we answer with an explanation instead of generating/running code.
    if is_explanation_request(user_input):
        click.echo(click.style("\n🧠 Explaining...\n", fg="bright_black"))
        explanation = explain_topic(user_input)
        print_explanation(explanation)
        return

    # ── Normal run ─────────────────────────────────────────────
    code = run_agent(task, max_retries=retries, save_path=full_path)

    if full_path and code:
        save_code(code, full_path)

    # ── Explain if flag set ────────────────────────────────────
    if explain and code:
        click.echo(click.style("\n🧠 Explaining the code...", fg="bright_black"))
        explanation = explain_code(code)
        print_explanation(explanation)

    print_footer(1, success=True)


if __name__ == "__main__":
    main()