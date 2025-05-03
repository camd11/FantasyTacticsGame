"""
Thief Loot Archetype Handler Module

This module implements the handler for the THIEF_LOOT AI archetype.
The THIEF_LOOT archetype represents specialized units that prioritize interacting
with map objects like chests and doors, stealing items from enemies, and generally
avoiding combat. This behavior is designed for thief units whose primary purpose
is to collect loot and open paths rather than engage in combat.

The ThiefLootArchetypeHandler implements a utility-focused behavior pattern that
prioritizes acquiring valuable items and opening paths over combat. It represents
the specialized behavior for thief units and other units with lockpicking abilities.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any

from src.gameplay_systems.ai.ai_types import AIProfile, AIBehaviorType, AIAction
from src.gameplay_systems.ai.ai_archetype_handler import AIArchetypeHandler


class ThiefLootArchetypeHandler(AIArchetypeHandler):
    """
    Handler for the THIEF_LOOT AI archetype.
    
    This archetype implements specialized behavior for thief units that focus on
    collecting loot and opening paths. It prioritizes:
    1. Opening chests to collect valuable items
    2. Opening doors to create new paths
    3. Stealing items from enemy units
    4. Moving towards these objectives (chests, doors, steal targets)
    5. Avoiding combat whenever possible
    
    The THIEF_LOOT archetype is suitable for thief units, lockpick users, and
    other specialized units whose primary purpose is not combat. It corresponds
    to the THIEF behavior type in legacy AI configurations and implements a
    utility-focused behavior pattern.
    """
    
    def can_handle(self, ai_profile: AIProfile) -> bool:
        """
        Check if this handler can handle the given AI profile.
        
        This method determines whether this handler is appropriate for the given
        AI profile by checking if its behavior type is either THIEF_LOOT or THIEF
        (the legacy equivalent).
        
        The ThiefLootArchetypeHandler handles two behavior types:
        - THIEF_LOOT: The modern archetype for utility-focused thief units
        - THIEF: The legacy equivalent for backward compatibility
        
        Args:
            ai_profile: The AI profile to check, containing the behavior type
            
        Returns:
            True if the profile has THIEF_LOOT or THIEF behavior type, False otherwise
        """
        return ai_profile.behavior_type in [AIBehaviorType.THIEF_LOOT, AIBehaviorType.THIEF]
    
    def modify_action_scores(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> List[Dict]:
        """
        Modify action scores based on the THIEF_LOOT archetype.
        
        This method adjusts the scores of possible actions to reflect the specialized
        priorities of the THIEF_LOOT archetype:
        1. INTERACT_MAP actions (chest/door interactions) receive a 100% score boost
        2. STEAL actions receive an 80% score boost
        3. MOVE actions toward thief targets receive a 50% score boost
        4. ATTACK actions receive a 70% score penalty to discourage combat
        
        These adjustments ensure that THIEF_LOOT units will prioritize their
        specialized actions over combat, reflecting their role as utility units.
        
        The score modifications implement the core THIEF_LOOT behavior pattern:
        - Highest priority for accessing and opening chests and doors
        - Strong preference for stealing valuable items from enemies
        - Proactive movement toward utility objectives
        - Strong avoidance of combat whenever possible
        
        Args:
            unit_id: ID of the unit whose actions are being evaluated
            possible_actions: List of possible actions with initial scores
            ai_profile: AI profile containing behavior parameters for the unit
            
        Returns:
            Modified list of possible actions with updated scores reflecting THIEF_LOOT priorities
        """
        for action in possible_actions:
            if action['type'] == 'INTERACT_MAP':
                # Boost chest/door interaction scores
                action['score'] *= 2.0  # Double the score for interacting with map objects
                print(f"DEBUG: _apply_archetype_score_modifiers - Boosted INTERACT_MAP score to {action['score']}")
            elif action['type'] == 'STEAL':
                # Boost steal action scores
                action['score'] *= 1.8  # 80% boost to steal actions
                print(f"DEBUG: _apply_archetype_score_modifiers - Boosted STEAL score to {action['score']}")
            elif action['type'] == 'MOVE' and 'context' in action and action['context'].get('target_type') in ['CHEST', 'DOOR', 'STEAL_TARGET']:
                # Boost moves towards thief targets
                action['score'] *= 1.5  # 50% boost to moves towards thief targets
                print(f"DEBUG: _apply_archetype_score_modifiers - Boosted MOVE towards {action['context'].get('target_type')} score to {action['score']}")
            elif action['type'] == 'ATTACK':
                # Penalize attack actions for thieves
                action['score'] *= 0.3  # 70% penalty to attack scores
                print(f"DEBUG: _apply_archetype_score_modifiers - Reduced ATTACK score to {action['score']}")
        
        return possible_actions
    
    def select_best_action(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> Optional[AIAction]:
        """
        Select the best action based on the THIEF_LOOT archetype.
        
        This method implements the action selection logic for the THIEF_LOOT archetype,
        using a strict priority system:
        1. First priority: Perform thief actions (INTERACT_MAP, STEAL) if available
        2. Second priority: Move towards thief targets (chests, doors, steal targets)
        3. Third priority: Safe actions (WAIT or MOVE without combat)
        4. Fall back to default selection if no specific actions are found
        
        This selection logic ensures that THIEF_LOOT units will always prioritize
        their specialized actions over other options, even if other actions might
        have higher scores after modification.
        
        The method implements a strict priority system that overrides normal score-based
        selection to ensure that thief units consistently fulfill their specialized role:
        - First priority: Direct utility actions (opening chests, stealing items)
        - Second priority: Movement toward utility objectives
        - Third priority: Safe actions that avoid combat
        - Fourth priority: Default selection logic (highest scoring action)
        
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
            
        # THIEF_LOOT: Prioritize chest/door interactions and stealing
        thief_actions = [a for a in valid_actions if a['type'] in ['INTERACT_MAP', 'STEAL']]
        move_to_thief_actions = [a for a in valid_actions if a['type'] == 'MOVE' and
                                'context' in a and a['context'].get('target_type') in ['CHEST', 'DOOR', 'STEAL_TARGET']]
        
        # Log for debugging
        print(f"DEBUG: select_best_action - Found {len(thief_actions)} thief actions and {len(move_to_thief_actions)} move-to-thief actions")
        
        # Priority 1: Perform Thief Actions if possible
        if thief_actions:
            # Sort thief actions by score
            thief_actions.sort(key=lambda a: a['score'], reverse=True)
            best_thief_action = thief_actions[0]
            
            print(f"DEBUG: select_best_action - Selected thief action: {best_thief_action['type']} with score {best_thief_action['score']}")
            
            target_data = best_thief_action.get('target_info', {}).copy()
            if best_thief_action.get('path'):
                target_data['path'] = best_thief_action['path']
            return AIAction(best_thief_action['type'], unit_id, target_data)
        
        # Priority 2: Move towards Thief Targets
        if move_to_thief_actions:
            # Sort move actions by score
            move_to_thief_actions.sort(key=lambda a: a['score'], reverse=True)
            best_move_action = move_to_thief_actions[0]
            
            print(f"DEBUG: select_best_action - Selected move-to-thief action with score {best_move_action['score']} towards {best_move_action['context'].get('target_type')}")
            
            target_data = best_move_action.get('target_info', {}).copy()
            if best_move_action.get('path'):
                target_data['path'] = best_move_action['path']
            return AIAction(best_move_action['type'], unit_id, target_data)
        
        # Priority 3: Default Behavior (No thief targets reachable/exist)
        # Avoid combat, move towards objective/escape, or wait safely
        safe_actions = [a for a in valid_actions if a['type'] == 'WAIT' or
                       (a['type'] == 'MOVE' and 'context' not in a)]
        
        if safe_actions:
            # Sort safe actions by score
            safe_actions.sort(key=lambda a: a['score'], reverse=True)
            best_safe_action = safe_actions[0]
            
            target_data = best_safe_action.get('target_info', {}).copy()
            if best_safe_action.get('path'):
                target_data['path'] = best_safe_action['path']
            return AIAction(best_safe_action['type'], unit_id, target_data)
        
        # Fall back to default selection if no specific actions found
        return super().select_best_action(unit_id, valid_actions, ai_profile)
    
    def find_specific_targets(self, unit_id: str, ai_profile: AIProfile) -> List[Dict]:
        """
        Find specific targets for the THIEF_LOOT archetype.
        
        This method identifies potential targets that are specifically relevant
        to the THIEF_LOOT archetype's behavior. It searches for:
        1. Chests on the map that can be opened
        2. Doors on the map that can be unlocked
        3. Enemy units with items that can be stolen
        
        Each target is returned with its position and relevant information,
        allowing the AI to plan movements and actions toward these objectives.
        
        This proactive target identification is a key component of the THIEF_LOOT
        behavior pattern, enabling thief units to identify and prioritize valuable
        objectives across the map rather than simply reacting to nearby opportunities.
        The method provides the strategic direction for thief units, guiding their
        movement and actions toward high-value targets.
        
        Args:
            unit_id: ID of the unit seeking targets
            ai_profile: AI profile containing behavior parameters for the unit
            
        Returns:
            List of target information dictionaries containing data about chests,
            doors, and steal targets
        """
        targets = []
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return targets
            
        # Find Chests
        try:
            chests = self.mapSystem.get_map_objects(type="Chest")
            for chest in chests:
                targets.append({
                    "coord": chest.position,
                    "type": "CHEST",
                    "object_id": chest.object_id
                })
        except Exception as e:
            logging.error(f"Error finding chests: {e}")
        
        # Find Locked Doors
        try:
            doors = self.mapSystem.get_map_objects(type="Door")
            for door in doors:
                targets.append({
                    "coord": door.position,
                    "type": "DOOR",
                    "object_id": door.object_id
                })
        except Exception as e:
            logging.error(f"Error finding doors: {e}")
        
        # Find Stealable Items on Enemies
        enemies = []
        for enemy_id, enemy_state in self.gameStateManager.current_game_state.unit_states.items():
            if enemy_state.faction != unit.faction:
                enemies.append(enemy_id)
                
        for enemy_id in enemies:
            enemy_unit = self.unitSystem.get_unit(enemy_id)
            if not enemy_unit:
                continue
                
            stealable_items = self.stealingSystem.get_stealable_items(unit, enemy_unit)
            if stealable_items:
                targets.append({
                    "coord": enemy_unit.position,
                    "type": "STEAL_TARGET",
                    "unit_id": enemy_id
                })
        
        return targets
    
    def find_map_interactables_from(self, unit_id: str, coord: Tuple[int, int]) -> List[Tuple[Tuple[int, int], str]]:
        """
        Checks adjacent tiles to 'coord' for chests or doors.
        
        This helper method identifies map objects that can be interacted with
        from a specific position. It checks the four adjacent tiles (up, right,
        down, left) for chests and doors that the unit could potentially open.
        
        This method is used to identify immediate interaction opportunities
        when evaluating potential positions for the THIEF_LOOT unit to move to.
        It provides tactical-level information about nearby interactable objects,
        complementing the strategic-level target identification provided by
        find_specific_targets().
        
        The method focuses on the four cardinal directions (up, right, down, left)
        to identify objects that can be directly interacted with from the specified
        position, enabling precise positioning for thief actions.
        
        Args:
            unit_id: ID of the unit checking for interactables
            coord: Coordinate (x, y) to check from
            
        Returns:
            List of tuples containing (coordinate, object type), where object type
            is either "CHEST" or "DOOR"
        """
        adjacent_interactables = []
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return adjacent_interactables
            
        # Get adjacent tiles
        adjacent_tiles = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            adjacent_tiles.append((coord[0] + dx, coord[1] + dy))
        
        # Check for chests
        try:
            chests = self.mapSystem.get_map_objects(type="Chest")
            for chest in chests:
                if chest.position in adjacent_tiles:
                    adjacent_interactables.append((chest.position, "CHEST"))
                    print(f"DEBUG: find_map_interactables_from - Found chest at {chest.position}")
        except Exception as e:
            logging.error(f"Error getting chests: {e}")
        
        # Check for doors
        try:
            doors = self.mapSystem.get_map_objects(type="Door")
            for door in doors:
                if door.position in adjacent_tiles:
                    adjacent_interactables.append((door.position, "DOOR"))
                    print(f"DEBUG: find_map_interactables_from - Found door at {door.position}")
        except Exception as e:
            logging.error(f"Error getting doors: {e}")
        
        return adjacent_interactables
    
    def find_steal_targets_from(self, unit_id: str, coord: Tuple[int, int]) -> List[Tuple[Any, Dict]]:
        """
        Checks adjacent tiles to 'coord' for enemies with stealable items.
        
        This helper method identifies enemy units that have items that can be
        stolen from a specific position. It checks the four adjacent tiles
        (up, right, down, left) for enemy units, and then determines if they
        have items that can be stolen based on the game's stealing rules.
        
        This method is used to identify immediate stealing opportunities
        when evaluating potential positions for the THIEF_LOOT unit to move to.
        It provides tactical-level information about nearby stealing opportunities,
        complementing the strategic-level target identification provided by
        find_specific_targets().
        
        The method not only identifies enemy units in adjacent positions but also
        checks if the thief can actually steal from them based on game rules like
        item weight, thief speed, and other factors that affect stealing success.
        
        Args:
            unit_id: ID of the thief unit checking for steal targets
            coord: Coordinate (x, y) to check from
            
        Returns:
            List of tuples containing (enemy unit, stealable item), where each
            tuple represents a potential stealing opportunity
        """
        adjacent_stealables = []
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return adjacent_stealables
            
        # Get adjacent tiles
        adjacent_tiles = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            adjacent_tiles.append((coord[0] + dx, coord[1] + dy))
        
        # Check for enemy units
        try:
            # First try to get units from the game state
            for enemy_id, enemy_unit in self.gameStateManager.current_game_state.unit_states.items():
                if enemy_unit.faction != unit.faction and enemy_unit.position in adjacent_tiles:
                    # Check for stealable items
                    stealable_items = self.stealingSystem.get_stealable_items(unit, enemy_unit)
                    for item in stealable_items:
                        # Check if the thief can steal this item (based on weight, speed, etc.)
                        if self.stealingSystem.can_steal(unit, enemy_unit, item):
                            adjacent_stealables.append((enemy_unit, item))
                            print(f"DEBUG: find_steal_targets_from - Found stealable item {item['id']} from {enemy_unit.id}")
        except Exception as e:
            logging.error(f"Error finding steal targets: {e}")
        
        return adjacent_stealables
    
    def calculate_interact_map_utility(self, unit_id: str, target_coord: Tuple[int, int],
                                      interact_type: str, profile: AIProfile) -> float:
        """
        Calculate the utility of interacting with a map object (chest/door).
        
        This method determines the value of interacting with a specific map object
        based on its type and strategic importance:
        1. Chests are assigned a very high base utility (200.0) as they contain valuable items
        2. Doors are evaluated based on whether they block access to objectives:
           - Doors blocking access to chests receive high utility (150.0)
           - Other doors receive moderate utility (50.0)
        
        This utility calculation helps the THIEF_LOOT archetype prioritize the most
        strategically valuable interactions.
        
        The method implements a strategic evaluation system that considers not just
        the immediate value of the interaction but also its impact on future objectives:
        - Chests are highly valued for their direct rewards (items, gold)
        - Doors are valued based on whether they enable access to other objectives
        - The calculation includes a simplified pathfinding check to determine if
          a door is blocking access to important locations
        
        Args:
            unit_id: ID of the unit considering the interaction
            target_coord: Coordinate (x, y) of the map object to interact with
            interact_type: Type of interaction ("CHEST" or "DOOR")
            profile: AI profile containing behavior parameters for the unit
            
        Returns:
            Numerical utility score for the interaction, where higher values
            indicate more desirable interactions
        """
        base_utility = 0.0
        
        if interact_type == "CHEST":
            # Chests are high priority
            base_utility = 200.0
        elif interact_type == "DOOR":
            # Check if door is blocking path to objective/chest
            is_blocking = False
            
            # Check if there are chests or objectives behind the door
            # This is a simplified check - in a real implementation, you would use pathfinding
            # to determine if the door blocks access to important locations
            try:
                chests = self.mapSystem.get_map_objects(type="Chest")
                unit = self.unitSystem.get_unit(unit_id)
            except Exception as e:
                logging.error(f"Error getting chests for utility calculation: {e}")
                chests = []
            if unit:
                for chest in chests:
                    # Check if chest is on the other side of the door
                    # This is a very simplified check
                    if (chest.position[0] > target_coord[0] and unit.position[0] < target_coord[0]) or \
                       (chest.position[0] < target_coord[0] and unit.position[0] > target_coord[0]) or \
                       (chest.position[1] > target_coord[1] and unit.position[1] < target_coord[1]) or \
                       (chest.position[1] < target_coord[1] and unit.position[1] > target_coord[1]):
                        is_blocking = True
                        break
            
            if is_blocking:
                base_utility = 150.0  # High value if blocking progress
            else:
                base_utility = 50.0  # Lower value otherwise
        
        return base_utility
    
    def calculate_steal_utility(self, unit_id: str, target_id: str, item_id: str, profile: AIProfile) -> float:
        """
        Calculate the utility of stealing an item.
        
        This method determines the value of stealing a specific item from an enemy unit,
        taking into account multiple factors:
        1. Base utility for stealing (100.0)
        2. Item value bonus (scaled based on the item's gold value)
        3. Success chance bonus (based on speed difference between thief and target)
        4. Risk penalty (potential damage from counter-attacks if stealing fails)
        5. Inventory space check (cannot steal if inventory is full)
        
        The method implements a comprehensive evaluation system that balances
        reward against risk:
        - Higher value items receive greater bonuses
        - Success probability significantly impacts utility
        - Potential counter-attack damage is factored in as a risk penalty
        - Hard constraints (inventory space, speed requirements) can make
          stealing impossible regardless of other factors
        
        The method returns a negative value (-1.0) if the steal action is impossible
        (due to inventory constraints or insufficient speed), ensuring these actions
        will not be selected.
        
        Args:
            unit_id: ID of the thief unit attempting to steal
            target_id: ID of the target unit to steal from
            item_id: ID of the item to be stolen
            profile: AI profile containing behavior parameters for the unit
            
        Returns:
            Numerical utility score for the steal action, where higher values
            indicate more desirable actions, or -1.0 if stealing is impossible
        """
        unit = self.unitSystem.get_unit(unit_id)
        target_unit = self.unitSystem.get_unit(target_id)
        if not unit or not target_unit:
            return 0.0
            
        # Get item data
        item_data = self.dataProvider.get_item_data(item_id)
        if not item_data:
            return 0.0
            
        # Base utility for stealing
        base_utility = 100.0
        
        # Bonus based on item value
        item_value = getattr(item_data, 'value', 0)
        if not isinstance(item_value, (int, float)):
            # Try to get value from a method if it exists
            item_value = self.dataProvider.get_item_value(item_id)
            
        # Ensure item_value is a number
        if not isinstance(item_value, (int, float)):
            item_value = 0
            
        item_value_bonus = item_value / 50.0  # Scale value to a reasonable bonus
        
        # Factor in success chance (based on Speed difference)
        success_chance = 1.0  # Default to 100% if we can't calculate
        
        # Get attack speeds if available
        thief_speed = getattr(unit.calculated_stats, 'attack_speed', None) if hasattr(unit, 'calculated_stats') else None
        target_speed = getattr(target_unit.calculated_stats, 'attack_speed', None) if hasattr(target_unit, 'calculated_stats') else None
        
        # If calculated_stats is not available, try regular stats
        if thief_speed is None:
            thief_speed = getattr(unit.stats, 'speed', 0) if hasattr(unit, 'stats') else 0
        if target_speed is None:
            target_speed = getattr(target_unit.stats, 'speed', 0) if hasattr(target_unit, 'stats') else 0
            
        # Ensure speeds are numbers
        if not isinstance(thief_speed, (int, float)):
            thief_speed = 0
        if not isinstance(target_speed, (int, float)):
            target_speed = 0
            
        # Calculate success chance based on speed difference
        if thief_speed > target_speed:
            success_chance = 1.0
        else:
            success_chance = 0.0  # Can't steal if not faster
            
        chance_bonus = success_chance * 100.0  # Max 100 bonus at 100% chance
        
        # Penalty based on risk (target retaliation)
        # Predict counter-attack if steal fails
        risk_penalty = 0.0
        
        # Check if target can counter-attack
        if self.combatSystem:
            prediction = self.combatSystem.simulate_combat(target_id, unit_id, is_capture=False)
            if prediction:
                defender_dmg = prediction['attacker']['dmg']  # Target would be attacker in counter
                defender_hit = prediction['attacker']['hit'] / 100.0
                expected_damage = defender_dmg * defender_hit
                risk_penalty = expected_damage * 1.5
        
        # Check inventory space
        has_space = True
        if self.inventorySystem:
            inventory = self.inventorySystem.get_inventory(unit_id)
            if inventory and len(inventory) >= 7:  # Assuming max inventory size is 7
                has_space = False
        
        # Calculate total utility
        total_utility = base_utility + item_value_bonus + chance_bonus - risk_penalty
        
        # Return -1 if can't steal due to inventory or success chance
        if not has_space or success_chance <= 0:
            return -1.0
            
        return total_utility