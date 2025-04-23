# AI System Tests

This directory contains tests for the AI system components, including the TacticalExecutor, goals, and related functionality.

## Test Files

- **test_tactical_executor_standalone.py**: The recommended approach for testing the TacticalExecutor and goals. Contains comprehensive standalone tests for all goal types using pytest fixtures and clean mocking patterns.

- **test_tactical_executor.py**: The original test file with class-based tests. This file contains two types of tests:
  1. Class-based tests in `TestTacticalExecutor` class (currently may fail with placeholder implementation)
  2. Standalone fixture-based tests at the bottom of the file (these tests work correctly)

- **test_ai_scenario_01.py**, **test_ai_scenario_02.py**, **test_ai_scenario_03.py**: Individual AI scenario tests that examine specific aspects of AI behavior.

- **test_ai_scenario_04.py**: Advanced tactical scenario with visual logging and 5-turn limit implementation.

## AI Scenario Guidelines

- **Maximum 5 Turns**: All AI scenario simulations should be limited to a maximum of 5 turns for performance and practical evaluation reasons.
- **Visual Logging**: Complex scenarios should include visual logging to help analyze AI behavior.
- **Focused Testing**: Each scenario should focus on testing specific aspects of AI behavior like tactical positioning, goal prioritization, etc.
- **Clear Win Conditions**: Include clearly defined win conditions for AI sides, such as capturing an objective or defeating all enemy units.

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

To run an AI scenario with visual logging:
```bash
python -m pytest tests/gameplay_systems/ai/test_ai_scenario_04.py -v
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

### AI Scenario Test Development

When developing AI scenario tests:

1. Always implement the 5-turn limit as shown in `test_ai_scenario_04.py`
2. Include visual logging to capture the moves made by AI units
3. Create interesting tactical situations with terrain variety
4. Test specific AI behaviors like terrain navigation, target prioritization, etc.
5. Include units with different AI personas to test their interactions

### Visual Log Analysis

Visual logs are created in the `logs/` directory and contain:
- Initial map state
- Turn-by-turn unit actions
- End-of-turn map states
- Final statistics

Use these logs to:
- Verify AI is making expected tactical decisions
- Debug unexpected behavior
- Track unit movements and combat outcomes

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