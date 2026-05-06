# Paper Fetch

Search and download academic papers with automatic mirror discovery.

## What It Does

- **Search** across OpenAlex, Semantic Scholar, Crossref, and arXiv
- **Download** papers by DOI or URL
- **Auto-discover** working academic mirrors with health probes
- **Set API keys** interactively via CLI

## Quick Install

### Prerequisites

- Python 3.10+ with `pip`
- `git` (to clone)

### Install

```bash
# Clone wherever you want
git clone <repo-url> ~/paper-fetch
cd ~/paper-fetch/skills/paper-fetch

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Codex Desktop (Skill Mode)

Copy the skill to your Codex skills directory:

```bash
# Linux / macOS
mkdir -p ~/.codex/skills
cp -r ~/paper-fetch/skills/paper-fetch ~/.codex/skills/paper-fetch

# Windows
mkdir %USERPROFILE%\.codex\skills
xcopy /E /I %USERPROFILE%\paper-fetch\skills\paper-fetch %USERPROFILE%\.codex\skills\paper-fetch
```

Restart Codex Desktop after installing.

### Codex Desktop (MCP Server Mode)

Add to your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "paper-fetch": {
      "command": "python3",
      "args": ["-m", "scripts.paper_dl", "serve"],
      "env": {
        "PAPER_FETCH_UNPAYWALL_EMAIL": "your@email.com"
      }
    }
  }
}
```

## Configuration

### Required: Unpaywall Email

Any valid email works. Set it interactively:

```bash
python3 scripts/paper_dl.py set-key unpaywall-email your@email.com
```

### Optional: API Keys (for better rate limits)

#### OpenAlex (Recommended — free, 30-second signup)

1. Go to https://openalex.org/settings/api-key
2. Click "Create account" or sign in
3. Copy your API key
4. Paste it into the chat so the AI can run:
   ```bash
   python3 scripts/paper_dl.py set-key openalex YOUR_KEY_HERE
   ```

#### Semantic Scholar (Optional — free)

1. Go to https://www.semanticscholar.org/product/api
2. Fill the form and request a key
3. Once you receive it, run:
   ```bash
   python3 scripts/paper_dl.py set-key semantic YOUR_KEY_HERE
   ```

#### CORE (Optional — free)

1. Go to https://core.ac.uk/services/api
2. Register for a free key
3. Run:
   ```bash
   python3 scripts/paper_dl.py set-key core YOUR_KEY_HERE
   ```

## Usage

### Search

```bash
python3 scripts/paper_dl.py search "quantum entanglement" -n 5
```

### Download

```bash
python3 scripts/paper_dl.py download 10.1038/nature12373
python3 scripts/paper_dl.py download https://doi.org/10.1038/nature12373
```

### List Mirrors

```bash
python3 scripts/paper_dl.py mirrors
```

### Lookup DOI

```bash
python3 scripts/paper_dl.py lookup 10.1038/nature12373
```

## Files

| File | Purpose |
|------|---------|
| `scripts/paper_dl.py` | Main CLI entry point |
| `scripts/search.py` | Search APIs (OpenAlex, Semantic Scholar, Crossref, arXiv) |
| `scripts/download.py` | Download pipeline |
| `scripts/mirrors.py` | Mirror discovery and health probes |
| `scripts/config.py` | Configuration and env vars |
| `scripts/pdf_utils.py` | PDF validation and filename handling |
| `SKILL.md` | Codex skill definition |
