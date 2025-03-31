# src/game/movement.py

from typing import Set, Tuple, Optional
from collections import deque
from .models import GameState, Unit

def calculate_move_range(game_state: GameState, unit: Unit) -> Set[Tuple[int, int]]:
    """
    Calculates the set of reachable tiles for a given unit using BFS.
    Considers only unit.mov, plain terrain cost (1), and blocking by other units.
    """
    if unit.has_acted:
        return set() # Unit has already acted

    start_pos = unit.position
    max_move = unit.mov
    reachable = {start_pos} # The starting position is always reachable (cost 0)
    # Queue stores tuples of (position, remaining_move)
    queue = deque([(start_pos, max_move)])
    visited_costs = {start_pos: max_move} # Store max remaining move to reach a tile

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

            # --- MVP Cost Calculation ---
            # Assume plain terrain cost is 1 for now
            move_cost = 1
            next_remaining_move = remaining_move - move_cost
            # --------------------------

            if next_remaining_move < 0:
                continue

            # Check if tile is occupied by another unit (cannot move through)
            # Allow moving *into* the start position (handled by visited_costs check)
            occupying_unit_id = tile.unit_id
            # Allow moving through the starting tile if revisiting with more move points
            if occupying_unit_id is not None and occupying_unit_id != unit.id and next_pos != start_pos:
                 continue # Blocked by another unit

            # Check if we've found a better path or a new path
            if next_pos not in visited_costs or next_remaining_move > visited_costs[next_pos]:
                visited_costs[next_pos] = next_remaining_move
                reachable.add(next_pos)
                queue.append((next_pos, next_remaining_move))

    # Remove the starting position itself if we only want destinations?
    # For display purposes, keeping the start position in the set is fine.
    # If only destinations are needed later, uncomment below:
    # reachable.discard(start_pos)

    return reachable