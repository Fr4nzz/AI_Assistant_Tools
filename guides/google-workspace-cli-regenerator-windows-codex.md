# Google Workspace CLI transferable setup for Codex Desktop on Windows, Linux, and WSL

This guide sets up a local Google Workspace CLI for Gmail, Drive, Calendar, Docs, Sheets, Forms, and related Google APIs so Codex Desktop can use it from any chat through a global skill.

This setup has been tested with Gmail read access, Google Drive listing and file upload, write-capable Docs/Sheets/Slides/Calendar scopes, and Google Forms creation for quiz-style workflows.

Important account-routing note for Codex Desktop: prefer the global `google-workspace` skill and local `gws` CLI for Google Workspace tasks. This uses the personal Google account authenticated through `gws`. Do not use the Codex Google Drive plugin unless the user explicitly asks for that connector, because the plugin may be authenticated to a different/shared Gmail account.

## Recommendation

Use `gws` from `googleworkspace/cli` as the primary setup.

Why:

- Better Windows/Linux install story: npm, prebuilt binaries, Homebrew, Cargo, Nix.
- Broadest Google Workspace API coverage because it dynamically builds commands from Google Discovery APIs.
- Structured JSON output and pagination are designed for automation.
- It ships Google Workspace agent skills, including Gmail and Drive skills.
- OAuth setup is integrated through `gws auth setup` / `gws auth login`, with manual OAuth fallback.

Keep `gog` from `openclaw/gogcli` as an alternative when you want stronger local safety controls such as `--gmail-no-send`, command allowlists/denylists, and baked safety-profile binaries.

Sources:

- `gws`: https://github.com/googleworkspace/cli
- `gws` releases: https://github.com/googleworkspace/cli/releases
- `gog`: https://github.com/openclaw/gogcli
- Google Cloud API Library: https://console.cloud.google.com/apis/library
- Google OAuth clients: https://console.cloud.google.com/apis/credentials
- Google OAuth consent screen: https://console.cloud.google.com/apis/credentials/consent
- Gmail API Python quickstart: https://developers.google.com/workspace/gmail/api/quickstart/python

## gws vs gog

| Area | `gws` (`googleworkspace/cli`) | `gog` (`openclaw/gogcli`) |
|---|---|---|
| Best use | Default Codex-friendly Google Workspace CLI | Safety-focused agent CLI |
| Install | npm, release binaries, Homebrew, Cargo, Nix | Homebrew, Docker, Windows zip, source build |
| OAuth | `gws auth setup`, `gws auth login`, manual OAuth, service accounts, access token env var | `gog auth credentials`, `gog auth add`, service accounts, direct tokens |
| Gmail | Full Gmail API surface plus helpers/skills | Curated Gmail UX, search/get/drafts/filters/backup |
| Drive/Docs/Sheets | Broad Discovery-generated API surface plus skills | Strong curated commands for Drive audits, Docs edits, Sheets tables |
| Agent output | Structured JSON, NDJSON pagination | `--json`, `--plain`, progress on stderr |
| Safety | Scope choice, skill discipline, sanitization options | `--gmail-no-send`, command allow/deny lists, safety-profile binaries |
| Maturity | Very broad, active, but pre-1.0 and not officially supported by Google | Active, more agent-shaped, smaller ecosystem |

## Install gws

### Option A: npm

Requires Node.js 18+.

Windows PowerShell, Linux, or WSL:

```powershell
npm install -g @googleworkspace/cli
gws --help
```

### Option B: prebuilt release binary

Download the latest release for your OS:

https://github.com/googleworkspace/cli/releases

Example Windows asset:

```text
google-workspace-cli-x86_64-pc-windows-msvc.zip
```

Extract it and put `gws.exe` somewhere on PATH, for example:

```powershell
mkdir "$HOME\.local\bin" -Force
Expand-Archive .\google-workspace-cli-x86_64-pc-windows-msvc.zip -DestinationPath "$HOME\.local\bin" -Force
gws --help
```

Example Linux x64 install:

```bash
curl -sLO https://github.com/googleworkspace/cli/releases/download/v0.22.5/google-workspace-cli-x86_64-unknown-linux-gnu.tar.gz
tar -xzf google-workspace-cli-x86_64-unknown-linux-gnu.tar.gz
chmod +x gws
mkdir -p ~/.local/bin
mv gws ~/.local/bin/
gws --help
```

Prefer the latest release version from the releases page instead of hardcoding `v0.22.5` forever.

### Option C: build from source

Requires Rust/Cargo.

```bash
cargo install --git https://github.com/googleworkspace/cli --locked
gws --help
```

## Google Cloud OAuth/API setup

You need a Google Cloud project and OAuth credentials.

Useful URLs:

- Create/select project: https://console.cloud.google.com/projectcreate
- Project selector: https://console.cloud.google.com/projectselector2/home/dashboard
- API Library: https://console.cloud.google.com/apis/library
- OAuth consent screen: https://console.cloud.google.com/apis/credentials/consent
- OAuth clients / credentials: https://console.cloud.google.com/apis/credentials

## First-time setup for a new Gmail account

Use the Gmail/Google Workspace account that should own the OAuth client and receive the API access. If a friend is setting this up, they should do this while logged into their own desired Google account.

1. Open a browser profile where you are logged into the desired Gmail account.
2. Go to https://console.cloud.google.com/projectcreate.
3. Create a project, for example `gws-cli-personal`.
4. Wait for Google Cloud to switch to the new project. If needed, use https://console.cloud.google.com/projectselector2/home/dashboard and select it.
5. Enable APIs from https://console.cloud.google.com/apis/library:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Docs API
   - Google Sheets API
   - Google Slides API, if needed
   - Google Forms API, if quizzes/forms are needed
6. Configure OAuth consent at https://console.cloud.google.com/apis/credentials/consent:
   - User Type: External
   - App name: `gws CLI`
   - Support email: the same Gmail account
   - Developer contact: the same Gmail account
   - Add the same Gmail account as a test user if the app stays in testing mode
7. Create OAuth client at https://console.cloud.google.com/apis/credentials:
   - Create Credentials
   - OAuth client ID
   - Application type: Desktop app
   - Name: `gws CLI`
8. Download the `client_secret_*.json` file.
9. Save it as:

```text
Windows: C:\Users\<USER>\.config\gws\client_secret.json
Linux/WSL: ~/.config/gws/client_secret.json
```

Then run:

```powershell
gws auth login -s gmail,drive,calendar,docs,sheets
```

For a read/write productivity setup where Codex can upload Drive files, edit Docs/Sheets/Slides, create Calendar events, and create Forms while keeping Gmail read-only, use explicit scopes:

```powershell
$scopes = 'https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/forms.body,https://www.googleapis.com/auth/forms.responses.readonly,openid,email,profile'
gws auth login --scopes $scopes
```

Linux/WSL:

```bash
gws auth login --scopes 'https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/forms.body,https://www.googleapis.com/auth/forms.responses.readonly,openid,email,profile'
```

If the OAuth app is still in testing mode, add the same Gmail account under Google Auth Platform -> Audience/Public -> Test users.

### Assisted browser option

An assistant can open the Google Cloud Console pages and navigate most non-sensitive UI steps, but the user should personally handle Google login, password, MFA, account selection, and OAuth consent. Google Cloud Console UI changes often, so the CLI/doc workflow above is the stable reference.

For a local assisted setup, ask Codex to open these pages in order:

1. https://console.cloud.google.com/projectcreate
2. https://console.cloud.google.com/apis/library
3. https://console.cloud.google.com/apis/credentials/consent
4. https://console.cloud.google.com/apis/credentials

After the OAuth client JSON is downloaded, move/rename it to `~/.config/gws/client_secret.json` and run `gws auth login -s gmail,drive,calendar,docs,sheets`.

Use AccountChooser when opening Google Cloud Console links so the browser does not silently use the wrong Google account:

```text
https://accounts.google.com/AccountChooser?continue=<URL-ENCODED-GOOGLE-CLOUD-URL>
```

### Windows Browser Use troubleshooting

If Codex Desktop Browser Use can see the in-app tab but external navigation fails with errors such as `failed to start codex app-server` or `The system cannot find the path specified`, apply this Windows workaround.

PowerShell:

```powershell
$pkg = Get-ChildItem 'C:\Program Files\WindowsApps' -Directory -Filter 'OpenAI.Codex_*' |
  Sort-Object Name -Descending |
  Select-Object -First 1

$src = Join-Path $pkg.FullName 'app\resources'
$dst = Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
$files = @(
  'codex.exe',
  'node.exe',
  'node_repl.exe',
  'codex-command-runner.exe',
  'codex-windows-sandbox-setup.exe'
)

New-Item -ItemType Directory -Force -Path $dst | Out-Null
foreach ($file in $files) {
  Copy-Item -LiteralPath (Join-Path $src $file) -Destination (Join-Path $dst $file) -Force
}

[Environment]::SetEnvironmentVariable('CODEX_CLI_PATH', (Join-Path $dst 'codex.exe'), 'User')
[Environment]::SetEnvironmentVariable('NODE_REPL_NODE_PATH', (Join-Path $dst 'node.exe'), 'User')
[Environment]::SetEnvironmentVariable('CODEX_HOME', (Join-Path $env:USERPROFILE '.codex'), 'User')
```

After running it, fully close and reopen Codex Desktop. Then test Browser Use with:

```text
open https://www.google.com in the in-app browser
```

### Preferred setup

If `gws auth setup` works in your environment, use it:

```powershell
gws auth setup
gws auth login -s gmail,drive,calendar,docs,sheets
```

Use only the services you need. For unverified OAuth apps in testing mode, Google can limit consent/scope behavior, so avoid huge all-service scope presets.

### Manual OAuth setup

Use this when `gws auth setup` cannot automate the Cloud project/client creation.

1. Open https://console.cloud.google.com/projectcreate and create/select a project.
2. Open https://console.cloud.google.com/apis/library and enable APIs you need:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Docs API
   - Google Sheets API
   - Google Slides API, if needed
3. Open https://console.cloud.google.com/apis/credentials/consent and configure OAuth consent:
   - App type: External is fine for personal testing.
   - Add your Google account as a test user.
4. Open https://console.cloud.google.com/apis/credentials.
5. Create OAuth client:
   - Application type: Desktop app.
6. Download the client JSON.
7. Save it where `gws` expects it, or point `gws` at it using the credential options described in the `gws` README.
8. Run:

```powershell
gws auth login -s gmail,drive,calendar,docs,sheets
```

Google's Gmail API quickstart also documents the Desktop app credential flow:

https://developers.google.com/workspace/gmail/api/quickstart/python

## Verify gws

Try small read-only commands first:

```powershell
gws drive files list --params '{"pageSize": 5}'
gws gmail users.messages.list --params '{"userId":"me","maxResults":5}'
gws calendar events list --params '{"calendarId":"primary","maxResults":5}'
```

On Windows PowerShell, inline JSON quoting can be annoying. Use `cmd /c` when a direct call fails:

```powershell
cmd /c "gws gmail users messages list --params ""{\""userId\"":\""me\"",\""maxResults\"":5}"""
cmd /c "gws drive files list --params ""{\""pageSize\"":5,\""fields\"":\""files(id,name,mimeType),nextPageToken\""}"""
```

## Windows PATH, UTF-8, and scripting notes

If `gws` was installed with npm, Windows usually creates `gws.ps1` and `gws.cmd` under:

```text
%APPDATA%\npm
```

Codex Desktop often includes `%USERPROFILE%\.local\bin` on PATH. For a stable Outlook-style shim, create:

```bat
:: %USERPROFILE%\.local\bin\gws.cmd
@echo off
call "%APPDATA%\npm\gws.cmd" %*
```

Use `gws` interactively, but use `gws.cmd` from Python/subprocess scripts because Windows process spawning may not resolve the PowerShell shim:

```python
subprocess.run(["gws.cmd", "auth", "status"], check=True)
```

Before commands that may print accented names, Spanish text, emoji, or hidden Unicode characters, set UTF-8:

```powershell
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

For Python helper scripts that print Gmail/Docs content:

```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

For repeated or complex `gws` calls, prefer writing request JSON to a local file or using a small helper script instead of fighting nested PowerShell quoting.

Use JSON output and pagination for automation. Check current command help because `gws` command surfaces are generated from Google Discovery APIs:

```powershell
gws --help
gws gmail --help
gws drive --help
gws schema gmail.users.messages.list
```

## Useful write-capable examples

Drive upload requires the uploaded file to be inside the current working directory tree. If the file is elsewhere, copy it into the workspace first, then upload it.

```powershell
gws drive files create --json '{"name":"notes.txt","mimeType":"text/plain"}' --upload ".\notes.txt" --upload-content-type text/plain
```

Create a Google Form:

```powershell
gws forms forms create --json '{"info":{"title":"Biology Quiz","documentTitle":"Biology Quiz"}}'
```

Google Forms can create quizzes and multiple-choice questions through `gws forms forms batchUpdate`. Use the Forms API request shape and prefer generating the full JSON body into a local file first when the quiz is more than a couple of questions.

Edit a Google Sheet value:

```powershell
gws sheets spreadsheets values update --params '{"spreadsheetId":"SPREADSHEET_ID","range":"Sheet1!A1","valueInputOption":"USER_ENTERED"}' --json '{"values":[["Hello from Codex"]]}'
```

Edit a Google Doc:

```powershell
gws docs documents batchUpdate --params '{"documentId":"DOCUMENT_ID"}' --json '{"requests":[{"insertText":{"location":{"index":1},"text":"Hello from Codex\n"}}]}'
```

## Install global Codex skill for gws

Create a global skill:

```powershell
$skillDir = Join-Path $HOME ".codex\skills\google-workspace"
New-Item -ItemType Directory -Force -Path $skillDir | Out-Null
notepad (Join-Path $skillDir "SKILL.md")
```

Use this `SKILL.md`:

```markdown
---
name: google-workspace
description: Use this skill whenever the user asks to search, read, summarize, triage, draft, or manage Gmail; list, search, inspect, download, or upload Google Drive files; inspect Google Calendar; work with Google Docs, Sheets, or Slides; or create/edit Google Forms and quizzes through the local `gws` Google Workspace CLI.
metadata:
  requires:
    bins: ["gws"]
---

# Google Workspace CLI

Use the local `gws` command for Google Workspace work. This is the account-routing skill: it exists to prefer the user's personal `gws` OAuth account over the Codex Google Drive/Gmail plugin account.

For general `gws` syntax, flags, schema discovery, and safety rules, read the installed upstream skills first:

- `../gws-shared/SKILL.md`
- `../gws-gmail/SKILL.md`
- `../gws-drive/SKILL.md`

Do not use the Codex Google Drive or Gmail plugins unless the user explicitly asks for those connectors; they may be authenticated to a different/shared account.

## Windows Reliability Notes

`gws` is normally on PATH through npm. On Windows, interactive shells may resolve `gws` to `gws.ps1`, while subprocesses and Python scripts often need the command shim explicitly as `gws.cmd`. If a script says it cannot find `gws`, call `gws.cmd`.

Use UTF-8 before commands that may print names, subjects, or message bodies with accents, emoji, or hidden Unicode characters:

```powershell
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

PowerShell is fine for `gws` as long as JSON quoting is handled deliberately. For simple commands, use `gws.cmd` directly. If inline JSON fails, call through `cmd /c`, for example:

```powershell
cmd /c "gws gmail users messages list --params ""{\""userId\"":\""me\"",\""maxResults\"":5}"""
```

If Git Bash is installed, it is also acceptable for direct `gws` commands because single-quoted JSON is cleaner there. Do not require Bash; it is only a convenience.

For repeated or complex `gws` calls, prefer writing request JSON to a local file and using a short helper script or `cmd /c` instead of fighting nested quoting. In Python, use `subprocess.run(["gws.cmd", ...])` and configure UTF-8 output with `sys.stdout.reconfigure(encoding="utf-8")` when printing API text.

## Local Checks

```powershell
gws.cmd --version
gws.cmd auth status
```

## Optional Upstream Skills

This custom skill is the account-routing skill and should stay installed. The minimal upstream `gws` skills to keep installed are `gws-shared`, `gws-gmail`, and `gws-drive`.

Some upstream skills mention helper skills such as `gws-gmail-read`, `gws-gmail-triage`, or `gws-drive-upload`. Those are not installed by default to avoid clutter. Use the base API commands directly, or install only the helper needed for the task:

```powershell
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-gmail-read
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-drive-upload
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-docs
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-sheets
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-forms
```

Do not install the whole repo unless the user explicitly wants many Google Workspace skills.


```

New Codex Desktop chats should load the skill automatically. If not, restart Codex Desktop.

Add this to the global `%USERPROFILE%\.codex\AGENTS.md` / `~/.codex/AGENTS.md` so new chats route Google Workspace tasks to the right account:

```markdown
For Google Workspace requests, prefer the global `google-workspace` skill and local `gws` CLI because it uses my personal Google account; avoid the Codex Google Drive plugin unless I explicitly ask for it.
```

## Optional: install official gws skills

The `gws` repo ships agent skills. Keep the custom `google-workspace` skill as the account-routing skill. The minimal recommended upstream set is:

- `gws-shared`
- `gws-gmail`
- `gws-drive`

Install those with:

```powershell
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-shared skills/gws-gmail skills/gws-drive
```

Install additional upstream skills only when a future task needs them:

```bash
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-docs
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-sheets
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-forms
```

For Codex Desktop, avoid installing the whole repo unless you explicitly want many Google Workspace skills in every chat. A simple global `SKILL.md` like the one above plus the three upstream skills is easier to audit and maintain.

## Alternative: gog setup

Use `gog` if you specifically want an agent-oriented CLI with stronger local safety controls.

Repo:

https://github.com/openclaw/gogcli

Docs:

https://gogcli.sh/

Windows:

1. Open https://github.com/openclaw/gogcli/releases.
2. Download `gogcli_<version>_windows_amd64.zip` or `gogcli_<version>_windows_arm64.zip`.
3. Extract `gog.exe`.
4. Put the folder on PATH.

macOS/Linux with Homebrew:

```bash
brew install gogcli
gog --version
```

Source build:

```bash
git clone https://github.com/openclaw/gogcli.git
cd gogcli
make
./bin/gog --version
```

OAuth setup:

```bash
gog auth credentials ~/Downloads/client_secret_....json
gog auth add you@gmail.com --services gmail,calendar,drive,docs,sheets,contacts
gog auth doctor --check
```

Useful `gog` examples:

```bash
gog gmail search 'newer_than:7d' --max 10 --json
gog gmail get MESSAGE_ID --sanitize-content --json
gog drive tree --depth 2 --json
gog drive get FILE_ID --fields 'id,name,mimeType,size,owners,emailAddress' --json
```

Agent-safe `gog` pattern:

```bash
gog --account you@gmail.com \
  --enable-commands gmail.search,gmail.get,drive.ls,docs.cat \
  --gmail-no-send \
  --json \
  gmail search 'newer_than:7d'
```

## Security notes

- Do not commit OAuth client JSON, tokens, refresh tokens, service-account keys, or keyring passwords.
- For personal Google Cloud projects in External testing mode, refresh tokens for sensitive user-data scopes can expire after a short testing window. Publishing/verifying the OAuth app or using a managed Workspace setup can change token behavior.
- Prefer narrow service/scopes. For example, use Gmail/Drive/Calendar only if those are needed.
- Treat send/share/delete/write operations as high-impact actions.


