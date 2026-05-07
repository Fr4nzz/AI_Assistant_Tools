---
name: exa-search
description: Use when the user asks to use, install, configure, or benchmark Exa search for web, academic, code, or literature discovery.
triggers:
  - exa
  - exa search
  - exa mcp
  - benchmark search
  - compare search engines
argument-hint: "<search query or benchmark topic>"
metadata:
  requires:
    bins: ["exa-search"]
---

# Exa Search

Exa is an optional search route for agents. Use the local `exa-search` CLI as an
additional engine, not as a replacement for native search until local benchmarks
show it is better for the user's topic.

Main pieces:

- Local CLI: `exa-search`, backed by the third-party `exa-cli` package.
- Hosted MCP, optional: `https://mcp.exa.ai/mcp`
- MCP repo: https://github.com/exa-labs/exa-mcp-server
- Python SDK: `exa-py`
- JavaScript SDK: `exa-js`

## Install / Configure

The AI_Assistant_Tools installer installs `exa-cli` in its Python environment
and exposes it as `exa-search` to avoid collisions with unrelated Linux `exa`
or `eza` commands. Set an API key before use:

```bash
export EXA_API_KEY="your_exa_key"
```

Get a key from https://dashboard.exa.ai/api-keys or the API key links in
https://exa.ai/docs. Treat the key like a password; do not paste it into public
logs or commits.

Basic test:

```bash
exa-search search "species distribution modeling spatial block cross validation" -n 5
```

Exa currently advertises a free monthly request tier, but API limits and pricing
can change; check https://exa.ai/pricing before heavy benchmarking.

Official repo and docs:

- https://github.com/exa-labs/exa-mcp-server
- https://exa.ai/docs/examples/exa-mcp

Optional hosted MCP setup for Codex, if the user prefers MCP:

```bash
codex mcp add exa --url https://mcp.exa.ai/mcp
```

## Useful Commands

```bash
exa-search search "query" -n 10
exa-search contents "https://example.org/paper"
exa-search similar "https://example.org/paper"
exa-search answer "what are the main methods for spatial cross-validation in SDMs?"
```

`exa-cli` prints text, not strict JSON. For benchmarking, capture stdout and
deduplicate results by URL/title/DOI.

## Benchmark Pattern

Use the same 3-5 prompts across:

- native Codex/web search
- Parallel search, if configured
- paper-search topic search
- Exa search, if available

Measure:

- elapsed time
- number of relevant papers found
- unique high-quality papers not found by other engines
- overlap by DOI/title
- whether results include DOI/full-text links

For literature reviews, prefer the union of high-quality results, then dedupe
and rank with `paper-search metadata-dois`.
