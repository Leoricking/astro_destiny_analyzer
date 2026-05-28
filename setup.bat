@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=0
title Astro Destiny Analyzer Setup
cd /d "%~dp0"

echo ============================================================
echo   Astro Destiny Analyzer Setup
echo   第一次使用請執行本腳本，之後雙擊 run.bat 即可啟動。
echo ============================================================
echo.

rem ── [1/4] Check Python ───────────────────────────────────────────────────
echo [1/4] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 找不到 Python，請先安裝 Python 3.10+
    echo         下載：https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo        %%v
echo.

rem ── [2/4] Create virtual environment ──────────────────────────────────────
echo [2/4] Creating virtual environment (.venv)...
if exist ".venv\Scripts\python.exe" (
    echo        .venv already exists, skipping.
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] 虛擬環境建立失敗。請確認 Python 版本 >= 3.10。
        pause
        exit /b 1
    )
    echo        OK: .venv created
)
echo.

rem ── [3/4] Install dependencies ────────────────────────────────────────────
echo [3/4] Installing dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo [ERROR] pip upgrade 失敗。
    pause
    exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] 套件安裝失敗。請確認 requirements.txt 存在且網路正常。
    pause
    exit /b 1
)
echo.

rem ── [4/4] Check environment ───────────────────────────────────────────────
echo [4/4] Checking environment...
.venv\Scripts\python.exe scripts\check_env.py
if %errorlevel% neq 0 (
    echo [WARN] 環境檢查發現問題，請確認必要套件已安裝。
    pause
    exit /b 1
)
echo.

echo ============================================================
echo   安裝完成，之後可雙擊 run.bat 啟動。
echo ============================================================
pause
