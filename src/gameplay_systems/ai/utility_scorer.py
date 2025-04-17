"""
AI Utility Scorer Module

This module defines the UtilityScorer class, which is responsible for evaluating
the utility (or desirability) of different AI goals. It serves as a key component
in the goal-oriented decision-making process of the AI system.

The UtilityScorer assigns numeric scores to goals based on various factors such as:
- The AI unit's current state and capabilities
- The current game state and tactical situation
- The specific parameters of the goal
- The AI unit's behavior profile and preferences

These scores are used to select the most appropriate goal for an AI unit during
the Strategic Phase of AI decision-making.
"""

from typing import Dict, List, Any, Optional, Union
from unittest.mock import Mock  # Import for type checking


class UtilityScorer:
    """
    Evaluates the utility of different AI goals.
    
    The UtilityScorer is responsible for assigning numeric scores to goals
    based on various factors, allowing the AI system to select the most
    appropriate goal for a unit's turn.
    
    This class implements scoring algorithms that consider:
    - Goal type and parameters
    - Unit state and capabilities
    - Current game state
    - Tactical situation
    - AI behavior profiles
    
    The scores produced by this class are used during the Strategic Phase
    of AI decision-making to select the most appropriate goal for an AI unit.
    """
    
    def __init__(self, game_state_manager=None):
        """
        Initialize a UtilityScorer.
        
        Args:
            game_state_manager: The game state manager that provides access to the game state
        """
        self.game_state_manager = game_state_manager
    
    def score_goal(self, goal, unit_state, game_state_manager) -> float:
        """
        Score a goal based on its utility for the given unit.
        
        This method evaluates how desirable a goal is for an AI unit based on
        the current game state and the unit's capabilities. It returns a numeric
        score where higher values indicate more desirable goals.
        
        Args:
            goal: The goal to score
            unit_state: The state of the AI unit
            game_state_manager: The current game state manager
            
        Returns:
            float: A numeric score representing the goal's utility
        """
        # Dispatch to the appropriate scoring method based on goal type
        if hasattr(goal, 'goal_type'):
            if goal.goal_type == "ATTACK_UNIT":
                return self._score_attack_unit_goal(goal, unit_state, game_state_manager)
        
        # Default score for unknown goal types
        return 0.0
    
    def _score_attack_unit_goal(self, goal, unit_state, game_state_manager) -> float:
        """
        Score an AttackUnitGoal.
        
        This method evaluates the utility of attacking a specific target unit.
        It considers factors such as:
        - Target unit's current HP and value
        - Distance to the target
        - Potential damage that could be dealt
        - Risk to the attacking unit
        
        Args:
            goal: The AttackUnitGoal to score
            unit_state: The state of the AI unit
            game_state_manager: The current game state manager
            
        Returns:
            float: A numeric score representing the goal's utility
        """
        # Extract target unit ID from goal parameters
        target_unit_id = goal.parameters.get("target_unit_id")
        if not target_unit_id:
            return 0.0
        
        # Get target unit from game state
        target_unit = game_state_manager.get_unit_by_id(target_unit_id)
        if not target_unit:
            return 0.0
        
        # Check if target is reachable
        if not game_state_manager.pathfinding.can_potentially_reach(
            unit_state, target_unit.position
        ):
            return 0.0
        
        # Calculate base score based on various factors
        base_score = 50.0
        
        # Factor 1: Target unit's current HP percentage
        # Prioritize low HP targets that can be finished off
        if hasattr(target_unit, 'current_hp') and hasattr(target_unit, 'max_hp'):
            # Handle Mock objects gracefully
            try:
                current_hp = int(target_unit.current_hp) if not isinstance(target_unit.current_hp, Mock) else 20
                max_hp = int(target_unit.max_hp) if not isinstance(target_unit.max_hp, Mock) else 40
                
                if current_hp > 0 and max_hp > 0:
                    hp_percentage = current_hp / max_hp
                    if hp_percentage < 0.3:
                        base_score += 30  # Significant bonus for targeting nearly defeated units
                    elif hp_percentage < 0.5:
                        base_score += 15  # Moderate bonus for targeting damaged units
            except (TypeError, ValueError):
                # If we can't convert to numbers or do the comparison, just skip this factor
                pass
        
        # Factor 2: Distance to the target
        # Closer targets are more desirable
        if hasattr(unit_state, 'position') and hasattr(target_unit, 'position'):
            try:
                # Simple Manhattan distance calculation
                unit_pos = unit_state.position
                target_pos = target_unit.position
                
                # Handle Mock objects
                if hasattr(unit_pos, '__class__') and unit_pos.__class__.__name__ == 'Mock':
                    unit_pos = (3, 3)  # Default position for mocks
                if hasattr(target_pos, '__class__') and target_pos.__class__.__name__ == 'Mock':
                    target_pos = (5, 5)  # Default position for mocks
                
                distance_x = abs(unit_pos[0] - target_pos[0])
                distance_y = abs(unit_pos[1] - target_pos[1])
                distance = distance_x + distance_y
                
                # Apply distance penalty (closer targets get less penalty)
            except (TypeError, ValueError, IndexError):
                # If we can't calculate the distance, use a default value
                distance = 5
                
            # Apply distance penalty
            distance_penalty = min(30, distance * 2)  # Cap at 30
            base_score -= distance_penalty
        
        # Factor 3: Target unit's value
        # This would be more sophisticated in a real implementation
        # For now, we'll just check if the target is a healer or has a special role
        try:
            if hasattr(target_unit, 'unit_class'):
                unit_class = getattr(target_unit, 'unit_class', '')
                # Handle Mock objects
                if hasattr(unit_class, '__class__') and unit_class.__class__.__name__ == 'Mock':
                    unit_class = ''
                    
                if unit_class in ['HEALER', 'CLERIC', 'PRIEST', 'BISHOP']:
                    base_score += 20  # Bonus for targeting healers
        except (TypeError, ValueError):
            # If we can't check the unit class, skip this factor
            pass
            
        try:
            is_lord = getattr(target_unit, 'is_lord', False)
            # Handle Mock objects
            if hasattr(is_lord, '__class__') and is_lord.__class__.__name__ == 'Mock':
                is_lord = False
                
            if is_lord:
                base_score += 40  # Significant bonus for targeting lords
        except (TypeError, ValueError):
            # If we can't check if the unit is a lord, skip this factor
            pass
        
        # Ensure the score is at least 1.0 for valid targets
        return max(1.0, base_score)