# Mechanic Tests

This directory contains lightweight tests for individual game mechanics, each focused on a specific gameplay element. The primary purpose of these tests is to validate that core game mechanics work correctly and to provide visual logs for easy inspection of the mechanics in action.

## Structure

Each test file corresponds to a category of mechanics:

- `test_movement_mechanics.py`: Tests for unit movement across different terrain types
- `test_combat_mechanics.py`: Tests for basic combat, critical hits, misses, etc.
- `test_ai_mechanics.py`: Tests for AI decision making with different personas
- `test_objective_mechanics.py`: Tests for capturing and defending objectives
- `test_event_mechanics.py`: Tests for various event triggers
- `test_unit_mechanics.py`: Tests for unit creation, modification, and death
- `test_misc_mechanics.py`: Tests for turn progression, phases, etc.

## Log Files

Each test writes to a fixed log file in the `logs/mechanic_tests/` directory, organized in subfolders by mechanic type. Unlike regular logs, these logs have **fixed filenames** and **overwrite previous logs** to ensure only the latest test results are stored.

The log structure is:

```
logs/
└── mechanic_tests/
    ├── movement/
    │   ├── basic_move.txt
    │   ├── terrain_cost_move.txt
    │   └── ...
    ├── combat/
    │   ├── basic_attack.txt
    │   ├── miss_attack.txt
    │   └── ...
    ... etc.
```

## Running Tests

To run all mechanic tests:

```
pytest tests/mechanic_tests/
```

To run tests for a specific mechanic category:

```
pytest tests/mechanic_tests/test_movement_mechanics.py
```

To run a specific test:

```
pytest tests/mechanic_tests/test_movement_mechanics.py::test_basic_movement_log
```

## Adding New Tests

When adding a new mechanic test:

1. Place it in the appropriate category file
2. Use a dedicated method to set up the minimal game state needed
3. Create a fixed log path in the proper subdirectory
4. Ensure the test deletes any existing log file before running
5. Set up the visual logger with the fixed log path
6. Run only the actions necessary to demonstrate the mechanic
7. Verify at the end that the log file was created

See existing tests for examples of the proper structure. 