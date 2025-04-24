@echo off
REM Setup virtual environment for the Fantasy Tactics Game
REM This script creates a virtual environment and installs required dependencies

SET VENV_DIR=venv

REM Create virtual environment if it doesn't exist
IF NOT EXIST %VENV_DIR% (
    echo Creating virtual environment in %VENV_DIR%...
    python -m venv %VENV_DIR%
    echo Virtual environment created!
) ELSE (
    echo Virtual environment already exists in %VENV_DIR%
)

REM Activate virtual environment
call %VENV_DIR%\Scripts\activate.bat

REM Install required packages
echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete! Virtual environment is now active.
echo To deactivate the virtual environment, run 'deactivate'
echo To activate the environment in the future, run:
echo %VENV_DIR%\Scripts\activate.bat 