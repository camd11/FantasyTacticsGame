"""
Capture Handler Module

This module handles the capture mechanics for the Fantasy Tactics Game.
It implements the unique capture system from Thracia 776, allowing units to capture
enemies under specific conditions and manage captured units.
"""

from typing import Dict, Any, Optional, List, Tuple


class CaptureHandler:
    """
    Handles the capture mechanics based on Thracia 776 rules.
    """

    def __init__(self, game_state_manager, data_provider, unit_system):
        """
        Initialize the CaptureHandler.
        
        Args:
            game_state_manager: Instance of the GameStateManager
            data_provider: Instance of the DataProvider
            unit_system: Instance of the UnitSystem
        """
        self.game_state_manager = game_state_manager
        self.data_provider = data_provider
        self.unit_system = unit_system

    def check_capture_conditions(self, attacker_unit, target_unit):
        """
        Check if a unit can capture another unit based on Thracia 776 rules.
        
        Conditions:
        - Attacker's Con > Target's Con, OR Attacker is mounted
        - Target is not mounted
        - Target's Con < 20
        - Target is not immune to capture
        
        Args:
            attacker_unit: The unit attempting to capture
            target_unit: The unit being targeted for capture
            
        Returns:
            True if capture is possible, False otherwise
        """
        # Check target conditions first (these are absolute)
        if target_unit.is_mounted or target_unit.con >= 20 or target_unit.is_capture_immune:
            return False
        
        # Check attacker conditions
        if attacker_unit.con > target_unit.con or attacker_unit.is_mounted:
            return True
        
        return False

    def process_capture_success(self, attacker_unit, captured_unit, combat_log):
        """
        Process a successful capture, updating unit states and inventory access.
        
        Args:
            attacker_unit: The capturing unit
            captured_unit: The captured unit
            combat_log: Combat log to update with capture information
            
        Returns:
            None
        """
        # Set attacker to carrying state
        attacker_unit.carrying_unit_id = captured_unit.id
        
        # Set captured unit state
        captured_unit.is_captured = True
        
        # Make captured unit's inventory accessible
        captured_unit.inventory.set_accessible(True)
        
        # Update combat log
        combat_log.set_capture_success()

    def release_captive(self, carrier_unit):
        """
        Release a captured unit, removing it from the map.
        
        Args:
            carrier_unit: The unit carrying the captive
            
        Returns:
            True if release was successful, False otherwise
        """
        if carrier_unit.state != "Carrying":
            return False
        
        # Get the captive
        captive = carrier_unit.carried_unit
        
        # Remove captive from map
        captive.remove_from_map()
        
        # Reset carrier state
        carrier_unit.state = "Idle"
        
        return True

    def take_captive(self, taker_unit, carrier_unit):
        """
        Take a captive from another unit.
        
        Args:
            taker_unit: The unit taking the captive
            carrier_unit: The unit currently carrying the captive
            
        Returns:
            True if taking was successful, False otherwise
        """
        if carrier_unit.state != "Carrying":
            return False
        
        # Get the captive
        captive_id = carrier_unit.carrying_unit_id
        
        # Transfer captive
        carrier_unit.carrying_unit_id = None
        carrier_unit.state = "Idle"
        
        taker_unit.carrying_unit_id = captive_id
        taker_unit.state = "Carrying"
        
        return True

    def drop_captive(self, carrier_unit, target_position):
        """
        Drop a captive onto an adjacent tile.
        
        Args:
            carrier_unit: The unit carrying the captive
            target_position: The position to drop the captive
            
        Returns:
            True if dropping was successful, False otherwise
        """
        if carrier_unit.state != "Carrying":
            return False
        
        # Check if target position is adjacent
        if not self._is_adjacent(carrier_unit.position, target_position):
            return False
        
        # Check if target position is valid (empty, passable)
        if not self._is_valid_drop_position(target_position):
            return False
        
        # Get the captive
        captive = self.game_state_manager.get_unit(carrier_unit.carrying_unit_id)
        if not captive:
            return False
        
        # Place captive on map
        captive.position = target_position
        captive.is_captured = False
        
        # Reset carrier state
        carrier_unit.carrying_unit_id = None
        carrier_unit.state = "Idle"
        
        return True

    def apply_carrying_penalties(self, unit_stats):
        """
        Apply stat penalties for carrying a captured unit.
        
        Args:
            unit_stats: Stats to modify
            
        Returns:
            Modified stats
        """
        # In Thracia 776, carrying a unit halves Str, Mag, Skl, Spd, Def (same as capture penalty)
        for stat in ['STR', 'MAG', 'SKL', 'SPD', 'DEF']:
            if stat in unit_stats:
                unit_stats[stat] //= 2
        
        # Recalculate derived stats
        if 'AS' in unit_stats and 'SPD' in unit_stats:
            # Recalculate AS based on new SPD
            unit_stats['AS'] = unit_stats['SPD']  # Simplified; would need to account for weapon weight
        
        # Apply movement penalty if needed
        if 'MOV' in unit_stats:
            unit_stats['MOV'] = max(1, unit_stats['MOV'] - 1)  # Reduce movement by 1, minimum 1
        
        return unit_stats

    # --- Helper Methods ---

    def _is_adjacent(self, pos1, pos2):
        """
        Check if two positions are adjacent.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            True if positions are adjacent, False otherwise
        """
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

    def _is_valid_drop_position(self, position):
        """
        Check if a position is valid for dropping a captive.
        
        Args:
            position: Position to check
            
        Returns:
            True if position is valid, False otherwise
        """
        # Check if position is on the map
        if not self.game_state_manager.is_position_on_map(position):
            return False
        
        # Check if position is empty (no unit)
        if self.game_state_manager.get_unit_at_position(position):
            return False
        
        # Check if position is passable terrain
        terrain_info = self.game_state_manager.get_terrain_at_position(position)
        if not terrain_info.get('passable', False):
            return False
        
        return True