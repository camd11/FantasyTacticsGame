# Usage Guide

This document explains how to run the Fantasy Tactics Game and interact with it.

## Running the Game

For setup instructions (installing Python, dependencies, etc.), please refer to the [Setup Guide](../setup.md).

To run the game, execute the main script from the project's root directory:

```bash
python src/main.py
```

## Command-Line Arguments

* `--ai-vs-ai`: Runs the game in AI vs AI mode for testing purposes.
* `--ascii-display`: Enables an optional ASCII representation of the map in the console during gameplay.
* `--chapter NAME`: Loads a specific chapter (e.g., `--chapter chapter_1`).
* `--gui`: Enables the Pygame visualization.

## Visual Tests

To run visual tests, use one of the following commands:

```bash
# Run a specific visual demo
python run_visual_tests.py simple_attack

# Run mechanic tests with visual display
bash tests/mechanic_tests/movement/run_movement_tests.sh --visual

# Run the visual test GUI (experimental)
python visual_tests_gui.py
```

## Interactive Player Input

When it is the Player Phase, you can directly control your units using the keyboard. The system guides you through selecting units, moving them, and choosing actions.

### Input States & Controls

The game uses different "states" to handle your input:

1. **Select Unit State:**
   * **Controls:**
     * `Arrow Keys`: Move the map cursor.
     * `Enter` / `Space`: Select the player unit under the cursor (if they haven't acted).
     * `E`: End the Player Phase manually.
   * **Visuals:** Map shown, cursor highlighted. Units that have acted appear greyed out.

2. **Display Movement Range State:**
   * **Controls:**
     * `Arrow Keys`: Move the cursor within the highlighted movement range.
     * `Enter` / `Space`: Confirm the destination tile.
     * `Backspace` / `Esc`: Cancel movement, return to Select Unit State.
   * **Visuals:** Selected unit highlighted. Valid movement tiles are overlaid.

3. **Display Action Menu State:**
   * **Controls:**
     * `Arrow Keys`: Navigate the action menu (Attack, Staff, Item, Wait, etc.).
     * `Enter` / `Space`: Select the highlighted menu option.
     * `A`, `S`, `I`, `W`: Shortcuts for Attack, Staff, Item, Wait (if available).
     * `Backspace` / `Esc`: Cancel action selection, revert movement.
   * **Visuals:** A menu appears near the unit listing available actions.

4. **Select Target State (if needed):**
   * **Controls:**
     * `Arrow Keys`: Cycle through valid targets within range.
     * `Enter` / `Space`: Confirm the selected target.
     * `Backspace` / `Esc`: Cancel targeting, return to Display Action Menu State.
   * **Visuals:** Action range is shown. Valid targets are highlighted.

5. **Execution & End Turn:**
   * Once an action is chosen or a target is confirmed, the action executes automatically.
   * The unit is marked as 'Acted' (greyed out).
   * The game returns to the **Select Unit State** for you to choose the next unit.

### General Tips

* Pay attention to the visual cues: highlighted tiles for movement/action range, greyed-out units that have acted.
* Use `Backspace` / `Esc` to cancel actions or selections if you change your mind.
* Remember the `E` key in the Select Unit state to end your turn when ready.

## AI vs AI Simulation

To run an AI vs AI simulation:

```bash
# Run with default settings
python src/main.py --ai-vs-ai

# Run with ASCII display
python src/main.py --ai-vs-ai --ascii-display

# Run a specific scenario
python tools/run_ai_vs_ai_test.py --scenario data/scenarios/your_ai_test_scenario.yaml
```

This mode is useful for testing AI behavior and game mechanics without player input. 