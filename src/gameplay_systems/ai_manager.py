"""
AI Manager Module

This module manages the AI behavior for enemy and NPC units. It determines the best actions
for AI-controlled units based on their AI profiles, current game state, and tactical situation.
"""

import logging
import random
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Set, Union

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum


class AIBehaviorType(Enum):
    """Types of AI behaviors."""
    AGGRESSIVE = auto()  # Prioritize attacking player units
    DEFENSIVE = auto()   # Prioritize staying in defensive positions
    CAUTIOUS = auto()    # Attack only when advantageous
    PASSIVE = auto()     # Don't move unless attacked
    STATIONARY = auto()  # Don't move at all
    HEALER = auto()      # Prioritize healing allies
    THIEF = auto()       # Prioritize stealing and opening chests/doors
    BOSS = auto()        # Special behavior for boss units
    FLEE = auto()        # Try to escape the map
    PROTECT = auto()     # Protect a specific unit or location
    PATROL = auto()      # Move between specific points


class AITargetPriority(Enum):
    """Target priority types for AI units."""
    WEAKEST = auto()     # Target the weakest player unit
    STRONGEST = auto()   # Target the strongest player unit
    CLOSEST = auto()     # Target the closest player unit
    LORD = auto()        # Target the lord (Leif)
    HEALER = auto()      # Target healers
    SPECIFIC = auto()    # Target a specific unit


class AIProfile:
    """Defines the behavior and priorities for an AI-controlled unit."""
    
    def __init__(self, behavior_type: AIBehaviorType, target_priority: AITargetPriority,
                 aggression: int = 50, movement_range: Optional[int] = None,
                 specific_target_id: Optional[str] = None, patrol_points: Optional[List[Tuple[int, int]]] = None,
                 protect_unit_id: Optional[str] = None, protect_location: Optional[Tuple[int, int]] = None):
        """
        Initialize an AIProfile.
        
        Args:
            behavior_type: Type of behavior
            target_priority: Target priority
            aggression: Aggression level (0-100)
            movement_range: Maximum movement range (None for unlimited)
            specific_target_id: ID of a specific target unit (for SPECIFIC priority)
            patrol_points: List of patrol points (for PATROL behavior)
            protect_unit_id: ID of unit to protect (for PROTECT behavior)
            protect_location: Location to protect (for PROTECT behavior)
        """
        self.behavior_type = behavior_type
        self.target_priority = target_priority
        self.aggression = aggression
        self.movement_range = movement_range
        self.specific_target_id = specific_target_id
        self.patrol_points = patrol_points or []
        self.protect_unit_id = protect_unit_id
        self.protect_location = protect_location
        
        # Runtime state
        self.current_patrol_index = 0


class AIAction:
    """Represents an action decision made by the AI."""
    
    def __init__(self, action_type: str, unit_id: str, target_data: Dict):
        """
        Initialize an AIAction.
        
        Args:
            action_type: Type of action
            unit_id: ID of the unit performing the action
            target_data: Data about the action target
        """
        self.action_type = action_type
        self.unit_id = unit_id
        self.target_data = target_data


class AIManager:
    """
    Manages the AI behavior for enemy and NPC units. Determines the best actions
    for AI-controlled units based on their AI profiles, current game state, and tactical situation.
    """
    
    def __init__(self):
        """Initialize the AIManager."""
        self.gameStateManager = None
        self.unitSystem = None
        self.mapSystem = None
        self.movementSystem = None
        self.combatSystem = None
        self.actionHandler = None
        self.dataProvider = None
        
        # State
        self.unit_ai_profiles = {}  # unit_id -> AIProfile
        self.last_attackers = {}    # unit_id -> attacker_unit_id
    
    def initialize(self, gameStateManager_instance, unitSystem_instance, mapSystem_instance,
                  movementSystem_instance, combatSystem_instance, actionHandler_instance,
                  dataProvider_instance):
        """
        Initialize the AIManager with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            unitSystem_instance: Instance of the UnitSystem
            mapSystem_instance: Instance of the MapSystem
            movementSystem_instance: Instance of the MovementSystem
            combatSystem_instance: Instance of the CombatSystem
            actionHandler_instance: Instance of the ActionHandler
            dataProvider_instance: Instance of the DataProvider
        """
        self.gameStateManager = gameStateManager_instance
        self.unitSystem = unitSystem_instance
        self.mapSystem = mapSystem_instance
        self.movementSystem = movementSystem_instance
        self.combatSystem = combatSystem_instance
        self.actionHandler = actionHandler_instance
        self.dataProvider = dataProvider_instance
        
        # Don't load profiles here, wait until chapter is initialized
        # self._load_ai_profiles()
        
        logging.info("AIManager initialized.")
    
    # --- AI Profile Management ---
    
    def _load_ai_profiles(self):
        """Load AI profiles for all units from the DataProvider."""
        for unit_id, unit in self.gameStateManager.current_game_state.unit_states.items():
            if unit.faction in [FactionEnum.ENEMY, FactionEnum.NPC]:
                # Get AI profile data from DataProvider
                ai_data = self.dataProvider.get_unit_ai_profile(unit_id)
                
                if ai_data:
                    # Create AIProfile from data
                    profile = AIProfile(
                        behavior_type=getattr(AIBehaviorType, ai_data.get('behavior_type', 'AGGRESSIVE')),
                        target_priority=getattr(AITargetPriority, ai_data.get('target_priority', 'CLOSEST')),
                        aggression=ai_data.get('aggression', 50),
                        movement_range=ai_data.get('movement_range'),
                        specific_target_id=ai_data.get('specific_target_id'),
                        patrol_points=ai_data.get('patrol_points'),
                        protect_unit_id=ai_data.get('protect_unit_id'),
                        protect_location=ai_data.get('protect_location')
                    )
                    
                    self.unit_ai_profiles[unit_id] = profile
                else:
                    # Default profile
                    self.unit_ai_profiles[unit_id] = AIProfile(
                        behavior_type=AIBehaviorType.AGGRESSIVE,
                        target_priority=AITargetPriority.CLOSEST,
                        aggression=50
                    )
    
    def change_unit_ai(self, unit_id: str, new_ai_profile: Dict):
        """
        Change the AI profile for a unit.
        
        Args:
            unit_id: ID of the unit
            new_ai_profile: New AI profile data
        """
        if unit_id not in self.unit_ai_profiles:
            return
        
        # Create new AIProfile from data
        profile = AIProfile(
            behavior_type=getattr(AIBehaviorType, new_ai_profile.get('behavior_type', 'AGGRESSIVE')),
            target_priority=getattr(AITargetPriority, new_ai_profile.get('target_priority', 'CLOSEST')),
            aggression=new_ai_profile.get('aggression', 50),
            movement_range=new_ai_profile.get('movement_range'),
            specific_target_id=new_ai_profile.get('specific_target_id'),
            patrol_points=new_ai_profile.get('patrol_points'),
            protect_unit_id=new_ai_profile.get('protect_unit_id'),
            protect_location=new_ai_profile.get('protect_location')
        )
        
        self.unit_ai_profiles[unit_id] = profile
        logging.info(f"Changed AI profile for unit {unit_id} to {profile.behavior_type.name}")
    
    # --- AI Decision Making ---
    
    def process_phase(self, phase):
        """
        Process the AI phase for a faction.
        
        Args:
            phase: The current phase (ENEMY or NPC)
            
        Returns:
            True if all units acted, False otherwise
        """
        logging.info(f"AI Manager processing phase: {phase}")
        ai_faction = FactionEnum.ENEMY if phase == PhaseEnum.ENEMY else FactionEnum.NPC
        
        # Get all active units for the faction in activation order
        active_ai_units = self.unitSystem.get_units_by_faction(ai_faction)
        
        for unit_id in active_ai_units:
            # Check if unit can act (not dead, slept, etc.)
            if self.unitSystem.can_act(unit_id) and not self.unitSystem.has_acted(unit_id):
                self.process_unit_turn(unit_id)
                # Small delay for visual pacing could be added here
        
        logging.info(f"AI Manager finished phase: {phase}")
        return True
    
    def process_unit_turn(self, unit_id: str):
        """
        Process the turn for a single AI unit.
        
        Args:
            unit_id: ID of the unit
        """
        unit = self.unitSystem.get_unit(unit_id)
        ai_profile = self.unit_ai_profiles.get(unit_id)
        
        if not unit or not ai_profile:
            logging.warning(f"Cannot process AI turn for unit {unit_id}: Unit or AI profile not found")
            return
        
        logging.info(f"Processing AI turn for: {unit.name} (AI: {ai_profile.behavior_type.name})")
        
        # Find possible actions for this unit
        possible_actions = self.find_possible_actions(unit_id, ai_profile)
        
        # Select the best action
        best_action = self.select_best_action(unit_id, possible_actions, ai_profile)
        
        if best_action:
            logging.info(f"AI {unit.name} chose action: {best_action.action_type} Target: {best_action.target_data}")
            
            # Execute Move first if needed
            if best_action.target_data.get('move_path'):
                move_outcome = self.actionHandler.perform_action(
                    unit_id,
                    'MOVE',
                    {'path': best_action.target_data.get('move_path')}
                )
                
                if not move_outcome.success:
                    logging.warning(f"AI move failed for {unit.name}")
                    # Fallback to Wait
                    self.actionHandler.perform_action(unit_id, 'WAIT', {})
                    return
            
            # Execute the main action
            action_outcome = self.actionHandler.perform_action(
                unit_id,
                best_action.action_type,
                {k: v for k, v in best_action.target_data.items() if k != 'move_path'}
            )
            
            if not action_outcome.success:
                logging.warning(f"AI action failed for {unit.name}: {action_outcome.message}")
                # If action failed after move, unit might just wait there
                if not self.unitSystem.has_acted(unit_id):  # Check if move already marked acted
                    self.actionHandler.perform_action(unit_id, 'WAIT', {})  # Explicit wait if action failed
        else:
            # No viable action found, just wait
            logging.info(f"AI {unit.name} found no action, waiting.")
            self.actionHandler.perform_action(unit_id, 'WAIT', {})
    
    def find_possible_actions(self, unit_id: str, ai_profile: AIProfile) -> List[Dict]:
        """
        Find all possible actions for an AI unit.
        
        Args:
            unit_id: ID of the unit
            ai_profile: AI profile for the unit
            
        Returns:
            List of potential actions with scores
        """
        actions = []
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return actions
            
        current_pos = unit.position
        
        # Get reachable tiles from the movement system
        movement_range = self.movementSystem.get_reachable_tiles(unit_id)
        
        # Consider actions from current position
        actions.extend(self.evaluate_actions_from_tile(
            unit_id, current_pos, ai_profile, is_current_pos=True
        ))
        
        # Consider actions after moving to each reachable tile
        for tile in movement_range:
            if tile != current_pos:
                tile_actions = self.evaluate_actions_from_tile(
                    unit_id, tile, ai_profile, is_current_pos=False
                )
                actions.extend(tile_actions)
        
        # Add Wait action as a fallback with lowest priority
        actions.append({
            'type': 'WAIT',
            'score': 0,
            'target_info': {},
            'move_path': None,
            'is_current_pos': True
        })
        
        return actions
    
    def evaluate_actions_from_tile(self, unit_id: str, tile: Tuple[int, int],
                                  ai_profile: AIProfile, is_current_pos: bool) -> List[Dict]:
        """
        Evaluate all possible actions from a specific tile.
        
        Args:
            unit_id: ID of the unit
            tile: Coordinate (x, y) to evaluate actions from
            ai_profile: AI profile for the unit
            is_current_pos: Whether this is the unit's current position
            
        Returns:
            List of potential actions with scores
        """
        evaluated_actions = []
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return evaluated_actions
            
        # Get units that could potentially be targeted from this tile
        potential_targets = self.unitSystem.get_units_in_range(unit_id, tile)
        
        # Get move path if not current position
        move_path = None if is_current_pos else self.movementSystem.find_path(unit_id, tile)
        
        # Evaluate Attack actions
        weapon = self.inventorySystem.get_equipped_weapon(unit_id)
        if weapon:
            weapon_data = self.dataProvider.get_item_data(weapon)
            if weapon_data:
                for target_unit_id in potential_targets:
                    target_unit = self.unitSystem.get_unit(target_unit_id)
                    if not target_unit:
                        continue
                        
                    # Check if target is an enemy
                    if self.unitSystem.is_enemy(unit.faction, target_unit.faction):
                        # Check if target is in weapon range
                        distance = self.mapSystem.calculate_distance(tile, target_unit.position)
                        if weapon_data.min_range <= distance <= weapon_data.max_range:
                            # Score the attack action
                            score = self.score_attack_action(unit_id, target_unit_id, tile, weapon, ai_profile)
                            
                            evaluated_actions.append({
                                'type': 'ATTACK',
                                'score': score,
                                'target_info': {'target_unit_id': target_unit_id},
                                'move_path': move_path,
                                'is_current_pos': is_current_pos
                            })
        
        # Evaluate Capture actions (if AI profile allows)
        if hasattr(ai_profile, 'can_capture') and ai_profile.can_capture:
            weapon = self.inventorySystem.get_equipped_weapon(unit_id)
            if weapon:
                weapon_data = self.dataProvider.get_item_data(weapon)
                if weapon_data:
                    for target_unit_id in potential_targets:
                        target_unit = self.unitSystem.get_unit(target_unit_id)
                        if not target_unit:
                            continue
                            
                        # Check if target is an enemy
                        if self.unitSystem.is_enemy(unit.faction, target_unit.faction):
                            # Check if target is in weapon range
                            distance = self.mapSystem.calculate_distance(tile, target_unit.position)
                            if weapon_data.min_range <= distance <= weapon_data.max_range:
                                # Check if capture is possible (Con, target immunity, etc.)
                                if self.unitSystem.can_capture(unit_id, target_unit_id):
                                    # Score the capture action
                                    score = self.score_capture_action(unit_id, target_unit_id, tile, ai_profile)
                                    
                                    evaluated_actions.append({
                                        'type': 'CAPTURE',
                                        'score': score,
                                        'target_info': {'target_unit_id': target_unit_id},
                                        'move_path': move_path,
                                        'is_current_pos': is_current_pos
                                    })
    
        # Evaluate Staff/Item actions
        usable_items = self.inventorySystem.get_usable_items(unit_id)
        for item_id in usable_items:
            item_data = self.dataProvider.get_item_data(item_id)
            if not item_data:
                continue
                
            if item_data.is_staff or item_data.is_usable_item:
                # Find potential targets for this item/staff
                item_targets = self.find_item_targets(unit_id, tile, item_id, item_data, potential_targets)
                
                for target_unit_id in item_targets:
                    # Score the item/staff action
                    score = self.score_item_action(unit_id, target_unit_id, tile, item_id, item_data, ai_profile)
                    
                    evaluated_actions.append({
                        'type': 'ITEM',
                        'score': score,
                        'target_info': {'item_id': item_id, 'target_unit_id': target_unit_id},
                        'move_path': move_path,
                        'is_current_pos': is_current_pos
                    })
        
        return evaluated_actions
        
    def find_item_targets(self, unit_id: str, from_tile: Tuple[int, int], item_id: str,
                         item_data, potential_targets: List[str]) -> List[str]:
        """
        Find potential targets for an item or staff.
        
        Args:
            unit_id: ID of the unit using the item
            from_tile: Coordinate to use the item from
            item_id: ID of the item
            item_data: Data for the item
            potential_targets: List of potential target unit IDs
            
        Returns:
            List of valid target unit IDs
        """
        targets = []
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return targets
            
        # Get item range
        item_range = (item_data.min_range, item_data.max_range)
        
        for target_unit_id in potential_targets:
            target_unit = self.unitSystem.get_unit(target_unit_id)
            if not target_unit:
                continue
                
            # Check if target is in range
            distance = self.mapSystem.calculate_distance(from_tile, target_unit.position)
            if item_data.min_range <= distance <= item_data.max_range:
                # Check if item targets allies or enemies
                is_ally = not self.unitSystem.is_enemy(unit.faction, target_unit.faction)
                
                # Healing items/staves target allies
                if item_data.heals_hp and is_ally and target_unit.current_hp < target_unit.max_hp:
                    targets.append(target_unit_id)
                    
                # Status staves target enemies
                elif item_data.inflicts_status and not is_ally and not self.unitSystem.has_status(target_unit_id, item_data.status_effect):
                    targets.append(target_unit_id)
                    
                # Add other item target conditions as needed
                
        return targets
    
    def select_best_action(self, unit_id: str, possible_actions: List[Dict], ai_profile: AIProfile) -> Optional[AIAction]:
        """
        Select the best action from a list of possible actions.
        
        Args:
            unit_id: ID of the unit
            possible_actions: List of possible actions with scores
            ai_profile: AI profile for the unit
            
        Returns:
            The best AIAction or None if no valid action is found
        """
        if not possible_actions:
            return None
            
        # Filter out invalid actions (e.g., path not found for move-actions)
        valid_actions = [a for a in possible_actions if a['type'] == 'WAIT' or
                         a['is_current_pos'] or a['move_path'] is not None]
        
        if not valid_actions:
            return None
            
        # Sort actions by score (descending)
        valid_actions.sort(key=lambda a: a['score'], reverse=True)
        
        # Apply AI profile specifics (e.g., Guard AI might prefer Wait if no threat)
        if ai_profile.behavior_type == AIBehaviorType.STATIONARY or ai_profile.behavior_type == AIBehaviorType.DEFENSIVE:
            # For stationary/defensive AI, only act if a good opportunity arises
            # or if threatened
            if not self._is_threatened(unit_id) and valid_actions[0]['score'] < 20:
                wait_action = next((a for a in valid_actions if a['type'] == 'WAIT'), None)
                if wait_action:
                    return AIAction('WAIT', unit_id, {})
        
        # Create AIAction from the highest scoring valid action
        best_action = valid_actions[0]
        target_data = best_action['target_info'].copy()
        
        # Add move path to target data if needed
        if best_action['move_path']:
            target_data['move_path'] = best_action['move_path']
            
        return AIAction(best_action['type'], unit_id, target_data)
    
    # --- Scoring Functions ---
    
    def score_attack_action(self, unit_id: str, target_id: str, from_tile: Tuple[int, int],
                           weapon: str, ai_profile: AIProfile) -> float:
        """
        Score an attack action.
        
        Args:
            unit_id: ID of the attacking unit
            target_id: ID of the target unit
            from_tile: Coordinate to attack from
            weapon: Weapon to use
            ai_profile: AI profile for the unit
            
        Returns:
            Score for the attack action
        """
        # Use CombatSystem to predict combat outcome
        prediction = self.combatSystem.simulate_combat(unit_id, target_id, is_capture=False)
        if not prediction:
            return 0.0
            
        score = 0.0
        
        # Extract relevant data from prediction
        attacker_dmg = prediction['attacker']['dmg']
        attacker_hit = prediction['attacker']['hit'] / 100.0  # Convert to probability
        attacker_crit = prediction['attacker']['crit'] / 100.0  # Convert to probability
        attacker_doubles = prediction['attacker']['doubles']
        
        defender_dmg = prediction['defender']['dmg']
        defender_hit = prediction['defender']['hit'] / 100.0  # Convert to probability
        defender_crit = prediction['defender']['crit'] / 100.0  # Convert to probability
        defender_doubles = prediction['defender']['doubles']
        
        # Get current HP values
        target_unit = self.unitSystem.get_unit(target_id)
        unit = self.unitSystem.get_unit(unit_id)
        if not target_unit or not unit:
            return 0.0
            
        target_hp = target_unit.current_hp
        unit_hp = unit.current_hp
        
        # Calculate expected damage
        expected_damage = attacker_dmg * attacker_hit
        if attacker_doubles:
            expected_damage += attacker_dmg * attacker_hit
            
        # Add critical hit bonus
        expected_damage += attacker_dmg * attacker_hit * attacker_crit
        
        # Calculate expected damage taken
        expected_damage_taken = defender_dmg * defender_hit
        if defender_doubles:
            expected_damage_taken += defender_dmg * defender_hit
            
        # Add critical hit bonus for defender
        expected_damage_taken += defender_dmg * defender_hit * defender_crit
        
        # Base score on expected damage
        score += expected_damage * 2
        
        # Bonus for potential kill
        if expected_damage >= target_hp:
            score += 50
            
            # Extra bonus for killing high-value targets
            if self._is_high_value_target(target_id):
                score += 25
                
        # Penalty for taking damage
        score -= expected_damage_taken
        
        # Severe penalty if we might die
        if expected_damage_taken >= unit_hp:
            score -= 75
            
        # Adjust based on AI profile
        if ai_profile.behavior_type == AIBehaviorType.AGGRESSIVE:
            score *= 1.2  # Aggressive AI values damage more
        elif ai_profile.behavior_type == AIBehaviorType.CAUTIOUS:
            # Cautious AI values survival more
            if expected_damage_taken > unit_hp / 3:
                score *= 0.5
                
        # Terrain considerations
        defender_terrain = self.mapSystem.get_terrain_at(target_unit.position)
        if defender_terrain and hasattr(defender_terrain, 'defense_bonus') and defender_terrain.defense_bonus > 20:
            # Penalty for attacking units on high-defense terrain
            score *= 0.8
            
        return score
        
    def score_capture_action(self, unit_id: str, target_id: str, from_tile: Tuple[int, int],
                            ai_profile: AIProfile) -> float:
        """
        Score a capture action.
        
        Args:
            unit_id: ID of the capturing unit
            target_id: ID of the target unit
            from_tile: Coordinate to capture from
            ai_profile: AI profile for the unit
            
        Returns:
            Score for the capture action
        """
        # Capture is high priority in Thracia AI if possible
        # Use CombatSystem to predict combat outcome with capture
        prediction = self.combatSystem.simulate_combat(unit_id, target_id, is_capture=True)
        if not prediction:
            return 0.0
            
        score = 0.0
        
        # Extract relevant data from prediction
        attacker_dmg = prediction['attacker']['dmg']
        attacker_hit = prediction['attacker']['hit'] / 100.0  # Convert to probability
        attacker_doubles = prediction['attacker']['doubles']
        
        defender_dmg = prediction['defender']['dmg']
        defender_hit = prediction['defender']['hit'] / 100.0  # Convert to probability
        defender_doubles = prediction['defender']['doubles']
        
        # Get current HP values
        target_unit = self.unitSystem.get_unit(target_id)
        unit = self.unitSystem.get_unit(unit_id)
        if not target_unit or not unit:
            return 0.0
            
        target_hp = target_unit.current_hp
        unit_hp = unit.current_hp
        
        # Calculate expected damage
        expected_damage = attacker_dmg * attacker_hit
        if attacker_doubles:
            expected_damage += attacker_dmg * attacker_hit
            
        # Calculate expected damage taken
        expected_damage_taken = defender_dmg * defender_hit
        if defender_doubles:
            expected_damage_taken += defender_dmg * defender_hit
        
        # Base score - capture is high priority in Thracia
        score = 80
        
        # Bonus if we can secure the capture this turn
        if expected_damage >= target_hp:
            score += 50
            
            # Bonus if target has valuable items
            target_items = self.inventorySystem.get_inventory(target_id)
            if target_items:
                # Simple heuristic: more items = more value
                score += len(target_items) * 5
                
                # Could be more sophisticated by checking item rarity/value
        
        # Penalty for damage taken during capture attempt (stats are halved)
        score -= expected_damage_taken * 1.5  # Higher penalty due to vulnerability during capture
        
        # Severe penalty if we might die
        if expected_damage_taken >= unit_hp:
            score -= 100
            
        return score
        
    def score_item_action(self, unit_id: str, target_id: str, from_tile: Tuple[int, int],
                         item_id: str, item_data, ai_profile: AIProfile) -> float:
        """
        Score an item/staff action.
        
        Args:
            unit_id: ID of the unit using the item
            target_id: ID of the target unit
            from_tile: Coordinate to use the item from
            item_id: ID of the item
            item_data: Data for the item
            ai_profile: AI profile for the unit
            
        Returns:
            Score for the item action
        """
        score = 0.0
        
        target_unit = self.unitSystem.get_unit(target_id)
        unit = self.unitSystem.get_unit(unit_id)
        if not target_unit or not unit:
            return 0.0
            
        # Healing items/staves
        if hasattr(item_data, 'heals_hp') and item_data.heals_hp:
            hp_missing = target_unit.max_hp - target_unit.current_hp
            hp_to_restore = min(hp_missing, item_data.heal_amount)
            
            # Base score on HP restored
            score += hp_to_restore * 2
            
            # Bonus for critically wounded allies
            if target_unit.current_hp / target_unit.max_hp < 0.3:
                score += 30
                
            # Bonus for healing high-value allies
            if self._is_high_value_ally(target_id):
                score += 20
                
        # Status staves
        elif hasattr(item_data, 'inflicts_status') and item_data.inflicts_status:
            # Base score for status effects
            score += 20
            
            # Bonus for high-threat targets
            if self._is_high_threat_target(target_id):
                score += 30
                
            # Adjust based on hit chance
            hit_chance = self._calculate_staff_hit_chance(unit_id, target_id, item_id)
            score *= (hit_chance / 100.0)
            
        # Other items (buffs, etc.)
        # Add scoring for other item types as needed
            
        return score
    
    # --- Additional Helper Methods ---
    
    def _is_threatened(self, unit_id: str) -> bool:
        """Check if a unit is threatened by enemy units."""
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return False
            
        # Simple implementation: check if any enemy unit can attack this unit
        for enemy_id, enemy in self.gameStateManager.current_game_state.unit_states.items():
            if self.unitSystem.is_enemy(unit.faction, enemy.faction):
                if self._can_attack_target(enemy_id, unit_id):
                    return True
                    
        return False
        
    def _is_high_value_target(self, unit_id: str) -> bool:
        """Check if a unit is a high-value target."""
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return False
            
        # Lord units are high value
        if hasattr(unit, 'is_lord') and unit.is_lord:
            return True
            
        # Units with low HP are high value
        if unit.current_hp / unit.max_hp < 0.3:
            return True
            
        # Units with powerful weapons or items could be high value
        # Add more conditions as needed
            
        return False
        
    def _is_high_value_ally(self, unit_id: str) -> bool:
        """Check if a unit is a high-value ally."""
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return False
            
        # Boss units are high value
        if hasattr(unit, 'is_boss') and unit.is_boss:
            return True
            
        # Units with leadership stars are high value
        if hasattr(unit, 'leadership_stars') and unit.leadership_stars > 0:
            return True
            
        return False
        
    def _is_high_threat_target(self, unit_id: str) -> bool:
        """Check if a unit is a high-threat target."""
        unit = self.unitSystem.get_unit(unit_id)
        if not unit:
            return False
            
        # Units with high attack power are high threat
        if hasattr(unit, 'attack') and unit.attack > 15:
            return True
            
        # Units that can attack multiple times are high threat
        if hasattr(unit, 'attack_speed') and unit.attack_speed > 15:
            return True
            
        return False
        
    def _calculate_staff_hit_chance(self, user_id: str, target_id: str, staff_id: str) -> int:
        """Calculate the hit chance for a staff."""
        # This would be more sophisticated in a real implementation
        # For now, return a default value
        return 70
    
    # --- Helper Methods ---
    
    def _execute_ai_action(self, action: AIAction):
        """
        Execute an AI action.
        
        Args:
            action: AIAction to execute
        """
        # Use the ActionHandler to execute the action
        if self.actionHandler:
            from src.core_engine.action_handler import ActionType
            
            # Convert action type string to ActionType enum
            action_type = getattr(ActionType, action.action_type)
            
            # Execute the action
            outcome = self.actionHandler.perform_action(action.unit_id, action_type, action.target_data)
            
            logging.info(f"AI executed {action.action_type} for unit {action.unit_id}: {outcome.success}")
    
    def _get_units_for_faction(self, faction: FactionEnum) -> List:
        """Get all units for a faction."""
        units = []
        
        for unit_id, unit in self.gameStateManager.current_game_state.unit_states.items():
            if unit.faction == faction:
                units.append(unit)
        
        return units
    
    def _sort_units_by_priority(self, units: List) -> List:
        """Sort units by priority (e.g., bosses first)."""
        # This would be more sophisticated in a real implementation
        return sorted(units, key=lambda unit: unit.id)
    
    def _find_targets(self, unit_id: str, priority: AITargetPriority, specific_target_id: Optional[str]) -> List:
        """Find potential targets based on priority."""
        # This would be more sophisticated in a real implementation
        targets = []
        
        for target_id, target in self.gameStateManager.current_game_state.unit_states.items():
            if target.faction == FactionEnum.PLAYER:
                targets.append(target)
        
        return targets
    
    def _sort_targets(self, targets: List, unit_id: str, priority: AITargetPriority) -> List:
        """Sort targets by priority."""
        # This would be more sophisticated in a real implementation
        return targets
    
    def _find_targets_in_range(self, unit_id: str) -> List:
        """Find potential targets within attack range."""
        # This would be more sophisticated in a real implementation
        return []
    
    def _can_attack_target(self, unit_id: str, target_id: str) -> bool:
        """Check if a unit can attack a target from current position."""
        # This would be more sophisticated in a real implementation
        return False
    
    def _find_path_to_attack(self, unit_id: str, target_id: str) -> List[Tuple[int, int]]:
        """Find a path to move within attack range of a target."""
        # This would be more sophisticated in a real implementation
        return []
    
    def _find_path_to_position(self, unit_id: str, position: Tuple[int, int], max_range: Optional[int]) -> List[Tuple[int, int]]:
        """Find a path to a position."""
        # This would be more sophisticated in a real implementation
        return []
    
    def _was_attacked_last_turn(self, unit_id: str) -> bool:
        """Check if a unit was attacked last turn."""
        return unit_id in self.last_attackers
    
    def _get_last_attacker(self, unit_id: str) -> Optional[str]:
        """Get the ID of the unit that last attacked this unit."""
        return self.last_attackers.get(unit_id)
    
    def _is_on_defensive_tile(self, unit_id: str) -> bool:
        """Check if a unit is on a defensive tile."""
        # This would be more sophisticated in a real implementation
        return False
    
    def _find_nearest_defensive_tile(self, unit_id: str) -> Optional[Tuple[int, int]]:
        """Find the nearest defensive tile."""
        # This would be more sophisticated in a real implementation
        return None
    
    def _evaluate_combat_advantage(self, unit_id: str, target_id: str) -> int:
        """Evaluate the advantage in combat against a target (0-100)."""
        # This would be more sophisticated in a real implementation
        return 50
    
    def _find_allies_needing_healing(self, unit_id: str) -> List:
        """Find allies that need healing."""
        # This would be more sophisticated in a real implementation
        return []
    
    def _can_heal_target(self, unit_id: str, target_id: str) -> bool:
        """Check if a unit can heal a target from current position."""
        # This would be more sophisticated in a real implementation
        return False
    
    def _find_healing_item(self, unit_id: str) -> Optional[str]:
        """Find a healing item in a unit's inventory."""
        # This would be more sophisticated in a real implementation
        return None
    
    def _find_nearest_chest(self, unit_id: str) -> Optional[Tuple[int, int]]:
        """Find the nearest chest."""
        # This would be more sophisticated in a real implementation
        return None
    
    def _is_adjacent_to_position(self, unit_id: str, position: Tuple[int, int]) -> bool:
        """Check if a unit is adjacent to a position."""
        # This would be more sophisticated in a real implementation
        return False
    
    def _find_key_item(self, unit_id: str, key_type: str) -> Optional[str]:
        """Find a key item in a unit's inventory."""
        # This would be more sophisticated in a real implementation
        return None
    
    def _find_nearest_door(self, unit_id: str) -> Optional[Tuple[int, int]]:
        """Find the nearest door."""
        # This would be more sophisticated in a real implementation
        return None
    
    def _find_steal_target(self, unit_id: str) -> Optional[Tuple[str, str]]:
        """Find a target to steal from (unit_id, item_id)."""
        # This would be more sophisticated in a real implementation
        return None
    
    def _is_adjacent_to_unit(self, unit_id: str, target_unit_id: str) -> bool:
        """Check if a unit is adjacent to another unit."""
        # This would be more sophisticated in a real implementation
        return False
    
    def _find_nearest_escape_point(self, unit_id: str) -> Optional[Tuple[int, int]]:
        """Find the nearest escape point."""
        # This would be more sophisticated in a real implementation
        return None
    
    def _find_safest_position(self, unit_id: str, enemies: List) -> Optional[Tuple[int, int]]:
        """Find the safest position to move to."""
        # This would be more sophisticated in a real implementation
        return None
    
    def _find_threats_to_position(self, position: Tuple[int, int]) -> List:
        """Find enemies threatening a position."""
        # This would be more sophisticated in a real implementation
        return []
    
    def _get_adjacent_positions(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get positions adjacent to a position."""
        x, y = position
        return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    
    def _is_position_occupied(self, position: Tuple[int, int]) -> bool:
        """Check if a position is occupied."""
        # This would be more sophisticated in a real implementation
        return False
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate the Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def record_attack(self, attacker_id: str, defender_id: str):
        """
        Record an attack for AI decision making.
        
        Args:
            attacker_id: ID of the attacking unit
            defender_id: ID of the defending unit
        """
        self.last_attackers[defender_id] = attacker_id
