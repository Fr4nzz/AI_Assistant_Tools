# D2L / Brightspace CLI

Read-only D2L/Brightspace access for Codex Desktop: courses, assignments, deadlines, announcements, grades, content, unread items, feedback, and course file downloads.

This tool was built for an institutional login where a simple API token was not the reliable path. It uses browser-backed authentication and authenticated D2L cookies from a headed/headless Chromium profile. It is read-only and should not submit assignments or modify course content.

## Files

- `bin/d2l.py` - CLI implementation.
- `bin/d2l.cmd` - Windows launcher.
- `skill/` - global Codex skill files.

## Install

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool d2l
```

Then run:

```powershell
d2l login
d2l classes
d2l deadlines
```

