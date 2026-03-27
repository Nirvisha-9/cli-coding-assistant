# agent/chat.py
# ─────────────────────────────────────────────────────────────
# Chat mode — persistent conversation across multiple tasks.
# The LLM remembers everything it wrote in the session so
# follow-up instructions like "add error handling to it"
# work exactly as expected.
#
# Key difference from normal mode:
# Normal: fresh conversation every single run
# Chat:   one conversation that grows with every message
# ─────────────────────────────────────────────────────────────

import os
import click
from pathlib import Path
from agent.core import generate_code, extract_code, execute_code
from agent.prompts import SYSTEM_PROMPT, fix_prompt
from agent.utils import save_code
from agent.parser import parse_intent


# ── Special commands the user can type ────────────────────────
COMMANDS = {
    "exit":  "quit the session",
    "quit":  "quit the session",
    "bye":   "quit the session",
    "reset": "clear conversation and start fresh",
    "clear": "clear conversation and start fresh",
    "show":  "show the last generated code",
    "save":  "save last code — usage: save ~/Desktop/file.py",
    "help":  "show available commands",
}


def run_chat(max_retries: int = 3):
    """
    Start an interactive chat session.
    Conversation history persists across all tasks in the session.
    """

    _print_welcome()

    # ── Conversation history ───────────────────────────────────
    # This is the core of chat mode.
    # Every message — user and assistant — gets appended here.
    # The full history is sent to the LLM on every request
    # so it always has full context of what it wrote before.
    conversation = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\nYou are in an ongoing chat session. "
                       "Remember all code you have written so far in this conversation. "
                       "When the user says 'it', 'that', 'the function', etc — "
                       "they are referring to code you wrote earlier in this session."
        }
    ]

    last_code = None  # tracks the most recently generated code

    while True:
        # ── Get user input ─────────────────────────────────────
        try:
            user_input = click.prompt(
                click.style("\nYou", fg="bright_cyan", bold=True),
                prompt_suffix=click.style(": ", fg="bright_cyan")
            )
        except (KeyboardInterrupt, EOFError):
            _print_goodbye()
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        # ── Handle special commands ────────────────────────────
        command = user_input.lower()

        if command in ("exit", "quit", "bye"):
            _print_goodbye()
            break

        if command in ("reset", "clear"):
            conversation = [conversation[0]]  # keep system prompt, clear the rest
            last_code = None
            click.echo(click.style(
                "🔄 Conversation reset — starting fresh.",
                fg="yellow"
            ))
            continue

        if command == "show":
            if last_code:
                _print_code_block(last_code)
            else:
                click.echo(click.style("No code generated yet.", fg="bright_black"))
            continue

        if command.startswith("save"):
            if not last_code:
                click.echo(click.style("No code to save yet.", fg="bright_black"))
                continue
            # Parse save path from command
            # "save ~/Desktop/file.py" or just "save" (auto-name)
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                save_path = os.path.expanduser(parts[1].strip())
            else:
                # Ask where to save
                save_path = click.prompt(
                    click.style("Save to", fg="bright_black"),
                    default=str(Path.home() / "Documents" / "output.py")
                )
                save_path = os.path.expanduser(save_path)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            save_code(last_code, save_path)
            continue

        if command == "help":
            _print_help()
            continue

        # ── Check if user mentioned saving in their message ────
        # e.g. "write a calculator and save to my desktop"
        # We parse the intent to extract task + path
        intent    = parse_intent(user_input)
        task      = intent["task"]
        save_path = intent["full_path"]

        if save_path:
            click.echo(click.style(
                f"   → Will save to: {save_path}",
                fg="bright_black"
            ))

        # ── Add user message to conversation ───────────────────
        # Build the message — if there's a save path, include it
        message_content = task
        if save_path:
            message_content += f"\n\nIMPORTANT: Save the file to: {save_path}"

        conversation.append({
            "role": "user",
            "content": message_content
        })

        # ── Generate → Execute → Fix loop ─────────────────────
        code = _generate_and_fix(conversation, max_retries)
        last_code = code

        # ── Add final code to conversation as assistant message ─
        # This is critical — the LLM needs to see its own output
        # in the conversation history for follow-ups to work.
        conversation.append({
            "role": "assistant",
            "content": code
        })

        # ── Auto-save if path was detected ─────────────────────
        if save_path and code:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            save_code(code, save_path)

        click.echo(click.style(
            "\n💬 What next? (type 'help' for commands)",
            fg="bright_black"
        ))


def _generate_and_fix(conversation: list[dict], max_retries: int) -> str:
    """
    Generate code, run it, fix if needed.
    Same feedback loop as normal mode but uses the shared conversation.

    Key difference: we don't append to conversation here —
    the caller (run_chat) handles that so the history stays clean.
    We use a local copy for the fix attempts.
    """

    # Work on a copy so fix attempts don't pollute the main conversation
    local_conv = list(conversation)
    last_code  = ""

    for attempt in range(1, max_retries + 1):
        click.echo(click.style(
            f"\n→ Generating... (attempt {attempt}/{max_retries})",
            fg="cyan"
        ))

        raw  = generate_code(local_conv)
        code = extract_code(raw)
        last_code = code

        _print_code_block(code)

        click.echo(click.style("→ Running...", fg="cyan"))
        stdout, stderr, returncode = execute_code(code)

        if returncode == 0:
            click.echo(click.style("✅ Done.", fg="green", bold=True))
            if stdout:
                _print_output_block(stdout)
            return code

        # Failed — show error and try to fix
        error_msg = stderr if stderr else stdout
        click.echo(click.style(f"✗ Error: {error_msg.strip()}", fg="red"))

        if attempt < max_retries:
            click.echo(click.style("→ Fixing...", fg="yellow"))
            local_conv.append({"role": "assistant", "content": raw})
            local_conv.append({"role": "user",      "content": fix_prompt(error_msg)})

    click.echo(click.style("⚠️  Could not fix. Showing best attempt.", fg="yellow"))
    return last_code


# ── Print helpers ──────────────────────────────────────────────

def _print_welcome():
    click.echo(click.style(
        "\n🤖  CLI Coding Assistant — Chat Mode",
        fg="bright_cyan", bold=True
    ))
    click.echo(click.style("─" * 44, fg="bright_black"))
    click.echo(click.style(
        "Describe tasks naturally. The assistant remembers\n"
        "everything it writes so follow-ups work perfectly.",
        fg="bright_black"
    ))
    click.echo(click.style(
        "Type 'help' for commands, 'exit' to quit.",
        fg="bright_black"
    ))
    click.echo(click.style("─" * 44, fg="bright_black"))


def _print_goodbye():
    click.echo(click.style("\n👋 Bye!\n", fg="bright_cyan", bold=True))


def _print_help():
    click.echo(click.style("\nAvailable commands:", fg="bright_black"))
    for cmd, desc in COMMANDS.items():
        click.echo(
            click.style(f"  {cmd:<8}", fg="cyan") +
            click.style(f" — {desc}", fg="bright_black")
        )


def _print_code_block(code: str):
    click.echo(click.style(
        "\n┌── Generated code ──────────────────────",
        fg="bright_black"
    ))
    for line in code.splitlines():
        click.echo(click.style("│ ", fg="bright_black") + line)
    click.echo(click.style(
        "└────────────────────────────────────────\n",
        fg="bright_black"
    ))


def _print_output_block(output: str):
    click.echo(click.style(
        "\n┌── Output ───────────────────────────────",
        fg="bright_black"
    ))
    for line in output.strip().splitlines():
        click.echo(click.style("│ ", fg="bright_black") + line)
    click.echo(click.style(
        "└─────────────────────────────────────────",
        fg="bright_black"
    ))