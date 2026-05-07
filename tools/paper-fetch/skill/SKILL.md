---
name: paper-fetch
description: Search, download, and read academic papers from open repositories, public academic APIs, Unpaywall, and optional academic mirrors. Use when the user asks to find, search for, download, or read a paper, PDF, article, DOI, or reference.
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
    bins: ["paper-search"]
---

# Paper Fetch Skill

This skill uses the `paper-search` CLI from
`Fr4nzz/paper-search-mcp`, a fork of `openags/paper-search-mcp` with DOI
fallback downloads, Unpaywall-first DOI resolution, source timeouts, PDF
validation, and dynamic Sci-Hub mirror discovery.

## Setup

Install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) paper-fetch
```

The installer creates:

- `paper-search` on PATH
- `~/.ai-assistant-tools/paper-search-mcp/.env`

Recommend setting an Unpaywall contact email after installation. It is optional
for search and some fallbacks, but it enables the fastest and cleanest DOI PDF
path.

```bash
sed -i 's/^PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=.*/PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=your@email.com/' ~/.ai-assistant-tools/paper-search-mcp/.env
```

Optional API keys in the same `.env`:

- `PAPER_SEARCH_MCP_CORE_API_KEY`
- `PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY`
- `PAPER_SEARCH_MCP_GOOGLE_SCHOLAR_PROXY_URL`

## Commands

### Search

```bash
paper-search search "quantum entanglement" -n 5 -s openalex,crossref,arxiv,semantic --source-timeout 20
```

Use targeted sources for speed. Broad `-s all` can be useful, but some providers
are slow or rate-limited.

Common sources:

```text
arxiv,pubmed,biorxiv,medrxiv,google_scholar,iacr,semantic,crossref,openalex,pmc,core,europepmc,dblp,openaire,citeseerx,doaj,base,zenodo,hal,ssrn,unpaywall
```

### Download By DOI

Prefer this when the user provides a DOI:

```bash
paper-search download-doi 10.1038/s41593-020-0658-y -o ~/Downloads/papers
```

For open-access-only behavior:

```bash
paper-search download-doi 10.1038/s41593-020-0658-y -o ~/Downloads/papers --no-scihub
```

Download pipeline:

1. Source-native download
2. Unpaywall DOI resolution
3. Open repositories such as OpenAIRE, CORE, Europe PMC, and PMC
4. Optional Sci-Hub fallback with discovered/cached working mirrors

### Download From A Specific Source

Use this when search returns a source-specific `paper_id`:

```bash
paper-search download arxiv 2106.12345 -o ~/Downloads/papers
paper-search download semantic DOI:10.1038/s41593-020-0658-y -o ~/Downloads/papers
```

### Read / Extract Text

```bash
paper-search read arxiv 2106.12345 -o ~/Downloads/papers
```

## Workflow For Agents

1. If the user gives a DOI and wants the PDF, run `paper-search download-doi <doi> -o ~/Downloads/papers`.
2. If the user asks to find papers by topic/title, run `paper-search search "<query>" -n 5 -s openalex,crossref,arxiv,semantic --source-timeout 20`.
3. Present the best results with title, year, source, DOI, and PDF availability.
4. Download the selected paper with `download-doi` when a DOI exists; otherwise use `download <source> <paper_id>`.
5. Always report the saved path and whether the source was Unpaywall/OA, repository, source-native, or mirror fallback when available.

## Notes

- Unpaywall email is recommended because DOI downloads are usually faster than repository/mirror fallbacks.
- Google Scholar may return no results or time out because of bot detection; use targeted public sources first.
- Optional mirror fallback is user responsibility. The tool tries open/source-native and Unpaywall paths before mirrors.
