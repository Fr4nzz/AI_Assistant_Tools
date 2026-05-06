# Google Workspace via gws, Gmail via gog

Google Workspace access for Codex Desktop through local CLIs:

- `gog` for Gmail search, message reads, thread reads, and agent-friendly sanitized JSON.
- `gws` for Drive, Docs, Sheets, Slides, Forms, Calendar, and broader Google Workspace editing.

Unlike the Microsoft tools, Gmail does not expose a convenient reusable browser token for this workflow. The reliable setup is to create a Google Cloud project, enable the relevant APIs, create a Desktop OAuth client, and authenticate `gws` with the needed scopes.

## Files

- `skill/` - custom global Codex routing skill that prefers the personal `gws` account and avoids the Codex Google Drive/Gmail plugins unless explicitly requested.
- The installer also installs the essential upstream `gws` skills: `gws-shared`, `gws-gmail`, `gws-drive`, and `gws-docs`.
- The installer can also install `gogcli`, which places `gog.exe` directly in `%USERPROFILE%\.local\bin`.

## Install

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool google-workspace
```

Then follow the OAuth setup below.

Useful checks:

```powershell
gws.cmd auth status
gog auth status
gog --account you@gmail.com --gmail-no-send gmail search "newer_than:2d" --max 10 --json
gws.cmd gmail users messages list --params '{"userId":"me","maxResults":5}'
gws.cmd drive files list --params '{"pageSize":5}'
```
