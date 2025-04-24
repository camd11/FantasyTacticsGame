"""
Rescue System Module

This module implements the Rescue, Drop, and Take mechanics, primarily based on Fire Emblem: Thracia 776 rules.
These actions allow units to carry allies, reposition them, or transfer them between carriers.
"""

import logging
from typing import Dict, Optional, Tuple

from src.core_engine.game_state import GameStateManager, FactionEnum, StatusEnum, DispositionEnum


class RescueSystem:
    """
    Manages the Rescue, Drop, and Take mechanics.
    Allows units to carry allies, reposition them, or transfer them between carriers.
    """
    
    def __init__(self):
        """Initialize the RescueSystem."""
        self.game_state_manager = None
        self.data_provider = None
        self.map_system = None
        self.action_system = None
    
    def initialize(self, game_state_manager, data_provider, map_system, action_system) -> None:
        """
        Initialize the RescueSystem with the necessary dependencies.
        
        Args:
            game_state_manager: Instance of the GameStateManager
            data_provider: Instance of the DataProvider
            map_system: Instance of the MapSystem
            action_system: Instance of the ActionSystem
        """
        self.game_state_manager = game_state_manager
        self.data_provider = data_provider
        self.map_system = map_system
        self.action_system = action_system
        logging.info("RescueSystem initialized.")
    
    def can_rescue(self, rescuer_id: str, target_id: str) -> bool:
        """
        Check if a unit can rescue another unit.
        
        Rescue Mechanics (based on Thracia 776 with custom adjustments):
        1. Rescuer must be adjacent to target
        2. Target must not be already rescued
        3. Rescuer must not be already carrying a unit
        4. Rescuer's Con must be greater than the target's Con
        5. Mounted rescuers and ballistas have 20 Con for rescue purposes
        
        Args:
            rescuer_id: ID of the unit doing the rescuing
            target_id: ID of the unit to be rescued
            
        Returns:
            True if the rescue action is valid, False otherwise
        """
        # Get the units
        rescuer = self.game_state_manager.get_unit(rescuer_id)
        target = self.game_state_manager.get_unit(target_id)
        
        # Basic validation
        if not rescuer or not target:
            return False
        
        # Cannot rescue self
        if rescuer_id == target_id:
            return False
        
        # Check adjacency
        if not self.map_system.is_adjacent(rescuer.position, target.position):
            return False
        
        # Check if target is already rescued
        if target.status == StatusEnum.RESCUED:
            return False
        
        # Check if rescuer is already carrying someone
        if rescuer.status == StatusEnum.RESCUING:
            return False
        
        # Check Constitution: Rescuer's Con > Target's Con
        rescuer_con = rescuer.stats.get("con", 0)
        target_con = target.stats.get("con", 0)
        
        # Calculate effective Constitution for the rescuer
        effective_rescuer_con = rescuer_con
        if hasattr(rescuer, 'is_mounted') and rescuer.is_mounted and not rescuer.is_dismounted:
            effective_rescuer_con = 20
        elif hasattr(rescuer, 'unit_type') and rescuer.unit_type == 'ballista':
            effective_rescuer_con = 20
            
        # Perform the Con check
        if effective_rescuer_con <= target_con:
            return False
            
        return True
    
    def initiate_rescue(self, rescuer_id: str, target_id: str) -> bool:
        """
        Execute the Rescue action.
        
        Args:
            rescuer_id: ID of the unit doing the rescuing
            target_id: ID of the unit to be rescued
            
        Returns:
            True if the rescue was successful, False otherwise
        """
        if not self.can_rescue(rescuer_id, target_id):
            return False
        
        # Get the units
        rescuer = self.game_state_manager.get_unit(rescuer_id)
        target = self.game_state_manager.get_unit(target_id)
        
        # Set the target's status to RESCUED
        target.status = StatusEnum.RESCUED
        target.carrier_unit_id = rescuer_id
        target.last_position = target.position.copy()
        
        # Hide the target (visually)
        target.position.x = -999
        target.position.y = -999
        
        # Set the rescuer's status to RESCUING
        rescuer.status = StatusEnum.RESCUING
        rescuer.carried_unit_id = target_id
        
        # Apply penalties to the rescuer
        self.apply_carry_penalties(rescuer, target)
        
        # Consume the rescuer's action
        rescuer.action_taken = True
        
        return True
    
    def can_drop(self, rescuer_id: str, drop_position: Tuple[int, int]) -> bool:
        """
        Check if a unit can drop their carried unit at a specific position.
        
        Args:
            rescuer_id: ID of the rescuer unit
            drop_position: Position (x, y) to drop the carried unit
            
        Returns:
            True if the drop action is valid, False otherwise
        """
        # Get the rescuer
        rescuer = self.game_state_manager.get_unit(rescuer_id)
        
        # Basic validation
        if not rescuer or rescuer.status != StatusEnum.RESCUING or not rescuer.carried_unit_id:
            return False
        
        # Check adjacency
        if not self.map_system.is_adjacent(rescuer.position, drop_position):
            return False
        
        # Check if the drop position is occupied
        if self.map_system.get_unit_at(drop_position):
            return False
        
        # Check if the drop position is passable for the carried unit
        carried_unit = self.game_state_manager.get_unit(rescuer.carried_unit_id)
        if not self.map_system.is_passable(drop_position, carried_unit.movement_type):
            return False
        
        return True
    
    def initiate_drop(self, rescuer_id: str, drop_position: Tuple[int, int]) -> bool:
        """
        Execute the Drop action.
        
        Args:
            rescuer_id: ID of the rescuer unit
            drop_position: Position (x, y) to drop the carried unit
            
        Returns:
            True if the drop was successful, False otherwise
        """
        if not self.can_drop(rescuer_id, drop_position):
            return False
        
        # Get the units
        rescuer = self.game_state_manager.get_unit(rescuer_id)
        dropped_unit = self.game_state_manager.get_unit(rescuer.carried_unit_id)
        
        # Update states
        rescuer.status = StatusEnum.NORMAL
        rescuer.carried_unit_id = None
        dropped_unit.status = StatusEnum.NORMAL
        dropped_unit.carrier_unit_id = None
        dropped_unit.position = drop_position
        
        # Dropped unit cannot act this turn
        dropped_unit.action_taken = True
        
        # Remove penalties from rescuer
        self.remove_carry_penalties(rescuer)
        
        # Update map state (dropped unit is now visible at drop_position)
        self.map_system.update_unit_visibility(dropped_unit, True)
        self.map_system.update_unit_position(dropped_unit, drop_position)
        
        # Consume action
        rescuer.action_taken = True
        
        return True
    
    def can_take(self, taker_id: str, current_rescuer_id: str) -> bool:
        """
        Check if a unit can take a carried unit from another unit.
        
        Take Mechanics (based on Thracia 776 with custom adjustments):
        1. Taker must be adjacent to the current rescuer
        2. Current rescuer must be carrying a unit
        3. Taker cannot already be carrying a unit
        4. Taker's Con must be >= Carried Unit's Con / 2
        5. Mounted takers get +5 effective Con for take checks
        
        Args:
            taker_id: ID of the unit taking the carried unit
            current_rescuer_id: ID of the unit currently carrying a unit
            
        Returns:
            True if the take action is valid, False otherwise
        """
        # Get the units
        taker = self.game_state_manager.get_unit(taker_id)
        current_rescuer = self.game_state_manager.get_unit(current_rescuer_id)
        
        # Basic validation
        if not taker or not current_rescuer:
            return False
        
        # Check if current rescuer is actually carrying someone
        if current_rescuer.status != StatusEnum.RESCUING or not current_rescuer.carried_unit_id:
            return False
        
        # Check if taker is already carrying someone
        if taker.status == StatusEnum.RESCUING:
            return False
        
        # Check adjacency
        if not self.map_system.is_adjacent(taker.position, current_rescuer.position):
            return False
        
        # Check if taker can carry the unit based on Constitution
        carried_unit = self.game_state_manager.get_unit(current_rescuer.carried_unit_id)
        taker_con = taker.stats.get("con", 0)
        carried_unit_con = carried_unit.stats.get("con", 0)
        
        # Calculate effective Constitution for the taker
        effective_taker_con = taker_con
        if hasattr(taker, 'is_mounted') and taker.is_mounted and not taker.is_dismounted:
            effective_taker_con = 20
        elif hasattr(taker, 'unit_type') and taker.unit_type == 'ballista':
            effective_taker_con = 20
            
        # Perform the Con check
        if effective_taker_con < (carried_unit_con / 2):
            return False
            
        return True
    
    def initiate_take(self, taker_id: str, current_rescuer_id: str) -> bool:
        """
        Execute the Take action.
        
        Args:
            taker_id: ID of the unit taking the carried unit
            current_rescuer_id: ID of the unit currently carrying a unit
            
        Returns:
            True if the take was successful, False otherwise
        """
        if not self.can_take(taker_id, current_rescuer_id):
            return False
        
        # Get all involved units
        taker = self.game_state_manager.get_unit(taker_id)
        current_rescuer = self.game_state_manager.get_unit(current_rescuer_id)
        carried_unit_id = current_rescuer.carried_unit_id
        carried_unit = self.game_state_manager.get_unit(carried_unit_id)
        
        # Remove carried unit from current rescuer
        current_rescuer.status = StatusEnum.NORMAL
        current_rescuer.carried_unit_id = None
        
        # Remove carry penalties from current rescuer
        self.remove_carry_penalties(current_rescuer)
        
        # Apply carried unit to taker
        taker.status = StatusEnum.RESCUING
        taker.carried_unit_id = carried_unit_id
        carried_unit.carrier_unit_id = taker_id
        
        # Apply penalties to taker
        self.apply_carry_penalties(taker, carried_unit)
        
        # Consume action
        taker.action_taken = True
        
        return True
    
    def apply_carry_penalties(self, carrier, carried_unit) -> None:
        """
        Apply penalties to a unit for carrying another unit.
        
        Standard Fire Emblem Carrying penalties:
        - Carrier's Str, Mag, Skl, Spd, and Def are all halved (rounded down)
        - Movement is halved (rounded down) if carried unit's Con exceeds half of carrier's Con
        
        Args:
            carrier: The unit carrying another unit
            carried_unit: The unit being carried
        """
        # Store original stats to allow restoration when dropping
        if not hasattr(carrier, 'original_stats_before_carrying'):
            carrier.original_stats_before_carrying = {}
            
        # Store original stats
        stats_to_halve = ['str', 'mag', 'skl', 'spd', 'def']
        for stat in stats_to_halve:
            if stat in carrier.stats:
                carrier.original_stats_before_carrying[stat] = carrier.stats.get(stat, 0)
                # Halve the stat (integer division for rounding down)
                carrier.stats[stat] = carrier.stats.get(stat, 0) // 2
        
        # Store original movement if it exists
        if 'mov' in carrier.stats:
            carrier.original_stats_before_carrying['mov'] = carrier.stats.get('mov', 0)
            
            # Apply movement penalty if carried unit's Con > half of carrier's Con
            carrier_con = carrier.stats.get('con', 0)
            carried_unit_con = carried_unit.stats.get('con', 0)
            
            if carried_unit_con > (carrier_con / 2):
                # Halve movement (integer division for rounding down)
                carrier.stats['mov'] = carrier.stats.get('mov', 0) // 2
    
    def remove_carry_penalties(self, carrier) -> None:
        """
        Remove penalties from a unit that was carrying another unit.
        
        Args:
            carrier: The unit that was carrying another unit
        """
        if hasattr(carrier, 'original_stats_before_carrying'):
            # Restore original stats
            for stat, original_value in carrier.original_stats_before_carrying.items():
                carrier.stats[stat] = original_value
            
            # Clear stored original stats
            delattr(carrier, 'original_stats_before_carrying')
    
    def get_carried_unit(self, carrier_id: str) -> Optional[str]:
        """
        Get the ID of the unit being carried by the specified carrier.
        
        Args:
            carrier_id: ID of the carrier unit
            
        Returns:
            ID of the carried unit if found, None otherwise
        """
        carrier = self.game_state_manager.get_unit(carrier_id)
        if carrier and carrier.status == StatusEnum.RESCUING and carrier.carried_unit_id:
            return carrier.carried_unit_id
        return None
    
    def get_carrier_unit(self, carried_id: str) -> Optional[str]:
        """
        Get the ID of the unit carrying the specified unit.
        
        Args:
            carried_id: ID of the carried unit
            
        Returns:
            ID of the carrier unit if found, None otherwise
        """
        carried = self.game_state_manager.get_unit(carried_id)
        if carried and carried.status == StatusEnum.RESCUED and carried.carrier_unit_id:
            return carried.carrier_unit_id
        return None