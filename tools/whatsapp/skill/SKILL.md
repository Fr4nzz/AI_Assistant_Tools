---
name: whatsapp
description: Use this skill whenever the user asks to search WhatsApp chats, inspect WhatsApp history, find WhatsApp context, list WhatsApp chats, find/download WhatsApp media, or work with WhatsApp data. On Linux prefer `wacli`; on Windows use the local `wha` CLI backed by Whasapo.
metadata:
  optional_bins: ["wacli", "wha"]
---

# WhatsApp

Use the local WhatsApp CLI. Prefer `wacli` when available, especially on Linux.
On Windows, this repo currently installs `wha`, a wrapper around Whasapo's
SQLite cache and live tools.

## Safety

- Never send unless the user explicitly provides the exact recipient and exact message/file.
- Treat local CLI output as cached/synced data. If a message has not synced yet, say that clearly.
- Do not dump private chats unnecessarily. Summarize only what is needed.
- Prefer JSON output for parsing.

## Linux / wacli

Check status:

```bash
wacli --json doctor
wacli --json auth status
```

First-time pairing:

```bash
wacli auth
```

This prints a QR code in the terminal and bootstraps sync after pairing. The
user scans it from WhatsApp phone app > Settings > Linked Devices > Link a
Device.

For normal context/search requests:

1. Start or refresh sync.

```bash
wacli sync --once
```

For a longer background sync:

```bash
nohup wacli sync --follow >/tmp/wacli-sync.log 2>&1 &
```

2. Inspect status if needed.

```bash
wacli --json doctor
```

3. Search/list local data.

```bash
wacli --json messages search "field report" --limit 20
wacli --json messages search "field report" --chat CHAT_JID --limit 50
wacli --json chats list --limit 50
wacli --json contacts search "Manuel"
wacli --json messages search ".pdf" --chat CHAT_JID --has-media --limit 20
```

4. If older messages are missing, check coverage and backfill only when useful.

```bash
wacli history coverage --include-blocked
wacli history fill --dry-run --limit 20
wacli history backfill --chat CHAT_JID --requests 10 --count 50
```

For sending, only after the user gives the exact recipient and exact content:

```bash
wacli send text --to RECIPIENT --message "Exact message text"
wacli send file --to RECIPIENT --file ./file.pdf --caption "Exact caption"
```

## Windows / wha + Whasapo

Use first-class `wha` commands, not Codex MCP tools. `wha download`,
`wha send-message`, and `wha send-file` are the only commands that use the live
Whasapo connection; all search/context commands read SQLite directly.

Read-only commands:

```powershell
wha doctor
wha sync
wha search intillacta -n 20
wha search "field report" -n 20
wha chats --query "Global Environ" -n 10
wha chat 120363422478862111@g.us -n 50 --asc
wha contacts Ricardina -n 20
wha media --chat 120363405350719367@g.us --query .m4a -n 20
wha alias set 593991978514@s.whatsapp.net Manuel
wha alias import-live
wha alias import-recent-groups -n 25
wha alias import-recent-directs -n 50
wha alias list --json
wha download --chat 120363405350719367@g.us --message-id MESSAGE_ID
```

Use `--json` for structured parsing:

```powershell
wha search intillacta -n 50 --json
wha media --chat 120363405350719367@g.us --query .m4a --json
```

Workflow:

1. Start sync without blocking the chat.

```powershell
wha sync
```

If the AI needs to explicitly launch it detached:

```powershell
Start-Process -WindowStyle Hidden -FilePath wha -ArgumentList 'sync'
```

2. Run `wha doctor` if you need cache counts or database modified time.
3. Run broad `wha search` terms.
4. Identify relevant chat JIDs.
5. If `wha chats --query "Name"` misses a known chat/group, search distinctive
   message text, participant names, filenames, or screenshot anchors with
   `wha search`, then map the discovered chat JID back to the requested name.
6. Use aliases when Whasapo lacks a contact/display name.
7. Use `wha chat CHAT_JID --asc` to inspect surrounding context.

For media:

1. Use `wha media` or `wha search` to find the media message ID, chat JID,
   media type, and visible filename/caption.
2. If the user asks to download media, run
   `wha download --chat CHAT_JID --message-id MESSAGE_ID`.
3. If a file already exists under `%LOCALAPPDATA%\whasapo\media`, copy it to
   `%USERPROFILE%\Downloads` with a readable filename before giving the user a
   link.

For sending:

```powershell
wha send-message --to CHAT_JID --message "Exact message text"
wha send-file --to CHAT_JID --path "C:\path\to\file.pdf"
```

## Notes

`wacli` and Whasapo both rely on WhatsApp Web-style linked-device behavior.
Sync completeness can vary. If search returns no results, the message may not
be cached yet, or older history may need a best-effort backfill.
