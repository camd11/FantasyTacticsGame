# AI System Tests

This directory contains tests for the AI system components, including the TacticalExecutor, goals, and related functionality.

## Test Files

- **test_tactical_executor_standalone.py**: The recommended approach for testing the TacticalExecutor and goals. Contains comprehensive standalone tests for all goal types using pytest fixtures and clean mocking patterns.

- **test_tactical_executor.py**: The original test file with class-based tests. This file contains two types of tests:
  1. Class-based tests in `TestTacticalExecutor` class (currently may fail with placeholder implementation)
  2. Standalone fixture-based tests at the bottom of the file (these tests work correctly)

## Running Tests

To run all AI system tests:
```bash
python -m pytest tests/gameplay_systems/ai/
```

To run only the recommended standalone tests:
```bash
python -m pytest tests/gameplay_systems/ai/test_tactical_executor_standalone.py
```

To run a specific test:
```bash
python -m pytest tests/gameplay_systems/ai/test_tactical_executor_standalone.py::test_secure_position_goal_success
```

Add `-v` flag for verbose output:
```bash
python -m pytest tests/gameplay_systems/ai/test_tactical_executor_standalone.py -v
```

## Test Development

### Recommended Approach

1. Add new tests to `test_tactical_executor_standalone.py`
2. Follow the existing fixture-based pattern
3. Use the existing fixtures for consistent setup:
   - `mock_unit_state`: Basic AI unit
   - `mock_game_state_manager`: Game state with required mocks
   - `mock_movement_system`: Movement system with reachable tiles
   - `mock_combat_system`: Basic combat system
   - `mock_healing_system`: Basic healing system
   - `tactical_executor`: Initialized executor with mocks
   - `target_unit`: Standard target unit for attacks/heals

### Test Structure

Each test should:
1. Create the appropriate goal object
2. Set up any specific mock behaviors needed
3. Execute the `determine_action_for_goal` method
4. Assert the expected behavior

### Example

```python
def test_my_new_goal(tactical_executor, mock_unit_state, mock_game_state_manager, mock_movement_system):
    """Test description here."""
    # Setup
    goal = MyNewGoal()
    
    # Mock specific behaviors
    mock_movement_system.calculate_movement_range.return_value = {...}
    
    # Execute
    action = tactical_executor.determine_action_for_goal(goal, mock_unit_state, mock_game_state_manager)
    
    # Assert
    assert action is not None
    assert action.action_type == "EXPECTED_ACTION"
    assert action.unit_id == mock_unit_state.id
```

## Troubleshooting

If tests fail with implementation details not matching (e.g., a method not being called), focus on asserting the correct outcome rather than implementation details. The placeholder implementation might use different internal logic than the real implementation.

For example, instead of:
```python
mock_game_state_manager.get_unit_by_id.assert_called_with(unit_id)
```

Consider focusing on the outcome:
```python
assert action is not None
assert action.action_type == "EXPECTED_ACTION"
``` 