"""
Berserk Turn Logic Module

This module implements the logic for handling turns of units affected by the Berserk status effect.
When a unit is berserked, it will automatically attack the nearest unit within range, regardless of allegiance.
"""

import logging
import random
from typing import Dict, List, Tuple, Optional, Any, Set, Union

from src.core_engine.game_state import GameStateManager, FactionEnum, DispositionEnum


class BerserkTurnLogic:
    """
    Handles the turn logic for units affected by the Berserk status effect.
    
    When a unit is berserked, it will:
    1. Identify all units on the map
    2. Calculate distances to find the nearest unit(s)
    3. Check if the nearest unit(s) are within attack range
    4. If a target is in range: Select the target and execute an attack
    5. If no target is in range: Move towards the nearest unit
    """
    
    def __init__(self):
        """Initialize the BerserkTurnLogic."""
        self.game_state_manager = None
        self.unit_system = None
        self.combat_system = None
        self.map_system = None
        self.movement_system = None
        self.action_system = None
        
    def initialize(self, game_state_manager, unit_system, combat_system, map_system, movement_system, action_system):
        """
        Initialize the BerserkTurnLogic with the necessary dependencies.
        
        Args:
            game_state_manager: Instance of the GameStateManager
            unit_system: Instance of the UnitSystem
            combat_system: Instance of the CombatSystem
            map_system: Instance of the MapSystem
            movement_system: Instance of the MovementSystem
            action_system: Instance of the ActionSystem
        """
        self.game_state_manager = game_state_manager
        self.unit_system = unit_system
        self.combat_system = combat_system
        self.map_system = map_system
        self.movement_system = movement_system
        self.action_system = action_system
        logging.info("BerserkTurnLogic initialized.")
        
    def execute_berserk_turn(self, unit_id: str) -> bool:
        """
        Execute a berserk turn for the given unit.
        
        Args:
            unit_id: ID of the berserked unit
            
        Returns:
            bool: True if the turn was executed successfully, False otherwise
        """
        unit = self.game_state_manager.get_unit(unit_id)
        if not unit:
            logging.error(f"BerserkTurnLogic: Unit {unit_id} not found")
            return False
        
        logging.info(f"BerserkTurnLogic: Executing berserk turn for unit {unit_id}")
        
        # Find nearest target
        target_id, distance = self._find_nearest_target(unit_id)
        
        if target_id:
            # Check if target is in attack range
            if self._is_target_in_attack_range(unit_id, target_id):
                # Attack target
                logging.info(f"BerserkTurnLogic: Unit {unit_id} attacking {target_id}")
                self._attack_target(unit_id, target_id)
                return True
            else:
                # Move towards target
                logging.info(f"BerserkTurnLogic: Unit {unit_id} moving towards {target_id}")
                self._move_towards_target(unit_id, target_id)
                return True
        else:
            # No targets, wait
            logging.info(f"BerserkTurnLogic: No targets for unit {unit_id}, waiting")
            self.action_system.mark_unit_action_complete(unit_id)
            return True
    
    def _find_nearest_target(self, unit_id: str) -> Tuple[Optional[str], int]:
        """
        Find the nearest target for the berserked unit.
        
        Args:
            unit_id: ID of the berserked unit
            
        Returns:
            Tuple containing the ID of the nearest target and the distance to it,
            or (None, float('inf')) if no target is found
        """
        unit = self.game_state_manager.get_unit(unit_id)
        if not unit:
            return None, float('inf')
        
        unit_position = unit.position
        nearest_distance = float('inf')
        nearest_targets = []
        
        # Get all active units
        for target_id, target in self.game_state_manager.current_game_state.unit_states.items():
            # Skip self and non-active units
            if target_id == unit_id or target.disposition != DispositionEnum.ACTIVE:
                continue
            
            # Calculate Manhattan distance
            target_position = target.position
            distance = abs(unit_position[0] - target_position[0]) + abs(unit_position[1] - target_position[1])
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_targets = [target_id]
            elif distance == nearest_distance:
                nearest_targets.append(target_id)
        
        if not nearest_targets:
            return None, float('inf')
        
        # If multiple targets at same distance, choose one with lowest HP or randomly
        if len(nearest_targets) > 1:
            # Find target with lowest HP
            lowest_hp = float('inf')
            lowest_hp_targets = []
            
            for target_id in nearest_targets:
                target = self.game_state_manager.get_unit(target_id)
                if target.current_hp < lowest_hp:
                    lowest_hp = target.current_hp
                    lowest_hp_targets = [target_id]
                elif target.current_hp == lowest_hp:
                    lowest_hp_targets.append(target_id)
            
            # If still multiple targets, choose randomly
            return random.choice(lowest_hp_targets), nearest_distance
        
        return nearest_targets[0], nearest_distance
    
    def _is_target_in_attack_range(self, unit_id: str, target_id: str) -> bool:
        """
        Check if the target is in attack range of the unit.
        
        Args:
            unit_id: ID of the berserked unit
            target_id: ID of the target unit
            
        Returns:
            bool: True if the target is in attack range, False otherwise
        """
        unit = self.game_state_manager.get_unit(unit_id)
        target = self.game_state_manager.get_unit(target_id)
        
        if not unit or not target:
            return False
        
        # Check if unit has a weapon equipped
        if unit.equipped_weapon_index < 0 or unit.equipped_weapon_index >= len(unit.inventory):
            return False
        
        # Get the equipped weapon
        weapon = unit.inventory[unit.equipped_weapon_index]
        
        # Get weapon data
        weapon_data = self.game_state_manager.data_provider.get_item_data(weapon.item_id)
        if not weapon_data:
            return False
        
        # Calculate distance
        unit_position = unit.position
        target_position = target.position
        distance = abs(unit_position[0] - target_position[0]) + abs(unit_position[1] - target_position[1])
        
        # Check if distance is within weapon range
        return weapon_data.range_min <= distance <= weapon_data.range_max
    
    def _attack_target(self, unit_id: str, target_id: str) -> bool:
        """
        Attack the target.
        
        Args:
            unit_id: ID of the berserked unit
            target_id: ID of the target unit
            
        Returns:
            bool: True if the attack was executed successfully, False otherwise
        """
        # Execute combat
        combat_result = self.combat_system.execute_combat(unit_id, target_id)
        
        # Mark unit as having acted
        self.action_system.mark_unit_action_complete(unit_id)
        
        return combat_result is not None
    
    def _move_towards_target(self, unit_id: str, target_id: str) -> bool:
        """
        Move towards the target.
        
        Args:
            unit_id: ID of the berserked unit
            target_id: ID of the target unit
            
        Returns:
            bool: True if the movement was executed successfully, False otherwise
        """
        unit = self.game_state_manager.get_unit(unit_id)
        target = self.game_state_manager.get_unit(target_id)
        
        if not unit or not target:
            return False
        
        # Get unit's movement range
        movement_range = self.movement_system.calculate_movement_range(unit_id)
        
        # Find path to target
        target_position = target.position
        best_position = None
        best_distance = float('inf')
        
        for position in movement_range:
            # Calculate distance from this position to target
            distance = abs(position[0] - target_position[0]) + abs(position[1] - target_position[1])
            
            # If this position is closer to the target than our current best, update best
            if distance < best_distance:
                best_distance = distance
                best_position = position
        
        if best_position:
            # Move to best position
            success = self.movement_system.move_unit(unit_id, best_position)
            
            # Mark unit as having acted
            self.action_system.mark_unit_action_complete(unit_id)
            
            return success
        
        # If no valid movement found, just mark as acted
        self.action_system.mark_unit_action_complete(unit_id)
        return True