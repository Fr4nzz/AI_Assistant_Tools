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
2. Ask which tools to install: `gogcli`, `outlook`, `onedrive`, `d2l`, `whatsapp`, `humanizer`, `paper-fetch`, or `all`.
3. Detect the OS and use the Windows or Linux install path below.
4. On Windows, check prerequisites before running the installer:
   `python --version`, `py --version`, and whether `~\.local\bin` is on the
   user PATH. The Outlook, OneDrive, and D2L tools need Python + pip for
   Playwright. If `python` is missing, install Python first or make the existing
   Python available on PATH, then rerun the installer.
5. Run the installer for the selected tools. The installer is safe to rerun if
   a prerequisite fails partway through.
6. Guide browser logins, OAuth consent, QR pairing, or institutional sign-in one tool at a time.
   For Microsoft/USFQ logins, explicitly remind the user to choose
   "Mantener mi sesion iniciada" / "Stay signed in" when prompted.
   This is what makes later headless commands reuse the same session.
   Always do first-time logins in visible browser windows before trying read-only
   headless commands. When installing `d2l`, `outlook`, and `onedrive` together,
   open both D2L and Outlook in headed browser windows during initial setup. They
   share a Chromium profile, but each service may still need its own first-time
   web load, cookies, or token bootstrap.
7. Close visible Chromium, Chrome, or Edge windows that were opened with the
   shared tool profile before running headless commands. A visible browser can
   lock the profile and make headless Outlook, OneDrive, or D2L tests fail.
8. If pairing WhatsApp from Codex Desktop, open `whasapo pair` in an external
   visible terminal window. The QR code is printed to the terminal; if it runs
   inside an agent-only console, the user cannot scan it.
9. Restart Codex Desktop when skills are installed.
10. Test each installed tool with a safe read-only command. For CLIs with a
    global JSON flag, put `--json` before the subcommand, for example
    `outlook --json profile` and `d2l --json classes`.

## Tools

| Install name | Tool | What it enables | Why this setup exists |
|---|---|---|---|
| `gogcli` | Google Workspace / Gmail | Gmail, Calendar, Drive, Docs, Sheets, Slides, Forms, Tasks, and related Google APIs through `gog` | Gmail does not provide a practical reusable browser token for this workflow, so the reliable route is a Google Cloud project + Desktop OAuth client. `gog` is agent-friendly and supports structured JSON, sanitized Gmail reads, command guards, and multiple Google services. |
| `outlook` | Outlook / Microsoft 365 | Institutional Outlook mail and calendar | Built for an institutional Microsoft account where third-party Graph app/API permissions were restricted. Uses a headed/headless Outlook Web browser profile and the Outlook Web token path that works for mail/calendar. |
| `onedrive` | OneDrive / Microsoft 365 files | OneDrive and shared Microsoft files | Uses Microsoft Graph file APIs from the signed-in Microsoft web session. Graph file access worked, while Graph mail/calendar scopes did not. |
| `d2l` | D2L / Brightspace | Course, assignment, deadline, grade, announcement, and LMS file context | Uses browser-backed institutional login because simple API-token setup was not reliable for this environment. |
| `whatsapp` | WhatsApp / Whasapo + wha CLI | WhatsApp chats, search, groups, media discovery/download, explicit sending | Uses Whasapo pairing plus a local `wha` CLI. We moved away from the previous MCP-first approach because historical message sync/tool visibility was inconsistent; `wha` reads Whasapo's SQLite cache directly. |
| `humanizer` | Humanizer skill | Natural-language rewrite and prose polishing for drafts, docs, emails, PR descriptions, and similar text | Vendors the MIT-licensed Hermes Agent humanizer skill so Codex can apply a focused style pass without any external account setup. |
| `paper-fetch` | Paper Fetch | Search and download academic papers from open access sources, repositories, and academic mirrors | Searches OpenAlex, Semantic Scholar, Crossref, arXiv, bioRxiv, and Google Scholar in parallel. Downloads papers by DOI with multi-source fallback: OA → mirrors → Anna's Archive → direct PDF. |

## Quick Install - Windows

Requirements:

- Python 3.10+ with `pip` available as `python` on PATH for `outlook`,
  `onedrive`, and `d2l`.
- Internet access for GitHub downloads, pip packages, and Playwright Chromium.
- `~\.local\bin` on the user PATH after installation. The installer creates
  shims there, but a running terminal or Codex session may need PATH refreshed
  or Codex Desktop restarted before commands are found.

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
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool humanizer
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool paper-fetch
```

For `paper-fetch`, set an Unpaywall contact email after installation. Search and
mirror fallback can work without it, but Unpaywall is usually the fastest and
cleanest DOI download path:

```powershell
paper-dl set-key unpaywall-email your@email.com
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

If the installer stops with `python : The term 'python' is not recognized`,
install Python for the current user with pip enabled and rerun the same
installer command. The already installed tools do not need to be cleaned up.

Restart Codex Desktop after installing skills or MCP servers.

Windows login notes:

- Outlook, OneDrive, and D2L share the browser profile at
  `%LOCALAPPDATA%\outlook-cli\browser-data`.
- Run `outlook login` and `d2l login` in visible browser windows the first time.
  Choose "Mantener mi sesion iniciada" / "Stay signed in" if Microsoft asks.
- Close those visible browser windows before testing commands such as
  `outlook inbox -n 5`, `onedrive profile`, or `d2l classes`.
- If an agent needs to close only the tool browser, target processes whose
  command line contains `outlook-cli\browser-data`, not the user's normal
  browser sessions.
- For WhatsApp, run `whasapo pair` in a terminal window the user can see, scan
  the QR code, then run `wha sync --wait 60` immediately so sync begins. Check
  `wha doctor` and wait until `messages` and `whatsmeow_contacts` are non-zero
  before searching chats or media. For later day-to-day WhatsApp tasks, start
  nonblocking sync with
  `Start-Process -WindowStyle Hidden -FilePath wha -ArgumentList 'sync','--wait','0'`
  before searching.

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
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) humanizer
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) paper-fetch
```

For `paper-fetch`, set an Unpaywall contact email after installation. Search and
mirror fallback can work without it, but Unpaywall is usually the fastest and
cleanest DOI download path:

```bash
paper-dl set-key unpaywall-email your@email.com
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

- Prefer installing Google Cloud CLI and using `gcloud` for the parts it can
  automate: authenticating the owner account, creating the project, selecting
  it, and enabling APIs. On Windows, call `gcloud.cmd` from automation if
  PowerShell blocks `gcloud.ps1`.
- If `gcloud projects create` fails with `Callers must accept Terms of Service`,
  open Google Cloud Console with the project owner account, accept the Google
  Cloud Terms of Service, then rerun project creation with a new project ID.
- Open Google Auth Platform console pages through an account chooser URL when
  the browser has multiple Google accounts. Open one setup page at a time, not
  all links at once:

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
  humanizer/
    skill/
    README.md
  paper-fetch/
    bin/
    skill/
    README.md
scripts/
  install.ps1
```

Each `tools/<name>/README.md` is the setup reference for that tool. The installer uses the files from `tools/`.
