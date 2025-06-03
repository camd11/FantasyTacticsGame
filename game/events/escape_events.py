from lexiongton.engine import (
    skill_system,
    region_system,
    game_state_functions as gsf,
    action
)
from lexiongton.engine.game_state import game
from lexiongton.engine.objects.unit import UnitObject

ESCAPE_REGION_NID = "EscapePoint"
LORD_SKILL_NID = "Lord"
CAPTURED_SKILL_NID = "Captured"

def on_unit_move(event_name: str, unit: UnitObject, new_position: tuple):
    """
    Handles logic when a unit moves, specifically for escape objectives.
    """
    if not unit or unit.team != 'player':
        return

    current_region = region_system.get_region_at(new_position)
    if not current_region or current_region.nid != ESCAPE_REGION_NID:
        return

    is_lord = skill_system.check_skill(unit, LORD_SKILL_NID)

    if is_lord:
        # Lord escapes, end chapter
        action.do(action.RemoveUnit(unit))
        game.alerts.append_event_alert(
            f"{unit.name} has escaped! The chapter ends."
        )
        game.dialog_log.add_message(
            f"{unit.name} has escaped! The chapter ends."
        )

        # Flag remaining player units as captured
        for other_unit_nid in game.units.get_nids_by_team('player'):
            other_unit = game.units.get(other_unit_nid)
            if other_unit and other_unit.nid != unit.nid and other_unit.position: # Still on map
                # Check if unit already escaped or is captured
                already_escaped_or_captured = False
                for skill in other_unit.skills:
                    if skill.nid == CAPTURED_SKILL_NID:
                        already_escaped_or_captured = True
                        break
                if not region_system.get_region_at(other_unit.position) or region_system.get_region_at(other_unit.position).nid != ESCAPE_REGION_NID:
                    if not already_escaped_or_captured:
                        skill_system.assign_skill(other_unit, CAPTURED_SKILL_NID)
                        game.alerts.append_event_alert(
                            f"{other_unit.name} has been captured!"
                        )
                        game.dialog_log.add_message(
                            f"{other_unit.name} has been captured!"
                        )
                        # Optionally remove them from map visually, though prevent_deployment handles future chapters
                        # action.do(action.RemoveUnit(other_unit))


        # End the chapter - replace 'NEXT_CHAPTER_NID' with actual next chapter ID or a game over screen
        game.level_vars['next_level'] = 'NEXT_CHAPTER_NID' # Placeholder
        game.game_vars['_win_game'] = True
        action.do(action.EndPhase()) # Ensure current actions are processed
        action.do(action.WinGame())

    else:
        # Non-lord unit escapes
        action.do(action.RemoveUnit(unit))
        # Unit remains in party, just removed from map
        game.alerts.append_event_alert(f"{unit.name} has escaped!")
        game.dialog_log.add_message(f"{unit.name} has escaped!")
        # No need to add to game.killed_units as they are not dead

# Event subscription
# This assumes your event system can call functions directly.
# If it uses a different mechanism (e.g., event names in a YAML file that map to scripts),
# you'll need to register "on_unit_move" or a similar global event trigger.

# For Lexiongton engine, typically events are hooked up in a central event manager
# or by naming convention if the engine supports auto-discovery based on function names.
# Let's assume a hypothetical direct subscription for now, or that this will be
# called by a global event script that fires on any unit_move.

# If using a global event script in YAML that calls Python functions:
# 1. Create a global event in your events.yaml (or similar)
#    trigger: unit_move
#    script: game.events.escape_events.handle_escape_move
# 2. Rename on_unit_move to handle_escape_move(unit, new_position) or adapt parameters.

# For now, this script defines the functions. Hooking it into the game's event loop
# will depend on the specific engine's event handling mechanism.
# A common pattern is to have a main event script that imports and calls functions from others.

# Example of how it might be registered if the engine has a direct event bus:
# if hasattr(game, 'events') and hasattr(game.events, 'subscribe'):
#     game.events.subscribe('unit_move', on_unit_move)

# If the engine uses event names in level data (e.g. level_events.yaml)
# you might have an entry like:
# - name: CheckEscapeOnMove
#   trigger: unit_move
#   event_id: Global_Escape_Check
# And then Global_Escape_Check would be a script call to this python function.
# For simplicity, we'll assume this function `on_unit_move` will be correctly
# invoked by the engine whenever a unit completes a move.