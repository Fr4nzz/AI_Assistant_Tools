---
name: ytfetcher
description: Use this skill whenever the user asks to fetch YouTube channel, playlist, search, or video transcript text plus metadata such as titles, descriptions, publish dates, thumbnails, views, comments, or JSON/CSV/TXT datasets through the local `ytfetcher` CLI.
triggers:
  - youtube transcripts
  - youtube channel metadata
  - youtube subtitles
  - youtube dataset
  - ytfetcher
metadata:
  requires:
    bins: ["ytfetcher"]
---

# YTFetcher

Use the local `ytfetcher` CLI for YouTube transcript and metadata dataset
work. It is best for agent-readable exports from channels, playlists, video
IDs, and YouTube search results.

`ytfetcher` fetches transcript/subtitle text with timestamps. It does not focus
on downloading native subtitle files such as `.srt` or `.vtt`; use TubeScrape
for that specific file-download workflow when it is installed.

## Setup

Install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) ytfetcher
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool ytfetcher
```

## Commands

Use command discovery first when uncertain:

```bash
ytfetcher --help
ytfetcher channel --help
ytfetcher playlist --help
ytfetcher video --help
ytfetcher search --help
```

Fetch channel transcripts and metadata:

```bash
ytfetcher channel TheOffice -m 50 -f json
ytfetcher channel TheOffice -m 50 -f csv --metadata title description
ytfetcher channel TheOffice -m 20 --tab shorts -f json
ytfetcher channel TheOffice -m 20 --tab streams -f json
ytfetcher channel TheOffice --all -f json
```

Fetch a playlist, video IDs, or search results:

```bash
ytfetcher playlist PLAYLIST_ID -m 25 -f json
ytfetcher video VIDEO_ID_1 VIDEO_ID_2 -f json
ytfetcher search "keto carnivore interview" -m 25 -f json
```

When full video descriptions are required, prefer `video` mode for the
shortlisted video IDs. Channel/listing mode is good for recent video discovery
and transcripts, but it may return compact metadata without full descriptions
for some videos.

Choose transcript languages:

```bash
ytfetcher channel TheOffice -m 50 -f json --languages en es
```

Restrict to manually created transcripts when accuracy matters:

```bash
ytfetcher channel TEDx -m 50 -f json --manually-created
```

Filter before fetching transcripts:

```bash
ytfetcher channel TheOffice -m 50 -f json --min-views 1000
ytfetcher channel TheOffice -m 50 -f json --min-duration 300
ytfetcher channel TheOffice -m 50 -f json --includes-title "episode"
ytfetcher channel TheOffice -m 50 -f json --min-views 1000 --min-duration 300 --includes-title "tutorial"
```

Filters are applied to metadata before transcript fetching. Multiple filters
use AND logic. Treat `--min-views` as a popularity threshold over the videos
YTFetcher is already inspecting, not as a whole-channel popularity sort. For
example, `-m 50 --min-views 100000` checks the first 50 videos from the channel
feed and then keeps videos over 100,000 views. Old high-view videos outside
that listing window can be missed unless you use a larger `-m` or `--all`.

For "most popular videos on this channel" tasks, prefer TubeScrape when it is
installed. TubeScrape channel inventory includes view counts and can be sorted
locally. `ytfetcher --min-views` only filters inspected videos; it does not sort
the whole channel. If TubeScrape is unavailable, collect a bounded candidate
window first, sort by `view_count` where available, then run
`ytfetcher video <VIDEO_ID...>` for transcripts and full descriptions on
selected videos.

Include comments only when needed, because comment fetching can be slower:

```bash
ytfetcher channel TheOffice -m 20 --comments 10 -f json
ytfetcher channel TheOffice -m 20 --comments-only 10 -f json
```

Control export location and filenames:

```bash
ytfetcher channel TheOffice -m 20 -f json -o ./exports --filename office_videos
ytfetcher channel TheOffice -m 20 -f json --stdout
```

If both `--format` and `--stdout` are specified, YTFetcher exports to a file
and prints to the console.

Manage cache:

```bash
ytfetcher channel TheOffice -m 20 --no-cache -f json
ytfetcher channel TheOffice -m 20 --cache-path ./my_cache --cache-ttl 3 -f json
ytfetcher cache --clean
ytfetcher cache --clean --cache-path ./my_cache
```

Use proxies for larger jobs or rate-limit avoidance:

```bash
ytfetcher channel TheOffice -m 100 -f json --http-proxy "http://user:pass@host:port"
ytfetcher channel TheOffice -m 100 -f json --https-proxy "https://user:pass@host:port"
```

## Workflow For Agents

1. Use `ytfetcher` when the user wants YouTube channel/video transcript text,
   titles, descriptions, or structured exports for research, RAG, NLP, or
   review workflows.
2. Prefer JSON for agent processing unless the user asks for CSV or TXT.
3. Keep initial runs small with `-m 5` or `-m 10` when testing a new channel.
4. For full descriptions, first discover recent videos with `channel`, then run
   `video <VIDEO_ID...> --metadata title description url duration view_count`.
5. For popularity tasks, prefer TubeScrape if it is installed. Do not assume
   `--min-views` sorts the whole channel. It only filters videos YTFetcher has
   already inspected.
6. Use `--languages` when the user names a target language.
7. Use `--manually-created` only when the user prioritizes precision over
   coverage.
8. Use comments flags only when comments are part of the task.
9. If the user needs `.srt` or `.vtt` subtitle files, explain that `ytfetcher`
   exports transcript data and use `tubescrape transcript VIDEO_ID --format
   srt|vtt --save <file>` instead when TubeScrape is available.

## Notes

- YouTube may rate-limit transcript scraping. Start small, use caching, and
  retry later if a channel produces transient failures.
- Some videos have no available transcript in the requested language.
- Search results can vary by IP/geographic location. Use `--languages` when
  language matters.
- Respect YouTube's terms and the rights of video creators.
