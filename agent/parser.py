# agent/parser.py
# ─────────────────────────────────────────────────────────────
# Parses natural language input to extract:
# - The actual coding task
# - Where to save the file (if mentioned)
# - What to name the file (if mentioned)
#
# Examples it handles:
# "build a calculator and save it to my documents"
#   → task: "build a calculator"
#   → path: ~/Documents/calculator.py
#
# "create a snake game on my desktop as snake.py"
#   → task: "create a snake game"
#   → path: ~/Desktop/snake.py
#
# "write a todo app and put it in ~/Projects/myapp"
#   → task: "write a todo app"
#   → path: ~/Projects/myapp/todo_app.py
# ─────────────────────────────────────────────────────────────

import os
import re
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Common location shortcuts ──────────────────────────────────
# Maps natural language locations to real paths.
# Works on any machine because Path.home() is always the user's home.

LOCATION_MAP = {
    # Documents
    "documents":        Path.home() / "Documents",
    "document":         Path.home() / "Documents",
    "docs":             Path.home() / "Documents",
    "my documents":     Path.home() / "Documents",

    # Desktop
    "desktop":          Path.home() / "Desktop",
    "my desktop":       Path.home() / "Desktop",

    # Downloads
    "downloads":        Path.home() / "Downloads",
    "my downloads":     Path.home() / "Downloads",

    # Home
    "home":             Path.home(),
    "home folder":      Path.home(),
    "home directory":   Path.home(),

    # Current folder
    "here":             Path.cwd(),
    "current folder":   Path.cwd(),
    "current directory": Path.cwd(),
    "this folder":      Path.cwd(),
}


def parse_intent(user_input: str) -> dict:
    """
    Use the LLM to extract task and save path from natural language.

    Returns:
    {
        "task": "build a calculator",
        "filename": "calculator.py",    # or null
        "location": "~/Documents",      # or null
        "full_path": "/Users/.../Documents/calculator.py"  # or null
    }
    """

    prompt = f"""Extract information from this user request about a coding task.

User said: "{user_input}"

Extract:
1. task — what coding task they want done (remove any file/location mentions)
2. filename — if they named a specific file (e.g. "calc.py", "snake.py"), else null
3. location — if they mentioned where to save it (e.g. "documents", "desktop", "~/Projects"), else null

Return ONLY a JSON object like this:
{{
  "task": "build a calculator",
  "filename": "calc.py",
  "location": "documents"
}}

Rules:
- task should be clean — no save/location language in it
- filename should include .py extension if not specified
- location should be the raw location they mentioned, lowercase
- if no location mentioned, set location to null
- if no filename mentioned, set filename to null
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=200
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]

    try:
        parsed = json.loads(raw.strip())
    except json.JSONDecodeError:
        # Fallback — treat entire input as the task, no path
        return {
            "task": user_input,
            "filename": None,
            "location": None,
            "full_path": None
        }

    # ── Resolve location to real path ──────────────────────────
    full_path = None
    location  = parsed.get("location")
    filename  = parsed.get("filename")
    task      = parsed.get("task", user_input)

    if location:
        resolved = _resolve_location(location, task, filename)
        full_path = str(resolved) if resolved else None

    return {
        "task":      task,
        "filename":  filename,
        "location":  location,
        "full_path": full_path
    }


def _resolve_location(location: str, task: str, filename: str = None):
    """
    Turn a location string into a real absolute Path.
    Handles shortcuts (desktop, documents), ~ paths, and relative paths.
    """
    if not location:
        return None

    location_lower = location.lower().strip()

    # Check shortcut map first
    for key, path in LOCATION_MAP.items():
        if key in location_lower:
            base = path
            fname = filename or _generate_filename(task)
            return base / fname

    # Handle explicit ~ paths like ~/Projects/myapp
    if "~" in location or "/" in location:
        expanded = Path(os.path.expanduser(location))
        fname = filename or _generate_filename(task)
        # If they gave a full file path already (ends in .py)
        if str(expanded).endswith(".py"):
            return expanded
        return expanded / fname

    # Default — treat as subfolder of Documents
    base  = Path.home() / "Documents" / location
    fname = filename or _generate_filename(task)
    return base / fname


def _generate_filename(task: str) -> str:
    """
    Auto-generate a sensible filename from the task description.
    "build a calculator" → "calculator.py"
    "create a snake game" → "snake_game.py"
    """
    # Remove common filler words
    stopwords = {
        "a", "an", "the", "build", "create", "make", "write",
        "implement", "code", "program", "script", "develop", "generate"
    }
    words = task.lower().split()
    meaningful = [w for w in words if w not in stopwords][:3]

    if not meaningful:
        return "output.py"

    return "_".join(meaningful) + ".py"

# Keywords that signal the user wants an explanation
# not code generation
EXPLAIN_TRIGGERS = [
    "explain", "what is", "what are", "how does",
    "how do", "tell me about", "describe", "walk me through",
    "what's the difference", "help me understand", "break down"
]

def is_explanation_request(user_input: str) -> bool:
    """
    Returns True if the user wants an explanation
    rather than code to be generated and run.
    """
    lowered = user_input.lower().strip()
    return any(lowered.startswith(trigger) for trigger in EXPLAIN_TRIGGERS)