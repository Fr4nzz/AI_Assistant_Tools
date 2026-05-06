# gogcli for Google Workspace

`gog` is the preferred Google CLI for Codex agents because it has compact JSON output, sanitized Gmail message/thread reads, account selection, command guards, and broad support for Gmail, Calendar, Drive, Docs, Sheets, Slides, Forms, Apps Script, Contacts, Tasks, People, and Classroom.

Use `gog` for Google Workspace summaries, triage, context gathering, uploads, and editing. Avoid the Codex Google Drive/Gmail plugins unless the user explicitly asks for those connectors because they may be authenticated to a different account.

## Install - Windows

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool gogcli
```

The installer downloads the latest Windows amd64 release from `openclaw/gogcli`, extracts `gog.exe`, and copies it directly to:

```text
%USERPROFILE%\.local\bin\gog.exe
```

That follows the upstream Windows recommendation: put the directory containing `gog.exe` on PATH. No `gog.cmd` shim is used.

## Install - Linux / CachyOS

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) gogcli
```

The Linux installer downloads the latest `openclaw/gogcli` Linux release for
the current architecture and installs `gog` to:

```text
~/.local/bin/gog
```

## Google Cloud Setup

`gog` needs a Google Cloud project with Workspace APIs enabled and a Desktop app
OAuth client. The recommended setup path is to install Google Cloud CLI and let
the agent use `gcloud` for the project and API setup. The Google Auth Platform
consent screen and Desktop OAuth client still need to be completed in the
browser.

On Windows, install Google Cloud CLI first if `gcloud` is not already available:

```powershell
$installer = Join-Path $env:TEMP 'GoogleCloudSDKInstaller.exe'
Invoke-WebRequest -Uri 'https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe' -OutFile $installer
Start-Process -FilePath $installer -ArgumentList @('/S', '/allusers') -Wait
```

After install, `gcloud.cmd` may be available before `gcloud` is on PATH, and
PowerShell may block `gcloud.ps1` depending on ExecutionPolicy. Prefer calling
the `.cmd` wrapper from automation:

```powershell
$gcloud = Join-Path ${env:ProgramFiles(x86)} 'Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd'
& $gcloud --version
```

First authenticate `gcloud` as the Google account that should own the project:

```powershell
& $gcloud auth login
```

If a terminal is hidden from the user, open this command in a visible external
PowerShell window so the user can complete the browser login and any prompts.

Then create the project and enable APIs:

```powershell
$PROJECT_ID = "ai-assistant-$(Get-Date -Format 'yyMMddHHmmss')"
& $gcloud projects create $PROJECT_ID --name='AI Assistant'
& $gcloud config set project $PROJECT_ID
& $gcloud services enable `
  gmail.googleapis.com `
  calendar-json.googleapis.com `
  drive.googleapis.com `
  docs.googleapis.com `
  sheets.googleapis.com `
  slides.googleapis.com `
  tasks.googleapis.com `
  --project $PROJECT_ID
```

If project creation fails with `Callers must accept Terms of Service`, open
Google Cloud Console once with the project owner account, accept the Google
Cloud Terms of Service, and rerun the `projects create` command with a new
project ID.

Linux/macOS shells can use the equivalent Bash form:

```bash
PROJECT_ID="ai-assistant-$(date +%y%m%d%H%M%S)"
gcloud projects create "$PROJECT_ID" --name="AI Assistant"
gcloud config set project "$PROJECT_ID"
gcloud services enable gmail.googleapis.com calendar-json.googleapis.com drive.googleapis.com docs.googleapis.com sheets.googleapis.com slides.googleapis.com tasks.googleapis.com --project "$PROJECT_ID"
```

Open the remaining setup pages with Google account chooser URLs so a browser
with multiple Google accounts does not silently use the wrong account. Open one
page at a time and finish it before moving to the next:

```text
https://accounts.google.com/AccountChooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fauth%2Faudience%3Fproject%3DPROJECT_ID
https://accounts.google.com/AccountChooser?continue=https%3A%2F%2Fconsole.cloud.google.com%2Fauth%2Fclients%3Fproject%3DPROJECT_ID
```

In **OAuth consent / Audience**:

- App name: `AI Assistant` or a similar personal name.
- User support email: the same Gmail account.
- Audience: choose **External users / Usuarios externos** for normal Gmail
  accounts. **Internal** only works for Google Workspace organizations.
- In **Test users / Usuarios de prueba**, click **Add users / Agregar usuarios**
  and add the Gmail account that will authorize `gog`. While the app is in
  Testing, Google blocks any account that is not in this list with
  `403 access_denied`.

In **Clients**, create an OAuth client:

- Click **Create client / Crear cliente**.
- Application type / Tipo de aplicacion: **Desktop app / App de escritorio**.
- Name / Nombre: the default such as `Desktop client 1` /
  `Cliente de escritorio 1` is fine.
- Click **Create / Crear**.
- In the success dialog, click **Download JSON / Descargar JSON** before
  closing the dialog. The client secret may not be shown again after the dialog
  is closed.
- Treat the downloaded JSON as sensitive and keep it in a private local path.

## OAuth

Create a Google Cloud project, enable the APIs you need, create a Desktop OAuth client, then store that client JSON in `gog`.

```bash
gog auth credentials set "$HOME/Downloads/client_secret_....json"
gog auth add you@gmail.com --services gmail,calendar,drive,docs,sheets,slides,forms,tasks
```

Token storage depends on the OS keyring backend:

- Windows usually uses Windows Credential Manager and should not need a
  `GOG_KEYRING_PASSWORD`.
- Linux desktop sessions can use a system keyring such as KDE Wallet or GNOME
  Keyring with `gog auth keyring auto`. The desktop may show a prompt asking
  whether to allow access; approve it if you want `gog` to run without an
  environment passphrase.
- Linux fallback is the encrypted file keyring. In that mode, `gog` asks for a
  passphrase to save or read OAuth refresh tokens. Choose a memorable passphrase
  and keep it stable; the same value must be used in future shells, services,
  and agent sessions via `GOG_KEYRING_PASSWORD`.

Examples of local-only passphrase ideas:

```text
ai_assistant
ai_assistant_tools
personal_gog_keyring
```

Do not paste the passphrase into chats or logs. Type it directly into the local
terminal prompt, or export it only in a private shell/session:

```bash
export GOG_KEYRING_PASSWORD='ai_assistant'
```

If the passphrase is forgotten, back up the old keyring directory before
creating a fresh one. Old tokens encrypted with the forgotten passphrase will not
be readable.

To try the system keyring on Linux after approving the desktop prompt:

```bash
gog auth keyring auto
gog auth doctor --check
```

If `auto` cannot open the desktop keyring, switch back to file storage:

```bash
gog auth keyring file
export GOG_KEYRING_PASSWORD='ai_assistant'
```

If the browser has multiple Google accounts, force account choice by adding
`prompt=select_account` or using an incognito/private window. If the OAuth app
is still in Testing, the Gmail account must be listed as a test user or Google
will block authorization with `403 access_denied`.

The default service set covers mail, files, documents, spreadsheets, presentations, forms/quizzes, calendar, and tasks. Add optional services such as `contacts`, `people`, `classroom`, or `appscript` only when needed.

For read-only Gmail workflows, keep auth narrow if preferred:

```bash
gog auth add you@gmail.com --services gmail --readonly --gmail-scope readonly
```

If the OAuth app is External + Testing, Google refresh tokens for user-data scopes can expire after 7 days. Publish the personal OAuth app for long-lived refresh tokens.

## Tests

```bash
gog --version
gog auth list
gog auth doctor --check
gog --account you@gmail.com --gmail-no-send gmail search "newer_than:2d" --max 10 --json
gog --account you@gmail.com --gmail-no-send gmail thread get THREAD_ID --sanitize-content --json
gog --account you@gmail.com drive inventory --max 20 --json
gog --account you@gmail.com docs raw DOCUMENT_ID --pretty
gog --account you@gmail.com sheets get SPREADSHEET_ID "Sheet1!A1:D20" --json
```
