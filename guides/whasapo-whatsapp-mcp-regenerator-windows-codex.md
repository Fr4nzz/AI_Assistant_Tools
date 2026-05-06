# Whasapo WhatsApp MCP Setup for Codex Desktop on Windows

This guide installs Whasapo as a WhatsApp MCP server for Codex Desktop. Whasapo uses a local SQLite database and exposes WhatsApp tools directly to Codex, including chat listing, message search, contact search, media download, and explicit sending.

## What This Provides

- WhatsApp access in Codex Desktop through MCP tools.
- Group chat discovery, including WhatsApp groups.
- Local SQLite message storage at `%LOCALAPPDATA%\whasapo\session.db`.
- Message search after Whasapo has had time to receive/sync messages.
- Safer sending workflow: Codex should only send when the user gives the exact recipient and exact message or file.

## Important Behavior

Whasapo does not necessarily make all historical messages searchable immediately after pairing.

After pairing, it may need time to populate its SQLite database. Chat and group names can appear quickly, but message search improves as the `messages` table grows. Leave Codex/Whasapo running for several minutes after pairing before judging search quality.

Check whether the database is growing:

```powershell
$db = "$env:LOCALAPPDATA\whasapo\session.db"
Get-Item $db
```

If Python is available, inspect table counts:

```powershell
python - <<'PY'
import os, sqlite3
db = os.path.join(os.environ["LOCALAPPDATA"], "whasapo", "session.db")
con = sqlite3.connect(db)
for name, in con.execute("select name from sqlite_master where type='table' order by name"):
    try:
        count = con.execute(f'select count(*) from "{name}"').fetchone()[0]
        print(f"{name}: {count}")
    except Exception as e:
        print(f"{name}: {e}")
PY
```

The useful table for search is usually `messages`. In a healthy setup, it should grow beyond a few live messages after Whasapo has been connected for a while.

## Install Whasapo

Run PowerShell:

```powershell
irm https://raw.githubusercontent.com/toloco/whasapo/main/install.ps1 | iex
```

The installer downloads `whasapo.exe` into:

```text
%LOCALAPPDATA%\whasapo\whasapo.exe
```

It may also configure Claude Desktop. That is harmless but not required for Codex Desktop.

Verify:

```powershell
whasapo version
whasapo status
```

If `whasapo` is not on PATH in the current terminal, call it directly:

```powershell
& "$env:LOCALAPPDATA\whasapo\whasapo.exe" version
```

## Pair WhatsApp

Run:

```powershell
whasapo pair
```

Then scan the QR code from:

```text
WhatsApp phone app > Settings > Linked Devices > Link a Device
```

Verify:

```powershell
whasapo status
```

Expected:

```text
Status: paired
Connection: OK
```

## Register Whasapo with Codex MCP

Run:

```powershell
codex mcp add whatsapp-whasapo -- "$env:LOCALAPPDATA\whasapo\whasapo.exe" serve
```

If the command has trouble expanding `%LOCALAPPDATA%`, use the full path:

```powershell
codex mcp add whatsapp-whasapo -- C:\Users\YOUR_USER\AppData\Local\whasapo\whasapo.exe serve
```

Verify:

```powershell
codex mcp get whatsapp-whasapo
codex mcp list --json
```

Expected:

```text
whatsapp-whasapo
  enabled: true
  transport: stdio
  command: C:\Users\...\AppData\Local\whasapo\whasapo.exe
  args: serve
```

Restart Codex Desktop after adding the MCP server. Codex usually loads MCP servers at app startup.

## Global Codex Hint

Add this one-line hint to:

```text
%USERPROFILE%\.codex\AGENTS.md
```

Line:

```text
For WhatsApp requests, use the `whatsapp-whasapo` MCP server/tools; never send unless I explicitly provide the exact recipient and message/file.
```

## Test in Codex Desktop

After restarting Codex Desktop, ask:

```text
Can you list my WhatsApp chats using Whasapo?
```

Expected behavior:

- Codex should have MCP tools named under `whatsapp-whasapo`.
- Chat listing should return group and direct chats.
- Message search may initially return few or no messages until the SQLite database grows.

Example useful requests:

```text
Search my WhatsApp for "intillacta" using Whasapo.
Find WhatsApp messages in the group "Global Environ. Change METC" about the field report.
Summarize recent WhatsApp messages from Project_Environmental change.
```

## Troubleshooting

This setup uses a local Codex-patched Whasapo build named `0.8.0-codex-reconnect`. The patch makes the MCP server retry after WhatsApp `StreamReplaced` and disconnect events instead of staying permanently stuck in a `connection lost` state.

The original release binary is backed up at:

```text
%LOCALAPPDATA%\whasapo\whasapo-release-0.8.0.exe.bak
```

If you run `whasapo update`, the upstream binary may replace the patched build. If connection-loss behavior returns after updating, rebuild or reinstall the patched build, or check whether upstream has fixed reconnect handling.

If Codex says it cannot access WhatsApp tools:

1. Verify MCP registration:

```powershell
codex mcp get whatsapp-whasapo
```

2. Verify pairing:

```powershell
whasapo status
```

3. Restart Codex Desktop.

If MCP tools report that WhatsApp is reconnecting or disconnected, but `whasapo status` says `Connection: OK`, stale server processes may be stuck. Close Codex Desktop, then run:

```powershell
Get-Process whasapo -ErrorAction SilentlyContinue | Stop-Process -Force
```

Reopen Codex Desktop. It should launch a fresh MCP server.

Avoid running many Whasapo MCP calls in parallel. Also avoid running `whasapo status` repeatedly while Codex has an active MCP server unless troubleshooting, because it opens another WhatsApp Web client session and can replace the active stream.

If message search returns no historical messages:

- Leave Codex Desktop open for several minutes.
- Send or receive a WhatsApp message to confirm live capture works.
- Recheck the SQLite database size and `messages` row count.
- Chat/group listing can work before message search is fully useful.

## Maintenance

Update Whasapo:

```powershell
whasapo update
```

Check version:

```powershell
whasapo version
```

Uninstall Whasapo:

```powershell
whasapo uninstall
codex mcp remove whatsapp-whasapo
```

Do not delete `%LOCALAPPDATA%\whasapo\session.db` unless you want to remove the paired session and local message database.
