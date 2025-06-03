from lexpr.events import EventDefinition
from lexpr.units import Unit
from lexpr.game_state import game
from lexpr.text_engine import text_engine
from lexpr.ui_framework import choice_menu # Assuming a choice_menu is available

class GlobalStealEvent(EventDefinition):
    nid = "Global_Steal_Event"
    name = "Global Steal Event"
    event_trigger = None  # Triggered by StealArtEffect skill component

    def _run(self, unit: Unit, target: Unit, **kwargs):
        """
        Handles the Steal command logic.
        Unit is the thief, target is the enemy.
        """
        thief = unit
        enemy = target

        thief_con = thief.stats.get('CON', 0)
        enemy_con = enemy.stats.get('CON', 0)

        if thief_con < enemy_con:
            game.speak(thief.name, f"My Build ({thief_con}) is too low to steal from {enemy.name} (Build: {enemy_con}).")
            return False # Indicate event failure or no action

        stealable_items = []
        for item in enemy.items:
            item_weight = game.get_item_data(item.nid).weight if game.get_item_data(item.nid) else 0 # Assumes item_data has weight
            if thief_con >= item_weight:
                stealable_items.append(item)

        if not stealable_items:
            game.speak(thief.name, f"{enemy.name} has nothing I can carry.")
            return False

        # Prepare choices for the UI
        # Each choice could be a tuple: (item_nid, display_text)
        item_choices = []
        for item_obj in stealable_items:
            item_data = game.get_item_data(item_obj.nid)
            if item_data:
                display_text = f"{item_data.name} (Wt: {item_data.weight or 0})"
                item_choices.append({'nid': item_obj.nid, 'text': display_text, 'obj': item_obj})

        if not item_choices: # Should be redundant if stealable_items check passed, but good for safety
            game.speak(thief.name, f"Found no items I can steal from {enemy.name}.")
            return False

        # Show item selection menu
        # This part is highly dependent on LT's UI capabilities.
        # Assuming choice_menu.display returns the 'nid' of the chosen item or None
        chosen_item_dict = choice_menu.display("Steal which item?", item_choices, one_column=True)

        if chosen_item_dict and 'obj' in chosen_item_dict:
            selected_item_object = chosen_item_dict['obj']
            
            # Perform the steal
            game.remove_item(enemy, selected_item_object)
            game.add_item(thief, selected_item_object.nid) # Assuming add_item takes nid

            item_data = game.get_item_data(selected_item_object.nid)
            game.speak(thief.name, f"Stole {item_data.name} from {enemy.name}!")
            
            # Consume action if not already handled by combat_art
            # game.set_unit_state(thief, 'done') # Or similar command if needed
            
            return True # Indicate successful event completion
        else:
            game.speak(thief.name, "Decided not to steal anything.")
            return False # Player cancelled or no item chosen