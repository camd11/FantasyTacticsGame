# Specification: Movement System

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The Movement System handles the process of moving units across the game map. It determines the range of movement available to a unit, validates proposed moves, and updates the unit's position in the game state. It collaborates closely with the `MapSystem` to understand terrain costs and pathfinding, and with the `GameStateManager` to access unit stats (Movement) and update unit positions. It also plays a role in enabling Canto movement after certain actions.

## 2. Functional Requirements

### 2.1. Movement Range Calculation
    - Determine the set of reachable tiles for a selected unit.
    - Delegate the core pathfinding logic to the `MapSystem`'s `get_reachable_tiles(unit_id)` function, which considers:
        - Unit's Movement stat (`GameStateManager`).
        - Unit's movement type and state (mounted/dismounted) (`GameStateManager`, `DataProvider`).
        - Terrain costs (`MapSystem`, `DataProvider`).
        - Obstacles (enemy units) (`GameStateManager`, `MapSystem`).
    - Provide an interface for the UI or AI to request this movement range.

### 2.2. Move Validation
    - Validate if a target destination tile is within the calculated reachable tiles for the selected unit.
    - Ensure the target tile is not occupied by another unit (unless specific rules allow, e.g., rescuing).

### 2.3. Move Execution
    - Update the unit's position in the `GameStateManager` upon confirming a valid move.
    - Mark the unit as having moved (`has_moved = true` in `UnitState` via `GameStateManager`).
    - Potentially store the path taken if needed for Canto calculation or visualization.

### 2.4. Canto Movement Handling
    - Calculate remaining movement points after a unit performs an action that allows Canto (e.g., using item, trading, visiting) (Ref: `research.md`, Sec 1).
        - This requires knowing the cost of the path taken for the initial move.
    - Determine the Canto movement range based on remaining points and the unit's current position. This re-uses the pathfinding logic (`MapSystem.get_reachable_tiles`) with the remaining movement points.
    - Execute the Canto move by updating the unit's position in `GameStateManager`.

## 3. Pseudocode (movement_system.py)

```python
# --- movement_system.py ---

# Import necessary modules/classes (GameStateManager, MapSystem)

class MovementSystem:
    gameStateManager = null
    mapSystem = null
    
    # Store temporary data for the current unit's move calculation
    _current_unit_id = null
    _reachable_tiles = set()
    _path_costs = {} # Optional: Store cost to reach each tile {pos: cost}

    function initialize(gameStateManager_instance, mapSystem_instance):
        gameStateManager = gameStateManager_instance
        mapSystem = mapSystem_instance
        log("MovementSystem initialized.")

    # --- Movement Calculation ---

    # TDD: Test calculate_movement_range calls MapSystem and returns correct tiles
    function calculate_movement_range(unit_id):
        """Calculates and stores the reachable tiles for the given unit."""
        self._current_unit_id = unit_id
        # Delegate pathfinding to MapSystem
        # MapSystem's get_reachable_tiles handles terrain, unit type, Mov stat etc.
        self._reachable_tiles = mapSystem.get_reachable_tiles(unit_id) 
        # Optionally store costs if MapSystem provides them, needed for Canto
        # self._path_costs = mapSystem.get_path_costs(unit_id) 
        log(f"Calculated movement range for {unit_id}: {len(self._reachable_tiles)} tiles.")
        return self._reachable_tiles

    # TDD: Test get_current_range returns the previously calculated range
    function get_current_range():
        """Returns the set of reachable tiles calculated by the last call to calculate_movement_range."""
        return self._reachable_tiles

    # --- Move Validation ---

    # TDD: Test is_valid_destination checks against the calculated reachable tiles
    function is_valid_destination(unit_id, target_pos):
        """Checks if the target position is within the unit's current calculated movement range."""
        if unit_id != self._current_unit_id:
            log("Warning: Validating move for unit different from last calculation.")
            # Optionally recalculate range, or return False
            self.calculate_movement_range(unit_id) 
            
        if target_pos not in self._reachable_tiles:
            log(f"Move validation failed: {target_pos} not in reachable tiles for {unit_id}.")
            return False
            
        # Additional check: Ensure target tile isn't blocked *right now* (e.g., by an ally who just moved there)
        # Although MapSystem pathfinding should prevent moving *through* enemies, final destination check is good.
        occupying_unit_id = gameStateManager.get_unit_at(target_pos)
        if occupying_unit_id and occupying_unit_id != unit_id:
             log(f"Move validation failed: {target_pos} is currently occupied by {occupying_unit_id}.")
             return False # Cannot end move on an occupied tile

        return True

    # --- Move Execution ---

    # TDD: Test execute_move updates unit position and has_moved flag in GameStateManager
    function execute_move(unit_id, path): # path is a list of coordinates [start, ..., end]
        """Executes the move, updating the unit's state."""
        if not path:
            log("Error: Cannot execute move with empty path.")
            return False
            
        target_pos = path[-1]
        
        # Re-validate just in case state changed? Or rely on EngineCore sequence. Assume valid for now.
        # if not self.is_valid_destination(unit_id, target_pos): return False 

        unit = gameStateManager.get_unit(unit_id)
        if not unit: return False

        log(f"Executing move for {unit_id} to {target_pos}.")
        gameStateManager.move_unit(unit_id, target_pos)
        unit.has_moved = True # Set flag via GameStateManager if direct access isn't allowed
        
        # Store path taken cost if needed for Canto
        # path_cost = self.calculate_path_cost(path, unit_id)
        # gameStateManager.set_unit_last_move_cost(unit_id, path_cost) # Store temporarily

        # Clear cached range for the moved unit
        if unit_id == self._current_unit_id:
             self._current_unit_id = None
             self._reachable_tiles = set()
             self._path_costs = {}

        return True

    # --- Canto Handling ---

    # TDD: Test calculate_canto_range uses remaining movement points correctly
    function calculate_canto_range(unit_id):
        """Calculates the Canto movement range based on remaining movement points."""
        unit = gameStateManager.get_unit(unit_id)
        if not unit: return set()

        # Retrieve the cost of the initial move (needs to be stored after execute_move)
        # initial_move_cost = gameStateManager.get_unit_last_move_cost(unit_id) 
        initial_move_cost = self.get_cost_to_reach(unit.position) # Use stored costs if available

        total_movement = unit.base_stats.get(MOV, 0)
        remaining_movement = total_movement - initial_move_cost

        if remaining_movement <= 0:
            return set()

        # Calculate reachable tiles from current position with remaining movement
        # Use MapSystem's pathfinder again
        canto_reachable_nodes = mapSystem.pathfinder.find_reachable(unit.position, remaining_movement, unit_id)
        canto_tiles = set(canto_reachable_nodes.keys())
        
        # Store this temporarily if needed for validation/execution
        self._current_unit_id = unit_id # Reuse cache for Canto move
        self._reachable_tiles = canto_tiles
        # self._path_costs = canto_reachable_nodes # Store costs if needed

        log(f"Calculated Canto range for {unit_id} with {remaining_movement} points: {len(canto_tiles)} tiles.")
        return canto_tiles

    # TDD: Test execute_canto_move updates position without changing has_acted flag
    function execute_canto_move(unit_id, path):
        """Executes the Canto move."""
        if not path: return False
        target_pos = path[-1]

        # Validate Canto destination (check against _reachable_tiles calculated by calculate_canto_range)
        if not self.is_valid_destination(unit_id, target_pos): # Reuse validation logic
             log(f"Invalid Canto destination {target_pos}")
             return False

        log(f"Executing Canto move for {unit_id} to {target_pos}.")
        gameStateManager.move_unit(unit_id, target_pos)
        # Do NOT set has_acted = True here, Canto happens after the action is done.
        # Do NOT reset has_moved = False, the unit *has* moved this turn.

        # Clear cached range
        if unit_id == self._current_unit_id:
             self._current_unit_id = None
             self._reachable_tiles = set()
             self._path_costs = {}
             
        return True

    # --- Helpers ---

    function get_cost_to_reach(position):
        """Retrieves the calculated movement cost to reach a specific tile from the last range calculation."""
        # Requires _path_costs to be populated by calculate_movement_range
        return self._path_costs.get(position, IMPASSABLE)

    # function calculate_path_cost(path, unit_id):
    #     """Calculates the total movement cost of a given path."""
    #     cost = 0
    #     for i in range(1, len(path)):
    #         tile_cost = mapSystem.get_movement_cost(path[i], unit_id)
    #         if tile_cost == IMPASSABLE: return IMPASSABLE # Should not happen for valid path
    #         cost += tile_cost
    #     return cost