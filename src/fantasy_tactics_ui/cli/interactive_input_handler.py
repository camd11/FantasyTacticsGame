"""
Interactive Input Handler Module

This module provides an interactive input handler for player actions in the game.
It uses a state-based approach to handle different stages of player input, such as
unit selection, movement, action selection, and targeting. The handler manages
transitions between states based on user input and maintains the current game context.

The state pattern implemented here allows for clean separation of input handling logic
for different game states, making the code more maintainable and extensible.
"""

import logging
import platform
from typing import Dict, List, Tuple, Optional, Any, Set

# Conditionally import curses
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False

from src.fantasy_tactics_ui.input_states import (
    InputState, SelectUnitState, DisplayMovementRangeState, ConfirmMovementState,
    DisplayActionMenuState, SelectTargetState, ExecuteActionState,
    EndUnitTurnState, EndPlayerPhaseState
)


class InteractiveInputHandler:
    """
    An interactive input handler for player actions in the game.
    
    This class handles user input for unit selection, movement, combat, and other actions
    using a state-based approach. It manages the current state and transitions between states
    based on user input.
    
    The handler maintains the game context (cursor position, selected unit, available actions, etc.)
    and delegates the actual input handling to the current state object. Each state implements
    specific behavior for handling input in that state and determines the next state to transition to.
    
    The class supports both curses-based terminal UI and a simpler input-based interface for
    systems without curses support.
    """
    
    def __init__(self, auto_end_turn=False):
        """
        Initialize the InteractiveInputHandler.
        
        Args:
            auto_end_turn: Whether to automatically end the turn when all units have acted
        """
        self.game_state_manager = None
        self.unit_system = None
        self.movement_system = None
        self.map_system = None
        self.action_system = None
        self.targeting_system = None
        self.display_system = None
        
        self.auto_end_turn = auto_end_turn
        
        # State variables
        self.current_state = None
        self.cursor_position = (0, 0)
        self.selected_unit_id = None
        self.original_position = None
        self.destination = None
        self.path = None
        self.movement_range = set()
        self.available_actions = []
        self.selected_action = None
        self.selected_action_index = 0
        self.valid_targets = []
        self.selected_target_id = None
        self.selected_target_index = 0
        
        logging.info("InteractiveInputHandler initialized.")
    
    def initialize(self, game_state_manager, unit_system, movement_system, map_system,
                  action_system, targeting_system, display_system):
        """
        Initialize the InteractiveInputHandler with the necessary dependencies.
        
        Args:
            game_state_manager: Instance of the GameStateManager
            unit_system: Instance of the UnitSystem
            movement_system: Instance of the MovementSystem
            map_system: Instance of the MapSystem
            action_system: Instance of the ActionSystem
            targeting_system: Instance of the TargetingSystem
            display_system: Instance of the DisplaySystem
        """
        self.game_state_manager = game_state_manager
        self.unit_system = unit_system
        self.movement_system = movement_system
        self.map_system = map_system
        self.action_system = action_system
        self.targeting_system = targeting_system
        self.display_system = display_system
        
        # Set initial state
        self.current_state = SelectUnitState()
        
        logging.info("InteractiveInputHandler dependencies initialized.")
    
    def start_player_phase(self):
        """
        Start the player phase.
        
        This method initializes the player phase by resetting unit action status
        and entering the initial state.
        """
        # Reset all player units to not having acted
        for unit in self._get_player_units():
            unit.has_acted = False
        
        # Set initial cursor position to the first player unit
        player_units = self._get_player_units()
        if player_units:
            self.cursor_position = player_units[0].position
        
        # Enter the initial state
        self.current_state = SelectUnitState()
        self.current_state.enter(self)
        
        logging.info("Player phase started.")
    
    def handle_input(self, key: str) -> bool:
        """
        Handle user input based on the current state.
        
        Args:
            key: The key pressed by the user
            
        Returns:
            True if the player phase is still active, False if it has ended
        """
        if not self.current_state:
            logging.error("No current state set.")
            return False
        
        # Handle input in the current state
        next_state = self.current_state.handle_input(key, self)
        
        # If the state has changed, exit the current state and enter the new one
        if next_state is not self.current_state:
            self.current_state.exit(self)
            self.current_state = next_state
            self.current_state.enter(self)
        
        # Check if we've reached the end of the player phase
        if isinstance(self.current_state, EndPlayerPhaseState):
            return False
        
        return True
    
    def run_interactive_mode(self):
        """
        Run the interactive input handler in a terminal UI.
        
        This method sets up a terminal interface and handles keyboard input until the player phase ends.
        If curses is available, it uses that for advanced terminal control.
        Otherwise, it falls back to a simple input-based interface.
        """
        if CURSES_AVAILABLE:
            self._run_with_curses()
        else:
            self._run_with_input()
    
    def _run_with_curses(self):
        """
        Run the interactive input handler using curses for terminal control.
        """
        # Initialize curses
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        
        try:
            # Start the player phase
            self.start_player_phase()
            
            # Main input loop
            player_phase_active = True
            while player_phase_active:
                # Get user input
                key = stdscr.getkey()
                
                # Handle input
                player_phase_active = self.handle_input(key)
        finally:
            # Clean up curses
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()
    
    def _run_with_input(self):
        """
        Run the interactive input handler using simple input for terminal control.
        This is a fallback for systems without curses support.
        """
        # Start the player phase
        self.start_player_phase()
        
        # Main input loop
        player_phase_active = True
        while player_phase_active:
            # Display prompt
            print("\nEnter command (arrow keys as UP/DOWN/LEFT/RIGHT, Enter as ENTER, Esc as ESC, Space as SPACE):")
            key = input("> ").strip().upper()
            
            # Convert input to key codes
            if key == "UP":
                key = "KEY_UP"
            elif key == "DOWN":
                key = "KEY_DOWN"
            elif key == "LEFT":
                key = "KEY_LEFT"
            elif key == "RIGHT":
                key = "KEY_RIGHT"
            elif key == "ENTER":
                key = "KEY_ENTER"
            elif key == "ESC":
                key = "\x1b"  # Escape key
            elif key == "SPACE":
                key = " "
            elif key == "BACKSPACE":
                key = "KEY_BACKSPACE"
            
            # Handle input
            player_phase_active = self.handle_input(key)
    
    # --- Helper Methods ---
    
    def _get_player_units(self) -> List:
        """
        Get all player units.
        
        This helper method retrieves all units belonging to the player faction,
        regardless of whether they have acted or have disabling status effects.
        
        Returns:
            List of player units
        """
        return self.game_state_manager.get_units_by_faction('PLAYER')
    
    def _get_active_player_units(self) -> List:
        """
        Get active player units that haven't acted yet.
        
        This helper method filters player units to only include those that:
        1. Haven't acted in the current turn
        2. Don't have disabling status effects (like SLEEP or STONE)
        
        These are the units that the player can control in the current phase.
        
        Returns:
            List of active player units
        """
        player_units = self._get_player_units()
        return [unit for unit in player_units if not unit.has_acted and not self._has_disabling_status_effects(unit)]
    
    def _get_unit_at_position(self, position: Tuple[int, int]) -> Optional[str]:
        """
        Get the ID of the unit at a position.
        
        This helper method checks if there is a unit at the specified map coordinates.
        It's used for unit selection when the player clicks on a tile or moves the cursor.
        
        Args:
            position: Position (x, y) on the map
            
        Returns:
            Unit ID or None if no unit is present at the specified position
        """
        for unit_id, unit in self.game_state_manager.current_game_state.unit_states.items():
            if unit.position == position:
                return unit_id
        return None
    
    def _has_disabling_status_effects(self, unit) -> bool:
        """
        Check if a unit has status effects that prevent it from acting.
        
        This helper method determines if a unit is affected by status effects
        that prevent it from taking actions, such as SLEEP or STONE. Units with
        these effects cannot be selected or controlled by the player.
        
        Args:
            unit: The unit to check
            
        Returns:
            True if the unit has disabling status effects, False otherwise
        """
        if not hasattr(unit, 'status_effects'):
            return False
        
        disabling_effects = ['SLEEP', 'STONE']
        return any(effect in disabling_effects for effect in unit.status_effects)
    
    def _get_available_actions(self) -> List[str]:
        """
        Get available actions for the selected unit.
        
        This helper method determines what actions the currently selected unit
        can perform based on its position, equipment, and status. It queries
        the action system if available, or falls back to a default set of actions.
        
        The returned actions are displayed in the action menu for the player to choose from.
        
        Returns:
            List of available action names (e.g., "Wait", "Attack", "Staff", "Item")
        """
        if not self.selected_unit_id:
            return []
        
        # Get available actions from the action system
        if self.action_system:
            return self.action_system.get_available_actions(self.selected_unit_id)
        
        # Fallback if action system is not available
        return ["Wait", "Attack", "Staff", "Item"]
    
    def _get_valid_attack_targets(self) -> List[str]:
        """
        Get valid attack targets for the selected unit.
        
        This helper method determines which enemy units the currently selected unit
        can attack based on its position, weapon range, and other factors. It queries
        the targeting system if available, or falls back to the map system to find
        units within attack range.
        
        Returns:
            List of valid target unit IDs that can be attacked by the selected unit
        """
        if not self.selected_unit_id:
            return []
        
        # Get valid targets from the targeting system
        if self.targeting_system:
            return self.targeting_system.get_valid_targets(self.selected_unit_id)
        
        # Fallback if targeting system is not available
        return self.map_system.get_units_in_attack_range(self.selected_unit_id)
    
    def _get_valid_staff_targets(self) -> List[str]:
        """
        Get valid staff targets for the selected unit.
        
        This helper method determines which units the currently selected unit
        can target with a staff (healing item or special ability) based on its
        position, staff range, and other factors. It queries the targeting system
        if available, or falls back to an empty list if no targeting system is provided.
        
        Staff targets are typically allies for healing staves or enemies for offensive staves.
        
        Returns:
            List of valid target unit IDs that can be targeted with the selected unit's staff
        """
        if not self.selected_unit_id:
            return []
        
        # Get valid targets from the targeting system
        if self.targeting_system:
            return self.targeting_system.get_valid_staff_targets(self.selected_unit_id)
        
        # Fallback if targeting system is not available
        # For now, just return an empty list
        return []