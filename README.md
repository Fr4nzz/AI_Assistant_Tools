# AI Assistant Tools

Local-first setup files for giving Codex Desktop access to personal productivity tools.

This repo is organized as one folder per tool. Each folder contains the actual scripts/skills when the tool is custom, plus a short README explaining the authentication model and first test commands.

## Use With An AI Agent

Send this repo URL to your AI coding assistant and ask it to guide the install. Copy/paste this prompt:

```text
Ayudame a instalar las herramientas de https://github.com/Fr4nzz/AI_Assistant_Tools.

Primero lee el README del repo. Luego dime que herramientas puedo instalar, enumeralas, y preguntame cuales quiero: todas o solo algunas. Despues instala una por una las que elija, explicando cada login o paso sensible antes de hacerlo. Cuando termines, prueba cada herramienta instalada con un comando de lectura seguro.
```

Expected agent flow:

1. Read this README and the relevant `tools/<name>/README.md` files.
2. Ask which tools to install: `gogcli`, `outlook`, `onedrive`, `d2l`, `whatsapp`, or `all`.
3. Run the installer for the selected tools.
4. Guide browser logins, OAuth consent, QR pairing, or institutional sign-in one tool at a time.
5. Restart Codex Desktop when skills are installed.
6. Test each installed tool with a safe read-only command.

## Tools

| Install name | Tool | What it enables | Why this setup exists |
|---|---|---|---|
| `gogcli` | Google Workspace / Gmail | Gmail, Calendar, Drive, Docs, Sheets, Slides, Forms, Tasks, and related Google APIs through `gog` | Gmail does not provide a practical reusable browser token for this workflow, so the reliable route is a Google Cloud project + Desktop OAuth client. `gog` is agent-friendly and supports structured JSON, sanitized Gmail reads, command guards, and multiple Google services. |
| `outlook` | Outlook / Microsoft 365 | Institutional Outlook mail and calendar | Built for an institutional Microsoft account where third-party Graph app/API permissions were restricted. Uses a headed/headless Outlook Web browser profile and the Outlook Web token path that works for mail/calendar. |
| `onedrive` | OneDrive / Microsoft 365 files | OneDrive and shared Microsoft files | Uses Microsoft Graph file APIs from the signed-in Microsoft web session. Graph file access worked, while Graph mail/calendar scopes did not. |
| `d2l` | D2L / Brightspace | Course, assignment, deadline, grade, announcement, and LMS file context | Uses browser-backed institutional login because simple API-token setup was not reliable for this environment. |
| `whatsapp` | WhatsApp / Whasapo + wha CLI | WhatsApp chats, search, groups, media discovery/download, explicit sending | Uses Whasapo pairing plus a local `wha` CLI. We moved away from the previous MCP-first approach because historical message sync/tool visibility was inconsistent; `wha` reads Whasapo's SQLite cache directly. |

## Quick Install

Install everything:

```powershell
irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1 | iex
```

Install only one tool:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool outlook
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool onedrive
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool d2l
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool gogcli
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool whatsapp
```

Download files and skills without installing dependencies:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool outlook -SkipDependencies
```

Installed custom CLIs are placed under:

```text
%USERPROFILE%\.ai-assistant-tools
```

PATH shims are placed under:

```text
%USERPROFILE%\.local\bin
```

Codex skills are placed under:

```text
%USERPROFILE%\.codex\skills
```

Restart Codex Desktop after installing skills or MCP servers.

## Repository Layout

```text
tools/
  outlook/
    bin/
    skill/
    README.md
  onedrive/
    bin/
    skill/
    README.md
  d2l/
    bin/
    skill/
    README.md
  gogcli/
    skill/
    README.md
  whatsapp/
    bin/
    skill/
    README.md
scripts/
  install.ps1
```

Each `tools/<name>/README.md` is the setup reference for that tool. The installer uses the files from `tools/`.
