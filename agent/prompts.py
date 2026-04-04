# agent/prompts.py
# ─────────────────────────────────────────────────────────────
# All prompts in one place.
# Now supports multiple languages.
# ─────────────────────────────────────────────────────────────


# ── Language configs ──────────────────────────────────────────
LANGUAGES = {
    "python": {
        "extension": ".py",
        "runner":    ["python3"],
        "notes": (
            "- Use only standard library unless task clearly needs third-party packages\n"
            "- Always print output so results are visible\n"
            "- NEVER use input() or interactive prompts\n"
            "- Hardcode sample values to demonstrate the code working"
        )
    },
    "javascript": {
        "extension": ".js",
        "runner":    ["node"],
        "notes": (
            "- Use vanilla JavaScript, no frameworks unless asked\n"
            "- Use console.log() to show output\n"
            "- NEVER use readline or interactive prompts\n"
            "- Hardcode sample values to demonstrate the code working\n"
            "- Use const and let, never var"
        )
    },
    "typescript": {
        "extension": ".ts",
        "runner":    ["npx", "ts-node"],
        "notes": (
            "- Use proper TypeScript types everywhere\n"
            "- Use console.log() to show output\n"
            "- NEVER use readline or interactive prompts\n"
            "- Hardcode sample values to demonstrate the code working\n"
            "- Use interfaces and type aliases where appropriate"
        )
    },
    "rust": {
        "extension": ".rs",
        "runner":    None,
        "notes": (
            "- Write a complete self-contained program with fn main()\n"
            "- Use println! macro for output\n"
            "- Handle errors with unwrap() for simplicity unless asked otherwise\n"
            "- Hardcode sample values to demonstrate the code working"
        )
    },
    "go": {
        "extension": ".go",
        "runner":    ["go", "run"],
        "notes": (
            "- Write a complete program with package main and func main()\n"
            "- Use fmt.Println for output\n"
            "- Hardcode sample values to demonstrate the code working"
        )
    },
    "bash": {
        "extension": ".sh",
        "runner":    ["bash"],
        "notes": (
            "- Write clean bash script\n"
            "- Use echo for output\n"
            "- Add #!/bin/bash at the top\n"
            "- Hardcode sample values to demonstrate the script working"
        )
    },
    "java": {
        "extension": ".java",
        "runner":    None,  # needs compile step — handled separately
        "notes": (
            "- Write a complete Java program with a public class named Main\n"
            "- The class must be named exactly 'Main'\n"
            "- Include public static void main(String[] args)\n"
            "- Use System.out.println() for output\n"
            "- NEVER use Scanner or interactive input\n"
            "- Hardcode sample values to demonstrate the code working"
        )
    },
    "c": {
        "extension": ".c",
        "runner":    None,  # needs compile step — handled separately
        "notes": (
            "- Write a complete C program with a main() function\n"
            "- Include necessary headers like stdio.h\n"
            "- Use printf() for output\n"
            "- NEVER use scanf() or interactive input\n"
            "- Hardcode sample values to demonstrate the code working"
        )
    },
}

DEFAULT_LANGUAGE = "python"


def get_language_config(lang: str) -> dict:
    lang = lang.lower().strip()
    if lang not in LANGUAGES:
        return LANGUAGES[DEFAULT_LANGUAGE]
    return LANGUAGES[lang]


def get_supported_languages() -> list:
    return list(LANGUAGES.keys())


def build_system_prompt(lang: str = "python") -> str:
    config = get_language_config(lang)
    lang_display = lang.capitalize()
    return f"""You are an expert {lang_display} developer.
When given a task, write clean, working {lang_display} code.
Rules:
- Return ONLY the {lang_display} code
- No markdown fences (no ```)
- No explanations before or after the code
- No unnecessary comments
- If a file path is provided, save the file to EXACTLY that path
{config['notes']}
"""

# Keep SYSTEM_PROMPT as default Python for backward compatibility
SYSTEM_PROMPT = build_system_prompt("python")


def user_task_prompt(task: str, save_path: str = None, lang: str = "python") -> str:
    lang_display = lang.capitalize()
    base = f"Write {lang_display} code to: {task}"
    if save_path:
        base += (
            f"\n\nIMPORTANT: Save the file to this exact path: {save_path}\n"
            f"Use the full absolute path as given. Do not change it."
        )
    return base


def fix_prompt(error: str) -> str:
    return (
        f"That code failed with this error:\n\n"
        f"{error}\n\n"
        f"Fix the code. Return ONLY the corrected code. Nothing else."
    )


def explain_prompt(code: str) -> str:
    return f"""Explain this code in plain English for someone learning to code.

{code}

Structure your explanation like this:
1. One sentence summary of what it does
2. How it works step by step (numbered list, simple language)
3. Key concepts used (e.g. recursion, loops, classes)
4. Time and space complexity if relevant

Be concise and clear. No jargon. Max 15 lines."""


# ── Language detection from natural language ──────────────────
LANG_TRIGGERS = {
    "python":     ["python", " py "],
    "javascript": ["javascript", " js ", "node", "nodejs"],
    "typescript": ["typescript", " ts "],
    "rust":       ["rust", " rs "],
    "go":         ["golang", " go code", "in go"],
    "bash":       ["bash", "shell script", " sh "],
    "java":       ["java", " java "],
    "c":          [" in c", "in c ", "c program", "c code"],
}


def detect_language(text: str) -> str:
    """
    Detect programming language from natural language.
    'write a calculator in javascript' → 'javascript'
    'build a calculator' → 'python' (default)
    """
    text_lower = text.lower()
    for lang, triggers in LANG_TRIGGERS.items():
        for trigger in triggers:
            if trigger in text_lower:
                return lang
    return DEFAULT_LANGUAGE