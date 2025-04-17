# AI vs AI Testing Framework

This document describes the AI vs AI testing framework for the Fantasy Tactics Game, designed to facilitate automated testing and observation of AI behavior and interactions between AI-controlled units using the v2 Goal-Oriented AI system.

## Overview

The AI vs AI testing framework allows developers to:

1.  Create scenarios where both factions are controlled by AI using different personas.
2.  Observe and test different AI personas against each other in a dynamic environment.
3.  Verify that AI units make appropriate strategic (Goal) and tactical (Action) decisions based on their personas and the game state.
4.  Analyze emergent AI behavior in complex tactical situations over multiple turns.
5.  Provide a basis for regression testing of the AI system.

## Components

### 1. AI vs AI Test Scenarios

Located in `data/scenarios/`, these YAML files define test scenarios specifically designed for AI vs AI testing.

*   **Example:** `data/scenarios/ai_vs_ai_basic_test.yaml` (or similar) - A scenario designed to test fundamental interactions between different personas.

Each scenario typically includes:
*   Map layout definition (`layout_path`).
*   Unit placements (`units`) for both factions, specifying `team`, `class_id`, starting `position`, `level`, `items`, and crucially, the `ai_persona`.
*   Optional event triggers (`events`).
*   Game configuration (`config`), potentially including turn limits or specific objectives.

### 2. Test Execution Scripts

Located in the project root:

*   **`run_ai_vs_ai_test.py`:** The primary script for running an AI vs AI simulation. It loads a specified scenario, sets both teams to AI control, and runs the game simulation, outputting detailed logs. This is ideal for observation and manual analysis.
*   **`test_ai_vs_ai_fixed.py` (or similar pytest files):** Automated test scripts using `pytest`. These load specific scenarios, run simulations, and include assertions to programmatically verify expected outcomes or behaviors (e.g., checking if a certain goal was prioritized, if a unit survived, etc.). These are used for automated regression testing.

### 3. Logging System

*   **`src/gameplay_systems/ai/ai_logger.py` (`AILogger`):** Integrated into the AI Manager, this logs detailed decision-making information during simulations.
*   **Log Files:**
    *   `ai_behavior.log`: Captures detailed turn-by-turn decisions for *individual* AI units, including goal evaluation scores, chosen goals, action generation, action evaluation scores, and chosen actions. Essential for deep dives into a specific unit's logic.
    *   `ai_vs_ai_test.log`: Captures higher-level events and state changes during an AI vs AI simulation run via `run_ai_vs_ai_test.py`, such as turn progression, unit actions taken, combat results, and game end conditions. Useful for understanding the overall flow of the simulation.

## AI Personas (Examples)

The framework allows testing various AI personas defined in `data/ai_personas.yaml`:

1.  **Aggressor**: Prioritizes attacking enemy units (High weight for `AttackUnitGoal`).
2.  **Defender**: Prioritizes holding strategic positions (High weight for `SecurePositionGoal`).
3.  **Support**: Prioritizes healing and assisting allies (High weight for `HealUnitGoal`).
4.  **ObjectiveRusher**: Prioritizes advancing toward map objectives (High weight for `AdvanceToObjectiveGoal` or `SeizeTileGoal`).

## Running AI vs AI Tests

### Method 1: Observation & Manual Analysis

Use this method to watch a simulation unfold and analyze the detailed logs afterward.

1.  **Run the Simulation Script:**
    ```bash
    python run_ai_vs_ai_test.py --scenario data/scenarios/your_ai_test_scenario.yaml [--max_turns 50] [--ascii-display]
    ```
    *   Replace `your_ai_test_scenario.yaml` with the desired scenario file.
    *   `--max_turns` (optional): Limits the simulation duration.
    *   `--ascii-display` (optional): Shows a basic text-based representation of the map state in the console during the simulation.

2.  **Observe:** Watch the console output (especially if using `--ascii-display`) or wait for the simulation to complete.

3.  **Analyze Logs:** Examine `ai_behavior.log` and `ai_vs_ai_test.log` (see "Interpreting Logs" below).

### Method 2: Automated Regression Testing

Use this method to run predefined tests with automated checks.

1.  **Run Pytest:**
    ```bash
    pytest test_ai_vs_ai_fixed.py -v
    ```
    *   This will execute all test functions within the specified file.
    *   `-v` provides verbose output, showing which tests passed or failed.

2.  **Review Failures:** If any tests fail, examine the pytest output and the relevant logs (`ai_behavior.log`, `ai_vs_ai_test.log`) to diagnose the issue.

## Interpreting AI Behavior Logs

*   **`ai_vs_ai_test.log`:**
    *   **Purpose:** Provides a high-level overview of the simulation flow.
    *   **Key Information:** Turn start/end markers, unit actions executed (Move, Attack, Wait, Use Skill/Item), combat results (damage dealt, unit defeated), game end conditions.
    *   **Use Case:** Understanding the sequence of events, identifying major outcomes, tracking overall simulation progress.

*   **`ai_behavior.log`:**
    *   **Purpose:** Provides deep insight into the AI's decision-making process for each unit's turn.
    *   **Key Information:**
        *   `Evaluating Goals for Unit X`: Lists all valid goals considered.
        *   `Goal Y Relevance Score: Z`: Shows the calculated score for each goal based on persona and game state.
        *   `Selected Goal: Y`: Indicates the chosen strategic goal.
        *   `Evaluating Actions for Goal Y`: Lists potential tactical actions generated for the chosen goal.
        *   `Action Z Utility Score: W`: Shows the calculated score for each action.
        *   `Selected Action Sequence: Z`: Indicates the chosen action(s) to execute.
    *   **Use Case:** Debugging unexpected behavior, verifying goal/action scoring logic, tuning AI persona weights, understanding *why* an AI made a specific choice.

## Creating New AI Test Scenarios

1.  **Define Objectives:** What specific AI behavior or interaction do you want to test? (e.g., How does a Defender react to an Aggressor? Does a Support unit correctly prioritize healing?)
2.  **Create YAML File:** Create a new `.yaml` file in `data/scenarios/` (e.g., `data/scenarios/ai_test_flanking.yaml`).
3.  **Design Map Layout:** Reference or create a map layout (`layout_path`) that facilitates the desired interaction. Consider terrain placement (chokepoints, defensive tiles, open ground).
4.  **Place Units:**
    *   Define units for both `player` and `enemy` teams.
    *   Assign appropriate `class_id`.
    *   Set starting `position`.
    *   Assign the desired `ai_persona` to each AI unit.
    *   Equip relevant `items`.
5.  **Configure Simulation:** Set `config` options like `turn_limit` if needed.
6.  **(Optional) Add Events:** Define simple `events` if necessary for the scenario setup.
7.  **Document:** Add comments within the YAML file explaining the scenario's purpose and expected outcome.
8.  **Test:** Run the scenario using `run_ai_vs_ai_test.py` for observation and consider creating a corresponding `pytest` function in `test_ai_vs_ai_fixed.py` for automated validation.

## Future Enhancements

*   Automated analysis tools for logs (e.g., scripts to calculate goal frequency per persona).
*   More sophisticated scenario definition options (e.g., complex win conditions).
*   Integration with visualization tools beyond basic ASCII display.