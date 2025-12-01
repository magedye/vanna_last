@echo off
REM ============================================================================
REM Project Command System Launcher - Windows
REM ============================================================================
REM Usage:
REM   run_listcmd.cmd              - Show all commands
REM   run_listcmd.cmd cat build    - Show build category
REM   run_listcmd.cmd search test  - Search for 'test'
REM   run_listcmd.cmd dry          - Dry run mode
REM ============================================================================

setlocal

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%listcmd.ps1"

if not exist "%PS_SCRIPT%" (
    echo Error: listcmd.ps1 not found in %SCRIPT_DIR%
    exit /b 1
)

REM Pass all arguments to PowerShell script
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%PS_SCRIPT%" %*

endlocal
