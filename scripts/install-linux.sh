#!/usr/bin/env bash
set -euo pipefail

TOOL="${1:-all}"
INSTALL_ROOT="${INSTALL_ROOT:-$HOME/.ai-assistant-tools}"
LOCAL_BIN="${LOCAL_BIN:-$HOME/.local/bin}"
CODEX_SKILLS="${CODEX_SKILLS:-$HOME/.codex/skills}"
REPO_RAW_BASE="${REPO_RAW_BASE:-https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main}"

usage() {
  cat <<'EOF'
Usage: scripts/install-linux.sh [all|gogcli|outlook|onedrive|d2l|humanizer|paper-fetch|literature-search|citation-zotero|scientific-writing|literature-appraisal|exa-search]

Environment overrides:
  INSTALL_ROOT   Default: $HOME/.ai-assistant-tools
  LOCAL_BIN      Default: $HOME/.local/bin
  CODEX_SKILLS   Default: $HOME/.codex/skills
  REPO_RAW_BASE  Default: raw GitHub main branch
EOF
}

case "$TOOL" in
  all|gogcli|outlook|onedrive|d2l|humanizer|paper-fetch|literature-search|citation-zotero|scientific-writing|literature-appraisal|exa-search) ;;
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
  download "$REPO_RAW_BASE/tools/humanizer/skill/LICENSE" "$CODEX_SKILLS/humanizer/LICENSE"
  echo "Installed humanizer Codex skill."
}

install_scientific_writing() {
  install_skill "scientific-writing" "scientific-writing"
  install_skill_reference "scientific-writing" "scientific-writing" "humanizer.md"
  echo "Installed scientific-writing Codex skill."
}

install_skill_only() {
  local name="$1"
  install_skill "$name" "$name"
  echo "Installed $name Codex skill."
}

install_exa_search() {
  mkdir -p "$INSTALL_ROOT/exa-search"
  download "$REPO_RAW_BASE/tools/exa-search/bin/exa-search.py" "$INSTALL_ROOT/exa-search/exa-search.py"
  chmod +x "$INSTALL_ROOT/exa-search/exa-search.py"
  if [ ! -f "$INSTALL_ROOT/exa-search/.env" ]; then
    cat > "$INSTALL_ROOT/exa-search/.env" <<'EOF'
EXA_API_KEY=
EOF
  fi
  cat > "$LOCAL_BIN/exa-search" <<EOF
#!/usr/bin/env bash
export EXA_SEARCH_ENV_FILE="$INSTALL_ROOT/exa-search/.env"
exec python "$INSTALL_ROOT/exa-search/exa-search.py" "\$@"
EOF
  chmod +x "$LOCAL_BIN/exa-search"
  install_skill "exa-search" "exa-search"
  echo "Installed exa-search CLI to $INSTALL_ROOT/exa-search"
  echo "Config file: $INSTALL_ROOT/exa-search/.env"
  echo "Installed PATH shim to $LOCAL_BIN/exa-search"
  echo "Installed exa-search Codex skill."
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
  echo "Installed paper-search from Fr4nzz/paper-search-mcp to $INSTALL_ROOT/venv"
  echo "Config file: $INSTALL_ROOT/paper-search-mcp/.env"
  echo "Installed PATH shim to $LOCAL_BIN/paper-search"
}

selected_tools() {
  if [ "$TOOL" = "all" ]; then
    printf '%s\n' gogcli outlook onedrive d2l humanizer paper-fetch literature-search citation-zotero scientific-writing literature-appraisal exa-search
  else
    printf '%s\n' "$TOOL"
  fi
}

while IFS= read -r item; do
  case "$item" in
    gogcli) install_gogcli ;;
    outlook|onedrive|d2l) install_python_cli "$item" ;;
    humanizer) install_humanizer ;;
    paper-fetch) install_paper_fetch ;;
    literature-search|citation-zotero|literature-appraisal) install_skill_only "$item" ;;
    scientific-writing) install_scientific_writing ;;
    exa-search) install_exa_search ;;
  esac
done < <(selected_tools)

cat <<EOF

Done. Make sure $LOCAL_BIN is on PATH, then restart Codex Desktop so new global skills are loaded.
EOF
