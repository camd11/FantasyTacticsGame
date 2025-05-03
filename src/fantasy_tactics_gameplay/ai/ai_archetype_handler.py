"""
AI Archetype Handler Module

This module defines the base class for AI archetype handlers.
It serves as the foundation for the archetype-based behavior system in the modular
AI architecture. Each specific AI behavior type (CHARGE, GUARD, HEAL_SUPPORT, etc.)
is implemented as a subclass of AIArchetypeHandler, allowing for specialized
decision-making logic tailored to different unit roles.

The archetype handler system is a key component of the AI architecture, enabling
polymorphic behavior patterns through a common interface. This approach allows
for easy extension with new unit types and behaviors without modifying the core
AI decision-making components.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any

from src.gameplay_systems.ai.ai_types import AIProfile, AIBehaviorType, AIAction


class AIArchetypeHandler:
    """
    Base class for AI archetype handlers.
    
    Each archetype handler is responsible for implementing behavior specific to a particular
    AI archetype, such as CHARGE, GUARD, HEAL_SUPPORT, or THIEF_LOOT. This class defines
    the common interface and default implementations for all archetype handlers.
    
    The archetype handler system is a key component of the modular AI architecture,
    allowing for:
    1. Specialized behavior patterns for different unit types
    2. Encapsulation of archetype-specific logic in dedicated classes
    3. Easy extension with new archetypes without modifying core AI components
    4. Polymorphic handling of different unit behaviors through a common interface
    
    Concrete archetype handlers should override the methods in this class to implement
    their specific behavior patterns.
    """
    
    def __init__(self, gameStateManager, unitSystem, mapSystem, movementSystem,
                 combatSystem, inventorySystem, dataProvider):
        """
        Initialize the AIArchetypeHandler.
        
        This method sets up the AIArchetypeHandler with references to all the game systems
        needed to implement archetype-specific behavior. It should be called when creating
        a new instance of any archetype handler.
        
        The handler requires access to multiple game systems to perform its functions:
        - GameStateManager for accessing the current state of the game
        - UnitSystem for unit data and capabilities
        - MapSystem for terrain effects and pathfinding
        - MovementSystem for calculating movement ranges and paths
        - CombatSystem for simulating potential combat outcomes
        - InventorySystem for accessing weapons and items
        - DataProvider for game data definitions
        
        Concrete archetype handlers will use these systems to implement their
        specific behavior patterns and decision-making logic.
        
        Args:
            gameStateManager: Instance of the GameStateManager that provides access to the current game state
            unitSystem: Instance of the UnitSystem for accessing unit data and capabilities
            mapSystem: Instance of the MapSystem for terrain and pathfinding operations
            movementSystem: Instance of the MovementSystem for calculating movement ranges
            combatSystem: Instance of the CombatSystem for simulating combat outcomes
            inventorySystem: Instance of the InventorySystem for accessing unit equipment and items
            dataProvider: Instance of the DataProvider for accessing game data definitions
        """
        self.gameStateManager = gameStateManager
        self.unitSystem = unitSystem
        self.mapSystem = mapSystem
        self.movementSystem = movementSystem
        self.combatSystem = combatSystem
        self.inventorySystem = inventorySystem
        self.dataProvider = dataProvider
    
    def can_handle(self, ai_profile: AIProfile) -> bool:
        """
        Check if this handler can handle the given AI profile.
        
        This method determines whether this archetype handler is appropriate for
        a specific AI profile based on its behavior type. Each concrete archetype
        handler should override this method to check for the behavior types it
        can handle.
        
        The base implementation always returns False, as the base class doesn't
        handle any specific behavior type. Concrete subclasses must override this
        method to specify which behavior types they can handle.
        
        This method is used by the AIManager to select the appropriate handler
        for each unit based on its AI profile.
        
        Args:
            ai_profile: The AI profile to check, containing the behavior type and other parameters
            
        Returns:
            True if this handler can handle the profile, False otherwise
        """
        # Base implementation always returns False
        # Subclasses should override this method
        return False
    
    def modify_action_scores(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> List[Dict]:
        """
        Modify action scores based on the AI archetype.
        
        This method adjusts the scores of possible actions based on the specific
        behavior patterns of the archetype. For example, a CHARGE archetype might
        increase scores for attack actions, while a HEAL_SUPPORT archetype might
        increase scores for healing actions.
        
        The base implementation returns actions unchanged. Concrete archetype handlers
        should override this method to implement their specific scoring adjustments.
        
        This method is a key part of the archetype-based behavior system, allowing
        each archetype to express its unique priorities through score modifications.
        These modifications influence the final action selection, ensuring that
        units behave according to their designated role.
        
        Args:
            unit_id: ID of the unit whose actions are being evaluated
            possible_actions: List of possible actions with initial scores from AIActionEvaluator
            ai_profile: AI profile containing behavior parameters for the unit
            
        Returns:
            Modified list of possible actions with updated scores reflecting archetype priorities
        """
        # Base implementation returns actions unchanged
        # Subclasses should override this method
        return possible_actions
    
    def select_best_action(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> Optional[AIAction]:
        """
        Select the best action based on the AI archetype.
        
        This method chooses the most appropriate action for a unit based on the
        archetype's behavior patterns and the scored list of possible actions.
        
        The base implementation selects the highest scoring valid action after
        filtering out invalid actions (e.g., moves with no valid path). Concrete
        archetype handlers may override this method to implement more sophisticated
        selection logic, such as prioritizing certain action types regardless of score.
        
        The selection process includes:
        1. Filtering out invalid actions (e.g., moves with no valid path)
        2. Sorting the remaining actions by score in descending order
        3. Selecting the highest-scoring action
        4. Creating an AIAction object with the appropriate action type and target data
        
        This method represents the final decision-making step in the AI process,
        translating scored possibilities into a concrete action decision.
        
        Args:
            unit_id: ID of the unit whose actions are being evaluated
            possible_actions: List of possible actions with scores (possibly modified by modify_action_scores)
            ai_profile: AI profile containing behavior parameters for the unit
            
        Returns:
            The best AIAction object representing the selected action, or None if no valid action is found
        """
        # Base implementation selects the highest scoring action
        # Subclasses may override this method for more specific behavior
        
        if not possible_actions:
            return None
            
        # Filter out invalid actions (e.g., path not found for move-actions)
        valid_actions = [a for a in possible_actions if a['type'] == 'WAIT' or
                          a['is_current_pos'] or a['path'] is not None]
        
        if not valid_actions:
            return None
            
        # Sort actions by score (descending)
        valid_actions.sort(key=lambda a: a['score'], reverse=True)
        
        # Create AIAction from the highest scoring valid action
        best_action = valid_actions[0]
        target_data = best_action.get('target_info', {}).copy()
        
        # Add move path to target data if needed
        if best_action.get('path'):
            target_data['path'] = best_action['path']
            
        return AIAction(best_action['type'], unit_id, target_data)
    
    def find_specific_targets(self, unit_id: str, ai_profile: AIProfile) -> List[Dict]:
        """
        Find specific targets for this AI archetype.
        
        This method identifies potential targets that are particularly relevant
        to the archetype's behavior patterns. For example, a CHARGE archetype might
        look for high-value enemy targets, while a HEAL_SUPPORT archetype might
        look for injured allies.
        
        The base implementation returns an empty list. Concrete archetype handlers
        should override this method to implement their specific target identification logic.
        
        This method allows archetypes to proactively identify strategic targets
        beyond what the general action evaluation system might consider. It's
        particularly useful for specialized behaviors like thieves seeking chests,
        healers identifying critical healing targets, or guard units monitoring
        specific areas.
        
        Args:
            unit_id: ID of the unit seeking targets
            ai_profile: AI profile containing behavior parameters for the unit
            
        Returns:
            List of target information dictionaries containing data about potential targets,
            where each dictionary typically includes position coordinates and target-specific
            information like type, ID, and other relevant attributes
        """
        # Base implementation returns an empty list
        # Subclasses should override this method
        return []