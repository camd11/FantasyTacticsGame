#!/bin/bash
# Fantasy Tactics Game Launcher
# This script sets up the environment and launches the game options

echo "Fantasy Tactics Game Launcher"
echo "============================"

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    chmod +x setup_venv.sh
    ./setup_venv.sh
else
    echo "Activating existing virtual environment..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows with Git Bash
        source venv/Scripts/activate
    else
        # Unix-like systems
        source venv/bin/activate
    fi
fi

# Launch the options menu
python run_options.py

# Deactivate virtual environment when done
deactivate

echo "Launcher completed." 