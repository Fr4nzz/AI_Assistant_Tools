# Literature Search

Installs a Codex skill for literature-review discovery. It coordinates native
web search, Parallel search when configured, and supplemental
`paper-search search`, then uses `paper-search metadata-dois` for DOI metadata
and ranking.

`paper-search search` now returns a broader compact candidate list by default:
up to 10 results per source, without abstracts unless `--include-abstracts` is
requested.

This is a skill-only tool; no extra binary is required beyond the optional
search tools it can use.

## Install

Linux:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) literature-search
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool literature-search
```
