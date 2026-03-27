# CLI Coding Assistant

A command-line tool that turns plain English into working Python code — powered by Groq + LLaMA 3.

No flags, no syntax to learn. Just describe what you want and it writes, runs, and fixes the code for you.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | LLaMA 3.3 70B (via Groq) |
| Inference | [Groq API](https://console.groq.com) — ultra-fast inference |
| CLI | [Click](https://click.palletsprojects.com/) |
| Config | python-dotenv |
| Language | Python 3.9+ |

---

## How It Works

1. **Parse** — Your plain English request is parsed to extract the task and an optional save path (e.g. "save to documents as calc.py")
2. **Generate** — The agent sends your task to LLaMA 3.3 70B on Groq and gets back Python code
3. **Run** — The code is executed in a temporary sandbox
4. **Fix** — If it errors, the agent feeds the error back to the model and retries automatically (up to 3 times by default)
5. **Save** — If you specified a path, the final working code is saved there

```
Your words ──► Parse intent ──► Generate code ──► Run it
                                                     │
                                              ✅ Done │ ❌ Error
                                                      ▼
                                              Feed error back ──► Retry (up to 3x)
```

---

## Example Output

```
$ code "build a calculator and save to my desktop as calc.py"

🧠 Understanding your request...
   Task:    build a calculator
   Save to: ~/Desktop/calc.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 build a calculator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙ Attempt 1 — generating code...
▶ Running...
✅ Success on attempt 1
💾 Saved to ~/Desktop/calc.py
```

---

## Install

```bash
pip install git+https://github.com/Nirvisha-9/cli-coding-assistant.git
```

Then set your Groq API key (get one free at [console.groq.com](https://console.groq.com)):

```bash
export GROQ_API_KEY=your_key_here
```

To make it permanent, add that line to your `~/.zshrc` or `~/.bashrc`.

---

## Usage

```bash
code "print fibonacci numbers"
code "build a calculator and save it to my documents"
code "create a snake game on my desktop"
code "write a todo app and put it in ~/Projects as todo.py"
code "make a password generator and save to documents as passwords.py"
code "build a web scraper" --dry-run
```

## Options

| Flag | Description |
|---|---|
| `--retries` / `-r` | Max fix attempts (default: 3) |
| `--dry-run` | Show generated code without running it |