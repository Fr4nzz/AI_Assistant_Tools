# TubeScrape

Fast YouTube channel inventory, transcript, subtitle, and search tooling for
Codex Desktop through
[`zaidkx37/tubescrape`](https://github.com/zaidkx37/tubescrape).

This installs the `tubescrape` CLI and the Codex `tubescrape` skill.

## What It Does

- Lists YouTube channel videos quickly, including view counts, video IDs,
  titles, durations, publish dates, and URLs.
- Exports channel inventories as JSON for local sorting by popularity.
- Downloads transcripts as text, JSON, SRT, or VTT.
- Searches YouTube with filters and sort options such as upload date, rating,
  relevance, and view count.

Use TubeScrape when the user needs fast channel inventory, popularity ranking,
or native subtitle files. Keep YTFetcher available for comment fetching,
transcript caching, and transcript-first JSON/CSV/TXT dataset exports.

## Linux / CachyOS

Install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) tubescrape
```

The Linux installer installs TubeScrape into
`~/.ai-assistant-tools/tubescrape-venv` and creates a
`~/.local/bin/tubescrape` shim.

TubeScrape requires Python 3.10, 3.11, 3.12, or 3.13. If needed, set
`TUBESCRAPE_PYTHON` before running the installer:

```bash
TUBESCRAPE_PYTHON=python3.13 bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) tubescrape
```

## Windows

Install:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool tubescrape
```

The Windows installer installs TubeScrape into
`~\.ai-assistant-tools\tubescrape-venv` and creates a
`~\.local\bin\tubescrape.cmd` shim.

TubeScrape requires Python 3.10, 3.11, 3.12, or 3.13. If needed, set
`TUBESCRAPE_PYTHON` to a compatible `python.exe` before running the installer.

## Basic Use

```bash
tubescrape --help
tubescrape channel --help
tubescrape transcript --help
tubescrape search --help
```

Fetch recent channel videos:

```bash
tubescrape channel -n 20 --json @nicknorwitzMDPhD
```

Fetch the full channel inventory, then sort locally by parsed numeric views:

```bash
tubescrape channel -n 0 --json @nicknorwitzMDPhD > nicknorwitz.json
```

Download subtitles/transcripts:

```bash
tubescrape transcript VIDEO_ID --format srt --save video.srt
tubescrape transcript VIDEO_ID --format vtt --save video.vtt
tubescrape transcript VIDEO_ID --format json --save transcript.json
tubescrape transcript VIDEO_ID --list-languages
```

Search YouTube by popularity:

```bash
tubescrape search "keto carnivore interview" --sort-by view_count --json
```

Use an HTTP proxy by placing `--proxy` before the subcommand:

```bash
tubescrape --proxy http://127.0.0.1:8080 channel -n 20 --json @nicknorwitzMDPhD
tubescrape --proxy http://user:pass@proxy.example.com:8080 search "keto carnivore" --json
tubescrape --proxy http://127.0.0.1:8080 transcript VIDEO_ID --format srt --save video.srt
```

Proxy use is mainly for approved alternate networks when YouTube rate-limits or
temporarily blocks the current IP. Keep scraping bounded and avoid public proxy
lists.

## Updating

Linux:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) tubescrape
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool tubescrape
```
