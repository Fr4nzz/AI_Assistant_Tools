# AI Assistant Tools

Transferable setup guides and helper installers for giving Codex Desktop access to useful personal productivity tools.

These guides are meant for personal accounts and local-first setups. They help a user recreate the same tool access on another Windows Codex Desktop machine, then optionally adapt the commands for Linux or WSL where the guide supports it.

## Tools Included

| Tool | Main capability | Setup approach |
|---|---|---|
| Google Workspace / Gmail | Gmail search, Drive, Docs, Sheets, Slides, Forms, Calendar through `gws` | Uses a user-created Google Cloud project and OAuth desktop client. Gmail does not expose a convenient reusable web token for this workflow, so API access needs proper OAuth setup. |
| Outlook / Microsoft 365 | Institutional Outlook mail and calendar | Uses a persistent headed/headless browser profile to access Outlook Web tokens because the institutional account made normal third-party Microsoft Graph app/API registration impractical. The working mail/calendar path uses Outlook Web/Outlook REST token behavior rather than a custom Graph app. |
| OneDrive / Microsoft 365 files | OneDrive and shared file access | Uses Microsoft Graph file APIs, with token discovery from the signed-in Microsoft web session. This is separated from Outlook mail/calendar because Graph file scopes were available while Graph mail/calendar scopes were restricted. |
| D2L / Brightspace | Course, assignment, deadline, and LMS context | Uses a local CLI with browser-backed authentication because institutional login restrictions make simple API-token setup unreliable. |
| WhatsApp / Whasapo MCP | WhatsApp chat search, media download, group discovery, explicit sending | Uses Whasapo as an MCP server. We moved away from the previous WhatsApp approach because it did not sync historical messages reliably; Whasapo stores messages locally and works better once its SQLite database has populated. |

## Quick Install Of Guides

After this repo is public, a friend can download the guide pack with PowerShell:

```powershell
irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-guides.ps1 | iex
```

To download only one guide:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-guides.ps1))) -Tool google-workspace
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-guides.ps1))) -Tool outlook
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-guides.ps1))) -Tool onedrive
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-guides.ps1))) -Tool d2l
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-guides.ps1))) -Tool whatsapp
```

The installer downloads Markdown guides into:

```text
%USERPROFILE%\Documents\AI_Assistant_Tools
```

Review downloaded scripts and OAuth steps before running anything that authenticates an account.

## Guide Files

- [`guides/google-workspace-cli-regenerator-windows-codex.md`](guides/google-workspace-cli-regenerator-windows-codex.md)
- [`guides/outlook-cli-regenerator-windows-codex.md`](guides/outlook-cli-regenerator-windows-codex.md)
- [`guides/onedrive-cli-regenerator-windows-codex.md`](guides/onedrive-cli-regenerator-windows-codex.md)
- [`guides/d2l-cli-regenerator-windows-codex.md`](guides/d2l-cli-regenerator-windows-codex.md)
- [`guides/whasapo-whatsapp-mcp-regenerator-windows-codex.md`](guides/whasapo-whatsapp-mcp-regenerator-windows-codex.md)

## Security Notes

- Do not commit OAuth client secrets, tokens, browser profiles, SQLite message databases, cookies, or downloaded private attachments.
- Prefer read-only scopes unless write access is needed.
- Treat send/share/delete/move/write actions as explicit-confirmation operations.
- These setups are personal productivity tooling, not centrally managed enterprise deployments.

