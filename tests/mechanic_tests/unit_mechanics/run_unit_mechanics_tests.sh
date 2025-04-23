#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs/mechanic_tests/units

echo "Running Unit Mechanics Tests"
echo "============================="

# Run all unit mechanics tests
python tests/mechanic_tests/unit_mechanics/test_unit_mechanics.py

echo "============================="
echo "All unit mechanics tests completed"
echo "Check logs in logs/mechanic_tests/units/" 