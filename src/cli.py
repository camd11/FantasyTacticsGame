# src/cli.py (Updated)

import sys
import os
from typing import Optional, Set, Tuple

# Ensure the 'src' directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import necessary components
from game.models import GameState, GameMap, Unit, Weapon, Faction
from game.display import render_map # Display needs update too
from game.movement import calculate_move_range
from game.combat import simulate_combat # Import combat simulation

# --- Helper Function ---
def get_attack_range(unit: Unit, game_state: GameState) -> Set[Tuple[int, int]]:
    """Calculates the set of tiles the unit can attack."""
    attack_range = set()
    if not unit.equipped_weapon or not unit.is_alive: # Cannot attack if dead or no weapon
        return attack_range

    min_r = unit.equipped_weapon.range_min
    max_r = unit.equipped_weapon.range_max
    ux, uy = unit.position

    # Iterate through a bounding box around the unit
    # Ensure bounds check against the actual map dimensions from game_state
    for x in range(max(0, ux - max_r), min(game_state.game_map.width, ux + max_r + 1)):
        for y in range(max(0, uy - max_r), min(game_state.game_map.height, uy + max_r + 1)):
            # Calculate Manhattan distance
            dist = abs(x - ux) + abs(y - uy)
            if min_r <= dist <= max_r:
                attack_range.add((x, y))
    return attack_range


# --- Initial Game Setup (Updated with Stats & Weapons) ---
def setup_initial_state() -> GameState:
    """Creates a simple initial game state for testing with combat."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", range_min=1, range_max=1)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", range_min=1, range_max=1)

    # Add Leif (Player) - Changed starting position
    leif = Unit(
        id=1, name="Leif", faction=Faction.PLAYER, position=(4, 4), # Start at (4, 4)
        max_hp=20, hp=20, strength=5, magic=0, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=5,
        equipped_weapon=iron_sword
    )
    game_state.add_unit(leif)

    # Add a generic enemy
    bandit = Unit(
        id=101, name="Bandit", faction=Faction.ENEMY, position=(5, 4),
        max_hp=25, hp=25, strength=6, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4,
        equipped_weapon=iron_axe
    )
    game_state.add_unit(bandit)

    return game_state

# --- Main CLI Loop (Updated) ---
def run_cli():
    """Runs the main command-line interface loop."""
    # No longer global, pass game_state where needed
    game_state = setup_initial_state()
    current_move_range: Optional[Set[Tuple[int, int]]] = None
    current_attack_range: Optional[Set[Tuple[int, int]]] = None # Track attack range

    while True:
        # Render the map, passing ranges for display
        # TODO: Update render_map to show attack range (e.g., with '+')
        render_map(game_state, current_move_range) # Attack range display TBD

        # Get user input
        prompt = "Enter command (select x y | move x y | attack x y | wait | info [x y] | endturn | quit): "
        command_str = input(prompt).strip().lower()
        parts = command_str.split()
        if not parts:
            continue

        command = parts[0]
        args = parts[1:]

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
                        if unit and unit.faction == Faction.PLAYER and not unit.has_acted and unit.is_alive:
                            game_state.selected_unit_id = unit_id
                            current_move_range = calculate_move_range(game_state, unit)
                            current_attack_range = get_attack_range(unit, game_state) # Calculate attack range
                            print(f"Selected {unit.name}. Move(*), Attack(+) - Attack range display TBD.")
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
                        elif unit and unit.has_acted:
                            print(f"{unit.name} has already acted this turn.")
                            game_state.selected_unit_id = None
                            current_move_range = None
                            current_attack_range = None
                        else: # Should not happen if unit_id is valid
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
                    if selected_unit.has_acted:
                        print(f"{selected_unit.name} has already acted.")
                        continue
                    if len(args) != 2:
                        print("Usage: move <x> <y>")
                        continue

                    x, y = int(args[0]), int(args[1])
                    target_pos = (x, y)

                    # Need to recalculate move range if not already calculated
                    if current_move_range is None:
                         current_move_range = calculate_move_range(game_state, selected_unit)

                    if target_pos in current_move_range:
                        if game_state.game_map.move_unit(selected_unit, x, y):
                            print(f"Moved {selected_unit.name} to ({x}, {y}).")
                            # Unit can still act after moving (e.g., attack)
                            # Update ranges from new position
                            current_move_range = None # Clear move range after move
                            current_attack_range = get_attack_range(selected_unit, game_state)
                            # Keep unit selected
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
                    if not attacker.equipped_weapon:
                        print(f"{attacker.name} has no weapon equipped.")
                        continue
                    if len(args) != 2:
                        print("Usage: attack <x> <y>")
                        continue

                    x, y = int(args[0]), int(args[1])
                    target_pos = (x, y)

                    # Calculate current attack range from attacker's position
                    # Need to recalculate in case unit moved
                    current_attack_range = get_attack_range(attacker, game_state)

                    if target_pos in current_attack_range:
                        defender_id = game_state.game_map.get_unit_id_at(x, y)
                        if defender_id is not None:
                            defender = game_state.get_unit(defender_id)
                            # Check if defender exists, is alive, and is not on the same faction
                            if defender and defender.is_alive and defender.faction != attacker.faction:
                                # --- Execute Combat ---
                                simulate_combat(attacker, defender, game_state)
                                # --------------------
                                attacker.has_acted = True # Mark attacker as acted
                                game_state.selected_unit_id = None # Deselect
                                current_move_range = None
                                current_attack_range = None
                            elif defender and defender.faction == attacker.faction:
                                print("Cannot attack allied units.")
                            elif defender and not defender.is_alive:
                                print("Target is already defeated.")
                            else: # Should not happen if defender_id is valid
                                print(f"Invalid target unit at ({x}, {y}).")
                        else:
                            print(f"No unit to attack at ({x}, {y}).")
                    else:
                        print(f"Target ({x}, {y}) is out of attack range.")


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
                    game_state.selected_unit_id = None # Deselect after action
                    current_move_range = None
                    current_attack_range = None

                elif command == "info":
                    target_unit = None
                    if len(args) == 2:
                        x, y = int(args[0]), int(args[1])
                        unit_id = game_state.game_map.get_unit_id_at(x, y)
                        if unit_id is not None:
                            target_unit = game_state.get_unit(unit_id)
                        else:
                            print(f"No unit at ({x}, {y}).")
                    elif len(args) == 0:
                        target_unit = game_state.get_selected_unit()
                        if not target_unit:
                             print("No unit selected and no coordinates provided.")
                    else:
                        print("Usage: info [x y]")

                    if target_unit:
                         weapon_name = target_unit.equipped_weapon.name if target_unit.equipped_weapon else "None"
                         status = "Alive" if target_unit.is_alive else "Defeated"
                         print(f"Info: {target_unit.name} (ID: {target_unit.id}) | Faction: {target_unit.faction} | Status: {status}")
                         print(f"  Pos: {target_unit.position} | HP: {target_unit.hp}/{target_unit.max_hp} | Mov: {target_unit.mov}")
                         print(f"  Stats: Str:{target_unit.strength} Skl:{target_unit.skill} Spd:{target_unit.speed} Lck:{target_unit.luck} Def:{target_unit.defense} Con:{target_unit.constitution}")
                         print(f"  Weapon: {weapon_name} | Acted: {target_unit.has_acted}")


                elif command == "endturn":
                    print("\n--- Ending Player Phase ---")
                    game_state.active_faction = Faction.ENEMY
                    game_state.selected_unit_id = None # Deselect unit
                    current_move_range = None
                    current_attack_range = None

                    # --- Trigger Enemy Phase ---
                    # (Still basic for now)
                    render_map(game_state) # Show map before enemy phase message
                    print("\n--- Enemy Phase ---")
                    # TODO: Implement basic enemy AI here later
                    print("(Enemy AI not implemented yet)")
                    print("--- Ending Enemy Phase ---")
                    # ---------------------

                    game_state.active_faction = Faction.PLAYER
                    game_state.turn += 1
                    game_state.reset_player_actions()
                    print(f"\n--- Starting Turn {game_state.turn} - Player Phase ---")

                else:
                    print(f"Unknown command: {command}")

            # --- Enemy Turn Commands (Not interactive in MVP) ---
            elif game_state.active_faction == Faction.ENEMY:
                 # This block shouldn't be reached with current endturn logic
                 print("Error: Input received during Enemy Phase.")
                 # Force end enemy turn for now if somehow reached
                 game_state.active_faction = Faction.PLAYER
                 game_state.turn += 1
                 game_state.reset_player_actions()


        except ValueError:
            print("Invalid input. Please enter numbers for coordinates.")
        except IndexError:
             print("Invalid command arguments.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Consider adding more robust error handling or logging later

if __name__ == "__main__":
    # Create __init__.py files if they don't exist to make 'game' a package
    src_dir = os.path.dirname(__file__)
    game_dir = os.path.join(src_dir, "game")
    if not os.path.exists(os.path.join(game_dir, "__init__.py")):
        open(os.path.join(game_dir, "__init__.py"), 'a').close()

    run_cli()