---
name: paper-fetch
description: Search and download academic papers from open repositories and academic mirrors. Use when the user asks to find, search for, or download a paper, PDF, article, DOI, or reference.
metadata:
  requires:
    bins: ["python3"]
---

# Paper Fetch

Search and download academic papers with automatic mirror discovery.

## Setup (First Time)

Before using this skill, ensure it is installed and configured:

```bash
# Configure the required email
paper-dl set-key unpaywall-email your@email.com
```

### Optional: Get an OpenAlex API Key (Recommended)

1. Go to https://openalex.org/settings/api-key
2. Create an account or sign in
3. Copy the API key
4. Run:
   ```bash
   paper-dl set-key openalex YOUR_KEY_HERE
   ```

This improves search rate limits and is free.

## Commands

### Search for papers
```bash
paper-dl search "quantum entanglement" -n 5
```

Searches across OpenAlex, Semantic Scholar, Crossref, and arXiv. Returns title, authors, year, DOI, and PDF URL (if available).

### Download a paper
```bash
paper-dl download 10.1038/nature12373
paper-dl download https://doi.org/10.1038/nature12373
```

Download pipeline (fully automatic):
1. Extract/normalize DOI
2. Try Open Access download via Unpaywall (fast path)
3. Try academic mirrors with auto-discovery (primary)
4. Fallback to direct PDF from search APIs

### Lookup DOI metadata
```bash
paper-dl lookup 10.1038/nature12373
```

Returns title, OA status, and PDF URL from Unpaywall.

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

## Workflow

When the user asks for a paper:

1. **If they have a DOI or URL**: Run `paper-dl download <identifier>` directly.
2. **If they describe a paper by title/topic**: Run `paper-dl search "<query>"` first, show results, then download the best match.
3. **Always report the source**: Tell the user whether it was downloaded via Open Access or academic mirror.
4. **If download fails**: Report which sources were tried and suggest checking connection or trying a different DOI.

## Notes

- For very recent papers (2022+), Open Access sources are more reliable.
- The skill does not require any paid API keys to function.
- Downloads are saved to `~/Downloads/papers/` by default.
