"""
AI Strategic Evaluator Module

This module defines the StrategicEvaluator class, which is responsible for selecting
the most appropriate high-level goal for an AI unit's turn. It serves as a key component
in the goal-oriented decision-making process of the AI system.

The StrategicEvaluator evaluates different potential goals based on various factors such as:
- The AI unit's current state and capabilities
- The current game state and tactical situation
- The AI unit's behavior profile and preferences

It selects the goal with the highest utility score, which is then used to guide
the Tactical Phase of AI decision-making.
"""

import logging
from typing import List, Optional, Any, Dict, Type, Union
from src.gameplay_systems.ai.utility_scorer import UtilityScorer
from src.gameplay_systems.ai.goals import Goal, AttackUnitGoal
from src.gameplay_systems.ai.ai_persona import AIPersona
from src.core_engine.game_state import FactionEnum


class StrategicEvaluator:
    """
    Selects the best high-level goal for an AI unit's turn.
    
    The StrategicEvaluator is responsible for evaluating different potential goals
    and selecting the most appropriate one based on utility scoring. It considers
    the unit's state, the game state, and the AI persona to make this decision.
    
    This class implements the Strategic Phase of the two-phase AI decision-making process.
    """
    
    def __init__(self, utility_scorer: UtilityScorer, goal_library: List[Type[Goal]] = None):
        """
        Initialize a StrategicEvaluator.
        
        Args:
            utility_scorer: The utility scorer used to evaluate goals
            goal_library: A list of available goal types (classes, not instances)
        """
        self.utility_scorer = utility_scorer
        self.goal_library = goal_library or [AttackUnitGoal]  # Default to AttackUnitGoal if none provided
        self.logger = logging.getLogger(__name__)
    
    def select_best_goal(self, unit_state, game_state_manager, persona=None) -> Optional[Goal]:
        """
        Select the best goal for the given unit based on utility scoring.
        
        This method evaluates all valid potential goals and selects the one
        with the highest utility score, taking into account the unit's AI persona.
        
        Args:
            unit_state: The state of the AI unit
            game_state_manager: The current game state manager
            persona: The AI persona/profile that influences scoring
            
        Returns:
            Goal: The selected goal, or None if no valid goals are available
        """
        # Get unit ID for logging
        unit_id = getattr(unit_state, 'id', getattr(unit_state, 'unit_id', 'unknown'))
        best_goal = None
        highest_score = float('-inf')
        
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
            
        # Log unit info and persona
        persona_name = getattr(persona, 'name', str(persona))
        self.logger.info(f"Strategic Evaluation: Unit {unit_id} with persona {persona_name}")
        
        # 1. Goal Enumeration & Validation
        potential_goals = self.generate_valid_goal_instances(unit_state, game_state_manager)
        self.logger.info(f"Valid goals considered: {len(potential_goals)}")
        # 2. Strategic Evaluation
        goal_scores = []
        for goal in potential_goals:
            # Get the base score from the utility scorer
            base_score = self.utility_scorer.score_goal(goal, unit_state, game_state_manager)
            
            # Apply persona-specific goal weight
            goal_weight = persona.get_goal_weight(goal.goal_type)
            weighted_score = base_score * goal_weight
            
            # Log goal and score
            goal_info = f"{goal.goal_type}"
            if hasattr(goal, 'parameters') and goal.parameters:
                for key, value in goal.parameters.items():
                    goal_info += f", {key}: {value}"
            goal_scores.append((goal, weighted_score, goal_info))
            
            if weighted_score > highest_score:
                highest_score = weighted_score
                best_goal = goal
        
        # Log all goal scores
        for goal, score, goal_info in goal_scores:
            self.logger.info(f"Goal {goal_info} - Score: {score:.2f}")
        
        # 3. Goal Selection
        if best_goal:
            best_goal_info = f"{best_goal.goal_type}"
            if hasattr(best_goal, 'parameters') and best_goal.parameters:
                for key, value in best_goal.parameters.items():
                    best_goal_info += f", {key}: {value}"
            self.logger.info(f"Selected goal: {best_goal_info} with score {highest_score:.2f}")
        else:
            self.logger.info("No valid goal selected")
        
        return best_goal
    
    def generate_valid_goal_instances(self, unit, game_state) -> List[Goal]:
        """
        Generate valid goal instances based on the current game state.
        
        This method creates specific goal instances for each potential target
        or objective in the game state, and filters out invalid ones.
        
        Args:
            unit: The unit for which to generate goals
            game_state: The current game state
            
        Returns:
            List[Goal]: A list of valid goal instances
        """
        valid_instances = []
        
        for GoalType in self.goal_library:
            # Generate instances based on context (e.g., AttackUnit for each enemy)
            if GoalType == AttackUnitGoal:
                # Get all factions
                all_factions = list(FactionEnum)
                # Filter out the unit's own faction to get enemy factions
                enemy_factions = [faction for faction in all_factions if faction != unit.faction]
                
                # Get units from enemy factions
                for enemy_faction in enemy_factions:
                    for enemy in game_state.get_units_by_faction(enemy_faction):
                        goal_instance = AttackUnitGoal(target_unit_id=enemy.id)
                        if goal_instance.is_valid(unit, game_state):
                            valid_instances.append(goal_instance)
        
        return valid_instances