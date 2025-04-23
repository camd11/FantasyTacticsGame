#!/bin/bash

# Set script path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Setup Python path
export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH

# Create log directory if it doesn't exist
LOG_DIR="$PROJECT_ROOT/logs/mechanic_tests/combat"
mkdir -p "$LOG_DIR"

echo "Running combat mechanics tests..."

# Run the combat mechanics test
python "$SCRIPT_DIR/test_combat_mechanics.py"

# Check result
if [ $? -eq 0 ]; then
    echo "Combat mechanics test completed successfully!"
    echo "Logs saved to: $LOG_DIR"
else
    echo "Combat mechanics test failed!"
    exit 1
fi

echo "All combat mechanics tests completed."
exit 0 