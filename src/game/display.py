# src/game/display.py (Updated)

from typing import Set, Tuple, Optional
from .models import GameState, Unit, Faction, TerrainType # Import Faction, TerrainType

def render_map(game_state: GameState, move_range: Optional[Set[Tuple[int, int]]] = None):
    """Renders the current game map and state to the console."""
    print(f"\n--- Turn {game_state.turn} - {game_state.active_faction} Phase ---")

    selected_unit = game_state.get_selected_unit()
    selected_pos = selected_unit.position if selected_unit else None
    if move_range is None:
        move_range = set() # Default to empty set if no range provided

    # Header row (X coordinates)
    header = "   " + " ".join(f"{str(i):<2}" for i in range(game_state.game_map.width))
    print(header)
    # Adjust border length
    print("  +" + "---"*game_state.game_map.width + "+") # Top border

    for y in range(game_state.game_map.height):
        row_str = f"{str(y):<2}|" # Y coordinate prefix
        for x in range(game_state.game_map.width):
            unit_id = game_state.game_map.get_unit_id_at(x, y)
            current_pos = (x, y)

            # Determine base terrain character
            terrain_char = "." # Default Plain
            tile_for_render = game_state.game_map.get_tile(x, y)
            if tile_for_render:
                if tile_for_render.terrain_type == TerrainType.FOREST:
                    terrain_char = "F"
                elif tile_for_render.terrain_type == TerrainType.MOUNTAIN:
                    terrain_char = "M"
                # Add more terrain chars later (e.g., '#' for Fort, '~' for Water)

            display_char = terrain_char # Start with terrain char

            # Check unit status first
            unit = None
            if unit_id is not None:
                # Get unit directly from dictionary to handle captured/capturing status display
                unit = game_state.units.get(unit_id)

            # Overlay unit/selection/range markers
            # Order matters: Defeated > Selected > Capturing > Normal Unit > Move Range
            if unit and not unit.is_alive:
                display_char = "X" # Defeated
            elif unit and unit.is_captured:
                 # Should not appear on map, but just in case
                 display_char = "?" # Captured (should be off-map)
            elif selected_pos == current_pos:
                display_char = "@" # Selected
            elif unit: # Unit exists, is alive, and not captured
                if unit.is_capturing is not None: # Check if capturing FIRST
                    if unit.faction == Faction.PLAYER:
                        display_char = "C" # Player Capturing
                    elif unit.faction == Faction.ENEMY:
                        display_char = "c" # Enemy Capturing
                    # Add Ally capturing later if needed ('G'?)
                elif unit.faction == Faction.PLAYER:
                    display_char = "P" if not unit.has_acted else "p"
                elif unit.faction == Faction.ENEMY:
                    display_char = "E"
                elif unit.faction == Faction.ALLY:
                    display_char = "A"
            elif current_pos in move_range: # Check move_range only if tile is empty/passable terrain
                 # Show move range only if no unit is present
                 if display_char == terrain_char: # Only overlay if it's just terrain
                    display_char = "*" # Reachable tile for selected unit
            # TODO: Add display for attack range ('+') later

            row_str += f" {display_char} " # Add spacing around character
        row_str += "|" # Right border
        print(row_str)

    # Adjust border length
    print("  +" + "---"*game_state.game_map.width + "+") # Bottom border

    # Display selected unit info
    if selected_unit:
        weapon_name = selected_unit.equipped_weapon.name if selected_unit.equipped_weapon else "None"
        capture_status_str = ""
        if selected_unit.is_capturing is not None:
            # Get captive name directly from dictionary
            captive = game_state.units.get(selected_unit.is_capturing)
            captive_name = captive.name if captive else "Unknown"
            capture_status_str = f" | Capturing: {captive_name}"
        # Added MoveType and Capture Status to selected unit info
        print(f"Selected: {selected_unit.name} ({selected_unit.move_type}) at {selected_unit.position}{capture_status_str} | HP: {selected_unit.hp}/{selected_unit.max_hp} | Mov: {selected_unit.mov} | Weapon: {weapon_name} | Acted: {selected_unit.has_acted}")
    else:
        print("Selected: None")

    print("-" * (len(header))) # Separator
