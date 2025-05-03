"""
Map Interaction System Module

This module handles unit interactions with interactive map elements, specifically Doors and Chests.
It defines how these objects are represented, the conditions for interaction, the effects of
interaction, and integration with other game systems (Units, Items, AI, Actions).
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass

# Import necessary modules/classes
from src.core_engine.game_state import GameStateManager
from src.core_engine.data_provider import DataProvider


@dataclass
class InteractionResult:
    """Result of an interaction attempt."""
    success: bool
    message: str = ""
    consumed_key_id: Optional[str] = None
    gained_item_id: Optional[str] = None
    gained_gold: Optional[int] = None


class MapInteractionSystem:
    """
    Manages interactions with map objects like doors and chests.
    """
    
    def __init__(self):
        """Initialize the MapInteractionSystem."""
        self.gameStateManager = None
        self.dataProvider = None
        self.mapSystem = None
        self.inventorySystem = None
        self.unitSystem = None
        self.skillSystem = None
        self.actionSystem = None
    
    def initialize(self, gameStateManager_instance: GameStateManager, 
                  dataProvider_instance: DataProvider,
                  mapSystem_instance=None,
                  inventorySystem_instance=None,
                  unitSystem_instance=None,
                  skillSystem_instance=None,
                  actionSystem_instance=None) -> None:
        """
        Initialize the MapInteractionSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
            mapSystem_instance: Instance of the MapSystem
            inventorySystem_instance: Instance of the InventorySystem
            unitSystem_instance: Instance of the UnitSystem
            skillSystem_instance: Instance of the SkillSystem
            actionSystem_instance: Instance of the ActionSystem
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        self.mapSystem = mapSystem_instance
        self.inventorySystem = inventorySystem_instance
        self.unitSystem = unitSystem_instance
        self.skillSystem = skillSystem_instance
        self.actionSystem = actionSystem_instance
        logging.info("MapInteractionSystem initialized.")
    
    # --- Core Interaction Logic ---
    
    def can_interact_with_object(self, unit_id: str, object_id: str) -> bool:
        """
        Determines if a unit can potentially interact with a door/chest.
        
        Args:
            unit_id: ID of the unit
            object_id: ID of the map object
            
        Returns:
            True if the unit can interact with the object, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        map_object = self.gameStateManager.get_map_object(object_id)
        
        if map_object is None or unit is None:
            logging.debug(f"Cannot interact: Unit {unit_id} or object {object_id} not found")
            return False
        
        # 1. Check Adjacency
        if not self.is_adjacent(unit.position, map_object.position):
            logging.debug(f"Cannot interact: Unit {unit_id} is not adjacent to object {object_id}")
            return False
        
        # 2. Check Object State
        if map_object.state in ["Opened", "Empty"]:
            logging.debug(f"Cannot interact: Object {object_id} is already {map_object.state}")
            return False
        
        # 3. Check if interaction is possible via key or skill
        has_key = self.has_required_key(unit, map_object)
        has_skill = self.has_required_skill(unit, map_object)
        
        if not (has_key or has_skill):
            logging.debug(f"Cannot interact: Unit {unit_id} has neither required key nor skill for {object_id}")
            return False
        
        return True
    
    def has_required_key(self, unit, map_object) -> bool:
        """
        Checks if the unit possesses the necessary key in their inventory.
        
        Args:
            unit: Unit object
            map_object: Map object (door or chest)
            
        Returns:
            True if the unit has the required key, False otherwise
        """
        required_key_type = None
        if map_object.object_type == "Door":
            required_key_type = "DoorKey"
        elif map_object.object_type == "Chest":
            required_key_type = "ChestKey"
        else:
            return False  # Unknown object type
        
        for item_id in unit.inventory:
            item = self.dataProvider.get_item_data(item_id)
            if item is not None and item.type == "Key":
                if item.key_type == required_key_type or item.key_type == "MasterKey":
                    if item.uses > 0:
                        return True  # Found a valid key with uses remaining
        
        return False  # No suitable key found
    
    def has_required_skill(self, unit, map_object) -> bool:
        """
        Checks if the unit possesses the necessary skill (e.g., Locktouch).
        
        Args:
            unit: Unit object
            map_object: Map object (door or chest)
            
        Returns:
            True if the unit has the required skill, False otherwise
        """
        if map_object.object_type in ["Door", "Chest"]:
            for skill_id in unit.skills:
                skill = self.dataProvider.get_skill_data(skill_id)
                if skill is not None and skill.name == "Locktouch":
                    return True
        
        return False
    
    def is_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """
        Checks if two positions are adjacent.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            True if the positions are adjacent, False otherwise
        """
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Check Manhattan distance
        return abs(x1 - x2) + abs(y1 - y2) == 1
    
    def attempt_interaction(self, unit_id: str, object_id: str) -> InteractionResult:
        """
        Executes the interaction if possible, consuming keys/actions and updating state.
        
        Args:
            unit_id: ID of the unit
            object_id: ID of the map object
            
        Returns:
            InteractionResult object with the result of the interaction
        """
        result = InteractionResult(success=False)
        unit = self.gameStateManager.get_unit(unit_id)
        map_object = self.gameStateManager.get_map_object(object_id)
        
        if not self.can_interact_with_object(unit_id, object_id):
            result.message = "Cannot interact with object."
            return result  # Basic checks failed
        
        # Determine interaction method: Prioritize Skill (Locktouch) over Key
        used_skill = False
        consumed_key_id = None
        
        if self.has_required_skill(unit, map_object):
            used_skill = True
        elif self.has_required_key(unit, map_object):
            # Find the specific key to consume
            key_to_consume = self.find_key_in_inventory(unit, map_object)
            if key_to_consume is not None:
                self.inventorySystem.consume_item_use(key_to_consume.item_id)
                consumed_key_id = key_to_consume.item_id
            else:
                result.message = "Error: Key check passed but no key found to consume."
                return result  # Should not happen if can_interact logic is correct
        else:
            result.message = "No key or skill available."
            return result
        
        # Perform the action based on object type
        if map_object.object_type == "Door":
            result = self.open_door(unit, map_object, used_skill)
        elif map_object.object_type == "Chest":
            result = self.open_chest(unit, map_object, used_skill)
        
        result.consumed_key_id = consumed_key_id
        if result.success:
            # Mark unit action as complete for the turn
            self.actionSystem.mark_unit_action_complete(unit_id)
        
        return result
    
    def find_key_in_inventory(self, unit, map_object):
        """
        Find the first valid key in a unit's inventory for a specific map object.
        
        Args:
            unit: Unit object
            map_object: Map object (door or chest)
            
        Returns:
            Key item or None if no valid key is found
        """
        required_key_type = "DoorKey" if map_object.object_type == "Door" else "ChestKey"
        
        for item_id in unit.inventory:
            item = self.dataProvider.get_item_data(item_id)
            if item is not None and item.type == "Key" and item.uses > 0:
                if item.key_type == required_key_type or item.key_type == "MasterKey":
                    return item
        
        return None
    
    def open_door(self, unit, map_object, used_skill) -> InteractionResult:
        """
        Handles the specific logic for opening a door.
        
        Args:
            unit: Unit object
            map_object: Door object
            used_skill: Whether the Locktouch skill was used
            
        Returns:
            InteractionResult object with the result of the interaction
        """
        result = InteractionResult(success=True)
        
        # Update Door State
        map_object.state = "Opened"
        
        # Update Map Terrain
        self.mapSystem.update_tile_terrain(map_object.position, "OpenDoor")
        self.mapSystem.update_map_passability(map_object.position)
        
        # Handle linked doors (if applicable)
        if hasattr(map_object, 'linked_door_id') and map_object.linked_door_id is not None:
            linked_door = self.gameStateManager.get_map_object(map_object.linked_door_id)
            if linked_door is not None and linked_door.state == "Locked":
                linked_door.state = "Opened"
                self.mapSystem.update_tile_terrain(linked_door.position, "OpenDoor")
                self.mapSystem.update_map_passability(linked_door.position)
        
        result.message = "Door opened."
        if used_skill:
            result.message += " (Used Locktouch)"
        
        return result
    
    def open_chest(self, unit, map_object, used_skill) -> InteractionResult:
        """
        Handles the specific logic for opening a chest.
        
        Args:
            unit: Unit object
            map_object: Chest object
            used_skill: Whether the Locktouch skill was used
            
        Returns:
            InteractionResult object with the result of the interaction
        """
        result = InteractionResult(success=True)
        
        # Check if chest is already empty (should be caught earlier, but double-check)
        if map_object.state == "Empty":
            result.success = False
            result.message = "Chest is already empty."
            return result
        
        # Grant Content to Unit
        if map_object.content_type == "Item":
            item_id = map_object.content_value
            if self.inventorySystem.can_unit_carry_item(unit):
                self.inventorySystem.add_item_to_inventory(unit.unit_id, item_id)
                result.gained_item_id = item_id
                item_name = self.dataProvider.get_item_data(item_id).name
                result.message = f"Obtained {item_name}."
            else:
                result.success = False
                result.message = "Inventory is full."
                return result
        elif map_object.content_type == "Gold":
            gold_amount = map_object.content_value
            self.inventorySystem.add_gold_to_party(gold_amount)
            result.gained_gold = gold_amount
            result.message = f"Obtained {gold_amount} Gold."
        else:
            result.message = "Chest is empty."
        
        # Update Chest State
        map_object.state = "Empty"
        map_object.content_type = None
        map_object.content_value = None
        
        if used_skill:
            result.message += " (Used Locktouch)"
        
        return result