# OneDrive CLI

OneDrive and Microsoft 365 file access for Codex Desktop through Microsoft Graph file APIs.

This is separated from Outlook mail/calendar because Graph file scopes were available from the signed-in Microsoft web session, while Graph mail/calendar scopes were restricted by the institutional tenant. Outlook therefore uses the Outlook Web/REST route, while OneDrive uses Microsoft Graph for files.

## Files

- `bin/onedrive.py` - CLI implementation.
- `bin/onedrive.cmd` - Windows launcher.
- `skill/` - global Codex skill files.

## Install

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool onedrive
```

Set up Outlook first so the shared Microsoft browser profile is signed in. Then test:

```powershell
onedrive profile
onedrive ls
onedrive shared -n 10
```

