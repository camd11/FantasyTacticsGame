from src.game_state import GameState
from src.map import Map
from src.unit import Unit
from src.render_engine import render_game_state
from src.input_handler import get_player_input, parse_command # Import input handling
from data import chapter1_map as map_data # Import the map data module

def initialize_game():
    """Loads data and creates the initial GameState."""

    # Create the map object
    game_map = Map(map_data.WIDTH, map_data.HEIGHT, map_data.GRID_DATA)

    # Create unit objects from data
    units = []
    for unit_def in map_data.INITIAL_UNITS:
        unit_id, name, affiliation, stats, position = unit_def
        # TODO: Handle items later
        unit = Unit(unit_id, name, affiliation, stats, position)
        units.append(unit)

    # Create the game state
    game_state = GameState(game_map, units)

    return game_state

def main():
    """Main function to initialize and run the game loop."""
    print("Initializing game...")
    game_state = initialize_game()
    cursor_x, cursor_y = 0, 0 # Initial cursor position

    print("Starting game loop...")
    while True:
        # 1. Render current state
        render_game_state(game_state, cursor_pos=(cursor_x, cursor_y))
        # 2. Get player input
        # Update prompt to include 'e' for select/examine
        command_str = get_player_input(f"({cursor_x},{cursor_y}) Enter command (wasd=move, e=select, quit): ")
        action, args = parse_command(command_str)

        # 3. Process input
        if action == 'quit':
            print("Exiting game.")
            break
        elif action == 'cursor_up':
            cursor_y = max(0, cursor_y - 1)
        elif action == 'cursor_down':
            cursor_y = min(game_state.map.height - 1, cursor_y + 1)
        elif action == 'cursor_left':
            cursor_x = max(0, cursor_x - 1)
        elif action == 'cursor_right':
            cursor_x = min(game_state.map.width - 1, cursor_x + 1)
        elif action == 'select':
            unit_at_cursor = game_state.get_unit_at(cursor_x, cursor_y)
            if unit_at_cursor and unit_at_cursor.affiliation == 'player':
                # Select the player unit
                game_state.selected_unit_id = unit_at_cursor.unit_id
                print(f"Selected {unit_at_cursor.name}.")
                # TODO: Show movement range or action menu later
            else:
                # Deselect if clicking empty space or non-player unit
                if game_state.selected_unit_id:
                    print("Deselected unit.")
                game_state.selected_unit_id = None
        elif action:
            # Placeholder for other actions (move, attack, etc.)
            print(f"Action '{action}' not implemented yet.")
        else:
            if command_str: # Avoid printing for empty input
                print(f"Unknown command: '{command_str}'")

        # Add game logic updates here later (e.g., unit movement, enemy turn)

if __name__ == "__main__":
    main()