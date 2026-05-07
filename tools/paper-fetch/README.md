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
`requests`, `beautifulsoup4`, `urllib3`, and `lxml`, copies the CLI files to
`~/.ai-assistant-tools/paper-fetch`, and creates the `~/.local/bin/paper-dl` shim.

## Configuration

Set the required email and optional API keys:

```bash
paper-dl set-key unpaywall-email your@email.com
paper-dl set-key openalex YOUR_KEY_HERE
paper-dl set-key semantic YOUR_KEY_HERE
```

Get a free OpenAlex key at https://openalex.org/settings/api-key (30-second signup).

## Test

```bash
paper-dl search "CRISPR" -n 5
paper-dl download 10.1038/s41586-019-1055-0
paper-dl mirrors
```
