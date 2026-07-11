@echo off
cd /d "%~dp0"
start "Robot AI Server" cmd /k ".venv\Scripts\python.exe web_app.py"
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:8000"
