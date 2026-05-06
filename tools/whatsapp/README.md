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

When an AI agent is guiding setup from Codex Desktop, run this command in an
external visible PowerShell window. The QR code is printed in the terminal; if
the command runs inside the agent's hidden/internal console, the user will not
be able to scan it.

One way to open a visible pairing window from PowerShell is:

```powershell
Start-Process powershell.exe -ArgumentList '-NoExit', '-Command', 'whasapo pair; Read-Host "Press Enter to close"'
```

Scan the QR code from:

```text
WhatsApp phone app > Settings > Linked Devices > Link a Device
```

Let Whasapo run for several minutes after pairing so
`%LOCALAPPDATA%\whasapo\session.db` can populate. Immediately after pairing,
`wha doctor` may report a valid paired connection while the local cache still
shows `0` messages or contacts. That is expected; wait for sync before relying
on search results.

In Codex Desktop, pairing and sync are separate steps. After a successful
`whasapo pair`, start the Whasapo server so it can stay connected and populate
the SQLite cache before searching chats:

```powershell
wha sync --wait 60
```

Then watch `wha doctor` until `messages` and `whatsmeow_contacts` are non-zero:

```powershell
wha doctor
```

Do this before running `wha search`, `wha chats`, `wha contacts`, or `wha media`.
If the cache is still at `0` messages, searches can return no results even
though WhatsApp is correctly paired.

For normal future use, run `wha sync --wait 20` before search-heavy tasks. The
local database is a cache, so it can be stale if Whasapo has not been running
since the phone received new messages. `wha sync` starts `whasapo serve` in the
background if it is not already running and then reports the current cache
counts.

## Test

```powershell
wha doctor
wha sync --wait 20
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

