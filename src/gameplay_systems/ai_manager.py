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
    
    def process_ai_turn(self, faction: FactionEnum):
        """
        Process the AI turn for a faction.
        
        Args:
            faction: Faction to process
            
        Returns:
            True if all units acted, False otherwise
        """
        # Get all units for the faction
        units = self._get_units_for_faction(faction)
        
        # Sort units by priority (e.g., bosses first, then normal units)
        units = self._sort_units_by_priority(units)
        
        # Process each unit
        for unit in units:
            if not unit.has_acted:
                # Determine the best action for the unit
                action = self.determine_best_action(unit.id)
                
                if action:
                    # Execute the action
                    self._execute_ai_action(action)
        
        return True
    
    def determine_best_action(self, unit_id: str) -> Optional[AIAction]:
        """
        Determine the best action for an AI unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            AIAction or None if no action is possible
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return None
        
        profile = self.unit_ai_profiles.get(unit_id)
        if not profile:
            return None
        
        # Get possible actions based on behavior type
        if profile.behavior_type == AIBehaviorType.AGGRESSIVE:
            return self._determine_aggressive_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.DEFENSIVE:
            return self._determine_defensive_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.CAUTIOUS:
            return self._determine_cautious_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.PASSIVE:
            return self._determine_passive_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.STATIONARY:
            return self._determine_stationary_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.HEALER:
            return self._determine_healer_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.THIEF:
            return self._determine_thief_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.BOSS:
            return self._determine_boss_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.FLEE:
            return self._determine_flee_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.PROTECT:
            return self._determine_protect_action(unit_id, profile)
        elif profile.behavior_type == AIBehaviorType.PATROL:
            return self._determine_patrol_action(unit_id, profile)
        else:
            # Default to aggressive
            return self._determine_aggressive_action(unit_id, profile)
    
    # --- Behavior-Specific Action Determination ---
    
    def _determine_aggressive_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """
        Determine the best action for an aggressive unit.
        
        Args:
            unit_id: ID of the unit
            profile: AI profile
            
        Returns:
            AIAction or None if no action is possible
        """
        # Find potential targets based on priority
        targets = self._find_targets(unit_id, profile.target_priority, profile.specific_target_id)
        
        if not targets:
            # No targets, just wait
            return AIAction("WAIT", unit_id, {})
        
        # Sort targets by priority
        targets = self._sort_targets(targets, unit_id, profile.target_priority)
        
        # Try to attack a target
        for target in targets:
            # Check if we can attack the target from current position
            if self._can_attack_target(unit_id, target.id):
                return AIAction("ATTACK", unit_id, {"target_unit_id": target.id})
            
            # If not, try to move within attack range
            path = self._find_path_to_attack(unit_id, target.id)
            if path:
                # Move to attack position
                return AIAction("MOVE", unit_id, {"path": path})
        
        # If we can't attack any target, move towards the highest priority target
        if targets:
            path = self._find_path_to_position(unit_id, targets[0].position, profile.movement_range)
            if path:
                return AIAction("MOVE", unit_id, {"path": path})
        
        # If all else fails, wait
        return AIAction("WAIT", unit_id, {})
    
    def _determine_defensive_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified defensive action determination."""
        # Find potential targets within attack range
        targets = self._find_targets_in_range(unit_id)
        
        if targets:
            # Attack the highest priority target
            return AIAction("ATTACK", unit_id, {"target_unit_id": targets[0].id})
        
        # If no targets in range, just wait
        return AIAction("WAIT", unit_id, {})
    
    def _determine_cautious_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified cautious action determination."""
        # Similar to aggressive but only attack if advantage is good
        return self._determine_aggressive_action(unit_id, profile)
    
    def _determine_passive_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified passive action determination."""
        # Only attack if we were attacked last turn
        if self._was_attacked_last_turn(unit_id):
            attacker_id = self._get_last_attacker(unit_id)
            if attacker_id and self._can_attack_target(unit_id, attacker_id):
                return AIAction("ATTACK", unit_id, {"target_unit_id": attacker_id})
        
        # If not attacked or can't attack back, just wait
        return AIAction("WAIT", unit_id, {})
    
    def _determine_stationary_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified stationary action determination."""
        # Find potential targets within attack range
        targets = self._find_targets_in_range(unit_id)
        
        if targets:
            # Attack the highest priority target
            return AIAction("ATTACK", unit_id, {"target_unit_id": targets[0].id})
        
        # If no targets in range, just wait
        return AIAction("WAIT", unit_id, {})
    
    def _determine_healer_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified healer action determination."""
        # Find allies that need healing
        allies_needing_healing = self._find_allies_needing_healing(unit_id)
        
        if allies_needing_healing:
            # Check if we can heal any ally from current position
            for ally in allies_needing_healing:
                if self._can_heal_target(unit_id, ally.id):
                    # Find the appropriate healing item or staff
                    healing_item = self._find_healing_item(unit_id)
                    if healing_item:
                        return AIAction("ITEM", unit_id, {"item_id": healing_item, "target_unit_id": ally.id})
        
        # If no healing to do, just wait
        return AIAction("WAIT", unit_id, {})
    
    def _determine_thief_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified thief action determination."""
        # Default to aggressive behavior
        return self._determine_aggressive_action(unit_id, profile)
    
    def _determine_boss_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified boss action determination."""
        # Find potential targets within attack range
        targets = self._find_targets_in_range(unit_id)
        
        if targets:
            # Attack the highest priority target
            return AIAction("ATTACK", unit_id, {"target_unit_id": targets[0].id})
        
        # If no targets in range, just wait
        return AIAction("WAIT", unit_id, {})
    
    def _determine_flee_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified flee action determination."""
        # Find the nearest escape point
        escape_point = self._find_nearest_escape_point(unit_id)
        
        if escape_point:
            # Move towards escape point
            path = self._find_path_to_position(unit_id, escape_point, profile.movement_range)
            if path:
                return AIAction("MOVE", unit_id, {"path": path})
        
        # If no escape point or can't move towards it, just wait
        return AIAction("WAIT", unit_id, {})
    
    def _determine_protect_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified protect action determination."""
        # Default to aggressive behavior
        return self._determine_aggressive_action(unit_id, profile)
    
    def _determine_patrol_action(self, unit_id: str, profile: AIProfile) -> Optional[AIAction]:
        """Simplified patrol action determination."""
        # Default to aggressive behavior
        return self._determine_aggressive_action(unit_id, profile)
    
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
