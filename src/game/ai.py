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

        # Check if tile is empty (cannot move onto occupied tiles)
        occupant_id = game_state.game_map.get_unit_id_at(adj_x, adj_y)
        if occupant_id is None: # Only consider empty tiles
            potential_targets.append(adj_pos)

    if not potential_targets:
        print(f"  AI DEBUG (get_simple_move_target): No empty adjacent tiles found for target {target_unit.name} at {(tx, ty)}")
        return None # No empty adjacent tiles

    print(f"  AI DEBUG (get_simple_move_target): Target: {target_unit.name} at {(tx, ty)}")
    print(f"  AI DEBUG (get_simple_move_target): Potential adjacent targets: {potential_targets}")
    # Find reachable adjacent tiles
    # Ensure move range calculation happens correctly for AI unit
    # Need to temporarily unset has_acted if AI units use it, but they don't yet
    move_range = calculate_move_range(game_state, enemy_unit)
    print(f"  AI DEBUG (get_simple_move_target): Enemy {enemy_unit.name} move_range keys: {list(move_range.keys())}")
    reachable_adj_targets = [pos for pos in potential_targets if pos in move_range]

    print(f"  AI DEBUG (get_simple_move_target): Reachable adjacent targets: {reachable_adj_targets}")

    if not reachable_adj_targets:
        print(f"  AI DEBUG (get_simple_move_target): Cannot reach any empty adjacent tile for target {target_unit.name}")
        return None # Cannot reach any empty adjacent tile

    # Simplistic choice: pick the first reachable adjacent tile found
    # TODO: Improve this later (e.g., pick closest reachable, pathfinding, consider safety)
    result_pos = reachable_adj_targets[0]
    print(f"  AI DEBUG (get_simple_move_target): Returning target position: {result_pos}")
    return result_pos


from .staff_actions import _handle_heal_staff, _handle_status_staff, _apply_staff_costs # Import staff handlers and cost application

def run_enemy_ai(game_state: GameState):
    """Runs the AI logic for all enemy units, including basic staff usage."""
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

        # --- Staff Usage Check (Priority 1) ---
        equipped_item = enemy.equipped_weapon # Use property for equipped item
        if equipped_item and isinstance(equipped_item, Weapon) and equipped_item.wtype == "Staff":
            staff_name = equipped_item.name.lower()
            # TODO: Add more sophisticated target selection and priority
            # Simple Heal AI: Find closest injured enemy within range
            if staff_name in ["heal staff", "mend staff"]:
                 # Find injured allies within staff range
                 potential_heal_targets = []
                 min_r, max_r = equipped_item.range_min, equipped_item.range_max
                 for other_enemy in enemy_units:
                     if other_enemy.id != enemy.id and other_enemy.is_alive and not other_enemy.is_captured and other_enemy.hp < other_enemy.max_hp:
                         dist = abs(enemy.position[0] - other_enemy.position[0]) + abs(enemy.position[1] - other_enemy.position[1])
                         if min_r <= dist <= max_r:
                             potential_heal_targets.append(other_enemy)
                 # Heal the most injured ally in range (simplistic)
                 if potential_heal_targets:
                     potential_heal_targets.sort(key=lambda u: u.hp / u.max_hp) # Sort by lowest HP percentage
                     heal_target = potential_heal_targets[0]
                     print(f"  AI STAFF: {enemy.name} attempting to heal {heal_target.name}.")
                     if _handle_heal_staff(enemy, heal_target, equipped_item):
                         _apply_staff_costs(enemy, equipped_item, game_state)
                         action_taken = True

            # Simple Status Staff AI: Target closest player if in range
            elif staff_name in ["sleep staff", "silence staff", "berserk staff"]:
                 if target_player: # Ensure a player target exists
                     dist = abs(enemy.position[0] - target_player.position[0]) + abs(enemy.position[1] - target_player.position[1])
                     min_r, max_r = equipped_item.range_min, equipped_item.range_max
                     if min_r <= dist <= max_r:
                         print(f"  AI STAFF: {enemy.name} attempting to use {staff_name} on {target_player.name}.")
                         # _handle_status_staff returns True even on miss, indicating an attempt was made
                         if _handle_status_staff(enemy, target_player, equipped_item, staff_name):
                              _apply_staff_costs(enemy, equipped_item, game_state)
                              action_taken = True
            # Add other staff AI logic here (Repair, Torch, etc.)

        # --- Attack Check (Priority 2, if staff not used) ---
        if not action_taken and equipped_item and isinstance(equipped_item, Weapon) and equipped_item.wtype != "Staff":
            # Check if can attack from current position
            dist = abs(enemy.position[0] - target_player.position[0]) + abs(enemy.position[1] - target_player.position[1])
            if equipped_item.range_min <= dist <= equipped_item.range_max:
                print(f"  {enemy.name} is in range. Attacking.")
                simulate_combat(enemy, target_player, game_state)
                action_taken = True
                # Check if target player was defeated
                if not target_player.is_alive:
                    # Check if target_player is still in the list before removing
                    if target_player in player_units:
                         player_units.remove(target_player) # Update list for subsequent AI

        # 2. If couldn't attack from current position, try to move and attack
        # --- Movement Check (Priority 3, if staff/attack not used) ---
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
                        # Recalculate distance after moving
                        dist = abs(enemy.position[0] - target_player.position[0]) + abs(enemy.position[1] - target_player.position[1])
                        if enemy.equipped_weapon and enemy.equipped_weapon.range_min <= dist <= enemy.equipped_weapon.range_max:
                             print(f"  {enemy.name} attacking after moving.")
                             simulate_combat(enemy, target_player, game_state)
                             # Check if target player was defeated
                             if not target_player.is_alive:
                                 # Check if target_player is still in the list before removing
                                 if target_player in player_units:
                                     player_units.remove(target_player) # Update list
                        else:
                             print(f"  {enemy.name} moved but cannot attack target.")
                    else:
                        print(f"  {enemy.name} failed to move to {move_target_pos} (tile might be occupied or invalid).")
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

def run_npc_ai(game_state: GameState):
    """Runs the AI logic for all NPC/Ally units."""
    print("\n--- NPC Phase ---")
    # Get lists of units at the start of the phase
    npc_units = game_state.get_units_by_faction(Faction.ALLY)
    # player_units = game_state.get_units_by_faction(Faction.PLAYER) # NPCs might target enemies or move to objectives
    # enemy_units = game_state.get_units_by_faction(Faction.ENEMY)

    if not npc_units:
        print("No NPC units remaining.")
        print("--- Ending NPC Phase ---")
        return

    for npc in npc_units:
        if not npc.is_alive or npc.is_captured:
            continue

        # Check for status effects preventing action
        if npc.status_effect == StatusEffect.SLEEP:
            print(f"  NPC SKIP: {npc.name} cannot act (Sleeping).")
            continue
        if npc.status_effect == StatusEffect.BERSERK:
            print(f"  NPC SKIP: {npc.name} cannot act (Berserk - AI control not implemented).")
            continue

        print(f"Processing AI for NPC {npc.name} at {npc.position}...")
        # TODO: Implement actual NPC AI logic (e.g., move towards player, attack enemies, escape)
        print(f"  (NPC AI for {npc.name} not implemented yet - taking no action)")
        # Simple placeholder: NPCs do nothing for now

    print("--- Ending NPC Phase ---")