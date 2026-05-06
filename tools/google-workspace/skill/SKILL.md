---
name: google-workspace
description: Use this skill whenever the user asks to search, read, summarize, triage, draft, or manage Gmail through the local `gog` CLI; or list, search, inspect, download, upload, create, or edit Google Drive, Calendar, Docs, Sheets, Slides, and Forms through the local `gws` Google Workspace CLI.
metadata:
  requires:
    bins: ["gws", "gog"]
---

# Google Workspace CLI

Use local CLIs for Google Workspace work. This is the account-routing skill: it exists to prefer the user's personal Google OAuth accounts over the Codex Google Drive/Gmail plugin account.

- Prefer `gog` for Gmail search, message reads, thread reads, and summaries.
- Prefer `gws` for Drive, Docs, Sheets, Slides, Forms, Calendar, uploads, and editing.

For general `gws` syntax, flags, schema discovery, and safety rules, read the installed upstream skills first:

- `../gws-shared/SKILL.md`
- `../gws-gmail/SKILL.md`
- `../gws-drive/SKILL.md`
- `../gws-docs/SKILL.md`

Do not use the Codex Google Drive or Gmail plugins unless the user explicitly asks for those connectors; they may be authenticated to a different/shared account.

## Gmail With gog

Use `--gmail-no-send` by default for read/search tasks:

```powershell
gog --account user@gmail.com --gmail-no-send gmail search "newer_than:2d" --max 20 --json
gog --account user@gmail.com --gmail-no-send gmail thread get THREAD_ID --sanitize-content --json
gog --account user@gmail.com --gmail-no-send gmail get MESSAGE_ID --sanitize-content --json
```

Use `gog auth list` or `gog auth status` to find configured accounts. For normal summaries, search first, then fetch only the relevant threads with `--sanitize-content --json`.

## Windows Reliability Notes

`gog.exe` should be placed directly in `%USERPROFILE%\.local\bin` and called as `gog`.

`gws` is normally on PATH through npm. On Windows, interactive shells may resolve `gws` to `gws.ps1`, while subprocesses and Python scripts often need the command shim explicitly as `gws.cmd`. If a script says it cannot find `gws`, call `gws.cmd`.

Use UTF-8 before commands that may print names, subjects, or message bodies with accents, emoji, or hidden Unicode characters:

```powershell
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

PowerShell is fine for `gws` as long as JSON quoting is handled deliberately. For simple commands, use `gws.cmd` directly. If inline JSON fails, call through `cmd /c`, for example:

```powershell
cmd /c "gws gmail users messages list --params ""{\""userId\"":\""me\"",\""maxResults\"":5}"""
```

If Git Bash is installed, it is also acceptable for direct `gws` commands because single-quoted JSON is cleaner there. Do not require Bash; it is only a convenience.

For repeated or complex `gws` calls, prefer writing request JSON to a local file and using a short helper script or `cmd /c` instead of fighting nested quoting. In Python, use `subprocess.run(["gws.cmd", ...])` and configure UTF-8 output with `sys.stdout.reconfigure(encoding="utf-8")` when printing API text.

## Local Checks

```powershell
gws.cmd --version
gws.cmd auth status
```

## Optional Upstream Skills

This custom skill is the account-routing skill and should stay installed. The essential upstream `gws` skills to keep installed are `gws-shared`, `gws-gmail`, `gws-drive`, and `gws-docs`.

Some upstream skills mention helper skills such as `gws-gmail-read`, `gws-gmail-triage`, or `gws-drive-upload`. Those are not installed by default to avoid clutter. Use the base API commands directly, or install only the helper needed for the task:

```powershell
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-gmail-read
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-drive-upload
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-sheets
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-forms
```

Do not install the whole repo unless the user explicitly wants many Google Workspace skills.
