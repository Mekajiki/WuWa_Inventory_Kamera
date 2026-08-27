@echo off
rem フォーク版 WuWa Inventory Kamera をソースから管理者権限で起動する
rem (%~dp0 の末尾バックスラッシュが引用符を壊すため "." を付けて回避)
powershell -NoProfile -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c cd /d \"%~dp0.\" && set PYTHONUTF8=1&& .venv\Scripts\pythonw.exe main.py'"
