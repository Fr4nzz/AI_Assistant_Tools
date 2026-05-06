---
name: whatsapp
description: Use this skill whenever the user asks to search WhatsApp chats, inspect WhatsApp history, find WhatsApp context, list WhatsApp chats, find/download WhatsApp media, or work with WhatsApp data. Use the local `wha` CLI backed by Whasapo's SQLite cache.
metadata:
  requires:
    bins: ["wha"]
---

# WhatsApp

Use the local `wha` CLI for WhatsApp search, context gathering, message history, chat lookup, and media-message lookup. It reads Whasapo's SQLite cache at `%LOCALAPPDATA%\whasapo\session.db` and does not open a new WhatsApp Web connection.

Do not rely on a Codex `whatsapp-whasapo` MCP tool. This setup is CLI-first so new chats can use WhatsApp without MCP tool visibility or connection conflicts.

Use first-class `wha` commands, not Codex MCP tools. `wha download`, `wha send-message`, and `wha send-file` are the only commands that use the live Whasapo connection; all search/context commands read SQLite directly.

## Safety

- Never send unless the user explicitly provides the exact recipient and exact message/file.
- Treat `wha` output as local cache data. If the cache has not synced a message yet, say that clearly.
- Do not dump private chats unnecessarily. Summarize only what is needed.

## Read-Only CLI

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

## Workflow

For context/search requests:

1. Start sync without blocking the chat:

```powershell
wha sync
```

This starts `whasapo serve` in the background if needed, reports current cache counts, and returns immediately.

If the AI needs to explicitly launch it as a detached process and continue without even reading sync status, use this on Windows:

```powershell
Start-Process -WindowStyle Hidden -FilePath wha -ArgumentList 'sync'
```

Or this on Linux/macOS:

```bash
nohup wha sync >/dev/null 2>&1 &
```

Use `wha sync --wait 10` or longer only during first-time setup or when the user explicitly needs the newest messages and accepts waiting.

2. Run `wha doctor` if you need to inspect current cache counts or database modified time.
3. Run broad `wha search` terms.
4. Identify relevant chat JIDs.
5. If `wha chats --query "Name"` misses a known chat/group, do not stop. Search distinctive message text, participant names, filenames, or screenshots anchors with `wha search`, then map the discovered chat JID back to the requested name.
6. If Whasapo lacks a contact/display name, run `wha alias import-recent-groups -n 25` for recent groups, `wha alias import-recent-directs -n 50` for recent direct chats, `wha alias import-live` for broad live chat names, or add a local alias with `wha alias set CHAT_JID "Name"` so future searches can find it by name.
7. Use `wha chat CHAT_JID --asc` to inspect surrounding context.
8. Summarize concise findings with dates, chat names/JIDs when useful, and any media/document names.

For media:

1. Use `wha media` or `wha search` to find the media message ID, chat JID, media type, and visible filename/caption.
2. If the user asks to download media, run `wha download --chat CHAT_JID --message-id MESSAGE_ID`.
3. If a file already exists under `%LOCALAPPDATA%\whasapo\media`, copy it to `%USERPROFILE%\Downloads` with a readable filename before giving the user a link.

For sending:

1. Confirm exact recipient JID/phone and exact message/file.
2. Use `wha send-message --to CHAT_JID --message "text"` or `wha send-file --to CHAT_JID --path "file"`. Never send from cached search commands.

## Notes

Whasapo's SQLite cache improves as Whasapo runs and syncs messages. If a search returns no results, the message may not be cached yet.

The cache can be stale if Whasapo has not been running recently. Run `wha sync` at the start of WhatsApp tasks so Whasapo can refresh the cache while searches run. If results look stale or the user needs messages from the last few minutes, run `wha doctor`, sleep briefly, rerun `wha sync`, or consider a foreground `wha sync --wait 10`.

Whasapo does not expose an exact "messages left to sync" total through this cache. Use `messages`, `whatsmeow_contacts`, `size_bytes`, and `modified_age_seconds` from `wha sync` or `wha doctor` as practical progress indicators.

SQLite-backed commands are fast and parallel-safe. Live commands (`wha download`, `wha send-message`, `wha send-file`, and alias imports that explicitly need live data) use a local lock so parallel calls from different assistants queue instead of opening multiple WhatsApp Web streams at once.

Direct one-to-one WhatsApp display names are less reliable than group names in Whasapo. `import-recent-directs` uses the local contacts table by default and stays fast; use `--live` only when explicitly troubleshooting because live direct lookups usually return only phone/JID. If it reports `no-name`, use manual aliases for important contacts.

`wha live` exists only as a debugging escape hatch for raw Whasapo MCP tools. Do not use it for normal research.
