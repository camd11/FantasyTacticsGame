"""
Fatigue System Module

This module is responsible for managing unit fatigue across chapters, forcing players to rotate their army members.
Units accumulate fatigue points based on their actions during a chapter. If a unit's fatigue meets or exceeds their
maximum HP, they become fatigued and cannot be deployed in the subsequent chapter unless a special item is used.
"""

import logging
from typing import List, Optional, Dict


class FatigueManager:
    """
    Manages the fatigue system for units across chapters.
    
    The fatigue system tracks unit stamina, requiring players to rotate their roster.
    Units accumulate fatigue during chapters, and if it exceeds their max HP,
    they cannot be deployed in the next chapter (except the Lord).
    """
    
    # Constants
    # Note: This value is arbitrary and will be finalized when the actual game is developed
    FATIGUE_START_CHAPTER = 8
    FATIGUE_PER_COMBAT = 1
    FATIGUE_PER_STEAL = 1
    FATIGUE_PER_DANCE = 1
    FATIGUE_STAFF_COST = {
        'E': 1,
        'D': 2,
        'C': 3,
        'B': 4,
        'A': 5,
        '*': 5  # Assuming '*' rank staves cost the same as A
    }
    LORD_UNIT_ID = "Leif"  # Example ID for the Lord
    
    def __init__(self):
        """Initialize the FatigueManager."""
        self.game_state_manager = None
        self.data_provider = None
        self.inventory_manager = None
    
    def initialize(self, game_state_manager, data_provider, inventory_manager):
        """Initialize with required dependencies."""
        self.game_state_manager = game_state_manager
        self.data_provider = data_provider
        self.inventory_manager = inventory_manager
        logging.info("FatigueManager initialized")
    
    def increment_fatigue(self, unit, action_type, staff_rank=None):
        """
        Increment a unit's fatigue based on the action performed.
        
        Args:
            unit: The unit performing the action
            action_type: Type of action (COMBAT, STAFF, STEAL, DANCE)
            staff_rank: Rank of staff used (only for STAFF actions)
        """
        # Fatigue system not active yet
        if self.game_state_manager.current_game_state.current_chapter < self.FATIGUE_START_CHAPTER:
            return
        
        fatigue_increase = 0
        
        if action_type == "COMBAT":
            fatigue_increase = self.FATIGUE_PER_COMBAT
        elif action_type == "STAFF":
            if staff_rank is not None and staff_rank in self.FATIGUE_STAFF_COST:
                fatigue_increase = self.FATIGUE_STAFF_COST[staff_rank]
            else:
                # Default to 1 if rank is missing/invalid
                fatigue_increase = 1
                logging.warning(f"Invalid staff rank: {staff_rank}, using default fatigue cost")
        elif action_type == "STEAL":
            fatigue_increase = self.FATIGUE_PER_STEAL
        elif action_type == "DANCE":
            fatigue_increase = self.FATIGUE_PER_DANCE
        
        unit.current_fatigue += fatigue_increase
    
    def check_and_set_fatigue_status_post_chapter(self, all_player_units):
        """
        Check and set fatigue status for all player units at the end of a chapter.
        
        Args:
            all_player_units: List of all player units
        """
        # Ensure all units are marked as not fatigued if before Chapter 8
        if self.game_state_manager.current_game_state.current_chapter < self.FATIGUE_START_CHAPTER:
            for unit in all_player_units:
                unit.is_fatigued = False
            return
        
        for unit in all_player_units:
            # Lord exemption: Leif never becomes 'is_fatigued' for deployment purposes
            if unit.id == self.LORD_UNIT_ID:
                unit.is_fatigued = False
            else:
                # Check if fatigue meets or exceeds max HP
                if unit.current_fatigue >= unit.max_hp:
                    unit.is_fatigued = True
                else:
                    unit.is_fatigued = False
            
            # Reset the current chapter fatigue counter for the next map/prep screen
            # The 'is_fatigued' flag persists until cleared
            unit.current_fatigue = 0
    
    def reset_fatigue_for_unit(self, unit):
        """
        Reset fatigue for a unit (when they sit out a chapter or use an S-Drink).
        
        Args:
            unit: The unit to reset fatigue for
        """
        unit.current_fatigue = 0
        unit.is_fatigued = False
    
    def handle_deployment_fatigue(self, deployed_units, benched_units):
        """
        Handle fatigue at the start of a new chapter deployment.
        
        Args:
            deployed_units: List of units being deployed
            benched_units: List of units being benched
        """
        # Reset fatigue for units who were benched (sat out)
        for unit in benched_units:
            self.reset_fatigue_for_unit(unit)
        
        # Deployed units retain their 'is_fatigued' status
        # Their 'current_fatigue' is already 0, ready for the new chapter
    
    def can_deploy_unit(self, unit):
        """
        Check if a unit can be deployed based on fatigue status.
        
        Args:
            unit: The unit to check
            
        Returns:
            bool: True if the unit can be deployed, False otherwise
        """
        # Fatigue not enforced yet
        if self.game_state_manager.current_game_state.current_chapter < self.FATIGUE_START_CHAPTER:
            return True
        
        # Lord can always deploy
        if unit.id == self.LORD_UNIT_ID:
            return True
        
        # Other units can deploy if not fatigued
        return not unit.is_fatigued
    
    def use_stamina_drink(self, unit):
        """
        Use a Stamina Drink to reset a unit's fatigue.
        
        Args:
            unit: The unit using the S-Drink
        """
        self.reset_fatigue_for_unit(unit)
        # Consume the S-Drink item from inventory
        self.inventory_manager.remove_item(unit, "S-Drink", 1)
