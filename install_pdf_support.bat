@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=0
title Astro Destiny Analyzer — Install PDF Support
cd /d "%~dp0"

echo ============================================================
echo   Install PDF Support (WeasyPrint)
echo   安裝 PDF 匯出支援（WeasyPrint）
echo ============================================================
echo.
echo   注意：WeasyPrint 在 Windows 上可能需要 GTK / Pango 系統依賴。
echo   若安裝後仍無法匯出 PDF，建議改用 HTML 或 Word 格式。
echo.

rem ── Check for .venv ───────────────────────────────────────────────────────
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] 找不到 .venv，請先執行 setup.bat 完成基本安裝。
    pause
    exit /b 1
)
set PYTHON_EXE=.venv\Scripts\python.exe

rem ── Install weasyprint ────────────────────────────────────────────────────
echo [1/2] Installing WeasyPrint...
"%PYTHON_EXE%" -m pip install weasyprint
if %errorlevel% neq 0 (
    echo [ERROR] WeasyPrint 安裝失敗。
    echo         WeasyPrint Python 套件或 Windows GTK/Pango 系統依賴不足；
    echo         可先使用 HTML 或 Word 匯出。
    pause
    exit /b 1
)
echo.

rem ── Verify import ─────────────────────────────────────────────────────────
echo [2/2] Verifying WeasyPrint...
"%PYTHON_EXE%" -c "import weasyprint; print('WeasyPrint OK')"
if %errorlevel% neq 0 (
    echo [WARN] WeasyPrint Python 套件或 Windows GTK/Pango 系統依賴不足；
    echo        可先使用 HTML 或 Word 匯出。
    pause
    exit /b 1
)
echo.

echo ============================================================
echo   WeasyPrint 安裝成功，PDF 匯出功能已啟用。
echo   重新啟動 run.bat 即可使用 PDF 匯出。
echo ============================================================
pause
