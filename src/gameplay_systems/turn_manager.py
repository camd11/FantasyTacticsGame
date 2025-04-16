"""
Turn Manager Module (Gameplay Systems)

This module manages the turn-based flow of the game at the gameplay level,
handling phase transitions, turn counting, and coordinating with the core engine.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Set, Union

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.core_engine.turn_manager import TurnManager as CoreTurnManager

class TurnManager:
    """
    Manages the turn-based flow of the game at the gameplay level.
    This class wraps the core engine's TurnManager and provides additional
    gameplay-specific functionality.
    """
    
    def __init__(self):
        """Initialize the TurnManager."""
        self.core_turn_manager = None
        self.gameStateManager = None
        self.statusEffectManager = None
        self.actionSystem = None
        self.berserkTurnLogic = None
    
    def initialize(self, core_turn_manager: CoreTurnManager,
                  gameStateManager_instance: GameStateManager,
                  statusEffectManager_instance=None,
                  actionSystem_instance=None,
                  berserkTurnLogic_instance=None):
        """
        Initialize the TurnManager with the necessary dependencies.
        
        Args:
            core_turn_manager: Instance of the core engine's TurnManager
            gameStateManager_instance: Instance of the GameStateManager
            statusEffectManager_instance: Instance of the StatusEffectManager (optional)
            actionSystem_instance: Instance of the ActionSystem (optional)
            berserkTurnLogic_instance: Instance of the BerserkTurnLogic (optional)
        """
        self.core_turn_manager = core_turn_manager
        self.gameStateManager = gameStateManager_instance
        self.statusEffectManager = statusEffectManager_instance
        self.actionSystem = actionSystem_instance
        self.berserkTurnLogic = berserkTurnLogic_instance
        logging.info("Gameplay TurnManager initialized.")
    
    def start_player_phase(self) -> bool:
        """
        Start the player phase.
        
        Returns:
            True if the phase started successfully, False otherwise
        """
        # Reset all player units
        if self.gameStateManager and self.gameStateManager.current_game_state:
            for unit_id, unit in self.gameStateManager.current_game_state.unit_states.items():
                if unit.faction == FactionEnum.PLAYER:
                    unit.has_acted_this_turn = False
                    unit.was_refreshed_this_turn = False
        
        # Delegate to core turn manager if available
        if self.core_turn_manager:
            return self.core_turn_manager.start_phase(self.core_turn_manager.get_phase_for_faction(FactionEnum.PLAYER))
        
        return True
    
    def has_action_preventing_status(self, unit_id: str) -> bool:
        """
        Check if a unit has a status effect that prevents actions.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit has an action-preventing status, False otherwise
        """
        if not self.statusEffectManager:
            return False
        
        return self.statusEffectManager.has_action_preventing_status(unit_id)
        
    def process_unit_turn(self, unit_id: str) -> bool:
        """
        Process a unit's turn based on its status and faction.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the turn was processed successfully, False otherwise
        """
        # Check if unit exists
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            logging.error(f"TurnManager: Unit {unit_id} not found")
            return False
        
        # Check for status effects that override normal turn processing
        if self.statusEffectManager:
            ai_override = self.statusEffectManager.get_ai_override(unit_id)
            
            if ai_override == "BERSERK_AI" and self.berserkTurnLogic:
                # Process berserk turn
                logging.info(f"TurnManager: Processing berserk turn for unit {unit_id}")
                return self.berserkTurnLogic.execute_berserk_turn(unit_id)
            elif ai_override == "NO_ACTION_AI":
                # Unit cannot act due to status effect (Sleep, Petrify, etc.)
                logging.info(f"TurnManager: Unit {unit_id} cannot act due to status effect")
                if self.actionSystem:
                    self.actionSystem.mark_unit_action_complete(unit_id)
                return True
        
        # Process normal turn based on faction
        if unit.faction == FactionEnum.PLAYER:
            # Player units are controlled by the player, so we don't do anything here
            # The player will control the unit through the UI
            return True
        else:
            # AI-controlled units (Enemy, NPC)
            # This would normally call the AI system to process the turn
            # For now, just mark the unit as having acted
            if self.actionSystem:
                self.actionSystem.mark_unit_action_complete(unit_id)
            return True