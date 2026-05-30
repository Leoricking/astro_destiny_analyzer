@echo off
chcp 65001 >nul
setlocal

set "SCRIPT_DIR=%~dp0"
set "EXE=%SCRIPT_DIR%AstroDestinyAnalyzer\AstroDestinyAnalyzer.exe"

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONLEGACYWINDOWSSTDIO=0"

set "ASTRO_CUSTOMER_MODE=1"
set "ASTRO_CONSULTANT_MODE=0"
set "ASTRO_DEVELOPER_MODE=0"
set "ASTRO_TRIAL_MODE=1"
set "ASTRO_PORTABLE_MODE=1"
set "ASTRO_BUILD_PROFILE=protected_trial"

set "PORT="
set "STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false"
set "STREAMLIT_SERVER_PORT=8501"
set "STREAMLIT_SERVER_ADDRESS=127.0.0.1"
set "STREAMLIT_BROWSER_SERVER_PORT=8501"
set "STREAMLIT_BROWSER_SERVER_ADDRESS=127.0.0.1"
set "STREAMLIT_BROWSER_GATHER_USAGE_STATS=false"
set "STREAMLIT_SERVER_HEADLESS=true"

title Astro Destiny Analyzer - Protected Trial

if not exist "%EXE%" (
    echo [ERROR] AstroDestinyAnalyzer.exe not found.
    echo Expected: %EXE%
    echo.
    echo Please ensure the package is fully extracted and intact.
    echo Contact support if the problem persists.
    echo.
    pause
    exit /b 1
)

echo Starting Astro Destiny Analyzer...
echo.
echo If the browser does not open automatically, go to:
echo http://127.0.0.1:8501
echo.

"%EXE%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] Application exited with error code %EXIT_CODE%.
    echo.
    pause
    exit /b %EXIT_CODE%
)

pause
