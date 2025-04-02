# src/game/ai.py

import math
from typing import List, Optional, Tuple
from .models import Unit, GameState, Faction, StatusEffect # NEW: Import StatusEffect
from .movement import calculate_move_range # Need this to check reachability
from .combat import simulate_combat

def find_closest_player_unit(enemy_unit: Unit, player_units: List[Unit]) -> Optional[Unit]:
    """Finds the player unit closest to the enemy unit (Manhattan distance)."""
    closest_unit = None
    min_dist = float('inf')
    ex, ey = enemy_unit.position

    for player_unit in player_units:
        # Ensure target is valid (alive and not captured)
        if not player_unit.is_alive or player_unit.is_captured:
            continue
        px, py = player_unit.position
        dist = abs(ex - px) + abs(ey - py)
        if dist < min_dist:
            min_dist = dist
            closest_unit = player_unit
    return closest_unit

def get_simple_move_target(enemy_unit: Unit, target_unit: Unit, game_state: GameState) -> Optional[Tuple[int, int]]:
    """
    Determines a potential tile adjacent to the target for the enemy to move to.
    Very basic: tries adjacent tiles, checks if reachable and empty.
    Returns the target tile coordinates (x, y) or None.
    """
    tx, ty = target_unit.position
    potential_targets = []

    # Check adjacent tiles (up, down, left, right) for attack position
    # Assumes melee range (1) for now
    # TODO: Adapt for different weapon ranges
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        adj_x, adj_y = tx + dx, ty + dy
        adj_pos = (adj_x, adj_y)

        # Check bounds
        if not (0 <= adj_x < game_state.game_map.width and 0 <= adj_y < game_state.game_map.height):
            continue

        # Check if tile is empty or occupied by the moving unit itself (shouldn't happen here)
        occupant_id = game_state.game_map.get_unit_id_at(adj_x, adj_y)
        if occupant_id is None or occupant_id == enemy_unit.id:
            potential_targets.append(adj_pos)

    if not potential_targets:
        # print(f"Debug AI: No empty adjacent tiles found for target {target_unit.name}")
        return None # No empty adjacent tiles

    # Find reachable adjacent tiles
    # Ensure move range calculation happens correctly for AI unit
    # Need to temporarily unset has_acted if AI units use it, but they don't yet
    move_range = calculate_move_range(game_state, enemy_unit)
    reachable_adj_targets = [pos for pos in potential_targets if pos in move_range]

    if not reachable_adj_targets:
        # print(f"Debug AI: Cannot reach any empty adjacent tile for target {target_unit.name}")
        return None # Cannot reach any empty adjacent tile

    # Simplistic choice: pick the first reachable adjacent tile found
    # TODO: Improve this later (e.g., pick closest reachable, pathfinding, consider safety)
    # print(f"Debug AI: Found reachable adjacent tiles: {reachable_adj_targets}")
    return reachable_adj_targets[0]


def run_enemy_ai(game_state: GameState):
    """Runs the AI logic for all enemy units."""
    print("\n--- Enemy Phase ---")
    # Get lists of units at the start of the phase
    # Use the function that already filters correctly
    enemy_units = game_state.get_units_by_faction(Faction.ENEMY)
    player_units = game_state.get_units_by_faction(Faction.PLAYER)

    if not player_units:
        print("No player units remaining.")
        print("--- Ending Enemy Phase ---")
        return
    if not enemy_units:
        print("No enemy units remaining.")
        print("--- Ending Enemy Phase ---")
        return

    # Process enemies one by one
    for enemy in enemy_units:
        # Explicit check at the start of each enemy's turn processing
        # This handles cases where an enemy might be defeated/captured by player actions
        # or even by another AI unit's action if AI targeted allies (not applicable yet)
        if not enemy.is_alive or enemy.is_captured:
            continue

        # NEW: Check for status effects that prevent action
        print(f"  DEBUG: Checking status for {enemy.name}. Status: {enemy.status_effect}") # DEBUG
        if enemy.status_effect == StatusEffect.SLEEP:
            print(f"  AI SKIP: {enemy.name} cannot act (Sleeping).") # DEBUG
            continue
        if enemy.status_effect == StatusEffect.BERSERK:
            print(f"  AI SKIP: {enemy.name} cannot act (Berserk - AI control not implemented).") # DEBUG
            continue
        print(f"  DEBUG: Status OK for {enemy.name}. Proceeding with AI.") # DEBUG

        # Refresh player unit list in case one was defeated *by a previous enemy*
        current_player_units = [p for p in player_units if p.is_alive and not p.is_captured]
        if not current_player_units:
            print("No valid player units left for targeting.")
            break # No more players left to target this phase

        print(f"Processing AI for {enemy.name} at {enemy.position}...")
        target_player = find_closest_player_unit(enemy, current_player_units)

        if not target_player:
            print(f"  {enemy.name} found no targets.")
            continue # No action if no target

        print(f"  {enemy.name} targeting {target_player.name} at {target_player.position}.")

        # --- AI Action Decision ---
        action_taken = False

        # 1. Check if can attack from current position
        if enemy.equipped_weapon:
            dist = abs(enemy.position[0] - target_player.position[0]) + abs(enemy.position[1] - target_player.position[1])
            weapon = enemy.equipped_weapon
            if weapon.range_min <= dist <= weapon.range_max:
                print(f"  {enemy.name} is in range. Attacking.")
                simulate_combat(enemy, target_player, game_state)
                action_taken = True
                # Check if target player was defeated
                if not target_player.is_alive:
                    player_units.remove(target_player) # Update list for subsequent AI

        # 2. If couldn't attack, try to move and attack
        if not action_taken:
            # Ensure enemy can move (not capturing)
            if enemy.is_capturing is not None:
                 print(f"  {enemy.name} cannot move (is capturing).")
            else:
                print(f"  {enemy.name} attempting to move towards target.")
                move_target_pos = get_simple_move_target(enemy, target_player, game_state)

                if move_target_pos:
                    move_x, move_y = move_target_pos
                    # Attempt to move
                    if game_state.game_map.move_unit(enemy, move_x, move_y):
                        print(f"  {enemy.name} moved to {move_target_pos}.")
                        action_taken = True # Consider move as an action for now
                        # Check if can attack after moving
                        dist = abs(enemy.position[0] - target_player.position[0]) + abs(enemy.position[1] - target_player.position[1])
                        if enemy.equipped_weapon and enemy.equipped_weapon.range_min <= dist <= enemy.equipped_weapon.range_max:
                             print(f"  {enemy.name} attacking after moving.")
                             simulate_combat(enemy, target_player, game_state)
                             # Check if target player was defeated
                             if not target_player.is_alive:
                                 player_units.remove(target_player) # Update list
                        else:
                             print(f"  {enemy.name} moved but cannot attack target.")
                    else:
                        print(f"  {enemy.name} failed to move to {move_target_pos} (unexpected).")
                        action_taken = False # Move failed, no action taken
                else:
                    print(f"  {enemy.name} cannot find a suitable position to move and attack.")
                    action_taken = False # No move found

        # 3. If no action taken
        if not action_taken:
            print(f"  {enemy.name} takes no action.")


        # Simple AI: Each enemy acts once
        # No need to track 'has_acted' for enemies in this simple version yet

    print("--- Ending Enemy Phase ---")