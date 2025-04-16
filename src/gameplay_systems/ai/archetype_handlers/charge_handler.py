"""
Charge Archetype Handler Module

This module implements the handler for the CHARGE AI archetype.
The CHARGE archetype represents aggressive units that prioritize engaging enemy units
in combat, moving toward enemies when attacks aren't immediately available, and
focusing on high-value targets. This is one of the most common AI behaviors for
enemy units in the game.

The ChargeArchetypeHandler implements an aggressive, offense-oriented behavior pattern
that seeks to engage enemy units in combat whenever possible. It represents the standard
behavior for most offensive enemy units in the game.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any

from src.gameplay_systems.ai.ai_types import AIProfile, AIBehaviorType, AIAction
from src.gameplay_systems.ai.ai_archetype_handler import AIArchetypeHandler


class ChargeArchetypeHandler(AIArchetypeHandler):
    """
    Handler for the CHARGE AI archetype.
    
    This archetype implements aggressive behavior for units that actively seek out
    and engage enemy units. It prioritizes:
    1. Attacking enemies within range (with preference for high-value targets)
    2. Moving towards the nearest enemy when attacks aren't immediately available
    3. Prioritizing high-value targets such as lords, healers, and weakened units
    
    The CHARGE archetype is suitable for most offensive enemy units and represents
    the standard aggressive behavior pattern. It corresponds to the AGGRESSIVE
    behavior type in legacy AI configurations.
    """
    
    def can_handle(self, ai_profile: AIProfile) -> bool:
        """
        Check if this handler can handle the given AI profile.
        
        This method determines whether this handler is appropriate for the given
        AI profile by checking if its behavior type is either CHARGE or AGGRESSIVE
        (the legacy equivalent).
        
        The ChargeArchetypeHandler handles two behavior types:
        - CHARGE: The modern archetype for aggressive, attack-oriented units
        - AGGRESSIVE: The legacy equivalent for backward compatibility
        
        Args:
            ai_profile: The AI profile to check, containing the behavior type
            
        Returns:
            True if the profile has CHARGE or AGGRESSIVE behavior type, False otherwise
        """
        return ai_profile.behavior_type in [AIBehaviorType.CHARGE, AIBehaviorType.AGGRESSIVE]
    
    def modify_action_scores(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> List[Dict]:
        """
        Modify action scores based on the CHARGE archetype.
        
        This method adjusts the scores of possible actions to reflect the aggressive
        priorities of the CHARGE archetype:
        1. Attack actions receive a 30% score boost to prioritize combat
        2. Move actions that bring the unit closer to enemies receive a 50% score boost
        
        These adjustments ensure that CHARGE units will prefer attacking when possible
        and will move toward enemies when attacks aren't immediately available.
        
        The score modifications implement the core CHARGE behavior pattern:
        - Aggressive pursuit of combat opportunities
        - Proactive movement toward enemy units when attacks aren't available
        - Consistent pressure on enemy positions
        
        Args:
            unit_id: ID of the unit whose actions are being evaluated
            possible_actions: List of possible actions with initial scores
            ai_profile: AI profile containing behavior parameters for the unit
            
        Returns:
            Modified list of possible actions with updated scores reflecting CHARGE priorities
        """
        for action in possible_actions:
            if action['type'] == 'ATTACK':
                # Boost attack scores
                action['score'] *= 1.3  # 30% boost to attack scores
            elif action['type'] == 'MOVE':
                # Check if the move is towards an enemy
                if self._is_move_towards_enemy(unit_id, action.get('move_path', [])):
                    action['score'] *= 1.5  # 50% boost to moves towards enemies
        
        return possible_actions
    
    def select_best_action(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> Optional[AIAction]:
        """
        Select the best action based on the CHARGE archetype.
        
        This method implements the action selection logic for the CHARGE archetype:
        1. Prioritize attack actions over all others, selecting the highest-scoring attack
        2. If no attacks are available, prioritize moves toward enemies
        3. Fall back to the default selection logic if no specific actions are found
        
        This selection logic ensures that CHARGE units will always attack when possible,
        even if the attack score is lower than other action types, reflecting the
        aggressive nature of this archetype.
        
        The method implements a strict priority system:
        - First priority: Any attack action (sorted by score)
        - Second priority: Movement toward enemy units
        - Third priority: Default selection logic (highest scoring action)
        
        This priority system ensures that CHARGE units consistently behave aggressively,
        seeking combat whenever possible and advancing toward enemies when no immediate
        attacks are available.
        
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
                          a['is_current_pos'] or a['move_path'] is not None]
        
        if not valid_actions:
            return None
            
        # Prioritize attacks
        attack_actions = [a for a in valid_actions if a['type'] == 'ATTACK']
        if attack_actions:
            # Sort attack actions by score
            attack_actions.sort(key=lambda a: a['score'], reverse=True)
            best_attack = attack_actions[0]
            
            target_data = best_attack.get('target_info', {}).copy()
            if best_attack.get('move_path'):
                target_data['move_path'] = best_attack['move_path']
            return AIAction(best_attack['type'], unit_id, target_data)
        
        # If no attacks, prioritize moves towards enemies
        move_actions = [a for a in valid_actions if a['type'] == 'MOVE' and 
                        self._is_move_towards_enemy(unit_id, a.get('move_path', []))]
        if move_actions:
            # Sort move actions by score
            move_actions.sort(key=lambda a: a['score'], reverse=True)
            best_move = move_actions[0]
            
            target_data = best_move.get('target_info', {}).copy()
            if best_move.get('move_path'):
                target_data['move_path'] = best_move['move_path']
            return AIAction(best_move['type'], unit_id, target_data)
        
        # Fall back to default selection if no specific actions found
        return super().select_best_action(unit_id, valid_actions, ai_profile)
    
    def _is_move_towards_enemy(self, unit_id: str, move_path: List[Tuple[int, int]]) -> bool:
        """
        Check if a move is towards an enemy unit.
        
        This helper method determines whether a movement path brings the unit
        closer to the nearest enemy. It works by:
        1. Finding the nearest enemy to the unit's current position
        2. Calculating the distance from the current position to that enemy
        3. Calculating the distance from the destination to that enemy
        4. Returning true if the destination is closer to the enemy than the current position
        
        This method is used to identify and prioritize moves that advance toward enemies,
        which is a key behavior of the CHARGE archetype. It enables the AI to make
        progress toward engaging enemies even when no immediate attacks are available,
        maintaining offensive pressure throughout the battle.
        
        The method uses Manhattan distance (sum of horizontal and vertical distance)
        to determine proximity to enemies, which is appropriate for grid-based movement
        in tactical games.
        
        Args:
            unit_id: ID of the unit considering the move
            move_path: Path of coordinates (x, y) to move along
            
        Returns:
            True if the move brings the unit closer to an enemy, False otherwise
        """
        if not move_path:
            return False
            
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return False
            
        # Get the current position and the destination
        current_pos = unit.position
        destination = move_path[-1]
        
        # Find the nearest enemy from the current position
        nearest_enemy_pos = None
        nearest_enemy_distance = float('inf')
        
        for other_id, other_unit in self.gameStateManager.current_game_state.unit_states.items():
            if unit.faction != other_unit.faction:
                distance = self.mapSystem.calculate_manhattan_distance(current_pos, other_unit.position)
                if distance < nearest_enemy_distance:
                    nearest_enemy_distance = distance
                    nearest_enemy_pos = other_unit.position
        
        if not nearest_enemy_pos:
            return False
            
        # Calculate distances from current position and destination to the nearest enemy
        current_distance = self.mapSystem.calculate_manhattan_distance(current_pos, nearest_enemy_pos)
        destination_distance = self.mapSystem.calculate_manhattan_distance(destination, nearest_enemy_pos)
        
        # If the destination is closer to the enemy than the current position, it's moving towards the enemy
        return destination_distance < current_distance
    
    def _find_nearest_enemy(self, unit_id: str) -> Optional[str]:
        """
        Find the nearest enemy unit.
        
        This helper method identifies the enemy unit that is closest to the
        specified unit based on Manhattan distance. It's used to determine
        movement targets when no immediate attacks are available.
        
        The method iterates through all units in the game state, identifies those
        of different factions (enemies), calculates the Manhattan distance to each,
        and returns the ID of the closest enemy. This provides a simple but effective
        targeting mechanism for the CHARGE archetype when no specific high-value
        targets are identified.
        
        Args:
            unit_id: ID of the unit seeking an enemy
            
        Returns:
            ID of the nearest enemy unit, or None if no enemies are found
        """
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return None
            
        nearest_enemy_id = None
        nearest_enemy_distance = float('inf')
        
        for other_id, other_unit in self.gameStateManager.current_game_state.unit_states.items():
            if unit.faction != other_unit.faction:
                distance = self.mapSystem.calculate_manhattan_distance(unit.position, other_unit.position)
                if distance < nearest_enemy_distance:
                    nearest_enemy_distance = distance
                    nearest_enemy_id = other_id
        
        return nearest_enemy_id
    
    def _find_high_value_target(self, unit_id: str) -> Optional[str]:
        """
        Find a high-value target based on the target priority.
        
        This helper method identifies high-value enemy targets that should be
        prioritized by the CHARGE archetype. It works by:
        1. Identifying all enemy units
        2. Filtering for high-value targets (lords, healers, weakened units)
        3. Finding the closest high-value target
        4. Falling back to the nearest enemy if no high-value targets are found
        
        This method implements strategic targeting for the CHARGE archetype,
        focusing attacks on enemies that provide the greatest tactical advantage
        when defeated. By prioritizing lords, healers, and weakened units, the
        CHARGE archetype can maximize its impact on the battlefield.
        
        The method balances target value with proximity, ensuring that units
        don't ignore nearby threats to pursue distant high-value targets.
        
        Args:
            unit_id: ID of the unit seeking a target
            
        Returns:
            ID of the high-value target, or None if no suitable target is found
        """
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return None
            
        # Get all enemy units
        enemies = []
        for other_id, other_unit in self.gameStateManager.current_game_state.unit_states.items():
            if unit.faction != other_unit.faction:
                enemies.append(other_id)
        
        if not enemies:
            return None
            
        # Find high-value targets (lords, healers, etc.)
        high_value_targets = []
        for enemy_id in enemies:
            if self._is_high_value_target(enemy_id):
                high_value_targets.append(enemy_id)
        
        if high_value_targets:
            # Find the closest high-value target
            closest_target_id = None
            closest_target_distance = float('inf')
            
            for target_id in high_value_targets:
                target_unit = self.unitSystem.get_unit(target_id)
                if target_unit:
                    distance = self.mapSystem.calculate_manhattan_distance(unit.position, target_unit.position)
                    if distance < closest_target_distance:
                        closest_target_distance = distance
                        closest_target_id = target_id
            
            return closest_target_id
        
        # If no high-value targets, return the nearest enemy
        return self._find_nearest_enemy(unit_id)
    
    def _is_high_value_target(self, unit_id: str) -> bool:
        """
        Check if a unit is a high-value target.
        
        This helper method determines whether an enemy unit should be considered
        a high-priority target based on several factors:
        1. Lord status (main character units)
        2. Current HP (units with less than 30% HP are high value)
        3. Unit class (healers are high value targets)
        
        A unit is considered high-value if any of these conditions are met:
        - The unit is a lord (has the is_lord attribute set to True)
        - The unit has less than 30% of its maximum HP
        - The unit belongs to a healer class (Priest, Cleric, Bishop, etc.)
        
        High-value targets are prioritized in target selection for the CHARGE
        archetype, ensuring that important enemy units are targeted first.
        This strategic targeting helps maximize the impact of CHARGE units
        on the battlefield.
        
        Args:
            unit_id: ID of the unit to check
            
        Returns:
            True if the unit is a high-value target, False otherwise
        """
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return False
            
        # Lord units are high value
        if hasattr(unit, 'is_lord') and unit.is_lord:
            return True
            
        # Units with low HP are high value
        if unit.current_hp / unit.max_hp < 0.3:
            return True
            
        # Healers are high value targets
        if hasattr(unit, 'class_name') and unit.class_name in ["Priest", "Cleric", "Bishop", "Valkyrie", "Troubadour"]:
            return True
            
        return False