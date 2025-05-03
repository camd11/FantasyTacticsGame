"""
Input States Module

This module defines the various states for the interactive player input system.
Each state handles specific user interactions and transitions to other states based on input.

The module implements the State pattern, where each state encapsulates behavior specific
to a particular phase of user interaction (unit selection, movement, action selection, etc.).
States are responsible for handling input, updating the game state, and determining the
next state to transition to.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Set


class InputState(ABC):
    """
    Abstract base class for all input states.
    
    Each state handles specific user interactions and transitions to other states based on input.
    This abstract class defines the interface that all concrete state classes must implement,
    ensuring consistent behavior across the state hierarchy.
    
    The state pattern allows for clean separation of input handling logic for different
    game states, making the code more maintainable and extensible.
    """
    
    @abstractmethod
    def handle_input(self, key: str, handler) -> 'InputState':
        """
        Handle user input and return the next state.
        
        Args:
            key: The key pressed by the user
            handler: The InteractiveInputHandler instance
            
        Returns:
            The next state to transition to
        """
        pass
    
    @abstractmethod
    def enter(self, handler) -> None:
        """
        Called when entering this state.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        pass
    
    @abstractmethod
    def exit(self, handler) -> None:
        """
        Called when exiting this state.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        pass


class SelectUnitState(InputState):
    """
    State for selecting a unit to control.
    
    In this state, the player navigates the map cursor to select an available player unit.
    """
    
    def enter(self, handler) -> None:
        """
        Enter the SelectUnitState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Display the map with cursor
        handler.display_system.display_map(cursor_position=handler.cursor_position)
        
        # Display active units
        active_units = handler._get_active_player_units()
        if active_units:
            print("\nSelect a unit to control (use arrow keys to move cursor, Enter to select):")
            handler.display_system.display_active_units(active_units)
        else:
            print("\nNo active units available. Press 'E' to end your turn.")
    
    def handle_input(self, key: str, handler) -> InputState:
        """
        Handle input in the SelectUnitState.
        
        Args:
            key: The key pressed by the user
            handler: The InteractiveInputHandler instance
            
        Returns:
            The next state to transition to
        """
        # Get map dimensions
        map_width, map_height = handler.map_system.get_width(), handler.map_system.get_height()
        
        # Handle cursor movement
        if key == 'KEY_UP' and handler.cursor_position[1] > 0:
            handler.cursor_position = (handler.cursor_position[0], handler.cursor_position[1] - 1)
            return self  # Stay in the same state
        elif key == 'KEY_DOWN' and handler.cursor_position[1] < map_height - 1:
            handler.cursor_position = (handler.cursor_position[0], handler.cursor_position[1] + 1)
            return self  # Stay in the same state
        elif key == 'KEY_LEFT' and handler.cursor_position[0] > 0:
            handler.cursor_position = (handler.cursor_position[0] - 1, handler.cursor_position[1])
            return self  # Stay in the same state
        elif key == 'KEY_RIGHT' and handler.cursor_position[0] < map_width - 1:
            handler.cursor_position = (handler.cursor_position[0] + 1, handler.cursor_position[1])
            return self  # Stay in the same state
        
        # Handle unit selection (Enter/Space)
        elif key in ('KEY_ENTER', ' '):
            # Check if there's a unit at the cursor position
            unit_id = handler._get_unit_at_position(handler.cursor_position)
            
            if unit_id:
                unit = handler.game_state_manager.get_unit(unit_id)
                
                # Check if it's a player unit that hasn't acted and has no disabling status effects
                if (unit.faction == 'PLAYER' and 
                    not unit.has_acted and 
                    not handler._has_disabling_status_effects(unit)):
                    
                    # Select the unit
                    handler.selected_unit_id = unit_id
                    handler.original_position = unit.position  # Store original position for cancellation
                    
                    # Transition to DisplayMovementRangeState
                    return DisplayMovementRangeState()
                else:
                    if unit.has_acted:
                        print("This unit has already acted.")
                    elif handler._has_disabling_status_effects(unit):
                        print(f"This unit cannot act due to status effects: {', '.join(unit.status_effects)}")
                    else:
                        print("You can only control player units.")
            else:
                print("No unit at this position.")
            
            return self  # Stay in the same state
        
        # Handle end turn (E key)
        elif key.lower() == 'e':
            return EndPlayerPhaseState()
        
        # Any other key - stay in the same state
        return self
    
    def exit(self, handler) -> None:
        """
        Exit the SelectUnitState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Nothing specific to do when exiting this state
        pass


class DisplayMovementRangeState(InputState):
    """
    State for displaying and selecting a movement destination.
    
    In this state, the player sees the movement range of the selected unit and chooses a destination.
    """
    
    def enter(self, handler) -> None:
        """
        Enter the DisplayMovementRangeState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Calculate movement range
        handler.movement_range = handler.movement_system.calculate_movement_range(handler.selected_unit_id)
        
        # Display the map with movement range
        handler.display_system.display_movement_range(handler.movement_range, handler.selected_unit_id)
        
        # Display unit details
        handler.display_system.display_unit_details(handler.selected_unit_id)
        
        # Set cursor to unit's position initially
        unit = handler.game_state_manager.get_unit(handler.selected_unit_id)
        handler.cursor_position = unit.position
        
        print("\nSelect a destination (use arrow keys to move cursor, Enter to confirm, Backspace/Esc to cancel):")
    
    def handle_input(self, key: str, handler) -> InputState:
        """
        Handle input in the DisplayMovementRangeState.
        
        Args:
            key: The key pressed by the user
            handler: The InteractiveInputHandler instance
            
        Returns:
            The next state to transition to
        """
        # Get map dimensions
        map_width, map_height = handler.map_system.get_width(), handler.map_system.get_height()
        
        # Handle cursor movement
        if key == 'KEY_UP' and handler.cursor_position[1] > 0:
            new_pos = (handler.cursor_position[0], handler.cursor_position[1] - 1)
            if new_pos in handler.movement_range or new_pos == handler.game_state_manager.get_unit(handler.selected_unit_id).position:
                handler.cursor_position = new_pos
            return self  # Stay in the same state
        elif key == 'KEY_DOWN' and handler.cursor_position[1] < map_height - 1:
            new_pos = (handler.cursor_position[0], handler.cursor_position[1] + 1)
            if new_pos in handler.movement_range or new_pos == handler.game_state_manager.get_unit(handler.selected_unit_id).position:
                handler.cursor_position = new_pos
            return self  # Stay in the same state
        elif key == 'KEY_LEFT' and handler.cursor_position[0] > 0:
            new_pos = (handler.cursor_position[0] - 1, handler.cursor_position[1])
            if new_pos in handler.movement_range or new_pos == handler.game_state_manager.get_unit(handler.selected_unit_id).position:
                handler.cursor_position = new_pos
            return self  # Stay in the same state
        elif key == 'KEY_RIGHT' and handler.cursor_position[0] < map_width - 1:
            new_pos = (handler.cursor_position[0] + 1, handler.cursor_position[1])
            if new_pos in handler.movement_range or new_pos == handler.game_state_manager.get_unit(handler.selected_unit_id).position:
                handler.cursor_position = new_pos
            return self  # Stay in the same state
        
        # Handle destination confirmation (Enter/Space)
        elif key in ('KEY_ENTER', ' '):
            # Check if the cursor is on a valid destination
            if (handler.cursor_position in handler.movement_range or 
                handler.cursor_position == handler.game_state_manager.get_unit(handler.selected_unit_id).position):
                
                # Store the destination
                handler.destination = handler.cursor_position
                
                # Transition to ConfirmMovementState
                return ConfirmMovementState()
            else:
                print("Invalid destination. Please select a tile within the movement range.")
                return self  # Stay in the same state
        
        # Handle cancellation (Backspace/Esc)
        elif key in ('KEY_BACKSPACE', '\x1b'):  # \x1b is the escape key
            # Deselect unit
            handler.selected_unit_id = None
            handler.movement_range = set()
            
            # Transition back to SelectUnitState
            return SelectUnitState()
        
        # Any other key - stay in the same state
        return self
    
    def exit(self, handler) -> None:
        """
        Exit the DisplayMovementRangeState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Nothing specific to do when exiting this state
        pass


class ConfirmMovementState(InputState):
    """
    State for confirming movement and updating unit position.
    
    This is a brief internal state that updates the unit's position and transitions to the action menu.
    """
    
    def enter(self, handler) -> None:
        """
        Enter the ConfirmMovementState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Get the unit
        unit = handler.game_state_manager.get_unit(handler.selected_unit_id)
        
        # Update the unit's position
        if handler.destination != unit.position:  # Only update if actually moving
            unit.position = handler.destination
            
            # Get path for animation (if needed)
            handler.path = handler.map_system.get_path(handler.selected_unit_id, handler.destination)
            
            print(f"Moving {unit.name} to {handler.destination}")
        
        # Immediately transition to DisplayActionMenuState
        # This is done in handle_input
    
    def handle_input(self, key: str, handler) -> InputState:
        """
        Handle input in the ConfirmMovementState.
        
        This state is brief and automatically transitions to DisplayActionMenuState.
        
        Args:
            key: The key pressed by the user
            handler: The InteractiveInputHandler instance
            
        Returns:
            The next state to transition to
        """
        # Automatically transition to DisplayActionMenuState
        return DisplayActionMenuState()
    
    def exit(self, handler) -> None:
        """
        Exit the ConfirmMovementState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Redraw the map with the unit in the new position
        handler.display_system.display_map(selected_unit_id=handler.selected_unit_id, cursor_position=handler.cursor_position)


class DisplayActionMenuState(InputState):
    """
    State for displaying and selecting an action.
    
    In this state, the player selects an action for the unit to perform (Attack, Staff, Item, Wait, etc.).
    """
    
    def enter(self, handler) -> None:
        """
        Enter the DisplayActionMenuState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Determine available actions
        handler.available_actions = handler._get_available_actions()
        
        # Display the map
        handler.display_system.display_map(selected_unit_id=handler.selected_unit_id, cursor_position=handler.cursor_position)
        
        # Display action menu
        handler.display_system.display_action_menu(handler.selected_unit_id, handler.available_actions)
        
        # Initialize selected action index
        handler.selected_action_index = 0
        
        print("\nSelect an action (use arrow keys to navigate, Enter to select, Backspace/Esc to cancel):")
    
    def handle_input(self, key: str, handler) -> InputState:
        """
        Handle input in the DisplayActionMenuState.
        
        Args:
            key: The key pressed by the user
            handler: The InteractiveInputHandler instance
            
        Returns:
            The next state to transition to
        """
        # Handle menu navigation
        if key == 'KEY_UP' and handler.selected_action_index > 0:
            handler.selected_action_index -= 1
            handler.display_system.display_action_menu(handler.selected_unit_id, handler.available_actions)
            return self  # Stay in the same state
        elif key == 'KEY_DOWN' and handler.selected_action_index < len(handler.available_actions) - 1:
            handler.selected_action_index += 1
            handler.display_system.display_action_menu(handler.selected_unit_id, handler.available_actions)
            return self  # Stay in the same state
        
        # Handle action selection (Enter/Space)
        elif key in ('KEY_ENTER', ' '):
            selected_action = handler.available_actions[handler.selected_action_index]
            handler.selected_action = selected_action
            
            # Handle different actions
            if selected_action == 'Wait':
                return ExecuteActionState()  # Wait doesn't need targeting
            elif selected_action == 'Attack':
                # Check if there are valid targets
                targets = handler._get_valid_attack_targets()
                if targets:
                    handler.valid_targets = targets
                    return SelectTargetState()
                else:
                    print("No valid targets in range.")
                    return self  # Stay in the same state
            elif selected_action == 'Staff':
                # Check if there are valid targets
                targets = handler._get_valid_staff_targets()
                if targets:
                    handler.valid_targets = targets
                    return SelectTargetState()
                else:
                    print("No valid targets in range.")
                    return self  # Stay in the same state
            elif selected_action == 'Item':
                # For now, just execute the item action
                # In a full implementation, this might go to an item selection state
                return ExecuteActionState()
            else:
                print(f"Action '{selected_action}' not implemented yet.")
                return self  # Stay in the same state
        
        # Handle action shortcuts
        elif key.lower() == 'a' and 'Attack' in handler.available_actions:
            handler.selected_action = 'Attack'
            targets = handler._get_valid_attack_targets()
            if targets:
                handler.valid_targets = targets
                return SelectTargetState()
            else:
                print("No valid targets in range.")
                return self  # Stay in the same state
        elif key.lower() == 's' and 'Staff' in handler.available_actions:
            handler.selected_action = 'Staff'
            targets = handler._get_valid_staff_targets()
            if targets:
                handler.valid_targets = targets
                return SelectTargetState()
            else:
                print("No valid targets in range.")
                return self  # Stay in the same state
        elif key.lower() == 'i' and 'Item' in handler.available_actions:
            handler.selected_action = 'Item'
            return ExecuteActionState()
        elif key.lower() == 'w' and 'Wait' in handler.available_actions:
            handler.selected_action = 'Wait'
            return ExecuteActionState()
        
        # Handle cancellation (Backspace/Esc)
        elif key in ('KEY_BACKSPACE', '\x1b'):  # \x1b is the escape key
            # Revert unit position to original position
            unit = handler.game_state_manager.get_unit(handler.selected_unit_id)
            unit.position = handler.original_position
            
            # Reset cursor position to original unit position
            handler.cursor_position = handler.original_position
            
            # Transition back to DisplayMovementRangeState
            return DisplayMovementRangeState()
        
        # Any other key - stay in the same state
        return self
    
    def exit(self, handler) -> None:
        """
        Exit the DisplayActionMenuState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Nothing specific to do when exiting this state
        pass


class SelectTargetState(InputState):
    """
    State for selecting a target for an action.
    
    In this state, the player selects a target for actions like Attack or Staff.
    """
    
    def enter(self, handler) -> None:
        """
        Enter the SelectTargetState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Display the map with valid targets
        if handler.selected_action == 'Attack':
            attack_range = handler.map_system.get_attackable_tiles(handler.selected_unit_id)
            handler.display_system.display_attack_range(attack_range, handler.selected_unit_id)
        elif handler.selected_action == 'Staff':
            # For now, just use the same display as attack range
            # In a full implementation, this would use a staff-specific range display
            attack_range = handler.map_system.get_attackable_tiles(handler.selected_unit_id)
            handler.display_system.display_attack_range(attack_range, handler.selected_unit_id)
        
        # Display targets
        handler.display_system.display_targets(handler.valid_targets, handler.selected_action)
        
        # Initialize selected target index
        handler.selected_target_index = 0
        
        # Set cursor to first target's position
        if handler.valid_targets:
            target_unit = handler.game_state_manager.get_unit(handler.valid_targets[0])
            handler.cursor_position = target_unit.position
        
        print(f"\nSelect a target for {handler.selected_action} (use arrow keys to cycle targets, Enter to confirm, Backspace/Esc to cancel):")
    
    def handle_input(self, key: str, handler) -> InputState:
        """
        Handle input in the SelectTargetState.
        
        Args:
            key: The key pressed by the user
            handler: The InteractiveInputHandler instance
            
        Returns:
            The next state to transition to
        """
        # Handle target cycling
        if key in ('KEY_UP', 'KEY_DOWN', 'KEY_LEFT', 'KEY_RIGHT'):
            # Cycle to next target
            if handler.valid_targets:
                handler.selected_target_index = (handler.selected_target_index + 1) % len(handler.valid_targets)
                target_unit = handler.game_state_manager.get_unit(handler.valid_targets[handler.selected_target_index])
                handler.cursor_position = target_unit.position
                
                # Display the map with updated cursor
                if handler.selected_action == 'Attack':
                    attack_range = handler.map_system.get_attackable_tiles(handler.selected_unit_id)
                    handler.display_system.display_attack_range(attack_range, handler.selected_unit_id)
                elif handler.selected_action == 'Staff':
                    attack_range = handler.map_system.get_attackable_tiles(handler.selected_unit_id)
                    handler.display_system.display_attack_range(attack_range, handler.selected_unit_id)
                
                # Display targets with updated selection
                handler.display_system.display_targets(handler.valid_targets, handler.selected_action)
            
            return self  # Stay in the same state
        
        # Handle target confirmation (Enter/Space)
        elif key in ('KEY_ENTER', ' '):
            if handler.valid_targets:
                handler.selected_target_id = handler.valid_targets[handler.selected_target_index]
                
                # If this is an attack, display combat forecast
                if handler.selected_action == 'Attack' and hasattr(handler.display_system, 'combat_system') and handler.display_system.combat_system:
                    handler.display_system.display_combat_forecast(handler.selected_unit_id, handler.selected_target_id)
                    
                    # Ask for confirmation
                    print("\nConfirm attack? (Y/N)")
                    # This would normally wait for input, but for now we'll just proceed
                    # In a real implementation, this would be handled by another state or input prompt
                
                # Transition to ExecuteActionState
                return ExecuteActionState()
            else:
                print("No valid targets available.")
                return self  # Stay in the same state
        
        # Handle cancellation (Backspace/Esc)
        elif key in ('KEY_BACKSPACE', '\x1b'):  # \x1b is the escape key
            # Transition back to DisplayActionMenuState
            return DisplayActionMenuState()
        
        # Any other key - stay in the same state
        return self
    
    def exit(self, handler) -> None:
        """
        Exit the SelectTargetState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Nothing specific to do when exiting this state
        pass


class ExecuteActionState(InputState):
    """
    State for executing the selected action.
    
    This state executes the selected action and transitions to EndUnitTurnState.
    """
    
    def enter(self, handler) -> None:
        """
        Enter the ExecuteActionState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Execute the selected action
        if handler.selected_action == 'Wait':
            print(f"{handler.game_state_manager.get_unit(handler.selected_unit_id).name} waits.")
        elif handler.selected_action == 'Attack':
            attacker = handler.game_state_manager.get_unit(handler.selected_unit_id)
            defender = handler.game_state_manager.get_unit(handler.selected_target_id)
            print(f"{attacker.name} attacks {defender.name}!")
            
            # In a real implementation, this would call the combat system
            # For now, we'll just print a message
        elif handler.selected_action == 'Staff':
            user = handler.game_state_manager.get_unit(handler.selected_unit_id)
            target = handler.game_state_manager.get_unit(handler.selected_target_id)
            print(f"{user.name} uses staff on {target.name}!")
            
            # In a real implementation, this would call the staff effect system
            # For now, we'll just print a message
        elif handler.selected_action == 'Item':
            user = handler.game_state_manager.get_unit(handler.selected_unit_id)
            print(f"{user.name} uses an item!")
            
            # In a real implementation, this would call the item system
            # For now, we'll just print a message
        
        # Immediately transition to EndUnitTurnState
        # This is done in handle_input
    
    def handle_input(self, key: str, handler) -> InputState:
        """
        Handle input in the ExecuteActionState.
        
        This state is brief and automatically transitions to EndUnitTurnState.
        
        Args:
            key: The key pressed by the user
            handler: The InteractiveInputHandler instance
            
        Returns:
            The next state to transition to
        """
        # Automatically transition to EndUnitTurnState
        return EndUnitTurnState()
    
    def exit(self, handler) -> None:
        """
        Exit the ExecuteActionState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Nothing specific to do when exiting this state
        pass


class EndUnitTurnState(InputState):
    """
    State for ending a unit's turn.
    
    This state marks the unit as having acted and transitions back to SelectUnitState.
    """
    
    def enter(self, handler) -> None:
        """
        Enter the EndUnitTurnState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Mark the unit as having acted
        unit = handler.game_state_manager.get_unit(handler.selected_unit_id)
        unit.has_acted = True
        
        print(f"{unit.name} has completed their turn.")
        
        # Check if all player units have acted
        all_acted = True
        for unit in handler._get_player_units():
            if not unit.has_acted and not handler._has_disabling_status_effects(unit):
                all_acted = False
                break
        
        # If all units have acted and auto-end turn is enabled, end the player phase
        if all_acted and handler.auto_end_turn:
            print("All units have acted. Ending player phase.")
            handler.selected_unit_id = None
            return EndPlayerPhaseState()
        
        # Reset selected unit and action
        handler.selected_unit_id = None
        handler.selected_action = None
        handler.selected_target_id = None
        
        # Immediately transition to SelectUnitState
        # This is done in handle_input
    
    def handle_input(self, key: str, handler) -> InputState:
        """
        Handle input in the EndUnitTurnState.
        
        This state is brief and automatically transitions to SelectUnitState.
        
        Args:
            key: The key pressed by the user
            handler: The InteractiveInputHandler instance
            
        Returns:
            The next state to transition to
        """
        # Automatically transition to SelectUnitState
        return SelectUnitState()
    
    def exit(self, handler) -> None:
        """
        Exit the EndUnitTurnState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Redraw the map
        handler.display_system.display_map(cursor_position=handler.cursor_position)


class EndPlayerPhaseState(InputState):
    """
    State for ending the player phase.
    
    This state signals the game to transition to the next phase.
    """
    
    def enter(self, handler) -> None:
        """
        Enter the EndPlayerPhaseState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        print("Ending player phase...")
        
        # Signal the game to end the current phase
        handler.game_state_manager.end_current_phase()
        
        # Reset all state variables
        handler.selected_unit_id = None
        handler.selected_action = None
        handler.selected_target_id = None
        handler.movement_range = set()
        
        # In a real implementation, this would transition to the next phase
        # For now, we'll just print a message
        print("Player phase ended.")
    
    def handle_input(self, key: str, handler) -> InputState:
        """
        Handle input in the EndPlayerPhaseState.
        
        This state doesn't handle any input as it's the end of the player's turn.
        
        Args:
            key: The key pressed by the user
            handler: The InteractiveInputHandler instance
            
        Returns:
            The next state to transition to
        """
        # This state doesn't transition based on input
        # In a real implementation, control would return to the main game loop
        return self
    
    def exit(self, handler) -> None:
        """
        Exit the EndPlayerPhaseState.
        
        Args:
            handler: The InteractiveInputHandler instance
        """
        # Nothing specific to do when exiting this state
        pass