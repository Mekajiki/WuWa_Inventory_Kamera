@echo off
rem スキャン用の最上位権限タスクを登録する(初回のみ実行、UACあり)
rem 登録後は UAC なしで "schtasks /run /tn WuWaKameraScan" からスキャン実行可能
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
schtasks /Create /F /TN "WuWaKameraScan" /SC ONCE /ST 00:00 /RL HIGHEST ^
  /TR "cmd /c cd /d \"%~dp0.\" && set PYTHONUTF8=1&& .venv\Scripts\python.exe scan_cli.py > scan_cli_out.txt 2>&1"
if %errorlevel% equ 0 (
    echo Task "WuWaKameraScan" registered.
) else (
    echo Failed to register task.
)
pause
