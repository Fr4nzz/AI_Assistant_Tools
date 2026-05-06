# D2L / Brightspace CLI Setup For Codex Desktop

Install:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool d2l
```

The installer downloads:

- `tools/d2l/bin/d2l.py`
- `tools/d2l/bin/d2l.cmd`
- `tools/d2l/skill/`

## Why This Exists

D2L/Brightspace access uses browser-backed institutional login because a simple API-token setup was not reliable in this environment. The CLI is read-only and should not submit assignments, edit content, send messages, or change grades.

## Login

```powershell
d2l login
```

## Test

```powershell
d2l classes
d2l deadlines
d2l assignments
```

