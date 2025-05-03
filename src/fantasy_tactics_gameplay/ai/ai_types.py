"""
AI Types Module

This module defines the foundational types and data structures used throughout the AI system.
It serves as the core type definition layer for the modular AI architecture, providing
enums, classes, and data structures that are used by all other AI components.

The module contains three primary components:
1. AIBehaviorType: Enum defining the different AI behavior archetypes
2. AITargetPriority: Enum defining how AI units prioritize targets
3. AIProfile: Class encapsulating all parameters for an AI unit's behavior
4. AIAction: Class representing a decision made by the AI system
"""

from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Set, Union


class AIBehaviorType(Enum):
    """
    Types of AI behaviors based on the AI specification.
    
    These behavior types define the high-level decision-making patterns for AI units.
    Each behavior type corresponds to a specific archetype handler that implements
    the detailed logic for that behavior pattern.
    
    The enum includes both core archetypes from the new AI specification and
    legacy behavior types for backward compatibility with existing content.
    Each archetype represents a distinct behavior pattern that influences
    how units evaluate and select actions.
    """
    # Core archetypes from the specification
    CHARGE = auto()          # Prioritize moving towards and engaging player units
    GUARD = auto()           # Remain stationary unless a player unit enters defined range
    DEFEND_AREA = auto()     # Similar to Guard, but may move within a larger designated area
    ESCAPE = auto()          # Prioritize moving towards the nearest escape point
    HEAL_SUPPORT = auto()    # Prioritize healing allied units
    CAPTURE_PRIORITY = auto() # Evaluate capture actions against eligible targets
    THIEF_LOOT = auto()      # Prioritize moving towards and interacting with chests
    BOSS_GUARD = auto()      # Special behavior for boss units (typically on thrones)
    FOLLOW_PLAYER = auto()   # Follow player units (for NPCs)
    OBJECTIVE_ORIENTED = auto() # Focus on specific map objectives
    
    # Legacy behavior types (for backward compatibility)
    AGGRESSIVE = auto()      # Alias for CHARGE
    DEFENSIVE = auto()       # Prioritize staying in defensive positions
    CAUTIOUS = auto()        # Attack only when advantageous
    PASSIVE = auto()         # Don't move unless attacked
    STATIONARY = auto()      # Don't move at all
    HEALER = auto()          # Alias for HEAL_SUPPORT
    THIEF = auto()           # Alias for THIEF_LOOT
    BOSS = auto()            # Alias for BOSS_GUARD
    FLEE = auto()            # Alias for ESCAPE
    PROTECT = auto()         # Protect a specific unit or location
    PATROL = auto()          # Move between specific points


class AITargetPriority(Enum):
    """
    Target priority types for AI units.
    
    These priorities determine how AI units select targets when multiple
    options are available. The priority affects action scoring and target selection
    across different AI behavior types.
    
    Each priority type represents a different strategy for selecting targets:
    - WEAKEST: Target the unit with the lowest HP or defense
    - STRONGEST: Target the unit with the highest attack or threat level
    - CLOSEST: Target the nearest unit (default for most AI units)
    - LORD: Target the player's lord character as highest priority
    - HEALER: Target healing units to disrupt enemy support
    - SPECIFIC: Target a specific unit defined in the AI profile
    """
    WEAKEST = auto()     # Target the weakest player unit
    STRONGEST = auto()   # Target the strongest player unit
    CLOSEST = auto()     # Target the closest player unit
    LORD = auto()        # Target the lord (Leif)
    HEALER = auto()      # Target healers
    SPECIFIC = auto()    # Target a specific unit


class AIProfile:
    """
    Defines the behavior and priorities for an AI-controlled unit.
    
    The AIProfile encapsulates all parameters that influence an AI unit's decision-making,
    including its behavior type, target priorities, and various thresholds that affect
    action scoring. It serves as the configuration object that is passed to archetype
    handlers to determine specific behaviors.
    
    The profile contains a comprehensive set of parameters that control different
    aspects of AI behavior:
    - Core behavior pattern (CHARGE, GUARD, HEAL_SUPPORT, etc.)
    - Target selection strategy (WEAKEST, CLOSEST, LORD, etc.)
    - Aggression level and movement constraints
    - Special behavior parameters like guard radius and healing thresholds
    - Flags for enabling specialized actions like capturing
    
    This class provides a flexible configuration system that can represent
    a wide range of AI behaviors through parameter combinations.
    """
    
    def __init__(self, behavior_type: AIBehaviorType, target_priority: AITargetPriority,
                 aggression: int = 50, movement_range: Optional[int] = None,
                 specific_target_id: Optional[str] = None, patrol_points: Optional[List[Tuple[int, int]]] = None,
                 protect_unit_id: Optional[str] = None, protect_location: Optional[Tuple[int, int]] = None,
                 guard_radius: Optional[int] = None, heal_threshold_ally: float = 0.5,
                 heal_threshold_self: float = 0.3, retreat_threshold: float = 0.3,
                 capture_enabled: bool = False, use_status_staves: bool = False,
                 special_flags: Optional[List[str]] = None):
        """
        Initialize an AIProfile.
        
        Creates a new AI profile with the specified behavior parameters.
        All parameters have sensible defaults that can be overridden as needed.
        
        Args:
            behavior_type: Type of behavior (e.g., CHARGE, GUARD, HEAL_SUPPORT)
            target_priority: Target priority (e.g., WEAKEST, CLOSEST, LORD)
            aggression: Aggression level (0-100) - higher values favor offensive actions
            movement_range: Maximum movement range (None for unlimited)
            specific_target_id: ID of a specific target unit (for SPECIFIC priority)
            patrol_points: List of patrol points (for PATROL behavior)
            protect_unit_id: ID of unit to protect (for PROTECT behavior)
            protect_location: Location to protect (for PROTECT behavior)
            guard_radius: For GUARD/DEFEND_AREA: how far from the post to pursue
            heal_threshold_ally: HP% below which allies are considered for healing
            heal_threshold_self: HP% below which self-healing is prioritized
            retreat_threshold: HP% below which retreat behavior might trigger
            capture_enabled: Whether this unit will attempt captures
            use_status_staves: Whether this unit will use offensive staves
            special_flags: List of special behavior flags for custom behaviors
        """
        self.behavior_type = behavior_type
        self.target_priority = target_priority
        self.aggression = aggression
        self.movement_range = movement_range
        self.specific_target_id = specific_target_id
        self.patrol_points = patrol_points or []
        self.protect_unit_id = protect_unit_id
        self.protect_location = protect_location
        
        # New parameters from the AI specification
        self.guard_radius = guard_radius
        self.heal_threshold_ally = heal_threshold_ally
        self.heal_threshold_self = heal_threshold_self
        self.retreat_threshold = retreat_threshold
        self.capture_enabled = capture_enabled
        self.use_status_staves = use_status_staves
        self.special_flags = special_flags or []
        
        # Runtime state
        self.current_patrol_index = 0


class AIAction:
    """
    Represents an action decision made by the AI.
    
    This class encapsulates the final decision made by the AI system for a specific unit.
    It contains all necessary information to execute the action, including the action type,
    the unit performing the action, and any target-specific data needed for execution.
    AIAction objects are the output of the AI decision-making process and are consumed
    by the game's action execution system.
    
    The AIAction serves as the interface between the AI decision-making components
    and the game's action execution system. It provides a standardized format
    for representing AI decisions that can be translated into game actions.
    
    Common action types include:
    - MOVE: Movement to a new position
    - ATTACK: Attack an enemy unit
    - ITEM: Use an item or staff
    - WAIT: End turn without further action
    - CAPTURE: Attempt to capture an enemy unit
    """
    
    def __init__(self, action_type: str, unit_id: str, target_data: Dict):
        """
        Initialize an AIAction.
        
        Creates a new AIAction with the specified action type, unit ID, and target data.
        The target_data dictionary contains all additional information needed to execute
        the action, such as target coordinates, target unit IDs, item IDs, or movement paths.
        
        Args:
            action_type: Type of action (e.g., 'MOVE', 'ATTACK', 'ITEM', 'WAIT')
            unit_id: ID of the unit performing the action
            target_data: Dictionary containing data about the action target and parameters.
                       For movement actions, this may include a 'path' key.
                       For attacks, this may include a 'target_unit_id' key.
                       For item usage, this may include 'item_id' and 'target_unit_id' keys.
        """
        self.action_type = action_type
        self.unit_id = unit_id
        self.target_data = target_data