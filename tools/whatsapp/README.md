# WhatsApp

WhatsApp access for Codex Desktop.

- Linux/CachyOS: use [`openclaw/wacli`](https://github.com/openclaw/wacli).
- Windows: keep using Whasapo plus the local `wha` wrapper for now.

`wacli` is also published for Windows (`wacli-windows-amd64.zip` in the
upstream releases), so replacing the Windows Whasapo flow is possible later.
The current repo keeps Windows on Whasapo because that path has already been
tested end to end in Codex Desktop on Windows.

## Linux / CachyOS

Install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) whatsapp
```

The Linux installer downloads the latest `openclaw/wacli` release binary for
the current architecture, installs it as `~/.local/bin/wacli`, and installs the
Codex `whatsapp` skill.

Pair:

```bash
wacli auth
```

This prints a QR code in the terminal and performs a first bootstrap sync after
pairing. Scan the QR code from:

```text
WhatsApp phone app > Settings > Linked Devices > Link a Device
```

Check status:

```bash
wacli --json doctor
wacli --json auth status
```

Sync:

```bash
wacli sync --once
nohup wacli sync --follow >/tmp/wacli-sync.log 2>&1 &
```

Search:

```bash
wacli --json messages search "field report" --limit 20
wacli --json chats list --limit 50
wacli --json contacts search "Manuel"
```

Send only when the user gives the exact recipient and exact message/file:

```bash
wacli send text --to 593991978514 --message "Exact message text"
wacli send file --to 593991978514 --file ./report.pdf --caption "Exact caption"
```

Notes:

- Default Linux store: `~/.local/state/wacli`.
- Use `--account NAME` for multiple WhatsApp identities.
- `wacli sync` stores what WhatsApp Web provides. Older history is best-effort;
  after a normal sync, use `wacli history coverage` and
  `wacli history backfill` when older messages are needed.
- Prefer `--json` for agent parsing.

## Windows

Install:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool whatsapp
```

The Windows installer downloads:

- `tools/whatsapp/bin/wha.py`
- `tools/whatsapp/bin/wha.cmd`
- `tools/whatsapp/skill/`

It also runs the upstream Whasapo installer unless `-SkipDependencies` is
passed.

Pair:

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

For normal future use, start sync without blocking the AI chat before
search-heavy tasks:

```powershell
wha sync
```

Test:

```powershell
wha doctor
wha sync
wha search intillacta -n 20
wha chats --query "Global Environ" -n 20
wha media --query .pdf -n 20
```

Use `--json` when Codex needs structured parsing.
