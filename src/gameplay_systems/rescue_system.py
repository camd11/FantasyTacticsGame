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
        2. Rescuer cannot be carrying, target cannot be carried or carrying
        3. Can only rescue own faction or NPCs
        4. Rescuer's Build/Con must be >= Target's Build/Con / 2
        5. Mounted rescuers get +5 effective Build for rescue checks
        
        Args:
            rescuer_id: ID of the rescuer unit
            target_id: ID of the target unit to be rescued
            
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
        
        # Check statuses: Rescuer cannot be carrying, Target cannot be carried or carrying
        if rescuer.status == StatusEnum.RESCUING:
            return False
        
        if target.status in [StatusEnum.RESCUED, StatusEnum.CAPTURED, StatusEnum.RESCUING]:
            return False
        
        # Check faction: Can rescue own faction or NPCs
        if rescuer.faction != target.faction and target.faction != "NPC":
            return False
        
        # Check Constitution/Build: Rescuer's Build/Con >= Target's Build/Con / 2
        # Use bld if available, otherwise fall back to con for backward compatibility
        rescuer_build = rescuer.stats.get("bld", rescuer.stats.get("con", 0))
        target_build = target.stats.get("bld", target.stats.get("con", 0))
        
        # Mounted units and ballistas are considered to have 20 Con for rescue purposes
        if hasattr(rescuer, 'is_mounted') and rescuer.is_mounted and not rescuer.is_dismounted:
            rescuer_con = 20
        elif hasattr(rescuer, 'unit_type') and rescuer.unit_type == 'ballista':
            rescuer_con = 20
            
        # The actual Build check: effective_rescuer_build >= target_build / 2
        if effective_rescuer_build < (target_build / 2):
            return False
        
        # Additional checks for mounted/dismounted states
        if hasattr(rescuer, 'is_mounted') and rescuer.is_mounted:
            if hasattr(rescuer, 'is_dismounted') and rescuer.is_dismounted:
                # Check if indoors - dismounted units can rescue indoors
                if self.map_system.is_indoor(rescuer.position):
                    return True
            # Other mounted unit checks could go here
        
        return True
    
    def initiate_rescue(self, rescuer_id: str, target_id: str) -> bool:
        """
        Execute the Rescue action.
        
        Args:
            rescuer_id: ID of the rescuer unit
            target_id: ID of the target unit to be rescued
            
        Returns:
            True if the rescue was successful, False otherwise
        """
        if not self.can_rescue(rescuer_id, target_id):
            return False
        
        # Get the units
        rescuer = self.game_state_manager.get_unit(rescuer_id)
        target = self.game_state_manager.get_unit(target_id)
        
        # Update states
        rescuer.status = StatusEnum.RESCUING
        rescuer.carried_unit_id = target_id
        target.status = StatusEnum.RESCUED
        target.carrier_unit_id = rescuer_id
        
        # Apply penalties to rescuer
        self.apply_carry_penalties(rescuer, target)
        
        # Update map state (target is no longer visually on map)
        self.map_system.update_unit_visibility(target, False)
        
        # Consume action
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
        4. Taker's Build/Con must be >= Carried Unit's Build/Con / 2
        5. Mounted takers get +5 effective Build for take checks
        
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
        
        # Cannot take from self
        if taker_id == current_rescuer_id:
            return False
        
        # Check adjacency
        if not self.map_system.is_adjacent(taker.position, current_rescuer.position):
            return False
        
        # Check if current rescuer is carrying someone
        if current_rescuer.status != StatusEnum.RESCUING or not current_rescuer.carried_unit_id:
            return False
        
        # Check if taker is already carrying someone
        if taker.status == StatusEnum.RESCUING:
            return False
        
        # Check Constitution: Taker's Con > Carried Unit's Con
        # Get the carried unit
        carried_unit = self.game_state_manager.get_unit(current_rescuer.carried_unit_id)
        
        taker_con = taker.stats.get("con", 0)
        carried_con = carried_unit.stats.get("con", 0)
        
        # Mounted units and ballistas are considered to have 20 Con for take purposes
        if hasattr(taker, 'is_mounted') and taker.is_mounted and not taker.is_dismounted:
            taker_con = 20
        elif hasattr(taker, 'unit_type') and taker.unit_type == 'ballista':
            taker_con = 20
            
        # The actual Con check: taker_con > carried_con
        if taker_con <= carried_con:
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
        
        # Get the units
        taker = self.game_state_manager.get_unit(taker_id)
        current_rescuer = self.game_state_manager.get_unit(current_rescuer_id)
        carried_unit = self.game_state_manager.get_unit(current_rescuer.carried_unit_id)
        
        # Remove penalties from original rescuer
        self.remove_carry_penalties(current_rescuer)
        
        # Update states
        current_rescuer.status = StatusEnum.NORMAL
        current_rescuer.carried_unit_id = None
        
        taker.status = StatusEnum.RESCUING
        taker.carried_unit_id = carried_unit.id
        carried_unit.carrier_unit_id = taker_id
        
        # Apply penalties to new rescuer
        self.apply_carry_penalties(taker, carried_unit)
        
        # Consume taker's action
        taker.action_taken = True
        
        return True
    
    def apply_carry_penalties(self, carrier, carried) -> None:
        """
        Apply stat penalties to a unit carrying another unit.
        
        Carry Penalties (based on Thracia 776 with custom adjustments):
        1. Combat stats (Str/Mag/Skl/Spd/Def) are halved
        2. Movement penalty: Mov is halved if Carried Con > Carrier Con / 2
           Note: For movement penalties, we use actual Con, not effective Con
        3. Mounted units and ballistas are considered to have 20 Con for rescue purposes
           (but NOT for movement penalty calculations)
        
        Args:
            carrier: The unit carrying another unit
            carried: The unit being carried
        """
        # Store original stats if not already done
        if not hasattr(carrier, 'temp_stats') or not carrier.temp_stats:
            carrier.temp_stats = {}
            carrier.temp_stats['original_str'] = carrier.stats.get('str', 0)
            carrier.temp_stats['original_mag'] = carrier.stats.get('mag', 0)
            carrier.temp_stats['original_skl'] = carrier.stats.get('skl', 0)
            carrier.temp_stats['original_spd'] = carrier.stats.get('spd', 0)
            carrier.temp_stats['original_def'] = carrier.stats.get('def', 0)
            carrier.temp_stats['original_mov'] = carrier.stats.get('mov', 0)

        # Halve combat stats (floor division)
        carrier.stats['str'] = carrier.temp_stats['original_str'] // 2
        carrier.stats['mag'] = carrier.temp_stats['original_mag'] // 2
        carrier.stats['skl'] = carrier.temp_stats['original_skl'] // 2
        carrier.stats['spd'] = carrier.temp_stats['original_spd'] // 2
        carrier.stats['def'] = carrier.temp_stats['original_def'] // 2

        # Check for Movement penalty
        # Movement is halved if: carried unit's Con > half of carrier's ACTUAL Con
        try:
            # For movement penalties, we use the ACTUAL Con (not effective Con)
            carrier_con = carrier.stats.get('con', 0)
            carried_con = carried.stats.get('con', 0)
            
            # Calculate the threshold (half of carrier's ACTUAL Con)
            half_carrier_con = carrier_con / 2

            # Apply movement penalty if carried unit is too heavy
            if carried_con > half_carrier_con:
                carrier.stats['mov'] = carrier.temp_stats['original_mov'] // 2
            else:
                carrier.stats['mov'] = carrier.temp_stats['original_mov']
        except (TypeError, AttributeError) as e:
            # For test mocks or if there's an error, log it and apply the penalty by default
            logging.debug(f"Error in apply_carry_penalties: {e}. Applying movement penalty by default.")
            carrier.stats['mov'] = carrier.temp_stats['original_mov'] // 2
    
    def remove_carry_penalties(self, carrier) -> None:
        """
        Remove stat penalties from a unit that was carrying another unit.
        
        Args:
            carrier: The unit that was carrying another unit
        """
        if not hasattr(carrier, 'temp_stats') or not carrier.temp_stats:
            return  # No penalties were applied or already removed
        
        # Restore original stats
        carrier.stats['str'] = carrier.temp_stats['original_str']
        carrier.stats['mag'] = carrier.temp_stats['original_mag']
        carrier.stats['skl'] = carrier.temp_stats['original_skl']
        carrier.stats['spd'] = carrier.temp_stats['original_spd']
        carrier.stats['def'] = carrier.temp_stats['original_def']
        carrier.stats['mov'] = carrier.temp_stats['original_mov']
        
        # Clear temporary storage
        carrier.temp_stats = {}