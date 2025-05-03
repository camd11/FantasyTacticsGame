"""
AI Manager Module

This module defines the AIManager class, which serves as the main orchestrator for the
AI decision-making process. It coordinates the two-phase decision flow:

1. Strategic Goal Selection: Using the StrategicEvaluator to select the best high-level goal
2. Tactical Action Execution: Using the TacticalExecutor to determine the best action to achieve the goal

The AIManager provides a clean interface for the game system to interact with the AI,
handling all the complexity of the decision-making process internally.
"""

import logging
from typing import Optional, Union

from src.gameplay_systems.ai.strategic_evaluator import StrategicEvaluator
from src.gameplay_systems.ai.tactical_executor import TacticalExecutor
from src.gameplay_systems.ai.ai_types import AIAction
from src.gameplay_systems.ai.ai_persona import AIPersona


class AIManager:
    """
    Main orchestrator for the AI decision-making process.
    
    The AIManager coordinates the two-phase decision flow:
    1. Strategic Goal Selection: Using the StrategicEvaluator to select the best high-level goal
    2. Tactical Action Execution: Using the TacticalExecutor to determine the best action to achieve the goal
    
    It provides a clean interface for the game system to interact with the AI,
    handling all the complexity of the decision-making process internally.
    """
    def __init__(self, strategic_evaluator: StrategicEvaluator, tactical_executor: TacticalExecutor, state_manager=None):
        """
        Initialize an AIManager.
        
        Args:
            strategic_evaluator: The strategic evaluator used to select goals
            tactical_executor: The tactical executor used to determine actions
            state_manager: The state manager used to maintain consistent state
        """
        self.strategic_evaluator = strategic_evaluator
        self.tactical_executor = tactical_executor
        self.state_manager = state_manager
        
        # Load AI personas
        AIPersona.load_personas()
        self.state_manager = state_manager
        
        # Set up logger
        self.logger = logging.getLogger(__name__)
    
    def determine_and_execute_action(self, unit_state, game_state_manager, persona=None) -> Optional[AIAction]:
        """
        Determine and execute the best action for the given unit.
        
        This method implements the two-phase decision flow:
        1. Use the strategic evaluator to select the best goal
        2. Use the tactical executor to determine the best action to achieve that goal
        
        Args:
            unit_state: The state of the AI unit
            game_state_manager: The current game state manager
            persona: The AI persona/profile that influences decision-making
            
        Returns:
            AIAction: The selected action, or None if no valid action is possible
        """
        # Log the start of AI turn processing
        unit_id = getattr(unit_state, 'id', getattr(unit_state, 'unit_id', 'unknown'))
        self.logger.info(f"AI Turn Start: Processing unit {unit_id}")
        # Get the unit's persona if not provided
        if persona is None:
            # Try to get persona from unit_state
            persona_name = getattr(unit_state, 'ai_persona', 'BALANCED')
            # Handle Mock objects in tests
            if hasattr(persona_name, '__class__') and persona_name.__class__.__name__ == 'Mock':
                persona_name = 'BALANCED'
            # Get the persona object
            persona = AIPersona.get_persona(persona_name)
        elif isinstance(persona, str):
            # If persona is provided as a string, get the persona object
            persona = AIPersona.get_persona(persona)
            
        # Phase 1: Strategic Goal Selection
        selected_goal = self.strategic_evaluator.select_best_goal(
            unit_state,
            game_state_manager,
            persona
        )
        
        # If no valid goal is found, return None
        if selected_goal is None:
            return None
        
        # Phase 2: Tactical Action Execution
        selected_action = self.tactical_executor.determine_action_for_goal(
            selected_goal,
            unit_state,
            game_state_manager
        )
        # Return the selected action
        self.logger.info(f"AI Turn End: Unit {unit_id} action determined: {selected_action.action_type if selected_action else 'None'}")
        return selected_action
        return selected_action