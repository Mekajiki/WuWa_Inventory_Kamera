@echo off
rem スキル/チェーンのポップアップ撮影(要: ゲームで共鳴者画面を開いた状態)
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"
set PYTHONUTF8=1
.venv\Scripts\python.exe capture_popups.py > popups_result.txt 2>&1
type popups_result.txt
pause
