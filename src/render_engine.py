import os

# Simple ASCII characters for units (can be expanded)
PLAYER_CHAR = '@'
ENEMY_CHAR = 'E'
CURSOR_CHAR = 'X' # Example cursor

def clear_console():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def render_game_state(game_state, cursor_pos=None):
    """
    Renders the current game state (map and units) to the console.
    Optionally highlights the cursor position.
    """
    clear_console()
    
    # Create a display grid based on the map
    display_grid = [list(row) for row in game_state.map.grid]

    # Place units on the display grid
    units_by_pos = {(unit.x, unit.y): unit for unit in game_state.units}
    for y in range(game_state.map.height):
        for x in range(game_state.map.width):
            pos = (x, y)
            if pos in units_by_pos:
                unit = units_by_pos[pos]
                display_grid[y][x] = PLAYER_CHAR if unit.affiliation == 'player' else ENEMY_CHAR

    # Place cursor on the display grid
    if cursor_pos and game_state.map.is_valid_coordinate(cursor_pos[0], cursor_pos[1]):
        cx, cy = cursor_pos
        # If cursor is on a unit, maybe display differently? For now, overwrite.
        display_grid[cy][cx] = CURSOR_CHAR

    # Print the grid row by row
    print(f"Turn: {game_state.turn_count} ({game_state.current_turn.capitalize()})")
    print("-" * (game_state.map.width * 2 - 1)) # Separator
    for y in range(game_state.map.height):
        print(" ".join(display_grid[y]))
    print("-" * (game_state.map.width * 2 - 1)) # Separator

    # Print selected unit info if available
    selected_unit = None
    if game_state.selected_unit_id:
        for unit in game_state.units:
            if unit.unit_id == game_state.selected_unit_id:
                selected_unit = unit
                break
    
    if selected_unit:
        print(f"Selected: {selected_unit.name} ({selected_unit.affiliation}) HP: {selected_unit.current_hp}/{selected_unit.max_hp} Pos:({selected_unit.x},{selected_unit.y})")
    else:
        # Optionally print info about the unit under the cursor
        unit_at_cursor = None
        if cursor_pos:
            unit_at_cursor = game_state.get_unit_at(cursor_pos[0], cursor_pos[1])
        if unit_at_cursor:
             print(f"Cursor on: {unit_at_cursor.name} ({unit_at_cursor.affiliation}) HP: {unit_at_cursor.current_hp}/{unit_at_cursor.max_hp}")
        else:
             print("Selected: None") # Indicate nothing is selected

    # Add space for command input prompt
    print("") # Add a blank line before the input prompt