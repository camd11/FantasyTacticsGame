# Technical Documentation

This document provides technical details about the Fantasy Tactics Game, including usage instructions and technical analysis of key systems.

## Table of Contents
1. [Usage Guide](#usage-guide)
2. [Movement System Analysis](#movement-system-analysis)

---

<a id="usage-guide"></a>
# 1. Usage Guide

This section explains how to run the Fantasy Tactics Game and interact with it.

## Running the Game

For setup instructions (installing Python, dependencies, etc.), please refer to the [SETUP.md](./SETUP.md) guide.

To run the game, execute the main script from the project's root directory:

```bash
python src/main.py
```

### Command-Line Arguments

* `--ai-vs-ai`: Runs the game in AI vs AI mode for testing purposes.
* `--ascii-display`: Enables an optional ASCII representation of the map in the console during gameplay.

*(Note: Additional arguments for chapter selection might be added later.)*

## Interactive Player Input

When it is the Player Phase, you can directly control your units using the keyboard. The system guides you through selecting units, moving them, and choosing actions.

### Input States & Controls

The game uses different "states" to handle your input. Here's a breakdown:

1. **Select Unit State:**
   * **Goal:** Choose a unit to act.
   * **Controls:**
     * `Arrow Keys`: Move the map cursor.
     * `Enter` / `Space`: Select the player unit under the cursor (if they haven't acted).
     * `E`: End the Player Phase manually.
   * **Visuals:** Map shown, cursor highlighted. Units that have acted appear greyed out.

2. **Display Movement Range State:**
   * **Goal:** Choose where to move the selected unit.
   * **Controls:**
     * `Arrow Keys`: Move the cursor within the highlighted movement range.
     * `Enter` / `Space`: Confirm the destination tile.
     * `Backspace` / `Esc`: Cancel movement, return to Select Unit State.
   * **Visuals:** Selected unit highlighted. Valid movement tiles are overlaid. Cursor moves only within this range.

3. **Display Action Menu State:**
   * **Goal:** Choose an action for the unit after moving.
   * **Controls:**
     * `Arrow Keys`: Navigate the action menu (Attack, Staff, Item, Wait, Dance/Play, etc.).
     * `Enter` / `Space`: Select the highlighted menu option.
     * `A`, `S`, `I`, `W`: Shortcuts for Attack, Staff, Item, Wait (if available).
     * `Backspace` / `Esc`: Cancel action selection, revert movement, and return to Display Movement Range State.
   * **Visuals:** A menu appears near the unit listing available actions.

4. **Select Target State (if needed):**
   * **Goal:** Choose a target for an action like Attack, Staff, or Dance/Play.
   * **Controls:**
     * `Arrow Keys`: Cycle through valid targets within range.
     * `Enter` / `Space`: Confirm the selected target.
     * `Backspace` / `Esc`: Cancel targeting, return to Display Action Menu State.
   * **Visuals:** Action range is shown. Valid targets are highlighted. The currently selected target has a distinct indicator.

5. **Execution & End Turn:**
   * Once an action is chosen or a target is confirmed, the action executes automatically.
   * The unit is marked as 'Acted' (greyed out).
   * The game returns to the **Select Unit State** for you to choose the next unit.

### General Tips

* Pay attention to the visual cues: highlighted tiles for movement/action range, greyed-out units that have acted.
* Use `Backspace` / `Esc` frequently to cancel actions or selections if you change your mind.
* Remember the `E` key in the Select Unit state to end your turn when ready.

---

<a id="movement-system-analysis"></a>
# 2. Movement System Analysis

This section provides a technical analysis of the movement system, including how the pathfinding works and how unit movement is processed.

## Overview

The movement system handles calculating reachable tiles, finding paths, and executing movement for units on the map. It integrates with the input handling system and the game state to ensure units move according to their capabilities and the game rules.

## Key Components

1. **MovementSystem**: The main class that orchestrates movement operations, including:
   * `calculate_movement_range()`: Determines which tiles a unit can reach
   * `get_path()`: Finds a path to a target location
   * `execute_move()`: Updates a unit's position by moving along a path

2. **MapSystem**: Provides map-related functionality:
   * `get_reachable_tiles()`: Uses a pathfinding algorithm to find all reachable tiles
   * `is_valid_destination()`: Checks if a tile is a valid movement destination

3. **Pathfinder**: Implements the algorithms to find paths:
   * Uses Dijkstra's algorithm to find reachable tiles
   * `reconstruct_path()`: Creates a step-by-step path between two points

## Input Processing Flow

When a player issues a move command:

1. **CLI Input Handler**: Creates a combined action (e.g., "MOVE_AND_WAIT") with:
   * `move_data` containing the unit ID and path
   * `action_data` for the follow-up action (usually "WAIT")

2. **Engine**: Processes the input and delegates to the Action Handler

3. **Action Handler**: Splits combined actions and calls:
   * `handle_move()` with the path
   * `handle_wait()` or other follow-up action

4. **Movement Execution**: The movement system executes the movement in one step (updating coordinates without animation)

## Technical Implementation Details

### Pathfinding Algorithm

The game uses Dijkstra's algorithm in the pathfinder:

```python
def find_reachable(start_pos, movement_points, terrain_costs, occupied_positions=None):
    # Initialize distances, visited set, and queue
    distances = {start_pos: 0}
    previous = {start_pos: None}
    visited = set()
    queue = [(0, start_pos)]
    
    # Pathfinding loop
    while queue:
        current_distance, current_pos = heapq.heappop(queue)
        
        # Skip if already visited or too far
        if current_pos in visited or current_distance > movement_points:
            continue
            
        visited.add(current_pos)
        
        # Check neighbors
        for next_pos in get_neighbors(current_pos):
            # Skip if occupied
            if occupied_positions and next_pos in occupied_positions:
                continue
                
            # Get terrain cost
            terrain_cost = terrain_costs.get(next_pos, 1)
            
            # Calculate new distance
            new_distance = current_distance + terrain_cost
            
            # Update if better path found
            if new_distance <= movement_points and (next_pos not in distances or new_distance < distances[next_pos]):
                distances[next_pos] = new_distance
                previous[next_pos] = current_pos
                heapq.heappush(queue, (new_distance, next_pos))
    
    return visited, previous
```

### Movement Execution

When executing movement, the system updates the unit's position directly:

```python
def execute_move(self, unit_id, path):
    # Validate the path
    if not path or len(path) < 2:
        return False
        
    # Get the current and target positions
    current_pos = path[0]
    target_pos = path[-1]
    
    # Verify the unit exists and is at the start position
    unit = self.game_state_manager.get_unit(unit_id)
    if not unit or unit.position != current_pos:
        return False
    
    # Update the unit's position
    self.game_state_manager.update_unit_position(unit_id, target_pos)
    
    # Mark that the unit has moved
    unit.has_moved = True
    
    return True
```

## Common Issues and Solutions

### Issue: Units Not Moving or Moving Only One Tile

This can occur when:

1. **Combined Actions Not Processed**: If the game engine doesn't recognize combined action types (e.g., "MOVE_AND_WAIT").
   * **Solution**: Ensure the engine's action processing includes combined types:
     ```python
     if player_input['type'] in ["MOVE", "WAIT", "ATTACK", ..., "MOVE_AND_WAIT", "MOVE_AND_ATTACK"]:
         self.action_handler.process_action(player_input['unit_id'], player_input)
     ```

2. **Path Not Being Fully Executed**: If only part of the path is being processed.
   * **Solution**: Verify that `execute_move()` is receiving the complete path and using the final destination.

3. **Unit State Flag Issues**: If a unit is incorrectly marked as having moved.
   * **Solution**: Check that `has_moved` and `has_acted` flags are properly reset at the start of each turn.

### Issue: Invalid Destination Errors

If units cannot reach seemingly valid destinations:

1. **Check Terrain Costs**: Ensure terrain costs are correctly loaded from data.
2. **Verify Occupied Positions**: Make sure the system correctly tracks which tiles are occupied.
3. **Debug Movement Range Calculation**: Log the output of `calculate_movement_range()` to verify reachable tiles.

## Logging

### Visual Scenario Logger (`src.utils.visual_logger`)

**Purpose:** Provides a human-readable text log of a game scenario, primarily designed for debugging and reviewing AI behavior or specific game sequences. When enabled, it outputs key events and ASCII representations of the map state throughout the simulation.

**Activation:** The logger is activated by passing the `--ascii` command-line flag when running `src/app.py`.

**Output Format (`logs/visual_log_*.txt`):**
- **Initial State:** Records the starting map layout and unit positions.
- **Turn Start:** Marks the beginning of each turn (`----- TURN X START -----`).
- **Phase Start:** Indicates the start of each phase (`--- PHASE ---`).
- **Actions:** Logs actions performed by units, including the unit name, ID, action type, and relevant details (e.g., target position for movement).
- **End-of-Turn State:** Records the map state after the final active phase of each turn (`===== END OF TURN X STATE =====`).

**Integration:**
- An instance of `VisualScenarioLogger` is created in `src/app.py` if the `--ascii` flag is present.
- It's passed to the `EngineCore` instance via the `set_visual_logger()` method after the engine is initialized.
- The `EngineCore` calls the logger's methods (`log_initial_state`, `log_turn_start`, `log_phase_start`, `log_action`, `log_end_of_turn_state`) at appropriate points in the game loop execution.

The logger uses the `CLIDisplay`'s `render_ascii_map` method to generate the map snapshots. 