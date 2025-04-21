"""
Guard Archetype Handler Module

This module implements the handler for the GUARD and BOSS_GUARD AI archetypes.
These archetypes represent defensive units that remain in a specific area (guard post)
and only engage enemies that enter their designated guard radius. This behavior is
commonly used for stationary enemies like throne guards, boss units, and defensive
formations.

The GuardArchetypeHandler implements a defensive, position-focused behavior pattern
that prioritizes maintaining control of a specific area rather than pursuing enemies.
It represents the standard behavior for defensive enemy formations and boss units.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any

from src.gameplay_systems.ai.ai_types import AIProfile, AIBehaviorType, AIAction
from src.gameplay_systems.ai.ai_archetype_handler import AIArchetypeHandler


class GuardArchetypeHandler(AIArchetypeHandler):
    """
    Handler for the GUARD and BOSS_GUARD AI archetypes.
    
    This archetype implements defensive behavior for units that protect a specific
    area or position. It prioritizes:
    1. Staying in a designated area (guard post) defined by a guard radius
    2. Attacking enemies that enter the guard radius
    3. Only moving within the guard radius when necessary
    4. Maintaining position when no enemies are nearby
    
    The GUARD archetype is suitable for defensive enemy formations, throne guards,
    and boss units. It corresponds to the STATIONARY and DEFENSIVE behavior types
    in legacy AI configurations and implements a position-focused behavior pattern.
    """
    
    def can_handle(self, ai_profile: AIProfile) -> bool:
        """
        Check if this handler can handle the given AI profile.
        
        This method determines whether this handler is appropriate for the given
        AI profile by checking if its behavior type is one of the guard-related types:
        GUARD, BOSS_GUARD, STATIONARY, or DEFENSIVE (legacy equivalents).
        
        The GuardArchetypeHandler handles four behavior types:
        - GUARD: The modern archetype for defensive, position-focused units
        - BOSS_GUARD: A specialized variant for boss units (often on thrones)
        - STATIONARY: Legacy equivalent that doesn't move unless attacked
        - DEFENSIVE: Legacy equivalent that prioritizes defensive positions
        
        Args:
            ai_profile: The AI profile to check, containing the behavior type
            
        Returns:
            True if the profile has a guard-related behavior type, False otherwise
        """
        return ai_profile.behavior_type in [
            AIBehaviorType.GUARD, 
            AIBehaviorType.BOSS_GUARD,
            AIBehaviorType.STATIONARY, 
            AIBehaviorType.DEFENSIVE
        ]
    
    def modify_action_scores(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> List[Dict]:
        """
        Modify action scores based on the GUARD archetype.
        
        This method adjusts the scores of possible actions to reflect the defensive
        priorities of the GUARD archetype:
        1. Attack actions against targets within guard radius receive a 20% score boost
        2. Attack actions against targets outside guard radius receive a 50% score penalty
        3. Move actions are penalized based on distance from the guard post
        4. Moves outside the guard radius receive a severe 70% penalty
        
        These adjustments ensure that GUARD units will prefer to stay near their post
        and only engage enemies that enter their designated area.
        
        The score modifications implement the core GUARD behavior pattern:
        - Territorial defense of a specific area (guard post)
        - Limited pursuit of enemies that enter the guard radius
        - Strong preference for maintaining position when no threats are present
        - Gradual reduction in action utility as distance from post increases
        
        Args:
            unit_id: ID of the unit whose actions are being evaluated
            possible_actions: List of possible actions with initial scores
            ai_profile: AI profile containing behavior parameters for the unit
            
        Returns:
            Modified list of possible actions with updated scores reflecting GUARD priorities
        """
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return possible_actions
            
        # Get guard radius and post position
        guard_radius = ai_profile.guard_radius or 3  # Default guard radius if not specified
        post_position = unit.position  # Default to current position
        
        # If a protect_location is specified, use that instead
        if ai_profile.protect_location:
            post_position = ai_profile.protect_location
        
        for action in possible_actions:
            if action['type'] == 'ATTACK':
                # Check if target is within guard radius
                target_id = action['target_info'].get('target_unit_id')
                if target_id:
                    target_unit = self.unitSystem.get_unit(target_id)
                    if target_unit:
                        distance = self.mapSystem.calculate_manhattan_distance(post_position, target_unit.position)
                        if distance <= guard_radius:
                            action['score'] *= 1.2  # Boost attacks within guard radius
                        else:
                            action['score'] *= 0.5  # Penalize attacks outside guard radius
            
            elif action['type'] == 'MOVE' and not action['is_current_pos'] and action.get('path'):
                # Penalize moves that take the unit far from its post
                move_destination = action['path'][-1]
                distance_from_post = self.mapSystem.calculate_manhattan_distance(move_destination, post_position)
                
                if distance_from_post > guard_radius:
                    action['score'] *= 0.3  # Severely penalize moves outside guard radius
                elif distance_from_post > 0:
                    # Gradually reduce score as distance increases
                    action['score'] *= (1.0 - (distance_from_post / (guard_radius * 2)))
        
        return possible_actions
    
    def select_best_action(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> Optional[AIAction]:
        """
        Select the best action based on the GUARD archetype.
        
        This method implements the action selection logic for the GUARD archetype:
        1. Check if any enemies are within the guard radius
        2. If no enemies are in range and the unit is not threatened, prefer to stay in place
        3. If staying in place has no good actions, default to WAIT
        4. If enemies are in range or the unit is threatened, fall back to standard selection
        
        This selection logic ensures that GUARD units will maintain their position when
        no threats are present, but will respond appropriately when enemies enter their
        guard radius or directly threaten them.
        
        The method implements a conditional priority system:
        - When no enemies are in guard radius and unit is not threatened:
          * First priority: Stationary actions (actions from current position)
          * Second priority: WAIT action
        - When enemies are in guard radius or unit is threatened:
          * Fall back to standard selection logic (highest scoring action)
        
        This priority system ensures that GUARD units maintain their defensive posture
        when not threatened, but respond appropriately to threats within their area.
        
        Args:
            unit_id: ID of the unit whose actions are being evaluated
            possible_actions: List of possible actions with scores (modified by modify_action_scores)
            ai_profile: AI profile containing behavior parameters for the unit
            
        Returns:
            The best AIAction object representing the selected action, or None if no valid action is found
        """
        if not possible_actions:
            return None
            
        # Filter out invalid actions (e.g., path not found for move-actions)
        valid_actions = [a for a in possible_actions if a['type'] == 'WAIT' or
                          a['is_current_pos'] or a['path'] is not None]
        
        if not valid_actions:
            return None
            
        # Get guard radius
        guard_radius = ai_profile.guard_radius or 3  # Default guard radius if not specified
        
        # Check if any enemy is within guard radius
        unit = self.unitSystem.get_unit(unit_id)
        if unit:
            enemies_in_range = self._get_enemies_in_radius(unit.position, guard_radius)
            
            if not enemies_in_range and not self._is_threatened(unit_id):
                # No enemies in guard radius and not threatened, prefer to stay put
                stationary_actions = [a for a in valid_actions if a['is_current_pos']]
                if stationary_actions:
                    # Sort stationary actions by score
                    stationary_actions.sort(key=lambda a: a['score'], reverse=True)
                    best_stationary = stationary_actions[0]
                    
                    # If the best stationary action has a reasonable score, choose it
                    if best_stationary['score'] >= 10:
                        target_data = best_stationary.get('target_info', {}).copy()
                        return AIAction(best_stationary['type'], unit_id, target_data)
                
                # If no good stationary action, just wait
                wait_action = next((a for a in valid_actions if a['type'] == 'WAIT'), None)
                if wait_action:
                    return AIAction('WAIT', unit_id, {})
        
        # Fall back to default selection if enemies are in range or unit is threatened
        return super().select_best_action(unit_id, valid_actions, ai_profile)
    
    def _get_enemies_in_radius(self, position: Tuple[int, int], radius: int) -> List[str]:
        """
        Get a list of enemy unit IDs within a certain radius of a position.
        
        This helper method identifies all enemy units within a specified Manhattan
        distance of a given position. It's used to determine if any enemies have
        entered the guard radius, which would trigger a response from the GUARD unit.
        
        The method:
        1. Determines the current faction from the game state
        2. Iterates through all units in the game state
        3. Identifies units of different factions (enemies)
        4. Calculates the Manhattan distance from the specified position
        5. Returns IDs of enemy units within the specified radius
        
        This method is central to the GUARD behavior pattern, as it defines the
        "territory" that the unit is responsible for defending.
        
        Args:
            position: The coordinate (x, y) to check from (typically the guard post)
            radius: The maximum Manhattan distance to include in the search
            
        Returns:
            List of enemy unit IDs that are within the specified radius
        """
        enemies = []
        
        # Get the current faction
        current_phase = self.gameStateManager.current_game_state.current_phase
        current_faction = self.gameStateManager.get_faction_for_phase(current_phase)
        
        # Check all units
        for unit_id, unit in self.gameStateManager.current_game_state.unit_states.items():
            if unit.faction != current_faction:
                distance = self.mapSystem.calculate_manhattan_distance(position, unit.position)
                if distance <= radius:
                    enemies.append(unit_id)
        
        return enemies
    
    def _is_threatened(self, unit_id: str) -> bool:
        """
        Check if a unit is threatened by enemy units.
        
        This helper method determines whether a unit is currently in danger of
        being attacked by any enemy unit. It's used to decide whether a GUARD
        unit should maintain its stationary position or take defensive action.
        
        The method checks if any enemy unit can attack the specified unit from
        its current position by:
        1. Iterating through all units in the game state
        2. Identifying units of different factions (enemies)
        3. Checking if each enemy can attack the specified unit
        
        This threat detection allows GUARD units to respond to immediate dangers
        even if the threatening unit hasn't entered the guard radius, providing
        a self-preservation mechanism that overrides the normal guard behavior.
        
        Args:
            unit_id: ID of the unit to check for threats
            
        Returns:
            True if any enemy can attack the unit, False otherwise
        """
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return False
            
        # Simple implementation: check if any enemy unit can attack this unit
        for enemy_id, enemy in self.gameStateManager.current_game_state.unit_states.items():
            if unit.faction != enemy.faction:
                if self._can_attack_target(enemy_id, unit_id):
                    return True
                    
        return False
    
    def _can_attack_target(self, attacker_id: str, target_id: str) -> bool:
        """
        Check if a unit can attack a target from current position.
        
        This helper method determines whether one unit can attack another from
        their current positions. It considers:
        1. The attacker's equipped weapon range
        2. The distance between the attacker and target
        3. The faction relationship (must be different factions)
        
        The method:
        1. Retrieves the attacker and target units
        2. Gets the attacker's equipped weapon and its range
        3. Calculates the Manhattan distance between the units
        4. Checks if the target is within the weapon's range
        5. Verifies that the units belong to different factions
        
        This method is used by _is_threatened to determine if a unit is in danger,
        providing a critical component of the GUARD unit's threat assessment.
        
        Args:
            attacker_id: ID of the attacking unit
            target_id: ID of the target unit
            
        Returns:
            True if the attacker can attack the target from its current position, False otherwise
        """
        attacker = self.unitSystem.get_unit(attacker_id)
        target = self.unitSystem.get_unit(target_id)
        if not attacker or not target:
            return False
            
        # Get attacker's weapon range
        weapon = self.inventorySystem.get_equipped_weapon(attacker_id)
        if not weapon:
            weapon_range_min = 1
            weapon_range_max = 1
        else:
            weapon_data = self.dataProvider.get_item_data(weapon)
            if not weapon_data:
                weapon_range_min = 1
                weapon_range_max = 1
            else:
                weapon_range_min = weapon_data.range_min
                weapon_range_max = weapon_data.range_max
        
        # Check if target is in range
        distance = self.mapSystem.calculate_manhattan_distance(attacker.position, target.position)
        return weapon_range_min <= distance <= weapon_range_max and attacker.faction != target.faction