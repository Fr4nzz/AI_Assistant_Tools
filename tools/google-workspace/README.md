# Google Workspace / Gmail via gws

Google Workspace access for Codex Desktop through the local `gws` CLI: Gmail, Drive, Docs, Sheets, Slides, Forms, and Calendar.

Unlike the Microsoft tools, Gmail does not expose a convenient reusable browser token for this workflow. The reliable setup is to create a Google Cloud project, enable the relevant APIs, create a Desktop OAuth client, and authenticate `gws` with the needed scopes.

## Files

- `skill/` - custom global Codex routing skill that prefers the personal `gws` account and avoids the Codex Google Drive/Gmail plugins unless explicitly requested.

## Install

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool google-workspace
```

Then follow the OAuth setup in `guides/google-workspace-cli-regenerator-windows-codex.md`.

Useful checks:

```powershell
gws.cmd auth status
gws.cmd gmail users messages list --params '{"userId":"me","maxResults":5}'
gws.cmd drive files list --params '{"pageSize":5}'
```

