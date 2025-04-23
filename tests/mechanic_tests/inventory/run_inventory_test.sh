#!/bin/bash

# Run the inventory mechanics test
# This script runs the inventory mechanics test and outputs logs to the appropriate directory

# Create log directory if it doesn't exist
mkdir -p logs/mechanic_tests/inventory

echo "Running inventory mechanics test..."

# Run the test using the Python script
python tests/mechanic_tests/inventory/test_inventory_mechanics.py

# Check if the test was successful
if [ $? -eq 0 ]; then
    echo "Inventory mechanics test completed successfully."
    echo "Logs are available in the logs/mechanic_tests/inventory directory."
    exit 0
else
    echo "Inventory mechanics test failed."
    exit 1
fi 