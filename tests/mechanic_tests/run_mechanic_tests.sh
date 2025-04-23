#!/bin/bash

# Script to run all mechanic tests
# This script runs all of the individual mechanic tests in the tests/mechanic_tests/ directory

# Create logs directory if it doesn't exist
mkdir -p logs/mechanic_tests

echo "Running mechanic tests..."

# Run unit mechanic tests
echo "Running unit mechanic tests..."
bash tests/mechanic_tests/unit_mechanics/run_unit_mechanics_tests.sh

# Run movement mechanic tests
echo "Running movement mechanic tests..."
python tests/mechanic_tests/movement/test_movement_mechanics.py

# Run combat mechanic tests 
echo "Running combat mechanic tests..."
python tests/mechanic_tests/combat/test_combat_mechanics.py

# Run inventory mechanic tests
echo "Running inventory mechanic tests..."
python tests/mechanic_tests/inventory/test_inventory_mechanics.py

# Run status effect mechanic tests
echo "Running status effect mechanic tests..."
python tests/mechanic_tests/status_effects/test_status_effect_mechanics.py

echo "All mechanic tests completed!"
echo "Logs available in logs/mechanic_tests/ directory" 