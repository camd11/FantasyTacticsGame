#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "========================================="
echo "Running all mechanics tests..."
echo "========================================="

# Run unit mechanics tests
echo -e "\n========== UNIT MECHANICS TESTS =========="
bash "${DIR}/unit_mechanics/run_unit_mechanics_tests.sh" | cat
if [ $? -ne 0 ]; then
    echo "Unit mechanics tests failed!"
    exit 1
fi

# Run combat mechanics tests
echo -e "\n========== COMBAT MECHANICS TESTS =========="
if [ -d "${DIR}/combat" ]; then
    bash "${DIR}/combat/run_combat_tests.sh" | cat
    if [ $? -ne 0 ]; then
        echo "Combat mechanics tests failed!"
        exit 1
    fi
else
    echo "Combat mechanics tests directory not found. Skipping..."
fi

# Run movement mechanics tests
echo -e "\n========== MOVEMENT MECHANICS TESTS =========="
if [ -d "${DIR}/movement" ]; then
    bash "${DIR}/movement/run_movement_tests.sh" | cat
    if [ $? -ne 0 ]; then
        echo "Movement mechanics tests failed!"
        exit 1
    fi
else
    echo "Movement mechanics tests directory not found. Skipping..."
fi

# Run status effect mechanics tests
echo -e "\n========== STATUS EFFECT MECHANICS TESTS =========="
if [ -d "${DIR}/status_effects" ]; then
    bash "${DIR}/status_effects/run_status_effects_tests.sh" | cat
    if [ $? -ne 0 ]; then
        echo "Status effect mechanics tests failed!"
        exit 1
    fi
else
    echo "Status effect mechanics tests directory not found. Skipping..."
fi

# Run inventory mechanics tests
echo -e "\n========== INVENTORY MECHANICS TESTS =========="
if [ -d "${DIR}/inventory" ]; then
    bash "${DIR}/inventory/run_inventory_tests.sh" | cat
    if [ $? -ne 0 ]; then
        echo "Inventory mechanics tests failed!"
        exit 1
    fi
else
    echo "Inventory mechanics tests directory not found. Skipping..."
fi

echo -e "\n========================================="
echo "All mechanics tests completed successfully!"
echo "=========================================="\n 