# src/cli.py (Updated)

import sys
import os
from typing import Optional, Set, Tuple

# Ensure the 'src' directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import necessary components
from game.models import GameState, GameMap, Unit, Weapon, Faction, MoveType, TerrainType, Vulnerary, Item
from game.display import render_map
from game.movement import calculate_move_range
from game.combat import simulate_combat
from game.ai import run_enemy_ai

# --- Helper Function ---
def get_attack_range(unit: Unit, game_state: GameState) -> Set[Tuple[int, int]]:
    """Calculates the set of tiles the unit can attack."""
    attack_range = set()
    # Cannot attack if capturing, no weapon, or not alive
    if unit.is_capturing is not None or not unit.equipped_weapon or not unit.is_alive:
        return attack_range

    min_r = unit.equipped_weapon.range_min
    max_r = unit.equipped_weapon.range_max
    ux, uy = unit.position

    # Iterate through a bounding box around the unit
    for x in range(max(0, ux - max_r), min(game_state.game_map.width, ux + max_r + 1)):
        for y in range(max(0, uy - max_r), min(game_state.game_map.height, uy + max_r + 1)):
            dist = abs(x - ux) + abs(y - uy)
            if min_r <= dist <= max_r:
                attack_range.add((x, y))
    return attack_range


# --- Initial Game Setup (Updated with Inventory) ---
def setup_initial_state() -> GameState:
    """Creates a simple initial game state for testing terrain."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)

    # Add some terrain features
    game_map.set_tile_terrain(3, 3, TerrainType.FOREST)
    game_map.set_tile_terrain(4, 3, TerrainType.FOREST)
    game_map.set_tile_terrain(5, 3, TerrainType.FOREST)
    game_map.set_tile_terrain(6, 3, TerrainType.MOUNTAIN)
    game_map.set_tile_terrain(6, 4, TerrainType.MOUNTAIN)
    game_map.set_tile_terrain(6, 5, TerrainType.MOUNTAIN)

    game_state = GameState(game_map=game_map)

    # Weapons & Items
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", range_min=1, range_max=1, uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", range_min=1, range_max=1, uses=50, max_uses=50)
    vulnerary = Vulnerary() # Create a vulnerary instance

    # Add Leif (Player - Cavalry)
    leif_inventory = [iron_sword, vulnerary] # Give Leif items
    leif = Unit(
        id=1, name="Leif", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=0, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7,
        inventory=leif_inventory # Assign inventory
    )
    game_state.add_unit(leif) # add_unit will auto-equip first weapon

    # Add Bandit (Enemy - Infantry) - Lower Con to make capturable by Leif
    bandit_inventory = [iron_axe]
    bandit = Unit(
        id=101, name="Bandit", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=25, hp=1, strength=6, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=4, mov=4, # Lowered Con, start HP low for testing
        inventory=bandit_inventory
    )
    game_state.add_unit(bandit)

    return game_state

# --- Main CLI Loop (Updated) ---
def run_cli():
    """Runs the main command-line interface loop."""
    game_state = setup_initial_state()
    current_move_range: Optional[Set[Tuple[int, int]]] = None
    current_attack_range: Optional[Set[Tuple[int, int]]] = None

    while True:
        render_map(game_state, current_move_range)
        # Update prompt
        prompt = "Cmds: select|move|attack|capture|item|trade|release|wait|info|endturn|quit: "
        command_str = input(prompt).strip() # Don't lowercase yet

        # Ignore empty lines and comments
        if not command_str or command_str.startswith("#"):
            continue

        parts = command_str.lower().split() # Lowercase after comment check
        command = parts[0]
        args = parts[1:] # Arguments are now a list

        try:
            if command == "quit":
                print("Exiting game.")
                sys.exit(0)

            # --- Player Turn Commands ---
            if game_state.active_faction == Faction.PLAYER:
                if command == "select":
                    if len(args) != 2:
                        print("Usage: select <x> <y>")
                        continue
                    x, y = int(args[0]), int(args[1])
                    unit_id = game_state.game_map.get_unit_id_at(x, y)
                    if unit_id is not None:
                        unit = game_state.get_unit(unit_id)
                        # Can't select captured units
                        if unit and unit.is_captured:
                            print(f"{unit.name} is captured and cannot be selected.")
                            game_state.selected_unit_id = None
                            current_move_range = None
                            current_attack_range = None
                        # Allow selecting own unit even if acted (to check info, trade, release)
                        elif unit and unit.faction == Faction.PLAYER and unit.is_alive:
                            game_state.selected_unit_id = unit_id
                            # Only calculate move/attack range if unit hasn't acted
                            if not unit.has_acted:
                                current_move_range = calculate_move_range(game_state, unit)
                                current_attack_range = get_attack_range(unit, game_state)
                            else:
                                current_move_range = None
                                current_attack_range = None # Clear range if acted
                            inventory_names = [(f"{item.name}" + (f" ({item.uses}/{item.max_uses})" if item.uses is not None else "")) for item in unit.inventory]
                            capture_status = f" | Capturing: {game_state.units.get(unit.is_capturing).name}" if unit.is_capturing is not None else "" # Use .units.get()
                            acted_status = " [Acted]" if unit.has_acted else ""
                            print(f"Selected {unit.name}{acted_status}. Move(*). Items: {inventory_names or ['None']}{capture_status}")
                        elif unit and unit.faction != Faction.PLAYER:
                            print("Cannot select non-player units.")
                            game_state.selected_unit_id = None
                            current_move_range = None
                            current_attack_range = None
                        elif unit and not unit.is_alive:
                             print(f"{unit.name} is defeated.")
                             game_state.selected_unit_id = None
                             current_move_range = None
                             current_attack_range = None
                        else:
                             game_state.selected_unit_id = None
                             current_move_range = None
                             current_attack_range = None
                    else:
                        print(f"No unit at ({x}, {y}).")
                        game_state.selected_unit_id = None
                        current_move_range = None
                        current_attack_range = None

                elif command == "move":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    # Check has_acted *before* capture check for correct message priority
                    if selected_unit.has_acted:
                        print(f"{selected_unit.name} has already acted.")
                        continue
                    if selected_unit.is_capturing is not None:
                        print(f"{selected_unit.name} cannot move while capturing (MVP limitation).")
                        continue
                    if len(args) != 2:
                        print("Usage: move <x> <y>")
                        continue

                    x, y = int(args[0]), int(args[1])
                    target_pos = (x, y)

                    # Move range should have been calculated on select if unit hadn't acted
                    if current_move_range is None:
                         print(f"Cannot move {selected_unit.name} (already acted or no range calculated).")
                         continue

                    if target_pos in current_move_range:
                        if game_state.game_map.move_unit(selected_unit, x, y):
                            print(f"Moved {selected_unit.name} to ({x}, {y}).")
                            current_move_range = None
                            current_attack_range = get_attack_range(selected_unit, game_state)
                            inventory_names = [(f"{item.name}" + (f" ({item.uses}/{item.max_uses})" if item.uses is not None else "")) for item in selected_unit.inventory]
                            print(f"Items: {inventory_names or ['None']}")
                        else:
                            print(f"Cannot move to ({x}, {y}) - tile might be occupied or invalid.")
                    else:
                        print(f"Cannot move to ({x}, {y}) - not in range.")

                elif command == "attack":
                    attacker = game_state.get_selected_unit()
                    if not attacker:
                        print("No unit selected.")
                        continue
                    if attacker.has_acted:
                        print(f"{attacker.name} has already acted.")
                        continue
                    if attacker.is_capturing is not None:
                        print(f"{attacker.name} cannot attack while capturing.")
                        continue
                    if not attacker.equipped_weapon:
                        print(f"{attacker.name} has no weapon equipped.")
                        continue
                    if len(args) != 2:
                        print("Usage: attack <x> <y>")
                        continue

                    x, y = int(args[0]), int(args[1])
                    target_pos = (x, y)
                    # Attack range should be calculated on select or move
                    if current_attack_range is None:
                         current_attack_range = get_attack_range(attacker, game_state)

                    if target_pos in current_attack_range:
                        defender_id = game_state.game_map.get_unit_id_at(x, y)
                        if defender_id is not None:
                            defender = game_state.get_unit(defender_id)
                            if defender and defender.is_alive and not defender.is_captured and defender.faction != attacker.faction:
                                simulate_combat(attacker, defender, game_state, is_capture_attempt=False) # Normal attack
                                attacker.has_acted = True
                                game_state.selected_unit_id = None
                                current_move_range = None
                                current_attack_range = None
                            elif defender and defender.faction == attacker.faction:
                                print("Cannot attack allied units.")
                            elif defender and not defender.is_alive:
                                print("Target is already defeated.")
                            elif defender and defender.is_captured:
                                print("Cannot attack captured units.")
                            else:
                                print(f"Invalid target unit at ({x}, {y}).")
                        else:
                            print(f"No unit to attack at ({x}, {y}).")
                    else:
                        print(f"Target ({x}, {y}) is out of attack range.")


                elif command == "capture":
                    attacker = game_state.get_selected_unit()
                    if not attacker:
                        print("No unit selected.")
                        continue
                    if attacker.has_acted:
                        print(f"{attacker.name} has already acted.")
                        continue
                    if attacker.is_capturing is not None:
                        print(f"{attacker.name} is already capturing someone.")
                        continue
                    if not attacker.equipped_weapon:
                        print(f"{attacker.name} has no weapon equipped (needed for capture attempt).")
                        continue
                    if len(args) != 2:
                        print("Usage: capture <x> <y>")
                        continue

                    x, y = int(args[0]), int(args[1])
                    target_pos = (x, y)
                    # Attack range should be calculated on select or move
                    if current_attack_range is None:
                         current_attack_range = get_attack_range(attacker, game_state)

                    if target_pos in current_attack_range:
                        defender_id = game_state.game_map.get_unit_id_at(x, y)
                        if defender_id is not None:
                            defender = game_state.get_unit(defender_id)
                            if defender and defender.is_alive and not defender.is_captured and defender.faction == Faction.ENEMY:
                                simulate_combat(attacker, defender, game_state, is_capture_attempt=True) # Capture attempt
                                attacker.has_acted = True
                                # Keep unit selected after capture attempt
                                current_move_range = None # Clear ranges
                                current_attack_range = None
                            elif defender and defender.faction != Faction.ENEMY:
                                print("Cannot capture non-enemy units.")
                            elif defender and not defender.is_alive:
                                print("Target is already defeated.")
                            elif defender and defender.is_captured:
                                print("Target is already captured.")
                            else:
                                print(f"Invalid target unit at ({x}, {y}).")
                        else:
                            print(f"No unit to capture at ({x}, {y}).")
                    else:
                        print(f"Target ({x}, {y}) is out of range for capture attempt.")


                elif command == "item":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    if selected_unit.has_acted:
                         print(f"{selected_unit.name} has already acted.")
                         continue
                    if selected_unit.is_capturing is not None:
                        print(f"{selected_unit.name} cannot use items while capturing.")
                        continue
                    if not args:
                        usable_items = [f"{item.name}({item.uses})" for item in selected_unit.inventory if not isinstance(item, Weapon) and item.is_usable()]
                        print(f"Usable items for {selected_unit.name}: {usable_items or ['None']}")
                        continue

                    item_name_to_use = " ".join(args)
                    item_to_use = selected_unit.get_item_by_name(item_name_to_use)

                    if not item_to_use:
                        print(f"{selected_unit.name} does not have '{item_name_to_use}'.")
                        continue
                    if isinstance(item_to_use, Weapon):
                        print(f"Cannot 'use' a weapon directly. Use 'attack' or 'capture'.")
                        continue
                    if not item_to_use.is_usable():
                         print(f"Cannot use {item_to_use.name}, no uses left.")
                         continue

                    item_used_successfully = False
                    if isinstance(item_to_use, Vulnerary):
                        if selected_unit.hp >= selected_unit.max_hp:
                            print(f"{selected_unit.name} is already at full HP.")
                        else:
                            if item_to_use.use():
                                healed_amount = min(item_to_use.heal_amount, selected_unit.max_hp - selected_unit.hp)
                                selected_unit.hp += healed_amount
                                print(f"{selected_unit.name} used {item_to_use.name}, recovered {healed_amount} HP. (HP: {selected_unit.hp}/{selected_unit.max_hp})")
                                item_used_successfully = True
                                if item_to_use.uses == 0:
                                    print(f"{item_to_use.name} broke.")
                                    selected_unit.remove_item(item_to_use)
                            else:
                                print(f"Failed to use {item_to_use.name} (no uses left).")
                    else:
                        print(f"Item type '{item_to_use.name}' use effect not implemented yet.")

                    if item_used_successfully:
                        selected_unit.has_acted = True
                        game_state.selected_unit_id = None
                        current_move_range = None
                        current_attack_range = None


                elif command == "trade":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue

                    print(f"Trade for {selected_unit.name}:")
                    inventory_names = [(f"{item.name}" + (f" ({item.uses}/{item.max_uses})" if item.uses is not None else "")) for item in selected_unit.inventory]
                    print(f"  Own Inventory: {inventory_names or ['None']}")

                    adjacent_units = []
                    sx, sy = selected_unit.position
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = sx + dx, sy + dy
                        adj_unit_id = game_state.game_map.get_unit_id_at(nx, ny)
                        if adj_unit_id is not None:
                            adj_unit = game_state.get_unit(adj_unit_id)
                            if adj_unit and adj_unit.is_alive and adj_unit.faction == Faction.PLAYER:
                                adjacent_units.append(adj_unit)

                    captive_unit = None
                    if selected_unit.is_capturing is not None:
                        captive_unit = game_state.units.get(selected_unit.is_capturing)

                    if captive_unit:
                        captive_inv_names = [(f"{item.name}" + (f" ({item.uses}/{item.max_uses})" if item.uses is not None else "")) for item in captive_unit.inventory]
                        print(f"  Captive ({captive_unit.name}) Inventory: {captive_inv_names or ['None']}")
                        # TODO: Add command like 'take <item_name> from captive'
                    elif adjacent_units:
                        print("  Adjacent Allies:")
                        for ally in adjacent_units:
                            ally_inv_names = [(f"{item.name}" + (f" ({item.uses}/{item.max_uses})" if item.uses is not None else "")) for item in ally.inventory]
                            print(f"    - {ally.name} at {ally.position}: {ally_inv_names or ['None']}")
                        # TODO: Add command like 'give <item_name> to <ally_id>' or 'swap <own_idx> <ally_idx> with <ally_id>'
                    else:
                        print("  No adjacent allies or captive to trade with.")


                elif command == "release":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    # Allow release even if acted? Yes.

                    if selected_unit.is_capturing is not None:
                        captive_id = selected_unit.is_capturing
                        captive_unit = game_state.units.get(captive_id)
                        if captive_unit:
                            print(f"{selected_unit.name} releases {captive_unit.name}.")
                            captive_unit.is_captured = False
                        else:
                             print(f"Error: Captive unit ID {captive_id} not found.")

                        selected_unit.is_capturing = None
                        # Releasing counts as action
                        selected_unit.has_acted = True
                        # Keep unit selected after release
                        # game_state.selected_unit_id = None # REMOVED
                        current_move_range = None # Clear ranges
                        current_attack_range = None
                    else:
                        print(f"{selected_unit.name} is not capturing anyone.")


                elif command == "wait":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    if selected_unit.has_acted:
                         print(f"{selected_unit.name} has already acted.")
                         continue
                    selected_unit.has_acted = True
                    print(f"{selected_unit.name} waits.")
                    game_state.selected_unit_id = None
                    current_move_range = None
                    current_attack_range = None

                elif command == "info":
                    target_unit = None
                    # PRIORITIZE checking for coordinate arguments
                    if len(args) == 2:
                        try:
                            x, y = int(args[0]), int(args[1])
                            unit_id = game_state.game_map.get_unit_id_at(x, y)
                            if unit_id is not None:
                                target_unit = game_state.units.get(unit_id) # Get directly from dict
                                if not target_unit:
                                     print(f"Error: Unit ID {unit_id} found on map but not in units dictionary.")
                            else:
                                print(f"No unit at ({x}, {y}).")
                                target_unit = None # Ensure target_unit is None
                        except ValueError:
                             print("Invalid coordinates for info command.")
                             target_unit = None # Ensure target_unit is None on error
                    elif len(args) == 0: # No coordinates provided, use selected unit
                        target_unit = game_state.get_selected_unit()
                        if not target_unit:
                             print("No unit selected and no coordinates provided.")
                    else: # Incorrect number of arguments
                        print("Usage: info or info <x> <y>")

                    # Display info if a unit was found by either method
                    if target_unit:
                         capture_status_str = ""
                         if target_unit.is_captured:
                             capture_status_str = " | Status: Captured"
                         elif target_unit.is_capturing is not None:
                             captive = game_state.units.get(target_unit.is_capturing)
                             captive_name = captive.name if captive else "Unknown"
                             capture_status_str = f" | Status: Capturing {captive_name}"
                         elif not target_unit.is_alive:
                              capture_status_str = " | Status: Defeated"
                         else:
                              capture_status_str = " | Status: Alive"

                         print(f"Info: {target_unit.name} (ID: {target_unit.id}) | Faction: {target_unit.faction} | MoveType: {target_unit.move_type}{capture_status_str}")
                         print(f"  Pos: {target_unit.position} | HP: {target_unit.hp}/{target_unit.max_hp} | Mov: {target_unit.mov}")
                         print(f"  Stats: Str:{target_unit.strength} Skl:{target_unit.skill} Spd:{target_unit.speed} Lck:{target_unit.luck} Def:{target_unit.defense} Con:{target_unit.constitution}")
                         inventory_names = [(f"{item.name}" + (f" ({item.uses}/{item.max_uses})" if item.uses is not None else "")) for item in target_unit.inventory]
                         print(f"  Inventory: {inventory_names or ['None']}")
                         equipped_idx = target_unit.equipped_weapon_index
                         equipped_name = target_unit.inventory[equipped_idx].name if equipped_idx is not None and equipped_idx < len(target_unit.inventory) else "None"
                         acted_status = " [Acted]" if target_unit.has_acted else ""
                         print(f"  Equipped: {equipped_name} | Acted: {target_unit.has_acted}{acted_status}")


                elif command == "endturn":
                    if game_state.active_faction == Faction.PLAYER:
                        print("\n--- Ending Player Phase ---")
                        game_state.active_faction = Faction.ENEMY
                        game_state.selected_unit_id = None
                        current_move_range = None
                        current_attack_range = None

                        render_map(game_state)
                        run_enemy_ai(game_state)

                        leif = game_state.units.get(1)
                        if leif and not leif.is_alive:
                            render_map(game_state)
                            print("\n--- GAME OVER ---")
                            print("Leif has been defeated!")
                            sys.exit(0)

                        game_state.active_faction = Faction.PLAYER
                        game_state.turn += 1
                        game_state.reset_player_actions()
                        print(f"\n--- Starting Turn {game_state.turn} - Player Phase ---")
                    else:
                        print("Cannot end turn now.")

                else:
                    print(f"Unknown command: {command}")

            elif game_state.active_faction == Faction.ENEMY:
                 print("Waiting for Enemy Phase to complete...")

        except ValueError:
            print("Invalid input. Please enter numbers for coordinates.")
        except IndexError:
             print("Invalid command arguments.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    src_dir = os.path.dirname(__file__)
    game_dir = os.path.join(src_dir, "game")
    if not os.path.exists(os.path.join(game_dir, "__init__.py")):
        open(os.path.join(game_dir, "__init__.py"), 'a').close()

    run_cli()