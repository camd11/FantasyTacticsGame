from lexpr.events import EventDefinition
from lexpr.units import Unit
from lexpr.game_state import game
from lexpr.text_engine import text_engine

class GlobalGainFatigueEvent(EventDefinition):
    nid = "Global_Gain_Fatigue_Event"
    name = "Global Gain Fatigue Event"
    event_trigger = None # This will be triggered by the skill component

    def _run(self, unit: Unit, **kwargs):
        """
        Increases the unit's fatigue by FATIGUE_PER_ACTION.
        """
        fatigue_per_action = game.game_vars.get('FATIGUE_PER_ACTION', 1) # Default to 1 if not found
        
        if hasattr(unit, 'fatigue'):
            unit.fatigue += fatigue_per_action
            # game.alerts.append(f"{unit.name} gained {fatigue_per_action} fatigue. Now at {unit.fatigue}.")
            # game.speak(None, f"{unit.name} gained {fatigue_per_action} fatigue.", position='center') # Optional: for debugging
        else:
            # This case should ideally not happen if units.json is updated correctly
            # game.alerts.append(f"Error: {unit.name} has no fatigue attribute.")
            # game.speak(None, f"Error: {unit.name} has no fatigue attribute.", position='center')
            # Initialize fatigue if missing, though this indicates a setup issue
            unit.fatigue = fatigue_per_action
            # game.alerts.append(f"{unit.name} fatigue initialized and set to {unit.fatigue}.")

# To make this event discoverable by the engine, it needs to be registered.
# This typically happens in an __init__.py in the events folder or a main plugin file.
# For now, this defines the event. Registration might be a separate step or handled by LT's discovery.

# Placeholder for Chapter End Fatigue Processing Event
class ChapterEndFatigueProcessing(EventDefinition):
    nid = "Chapter_End_Fatigue_Processing"
    name = "Chapter End Fatigue Processing"
    event_trigger = 'level_end' # Or 'chapter_end', check LT docs for correct hook

    def _run(self, **kwargs):
        """
        Checks all player units. If fatigue >= MaxHP, applies 'Fatigued_Out' status.
        Clears 'Fatigued_Out' if fatigue < MaxHP.
        """
        fatigued_out_nid = "Fatigued_Out"
        
        for unit_nid in game.get_all_units_in_party():
            unit = game.get_unit(unit_nid)
            if not unit or not unit.is_player_team(): # Ensure unit exists and is a player unit
                continue

            if hasattr(unit, 'fatigue') and hasattr(unit.stats, 'HP'):
                max_hp = unit.stats.get('HP', 1) # Get MaxHP, default to 1 to avoid division by zero if error
                current_fatigue = unit.fatigue

                has_fatigued_out_status = any(skill.nid == fatigued_out_nid for skill in unit.skills)

                if current_fatigue >= max_hp:
                    if not has_fatigued_out_status:
                        game.add_skill(unit, fatigued_out_nid)
                        # game.alerts.append(f"{unit.name} is Fatigued Out!")
                        # game.speak(None, f"{unit.name} is now Fatigued Out!", position='center')
                else:
                    if has_fatigued_out_status:
                        game.remove_skill(unit, fatigued_out_nid)
                        # game.alerts.append(f"{unit.name} is no longer Fatigued Out.")
                        # game.speak(None, f"{unit.name} recovered from fatigue.", position='center')
            else:
                # Log error if unit is missing fatigue or HP stat
                # game.alerts.append(f"Error processing fatigue for {unit.name}: Missing fatigue or HP stat.")
                pass
        return True # Indicate successful event completion

class UseStaminaDrinkEvent(EventDefinition):
    nid = "Use_Stamina_Drink_Event"
    name = "Use Stamina Drink Event"
    event_trigger = None # Triggered by item component

    def _run(self, unit: Unit, target_unit: Unit, item, **kwargs):
        """
        Sets the target unit's fatigue to 0.
        Also clears the "Fatigued_Out" status if present.
        """
        if hasattr(target_unit, 'fatigue'):
            target_unit.fatigue = 0
            # game.alerts.append(f"{target_unit.name}'s fatigue reset to 0.")
            # game.speak(None, f"{target_unit.name}'s fatigue was reset.", position='center')

            # Also check and remove "Fatigued_Out" status if it exists
            fatigued_out_nid = "Fatigued_Out"
            has_fatigued_out_status = any(skill.nid == fatigued_out_nid for skill in target_unit.skills)
            if has_fatigued_out_status:
                game.remove_skill(target_unit, fatigued_out_nid)
                # game.alerts.append(f"{target_unit.name} is no longer Fatigued Out.")
        else:
            # game.alerts.append(f"Error: {target_unit.name} has no fatigue attribute.")
            # game.speak(None, f"Error: {target_unit.name} has no fatigue attribute.", position='center')
            pass
        return True # Indicate successful event completion