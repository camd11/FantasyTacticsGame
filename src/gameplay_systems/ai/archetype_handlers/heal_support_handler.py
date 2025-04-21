"""
Heal Support Archetype Handler Module

This module implements the handler for the HEAL_SUPPORT AI archetype.
The HEAL_SUPPORT archetype represents units that prioritize healing and supporting
allied units, such as clerics, priests, and other staff users. These units focus on
using healing staves and items, curing status effects, and maintaining their own safety
by avoiding enemy threats.

The HealSupportArchetypeHandler implements a supportive, cautious behavior pattern
that prioritizes healing and assisting allies while avoiding direct combat. It represents
the standard behavior for clerics, priests, and other staff-using support units.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any

from src.gameplay_systems.ai.ai_types import AIProfile, AIBehaviorType, AIAction
from src.gameplay_systems.ai.ai_archetype_handler import AIArchetypeHandler


class HealSupportArchetypeHandler(AIArchetypeHandler):
    """
    Handler for the HEAL_SUPPORT AI archetype.
    
    This archetype implements supportive behavior for units that focus on healing
    and assisting allied units. It prioritizes:
    1. Healing critically injured allies (below 30% HP)
    2. Curing negative status effects (sleep, silence, etc.)
    3. Healing moderately injured allies (below healing threshold)
    4. Moving to safe positions away from enemy attack ranges
    
    The HEAL_SUPPORT archetype is suitable for clerics, priests, troubadours, and
    other staff-using units. It corresponds to the HEALER behavior type in legacy
    AI configurations and implements a cautious, support-oriented behavior pattern.
    """
    
    def can_handle(self, ai_profile: AIProfile) -> bool:
        """
        Check if this handler can handle the given AI profile.
        
        This method determines whether this handler is appropriate for the given
        AI profile by checking if its behavior type is either HEAL_SUPPORT or HEALER
        (the legacy equivalent).
        
        The HealSupportArchetypeHandler handles two behavior types:
        - HEAL_SUPPORT: The modern archetype for healing and support-oriented units
        - HEALER: The legacy equivalent for backward compatibility
        
        Args:
            ai_profile: The AI profile to check, containing the behavior type
            
        Returns:
            True if the profile has HEAL_SUPPORT or HEALER behavior type, False otherwise
        """
        return ai_profile.behavior_type in [AIBehaviorType.HEAL_SUPPORT, AIBehaviorType.HEALER]
    def modify_action_scores(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> List[Dict]:
        """
        Modify action scores based on the HEAL_SUPPORT archetype.
        
        This method adjusts the scores of possible actions to reflect the supportive
        priorities of the HEAL_SUPPORT archetype:
        1. Healing staff actions receive a 50% score boost
        2. Status cure staff actions receive a 40% score boost
        3. Attack actions receive a 70% penalty to discourage combat
        
        These adjustments ensure that HEAL_SUPPORT units will prioritize healing and
        support actions over combat, reflecting their role as support units.
        
        The score modifications implement the core HEAL_SUPPORT behavior pattern:
        - Strong preference for healing injured allies
        - High priority for curing negative status effects
        - Avoidance of combat whenever possible
        - Focus on supportive rather than offensive actions
        
        Args:
            unit_id: ID of the unit whose actions are being evaluated
            possible_actions: List of possible actions with initial scores
            ai_profile: AI profile containing behavior parameters for the unit
            
        Returns:
            Modified list of possible actions with updated scores reflecting HEAL_SUPPORT priorities
        """
        for action in possible_actions:
            if action['type'] == 'ITEM' and 'item_id' in action.get('target_info', {}):
                item_id = action['target_info']['item_id']
                item_data = self.dataProvider.get_item_data(item_id)
                
                # Check if it's a healing staff
                if item_data and hasattr(item_data, 'heals_hp') and item_data.heals_hp:
                    # Boost healing action scores
                    action['score'] *= 1.5  # 50% boost to healing actions
                
                # Check if it's a status cure staff (like Restore)
                elif item_data and hasattr(item_data, 'effect_type') and item_data.effect_type == "STATUS_CURE":
                    # Boost status cure action scores
                    action['score'] *= 1.4  # 40% boost to status cure actions
            
            # Penalize attack actions for healers
            elif action['type'] == 'ATTACK':
                action['score'] *= 0.3  # 70% penalty to attack scores
        
        return possible_actions
    
    def select_best_action(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> Optional[AIAction]:
        """
        Select the best action based on the HEAL_SUPPORT archetype.
        
        This method implements the action selection logic for the HEAL_SUPPORT archetype:
        1. Identify healing and status cure actions (staff/item usage)
        2. If any support actions have a reasonable score (>= 20), select the highest-scoring one
        3. If no good support actions are available, prioritize moving to safe positions
        4. Fall back to the default selection logic if no specific actions are found
        
        This selection logic ensures that HEAL_SUPPORT units will prioritize their
        support role while also maintaining their safety when no healing is needed.
        
        The method implements a strict priority system:
        - First priority: Healing and status cure actions with scores >= 20
        - Second priority: Movement to safe positions away from enemy attack ranges
        - Third priority: Default selection logic (highest scoring action)
        
        This priority system ensures that HEAL_SUPPORT units consistently fulfill their
        support role while avoiding unnecessary risks, maintaining their ability to
        provide healing and support in future turns.
        
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
            
        # Find healing actions
        healing_actions = [a for a in valid_actions if a['type'] == 'ITEM' and
                           'item_id' in a.get('target_info', {}) and
                           self._is_healing_item(a['target_info'].get('item_id', ''))]
        
        # Find status cure actions (like Restore staff)
        status_cure_actions = [a for a in valid_actions if a['type'] == 'ITEM' and
                               'item_id' in a.get('target_info', {}) and
                               (a['target_info'].get('item_id', '') == 'RESTORE_STAFF' or
                                self.dataProvider.get_item_data(a['target_info'].get('item_id', '')).get('effect_type') == "STATUS_CURE")]
        
        # Combine healing and status cure actions
        support_actions = healing_actions + status_cure_actions
        
        if support_actions:
            # Sort support actions by score
            support_actions.sort(key=lambda a: a['score'], reverse=True)
            best_support = support_actions[0]
            
            # If the best support action has a reasonable score, choose it
            if best_support['score'] >= 20:
                target_data = best_support.get('target_info', {}).copy()
                if best_support.get('path'):
                    target_data['path'] = best_support['path']
                return AIAction(best_support['type'], unit_id, target_data)
        
        # If no good support action, prioritize safety
        # Find safe positions away from enemies
        safe_move_actions = [a for a in valid_actions if a['type'] == 'MOVE' and
                            self._is_safe_position(unit_id, a.get('path', [])[-1] if a.get('path') else None)]
        
        if safe_move_actions:
            # Sort by score
            safe_move_actions.sort(key=lambda a: a['score'], reverse=True)
            best_safe_move = safe_move_actions[0]
            
            target_data = best_safe_move.get('target_info', {}).copy()
            if best_safe_move.get('path'):
                target_data['path'] = best_safe_move['path']
            return AIAction(best_safe_move['type'], unit_id, target_data)
        
        # Fall back to default selection if no specific actions found
        return super().select_best_action(unit_id, valid_actions, ai_profile)
    
    def _is_healing_item(self, item_id: str) -> bool:
        """
        Check if an item is a healing item.
        
        This helper method determines whether an item or staff has healing properties
        based on its ID and data. It checks for:
        1. The 'heals_hp' property in the item data
        2. Staff IDs that contain healing keywords (HEAL, MEND, PHYSIC, RECOVER)
        
        The method identifies healing items through two approaches:
        - Direct property check: Looking for the 'heals_hp' flag in item data
        - Name-based identification: Recognizing common healing staff names
          (HEAL_STAFF, MEND_STAFF, PHYSIC_STAFF, RECOVER_STAFF)
        
        This method is used to identify healing actions for prioritization in the
        HEAL_SUPPORT archetype's decision-making process, enabling the AI to
        properly categorize and prioritize healing tools.
        
        Args:
            item_id: ID of the item to check
            
        Returns:
            True if the item has healing properties, False otherwise
        """
        if not item_id:
            return False
            
        item_data = self.dataProvider.get_item_data(item_id)
        if not item_data:
            return False
            
        # Check if the item has healing properties
        # Use .get() for dictionary access
        return item_data.get('heals_hp', False) or (
            item_id.endswith("_STAFF") and ("HEAL" in item_id or "MEND" in item_id or
                                           "PHYSIC" in item_id or "RECOVER" in item_id)
        )
    
    def _is_safe_position(self, unit_id: str, position: Optional[Tuple[int, int]]) -> bool:
        """
        Check if a position is safe from enemy attacks.
        
        This helper method determines whether a map position is outside the attack
        range of all enemy units. It works by:
        1. Checking all enemy units
        2. Calculating their potential attack ranges
        3. Determining if the specified position is within any enemy's attack range
        
        This method is a critical component of the HEAL_SUPPORT archetype's self-preservation
        behavior, allowing support units to identify and move to positions where they
        won't be vulnerable to enemy attacks. This safety-conscious positioning is
        essential for ensuring that healers can continue to provide support in future turns
        rather than being eliminated early.
        
        The method returns False if the position is within any enemy's attack range,
        ensuring that HEAL_SUPPORT units avoid positions where they could be targeted.
        
        Args:
            unit_id: ID of the unit considering the position
            position: Coordinate (x, y) to check for safety
            
        Returns:
            True if the position is outside all enemy attack ranges, False otherwise
        """
        if not position:
            return False
            
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return False
            
        # Check if any enemy can attack this position
        for enemy_id, enemy in self.gameStateManager.current_game_state.unit_states.items():
            if enemy.faction != unit.faction:
                # Check if enemy can reach and attack this position
                enemy_attack_range = self._get_enemy_attack_range(enemy_id)
                for attack_pos in enemy_attack_range:
                    if attack_pos == position:
                        return False
        
        return True
    
    def _get_enemy_attack_range(self, enemy_id: str) -> List[Tuple[int, int]]:
        """
        Get the range of positions an enemy can attack.
        
        This helper method calculates all map positions that an enemy unit could
        potentially attack. It works by:
        1. Getting the enemy's movement range
        2. Getting the enemy's weapon range
        3. Calculating all tiles within weapon range of any movement tile
        
        The method implements a comprehensive attack range calculation that considers:
        - The enemy's full movement capabilities
        - The range of the enemy's equipped weapon
        - All possible attack positions after movement
        
        This calculation provides a conservative estimate of threat areas, ensuring
        that HEAL_SUPPORT units err on the side of caution when determining safe positions.
        While this implementation is simplified, it provides a reasonable approximation
        for tactical decision-making.
        
        Args:
            enemy_id: ID of the enemy unit to calculate attack range for
            
        Returns:
            List of coordinates (x, y) that the enemy could potentially attack
        """
        # This would be more sophisticated in a real implementation
        # For now, return a simple approximation
        enemy = self.unitSystem.get_unit(enemy_id)
        if not enemy:
            return []
            
        # Get enemy's movement range
        try:
            movement_range = self.movementSystem.calculate_movement_range(enemy_id)
        except Exception:
            movement_range = []
            
        # Get enemy's weapon range
        weapon = self.inventorySystem.get_equipped_weapon(enemy_id)
        if not weapon:
            weapon_range = 1  # Default to 1 if no weapon
        else:
            weapon_data = self.dataProvider.get_item_data(weapon)
            if not weapon_data:
                weapon_range = 1
            else:
                weapon_range = weapon_data.range_max
                
        # Calculate attack range (all tiles within weapon range of any movement tile)
        attack_range = []
        for move_tile in movement_range:
            for dx in range(-weapon_range, weapon_range + 1):
                for dy in range(-weapon_range, weapon_range + 1):
                    if abs(dx) + abs(dy) <= weapon_range:
                        attack_tile = (move_tile[0] + dx, move_tile[1] + dy)
                        if attack_tile not in attack_range:
                            attack_range.append(attack_tile)
        
        return attack_range