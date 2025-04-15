# Usage Guide

This document explains how to run the Fantasy Tactics Game and interact with it.

## Running the Game

*(Instructions on how to start the game need to be added here. Assuming a standard Python execution for now.)*

To run the game, execute the main script from the project's root directory:

```bash
python src/main.py
```

*(Add any specific command-line arguments or setup steps if necessary, e.g., selecting a chapter or mode)*

## Interactive Player Input

When it is the Player Phase, you can directly control your units using the keyboard. The system guides you through selecting units, moving them, and choosing actions.

### Input States & Controls

The game uses different "states" to handle your input. Here's a breakdown:

1.  **Select Unit State:**
    *   **Goal:** Choose a unit to act.
    *   **Controls:**
        *   `Arrow Keys`: Move the map cursor.
        *   `Enter` / `Space`: Select the player unit under the cursor (if they haven't acted).
        *   `E`: End the Player Phase manually.
    *   **Visuals:** Map shown, cursor highlighted. Units that have acted appear greyed out.

2.  **Display Movement Range State:**
    *   **Goal:** Choose where to move the selected unit.
    *   **Controls:**
        *   `Arrow Keys`: Move the cursor within the highlighted movement range.
        *   `Enter` / `Space`: Confirm the destination tile.
        *   `Backspace` / `Esc`: Cancel movement, return to Select Unit State.
    *   **Visuals:** Selected unit highlighted. Valid movement tiles are overlaid. Cursor moves only within this range.

3.  **Display Action Menu State:**
    *   **Goal:** Choose an action for the unit after moving.
    *   **Controls:**
        *   `Arrow Keys`: Navigate the action menu (Attack, Staff, Item, Wait, **Dance/Play**, etc.). The `Dance`/`Play` action will appear if the unit has the skill and there's a potential target nearby.
        *   `Enter` / `Space`: Select the highlighted menu option.
        *   `A`, `S`, `I`, `W`: Shortcuts for Attack, Staff, Item, Wait (if available).
        *   `Backspace` / `Esc`: Cancel action selection, revert movement, and return to Display Movement Range State (allowing you to choose a different move).
    *   **Visuals:** A menu appears near the unit listing available actions.

4.  **Select Target State (if needed):**
    *   **Goal:** Choose a target for an action like Attack, Staff, or **Dance/Play**.
    *   **Controls:**
        *   `Arrow Keys`: Cycle through valid targets within range.
        *   `Enter` / `Space`: Confirm the selected target.
        *   `Backspace` / `Esc`: Cancel targeting, return to Display Action Menu State.
    *   **Visuals:** Action range is shown. Valid targets are highlighted. The currently selected target has a distinct indicator. Potential combat preview might be shown for attacks. For **Dance/Play**, only adjacent allies who have already acted (and haven't been refreshed yet) will be valid targets.

5.  **Execution & End Turn:**
    *   Once an action (like Wait) is chosen or a target is confirmed, the action executes automatically.
    *   The unit is marked as 'Acted' (greyed out).
    *   The game returns to the **Select Unit State** for you to choose the next unit. If a unit was targeted by **Dance/Play**, they will no longer be greyed out and can be selected to act again.

### General Tips

*   Pay attention to the visual cues: highlighted tiles for movement/action range, greyed-out units that have acted.
*   Use `Backspace` / `Esc` frequently to cancel actions or selections if you change your mind.
*   Remember the `E` key in the Select Unit state to end your turn when ready.