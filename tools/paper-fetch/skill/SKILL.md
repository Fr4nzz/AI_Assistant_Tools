---
name: paper-fetch
description: Download/read known academic paper PDFs and enrich known DOI batches using DOI, arXiv ID, source-specific paper ID, or direct paper URL. Use after papers have already been identified; for broad paper discovery or literature search, prefer normal web/search tools first.
triggers:
  - download paper
  - doi
  - pdf
  - paper url
  - arxiv id
  - read paper
argument-hint: "<query|doi|url>"
metadata:
  requires:
    bins: ["paper-search"]
---

# Paper Fetch Skill

This skill uses the `paper-search` CLI from `Fr4nzz/paper-search-mcp`, a fork
of `openags/paper-search-mcp` with DOI fallback downloads, Unpaywall-first DOI
resolution, PDF validation, and dynamic Sci-Hub mirror discovery.

Use this skill primarily for PDF retrieval, text extraction, and DOI metadata
enrichment once target papers are known. For broad discovery, recommendations,
or literature search, use normal web/search tools first because they are usually
better at ranking, current coverage, and disambiguation than
`paper-search search`.

## Setup

Install:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) paper-fetch
```

The installer creates:

- `paper-search` on PATH
- `~/.ai-assistant-tools/paper-search-mcp/.env`

Recommend setting an Unpaywall contact email after installation. It is optional
for some fallbacks, but it enables the fastest and cleanest DOI PDF path.

```bash
sed -i 's/^PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=.*/PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=your@email.com/' ~/.ai-assistant-tools/paper-search-mcp/.env
```

Optional API keys in the same `.env`:

- `PAPER_SEARCH_MCP_CORE_API_KEY`
- `PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY`
- `PAPER_SEARCH_MCP_GOOGLE_SCHOLAR_PROXY_URL`

## Commands

### Enrich DOI Metadata In Batch

Use this after native/Parallel/web discovery finds candidate DOIs and you need a
ranking table:

```bash
paper-search metadata-dois 10.1038/s41593-020-0658-y 10.1111/ecog.03049 -o ~/Downloads/papers/metadata.json
paper-search metadata-dois --input dois.txt --output ~/Downloads/papers/metadata.json
```

The command queries Crossref, OpenAlex, and Unpaywall in parallel. If
`PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY` is configured, Semantic Scholar is
included automatically. Output includes merged title, authors, year, DOI,
abstract when available, citation count, OA/PDF URL, source coverage, and raw
per-source records. Ranking fields include `rank_score`, `rank_components`,
`rank_reasons`, and `oa_pdf_sources`. PDF availability in the ranking uses all
fast OA metadata sources checked for that DOI, not only OpenAlex; mirror probing
is reserved for `download-doi`.

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
2. If the user asks to find papers by topic/title, use normal web/search tools first to identify the paper and DOI. Do not use `paper-search search` as the default discovery method.
3. If normal/Parallel search returns multiple DOIs, use `metadata-dois` to enrich and rank them before deciding what to read or download.
4. If normal search returns one DOI and the user wants the PDF, use `download-doi`; if it returns only a source-specific ID, use `download <source> <paper_id>`.
5. Use `paper-search search` only as a supplementary/last-resort metadata lookup when normal search is unavailable or the user explicitly asks to use this CLI.
6. Always report the saved path and whether the source was Unpaywall/OA, repository, source-native, or mirror fallback when available.

## Notes

- Unpaywall email is recommended because DOI downloads are usually faster than repository/mirror fallbacks.
- `paper-search search` is not the preferred broad discovery tool, but when used it returns compact records without abstracts by default. Add `--include-abstracts` only for shortlisted papers.
- Optional mirror fallback is user responsibility. The tool tries open/source-native and Unpaywall paths before mirrors.
