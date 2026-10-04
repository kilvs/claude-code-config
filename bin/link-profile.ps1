# Wire a Claude Code profile (config dir) to this AI Agent Config folder. Safe to rerun.
# Usage (PowerShell):  .\bin\link-profile.ps1                     wires $HOME\.claude
#                      .\bin\link-profile.ps1 $HOME\.claude-work   wires a second profile
# Needs Developer Mode on (Settings > System > For developers) so files can be symlinked.
param([string]$ConfigDir = (Join-Path $HOME '.claude'))
$ErrorActionPreference = 'Stop'
$R = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$P = $ConfigDir.TrimEnd('\', '/')
$Sup = Join-Path $R 'settings\superseded'
$Stamp = Get-Date -Format 'yyyy-MM-dd'
$Name = Split-Path $P -Leaf
foreach ($d in @($P, (Join-Path $P 'skills'), $Sup)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

if (-not ('Win32.Link' -as [type])) { Add-Type -Namespace Win32 -Name Link -MemberDefinition @'
[DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
public static extern bool CreateSymbolicLink(string link, string target, int flags);
'@ }

function Get-Existing($path) { Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue }

# A real file or folder found where a link should go is moved aside, never deleted.
function Move-Aside($dest) {
  $to = Join-Path $Sup "$Name-$(Split-Path $dest -Leaf)-$Stamp"
  $n = 1; $base = $to
  while (Get-Existing $to) { $to = "$base-$n"; $n++ }
  Move-Item -LiteralPath $dest -Destination $to
  Write-Host "  moved aside: $dest -> $to"
}

# Link-Item <target> <path> <Junction|SymbolicLink>
function Link-Item($target, $dest, $type) {
  $item = Get-Existing $dest
  if ($item -and $item.LinkType -and (@($item.Target)[0] -eq $target)) { return }
  if ($item) { Move-Aside $dest }
  if ($type -eq 'Junction') {
    New-Item -ItemType Junction -Path $dest -Target $target | Out-Null   # junctions need no admin
  } elseif (-not [Win32.Link]::CreateSymbolicLink($dest, $target, 2)) {   # 2 = allowed in Developer Mode
    throw "Could not link $dest. Turn on Developer Mode (Settings > System > For developers) or run PowerShell as administrator, then rerun this script."
  }
  Write-Host "  linked: $dest"
}

Write-Host "Wiring $P"
Link-Item (Join-Path $R 'CLAUDE.md') (Join-Path $P 'CLAUDE.md') 'SymbolicLink'
Link-Item (Join-Path $R 'settings\settings.json') (Join-Path $P 'settings.json') 'SymbolicLink'
Get-ChildItem -LiteralPath (Join-Path $R 'skills') -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } | ForEach-Object {
  Link-Item $_.FullName (Join-Path $P "skills\$($_.Name)") 'Junction'
}

# Auto memory lives in $R\memory for every profile.
$settingsFile = Join-Path $R 'settings\settings.json'
$settings = Get-Content -Raw -LiteralPath $settingsFile | ConvertFrom-Json
$mem = (Join-Path $R 'memory') -replace '\\', '/'
if ($settings.autoMemoryDirectory -ne $mem) {
  $settings | Add-Member -NotePropertyName autoMemoryDirectory -NotePropertyValue $mem -Force
  [IO.File]::WriteAllText($settingsFile, ($settings | ConvertTo-Json -Depth 20) + "`n")
  Write-Host "  autoMemoryDirectory: $mem"
}

# User-scope MCP servers: add any missing ones (never overwrite). The default profile keeps
# them in $HOME\.claude.json; a profile started with CLAUDE_CONFIG_DIR keeps them inside its dir.
$cfg = if ($P -eq (Join-Path $HOME '.claude')) { Join-Path $HOME '.claude.json' } else { Join-Path $P '.claude.json' }
$conf = if (Test-Path -LiteralPath $cfg) { Get-Content -Raw -LiteralPath $cfg | ConvertFrom-Json } else { [pscustomobject]@{} }
if (-not $conf.PSObject.Properties['mcpServers']) { $conf | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{}) }
$want = (Get-Content -Raw -LiteralPath (Join-Path $R 'settings\mcp-servers.json') | ConvertFrom-Json).mcpServers
$added = @()
foreach ($s in $want.PSObject.Properties) {
  if (-not $conf.mcpServers.PSObject.Properties[$s.Name]) {
    $conf.mcpServers | Add-Member -NotePropertyName $s.Name -NotePropertyValue $s.Value; $added += $s.Name
  }
}
if ($added.Count) {
  [IO.File]::WriteAllText($cfg, ($conf | ConvertTo-Json -Depth 50))
  Write-Host "  mcp servers added: $($added -join ', ')"
} else { Write-Host '  mcp servers: already present' }
Write-Host 'Done. Start claude, run /mcp once to log in to the MCP servers.'
