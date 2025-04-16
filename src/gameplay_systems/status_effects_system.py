"""
Status Effects System Module

This module implements the Status Effects system for the Fantasy Tactics Game,
based on the mechanics found in Fire Emblem: Thracia 776.
"""
from typing import Dict, List, Optional, Any, Union
import logging
from src.core_engine.data_provider import StatEnum



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
        
        # Subscribe to relevant events
        if event_system:
            event_system.subscribe("TURN_START", self._handle_turn_start)
            event_system.subscribe("TURN_END", self._handle_turn_end)
    
    def _handle_turn_start(self, event_data):
        """Handle turn start events."""
        if 'unit_id' in event_data:
            self.process_turn_start_effects(event_data['unit_id'])
    
    def _handle_turn_end(self, event_data):
        """Handle turn end events."""
        if 'unit_id' in event_data:
            self.process_turn_end(event_data['unit_id'])
    
    def apply_status(self, unit_id: str, status_effect_name: str, source=None, duration=None) -> bool:
        """
        Apply a status effect to a unit.
        
        For Sleep status specifically:
        - Prevents the unit from taking any actions
        - Sets the unit's Avoid stat to 0
        - Causes mounted units to dismount
        - Can be cured by taking damage or when duration expires
        
        For Petrify status specifically:
        - Prevents the unit from taking any actions
        - Sets the unit's Avoid stat to 0
        - Increases Defense and Resistance by +10
        - Sets combat stats (STR, MAG, SKL, SPD) to 0
        - Can only be cured by Restore staff or equivalent status-clearing effect
        - Does not expire over time
        
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
    def handle_damage_taken(self, unit_id: str, damage: int):
        """
        Handle status effects that should be removed when a unit takes damage.
        
        Specifically for Sleep status:
        - Sleep is cured when a unit takes any amount of damage greater than 0
        - This occurs after damage calculation but before any potential counter-attack
        
        Args:
            unit_id: The ID of the unit
            damage: The amount of damage taken
        """
        if damage <= 0 or unit_id not in self.active_statuses:
            return
        
        statuses_to_remove = []
        unit = self.game_state_manager.get_unit(unit_id)
        
        # Check for statuses with CURE_ON_DAMAGE effect
        for status in self.active_statuses[unit_id]:
            for effect in status.effects:
                if effect["type"] == "CURE_ON_DAMAGE":
                    statuses_to_remove.append(status)
                    logging.info(f"Status {status.name} removed from unit {unit_id} due to taking damage")
                    break
        
        # Remove the statuses
        for status in statuses_to_remove:
            self.active_statuses[unit_id].remove(status)
            self.event_system.publish("STATUS_REMOVED", {
                "unit": unit,
                "status": status.name,
                "reason": "Damage Taken"
            })
        
        # Remove the unit entry if no statuses remain
        if unit_id in self.active_statuses and not self.active_statuses[unit_id]:
            del self.active_statuses[unit_id]
    
    def process_turn_start_effects(self, unit_id: str):
        """
        Process status effects at the start of a unit's turn.
        
        Args:
            unit_id: The ID of the unit
        """
        if unit_id not in self.active_statuses:
            return
        
        unit = self.game_state_manager.get_unit(unit_id)
        
        # Process status effects that apply at turn start
        for status in self.active_statuses[unit_id]:
            if status.name == "Poison":
                damage = status.get_effect_parameter("PERIODIC_DAMAGE", "amount", default=1)
                self.unit_system.apply_damage(unit, damage, source="Poison")
                self.event_system.publish("POISON_DAMAGE", {
                    "unit": unit,
                    "damage": damage
                })
            elif status.name == "Berserk":
                # Log that the unit is berserked
                logging.info(f"Unit {unit_id} is berserked and will attack the nearest unit")
                self.event_system.publish("BERSERK_ACTIVE", {
                    "unit": unit
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
        unit = self.game_state_manager.get_unit(unit_id)
        
        for status in self.active_statuses[unit_id]:
            # Only decrement scripted duration statuses
            if status.duration_type == "SCRIPTED_TURNS":
                if status.decrement_turn():
                    statuses_to_remove.append(status)
                    # Log status expiry
                    logging.info(f"Status {status.name} expired for unit {unit_id}")
        
        # Remove expired statuses
        for status in statuses_to_remove:
            self.active_statuses[unit_id].remove(status)
            self.event_system.publish("STATUS_EXPIRED", {
                "unit_id": unit_id,
                "status": status.name
            })
            
            # Special handling for Berserk expiry
            if status.name == "Berserk":
                self.event_system.publish("BERSERK_EXPIRED", {
                    "unit_id": unit_id
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
        
        For Petrify status specifically:
        - Sets combat stats (STR, MAG, SKL, SPD) to 0
        - Increases Defense and Resistance by +10
        - Sets Avoid to 0 (handled in combat calculations)
        
        Args:
            unit_id: The ID of the unit
            base_stats: The unit's base stats
            
        Returns:
            Modified stats dictionary
        """
        modified_stats = base_stats.copy()
        
        # Apply status effects
        if unit_id in self.active_statuses:
            # Special handling for Petrify status - zeroes out combat stats first
            if self.has_status(unit_id, "Petrify"):
                # Zero out combat stats but leave other stats unchanged
                modified_stats[StatEnum.STR] = 0
                modified_stats[StatEnum.MAG] = 0
                modified_stats[StatEnum.SKL] = 0
                modified_stats[StatEnum.SPD] = 0
                modified_stats[StatEnum.DEF] = 0  # Note: Petrify might also add flat DEF later
                # LUK, CON, MOV, and HP are not zeroed by Petrify's zeroing effect
            # Apply other stat modifications
            for status in self.active_statuses[unit_id]:
                for effect in status.effects:
                    if effect["type"] == "SET_STAT" or effect["type"] == "STAT_OVERRIDE":
                        stat_name = effect["parameters"].get("stat")
                        stat_value = effect["parameters"].get("value")
                        if stat_name and stat_value is not None:
                            # Convert string stat name to enum if needed
                            # Use StatEnum if possible, otherwise use string key
                            try:
                                stat_enum = StatEnum[stat_name.upper()]
                                modified_stats[stat_enum] = stat_value
                            except KeyError:
                                modified_stats[stat_name] = stat_value # Handle non-enum stats like AVOID
                    elif effect["type"] == "STAT_MODIFIER_FLAT":
                        stat_name = effect["parameters"].get("stat")
                        stat_value = effect["parameters"].get("value", 0)
                        if stat_name and stat_value is not None:
                            # Use StatEnum if possible, otherwise use string key
                            try:
                                stat_enum = StatEnum[stat_name.upper()]
                                if stat_enum in modified_stats: # Ensure stat exists before modifying
                                     modified_stats[stat_enum] += stat_value
                            except KeyError:
                                # Handle non-enum stats like AVOID, DEF, RES directly if needed
                                if stat_name in modified_stats:
                                    modified_stats[stat_name] += stat_value
        
        return modified_stats
    
    # This method is replaced by the more comprehensive version below
    
    def can_perform_action(self, unit_id: str, action_type: str) -> bool:
        """
        Check if a unit can perform a specific action based on status effects.
        
        Sleep status prevents a unit from performing any action, regardless of the action type.
        Petrify status prevents a unit from performing any action, regardless of the action type.
        The unit's turn is immediately skipped if they are petrified.
        Other status effects like Silence may only prevent specific actions (e.g., Magic, Staff).
        
        Args:
            unit_id: The ID of the unit
            action_type: The type of action to check, or "ANY" to check if any action is possible
            
        Returns:
            bool: True if the unit can perform the action, False otherwise
        """
        # Statuses that prevent any player-controlled action
        action_blocking_statuses = {"Sleep", "Petrify", "Paralysis", "Berserk"}
        
        active_unit_statuses = self.get_active_statuses(unit_id)
        unit_status_names = {status.name for status in active_unit_statuses}

        if any(status in unit_status_names for status in action_blocking_statuses):
             return False # Cannot perform any player-controlled action
        
        # If checking for any action, we've already passed the main checks
        if action_type == "ANY":
            return True
        
        # Check for Silence preventing magic/staff use
        # Check for Silence preventing magic/staff use
        if "Silence" in unit_status_names and action_type in ["Magic", "Staff"]:
            return False
        
        # Check specific action restrictions from effects list
        # Check specific action restrictions from effects list
        for status in active_unit_statuses:
            for effect in status.effects:
                effect_type = effect.get("type")
                if effect_type == "ACTION_RESTRICTION" or effect_type == "BLOCK_ACTION":
                    params = effect.get("parameters", {})
                    # Check if this effect blocks all actions
                    if params.get("all", False) or params.get("value") == "ALL":
                        return False
                    # Check if this effect blocks the specific action type
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
            
        # The nested function `can_unit_act` was unused and its logic is covered
        # by the loop below and the `can_perform_action` method. Removed it.
        # Check for statuses that override AI
        for status in self.active_statuses[unit_id]:
            if status.name == "Berserk":
                return "BERSERK_AI"
            if status.name in ["Sleep", "Petrify", "Paralysis"]:
                return "NO_ACTION_AI"
        
        return None