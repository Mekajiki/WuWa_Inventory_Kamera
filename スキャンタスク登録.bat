@echo off
rem 昇格ランナータスクを登録する(初回のみ実行、UACあり)
rem 登録後は UAC なしで "schtasks /run /tn WuWaKameraRunner" から
rem runner_cmd.txt に書いたスクリプトを昇格実行できる
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
schtasks /Create /F /TN "WuWaKameraRunner" /SC ONCE /ST 00:00 /RL HIGHEST ^
  /TR "cmd /c cd /d \"%~dp0.\" && .venv\Scripts\python.exe runner.py"
if %errorlevel% equ 0 (
    echo Task "WuWaKameraRunner" registered.
) else (
    echo Failed to register task.
)
pause
