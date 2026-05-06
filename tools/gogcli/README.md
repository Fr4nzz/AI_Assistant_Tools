# gogcli for Google Workspace

`gog` is the preferred Google CLI for Codex agents because it has compact JSON output, sanitized Gmail message/thread reads, account selection, command guards, and broad support for Gmail, Calendar, Drive, Docs, Sheets, Slides, Forms, Apps Script, Contacts, Tasks, People, and Classroom.

Use `gog` for Google Workspace summaries, triage, context gathering, uploads, and editing. Avoid the Codex Google Drive/Gmail plugins unless the user explicitly asks for those connectors because they may be authenticated to a different account.

## Install

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool gogcli
```

The installer downloads the latest Windows amd64 release from `openclaw/gogcli`, extracts `gog.exe`, and copies it directly to:

```text
%USERPROFILE%\.local\bin\gog.exe
```

That follows the upstream Windows recommendation: put the directory containing `gog.exe` on PATH. No `gog.cmd` shim is used.

## OAuth

Create a Google Cloud project, enable the APIs you need, create a Desktop OAuth client, then store that client JSON in `gog`.

```powershell
gog auth credentials set "$HOME\Downloads\client_secret_....json"
gog auth add you@gmail.com --services gmail,calendar,drive,docs,sheets,slides,forms,tasks
```

The default service set covers mail, files, documents, spreadsheets, presentations, forms/quizzes, calendar, and tasks. Add optional services such as `contacts`, `people`, `classroom`, or `appscript` only when needed.

For read-only Gmail workflows, keep auth narrow if preferred:

```powershell
gog auth add you@gmail.com --services gmail --readonly --gmail-scope readonly
```

If the OAuth app is External + Testing, Google refresh tokens for user-data scopes can expire after 7 days. Publish the personal OAuth app for long-lived refresh tokens.

## Tests

```powershell
gog --version
gog auth list
gog auth doctor --check
gog --account you@gmail.com --gmail-no-send gmail search "newer_than:2d" --max 10 --json
gog --account you@gmail.com --gmail-no-send gmail thread get THREAD_ID --sanitize-content --json
gog --account you@gmail.com drive inventory --max 20 --json
gog --account you@gmail.com docs raw DOCUMENT_ID --pretty
gog --account you@gmail.com sheets get SPREADSHEET_ID "Sheet1!A1:D20" --json
```
