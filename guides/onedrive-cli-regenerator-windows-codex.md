# OneDrive CLI Setup For Codex Desktop

Install:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool onedrive
```

The installer downloads:

- `tools/onedrive/bin/onedrive.py`
- `tools/onedrive/bin/onedrive.cmd`
- `tools/onedrive/skill/`

## Why This Exists

OneDrive uses Microsoft Graph file APIs from the signed-in Microsoft web session. This is separate from Outlook mail/calendar because Graph file scopes were available, while Graph mail/calendar scopes were restricted in the institutional tenant.

## Prerequisite

Set up and sign into Outlook first, because this OneDrive tool reuses the Microsoft browser profile.

## Test

```powershell
onedrive profile
onedrive ls
onedrive shared -n 10
```

