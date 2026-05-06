# Outlook CLI Setup For Codex Desktop

Use the repo installer instead of copying embedded code from this guide:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool outlook
```

The installer downloads:

- `tools/outlook/bin/outlook.py`
- `tools/outlook/bin/outlook.cmd`
- `tools/outlook/skill/`

## Why This Exists

This setup was built for institutional Microsoft accounts where creating a normal third-party Microsoft Graph app or getting Graph mail/calendar scopes was blocked by tenant restrictions. It uses a persistent Outlook Web browser profile and the Outlook Web/Outlook REST token behavior that works for mail/calendar.

## First Login

Run:

```powershell
outlook login
```

Sign in in the headed browser, choose to stay signed in, wait for Outlook mail to load, then close the window.

## Test

```powershell
outlook inbox -n 5
outlook search "thesis" -n 10
outlook calendar --days 7
```

