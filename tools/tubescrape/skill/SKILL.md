---
name: tubescrape
description: Use this skill whenever the user asks to inspect YouTube channels quickly, sort channel videos by popularity, download YouTube transcripts as SRT/VTT/JSON/text, or search YouTube with filters through the local `tubescrape` CLI.
triggers:
  - youtube channel popularity
  - youtube subtitles
  - youtube transcripts
  - youtube channel inventory
  - tubescrape
metadata:
  requires:
    bins: ["tubescrape"]
---

# TubeScrape

Use the local `tubescrape` CLI when the user needs fast YouTube channel
inventory, popularity ranking, subtitle files, transcript downloads, or YouTube
search.

TubeScrape is the preferred tool for:

- Getting a channel inventory with view counts.
- Sorting a channel's videos by popularity.
- Downloading native-ish transcript/subtitle files as `.srt` or `.vtt`.
- YouTube search with basic sort/filter options.

Keep `ytfetcher` in mind when the user needs comment fetching, transcript
caching, or transcript-first JSON/CSV/TXT datasets. YTFetcher has useful
dataset-building features that TubeScrape does not replace.

## Setup

Install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) tubescrape
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool tubescrape
```

## Commands

Use command discovery first when uncertain:

```bash
tubescrape --help
tubescrape channel --help
tubescrape transcript --help
tubescrape search --help
```

Fetch recent channel videos:

```bash
tubescrape channel -n 20 --json @nicknorwitzMDPhD
tubescrape channel -n 20 --json https://www.youtube.com/@nicknorwitzMDPhD
```

Fetch the whole channel inventory:

```bash
tubescrape channel -n 0 --json @nicknorwitzMDPhD
```

For popularity tasks, prefer TubeScrape over ytfetcher. TubeScrape channel
output includes view counts in listing results, so it can inventory a channel
quickly and sort locally. Parse strings such as `"733,599 views"` into integers
before sorting.

Download transcripts/subtitles:

```bash
tubescrape transcript VIDEO_ID --format text
tubescrape transcript VIDEO_ID --format srt --save transcript.srt
tubescrape transcript VIDEO_ID --format vtt --save transcript.vtt
tubescrape transcript VIDEO_ID --list-languages
```

Search YouTube:

```bash
tubescrape search "keto carnivore interview" --json
tubescrape search "keto carnivore interview" --sort-by view_count --json
tubescrape search "keto carnivore interview" --upload-date month --duration long --json
```

## Workflow For Agents

1. Use `tubescrape` first for channel video listings, view counts, popularity
   sorting, and direct `.srt` or `.vtt` transcript files.
2. Put channel options before the channel argument for the current CLI, for
   example `tubescrape channel -n 20 --json @handle`.
3. For full-channel popularity, run `tubescrape channel -n 0 --json <channel>`
   and sort the returned videos locally by parsed numeric `view_count`.
4. For recent-only tasks, keep `-n` bounded, such as `-n 10` or `-n 20`.
5. Use JSON for agent processing unless the user asks for text, SRT, VTT, or
   another format.
6. Use `tubescrape transcript --list-languages` when transcript language
   availability matters.
7. Use `ytfetcher` instead when comments, cache controls, or transcript-first
   dataset exports are the main task.

## Notes

- YouTube can change internal endpoints and may rate-limit scraping. Start
  bounded when testing a new channel.
- Channel `view_count` values are human-readable strings. Parse them before
  numerical comparisons.
- Search sorting uses YouTube search semantics; channel popularity ranking
  should come from channel inventory plus local sorting.
- TubeScrape also has SDK/API/playlist/channel-shorts features in its upstream
  guide. Prefer `tubescrape --help` before mentioning those, and do not default
  to them for ordinary agent workflows.
- Respect YouTube's terms and the rights of video creators.
