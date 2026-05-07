# Paper Fetch

Download academic papers from open access sources, repositories, and academic
mirrors after the best candidates have been found through normal research.

## What It Does

- **Search** across OpenAlex, Semantic Scholar, Crossref, arXiv, bioRxiv, and Google Scholar in parallel, useful as a fallback or quick first pass
- **Download** papers by DOI or URL with multi-source fallback (OA → mirrors → Anna's Archive → direct PDF)
- **Auto-discover** working academic mirrors with parallel health probes and latency-based ordering
- **Set API keys** interactively via CLI

## Recommended Agent Workflow

For literature discovery, ranking, and "best papers" requests, use normal web
research first. Normal search is better at finding recent papers, benchmark
pages, publisher pages, dataset pages, and field-specific context. Use
`paper-dl search` only as a quick fallback or to supplement metadata.

Use this tool primarily after candidate papers are known:

1. Find and rank papers with normal search.
2. Extract DOI, arXiv URL, publisher URL, or title from the selected papers.
3. Use `paper-dl lookup <doi>` to check open-access metadata when an Unpaywall
   email is configured.
4. Use `paper-dl download <doi-or-url>` to fetch the PDF through Open Access,
   mirrors, archives, or direct PDF links.
5. Report which source was used for the download.

## Files

- `bin/paper-dl.py` - CLI implementation.
- `bin/paper-dl.cmd` - Windows launcher.
- `skill/` - global Codex skill files.

## Install - Windows

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool paper-fetch
```

## Install - Linux / CachyOS

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) paper-fetch
```

The Linux installer creates a venv under `~/.ai-assistant-tools/venv`, installs
dependencies from `requirements.txt`, copies the CLI files to
`~/.ai-assistant-tools/paper-fetch`, and creates the `~/.local/bin/paper-dl` shim.

## Configuration

Search and mirror fallback download work without configuration, but you should
set an Unpaywall contact email after installation. Unpaywall is usually faster
and cleaner than mirror or archive fallbacks for DOI downloads. Optional API
keys improve search rate limits.

```bash
paper-dl set-key unpaywall-email your@email.com
paper-dl set-key openalex YOUR_KEY_HERE
paper-dl set-key semantic YOUR_KEY_HERE
```

Get a free OpenAlex key at https://openalex.org/settings/api-key (30-second signup).

`unpaywall-email` is optional for search and mirror fallback downloads, but
recommended because it enables `paper-dl lookup` and the fastest Unpaywall
open-access download path. Use the user's real contact email; Unpaywall and
Crossref use it for polite API contact/rate-limit identification.

Semantic Scholar may return HTTP 429 without an API key. That does not mean the
tool failed; other providers can still return results. Add a Semantic Scholar
key only if higher search throughput is needed.

Global flags go before the subcommand. Use `paper-dl --json search ...`, not
`paper-dl search ... --json`.

## Test

```bash
paper-dl search "CRISPR" -n 5
paper-dl --json search "species distribution modeling" -n 3
paper-dl download 10.1038/s41586-019-1055-0
paper-dl mirrors
```

Use `paper-dl mirrors --refresh` to force a new mirror discovery pass. The tool
checks candidate mirrors in parallel, drops mirrors that do not respond, sorts
working mirrors by latency, and caches that order for 6 hours. This keeps dead
mirrors from being tried before mirrors that are currently responding.

After setting `unpaywall-email`, also test:

```bash
paper-dl --json lookup 10.1038/s41586-019-1055-0
```
