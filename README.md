# AI Assistant Tools

Local-first setup files for giving Codex Desktop access to personal productivity tools.

This repo is organized as one folder per tool. Each folder contains the actual scripts/skills when the tool is custom, plus a short README explaining the authentication model and first test commands.

## Use With An AI Agent

Send this repo URL to your AI coding assistant and ask it to guide the install. Copy/paste this prompt:

```text
Ayudame a instalar las herramientas de https://github.com/Fr4nzz/AI_Assistant_Tools.

Primero lee el README del repo. Luego dime que herramientas puedo instalar, enumeralas, y preguntame cuales quiero: todas o solo algunas. Despues instala una por una las que elija, explicando cada login o paso sensible antes de hacerlo. Cuando termines, prueba cada herramienta instalada.
```

Expected agent flow:

1. Read this README and the relevant `tools/<name>/README.md` files.
2. Ask which tools to install: `gogcli`, `outlook`, `onedrive`, `d2l`, `whatsapp`, or `all`.
3. Detect the OS and use the Windows or Linux install path below.
4. Run the installer for the selected tools.
5. Guide browser logins, OAuth consent, QR pairing, or institutional sign-in one tool at a time.
   For Microsoft/USFQ logins, explicitly remind the user to choose
   "Mantener mi sesion iniciada" / "Stay signed in" when prompted.
   This is what makes later headless commands reuse the same session.
   Always do first-time logins in visible browser windows before trying read-only
   headless commands. When installing `d2l`, `outlook`, and `onedrive` together,
   open both D2L and Outlook in headed browser windows during initial setup. They
   share a Chromium profile, but each service may still need its own first-time
   web load, cookies, or token bootstrap.
6. Restart Codex Desktop when skills are installed.
7. Test each installed tool with a safe read-only command.

## Tools

| Install name | Tool | What it enables | Why this setup exists |
|---|---|---|---|
| `gogcli` | Google Workspace / Gmail | Gmail, Calendar, Drive, Docs, Sheets, Slides, Forms, Tasks, and related Google APIs through `gog` | Gmail does not provide a practical reusable browser token for this workflow, so the reliable route is a Google Cloud project + Desktop OAuth client. `gog` is agent-friendly and supports structured JSON, sanitized Gmail reads, command guards, and multiple Google services. |
| `outlook` | Outlook / Microsoft 365 | Institutional Outlook mail and calendar | Built for an institutional Microsoft account where third-party Graph app/API permissions were restricted. Uses a headed/headless Outlook Web browser profile and the Outlook Web token path that works for mail/calendar. |
| `onedrive` | OneDrive / Microsoft 365 files | OneDrive and shared Microsoft files | Uses Microsoft Graph file APIs from the signed-in Microsoft web session. Graph file access worked, while Graph mail/calendar scopes did not. |
| `d2l` | D2L / Brightspace | Course, assignment, deadline, grade, announcement, and LMS file context | Uses browser-backed institutional login because simple API-token setup was not reliable for this environment. |
| `whatsapp` | WhatsApp / Whasapo + wha CLI | WhatsApp chats, search, groups, media discovery/download, explicit sending | Uses Whasapo pairing plus a local `wha` CLI. We moved away from the previous MCP-first approach because historical message sync/tool visibility was inconsistent; `wha` reads Whasapo's SQLite cache directly. |

## Quick Install - Windows

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

## Quick Install - Linux / CachyOS

Linux uses a Bash installer instead of the Windows PowerShell installer. It
places custom CLIs under `~/.ai-assistant-tools`, creates POSIX shims under
`~/.local/bin`, installs Python dependencies in an isolated venv, and copies
Codex skills to `~/.codex/skills`.

Install everything supported on Linux:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh)
```

Install only one tool:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) outlook
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) onedrive
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) d2l
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) gogcli
```

Requirements:

- `python`, `python-venv` support, `curl`, and `tar`
- Chromium or Chrome on PATH. CachyOS/Arch usually works with `chromium`.
- `~/.local/bin` on PATH

Installed custom CLIs are placed under:

```text
~/.ai-assistant-tools
```

PATH shims are placed under:

```text
~/.local/bin
```

Codex skills are placed under:

```text
~/.codex/skills
```

Restart Codex Desktop after installing skills.

Linux login notes:

- D2L, Outlook, and OneDrive share the Chromium profile at
  `~/.local/share/outlook-cli/browser-data`.
- If installing D2L and Outlook together, open both headed login flows during
  initial setup: `d2l login` for Brightspace and `outlook login` for Outlook
  Web. They share Microsoft SSO state, but a second visible login or service
  load may still be needed the first time.
- If Outlook or OneDrive are installed without D2L, use `outlook login` to open
  the same shared profile.
- If Microsoft asks whether to stay signed in, check
  "Mantener mi sesion iniciada" / "Stay signed in".
- If the browser does not appear in KDE/Wayland, try:

```bash
setsid chromium --new-window --ozone-platform-hint=auto \
  --user-data-dir="$HOME/.local/share/outlook-cli/browser-data" \
  "https://outlook.cloud.microsoft/mail/" \
  >"$HOME/.local/share/outlook-cli/chromium-login.log" 2>&1 &
```

After signing in, close visible Chromium windows before running headless
commands. Chromium locks the profile while a visible window is open, so headless
commands may fail with `ProcessSingleton` errors if the window is left running.

Google Workspace / `gogcli` setup notes:

- Use `gcloud` only for the parts it can automate: authenticating the owner
  account, creating the project, selecting it, and enabling APIs.
- Open Google Auth Platform console pages through an account chooser URL when
  the browser has multiple Google accounts:

```text
https://accounts.google.com/AccountChooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fauth%2Faudience%3Fproject%3DPROJECT_ID
https://accounts.google.com/AccountChooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fauth%2Fclients%3Fproject%3DPROJECT_ID
```

- For normal Gmail accounts, choose **External users / Usuarios externos** on
  the OAuth audience screen. **Internal** is only for Google Workspace
  organizations.
- In **Test users / Usuarios de prueba**, click **Add users / Agregar usuarios**
  and add the Gmail account while the app is in Testing. Otherwise Google blocks
  OAuth with `403 access_denied`.
- In **Clients**, click **Create client / Crear cliente**, choose
  **Desktop app / App de escritorio**, keep a simple name such as
  `Desktop client 1` / `Cliente de escritorio 1`, click **Create / Crear**, then
  click **Download JSON / Descargar JSON** in the success dialog before closing
  it. Use that downloaded JSON with `gog auth credentials set`.
- When `gog` saves OAuth tokens, prefer the OS keyring when available. Windows
  usually uses Windows Credential Manager without an extra passphrase. Linux
  desktop sessions may show a KDE Wallet / GNOME Keyring access prompt; approve
  it to use `gog auth keyring auto` without `GOG_KEYRING_PASSWORD`. If the
  system keyring is unavailable, `gog` falls back to encrypted file storage and
  may ask for a stable local passphrase. Suggest a memorable value such as
  `ai_assistant`, `ai_assistant_tools`, or another private phrase. The user
  should type it directly in their terminal or set `GOG_KEYRING_PASSWORD` in a
  private shell; they should not paste it into chats or logs.

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
