param(
  [ValidateSet('all', 'gogcli', 'outlook', 'onedrive', 'd2l', 'whatsapp', 'humanizer', 'paper-fetch')]
  [string] $Tool = 'all',

  [string] $InstallRoot = (Join-Path $HOME '.ai-assistant-tools'),

  [string] $RepoRawBase = 'https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main',

  [switch] $SkipDependencies,

  [switch] $SkipWhasapoMcp
)

$ErrorActionPreference = 'Stop'

function Get-UrlFile {
  param([string] $Url, [string] $Path)
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
  try {
    Invoke-WebRequest -Uri $Url -OutFile $Path
  } catch {
    if ($Url -notmatch '^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)$') {
      throw
    }
    $owner = $Matches[1]
    $repo = $Matches[2]
    $ref = $Matches[3]
    $repoPath = $Matches[4]
    $api = "https://api.github.com/repos/$owner/$repo/contents/$repoPath`?ref=$ref"
    $item = Invoke-RestMethod -Uri $api -Headers @{ 'User-Agent' = 'AI_Assistant_Tools installer' }
    $bytes = [Convert]::FromBase64String(($item.content -replace '\s', ''))
    [IO.File]::WriteAllBytes($Path, $bytes)
  }
}

function Install-Skill {
  param([string] $Name, [string] $Source)
  $dest = Join-Path $HOME ".codex\skills\$Name"
  New-Item -ItemType Directory -Force -Path (Join-Path $dest 'agents') | Out-Null
  Get-UrlFile "$RepoRawBase/tools/$Source/skill/SKILL.md" (Join-Path $dest 'SKILL.md')
  Get-UrlFile "$RepoRawBase/tools/$Source/skill/agents/openai.yaml" (Join-Path $dest 'agents\openai.yaml')
}

function Install-CliTool {
  param(
    [string] $Name,
    [string[]] $Files,
    [string[]] $PipPackages = @()
  )
  $toolDir = Join-Path $InstallRoot $Name
  New-Item -ItemType Directory -Force -Path $toolDir | Out-Null

  foreach ($file in $Files) {
    Get-UrlFile "$RepoRawBase/tools/$Name/bin/$file" (Join-Path $toolDir $file)
  }

  $localBin = Join-Path $HOME '.local\bin'
  New-Item -ItemType Directory -Force -Path $localBin | Out-Null
  $shim = Join-Path $localBin "$Name.cmd"
  "@echo off`r`ncall `"$toolDir\$Name.cmd`" %*`r`n" | Set-Content -LiteralPath $shim -Encoding ASCII

  Install-Skill $Name $Name

  if (-not $SkipDependencies -and $PipPackages.Count -gt 0) {
    python -m pip install @PipPackages
    python -m playwright install chromium
  }

  Write-Host "Installed $Name CLI to $toolDir"
  Write-Host "Installed PATH shim to $shim"
}

function Install-WhaCli {
  $toolDir = Join-Path $InstallRoot 'whatsapp'
  New-Item -ItemType Directory -Force -Path $toolDir | Out-Null

  Get-UrlFile "$RepoRawBase/tools/whatsapp/bin/wha.py" (Join-Path $toolDir 'wha.py')
  Get-UrlFile "$RepoRawBase/tools/whatsapp/bin/wha.cmd" (Join-Path $toolDir 'wha.cmd')

  $localBin = Join-Path $HOME '.local\bin'
  New-Item -ItemType Directory -Force -Path $localBin | Out-Null
  $shim = Join-Path $localBin 'wha.cmd'
  "@echo off`r`ncall `"$toolDir\wha.cmd`" %*`r`n" | Set-Content -LiteralPath $shim -Encoding ASCII

  Install-Skill 'whatsapp' 'whatsapp'

  Write-Host "Installed wha CLI to $toolDir"
  Write-Host "Installed PATH shim to $shim"
}

function Install-GogCli {
  $localBin = Join-Path $HOME '.local\bin'
  New-Item -ItemType Directory -Force -Path $localBin | Out-Null

  $release = Invoke-RestMethod -Uri 'https://api.github.com/repos/openclaw/gogcli/releases/latest' -Headers @{ 'User-Agent' = 'AI_Assistant_Tools installer' }
  $asset = $release.assets | Where-Object { $_.name -match '^gogcli_.*_windows_amd64\.zip$' } | Select-Object -First 1
  if (-not $asset) {
    throw 'Could not find a Windows amd64 gogcli release asset.'
  }

  $toolDir = Join-Path $InstallRoot 'gogcli'
  New-Item -ItemType Directory -Force -Path $toolDir | Out-Null
  $zip = Join-Path $env:TEMP $asset.name
  Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zip
  Expand-Archive -LiteralPath $zip -DestinationPath $toolDir -Force

  $exe = Get-ChildItem -LiteralPath $toolDir -Recurse -Filter 'gog.exe' | Select-Object -First 1
  if (-not $exe) {
    throw 'gog.exe was not found after extracting gogcli.'
  }

  Copy-Item -LiteralPath $exe.FullName -Destination (Join-Path $localBin 'gog.exe') -Force
  Remove-Item -LiteralPath (Join-Path $localBin 'gog.cmd') -Force -ErrorAction SilentlyContinue
  Install-Skill 'gogcli' 'gogcli'

  Write-Host "Installed gog.exe to $localBin"
  Write-Host 'Run: gog --version'
  Write-Host 'Then authenticate with: gog auth credentials set <client_secret.json>; gog auth add you@gmail.com --services gmail,calendar,drive,docs,sheets,slides,forms,tasks'
}

function Install-WhatsApp {
  if (-not $SkipDependencies) {
    Invoke-Expression (Invoke-RestMethod 'https://raw.githubusercontent.com/toloco/whasapo/main/install.ps1')
  }

  Install-WhaCli

  $agents = Join-Path $HOME '.codex\AGENTS.md'
  $line = 'For WhatsApp requests, use the global `whatsapp` skill and local `wha` CLI backed by Whasapo; never send unless I explicitly provide the exact recipient and message/file.'
  if (-not (Test-Path $agents) -or -not (Select-String -LiteralPath $agents -SimpleMatch $line -Quiet)) {
    Add-Content -LiteralPath $agents -Value $line
  }

  if (-not $SkipWhasapoMcp) {
    Write-Host 'MCP registration is no longer required for normal WhatsApp use. Use wha CLI commands.'
  }
  Write-Host 'Run: whasapo pair'
  Write-Host 'Then test: wha doctor'
}

function Install-Humanizer {
  Install-Skill 'humanizer' 'humanizer'
  Get-UrlFile "$RepoRawBase/tools/humanizer/skill/LICENSE" (Join-Path $HOME '.codex\skills\humanizer\LICENSE')
  Write-Host 'Installed humanizer Codex skill.'
}

function Install-PaperFetch {
  $toolDir = Join-Path $InstallRoot 'paper-search-mcp'
  New-Item -ItemType Directory -Force -Path $toolDir | Out-Null

  $localBin = Join-Path $HOME '.local\bin'
  New-Item -ItemType Directory -Force -Path $localBin | Out-Null

  $envFile = Join-Path $toolDir '.env'
  if (-not (Test-Path -LiteralPath $envFile)) {
@'
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
'@ | Set-Content -LiteralPath $envFile -Encoding ASCII
  }

  $shim = Join-Path $localBin 'paper-search.cmd'
  "@echo off`r`nset `"PAPER_SEARCH_MCP_ENV_FILE=$envFile`"`r`npython -m paper_search_mcp.cli %*`r`n" | Set-Content -LiteralPath $shim -Encoding ASCII

  Install-Skill 'paper-fetch' 'paper-fetch'

  if (-not $SkipDependencies) {
    python -m pip install --upgrade 'git+https://github.com/Fr4nzz/paper-search-mcp.git@codex/fallback-download-improvements'
  }

  Write-Host 'Installed paper-search from Fr4nzz/paper-search-mcp.'
  Write-Host "Config file: $envFile"
  Write-Host "Installed PATH shim to $shim"
}

$selected = if ($Tool -eq 'all') {
  @('gogcli', 'outlook', 'onedrive', 'd2l', 'whatsapp', 'humanizer', 'paper-fetch')
} else {
  @($Tool)
}

foreach ($item in $selected) {
  switch ($item) {
    'outlook' { Install-CliTool 'outlook' @('outlook.py', 'outlook.cmd') @('playwright') }
    'onedrive' { Install-CliTool 'onedrive' @('onedrive.py', 'onedrive.cmd') @('playwright') }
    'd2l' { Install-CliTool 'd2l' @('d2l.py', 'd2l.cmd') @('playwright', 'websockets') }
    'gogcli' { Install-GogCli }
    'whatsapp' { Install-WhatsApp }
    'humanizer' { Install-Humanizer }
    'paper-fetch' { Install-PaperFetch }
  }
}

Write-Host ''
Write-Host 'Done. Restart Codex Desktop so new global skills and MCP servers are loaded.'
