"""
Unit State Module

This module defines the UnitState class which represents the current state of a unit on the map.
It includes attributes for tracking unit properties, stats, inventory, and action state, including
support for special actions like the 'Move Again' (Dance/Play) skill.
"""

from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Set, Union

class StatusEnum(Enum):
    """Enum representing the status of a unit."""
    NORMAL = auto()
    RESCUING = auto()  # Unit is carrying another unit
    RESCUED = auto()   # Unit is being carried
    CAPTURED = auto()  # Unit has been captured by an enemy

class DispositionEnum(Enum):
    ACTIVE = auto()  # Unit is active in the current chapter
    DEAD = auto()    # Unit has been killed
    ESCAPED = auto() # Unit has escaped the map
    CAPTURED_BY_ENEMY = auto()  # Unit has been captured by an enemy
    BENCHED = auto() # Unit is not deployed in the current chapter

class StatusEffectEnum(Enum):
    POISON = auto()
    SLEEP = auto()
    SILENCE = auto()
    BERSERK = auto()
    PETRIFY = auto()  # Added for petrify status
    STAT_BOOST = auto()  # For temporary stat boosts

class StatusEffectInstance:
    """Represents an active status effect on a unit."""
    def __init__(self, type: StatusEffectEnum, duration: int, magnitude: int = 0):
        self.type = type
        self.duration = duration  # Turns remaining, -1 for permanent until cured/chapter end
        self.magnitude = magnitude  # For stat boosts

class ItemInstance:
    """Represents an item instance in a unit's inventory."""
    def __init__(self, item_id: str, current_durability: int):
        self.item_id = item_id
        self.current_durability = current_durability

class UnitState:
    """Represents the current state of a unit on the map."""
    
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.class_id: str = ""
        self.faction = None  # FactionEnum.PLAYER
        self.position: Tuple[int, int] = (0, 0)
        
        self.current_hp: int = 0
        self.max_hp: int = 0
        
        # Base Stats
        self.base_stats: Dict[str, int] = {}
        
        # Growths
        self.growth_rates: Dict[str, int] = {}
        
        self.level: int = 1
        self.experience: int = 0
        
        self.inventory: List[ItemInstance] = []
        self.equipped_weapon_index: int = -1  # -1 if none
        
        self.weapon_ranks: Dict[str, str] = {}  # WeaponType -> Rank
        self.weapon_exp: Dict[str, int] = {}    # WeaponType -> Experience points
        
        self.current_fatigue: int = 0
        
        self.status_effects: List[StatusEffectInstance] = []
        
        # Action state for current turn
        self.has_moved: bool = False
        self.has_acted: bool = False
        self.is_immobile: bool = False  # Added for ballista system
        
        # Move Again skill attributes
        self.has_acted_this_turn: bool = False  # Tracks if the unit has performed its primary action this phase
        self.was_refreshed_this_turn: bool = False  # Tracks if the unit has been granted an extra action via Dance/Play this phase
        
        # Relationships/Bonuses
        self.support_partner_ids: List[str] = []
        self.leadership_stars: int = 0
        self.pcc: int = 0  # Pursuit Critical Coefficient
        
        # Capture/Rescue State
        self.is_captured: bool = False
        self.carrying_unit_id: Optional[str] = None
        
        # Overall Status
        self.disposition: DispositionEnum = DispositionEnum.ACTIVE
        
        # Component system
        self.components: Dict[str, Any] = {}
    
    def has_status(self, status_type: StatusEffectEnum) -> bool:
        """Check if the unit has a specific status effect."""
        return any(status.type == status_type for status in self.status_effects)
    
    def add_component(self, component) -> None:
        """
        Add a component to the unit.
        
        Args:
            component: The component to add
        """
        component_type = component.__class__.__name__
        self.components[component_type] = component
    
    def remove_component(self, component_type: str) -> None:
        """
        Remove a component from the unit.
        
        Args:
            component_type: Type of component to remove
        """
        if component_type in self.components:
            del self.components[component_type]
    
    def get_component(self, component_type: str) -> Optional[Any]:
        """
        Get a component from the unit.
        
        Args:
            component_type: Type of component to get
            
        Returns:
            The component if found, None otherwise
        """
        return self.components.get(component_type)
    
    def has_component(self, component_type: str) -> bool:
        """
        Check if the unit has a component.
        
        Args:
            component_type: Type of component to check for
            
        Returns:
            True if the unit has the component, False otherwise
        """
        return component_type in self.components
    
    def set_immobile(self, immobile: bool) -> None:
        """
        Set whether the unit is immobile.
        
        Args:
            immobile: True if the unit should be immobile, False otherwise
        """
        self.is_immobile = immobile
    
    def is_attackable(self) -> bool:
        """
        Check if the unit can be attacked.
        
        Returns:
            True if the unit can be attacked, False otherwise
        """
        return self.disposition == DispositionEnum.ACTIVE
    
    def has_property(self, property_name: str) -> bool:
        """
        Check if the unit has a specific property.
        
        Args:
            property_name: Name of the property to check for
            
        Returns:
            True if the unit has the property, False otherwise
        """
        # For now, just handle IS_FLYING property
        if property_name == "IS_FLYING":
            # Check if the unit's class has the FLYING movement type
            return hasattr(self, 'movement_type') and self.movement_type == "FLYING"
        
        return False