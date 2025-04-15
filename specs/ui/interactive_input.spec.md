# Specification: Interactive Player Input System
# File: specs/ui/interactive_input.spec.md
# Status: Implemented

## 1. Introduction

This document outlines the specification for a new interactive player input system for the Thracia 776 command-line game. The goal is to allow players to directly control their units using keyboard input during the Player Phase, replacing the previous scenario-driven execution model for player actions. This system will handle unit selection, movement, action selection, targeting, and turn management.

## 2. Core Player Turn Loop

The player interaction follows a state-based loop:

1.  **Start Player Phase:** Initialize turn status for all player units (e.g., set to 'Can Act').
2.  **Select Unit State:** Player navigates the map cursor to select an available player unit.
3.  **Display Movement Range State:** Once a unit is selected, calculate and display its valid movement range. Player navigates the cursor within this range.
4.  **Confirm Movement State:** Player confirms a destination tile for the selected unit.
5.  **Display Action Menu State:** After movement, display the available actions for the unit (e.g., Attack, Staff, Item, Wait). Player selects an action.
6.  **Select Target State (Conditional):** If the chosen action requires a target (e.g., Attack, Staff), display valid targets and allow the player to select one.
7.  **Execute Action State:** Perform the selected action (including combat, healing, item use, or waiting).
8.  **End Unit Turn:** Mark the unit as having acted. Return to **Select Unit State**.
9.  **End Player Phase:** If all units have acted or the player manually ends the phase, transition to the next game phase (e.g., Enemy Phase).

## 3. Input Mapping

The following keyboard inputs will be used (specific keys can be configured, but these are defaults):

| Key(s)         | State(s) Applicable        | Action                                      |
| :------------- | :------------------------- | :------------------------------------------ |
| Arrow Keys     | All (Map Navigation)       | Move map cursor (up, down, left, right)     |
| Enter / Space  | Select Unit                | Select unit under cursor                    |
| Enter / Space  | Display Movement Range     | Confirm movement destination tile           |
| Enter / Space  | Display Action Menu        | Select highlighted menu option              |
| Enter / Space  | Select Target              | Confirm selected target                     |
| Backspace / Esc| Display Movement Range     | Cancel selection, return to Select Unit     |
| Backspace / Esc| Confirm Movement           | (Handled by Display Movement Range state)   |
| Backspace / Esc| Display Action Menu        | Cancel action, return to Display Movement Range |
| Backspace / Esc| Select Target              | Cancel targeting, return to Display Action Menu |
| `A`            | Display Action Menu        | Shortcut for Attack (if available)          |
| `S`            | Display Action Menu        | Shortcut for Staff (if available)           |
| `I`            | Display Action Menu        | Shortcut for Item (if available)            |
| `W`            | Display Action Menu        | Shortcut for Wait                           |
| `E`            | Select Unit                | Manually End Player Phase                   |
| Arrow Keys     | Display Action Menu        | Navigate menu options                       |
| Arrow Keys     | Select Target              | Cycle through valid targets                 |

## 4. State Management & Flow

The system operates based on distinct states controlling input interpretation and display updates.

### 4.1. Select Unit State

*   **Entry:** Start of Player Phase, or after a unit finishes its action.
*   **Input:** Arrow keys move the map cursor. Enter/Space selects the player unit under the cursor if it hasn't acted. 'E' ends the player phase.
*   **Display:** Map grid with units. Cursor position is highlighted. Units that have acted are visually distinct (e.g., greyed out).
*   **Logic:**
    *   Check if the unit under the cursor is a player unit and can act.
    *   [TDD: Test unit selection eligibility (player-controlled, hasn't acted)]
    *   If Enter/Space on a valid unit: Transition to **Display Movement Range State**.
    *   If 'E': Transition to **End Player Phase**.
*   **Exit:** Unit selected or phase ended.

### 4.2. Display Movement Range State

*   **Entry:** After selecting a valid unit.
*   **Input:** Arrow keys move the cursor within the calculated movement range. Enter/Space confirms the destination tile. Backspace/Esc cancels.
*   **Display:** Map grid. Selected unit highlighted. Valid movement tiles are overlaid with a distinct character/color. Cursor position highlighted within the range.
*   **Logic:**
    *   Calculate movement range based on unit's Move stat, terrain costs, and blocking units/terrain. (Depends on `MovementSystem`)
    *   [TDD: Test movement range calculation]
    *   [TDD: Test movement range display overlay]
    *   Validate cursor movement stays within calculated range.
    *   [TDD: Test cursor confinement to movement range]
    *   If Enter/Space on a valid tile: Store selected destination, transition to **Confirm Movement State** (momentary) then **Display Action Menu State**.
    *   If Backspace/Esc: Transition back to **Select Unit State**.
*   **Exit:** Destination confirmed or selection cancelled.

### 4.3. Confirm Movement State (Internal/Brief)

*   **Entry:** After selecting a destination tile in the previous state.
*   **Logic:**
    *   Update the unit's position in the game state to the selected destination tile.
    *   [TDD: Test unit position update after move confirmation]
    *   Redraw the map with the unit in the new position.
    *   Immediately transition to **Display Action Menu State**.
*   **Display:** Map updates to show the unit at the new location. Movement range overlay is removed.
*   **Exit:** Automatically transitions.

### 4.4. Display Action Menu State

*   **Entry:** After unit movement is confirmed.
*   **Input:** Arrow keys navigate the menu. Enter/Space or shortcut keys (`A`, `S`, `I`, `W`) select an action. Backspace/Esc cancels.
*   **Display:** A menu box appears near the unit, listing available actions (e.g., "Attack", "Staff", "Item", "Wait"). The currently selected option is highlighted.
*   **Logic:**
    *   Determine available actions based on unit capabilities, items, and surroundings (e.g., enemies in range for Attack, allies for Staff). (Depends on `ActionSystem`, `InventorySystem`, `CombatSystem`)
    *   [TDD: Test available action determination (e.g., Attack requires weapon and target)]
    *   [TDD: Test action menu display content]
    *   If Enter/Space or shortcut on "Wait": Transition to **Execute Action State** (Wait action).
    *   If Enter/Space or shortcut on "Attack": Check for valid targets. If targets exist, transition to **Select Target State** (Attack). If not, provide feedback (e.g., "No targets in range") and remain in this state. [TDD: Test Attack action prerequisites (targets exist)]
    *   If Enter/Space or shortcut on "Staff": Check for valid targets. If targets exist, transition to **Select Target State** (Staff). If not, provide feedback and remain. [TDD: Test Staff action prerequisites (targets exist)]
    *   If Enter/Space or shortcut on "Item": Transition to a sub-state/menu for item selection (details TBD, potentially another spec). For now, assume it leads to **Execute Action State** or **Select Target State** if the item requires targeting. [TDD: Test Item action selection]
    *   If Backspace/Esc: Revert unit position to its original location *before* movement, transition back to **Display Movement Range State** (allowing re-selection of movement). [TDD: Test action menu cancellation reverts movement]
*   **Exit:** Action selected or cancelled.

### 4.5. Select Target State

*   **Entry:** After selecting an action (Attack, Staff, some Items) that requires a target.
*   **Input:** Arrow keys cycle through valid targets. Enter/Space confirms the target. Backspace/Esc cancels.
*   **Display:** Map grid. Action-specific range (attack range, staff range) is displayed. Valid target units within that range are highlighted. The currently selected target has a distinct highlight/cursor. A small info panel might show predicted combat results (for Attack).
*   **Logic:**
    *   Identify all valid targets within the action's range based on action type (enemy for attack, ally for heal staff, etc.). (Depends on `TargetingSystem`, `RangeSystem`)
    *   [TDD: Test target identification for Attack]
    *   [TDD: Test target identification for Staff]
    *   Allow cycling through targets using arrow keys.
    *   [TDD: Test target cycling]
    *   If Enter/Space: Store selected target, transition to **Execute Action State**.
    *   If Backspace/Esc: Transition back to **Display Action Menu State**.
*   **Exit:** Target confirmed or targeting cancelled.

### 4.6. Execute Action State

*   **Entry:** After selecting "Wait", or confirming a target (if required), or selecting a non-targeting Item.
*   **Input:** None (automatic execution).
*   **Display:** Action animation/feedback (e.g., text log update: "Leif attacks Bandit!", "Nanna heals Finn.", "Leif waits."). Map updates if the action causes changes (HP reduction, status effects).
*   **Logic:**
    *   Execute the chosen action using the selected unit and target (if any). This involves calling appropriate game systems (Combat, Item Effects, Status Effects).
    *   [TDD: Test Wait action execution]
    *   [TDD: Test Attack action execution (invokes combat)]
    *   [TDD: Test Staff action execution (invokes healing/status)]
    *   [TDD: Test Item action execution (invokes item effect)]
    *   After execution, transition to **End Unit Turn State**.
*   **Exit:** Action completed.

### 4.7. End Unit Turn State (Internal/Brief)

*   **Entry:** After action execution.
*   **Logic:**
    *   Mark the unit as having completed its action for the current Player Phase (e.g., set status to 'Acted').
    *   [TDD: Test unit status update to 'Acted']
    *   Check if all player units have acted. If so, potentially auto-advance to **End Player Phase**. (Configurable behavior - auto-end vs. manual end).
    *   Transition back to **Select Unit State**.
*   **Display:** Unit appearance changes to indicate it has acted (e.g., greyed out).
*   **Exit:** Automatically transitions.

### 4.8. End Player Phase State

*   **Entry:** Player selects "End Turn" command ('E') in **Select Unit State**, OR automatically if all units have acted (configurable).
*   **Logic:**
    *   Perform any end-of-player-phase cleanup or checks (e.g., status effect durations).
    *   Signal the main game loop to transition to the next phase (Enemy Phase).
    *   [TDD: Test player phase end trigger]
*   **Exit:** Control returns to the main game loop for phase transition.

## 5. Display Interaction Summary

*   **Cursor:** A distinct character/highlight indicating the player's current focus on the map.
*   **Unit Highlighting:** Selected unit is clearly marked.
*   **Movement Range:** Tiles reachable by the selected unit are overlaid with a specific character or background color.
*   **Action Range:** Tiles reachable by a selected action (Attack, Staff) are overlaid (potentially different style than movement).
*   **Target Highlighting:** Valid targets for an action are highlighted. The currently selected target has a unique indicator.
*   **Menus:** Action menus appear as text boxes near the active unit.
*   **Unit Status:** Units that have completed their turn are visually distinct (e.g., greyed out/desaturated color).
*   **Feedback:** Text messages in a log area or temporary pop-ups provide information (e.g., "Cannot move there", "No targets in range", combat results).

## 6. Dependencies

This system relies on:

*   `MapData`: Terrain information, unit locations.
*   `UnitData`: Unit stats (Move), status (acted/not acted), inventory, skills.
*   `MovementSystem`: Calculates valid movement tiles.
*   `RangeSystem`: Calculates action ranges (attack, staff).
*   `TargetingSystem`: Identifies valid targets based on action type and range.
*   `ActionSystem`: Determines available actions for a unit.
*   `CombatSystem`: Executes attack actions.
*   `ItemSystem`/`InventorySystem`: Manages item usage and effects.
*   `StatusEffectSystem`: Applies and manages status effects resulting from actions.
*   `DisplaySystem`: Renders the map, units, overlays, and menus to the terminal. (Likely using a library like `curses`).

## 7. Edge Cases & Considerations

*   **Units unable to act:** Units with status effects preventing action (Sleep, Stone) should not be selectable.
*   **No valid moves:** If a unit has 0 Move or is completely blocked, selecting them should immediately show no movement range and potentially skip directly to the Action Menu (only 'Wait' or 'Item' might be possible).
*   **Input Buffering:** How to handle rapid key presses? (Likely handled by the underlying terminal library).
*   **Terminal Resizing:** How does the display adapt? (Lower priority for initial spec).
*   **Saving/Loading:** Game state must include the current input state if saving is possible mid-turn.