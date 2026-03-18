# agent/loop.py
# ─────────────────────────────────────────────────────────────
# The agent brain — the feedback loop.
# This is what separates an agent from a simple LLM call.
#
# The pattern: Generate → Execute → Observe → Fix → Repeat
# This same pattern appears in EVERY serious agent system.
# Learn it here, use it everywhere.
# ─────────────────────────────────────────────────────────────

import click
from agent.core import generate_code, extract_code, execute_code
from agent.prompts import SYSTEM_PROMPT, user_task_prompt, fix_prompt


def run_agent(task: str, max_retries: int = 3) -> str:
    """
    Main agent loop.

    How it works:
    1. Build a conversation starting with system prompt + user task
    2. Ask the LLM to generate code
    3. Extract clean code from the response
    4. Execute the code
    5. If it passes → done, return the code
    6. If it fails → append the error to conversation, ask LLM to fix
    7. Repeat from step 2 up to max_retries times

    The conversation history is the key — by appending each attempt
    and each error, the LLM builds up context about what went wrong.
    It's not just retrying blindly, it's learning from each failure
    within the same session.

    Args:
        task: plain English description of what to build
        max_retries: how many fix attempts before giving up

    Returns:
        The best code generated (even if it never fully passed)
    """

    # ── Step 1: Initialize conversation ───────────────────────
    # Every conversation starts with a system message (instructions)
    # followed by the user's task.
    # This is the standard message format for all LLM APIs.
    conversation = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_task_prompt(task)
        }
    ]

    last_code = ""

    for attempt in range(1, max_retries + 1):

        # ── Step 2: Generate ───────────────────────────────────
        _print_divider()
        click.echo(click.style(
            f"→ Attempt {attempt}/{max_retries}: Generating code...",
            fg="cyan"
        ))

        raw_response = generate_code(conversation)
        code = extract_code(raw_response)
        last_code = code

        _print_code_block(code)

        # ── Step 3: Execute ────────────────────────────────────
        click.echo(click.style("→ Running code...", fg="cyan"))
        stdout, stderr, returncode = execute_code(code)

        # ── Step 4: Observe ────────────────────────────────────
        if returncode == 0:
            # Success — print output and return
            click.echo(click.style("✅ Success!", fg="green", bold=True))
            if stdout:
                _print_output_block(stdout)
            return code

        # Failure — show the error
        error_msg = stderr if stderr else stdout
        click.echo(click.style("✗ Failed:", fg="red"))
        click.echo(click.style(error_msg.strip(), fg="red"))

        # ── Step 5: Fix ────────────────────────────────────────
        # Only attempt a fix if we have retries remaining
        if attempt < max_retries:
            click.echo(click.style(
                f"→ Fixing... ({max_retries - attempt} attempt(s) remaining)",
                fg="yellow"
            ))

            # This is the core of the feedback loop:
            # We append TWO messages to the conversation:
            # 1. The assistant's previous attempt (role: assistant)
            # 2. The error message as a new user message (role: user)
            #
            # Now the LLM's context looks like:
            # system: be a good coder
            # user: write code for X
            # assistant: [broken code]       ← what it tried
            # user: that failed with error Y  ← what went wrong
            #
            # The LLM now has everything it needs to write a better fix.
            conversation.append({
                "role": "assistant",
                "content": raw_response
            })
            conversation.append({
                "role": "user",
                "content": fix_prompt(error_msg)
            })

    # Exhausted all retries
    click.echo(click.style(
        f"\n⚠️  Could not fix after {max_retries} attempts. Showing best attempt.",
        fg="yellow"
    ))
    return last_code


# ── Private helper functions ───────────────────────────────────
# These just handle terminal formatting — not core agent logic.
# Prefixed with _ to signal they're internal to this module.

def _print_divider():
    click.echo(click.style("\n" + "─" * 44, fg="bright_black"))


def _print_code_block(code: str):
    click.echo(click.style("\n┌── Generated code ──────────────────────", fg="bright_black"))
    for line in code.splitlines():
        click.echo(click.style("│ ", fg="bright_black") + line)
    click.echo(click.style("└────────────────────────────────────────\n", fg="bright_black"))


def _print_output_block(output: str):
    click.echo(click.style("\n┌── Output ───────────────────────────────", fg="bright_black"))
    for line in output.strip().splitlines():
        click.echo(click.style("│ ", fg="bright_black") + line)
    click.echo(click.style("└─────────────────────────────────────────", fg="bright_black"))