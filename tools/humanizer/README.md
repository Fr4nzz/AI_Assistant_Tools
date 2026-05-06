# Humanizer

Installs the MIT-licensed `humanizer` Codex skill from the Hermes Agent repo.

Use it when you want Codex to rewrite drafts, docs, emails, PR descriptions,
release notes, resumes, or other prose so the writing sounds more natural and
less formulaic while preserving the original meaning.

Source:

- <https://github.com/NousResearch/hermes-agent/tree/main/skills/creative/humanizer>
- Original project: <https://github.com/blader/humanizer>

## Install

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool humanizer
```

Restart Codex Desktop after installing the skill.

## Test

Start a new Codex chat and ask:

```text
Use the humanizer skill to rewrite this paragraph so it sounds more natural:
[paste text]
```
