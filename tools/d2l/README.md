# D2L / Brightspace CLI

Read-only D2L/Brightspace access for Codex Desktop: courses, assignments, deadlines, announcements, grades, content, unread items, feedback, and course file downloads.

This tool was built for an institutional login where a simple API token was not the reliable path. It uses browser-backed authentication and authenticated D2L cookies from a headed/headless Chromium profile. It is read-only and should not submit assignments or modify course content.

## Files

- `bin/d2l.py` - CLI implementation.
- `bin/d2l.cmd` - Windows launcher.
- `skill/` - global Codex skill files.

## Install - Windows

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool d2l
```

## Install - Linux / CachyOS

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) d2l
```

The Linux installer creates a venv under `~/.ai-assistant-tools/venv`, installs
Playwright and `websockets`, copies the CLI to `~/.ai-assistant-tools/d2l`, and
creates the `~/.local/bin/d2l` shim.

## Login and Test

D2L uses the same persistent Chromium profile as Outlook and OneDrive. If you
are installing D2L and Outlook together, open both headed login flows during
initial setup: `d2l login` for Brightspace and `outlook login` for Outlook Web.
They share Microsoft SSO state, but each service may still need its own
first-time web load, cookies, or token bootstrap.

Then run:

```bash
d2l login
d2l classes
d2l deadlines
```

During Microsoft/USFQ sign-in, choose "Mantener mi sesion iniciada" / "Stay
signed in" if prompted. Wait for D2L to load, then close the visible Chromium
window before using headless `d2l` commands.

If Outlook or OneDrive already logged in successfully, D2L may still ask for a
visible login once. That is expected: Microsoft SSO proves the account, but D2L
must also complete the SAML handoff and save Brightspace cookies for the D2L
domain.

A D2L login may reduce or skip parts of the Microsoft account flow for Outlook,
but Outlook may still need to be opened once with `outlook login`. Close visible
Chromium windows before running headless commands, otherwise the shared profile
may be locked.
