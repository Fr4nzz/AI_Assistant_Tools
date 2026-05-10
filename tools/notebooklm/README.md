# NotebookLM

NotebookLM access for Codex Desktop through
[`teng-lin/notebooklm-py`](https://github.com/teng-lin/notebooklm-py).

This installs the `notebooklm` CLI and the Codex `notebooklm` skill.

## Linux / CachyOS

Install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) notebooklm
```

The Linux installer prefers `uv tool install --upgrade "notebooklm-py[browser]"`
when `uv` is available. If `uv` is missing, it installs into the shared
AI_Assistant_Tools Python venv and creates a `~/.local/bin/notebooklm` shim.

## Windows

Install:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool notebooklm
```

The Windows installer uses `python -m pip install --user --upgrade
"notebooklm-py[browser]"` and installs the Codex skill.

## Login

Run login only when you are ready for the browser authentication flow:

```bash
notebooklm login
```

Check auth:

```bash
notebooklm auth check --test
notebooklm profile list
```

## Basic Use

```bash
notebooklm list
notebooklm create "My Research"
notebooklm use NOTEBOOK_ID
notebooklm source add "https://example.com/article"
notebooklm source add "./paper.pdf"
notebooklm ask "What are the key themes?"
notebooklm generate audio "make it engaging" --wait
notebooklm download audio ./podcast.mp3
```

For long audio generation, it is often better to start generation, poll the
artifact, then download it:

```bash
notebooklm generate audio "long study summary" --format deep-dive --length long --language en --no-wait --json
notebooklm artifact list --notebook NOTEBOOK_ID --json
notebooklm artifact wait ARTIFACT_ID --notebook NOTEBOOK_ID
notebooklm download audio ~/Downloads/summary.mp3 --notebook NOTEBOOK_ID --artifact ARTIFACT_ID
```

## Updating

Do not update before every task. If commands that used to work start failing
and auth/profile/network checks do not explain it, update the tool.

Linux with `uv`:

```bash
uv tool upgrade notebooklm-py
```

Or rerun the installer:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) notebooklm
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool notebooklm
```

After updating:

```bash
notebooklm --version
notebooklm auth check --test
```
