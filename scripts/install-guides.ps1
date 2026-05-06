param(
  [ValidateSet('all', 'google-workspace', 'outlook', 'onedrive', 'd2l', 'whatsapp')]
  [string] $Tool = 'all',

  [string] $Destination = (Join-Path $HOME 'Documents\AI_Assistant_Tools'),

  [string] $RepoRawBase = 'https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main'
)

$ErrorActionPreference = 'Stop'

$guides = [ordered]@{
  'google-workspace' = 'google-workspace-cli-regenerator-windows-codex.md'
  'outlook' = 'outlook-cli-regenerator-windows-codex.md'
  'onedrive' = 'onedrive-cli-regenerator-windows-codex.md'
  'd2l' = 'd2l-cli-regenerator-windows-codex.md'
  'whatsapp' = 'whasapo-whatsapp-mcp-regenerator-windows-codex.md'
}

if ($Tool -eq 'all') {
  $selected = @($guides.Keys)
} else {
  $selected = @($Tool)
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null

foreach ($name in $selected) {
  $file = $guides[$name]
  $url = "$RepoRawBase/guides/$file"
  $target = Join-Path $Destination $file
  Write-Host "Downloading $name guide..."
  Invoke-WebRequest -Uri $url -OutFile $target
  Write-Host "  $target"
}

Write-Host ''
Write-Host "Downloaded $($selected.Count) guide(s) to $Destination"
Write-Host 'Open the Markdown file for the tool you want to set up and follow it step by step.'
Write-Host 'Do not commit or share OAuth secrets, browser profiles, tokens, cookies, or local message databases.'

