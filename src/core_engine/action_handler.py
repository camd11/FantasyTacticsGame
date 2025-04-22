"""
Action Handler Module

This module processes requests for units to perform actions on the map. It validates
the legality of requested actions based on the current game state, unit status, rules,
and context, then executes valid actions by coordinating with other systems.
"""

import logging
import random
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Set, Union, TYPE_CHECKING

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum, StatusEffectEnum
from src.gameplay_systems.ai.ai_types import AIAction # Add import for AIAction

if TYPE_CHECKING:
    # Import types for systems to avoid circular imports
    from src.core_engine.data_provider import DataProvider
    from src.core_engine.event_handler import EventHandler
    from src.core_engine.turn_manager import TurnManager as CoreTurnManager
    from src.gameplay_systems.turn_manager import TurnManager as GameplayTurnManager
    from src.gameplay_systems.unit_system import UnitSystem
    from src.gameplay_systems.map_system import MapSystem
    from src.gameplay_systems.movement_system import MovementSystem
    from src.gameplay_systems.combat_system import CombatSystem
    from src.gameplay_systems.inventory_system import InventorySystem
    from src.utils.visual_logger import VisualScenarioLogger


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
    HEAL = auto()


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
        self.turnManager = None # Gameplay TurnManager
        self.coreTurnManager = None # Core Engine TurnManager
        self.visual_logger: Optional['VisualScenarioLogger'] = None # Add visual logger
        self.eventHandler = None
        self.dataProvider = None
        self.ai_vs_ai = False  # Flag for AI vs AI mode
    
    def initialize(self, gameStateManager_instance, unitSystem_instance, mapSystem_instance,
                  movementSystem_instance, combatSystem_instance, inventorySystem_instance,
                  turnManager_instance, eventHandler_instance, dataProvider_instance,
                  core_turn_manager_instance, visual_logger: Optional['VisualScenarioLogger'] = None):
        """
        Initialize the ActionHandler with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            unitSystem_instance: Instance of the UnitSystem
            mapSystem_instance: Instance of the MapSystem
            movementSystem_instance: Instance of the MovementSystem
            combatSystem_instance: Instance of the CombatSystem
            inventorySystem_instance: Instance of the InventorySystem
            turnManager_instance: Instance of the Gameplay TurnManager
            core_turn_manager_instance: Instance of the Core Engine TurnManager
            eventHandler_instance: Instance of the EventHandler
            dataProvider_instance: Instance of the DataProvider
            visual_logger: Optional instance of VisualScenarioLogger
        """
        self.gameStateManager = gameStateManager_instance
        self.unitSystem = unitSystem_instance
        self.mapSystem = mapSystem_instance
        self.movementSystem = movementSystem_instance
        self.combatSystem = combatSystem_instance
        self.inventorySystem = inventorySystem_instance
        self.turnManager = turnManager_instance # Gameplay TurnManager
        self.coreTurnManager = core_turn_manager_instance # Store Core Engine TurnManager
        self.eventHandler = eventHandler_instance
        self.dataProvider = dataProvider_instance
        self.visual_logger = visual_logger # Store visual logger
        
        logging.info("ActionHandler initialized.")
    
    def process_action(self, unit_id: str, action_data: Union[Dict[str, Any], AIAction]) -> bool:
        """
        Process an action for a unit based on the action data.
        
        Args:
            unit_id: ID of the unit performing the action
            action_data: Dictionary or AIAction object containing action type and parameters
            
        Returns:
            True if the action was processed successfully, False otherwise
        """
        
        # Extract action type and target data regardless of input type
        action_type_str = ''
        action_params = {}
        
        if isinstance(action_data, AIAction):
            action_type_str = action_data.action_type
            action_params = action_data.target_data # target_data is already a dict
            logging.debug(f"ActionHandler.process_action received AIAction: type={action_type_str}, params={action_params}")
        elif isinstance(action_data, dict):
            action_type_str = action_data.get('type', '')
            action_params = action_data # The whole dict is the params
            logging.debug(f"ActionHandler.process_action received Dict: type={action_type_str}, params={action_params}")
        else:
            logging.error(f"ActionHandler.process_action received invalid action_data type: {type(action_data)}")
            return False
            
        # Original logging remains useful
        logging.debug(f"ActionHandler.process_action determined action_type_str: '{action_type_str}'")
        
        # Get unit information for logging
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            logging.error(f"Cannot process action: Unit {unit_id} not found")
            return False
            
        # Determine if this is an AI-controlled action in AI vs AI mode
        current_phase = self.gameStateManager.current_game_state.current_phase
        is_ai_controlled = True  # Assume AI-controlled for logging purposes
        faction_label = "PLAYER" if current_phase == PhaseEnum.PLAYER else "ENEMY"
        
        # Convert string action type to ActionType enum
        try:
            # Handle combined actions like MOVE_AND_WAIT
            if action_type_str == 'MOVE_AND_WAIT':
                # Process move action
                # Use action_params dictionary now
                move_data = action_params.get('move_data', {})
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
                move_data = action_params.get('move_data', {})
                move_result = self.handle_move(unit_id, move_data.get('path', []))
                
                if not move_result or not move_result.success:
                    logging.error(f"Move action failed: {move_result.message if move_result else 'Unknown error'}")
                    return False
                
                # Process attack action
                attack_data = action_params.get('action_data', {})
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
            elif action_type_str in ['MOVE', 'WAIT', 'ATTACK', 'CAPTURE', 'ITEM', 'TRADE', 'VISIT', 'SEIZE', 'HEAL']:
                # Map string action type to enum
                action_type_map = {
                    'MOVE': ActionType.MOVE,
                    'WAIT': ActionType.WAIT,
                    'ATTACK': ActionType.ATTACK,
                    'CAPTURE': ActionType.CAPTURE,
                    'ITEM': ActionType.ITEM,
                    'TRADE': ActionType.TRADE,
                    'VISIT': ActionType.VISIT,
                    'SEIZE': ActionType.SEIZE,
                    'HEAL': ActionType.HEAL
                }
                
                action_type = action_type_map.get(action_type_str)
                logging.debug(f"ActionHandler.process_action mapped to action_type: {action_type}") # DEBUG LOGGING
                if not action_type:
                    logging.error(f"Unknown action type: {action_type_str}")
                    return False
                
                # Process the action
                result = self.perform_action(unit_id, action_type, action_params)
                
                if not result or not result.success:
                    logging.error(f"Action failed: {result.message if result else 'Unknown error'}")
                    return False
                
                # Log the action execution with detailed information if it's an AI action
                # Removed - Logging handled elsewhere
                
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
        logging.debug(f"ActionHandler.perform_action dispatching based on action_type: {action_type}") # ADDED DEBUG LOGGING
        logging.debug(f"ActionHandler.perform_action processing action_type: {action_type} with target_data: {target_data}") # DEBUG LOGGING
        
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
        elif action_type == ActionType.HEAL:
            outcome = self.handle_heal(unit_id, target_data.get('target_unit_id'))
        else:
            outcome = ActionOutcome(success=False, message=f"Unsupported action type: {action_type}")
        
        # 3. Post-Action Processing (if successful and action consumes turn)
        if outcome and outcome.success:
            # Trade is a free action and doesn't consume the turn
            if action_type != ActionType.TRADE:
                # Log successful action result here (before potential Canto/MovementStar resets)
                # The specific result details are often logged within the handle_ methods
                # We might log a generic success or let handle_ methods do it.
                # For now, let handle_ methods log specifics.
                
                # Make sure to set the has_acted flag
                unit = self.gameStateManager.get_unit(unit_id)
                if unit:
                    unit.has_acted = True
                
                # Record fatigue for the action using CoreTurnManager
                if self.coreTurnManager:
                    self.coreTurnManager.record_action_fatigue(unit_id, action_type.name)
                else:
                    logging.warning("CoreTurnManager not available for fatigue recording.")
                
                # Check for Canto
                # FIXME: Canto logic needs proper implementation. Temporarily disabled.
                # Ensure this block remains commented out until implemented
                #if self._can_unit_canto(unit_id) and self._is_action_canto_eligible(action_type):
                #    remaining_movement = self._get_remaining_movement(unit_id)
                #    if remaining_movement > 0:
                #        # Set unit state to pending Canto move
                #        self._set_unit_state(unit_id, UnitState.CANTO_MOVE_PENDING)
                #        logging.info(f"{unit.name} can Canto with {remaining_movement} movement remaining.")
                
                # Check for Movement Star (if not Canto pending)
                # Note: check_movement_star might belong to CoreTurnManager as well? Assuming Gameplay TM for now.
                # FIXME: Replace _get_unit_state with proper state check if implemented
                # if not self._get_unit_state(unit_id) == UnitState.CANTO_MOVE_PENDING: 
                if True: # Temporarily bypass Canto check for Movement Star
                    if self.turnManager and hasattr(self.turnManager, 'check_movement_star') and self.turnManager.check_movement_star(unit_id):
                        # Unit state is reset by TurnManager, allow another action
                        unit.has_acted = False
                        unit.has_moved = False
                        # self._set_unit_state(unit_id, UnitState.IDLE) # REMOVED - Method does not exist
        
        # Log failure outcome if visual logger is enabled (if not logged in handle_ method)
        # Note: Most failures should be logged within the specific handle_ method
        # This is tricky, might lead to double logging. Prefer logging in handle_ methods.
        # Example: self.visual_logger.log_action_result(f"Action FAILED: {outcome.message}")
        elif self.visual_logger and outcome and not outcome.success:
            # Check if a more specific message was already logged by handle_ method
            # This is tricky, might lead to double logging. Prefer logging in handle_ methods.
            # Example: self.visual_logger.log_action_result(f"Action FAILED: {outcome.message}")
            pass # Avoid double logging - handle methods should log failures
        
        return outcome
    
    # --- Action Handlers (modified to include logging) ---
    
    def handle_move(self, unit_id: str, path: List[Tuple[int, int]]) -> ActionOutcome:
        """
        Handle a move action.
        
        Args:
            unit_id: ID of the moving unit
            path: List of coordinates representing the movement path
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        log_details = f"to {path[-1] if path else 'invalid destination'} via path length {len(path)}"
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "MOVE", log_details)
        
        # Basic validation
        if not path:
            message = "Move path cannot be empty."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        unit = self.gameStateManager.get_unit(unit_id)
        start_pos = unit.position
        end_pos = path[-1]
        
        # Validate destination using MovementSystem's is_valid_destination
        # Note: Path itself assumed to be valid if generated by a reliable source (e.g., pathfinder)
        if not self.movementSystem.is_valid_destination(unit_id, end_pos):
            message = f"Invalid move destination: {end_pos}."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
        # Execute move
        # Use MovementSystem's execute_move for consistency (if it exists and handles state)
        # Or directly call GameStateManager if MovementSystem doesn't have execute_move
        # success = self.movementSystem.move_unit(unit_id, end_pos) # Assuming move_unit exists in MovementSystem
        success = self.gameStateManager.move_unit(unit_id, end_pos) # Directly use GameStateManager
        
        if success:
            # Mark unit as moved
            unit.has_moved = True
            
            # Record movement fatigue
            if self.coreTurnManager:
                self.coreTurnManager.record_action_fatigue(unit_id, "MOVE")
            
            # Log successful move
            if self.visual_logger:
                self.visual_logger.log_action_result(f"Successfully moved to {end_pos}")
            
            return ActionOutcome(success=True, data={'new_position': end_pos})
        else:
            # This case might indicate an internal error if validation passed
            message = f"Failed to update unit {unit_id} position in GameState."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
    
    def handle_wait(self, unit_id: str) -> ActionOutcome:
        """
        Handle a wait action.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "WAIT")
        
        # Wait action always succeeds if the unit can act
        # The perform_action method already checks if the unit can act
        # and sets the has_acted flag upon successful return.
        if self.visual_logger:
            self.visual_logger.log_action_result("Unit waits.")
        
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
        # Log action start
        target_name = "Unknown Target"
        if target_unit_id:
            target_unit = self.gameStateManager.get_unit(target_unit_id)
            if target_unit: target_name = target_unit.name
        
        log_details = f"on {target_name} ({target_unit_id})"
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "ATTACK", log_details)
        
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
            message = "No weapon equipped."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
        # Check if target is in range
        distance = self._calculate_distance(attacker.position, defender.position)
        weapon_range = self._get_weapon_range(weapon)
        if distance not in weapon_range:
            message = "Target out of range."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
        # Execute combat
        combat_result = self.combatSystem.execute_combat(unit_id, target_unit_id, is_capture=False)
        
        # Log combat results extensively using visual logger
        if self.visual_logger:
            if isinstance(combat_result, list):
                final_outcome_logged = False
                for round_info in combat_result:
                    actor = round_info.get('actor')
                    target = round_info.get('target')
                    damage = round_info.get('damage')
                    hit = round_info.get('hit')
                    crit = round_info.get('crit')
                    target_hp_after = round_info.get('target_hp_after')
                    target_defeated = round_info.get('target_defeated')
                    
                    actor_unit = self.gameStateManager.get_unit(actor)
                    target_unit = self.gameStateManager.get_unit(target)
                    actor_name = actor_unit.name if actor_unit else actor
                    target_name = target_unit.name if target_unit else target
                    
                    if hit:
                        crit_text = " (CRITICAL HIT!)" if crit else ""
                        result_msg = f"{actor_name} hits {target_name} for {damage} damage{crit_text}."
                        if target_defeated:
                            result_msg += f" {target_name} defeated!"
                            final_outcome_logged = True # Final outcome is defeat
                        elif target_hp_after is not None:
                            result_msg += f" ({target_name} HP: {target_hp_after})"
                        self.visual_logger.log_action_result(result_msg)
                    else:
                        self.visual_logger.log_action_result(f"{actor_name}'s attack misses {target_name}.")
                # If no explicit defeat was logged, log the end state if target survived
                if not final_outcome_logged:
                    defender_final = self.gameStateManager.get_unit(target_unit_id) # Re-fetch defender state
                    if defender_final and defender_final.current_hp > 0:
                        self.visual_logger.log_action_result(f"Combat ends. {defender_final.name} HP: {defender_final.current_hp}")
                        
            elif isinstance(combat_result, dict) and 'error' in combat_result:
                self.visual_logger.log_action_result(f"FAILED: {combat_result['error']}")
                return ActionOutcome(success=False, message=combat_result['error'])
            else:
                self.visual_logger.log_action_result(f"Combat finished (details unavailable: {type(combat_result)}).")
        
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
        # Log action start
        target_name = "Unknown Target"
        if target_unit_id:
            target_unit = self.gameStateManager.get_unit(target_unit_id)
            if target_unit: target_name = target_unit.name
        
        log_details = f"on {target_name} ({target_unit_id})"
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "CAPTURE", log_details)
        
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
            message = "No weapon equipped for capture attempt."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
        # Check if target is in range
        distance = self._calculate_distance(attacker.position, target.position)
        weapon_range = self._get_weapon_range(weapon)
        if distance not in weapon_range:
            message = "Target out of range for capture attempt."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
        # Check if target is unarmed or incapacitated (auto-capture)
        target_weapon = self._get_equipped_weapon(target_unit_id)
        if not target_weapon or not self._can_unit_act(target):
            logging.info(f"Target {target.name} is unarmed/incapacitated. Auto-capturing.")
            self._capture_unit(unit_id, target_unit_id)
            if self.visual_logger: self.visual_logger.log_action_result(f"Successfully captured {target.name} (unarmed/incapacitated)." )
            return ActionOutcome(success=True, data={'auto_capture': True})
        
        # Execute capture combat (with penalties)
        combat_result = self.combatSystem.execute_combat(unit_id, target_unit_id, is_capture=True)
        
        # Log combat results similarly to handle_attack
        if self.visual_logger:
            if isinstance(combat_result, list):
                final_outcome_logged = False
                for round_info in combat_result:
                    # (Similar logging logic as in handle_attack)
                    actor = round_info.get('actor')
                    target_ = round_info.get('target') # Use target_ to avoid variable name conflict
                    damage = round_info.get('damage')
                    hit = round_info.get('hit')
                    crit = round_info.get('crit')
                    target_hp_after = round_info.get('target_hp_after')
                    target_defeated = round_info.get('target_defeated') # Capture happens if target is defeated
                    
                    actor_unit = self.gameStateManager.get_unit(actor)
                    target_unit = self.gameStateManager.get_unit(target_)
                    actor_name = actor_unit.name if actor_unit else actor
                    target_name_ = target_unit.name if target_unit else target_ # Use target_name_
                    
                    if hit:
                        crit_text = " (CRITICAL HIT!)" if crit else ""
                        result_msg = f"{actor_name} hits {target_name_} for {damage} damage{crit_text} (Capture)."
                        if target_defeated:
                            # Capture success is handled below, just log defeat here
                            result_msg += f" {target_name_} defeated in capture attempt."
                            final_outcome_logged = True # Final outcome is defeat
                        elif target_hp_after is not None:
                            result_msg += f" ({target_name_} HP: {target_hp_after})"
                        self.visual_logger.log_action_result(result_msg)
                    else:
                        self.visual_logger.log_action_result(f"{actor_name}'s capture attack misses {target_name_}.")
                # Log if target survived
                if not final_outcome_logged:
                    target_final = self.gameStateManager.get_unit(target_unit_id)
                    if target_final and target_final.current_hp > 0:
                        self.visual_logger.log_action_result(f"Capture combat ends. {target_final.name} HP: {target_final.current_hp}")
                        
            elif isinstance(combat_result, dict) and 'error' in combat_result:
                self.visual_logger.log_action_result(f"FAILED: {combat_result['error']}")
                return ActionOutcome(success=False, message=combat_result['error'])
            else:
                self.visual_logger.log_action_result(f"Capture combat finished (details unavailable: {type(combat_result)}).")
        
        # Check capture success based on combat outcome
        if combat_result and isinstance(combat_result, list) and combat_result[-1].get('target_defeated', False):
            if self._capture_unit(unit_id, target_unit_id):
                if self.visual_logger: self.visual_logger.log_action_result(f"Successfully captured {target.name} after combat.")
                return ActionOutcome(success=True, data={'combat_result': combat_result})
            else:
                message = "Target defeated, but failed to apply captured status."
                if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
                return ActionOutcome(success=False, message=message, data={'combat_result': combat_result})
        else:
            # Capture failed (target survived combat)
            message = "Capture attempt failed (target survived combat)."
            # Check if combat system returned an error message
            if combat_result and isinstance(combat_result, dict) and 'message' in combat_result:
                message = f"Capture attempt failed: {combat_result['message']}"
            elif combat_result and not isinstance(combat_result, list): # Handle non-list results that aren't errors explicitly
                message = f"Capture attempt failed (unexpected combat result: {type(combat_result)})."
            
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message, data={'combat_result': combat_result})
    
    def handle_item(self, unit_id: str, item_id: str, target_unit_id: str = None) -> ActionOutcome:
        """
        Handle using an item from the inventory.
        
        Args:
            unit_id: ID of the unit using the item
            item_id: ID of the item being used
            target_unit_id: ID of the target unit (if applicable, e.g., healing staff)
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        self._log_item_start(unit_id, item_id, target_unit_id)
        
        item = self._get_item_from_inventory(unit_id, item_id)
        item_name = item.name if item else f"Item_{item_id}"
        
        # Check if item is usable
        item_data = self.dataProvider.get_item_data(item_id)
        if not item_data or not item_data.is_usable:
            message = f"Item {item_name} is not usable."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check durability
        if item.durability is not None and item.durability <= 0:
            message = f"Item {item_name} has no remaining uses."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # --- Action Specific Logic (Example: Healing Item) ---
        # This would ideally be handled by a dedicated ItemSystem or effect handlers
        # For demonstration, let's assume a simple healing item effect
        if item_data.effect == "HEAL":
            heal_amount = item_data.effect_potency.get("heal_amount", 10)
            target_id_to_heal = target_unit_id if target_unit_id else unit_id # Self-heal if no target
            
            heal_outcome = self.handle_heal(unit_id, target_id_to_heal, source_item=item) # Pass item for durability
            
            # handle_heal should do its own logging, but we confirm item use here
            if heal_outcome.success:
                if self.visual_logger: self.visual_logger.log_action_result(f"Used {item_name}. {heal_outcome.message}")
                # Decrement durability handled within handle_heal or item system ideally
                return ActionOutcome(success=True, data={'heal_result': heal_outcome.data})
            else:
                # Failure already logged by handle_heal
                return ActionOutcome(success=False, message=f"Failed to use {item_name}: {heal_outcome.message}")
        else:
            # Placeholder for other item effects
            message = f"Item effect '{item_data.effect}' not implemented."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
    
    def handle_trade(self, unit_id: str, partner_unit_id: str, item_transfers: List) -> ActionOutcome:
        """
        Handle trading items between two adjacent units.
        
        Args:
            unit_id: ID of the unit initiating the trade
            partner_unit_id: ID of the trading partner unit
            item_transfers: List of items to transfer (details depend on InventorySystem)
            
        Returns:
            ActionOutcome object (Trade is usually a free action, success doesn't set has_acted)
        """
        # Log action start
        self._log_trade_start(unit_id, partner_unit_id)
        
        partner_unit = self.gameStateManager.get_unit(partner_unit_id)
        partner_name = partner_unit.name if partner_unit else f"Unit_{partner_unit_id}"
        
        # Basic validation
        unit = self.gameStateManager.get_unit(unit_id)
        if not partner_unit:
            message = "Trading partner not found."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check adjacency
        distance = self._calculate_distance(unit.position, partner_unit.position)
        if distance != 1:
            message = "Units must be adjacent to trade."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if units are valid trading partners (e.g., same faction or specific event)
        if unit.faction != partner_unit.faction:
             message = "Cannot trade with units of different factions."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)

        # Execute trade via InventorySystem
        trade_success = self.inventorySystem.execute_trade(unit_id, partner_unit_id, item_transfers)
        
        if trade_success:
            if self.visual_logger: self.visual_logger.log_action_result(f"Successfully traded items with {partner_name}.")
            # Trade does NOT set unit.has_acted = True
            return ActionOutcome(success=True)
        else:
            # InventorySystem should provide a more specific error message ideally
            message = "Trade failed (e.g., inventory full, item invalid)."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
    
    def handle_rescue(self, unit_id: str, target_unit_id: str) -> ActionOutcome:
        """
        Handle rescuing an adjacent, valid target unit.
        
        Args:
            unit_id: ID of the rescuing unit
            target_unit_id: ID of the unit to be rescued
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        self._log_rescue_start(unit_id, target_unit_id)
        
        target_unit = self.gameStateManager.get_unit(target_unit_id)
        target_name = target_unit.name if target_unit else f"Unit_{target_unit_id}"
        
        # Basic validation
        unit = self.gameStateManager.get_unit(unit_id)
        if not target_unit:
            message = "Rescue target not found."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check adjacency
        if self._calculate_distance(unit.position, target_unit.position) != 1:
            message = "Target must be adjacent to rescue."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if rescuer can rescue (not carrying anyone)
        if self._get_captive_unit(unit_id):
            message = "Cannot rescue while carrying another unit."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if target can be rescued (not mounted, not carrying, CON check)
        if self.gameStateManager.is_unit_mounted(target_unit_id):
             message = "Cannot rescue a mounted unit."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
        if self._get_captive_unit(target_unit_id):
             message = "Cannot rescue a unit carrying another."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
             
        # CON Check: Rescuer CON > Target CON (unless Rescuer is Mounted)
        rescuer_con = unit.base_stats.get('CON', 0)
        target_con = target_unit.base_stats.get('CON', 0)
        can_rescue_by_mount = self.gameStateManager.is_unit_mounted(unit_id)
        if not (rescuer_con > target_con or can_rescue_by_mount):
             message = "Constitution too low to rescue target."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
        
        # Execute rescue
        if self._rescue_unit(unit_id, target_unit_id):
            if self.visual_logger: self.visual_logger.log_action_result(f"Successfully rescued {target_name}.")
            return ActionOutcome(success=True)
        else:
            # _rescue_unit should ideally provide a reason
            message = "Rescue failed (internal error)."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
    
    def handle_drop(self, unit_id: str, target_tile: Tuple[int, int]) -> ActionOutcome:
        """
        Handle dropping a carried unit onto an adjacent, valid tile.
        
        Args:
            unit_id: ID of the unit dropping the captive
            target_tile: The (x, y) coordinates to drop the unit onto
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        self._log_drop_start(unit_id, target_tile)
        
        captive_unit = self._get_captive_unit(unit_id)
        captive_name = captive_unit.name if captive_unit else "Unknown Captive"
        
        unit = self.gameStateManager.get_unit(unit_id)
        
        # Check adjacency of target tile
        if self._calculate_distance(unit.position, target_tile) != 1:
            message = "Drop location must be adjacent."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if target tile is valid drop location (passable, unoccupied)
        if not self.mapSystem.is_tile_passable(target_tile, unit): # Check passability for dropping unit
             message = "Drop location is impassable."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
             
        if self._is_tile_occupied(target_tile):
             message = "Drop location is occupied."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
        
        # Execute drop
        if self._drop_unit(unit_id, target_tile):
            if self.visual_logger: self.visual_logger.log_action_result(f"Successfully dropped {captive_name} at {target_tile}.")
            return ActionOutcome(success=True)
        else:
            message = "Drop failed (internal error)."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
    
    def handle_take(self, unit_id: str, partner_unit_id: str) -> ActionOutcome:
        """
        Handle taking a captive unit from an adjacent ally.
        
        Args:
            unit_id: ID of the unit taking the captive
            partner_unit_id: ID of the unit currently carrying the captive
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        self._log_take_start(unit_id, partner_unit_id)

        # Basic validation
        unit = self.gameStateManager.get_unit(unit_id)
        partner_unit = self.gameStateManager.get_unit(partner_unit_id)
        captive_unit = self._get_captive_unit(partner_unit_id)
        if not partner_unit:
            message = "Partner unit not found."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        if not captive_unit:
            message = f"{partner_unit.name} is not carrying anyone."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check adjacency
        if self._calculate_distance(unit.position, partner_unit.position) != 1:
            message = "Units must be adjacent to take captive."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if taker can take (not carrying anyone)
        if self._get_captive_unit(unit_id):
            message = "Cannot take captive while carrying another unit."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check CON requirement (Taker CON > Captive CON unless Taker is Mounted)
        taker_con = unit.base_stats.get('CON', 0)
        captive_con = captive_unit.base_stats.get('CON', 0)
        can_take_by_mount = self.gameStateManager.is_unit_mounted(unit_id)
        if not (taker_con > captive_con or can_take_by_mount):
             message = "Constitution too low to take this captive."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
        
        # Execute take
        if self._take_unit(unit_id, partner_unit_id):
            captive_name = captive_unit.name
            partner_name = partner_unit.name
            if self.visual_logger: self.visual_logger.log_action_result(f"Successfully took {captive_name} from {partner_name}.")
            return ActionOutcome(success=True)
        else:
             message = "Take failed (internal error)."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
    
    def handle_release(self, unit_id: str) -> ActionOutcome:
        """
        Handle releasing a captured enemy unit.
        
        Args:
            unit_id: ID of the unit carrying the captive to be released
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        captive_unit = self._get_captive_unit(unit_id)
        captive_name = captive_unit.name if captive_unit else "Unknown Captive"
        log_details = f"captive {captive_name}"
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "RELEASE", log_details)
            
        # Basic validation
        if not captive_unit:
            message = "Unit is not carrying anyone to release."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Can only release captured enemies
        if captive_unit.faction != FactionEnum.ENEMY:
             message = "Can only release captured enemies (not rescued allies)."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
        
        # Execute release
        if self._release_captive(unit_id): # Assumes release simply removes the captive
             if self.visual_logger: self.visual_logger.log_action_result(f"Successfully released captive {captive_name}.")
             return ActionOutcome(success=True)
        else:
             message = "Release failed (internal error)."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
    
    def handle_dismount(self, unit_id: str) -> ActionOutcome:
        """
        Handle dismounting a mounted unit.
        
        Args:
            unit_id: ID of the mounted unit
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "DISMOUNT")

        # Basic validation
        if not self.gameStateManager.is_unit_mounted(unit_id):
            message = "Unit is not mounted."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
        # Find adjacent valid tile to dismount to (similar to drop)
        # This logic might need refinement - pick best tile? let player choose?
        adjacent_tiles = self._get_adjacent_tiles(self.gameStateManager.get_unit(unit_id).position)
        valid_dismount_tile = None
        for tile in adjacent_tiles:
            if self.mapSystem.is_tile_passable(tile, self.gameStateManager.get_unit(unit_id)) and not self._is_tile_occupied(tile):
                valid_dismount_tile = tile
                break

        if not valid_dismount_tile:
            message = "No valid adjacent tile to dismount onto."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Execute dismount
        if self._dismount_unit(unit_id, valid_dismount_tile):
             if self.visual_logger: self.visual_logger.log_action_result(f"Successfully dismounted to {valid_dismount_tile}.")
             return ActionOutcome(success=True, data={'dismount_pos': valid_dismount_tile})
        else:
             message = "Dismount failed (internal error)."
             if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
             return ActionOutcome(success=False, message=message)
    
    def handle_mount(self, unit_id: str) -> ActionOutcome:
        """
        Handle mounting for a dismounted unit.
        
        Args:
            unit_id: ID of the dismounted unit
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "MOUNT")

        # Basic validation
        if self.gameStateManager.is_unit_mounted(unit_id):
            message = "Unit is already mounted."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if unit is eligible to mount (e.g., specific class, has mount 'item')
        if not self._can_unit_mount(unit_id):
            message = "Unit cannot mount."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check terrain (e.g., cannot mount indoors?)
        # TBD: Add terrain check logic if applicable
        
        # Execute mount
        if self._mount_unit(unit_id):
            if self.visual_logger: self.visual_logger.log_action_result(f"Successfully mounted.")
            return ActionOutcome(success=True)
        else:
            message = "Mount failed (internal error)."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
    
    def handle_visit(self, unit_id: str, target_tile: Tuple[int, int]) -> ActionOutcome:
        """
        Handle visiting a feature (village, house, etc.) at the target tile.
        
        Args:
            unit_id: ID of the visiting unit
            target_tile: The (x, y) coordinates of the feature to visit
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        self._log_visit_start(unit_id, target_tile)
        
        feature = self._get_tile_feature(target_tile)
        feature_type = feature.get('type', 'Unknown Feature') if feature else 'No Feature'
        
        unit = self.gameStateManager.get_unit(unit_id)
        if unit.position != target_tile:
            message = "Unit must be on the target tile to visit."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)

        if not feature:
            message = f"No visitable feature at {target_tile}."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        if feature.get('visited', False):
            message = f"Feature '{feature_type}' at {target_tile} has already been visited."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
             
        # Trigger event associated with visiting
        event_id = feature.get('event_id')
        if event_id and self.eventHandler:
            # Mark feature as visited *before* triggering event to prevent re-triggering
            self._mark_feature_as_visited(target_tile)
            
            self.eventHandler.trigger_event(event_id, context={'unit_id': unit_id, 'tile': target_tile})
            if self.visual_logger: self.visual_logger.log_action_result(f"Visited {feature_type} at {target_tile}, triggered event {event_id}.")
            return ActionOutcome(success=True, data={'event_triggered': event_id})
        elif event_id:
            message = f"Visit failed: EventHandler not available to trigger event {event_id}."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        else:
            # If no event, just mark as visited (e.g., simple healing house)
            self._mark_feature_as_visited(target_tile)
            if self.visual_logger: self.visual_logger.log_action_result(f"Visited {feature_type} at {target_tile} (no event).")
            return ActionOutcome(success=True)
    
    def handle_seize(self, unit_id: str, target_tile: Tuple[int, int]) -> ActionOutcome:
        """
        Handle seizing a specific point (throne, gate) by the lord unit.
        
        Args:
            unit_id: ID of the seizing unit (must be the lord)
            target_tile: The (x, y) coordinates of the seize point
            
        Returns:
            ActionOutcome object
        """
        # Log action start
        self._log_seize_start(unit_id, target_tile)
        
        # Basic validation
        unit = self.gameStateManager.get_unit(unit_id)
        if not self._is_lord(unit_id):
            message = "Only the lord can seize."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
        if unit.position != target_tile:
            message = "Lord must be on the target tile to seize."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
             
        # Check if the tile is a seize point
        # This might involve checking MapData or a specific property from MapSystem
        # Assume mapSystem has a method is_seize_point(tile)
        if not self.mapSystem.is_seize_point(target_tile):
            message = f"Tile {target_tile} is not a seize point."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Seizing usually triggers a victory/chapter end event
        # Let EventHandler handle victory conditions based on seize
        if self.eventHandler:
            # Trigger a generic "Seize" event or check conditions directly
            self.eventHandler.check_victory_conditions(self.gameStateManager, self.coreTurnManager.get_current_turn())
            # Assuming the event handler sets game state flags
            if self.gameStateManager.current_game_state.event_flags.get('victory_achieved', False):
                if self.visual_logger: self.visual_logger.log_action_result(f"Successfully seized {target_tile}! Victory achieved.")
                return ActionOutcome(success=True, data={'victory': True})
            else:
                # This case shouldn't normally happen if seize = victory
                message = "Seized point, but victory condition not triggered."
                if self.visual_logger: self.visual_logger.log_action_result(f"INFO: {message}")
                return ActionOutcome(success=True, message=message) # Technically successful action
        else:
            message = "Seize failed: EventHandler not available to check victory."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
    
    def handle_talk(self, unit_id: str, target_unit_id: str) -> ActionOutcome:
        """
        Handle a talk interaction between two adjacent units.
            
        Args:
            unit_id: ID of the unit initiating the talk
            target_unit_id: ID of the target unit
                
        Returns:
            ActionOutcome object
        """
        # Log action start
        target_unit = self.gameStateManager.get_unit(target_unit_id)
        target_name = target_unit.name if target_unit else f"Unit_{target_unit_id}"
        log_details = f"with {target_name} ({target_unit_id})"
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "TALK", log_details)
            
        # Basic validation
        unit = self.gameStateManager.get_unit(unit_id)
        if not target_unit:
            message = "Talk target not found."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check adjacency
        if self._calculate_distance(unit.position, target_unit.position) != 1:
            message = "Units must be adjacent to talk."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if a talk event exists for this pair
        if self.eventHandler:
            event_id = self.eventHandler.find_talk_event(unit_id, target_unit_id)
            if event_id:
                # Mark event as potentially triggered (EventHandler might handle single trigger)
                self.eventHandler.trigger_event(event_id, context={'unit1': unit_id, 'unit2': target_unit_id})
                if self.visual_logger: self.visual_logger.log_action_result(f"Talked with {target_name}, triggered event {event_id}.")
                return ActionOutcome(success=True, data={'event_triggered': event_id})
            else:
                message = f"No talk event found between {unit.name} and {target_name}."
                if self.visual_logger: self.visual_logger.log_action_result(f"INFO: {message}")
                # Still a successful 'Talk' action even if no event, consumes turn
                return ActionOutcome(success=True, message=message)
        else:
            message = "Talk failed: EventHandler not available."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)

    def handle_steal(self, unit_id: str, target_unit_id: str, item_id: str) -> ActionOutcome:
        """
        Handle stealing an item from an adjacent enemy unit.
        
        Args:
            unit_id: ID of the stealing unit (thief)
            target_unit_id: ID of the target unit
            item_id: ID of the item to steal
                
        Returns:
            ActionOutcome object
        """
        # Log action start
        target_unit = self.gameStateManager.get_unit(target_unit_id)
        target_name = target_unit.name if target_unit else f"Unit_{target_unit_id}"
        item_instance = self._get_item_from_inventory(target_unit_id, item_id)
        item_name = item_instance.name if item_instance else f"Item_{item_id}"
        log_details = f"item {item_name} ({item_id}) from {target_name} ({target_unit_id})"
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "STEAL", log_details)
            
        # Basic validation
        unit = self.gameStateManager.get_unit(unit_id)
        if not target_unit:
            message = "Steal target not found."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        if not item_instance:
            message = f"Item {item_name} not found in target's inventory."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)

        # Check adjacency
        if self._calculate_distance(unit.position, target_unit.position) != 1:
            message = "Units must be adjacent to steal."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if unit is a thief
        if not self._has_steal_skill(unit_id):
            message = "Unit cannot steal (missing Steal skill)."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if target is enemy
        if target_unit.faction == FactionEnum.PLAYER or target_unit.faction == FactionEnum.NPC:
            message = "Cannot steal from allies."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
             
        # Check speed requirement (Thief SPD > Target SPD)
        thief_spd = self.unitSystem.get_unit_calculated_stats(unit_id)['AS']
        target_spd = self.unitSystem.get_unit_calculated_stats(target_unit_id)['AS']
        if not thief_spd > target_spd:
            message = f"Cannot steal: Thief Speed ({thief_spd}) must be greater than Target Speed ({target_spd})."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
             
        # Check inventory space
        if self._is_inventory_full(unit_id):
            message = "Cannot steal: Inventory is full."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if item is stealable (not equipped weapon/essential item?)
        # TODO: Add logic to check if item_id is stealable
        
        # Execute steal via InventorySystem
        steal_success = self.inventorySystem.transfer_item(target_unit_id, unit_id, item_id)
        
        if steal_success:
            if self.visual_logger: self.visual_logger.log_action_result(f"Successfully stole {item_name} from {target_name}.")
            return ActionOutcome(success=True)
        else:
            message = "Steal failed (internal inventory transfer error)."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
    def handle_open_door(self, unit_id: str, target_tile: Tuple[int, int], key_item_id: str = None) -> ActionOutcome:
        """
        Handle opening a door at the target tile using a key or skill.
            
        Args:
            unit_id: ID of the unit opening the door
            target_tile: The (x, y) coordinates of the door
            key_item_id: Optional ID of the key item used
                
        Returns:
            ActionOutcome object
        """
        # Log action start
        log_details = f"at {target_tile}"
        if key_item_id:
            key_item = self._get_item_from_inventory(unit_id, key_item_id)
            key_name = key_item.name if key_item else f"Key_{key_item_id}"
            log_details += f" using {key_name}"
        else:
            log_details += f" using skill"
            
        if self.visual_logger:
            self.visual_logger.log_action(unit_id, "OPEN_DOOR", log_details)
            
        # Basic validation
        unit = self.gameStateManager.get_unit(unit_id)
            
        # Check adjacency to door
        if self._calculate_distance(unit.position, target_tile) != 1:
            message = "Must be adjacent to the door to open it."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
            
        # Check if target tile is a closed door
        # Assume mapSystem has get_terrain_properties and it returns a dict with 'type' and 'state'
        terrain_props = self.mapSystem.get_terrain_properties(target_tile)
        if not terrain_props or terrain_props.get('type') != 'DOOR' or terrain_props.get('state') != 'CLOSED':
            message = f"Tile {target_tile} is not a closed door."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
             
        # Check if unit can open (has key or Lockpick skill)
        has_key = False
        if key_item_id:
            key_item = self._get_item_from_inventory(unit_id, key_item_id)
            # TODO: Check if key_item is the correct key for this door type?
            if key_item and key_item.durability is not None and key_item.durability > 0:
                has_key = True
            else:
                key_name = key_item.name if key_item else f"Key_{key_item_id}"
                message = f"Invalid or used key: {key_name}."
                if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
                return ActionOutcome(success=False, message=message)
        
        has_lockpick = self._has_lockpick_skill(unit_id)
        
        if not has_key and not has_lockpick:
            message = "Cannot open door (needs key or Lockpick skill)."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
        # Execute open door (change map state)
        if self._open_door(target_tile):
            # Consume key durability if used
            if has_key and key_item:
                self.inventorySystem.decrement_item_durability(unit_id, key_item_id)
                
            if self.visual_logger: self.visual_logger.log_action_result(f"Successfully opened door at {target_tile}.")
            return ActionOutcome(success=True)
        else:
            message = "Failed to open door (internal map update error)."
            if self.visual_logger: self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
    
    def handle_heal(self, unit_id: str, target_unit_id: str, source_item=None) -> ActionOutcome:
        """
        Handle healing between units
        
        Args:
            unit_id: ID of the healing unit
            target_unit_id: ID of the unit being healed
            source_item: Optional healing item/staff
            
        Returns:
            ActionOutcome object indicating success/failure
        """
        # Validation checks would go here
        
        # Implementation
        target_unit = self.gameStateManager.get_unit(target_unit_id)
        if not target_unit:
            message = f"Target unit {target_unit_id} not found."
            if self.visual_logger:
                self.visual_logger.log_action_result(f"FAILED: {message}")
            return ActionOutcome(success=False, message=message)
        
        # Check if target already at max health
        if target_unit.current_hp >= target_unit.max_hp:
            message = f"{target_unit.name} is already at full health."
            if self.visual_logger:
                self.visual_logger.log_action_result(f"INFO: {message}")
            return ActionOutcome(success=True, message=message)
        
        # Calculate healing amount based on staff/item/skill
        healing_amount = 10  # Default placeholder
        if source_item and hasattr(source_item, 'healing_amount'):
            healing_amount = source_item.healing_amount
        
        # Apply healing
        new_hp = min(target_unit.current_hp + healing_amount, target_unit.max_hp)
        actual_healing = new_hp - target_unit.current_hp
        
        # Update the target unit's HP
        self.gameStateManager.update_unit_hp(target_unit_id, new_hp)
        
        # Log the result
        message = f"Healed {target_unit.name} for {actual_healing} HP."
        if self.visual_logger:
            self.visual_logger.log_action_result(message)
        
        return ActionOutcome(success=True, message=message)

    # --- Internal Helper Methods ---

    def _log_item_start(self, unit_id: str, item_id: str, target_unit_id: Optional[str]):
        if not self.visual_logger: return
        item = self._get_item_from_inventory(unit_id, item_id)
        item_name = item.name if item else f"Item_{item_id}"
        log_details = f"item {item_name} ({item_id})"
        if target_unit_id:
            target_unit = self.gameStateManager.get_unit(target_unit_id)
            target_name = target_unit.name if target_unit else f"Unit_{target_unit_id}"
            log_details += f" on {target_name} ({target_unit_id})"
        self.visual_logger.log_action(unit_id, "ITEM", log_details)
        
    def _log_trade_start(self, unit_id: str, partner_unit_id: str):
        if not self.visual_logger: return
        partner_unit = self.gameStateManager.get_unit(partner_unit_id)
        partner_name = partner_unit.name if partner_unit else f"Unit_{partner_unit_id}"
        log_details = f"with {partner_name} ({partner_unit_id})"
        self.visual_logger.log_action(unit_id, "TRADE", log_details)
        
    def _log_rescue_start(self, unit_id: str, target_unit_id: str):
        if not self.visual_logger: return
        target_unit = self.gameStateManager.get_unit(target_unit_id)
        target_name = target_unit.name if target_unit else f"Unit_{target_unit_id}"
        log_details = f"target {target_name} ({target_unit_id})"
        self.visual_logger.log_action(unit_id, "RESCUE", log_details)
        
    def _log_drop_start(self, unit_id: str, target_tile: Tuple[int, int]):
        if not self.visual_logger: return
        captive_unit = self._get_captive_unit(unit_id)
        captive_name = captive_unit.name if captive_unit else "Unknown Captive"
        log_details = f"captive {captive_name} at {target_tile}"
        self.visual_logger.log_action(unit_id, "DROP", log_details)

    def _log_visit_start(self, unit_id: str, target_tile: Tuple[int, int]):
        if not self.visual_logger: return
        feature = self._get_tile_feature(target_tile)
        feature_type = feature.get('type', 'Unknown Feature') if feature else 'No Feature'
        log_details = f"feature '{feature_type}' at {target_tile}"
        self.visual_logger.log_action(unit_id, "VISIT", log_details)
        
    def _log_seize_start(self, unit_id: str, target_tile: Tuple[int, int]):
        if not self.visual_logger: return
        log_details = f"point at {target_tile}"
        self.visual_logger.log_action(unit_id, "SEIZE", log_details)

    def _log_take_start(self, unit_id: str, partner_unit_id: str):
        if not self.visual_logger: return
        partner_unit = self.gameStateManager.get_unit(partner_unit_id)
        partner_name = partner_unit.name if partner_unit else f"Unit_{partner_unit_id}"
        captive_unit = self._get_captive_unit(partner_unit_id)
        captive_name = captive_unit.name if captive_unit else "Unknown Captive"
        log_details = f"captive {captive_name} from {partner_name} ({partner_unit_id})"
        self.visual_logger.log_action(unit_id, "TAKE", log_details)
        
    def _log_release_start(self, unit_id: str):
        if not self.visual_logger: return
        captive_unit = self._get_captive_unit(unit_id)
        captive_name = captive_unit.name if captive_unit else "Unknown Captive"
        log_details = f"captive {captive_name}"
        self.visual_logger.log_action(unit_id, "RELEASE", log_details)
        
    def _log_dismount_start(self, unit_id: str):
        if not self.visual_logger: return
        self.visual_logger.log_action(unit_id, "DISMOUNT")
        
    def _log_mount_start(self, unit_id: str):
        if not self.visual_logger: return
        self.visual_logger.log_action(unit_id, "MOUNT")
        
    def _log_talk_start(self, unit_id: str, target_unit_id: str):
        if not self.visual_logger: return
        target_unit = self.gameStateManager.get_unit(target_unit_id)
        target_name = target_unit.name if target_unit else f"Unit_{target_unit_id}"
        log_details = f"with {target_name} ({target_unit_id})"
        self.visual_logger.log_action(unit_id, "TALK", log_details)
        
    def _log_steal_start(self, unit_id: str, target_unit_id: str, item_id: str):
        if not self.visual_logger: return
        target_unit = self.gameStateManager.get_unit(target_unit_id)
        target_name = target_unit.name if target_unit else f"Unit_{target_unit_id}"
        item_instance = self._get_item_from_inventory(target_unit_id, item_id)
        item_name = item_instance.name if item_instance else f"Item_{item_id}"
        log_details = f"item {item_name} ({item_id}) from {target_name} ({target_unit_id})"
        self.visual_logger.log_action(unit_id, "STEAL", log_details)
        
    def _log_open_door_start(self, unit_id: str, target_tile: Tuple[int, int], key_item_id: Optional[str]):
        if not self.visual_logger: return
        log_details = f"at {target_tile}"
        if key_item_id:
            key_item = self._get_item_from_inventory(unit_id, key_item_id)
            key_name = key_item.name if key_item else f"Key_{key_item_id}"
            log_details += f" using {key_name}"
        else:
            log_details += f" using skill"
        self.visual_logger.log_action(unit_id, "OPEN_DOOR", log_details)
        
    def _log_heal_start(self, unit_id: str, target_unit_id: str, source_item=None):
        if not self.visual_logger: return
        target_unit = self.gameStateManager.get_unit(target_unit_id)
        target_name = target_unit.name if target_unit else f"Unit_{target_unit_id}"
        source_name = f"item {source_item.name}" if source_item else "staff"
        log_details = f"target {target_name} ({target_unit_id}) using {source_name}"
        self.visual_logger.log_action(unit_id, "HEAL", log_details)

    def _can_unit_act(self, unit: Any) -> bool:
        """
        Check if a unit can act (not affected by disabling status effects).
        Args:
            unit: The unit object (from GameStateManager)
        Returns:
            True if the unit can act, False otherwise
        """
        if not unit:
            return False
        # Check for statuses like Sleep, Petrify, etc.
        # Assuming unit is a UnitState object which has the has_status method
        # Use StatusEffectEnum directly
        return not unit.has_status(StatusEffectEnum.SLEEP) and not unit.has_status(StatusEffectEnum.PETRIFY)
    
    def _is_correct_phase_for_faction(self, current_phase: PhaseEnum, unit_faction: FactionEnum) -> bool:
        """
        Check if the unit's faction matches the current game phase.
        Args:
            current_phase: The current PhaseEnum
            unit_faction: The FactionEnum of the unit
        Returns:
            True if the unit's faction can act in the current phase, False otherwise
        """
        if current_phase == PhaseEnum.PLAYER and unit_faction == FactionEnum.PLAYER:
            return True
        if current_phase == PhaseEnum.ENEMY and unit_faction == FactionEnum.ENEMY:
            return True
        if current_phase == PhaseEnum.NPC and unit_faction == FactionEnum.NPC:
            return True
        # Add other phase/faction rules if necessary (e.g., Event phase)
        return False
