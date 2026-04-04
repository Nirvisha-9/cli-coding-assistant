# CLI Coding Assistant 🤖

An AI agent that writes, runs, and fixes code from plain English.
Describe what you want — it generates code, executes it, self-heals from errors, and saves files wherever you tell it to.

---

## What it does

- Understands natural language — no flags or syntax to remember
- Generates code in **8 languages** — Python, JavaScript, TypeScript, Java, C, Rust, Go, Bash
- **Self-healing** — runs the code, reads errors, fixes itself automatically
- **Chat mode** — remembers everything across tasks in a session
- **Explains code** — breaks down what the generated code does in plain English
- Saves files anywhere on your system from natural language like *"save to my desktop"*

---

## Install

```bash
pip install git+https://github.com/Nirvisha-9/cli-coding-assistant.git
```

---

## Setup

**1. Get a free Groq API key**
- Go to [console.groq.com](https://console.groq.com)
- Sign up — completely free, no credit card needed
- Click **API Keys** → **Create new key** → copy it

**2. Create a `.env` file in your home folder**

```bash
echo "GROQ_API_KEY=your_key_here" > ~/.env
```

That's it. You're ready to go.

---

## Usage

### Basic — just describe what you want

```bash
codeai "print the first 10 fibonacci numbers"
codeai "sort a list of dictionaries by age key"
codeai "find all duplicate files in a folder"
```

### Save files anywhere — just say where

```bash
codeai "build a calculator and save it to my documents"
codeai "create a snake game on my desktop"
codeai "write a todo app and put it in ~/Projects as todo.py"
codeai "make a password generator and save to documents as passwords.py"
```

### Choose a language

```bash
codeai "build a calculator" --lang javascript
codeai "parse a csv file" --lang typescript
codeai "implement binary search" --lang java
codeai "write bubble sort" --lang c
codeai "make an http request" --lang rust
codeai "write a fibonacci function" --lang go
```

### Or just write it naturally — no flag needed

```bash
codeai "write a calculator in javascript"
codeai "implement merge sort in java"
codeai "build a linked list as a c program"
```

### Explain a concept

```bash
codeai "explain binary search to me"
codeai "what is a hash map"
codeai "how does recursion work"
codeai "what is the difference between a stack and a queue"
```

### Explain generated code

```bash
codeai "implement dijkstra's algorithm" --explain
codeai "build a binary search tree" --lang java --explain
```

### Preview without running

```bash
codeai "build a web scraper" --dry-run
codeai "implement quicksort" --lang rust --dry-run
```

### More retries for complex tasks

```bash
codeai "implement a compiler" --retries 5
```

---

## Chat mode — remembers everything across tasks

```bash
codeai --chat
```

```
You: write a function to parse CSV files
✅ Done.

You: now add error handling to it
✅ Done.

You: write 3 unit tests for it
✅ Done.

You: explain it
✅ Explained.

You: save ~/Documents/csv_parser.py
✅ Saved.

You: reset
🔄 Fresh start.

You: exit
👋 Bye!
```

**Chat commands:**

| Command | What it does |
|---|---|
| `exit` / `quit` / `bye` | End the session |
| `reset` / `clear` | Fresh conversation, keep session open |
| `show` | Print the last generated code |
| `explain` | Explain the last generated code |
| `save ~/path/file.py` | Save last code to any path |
| `help` | Show all commands |

---

## Supported languages

| Language | Flag | Requires |
|---|---|---|
| Python | `--lang python` | Pre-installed on Mac/Linux |
| JavaScript | `--lang javascript` | Node.js |
| TypeScript | `--lang typescript` | Node.js + ts-node |
| Java | `--lang java` | JDK |
| C | `--lang c` | gcc (pre-installed on Mac) |
| Rust | `--lang rust` | rustc |
| Go | `--lang go` | Go |
| Bash | `--lang bash` | Pre-installed on Mac/Linux |

**Install missing runtimes on Mac:**
```bash
brew install node        # JavaScript / TypeScript
brew install openjdk     # Java
brew install rust        # Rust
brew install go          # Go
npm install -g ts-node typescript   # TypeScript runner
```

---

## How it works

```
You describe a task
        ↓
Agent generates code
        ↓
Runs it automatically
        ↓
If it fails → reads the error → fixes itself → retries
        ↓
Success → prints output → saves file if you asked
```

The self-healing loop retries up to 3 times by default.
Each retry the LLM sees its previous attempt + the error,
so fixes get smarter each round.

---

## Tech stack

`Python` `Groq API` `Llama 3.3 70B` `Click` `Subprocess` `Prompt Engineering`

---

## Requirements

- Python 3.9+
- Free Groq API key from [console.groq.com](https://console.groq.com)
- Language runtimes for whichever languages you want to use

---

## License

MIT