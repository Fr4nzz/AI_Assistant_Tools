param(
  [ValidateSet('all', 'gogcli', 'outlook', 'onedrive', 'd2l', 'whatsapp', 'humanizer', 'paper-fetch', 'academic-research', 'notebooklm', 'superpowers')]
  [string] $Tool = 'all'
)

Write-Warning 'install-guides.ps1 is deprecated. Use scripts/install.ps1 instead.'
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/Fr4nzz/AI_Assistant_Tools/main/scripts/install.ps1'))) -Tool $Tool -SkipDependencies
