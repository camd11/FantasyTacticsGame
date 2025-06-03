import random
from lex_luthor import engine
from lex_luthor.engine.game_state import game
from lex_luthor.engine.combat import combat_calcs # For potential RNG access if not global

# Assuming constants are loaded and accessible.
# MOVEMENT_STAR_REFRESH_CHANCE_PER_STAR = game.constants.MOVEMENT_STAR_REFRESH_CHANCE_PER_STAR
# For now, hardcoding for clarity, will need to integrate with actual constant loading.
MOVEMENT_STAR_REFRESH_CHANCE_PER_STAR = 0.05 # Placeholder

# Custom data key to track refresh status
REFRESH_TRACK_KEY = 'movement_star_refreshed_this_turn'

def get_stars_from_skill_nid(skill_nid: str, prefix: str) -> int:
    """Helper to extract star count from skill NID, e.g., 'MovementStar_3' -> 3"""
    if skill_nid.startswith(prefix) and skill_nid.split('_')[-1].isdigit():
        return int(skill_nid.split('_')[-1])
    return 0

def handle_movement_star_refresh(event):
    """
    Handles the logic for a unit attempting to refresh their action via Movement Stars
    after performing a "Wait" action.
    Triggered by the 'event_after_wait_action' component on MovementStar_X skills.
    """
    acting_unit = event.unit # Assuming the event object has a 'unit' attribute for the actor

    if not acting_unit:
        # print("Movement Star Refresh: No acting unit found in event.") # Debug
        return

    # 1. Check if already refreshed this turn
    if getattr(acting_unit.custom_data, REFRESH_TRACK_KEY, False):
        # print(f"Movement Star Refresh: Unit {acting_unit.nid} already refreshed this turn.") # Debug
        return

    # 2. Calculate total movement stars for the unit
    total_movement_stars = 0
    for skill_obj in acting_unit.skills:
        stars = get_stars_from_skill_nid(skill_obj.nid, "MovementStar_")
        if stars > 0:
            total_movement_stars += stars
    
    if total_movement_stars == 0:
        # print(f"Movement Star Refresh: Unit {acting_unit.nid} has no movement stars.") # Debug
        return

    # 3. Retrieve constant (use placeholder for now)
    # refresh_chance_per_star = game.current_constants.get('MOVEMENT_STAR_REFRESH_CHANCE_PER_STAR', 0.05)
    refresh_chance_per_star = MOVEMENT_STAR_REFRESH_CHANCE_PER_STAR


    # 4. Calculate refresh chance
    refresh_chance = total_movement_stars * refresh_chance_per_star

    # 5. Perform random number check
    # Assuming random.random() gives a float between 0.0 and 1.0
    # The engine might have its own RNG function, e.g., game.rng.random() or similar
    roll = random.random() 
    # print(f"Movement Star Refresh: Unit {acting_unit.nid}, Stars: {total_movement_stars}, Chance: {refresh_chance:.2f}, Roll: {roll:.2f}") # Debug

    if roll < refresh_chance:
        # 6. If successful, refresh action and set flag
        # The method to refresh a unit is engine-specific.
        # Examples: acting_unit.has_acted = False; acting_unit.has_moved = False;
        # Or a dedicated function: game.actions.refresh_unit(acting_unit)
        
        refreshed = False
        if hasattr(acting_unit, 'has_acted'): # Common in LT
            acting_unit.has_acted = False
            refreshed = True
        if hasattr(acting_unit, 'has_moved'): # Common in LT
            acting_unit.has_moved = False # Also reset movement if applicable
            refreshed = True
        
        # If the engine has a more specific refresh function, use that.
        # e.g., if game.engine.action_system.refresh_action(acting_unit):
        
        if refreshed:
            # print(f"Movement Star Refresh: Unit {acting_unit.nid} REFRESHED!") # Debug
            if not hasattr(acting_unit, 'custom_data') or acting_unit.custom_data is None:
                acting_unit.custom_data = {} # Ensure custom_data exists
            acting_unit.custom_data[REFRESH_TRACK_KEY] = True

            # Optional: Display a message or animation
            # game.alerts.add_alert(f"{acting_unit.name} feels invigorated!", unit=acting_unit)
            # game.fx.play_effect_on_unit(acting_unit, 'refresh_sparkle_effect') # Conceptual
            if hasattr(game, 'speak'):
                 game.speak(None, "{unit} feels invigorated and can act again!", unit=acting_unit, position=acting_unit.position)
        # else:
            # print(f"Movement Star Refresh: Unit {acting_unit.nid} refresh attempt successful, but no refresh mechanism found.") # Debug
            pass
    # else:
        # print(f"Movement Star Refresh: Unit {acting_unit.nid} failed refresh check.") # Debug
        pass


def reset_movement_star_refresh_flags():
    """
    Resets the 'movement_star_refreshed_this_turn' flag for all units.
    Should be called at the start of a new global turn (e.g., Player Phase start and Enemy Phase start).
    """
    # print("Resetting movement star refresh flags for all units...") # Debug
    for unit in game.units:
        if hasattr(unit, 'custom_data') and unit.custom_data is not None:
            if REFRESH_TRACK_KEY in unit.custom_data:
                unit.custom_data[REFRESH_TRACK_KEY] = False

# Registration of these events:
# The 'handle_movement_star_refresh' function is intended to be called by an event NID
# 'Global_Movement_Star_Refresh_Event' which is set in the skill component.
# The engine needs to map this event NID to this Python function.

# The 'reset_movement_star_refresh_flags' needs to be hooked into phase start events.
# Example (conceptual):
# engine.register_event_hook('on_phase_start', reset_movement_star_refresh_flags)
# game.events.subscribe('phase_start', reset_movement_star_refresh_flags, 'reset_mov_star_flags')

# This script provides the functions. Their integration into the event flow is a separate step
# and depends on how the main event system in LT is structured (e.g., a central event_manager.py
# or direct calls from engine hooks).