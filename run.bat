@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=0
set ASTRO_CUSTOMER_MODE=1
set ASTRO_SHOW_DEMO_DATA=0
title Astro Destiny Analyzer Launcher
cd /d "%~dp0"

echo ============================================================
echo   Astro Destiny Analyzer Launcher
echo ============================================================
echo.

rem ── [1/5] Check Python ───────────────────────────────────────────────────
echo [1/5] Checking Python...
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    echo        OK: using .venv\Scripts\python.exe
    goto :step2
)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 找不到 Python，請先安裝 Python 3.10+
    echo         下載：https://www.python.org/downloads/
    pause
    exit /b 1
)
set PYTHON_EXE=python
echo        OK: using system python
echo.

rem ── [2/5] Create virtual environment ──────────────────────────────────────
:step2
echo.
echo [2/5] Creating virtual environment...
if exist ".venv\Scripts\python.exe" (
    echo        .venv already exists, skipping.
    goto :step3
)
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] 虛擬環境建立失敗。請確認 Python 版本 >= 3.10。
    pause
    exit /b 1
)
echo        OK: .venv created

:step3
set PYTHON_EXE=.venv\Scripts\python.exe
echo.

rem ── [3/5] Install / update dependencies ──────────────────────────────────
echo [3/5] Installing dependencies...
"%PYTHON_EXE%" -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo [ERROR] pip upgrade 失敗。
    pause
    exit /b 1
)
"%PYTHON_EXE%" -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] 套件安裝失敗。請確認 requirements.txt 存在且網路正常。
    pause
    exit /b 1
)
echo        OK: dependencies installed
echo.

rem ── [4/5] Check environment ───────────────────────────────────────────────
echo [4/5] Checking environment...
"%PYTHON_EXE%" scripts\check_env.py
if %errorlevel% neq 0 (
    echo [ERROR] 環境檢查未通過，請確認必要套件已安裝。
    pause
    exit /b 1
)
echo.

rem ── [5/5] Launch Streamlit ────────────────────────────────────────────────
echo [5/5] Launching Streamlit...
echo        開啟瀏覽器：http://localhost:8501
echo        按 Ctrl+C 可停止服務
echo.
"%PYTHON_EXE%" -m streamlit run ui\streamlit_app.py
if %errorlevel% neq 0 (
    echo [ERROR] Streamlit 啟動失敗。請確認 streamlit 已安裝。
    pause
    exit /b 1
)
