# Testing Guide

This document provides a comprehensive guide to testing the Fantasy Tactics Game. The project uses multiple testing approaches to verify different aspects of the game, from core mechanics to visual rendering.

## Table of Contents

- [General Testing Information](#general-testing-information)
- [Standard Tests (pytest)](#standard-tests-pytest)
- [Mechanic Tests](#mechanic-tests)
- [Visual Tests](#visual-tests)
- [AI Tests](#ai-tests)
- [Interpreting Test Results](#interpreting-test-results)
- [Troubleshooting](#troubleshooting)

## General Testing Information

The project uses pytest as its primary testing framework. Test directories are organized by component or system being tested:

- `tests/` - Root directory containing all tests
  - `tests/core_engine/` - Tests for core game engine components
  - `tests/gameplay_systems/` - Tests for gameplay mechanics and systems
  - `tests/mechanic_tests/` - Specific mechanic tests (movement, combat, etc.)
  - `tests/visual_tests/` - Tests for visual components and renderers
  - `tests/ai/` - Tests for AI components and decision-making

## Standard Tests (pytest)

Standard tests verify core functionality without visual components.

### Running Standard Tests

To run all tests:

```bash
python -m pytest
```

To run tests for a specific module:

```bash
python -m pytest tests/gameplay_systems/
```

To run a specific test file:

```bash
python -m pytest tests/gameplay_systems/test_combat_system.py
```

To run a specific test function:

```bash
python -m pytest tests/gameplay_systems/test_combat_system.py::test_basic_attack
```

## Mechanic Tests

Mechanic tests focus on specific game mechanics (movement, combat, etc.) and can be run with or without visual output.

### Running Mechanic Tests

To run all mechanic tests:

```bash
./run_mechanic_tests.sh
```

To run tests for a specific mechanic:

```bash
python -m pytest tests/mechanic_tests/test_movement_mechanics.py
```

To run mechanic tests with visual feedback:

```bash
bash tests/mechanic_tests/movement/run_movement_tests.sh --visual
```

## Visual Tests

Visual tests verify rendering, animations, and user interface components.

### Running Visual Tests

To run all visual tests (generates logs but no display):

```bash
python tests/visual_tests/run_all_visual_tests.py
```

To run a specific visual test with display:

```bash
python tests/visual_tests/run_visual_tests.py simple_attack
```

### Visual Testing Tools

Several tools are available for visual testing:

| Tool | Purpose | Usage |
|------|---------|-------|
| `run_visual_tests.py` | Runs specific visual demos | Most reliable for seeing the Pygame window |
| `automated_visual_tests.py` | Runs all tests with a visible window | Manual verification of visual elements |
| `headless_visual_tests.py` | Runs all tests without a visible window | CI/CD integration and automated testing |
| `visual_test_runner.py` | Unified tool with visible and headless modes | General-purpose testing |
| `test_selector.py` | Interactive tool for running specific tests | Debugging and focused testing |

To use the test selector:

```bash
python tests/visual_tests/test_selector.py
```

## AI Tests

AI tests verify the decision-making and behavior of AI-controlled units.

### AI vs AI Testing

The AI vs AI Testing Framework allows running simulations with AI controlling both sides.

To run an AI vs AI simulation:

```bash
python tools/run_ai_vs_ai_test.py --scenario data/scenarios/your_ai_test_scenario.yaml
```

Options:
- `--max_turns [N]`: Limits the simulation to N turns
- `--ascii-display`: Shows a basic text-based representation of the map

### Running AI Unit Tests

To run all AI system tests:

```bash
python -m pytest tests/gameplay_systems/ai/
```

To run standalone tactical executor tests:

```bash
python -m pytest tests/gameplay_systems/ai/test_tactical_executor_standalone.py
```

To run a specific AI test:

```bash
python -m pytest tests/gameplay_systems/ai/test_tactical_executor_standalone.py::test_secure_position_goal_success
```

## Interpreting Test Results

### Log Files

Different test types generate different log files:

- Standard tests: Output to console and `pytest.log`
- Mechanic tests: Output to `logs/mechanic_tests/[category]/[test_name].log`
- Visual tests: Output to `logs/visual_tests/[test_name].log` and screenshots in `logs/visual_tests/screenshots/`
- AI tests: Output to `ai_behavior.log` (detailed decision-making) and `ai_vs_ai_test.log` (high-level simulation events)

### Understanding AI Test Logs

- **`ai_behavior.log`**: Contains detailed AI decision-making information including:
  - Goal evaluation and selection
  - Action generation and scoring
  - Final action selection

- **`ai_vs_ai_test.log`**: High-level overview of AI simulation events:
  - Turn progression
  - Unit actions
  - Combat results
  - Game end conditions

## Troubleshooting

### Common Test Issues

- **Test fails to start**: Check that all dependencies are installed and the virtual environment is activated
- **Visual tests show no window**: Ensure pygame is installed and your environment supports graphics
- **AI tests fail**: Check log files for specific decision-making failures or issues
- **Mechanic tests fail**: Examine the test logs for the specific rule or condition that failed

### Debugging Tips

- Add the `-v` flag to pytest commands for verbose output
- Use `--pdb` to enter the Python debugger on test failures
- Check log files in the `logs/` directory for detailed error information
- For visual test issues, try running with the `--visual` flag to see what's happening

### CI/CD Integration

If you're running tests in a CI/CD environment:

- Use headless visual tests
- Set the `HEADLESS=1` environment variable
- Verify log outputs rather than expecting visual display

---

For more detailed information on AI testing, see the [AI Research Summary](systems/ai_research_summary.md#ai-vs-ai-testing-framework).

For more information on visual testing, see [Visual System Documentation](systems/visual.md). 