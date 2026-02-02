@echo off
cd /d "%~dp0"
cd..
call .venv\Scripts\activate.bat
cd desktop-app
python main.py
pause
