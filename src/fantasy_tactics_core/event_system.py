"""
Event System Module

This module is responsible for managing and executing scripted events within a chapter
based on various conditions. It provides the mechanism for triggering reinforcements,
dialogues, map changes, victory/loss conditions, and other dynamic gameplay elements.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union


class EventCondition:
    """Represents a specific condition that must be true for an event to execute."""
    
    def __init__(self, type: str, **kwargs):
        """
        Initialize an EventCondition.
        
        Args:
            type: Type of condition (e.g., "TurnNumber", "FlagSet", "Location")
            **kwargs: Parameters for the condition
        """
        self.type = type
        self.__dict__.update(kwargs)


class EventAction:
    """Represents a single action performed during an event sequence."""
    
    def __init__(self, type: str, **kwargs):
        """
        Initialize an EventAction.
        
        Args:
            type: Type of action (e.g., "SpawnUnit", "DisplayMessage", "SetFlag")
            **kwargs: Parameters for the action
        """
        self.type = type
        self.__dict__.update(kwargs)


class EventDefinition:
    """Represents a single event definition, containing trigger point, conditions, actions, and metadata."""
    
    def __init__(self, event_id: str, trigger_point: str, repeatable: bool, 
                 conditions: List[EventCondition], actions: List[EventAction]):
        """
        Initialize an EventDefinition.
        
        Args:
            event_id: Unique identifier for the event
            trigger_point: When to check the event conditions (e.g., "StartPlayerPhase", "EndEnemyPhase")
            repeatable: Whether the event can trigger multiple times
            conditions: List of conditions that must be met for the event to execute
            actions: List of actions to perform when the event executes
        """
        self.event_id = event_id
        self.trigger_point = trigger_point
        self.repeatable = repeatable
        self.conditions = conditions
        self.actions = actions


class ActionExecutor:
    """Executes actions defined in events by delegating to appropriate game systems."""
    
    def __init__(self, game_state_manager, unit_manager, map_system, ui_manager):
        """
        Initialize the ActionExecutor with references to game systems.
        
        Args:
            game_state_manager: Reference to the GameStateManager
            unit_manager: Reference to the UnitManager
            map_system: Reference to the MapSystem
            ui_manager: Reference to the UIManager
        """
        self.game_state_manager = game_state_manager
        self.unit_manager = unit_manager
        self.map_system = map_system
        self.ui_manager = ui_manager
    
    def execute(self, action: EventAction, context: Dict):
        """
        Execute a specific action.
        
        Args:
            action: The action to execute
            context: Context data for the action
        """
        if action.type == "SpawnUnit":
            self.unit_manager.spawn_unit(
                action.unit_template_id,
                action.location,
                getattr(action, 'count', 1),
                getattr(action, 'ai_settings', None)
            )
        
        elif action.type == "DisplayMessage":
            self.ui_manager.show_dialogue(action.message_key)
        
        elif action.type == "SetFlag":
            self.game_state_manager.set_flag(action.flag_id, True)
        
        elif action.type == "ClearFlag":
            self.game_state_manager.set_flag(action.flag_id, False)
        
        elif action.type == "EndChapter":
            self.game_state_manager.end_chapter(
                action.outcome,
                getattr(action, 'next_chapter_id', None)
            )
        
        elif action.type == "ChangeTile":
            self.map_system.change_tile(action.location, action.new_tile_type)
        
        elif action.type == "GiveItem":
            self.unit_manager.give_item(action.target_unit, action.item_id)
        
        elif action.type == "RemoveItem":
            self.unit_manager.remove_item(action.target_unit, action.item_id)
        
        elif action.type == "MoveUnit":
            self.unit_manager.move_unit(
                action.unit_id,
                action.target_location,
                getattr(action, 'pathfinding_type', "Default")
            )
        
        elif action.type == "ChangeUnitAI":
            self.unit_manager.change_unit_ai(
                action.target_unit,
                action.new_ai_settings
            )
        
        elif action.type == "ChangeUnitAffiliation":
            self.unit_manager.change_unit_affiliation(
                action.unit_id,
                action.new_affiliation
            )
        
        elif action.type == "PlaySound":
            if hasattr(self.ui_manager, 'play_sound'):
                self.ui_manager.play_sound(action.sound_id)
        
        elif action.type == "PlayMusic":
            if hasattr(self.ui_manager, 'play_music'):
                self.ui_manager.play_music(action.music_id)
        
        elif action.type == "ScreenFade":
            if hasattr(self.ui_manager, 'screen_fade'):
                self.ui_manager.screen_fade(
                    action.direction,
                    getattr(action, 'speed', 1.0),
                    getattr(action, 'color', (0, 0, 0))
                )
        
        elif action.type == "CameraFocus":
            if hasattr(self.ui_manager, 'camera_focus'):
                self.ui_manager.camera_focus(action.target)
        
        elif action.type == "Wait":
            if hasattr(self.ui_manager, 'wait'):
                self.ui_manager.wait(action.duration)
        
        elif action.type == "MarkUnitsLeftBehind":
            player_units = self.unit_manager.get_player_units_on_map()
            for unit in player_units:
                if unit.id != "LEIF":  # Assuming Leif is the one escaping
                    self.unit_manager.set_unit_status(unit.id, "CapturedLeftBehind")
        
        elif action.type == "ModifyUnitStats":
            self.unit_manager.modify_unit_stats(
                action.unit_id,
                action.stat_changes,
                getattr(action, 'duration', None)
            )
        
        elif action.type == "HealUnit":
            self.unit_manager.heal_unit(
                action.unit_id,
                getattr(action, 'amount', None),
                getattr(action, 'status_type', None)
            )
        
        else:
            logging.warning(f"Unsupported action type: {action.type}")


class EventManager:
    """
    Manages scripted events within a chapter, monitoring the game state for specific trigger
    conditions and executing predefined sequences of actions when those conditions are met.
    """
    
    def __init__(self):
        """Initialize the EventManager."""
        self.game_state = None
        self.data_provider = None
        self.action_executor = None
        self.chapter_events = []
        self.active_events = []
    
    def initialize(self, game_state, data_provider, action_executor, map_system=None):
        """
        Initialize the EventManager with the necessary dependencies.
        
        Args:
            game_state: Reference to the game state
            data_provider: Reference to the data provider
            action_executor: Reference to the action executor
            map_system: Reference to the map system (optional)
        """
        self.game_state = game_state
        self.data_provider = data_provider
        self.action_executor = action_executor
        self.map_system = map_system
        self.chapter_events = []
        self.active_events = []
    
    def load_chapter_events(self, chapter_id: str):
        """
        Load event definitions for a chapter.
        
        Args:
            chapter_id: ID of the chapter
        """
        self.chapter_events = self.data_provider.get_events_for_chapter(chapter_id)
        
        # Initialize internal flags for non-repeatable events if needed
        for event_def in self.chapter_events:
            if not event_def.repeatable:
                # Ensure a flag exists to track execution
                flag_name = f"event_{event_def.event_id}_triggered"
                try:
                    if not self.game_state.get_flag(flag_name):
                        try:
                            self.game_state.set_flag(flag_name, False)
                        except (AttributeError, TypeError):
                            logging.warning(f"Could not set flag {flag_name}")
                except (AttributeError, TypeError):
                    logging.warning(f"Could not check flag {flag_name}")
    
    def register_triggers(self, trigger_definitions: List[Dict]):
        """
        Register event triggers from chapter data.
        
        Args:
            trigger_definitions: List of trigger definition dictionaries
        """
        for trigger_def in trigger_definitions:
            # Convert trigger definition to EventCondition
            trigger_type = trigger_def.get('type', '')
            
            # Map chapter data trigger types to EventCondition types
            condition_type_map = {
                'turn_start': 'TurnNumber',
                'area_entered': 'Location',
                'talk_available': 'TalkBetweenUnits',
                'unit_defeated': 'UnitDeath',
                'village_visited': 'VisitLocation'
            }
            
            condition_type = condition_type_map.get(trigger_type, trigger_type)
            
            # Create condition with appropriate parameters based on type
            condition_params = {}
            if trigger_type == 'turn_start':
                condition_params = {'turn': trigger_def.get('value')}
            elif trigger_type == 'area_entered':
                # Convert area coordinates to a region or location format
                area = trigger_def.get('area', [])
                if len(area) == 2:  # Assuming format is [[x1, y1], [x2, y2]]
                    unit_id = 'any'  # Default to any unit
                    if 'faction' in trigger_def:
                        # This is simplified; in a real implementation we'd track units by faction
                        unit_id = f"{trigger_def['faction']}_unit"
                    
                    # For simplicity, we'll use the center of the area as the location
                    x1, y1 = area[0]
                    x2, y2 = area[1]
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    condition_params = {
                        'unit_id': unit_id,
                        'location': (center_x, center_y)
                    }
            elif trigger_type == 'talk_available':
                condition_params = {
                    'talker_id': trigger_def.get('unit1_id'),
                    'listener_id': trigger_def.get('unit2_id')
                }
            elif trigger_type == 'unit_defeated':
                condition_params = {'unit_id': trigger_def.get('target_unit_id')}
            elif trigger_type == 'village_visited':
                condition_params = {
                    'unit_id': trigger_def.get('visiting_unit_faction', 'any'),
                    'location': trigger_def.get('target_position')
                }
            
            # Store the trigger with its ID for later reference
            condition = EventCondition(type=condition_type, **condition_params)
            condition.trigger_id = trigger_def.get('trigger_id')
            
            # Add to a dictionary of available triggers
            if not hasattr(self, 'available_triggers'):
                self.available_triggers = {}
            
            self.available_triggers[trigger_def.get('trigger_id')] = condition
    
    def register_events(self, event_definitions: List[Dict]):
        """
        Register events from chapter data.
        
        Args:
            event_definitions: List of event definition dictionaries
        """
        if not hasattr(self, 'available_triggers'):
            self.available_triggers = {}
        
        for event_def in event_definitions:
            event_id = event_def.get('event_id')
            trigger_id = event_def.get('trigger')
            
            # Find the corresponding trigger condition
            conditions = []
            if trigger_id in self.available_triggers:
                conditions.append(self.available_triggers[trigger_id])
            
            # Map trigger to appropriate trigger point
            trigger_to_point = {
                'turn_start': 'StartPlayerPhase',
                'area_entered': 'UnitMoved',
                'talk_available': 'UnitAction',
                'unit_defeated': 'UnitDefeated',
                'village_visited': 'UnitAction'
            }
            
            # Determine trigger point based on the trigger type
            trigger_point = 'StartPlayerPhase'  # Default
            if conditions and hasattr(conditions[0], 'type'):
                condition_type = conditions[0].type
                # Map condition type back to trigger type
                type_to_trigger = {v: k for k, v in {
                    'turn_start': 'TurnNumber',
                    'area_entered': 'Location',
                    'talk_available': 'TalkBetweenUnits',
                    'unit_defeated': 'UnitDeath',
                    'village_visited': 'VisitLocation'
                }.items()}
                
                trigger_type = type_to_trigger.get(condition_type, '')
                trigger_point = trigger_to_point.get(trigger_type, 'StartPlayerPhase')
            
            # Convert actions
            actions = []
            for action_def in event_def.get('actions', []):
                action_type = action_def.get('type')
                
                # Map chapter data action types to EventAction types
                action_type_map = {
                    'spawn_reinforcements': 'SpawnUnit',
                    'show_dialogue': 'DisplayMessage',
                    'set_trigger_inactive': 'SetFlag',
                    'enable_talk_option': 'SetFlag',
                    'drop_item_at': 'GiveItem',
                    'give_item_to_unit': 'GiveItem'
                }
                
                mapped_type = action_type_map.get(action_type, action_type)
                
                # Create action with appropriate parameters based on type
                action_params = {}
                if action_type == 'spawn_reinforcements':
                    # This is simplified; in a real implementation we'd look up the reinforcement group
                    action_params = {
                        'unit_template_id': 'REINFORCEMENT',
                        'location': (0, 0)  # Placeholder
                    }
                elif action_type == 'show_dialogue':
                    action_params = {'message_key': action_def.get('dialogue_id')}
                elif action_type == 'set_trigger_inactive':
                    action_params = {'flag_id': f"event_{action_def.get('target_trigger_id')}_triggered"}
                elif action_type == 'enable_talk_option':
                    action_params = {'flag_id': f"talk_{action_def.get('unit1_id')}_{action_def.get('unit2_id')}_enabled"}
                elif action_type == 'drop_item_at' or action_type == 'give_item_to_unit':
                    action_params = {
                        'item_id': action_def.get('item_id'),
                        'target_unit': action_def.get('recipient_unit_triggering', 'NONE')
                    }
                
                actions.append(EventAction(type=mapped_type, **action_params))
            
            # Create and add the event definition
            event = EventDefinition(
                event_id=event_id,
                trigger_point=trigger_point,
                repeatable=False,  # Default to non-repeatable
                conditions=conditions,
                actions=actions
            )
            
            self.chapter_events.append(event)
    
    def check_events(self, trigger_point: str, context: Dict):
        """
        Check for events triggered at a specific point.
        
        Args:
            trigger_point: The trigger point to check
            context: Context data for the trigger
        """
        triggered_events = []
        
        for event_def in self.chapter_events:
            if event_def.trigger_point == trigger_point:
                # Check if already triggered (for non-repeatable)
                if not event_def.repeatable:
                    flag_name = f"event_{event_def.event_id}_triggered"
                    try:
                        if self.game_state.get_flag(flag_name):
                            continue
                    except (AttributeError, TypeError):
                        # If get_flag is not available, assume not triggered
                        logging.warning(f"Could not check flag {flag_name}, assuming not triggered")
                        pass
                
                # Check conditions
                if self.check_conditions(event_def, context):
                    triggered_events.append(event_def)
        
        # Handle priority if needed (e.g., EndChapter first)
        # Sort triggered_events based on priority rules
        
        for event_def in triggered_events:
            self.execute_event(event_def, context)
            if not event_def.repeatable:
                flag_name = f"event_{event_def.event_id}_triggered"
                try:
                    self.game_state.set_flag(flag_name, True)
                except (AttributeError, TypeError):
                    # If set_flag is not available, log a warning
                    logging.warning(f"Could not set flag {flag_name}")
                    pass
    
    def check_conditions(self, event_def: EventDefinition, context: Dict) -> bool:
        """
        Check if all conditions for an event are met.
        
        Args:
            event_def: The event definition
            context: Context data for the trigger
            
        Returns:
            True if all conditions are met, False otherwise
        """
        for condition in event_def.conditions:
            result = self.evaluate_condition(condition, context)
            if not result:
                return False  # AND logic: all conditions must pass
        
        return True  # All conditions passed
    
    def evaluate_condition(self, condition: EventCondition, context: Dict) -> bool:
        """
        Evaluate a specific condition.
        
        Args:
            condition: The condition to evaluate
            context: Context data for the trigger
            
        Returns:
            True if the condition is met, False otherwise
        """
        if condition.type == "TurnNumber":
            return self.game_state.current_turn == condition.turn
        
        elif condition.type == "FlagSet":
            return self.game_state.get_flag(condition.flag_id) == True
        
        elif condition.type == "FlagNotSet":
            return self.game_state.get_flag(condition.flag_id) == False
        
        elif condition.type == "Location":
            return check_unit_location(
                condition.unit_id,
                condition.location,
                self.game_state,
                self.map_system
            )
        
        elif condition.type == "UnitDeath":
            return self.game_state.is_unit_dead(condition.unit_id)
        
        elif condition.type == "TalkBetweenUnits":
            return check_talk_condition(condition, context)
        
        elif condition.type == "VisitLocation":
            return (context.get('action_type') == "Visit" and
                    context.get('unit_id') == condition.unit_id and
                    context.get('location') == condition.location)
        
        elif condition.type == "SeizeLocation":
            return (context.get('action_type') == "Seize" and
                    context.get('unit_id') == "LEIF" and  # Assuming Leif is the Lord
                    context.get('location') == condition.location)
        
        elif condition.type == "EscapeAction":
            return (context.get('action_type') == "Escape" and
                    context.get('unit_id') == condition.unit_id)
        
        elif condition.type == "UnitExists":
            unit = self.game_state.get_unit(condition.unit_id)
            return unit is not None and unit.is_on_map
        
        elif condition.type == "UnitHasItem":
            unit = self.game_state.get_unit(condition.unit_id)
            if not unit:
                return False
            
            for item in unit.inventory:
                if item.item_id == condition.item_id:
                    return True
            return False
        
        elif condition.type == "UnitsInRegion":
            region_tiles = self.map_system.get_region_tiles(condition.region_id)
            count = 0
            
            for unit_id, unit in self.game_state.unit_states.items():
                if unit.faction == condition.affiliation and unit.position in region_tiles:
                    count += 1
            
            return count >= condition.count
        
        elif condition.type == "ChapterObjectiveComplete":
            # This would check if the main objective is complete
            return self.game_state.is_objective_complete()
        
        elif condition.type == "IsIndoors":
            return self.map_system.is_indoor_map()
        
        elif condition.type == "IsOutdoors":
            return not self.map_system.is_indoor_map()
        
        else:
            logging.warning(f"Unsupported condition type: {condition.type}")
            return False
    
    def execute_event(self, event_def: EventDefinition, context: Dict):
        """
        Execute an event.
        
        Args:
            event_def: The event definition
            context: Context data for the trigger
        """
        logging.info(f"Executing event: {event_def.event_id}")
        
        for action in event_def.actions:
            self.action_executor.execute(action, context)


def check_unit_location(unit_id: str, location, unit_manager, map_system) -> bool:
    """
    Check if a unit is at a specific location.
    
    Args:
        unit_id: ID of the unit
        location: Location to check (coordinate or region ID)
        unit_manager: Reference to the unit manager
        map_system: Reference to the map system
        
    Returns:
        True if the unit is at the location, False otherwise
    """
    unit = unit_manager.get_unit(unit_id)
    if unit is None or not unit.is_on_map:
        return False
    
    if isinstance(location, tuple):
        # Exact coordinate
        return unit.position == location
    elif isinstance(location, str):
        # Region ID
        region_tiles = map_system.get_region_tiles(location)
        return unit.position in region_tiles
    
    return False


def check_talk_condition(condition: EventCondition, context: Dict) -> bool:
    """
    Check if a talk action matches the condition.
    
    Args:
        condition: The talk condition
        context: Context data for the trigger
        
    Returns:
        True if the talk action matches the condition, False otherwise
    """
    if context.get('action_type') != "Talk":
        return False
    
    talker_id = context.get('talker_id')
    listener_id = context.get('listener_id')
    
    # Check if the pair matches (in either order)
    return ((condition.talker_id == talker_id and condition.listener_id == listener_id) or
            (condition.talker_id == listener_id and condition.listener_id == talker_id))