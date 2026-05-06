param(
  [ValidateSet('all', 'google-workspace', 'outlook', 'onedrive', 'd2l', 'whatsapp')]
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

function Install-GoogleWorkspace {
  Install-Skill 'google-workspace' 'google-workspace'

  $skillInstaller = Join-Path $HOME '.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py'
  if (Test-Path -LiteralPath $skillInstaller) {
    foreach ($skill in @('gws-shared', 'gws-gmail', 'gws-drive', 'gws-docs')) {
      python $skillInstaller --repo googleworkspace/cli --path "skills/$skill"
    }
  } else {
    Write-Warning 'Codex skill-installer was not found. Install upstream gws-shared, gws-gmail, gws-drive, and gws-docs skills manually if needed.'
  }

  $localBin = Join-Path $HOME '.local\bin'
  New-Item -ItemType Directory -Force -Path $localBin | Out-Null
  $shim = Join-Path $localBin 'gws.cmd'
  "@echo off`r`ncall `"%APPDATA%\npm\gws.cmd`" %*`r`n" | Set-Content -LiteralPath $shim -Encoding ASCII

  if (-not (Get-Command gws.cmd -ErrorAction SilentlyContinue)) {
    if (-not $SkipDependencies) {
      npm install -g '@googleworkspace/cli'
    } else {
      Write-Warning 'gws.cmd was not found. Install it with: npm install -g @googleworkspace/cli'
    }
  }

  Write-Host 'Installed google-workspace Codex skill.'
  Write-Host 'Follow tools/google-workspace/README.md for Google Cloud OAuth setup.'
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

$selected = if ($Tool -eq 'all') {
  @('google-workspace', 'outlook', 'onedrive', 'd2l', 'whatsapp')
} else {
  @($Tool)
}

foreach ($item in $selected) {
  switch ($item) {
    'outlook' { Install-CliTool 'outlook' @('outlook.py', 'outlook.cmd') @('playwright') }
    'onedrive' { Install-CliTool 'onedrive' @('onedrive.py', 'onedrive.cmd') @('playwright') }
    'd2l' { Install-CliTool 'd2l' @('d2l.py', 'd2l.cmd') @('playwright', 'websockets') }
    'google-workspace' { Install-GoogleWorkspace }
    'whatsapp' { Install-WhatsApp }
  }
}

Write-Host ''
Write-Host 'Done. Restart Codex Desktop so new global skills and MCP servers are loaded.'
