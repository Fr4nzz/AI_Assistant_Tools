# Whasapo WhatsApp MCP Setup For Codex Desktop

Install:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool whatsapp
```

## Why Whasapo

We tried another WhatsApp approach, but it did not sync historical messages reliably. Whasapo stores messages in a local SQLite database and works better after pairing and letting the database populate.

## Pair

```powershell
whasapo pair
```

Scan the QR code from WhatsApp on your phone:

```text
Settings > Linked Devices > Link a Device
```

## Register MCP Manually

If needed:

```powershell
codex mcp add whatsapp-whasapo -- "$env:LOCALAPPDATA\whasapo\whasapo.exe" serve
```

Restart Codex Desktop after adding or changing MCP servers.

## Notes

- Message search may initially return few or no historical messages until `%LOCALAPPDATA%\whasapo\session.db` grows.
- Never send WhatsApp messages unless the user explicitly provides the exact recipient and exact message or file.

