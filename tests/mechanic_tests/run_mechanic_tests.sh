#!/bin/bash

# Create log directories
mkdir -p logs/mechanic_tests/movement
mkdir -p logs/mechanic_tests/combat
mkdir -p logs/mechanic_tests/ai
mkdir -p logs/mechanic_tests/objectives
mkdir -p logs/mechanic_tests/events
mkdir -p logs/mechanic_tests/units
mkdir -p logs/mechanic_tests/misc

echo "Created log directories"

# Run movement mechanic tests
echo "Running movement mechanic tests..."
python -m pytest tests/mechanic_tests/test_movement_mechanics.py -v

# Run combat mechanic tests
echo "Running combat mechanic tests..."
python -m pytest tests/mechanic_tests/test_combat_mechanics.py -v

# Run AI mechanic tests
echo "Running AI mechanic tests..."
python -m pytest tests/mechanic_tests/test_ai_mechanics.py -v

# Run objective mechanic tests
echo "Running objective mechanic tests..."
python -m pytest tests/mechanic_tests/test_objective_mechanics.py -v

# Run event mechanic tests
echo "Running event mechanic tests..."
python -m pytest tests/mechanic_tests/test_event_mechanics.py -v

# Run unit mechanic tests (split into separate modules)
echo "Running core unit mechanic tests..."
python -m pytest tests/mechanic_tests/test_unit_mechanics.py -v

echo "Running level up mechanic tests..."
python -m pytest tests/mechanic_tests/test_level_up_mechanics.py -v

echo "Running promotion mechanic tests..."
python -m pytest tests/mechanic_tests/test_promotion_mechanics.py -v

echo "Running status effect mechanic tests..."
python -m pytest tests/mechanic_tests/test_status_effect_mechanics.py -v

echo "Running unit interaction mechanic tests..."
python -m pytest tests/mechanic_tests/test_unit_interaction_mechanics.py -v

# Run misc mechanic tests
# echo "Running misc mechanic tests..."
# python -m pytest tests/mechanic_tests/test_misc_mechanics.py -v

echo "All mechanic tests completed" 