#!/usr/bin/env bash
set -euo pipefail

TOOL="${1:-all}"
INSTALL_ROOT="${INSTALL_ROOT:-$HOME/.ai-assistant-tools}"
LOCAL_BIN="${LOCAL_BIN:-$HOME/.local/bin}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CODEX_SKILLS="${CODEX_SKILLS:-$CODEX_HOME/skills}"
CODEX_CONFIG="${CODEX_CONFIG:-$CODEX_HOME/config.toml}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
HERMES_SKILLS="${HERMES_SKILLS:-}"
REPO_RAW_BASE="${REPO_RAW_BASE:-https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main}"

usage() {
  cat <<'EOF'
Usage: scripts/install-linux.sh [all|gogcli|outlook|onedrive|d2l|humanizer|paper-fetch|academic-research|superpowers]

Environment overrides:
  INSTALL_ROOT   Default: $HOME/.ai-assistant-tools
  LOCAL_BIN      Default: $HOME/.local/bin
  CODEX_HOME     Default: $HOME/.codex
  CODEX_SKILLS   Default: $HOME/.codex/skills
  CODEX_CONFIG   Default: $HOME/.codex/config.toml
  HERMES_SKILLS  Default: (empty) — when set, also copies skills to this path
  REPO_RAW_BASE  Default: raw GitHub main branch
EOF
}

case "$TOOL" in
  all|gogcli|outlook|onedrive|d2l|humanizer|paper-fetch|academic-research|superpowers) ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

mkdir -p "$INSTALL_ROOT" "$LOCAL_BIN" "$CODEX_SKILLS"

download() {
  local url="$1"
  local path="$2"
  mkdir -p "$(dirname "$path")"
  if [[ "$url" == file://* ]]; then
    cp "${url#file://}" "$path"
  else
    curl -fsSL "$url" -o "$path"
  fi
}

install_skill() {
  local name="$1"
  local source="$2"
  mkdir -p "$CODEX_SKILLS/$name/agents"
  download "$REPO_RAW_BASE/tools/$source/skill/SKILL.md" "$CODEX_SKILLS/$name/SKILL.md"
  download "$REPO_RAW_BASE/tools/$source/skill/agents/openai.yaml" "$CODEX_SKILLS/$name/agents/openai.yaml"
}

install_skill_reference() {
  local name="$1"
  local source="$2"
  local ref="$3"
  mkdir -p "$CODEX_SKILLS/$name/references"
  download "$REPO_RAW_BASE/tools/$source/skill/references/$ref" "$CODEX_SKILLS/$name/references/$ref"
}

install_hermes_skill() {
  if [ -z "$HERMES_SKILLS" ]; then
    return 0
  fi
  local name="$1"
  local source="$2"
  mkdir -p "$HERMES_SKILLS/$name"
  download "$REPO_RAW_BASE/tools/$source/skill/SKILL.md" "$HERMES_SKILLS/$name/SKILL.md"
  echo "Installed $name Hermes skill to $HERMES_SKILLS/$name"
}

install_hermes_skill_reference() {
  if [ -z "$HERMES_SKILLS" ]; then
    return 0
  fi
  local name="$1"
  local source="$2"
  local ref="$3"
  mkdir -p "$HERMES_SKILLS/$name/references"
  download "$REPO_RAW_BASE/tools/$source/skill/references/$ref" "$HERMES_SKILLS/$name/references/$ref"
}

ensure_global_agents_note() {
  local agents="$CODEX_HOME/AGENTS.md"
  local marker="AI_ASSISTANT_TOOLS_RESEARCH_SKILLS"
  mkdir -p "$(dirname "$agents")"
  local block
  block="$(cat <<'EOF'

<!-- AI_ASSISTANT_TOOLS_RESEARCH_SKILLS -->
For scientific research and literature-review tasks, prefer the AI_Assistant_Tools research skills when installed:
- Use `academic-research` for literature discovery, review planning, paper reading, appraisal, Zotero/citation workflows, and scientific writing.
- Use `paper-fetch` / `paper-search` to download known PDFs and enrich DOI metadata.
- For initial discovery, run native search, Parallel search when configured, and paper-search in parallel when the review needs broad coverage.
- After selecting papers, make a todo list, screen papers, delegate reading when useful, write markdown paper summaries/topic extracts, build a synthesis matrix, then draft from evidence.
<!-- /AI_ASSISTANT_TOOLS_RESEARCH_SKILLS -->
EOF
)"
  if [ -f "$agents" ] && grep -q "$marker" "$agents"; then
    BLOCK="$block" python - "$agents" <<'PY'
from pathlib import Path
import os
import re
import sys

path = Path(sys.argv[1]).expanduser()
text = path.read_text()
block = os.environ["BLOCK"].strip("\n")
pattern = re.compile(r"\n?<!-- AI_ASSISTANT_TOOLS_RESEARCH_SKILLS -->.*?<!-- /AI_ASSISTANT_TOOLS_RESEARCH_SKILLS -->", re.S)
text = pattern.sub("\n" + block, text)
path.write_text(text)
PY
  else
    printf '%s\n' "$block" >> "$agents"
  fi
}

ensure_venv() {
  if [ ! -x "$INSTALL_ROOT/venv/bin/python" ]; then
    python -m venv "$INSTALL_ROOT/venv"
  fi
  "$INSTALL_ROOT/venv/bin/python" -m pip install --upgrade pip
  "$INSTALL_ROOT/venv/bin/python" -m pip install playwright websockets
}

install_python_cli() {
  local name="$1"
  ensure_venv
  mkdir -p "$INSTALL_ROOT/$name"
  download "$REPO_RAW_BASE/tools/$name/bin/$name.py" "$INSTALL_ROOT/$name/$name.py"
  chmod +x "$INSTALL_ROOT/$name/$name.py"
  cat > "$LOCAL_BIN/$name" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_ROOT/venv/bin/python" "$INSTALL_ROOT/$name/$name.py" "\$@"
EOF
  chmod +x "$LOCAL_BIN/$name"
  install_skill "$name" "$name"
  echo "Installed $name CLI to $INSTALL_ROOT/$name"
  echo "Installed PATH shim to $LOCAL_BIN/$name"
}

install_gogcli() {
  local tmp
  local arch
  tmp="$(mktemp -d)"
  arch="$(uname -m)"
  case "$arch" in
    x86_64|amd64) arch="amd64" ;;
    aarch64|arm64) arch="arm64" ;;
    *) echo "Unsupported architecture for gogcli: $arch" >&2; exit 1 ;;
  esac

  local release_json asset_url
  release_json="$(curl -fsSL https://api.github.com/repos/openclaw/gogcli/releases/latest)"
  asset_url="$(printf '%s' "$release_json" | python -c "import json,sys; data=json.load(sys.stdin); assets=data.get('assets', []); name='linux_${arch}.tar.gz'; print(next(a['browser_download_url'] for a in assets if name in a.get('name','')))")"
  download "$asset_url" "$tmp/gogcli.tar.gz"
  tar -xzf "$tmp/gogcli.tar.gz" -C "$tmp"
  install -m 0755 "$(find "$tmp" -type f -name gog | head -n 1)" "$LOCAL_BIN/gog"
  install_skill "gogcli" "gogcli"
  echo "Installed gog to $LOCAL_BIN/gog"
}

install_humanizer() {
  install_skill "humanizer" "humanizer"
  install_hermes_skill "humanizer" "humanizer"
  download "$REPO_RAW_BASE/tools/humanizer/skill/LICENSE" "$CODEX_SKILLS/humanizer/LICENSE"
  echo "Installed humanizer Codex skill."
}

install_academic_research() {
  install_skill "academic-research" "academic-research"
  install_skill_reference "academic-research" "academic-research" "humanizer.md"
  install_hermes_skill "academic-research" "academic-research"
  install_hermes_skill_reference "academic-research" "academic-research" "humanizer.md"
  ensure_global_agents_note
  echo "Installed academic-research Codex skill."
}

install_skill_only() {
  local name="$1"
  install_skill "$name" "$name"
  install_hermes_skill "$name" "$name"
  echo "Installed $name Codex skill."
}

install_superpowers() {
  install_skill "superpowers-helper" "superpowers"
  mkdir -p "$(dirname "$CODEX_CONFIG")"
  python - "$CODEX_CONFIG" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1]).expanduser()
text = path.read_text() if path.exists() else ""
header = '[plugins."superpowers@openai-curated"]'

if header in text:
    pattern = re.compile(r'(\[plugins\."superpowers@openai-curated"\]\n)(.*?)(?=\n\[|\Z)', re.S)
    def repl(match):
        body = match.group(2)
        if re.search(r'(?m)^enabled\s*=', body):
            body = re.sub(r'(?m)^enabled\s*=.*$', 'enabled = true', body)
        else:
            body = 'enabled = true\n' + body
        return match.group(1) + body.rstrip() + "\n"
    text = pattern.sub(repl, text)
else:
    if text and not text.endswith("\n"):
        text += "\n"
    text += '\n[plugins."superpowers@openai-curated"]\nenabled = true\n'

path.write_text(text)
PY
  echo "Enabled Superpowers plugin in $CODEX_CONFIG"
  echo "Restart Codex Desktop. If the plugin does not appear, install Superpowers from the Plugins UI."
}

install_paper_fetch() {
  ensure_venv
  mkdir -p "$INSTALL_ROOT/paper-search-mcp"
  "$INSTALL_ROOT/venv/bin/python" -m pip install --upgrade \
    "git+https://github.com/Fr4nzz/paper-search-mcp.git@codex/fallback-download-improvements"
  if [ ! -f "$INSTALL_ROOT/paper-search-mcp/.env" ]; then
    cat > "$INSTALL_ROOT/paper-search-mcp/.env" <<'EOF'
# Optional but recommended: enables faster Unpaywall DOI lookup/download.
PAPER_SEARCH_MCP_UNPAYWALL_EMAIL=

# Optional API keys / tuning.
PAPER_SEARCH_MCP_CORE_API_KEY=
PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY=
PAPER_SEARCH_MCP_GOOGLE_SCHOLAR_PROXY_URL=
PAPER_SEARCH_MCP_SCIHUB_MIRRORS=
PAPER_SEARCH_MCP_SCIHUB_MIRROR_CACHE_TTL=21600
PAPER_SEARCH_MCP_SCIHUB_MIRROR_PROBE_TIMEOUT=4
PAPER_SEARCH_MCP_SCIHUB_MIRROR_DISCOVERY_TIMEOUT=5
PAPER_SEARCH_MCP_SCIHUB_MIRROR_PROBE_WORKERS=8
EOF
  fi
  cat > "$LOCAL_BIN/paper-search" <<EOF
#!/usr/bin/env bash
export PAPER_SEARCH_MCP_ENV_FILE="$INSTALL_ROOT/paper-search-mcp/.env"
exec "$INSTALL_ROOT/venv/bin/python" -m paper_search_mcp.cli "\$@"
EOF
  chmod +x "$LOCAL_BIN/paper-search"
  install_skill "paper-fetch" "paper-fetch"
  install_hermes_skill "paper-fetch" "paper-fetch"
  echo "Installed paper-search from Fr4nzz/paper-search-mcp to $INSTALL_ROOT/venv"
  echo "Config file: $INSTALL_ROOT/paper-search-mcp/.env"
  echo "Installed PATH shim to $LOCAL_BIN/paper-search"
}

selected_tools() {
  if [ "$TOOL" = "all" ]; then
    printf '%s\n' gogcli outlook onedrive d2l humanizer paper-fetch academic-research superpowers
  else
    printf '%s\n' "$TOOL"
  fi
}

while IFS= read -r item; do
  case "$item" in
    gogcli) install_gogcli ;;
    outlook|onedrive|d2l) install_python_cli "$item" ;;
    humanizer) install_humanizer ;;
    paper-fetch) install_paper_fetch; ensure_global_agents_note ;;
    academic-research) install_academic_research ;;
    superpowers) install_superpowers ;;
  esac
done < <(selected_tools)

cat <<EOF

Done. Make sure $LOCAL_BIN is on PATH, then restart Codex Desktop so new global skills are loaded.
EOF

if [ -n "$HERMES_SKILLS" ]; then
  cat <<EOF
Hermes skills were also installed to $HERMES_SKILLS.
Restart your Hermes session or reload skills for them to take effect.
EOF
fi
