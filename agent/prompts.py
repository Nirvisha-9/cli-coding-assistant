# agent/prompts.py
# ─────────────────────────────────────────────────────────────
# All prompts live here. When you want to improve agent behavior,
# this is the only file you need to touch.
# ─────────────────────────────────────────────────────────────


# Tells the LLM what kind of assistant it is.
# Low temperature (set in core.py) + this system prompt = consistent, clean code output.
SYSTEM_PROMPT = """You are an expert Python developer.
When given a task, write clean, working Python code.
Rules:
- Return ONLY the Python code
- No markdown fences (no ```)
- No explanations before or after the code
- No unnecessary comments
- Use only Python standard library unless the task clearly requires third-party packages
- Always print or return output so the result is visible when run
"""


# Used on the very first message — tells the LLM what to build
def user_task_prompt(task: str, save_path: str = None) -> str:
    if save_path:
        return (
            f"Write Python code to: {task}\n\n"
            f"IMPORTANT: Save any created files to this exact path: {save_path}\n"
            f"Use the full absolute path as given. Do not change it."
        )
    return f"Write Python code to: {task}"


# Used when the code failed — sends the error back so LLM can fix it.
# This is the core of the self-healing loop.
# We include the previous code AND the error so the LLM has full context.
def fix_prompt(error: str) -> str:
    return (
        f"That code failed with this error:\n\n"
        f"{error}\n\n"
        f"Fix the code. Return ONLY the corrected Python code. Nothing else."
    )


# Used for dry-run mode — same as system prompt but explicit about no execution
DRY_RUN_SYSTEM_PROMPT = """You are an expert Python developer.
Write clean, working Python code for the given task.
Return ONLY the Python code — no markdown, no explanation."""
