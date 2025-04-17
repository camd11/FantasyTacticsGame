"""
AI Goals Module

This module defines the goal-oriented component of the AI system, representing high-level
strategic objectives that AI units can pursue. Goals define what the AI wants to achieve,
not how to achieve it.

Goals are evaluated during the Strategic Phase of AI decision-making to determine
the most appropriate objective for an AI unit's turn. Once a goal is selected,
it generates potential actions that are evaluated during the Tactical Phase.
"""

import abc
from typing import Dict, List, Any, Optional
from src.core_engine.game_state import DispositionEnum


class Goal(abc.ABC):
    """
    Abstract base class for all AI goals.
    
    Goals represent high-level strategic objectives for an AI unit.
    They define what the AI wants to achieve, not how to achieve it.
    
    Each goal type has:
    - A unique identifier (goal_type)
    - Parameters specific to the goal instance (e.g., target unit ID)
    - Methods to validate the goal and generate potential actions
    """
    
    def __init__(self, ai_unit=None):
        """
        Initialize a Goal.
        
        Args:
            ai_unit: The unit that will pursue this goal
        """
        self.goal_type = ""
        self.parameters = {}
        self.ai_unit = ai_unit
    
    @abc.abstractmethod
    def is_valid(self, unit, game_state_manager) -> bool:
        """
        Check if this goal is currently valid/possible given the game state.
        
        Args:
            unit: The unit considering this goal
            game_state_manager: The current game state
            
        Returns:
            bool: True if the goal is valid, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def generate_potential_actions(self, unit, game_state_manager) -> List[Any]:
        """
        Generate potential actions that could fulfill this goal.
        
        Args:
            unit: The unit pursuing this goal
            game_state_manager: The current game state
            
        Returns:
            List[Any]: A list of potential actions
        """
        pass
    
    @abc.abstractmethod
    def get_tactical_scorers(self, persona) -> List[Any]:
        """
        Provide goal-specific scoring considerations for tactical evaluation.
        
        Args:
            persona: The AI persona/profile that influences scoring
            
        Returns:
            List[Any]: A list of scoring considerations
        """
        pass


class AttackUnitGoal(Goal):
    """
    Goal to attack a specific enemy unit.
    
    This goal represents the strategic objective of targeting and attacking
    a specific enemy unit. It is valid if the target unit exists, is not
    defeated, and can potentially be reached by the AI unit.
    """
    
    def __init__(self, target_unit_id: str, ai_unit=None):
        """
        Initialize an AttackUnitGoal.
        
        Args:
            target_unit_id: ID of the target unit to attack
            ai_unit: The unit that will pursue this goal
        """
        super().__init__(ai_unit)
        self.goal_type = "ATTACK_UNIT"
        self.parameters = {"target_unit_id": target_unit_id}
    
    def is_valid(self, unit, game_state_manager) -> bool:
        """
        Check if attacking the target unit is a valid goal.
        
        A goal is valid if:
        - The target unit exists
        - The target unit is not defeated
        - The target unit can potentially be reached
        
        Args:
            unit: The unit considering this goal
            game_state_manager: The current game state
            
        Returns:
            bool: True if the goal is valid, False otherwise
        """
        target_unit_id = self.parameters["target_unit_id"]
        target_unit = game_state_manager.get_unit(target_unit_id)
        
        # Check if target exists and is not defeated
        if target_unit is None or target_unit.disposition == DispositionEnum.DEAD:
            return False
        
        # Check if target is of a different faction (not implemented in this version)
        # if target_unit.faction == unit.faction:
        #     return False
        
        # Check if target is potentially reachable
        return game_state_manager.pathfinding.can_potentially_reach(
            unit, target_unit.position
        )
    
    def generate_potential_actions(self, unit, game_state_manager) -> List[Any]:
        """
        Generate potential attack actions for this goal.
        
        Args:
            unit: The unit pursuing this goal
            game_state_manager: The current game state
            
        Returns:
            List[Any]: A list of potential attack actions
        """
        # This is a placeholder implementation
        # In a real implementation, this would generate Move+Attack actions
        # towards the target unit
        return []
    
    def get_tactical_scorers(self, persona) -> List[Any]:
        """
        Provide scorers relevant to attacking.
        
        Args:
            persona: The AI persona/profile that influences scoring
            
        Returns:
            List[Any]: A list of scoring considerations for attacking
        """
        # This is a placeholder implementation
        # In a real implementation, this would return scorers like
        # DamageDealt, KillPotential, SelfPreservation, etc.
        return []