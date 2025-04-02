# src/game/display.py (Updated)

from typing import Set, Tuple, Optional, Dict # Add Dict
from .models import GameState, Unit, Faction, TerrainType # Import Faction, TerrainType

def render_map(
    game_state: GameState,
    move_range: Optional[Dict[Tuple[int, int], int]] = None, # Changed to Dict
    canto_range: Optional[Dict[Tuple[int, int], int]] = None # NEW: Add canto_range
):
    """Renders the current game map and state to the console."""
    print(f"\n--- Turn {game_state.turn} - {game_state.active_faction} Phase ---")

    selected_unit = game_state.get_selected_unit()
    selected_pos = selected_unit.position if selected_unit else None
    # Default ranges to empty dicts if not provided
    if move_range is None:
        move_range = {}
    if canto_range is None:
        canto_range = {}

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
            # Order matters: Defeated > Selected > Capturing > Fatigued > Normal Unit > Move Range
            is_fatigued = unit and unit.fatigue >= unit.max_hp

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
                elif is_fatigued and unit.faction == Faction.PLAYER: # Check fatigue *after* capturing
                     display_char = "f" # Fatigued Player unit (lowercase 'f')
                elif unit.faction == Faction.PLAYER:
                    display_char = "P" if not unit.has_acted else "p"
                elif unit.faction == Faction.ENEMY:
                    display_char = "E"
                elif unit.faction == Faction.ALLY:
                    display_char = "A"
            # Check Canto range first, then normal move range
            elif current_pos in canto_range:
                 if display_char == terrain_char:
                    display_char = "+" # Canto range tile
            elif current_pos in move_range:
                 if display_char == terrain_char:
                    display_char = "*" # Normal move range tile
            # TODO: Add display for attack range ('x'?) later

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
        # Also add Fatigue display
        fatigue_status = f" | Fatigue: {selected_unit.fatigue}/{selected_unit.max_hp}"
        fatigued_warning = " [FATIGUED]" if selected_unit.fatigue >= selected_unit.max_hp else ""
        print(f"Selected: {selected_unit.name} ({selected_unit.move_type}) at {selected_unit.position}{capture_status_str}{fatigue_status}{fatigued_warning} | HP: {selected_unit.hp}/{selected_unit.max_hp} | Mov: {selected_unit.mov} | Weapon: {weapon_name} | Acted: {selected_unit.has_acted}")
    else:
        print("Selected: None")

    print("-" * (len(header))) # Separator
