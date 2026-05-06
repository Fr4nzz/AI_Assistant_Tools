# WhatsApp via Whasapo + wha CLI

WhatsApp access for Codex Desktop through Whasapo pairing plus a local `wha` CLI.

Codex should use the CLI for normal work, not a Codex MCP registration or raw MCP tools. The CLI reads Whasapo's SQLite cache for fast search and only uses a live Whasapo connection for downloads and sending.

## Why This Replaced The MCP-First Setup

The earlier WhatsApp approach did not sync historical messages reliably and MCP tool visibility in new Codex chats was inconsistent. Whasapo's local SQLite database plus `wha` gives faster cached search, group/direct chat lookup, media discovery, and fewer stream conflicts.

## Install

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool whatsapp
```

The installer downloads:

- `tools/whatsapp/bin/wha.py`
- `tools/whatsapp/bin/wha.cmd`
- `tools/whatsapp/skill/`

It also runs the upstream Whasapo installer unless `-SkipDependencies` is passed.

## Pair

```powershell
whasapo pair
```

Scan the QR code from:

```text
WhatsApp phone app > Settings > Linked Devices > Link a Device
```

Let Whasapo run for several minutes after pairing so `%LOCALAPPDATA%\whasapo\session.db` can populate.

## Test

```powershell
wha doctor
wha search intillacta -n 20
wha chats --query "Global Environ" -n 20
wha media --query .pdf -n 20
```

Use `--json` when Codex needs structured parsing.

## Sending

Never send unless the user gives the exact recipient and exact message/file.

```powershell
wha send-message --to CHAT_JID --message "Exact message text"
wha send-file --to CHAT_JID --path "C:\path\to\file.pdf"
```

