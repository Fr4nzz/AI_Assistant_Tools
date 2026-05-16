# HyperFrames

HyperFrames is a Codex plugin for building and rendering videos from HTML
compositions through [`npx hyperframes`](https://hyperframes.heygen.com).
It includes skills for composition authoring, the CLI, registry blocks, GSAP,
captions, TTS, transcription, and website-to-video capture.

This tool entry enables the official `hyperframes@openai-curated` Codex plugin
and installs a small helper skill that reminds agents how to install/use it.

## Recommended Install

In Codex Desktop, open Plugins, search for `HyperFrames`, and install it.

## Agent-Assisted Install

Linux / CachyOS:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) hyperframes
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool hyperframes
```

Then restart Codex Desktop. If the official marketplace cache is unavailable on
that machine, finish installation from the Codex Desktop Plugins UI.

The portable config entry is:

```toml
[plugins."hyperframes@openai-curated"]
enabled = true
```

## Runtime Dependencies

The plugin skills generally call `npx hyperframes`, so the machine should have:

- Node.js 22+
- npm/npx
- FFmpeg
- Chromium/browser dependencies for preview/render workflows

## Basic Agent Workflow

1. Use the HyperFrames plugin skills for video composition work.
2. Scaffold or inspect with `npx hyperframes init`, `lint`, `inspect`,
   `preview`, and `render`.
3. For narration, use `npx hyperframes tts`; for captions, use
   `npx hyperframes transcribe` or script-aligned caption timing when the script
   is known.
4. Always lint, inspect, and create contact sheets after meaningful
   visual/timing changes.
