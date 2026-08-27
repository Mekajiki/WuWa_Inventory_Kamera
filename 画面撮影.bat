@echo off
rem 今のゲーム画面を1枚撮影する(fullshot_連番.png に保存)
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"
set PYTHONUTF8=1
.venv\Scripts\python.exe capture_single.py
pause
