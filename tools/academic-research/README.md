# Academic Research

Installs one AI agent skill for academic research workflows around literature
reviews: discovery, screening, paper reading, synthesis, appraisal, citation
workflow planning, and scientific writing. Works with Codex Desktop and
Hermes Agent.

`paper-fetch` remains a separate tool because it installs the `paper-search`
CLI for DOI metadata and PDF download. Use `academic-research` to decide what
to search, read, cite, audit, and write; use `paper-fetch` when known papers
need metadata or full-text retrieval.

This skill merges the previous `literature-search`, `literature-review`,
`citation-zotero`, `scientific-writing`, and `literature-appraisal` skills so
agents have one coherent research workflow instead of five overlapping skills.

## Install

Linux:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install-linux.sh) academic-research
```

Windows:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1))) -Tool academic-research
```
