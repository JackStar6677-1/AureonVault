@echo off
setlocal EnableExtensions
cd /d "%~dp0"
pythonw app.py
if errorlevel 1 (
  python app.py
)
endlocal
