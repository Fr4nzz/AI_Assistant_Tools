# Superpowers

Superpowers is a Codex plugin, not a local CLI. It gives Codex workflow skills
for brainstorming, planning, subagent-driven development, verification, and
parallel agent coordination.

## Recommended Install

In Codex Desktop, open Plugins, search for `Superpowers`, and install it.

## Agent-Assisted Install

The installers can enable the official Codex plugin config entry:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) superpowers
```

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool superpowers
```

Then restart Codex Desktop. If the official marketplace cache is unavailable on
that machine, finish installation from the Codex Desktop Plugins UI.

The portable config entry is:

```toml
[plugins."superpowers@openai-curated"]
enabled = true
```
