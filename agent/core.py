# agent/core.py
# ─────────────────────────────────────────────────────────────
# Pure building blocks — generate code, clean it up, run it.
# No agent logic here. Just three focused functions.
# Each one does exactly one thing and can be tested independently.
# ─────────────────────────────────────────────────────────────

import os
import subprocess
import tempfile
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Client setup ──────────────────────────────────────────────
# Groq client is created once and reused.
# The API key is read from your .env file — never hardcoded.
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


# ── Function 1: generate_code ─────────────────────────────────
# Sends the full conversation history to Groq and gets code back.
#
# WHY conversation history matters:
# On attempt 1 → conversation has [system, user_task]
# On attempt 2 → conversation has [system, user_task, assistant_code, user_error]
# On attempt 3 → conversation has [system, user_task, assistant_code, user_error, assistant_fix, user_error2]
#
# The LLM sees everything it tried before + every error it caused.
# That's why the fixes get smarter each round — it has memory of what failed.
#
# temperature=0.2 means "be consistent, not creative"
# For code generation you want low randomness — same input should give similar output.
# Creative writing uses 0.7-0.9. Code uses 0.1-0.3.

def generate_code(conversation: list[dict]) -> str:
    """
    Send conversation history to Groq, get raw LLM response back.
    Returns the raw string — may contain markdown fences.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=conversation,
        temperature=0.2,
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()


# ── Function 2: extract_code ──────────────────────────────────
# LLMs sometimes ignore instructions and wrap code in markdown fences like:
# ```python
# print("hello")
# ```
# This function strips that wrapper so we get clean executable Python.
# The conversation history approach in generate_code means the LLM usually
# doesn't wrap code after attempt 1, but this is a safety net.

def extract_code(raw: str) -> str:
    """
    Strip markdown fences if the LLM added them.
    Returns clean Python code ready to execute.
    """
    if "```python" in raw:
        raw = raw.split("```python")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
    return raw.strip()


# ── Function 3: execute_code ──────────────────────────────────
# Runs the code safely and returns (stdout, stderr, exit_code).
#
# WHY we use a temp file:
# We can't exec() the code directly — that would run in our process
# and could crash our agent or access our variables.
# Writing to a temp file and using subprocess runs it in a completely
# separate process — isolated and safe.
#
# WHY timeout=30:
# If the generated code has an infinite loop (e.g. while True: pass)
# it would hang your terminal forever. The timeout kills it after 30 seconds.
#
# Return values:
# stdout → what the code printed (the actual output)
# stderr → the error message if it crashed
# returncode → 0 means success, anything else means failure
#
# The finally block always deletes the temp file — even if an error occurs.
# This prevents your /tmp folder filling up with leftover .py files.

def execute_code(code: str) -> tuple[str, str, int]:
    """
    Write code to a temp file and run it in a subprocess.
    Returns (stdout, stderr, returncode).
    returncode 0 = success, non-zero = failure.
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode

    except subprocess.TimeoutExpired:
        return "", "Error: code timed out after 30 seconds — possible infinite loop", 1

    finally:
        # Always clean up — runs whether code succeeded or failed
        os.unlink(tmp_path)