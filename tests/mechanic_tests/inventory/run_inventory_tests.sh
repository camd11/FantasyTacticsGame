#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create log directory if it doesn't exist
mkdir -p "${DIR}/../../../logs/mechanic_tests/inventory"

# Run the inventory tests
echo "Running inventory tests..."
python3 "${DIR}/test_inventory_mechanics.py"

# Check if test was successful
if [ $? -eq 0 ]; then
    echo "Inventory tests completed successfully!"
    echo "Logs available at: ${DIR}/../../../logs/mechanic_tests/inventory/"
else
    echo "Inventory tests failed!"
    exit 1
fi 