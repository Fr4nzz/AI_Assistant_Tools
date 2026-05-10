---
name: notebooklm
description: Use this skill whenever the user asks to use Google NotebookLM from Codex, automate NotebookLM notebooks, add sources, query notebook content, generate or download NotebookLM audio/video/slide/quiz/flashcard/mind-map/data-table artifacts, manage NotebookLM profiles/auth, or troubleshoot the local `notebooklm` CLI.
metadata:
  requires:
    bins: ["notebooklm"]
---

# NotebookLM

Use the local `notebooklm` CLI from `notebooklm-py` for NotebookLM work.
Prefer CLI commands for repeatable agent tasks and ask before opening an
interactive login flow.

## Setup

Install from AI_Assistant_Tools:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) notebooklm
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool notebooklm
```

Restart Codex Desktop after installing the skill.

## First-Time Auth

Run login only when the user is ready to authenticate in a browser:

```bash
notebooklm login
```

Check auth without changing data:

```bash
notebooklm auth check --test
notebooklm profile list
```

For multiple Google accounts, use profiles:

```bash
notebooklm login --profile work
notebooklm profile switch work
```

## Common Commands

List and select notebooks:

```bash
notebooklm list
notebooklm use NOTEBOOK_ID
notebooklm metadata --json
```

Create a notebook and add sources:

```bash
notebooklm create "Notebook title"
notebooklm source add "https://example.com/article"
notebooklm source add "./paper.pdf"
notebooklm source add-research "research query"
```

Ask grounded questions:

```bash
notebooklm ask "What are the key themes?"
```

Generate artifacts:

```bash
notebooklm generate audio "make it engaging" --wait
notebooklm generate video --wait
notebooklm generate slide-deck
notebooklm generate quiz
notebooklm generate flashcards
notebooklm generate mind-map
notebooklm generate data-table "compare key concepts"
```

For long-running audio/video generation, prefer the artifact workflow so Codex
can show progress and recover cleanly if the generation command is interrupted:

```bash
notebooklm generate audio "long study summary" --format deep-dive --length long --language en --no-wait --json
notebooklm artifact list --notebook NOTEBOOK_ID --json
notebooklm artifact wait ARTIFACT_ID --notebook NOTEBOOK_ID
```

Download artifacts:

```bash
notebooklm download audio ./podcast.mp3
notebooklm download video ./overview.mp4
notebooklm download slide-deck ./slides.pdf
notebooklm download quiz --format markdown ./quiz.md
notebooklm download flashcards --format json ./cards.json
notebooklm download mind-map ./mindmap.json
notebooklm download data-table ./data.csv
```

When the user asks for a voice summary, finish by downloading the audio to a
clear path and verify the file exists:

```bash
notebooklm download audio ~/Downloads/summary.mp3 --notebook NOTEBOOK_ID --artifact ARTIFACT_ID
ls -lh ~/Downloads/summary.mp3
```

Show bundled agent guidance when needed:

```bash
notebooklm agent show codex
notebooklm skill status
```

## Update When Commands Stop Working

Do not check for updates before every NotebookLM task. If commands that used to
work start failing and normal causes such as expired auth, wrong profile,
missing sources, or network problems do not explain it, update the tool.

Preferred update commands:

```bash
uv tool upgrade notebooklm-py
```

Or rerun the AI_Assistant_Tools installer:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) notebooklm
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool notebooklm
```

After updating, rerun:

```bash
notebooklm --version
notebooklm auth check --test
```

## Notes

- Prefer `--json` when the command supports it.
- Do not delete notebooks, sources, or generated artifacts unless the user
  explicitly asks.
- For long artifact generation, use `--wait` only when the user wants the task
  completed in the current turn.
