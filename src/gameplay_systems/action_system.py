"""
Action System Module

This module manages unit actions during gameplay, including movement, combat, item usage,
and special actions like stealing, capturing, rescuing, and dancing. It enforces action rules and
coordinates with other systems to execute actions. This includes the 'Move Again' (Dance/Play) skill
implementation that allows certain units to grant additional actions to allies.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union

from src.core_engine.game_state import GameStateManager, FactionEnum
from src.core_engine.data_provider import DataProvider
from src.core_engine.unit_state import UnitState

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
        self.statusEffectManager = None
    
    def initialize(self, gameStateManager_instance: GameStateManager,
                  dataProvider_instance: DataProvider,
                  mapSystem_instance,
                  inventorySystem_instance,
                  combatSystem_instance,
                  stealingSystem_instance=None,
                  uiSystem_instance=None,
                  statusEffectManager_instance=None) -> None:
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
            statusEffectManager_instance: Instance of the StatusEffectManager (optional)
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        self.mapSystem = mapSystem_instance
        self.inventorySystem = inventorySystem_instance
        self.combatSystem = combatSystem_instance
        self.stealingSystem = stealingSystem_instance
        self.uiSystem = uiSystem_instance
        self.statusEffectManager = statusEffectManager_instance
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
    def mark_unit_action_complete(self, unit_id: str) -> None:
        """
        Mark a unit as having completed their action for the turn.
        
        This sets both the has_acted flag (for immediate UI/interaction purposes) and
        the has_acted_this_turn flag (for tracking action state across the phase, including
        for Move Again skill interactions).
        
        Args:
            unit_id: ID of the unit
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if unit:
            unit.has_acted = True
            unit.has_acted_this_turn = True
            logging.info(f"Unit {unit_id} action marked as complete")
    def mark_unit_action_taken(self, unit_id: str) -> None:
        """
        Mark a unit as having taken an action for the turn.
        
        This sets both the has_acted flag (for immediate UI/interaction purposes) and
        the has_acted_this_turn flag (for tracking action state across the phase, including
        for Move Again skill interactions).
        
        Args:
            unit_id: ID of the unit
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if unit:
            unit.has_acted = True
            unit.has_acted_this_turn = True
            logging.info(f"Unit {unit_id} action marked as taken")
    
    def has_unit_acted_or_waited(self, unit_id: str) -> bool:
        """
        Check if a unit has already acted or waited this turn.
        
        This checks the has_acted_this_turn flag, which tracks whether a unit has performed
        its primary action during the current phase. This flag is used to determine if a unit
        can be targeted by the Move Again (Dance/Play) skill.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit has acted or waited, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        return unit.has_acted_this_turn

    def get_available_actions(self, unit_id: str) -> List[str]:
        """
        Get the list of available actions for a unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            List of available action types
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return []
        
        # If unit has already acted, no actions are available
        if unit.has_acted_this_turn:
            return []
        
        # Check for status effects that prevent actions
        if hasattr(self, 'statusEffectManager') and self.statusEffectManager:
            # Check for Berserk status
            if self.statusEffectManager.has_status(unit_id, "Berserk"):
                return []  # No actions available for berserked units
            
            # Check for other action-preventing statuses
            ai_override = self.statusEffectManager.get_ai_override(unit_id)
            if ai_override:
                return []  # No actions available for units with AI override
        
        available_actions = ["WAIT", "ATTACK"]  # Default actions
        
        # Check for special actions based on skills
        
        # Check for Dance skill
        if self.dataProvider.unit_has_skill(unit_id, "SKILL_DANCE"):
            # Check if there are valid targets for Dance
            if self._has_valid_dance_targets(unit):
                available_actions.append("DANCE")
        
        return available_actions
    
    def _has_valid_dance_targets(self, dancer_unit: UnitState) -> bool:
        """
        Check if a unit with the Dance skill has valid targets for the Move Again action.
        
        This method scans all units to find at least one valid target for the Dance action.
        A valid target must be adjacent, an ally, must have already acted this turn, and
        must not have already been refreshed by another Dance action.
        
        Args:
            dancer_unit: The unit with the Dance skill
            
        Returns:
            True if there are valid targets, False otherwise
        """
        # Get all units
        for unit_id, unit in self.gameStateManager.current_game_state.unit_states.items():
            if self.is_valid_dance_target(dancer_unit, unit):
                return True
        
        return False
    
    def is_valid_dance_target(self, dancer_unit: UnitState, potential_target_unit: UnitState) -> bool:
        """
        Check if a unit is a valid target for the Dance action (Move Again skill).
        
        A unit can be targeted by the Dance action if it meets all the following criteria:
        1. It is not the dancer unit itself (no self-targeting)
        2. It is adjacent to the dancer unit (Manhattan distance of 1)
        3. It belongs to the same faction as the dancer
        4. It has already acted this turn (has_acted_this_turn is True)
        5. It has not already been refreshed by another Dance action (was_refreshed_this_turn is False)
        
        Args:
            dancer_unit: The unit performing the Dance action
            potential_target_unit: The potential target unit
            
        Returns:
            True if the target is valid, False otherwise
        """
        if potential_target_unit is None:
            return False
        
        # Check if it's the same unit (can't dance for self)
        if dancer_unit.id == potential_target_unit.id:
            return False
        
        # Check adjacency
        dancer_pos = dancer_unit.position
        target_pos = potential_target_unit.position
        if abs(dancer_pos[0] - target_pos[0]) + abs(dancer_pos[1] - target_pos[1]) != 1:
            return False
        
        # Check faction
        if dancer_unit.faction != potential_target_unit.faction:
            return False
        
        # Check state
        if not potential_target_unit.has_acted_this_turn:
            return False
        
        if potential_target_unit.was_refreshed_this_turn:
            return False
        
        return True
    
    def execute_dance(self, dancer_unit_id: str, target_unit_id: str) -> bool:
        """
        Execute the Dance action (Move Again skill).
        
        This method retrieves the dancer and target units, validates that the target
        is eligible for the Dance action, and then applies the Dance effect if valid.
        
        Args:
            dancer_unit_id: ID of the unit performing the Dance action
            target_unit_id: ID of the target unit
            
        Returns:
            True if the action was successful, False otherwise
        """
        dancer_unit = self.gameStateManager.get_unit(dancer_unit_id)
        target_unit = self.gameStateManager.get_unit(target_unit_id)
        
        if not dancer_unit or not target_unit:
            return False
        
        # Validate target
        if not self.is_valid_dance_target(dancer_unit, target_unit):
            return False
        
        # Apply dance effect
        return self.apply_dance_effect(dancer_unit, target_unit)
    
    def apply_dance_effect(self, dancer_unit: UnitState, target_unit: UnitState) -> bool:
        """
        Apply the effect of the Dance action (Move Again skill).
        
        When the Dance action is successfully performed:
        1. The target unit's has_acted_this_turn flag is reset to False, allowing it to act again
        2. The target unit's was_refreshed_this_turn flag is set to True, preventing multiple refreshes
        3. The dancer unit's has_acted_this_turn flag is set to True, consuming its action
        
        This implements the core functionality of the Move Again skill, allowing specific units
        (e.g., Dancers, Bards) to grant an additional action to an allied unit that has already
        completed its action within the current player phase.
        
        Args:
            dancer_unit: The unit performing the Dance action
            target_unit: The target unit
            
        Returns:
            True if the effect was applied successfully, False otherwise
        """
        # Update target state
        target_unit.has_acted_this_turn = False  # Allow the target to act again
        target_unit.was_refreshed_this_turn = True  # Prevent multiple refreshes
        
        # Update dancer state
        dancer_unit.has_acted_this_turn = True  # Consume the dancer's action
        
        # Mark dancer as having acted
        self.mark_unit_action_taken(dancer_unit.id)
        
        logging.info(f"Unit {dancer_unit.id} danced for {target_unit.id}, allowing them to act again")
        
        return True
    
    def execute_action(self, action_type: str, actor_id: str, target_id: Optional[str] = None) -> bool:
        """
        Execute an action.
        
        Args:
            action_type: Type of action to execute
            actor_id: ID of the actor unit
            target_id: ID of the target unit (if applicable)
            
        Returns:
            True if the action was executed successfully, False otherwise
        """
        # Check if unit is berserked
        if hasattr(self, 'statusEffectManager') and self.statusEffectManager:
            if self.statusEffectManager.has_status(actor_id, "Berserk"):
                logging.warning(f"Cannot execute action for berserked unit {actor_id}")
                return False
            
            def can_unit_act(self, unit_id: str) -> bool:
                """
                Check if a unit can perform actions.
                
                Args:
                    unit_id: ID of the unit
                    
                Returns:
                    True if the unit can act, False otherwise
                """
                unit = self.gameStateManager.get_unit(unit_id)
                if not unit:
                    return False
                
                # Check if unit has already acted
                if unit.has_acted:
                    return False
                
                # Check for status effects that prevent actions
                if hasattr(self, 'statusEffectManager') and self.statusEffectManager:
                    if not self.statusEffectManager.can_perform_action(unit_id, "ANY"):
                        return False
                
                return True
        
        if action_type == "DANCE" and target_id:
            return self.execute_dance(actor_id, target_id)
        
        # Handle other action types...
        
        return False