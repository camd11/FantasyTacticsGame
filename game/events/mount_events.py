from lexpr.events import EventDefinition
from lexpr.units import Unit
from lexpr.game_state import game
from lexpr.text_engine import text_engine

class GlobalDismountEvent(EventDefinition):
    nid = "Global_Dismount_Event"
    name = "Global Dismount Event"
    event_trigger = None  # Triggered by DismountArtEffect

    def _run(self, unit: Unit, **kwargs):
        """
        Handles dismounting a unit.
        Changes the unit's class to their dismounted equivalent.
        """
        current_class_nid = unit.klass
        class_data = game.get_class_data(current_class_nid)

        dismounted_class_nid = None
        if class_data and class_data.fields:
            for field in class_data.fields:
                if field.startswith("dismount_pair:"):
                    # This assumes the original mounted class has a field like "dismount_pair:DismountedClassNid"
                    # For this event, we need to find the dismounted class based on the current mounted class.
                    # The dismounted class should have a field like "dismount_pair:MountedClassNid"
                    # Let's adjust the logic: the dismounted class's "dismount_pair" points to the MOUNTED class.
                    # So, we need to iterate all classes to find the one that pairs with the current class.
                    pass # This logic is better handled by finding the class that has unit.klass in ITS dismount_pair

        # Search for the dismounted class nid
        # A bit inefficient, but class list is not expected to be huge
        all_classes = game.get_all_class_data()
        for c_nid, c_data in all_classes.items():
            if c_data.fields:
                for field in c_data.fields:
                    if field == f"dismount_pair:{current_class_nid}" and "Dismounted" in c_nid: # Heuristic
                        dismounted_class_nid = c_nid
                        break
                if dismounted_class_nid:
                    break
        
        if dismounted_class_nid and game.get_class_data(dismounted_class_nid):
            game.change_class(unit, dismounted_class_nid)
            game.speak(unit.name, f"Dismounted. Now a {game.get_class_data(dismounted_class_nid).name}.")
            # Consume action if not already handled by combat_art
            # game.set_unit_state(unit, 'done')
            return True
        else:
            game.speak(unit.name, "Cannot dismount (no dismounted class found).")
            return False

class GlobalMountEvent(EventDefinition):
    nid = "Global_Mount_Event"
    name = "Global Mount Event"
    event_trigger = None  # Triggered by MountArtEffect

    def _run(self, unit: Unit, **kwargs):
        """
        Handles mounting a unit.
        Changes the unit's class back to their mounted equivalent.
        """
        current_class_nid = unit.klass
        # The current class is the dismounted one. Its "dismount_pair" field stores the NID of the mounted class.
        class_data = game.get_class_data(current_class_nid)
        mounted_class_nid = None

        if class_data and class_data.fields:
            for field in class_data.fields:
                if field.startswith("dismount_pair:"):
                    mounted_class_nid = field.split(":")[1]
                    break
        
        if mounted_class_nid and game.get_class_data(mounted_class_nid):
            game.change_class(unit, mounted_class_nid)
            game.speak(unit.name, f"Mounted. Now a {game.get_class_data(mounted_class_nid).name}.")
            # Consume action
            # game.set_unit_state(unit, 'done')
            return True
        else:
            game.speak(unit.name, "Cannot mount (no original mounted class found).")
            return False

class IndoorMapAutoDismount(EventDefinition):
    nid = "Indoor_Map_Auto_Dismount"
    name = "Indoor Map Auto Dismount"
    event_trigger = 'level_start' # Trigger at the start of a level

    def _run(self, **kwargs):
        """
        Checks if the map is "indoor". If so, dismounts all mounted player and enemy units.
        """
        # How to check if map is indoor? Assume a map property.
        # e.g., game.map.properties.get('terrain_type') == 'indoor'
        # Or a custom property like game.map.properties.get('is_indoor', False)
        if game.map_registry.get_current_map_data().properties.get('is_indoor', False):
            game.speak(None, "This is an indoor map. All mounted units will dismount.")
            
            all_units_on_map = game.get_all_units_on_map()
            for unit_nid in all_units_on_map:
                unit_obj = game.get_unit(unit_nid)
                if not unit_obj:
                    continue

                current_class_nid = unit_obj.klass
                class_data = game.get_class_data(current_class_nid)
                
                # Check if the unit is currently mounted.
                # A simple check could be if their movement_group is 'Mounted' or 'Flying'
                # Or if their class NID does not contain "Dismounted"
                is_mounted_type = class_data.movement_group in ['Mounted', 'Flying'] if class_data else False
                
                if is_mounted_type:
                    dismounted_class_nid_target = None
                    all_classes_data = game.get_all_class_data()
                    for c_nid_search, c_data_search in all_classes_data.items():
                        if c_data_search.fields:
                            for field in c_data_search.fields:
                                if field == f"dismount_pair:{current_class_nid}":
                                    dismounted_class_nid_target = c_nid_search
                                    break
                            if dismounted_class_nid_target:
                                break
                    
                    if dismounted_class_nid_target and game.get_class_data(dismounted_class_nid_target):
                        game.change_class(unit_obj, dismounted_class_nid_target)
                        # game.alerts.append(f"{unit_obj.name} automatically dismounted to {game.get_class_data(dismounted_class_nid_target).name}.")
                    # else:
                        # game.alerts.append(f"Could not find dismounted class for {unit_obj.name} ({current_class_nid}).")
            return True
        return False # Not an indoor map, or no action taken