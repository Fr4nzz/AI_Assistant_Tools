# Exa Search

Installs a small `exa-search` CLI plus a Codex skill for benchmarking Exa
search. The CLI calls Exa's current Search API directly, so it avoids MCP issues
and avoids the stale third-party `exa-cli` parameter set.

Set an API key before use:

```bash
export EXA_API_KEY="your_exa_key"
exa-search search "species distribution modeling spatial block cross validation" -n 5 --json
```

To get a key, create/sign in to an Exa account at
https://dashboard.exa.ai/api-keys or use the API key links from
https://exa.ai/docs. Treat it like a password.

The installer also creates:

```text
~/.ai-assistant-tools/exa-search/.env
```

Set `EXA_API_KEY=` there for persistent local use.

The installed command is named `exa-search` so it does not collide with the
unrelated old Linux `exa` directory-listing command. Useful commands:

```bash
exa-search search "query" -n 10 --type auto --json
exa-search search "query" --type deep --summary --json
exa-search contents "https://example.org" --text --json
```

See:

- https://github.com/exa-labs/exa-mcp-server
- https://exa.ai/docs/examples/exa-mcp
- https://exa.ai/docs

For SDK/API benchmarking, set `EXA_API_KEY`. Exa advertises a free monthly
request tier, but check https://exa.ai/pricing before large benchmarks.
