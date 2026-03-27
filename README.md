# CLI Coding Assistant

A command-line tool that turns plain English into working Python code — powered by Groq + LLaMA 3.

## Install

```bash
pip install git+https://github.com/Nirvisha-9/cli-coding-assistant.git
```

Then set your Groq API key (get one free at [console.groq.com](https://console.groq.com)):

```bash
export GROQ_API_KEY=your_key_here
```

To make it permanent, add that line to your `~/.zshrc` or `~/.bashrc`.

## Usage

```bash
code "print fibonacci numbers"
code "build a calculator and save it to my documents"
code "create a snake game on my desktop"
code "write a todo app and put it in ~/Projects as todo.py"
code "make a password generator and save to documents as passwords.py"
code "build a web scraper" --dry-run
```

