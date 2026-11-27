<#
.SYNOPSIS
  Runs the /auto-apply batch headless (or -Interactive to watch it in a Claude Code session).

.EXAMPLE
  powershell -File tools\run_auto_apply.ps1              # mode from config.json (dry run until you flip it)
  powershell -File tools\run_auto_apply.ps1 -DryRun -Max 3
  powershell -File tools\run_auto_apply.ps1 -Live
  powershell -File tools\run_auto_apply.ps1 -Interactive  # opens Claude Code with the Playwright MCP loaded
#>
param(
  [switch]$DryRun,
  [switch]$Live,
  [int]$Max = 0,
  [switch]$Interactive
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
$env:Path = "$env:ProgramFiles\nodejs;$env:Path"
$env:TRANSFORMERS_VERBOSITY = 'error'
$env:HF_HUB_DISABLE_PROGRESS_BARS = '1'

$mcp = Join-Path $repo '.claude\skills\auto-apply\mcp.json'
$prompt = '/auto-apply'
if ($DryRun) { $prompt += ' --dry-run' }
if ($Live) { $prompt += ' --live' }
if ($Max -gt 0) { $prompt += " --max $Max" }

$allowed = @(
  'mcp__playwright',
  'mcp__claude_ai_Google_Sheets__get_values',
  'mcp__claude_ai_Google_Sheets__get_spreadsheet',
  'mcp__claude_ai_Google_Sheets__update_values',
  'mcp__claude_ai_Google_Sheets__append_values',
  'mcp__claude_ai_Google_Sheets__update_spreadsheet',
  'mcp__claude_ai_Gmail__search_threads',
  'mcp__claude_ai_Gmail__get_thread',
  'WebFetch', 'WebSearch', 'Read', 'Glob', 'Grep', 'Skill(auto-apply)',
  'Write(documents/auto-apply/**)', 'Edit(documents/auto-apply/**)',
  'Bash(python tools/auto_apply.py:*)',
  'Bash(~/.venvs/ai-detector/Scripts/python tools/ai_detector.py:*)',
  'Bash(mkdir -p documents/auto-apply:*)'
)
$denied = @(
  'mcp__claude_ai_Gmail__send_message', 'mcp__claude_ai_Gmail__reply', 'mcp__claude_ai_Gmail__forward',
  'mcp__claude_ai_Gmail__create_draft', 'mcp__claude_ai_Gmail__trash_message', 'mcp__claude_ai_Gmail__trash_thread',
  'mcp__claude_ai_Google_Sheets__batch_clear_values', 'mcp__claude_ai_Google_Drive__trash_file',
  'mcp__claude_ai_Google_Drive__share_file'
)

if ($Interactive) {
  claude --mcp-config $mcp --allowedTools $allowed --disallowedTools $denied
  exit $LASTEXITCODE
}

$logDir = Join-Path $repo 'documents\auto-apply\logs'
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir ("run_{0}.log" -f (Get-Date -Format 'yyyy-MM-dd_HHmm'))
"[$(Get-Date -Format s)] $prompt" | Out-File $log -Encoding utf8
claude -p $prompt --mcp-config $mcp --allowedTools $allowed --disallowedTools $denied 2>&1 |
  Tee-Object -FilePath $log -Append
exit $LASTEXITCODE
