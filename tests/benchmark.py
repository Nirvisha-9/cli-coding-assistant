# tests/benchmark.py
# ─────────────────────────────────────────────────────────────
# Eval suite — measures how well your agent performs.
# Run this to get a pass rate score you can put in your portfolio.
#
# This is what separates a strong portfolio project from a weak one.
# "My agent achieves 85% pass rate on first attempt" is a real,
# concrete claim that impresses interviewers.
#
# How it works:
# - 15 tasks of increasing difficulty
# - Each task is run through run_agent()
# - We check if the generated code ran without errors
# - We track: first-attempt passes, retry passes, total failures
# ─────────────────────────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
from agent.loop import run_agent
from agent.core import execute_code

# ── Benchmark tasks ────────────────────────────────────────────
# Mix of easy, medium, and hard tasks.
# Covers different Python skills: math, strings, data structures,
# file I/O concepts, algorithms.

TASKS = [
    # Easy — pure logic, no imports needed
    {"id": 1, "difficulty": "easy",   "task": "print the first 20 fibonacci numbers"},
    {"id": 2, "difficulty": "easy",   "task": "print a 5x5 multiplication table"},
    {"id": 3, "difficulty": "easy",   "task": "reverse a string and print it"},
    {"id": 4, "difficulty": "easy",   "task": "count vowels in the string 'hello world'"},
    {"id": 5, "difficulty": "easy",   "task": "print all prime numbers between 1 and 50"},

    # Medium — needs data structures or standard library
    {"id": 6,  "difficulty": "medium", "task": "sort a list of dicts by the 'age' key"},
    {"id": 7,  "difficulty": "medium", "task": "find the most common word in a sample paragraph"},
    {"id": 8,  "difficulty": "medium", "task": "flatten a nested list like [[1,2],[3,[4,5]]] into [1,2,3,4,5]"},
    {"id": 9,  "difficulty": "medium", "task": "generate a random password with 12 chars including letters numbers and symbols"},
    {"id": 10, "difficulty": "medium", "task": "implement binary search on a sorted list and print the result"},

    # Hard — algorithms, classes, or complex logic
    {"id": 11, "difficulty": "hard", "task": "implement a simple stack class with push pop and peek methods then demo it"},
    {"id": 12, "difficulty": "hard", "task": "write a Caesar cipher encoder and decoder then encode and decode a sample message"},
    {"id": 13, "difficulty": "hard", "task": "find all anagram pairs in this list: ['eat','tea','tan','ate','nat','bat']"},
    {"id": 14, "difficulty": "hard", "task": "implement merge sort and sort a sample list of 10 random numbers"},
    {"id": 15, "difficulty": "hard", "task": "build a simple calculator that handles add subtract multiply divide using a function dispatch table"},
]


def run_benchmark(max_retries: int = 3):
    """Run all benchmark tasks and print a score report."""

    click.echo(click.style("\n📊 Running benchmark suite...", fg="bright_cyan", bold=True))
    click.echo(click.style(f"   {len(TASKS)} tasks × up to {max_retries} retries each\n", fg="bright_black"))

    results = []

    for item in TASKS:
        task_id    = item["id"]
        difficulty = item["difficulty"]
        task       = item["task"]

        click.echo(click.style(f"[{task_id:02d}/{len(TASKS)}] ", fg="bright_black") +
                   click.style(f"{difficulty.upper():6s} ", fg=_diff_color(difficulty)) +
                   task[:60])

        passed_on_attempt = None

        # Run the agent with tracking
        conversation = _build_conversation(task)
        from agent.core import generate_code, extract_code
        from agent.prompts import SYSTEM_PROMPT, user_task_prompt, fix_prompt

        conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_task_prompt(task)}
        ]

        for attempt in range(1, max_retries + 1):
            raw  = generate_code(conversation)
            code = extract_code(raw)
            stdout, stderr, returncode = execute_code(code)

            if returncode == 0:
                passed_on_attempt = attempt
                click.echo(click.style(f"       ✅ Passed on attempt {attempt}", fg="green"))
                break
            else:
                if attempt < max_retries:
                    error_msg = stderr if stderr else stdout
                    conversation.append({"role": "assistant", "content": raw})
                    conversation.append({"role": "user", "content": fix_prompt(error_msg)})

        if passed_on_attempt is None:
            click.echo(click.style(f"       ✗ Failed all {max_retries} attempts", fg="red"))

        results.append({
            "id":         task_id,
            "difficulty": difficulty,
            "task":       task,
            "passed":     passed_on_attempt is not None,
            "attempt":    passed_on_attempt
        })

    _print_report(results, max_retries)


def _build_conversation(task: str) -> list[dict]:
    from agent.prompts import SYSTEM_PROMPT, user_task_prompt
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_task_prompt(task)}
    ]


def _diff_color(difficulty: str) -> str:
    return {"easy": "green", "medium": "yellow", "hard": "red"}.get(difficulty, "white")


def _print_report(results: list[dict], max_retries: int):
    total   = len(results)
    passed  = sum(1 for r in results if r["passed"])
    first   = sum(1 for r in results if r["attempt"] == 1)
    retried = sum(1 for r in results if r["passed"] and r["attempt"] and r["attempt"] > 1)
    failed  = total - passed

    # By difficulty
    for diff in ["easy", "medium", "hard"]:
        subset       = [r for r in results if r["difficulty"] == diff]
        diff_passed  = sum(1 for r in subset if r["passed"])
        click_color  = _diff_color(diff)

    click.echo(click.style("\n" + "═" * 44, fg="bright_black"))
    click.echo(click.style("  BENCHMARK RESULTS", fg="bright_cyan", bold=True))
    click.echo(click.style("═" * 44, fg="bright_black"))

    click.echo(f"\n  Total tasks:       {total}")
    click.echo(click.style(f"  Passed:            {passed}/{total} ({100*passed//total}%)", fg="green"))
    click.echo(click.style(f"  First attempt:     {first}/{total} ({100*first//total}%)", fg="green"))
    click.echo(click.style(f"  Needed retries:    {retried}", fg="yellow"))
    click.echo(click.style(f"  Failed all:        {failed}", fg="red"))

    click.echo(click.style("\n  By difficulty:", fg="bright_black"))
    for diff in ["easy", "medium", "hard"]:
        subset      = [r for r in results if r["difficulty"] == diff]
        diff_passed = sum(1 for r in subset if r["passed"])
        color       = _diff_color(diff)
        click.echo(
            click.style(f"    {diff.capitalize():8s}", fg=color) +
            f" {diff_passed}/{len(subset)}"
        )

    click.echo(click.style("\n" + "═" * 44 + "\n", fg="bright_black"))

    # Your portfolio line
    click.echo(click.style(
        f"  Portfolio stat: agent passes {100*passed//total}% of tasks "
        f"({100*first//total}% on first attempt)",
        fg="bright_cyan"
    ))
    click.echo("")


if __name__ == "__main__":
    run_benchmark()