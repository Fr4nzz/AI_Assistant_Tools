# WhatsApp via Whasapo MCP

WhatsApp access for Codex Desktop through Whasapo as an MCP server.

We previously considered another WhatsApp setup, but it did not sync historical messages reliably. Whasapo stores messages in a local SQLite database and works better after it has been paired and allowed to populate the database.

## Install

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool whatsapp
```

Then pair WhatsApp:

```powershell
whasapo pair
```

Register with Codex if the installer did not do it:

```powershell
codex mcp add whatsapp-whasapo -- "$env:LOCALAPPDATA\whasapo\whasapo.exe" serve
```

Restart Codex Desktop after adding or changing MCP servers.

