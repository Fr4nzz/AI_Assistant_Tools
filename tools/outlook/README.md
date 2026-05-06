# Outlook CLI

Read-only Outlook/Microsoft 365 mail and calendar access for Codex Desktop.

This tool was built for institutional Microsoft accounts where creating a normal third-party Microsoft Graph app or getting Graph mail/calendar scopes was blocked by tenant restrictions. The CLI uses a persistent Chromium profile for Outlook Web, extracts the signed-in Outlook Web token, and calls the Outlook REST mail/calendar endpoint that works with that session.

## Files

- `bin/outlook.py` - CLI implementation.
- `bin/outlook.cmd` - Windows launcher.
- `skill/` - global Codex skill files.

## Install

From the repository installer:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool outlook
```

Then run a headed login once:

```powershell
outlook login
```

After signing in and letting Outlook load, headless commands should work:

```powershell
outlook inbox -n 5
outlook search "thesis" -n 10
outlook calendar --days 7
```

