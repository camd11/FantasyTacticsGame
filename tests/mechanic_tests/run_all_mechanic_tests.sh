#!/bin/bash

echo "==== Creating log directories ===="
mkdir -p logs/mechanic_tests
mkdir -p logs/mechanic_tests/units
mkdir -p logs/mechanic_tests/combat
mkdir -p logs/mechanic_tests/movement
mkdir -p logs/mechanic_tests/inventory
mkdir -p logs/mechanic_tests/status_effects
mkdir -p logs/mechanic_tests/interactions
mkdir -p logs/mechanic_tests/integrated

echo "==== Running Unit Mechanics Tests ===="
bash tests/mechanic_tests/unit_mechanics/run_unit_mechanics_tests.sh

echo "==== Running Combat Mechanics Tests ===="
python tests/mechanic_tests/combat/test_combat_mechanics.py

echo "==== Running Movement Mechanics Tests ===="
python tests/mechanic_tests/movement/test_movement_mechanics.py

echo "==== Running Inventory Mechanics Tests ===="
python tests/mechanic_tests/inventory/test_inventory_mechanics.py

echo "==== Running Status Effect Mechanics Tests ===="
python tests/mechanic_tests/status_effects/test_status_effect_mechanics.py

echo "==== Running Unit Interaction Mechanics Tests ===="
python tests/mechanic_tests/interactions/test_unit_interaction_mechanics.py

echo "==== Running Integrated Mechanics Tests ===="
python tests/mechanic_tests/integrated/test_integrated_mechanics.py

echo "==== All mechanic tests completed! ===="
echo "Check logs in logs/mechanic_tests/ directory" 