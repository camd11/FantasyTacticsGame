"""
Status Effects System Module

This module implements the Status Effects system for the Fantasy Tactics Game,
based on the mechanics found in Fire Emblem: Thracia 776.
"""

from typing import Dict, List, Optional, Any, Union


class StatusEffectInstance:
    """Represents an active status effect on a unit."""
    
    def __init__(self, status_data):
        """
        Initialize a new status effect instance.
        
        Args:
            status_data: Data object containing status effect properties
        """
        self.name = status_data.name
        self.description = status_data.description
        self.effects = status_data.effects
        self.duration_type = status_data.duration_type
        self.cure_methods = status_data.cure_methods
        self.icon = status_data.icon
        self.turns_remaining = None
        
        # Initialize turns_remaining if duration_type is SCRIPTED_TURNS
        if self.duration_type == "SCRIPTED_TURNS":
            self.turns_remaining = getattr(status_data, 'turns_remaining', None)
    
    def decrement_turn(self) -> bool:
        """
        Decrement the remaining turns for scripted duration statuses.
        
        Returns:
            bool: True if the status has expired, False otherwise
        """
        if self.duration_type == "SCRIPTED_TURNS" and self.turns_remaining is not None:
            self.turns_remaining -= 1
            return self.turns_remaining <= 0
        return False
    
    def get_effect_parameter(self, effect_type: str, param_name: str, default=None) -> Any:
        """
        Get a parameter value from an effect of the specified type.
        
        Args:
            effect_type: The type of effect to search for
            param_name: The name of the parameter to retrieve
            default: Default value to return if parameter is not found
            
        Returns:
            The parameter value or the default if not found
        """
        for effect in self.effects:
            if effect["type"] == effect_type:
                return effect.get("parameters", {}).get(param_name, default)
        return default


class StatusEffectManager:
    """Manages status effects for all units in the game."""
    
    def __init__(self):
        """Initialize the status effect manager."""
        self.active_statuses = {}
        self.game_state_manager = None
        self.data_provider = None
        self.unit_system = None
        self.event_system = None
    
    def initialize(self, game_state_manager, data_provider, unit_system, event_system):
        """
        Initialize the status effect manager with required dependencies.
        
        Args:
            game_state_manager: The game state manager instance
            data_provider: The data provider instance
            unit_system: The unit system instance
            event_system: The event system instance
        """
        self.game_state_manager = game_state_manager
        self.data_provider = data_provider
        self.unit_system = unit_system
        self.event_system = event_system
    
    def apply_status(self, unit_id: str, status_effect_name: str, source=None, duration=None) -> bool:
        """
        Apply a status effect to a unit.
        
        Args:
            unit_id: The ID of the target unit
            status_effect_name: The name of the status effect to apply
            source: The source of the status effect (e.g., weapon, staff)
            duration: Optional duration for scripted status effects
            
        Returns:
            bool: True if the status was applied, False otherwise
        """
        # Get the unit
        unit = self.game_state_manager.get_unit(unit_id)
        
        # Initialize the unit's status list if needed
        if unit_id not in self.active_statuses:
            self.active_statuses[unit_id] = []
        
        # Prevent stacking the same status effect
        for status in self.active_statuses[unit_id]:
            if status.name == status_effect_name:
                return False  # Already affected
        
        # Get status effect data
        status_data = self.data_provider.get_status_effect_data(status_effect_name)
        
        # Create a new status effect instance
        instance = StatusEffectInstance(status_data)
        
        # Set duration for scripted status effects
        if instance.duration_type == "SCRIPTED_TURNS" and duration is not None:
            instance.turns_remaining = duration
        
        # Add to active statuses
        self.active_statuses[unit_id].append(instance)
        
        # Handle immediate effects (e.g., Dismount on Sleep for mounted units)
        if status_effect_name == "Sleep" and unit.is_mounted():
            self.unit_system.dismount_unit(unit)
        
        # Publish event
        self.event_system.publish("STATUS_APPLIED", {
            "unit": unit,
            "status": status_effect_name,
            "source": source
        })
        
        return True
    
    def cure_status(self, unit_id: str, status_name=None, cure_method="Unknown") -> bool:
        """
        Cure a status effect from a unit.
        
        Args:
            unit_id: The ID of the unit
            status_name: The name of the status to cure (None to cure all applicable)
            cure_method: The method used to cure the status
            
        Returns:
            bool: True if any status was cured, False otherwise
        """
        # Get the unit
        unit = self.game_state_manager.get_unit(unit_id)
        
        # Check if unit has any statuses
        if unit_id not in self.active_statuses or not self.active_statuses[unit_id]:
            return False
        
        statuses_to_remove = []
        
        if status_name:  # Cure a specific status
            # Special case: Petrify requires Kia Staff
            if status_name == "Petrify" and cure_method != "Kia Staff":
                return False
            
            found = False
            for status in self.active_statuses[unit_id]:
                if status.name == status_name and cure_method in status.cure_methods:
                    statuses_to_remove.append(status)
                    found = True
                    break
            
            if not found:
                return False  # Status not found or cure method invalid
        else:  # Cure all applicable statuses
            for status in self.active_statuses[unit_id]:
                # Restore staff doesn't cure Petrify
                if status.name == "Petrify" and cure_method == "Restore Staff":
                    continue
                if cure_method in status.cure_methods:
                    statuses_to_remove.append(status)
        
        if not statuses_to_remove:
            return False  # Nothing was cured
        
        # Remove the cured statuses
        for status in statuses_to_remove:
            self.active_statuses[unit_id].remove(status)
            self.event_system.publish("STATUS_CURED", {
                "unit": unit,
                "status": status.name,
                "method": cure_method
            })
        
        # Remove the unit entry if no statuses remain
        if not self.active_statuses[unit_id]:
            del self.active_statuses[unit_id]
        
        return True
    
    def process_turn_start_effects(self, unit_id: str):
        """
        Process status effects at the start of a unit's turn.
        
        Args:
            unit_id: The ID of the unit
        """
        if unit_id not in self.active_statuses:
            return
        
        unit = self.game_state_manager.get_unit(unit_id)
        
        for status in self.active_statuses[unit_id]:
            if status.name == "Poison":
                damage = status.get_effect_parameter("PERIODIC_DAMAGE", "amount", default=1)
                self.unit_system.apply_damage(unit, damage, source="Poison")
                self.event_system.publish("POISON_DAMAGE", {
                    "unit": unit,
                    "damage": damage
                })
    
    def process_turn_end(self, unit_id: str):
        """
        Process status effects at the end of a unit's turn.
        
        Args:
            unit_id: The ID of the unit
        """
        if unit_id not in self.active_statuses:
            return
        
        statuses_to_remove = []
        
        for status in self.active_statuses[unit_id]:
            # Only decrement scripted duration statuses
            if status.duration_type == "SCRIPTED_TURNS":
                if status.decrement_turn():
                    statuses_to_remove.append(status)
        
        # Remove expired statuses
        for status in statuses_to_remove:
            self.active_statuses[unit_id].remove(status)
            self.event_system.publish("STATUS_EXPIRED", {
                "unit": unit_id,
                "status": status.name
            })
        
        # Remove the unit entry if no statuses remain
        if unit_id in self.active_statuses and not self.active_statuses[unit_id]:
            del self.active_statuses[unit_id]
    
    def process_chapter_end(self):
        """Clear all status effects at the end of a chapter."""
        self.active_statuses.clear()
        self.event_system.publish("ALL_STATUSES_CLEARED", {
            "reason": "Chapter End"
        })
    
    def has_status(self, unit_id: str, status_name: str) -> bool:
        """
        Check if a unit has a specific status effect.
        
        Args:
            unit_id: The ID of the unit
            status_name: The name of the status effect
            
        Returns:
            bool: True if the unit has the status, False otherwise
        """
        if unit_id not in self.active_statuses:
            return False
        
        for status in self.active_statuses[unit_id]:
            if status.name == status_name:
                return True
        
        return False
    
    def get_active_statuses(self, unit_id: str) -> List[StatusEffectInstance]:
        """
        Get all active status effects for a unit.
        
        Args:
            unit_id: The ID of the unit
            
        Returns:
            List of active status effect instances
        """
        return self.active_statuses.get(unit_id, [])
    
    def get_modified_stats(self, unit_id: str, base_stats: Dict) -> Dict:
        """
        Get modified stats based on active status effects.
        
        Args:
            unit_id: The ID of the unit
            base_stats: The unit's base stats
            
        Returns:
            Modified stats dictionary
        """
        modified_stats = base_stats.copy()
        
        # Check for statuses that zero stats
        zero_stats = self.has_status(unit_id, "Sleep") or self.has_status(unit_id, "Petrify")
        
        # Apply stat modifications
        if zero_stats:
            from src.core_engine.data_provider import StatEnum
            # Use the enum constants instead of string literals
            modified_stats[StatEnum.STR] = 0
            modified_stats[StatEnum.MAG] = 0
            modified_stats[StatEnum.SKL] = 0
            modified_stats[StatEnum.SPD] = 0
            modified_stats[StatEnum.DEF] = 0
            # Note: Luck, Con, Mov, HP are generally not zeroed by these statuses
        
        return modified_stats
    
    def can_perform_action(self, unit_id: str, action_type: str) -> bool:
        """
        Check if a unit can perform a specific action based on status effects.
        
        Args:
            unit_id: The ID of the unit
            action_type: The type of action to check
            
        Returns:
            bool: True if the unit can perform the action, False otherwise
            
        Notes:
            - Units with Sleep, Petrify, or Paralysis status cannot perform any actions
            - Units with Silence status cannot perform Magic or Staff actions
            - Other status effects may have specific action restrictions defined in their effects list
        """
        # Check for statuses that prevent all actions
        if self.has_status(unit_id, "Sleep") or self.has_status(unit_id, "Petrify") or self.has_status(unit_id, "Paralysis"):
            return False  # Cannot perform any action
        
        # Check for Silence preventing magic/staff use
        if self.has_status(unit_id, "Silence") and action_type in ["Magic", "Staff"]:
            return False
        
        # Check if unit has any statuses
        if unit_id not in self.active_statuses:
            return True
        
        # Check specific action restrictions from effects list
        for status in self.active_statuses[unit_id]:
            for effect in status.effects:
                if effect.get("type") == "ACTION_RESTRICTION":
                    params = effect.get("parameters", {})
                    if params.get("all", False):
                        return False  # All actions restricted
                    if params.get("action") == action_type and params.get("allowed") is False:
                        return False
        
        return True
    
    def get_ai_override(self, unit_id: str) -> Optional[str]:
        """
        Get AI override based on status effects.
        
        Args:
            unit_id: The ID of the unit
            
        Returns:
            String indicating AI override type, or None for standard AI
        """
        # Check if unit has any statuses
        if unit_id not in self.active_statuses:
            return None
        
        # Check for statuses that override AI
        for status in self.active_statuses[unit_id]:
            if status.name == "Berserk":
                return "BERSERK_AI"
            if status.name in ["Sleep", "Petrify", "Paralysis"]:
                return "NO_ACTION_AI"
        
        return None