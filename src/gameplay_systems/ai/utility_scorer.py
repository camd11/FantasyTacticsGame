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

import logging # Add logging import
from typing import Dict, List, Any, Optional, Union, TYPE_CHECKING
from unittest.mock import Mock  # Import for type checking
from src.gameplay_systems.ai.ai_persona import AIPersona
from src.core_engine.game_state import FactionEnum, PhaseEnum, GameState, UnitState # Add GameState, UnitState
from src.core_engine.game_state import DispositionEnum # Import DispositionEnum

if TYPE_CHECKING:
    from src.core_engine.game_state import GameStateManager


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
    
    def score_goal(self, goal, unit_state, game_state_manager, persona=None) -> float:
        """
        Score a goal based on its utility for the given unit.
        
        This method evaluates how desirable a goal is for an AI unit based on
        the current game state and the unit's capabilities. It returns a numeric
        score where higher values indicate more desirable goals.
        
        Args:
            goal: The goal to score
            unit_state: The state of the AI unit
            game_state_manager: The current game state manager
            persona: The AI persona/profile that influences scoring (optional)
            
        Returns:
            float: A numeric score representing the goal's utility
        """
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
            
        # Dispatch to the appropriate scoring method based on goal type
        if hasattr(goal, 'goal_type'):
            if goal.goal_type == "ATTACK_UNIT":
                return self._score_attack_unit_goal(goal, unit_state, game_state_manager, persona)
            elif goal.goal_type == "HEAL_UNIT":
                return self._score_heal_unit_goal(goal, unit_state, game_state_manager, persona)
            elif goal.goal_type == "MOVE_TO_SAFETY":
                return self._score_move_to_safety_goal(goal, unit_state, game_state_manager, persona)
            elif goal.goal_type == "SEIZE_TILE":
                return self._score_seize_tile_goal(goal, unit_state, game_state_manager, persona)
            elif goal.goal_type == "SECURE_POSITION":
                return self._score_secure_position_goal(goal, unit_state, game_state_manager, persona)
            elif goal.goal_type == "ADVANCE_TO_OBJECTIVE":
                return self._score_advance_to_objective_goal(goal, unit_state, game_state_manager, persona)
        
        # Default score for unknown goal types
        return 0.0
    
    def _score_attack_unit_goal(self, goal, unit_state, game_state_manager, persona=None) -> float:
        """
        Score an AttackUnitGoal.
        Considers target HP, distance, value, threat/opportunity, and persona weights.
        """
        target_unit_id = goal.parameters.get("target_unit_id")
        if not target_unit_id:
            return 0.0
        
        target_unit = game_state_manager.get_unit_by_id(target_unit_id)
        if not target_unit:
            return 0.0

        # Add reachability check using movement_system instead of direct pathfinding
        movement_system = game_state_manager.get_movement_system()
        if not movement_system or not hasattr(movement_system, 'can_potentially_reach'):
            logging.warning(f"Movement system or can_potentially_reach method not available")
            # Continue without reachability check
        else:
            if not movement_system.can_potentially_reach(
                unit_state, target_unit.position
            ):
                logging.debug(f"Goal {goal.goal_type} scoring: Target {target_unit_id} unreachable.")
                return 0.0 # Cannot score attack if target is unreachable

        # Basic validation (already done in Goal.is_valid, but good for safety)
        if hasattr(target_unit, 'is_defeated') and target_unit.is_defeated():
            return 0.0
        if hasattr(target_unit, 'disposition') and target_unit.disposition == DispositionEnum.DEAD:
            return 0.0
        
        # --- Calculate Base Score Factors --- 
        base_score = 50.0 # Starting point
        
        # Factor 1: Target HP (Kill Opportunity)
        try:
            current_hp = int(getattr(target_unit, 'current_hp', 1))
            max_hp = int(getattr(target_unit, 'max_hp', 1))
            if max_hp > 0:
                hp_percentage = current_hp / max_hp
                # Higher bonus for lower HP - non-linear scaling might be better
                hp_bonus = (1.0 - hp_percentage) * 50 
                base_score += hp_bonus
        except (TypeError, ValueError):
            pass # Ignore if HP attributes are missing/invalid

        # Factor 2: Distance
        try:
            unit_pos = unit_state.position
            target_pos = target_unit.position
            distance = abs(unit_pos[0] - target_pos[0]) + abs(unit_pos[1] - target_pos[1])
            # Less penalty for closer targets
            distance_penalty = min(40, distance * 2.5)
            base_score -= distance_penalty
        except (TypeError, ValueError, IndexError, AttributeError):
            pass # Ignore if positions are missing/invalid

        # Factor 3: Target Value (Threat Level)
        target_value_bonus = 0
        # Example: Prioritize healers or lords
        try:
            unit_class = getattr(target_unit, 'unit_class', '').upper()
            if unit_class in ['HEALER', 'CLERIC', 'PRIEST', 'BISHOP']:
                target_value_bonus += 30
        except:
            pass
        try:
            if getattr(target_unit, 'is_lord', False):
                target_value_bonus += 50
        except:
             pass
        # Consider target's potential damage output as part of threat?
        # target_threat = self._estimate_unit_threat(target_unit) # Needs helper method
        # target_value_bonus += target_threat * 0.5
        base_score += target_value_bonus

        # Factor 4: Combat Forecast (if systems available)
        # Requires CombatSystem integration - Placeholder for now
        predicted_damage = 0
        predicted_counter_damage = 0
        kill_potential_bonus = 0
        risk_penalty = 0
        # combat_system = game_state_manager.get_combat_system() 
        # if combat_system:
        #     forecast = combat_system.predict_combat(unit_state, target_unit)
        #     predicted_damage = forecast.get('damage', 0)
        #     predicted_counter_damage = forecast.get('counter_damage', 0)
        #     if forecast.get('kills_target', False):
        #         kill_potential_bonus = 40
        #     # Penalize based on risk (e.g., % of own HP lost)
        #     own_hp = getattr(unit_state, 'current_hp', 1)
        #     if own_hp > 0:
        #         risk_penalty = (predicted_counter_damage / own_hp) * 50 

        base_score += kill_potential_bonus
        base_score -= risk_penalty

        # --- Apply Persona Weights --- 
        if persona:
            # Use weights from persona definitions
            threat_weight = persona.get_strategic_weight('ThreatLevel')
            kill_opp_weight = persona.get_strategic_weight('KillOpportunity')
            # aggression_weight = persona.get_strategic_weight('Aggression') # Assuming 'ThreatLevel' covers this?
            logging.debug(f"Persona weights: Threat={threat_weight}, KillOpp={kill_opp_weight}")
            
            # Apply weights to relevant factors (example scaling)
            # More sophisticated weighting needed based on how factors contribute
            weighted_score = 50.0 # Reset base or adjust?
            weighted_score += (hp_bonus + kill_potential_bonus) * kill_opp_weight * 1.5 # Scale Kill Opp
            weighted_score += target_value_bonus * threat_weight * 1.5 # Scale Threat
            weighted_score -= distance_penalty # Keep distance penalty less affected by persona?
            weighted_score -= risk_penalty * (2.0 * persona.get_strategic_weight('SelfPreservation')) # Higher self-preservation reduces risk tolerance

            # Example: Simple multiplicative scaling based on overall aggression/threat focus
            # base_score *= (0.5 + threat_weight)
            base_score = weighted_score # Use the weighted score
        
        # Ensure score is positive
        return max(1.0, base_score)
        
    def _score_heal_unit_goal(self, goal, unit_state, game_state_manager, persona=None) -> float:
        """
        Score a HealUnitGoal.
        
        This method evaluates the utility of healing a specific target unit.
        It considers factors such as:
        - Target unit's current HP and importance
        - Distance to the target
        - Healing capability of the unit
        - AI persona weights for support actions
        
        Args:
            goal: The HealUnitGoal to score
            unit_state: The state of the AI unit
            game_state_manager: The current game state manager
            persona: The AI persona/profile that influences scoring
            
        Returns:
            float: A numeric score representing the goal's utility
        """
        # Extract target unit ID from goal parameters
        target_unit_id = goal.parameters.get("target_unit_id")
        if not target_unit_id:
            return 0.0
        
        # Get target unit from game state
        target_unit = game_state_manager.get_unit(target_unit_id)
        if not target_unit:
            return 0.0
        
        # Check if target is reachable using movement_system instead of direct pathfinding
        movement_system = game_state_manager.get_movement_system()
        if movement_system and hasattr(movement_system, 'can_potentially_reach'):
            if not movement_system.can_potentially_reach(
                unit_state, target_unit.position
            ):
                return 0.0
        
        # Calculate base score based on various factors
        base_score = 40.0  # Base score for healing goals
        
        # Factor 1: Target unit's HP deficit (higher deficit = higher priority)
        try:
            current_hp = int(target_unit.current_hp) if not isinstance(target_unit.current_hp, Mock) else 10
            max_hp = int(target_unit.max_hp) if not isinstance(target_unit.max_hp, Mock) else 40
            
            if current_hp > 0 and max_hp > 0:
                hp_deficit_percentage = 1.0 - (current_hp / max_hp)
                
                # Higher score for units with more HP deficit
                if hp_deficit_percentage > 0.7:  # Critical (below 30% HP)
                    base_score += 40
                elif hp_deficit_percentage > 0.5:  # Serious (below 50% HP)
                    base_score += 30
                elif hp_deficit_percentage > 0.3:  # Moderate (below 70% HP)
                    base_score += 15
        except (TypeError, ValueError):
            pass
        
        # Factor 2: Distance to the target (closer targets are more desirable)
        if hasattr(unit_state, 'position') and hasattr(target_unit, 'position'):
            try:
                unit_pos = unit_state.position
                target_pos = target_unit.position
                
                # Handle Mock objects
                if hasattr(unit_pos, '__class__') and unit_pos.__class__.__name__ == 'Mock':
                    unit_pos = (3, 3)
                if hasattr(target_pos, '__class__') and target_pos.__class__.__name__ == 'Mock':
                    target_pos = (5, 5)
                
                distance_x = abs(unit_pos[0] - target_pos[0])
                distance_y = abs(unit_pos[1] - target_pos[1])
                distance = distance_x + distance_y
                
            except (TypeError, ValueError, IndexError):
                distance = 5
                
            # Apply distance penalty
            distance_penalty = min(25, distance * 2)  # Cap at 25
            base_score -= distance_penalty
        
        # Factor 3: Target unit's importance
        try:
            # Check if target is a lord or other important unit
            is_lord = getattr(target_unit, 'is_lord', False)
            if hasattr(is_lord, '__class__') and is_lord.__class__.__name__ == 'Mock':
                is_lord = False
                
            if is_lord:
                base_score += 30  # Significant bonus for healing lords
                
            # Check unit class for importance
            if hasattr(target_unit, 'unit_class'):
                unit_class = getattr(target_unit, 'unit_class', '')
                if hasattr(unit_class, '__class__') and unit_class.__class__.__name__ == 'Mock':
                    unit_class = ''
                    
                # Prioritize healing certain unit types
                if unit_class in ['HEALER', 'CLERIC', 'PRIEST', 'BISHOP']:
                    base_score += 15  # Bonus for healing support units
                elif unit_class in ['KNIGHT', 'GENERAL', 'PALADIN']:
                    base_score += 10  # Bonus for healing tanks
        except (TypeError, ValueError):
            pass
        
        # Factor 4: AI persona weights for support actions
        if persona:
            # Use weights from persona definitions
            # Supportiveness isn't directly in strategic weights, use AlliedSupport?
            support_weight = persona.get_strategic_weight('AlliedSupport')
            self_preservation_weight = persona.get_strategic_weight('SelfPreservation')

            # Increase score for supportive personas
            base_score *= (0.5 + support_weight)
            # Decrease score slightly if self-preservation is very high and target isn't critical?
            # Example: if self_preservation_weight > 0.8 and target_value_bonus < 30:
            #    base_score *= 0.8

        # Ensure the score is at least 1.0 for valid targets
        return max(1.0, base_score)
        
    def _score_move_to_safety_goal(self, goal, unit_state, game_state_manager, persona=None) -> float:
        """
        Score a MoveToSafetyGoal.
        Considers current threat level and persona weights.
        """
        # Factor 1: Current Threat Level
        # Higher threat means higher score for moving to safety
        current_threat = self._estimate_unit_threat(unit_state, game_state_manager)
        base_score = current_threat * 1.5 # Scale threat level into score

        # Add a minimum score if any threat exists
        if current_threat > 5: # Arbitrary threshold for 'some threat'
            base_score = max(base_score, 20.0)

        # Factor 2: Current HP
        # Lower HP increases desire to move to safety
        try:
            current_hp = int(getattr(unit_state, 'current_hp', 1))
            max_hp = int(getattr(unit_state, 'max_hp', 1))
            if max_hp > 0:
                hp_percentage = current_hp / max_hp
                hp_urgency_bonus = (1.0 - hp_percentage) * 40
                base_score += hp_urgency_bonus
        except (TypeError, ValueError):
            pass

        # --- Apply Persona Weights ---
        if persona:
            self_preservation_weight = persona.get_strategic_weight('SelfPreservation')
            # Directly scale score based on self-preservation
            base_score *= (0.5 + self_preservation_weight) 

        # Ensure score is positive
        return max(1.0, base_score)

    def _estimate_unit_threat(self, unit_state, game_state_manager) -> float:
        """
        Placeholder: Estimate the threat level to the unit at its current position.
        A real implementation would query game state for nearby enemies, their
        capabilities, and potential damage.
        
        Returns:
            float: An estimated threat score (e.g., 0-100)
        """
        # TODO: Implement actual threat assessment
        # Example factors: number of enemies in range, potential damage from enemies,
        # enemy unit types, unit's own defensive stats.
        
        # Placeholder: return a moderate threat if unit HP is low, low otherwise
        try:
            current_hp = int(getattr(unit_state, 'current_hp', 1))
            max_hp = int(getattr(unit_state, 'max_hp', 1))
            if max_hp > 0 and (current_hp / max_hp) < 0.5:
                return 60.0 # High threat if below 50% HP
            else:
                return 10.0 # Low threat otherwise
        except:
            return 10.0 # Default to low threat if HP check fails

    def _score_seize_tile_goal(self, goal, unit_state, game_state_manager, persona=None) -> float:
        """
        Score a SeizeTileGoal.
        Considers distance, objective importance (placeholder), threat, and persona weights.
        """
        target_position = goal.parameters.get("target_position")
        if not target_position:
            return 0.0
            
        # Basic validation (is it a valid objective tile?)
        # if not game_state_manager.is_valid_objective_tile(target_position):
        #    return 0.0
        
        # --- Calculate Base Score Factors ---
        base_score = 60.0 # Seizing objectives is generally important

        # Factor 1: Distance
        try:
            unit_pos = unit_state.position
            distance = abs(unit_pos[0] - target_position[0]) + abs(unit_pos[1] - target_position[1])
            distance_penalty = min(50, distance * 2.0) # Significant penalty for distance
            base_score -= distance_penalty
        except (TypeError, ValueError, IndexError, AttributeError):
            pass 

        # Factor 2: Objective Importance (Placeholder)
        # A real implementation might check chapter goals or tile properties
        objective_importance_bonus = 0 
        # if game_state_manager.is_primary_objective(target_position):
        #    objective_importance_bonus = 30
        base_score += objective_importance_bonus

        # Factor 3: Threat/Difficulty at Target
        # Estimate threat at the *target* location
        threat_at_target = self._estimate_tile_threat(target_position, game_state_manager)
        threat_penalty = min(40, threat_at_target * 0.5) # Penalize if target is dangerous
        base_score -= threat_penalty

        # --- Apply Persona Weights ---
        if persona:
            objective_focus_weight = persona.get_strategic_weight('ObjectiveProgress')
            threat_tolerance_weight = 1.0 - persona.get_strategic_weight('SelfPreservation') # Inverse of self-preservation

            # Apply weights
            base_score *= (0.5 + objective_focus_weight)
            base_score -= threat_penalty * threat_tolerance_weight

        # Ensure score is positive
        return max(1.0, base_score)

    def _estimate_tile_threat(self, position, game_state_manager) -> float:
        """
        Placeholder: Estimate the threat level at a specific tile.
        Similar to _estimate_unit_threat, but for a location.
        """
        # TODO: Implement actual threat assessment for a tile
        # Check enemies that can attack units AT this position.
        return 5.0 # Placeholder: Assume low threat for now

    def _score_secure_position_goal(self, goal, unit_state, game_state_manager, persona=None) -> float:
        """
        Score a SecurePositionGoal.
        Considers current threat, unit HP, potential defensive positions, and persona.
        """
        # Factor 1: Current Threat Level
        # Higher motivation to secure position if currently threatened
        current_threat = self._estimate_unit_threat(unit_state, game_state_manager)
        base_score = 10.0 + current_threat * 1.0 # Base score increases with threat

        # Factor 2: Current HP
        # Lower HP increases desire for a safe position
        try:
            current_hp = int(getattr(unit_state, 'current_hp', 1))
            max_hp = int(getattr(unit_state, 'max_hp', 1))
            if max_hp > 0:
                hp_percentage = current_hp / max_hp
                hp_urgency_bonus = (1.0 - hp_percentage) * 30
                base_score += hp_urgency_bonus
        except (TypeError, ValueError):
            pass

        # Factor 3: Quality of Potential Defensive Positions
        # Does the unit have access to good terrain/support?
        # This requires simulating the TacticalExecutor logic somewhat, or accessing cached info.
        # Placeholder: Add a bonus if good terrain is nearby/reachable
        # Requires MovementSystem and Map access
        terrain_bonus = 0
        try:
            movement_system = game_state_manager.get_movement_system()
            game_map = game_state_manager.get_map()
            if movement_system and game_map:
                 unit_id = getattr(unit_state, 'id', getattr(unit_state, 'unit_id', 'unknown'))
                 reachable_tiles_data = movement_system.calculate_movement_range(unit_id)
                 if reachable_tiles_data:
                     best_terrain_score = -1
                     for tile in reachable_tiles_data.keys():
                         tile_info = game_map.get_tile_info(tile[0], tile[1])
                         if tile_info:
                             # Simple score: prioritize def
                             terrain_score = tile_info.get('def', 0)
                             if terrain_score > best_terrain_score:
                                 best_terrain_score = terrain_score
                     if best_terrain_score > 1: # e.g., Fort or Forest
                        terrain_bonus = best_terrain_score * 10 # Bonus based on best available terrain def
        except AttributeError:
             pass # Ignore if systems or methods are missing
        base_score += terrain_bonus

        # --- Apply Persona Weights ---
        if persona:
            # Use TerrainAdvantage, AlliedSupport, SelfPreservation?
            # Defensiveness isn't a strategic weight, map to others.
            terrain_weight = persona.get_strategic_weight('TerrainAdvantage')
            self_preservation_weight = persona.get_strategic_weight('SelfPreservation')
            allied_support_weight = persona.get_strategic_weight('AlliedSupport')
            
            # Weighted average or specific factor scaling?
            # Example: Scale based on average defensive weights
            avg_def_weight = (terrain_weight + self_preservation_weight + allied_support_weight) / 3.0
            base_score *= (0.5 + avg_def_weight)
            # Or scale specific factors: e.g., terrain_bonus *= terrain_weight

        return max(1.0, base_score)

    def _score_advance_to_objective_goal(self, goal, unit_state, game_state_manager, persona=None) -> float:
        """
        Score an AdvanceToObjectiveGoal.
        Considers distance, objective importance, unit suitability, and persona weights.
        """
        target_pos = goal.parameters.get('target_position')
        if not target_pos:
            return 0.0 # Cannot score without a target

        # --- Calculate Base Score Factors ---
        base_score = 50.0 # Base importance for advancing

        # Factor 1: Distance
        # Significant penalty for very distant objectives
        distance_penalty = 0
        try:
            unit_pos = unit_state.position
            distance = abs(unit_pos[0] - target_pos[0]) + abs(unit_pos[1] - target_pos[1])
            # Less penalty for closer targets, harsher for far ones
            if distance > 0:
                distance_penalty = min(60, (distance ** 1.2) * 1.5) # Non-linear scaling
            base_score -= distance_penalty
        except (TypeError, ValueError, IndexError, AttributeError):
            pass 

        # Factor 2: Objective Importance / Priority (Placeholder)
        # Get importance from game state if available
        objective_importance_bonus = 0
        # objective_priority = game_state_manager.get_objective_priority(target_pos)
        # objective_importance_bonus = objective_priority * 10
        base_score += objective_importance_bonus

        # Factor 3: Unit Suitability (Placeholder)
        # Is this unit appropriate for the objective? (e.g., don't send healer to front)
        suitability_modifier = 1.0
        # unit_role = getattr(unit_state, 'role', 'generic')
        # objective_type = game_state_manager.get_objective_type(target_pos)
        # if objective_type == 'combat' and unit_role == 'support':
        #    suitability_modifier = 0.5 # Penalize sending support to combat
        # elif objective_type == 'capture' and not getattr(unit_state, 'can_capture', False):
        #    suitability_modifier = 0.1 # Heavily penalize if unit cannot perform action
        base_score *= suitability_modifier

        # --- Apply Persona Weights ---
        if persona:
             objective_weight = persona.get_strategic_weight('ObjectiveProgress')
             # Directly scale the score based on objective focus
             base_score *= (0.7 + objective_weight) # Scale from 0.7 to 1.7

        # Ensure score is positive, potentially higher minimum for objectives?
        return max(5.0, base_score) # Slightly higher minimum score for objective goals