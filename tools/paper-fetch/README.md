# Paper Fetch

Search and download academic papers from open access sources, repositories, and academic mirrors.

## What It Does

- **Search** across OpenAlex, Semantic Scholar, Crossref, arXiv, bioRxiv, and Google Scholar in parallel
- **Download** papers by DOI or URL with multi-source fallback (OA → Anna's Archive → mirrors → direct PDF)
- **Auto-discover** working academic mirrors with health probes
- **Set API keys** interactively via CLI

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

Search and mirror fallback download work without configuration. For faster and
more reliable DOI lookup/open-access downloads, set an Unpaywall contact email.
Optional API keys improve rate limits.

```bash
paper-dl set-key unpaywall-email your@email.com
paper-dl set-key openalex YOUR_KEY_HERE
paper-dl set-key semantic YOUR_KEY_HERE
```

Get a free OpenAlex key at https://openalex.org/settings/api-key (30-second signup).

`unpaywall-email` is optional for search and mirror fallback downloads, but
required for `paper-dl lookup` and the fastest Unpaywall open-access download
path. Use the user's real contact email; Unpaywall and Crossref use it for
polite API contact/rate-limit identification.

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

After setting `unpaywall-email`, also test:

```bash
paper-dl --json lookup 10.1038/s41586-019-1055-0
```
