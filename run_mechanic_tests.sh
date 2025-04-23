#!/bin/bash

# Run Mechanic Tests
# This script runs the lightweight mechanic tests that generate visual logs
# for individual game mechanics.

echo "Running mechanic tests..."
echo "Logs will be stored in logs/mechanic_tests/"

# Create log directories if they don't exist
mkdir -p logs/mechanic_tests/{movement,combat,ai,objectives,events,unit,misc}

# Run tests with pytest
python -m pytest tests/mechanic_tests/test_movement_mechanics.py -v
python -m pytest tests/mechanic_tests/test_combat_mechanics.py -v
python -m pytest tests/mechanic_tests/test_ai_mechanics.py -v
python -m pytest tests/mechanic_tests/test_objective_mechanics.py -v
python -m pytest tests/mechanic_tests/test_event_mechanics.py -v

# Uncomment these as more tests are added
# python -m pytest tests/mechanic_tests/test_unit_mechanics.py -v
# python -m pytest tests/mechanic_tests/test_misc_mechanics.py -v

echo ""
echo "Tests completed. Check the log files in logs/mechanic_tests/"
echo "Movement logs: logs/mechanic_tests/movement/"
echo "Combat logs: logs/mechanic_tests/combat/"
echo "AI logs: logs/mechanic_tests/ai/"
echo "Objective logs: logs/mechanic_tests/objectives/"
echo "Event logs: logs/mechanic_tests/events/" 