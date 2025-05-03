"""
AI Profile Manager Module

This module manages AI profiles for units, including loading, storing, and updating profiles.
It serves as the central repository for AI behavior configurations and handles the mapping
between unit data and AI behavior profiles. The AIProfileManager is responsible for
initializing AI profiles from data sources and providing access to these profiles
throughout the AI decision-making process.

The module implements a flexible profile system that supports both modern archetype-based
AI behaviors and legacy behavior types, providing backward compatibility while enabling
the new modular AI architecture.
"""

import logging
from typing import Dict, Optional

from src.gameplay_systems.ai.ai_types import AIBehaviorType, AITargetPriority, AIProfile
from src.core_engine.game_state import FactionEnum


class AIProfileManager:
    """
    Manages AI profiles for units, including loading, storing, and updating profiles.
    
    This class serves as the central repository for AI behavior configurations and is
    responsible for:
    1. Loading AI profiles from data sources
    2. Mapping between legacy and new AI behavior types
    3. Creating default profiles when specific configurations are not available
    4. Providing access to profiles for the AI decision-making components
    5. Updating profiles during gameplay in response to events or scripted changes
    
    The AIProfileManager acts as a bridge between the data layer and the AI behavior
    implementation, ensuring that each unit has an appropriate AI profile based on
    its characteristics and the scenario requirements.
    """
    
    def __init__(self):
        """
        Initialize the AIProfileManager.
        
        Sets up the initial state with an empty dictionary for unit AI profiles
        and null references to the game state manager and data provider.
        These references will be populated when initialize() is called.
        """
        self.unit_ai_profiles = {}  # unit_id -> AIProfile
        self.gameStateManager = None
        self.dataProvider = None
    
    def initialize(self, gameStateManager, dataProvider):
        """
        Initialize the AIProfileManager with necessary dependencies.
        
        This method sets up the AIProfileManager with references to the game state
        and data sources needed to create and manage AI profiles. It should be called
        during system initialization before any AI profiles are loaded or accessed.
        
        Args:
            gameStateManager: Instance of the GameStateManager that provides access to the current game state
            dataProvider: Instance of the DataProvider that provides access to unit and AI configuration data
        """
        self.gameStateManager = gameStateManager
        self.dataProvider = dataProvider
        self.unit_ai_profiles = {}  # Reset profiles
    
    def load_ai_profiles(self):
        """
        Load AI profiles for all units from the DataProvider.
        
        This method iterates through all enemy and NPC units in the current game state,
        retrieves their AI configuration data, and creates appropriate AIProfile instances.
        It handles the mapping between legacy and new AI behavior types, and creates
        default profiles when specific configurations are not available.
        
        The method performs the following steps:
        1. Identifies all enemy and NPC units in the current game state
        2. Retrieves AI profile data for each unit from the data provider
        3. Maps legacy behavior types to new archetypes if needed
        4. Creates AIProfile instances with appropriate parameters
        5. Falls back to default profiles based on unit type when specific data is unavailable
        
        The method should be called whenever the game state changes significantly,
        such as when starting a new chapter or when units are added to the game.
        """
        for unit_id, unit in self.gameStateManager.current_game_state.unit_states.items():
            if unit.faction in [FactionEnum.ENEMY, FactionEnum.NPC]:
                # Get AI profile data from DataProvider
                ai_data = self.dataProvider.get_unit_ai_profile(unit_id)
                
                if ai_data:
                    # Get the behavior type, with mapping from legacy to new archetypes if needed
                    behavior_type_str = ai_data.get('behavior_type', 'CHARGE')
                    # Map legacy behavior types to new archetypes if needed
                    behavior_type_mapping = {
                        'AGGRESSIVE': 'CHARGE',
                        'HEALER': 'HEAL_SUPPORT',
                        'THIEF': 'THIEF_LOOT',
                        'BOSS': 'BOSS_GUARD',
                        'FLEE': 'ESCAPE'
                    }
                    
                    # Use the mapped behavior type if it exists, otherwise use the original
                    if behavior_type_str in behavior_type_mapping:
                        behavior_type_str = behavior_type_mapping[behavior_type_str]
                    
                    # Create AIProfile from data
                    profile = AIProfile(
                        behavior_type=getattr(AIBehaviorType, behavior_type_str),
                        target_priority=getattr(AITargetPriority, ai_data.get('target_priority', 'CLOSEST')),
                        aggression=ai_data.get('aggression', 50),
                        movement_range=ai_data.get('movement_range'),
                        specific_target_id=ai_data.get('specific_target_id'),
                        patrol_points=ai_data.get('patrol_points'),
                        protect_unit_id=ai_data.get('protect_unit_id'),
                        protect_location=ai_data.get('protect_location'),
                        # New parameters from the AI specification
                        guard_radius=ai_data.get('guard_radius'),
                        heal_threshold_ally=ai_data.get('heal_threshold_ally', 0.5),
                        heal_threshold_self=ai_data.get('heal_threshold_self', 0.3),
                        retreat_threshold=ai_data.get('retreat_threshold', 0.3),
                        capture_enabled=ai_data.get('capture_enabled', False),
                        use_status_staves=ai_data.get('use_status_staves', False),
                        special_flags=ai_data.get('special_flags', [])
                    )
                    
                    self.unit_ai_profiles[unit_id] = profile
                else:
                    # Check if the unit data has an ai_archetype field
                    unit_data = self.dataProvider.get_unit_data(unit_id)
                    ai_archetype = None
                    
                    if unit_data and 'ai_archetype' in unit_data:
                        ai_archetype = unit_data['ai_archetype']
                    
                    # Default profile based on unit type or specified archetype
                    behavior_type = AIBehaviorType.CHARGE  # Default
                    
                    if ai_archetype:
                        # Map the archetype string to AIBehaviorType
                        try:
                            behavior_type = getattr(AIBehaviorType, ai_archetype.upper())
                        except (AttributeError, ValueError):
                            logging.warning(f"Unknown AI archetype '{ai_archetype}' for unit {unit_id}, using default")
                    
                    self.unit_ai_profiles[unit_id] = AIProfile(
                        behavior_type=behavior_type,
                        target_priority=AITargetPriority.CLOSEST,
                        aggression=50
                    )
    
    def get_profile(self, unit_id: str) -> Optional[AIProfile]:
        """
        Get the AI profile for a unit.
        
        This method retrieves the AIProfile for a specific unit, which contains
        all the behavior parameters and configuration needed by the AI decision-making
        components to determine the unit's actions.
        
        The profile includes information such as:
        - Behavior type (CHARGE, GUARD, HEAL_SUPPORT, etc.)
        - Target priority (WEAKEST, STRONGEST, CLOSEST, etc.)
        - Aggression level and movement constraints
        - Special behavior parameters (guard radius, healing thresholds, etc.)
        
        Args:
            unit_id: ID of the unit to retrieve the profile for
            
        Returns:
            The unit's AI profile, or None if no profile exists for the unit
        """
        return self.unit_ai_profiles.get(unit_id)
    
    def set_profile(self, unit_id: str, profile: AIProfile):
        """
        Set the AI profile for a unit.
        
        This method assigns a new AIProfile to a specific unit, replacing any
        existing profile. This can be used to change a unit's behavior during
        gameplay in response to events or scripted changes.
        
        Unlike change_unit_ai(), this method accepts a pre-constructed AIProfile
        object rather than dictionary data, making it more suitable for programmatic
        profile changes within the AI system.
        
        Args:
            unit_id: ID of the unit to set the profile for
            profile: The new AI profile to assign to the unit
        """
        self.unit_ai_profiles[unit_id] = profile
    
    def change_unit_ai(self, unit_id: str, new_ai_profile: Dict):
        """
        Change the AI profile for a unit based on dictionary data.
        
        This method creates a new AIProfile from dictionary data and assigns it
        to a specific unit. It's typically used when receiving AI configuration
        changes from event scripts or other game systems that provide data in
        dictionary format rather than as AIProfile objects.
        
        The method handles the conversion from dictionary format to AIProfile object,
        ensuring all parameters are properly set with appropriate defaults when
        specific values are not provided in the input dictionary.
        
        Args:
            unit_id: ID of the unit to change the AI profile for
            new_ai_profile: Dictionary containing the new AI profile configuration data,
                           including behavior_type, target_priority, and other parameters
        """
        if unit_id not in self.unit_ai_profiles:
            return
        
        # Create new AIProfile from data
        profile = AIProfile(
            behavior_type=getattr(AIBehaviorType, new_ai_profile.get('behavior_type', 'CHARGE')),
            target_priority=getattr(AITargetPriority, new_ai_profile.get('target_priority', 'CLOSEST')),
            aggression=new_ai_profile.get('aggression', 50),
            movement_range=new_ai_profile.get('movement_range'),
            specific_target_id=new_ai_profile.get('specific_target_id'),
            patrol_points=new_ai_profile.get('patrol_points'),
            protect_unit_id=new_ai_profile.get('protect_unit_id'),
            protect_location=new_ai_profile.get('protect_location'),
            guard_radius=new_ai_profile.get('guard_radius'),
            heal_threshold_ally=new_ai_profile.get('heal_threshold_ally', 0.5),
            heal_threshold_self=new_ai_profile.get('heal_threshold_self', 0.3),
            retreat_threshold=new_ai_profile.get('retreat_threshold', 0.3),
            capture_enabled=new_ai_profile.get('capture_enabled', False),
            use_status_staves=new_ai_profile.get('use_status_staves', False),
            special_flags=new_ai_profile.get('special_flags', [])
        )
        
        self.unit_ai_profiles[unit_id] = profile
        logging.info(f"Changed AI profile for unit {unit_id} to {profile.behavior_type.name}")
    
    def ensure_profile_exists(self, unit_id: str) -> AIProfile:
        """
        Ensure that an AI profile exists for the given unit, creating a default one if needed.
        
        This method is a safety mechanism that guarantees an AIProfile will be available
        for any unit that needs one. If no profile exists for the specified unit, a default
        profile with basic CHARGE behavior is created and stored.
        
        The default profile uses:
        - CHARGE behavior type (aggressive, attack-oriented behavior)
        - CLOSEST target priority (targets the nearest enemy)
        - 50 aggression level (balanced between offense and defense)
        
        This method is typically called by AI decision-making components before attempting
        to use a unit's profile, to prevent null reference errors.
        
        Args:
            unit_id: ID of the unit to ensure a profile exists for
            
        Returns:
            The unit's existing AI profile or a newly created default profile
        """
        if unit_id not in self.unit_ai_profiles:
            # Create a default profile
            self.unit_ai_profiles[unit_id] = AIProfile(
                behavior_type=AIBehaviorType.CHARGE,
                target_priority=AITargetPriority.CLOSEST,
                aggression=50
            )
        
        return self.unit_ai_profiles[unit_id]