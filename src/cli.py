# src/cli.py

import sys
import os # Added for __init__.py check
from typing import Optional, Set, Tuple

# Ensure the 'src' directory is in the Python path
# This allows importing 'game.models' etc. when running cli.py directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.models import GameState, GameMap, Unit
from game.display import render_map
from game.movement import calculate_move_range

# --- Initial Game Setup (Example) ---
def setup_initial_state() -> GameState:
    """Creates a simple initial game state for testing."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Add Leif (Player)
    leif = Unit(id=1, name="Leif", faction="Player", position=(1, 1), hp=20, max_hp=20, mov=5)
    game_state.add_unit(leif)

    # Add a generic enemy
    enemy = Unit(id=101, name="Bandit", faction="Enemy", position=(5, 4), hp=15, max_hp=15, mov=4)
    game_state.add_unit(enemy)

    return game_state

# --- Main CLI Loop ---
def run_cli():
    """Runs the main command-line interface loop."""
    game_state = setup_initial_state()
    current_move_range: Optional[Set[Tuple[int, int]]] = None

    while True:
        # Render the map, passing the current move range for display
        render_map(game_state, current_move_range)

        # Get user input
        command_str = input("Enter command (select x y | move x y | wait | info [x y] | endturn | quit): ").strip().lower()
        parts = command_str.split()
        if not parts:
            continue

        command = parts[0]
        args = parts[1:]

        try:
            if command == "quit":
                print("Exiting game.")
                sys.exit(0)

            elif command == "select":
                if len(args) != 2:
                    print("Usage: select <x> <y>")
                    continue
                x, y = int(args[0]), int(args[1])
                unit_id = game_state.game_map.get_unit_id_at(x, y)
                if unit_id is not None:
                    unit = game_state.get_unit(unit_id)
                    if unit and unit.faction == "Player" and not unit.has_acted:
                        game_state.selected_unit_id = unit_id
                        current_move_range = calculate_move_range(game_state, unit)
                        print(f"Selected {unit.name}. Reachable tiles marked with '*'.")
                    elif unit and unit.faction != "Player":
                        print("Cannot select non-player units.")
                        game_state.selected_unit_id = None
                        current_move_range = None
                    elif unit and unit.has_acted:
                        print(f"{unit.name} has already acted this turn.")
                        game_state.selected_unit_id = None
                        current_move_range = None
                    else: # Should not happen if unit_id is valid
                         game_state.selected_unit_id = None
                         current_move_range = None
                else:
                    print(f"No unit at ({x}, {y}).")
                    game_state.selected_unit_id = None
                    current_move_range = None

            elif command == "move":
                selected_unit = game_state.get_selected_unit()
                if not selected_unit:
                    print("No unit selected.")
                    continue
                if len(args) != 2:
                    print("Usage: move <x> <y>")
                    continue

                x, y = int(args[0]), int(args[1])
                target_pos = (x, y)

                if current_move_range and target_pos in current_move_range:
                    # Attempt to move the unit on the map first
                    if game_state.game_map.move_unit(selected_unit, x, y):
                        print(f"Moved {selected_unit.name} to ({x}, {y}).")
                        selected_unit.has_acted = True # Mark as acted after moving
                        game_state.selected_unit_id = None # Deselect after action
                        current_move_range = None
                    else:
                        print(f"Cannot move to ({x}, {y}) - tile might be occupied or invalid.")
                else:
                    print(f"Cannot move to ({x}, {y}) - not in range.")

            elif command == "wait":
                selected_unit = game_state.get_selected_unit()
                if not selected_unit:
                    print("No unit selected.")
                    continue
                selected_unit.has_acted = True
                print(f"{selected_unit.name} waits.")
                game_state.selected_unit_id = None # Deselect after action
                current_move_range = None

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
                     print(f"Info: {target_unit.name} (ID: {target_unit.id}) | Faction: {target_unit.faction} | Pos: {target_unit.position} | HP: {target_unit.hp}/{target_unit.max_hp} | Mov: {target_unit.mov} | Acted: {target_unit.has_acted}")

            elif command == "endturn":
                if game_state.active_faction == "Player":
                    print("\n--- Ending Player Phase ---")
                    game_state.active_faction = "Enemy"
                    game_state.selected_unit_id = None # Deselect unit
                    current_move_range = None

                    # --- MVP Enemy Phase ---
                    render_map(game_state) # Show map before enemy phase message
                    print("\n--- Enemy Phase ---")
                    # (No actual enemy actions yet)
                    print("--- Ending Enemy Phase ---")
                    # ---------------------

                    game_state.active_faction = "Player"
                    game_state.turn += 1
                    game_state.reset_player_actions()
                    print(f"\n--- Starting Turn {game_state.turn} - Player Phase ---")

                else: # Should not happen in MVP
                    print("Cannot end turn during Enemy Phase.")

            else:
                print(f"Unknown command: {command}")

        except ValueError:
            print("Invalid input. Please enter numbers for coordinates.")
        except IndexError:
             print("Invalid command arguments.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Consider adding more robust error handling or logging later

if __name__ == "__main__":
    # Create __init__.py files if they don't exist to make 'game' a package
    # This helps with running the script directly using `python src/cli.py`
    src_dir = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(src_dir, "..", "__init__.py")):
         # This creates src/__init__.py if needed, though less common
         # open(os.path.join(src_dir, "..", "__init__.py"), 'a').close()
         pass # Usually not needed for top-level src
    if not os.path.exists(os.path.join(src_dir, "game", "__init__.py")):
        open(os.path.join(src_dir, "game", "__init__.py"), 'a').close()

    run_cli()