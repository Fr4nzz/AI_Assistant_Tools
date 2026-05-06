---
name: gogcli
description: Use this skill whenever the user asks to search, read, summarize, triage, or manage Gmail, Calendar, Drive, Docs, Sheets, Slides, Forms, Apps Script, Contacts, Tasks, People, or Classroom through the local `gog` CLI.
metadata:
  requires:
    bins: ["gog"]
---

# gogcli

Use the local `gog` command for Google Workspace work. It is built for agents: stable `--json` and `--plain` output, human hints on stderr, multiple accounts, OAuth clients, command allowlists/denylists, sanitized Gmail reads, and broad service coverage.

Do not use the Codex Gmail or Google Drive plugins unless the user explicitly asks for those connectors; they may be authenticated to a different/shared account.

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

The recommended default auth services are:

```powershell
gog auth add user@gmail.com --services gmail,calendar,drive,docs,sheets,slides,forms,tasks
```

Add optional services such as `contacts`, `people`, `classroom`, or `appscript` only when a task needs them.

For non-Gmail work, select the account explicitly and use JSON where possible:

```powershell
gog --account user@gmail.com calendar events --today --json
gog --account user@gmail.com drive search "budget" --max 10 --json
gog --account user@gmail.com drive inventory --max 20 --json
gog --account user@gmail.com docs write DOCUMENT_ID --append --markdown --text "## Status"
gog --account user@gmail.com sheets get SPREADSHEET_ID "Sheet1!A1:D20" --json
gog --account user@gmail.com slides create-from-markdown "Weekly update" --content-file slides.md
gog --account user@gmail.com forms responses list FORM_ID --json
```

Use command discovery instead of guessing flags:

```powershell
gog <service> --help
gog <service> <command> --help
gog schema --json
```

Prefer `--dry-run` first where a write command supports it. Do not add `--force` unless the user requested that exact mutation.
