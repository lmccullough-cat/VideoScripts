@echo off
REM Wrapper script to call Get-FileVersion.ps1 from CMD or Git Bash
REM Usage: fileversion <filepath>

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: fileversion ^<filepath^>
    exit /b 1
)

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Call PowerShell script with the provided argument
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Get-FileVersion.ps1" "%~1"

exit /b %ERRORLEVEL%
