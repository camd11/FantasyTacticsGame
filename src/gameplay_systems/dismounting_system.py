"""
Dismounting System Module

This module is responsible for handling the mounting and dismounting mechanics for units
in the game. It allows mounted units to switch between mounted and dismounted states,
affecting their stats, movement, weapon usability, and interactions with terrain.
"""

from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of a command execution."""
    success: bool
    message: str = ""


class DismountingSystem:
    """
    System for handling unit mounting and dismounting mechanics.
    
    This system allows mounted units to dismount and dismounted units to mount,
    affecting their stats, movement type, and weapon usability.
    """

    def initialize(self, game_state_manager, data_provider, unit_system, map_system):
        """Initialize the DismountingSystem with required dependencies."""
        self.game_state_manager = game_state_manager
        self.data_provider = data_provider
        self.unit_system = unit_system
        self.map_system = map_system

    def can_dismount(self, unit_id: str) -> bool:
        """
        Check if a unit is eligible to dismount.
        
        Args:
            unit_id: The ID of the unit to check
            
        Returns:
            bool: True if the unit can dismount, False otherwise
        """
        unit = self.unit_system.get_unit(unit_id)
        if not unit or not unit.is_mounted:
            return False
        
        mounted_class = self.data_provider.get_class(unit.mounted_class_id)
        if not mounted_class.can_mount:
            return False
        
        # Check if on valid terrain for dismounting
        current_tile = self.map_system.get_tile(unit.position)
        if self.map_system.is_tile_indoors(current_tile):
            return False  # Cannot use command if already forced dismount
        
        return True

    def can_mount(self, unit_id: str) -> bool:
        """
        Check if a unit is eligible to mount.
        
        Args:
            unit_id: The ID of the unit to check
            
        Returns:
            bool: True if the unit can mount, False otherwise
        """
        unit = self.unit_system.get_unit(unit_id)
        if not unit or unit.is_mounted:
            return False
        
        # Check if the unit was originally a mounted class
        original_class = self.data_provider.get_class(unit.mounted_class_id)
        if not original_class or not original_class.can_mount:
            return False
        
        # Check if on valid terrain for mounting (outdoors)
        current_tile = self.map_system.get_tile(unit.position)
        if self.map_system.is_tile_indoors(current_tile):
            return False
        
        return True

    def execute_dismount(self, unit_id: str) -> CommandResult:
        """
        Execute the dismount command for a unit.
        
        Args:
            unit_id: The ID of the unit to dismount
            
        Returns:
            CommandResult: Result of the command execution
        """
        if not self.can_dismount(unit_id):
            return CommandResult(False, "Unit cannot dismount")
        
        unit = self.unit_system.get_unit(unit_id)
        mounted_class = self.data_provider.get_class(unit.mounted_class_id)
        dismounted_class = self.data_provider.get_class(mounted_class.dismounted_equivalent_id)
        
        # 1. Update State Flag
        unit.is_mounted = False
        
        # 2. Apply Stat Changes
        if mounted_class.dismount_stat_modifiers:
            for stat, change in mounted_class.dismount_stat_modifiers.items():
                unit.current_stats[stat] += change
        
        # Always set MOV directly regardless of modifiers
        unit.current_stats["MOV"] = dismounted_class.mov
        
        # 3. Update Movement Type
        unit.current_movement_type = dismounted_class.movement_type
        
        # 4. Handle Weapon Restrictions
        self.handle_weapon_restriction(unit, dismounted_class.usable_weapon_types_dismounted)
        
        # 5. Consume Action
        self.unit_system.set_unit_action_taken(unit_id)
        
        # 6. Update Visuals
        self.game_state_manager.notify_visual_update(unit_id, "dismounted")
        
        return CommandResult(True)

    def execute_mount(self, unit_id: str) -> CommandResult:
        """
        Execute the mount command for a unit.
        
        Args:
            unit_id: The ID of the unit to mount
            
        Returns:
            CommandResult: Result of the command execution
        """
        if not self.can_mount(unit_id):
            return CommandResult(False, "Unit cannot mount")
        
        unit = self.unit_system.get_unit(unit_id)
        mounted_class = self.data_provider.get_class(unit.mounted_class_id)
        dismounted_class = self.data_provider.get_class(mounted_class.dismounted_equivalent_id)
        
        # 1. Update State Flag
        unit.is_mounted = True
        
        # 2. Revert Stat Changes
        if mounted_class.dismount_stat_modifiers:
            for stat, change in mounted_class.dismount_stat_modifiers.items():
                unit.current_stats[stat] -= change  # Reverse the change
        
        # Always set MOV directly regardless of modifiers
        unit.current_stats["MOV"] = mounted_class.mov
        
        # 3. Revert Movement Type
        unit.current_movement_type = mounted_class.movement_type
        
        # 4. Handle Weapon Access Restoration
        # Weapon access is restored implicitly by changing the mounted state
        
        # 5. Consume Action
        self.unit_system.set_unit_action_taken(unit_id)
        
        # 6. Update Visuals
        self.game_state_manager.notify_visual_update(unit_id, "mounted")
        
        return CommandResult(True)

    def handle_automatic_dismount_on_map_load(self, map_id: str) -> None:
        """
        Handle automatic dismounting when loading an indoor map.
        
        Args:
            map_id: The ID of the map being loaded
        """
        map_data = self.data_provider.get_map(map_id)
        if map_data.is_indoor:
            all_units = self.unit_system.get_all_player_units()
            for unit in all_units:
                if unit.is_mounted and self.data_provider.get_class(unit.mounted_class_id).can_mount:
                    # Apply dismount state changes WITHOUT consuming action
                    self.apply_dismount_state(unit.id, False)  # False indicates no action cost

    def handle_automatic_mount_on_prep_load(self, map_id: str) -> None:
        """
        Handle automatic mounting when loading the prep screen for an outdoor map.
        
        Args:
            map_id: The ID of the map being loaded
        """
        map_data = self.data_provider.get_map(map_id)
        if not map_data.is_indoor:
            all_units = self.unit_system.get_all_player_units_in_roster()
            for unit in all_units:
                original_class = self.data_provider.get_class(unit.mounted_class_id)
                if not unit.is_mounted and original_class and original_class.can_mount:
                    # Apply mount state changes
                    self.apply_mount_state(unit.id)

    def apply_dismount_state(self, unit_id: str, consumes_action: bool) -> None:
        """
        Apply dismount state changes to a unit.
        
        Args:
            unit_id: The ID of the unit to apply changes to
            consumes_action: Whether this should consume the unit's action
        """
        unit = self.unit_system.get_unit(unit_id)
        mounted_class = self.data_provider.get_class(unit.mounted_class_id)
        dismounted_class = self.data_provider.get_class(mounted_class.dismounted_equivalent_id)
        
        unit.is_mounted = False
        # Apply stat changes (Mov, etc.)
        unit.current_stats["MOV"] = dismounted_class.mov
        # Apply other potential stat adjustments based on class diff or modifiers
        unit.current_movement_type = dismounted_class.movement_type
        self.handle_weapon_restriction(unit, dismounted_class.usable_weapon_types_dismounted)
        
        if consumes_action:
            self.unit_system.set_unit_action_taken(unit_id)
        
        self.game_state_manager.notify_visual_update(unit_id, "dismounted")

    def apply_mount_state(self, unit_id: str) -> None:
        """
        Apply mount state changes to a unit.
        
        Args:
            unit_id: The ID of the unit to apply changes to
        """
        unit = self.unit_system.get_unit(unit_id)
        mounted_class = self.data_provider.get_class(unit.mounted_class_id)
        
        unit.is_mounted = True
        # Revert stat changes (Mov, etc.)
        unit.current_stats["MOV"] = mounted_class.mov
        # Revert other potential stat adjustments
        unit.current_movement_type = mounted_class.movement_type
        # Weapon access restored implicitly by state change
        
        self.game_state_manager.notify_visual_update(unit_id, "mounted")

    def handle_weapon_restriction(self, unit, allowed_weapon_types: List[str]) -> None:
        """
        Handle weapon restrictions when dismounting.
        
        Args:
            unit: The unit to handle weapon restrictions for
            allowed_weapon_types: List of weapon types that are allowed when dismounted
        """
        equipped_item = self.unit_system.get_equipped_item(unit.id)
        
        # Check if current equipped item is allowed
        need_to_unequip = False
        if equipped_item:
            item_data = self.data_provider.get_item(equipped_item.id)
            if item_data.type not in allowed_weapon_types:
                need_to_unequip = True
                self.unit_system.unequip_item(unit.id)
        
        # If we unequipped or had nothing equipped, try to find a valid weapon
        if need_to_unequip or not equipped_item:
            # Check all inventory items to find a valid weapon
            valid_item_found = False
            
            # First, get data for all items in inventory to ensure all items are checked
            inventory_item_data = []
            for item in unit.inventory:
                item_data = self.data_provider.get_item(item.id)
                inventory_item_data.append((item, item_data))
            
            # Then find a valid weapon to equip
            for i, (item, item_data) in enumerate(inventory_item_data):
                if item_data.type in allowed_weapon_types:
                    # Find the index of this item in the unit's inventory
                    for j, inv_item in enumerate(unit.inventory):
                        if inv_item.id == item.id:
                            self.unit_system.equip_item(unit.id, j)
                            break
                    valid_item_found = True
                    break