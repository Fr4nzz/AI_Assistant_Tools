# gogcli for Gmail

`gog` is the preferred Gmail search/read CLI for Codex agents because it has compact JSON search results, sanitized message/thread reads, account selection, and `--gmail-no-send`.

Use `gws` for broader Google Workspace editing. Use `gog` for Gmail summaries, triage, and context gathering.

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

Use the same Google Cloud Desktop OAuth client JSON created for Google Workspace setup.

```powershell
gog auth credentials set "$HOME\Downloads\client_secret_....json"
gog auth add you@gmail.com --services gmail --readonly --gmail-scope readonly
```

For Gmail read-only workflows, keep auth narrow. Add other services only if you deliberately want to test them through `gog`.

## Tests

```powershell
gog --version
gog auth list
gog --account you@gmail.com --gmail-no-send gmail search "newer_than:2d" --max 10 --json
gog --account you@gmail.com --gmail-no-send gmail thread get THREAD_ID --sanitize-content --json
```
