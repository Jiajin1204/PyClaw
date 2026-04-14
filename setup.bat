@echo off
REM setup.bat - Create virtual environment and install dependencies (Windows)

cd /d "%~dp0"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete! Activate with: venv\Scripts\activate.bat
echo Run PyClaw with: python main.py
