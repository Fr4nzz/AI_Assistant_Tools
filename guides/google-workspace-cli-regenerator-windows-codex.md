# Google Workspace / Gmail Setup For Codex Desktop

Install the Codex skill and `gws` shim:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool google-workspace
```

The installer downloads:

- `tools/google-workspace/skill/`

## Why This Uses Google Cloud OAuth

Gmail does not expose a convenient reusable browser token for this workflow. The reliable route is to create a Google Cloud project, enable APIs, create a Desktop OAuth client, download the OAuth client JSON, and run `gws auth login`.

## Install gws

```powershell
npm install -g @googleworkspace/cli
gws.cmd --version
```

## Google Cloud Setup

1. Create/select a project: https://console.cloud.google.com/projectcreate
2. Enable APIs:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Docs API
   - Google Sheets API
   - Google Slides API
   - Google Forms API, if needed
3. Configure OAuth consent:
   - User type: External
   - Add your Gmail account as a test user
4. Create an OAuth client:
   - Application type: Desktop app
5. Download `client_secret_*.json` to:

```text
%USERPROFILE%\.config\gws\client_secret.json
```

## Login

Read/write productivity setup while keeping Gmail read-only:

```powershell
$scopes = 'https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/forms.body,https://www.googleapis.com/auth/forms.responses.readonly,openid,email,profile'
gws.cmd auth login --scopes $scopes
```

## Recommended gws Skills

Keep the custom `google-workspace` skill installed for account routing. Optional upstream skills:

```powershell
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo googleworkspace/cli --path skills/gws-shared skills/gws-gmail skills/gws-drive skills/gws-docs
```

## Test

```powershell
gws.cmd auth status
gws.cmd gmail users messages list --params '{"userId":"me","maxResults":5}'
gws.cmd drive files list --params '{"pageSize":5}'
```

