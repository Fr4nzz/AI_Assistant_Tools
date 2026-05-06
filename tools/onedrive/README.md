# OneDrive CLI

OneDrive and Microsoft 365 file access for Codex Desktop through Microsoft Graph file APIs.

This is separated from Outlook mail/calendar because Graph file scopes were available from the signed-in Microsoft web session, while Graph mail/calendar scopes were restricted by the institutional tenant. Outlook therefore uses the Outlook Web/REST route, while OneDrive uses Microsoft Graph for files.

## Files

- `bin/onedrive.py` - CLI implementation.
- `bin/onedrive.cmd` - Windows launcher.
- `skill/` - global Codex skill files.

## Install - Windows

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool onedrive
```

## Install - Linux / CachyOS

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) onedrive
```

Set up either D2L or Outlook first so the shared Microsoft browser profile is
signed in. If Microsoft asks, choose "Mantener mi sesion iniciada" / "Stay
signed in"; OneDrive uses that same browser-backed Microsoft session to obtain
Graph file tokens.

If D2L was the first login and OneDrive does not work immediately, open Outlook
once with `outlook login` before testing OneDrive again. This gives the shared
Microsoft profile a chance to finish the Office / Outlook token bootstrap path.
Close visible Chromium windows before running headless `onedrive` commands.

If OneDrive still fails with:

```text
Could not extract Microsoft Graph token from browser MSAL cache
```

open OneDrive itself in the same shared profile, let it load fully with the
institutional account, then close the visible browser and retry:

```powershell
$profile = Join-Path $env:LOCALAPPDATA 'outlook-cli\browser-data'
Start-Process msedge.exe -ArgumentList @('--new-window', "--user-data-dir=$profile", 'https://www.office.com/launch/onedrive')
```

If the error persists after Outlook, D2L, and OneDrive have all loaded in that
profile, the tenant or Office web session may not be issuing a reusable Graph
token to localStorage. In that case the CLI is installed correctly, but OneDrive
access remains blocked until the token bootstrap path is adjusted or the tenant
allows the needed Graph file flow.

Then test with safe read-only commands:

```bash
onedrive profile
onedrive ls
onedrive shared -n 10
```
