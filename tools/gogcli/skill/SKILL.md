---
name: gogcli
description: Use this skill whenever the user asks to search, read, summarize, triage, or gather context from Gmail through the local `gog` CLI.
metadata:
  requires:
    bins: ["gog"]
---

# gogcli Gmail

Use the local `gog` command for Gmail search and read-only context gathering. It is usually more agent-friendly than raw `gws` for Gmail because it provides compact search output, full thread reads, sanitized content, and JSON.

Do not use the Codex Gmail plugin unless the user explicitly asks for that connector; it may be authenticated to a different/shared account.

## Defaults

Use `--gmail-no-send` for search, summary, and triage tasks:

```powershell
gog --account user@gmail.com --gmail-no-send gmail search "newer_than:2d" --max 20 --json
gog --account user@gmail.com --gmail-no-send gmail thread get THREAD_ID --sanitize-content --json
gog --account user@gmail.com --gmail-no-send gmail get MESSAGE_ID --sanitize-content --json
```

Find configured accounts:

```powershell
gog auth list
gog auth status
```

For summaries, search first and then fetch only the relevant threads with `--sanitize-content --json`.

Use `gws` instead when the task is about Drive, Docs, Sheets, Slides, Forms, Calendar, uploads, or Google Workspace editing.
