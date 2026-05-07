---
name: paper-fetch
description: Search and download academic papers from open repositories and academic mirrors. Use when the user asks to find, search for, or download a paper, PDF, article, DOI, or reference.
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

Search and download academic papers with automatic mirror discovery and Open Access fallback.

## Setup (First Time)

Before using this skill, ensure it is installed:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) paper-fetch
```

Search and mirror fallback download work without configuration. For faster and
more reliable DOI lookup/open-access downloads, configure an Unpaywall contact
email:

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
2. Try academic mirrors with auto-discovery (primary, no email needed)
3. Try Open Access download via Unpaywall (fast path, requires email)
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

Mirrors are auto-discovered from multiple sources, then health-probed and cached for 6 hours.

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

| Variable | Required | Description |
|----------|----------|-------------|
| `PAPER_FETCH_UNPAYWALL_EMAIL` | **Yes** | Any valid email for Unpaywall DOI lookup |
| `PAPER_FETCH_OPENALEX_API_KEY` | No | Improves rate limits (free at openalex.org) |
| `PAPER_FETCH_SEMANTIC_API_KEY` | No | Improves rate limits (free at semanticscholar.org) |
| `PAPER_FETCH_CORE_API_KEY` | No | Improves rate limits (free at core.ac.uk) |
| `PAPER_FETCH_PREFERRED_MIRROR` | No | Try this mirror first (default: https://sci-hub.box) |
| `PAPER_FETCH_DOWNLOAD_DIR` | No | Download directory (default: ~/Downloads/papers) |

## Workflow for the Agent

When the user asks for a paper:

1. **If they have a DOI or URL**: Run `paper_dl.py download <identifier>` directly.
2. **If they describe a paper by title/topic**: Run `paper_dl.py search "<query>"` first, show results, then download the best match.
3. **Always report the source**: Tell the user whether it was downloaded via Open Access or academic mirror.
4. **If download fails**: Report which sources were tried and suggest the user check their connection or try a different DOI.

## Notes

- For very recent papers (2022+), Open Access sources are more reliable.
- The skill does not require any paid API keys to function.
- Downloads are saved to `~/Downloads/papers/` by default.
- The agent using this skill does not need to know the underlying download mechanism — the abstraction is fully transparent.
