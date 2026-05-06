# Outlook CLI

Read-only Outlook/Microsoft 365 mail and calendar access for Codex Desktop.

This tool was built for institutional Microsoft accounts where creating a normal third-party Microsoft Graph app or getting Graph mail/calendar scopes was blocked by tenant restrictions. The CLI uses a persistent Chromium profile for Outlook Web, extracts the signed-in Outlook Web token, and calls the Outlook REST mail/calendar endpoint that works with that session.

## Files

- `bin/outlook.py` - CLI implementation.
- `bin/outlook.cmd` - Windows launcher.
- `skill/` - global Codex skill files.

## Install - Windows

From the repository installer:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool outlook
```

## Install - Linux / CachyOS

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) outlook
```

The Linux installer creates a venv under `~/.ai-assistant-tools/venv`, installs
Playwright there, copies the CLI to `~/.ai-assistant-tools/outlook`, and creates
the `~/.local/bin/outlook` shim.

## Login

Outlook uses the same persistent Chromium profile as D2L and OneDrive. If D2L
was already logged in successfully with "Stay signed in", the Microsoft account
picker may already be satisfied, but Outlook may still need its own first-time
visible web load. Do this headed login before running read-only Outlook
commands:

```bash
outlook login
```

Sign in to Microsoft/Outlook in the Chromium window. If prompted, check
"Mantener mi sesion iniciada" / "Stay signed in", then wait for Outlook to
load. Close that Chromium window before running headless CLI commands.
Leaving the visible Chromium window open can lock the shared profile and cause
headless commands to fail with a `ProcessSingleton` error.

On Linux/KDE/Wayland, if no visible window appears, launch the same profile
manually:

```bash
setsid chromium --new-window --ozone-platform-hint=auto \
  --user-data-dir="$HOME/.local/share/outlook-cli/browser-data" \
  "https://outlook.cloud.microsoft/mail/" \
  >"$HOME/.local/share/outlook-cli/chromium-login.log" 2>&1 &
```

After signing in and letting Outlook load, these safe read-only commands should
work:

```bash
outlook inbox -n 5
outlook search "thesis" -n 10
outlook calendar --days 7
```
