---
name: paper-fetch
description: Download academic papers from open repositories and academic mirrors after candidate papers are known. Use primarily when the user asks to download a paper/PDF/DOI/URL or check OA PDF availability.
triggers:
  - paper
  - download paper
  - find paper
  - search paper
  - doi
  - pdf
  - article
  - reference
  - academic
argument-hint: "<query|doi|url>"
metadata:
  requires:
    bins: ["paper-dl"]
---

# Paper Fetch Skill

Download academic papers with Open Access lookup, automatic mirror discovery,
and fallback sources. Normal web research is usually better for discovering and
ranking the best papers on a topic; use `paper-dl` mainly to retrieve PDFs or
check DOI/OA metadata once good candidates have been identified.

## Setup (First Time)

Before using this skill, ensure it is installed:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) paper-fetch
```

Search and mirror fallback download work without configuration, but agents
should recommend configuring an Unpaywall contact email after installation.
Unpaywall is usually faster and cleaner than mirror or archive fallbacks for DOI
downloads:

```bash
paper-dl set-key unpaywall-email your@email.com
paper-dl set-key mailto your@email.com
```

### Optional: Get an OpenAlex API Key (Recommended)

1. Go to https://openalex.org/settings/api-key
2. Create an account or sign in
3. Copy the API key
4. Run:
   ```bash
   paper-dl set-key openalex PASTE_KEY_HERE
   ```

This improves search rate limits and is free.

## Commands

### Search for papers
```bash
paper-dl search "quantum entanglement" -n 5
paper-dl --json search "quantum entanglement" -n 5
```

Searches across OpenAlex, Semantic Scholar, Crossref, arXiv, bioRxiv, and Google Scholar in parallel. Returns title, authors, year, DOI, and PDF URL (if available).

### Download a paper
```bash
paper-dl download 10.1038/nature12373
paper-dl download https://doi.org/10.1038/nature12373
```

Download pipeline (fully automatic, agent never specifies source):
1. Extract/normalize DOI
2. Try Open Access download via Unpaywall (fast path, requires email)
3. Try academic mirrors with auto-discovery (fallback, no email needed)
4. Try Anna's Archive fallback
5. Fallback to direct PDF from search APIs

### Lookup DOI metadata
```bash
paper-dl lookup 10.1038/nature12373
```

Returns title, OA status, and PDF URL from Unpaywall. This command requires
`unpaywall-email`; search and mirror fallback downloads can still work without
it.

### List working mirrors
```bash
paper-dl mirrors
paper-dl mirrors --refresh
```

Mirrors are auto-discovered from multiple sources, health-probed in parallel,
sorted by latency, and cached for 6 hours. Use `--refresh` if downloads are
falling through slow or dead mirrors.

### Set API keys interactively
```bash
paper-dl set-key openalex YOUR_KEY
paper-dl set-key semantic YOUR_KEY
paper-dl set-key core YOUR_KEY
paper-dl set-key unpaywall-email your@email.com
```

This writes keys to `.env` so the skill remembers them.

## JSON Output

Add `--json` to any command for machine-readable output:
```bash
paper-dl search "CRISPR" --json
```

## Configuration

Environment variables (loaded from `.env` in skill directory):

| Variable | Setup | Description |
|----------|-------|-------------|
| `PAPER_FETCH_UNPAYWALL_EMAIL` | Recommended | Any valid email for faster Unpaywall DOI lookup/download |
| `PAPER_FETCH_OPENALEX_API_KEY` | No | Improves rate limits (free at openalex.org) |
| `PAPER_FETCH_SEMANTIC_API_KEY` | No | Improves rate limits (free at semanticscholar.org) |
| `PAPER_FETCH_CORE_API_KEY` | No | Improves rate limits (free at core.ac.uk) |
| `PAPER_FETCH_PREFERRED_MIRROR` | No | Add this mirror at the front of the discovery candidates |
| `PAPER_FETCH_MIRRORS` | No | Comma-separated mirror override list |
| `PAPER_FETCH_DOWNLOAD_DIR` | No | Download directory (default: ~/Downloads/papers) |
| `PAPER_FETCH_MIRROR_DISCOVERY_TIMEOUT` | No | Seconds per mirror-list source (default: 5) |
| `PAPER_FETCH_MIRROR_PROBE_TIMEOUT` | No | Seconds per mirror health probe (default: 4) |
| `PAPER_FETCH_MIRROR_PROBE_WORKERS` | No | Parallel mirror probes (default: 8) |

## Workflow for the Agent

When the user asks for papers:

1. **If they ask for the best/relevant papers on a topic**: Use normal web
   research first to identify and rank candidates. Prefer publisher pages,
   arXiv, conference pages, dataset pages, PubMed, institutional repositories,
   and other authoritative sources.
2. **If they have a DOI or URL**: Run `paper-dl download <identifier>` directly.
3. **If they have a title but no DOI/URL**: Use normal search to resolve the
   DOI or canonical page first, then run `paper-dl download`.
4. **If normal search is unavailable or a quick metadata pass is enough**: Use
   `paper-dl search "<query>"`, but treat results as candidates, not as the
   final ranking.
5. **Always report the source**: Tell the user whether it was downloaded via
   Open Access, mirror, archive, or direct PDF.
6. **If download fails**: Report which sources were tried and suggest a
   different DOI/URL or manual access through the publisher/library.

## Notes

- For very recent papers (2022+), Open Access sources are more reliable.
- The skill does not require any paid API keys to function.
- Downloads are saved to `~/Downloads/papers/` by default.
- The agent using this skill does not need to know the underlying download mechanism — the abstraction is fully transparent.
