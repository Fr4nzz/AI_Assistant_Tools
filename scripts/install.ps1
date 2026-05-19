param(
  [ValidateSet('all', 'gogcli', 'outlook', 'onedrive', 'd2l', 'whatsapp', 'humanizer', 'paper-fetch', 'academic-research', 'notebooklm', 'ytfetcher', 'tubescrape', 'hyperframes', 'superpowers')]
  [string] $Tool = 'all',

  [string] $InstallRoot = (Join-Path $HOME '.ai-assistant-tools'),

  [string] $RepoRawBase = 'https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main',

  [switch] $SkipDependencies,

  [switch] $SkipWhasapoMcp,

  [string] $HermesSkills = ''
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

function Install-SkillReference {
  param([string] $Name, [string] $Source, [string] $Reference)
  $dest = Join-Path $HOME ".codex\skills\$Name\references"
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Get-UrlFile "$RepoRawBase/tools/$Source/skill/references/$Reference" (Join-Path $dest $Reference)
}

function Install-HermesSkill {
  param([string] $Name, [string] $Source)
  if (-not $HermesSkills) { return }
  $dest = Join-Path $HermesSkills $Name
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Get-UrlFile "$RepoRawBase/tools/$Source/skill/SKILL.md" (Join-Path $dest 'SKILL.md')
  Write-Host "Installed $Name Hermes skill to $dest"
}

function Install-HermesSkillReference {
  param([string] $Name, [string] $Source, [string] $Reference)
  if (-not $HermesSkills) { return }
  $dest = Join-Path $HermesSkills "$Name\references"
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Get-UrlFile "$RepoRawBase/tools/$Source/skill/references/$Reference" (Join-Path $dest $Reference)
}

function Ensure-GlobalAgentsNote {
  $agents = Join-Path $HOME '.codex\AGENTS.md'
  $marker = 'AI_ASSISTANT_TOOLS_RESEARCH_SKILLS'
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $agents) | Out-Null
  $block = @'

<!-- AI_ASSISTANT_TOOLS_RESEARCH_SKILLS -->
For scientific research and literature-review tasks, prefer the AI_Assistant_Tools research skills when installed:
- Use `academic-research` for literature discovery, review planning, paper reading, appraisal, Zotero/citation workflows, and scientific writing.
- Use `paper-fetch` / `paper-search` to download known PDFs and enrich DOI metadata.
- For initial discovery, run native search, Parallel search when configured, and paper-search in parallel when the review needs broad coverage.
- After selecting papers, make a todo list, screen papers, delegate reading when useful, write markdown paper summaries/topic extracts, build a synthesis matrix, then draft from evidence.
<!-- /AI_ASSISTANT_TOOLS_RESEARCH_SKILLS -->
'@
  if ((Test-Path -LiteralPath $agents) -and (Select-String -LiteralPath $agents -SimpleMatch $marker -Quiet)) {
    $text = Get-Content -Raw -LiteralPath $agents
    $pattern = '(?s)\r?\n?<!-- AI_ASSISTANT_TOOLS_RESEARCH_SKILLS -->.*?<!-- /AI_ASSISTANT_TOOLS_RESEARCH_SKILLS -->'
    $text = [regex]::Replace($text, $pattern, "`n$($block.Trim())")
    Set-Content -LiteralPath $agents -Value $text -Encoding UTF8
  } else {
    Add-Content -LiteralPath $agents -Value $block
  }
}

function Ensure-WhatsAppAgentsNote {
  $agents = Join-Path $HOME '.codex\AGENTS.md'
  $marker = 'AI_ASSISTANT_TOOLS_WHATSAPP'
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $agents) | Out-Null
  $block = @'

<!-- AI_ASSISTANT_TOOLS_WHATSAPP -->
For WhatsApp requests, use the global `whatsapp` skill when installed. On Linux prefer the local `wacli` CLI; on Windows use the local `wha` CLI backed by Whasapo. Never send unless I explicitly provide the exact recipient and exact message/file.
<!-- /AI_ASSISTANT_TOOLS_WHATSAPP -->
'@
  if ((Test-Path -LiteralPath $agents) -and (Select-String -LiteralPath $agents -SimpleMatch $marker -Quiet)) {
    $text = Get-Content -Raw -LiteralPath $agents
    $pattern = '(?s)\r?\n?<!-- AI_ASSISTANT_TOOLS_WHATSAPP -->.*?<!-- /AI_ASSISTANT_TOOLS_WHATSAPP -->'
    $text = [regex]::Replace($text, $pattern, "`n$($block.Trim())")
    Set-Content -LiteralPath $agents -Value $text -Encoding UTF8
  } else {
    Add-Content -LiteralPath $agents -Value $block
  }
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

function Get-YTFetcherPython {
  $candidates = @()
  if ($env:YTFETCHER_PYTHON) { $candidates += @($env:YTFETCHER_PYTHON) }
  $candidates += @('py -3.13', 'py -3.12', 'py -3.11', 'python')

  foreach ($candidate in $candidates) {
    $parts = $candidate -split ' ', 2
    $exe = $parts[0]
    $args = if ($parts.Count -gt 1) { $parts[1] } else { '' }
    $versionCheck = 'import sys; raise SystemExit(not ((3, 11) <= sys.version_info < (3, 14)))'
    try {
      if ($args) {
        $process = Start-Process -FilePath $exe -ArgumentList @($args, '-c', $versionCheck) -Wait -PassThru -WindowStyle Hidden -ErrorAction Stop
      } else {
        $process = Start-Process -FilePath $exe -ArgumentList @('-c', $versionCheck) -Wait -PassThru -WindowStyle Hidden -ErrorAction Stop
      }
      if ($process.ExitCode -eq 0) {
        return @{ Exe = $exe; Args = $args }
      }
    } catch {
      continue
    }
  }

  throw 'YTFetcher requires Python 3.11, 3.12, or 3.13. Set YTFETCHER_PYTHON to a compatible python.exe if needed.'
}

function Get-TubeScrapePython {
  $candidates = @()
  if ($env:TUBESCRAPE_PYTHON) { $candidates += @($env:TUBESCRAPE_PYTHON) }
  $candidates += @('py -3.13', 'py -3.12', 'py -3.11', 'py -3.10', 'python')

  foreach ($candidate in $candidates) {
    $parts = $candidate -split ' ', 2
    $exe = $parts[0]
    $args = if ($parts.Count -gt 1) { $parts[1] } else { '' }
    $versionCheck = 'import sys; raise SystemExit(not ((3, 10) <= sys.version_info < (3, 14)))'
    try {
      if ($args) {
        $process = Start-Process -FilePath $exe -ArgumentList @($args, '-c', $versionCheck) -Wait -PassThru -WindowStyle Hidden -ErrorAction Stop
      } else {
        $process = Start-Process -FilePath $exe -ArgumentList @('-c', $versionCheck) -Wait -PassThru -WindowStyle Hidden -ErrorAction Stop
      }
      if ($process.ExitCode -eq 0) {
        return @{ Exe = $exe; Args = $args }
      }
    } catch {
      continue
    }
  }

  throw 'TubeScrape requires Python 3.10, 3.11, 3.12, or 3.13. Set TUBESCRAPE_PYTHON to a compatible python.exe if needed.'
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
  Ensure-WhatsAppAgentsNote

  if (-not $SkipWhasapoMcp) {
    Write-Host 'MCP registration is no longer required for normal WhatsApp use. Use wha CLI commands.'
  }
  Write-Host 'Run: whasapo pair'
  Write-Host 'Then test: wha doctor'
}

function Install-Humanizer {
  Install-Skill 'humanizer' 'humanizer'
  Install-HermesSkill 'humanizer' 'humanizer'
  Get-UrlFile "$RepoRawBase/tools/humanizer/skill/LICENSE" (Join-Path $HOME '.codex\skills\humanizer\LICENSE')
  Write-Host 'Installed humanizer Codex skill.'
}

function Install-AcademicResearch {
  Install-Skill 'academic-research' 'academic-research'
  Install-SkillReference 'academic-research' 'academic-research' 'humanizer.md'
  Install-HermesSkill 'academic-research' 'academic-research'
  Install-HermesSkillReference 'academic-research' 'academic-research' 'humanizer.md'
  Ensure-GlobalAgentsNote
  Write-Host 'Installed academic-research Codex skill.'
}

function Install-SkillOnly {
  param([string] $Name)
  Install-Skill $Name $Name
  Install-HermesSkill $Name $Name
  Write-Host "Installed $Name Codex skill."
}

function Install-Hyperframes {
  Install-Skill 'hyperframes-helper' 'hyperframes'
  $config = Join-Path $HOME '.codex\config.toml'
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $config) | Out-Null
  $header = '[plugins."hyperframes@openai-curated"]'
  $text = if (Test-Path -LiteralPath $config) { Get-Content -Raw -LiteralPath $config } else { '' }

  if ($text.Contains($header)) {
    $pattern = '(?s)(\[plugins\."hyperframes@openai-curated"\]\r?\n)(.*?)(?=\r?\n\[|\z)'
    $text = [regex]::Replace($text, $pattern, {
      param($m)
      $body = $m.Groups[2].Value
      if ($body -match '(?m)^enabled\s*=') {
        $body = [regex]::Replace($body, '(?m)^enabled\s*=.*$', 'enabled = true')
      } else {
        $body = "enabled = true`n$body"
      }
      $m.Groups[1].Value + $body.TrimEnd() + "`n"
    })
  } else {
    if ($text -and -not $text.EndsWith("`n")) { $text += "`n" }
    $text += "`n[plugins.`"hyperframes@openai-curated`"]`nenabled = true`n"
  }

  Set-Content -LiteralPath $config -Value $text -Encoding UTF8
  Write-Host "Enabled HyperFrames plugin in $config"
  Write-Host 'Restart Codex Desktop. If the plugin does not appear, install HyperFrames from the Plugins UI.'
}

function Install-Superpowers {
  Install-Skill 'superpowers-helper' 'superpowers'
  $config = Join-Path $HOME '.codex\config.toml'
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $config) | Out-Null
  $header = '[plugins."superpowers@openai-curated"]'
  $text = if (Test-Path -LiteralPath $config) { Get-Content -Raw -LiteralPath $config } else { '' }

  if ($text.Contains($header)) {
    $pattern = '(?s)(\[plugins\."superpowers@openai-curated"\]\r?\n)(.*?)(?=\r?\n\[|\z)'
    $text = [regex]::Replace($text, $pattern, {
      param($m)
      $body = $m.Groups[2].Value
      if ($body -match '(?m)^enabled\s*=') {
        $body = [regex]::Replace($body, '(?m)^enabled\s*=.*$', 'enabled = true')
      } else {
        $body = "enabled = true`n$body"
      }
      $m.Groups[1].Value + $body.TrimEnd() + "`n"
    })
  } else {
    if ($text -and -not $text.EndsWith("`n")) { $text += "`n" }
    $text += "`n[plugins.`"superpowers@openai-curated`"]`nenabled = true`n"
  }

  Set-Content -LiteralPath $config -Value $text -Encoding UTF8
  Write-Host "Enabled Superpowers plugin in $config"
  Write-Host 'Restart Codex Desktop. If the plugin does not appear, install Superpowers from the Plugins UI.'
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
'@ | Set-Content -LiteralPath $envFile -Encoding ASCII
  }

  $shim = Join-Path $localBin 'paper-search.cmd'
  "@echo off`r`nset `"PAPER_SEARCH_MCP_ENV_FILE=$envFile`"`r`npython -m paper_search_mcp.cli %*`r`n" | Set-Content -LiteralPath $shim -Encoding ASCII

  Install-Skill 'paper-fetch' 'paper-fetch'
  Install-HermesSkill 'paper-fetch' 'paper-fetch'

  if (-not $SkipDependencies) {
    python -m pip install --upgrade 'git+https://github.com/Fr4nzz/paper-search-mcp.git@codex/fallback-download-improvements'
  }

  Write-Host 'Installed paper-search from Fr4nzz/paper-search-mcp.'
  Write-Host "Config file: $envFile"
  Write-Host "Installed PATH shim to $shim"
}

function Install-NotebookLM {
  Install-Skill 'notebooklm' 'notebooklm'
  Install-HermesSkill 'notebooklm' 'notebooklm'

  $localBin = Join-Path $HOME '.local\bin'
  New-Item -ItemType Directory -Force -Path $localBin | Out-Null

  if (-not $SkipDependencies) {
    python -m pip install --user --upgrade 'notebooklm-py[browser]'
  }

  $shim = Join-Path $localBin 'notebooklm.cmd'
  "@echo off`r`npython -c `"from notebooklm.notebooklm_cli import main; raise SystemExit(main())`" %*`r`n" | Set-Content -LiteralPath $shim -Encoding ASCII

  Write-Host 'Installed notebooklm-py and the NotebookLM Codex skill.'
  Write-Host "Installed PATH shim to $shim"
  Write-Host 'Run first-time auth with: notebooklm login'
  Write-Host 'If commands that used to work stop working, rerun this installer to update.'
}

function Install-YTFetcher {
  Install-Skill 'ytfetcher' 'ytfetcher'
  Install-HermesSkill 'ytfetcher' 'ytfetcher'

  $localBin = Join-Path $HOME '.local\bin'
  New-Item -ItemType Directory -Force -Path $localBin | Out-Null
  $venv = Join-Path $InstallRoot 'ytfetcher-venv'
  $venvPython = Join-Path $venv 'Scripts\python.exe'

  if (-not $SkipDependencies) {
    $python = Get-YTFetcherPython
    if (-not (Test-Path -LiteralPath $venvPython)) {
      if ($python.Args) {
        & $python.Exe $python.Args -m venv $venv
      } else {
        & $python.Exe -m venv $venv
      }
    }
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install --upgrade ytfetcher
  }

  $shim = Join-Path $localBin 'ytfetcher.cmd'
  "@echo off`r`n`"$venvPython`" -c `"from ytfetcher._cli import main; raise SystemExit(main())`" %*`r`n" | Set-Content -LiteralPath $shim -Encoding ASCII

  Write-Host 'Installed ytfetcher and the YTFetcher Codex skill.'
  Write-Host "Installed PATH shim to $shim"
}

function Install-TubeScrape {
  Install-Skill 'tubescrape' 'tubescrape'
  Install-HermesSkill 'tubescrape' 'tubescrape'

  $localBin = Join-Path $HOME '.local\bin'
  New-Item -ItemType Directory -Force -Path $localBin | Out-Null
  $venv = Join-Path $InstallRoot 'tubescrape-venv'
  $venvPython = Join-Path $venv 'Scripts\python.exe'

  if (-not $SkipDependencies) {
    $python = Get-TubeScrapePython
    if (-not (Test-Path -LiteralPath $venvPython)) {
      if ($python.Args) {
        & $python.Exe $python.Args -m venv $venv
      } else {
        & $python.Exe -m venv $venv
      }
    }
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install --upgrade 'tubescrape[cli]'
  }

  $shim = Join-Path $localBin 'tubescrape.cmd'
  $cli = Join-Path $venv 'Scripts\tubescrape.exe'
  "@echo off`r`n`"$cli`" %*`r`n" | Set-Content -LiteralPath $shim -Encoding ASCII

  Write-Host 'Installed tubescrape and the TubeScrape Codex skill.'
  Write-Host "Installed PATH shim to $shim"
}

$selected = if ($Tool -eq 'all') {
  @('gogcli', 'outlook', 'onedrive', 'd2l', 'whatsapp', 'humanizer', 'paper-fetch', 'academic-research', 'notebooklm', 'ytfetcher', 'tubescrape', 'hyperframes', 'superpowers')
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
    'paper-fetch' { Install-PaperFetch; Ensure-GlobalAgentsNote }
    'academic-research' { Install-AcademicResearch }
    'notebooklm' { Install-NotebookLM }
    'ytfetcher' { Install-YTFetcher }
    'tubescrape' { Install-TubeScrape }
    'hyperframes' { Install-Hyperframes }
    'superpowers' { Install-Superpowers }
  }
}

Write-Host ''
Write-Host 'Done. Restart Codex Desktop so new global skills and MCP servers are loaded.'

if ($HermesSkills) {
  Write-Host ''
  Write-Host "Hermes skills were also installed to $HermesSkills."
  Write-Host 'Restart your Hermes session or reload skills for them to take effect.'
}
