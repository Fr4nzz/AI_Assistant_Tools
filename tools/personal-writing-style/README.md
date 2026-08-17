# Personal writing style

Installs the `personal-writing-style` skill for Codex or Hermes Agent.

This skill captures a personal writing voice across manuscripts, reports, emails, documentation, and agent responses. Its core works on its own. Additional references provide scientific-writing guidance, correction-based voice evidence, an anti-slop audit, and a collaborative review workflow.

The repository's `humanizer` remains available as a separate generic skill. When both are active, the explicit preferences in `personal-writing-style` take priority.

## Install

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool personal-writing-style
```

Linux:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) personal-writing-style
```

Restart Codex Desktop or reload the Hermes session after installation.

## Test

Start a new chat and ask:

```text
Use the personal-writing-style skill to revise this text while preserving its meaning:
[paste text]
```
