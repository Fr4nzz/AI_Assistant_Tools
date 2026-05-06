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
---

# Paper Fetch Skill

Search and download academic papers with automatic mirror discovery and Open Access fallback.

## Setup (First Time)

Before using this skill, ensure it is installed:

```bash
# Linux / macOS — copy skill to Codex skills directory
mkdir -p ~/.codex/skills
cp -r /path/to/repo/skills/paper-fetch ~/.codex/skills/paper-fetch
cd ~/.codex/skills/paper-fetch
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then configure the required email:

```bash
python3 scripts/paper_dl.py set-key unpaywall-email your@email.com
```

### Optional: Get an OpenAlex API Key (Recommended)

1. Go to https://openalex.org/settings/api-key
2. Create an account or sign in
3. Copy the API key
4. Run:
   ```bash
   python3 scripts/paper_dl.py set-key openalex PASTE_KEY_HERE
   ```

This improves search rate limits and is free.

## Commands

### Search for papers
```bash
python3 scripts/paper_dl.py search "quantum entanglement" -n 5
```

Searches across OpenAlex, Semantic Scholar, Crossref, and arXiv. Returns title, authors, year, DOI, and PDF URL (if available).

### Download a paper
```bash
python3 scripts/paper_dl.py download 10.1038/nature12373
python3 scripts/paper_dl.py download https://doi.org/10.1038/nature12373
```

Download pipeline (fully automatic, agent never specifies source):
1. Extract/normalize DOI
2. Try Open Access download via Unpaywall (fast path)
3. Try academic mirrors with auto-discovery (primary)
4. Fallback to direct PDF from search APIs

### Lookup DOI metadata
```bash
python3 scripts/paper_dl.py lookup 10.1038/nature12373
```

Returns title, OA status, and PDF URL from Unpaywall.

### List working mirrors
```bash
python3 scripts/paper_dl.py mirrors
python3 scripts/paper_dl.py mirrors --refresh
```

Mirrors are auto-discovered from multiple sources, then health-probed and cached for 6 hours.

### Set API keys interactively
```bash
python3 scripts/paper_dl.py set-key openalex YOUR_KEY
python3 scripts/paper_dl.py set-key semantic YOUR_KEY
python3 scripts/paper_dl.py set-key core YOUR_KEY
python3 scripts/paper_dl.py set-key unpaywall-email your@email.com
```

This writes keys to `.env` so the skill remembers them.

## JSON Output

Add `--json` to any command for machine-readable output:
```bash
python3 scripts/paper_dl.py search "CRISPR" --json
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
