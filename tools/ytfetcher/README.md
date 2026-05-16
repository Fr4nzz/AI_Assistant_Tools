# YTFetcher

YouTube transcript and metadata fetching for Codex Desktop through
[`kaya70875/ytfetcher`](https://github.com/kaya70875/ytfetcher).

This installs the `ytfetcher` CLI and the Codex `ytfetcher` skill.

## What It Does

- Fetches transcript/subtitle text from YouTube channels, playlists, video IDs,
  and search results.
- Fetches metadata such as title, description, thumbnails, publish date,
  duration, and view count.
- Exports JSON, CSV, or TXT for AI, NLP, RAG, and research workflows.
- Can fetch comments when explicitly requested.

It is not primarily a native subtitle-file downloader. If you need `.srt` or
`.vtt` files, use TubeScrape for that specific job when it is installed.

## Linux / CachyOS

Install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) ytfetcher
```

The Linux installer installs `ytfetcher` into `~/.ai-assistant-tools/ytfetcher-venv`
and creates a `~/.local/bin/ytfetcher` shim.

YTFetcher requires Python 3.11, 3.12, or 3.13. If your default `python` is too
new or too old, set `YTFETCHER_PYTHON` before running the installer:

```bash
YTFETCHER_PYTHON=python3.13 bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) ytfetcher
```

## Windows

Install:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool ytfetcher
```

The Windows installer installs `ytfetcher` into
`~\.ai-assistant-tools\ytfetcher-venv` and creates a
`~\.local\bin\ytfetcher.cmd` shim.

YTFetcher requires Python 3.11, 3.12, or 3.13. If needed, set
`YTFETCHER_PYTHON` to a compatible `python.exe` before running the installer.

## Basic Use

```bash
ytfetcher --help
ytfetcher channel TheOffice -m 50 -f json
ytfetcher channel TheOffice -m 50 -f csv --metadata title description
ytfetcher channel TheOffice --all -f json -o ./exports --filename office_videos
ytfetcher playlist PLAYLIST_ID -m 25 -f json
ytfetcher video VIDEO_ID_1 VIDEO_ID_2 -f json
ytfetcher search "keto carnivore interview" -m 25 -f json
```

For full descriptions, use `video` mode on shortlisted video IDs:

```bash
ytfetcher video VIDEO_ID_1 VIDEO_ID_2 -f json --metadata title description url duration view_count
```

Choose transcript languages:

```bash
ytfetcher channel TheOffice -m 50 -f json --languages en es
```

Fetch only manually created transcripts:

```bash
ytfetcher channel TEDx -m 50 -f json --manually-created
```

Popularity filtering:

```bash
ytfetcher channel TheOffice -m 50 -f json --min-views 100000
```

`--min-views` filters the videos YTFetcher is already inspecting; it does not
sort the whole channel by popularity. Old high-view videos can be missed if
they are outside the `-m` window. Use TubeScrape for fast whole-channel
inventory and local sorting by parsed view count, then run
`ytfetcher video <VIDEO_ID...>` only if you need YTFetcher-specific exports,
comments, or cache behavior.

Download native subtitle files with TubeScrape:

```bash
tubescrape transcript VIDEO_ID --format vtt --save video.vtt
tubescrape transcript VIDEO_ID --format srt --save video.srt
```

Cache controls:

```bash
ytfetcher channel TheOffice -m 20 --no-cache -f json
ytfetcher channel TheOffice -m 20 --cache-path ./my_cache --cache-ttl 3 -f json
ytfetcher cache --clean
```

## Updating

Linux:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) ytfetcher
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool ytfetcher
```
