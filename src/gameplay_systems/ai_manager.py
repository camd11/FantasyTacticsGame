"""
AI Manager Module

This module manages the AI behavior for enemy and NPC units. It determines the best actions
for AI-controlled units based on their AI profiles, current game state, and tactical situation.
It serves as the main facade for the AI subsystem, coordinating between specialized components
like profile management, action evaluation, and archetype-specific handlers.
"""

import logging
import random
from typing import Dict, List, Tuple, Optional, Any, Set, Union

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.gameplay_systems.ai.ai_types import AIBehaviorType, AITargetPriority, AIProfile, AIAction
from src.gameplay_systems.ai.ai_profile_manager import AIProfileManager
from src.gameplay_systems.ai.ai_action_evaluator import AIActionEvaluator
from src.gameplay_systems.ai.ai_action_scoring import AIActionScoring
from src.gameplay_systems.ai.ai_action_scoring_helpers import AIActionScoringHelpers
from src.gameplay_systems.ai.archetype_handlers.thief_loot_handler import ThiefLootArchetypeHandler
from src.gameplay_systems.ai.archetype_handlers.heal_support_handler import HealSupportArchetypeHandler
from src.gameplay_systems.ai.archetype_handlers.guard_handler import GuardArchetypeHandler
from src.gameplay_systems.ai.archetype_handlers.charge_handler import ChargeArchetypeHandler


class AIManager:
    """
    Manages the AI behavior for enemy and NPC units. Determines the best actions
    for AI-controlled units based on their AI profiles, current game state, and tactical situation.
    
    This class acts as a facade that delegates to specialized classes for different aspects of AI behavior:
    - AIProfileManager: Manages AI profiles and behavior configurations
    - AIActionEvaluator: Discovers and evaluates possible actions
    - AIActionScoring: Scores combat and other actions
    - AIActionScoringHelpers: Provides utility functions for scoring
    - Archetype Handlers: Implement behavior patterns for different unit types
    
    The AIManager coordinates these components to provide a cohesive AI decision-making
    system that selects appropriate actions based on unit type, tactical situation,
    and strategic objectives.
    """
    
    def __init__(self):
        """
        Initialize the AIManager.
        
        Sets up the initial state with empty references to game systems and specialized
        AI components. These references will be populated when initialize() is called.
        """
        self.gameStateManager = None
        self.unitSystem = None
        self.mapSystem = None
        self.movementSystem = None
        self.combatSystem = None
        self.actionHandler = None
        self.dataProvider = None
        self.inventorySystem = None
        self.debug_mode = True  # Enable debug logging
        
        # State
        self.last_attackers = {}    # unit_id -> attacker_unit_id
        
        # Specialized components
        self.profile_manager = None
        self.action_evaluator = None
        self.action_scoring = None
        self.action_scoring_helpers = None
        self.archetype_handlers = []
    
    def initialize(self, gameStateManager_instance, unitSystem_instance, mapSystem_instance,
                  movementSystem_instance, combatSystem_instance, actionHandler_instance,
                  dataProvider_instance, inventorySystem_instance=None):
        """
        Initialize the AIManager with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            unitSystem_instance: Instance of the UnitSystem
            mapSystem_instance: Instance of the MapSystem
            movementSystem_instance: Instance of the MovementSystem
            combatSystem_instance: Instance of the CombatSystem
            actionHandler_instance: Instance of the ActionHandler
            dataProvider_instance: Instance of the DataProvider
            inventorySystem_instance: Instance of the InventorySystem (optional)
        """
        self.gameStateManager = gameStateManager_instance
        self.unitSystem = unitSystem_instance
        self.mapSystem = mapSystem_instance
        self.movementSystem = movementSystem_instance
        self.combatSystem = combatSystem_instance
        self.actionHandler = actionHandler_instance
        self.dataProvider = dataProvider_instance
        self.inventorySystem = inventorySystem_instance
        
        # Initialize state
        self.last_attackers = {}    # unit_id -> attacker_unit_id
        
        # Initialize specialized components
        self.profile_manager = AIProfileManager()
        self.profile_manager.initialize(self.gameStateManager, self.dataProvider)
        
        self.action_evaluator = AIActionEvaluator()
        self.action_evaluator.initialize(
            self.gameStateManager, self.unitSystem, self.mapSystem, 
            self.movementSystem, self.combatSystem, self.inventorySystem, 
            self.dataProvider
        )
        
        self.action_scoring = AIActionScoring(
            self.gameStateManager, self.unitSystem, self.mapSystem, 
            self.combatSystem, self.inventorySystem, self.dataProvider
        )
        
        self.action_scoring_helpers = AIActionScoringHelpers(
            self.gameStateManager, self.unitSystem, self.mapSystem, 
            self.combatSystem, self.inventorySystem, self.dataProvider
        )
        
        # Initialize archetype handlers
        self.archetype_handlers = [
            ThiefLootArchetypeHandler(
                self.gameStateManager, self.unitSystem, self.mapSystem, 
                self.movementSystem, self.combatSystem, self.inventorySystem, 
                self.dataProvider
            ),
            HealSupportArchetypeHandler(
                self.gameStateManager, self.unitSystem, self.mapSystem, 
                self.movementSystem, self.combatSystem, self.inventorySystem, 
                self.dataProvider
            ),
            GuardArchetypeHandler(
                self.gameStateManager, self.unitSystem, self.mapSystem, 
                self.movementSystem, self.combatSystem, self.inventorySystem, 
                self.dataProvider
            ),
            ChargeArchetypeHandler(
                self.gameStateManager, self.unitSystem, self.mapSystem, 
                self.movementSystem, self.combatSystem, self.inventorySystem, 
                self.dataProvider
            )
        ]
        
        # Don't load profiles here, wait until chapter is initialized
        # self.profile_manager.load_ai_profiles()
        
        logging.info("AIManager initialized.")
    
    # --- AI Profile Management ---
    
    def _load_ai_profiles(self):
        """
        Load AI profiles for all units from the DataProvider.
        
        Delegates to the profile_manager to load and initialize AI profiles
        for all units in the current game state.
        """
        self.profile_manager.load_ai_profiles()
    
    def change_unit_ai(self, unit_id: str, new_ai_profile: Dict):
        """
        Change the AI profile for a unit.
        
        Args:
            unit_id: ID of the unit
            new_ai_profile: New AI profile data
        """
        self.profile_manager.change_unit_ai(unit_id, new_ai_profile)
    
    # --- AI Decision Making ---
    
    def determine_action(self, unit, game_state_manager):
        """
        Determine the best action for a unit based on AI logic.
        This method is used by the EngineCore for AI vs AI mode.
        
        The method ensures the unit has a valid AI profile, then delegates to
        archetype-specific handlers to determine the most appropriate action
        based on the unit's behavior type and the current game state.
        
        Args:
            unit: The unit to determine an action for
            game_state_manager: Instance of the GameStateManager
            
        Returns:
            Dict containing the action data or None if no action is possible.
            The action data includes the action type, target information, and
            any movement path required.
        """
        unit_id = unit.id
        
        # Ensure we have a valid AI profile for this unit
        ai_profile = self.profile_manager.ensure_profile_exists(unit_id)
            
        if not unit or not ai_profile:
            logging.warning(f"Cannot determine action for unit {unit_id}: Unit or AI profile not found")
            return None
        
        if self.debug_mode:
            logging.info(f"Determining action for: {unit.name} (AI: {ai_profile.behavior_type.name})")
        
        # Temporarily store the current game state manager to ensure we're using the right one
        original_gsm = self.gameStateManager
        self.gameStateManager = game_state_manager
        logging.info(f"AI DEBUGGING: Processing unit {unit.name} (ID: {unit_id}) at position {unit.position}")
        logging.info(f"AI DEBUGGING: Unit faction: {unit.faction}, Current phase: {game_state_manager.current_game_state.current_phase}")
        logging.info(f"AI DEBUGGING: Unit AI archetype: {ai_profile.behavior_type.name}")
        
        # Use archetype-specific action determination
        action_dict = self._determine_action_by_archetype(unit, ai_profile)
        
        # Restore the original game state manager
        self.gameStateManager = original_gsm
        
        return action_dict
    
    def process_phase(self, phase):
        """
        Process the AI phase for a faction.
        
        This method handles the AI turn for all units of a specific faction (ENEMY or NPC).
        It iterates through all active units for the faction, checking if each can act,
        and processes their turns one by one.
        
        Args:
            phase: The current phase (ENEMY or NPC)
            
        Returns:
            True if all units acted, False otherwise
        """
        logging.info(f"AI Manager processing phase: {phase}")
        ai_faction = FactionEnum.ENEMY if phase == PhaseEnum.ENEMY else FactionEnum.NPC
        
        # Get all active units for the faction in activation order
        active_ai_units = self.unitSystem.get_units_by_faction(ai_faction)
        
        for unit_id in active_ai_units:
            # Check if unit can act (not dead, slept, etc.)
            if self.unitSystem.can_act(unit_id) and not self.unitSystem.has_acted(unit_id):
                self.process_unit_turn(unit_id)
                # Small delay for visual pacing could be added here
        
        logging.info(f"AI Manager finished phase: {phase}")
        return True
    
    def process_unit_turn(self, unit_id: str):
        """
        Process the turn for a single AI unit.
        
        This method handles the complete turn sequence for an AI-controlled unit:
        1. Retrieves the unit's AI profile
        2. Finds possible actions using the action evaluator
        3. Applies archetype-specific modifications to action scores
        4. Selects the best action based on scores and archetype priorities
        5. Executes the selected action through the action handler
        
        If no valid action is found or if an action fails, the unit will wait.
        
        Args:
            unit_id: ID of the unit to process the turn for
        """
        unit = self.unitSystem.get_unit(unit_id)
        ai_profile = self.profile_manager.get_profile(unit_id)
        
        if not unit or not ai_profile:
            logging.warning(f"Cannot process AI turn for unit {unit_id}: Unit or AI profile not found")
            return
        
        logging.info(f"Processing AI turn for: {unit.name} (AI: {ai_profile.behavior_type.name})")
        
        # Find possible actions for this unit
        possible_actions = self.action_evaluator.find_possible_actions(unit_id, ai_profile)
        
        # Apply archetype-specific modifications to action scores
        for handler in self.archetype_handlers:
            if handler.can_handle(ai_profile):
                possible_actions = handler.modify_action_scores(unit_id, possible_actions, ai_profile)
                break
        
        # Select the best action
        best_action = self.select_best_action(unit_id, possible_actions, ai_profile)
        
        if best_action:
            # Get the current phase to identify if this is a player or enemy unit
            current_phase = self.gameStateManager.current_game_state.current_phase
            faction_label = "PLAYER" if current_phase == PhaseEnum.PLAYER else "ENEMY"
            
            # Log the action with detailed information
            self._log_ai_action_details(unit, best_action, faction_label)
            
            # Execute Move first if needed
            if best_action.target_data.get('move_path'):
                print(f"DEBUG: process_unit_turn - Executing MOVE action with path: {best_action.target_data.get('move_path')}")
                move_path = best_action.target_data.get('move_path')
                move_outcome = self.actionHandler.perform_action(
                    unit_id,
                    'MOVE',
                    {'path': move_path}
                )
                
                if not move_outcome.success:
                    logging.warning(f"AI move failed for {unit.name}")
                    # Fallback to Wait
                    self.actionHandler.perform_action(unit_id, 'WAIT', {})
                    return
            
            # Execute the main action
            action_outcome = self.actionHandler.perform_action(
                unit_id,
                best_action.action_type,
                {k: v for k, v in best_action.target_data.items() if k != 'move_path'}
            )
            
            if not action_outcome.success:
                logging.warning(f"AI action failed for {unit.name}: {action_outcome.message}")
                # If action failed after move, unit might just wait there
                if not self.unitSystem.has_acted(unit_id):  # Check if move already marked acted
                    self.actionHandler.perform_action(unit_id, 'WAIT', {})  # Explicit wait if action failed
        else:
            # No viable action found, just wait
            logging.info(f"AI {unit.name} found no action, waiting.")
            self.actionHandler.perform_action(unit_id, 'WAIT', {})
    
    def select_best_action(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> Optional[AIAction]:
        """
        Select the best action from a list of possible actions.
        
        This method chooses the most appropriate action for a unit based on:
        1. The unit's AI archetype (delegating to archetype-specific handlers if available)
        2. The scores of possible actions
        3. The validity of actions (e.g., ensuring move paths exist)
        
        It filters out invalid actions, sorts by score, and constructs an AIAction
        object representing the selected action.
        
        Args:
            unit_id: ID of the unit
            possible_actions: List of possible actions with scores
            ai_profile: AI profile for the unit
            
        Returns:
            The best AIAction or None if no valid action is found
        """
        print(f"DEBUG: select_best_action - Selecting from {len(possible_actions)} possible actions")
        for i, action in enumerate(possible_actions):
            print(f"DEBUG: select_best_action - Action {i+1}: type={action.get('type')}, score={action.get('score')}, is_current_pos={action.get('is_current_pos')}, has_move_path={action.get('move_path') is not None}")
        
        if not possible_actions:
            print("DEBUG: select_best_action - No possible actions")
            return None
        
        # Use archetype-specific selection if available
        for handler in self.archetype_handlers:
            if handler.can_handle(ai_profile):
                return handler.select_best_action(unit_id, possible_actions, ai_profile)
        
        # Default selection logic if no archetype handler is available
        # Filter out invalid actions (e.g., path not found for move-actions)
        valid_actions = [a for a in possible_actions if a['type'] == 'WAIT' or
                          a['is_current_pos'] or a['move_path'] is not None]
        
        if not valid_actions:
            return None
            
        # Sort actions by score (descending)
        valid_actions.sort(key=lambda a: a['score'], reverse=True)
        
        # Create AIAction from the highest scoring valid action
        best_action = valid_actions[0]
        target_data = best_action.get('target_info', {}).copy()
        
        # Add move path to target data if needed
        if best_action.get('move_path'):
            target_data['move_path'] = best_action['move_path']
            print(f"DEBUG: select_best_action - Selected action with move_path: {best_action['move_path']}")
            
        action = AIAction(best_action['type'], unit_id, target_data)
        print(f"DEBUG: select_best_action - Final action: type={action.action_type}, has_move_path={action.target_data.get('move_path') is not None}")
        return action
    
    def _determine_action_by_archetype(self, unit, ai_profile):
        """
        Determine the best action for a unit based on its AI archetype.
        
        This method implements the core AI decision-making process:
        1. Finds all possible actions using the action evaluator
        2. Applies archetype-specific modifications to action scores
        3. Selects the best action based on the modified scores
        4. Converts the selected AIAction to the action dictionary format
           expected by the action handler
        
        Args:
            unit: The unit to determine an action for
            ai_profile: The AI profile for the unit
            
        Returns:
            Dict containing the action data or None if no action is possible.
            For combined actions like MOVE_AND_ATTACK, the dictionary includes
            nested move_data and action_data.
        """
        unit_id = unit.id
        
        logging.info(f"AI DEBUGGING: Processing unit {unit.name} (ID: {unit_id}) with archetype {ai_profile.behavior_type.name}")
        
        # Find possible actions for this unit
        possible_actions = self.action_evaluator.find_possible_actions(unit_id, ai_profile)
        
        logging.info(f"AI DEBUGGING: Found {len(possible_actions)} possible actions for {unit.name}")
        for i, action in enumerate(possible_actions):
            logging.info(f"AI DEBUGGING: Action {i+1}: {action['type']} with score {action['score']}")
        
        # Apply archetype-specific modifications to action scores
        for handler in self.archetype_handlers:
            if handler.can_handle(ai_profile):
                possible_actions = handler.modify_action_scores(unit_id, possible_actions, ai_profile)
                break
        
        # Select the best action
        best_action = self.select_best_action(unit_id, possible_actions, ai_profile)
        
        if best_action:
            logging.info(f"AI DEBUGGING: Selected best action: {best_action.action_type} for {unit.name}")
        else:
            logging.info(f"AI DEBUGGING: No best action selected for {unit.name}")
        
        if best_action:
            # Get the current phase to identify if this is a player or enemy unit
            current_phase = self.gameStateManager.current_game_state.current_phase
            faction_label = "PLAYER" if current_phase == PhaseEnum.PLAYER else "ENEMY"
            
            # Log the action with detailed information
            self._log_ai_action_details(unit, best_action, faction_label)
            
            # Convert AIAction to action dict format expected by ActionHandler
            action_dict = {
                'type': best_action.action_type,
                'unit_id': unit_id
            }
            
            # Add move path if present
            if 'move_path' in best_action.target_data:
                if best_action.action_type == 'MOVE':
                    action_dict['path'] = best_action.target_data['move_path']
                else:
                    # For combined actions like MOVE_AND_ATTACK
                    action_dict = {
                        'type': f"MOVE_AND_{best_action.action_type}",
                        'unit_id': unit_id,
                        'move_data': {
                            'type': 'MOVE',
                            'unit_id': unit_id,
                            'path': best_action.target_data['move_path']
                        },
                        'action_data': {
                            'type': best_action.action_type,
                            'unit_id': unit_id
                        }
                    }
                    
                    # Remove move_path from target_data to avoid duplication
                    target_data_copy = best_action.target_data.copy()
                    target_data_copy.pop('move_path', None)
                    
                    # Add remaining target data to action_data
                    action_dict['action_data'].update(target_data_copy)
            
            # Add target info if present
            if best_action.target_data and 'move_path' not in best_action.target_data:
                action_dict['target_info'] = best_action.target_data
            
            return action_dict
        else:
            # No viable action found, just wait
            logging.info(f"AI {unit.name} found no action, waiting.")
            return {
                'type': 'WAIT',
                'unit_id': unit_id
            }
    
    def _log_ai_action_details(self, unit, action, faction_label):
        """
        Log detailed information about an AI action.
        
        This method provides detailed logging of AI actions for debugging and analysis.
        It extracts relevant information based on the action type and logs appropriate
        details, including:
        - For MOVE actions: Source and destination positions
        - For ATTACK actions: Attacker, target, and weapon used
        - For CAPTURE actions: Capturing unit and target
        - For ITEM actions: Item used and target
        
        Args:
            unit: The unit performing the action
            action: The AIAction object containing action details
            faction_label: String indicating which faction the AI is controlling ("PLAYER" or "ENEMY")
        """
        action_type = action.action_type
        unit_name = unit.name
        unit_pos = unit.position
        
        if action_type == "MOVE":
            # Extract the destination from the move path
            if 'move_path' in action.target_data and action.target_data['move_path']:
                dest_pos = action.target_data['move_path'][-1]
                logging.info(f"AI ({faction_label}): {unit_name} moves from {unit_pos} to {dest_pos}")
            else:
                logging.info(f"AI ({faction_label}): {unit_name} attempts to move but no path found")
                
        elif action_type == "ATTACK":
            # Get target unit information
            target_id = action.target_data.get('target_unit_id')
            target_unit = self.unitSystem.get_unit(target_id) if target_id else None
            
            # Get weapon information
            weapon = self.inventorySystem.get_equipped_weapon(unit.id)
            weapon_name = "Unknown Weapon"
            if weapon:
                weapon_data = self.dataProvider.get_item_data(weapon)
                if weapon_data:
                    weapon_name = weapon_data.name
            
            if target_unit:
                logging.info(f"AI ({faction_label}): {unit_name} attacks {target_unit.name} with {weapon_name}")
            else:
                logging.info(f"AI ({faction_label}): {unit_name} attempts to attack but no valid target")
                
        elif action_type == "WAIT":
            logging.info(f"AI ({faction_label}): {unit_name} waits at {unit_pos}")
            
        elif action_type == "CAPTURE":
            target_id = action.target_data.get('target_unit_id')
            target_unit = self.unitSystem.get_unit(target_id) if target_id else None
            
            if target_unit:
                logging.info(f"AI ({faction_label}): {unit_name} attempts to capture {target_unit.name}")
            else:
                logging.info(f"AI ({faction_label}): {unit_name} attempts to capture but no valid target")
                
        elif action_type == "ITEM":
            item_id = action.target_data.get('item_id')
            target_id = action.target_data.get('target_unit_id')
            
            item_name = "Unknown Item"
            if item_id:
                item_data = self.dataProvider.get_item_data(item_id)
                if item_data:
                    item_name = item_data.name
            
            target_unit = self.unitSystem.get_unit(target_id) if target_id else None
            target_name = target_unit.name if target_unit else "self"
            
            logging.info(f"AI ({faction_label}): {unit_name} uses {item_name} on {target_name}")
        
        else:
            # Generic log for other action types
            logging.info(f"AI ({faction_label}): {unit_name} performs {action_type} action")
