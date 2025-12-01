<#
===============================================================================
  Project Command Management System - Windows Edition
  Version: 1.0.0
  Portable - No Install - No Admin - Project Folder Only
===============================================================================

USAGE:
  .\listcmd.ps1                    # Show all commands
  .\listcmd.ps1 cat build          # Show build category
  .\listcmd.ps1 search keyword     # Search commands
  .\listcmd.ps1 dry                # Dry run mode

FEATURES:
  - Category-based organization
  - Numeric selection
  - Safe execution with confirmation
  - Clipboard support (copy mode)
  - Logging all actions
  - No system modifications
  - Zero installation required

#>

Param(
    [string]$Action = "",
    [string]$Parameter = ""
)

# -----------------------------------------------------------------------------
# Configuration & Path Resolution
# -----------------------------------------------------------------------------
$Base = Split-Path -Parent $MyInvocation.MyCommand.Definition
$CmdFile  = Join-Path $Base "project_commands.txt"
$LogFile  = Join-Path $Base "project_commands.log"
$Sep = "::"

# Create files if they don't exist
if (!(Test-Path $CmdFile)) { 
    New-Item $CmdFile -ItemType File | Out-Null 
    Write-Host "Created $CmdFile - Add your commands there!" -ForegroundColor Yellow
}
if (!(Test-Path $LogFile)) { 
    New-Item $LogFile -ItemType File | Out-Null 
}

# -----------------------------------------------------------------------------
# Utility: Logging
# -----------------------------------------------------------------------------
function Write-CmdLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $user = $env:USERNAME
    $os = "Windows"
    Add-Content -Path $LogFile -Value "[$ts] [$os] ($user) [$Level] $Message"
}

# -----------------------------------------------------------------------------
# Parse Commands File
# -----------------------------------------------------------------------------
function Read-Commands {
    $group = "default"
    $cmds = @()
    $lineNum = 0

    try {
        foreach ($line in Get-Content $CmdFile -ErrorAction Stop) {
            $lineNum++
            $trim = $line.Trim()
            
            # Skip empty lines and comments
            if ($trim -eq "" -or $trim.StartsWith("#")) { continue }

            # Category header
            if ($trim -match "^\[(.+)\]$") {
                $group = $matches[1]
                continue
            }

            # Parse command line
            $p = $trim -split $Sep
            if ($p.Count -lt 2) {
                Write-CmdLog "Malformed command at line $lineNum`: $trim" "WARN"
                continue
            }

            $cmds += [pscustomobject]@{
                Group       = $group
                Command     = $p[0].Trim()
                Description = $p[1].Trim()
                Mode        = if ($p.Count -ge 3) { $p[2].Trim() } else { "exec" }
                Notes       = if ($p.Count -ge 4) { $p[3].Trim() } else { "" }
                LineNumber  = $lineNum
            }
        }
    }
    catch {
        Write-Host "Error reading commands file: $_" -ForegroundColor Red
        Write-CmdLog "Error reading commands file: $_" "ERROR"
    }

    return $cmds
}

# -----------------------------------------------------------------------------
# Execution Engine
# -----------------------------------------------------------------------------
function Execute-Entry {
    param(
        [pscustomobject]$Entry,
        [switch]$DryRun
    )

    if ($DryRun) {
        Write-Host "`n[DRY RUN MODE]" -ForegroundColor Yellow
        Write-Host "Would execute: $($Entry.Command)" -ForegroundColor Cyan
        Write-Host "Mode: $($Entry.Mode)" -ForegroundColor Gray
        if ($Entry.Notes) {
            Write-Host "Note: $($Entry.Notes)" -ForegroundColor Gray
        }
        return
    }

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Selected Command:" -ForegroundColor Cyan
    Write-Host "$($Entry.Command)" -ForegroundColor White
    Write-Host "Description: $($Entry.Description)" -ForegroundColor Gray
    Write-Host "Mode: $($Entry.Mode)" -ForegroundColor Gray
    if ($Entry.Notes) {
        Write-Host "Note: $($Entry.Notes)" -ForegroundColor Yellow
    }
    Write-Host "========================================" -ForegroundColor Cyan

    # Confirmation for exec mode
    if ($Entry.Mode.ToLower() -eq "exec") {
        $confirm = Read-Host "`nExecute this command? (y/n)"
        if ($confirm -ne "y") {
            Write-Host "Cancelled." -ForegroundColor Yellow
            Write-CmdLog "Cancelled: $($Entry.Command)" "INFO"
            return
        }
    }

    try {
        switch ($Entry.Mode.ToLower()) {
            "copy" {
                Set-Clipboard $Entry.Command
                Write-Host "`n✓ Copied to clipboard." -ForegroundColor Green
                Write-CmdLog "Copied: $($Entry.Command)" "INFO"
            }
            "show" {
                Write-Host "`n$($Entry.Command)" -ForegroundColor Green
                Write-CmdLog "Shown: $($Entry.Command)" "INFO"
            }
            "exec" {
                Write-Host "`nExecuting..." -ForegroundColor Cyan
                $result = Invoke-Expression $Entry.Command 2>&1
                $exitCode = $LASTEXITCODE
                Write-Host "`n✓ Command completed (Exit code: $exitCode)" -ForegroundColor Green
                Write-CmdLog "Executed: $($Entry.Command) [Exit: $exitCode]" "INFO"
            }
            default {
                Write-Host "Unknown mode: $($Entry.Mode)" -ForegroundColor Red
                Write-CmdLog "Unknown mode $($Entry.Mode) for: $($Entry.Command)" "ERROR"
            }
        }
    }
    catch {
        Write-Host "`n✗ Error: $_" -ForegroundColor Red
        Write-CmdLog "Error executing $($Entry.Command): $_" "ERROR"
    }
}

# -----------------------------------------------------------------------------
# Command Selection Menu
# -----------------------------------------------------------------------------
function Show-Numeric {
    param([array]$Entries)

    if ($Entries.Count -eq 0) {
        Write-Host "`nNo commands found." -ForegroundColor Yellow
        return $null
    }

    Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║              PROJECT COMMAND MANAGEMENT SYSTEM                       ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""

    $currentGroup = ""
    $i = 1
    
    foreach ($e in $Entries) {
        # Print category header when group changes
        if ($e.Group -ne $currentGroup) {
            Write-Host "`n[$($e.Group.ToUpper())]" -ForegroundColor Yellow
            $currentGroup = $e.Group
        }
        
        $modeColor = switch ($e.Mode) {
            "exec" { "Green" }
            "copy" { "Cyan" }
            "show" { "Magenta" }
            default { "White" }
        }
        
        Write-Host "  [$i] " -NoNewline -ForegroundColor White
        Write-Host "$($e.Command)" -NoNewline -ForegroundColor $modeColor
        Write-Host " — $($e.Description)" -ForegroundColor Gray
        $i++
    }

    Write-Host ""
    $sel = Read-Host "Enter number (or 'q' to quit)"
    
    if ($sel -eq 'q') {
        Write-Host "Goodbye!" -ForegroundColor Cyan
        return $null
    }
    
    if ($sel -match '^\d+$' -and $sel -ge 1 -and $sel -le $Entries.Count) {
        return $Entries[$sel - 1]
    }

    Write-Host "Invalid selection." -ForegroundColor Red
    return $null
}

# -----------------------------------------------------------------------------
# Main Entry Function
# -----------------------------------------------------------------------------
function Invoke-ListCmd {
    param(
        [string]$FilterCategory,
        [switch]$Search,
        [switch]$Dry
    )

    Write-CmdLog "Started - Action: $(if ($Search) {'Search'} elseif ($Dry) {'Dry'} else {'List'}), Filter: $FilterCategory" "INFO"

    $entries = Read-Commands

    if ($entries.Count -eq 0) {
        Write-Host "`nNo commands found in $CmdFile" -ForegroundColor Yellow
        Write-Host "Add commands in the format: command :: description :: mode" -ForegroundColor Gray
        return
    }

    # Apply filters
    if ($FilterCategory) {
        if ($Search) {
            # Search mode
            $entries = $entries | Where-Object {
                $_.Command -like "*$FilterCategory*" -or
                $_.Description -like "*$FilterCategory*" -or
                $_.Group -like "*$FilterCategory*"
            }
            if ($entries.Count -eq 0) {
                Write-Host "`nNo matches found for: $FilterCategory" -ForegroundColor Yellow
                return
            }
            Write-Host "`nFound $($entries.Count) match(es) for: $FilterCategory" -ForegroundColor Green
        }
        else {
            # Category filter
            $entries = $entries | Where-Object { $_.Group -eq $FilterCategory }
            if ($entries.Count -eq 0) {
                Write-Host "`nNo commands in category: $FilterCategory" -ForegroundColor Yellow
                return
            }
        }
    }

    $selected = Show-Numeric $entries
    if ($selected) {
        Execute-Entry $selected -DryRun:$Dry
    }
}

# -----------------------------------------------------------------------------
# Dispatcher (Action Handler)
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "Vanna Insight Engine - Command System v1.0.0" -ForegroundColor Cyan
Write-Host "OS: Windows | User: $env:USERNAME" -ForegroundColor Gray
Write-Host ""

switch ($Action.ToLower()) {
    "search" { 
        Invoke-ListCmd $Parameter -Search
        break 
    }
    "dry" { 
        Invoke-ListCmd $Parameter -Dry
        break 
    }
    "cat" { 
        Invoke-ListCmd $Parameter
        break 
    }
    "" { 
        Invoke-ListCmd
        break 
    }
    default { 
        Write-Host "Unknown action: $Action" -ForegroundColor Red
        Write-Host "Valid actions: search, dry, cat" -ForegroundColor Gray
        break 
    }
}

Write-Host ""
