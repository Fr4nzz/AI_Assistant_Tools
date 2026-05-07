# Exa Search

Installs the third-party `exa-cli` package in the AI_Assistant_Tools Python
environment, exposes it as `exa-search`, and installs a Codex skill for
benchmarking Exa search. This avoids depending on MCP availability for normal
agent workflows.

Set an API key before use:

```bash
export EXA_API_KEY="your_exa_key"
exa-search search "species distribution modeling spatial block cross validation" -n 5
```

To get a key, create/sign in to an Exa account at
https://dashboard.exa.ai/api-keys or use the API key links from
https://exa.ai/docs. Treat it like a password.

The installed command is named `exa-search` so it does not collide with the
unrelated old Linux `exa` directory-listing command. Useful commands:

```bash
exa-search search "query" -n 10
exa-search contents "https://example.org"
exa-search similar "https://example.org"
exa-search answer "question with citations"
```

See:

- https://github.com/exa-labs/exa-mcp-server
- https://exa.ai/docs/examples/exa-mcp
- https://exa.ai/docs

For SDK/API benchmarking, set `EXA_API_KEY`. Exa advertises a free monthly
request tier, but check https://exa.ai/pricing before large benchmarks.
