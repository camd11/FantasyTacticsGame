"""
Interactive Input Module

This module provides the main entry point for the interactive player input system.
It integrates the InteractiveInputHandler with the game's main loop and systems,
serving as a bridge between the game engine and the player's input handling.
The module abstracts the complexity of state management and input processing,
providing a clean interface for the game to interact with.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any

from src.ui.interactive_input_handler import InteractiveInputHandler


class InteractiveInput:
    """
    Main class for the interactive player input system.
    
    This class serves as an adapter between the game's main loop and the InteractiveInputHandler.
    It provides methods for initializing the input system, handling player turns, and processing input.
    
    The InteractiveInput class encapsulates the state-based input handling logic and provides
    a simplified interface for the game engine to manage player interactions. It handles the
    initialization of dependencies, manages player turns, and processes individual inputs,
    while delegating the actual input handling to the InteractiveInputHandler.
    """
    
    def __init__(self, auto_end_turn=False):
        """
        Initialize the InteractiveInput.
        
        Args:
            auto_end_turn: Whether to automatically end the turn when all units have acted
        """
        self.handler = InteractiveInputHandler(auto_end_turn=auto_end_turn)
        self.initialized = False
        logging.info("InteractiveInput initialized.")
    
    def initialize(self, game_state_manager, unit_system, movement_system, map_system,
                  action_system, targeting_system, display_system):
        """
        Initialize the InteractiveInput with the necessary dependencies.
        
        Args:
            game_state_manager: Instance of the GameStateManager
            unit_system: Instance of the UnitSystem
            movement_system: Instance of the MovementSystem
            map_system: Instance of the MapSystem
            action_system: Instance of the ActionSystem
            targeting_system: Instance of the TargetingSystem
            display_system: Instance of the DisplaySystem
        """
        self.handler.initialize(
            game_state_manager=game_state_manager,
            unit_system=unit_system,
            movement_system=movement_system,
            map_system=map_system,
            action_system=action_system,
            targeting_system=targeting_system,
            display_system=display_system
        )
        self.initialized = True
        logging.info("InteractiveInput dependencies initialized.")
    
    def handle_player_turn(self) -> Dict[str, Any]:
        """
        Handle the player's turn using the interactive input system.
        
        This method starts the player phase and runs the interactive input handler
        until the player phase ends.
        
        Returns:
            Dict containing the result of the player's turn
        """
        if not self.initialized:
            logging.error("InteractiveInput not initialized.")
            return {'type': 'ERROR', 'message': 'InteractiveInput not initialized'}
        
        try:
            # Start the player phase
            self.handler.start_player_phase()
            
            # Run the interactive input handler
            self.handler.run_interactive_mode()
            
            # Return success
            return {'type': 'END_TURN', 'message': 'Player phase completed'}
        except Exception as e:
            logging.error(f"Error in handle_player_turn: {e}")
            return {'type': 'ERROR', 'message': str(e)}
    
    def process_input(self, key: str) -> Dict[str, Any]:
        """
        Process a single input key.
        
        This method is useful for testing or when integrating with a custom input loop.
        
        Args:
            key: The key pressed by the user
            
        Returns:
            Dict containing the result of processing the input
        """
        if not self.initialized:
            logging.error("InteractiveInput not initialized.")
            return {'type': 'ERROR', 'message': 'InteractiveInput not initialized'}
        
        try:
            # Handle the input
            player_phase_active = self.handler.handle_input(key)
            
            if player_phase_active:
                return {'type': 'CONTINUE', 'message': 'Player phase continuing'}
            else:
                return {'type': 'END_TURN', 'message': 'Player phase completed'}
        except Exception as e:
            logging.error(f"Error in process_input: {e}")
            return {'type': 'ERROR', 'message': str(e)}
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current state of the interactive input system.
        
        This method is useful for testing or debugging.
        
        Returns:
            Dict containing the current state information
        """
        if not self.initialized:
            logging.error("InteractiveInput not initialized.")
            return {'type': 'ERROR', 'message': 'InteractiveInput not initialized'}
        
        return {
            'current_state': self.handler.current_state.__class__.__name__,
            'cursor_position': self.handler.cursor_position,
            'selected_unit_id': self.handler.selected_unit_id,
            'selected_action': self.handler.selected_action,
            'selected_target_id': self.handler.selected_target_id
        }