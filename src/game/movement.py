# src/game/movement.py (Updated)

import math # Import math
from typing import Set, Tuple, Optional
from collections import deque
# Import MoveType and TERRAIN_COSTS
from .models import GameState, Unit, MoveType, TERRAIN_COSTS, TerrainType

def calculate_move_range(game_state: GameState, unit: Unit) -> Set[Tuple[int, int]]:
    """
    Calculates the set of reachable tiles for a given unit using BFS.
    Considers unit.mov, terrain costs based on unit.move_type, blocking by other units,
    and movement penalty if capturing.
    """
    if not unit.is_alive or unit.has_acted: # Also check if alive
        return set()

    start_pos = unit.position
    max_move = unit.mov

    # --- Apply Capture Movement Penalty ---
    # Thracia: Mov halved if carried unit Con > half rescuer Con (+5 if mounted)
    # MVP Simplification: Halve movement if capturing anyone.
    if unit.is_capturing is not None:
        # print(f"  (Movement halved for {unit.name} due to capturing)") # Debug print
        max_move = math.floor(max_move / 2) # Use math.floor
    # ------------------------------------


    reachable = {start_pos}
    # Queue stores tuples of (position, remaining_move)
    queue = deque([(start_pos, max_move)])
    visited_costs = {start_pos: max_move} # Store max remaining move to reach a tile

    unit_move_type = unit.move_type
    cost_table = TERRAIN_COSTS.get(unit_move_type)

    # Handle potential missing move type in TERRAIN_COSTS (fallback or error)
    if not cost_table:
        print(f"Warning: No terrain cost table found for MoveType '{unit_move_type}'. Movement may be incorrect.")
        # Decide on fallback: treat as Infantry or block movement? Let's block for safety.
        return {start_pos} # Or maybe return empty set? {start_pos} seems safer.

    while queue:
        (current_x, current_y), remaining_move = queue.popleft()

        # Explore neighbors (up, down, left, right)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_x, next_y = current_x + dx, current_y + dy
            next_pos = (next_x, next_y)

            # Check map boundaries
            tile = game_state.game_map.get_tile(next_x, next_y)
            if not tile:
                continue

            # --- Terrain Cost Calculation ---
            terrain_type = tile.terrain_type
            move_cost = cost_table.get(terrain_type) # Look up cost

            # Check if impassable (None cost) or unknown terrain type for this move type
            if move_cost is None:
                # print(f"Debug: Tile ({next_x},{next_y}) terrain {terrain_type} impassable for {unit_move_type}")
                continue # Impassable terrain for this unit type

            # Ensure cost is positive
            if move_cost <= 0:
                move_cost = 1 # Minimum cost is 1
            # -----------------------------

            next_remaining_move = remaining_move - move_cost
            if next_remaining_move < 0:
                continue

            # Check if tile is occupied by another unit (cannot move through)
            occupying_unit_id = tile.unit_id
            # Allow moving through the starting tile if revisiting with more move points
            # Blocked only if occupied by a *different* unit
            if occupying_unit_id is not None and occupying_unit_id != unit.id:
                 continue # Blocked by another unit

            # Check if we've found a better path or a new path
            if next_pos not in visited_costs or next_remaining_move > visited_costs[next_pos]:
                visited_costs[next_pos] = next_remaining_move
                reachable.add(next_pos)
                queue.append((next_pos, next_remaining_move))

    return reachable