"""
Support and Leadership System Module

This module implements the Support, Leadership, and Charisma systems from Fire Emblem: Thracia 776.
These systems provide passive combat bonuses to units based on their proximity to allies with
specific relationships or skills.
"""

from typing import Dict, List, Tuple, Optional, Any
from src.core_engine.game_state import DispositionEnum

# Constants
ACTIVE = DispositionEnum.ACTIVE


class SupportLeadershipSystem:
    """
    Manages the Support, Leadership, and Charisma systems.
    
    These systems provide passive combat bonuses to units based on:
    - Support: Predefined relationships between specific character pairs
    - Leadership: Stars that provide global bonuses to all allied units
    - Charisma: A skill that provides bonuses to nearby allied units
    """
    
    def __init__(self):
        """Initialize the SupportLeadershipSystem."""
        self.gameStateManager = None
        self.dataProvider = None
    
    def initialize(self, game_state_manager, data_provider):
        """Initialize with dependencies."""
        self.gameStateManager = game_state_manager
        self.dataProvider = data_provider
    
    def calculate_support_bonus(self, unit_id: str) -> Dict[str, int]:
        """
        Calculate the total support bonus for a given unit based on nearby allies.
        
        Args:
            unit_id: The ID of the unit to calculate bonuses for
            
        Returns:
            A dictionary with bonuses for hit, avoid, crit, and crit_evade
        """
        # Default return value with zero bonuses
        total_bonus = {"hit": 0, "avoid": 0, "crit": 0, "crit_evade": 0}
        
        # Constants
        SUPPORT_RANGE = 3
        MAX_BONUS_PER_STAT = 30
        
        # Get the target unit
        target_unit = self.gameStateManager.get_unit(unit_id)
        if not target_unit:
            return total_bonus
        
        # Get all units and support data
        all_units = self.gameStateManager.get_all_units()
        support_data = self.dataProvider.get_support_data()
        
        # Calculate bonuses from nearby supporting units
        for other_unit in all_units:
            # Skip self
            if other_unit is target_unit:
                continue
                
            # Skip units from different factions
            if other_unit.faction != target_unit.faction:
                continue
                
            # Calculate distance
            distance = self._calculate_distance(target_unit.position, other_unit.position)
            
            # Check if within support range
            if distance <= SUPPORT_RANGE:
                # Check if other_unit supports target_unit
                support_pair_key = (other_unit.unit_id, target_unit.unit_id)
                if support_pair_key in support_data:
                    support_info = support_data[support_pair_key]
                    bonus_value = support_info["bonus"]
                    total_bonus["hit"] += bonus_value
                    total_bonus["avoid"] += bonus_value
                    total_bonus["crit"] += bonus_value
                    total_bonus["crit_evade"] += bonus_value
        
        # Apply caps
        total_bonus["hit"] = min(total_bonus["hit"], MAX_BONUS_PER_STAT)
        total_bonus["avoid"] = min(total_bonus["avoid"], MAX_BONUS_PER_STAT)
        total_bonus["crit"] = min(total_bonus["crit"], MAX_BONUS_PER_STAT)
        total_bonus["crit_evade"] = min(total_bonus["crit_evade"], MAX_BONUS_PER_STAT)
        
        return total_bonus
    
    def calculate_leadership_bonus(self, faction: str) -> Dict[str, int]:
        """
        Calculate the total leadership bonus for a given faction based on deployed leaders.
        
        Args:
            faction: The faction to calculate bonuses for
            
        Returns:
            A dictionary with bonuses for hit and avoid
        """
        # Default return value with zero bonuses
        total_bonus = {"hit": 0, "avoid": 0}
        
        # Get all units for the faction
        units = self.gameStateManager.get_units_by_faction(faction)
        
        # Calculate total leadership stars
        total_stars = 0
        for unit in units:
            if hasattr(unit, 'is_deployed') and unit.is_deployed and unit.disposition == ACTIVE:
                total_stars += unit.leadership_stars
        
        # Calculate bonuses (3% per star)
        bonus_per_star = 3
        total_bonus["hit"] = total_stars * bonus_per_star
        total_bonus["avoid"] = total_stars * bonus_per_star
        
        return total_bonus
    
    def calculate_charisma_bonus(self, unit_id: str) -> Dict[str, int]:
        """
        Calculate the total charisma bonus for a given unit based on nearby allies with the Charisma skill.
        
        Args:
            unit_id: The ID of the unit to calculate bonuses for
            
        Returns:
            A dictionary with bonuses for hit and avoid
        """
        # Default return value with zero bonuses
        total_bonus = {"hit": 0, "avoid": 0}
        
        # Constants
        CHARISMA_RANGE = 3
        CHARISMA_BONUS_PER_UNIT = 10
        
        # Get the target unit
        target_unit = self.gameStateManager.get_unit(unit_id)
        if not target_unit:
            return total_bonus
        
        # Get all units
        all_units = self.gameStateManager.get_all_units()
        
        # Calculate bonuses from nearby units with Charisma
        for other_unit in all_units:
            # Skip self
            if other_unit is target_unit:
                continue
                
            # Skip units from different factions
            if other_unit.faction != target_unit.faction:
                continue
                
            # Check if unit has Charisma skill
            if hasattr(other_unit, 'has_charisma_skill') and other_unit.has_charisma_skill:
                # Calculate distance
                distance = self._calculate_distance(target_unit.position, other_unit.position)
                
                # Check if within Charisma range
                if distance <= CHARISMA_RANGE:
                    total_bonus["hit"] += CHARISMA_BONUS_PER_UNIT
                    total_bonus["avoid"] += CHARISMA_BONUS_PER_UNIT
        
        return total_bonus
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculate the Manhattan distance between two positions.
        
        Args:
            pos1: The first position (x, y)
            pos2: The second position (x, y)
            
        Returns:
            The Manhattan distance between the positions
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])