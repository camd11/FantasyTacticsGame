#!/bin/bash

# Setup virtual environment for the Fantasy Tactics Game
# This script creates a virtual environment and installs required dependencies

# Exit on any error
set -e

VENV_DIR="venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python -m venv $VENV_DIR
    echo "Virtual environment created!"
else
    echo "Virtual environment already exists in $VENV_DIR"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows with Git Bash
    source $VENV_DIR/Scripts/activate
else
    # Unix-like systems
    source $VENV_DIR/bin/activate
fi

# Install required packages
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete! Virtual environment is now active."
echo "To deactivate the virtual environment, run 'deactivate'"
echo "To activate the environment in the future, run:"
echo "source $VENV_DIR/Scripts/activate (on Windows with Git Bash)"
echo "source $VENV_DIR/bin/activate (on Unix-like systems)" 