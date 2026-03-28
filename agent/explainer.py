# agent/explainer.py
# ─────────────────────────────────────────────────────────────
# Explains generated code in plain English.
# Used by both single task mode (--explain flag)
# and chat mode (user types "explain it")
# ─────────────────────────────────────────────────────────────

import click
from agent.core import generate_code
from agent.prompts import explain_prompt


def explain_code(code: str) -> str:
    """
    Send code to LLM and get a plain English explanation back.
    Uses a higher temperature than code generation —
    explanation benefits from more natural, varied language.
    """

    # We call generate_code with a custom conversation
    # just for the explanation — separate from the main conversation
    # so it doesn't interfere with the coding context
    conversation = [
        {
            "role": "system",
            "content": (
                "You are a patient coding teacher who explains code "
                "clearly and simply. You use plain English, avoid jargon, "
                "and make complex ideas easy to understand."
            )
        },
        {
            "role": "user",
            "content": explain_prompt(code)
        }
    ]

    # Use slightly higher temperature for more natural explanation
    # We import client directly here to override temperature
    import os
    from groq import Groq
    from dotenv import load_dotenv
    load_dotenv()

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversation,
        temperature=0.5,   # higher than code gen — more natural language
        max_tokens=600
    )

    return response.choices[0].message.content.strip()


def print_explanation(explanation: str) -> None:
    """Print the explanation in a clean formatted block."""
    click.echo(click.style(
        "\n┌── Code explanation ─────────────────────",
        fg="bright_cyan"
    ))
    for line in explanation.splitlines():
        click.echo(click.style("│ ", fg="bright_cyan") + line)
    click.echo(click.style(
        "└─────────────────────────────────────────\n",
        fg="bright_cyan"
    ))