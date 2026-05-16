---
name: hyperframes-helper
description: Use when installing, enabling, or explaining the Codex HyperFrames plugin for HTML-to-video composition, rendering, captions, TTS, transcription, GSAP/Tailwind/Three.js animation, or website-to-video workflows.
triggers:
  - hyperframes
  - install hyperframes
  - html video
  - render video
  - video captions
  - tts video
argument-hint: "<setup or video workflow question>"
---

# HyperFrames Helper

HyperFrames is a Codex plugin, not a normal AI_Assistant_Tools CLI. Prefer the
Codex Desktop Plugins UI when possible.

For agent-assisted setup, enable this config entry and restart Codex:

```toml
[plugins."hyperframes@openai-curated"]
enabled = true
```

If the plugin does not appear after restart, open Codex Desktop Plugins, search
for `HyperFrames`, and install it from the official Codex marketplace.

Once installed, use the plugin-provided skills rather than this helper for real
video work:

- `hyperframes` for HTML composition patterns, timing, captions, and visual style.
- `hyperframes-cli` for `npx hyperframes init/lint/inspect/preview/render/tts/transcribe`.
- `hyperframes-registry` for registry blocks/components.
- `gsap` when GSAP animation patterns are used.

Core runtime expectations: Node.js 22+, npm/npx, FFmpeg, and browser/Chromium
support for preview/render.
