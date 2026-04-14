@echo off
REM run.bat - Run PyClaw (Windows)

cd /d "%~dp0"

if not exist venv (
    call "%~dp0setup.bat"
)

call venv\Scripts\activate.bat
python main.py %*
