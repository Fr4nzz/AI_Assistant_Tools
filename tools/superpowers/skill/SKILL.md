---
name: superpowers-helper
description: Use when installing, enabling, or explaining the Codex Superpowers plugin for planning, brainstorming, verification, or subagent-driven workflows.
triggers:
  - superpowers
  - install superpowers
  - planning plugin
  - subagent workflow
argument-hint: "<setup or workflow question>"
---

# Superpowers Helper

Superpowers is a Codex plugin, not a normal AI_Assistant_Tools CLI. Prefer the
Codex Desktop Plugins UI when possible.

For agent-assisted setup, enable this config entry and restart Codex:

```toml
[plugins."superpowers@openai-curated"]
enabled = true
```

If the plugin does not appear after restart, open the Codex Desktop Plugins UI,
search for `Superpowers`, and install it from the official Codex marketplace.
