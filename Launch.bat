@echo off
REM Fantasy Tactics Game Launcher
REM This batch file sets up the environment and launches the game options

echo Fantasy Tactics Game Launcher
echo ============================

REM Check if venv exists, create if not
IF NOT EXIST venv (
    echo Setting up virtual environment...
    call setup_venv.bat
) ELSE (
    echo Activating existing virtual environment...
    call venv\Scripts\activate.bat
)

REM Launch the options menu
python run_options.py

REM Deactivate virtual environment when done
call deactivate

echo Launcher completed. 