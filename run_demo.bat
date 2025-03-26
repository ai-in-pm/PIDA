@echo off
echo Setting up environment...

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the demo
echo Running secure agent demonstration...
python secure_agent\demo.py

REM Deactivate virtual environment
echo Deactivating virtual environment...
call venv\Scripts\deactivate.bat

echo Done.
pause
