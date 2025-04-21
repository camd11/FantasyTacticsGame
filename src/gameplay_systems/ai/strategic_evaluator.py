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
# from src.gameplay_systems.ai.goals import Goal, AttackUnitGoal # Old
# Import all relevant goal types
from src.gameplay_systems.ai.goals import (
    Goal, AttackUnitGoal, HealUnitGoal, MoveToSafetyGoal, SeizeTileGoal,
    SecurePositionGoal, AdvanceToObjectiveGoal
)
from src.gameplay_systems.ai.ai_persona import AIPersona
from src.core_engine.game_state import FactionEnum
from src.core_engine.game_state import DispositionEnum


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
        # Define the default library including all standard goal types
        default_goal_library = [
            AttackUnitGoal, HealUnitGoal, MoveToSafetyGoal, SeizeTileGoal,
            SecurePositionGoal, AdvanceToObjectiveGoal
        ]
        self.goal_library = goal_library or default_goal_library
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
        Generate valid goal instances for all goal types in the library based on the current game state.
        """
        valid_instances = []
        unit_id = getattr(unit, 'id', getattr(unit, 'unit_id', 'unknown'))
        self.logger.debug(f"Generating valid goals for unit {unit_id} from library: {[g.__name__ for g in self.goal_library]}")

        # --- Get Potential Targets/Context from Game State --- 
        # These would ideally be optimized lookups
        all_units = game_state.get_all_units()
        enemy_units = [u for u in all_units if u.faction != unit.faction and getattr(u, 'disposition', None) != DispositionEnum.DEAD]
        allied_units = [u for u in all_units if u.faction == unit.faction and getattr(u, 'disposition', None) != DispositionEnum.DEAD and u.id != unit_id]
        # Objective tiles/units would be retrieved from game_state, e.g.:
        # objective_tiles = getattr(game_state, 'get_objective_tiles', lambda: [])() 
        # primary_objectives = getattr(game_state, 'get_primary_objectives', lambda: [])() # Could return positions or unit IDs
        
        # Get objectives from the current game state
        all_objectives = []
        if hasattr(game_state, 'current_game_state') and hasattr(game_state.current_game_state, 'objectives'):
            all_objectives = game_state.current_game_state.objectives
        else:
            self.logger.warning("Could not retrieve objectives from game_state.current_game_state.objectives")

        # Extract relevant objective positions based on type and faction
        seize_objective_tiles = [tuple(obj['position']) for obj in all_objectives if obj.get('type') == 'SEIZE' and 'position' in obj]
        # AdvanceToObjective might target SEIZE points or other designated locations/units
        advance_targets = [] 
        for obj in all_objectives:
             # Consider objectives relevant to the unit's faction or global objectives
             obj_faction = obj.get('faction')
             if obj_faction is None or obj_faction == unit.faction.name: # Match faction name string
                if obj.get('type') == 'SEIZE' and 'position' in obj:
                    advance_targets.append(tuple(obj['position']))
                # Add other potential objective types here (e.g., DEFEAT_BOSS, REACH_AREA)

        self.logger.debug(f"Found {len(enemy_units)} enemies, {len(allied_units)} allies.")
        self.logger.debug(f"Seize objective tiles: {seize_objective_tiles}")
        self.logger.debug(f"Advance targets: {advance_targets}")

        # --- Generate Instances for Each Goal Type --- 
        for GoalType in self.goal_library:
            generated_count = 0
            validated_count = 0
            
            # 1. AttackUnitGoal: Target each valid enemy
            if GoalType == AttackUnitGoal:
                for enemy in enemy_units:
                    goal_instance = AttackUnitGoal(target_unit_id=enemy.id, ai_unit=unit)
                    generated_count += 1
                    if goal_instance.is_valid(unit, game_state):
                        valid_instances.append(goal_instance)
                        validated_count += 1
            
            # 2. HealUnitGoal: Target each injured ally (if unit can heal)
            elif GoalType == HealUnitGoal:
                # Check if unit can heal (basic check, refine in Goal.is_valid)
                if hasattr(unit, 'can_heal') and unit.can_heal(): # Or check inventory/class
                    for ally in allied_units:
                        # Check if ally is injured (basic check, refine in Goal.is_valid)
                        if hasattr(ally, 'current_hp') and hasattr(ally, 'max_hp') and ally.current_hp < ally.max_hp:
                             goal_instance = HealUnitGoal(target_unit_id=ally.id, ai_unit=unit)
                             generated_count += 1
                             if goal_instance.is_valid(unit, game_state):
                                 valid_instances.append(goal_instance)
                                 validated_count += 1
            
            # 3. MoveToSafetyGoal: Always consider if threatened (validation checks threat)
            elif GoalType == MoveToSafetyGoal:
                 goal_instance = MoveToSafetyGoal(ai_unit=unit)
                 generated_count += 1
                 if goal_instance.is_valid(unit, game_state):
                     valid_instances.append(goal_instance)
                     validated_count += 1
            
            # 4. SeizeTileGoal: Target each objective tile
            elif GoalType == SeizeTileGoal:
                 # Check if unit can seize (basic check, refine in Goal.is_valid)
                 if hasattr(unit, 'can_seize') and unit.can_seize(): # Or check class
                     for tile_pos in seize_objective_tiles: # Use extracted seize tiles
                         goal_instance = SeizeTileGoal(target_position=tile_pos, ai_unit=unit)
                         generated_count += 1
                         if goal_instance.is_valid(unit, game_state):
                             valid_instances.append(goal_instance)
                             validated_count += 1
            
            # 5. SecurePositionGoal: Always consider (validation checks necessity)
            elif GoalType == SecurePositionGoal:
                 goal_instance = SecurePositionGoal(ai_unit=unit)
                 generated_count += 1
                 if goal_instance.is_valid(unit, game_state):
                     valid_instances.append(goal_instance)
                     validated_count += 1
            
            # 6. AdvanceToObjectiveGoal: Target primary objectives (position or unit)
            elif GoalType == AdvanceToObjectiveGoal:
                 for target_pos in advance_targets: # Use extracted advance targets
                     # target_pos = None # No longer needed
                     # self.logger.debug(f"Processing objective: {objective}")
                     # if isinstance(objective, tuple) and len(objective) == 2: # Assume it's a position
                     #     target_pos = objective
                     # elif hasattr(objective, 'position'): # Assume it's a unit/object with position
                     #     target_pos = objective.position
                     # Add other objective types? (e.g., defeat specific unit ID)
                      
                     if target_pos: # Target position is already derived
                         self.logger.debug(f"  Found target_pos: {target_pos}")
                         # Create goal with parameters set (unlike placeholder)
                         goal_instance = AdvanceToObjectiveGoal(ai_unit=unit)
                         goal_instance.parameters = {"target_position": target_pos} # Set target
                         generated_count += 1
                         if goal_instance.is_valid(unit, game_state):
                             self.logger.debug(f"    Goal instance VALID and added with parameters: {goal_instance.parameters}")
                             valid_instances.append(goal_instance)
                             validated_count += 1
                         else:
                             self.logger.debug(f"    Goal instance INVALID.")
                     else:
                         self.logger.debug(f"  No target_pos found for objective: {target_pos}")
            
            self.logger.debug(f"Goal Type {GoalType.__name__}: Generated {generated_count}, Validated {validated_count}")
        
        self.logger.debug(f"Total valid goal instances generated for unit {unit_id}: {len(valid_instances)}")
        return valid_instances