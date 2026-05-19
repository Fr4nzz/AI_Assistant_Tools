# Paper Fetch

Installs the `paper-search` CLI from
[`Fr4nzz/paper-search-mcp`](https://github.com/Fr4nzz/paper-search-mcp), a fork
of [`openags/paper-search-mcp`](https://github.com/openags/paper-search-mcp).

The install name remains `paper-fetch` for compatibility with existing
AI_Assistant_Tools setup commands. Works with Codex Desktop and Hermes Agent.

## What It Does

- Downloads known PDFs by DOI with source-native, Unpaywall, repository, and optional fallback.
- Enriches batches of known DOIs through Crossref, OpenAlex, Unpaywall, and optional Semantic Scholar.
- Extracts text from source-specific paper downloads when supported.
- Validates PDF downloads to avoid empty or non-PDF files.
- Uses dynamic mirror discovery for comprehensive access.

For broad discovery or literature search, prefer normal web/search tools first.
Use `paper-search` after the target paper is identified, especially when you
have a DOI, arXiv ID, or source-specific paper ID.

For literature-review workflows, use normal search and/or Parallel search for
initial discovery, then pass discovered DOI candidates to `metadata-dois` for a
structured ranking table.

`metadata-dois` checks fast open metadata sources in parallel for each DOI.
PDF availability in its ranking is based on all checked OA sources, exposed as
`oa_pdf_sources`, not only OpenAlex. Mirror probing is intentionally reserved
for `download-doi` so metadata ranking stays fast.

## Install - Windows

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool paper-fetch
```

## Install - Linux / CachyOS

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) paper-fetch
```

Linux installs into `~/.ai-assistant-tools/venv`, creates
`~/.local/bin/paper-search`, and writes configuration to:

```text
~/.ai-assistant-tools/paper-search-mcp/.env
```

## Configuration

Set an Unpaywall email after installation. Search and some fallbacks work
without it, but Unpaywall is usually the fastest and cleanest DOI PDF path.

Linux:

```bash
sed -i 's/^PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=.*/PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=your@email.com/' ~/.ai-assistant-tools/paper-search-mcp/.env
```

Windows:

```powershell
(Get-Content "$HOME\.ai-assistant-tools\paper-search-mcp\.env") -replace '^PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=.*', 'PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=your@email.com' | Set-Content "$HOME\.ai-assistant-tools\paper-search-mcp\.env"
```

Optional keys in the same file:

- `PAPER_SEARCH_MCP_CORE_API_KEY`
- `PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY`
- `PAPER_SEARCH_MCP_GOOGLE_SCHOLAR_PROXY_URL`

## Test

```bash
paper-search sources
paper-search metadata-dois 10.1038/s41593-020-0658-y 10.1111/ecog.03049 -o ~/Downloads/papers/metadata.json
paper-search download-doi 10.1038/s41593-020-0658-y -o ~/Downloads/papers
```

With Unpaywall configured, DOI downloads should normally use the fast
Unpaywall/open-access path when available.
