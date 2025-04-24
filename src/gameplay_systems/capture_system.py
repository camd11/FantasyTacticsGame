"""
Capture System Module

This module implements the capture mechanics for the Fantasy Tactics Game.
It allows units to capture enemies under specific conditions, manage captured units,
handle item stealing, and release captured units.

Note: Constitution (Con) replaced the Build/Bld stat from previous versions.
Mounted units are considered to have 20 Con for capturing/rescuing purposes only.
Units with 20 or more Con cannot be captured or rescued.

IMPORTANT: Mounted units don't actually change their Con value in stats - they retain 
their original Con stat but are TREATED as having 20 Con for capture mechanics only.

TODO: Implement rescue chains (allowing units to rescue others who are already carrying someone).
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union

from src.core_engine.game_state import GameStateManager, UnitState
from src.core_engine.data_provider import DataProvider
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.inventory_system import InventorySystem
from src.gameplay_systems.combat_system import CombatSystem


class CaptureSystem:
    """
    Implements the capture mechanics based on Thracia 776 rules.
    """

    def __init__(self):
        """Initialize the CaptureSystem."""
        self.game_state_manager = None
        self.data_provider = None
        self.unit_system = None
        self.map_system = None
        self.inventory_system = None
        self.combat_system = None

    def initialize(self, game_state_manager: GameStateManager, data_provider: DataProvider,
                  unit_system: UnitSystem, map_system: MapSystem,
                  inventory_system: InventorySystem, combat_system: CombatSystem) -> None:
        """
        Initialize the CaptureSystem with the necessary dependencies.
        
        Args:
            game_state_manager: Instance of the GameStateManager
            data_provider: Instance of the DataProvider
            unit_system: Instance of the UnitSystem
            map_system: Instance of the MapSystem
            inventory_system: Instance of the InventorySystem
            combat_system: Instance of the CombatSystem
        """
        self.game_state_manager = game_state_manager
        self.data_provider = data_provider
        self.unit_system = unit_system
        self.map_system = map_system
        self.inventory_system = inventory_system
        self.combat_system = combat_system
        logging.info("CaptureSystem initialized.")

    def can_initiate_capture(self, attacker: UnitState, defender: UnitState) -> bool:
        """
        Determine if the attacker can attempt to capture the defender.
        
        Conditions:
        - Defender's Con < 20 (units with 20+ Con cannot be captured)
        - Defender is not mounted
        - Attacker has a weapon usable at range 1 (melee weapon)
        - Attacker's Con > Defender's Con OR Attacker is mounted (mounted units have effective 20 Con)
        
        Args:
            attacker: The unit attempting to capture
            defender: The unit being targeted for capture
            
        Returns:
            True if capture is possible, False otherwise
        """
        # Check if attacker has a weapon usable at range 1
        has_melee_weapon = False
        if attacker.equipped_weapon_index >= 0:
            weapon = attacker.inventory[attacker.equipped_weapon_index]
            # Check if weapon can be used at range 1
            if hasattr(weapon, 'min_range') and hasattr(weapon, 'max_range'):
                has_melee_weapon = weapon.min_range <= 1 <= weapon.max_range
        
        if not has_melee_weapon:
            return False
        
        # Check defender conditions first (these are absolute)
        if defender.is_mounted or defender.stats.get('Con', 0) >= 20:
            return False
        
        # Calculate effective Constitution for the attacker
        attacker_con = attacker.stats.get('Con', 0)
        effective_attacker_con = 20 if attacker.is_mounted else attacker_con
        
        # Check attacker conditions
        if effective_attacker_con > defender.stats.get('Con', 0):
            return True
        
        return False

    def attempt_capture(self, attacker: UnitState, defender: UnitState) -> bool:
        """
        Initiate a capture attempt, potentially leading to combat.
        
        Args:
            attacker: The unit attempting to capture
            defender: The unit being targeted for capture
            
        Returns:
            True if the capture was successful, False otherwise
        """
        # Verify capture conditions
        if not self.can_initiate_capture(attacker, defender):
            logging.info(f"{attacker.name} cannot capture {defender.name}")
            return False
        
        # Check if defender is unarmed or incapacitated
        is_unarmed = defender.equipped_weapon_index < 0
        is_sleeping = defender.status == "Sleep"
        
        if is_unarmed or is_sleeping:
            # Capture succeeds without combat
            logging.info(f"{attacker.name} captures {defender.name} without combat (unarmed or sleeping)")
            self._apply_successful_capture(attacker, defender)
            return True
        
        # Apply temporary capture penalties to attacker
        original_stats = self._backup_stats(attacker)
        self._apply_capture_penalties(attacker)
        
        # Initiate combat
        combat_result = self.combat_system.execute_combat(attacker.id, defender.id, is_capture=True)
        
        # Restore original stats to attacker
        self._restore_stats(attacker, original_stats)
        
        # Check combat outcome
        if defender.current_hp <= 0:
            # Capture successful
            logging.info(f"{attacker.name} successfully captured {defender.name} in combat")
            self._apply_successful_capture(attacker, defender)
            return True
        else:
            # Capture failed
            logging.info(f"{attacker.name} failed to capture {defender.name}")
            return False

    def _apply_successful_capture(self, capturer: UnitState, captured_unit: UnitState) -> None:
        """
        Handle the state changes when a capture is successful.
        
        Args:
            capturer: The unit that captured
            captured_unit: The unit that was captured
        """
        # Set captured unit state
        captured_unit.status = "Captured"
        captured_unit.current_hp = 1  # Set to 1 HP
        
        # Set capturer state
        capturer.status = "Carrying"
        capturer.carried_unit = captured_unit
        
        # Apply carrying penalties to capturer
        self._apply_carrying_penalties(capturer, captured_unit)
        
        logging.info(f"{capturer.name} is now carrying {captured_unit.name}")

    def _apply_capture_penalties(self, unit: UnitState) -> None:
        """
        Apply temporary stat penalties during a capture attempt.
        
        Args:
            unit: The unit attempting to capture
        """
        # Halve Str, Mag, Skl, Spd, Def (round down)
        unit.stats["Str"] //= 2
        unit.stats["Mag"] //= 2
        unit.stats["Skl"] //= 2
        unit.stats["Spd"] //= 2
        unit.stats["Def"] //= 2

    def _apply_carrying_penalties(self, capturer: UnitState, captured_unit: UnitState) -> None:
        """
        Apply stat penalties for carrying a captured unit.
        
        Args:
            capturer: The unit carrying the captive
            captured_unit: The captured unit
        """
        # Halve Str, Mag, Skl, Spd, Def (round down)
        capturer.stats["Str"] //= 2
        capturer.stats["Mag"] //= 2
        capturer.stats["Skl"] //= 2
        capturer.stats["Spd"] //= 2
        capturer.stats["Def"] //= 2
        
        # Apply movement penalty if applicable
        capturer_con = capturer.stats.get("Con", 0)
        con_threshold = capturer_con // 2
        
        # Mounted units are considered to have 20 Con for rescue purposes
        if capturer.is_mounted and not getattr(capturer, 'is_dismounted', False):
            con_threshold = 10  # Half of effective 20 Con
            
        if captured_unit.stats.get("Con", 0) > con_threshold:
            capturer.stats["Mov"] //= 2  # Halve movement

    def access_captured_inventory(self, trading_unit: UnitState, capturer_unit: UnitState) -> List[Any]:
        """
        Allow a unit adjacent to the capturer to access the inventory of the carried unit.
        
        Args:
            trading_unit: The unit trying to access the inventory
            capturer_unit: The unit carrying the captured unit
            
        Returns:
            List of items in the captured unit's inventory or empty list if access is denied
        """
        # Verify capturer is carrying a unit
        if capturer_unit.status != "Carrying" or capturer_unit.carried_unit is None:
            logging.info(f"{capturer_unit.name} is not carrying a captured unit")
            return []
        
        # Verify trading unit is adjacent to capturer
        if not self._are_units_adjacent(trading_unit, capturer_unit):
            logging.info(f"{trading_unit.name} is not adjacent to {capturer_unit.name}")
            return []
        
        # Return captured unit's inventory
        return capturer_unit.carried_unit.inventory

    # Note: The trade_item functionality is handled by the InventorySystem class
    # The CaptureSystem only provides access to the captured unit's inventory

    def release_captured_unit(self, capturer: UnitState) -> bool:
        """
        Release the captured enemy, removing them from the map.
        
        Args:
            capturer: The unit carrying the captive
            
        Returns:
            True if the release was successful, False otherwise
        """
        # Verify capturer is carrying a unit
        if capturer.status != "Carrying" or capturer.carried_unit is None:
            logging.info(f"{capturer.name} is not carrying a captured unit")
            return False
        
        # Get reference to captured unit
        captured_unit = capturer.carried_unit
        
        # Remove captured unit from the map
        # Update the unit's disposition to remove it from active units
        self.game_state_manager.set_unit_disposition(captured_unit.id, "REMOVED")
        
        # Reset capturer status
        capturer.status = "Normal"
        capturer.carried_unit = None
        
        # Restore capturer's original stats
        self._remove_carrying_penalties(capturer)
        
        logging.info(f"{capturer.name} released {captured_unit.name}")
        return True

    def take_captured_unit(self, taker: UnitState, giver: UnitState) -> bool:
        """
        Allow an adjacent ally to take the captured unit from the current carrier.
        
        Args:
            taker: The unit taking the captive
            giver: The unit currently carrying the captive
            
        Returns:
            True if the transfer was successful, False otherwise
        """
        # Verify giver is carrying a unit
        if giver.status != "Carrying" or giver.carried_unit is None:
            logging.info(f"{giver.name} is not carrying a captured unit")
            return False
        
        # Verify taker is adjacent to giver
        if not self._are_units_adjacent(taker, giver):
            logging.info(f"{taker.name} is not adjacent to {giver.name}")
            return False
        
        # Verify taker is not already carrying someone
        if taker.status == "Carrying" or taker.carried_unit is not None:
            logging.info(f"{taker.name} is already carrying someone")
            return False
        
        # Check if taker can carry the captured unit (Con check)
        captured_unit = giver.carried_unit
        taker_con = taker.stats.get("Con", 0)
        effective_taker_con = 20 if taker.is_mounted else taker_con
        
        if effective_taker_con <= captured_unit.stats.get("Con", 0):
            logging.info(f"{taker.name} cannot carry {captured_unit.name} (Con too low)")
            return False
        
        # Transfer the captured unit
        taker.status = "Carrying"
        taker.carried_unit = captured_unit
        
        # Reset giver status
        giver.status = "Normal"
        giver.carried_unit = None
        
        # Remove penalties from giver
        self._remove_carrying_penalties(giver)
        
        # Apply penalties to taker
        self._apply_carrying_penalties(taker, captured_unit)
        
        logging.info(f"{taker.name} took {captured_unit.name} from {giver.name}")
        return True

    # --- Helper Methods ---

    def _backup_stats(self, unit: UnitState) -> Dict[str, int]:
        """
        Create a backup of a unit's stats.
        
        Args:
            unit: The unit to backup stats for
            
        Returns:
            Dictionary of original stat values
        """
        return {
            "Str": unit.stats["Str"],
            "Mag": unit.stats["Mag"],
            "Skl": unit.stats["Skl"],
            "Spd": unit.stats["Spd"],
            "Def": unit.stats["Def"],
            "Mov": unit.stats["Mov"]
        }

    def _restore_stats(self, unit: UnitState, original_stats: Dict[str, int]) -> None:
        """
        Restore a unit's stats from a backup.
        
        Args:
            unit: The unit to restore stats for
            original_stats: Dictionary of original stat values
        """
        unit.stats["Str"] = original_stats["Str"]
        unit.stats["Mag"] = original_stats["Mag"]
        unit.stats["Skl"] = original_stats["Skl"]
        unit.stats["Spd"] = original_stats["Spd"]
        unit.stats["Def"] = original_stats["Def"]
        unit.stats["Mov"] = original_stats["Mov"]

    def _remove_carrying_penalties(self, unit: UnitState) -> None:
        """
        Remove carrying penalties from a unit.
        
        Args:
            unit: The unit to remove penalties from
        """
        # Restore original stats from base_stats
        # This assumes that base_stats contains the original values
        # In a real implementation, we would store the original values before applying penalties
        unit.stats["Str"] = unit.base_stats["Str"]
        unit.stats["Mag"] = unit.base_stats["Mag"]
        unit.stats["Skl"] = unit.base_stats["Skl"]
        unit.stats["Spd"] = unit.base_stats["Spd"]
        unit.stats["Def"] = unit.base_stats["Def"]
        unit.stats["Mov"] = unit.base_stats["Mov"]

    def _are_units_adjacent(self, unit1: UnitState, unit2: UnitState) -> bool:
        """
        Check if two units are adjacent.
        
        Args:
            unit1: First unit
            unit2: Second unit
            
        Returns:
            True if the units are adjacent, False otherwise
        """
        x1, y1 = unit1.position
        x2, y2 = unit2.position
        
        # Check Manhattan distance
        return abs(x1 - x2) + abs(y1 - y2) == 1