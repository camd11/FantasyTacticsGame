"""
Action System Module

This module manages unit actions during gameplay, including movement, combat, item usage,
and special actions like stealing, capturing, and rescuing. It enforces action rules and
coordinates with other systems to execute actions.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union

from src.core_engine.game_state import GameStateManager, FactionEnum
from src.core_engine.data_provider import DataProvider

class ActionSystem:
    """
    Manages unit actions during gameplay, enforcing action rules and coordinating with other systems.
    """
    
    def __init__(self):
        """Initialize the ActionSystem."""
        self.gameStateManager = None
        self.dataProvider = None
        self.mapSystem = None
        self.inventorySystem = None
        self.combatSystem = None
        self.stealingSystem = None
        self.uiSystem = None
    
    def initialize(self, gameStateManager_instance: GameStateManager, 
                  dataProvider_instance: DataProvider,
                  mapSystem_instance,
                  inventorySystem_instance,
                  combatSystem_instance,
                  stealingSystem_instance=None,
                  uiSystem_instance=None) -> None:
        """
        Initialize the ActionSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
            mapSystem_instance: Instance of the MapSystem
            inventorySystem_instance: Instance of the InventorySystem
            combatSystem_instance: Instance of the CombatSystem
            stealingSystem_instance: Instance of the StealingSystem (optional)
            uiSystem_instance: Instance of the UISystem (optional)
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        self.mapSystem = mapSystem_instance
        self.inventorySystem = inventorySystem_instance
        self.combatSystem = combatSystem_instance
        self.stealingSystem = stealingSystem_instance
        self.uiSystem = uiSystem_instance
        logging.info("ActionSystem initialized.")
    
    def handle_steal_action(self, attacker, defender) -> bool:
        """
        Handle a steal action between two units.
        
        Args:
            attacker: The unit attempting to steal
            defender: The target unit
            
        Returns:
            True if the steal action was successful, False otherwise
        """
        if not self.stealingSystem:
            logging.error("StealingSystem not initialized")
            return False
        
        # Check if steal can be initiated
        if not self.stealingSystem.can_initiate_steal(attacker, defender):
            return False
        
        # Present steal item selection to the player
        selected_item = self.stealingSystem.present_steal_item_selection(attacker, defender)
        if not selected_item:
            return False
        
        # Execute the steal
        success = self.stealingSystem.execute_steal(attacker, defender, selected_item)
        
        # If successful, mark the unit as having acted
        if success:
            attacker.has_acted = True
        
        return success