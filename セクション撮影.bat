@echo off
rem 共鳴者画面の各セクションを自動撮影する(要: ゲームで共鳴者画面を開いた状態)
rem 管理者権限がなければ自動昇格する
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"
set PYTHONUTF8=1
.venv\Scripts\python.exe capture_sections.py > sections_result.txt 2>&1
type sections_result.txt
pause
