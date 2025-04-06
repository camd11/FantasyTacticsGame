"""
Action Handler Module

This module processes requests for units to perform actions on the map. It validates
the legality of requested actions based on the current game state, unit status, rules,
and context, then executes valid actions by coordinating with other systems.
"""

import logging
import random
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Set, Union

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum, StatusEffectEnum


class ActionType(Enum):
    """Types of actions that units can perform."""
    MOVE = auto()
    WAIT = auto()
    ATTACK = auto()
    CAPTURE = auto()
    ITEM = auto()
    TRADE = auto()
    RESCUE = auto()
    DROP = auto()
    TAKE = auto()
    RELEASE = auto()
    DISMOUNT = auto()
    MOUNT = auto()
    VISIT = auto()
    SEIZE = auto()
    TALK = auto()
    STEAL = auto()
    OPEN_DOOR = auto()
    STAFF = auto()
    DANCE = auto()


class UnitState(Enum):
    """States that a unit can be in during action processing."""
    IDLE = auto()
    MOVED = auto()
    ACTED = auto()
    CANTO_MOVE_PENDING = auto()


class ActionOutcome:
    """Result of an action attempt, including success status and optional data."""
    
    def __init__(self, success: bool, message: str = "", data: Dict = None):
        """
        Initialize an ActionOutcome.
        
        Args:
            success: Whether the action was successful
            message: Message describing the outcome
            data: Additional data about the outcome
        """
        self.success = success
        self.message = message
        self.data = data or {}


class ActionHandler:
    """
    Processes requests for units to perform actions, validates them against game rules,
    and executes valid actions by coordinating with other systems.
    """
    
    def __init__(self):
        """Initialize the ActionHandler."""
        self.gameStateManager = None
        self.unitSystem = None
        self.mapSystem = None
        self.movementSystem = None
        self.combatSystem = None
        self.inventorySystem = None
        self.turnManager = None
        self.eventHandler = None
        self.dataProvider = None
    
    def initialize(self, gameStateManager_instance, unitSystem_instance, mapSystem_instance,
                  movementSystem_instance, combatSystem_instance, inventorySystem_instance,
                  turnManager_instance, eventHandler_instance, dataProvider_instance):
        """
        Initialize the ActionHandler with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            unitSystem_instance: Instance of the UnitSystem
            mapSystem_instance: Instance of the MapSystem
            movementSystem_instance: Instance of the MovementSystem
            combatSystem_instance: Instance of the CombatSystem
            inventorySystem_instance: Instance of the InventorySystem
            turnManager_instance: Instance of the TurnManager
            eventHandler_instance: Instance of the EventHandler
            dataProvider_instance: Instance of the DataProvider
        """
        self.gameStateManager = gameStateManager_instance
        self.unitSystem = unitSystem_instance
        self.mapSystem = mapSystem_instance
        self.movementSystem = movementSystem_instance
        self.combatSystem = combatSystem_instance
        self.inventorySystem = inventorySystem_instance
        self.turnManager = turnManager_instance
        self.eventHandler = eventHandler_instance
        self.dataProvider = dataProvider_instance
        
        logging.info("ActionHandler initialized.")
    
    def process_action(self, unit_id: str, action_data: Dict[str, Any]) -> bool:
        """
        Process an action for a unit based on the action data.
        
        Args:
            unit_id: ID of the unit performing the action
            action_data: Dictionary containing action type and parameters
            
        Returns:
            True if the action was processed successfully, False otherwise
        """
        action_type_str = action_data.get('type', '')
        
        # Convert string action type to ActionType enum
        try:
            # Handle combined actions like MOVE_AND_WAIT
            if action_type_str == 'MOVE_AND_WAIT':
                # Process move action
                move_data = action_data.get('move_data', {})
                move_result = self.handle_move(unit_id, move_data.get('path', []))
                
                if not move_result or not move_result.success:
                    logging.error(f"Move action failed: {move_result.message if move_result else 'Unknown error'}")
                    return False
                
                # Process wait action
                wait_result = self.handle_wait(unit_id)
                
                if not wait_result or not wait_result.success:
                    logging.error(f"Wait action failed: {wait_result.message if wait_result else 'Unknown error'}")
                    return False
                
                # Mark unit as having acted
                unit = self.gameStateManager.get_unit(unit_id)
                if unit:
                    unit.has_acted = True
                
                return True
                
            elif action_type_str == 'MOVE_AND_ATTACK':
                # Process move action
                move_data = action_data.get('move_data', {})
                move_result = self.handle_move(unit_id, move_data.get('path', []))
                
                if not move_result or not move_result.success:
                    logging.error(f"Move action failed: {move_result.message if move_result else 'Unknown error'}")
                    return False
                
                # Process attack action
                attack_data = action_data.get('action_data', {})
                target_info = attack_data.get('target_info', {})
                attack_result = self.handle_attack(unit_id, target_info.get('target_unit_id'))
                
                if not attack_result or not attack_result.success:
                    logging.error(f"Attack action failed: {attack_result.message if attack_result else 'Unknown error'}")
                    return False
                
                # Mark unit as having acted
                unit = self.gameStateManager.get_unit(unit_id)
                if unit:
                    unit.has_acted = True
                
                return True
            
            # Handle simple actions
            elif action_type_str in ['MOVE', 'WAIT', 'ATTACK', 'CAPTURE', 'ITEM', 'TRADE', 'VISIT', 'SEIZE']:
                # Map string action type to enum
                action_type_map = {
                    'MOVE': ActionType.MOVE,
                    'WAIT': ActionType.WAIT,
                    'ATTACK': ActionType.ATTACK,
                    'CAPTURE': ActionType.CAPTURE,
                    'ITEM': ActionType.ITEM,
                    'TRADE': ActionType.TRADE,
                    'VISIT': ActionType.VISIT,
                    'SEIZE': ActionType.SEIZE
                }
                
                action_type = action_type_map.get(action_type_str)
                if not action_type:
                    logging.error(f"Unknown action type: {action_type_str}")
                    return False
                
                # Extract target data
                target_data = action_data.get('target_info', {})
                
                # For move actions, extract path
                if action_type == ActionType.MOVE:
                    target_data = {'path': action_data.get('path', [])}
                
                # Process the action
                result = self.perform_action(unit_id, action_type, target_data)
                
                if not result or not result.success:
                    logging.error(f"Action failed: {result.message if result else 'Unknown error'}")
                    return False
                
                return True
            
            else:
                logging.error(f"Unsupported action type: {action_type_str}")
                return False
                
        except Exception as e:
            logging.error(f"Error processing action: {e}")
            return False
    
    def perform_action(self, unit_id: str, action_type: ActionType, target_data: Dict) -> ActionOutcome:
        """
        Process an action request for a unit.
        
        Args:
            unit_id: ID of the unit performing the action
            action_type: Type of action to perform
            target_data: Data describing the action target and parameters
            
        Returns:
            ActionOutcome object with success status and additional data
        """
        # 1. Basic Validation
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return ActionOutcome(success=False, message="Unit not found.")
        
        if unit.has_acted:
            return ActionOutcome(success=False, message="Unit has already acted.")
        
        # Check if unit can act (not affected by disabling status effects)
        if not self._can_unit_act(unit):
            return ActionOutcome(success=False, message="Unit cannot act due to status effects.")
        
        # Check if it's the unit's faction's phase
        current_phase = self.gameStateManager.current_game_state.current_phase
        unit_faction = unit.faction
        if not self._is_correct_phase_for_faction(current_phase, unit_faction):
            return ActionOutcome(success=False, message="Not the unit's phase.")
        
        # 2. Action-Specific Validation & Execution
        outcome = None
        
        if action_type == ActionType.MOVE:
            outcome = self.handle_move(unit_id, target_data.get('path', []))
        elif action_type == ActionType.WAIT:
            outcome = self.handle_wait(unit_id)
        elif action_type == ActionType.ATTACK:
            outcome = self.handle_attack(unit_id, target_data.get('target_unit_id'))
        elif action_type == ActionType.CAPTURE:
            outcome = self.handle_capture(unit_id, target_data.get('target_unit_id'))
        elif action_type == ActionType.ITEM:
            outcome = self.handle_item(unit_id, target_data.get('item_id'), target_data.get('target_unit_id'))
        elif action_type == ActionType.TRADE:
            outcome = self.handle_trade(unit_id, target_data.get('partner_unit_id'), target_data.get('item_transfers', []))
        elif action_type == ActionType.RESCUE:
            outcome = self.handle_rescue(unit_id, target_data.get('target_unit_id'))
        elif action_type == ActionType.DROP:
            outcome = self.handle_drop(unit_id, target_data.get('target_tile'))
        elif action_type == ActionType.TAKE:
            outcome = self.handle_take(unit_id, target_data.get('partner_unit_id'))
        elif action_type == ActionType.RELEASE:
            outcome = self.handle_release(unit_id)
        elif action_type == ActionType.DISMOUNT:
            outcome = self.handle_dismount(unit_id)
        elif action_type == ActionType.MOUNT:
            outcome = self.handle_mount(unit_id)
        elif action_type == ActionType.VISIT:
            outcome = self.handle_visit(unit_id, target_data.get('target_tile'))
        elif action_type == ActionType.SEIZE:
            outcome = self.handle_seize(unit_id, target_data.get('target_tile'))
        elif action_type == ActionType.TALK:
            outcome = self.handle_talk(unit_id, target_data.get('target_unit_id'))
        elif action_type == ActionType.STEAL:
            outcome = self.handle_steal(unit_id, target_data.get('target_unit_id'), target_data.get('item_id'))
        elif action_type == ActionType.OPEN_DOOR:
            outcome = self.handle_open_door(unit_id, target_data.get('target_tile'), target_data.get('key_item_id'))
        else:
            outcome = ActionOutcome(success=False, message=f"Unsupported action type: {action_type}")
        
        # 3. Post-Action Processing (if successful and action consumes turn)
        if outcome and outcome.success:
            # Trade is a free action and doesn't consume the turn
            if action_type != ActionType.TRADE:
                # Make sure to set the has_acted flag
                unit = self.gameStateManager.get_unit(unit_id)
                if unit:
                    unit.has_acted = True
                
                # Record fatigue for the action
                self.turnManager.record_action_fatigue(unit_id, action_type.name)
                
                # Check for Canto
                if self._can_unit_canto(unit_id) and self._is_action_canto_eligible(action_type):
                    remaining_movement = self._get_remaining_movement(unit_id)
                    if remaining_movement > 0:
                        # Set unit state to pending Canto move
                        self._set_unit_state(unit_id, UnitState.CANTO_MOVE_PENDING)
                        logging.info(f"{unit.name} can Canto with {remaining_movement} movement remaining.")
                
                # Check for Movement Star (if not Canto pending)
                if not self._get_unit_state(unit_id) == UnitState.CANTO_MOVE_PENDING:
                    if self.turnManager.check_movement_star(unit_id):
                        # Unit state is reset by TurnManager, allow another action
                        unit.has_acted = False
                        unit.has_moved = False
                        self._set_unit_state(unit_id, UnitState.IDLE)
        
        return outcome
    
    # --- Action Handlers ---
    
    def handle_move(self, unit_id: str, path: List[Tuple[int, int]]) -> ActionOutcome:
        """
        Handle a move action.
        
        Args:
            unit_id: ID of the unit
            path: List of positions representing the path
            
        Returns:
            ActionOutcome object
        """
        if not path:
            return ActionOutcome(success=False, message="No path provided.")
        
        # Validate path using MovementSystem
        if not self.movementSystem.is_valid_destination(unit_id, path[-1]):
            return ActionOutcome(success=False, message="Invalid move path.")
        
        # Execute move
        success = self.movementSystem.execute_move(unit_id, path)
        if success:
            # Movement itself doesn't consume the action; subsequent action does
            unit = self.gameStateManager.get_unit(unit_id)
            unit.has_moved = True
            self._set_unit_state(unit_id, UnitState.MOVED)
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Failed to execute move.")
    
    def handle_wait(self, unit_id: str) -> ActionOutcome:
        """
        Handle a wait action.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            ActionOutcome object
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return ActionOutcome(success=False, message="Unit not found.")
        
        logging.info(f"{unit.name} waits.")
        return ActionOutcome(success=True)
    
    def handle_attack(self, unit_id: str, target_unit_id: str) -> ActionOutcome:
        """
        Handle an attack action.
        
        Args:
            unit_id: ID of the attacking unit
            target_unit_id: ID of the target unit
            
        Returns:
            ActionOutcome object
        """
        attacker = self.gameStateManager.get_unit(unit_id)
        defender = self.gameStateManager.get_unit(target_unit_id)
        
        if not defender:
            return ActionOutcome(success=False, message="Target unit not found.")
        
        # Check if target is valid (not an ally, not already captured, etc.)
        if not self._is_valid_combat_target(attacker, defender):
            return ActionOutcome(success=False, message="Invalid target.")
        
        # Check if attacker has a weapon equipped
        weapon = self._get_equipped_weapon(unit_id)
        if not weapon:
            return ActionOutcome(success=False, message="No weapon equipped.")
        
        # Check if target is in range
        distance = self._calculate_distance(attacker.position, defender.position)
        weapon_range = self._get_weapon_range(weapon)
        if distance not in weapon_range:
            return ActionOutcome(success=False, message="Target out of range.")
        
        # Execute combat
        combat_result = self.combatSystem.execute_combat(unit_id, target_unit_id, is_capture=False)
        return ActionOutcome(success=True, data={'combat_result': combat_result})
    
    def handle_capture(self, unit_id: str, target_unit_id: str) -> ActionOutcome:
        """
        Handle a capture action.
        
        Args:
            unit_id: ID of the capturing unit
            target_unit_id: ID of the target unit
            
        Returns:
            ActionOutcome object
        """
        attacker = self.gameStateManager.get_unit(unit_id)
        target = self.gameStateManager.get_unit(target_unit_id)
        
        if not target:
            return ActionOutcome(success=False, message="Target unit not found.")
        
        # Check if target is valid (must be enemy, not already captured)
        if target.faction == FactionEnum.PLAYER or target.faction == FactionEnum.NPC:
            return ActionOutcome(success=False, message="Cannot capture allies.")
        
        if not self._is_valid_combat_target(attacker, target):
            return ActionOutcome(success=False, message="Invalid target.")
        
        # Check capture immunity (Mounted or 20 Con)
        if self.gameStateManager.is_unit_mounted(target_unit_id) or target.base_stats.get('CON', 0) >= 20:
            return ActionOutcome(success=False, message="Target cannot be captured.")
        
        # Check Con requirement (Attacker Con > Target Con OR Attacker is Mounted)
        attacker_con = attacker.base_stats.get('CON', 0)
        target_con = target.base_stats.get('CON', 0)
        can_capture_by_con = attacker_con > target_con
        can_capture_by_mount = self.gameStateManager.is_unit_mounted(unit_id)
        
        if not (can_capture_by_con or can_capture_by_mount):
            return ActionOutcome(success=False, message="Constitution too low to capture.")
        
        # Check if attacker has a weapon equipped
        weapon = self._get_equipped_weapon(unit_id)
        if not weapon:
            return ActionOutcome(success=False, message="No weapon equipped for capture attempt.")
        
        # Check if target is in range
        distance = self._calculate_distance(attacker.position, target.position)
        weapon_range = self._get_weapon_range(weapon)
        if distance not in weapon_range:
            return ActionOutcome(success=False, message="Target out of range for capture attempt.")
        
        # Check if target is unarmed or incapacitated (auto-capture)
        target_weapon = self._get_equipped_weapon(target_unit_id)
        if not target_weapon or not self._can_unit_act(target):
            logging.info(f"Target {target.name} is unarmed/incapacitated. Auto-capturing.")
            self._capture_unit(unit_id, target_unit_id)
            return ActionOutcome(success=True, data={'auto_capture': True})
        
        # Execute capture combat (with penalties)
        combat_result = self.combatSystem.execute_combat(unit_id, target_unit_id, is_capture=True)
        
        if combat_result.get('target_defeated', False):
            self._capture_unit(unit_id, target_unit_id)
            return ActionOutcome(success=True, data={'combat_result': combat_result})
        else:
            # Capture failed (target survived combat)
            return ActionOutcome(success=False, message="Capture attempt failed.", data={'combat_result': combat_result})
    
    def handle_item(self, unit_id: str, item_id: str, target_unit_id: str = None) -> ActionOutcome:
        """
        Handle an item use action.
        
        Args:
            unit_id: ID of the unit using the item
            item_id: ID of the item to use
            target_unit_id: ID of the target unit (if applicable)
            
        Returns:
            ActionOutcome object
        """
        # Get the item from the unit's inventory
        item = self._get_item_from_inventory(unit_id, item_id)
        if not item:
            return ActionOutcome(success=False, message="Item not found in inventory.")
        
        if item.current_durability <= 0:
            return ActionOutcome(success=False, message="Item has no uses left.")
        
        # Get item data
        item_data = self.dataProvider.get_item_data(item_id)
        if not item_data:
            return ActionOutcome(success=False, message="Item data not found.")
        
        # Check if item is usable
        if not getattr(item_data, 'is_usable', False):
            return ActionOutcome(success=False, message="Item is not usable.")
        
        # Determine target (self or other unit)
        target_id = unit_id if getattr(item_data, 'targets_self', True) else target_unit_id
        if not target_id:
            return ActionOutcome(success=False, message="Target required for this item.")
        
        # Validate target range if applicable
        if target_id != unit_id:
            target_unit = self.gameStateManager.get_unit(target_id)
            if not target_unit:
                return ActionOutcome(success=False, message="Target unit not found.")
            
            # Check distance
            distance = self._calculate_distance(
                self.gameStateManager.get_unit(unit_id).position,
                target_unit.position
            )
            
            item_range = getattr(item_data, 'range', 1)
            if isinstance(item_range, int) and distance > item_range:
                return ActionOutcome(success=False, message="Target out of range.")
            elif isinstance(item_range, tuple) and (distance < item_range[0] or distance > item_range[1]):
                return ActionOutcome(success=False, message="Target out of range.")
        
        # Use the item
        success = self.inventorySystem.use_item(unit_id, item_id, target_id)
        
        if success:
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Failed to use item.")
    
    def handle_trade(self, unit_id: str, partner_unit_id: str, item_transfers: List) -> ActionOutcome:
        """
        Handle a trade action.
        
        Args:
            unit_id: ID of the initiating unit
            partner_unit_id: ID of the partner unit
            item_transfers: List of item transfers to perform
            
        Returns:
            ActionOutcome object
        """
        unit = self.gameStateManager.get_unit(unit_id)
        partner = self.gameStateManager.get_unit(partner_unit_id)
        captive_target_id = None
        
        if not partner:
            # Check if partner_unit_id refers to a captive held by unit_id
            captive = self._get_captive_unit(unit_id)
            if captive and captive.id == partner_unit_id:
                partner = captive
                captive_target_id = partner.id
                logging.info(f"Trading with captive: {partner.name}")
            else:
                return ActionOutcome(success=False, message="Trade partner not found.")
        
        # Check if partner is adjacent (unless trading with captive)
        if not captive_target_id:
            distance = self._calculate_distance(unit.position, partner.position)
            if distance != 1:
                return ActionOutcome(success=False, message="Trade partner not adjacent.")
        
        # Perform trade logic via InventorySystem
        success = self.inventorySystem.execute_trade(
            unit_id, partner_unit_id, item_transfers,
            is_captive_trade=(captive_target_id is not None)
        )
        
        if success:
            # Trade is a FREE action in Thracia - does not consume the turn
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Trade failed.")
    
    def handle_rescue(self, unit_id: str, target_unit_id: str) -> ActionOutcome:
        """
        Handle a rescue action.
        
        Args:
            unit_id: ID of the rescuing unit
            target_unit_id: ID of the unit to rescue
            
        Returns:
            ActionOutcome object
        """
        rescuer = self.gameStateManager.get_unit(unit_id)
        target = self.gameStateManager.get_unit(target_unit_id)
        
        if not target:
            return ActionOutcome(success=False, message="Target unit not found.")
        
        # Can only rescue player units (or NPCs?)
        if target.faction != FactionEnum.PLAYER:
            return ActionOutcome(success=False, message="Invalid rescue target.")
        
        # Check if target is adjacent
        distance = self._calculate_distance(rescuer.position, target.position)
        if distance != 1:
            return ActionOutcome(success=False, message="Target not adjacent.")
        
        # Check if either unit is already involved in a rescue
        if rescuer.carrying_unit_id is not None:
            return ActionOutcome(success=False, message="Rescuer is already carrying a unit.")
        
        if self._is_unit_carried(target_unit_id):
            return ActionOutcome(success=False, message="Target is already being carried.")
        
        # Check Con requirement (Rescuer Con > Target Con)
        rescuer_con = rescuer.base_stats.get('CON', 0)
        target_con = target.base_stats.get('CON', 0)
        
        if rescuer_con <= target_con:
            return ActionOutcome(success=False, message="Constitution too low to rescue.")
        
        # Execute rescue
        success = self._rescue_unit(unit_id, target_unit_id)
        
        if success:
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Rescue failed.")
    
    def handle_drop(self, unit_id: str, target_tile: Tuple[int, int]) -> ActionOutcome:
        """
        Handle a drop action.
        
        Args:
            unit_id: ID of the unit dropping a carried unit
            target_tile: Coordinates to drop the carried unit
            
        Returns:
            ActionOutcome object
        """
        unit = self.gameStateManager.get_unit(unit_id)
        
        # Check if unit is carrying someone
        if not unit.carrying_unit_id:
            return ActionOutcome(success=False, message="Unit is not carrying anyone.")
        
        carried_unit_id = unit.carrying_unit_id
        
        # Check if target tile is adjacent
        distance = self._calculate_distance(unit.position, target_tile)
        if distance != 1:
            return ActionOutcome(success=False, message="Drop location not adjacent.")
        
        # Check if target tile is valid (not occupied, not impassable)
        if self._is_tile_occupied(target_tile):
            return ActionOutcome(success=False, message="Target tile is occupied.")
        
        # Check if target tile is passable for the carried unit
        carried_unit = self.gameStateManager.get_unit(carried_unit_id)
        if self.mapSystem.get_movement_cost(target_tile, carried_unit_id) >= float('inf'):
            return ActionOutcome(success=False, message="Carried unit cannot be placed on that terrain.")
        
        # Execute drop
        success = self._drop_unit(unit_id, target_tile)
        
        if success:
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Drop failed.")
    
    def handle_take(self, unit_id: str, partner_unit_id: str) -> ActionOutcome:
        """
        Handle a take action (taking a carried unit from an adjacent ally).
        
        Args:
            unit_id: ID of the unit taking a carried unit
            partner_unit_id: ID of the unit currently carrying the unit to be taken
            
        Returns:
            ActionOutcome object
        """
        unit = self.gameStateManager.get_unit(unit_id)
        partner = self.gameStateManager.get_unit(partner_unit_id)
        
        if not partner:
            return ActionOutcome(success=False, message="Partner unit not found.")
        
        # Check if partner is carrying someone
        if not partner.carrying_unit_id:
            return ActionOutcome(success=False, message="Partner is not carrying anyone.")
        
        # Check if unit is already carrying someone
        if unit.carrying_unit_id:
            return ActionOutcome(success=False, message="Unit is already carrying someone.")
        
        # Check if partner is adjacent
        distance = self._calculate_distance(unit.position, partner.position)
        if distance != 1:
            return ActionOutcome(success=False, message="Partner not adjacent.")
        
        carried_unit_id = partner.carrying_unit_id
        carried_unit = self.gameStateManager.get_unit(carried_unit_id)
        
        # Check Con requirement (Taker Con > Carried Unit Con)
        taker_con = unit.base_stats.get('CON', 0)
        carried_con = carried_unit.base_stats.get('CON', 0)
        
        if taker_con <= carried_con:
            return ActionOutcome(success=False, message="Constitution too low to take carried unit.")
        
        # Execute take
        success = self._take_unit(unit_id, partner_unit_id)
        
        if success:
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Take failed.")
    
    def handle_release(self, unit_id: str) -> ActionOutcome:
        """
        Handle a release action (releasing a captured enemy).
        
        Args:
            unit_id: ID of the unit releasing a captured enemy
            
        Returns:
            ActionOutcome object
        """
        unit = self.gameStateManager.get_unit(unit_id)
        
        # Check if unit is carrying a captured enemy
        captive = self._get_captive_unit(unit_id)
        if not captive:
            return ActionOutcome(success=False, message="Unit is not holding a captive.")
        
        # Find an adjacent empty tile
        adjacent_tiles = self._get_adjacent_tiles(unit.position)
        valid_tiles = [tile for tile in adjacent_tiles if not self._is_tile_occupied(tile)]
        
        if not valid_tiles:
            return ActionOutcome(success=False, message="No adjacent tile available for release.")
        
        # Choose the first valid tile (could be more sophisticated)
        release_tile = valid_tiles[0]
        
        # Execute release
        success = self._release_captive(unit_id, release_tile)
        
        if success:
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Release failed.")
    
    def handle_dismount(self, unit_id: str) -> ActionOutcome:
        """
        Handle a dismount action.
        
        Args:
            unit_id: ID of the unit dismounting
            
        Returns:
            ActionOutcome object
        """
        if not self.gameStateManager.is_unit_mounted(unit_id):
            return ActionOutcome(success=False, message="Unit is not mounted.")
        
        # Check if already dismounted
        unit = self.gameStateManager.get_unit(unit_id)
        if hasattr(unit, 'is_dismounted') and unit.is_dismounted:
            return ActionOutcome(success=False, message="Unit is already dismounted.")
        
        # Execute dismount
        success = self._dismount_unit(unit_id)
        
        if success:
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Dismount failed.")
    
    def handle_mount(self, unit_id: str) -> ActionOutcome:
        """
        Handle a mount action.
        
        Args:
            unit_id: ID of the unit mounting
            
        Returns:
            ActionOutcome object
        """
        unit = self.gameStateManager.get_unit(unit_id)
        
        # Check if class can mount
        if not self._can_unit_mount(unit_id):
            return ActionOutcome(success=False, message="Unit class cannot mount.")
        
        # Check if already mounted
        if not hasattr(unit, 'is_dismounted') or not unit.is_dismounted:
            return ActionOutcome(success=False, message="Unit is already mounted.")
        
        # Check if indoors
        if self.mapSystem.get_terrain_properties(unit.position).get('is_indoor', False):
            return ActionOutcome(success=False, message="Cannot mount indoors.")
        
        # Execute mount
        success = self._mount_unit(unit_id)
        
        if success:
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Mount failed.")
    
    def handle_visit(self, unit_id: str, target_tile: Tuple[int, int]) -> ActionOutcome:
        """
        Handle a visit action.
        
        Args:
            unit_id: ID of the unit visiting
            target_tile: Coordinates of the tile to visit
            
        Returns:
            ActionOutcome object
        """
        unit = self.gameStateManager.get_unit(unit_id)
        
        # Check if unit is on the target tile
        if unit.position != target_tile:
            return ActionOutcome(success=False, message="Unit must be on the tile to visit.")
        
        # Check if tile has a visitable feature (e.g., village)
        tile_feature = self._get_tile_feature(target_tile)
        if not tile_feature or tile_feature.get('type') != 'VILLAGE' or tile_feature.get('is_visited', False):
            return ActionOutcome(success=False, message="Cannot visit this location.")
        
        # Trigger event associated with the village
        if self.eventHandler:
            event_triggered = self.eventHandler.trigger_map_event('VISIT', unit_id, target_tile)
            if event_triggered:
                # Mark feature as visited
                self._mark_feature_as_visited(target_tile)
                return ActionOutcome(success=True)
            else:
                return ActionOutcome(success=False, message="Visit event failed.")
        else:
            # If no event handler, just mark as visited
            self._mark_feature_as_visited(target_tile)
            return ActionOutcome(success=True)
    
    def handle_seize(self, unit_id: str, target_tile: Tuple[int, int]) -> ActionOutcome:
        """
        Handle a seize action.
        
        Args:
            unit_id: ID of the unit seizing
            target_tile: Coordinates of the tile to seize
            
        Returns:
            ActionOutcome object
        """
        unit = self.gameStateManager.get_unit(unit_id)
        
        # Check if unit is the Lord (Leif)
        if not self._is_lord(unit_id):
            return ActionOutcome(success=False, message="Only the Lord can seize.")
        
        # Check if unit is on the target tile
        if unit.position != target_tile:
            return ActionOutcome(success=False, message="Must be on the seize point.")
        
        # Check if tile is a seize point
        if not self.gameStateManager.is_tile_seize_point(target_tile):
            return ActionOutcome(success=False, message="Not a valid seize point.")
        
        # Trigger seize event (usually ends chapter)
        if self.eventHandler:
            event_triggered = self.eventHandler.trigger_map_event('SEIZE', unit_id, target_tile)
            if event_triggered:
                # Chapter end logic likely handled by EventHandler or GameStateManager
                return ActionOutcome(success=True, data={'chapter_end': True})
            else:
                return ActionOutcome(success=False, message="Seize event failed.")
        else:
            # If no event handler, just end the chapter
            # This would be handled by the game engine in a real implementation
            return ActionOutcome(success=True, data={'chapter_end': True})
    
    def handle_talk(self, unit_id: str, target_unit_id: str) -> ActionOutcome:
            """
            Handle a talk action.
            
            Args:
                unit_id: ID of the unit initiating the talk
                target_unit_id: ID of the target unit to talk to
                
            Returns:
                ActionOutcome object
            """
            talker = self.gameStateManager.get_unit(unit_id)
            target = self.gameStateManager.get_unit(target_unit_id)
            
            if not target:
                return ActionOutcome(success=False, message="Talk target not found.")
            
            # Check if target is adjacent
            distance = self._calculate_distance(talker.position, target.position)
            if distance != 1:
                return ActionOutcome(success=False, message="Talk target not adjacent.")
            
            # Check if a conversation exists between these two units
            if self.eventHandler and self.eventHandler.has_talk_event(unit_id, target_unit_id):
                event_triggered = self.eventHandler.trigger_talk_event(unit_id, target_unit_id)
                if event_triggered:
                    return ActionOutcome(success=True)
                else:
                    return ActionOutcome(success=False, message="Talk event failed to trigger.")
            else:
                return ActionOutcome(success=False, message="No conversation available.")
    def handle_steal(self, unit_id: str, target_unit_id: str, item_id: str) -> ActionOutcome:
        """
        Handle a steal action.
        
        Args:
            unit_id: ID of the thief
            target_unit_id: ID of the target unit
            item_id: ID of the item to steal
                
            Returns:
                ActionOutcome object
        """
        thief = self.gameStateManager.get_unit(unit_id)
        target = self.gameStateManager.get_unit(target_unit_id)
        
        # Check if unit has the Steal skill
        if not self._has_steal_skill(unit_id):
            return ActionOutcome(success=False, message="Unit cannot steal.")
        
        if not target or target.faction == FactionEnum.PLAYER:
            return ActionOutcome(success=False, message="Invalid steal target.")
        
        # Check if target is adjacent
        distance = self._calculate_distance(thief.position, target.position)
        if distance != 1:
            return ActionOutcome(success=False, message="Target not adjacent.")
        
        # Check if thief's inventory is full
        if self._is_inventory_full(unit_id):
            return ActionOutcome(success=False, message="Inventory full.")
        
        # Check if target has the item
        item_to_steal = self._get_item_from_inventory(target_unit_id, item_id)
        if not item_to_steal:
            return ActionOutcome(success=False, message="Target does not have that item.")
        
        # Get item weight
        item_data = self.dataProvider.get_item_data(item_id)
        if not item_data:
            return ActionOutcome(success=False, message="Item data not found.")
        
        item_weight = getattr(item_data, 'weight', 0)
        
        # Check Speed requirement (Thief AS > Target AS)
        thief_as = self._get_attack_speed(unit_id)
        target_as = self._get_attack_speed(target_unit_id)
        if thief_as <= target_as:
            return ActionOutcome(success=False, message="Thief not fast enough to steal.")
        
        # Check Con requirement (Thief Con >= Item Weight)
        thief_con = thief.base_stats.get('CON', 0)
        if thief_con < item_weight:
            return ActionOutcome(success=False, message="Item too heavy to steal.")
        
        # Execute steal
        success = self.inventorySystem.transfer_item(target_unit_id, unit_id, item_id)
        
        if success:
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Steal transfer failed.")
        
    def handle_open_door(self, unit_id: str, target_tile: Tuple[int, int], key_item_id: str = None) -> ActionOutcome:
            """
            Handle an open door action.
            
            Args:
                unit_id: ID of the unit opening the door
                target_tile: Coordinates of the door to open
                key_item_id: ID of the key item to use (optional)
                
            Returns:
                ActionOutcome object
            """
            unit = self.gameStateManager.get_unit(unit_id)
            
            # Check if target is adjacent
            distance = self._calculate_distance(unit.position, target_tile)
            if distance != 1:
                return ActionOutcome(success=False, message="Door not adjacent.")
            
            # Check if tile has a door
            tile_feature = self._get_tile_feature(target_tile)
            if not tile_feature or tile_feature.get('type') != 'DOOR':
                return ActionOutcome(success=False, message="No door at target location.")
            
            # Check if unit has a key or lockpick, or if a specific key was provided
            has_key = False
            key_to_use = None
            
            if key_item_id:
                # Check if unit has the specified key
                key_item = self._get_item_from_inventory(unit_id, key_item_id)
                if key_item:
                    key_to_use = key_item_id
                    has_key = True
            else:
                # Check if unit has any key or lockpick
                for item in self._get_inventory(unit_id):
                    item_data = self.dataProvider.get_item_data(item.item_id)
                    if item_data and item_data.type == 'KEY':
                        key_to_use = item.item_id
                        has_key = True
                        break
            
            # Check if unit has the Lockpick skill (thieves can open doors without keys)
            has_lockpick_skill = self._has_lockpick_skill(unit_id)
            
            if not has_key and not has_lockpick_skill:
                return ActionOutcome(success=False, message="No key or lockpick skill to open door.")
            
            # Execute door opening
            if has_key:
                # Use the key (reduce durability)
                self.inventorySystem.use_item(unit_id, key_to_use, None)
            
            # Open the door
            success = self._open_door(target_tile)
            
            if success:
                return ActionOutcome(success=True)
            else:
                return ActionOutcome(success=False, message="Failed to open door.")
    
    # --- Helper Methods ---
    
    def _can_unit_act(self, unit) -> bool:
        """
        Check if a unit can act (not affected by disabling status effects).
        
        Args:
            unit: The unit to check
            
        Returns:
            True if the unit can act, False otherwise
        """
        # Check for statuses like Sleep, Petrify, etc.
        return not unit.has_status(StatusEffectEnum.SLEEP) and not unit.has_status(StatusEffectEnum.BERSERK)
    
    def _is_correct_phase_for_faction(self, phase: PhaseEnum, faction: FactionEnum) -> bool:
        """
        Check if the current phase corresponds to the unit's faction.
        
        Args:
            phase: The current phase
            faction: The unit's faction
            
        Returns:
            True if the phase corresponds to the faction, False otherwise
        """
        if phase == PhaseEnum.PLAYER and faction == FactionEnum.PLAYER:
            return True
        elif phase == PhaseEnum.ENEMY and faction == FactionEnum.ENEMY:
            return True
        elif phase == PhaseEnum.NPC and faction == FactionEnum.NPC:
            return True
        return False
    
    def _is_valid_combat_target(self, attacker, defender) -> bool:
        """
        Check if a target is valid for combat.
        
        Args:
            attacker: The attacking unit
            defender: The defending unit
            
        Returns:
            True if the target is valid, False otherwise
        """
        # Check if target is an enemy
        if attacker.faction == defender.faction:
            return False
        
        # Check if target is already captured
        if defender.is_captured:
            return False
        
        # Check if target is active (not dead, escaped, etc.)
        if not hasattr(defender, 'disposition') or defender.disposition != 'ACTIVE':
            return False
        
        return True
    
    def _get_equipped_weapon(self, unit_id: str):
        """
        Get the equipped weapon for a unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            The equipped weapon or None if no weapon is equipped
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or unit.equipped_weapon_index < 0 or unit.equipped_weapon_index >= len(unit.inventory):
            return None
        
        return unit.inventory[unit.equipped_weapon_index]
    
    def _get_weapon_range(self, weapon) -> List[int]:
        """
        Get the range of a weapon.
        
        Args:
            weapon: The weapon
            
        Returns:
            List of valid ranges
        """
        item_data = self.dataProvider.get_item_data(weapon.item_id)
        if not item_data:
            return [1]  # Default to melee range
        
        min_range = getattr(item_data, 'range_min', 1)
        max_range = getattr(item_data, 'range_max', 1)
        
        return list(range(min_range, max_range + 1))
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculate the Manhattan distance between two positions.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            Manhattan distance
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _capture_unit(self, captor_id: str, captive_id: str) -> bool:
        """
        Capture a unit.
        
        Args:
            captor_id: ID of the capturing unit
            captive_id: ID of the unit to capture
            
        Returns:
            True if successful, False otherwise
        """
        captor = self.gameStateManager.get_unit(captor_id)
        captive = self.gameStateManager.get_unit(captive_id)
        
        if not captor or not captive:
            return False
        
        # Set captive as captured
        captive.is_captured = True
        
        # Set captor as carrying the captive
        captor.carrying_unit_id = captive_id
        
        # Remove captive from map
        # This would be handled by the GameStateManager in a real implementation
        
        return True
    
    def _get_item_from_inventory(self, unit_id: str, item_id: str):
        """
        Get an item from a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            item_id: ID of the item
            
        Returns:
            The item or None if not found
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return None
        
        for item in unit.inventory:
            if item.item_id == item_id:
                return item
        
        return None
    
    def _get_inventory(self, unit_id: str) -> List:
        """
        Get a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            List of items in the unit's inventory
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return []
        
        return unit.inventory
    
    def _is_inventory_full(self, unit_id: str) -> bool:
        """
        Check if a unit's inventory is full.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the inventory is full, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return True
        
        # Assuming max inventory size is 7 (Thracia 776)
        return len(unit.inventory) >= 7
    
    def _get_captive_unit(self, unit_id: str):
        """
        Get the captive unit held by a unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            The captive unit or None if no captive is held
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or not unit.carrying_unit_id:
            return None
        
        captive_id = unit.carrying_unit_id
        return self.gameStateManager.get_unit(captive_id)
    
    def _is_unit_carried(self, unit_id: str) -> bool:
        """
        Check if a unit is being carried.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit is being carried, False otherwise
        """
        # This would need to check all units to see if any are carrying this unit
        for unit in self.gameStateManager.current_game_state.unit_states.values():
            if unit.carrying_unit_id == unit_id:
                return True
        
        return False
    
    def _rescue_unit(self, rescuer_id: str, target_id: str) -> bool:
        """
        Rescue a unit.
        
        Args:
            rescuer_id: ID of the rescuing unit
            target_id: ID of the unit to rescue
            
        Returns:
            True if successful, False otherwise
        """
        rescuer = self.gameStateManager.get_unit(rescuer_id)
        target = self.gameStateManager.get_unit(target_id)
        
        if not rescuer or not target:
            return False
        
        # Set rescuer as carrying the target
        rescuer.carrying_unit_id = target_id
        
        # Remove target from map
        # This would be handled by the GameStateManager in a real implementation
        
        return True
    
    def _drop_unit(self, unit_id: str, target_tile: Tuple[int, int]) -> bool:
        """
        Drop a carried unit.
        
        Args:
            unit_id: ID of the unit dropping a carried unit
            target_tile: Coordinates to drop the carried unit
            
        Returns:
            True if successful, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or not unit.carrying_unit_id:
            return False
        
        carried_unit_id = unit.carrying_unit_id
        carried_unit = self.gameStateManager.get_unit(carried_unit_id)
        
        if not carried_unit:
            return False
        
        # Place carried unit at target tile
        carried_unit.position = target_tile
        
        # Update map state
        self.gameStateManager.current_game_state.map_state.unit_positions[carried_unit_id] = target_tile
        
        # Clear carrying state
        unit.carrying_unit_id = None
        
        return True
    
    def _take_unit(self, taker_id: str, partner_id: str) -> bool:
        """
        Take a carried unit from another unit.
        
        Args:
            taker_id: ID of the unit taking a carried unit
            partner_id: ID of the unit currently carrying the unit to be taken
            
        Returns:
            True if successful, False otherwise
        """
        taker = self.gameStateManager.get_unit(taker_id)
        partner = self.gameStateManager.get_unit(partner_id)
        
        if not taker or not partner or not partner.carrying_unit_id:
            return False
        
        carried_unit_id = partner.carrying_unit_id
        
        # Transfer carried unit
        taker.carrying_unit_id = carried_unit_id
        partner.carrying_unit_id = None
        
        return True
    
    def _release_captive(self, unit_id: str, release_tile: Tuple[int, int]) -> bool:
        """
        Release a captured enemy.
        
        Args:
            unit_id: ID of the unit releasing a captured enemy
            release_tile: Coordinates to release the captive
            
        Returns:
            True if successful, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or not unit.carrying_unit_id:
            return False
        
        captive_id = unit.carrying_unit_id
        captive = self.gameStateManager.get_unit(captive_id)
        
        if not captive or not captive.is_captured:
            return False
        
        # Place captive at release tile
        captive.position = release_tile
        captive.is_captured = False
        
        # Update map state
        self.gameStateManager.current_game_state.map_state.unit_positions[captive_id] = release_tile
        
        # Clear carrying state
        unit.carrying_unit_id = None
        
        return True
    
    def _dismount_unit(self, unit_id: str) -> bool:
        """
        Dismount a unit.
        
        Args:
            unit_id: ID of the unit dismounting
            
        Returns:
            True if successful, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        # Set dismounted state
        unit.is_dismounted = True
        
        # Change class to dismounted version
        class_data = self.dataProvider.get_class_data(unit.class_id)
        if class_data and class_data.dismount_class_id:
            unit.class_id = class_data.dismount_class_id
        
        return True
    
    def _mount_unit(self, unit_id: str) -> bool:
        """
        Mount a unit.
        
        Args:
            unit_id: ID of the unit mounting
            
        Returns:
            True if successful, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or not hasattr(unit, 'is_dismounted') or not unit.is_dismounted:
            return False
        
        # Clear dismounted state
        unit.is_dismounted = False
        
        # Change class back to mounted version
        # This would require knowing the original mounted class
        # For simplicity, we'll assume the current class has a reference to its mounted version
        class_data = self.dataProvider.get_class_data(unit.class_id)
        if class_data and hasattr(class_data, 'mount_class_id'):
            unit.class_id = class_data.mount_class_id
        
        return True
    
    def _can_unit_mount(self, unit_id: str) -> bool:
        """
        Check if a unit can mount.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit can mount, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        # Check if unit is dismounted
        if not hasattr(unit, 'is_dismounted') or not unit.is_dismounted:
            return False
        
        # Check if class can mount
        class_data = self.dataProvider.get_class_data(unit.class_id)
        return class_data and hasattr(class_data, 'mount_class_id')
    
    def _get_tile_feature(self, tile: Tuple[int, int]) -> Dict:
        """
        Get the feature at a tile.
        
        Args:
            tile: Coordinates of the tile
            
        Returns:
            Dictionary of feature properties or None if no feature
        """
        # This would be handled by the MapSystem in a real implementation
        return self.mapSystem.get_terrain_properties(tile)
    
    def _mark_feature_as_visited(self, tile: Tuple[int, int]) -> bool:
        """
        Mark a feature as visited.
        
        Args:
            tile: Coordinates of the tile
            
        Returns:
            True if successful, False otherwise
        """
        # This would be handled by the MapSystem in a real implementation
        return True
    
    def _is_lord(self, unit_id: str) -> bool:
        """
        Check if a unit is the Lord (Leif).
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit is the Lord, False otherwise
        """
        # In Thracia 776, Leif is the Lord
        return unit_id == "LEIF"
    
    def _has_steal_skill(self, unit_id: str) -> bool:
        """
        Check if a unit has the Steal skill.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit has the Steal skill, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        # Check if unit has the Steal skill
        # This would be handled by the UnitSystem in a real implementation
        return "STEAL" in getattr(unit, 'skills', [])
    
    def _has_lockpick_skill(self, unit_id: str) -> bool:
        """
        Check if a unit has the Lockpick skill.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit has the Lockpick skill, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        # Check if unit has the Lockpick skill
        # This would be handled by the UnitSystem in a real implementation
        return "LOCKPICK" in getattr(unit, 'skills', [])
    
    def _get_attack_speed(self, unit_id: str) -> int:
        """
        Get the attack speed of a unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Attack speed
        """
        # This would be handled by the UnitSystem in a real implementation
        return self.unitSystem.calculate_current_combat_stats(unit_id).get('AS', 0)
    
    def _get_adjacent_tiles(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get the adjacent tiles for a position.
        
        Args:
            position: Position (x, y)
            
        Returns:
            List of adjacent positions
        """
        x, y = position
        return [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]
    
    def _is_tile_occupied(self, position: Tuple[int, int]) -> bool:
        """
        Check if a tile is occupied.
        
        Args:
            position: Position (x, y)
            
        Returns:
            True if the tile is occupied, False otherwise
        """
        # This would be handled by the MapSystem in a real implementation
        return position in self.gameStateManager.current_game_state.map_state.unit_positions.values()
    
    def _open_door(self, position: Tuple[int, int]) -> bool:
        """
        Open a door.
        
        Args:
            position: Position (x, y) of the door
            
        Returns:
            True if successful, False otherwise
        """
        # This would be handled by the MapSystem in a real implementation
        return True
    
    def _can_unit_canto(self, unit_id: str) -> bool:
        """
        Check if a unit can Canto.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit can Canto, False otherwise
        """
        # In Thracia 776, mounted units can Canto
        return self.gameStateManager.is_unit_mounted(unit_id)
    
    def _is_action_canto_eligible(self, action_type: ActionType) -> bool:
        """
        Check if an action is eligible for Canto.
        
        Args:
            action_type: Type of action
            
        Returns:
            True if the action is eligible for Canto, False otherwise
        """
        # In Thracia 776, most actions except Attack and Capture allow Canto
        return action_type not in [ActionType.ATTACK, ActionType.CAPTURE]
    
    def _get_remaining_movement(self, unit_id: str) -> int:
        """
        Get the remaining movement for a unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Remaining movement points
        """
        # This would be calculated based on the unit's movement and how far they've moved
        # For simplicity, we'll return a fixed value
        return 2
    
    def _set_unit_state(self, unit_id: str, state: UnitState) -> None:
        """
        Set the state of a unit.
        
        Args:
            unit_id: ID of the unit
            state: New state
        """
        # This would be handled by the GameStateManager in a real implementation
        pass
    
    def _get_unit_state(self, unit_id: str) -> UnitState:
        """
        Get the state of a unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Current state
        """
        # This would be handled by the GameStateManager in a real implementation
        # For now, return a default state
        return UnitState.IDLE
