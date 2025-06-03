from lex_luthor import engine
from lex_luthor.engine.game_state import game

# Assuming constants are loaded and accessible, e.g., game.constants.LEADERSHIP_HIT_BONUS_PER_STAR
# For now, hardcoding for clarity, will need to integrate with actual constant loading.
LEADERSHIP_HIT_BONUS_PER_STAR = 3  # Placeholder, replace with game.constants.LEADERSHIP_HIT_BONUS_PER_STAR
LEADERSHIP_AVOID_BONUS_PER_STAR = 3 # Placeholder, replace with game.constants.LEADERSHIP_AVOID_BONUS_PER_STAR

# This dictionary will store the NIDs of the temporary status effects applied for leadership.
# We need to manage these to remove them at the end of the turn or when bonuses recalculate.
# Key: unit.nid, Value: list of status_nids applied by leadership bonus
# This is a simplified approach. A more robust system might use tagged statuses.
_applied_leadership_statuses = {}

def get_stars_from_skill_nid(skill_nid: str, prefix: str) -> int:
    """Helper to extract star count from skill NID, e.g., 'LeadershipStar_3' -> 3"""
    if skill_nid.startswith(prefix) and skill_nid.split('_')[-1].isdigit():
        return int(skill_nid.split('_')[-1])
    return 0

def apply_leadership_bonuses():
    """
    Calculates and applies leadership star bonuses to all units at the start of a phase.
    This function should be triggered by a game event (e.g., on_phase_start).
    """
    global _applied_leadership_statuses
    # print("Applying leadership bonuses...") # For debugging

    # 1. Clear any previously applied leadership bonus statuses
    for unit_nid, status_nids in _applied_leadership_statuses.items():
        unit = game.get_unit(unit_nid)
        if unit:
            for status_nid in status_nids:
                # Assuming a function like game.remove_status(unit, status_nid) exists
                # This part is highly dependent on the engine's status effect API
                # For now, we'll just clear our tracking
                pass # Placeholder for actual status removal
    _applied_leadership_statuses.clear()

    team_leadership_stars = {'player': 0, 'enemy': 0, 'other': 0}

    # 2. Calculate total leadership stars for each team
    for unit in game.units:
        if unit.position: # Check if unit is deployed
            unit_stars = 0
            for skill_obj in unit.skills:
                stars = get_stars_from_skill_nid(skill_obj.nid, "LeadershipStar_")
                if stars > 0:
                    unit_stars += stars
            
            if unit_stars > 0: # Only count units that are leaders themselves
                if unit.team in team_leadership_stars:
                    team_leadership_stars[unit.team] += unit_stars
                # else: # Handle neutral or other unclassified teams if necessary
                #     print(f"Warning: Unit {unit.nid} has unclassified team {unit.team} for leadership.")


    # 3. Apply bonuses to all units on each team
    for unit in game.units:
        if unit.position and unit.team in team_leadership_stars:
            total_stars_for_team = team_leadership_stars[unit.team]
            if total_stars_for_team > 0:
                hit_bonus = total_stars_for_team * LEADERSHIP_HIT_BONUS_PER_STAR
                avoid_bonus = total_stars_for_team * LEADERSHIP_AVOID_BONUS_PER_STAR

                # This is where the engine's API for applying temporary stat boosts or status effects is crucial.
                # Option A: Apply a temporary status effect.
                # This requires defining status effects for each possible bonus combination or a dynamic status.
                # Example:
                # status_nid_hit = f"leadership_hit_{hit_bonus}"
                # status_nid_avoid = f"leadership_avoid_{avoid_bonus}"
                # game.add_status(unit, status_nid_hit, duration=1) # Duration 1 turn/phase
                # game.add_status(unit, status_nid_avoid, duration=1)
                # if unit.nid not in _applied_leadership_statuses:
                #     _applied_leadership_statuses[unit.nid] = []
                # _applied_leadership_statuses[unit.nid].extend([status_nid_hit, status_nid_avoid])

                # Option B: Directly modify stats if the engine supports temporary turn-based modifiers.
                # This is simpler if available but might be harder to track/remove.
                # Example:
                # unit.stats.hit += hit_bonus # This is a conceptual example
                # unit.stats.avoid += avoid_bonus # Assumes direct mutable access or a method
                # game.register_temporary_stat_change(unit, 'hit', hit_bonus, 'leadership_bonus')
                # game.register_temporary_stat_change(unit, 'avoid', avoid_bonus, 'leadership_bonus')
                
                # For now, let's assume a conceptual direct modification for the purpose of this script's logic.
                # The actual implementation will depend on LT's capabilities.
                # We'll print the intended effect for now.
                # print(f"Unit {unit.nid} ({unit.team}) gets +{hit_bonus} Hit, +{avoid_bonus} Avoid from {total_stars_for_team} leadership stars.")

                # To make this testable with existing skill components, we'll try to add a skill
                # that grants these stats. This is a workaround and ideally, the engine
                # would have a more direct way to grant temporary, non-skill-based stat boosts.
                # We'll need to create skills like "LeadershipBonus_Hit_3_Avoid_3" on the fly or have them predefined.
                # This approach is complex due to the dynamic nature of bonuses.

                # A more practical approach with current LT skill system might be to have a single
                # "LeadershipAuraEffect" status that reads a value from the unit (e.g. unit.aura_bonus_hit)
                # which this script would set.
                # For now, this script calculates the values. The application needs engine specifics.
                # Let's assume a function `game.set_unit_turn_stat_bonus(unit, stat_name, value, source_tag)`
                if hasattr(game, 'set_unit_turn_stat_bonus'):
                    game.set_unit_turn_stat_bonus(unit, 'hit', hit_bonus, 'leadership_stars')
                    game.set_unit_turn_stat_bonus(unit, 'avo', avoid_bonus, 'leadership_stars') # 'avo' is common for avoid
                    # Track that a bonus was applied (even if conceptual)
                    if unit.nid not in _applied_leadership_statuses:
                        _applied_leadership_statuses[unit.nid] = ["leadership_active"] # Dummy tracker
                else:
                    # Fallback: If direct modification isn't available, this mechanic needs a different approach
                    # (e.g., custom status effects created on the fly or a set of predefined ones).
                    # This is a significant dependency on the engine's features.
                    # print(f"Engine lacks 'set_unit_turn_stat_bonus'. Leadership bonus for {unit.nid} not applied directly.")
                    pass


def clear_leadership_bonuses_on_turn_end():
    """
    Clears any temporary stat changes made by leadership bonuses.
    This should be triggered by a game event (e.g., on_turn_end or before next on_phase_start).
    """
    global _applied_leadership_statuses
    # print("Clearing leadership bonuses...") # For debugging

    for unit in game.units:
        if unit.position:
            # Assuming a function like game.clear_unit_turn_stat_bonus(unit, source_tag)
            if hasattr(game, 'clear_unit_turn_stat_bonus'):
                game.clear_unit_turn_stat_bonus(unit, 'hit', 'leadership_stars')
                game.clear_unit_turn_stat_bonus(unit, 'avo', 'leadership_stars')
            # else:
            #     print(f"Engine lacks 'clear_unit_turn_stat_bonus'. Leadership bonus for {unit.nid} not cleared directly.")
            pass
    
    _applied_leadership_statuses.clear()


# How to register these events depends on the engine's event system.
# Example (conceptual):
# engine.register_event_hook('on_phase_start', apply_leadership_bonuses)
# engine.register_event_hook('on_turn_end', clear_leadership_bonuses_on_turn_end)

# Or, if these are to be called from a master event script:
# game.events.subscribe('phase_start', apply_leadership_bonuses, 'leadership_bonus_calc')
# game.events.subscribe('turn_end', clear_leadership_bonuses_on_turn_end, 'leadership_bonus_clear')

# For Lex Talionis, event subscription is typically done in a top-level event file or through specific event components.
# This script provides the functions; their integration into the event flow is a separate step.

# It's also important that game.constants are properly loaded and accessible.
# If LEADERSHIP_HIT_BONUS_PER_STAR and LEADERSHIP_AVOID_BONUS_PER_STAR are in constants.json,
# they should be accessible via something like:
# game.current_constants.get('LEADERSHIP_HIT_BONUS_PER_STAR', 3)
# game.current_constants.get('LEADERSHIP_AVOID_BONUS_PER_STAR', 3)
# The script will need adjustment based on how constants are accessed.
# For now, using the placeholder values defined at the top of this script.

# Final check: Ensure game.units, unit.position, unit.skills, unit.team, skill_obj.nid are valid attributes/methods.
# Ensure game.get_unit(nid) is a valid way to retrieve a unit.
# The concept of "deployed" (unit.position) is crucial.