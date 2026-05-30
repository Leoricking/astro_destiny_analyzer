@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "EXE=%SCRIPT_DIR%AstroDestinyAnalyzer.exe"

if not exist "%EXE%" (
    echo [ERROR] AstroDestinyAnalyzer.exe not found.
    echo Please ensure the package is fully extracted and intact.
    echo Contact support if the problem persists.
    echo.
    pause
    exit /b 1
)

echo Starting Astro Destiny Analyzer (Protected Trial)...
start "" "%EXE%"
