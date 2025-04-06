"""
Command Line Input Handler Module

This module provides a command-line input handler for player actions in the game.
It handles user input for unit selection, movement, combat, and other actions.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Set


class CommandLineInputHandler:
    """
    A command-line input handler for player actions in the game.
    This class handles user input for unit selection, movement, combat, and other actions.
    """
    
    def __init__(self, interactive=True):
        """
        Initialize the CommandLineInputHandler.
        
        Args:
            interactive: Whether to enable interactive prompts for user input
        """
        self.game_state_manager = None
        self.unit_system = None
        self.movement_system = None
        self.map_system = None
        self.inventory_system = None
        self.data_provider = None
        self.interactive = interactive
        
    def initialize(self, game_state_manager, unit_system, movement_system, map_system, 
                  inventory_system, data_provider):
        """
        Initialize the CliInputHandler with the necessary dependencies.
        
        Args:
            game_state_manager: Instance of the GameStateManager
            unit_system: Instance of the UnitSystem
            movement_system: Instance of the MovementSystem
            map_system: Instance of the MapSystem
            inventory_system: Instance of the InventorySystem
            data_provider: Instance of the DataProvider
        """
        self.game_state_manager = game_state_manager
        self.unit_system = unit_system
        self.movement_system = movement_system
        self.map_system = map_system
        self.inventory_system = inventory_system
        self.data_provider = data_provider
        logging.info("CliInputHandler initialized.")
    
    def get_input(self) -> Dict[str, Any]:
        """
        Get player input for the current turn.
        
        This method displays the current turn and phase, lists active units,
        and prompts the user to select a unit or end the turn. It then handles
        the selected action and returns a structured response.
        
        Returns:
            Dict containing the input type and any associated data
        """
        # Display current turn and phase
        self._display_turn_info()
        
        # Get active player units that haven't acted yet
        active_units = self._get_active_player_units()
        
        if not active_units:
            print("No active units available. You must end your turn.")
            return {'type': 'END_TURN'}
        
        # Display active units
        self._display_active_units(active_units)
        
        # Prompt for unit selection or end turn
        choice = input("\nSelect a unit number, or 'end' to end turn: ").strip().lower()
        
        if choice == 'end':
            return {'type': 'END_TURN'}
        
        try:
            unit_index = int(choice) - 1  # Convert to 0-based index
            if unit_index < 0 or unit_index >= len(active_units):
                print("Invalid unit selection. Please try again.")
                return self.get_input()
                
            selected_unit_id = active_units[unit_index].id
            return self._handle_unit_actions(selected_unit_id)
            
        except ValueError:
            print("Invalid input. Please enter a number or 'end'.")
            return self.get_input()
    
    def _handle_unit_actions(self, unit_id: str) -> Dict[str, Any]:
        """
        Handle actions for a selected unit.
        
        Args:
            unit_id: ID of the selected unit
            
        Returns:
            Dict containing the action data
        """
        unit = self.game_state_manager.get_unit(unit_id)
        
        # Display unit details
        self._display_unit_details(unit_id)
        
        # Calculate and display movement range
        movement_range = self.movement_system.calculate_movement_range(unit_id)
        self._display_movement_range(movement_range)
        
        # Prompt for action
        print("\nAvailable actions:")
        print("1. Move")
        print("2. Wait")
        print("3. Attack")
        print("4. Item")
        print("5. Capture")
        print("6. Trade")
        print("7. Visit")
        print("8. Seize")
        print("9. Back (select another unit)")
        
        action_choice = input("Select an action (1-9): ").strip()
        
        if action_choice == '9':
            return self.get_input()
        
        # Handle different actions
        if action_choice == '1':  # Move
            return self._handle_move_action(unit_id, movement_range)
        elif action_choice == '2':  # Wait
            return {'type': 'WAIT', 'unit_id': unit_id}
        elif action_choice == '3':  # Attack
            return self._handle_attack_action(unit_id)
        elif action_choice == '4':  # Item
            return self._handle_item_action(unit_id)
        elif action_choice == '5':  # Capture
            return self._handle_capture_action(unit_id)
        elif action_choice == '6':  # Trade
            result = self._handle_trade_action(unit_id)
            if result['type'] == 'TRADE':
                # Trade is free, so continue with unit actions
                print("\nTrade complete. What would you like to do next?")
                return self._handle_unit_actions(unit_id)
            return result
        elif action_choice == '7':  # Visit
            return self._handle_visit_action(unit_id)
        elif action_choice == '8':  # Seize
            return self._handle_seize_action(unit_id)
        else:
            print("Invalid action. Please try again.")
            return self._handle_unit_actions(unit_id)
    
    def _handle_move_action(self, unit_id: str, movement_range: Set[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Handle the Move action for a unit.
        
        Args:
            unit_id: ID of the unit
            movement_range: Set of positions the unit can move to
            
        Returns:
            Dict containing the move action data
        """
        unit = self.game_state_manager.get_unit(unit_id)
        current_pos = unit.position
        
        print(f"\nCurrent position: {current_pos}")
        print("Enter target coordinates (x,y) or 'cancel':")
        
        target_input = input().strip().lower()
        if target_input == 'cancel':
            return self._handle_unit_actions(unit_id)
        
        try:
            x, y = map(int, target_input.split(','))
            target_pos = (x, y)
            
            # Validate destination
            if not self.movement_system.is_valid_destination(unit_id, target_pos):
                print("Invalid destination. Please try again.")
                return self._handle_move_action(unit_id, movement_range)
            
            # Get path
            path = self.map_system.get_path(unit_id, target_pos)
            if not path:
                print("Cannot find path to destination. Please try again.")
                return self._handle_move_action(unit_id, movement_range)
            
            # Execute move
            print(f"Moving to {target_pos} along path: {path}")
            
            # After moving, prompt for another action
            print("\nAfter moving, what would you like to do?")
            print("1. Wait")
            print("2. Attack")
            print("3. Item")
            print("4. Capture")
            print("5. Trade")
            print("6. Visit")
            print("7. Seize")
            
            post_move_action = input("Select an action (1-7): ").strip()
            
            # Create the move action data
            move_action = {
                'type': 'MOVE', 
                'unit_id': unit_id, 
                'path': path
            }
            
            # Handle post-move action
            if post_move_action == '1':  # Wait
                return {
                    'type': 'MOVE_AND_WAIT',
                    'unit_id': unit_id,
                    'move_data': move_action,
                    'action_data': {'type': 'WAIT'}
                }
            elif post_move_action == '2':  # Attack
                attack_data = self._handle_attack_action(unit_id, after_move=True)
                if attack_data['type'] == 'ATTACK':
                    return {
                        'type': 'MOVE_AND_ATTACK',
                        'unit_id': unit_id,
                        'move_data': move_action,
                        'action_data': attack_data
                    }
                return attack_data
            elif post_move_action == '3':  # Item
                item_data = self._handle_item_action(unit_id, after_move=True)
                if item_data['type'] == 'ITEM':
                    return {
                        'type': 'MOVE_AND_ITEM',
                        'unit_id': unit_id,
                        'move_data': move_action,
                        'action_data': item_data
                    }
                return item_data
            elif post_move_action == '4':  # Capture
                capture_data = self._handle_capture_action(unit_id, after_move=True)
                if capture_data['type'] == 'CAPTURE':
                    return {
                        'type': 'MOVE_AND_CAPTURE',
                        'unit_id': unit_id,
                        'move_data': move_action,
                        'action_data': capture_data
                    }
                return capture_data
            elif post_move_action == '5':  # Trade
                trade_data = self._handle_trade_action(unit_id, after_move=True)
                if trade_data['type'] == 'TRADE':
                    # Trade is free, so continue with unit actions
                    print("\nTrade complete. What would you like to do next?")
                    # First execute the move, then handle further actions
                    return {
                        'type': 'MOVE_AND_TRADE',
                        'unit_id': unit_id,
                        'move_data': move_action,
                        'action_data': trade_data,
                        'continue': True  # Signal that more actions can be taken
                    }
                return trade_data
            elif post_move_action == '6':  # Visit
                visit_data = self._handle_visit_action(unit_id, after_move=True)
                if visit_data['type'] == 'VISIT':
                    return {
                        'type': 'MOVE_AND_VISIT',
                        'unit_id': unit_id,
                        'move_data': move_action,
                        'action_data': visit_data
                    }
                return visit_data
            elif post_move_action == '7':  # Seize
                seize_data = self._handle_seize_action(unit_id, after_move=True)
                if seize_data['type'] == 'SEIZE':
                    return {
                        'type': 'MOVE_AND_SEIZE',
                        'unit_id': unit_id,
                        'move_data': move_action,
                        'action_data': seize_data
                    }
                return seize_data
            else:
                print("Invalid action. Defaulting to Wait.")
                return {
                    'type': 'MOVE_AND_WAIT',
                    'unit_id': unit_id,
                    'move_data': move_action,
                    'action_data': {'type': 'WAIT'}
                }
                
        except ValueError:
            print("Invalid coordinates format. Please use 'x,y' format.")
            return self._handle_move_action(unit_id, movement_range)
    
    def _handle_attack_action(self, unit_id: str, after_move: bool = False) -> Dict[str, Any]:
        """
        Handle the Attack action for a unit.
        
        Args:
            unit_id: ID of the unit
            after_move: Whether this action is being taken after a move
            
        Returns:
            Dict containing the attack action data
        """
        # Get targets in range
        targets = self.map_system.get_units_in_attack_range(unit_id)
        
        if not targets:
            print("No targets in range.")
            if after_move:
                print("1. Wait instead")
                print("2. Try another action")
                choice = input("Select an option (1-2): ").strip()
                if choice == '1':
                    return {'type': 'WAIT', 'unit_id': unit_id}
                else:
                    return self._handle_unit_actions(unit_id)
            else:
                return self._handle_unit_actions(unit_id)
        
        # Display targets
        print("\nTargets in range:")
        for i, target_id in enumerate(targets, 1):
            target = self.game_state_manager.get_unit(target_id)
            print(f"{i}. {target.name} at {target.position} (HP: {target.current_hp}/{target.max_hp})")
        
        print(f"{len(targets) + 1}. Cancel")
        
        # Prompt for target selection
        choice = input(f"Select a target (1-{len(targets) + 1}): ").strip()
        
        try:
            choice_index = int(choice) - 1
            if choice_index == len(targets):  # Cancel option
                if after_move:
                    print("1. Wait instead")
                    print("2. Try another action")
                    choice = input("Select an option (1-2): ").strip()
                    if choice == '1':
                        return {'type': 'WAIT', 'unit_id': unit_id}
                    else:
                        return self._handle_unit_actions(unit_id)
                else:
                    return self._handle_unit_actions(unit_id)
            
            if choice_index < 0 or choice_index >= len(targets):
                print("Invalid selection. Please try again.")
                return self._handle_attack_action(unit_id, after_move)
            
            target_unit_id = targets[choice_index]
            
            return {
                'type': 'ATTACK',
                'unit_id': unit_id,
                'target_info': {
                    'target_unit_id': target_unit_id
                }
            }
            
        except ValueError:
            print("Invalid input. Please enter a number.")
            return self._handle_attack_action(unit_id, after_move)
    
    def _handle_item_action(self, unit_id: str, after_move: bool = False) -> Dict[str, Any]:
        """
        Handle the Item action for a unit.
        
        Args:
            unit_id: ID of the unit
            after_move: Whether this action is being taken after a move
            
        Returns:
            Dict containing the item action data
        """
        unit = self.game_state_manager.get_unit(unit_id)
        
        if not unit.inventory:
            print("Unit has no items.")
            if after_move:
                print("1. Wait instead")
                print("2. Try another action")
                choice = input("Select an option (1-2): ").strip()
                if choice == '1':
                    return {'type': 'WAIT', 'unit_id': unit_id}
                else:
                    return self._handle_unit_actions(unit_id)
            else:
                return self._handle_unit_actions(unit_id)
        
        # Display inventory
        print("\nInventory:")
        for i, item in enumerate(unit.inventory, 1):
            item_data = self.data_provider.get_item_data(item.item_id)
            print(f"{i}. {item_data.name} ({item.current_durability}/{item_data.max_durability})")
        
        print(f"{len(unit.inventory) + 1}. Cancel")
        
        # Prompt for item selection
        choice = input(f"Select an item (1-{len(unit.inventory) + 1}): ").strip()
        
        try:
            choice_index = int(choice) - 1
            if choice_index == len(unit.inventory):  # Cancel option
                if after_move:
                    print("1. Wait instead")
                    print("2. Try another action")
                    choice = input("Select an option (1-2): ").strip()
                    if choice == '1':
                        return {'type': 'WAIT', 'unit_id': unit_id}
                    else:
                        return self._handle_unit_actions(unit_id)
                else:
                    return self._handle_unit_actions(unit_id)
            
            if choice_index < 0 or choice_index >= len(unit.inventory):
                print("Invalid selection. Please try again.")
                return self._handle_item_action(unit_id, after_move)
            
            selected_item = unit.inventory[choice_index]
            item_data = self.data_provider.get_item_data(selected_item.item_id)
            
            # Check if item needs a target
            target_unit_id = None
            if hasattr(item_data, 'target_type') and item_data.target_type == 'UNIT':
                # Get valid targets
                valid_targets = self._get_valid_item_targets(unit_id, selected_item.item_id)
                
                if not valid_targets:
                    print("No valid targets for this item.")
                    return self._handle_item_action(unit_id, after_move)
                
                # Display targets
                print("\nSelect target:")
                for i, target_id in enumerate(valid_targets, 1):
                    target = self.game_state_manager.get_unit(target_id)
                    print(f"{i}. {target.name} at {target.position}")
                
                print(f"{len(valid_targets) + 1}. Cancel")
                
                # Prompt for target selection
                target_choice = input(f"Select a target (1-{len(valid_targets) + 1}): ").strip()
                
                try:
                    target_index = int(target_choice) - 1
                    if target_index == len(valid_targets):  # Cancel option
                        return self._handle_item_action(unit_id, after_move)
                    
                    if target_index < 0 or target_index >= len(valid_targets):
                        print("Invalid selection. Please try again.")
                        return self._handle_item_action(unit_id, after_move)
                    
                    target_unit_id = valid_targets[target_index]
                    
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    return self._handle_item_action(unit_id, after_move)
            
            return {
                'type': 'ITEM',
                'unit_id': unit_id,
                'target_info': {
                    'item_id': selected_item.item_id,
                    'item_index': choice_index,
                    'target_unit_id': target_unit_id
                }
            }
            
        except ValueError:
            print("Invalid input. Please enter a number.")
            return self._handle_item_action(unit_id, after_move)
    
    def _handle_capture_action(self, unit_id: str, after_move: bool = False) -> Dict[str, Any]:
        """
        Handle the Capture action for a unit.
        
        Args:
            unit_id: ID of the unit
            after_move: Whether this action is being taken after a move
            
        Returns:
            Dict containing the capture action data
        """
        # Get capturable targets in range (similar to attack range)
        targets = self.map_system.get_units_in_attack_range(unit_id)
        
        # Filter for capturable units (enemies that are not bosses)
        capturable_targets = []
        for target_id in targets:
            target = self.game_state_manager.get_unit(target_id)
            if target.faction != 'PLAYER' and not getattr(target, 'is_boss', False):
                capturable_targets.append(target_id)
        
        if not capturable_targets:
            print("No capturable targets in range.")
            if after_move:
                print("1. Wait instead")
                print("2. Try another action")
                choice = input("Select an option (1-2): ").strip()
                if choice == '1':
                    return {'type': 'WAIT', 'unit_id': unit_id}
                else:
                    return self._handle_unit_actions(unit_id)
            else:
                return self._handle_unit_actions(unit_id)
        
        # Display targets
        print("\nCapturable targets:")
        for i, target_id in enumerate(capturable_targets, 1):
            target = self.game_state_manager.get_unit(target_id)
            print(f"{i}. {target.name} at {target.position} (HP: {target.current_hp}/{target.max_hp})")
        
        print(f"{len(capturable_targets) + 1}. Cancel")
        
        # Prompt for target selection
        choice = input(f"Select a target (1-{len(capturable_targets) + 1}): ").strip()
        
        try:
            choice_index = int(choice) - 1
            if choice_index == len(capturable_targets):  # Cancel option
                if after_move:
                    print("1. Wait instead")
                    print("2. Try another action")
                    choice = input("Select an option (1-2): ").strip()
                    if choice == '1':
                        return {'type': 'WAIT', 'unit_id': unit_id}
                    else:
                        return self._handle_unit_actions(unit_id)
                else:
                    return self._handle_unit_actions(unit_id)
            
            if choice_index < 0 or choice_index >= len(capturable_targets):
                print("Invalid selection. Please try again.")
                return self._handle_capture_action(unit_id, after_move)
            
            target_unit_id = capturable_targets[choice_index]
            
            return {
                'type': 'CAPTURE',
                'unit_id': unit_id,
                'target_info': {
                    'target_unit_id': target_unit_id
                }
            }
            
        except ValueError:
            print("Invalid input. Please enter a number.")
            return self._handle_capture_action(unit_id, after_move)
    
    def _handle_trade_action(self, unit_id: str, after_move: bool = False) -> Dict[str, Any]:
        """
        Handle the Trade action for a unit.
        
        Args:
            unit_id: ID of the unit
            after_move: Whether this action is being taken after a move
            
        Returns:
            Dict containing the trade action data
        """
        unit = self.game_state_manager.get_unit(unit_id)
        
        # Get adjacent allies
        adjacent_allies = self._get_adjacent_allies(unit_id)
        
        if not adjacent_allies:
            print("No adjacent allies to trade with.")
            if after_move:
                print("1. Wait instead")
                print("2. Try another action")
                choice = input("Select an option (1-2): ").strip()
                if choice == '1':
                    return {'type': 'WAIT', 'unit_id': unit_id}
                else:
                    return self._handle_unit_actions(unit_id)
            else:
                return self._handle_unit_actions(unit_id)
        
        # Display adjacent allies
        print("\nAdjacent allies:")
        for i, ally_id in enumerate(adjacent_allies, 1):
            ally = self.game_state_manager.get_unit(ally_id)
            print(f"{i}. {ally.name} at {ally.position}")
        
        print(f"{len(adjacent_allies) + 1}. Cancel")
        
        # Prompt for ally selection
        choice = input(f"Select an ally to trade with (1-{len(adjacent_allies) + 1}): ").strip()
        
        try:
            choice_index = int(choice) - 1
            if choice_index == len(adjacent_allies):  # Cancel option
                if after_move:
                    print("1. Wait instead")
                    print("2. Try another action")
                    choice = input("Select an option (1-2): ").strip()
                    if choice == '1':
                        return {'type': 'WAIT', 'unit_id': unit_id}
                    else:
                        return self._handle_unit_actions(unit_id)
                else:
                    return self._handle_unit_actions(unit_id)
            
            if choice_index < 0 or choice_index >= len(adjacent_allies):
                print("Invalid selection. Please try again.")
                return self._handle_trade_action(unit_id, after_move)
            
            partner_unit_id = adjacent_allies[choice_index]
            
            # Initiate trade
            trade_data = self.inventory_system.initiate_trade(unit_id, partner_unit_id)
            if not trade_data:
                print("Failed to initiate trade.")
                return self._handle_unit_actions(unit_id)
            
            # Display inventories
            self._display_trade_inventories(unit_id, partner_unit_id, trade_data)
            
            # Handle item transfers
            item_transfers = []
            
            while True:
                print("\nEnter trade command (e.g., 'give 1 0' to give your item 1 to partner's slot 0)")
                print("Type 'done' when finished or 'cancel' to cancel trade")
                
                command = input().strip().lower()
                
                if command == 'done':
                    break
                elif command == 'cancel':
                    return self._handle_unit_actions(unit_id)
                
                try:
                    parts = command.split()
                    if len(parts) != 3:
                        print("Invalid command format. Use 'give [your_item_index] [partner_slot]'")
                        continue
                    
                    action, source_index, dest_index = parts
                    source_index = int(source_index)
                    dest_index = int(dest_index)
                    
                    if action == 'give':
                        # Give item from unit to partner
                        if source_index < 0 or source_index >= len(trade_data['unit1_inventory']):
                            print("Invalid source item index.")
                            continue
                        
                        item_transfers.append((unit_id, source_index, partner_unit_id, dest_index))
                        print(f"Will give item {source_index} to partner's slot {dest_index}")
                    
                    elif action == 'take':
                        # Take item from partner to unit
                        if source_index < 0 or source_index >= len(trade_data['unit2_inventory']):
                            print("Invalid source item index.")
                            continue
                        
                        item_transfers.append((partner_unit_id, source_index, unit_id, dest_index))
                        print(f"Will take partner's item {source_index} to your slot {dest_index}")
                    
                    else:
                        print("Invalid action. Use 'give' or 'take'.")
                
                except ValueError:
                    print("Invalid indices. Please use numbers for item indices.")
                except Exception as e:
                    print(f"Error: {e}")
            
            # Execute trade
            if item_transfers:
                success = self.inventory_system.execute_trade(unit_id, partner_unit_id, item_transfers)
                if not success:
                    print("Trade failed.")
                    return self._handle_unit_actions(unit_id)
                
                print("Trade successful.")
            else:
                print("No items were traded.")
            
            return {
                'type': 'TRADE',
                'unit_id': unit_id,
                'target_info': {
                    'partner_unit_id': partner_unit_id,
                    'item_transfers': item_transfers
                }
            }
            
        except ValueError:
            print("Invalid input. Please enter a number.")
            return self._handle_trade_action(unit_id, after_move)
    
    def _handle_visit_action(self, unit_id: str, after_move: bool = False) -> Dict[str, Any]:
        """
        Handle the Visit action for a unit.
        
        Args:
            unit_id: ID of the unit
            after_move: Whether this action is being taken after a move
            
        Returns:
            Dict containing the visit action data
        """
        unit = self.game_state_manager.get_unit(unit_id)
        
        # Check if unit is on a visitable tile
        current_pos = unit.position
        tile_type = self.game_state_manager.get_terrain_type(current_pos)
        
        # Check if the tile is visitable (e.g., house, village)
        is_visitable = self._is_tile_visitable(current_pos)
        
        if not is_visitable:
            print("No visitable location at current position.")
            if after_move:
                print("1. Wait instead")
                print("2. Try another action")
                choice = input("Select an option (1-2): ").strip()
                if choice == '1':
                    return {'type': 'WAIT', 'unit_id': unit_id}
                else:
                    return self._handle_unit_actions(unit_id)
            else:
                return self._handle_unit_actions(unit_id)
        
        # Confirm visit
        print(f"Visit the location at {current_pos}?")
        print("1. Yes")
        print("2. No")
        
        choice = input("Select an option (1-2): ").strip()
        
        if choice == '1':
            return {
                'type': 'VISIT',
                'unit_id': unit_id,
                'target_info': {'target_tile': current_pos}
            }
        else:
            if after_move:
                print("1. Wait instead")
                print("2. Try another action")
                choice = input("Select an option (1-2): ").strip()
                if choice == '1':
                    return {'type': 'WAIT', 'unit_id': unit_id}
                else:
                    return self._handle_unit_actions(unit_id)
            else:
                return self._handle_unit_actions(unit_id)
    
    def _handle_seize_action(self, unit_id: str, after_move: bool = False) -> Dict[str, Any]:
        """
        Handle the Seize action for a unit.
        
        Args:
            unit_id: ID of the unit
            after_move: Whether this action is being taken after a move
            
        Returns:
            Dict containing the seize action data
        """
        unit = self.game_state_manager.get_unit(unit_id)
        
        # Check if unit is on a seizable tile
        current_pos = unit.position
        
        # Check if the tile is seizable (e.g., throne)
        is_seizable = self._is_tile_seizable(current_pos)
        
        if not is_seizable:
            print("No seizable location at current position.")
            if after_move:
                print("1. Wait instead")
                print("2. Try another action")
                choice = input("Select an option (1-2): ").strip()
                if choice == '1':
                    return {'type': 'WAIT', 'unit_id': unit_id}
                else:
                    return self._handle_unit_actions(unit_id)
            else:
                return self._handle_unit_actions(unit_id)
    
    # --- Helper Methods ---
    
    def _display_turn_info(self):
        """Display the current turn and phase."""
        turn_manager = self.game_state_manager.turn_manager
        current_turn = turn_manager.get_current_turn()
        current_phase = turn_manager.get_current_phase()
        
        print(f"\n=== Turn {current_turn}, {current_phase.name} ===")
    
    def _get_active_player_units(self) -> List:
        """
        Get active player units that haven't acted yet.
        
        Returns:
            List of active player units
        """
        player_units = self.game_state_manager.get_units_by_faction('PLAYER')
        return [unit for unit in player_units if not unit.has_acted and unit.disposition == 'ACTIVE']
    
    def _display_active_units(self, units: List):
        """
        Display active units.
        
        Args:
            units: List of active units
        """
        print("\nActive units:")
        for i, unit in enumerate(units, 1):
            print(f"{i}. {unit.name} at {unit.position} (HP: {unit.current_hp}/{unit.max_hp})")
    
    def _display_unit_details(self, unit_id: str):
        """
        Display details for a unit.
        
        Args:
            unit_id: ID of the unit
        """
        unit_details = self.unit_system.get_unit_details(unit_id)
        unit = unit_details['state']
        
        print(f"\n=== {unit.name} ===")
        print(f"Position: {unit.position}")
        print(f"HP: {unit.current_hp}/{unit.max_hp}")
        
        # Display inventory
        print("\nInventory:")
        for i, item_detail in enumerate(unit_details['inventory_details'], 1):
            print(f"{i}. {item_detail['name']} ({item_detail['durability']}/{item_detail['max_durability']})")
    
    def _display_movement_range(self, movement_range: Set[Tuple[int, int]]):
        """
        Display the movement range for a unit.
        
        Args:
            movement_range: Set of positions the unit can move to
        """
        print(f"\nMovement range: {len(movement_range)} tiles")
        # In a real implementation, this would display the range on a map
    
    def _display_trade_inventories(self, unit1_id: str, unit2_id: str, trade_data: Dict):
        """
        Display inventories for trade.
        
        Args:
            unit1_id: ID of the first unit
            unit2_id: ID of the second unit
            trade_data: Trade data from initiate_trade
        """
        unit1 = self.game_state_manager.get_unit(unit1_id)
        unit2 = self.game_state_manager.get_unit(unit2_id)
        
        print(f"\n=== Trade between {unit1.name} and {unit2.name} ===")
        
        print(f"\n{unit1.name}'s inventory:")
        for i, item in enumerate(trade_data['unit1_inventory']):
            item_data = self.data_provider.get_item_data(item.item_id)
            print(f"{i}. {item_data.name} ({item.current_durability}/{item_data.max_durability})")
        
        print(f"\n{unit2.name}'s inventory:")
        for i, item in enumerate(trade_data['unit2_inventory']):
            item_data = self.data_provider.get_item_data(item.item_id)
            print(f"{i}. {item_data.name} ({item.current_durability}/{item_data.max_durability})")
    
    def _get_adjacent_allies(self, unit_id: str) -> List[str]:
        """
        Get adjacent ally units.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            List of adjacent ally unit IDs
        """
        unit = self.game_state_manager.get_unit(unit_id)
        if not unit:
            return []
        
        adjacent_allies = []
        x, y = unit.position
        
        # Check adjacent tiles
        adjacent_positions = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        
        for pos in adjacent_positions:
            # Check if there's a unit at this position
            for other_id, other_unit in self.game_state_manager.current_game_state.unit_states.items():
                if other_unit.position == pos and other_unit.faction == unit.faction and other_id != unit_id:
                    adjacent_allies.append(other_id)
        
        return adjacent_allies
    
    def _get_valid_item_targets(self, unit_id: str, item_id: str) -> List[str]:
        """
        Get valid targets for an item.
        
        Args:
            unit_id: ID of the unit using the item
            item_id: ID of the item
            
        Returns:
            List of valid target unit IDs
        """
        item_data = self.data_provider.get_item_data(item_id)
        if not item_data:
            return []
        
        unit = self.game_state_manager.get_unit(unit_id)
        if not unit:
            return []
        
        valid_targets = []
        
        # Get item range
        min_range = getattr(item_data, 'range_min', 1)
        max_range = getattr(item_data, 'range_max', 1)
        
        # Get target type (ally, enemy, any)
        target_type = getattr(item_data, 'target_type', 'ALLY')
        
        # Check all units
        for target_id, target_unit in self.game_state_manager.current_game_state.unit_states.items():
            # Skip self for most items
            if target_id == unit_id and not getattr(item_data, 'can_target_self', False):
                continue
            
            # Check faction
            if target_type == 'ALLY' and target_unit.faction != unit.faction:
                continue
            elif target_type == 'ENEMY' and target_unit.faction == unit.faction:
                continue
            
            # Check range
            distance = self._calculate_distance(unit.position, target_unit.position)
            if distance < min_range or distance > max_range:
                continue
            
            # Check line of sight if needed
            if getattr(item_data, 'requires_los', False):
                if not self.map_system.has_line_of_sight(unit.position, target_unit.position):
                    continue
            
            valid_targets.append(target_id)
        
        return valid_targets
    
    def _is_tile_visitable(self, position: Tuple[int, int]) -> bool:
        """
        Check if a tile is visitable.
        
        Args:
            position: Position to check
            
        Returns:
            True if the tile is visitable, False otherwise
        """
        # Get terrain type
        terrain_type = self.game_state_manager.get_terrain_type(position)
        
        # Check if it's a visitable terrain (e.g., house, village)
        visitable_terrains = ['HOUSE', 'VILLAGE', 'SHOP', 'ARMORY', 'VENDOR']
        
        # Convert terrain_type to string for comparison
        terrain_str = str(terrain_type)
        
        return terrain_str in visitable_terrains
    
    def _is_tile_seizable(self, position: Tuple[int, int]) -> bool:
        """
        Check if a tile is seizable.
        
        Args:
            position: Position to check
            
        Returns:
            True if the tile is seizable, False otherwise
        """
        # Get terrain type
        terrain_type = self.game_state_manager.get_terrain_type(position)
        
        # Check if it's a seizable terrain (e.g., throne)
        seizable_terrains = ['THRONE', 'GATE', 'CASTLE']
        
        # Convert terrain_type to string for comparison
        terrain_str = str(terrain_type)
        
        return terrain_str in seizable_terrains
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculate the Manhattan distance between two positions.
        
        Args:
            pos1: First position
            pos2: Second position
            
        Returns:
            Manhattan distance
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Confirm seize
        print(f"Seize the location at {current_pos}?")
        print("1. Yes")
        print("2. No")
        
        choice = input("Select an option (1-2): ").strip()
        
        if choice == '1':
            return {
                'type': 'SEIZE',
                'unit_id': unit_id,
                'target_info': {'target_tile': current_pos}
            }
        else:
            if after_move:
                print("1. Wait instead")
                print("2. Try another action")
                choice = input("Select an option (1-2): ").strip()
                if choice == '1':
                    return {'type': 'WAIT', 'unit_id': unit_id}
                else:
                    return self._handle_unit_actions(unit_id)
            else:
                return self._handle_unit_actions(unit_id)
