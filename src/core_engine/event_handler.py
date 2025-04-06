"""
Event Handler Module

This module manages scripted events within a chapter. It monitors the game state for specific
trigger conditions and executes predefined sequences of actions when those conditions are met.
"""

import logging
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Set, Union

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum


class EventTrigger(Enum):
    """Types of triggers that can initiate an event check."""
    TURN_START = auto()
    PHASE_START = auto()
    PHASE_END = auto()
    LOCATION_ENTER = auto()
    LOCATION_STAND = auto()
    ACTION_VISIT = auto()
    ACTION_TALK = auto()
    ACTION_SEIZE = auto()
    ACTION_ATTACK = auto()
    UNIT_DEATH = auto()
    FLAG_SET_EXTERNALLY = auto()


class ConditionType(Enum):
    """Types of conditions that can be checked for an event."""
    UNIT_ALIVE = auto()
    UNIT_DEAD = auto()
    FLAG_SET = auto()
    FLAG_NOT_SET = auto()
    UNIT_IN_REGION = auto()
    UNIT_HAS_ITEM = auto()
    TURN_GE = auto()
    TURN_LE = auto()
    TURN_NUMBER = auto()  # Exact turn number match
    RANDOM_CHANCE = auto()


class EventActionType(Enum):
    """Types of actions that can be performed during an event."""
    SHOW_DIALOGUE = auto()
    SPAWN_UNIT = auto()
    GIVE_ITEM = auto()
    SET_FLAG = auto()
    CLEAR_FLAG = auto()
    CHANGE_AI = auto()
    MODIFY_MAP = auto()
    MOVE_UNIT = auto()
    END_CHAPTER = auto()
    PLAY_SOUND = auto()
    PLAY_MUSIC = auto()
    CHANGE_FACTION = auto()
    END_SCENARIO = auto()


class EventCondition:
    """Represents a specific condition that must be true for an event to execute."""
    
    def __init__(self, condition_type: ConditionType, params: Dict):
        """
        Initialize an EventCondition.
        
        Args:
            condition_type: Type of condition
            params: Parameters for the condition
        """
        self.type = condition_type
        self.params = params


class EventAction:
    """Represents a single action performed during an event sequence."""
    
    def __init__(self, action_type: EventActionType, params: Dict):
        """
        Initialize an EventAction.
        
        Args:
            action_type: Type of action
            params: Parameters for the action
        """
        self.type = action_type
        self.params = params


class EventData:
    """Represents a single event definition, containing trigger, conditions, actions, and metadata."""
    
    def __init__(self, event_id: str, trigger: EventTrigger, trigger_params: Dict,
                 conditions: List[EventCondition], actions: List[EventAction],
                 priority: int = 0, is_repeatable: bool = False):
        """
        Initialize an EventData.
        
        Args:
            event_id: Unique identifier for the event
            trigger: Type of trigger that initiates the event check
            trigger_params: Parameters for the trigger
            conditions: List of conditions that must be met for the event to execute
            actions: List of actions to perform when the event executes
            priority: Priority for resolving simultaneous events
            is_repeatable: Whether the event can trigger multiple times
        """
        self.id = event_id
        self.trigger = trigger
        self.trigger_params = trigger_params
        self.conditions = conditions
        self.actions = actions
        self.priority = priority
        self.is_repeatable = is_repeatable
        self.has_triggered = False  # Runtime state


class EventHandler:
    """
    Manages scripted events within a chapter, monitoring the game state for specific trigger
    conditions and executing predefined sequences of actions when those conditions are met.
    """
    
    def __init__(self):
        """Initialize the EventHandler."""
        self.gameStateManager = None
        self.turnManager = None
        self.unitSystem = None
        self.mapSystem = None
        self.inventorySystem = None
        self.dataProvider = None
        self.uiManager = None
        self.aiManager = None
        
        # State
        self.chapterEvents = []
        self.activeEventFlags = set()
    
    def initialize(self, gameStateManager_instance, turnManager_instance, unitSystem_instance,
                  mapSystem_instance, inventorySystem_instance, dataProvider_instance,
                  uiManager_instance=None, aiManager_instance=None):
        """
        Initialize the EventHandler with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            turnManager_instance: Instance of the TurnManager
            unitSystem_instance: Instance of the UnitSystem
            mapSystem_instance: Instance of the MapSystem
            inventorySystem_instance: Instance of the InventorySystem
            dataProvider_instance: Instance of the DataProvider
            uiManager_instance: Instance of the UIManager (optional)
            aiManager_instance: Instance of the AIManager (optional)
        """
        self.gameStateManager = gameStateManager_instance
        self.turnManager = turnManager_instance
        self.unitSystem = unitSystem_instance
        self.mapSystem = mapSystem_instance
        self.inventorySystem = inventorySystem_instance
        self.dataProvider = dataProvider_instance
        self.uiManager = uiManager_instance
        self.aiManager = aiManager_instance
        
        # Load initial flags from game state
        if self.gameStateManager and self.gameStateManager.current_game_state:
            self.activeEventFlags = set(self.gameStateManager.current_game_state.event_flags.keys())
        
        logging.info("EventHandler initialized.")
    
    def load_chapter_events(self, chapter_id: str, scenario_name: Optional[str] = None):
        """
        Load event definitions for a chapter or scenario.
        
        Args:
            chapter_id: ID of the chapter
            scenario_name: Optional name of a test scenario
        """
        # Load event definitions from DataProvider
        raw_data = self.dataProvider.get_event_scripts(chapter_id, scenario_name)
        
        # Extract events list from the data structure
        # The events.yaml file has a structure with chapter_id and events keys
        if isinstance(raw_data, dict) and 'events' in raw_data:
            events_list = raw_data.get('events', [])
        else:
            events_list = raw_data if isinstance(raw_data, list) else []
        
        # Convert raw data to EventData objects if needed
        if events_list and len(events_list) > 0:
            if not isinstance(events_list[0], EventData):
                self.chapterEvents = self._convert_raw_events(events_list)
        else:
            # Ensure chapterEvents is always a list
            self.chapterEvents = []
        
        if scenario_name:
            logging.info(f"Loaded {len(self.chapterEvents)} events for scenario {scenario_name}.")
        else:
            logging.info(f"Loaded {len(self.chapterEvents)} events for chapter {chapter_id}.")
    
    # --- Event Checking Methods ---
    
    def check_turn_events(self, turn: int, phase: PhaseEnum):
        """
        Check for events triggered by the start of a turn or phase.
        
        Args:
            turn: Current turn number
            phase: Current phase
        """
        # Always check for TURN_START events, regardless of phase
        # This ensures that events like scenario_end will trigger at the start of any phase
        trigger_type = EventTrigger.TURN_START
        
        # Log the check for debugging purposes
        logging.info(f"Checking turn events for turn {turn}, phase {phase.name}")
        
        self.find_and_execute_events(trigger_type, {'turn': turn, 'phase': phase})
    
    def check_phase_end_events(self, turn: int, phase: PhaseEnum):
        """
        Check for events triggered by the end of a phase.
        
        Args:
            turn: Current turn number
            phase: Current phase
        """
        self.find_and_execute_events(EventTrigger.PHASE_END, {'turn': turn, 'phase': phase})
    
    def check_location_events(self, unit_id: str, new_position: Tuple[int, int]):
        """
        Check for events triggered by a unit moving to a specific location.
        
        Args:
            unit_id: ID of the unit
            new_position: New position of the unit
        """
        trigger_data = {'unit_id': unit_id, 'position': new_position}
        self.find_and_execute_events(EventTrigger.LOCATION_ENTER, trigger_data)
        self.find_and_execute_events(EventTrigger.LOCATION_STAND, trigger_data)
    
    def check_loss_conditions(self, game_state_manager) -> bool:
        """
        Check if any loss conditions are met based on events.
        
        Args:
            game_state_manager: GameStateManager instance
            
        Returns:
            True if a loss condition is met, False otherwise
        """
        # In a full implementation, this would check for specific event flags
        # that indicate loss conditions (e.g., "ally_unit_escaped", "time_expired")
        
        # For now, just check if any loss-related flags are set
        loss_flags = ["loss_condition", "ally_escaped", "time_expired", "objective_failed"]
        return any(flag in self.activeEventFlags for flag in loss_flags)
    
    def check_victory_conditions(self, game_state_manager, current_turn: int) -> bool:
        """
        Check if any victory conditions are met based on events.
        
        Args:
            game_state_manager: GameStateManager instance
            current_turn: Current turn number
            
        Returns:
            True if a victory condition is met, False otherwise
        """
        # In a full implementation, this would check for specific event flags
        # that indicate victory conditions (e.g., "boss_defeated", "all_enemies_defeated")
        
        # For now, just check if any victory-related flags are set
        victory_flags = ["victory_condition", "boss_defeated", "all_enemies_defeated", "objective_completed"]
        return any(flag in self.activeEventFlags for flag in victory_flags)
    
    def check_action_event(self, action_type: str, unit_id: str, target_data: Dict):
        """
        Check for events triggered by a specific action.
        
        Args:
            action_type: Type of action
            unit_id: ID of the unit performing the action
            target_data: Data about the action target
        """
        trigger_type = None
        trigger_data = {'unit_id': unit_id, **target_data}
        
        if action_type == "TALK":
            trigger_type = EventTrigger.ACTION_TALK
        elif action_type == "VISIT":
            trigger_type = EventTrigger.ACTION_VISIT
        elif action_type == "SEIZE":
            trigger_type = EventTrigger.ACTION_SEIZE
        elif action_type == "ATTACK":
            trigger_type = EventTrigger.ACTION_ATTACK
        
        if trigger_type:
            self.find_and_execute_events(trigger_type, trigger_data)
    
    def check_death_event(self, unit_id: str):
        """
        Check for events triggered by a unit's death.
        
        Args:
            unit_id: ID of the unit that died
        """
        self.find_and_execute_events(EventTrigger.UNIT_DEATH, {'unit_id': unit_id})
    
    # --- Core Event Logic ---
    
    def find_and_execute_events(self, trigger: EventTrigger, context: Dict):
        """
        Find and execute events that match the trigger and context.
        
        Args:
            trigger: Type of trigger
            context: Context data for the trigger
        """
        triggered_events = []
        
        for event in self.chapterEvents:
            if event.has_triggered and not event.is_repeatable:
                continue  # Already triggered
            
            if event.trigger == trigger:
                # Check specific trigger details (e.g., turn number matches context['turn'])
                if self.check_trigger_details(event, context):
                    # Check additional conditions (unit alive, flags set, etc.)
                    if self.check_event_conditions(event.conditions, context):
                        triggered_events.append(event)
        
        # Sort events by priority (higher priority first)
        triggered_events.sort(key=lambda e: e.priority, reverse=True)
        
        for event in triggered_events:
            self.execute_event(event, context)
            event.has_triggered = True  # Mark as triggered
    
    def check_trigger_details(self, event: EventData, context: Dict) -> bool:
        """
        Check if the trigger details match the context.
        
        Args:
            event: Event data
            context: Context data for the trigger
            
        Returns:
            True if the trigger details match, False otherwise
        """
        if event.trigger == EventTrigger.TURN_START:
            return event.trigger_params.get('turn') == context.get('turn')
        
        elif event.trigger in [EventTrigger.LOCATION_ENTER, EventTrigger.LOCATION_STAND]:
            # Check if context['position'] matches event.trigger_params['location'] (tile or region)
            # Check if context['unit_id'] matches event.trigger_params['unit_id'] (if specific unit)
            location_match = self._is_location_match(
                context.get('position'),
                event.trigger_params.get('location')
            )
            unit_match = (
                event.trigger_params.get('unit_id') is None or
                event.trigger_params.get('unit_id') == context.get('unit_id')
            )
            return location_match and unit_match
        
        elif event.trigger == EventTrigger.ACTION_TALK:
            # Check if context['unit_id'] and context['target_unit_id'] match event params
            talker_id = event.trigger_params.get('talker_id')
            listener_id = event.trigger_params.get('listener_id')
            unit_id = context.get('unit_id')
            target_unit_id = context.get('target_unit_id')
            
            return (
                (talker_id == unit_id and listener_id == target_unit_id) or
                (talker_id == target_unit_id and listener_id == unit_id)
            )
        
        elif event.trigger == EventTrigger.ACTION_VISIT:
            # Check if context['unit_id'] matches and context['target_tile'] matches
            return (
                event.trigger_params.get('visitor_id') == context.get('unit_id') and
                event.trigger_params.get('location') == context.get('target_tile')
            )
        
        elif event.trigger == EventTrigger.ACTION_SEIZE:
            # Check if context['unit_id'] (must be Lord) matches and context['target_tile'] matches
            return (
                self._is_lord(context.get('unit_id')) and
                event.trigger_params.get('location') == context.get('target_tile')
            )
        
        elif event.trigger == EventTrigger.UNIT_DEATH:
            return event.trigger_params.get('unit_id') == context.get('unit_id')
        
        return False
    
    def check_event_conditions(self, conditions: List[EventCondition], context: Dict) -> bool:
        """
        Check if all conditions for an event are met.
        
        Args:
            conditions: List of conditions
            context: Context data for the trigger
            
        Returns:
            True if all conditions are met, False otherwise
        """
        for condition in conditions:
            if condition.type == ConditionType.UNIT_ALIVE:
                unit_id = condition.params.get('unit_id')
                if not self._is_unit_alive(unit_id):
                    return False
            
            elif condition.type == ConditionType.UNIT_DEAD:
                unit_id = condition.params.get('unit_id')
                if self._is_unit_alive(unit_id):
                    return False
            
            elif condition.type == ConditionType.FLAG_SET:
                flag_name = condition.params.get('flag_name')
                if flag_name not in self.activeEventFlags:
                    return False
            
            elif condition.type == ConditionType.FLAG_NOT_SET:
                flag_name = condition.params.get('flag_name')
                if flag_name in self.activeEventFlags:
                    return False
            
            elif condition.type == ConditionType.UNIT_IN_REGION:
                unit_id = condition.params.get('unit_id')
                region = condition.params.get('region')
                if not self._is_unit_in_region(unit_id, region):
                    return False
            
            elif condition.type == ConditionType.UNIT_HAS_ITEM:
                unit_id = condition.params.get('unit_id')
                item_type = condition.params.get('item_type')
                if not self._unit_has_item(unit_id, item_type):
                    return False
            
            elif condition.type == ConditionType.TURN_GE:
                turn = condition.params.get('turn')
                current_turn = self.gameStateManager.current_game_state.current_turn
                if current_turn < turn:
                    return False
            
            elif condition.type == ConditionType.TURN_LE:
                turn = condition.params.get('turn')
                current_turn = self.gameStateManager.current_game_state.current_turn
                if current_turn > turn:
                    return False
            
            elif condition.type == ConditionType.TURN_NUMBER:
                turn = condition.params.get('turn')
                current_turn = self.gameStateManager.current_game_state.current_turn
                if current_turn != turn:
                    return False
            
            elif condition.type == ConditionType.RANDOM_CHANCE:
                chance = condition.params.get('chance')
                import random
                if random.randint(1, 100) > chance:
                    return False
            
            else:
                logging.warning(f"Unknown condition type: {condition.type}")
                return False
        
        return True  # All conditions passed
    
    def execute_event(self, event: EventData, context: Dict):
        """
        Execute an event.
        
        Args:
            event: Event data
            context: Context data for the trigger
        """
        logging.info(f"Executing Event: {event.id}")
        
        for action in event.actions:
            self.execute_event_action(action, context)
    
    def execute_event_action(self, action: EventAction, context: Dict):
        """
        Execute a single event action.
        
        Args:
            action: Action data
            context: Context data for the trigger
        """
        if action.type == EventActionType.SHOW_DIALOGUE:
            if self.uiManager:
                self.uiManager.show_dialogue(
                    action.params.get('dialogue_id'),
                    action.params.get('speaker_unit_id')
                )
            else:
                logging.info(f"Dialogue: {action.params.get('dialogue_id')}")
        
        elif action.type == EventActionType.SPAWN_UNIT:
            if self.unitSystem:
                self.unitSystem.spawn_unit(
                    action.params.get('unit_data'),
                    action.params.get('location'),
                    action.params.get('ai_override')
                )
            else:
                logging.info(f"Spawn Unit: {action.params.get('unit_data')} at {action.params.get('location')}")
        
        elif action.type == EventActionType.GIVE_ITEM:
            if self.inventorySystem:
                self.inventorySystem.give_item(
                    action.params.get('recipient_unit_id'),
                    action.params.get('item_type')
                )
            else:
                logging.info(f"Give Item: {action.params.get('item_type')} to {action.params.get('recipient_unit_id')}")
        
        elif action.type == EventActionType.SET_FLAG:
            flag_name = action.params.get('flag_name')
            self.activeEventFlags.add(flag_name)
            if self.gameStateManager:
                self.gameStateManager.current_game_state.event_flags[flag_name] = True
            logging.info(f"Set Flag: {flag_name}")
        
        elif action.type == EventActionType.CLEAR_FLAG:
            flag_name = action.params.get('flag_name')
            self.activeEventFlags.discard(flag_name)
            if self.gameStateManager and flag_name in self.gameStateManager.current_game_state.event_flags:
                del self.gameStateManager.current_game_state.event_flags[flag_name]
            logging.info(f"Clear Flag: {flag_name}")
        
        elif action.type == EventActionType.CHANGE_AI:
            if self.aiManager:
                self.aiManager.change_unit_ai(
                    action.params.get('unit_id'),
                    action.params.get('new_ai_profile')
                )
            else:
                logging.info(f"Change AI: {action.params.get('unit_id')} to {action.params.get('new_ai_profile')}")
        
        elif action.type == EventActionType.MODIFY_MAP:
            if self.mapSystem:
                self.mapSystem.modify_tile(
                    action.params.get('location'),
                    action.params.get('new_tile_type')
                )
            else:
                logging.info(f"Modify Map: {action.params.get('location')} to {action.params.get('new_tile_type')}")
        
        elif action.type == EventActionType.MOVE_UNIT:
            if self.mapSystem:
                self.mapSystem.execute_scripted_move(
                    action.params.get('unit_id'),
                    action.params.get('path')
                )
            else:
                logging.info(f"Move Unit: {action.params.get('unit_id')} along path")
        
        elif action.type == EventActionType.END_CHAPTER:
            if self.gameStateManager:
                outcome = action.params.get('outcome', 'victory')
                # This would trigger chapter end logic in the game engine
                logging.info(f"End Chapter: {outcome}")
        
        elif action.type == EventActionType.PLAY_SOUND:
            if self.uiManager:
                self.uiManager.play_sound(action.params.get('sound_id'))
            else:
                logging.info(f"Play Sound: {action.params.get('sound_id')}")
        
        elif action.type == EventActionType.PLAY_MUSIC:
            if self.uiManager:
                self.uiManager.play_music(action.params.get('music_id'))
            else:
                logging.info(f"Play Music: {action.params.get('music_id')}")
        
        elif action.type == EventActionType.CHANGE_FACTION:
            if self.unitSystem:
                self.unitSystem.change_unit_faction(
                    action.params.get('unit_id'),
                    action.params.get('new_faction')
                )
            else:
                logging.info(f"Change Faction: {action.params.get('unit_id')} to {action.params.get('new_faction')}")
        
        elif action.type == EventActionType.END_SCENARIO:
            self.execute_end_scenario(action.params.get('reason', 'Scenario completed'))
        
        else:
            logging.warning(f"Unknown event action type: {action.type}")
    
    # --- Public helpers for ActionHandler ---
    
    def has_talk_event(self, unit1_id: str, unit2_id: str) -> bool:
        """
        Check if a talk event exists between two units.
        
        Args:
            unit1_id: ID of the first unit
            unit2_id: ID of the second unit
            
        Returns:
            True if a talk event exists, False otherwise
        """
        for event in self.chapterEvents:
            if event.trigger == EventTrigger.ACTION_TALK:
                # Check if this pair matches the event params (either direction)
                p = event.trigger_params
                if (p.get('talker_id') == unit1_id and p.get('listener_id') == unit2_id) or \
                   (p.get('talker_id') == unit2_id and p.get('listener_id') == unit1_id):
                    return True
        return False
    
    def trigger_talk_event(self, unit1_id: str, unit2_id: str) -> bool:
        """
        Trigger a talk event between two units.
        
        Args:
            unit1_id: ID of the first unit
            unit2_id: ID of the second unit
            
        Returns:
            True if the event was triggered, False otherwise
        """
        context = {'unit_id': unit1_id, 'target_unit_id': unit2_id}
        
        # Find the specific event again and execute it
        for event in self.chapterEvents:
            if event.trigger == EventTrigger.ACTION_TALK:
                p = event.trigger_params
                if (p.get('talker_id') == unit1_id and p.get('listener_id') == unit2_id) or \
                   (p.get('talker_id') == unit2_id and p.get('listener_id') == unit1_id):
                    if self.check_event_conditions(event.conditions, context):
                        self.execute_event(event, context)
                        event.has_triggered = True
                        return True
        return False
    
    def trigger_map_event(self, event_type: str, unit_id: str, target_tile: Tuple[int, int]) -> bool:
        """
        Trigger a map event (Visit, Seize).
        
        Args:
            event_type: Type of event
            unit_id: ID of the unit
            target_tile: Coordinates of the target tile
            
        Returns:
            True if the event was triggered, False otherwise
        """
        trigger_type = None
        
        if event_type == "VISIT":
            trigger_type = EventTrigger.ACTION_VISIT
        elif event_type == "SEIZE":
            trigger_type = EventTrigger.ACTION_SEIZE
        
        if not trigger_type:
            return False
        
        context = {'unit_id': unit_id, 'target_tile': target_tile}
        
        # Find and execute matching events
        for event in self.chapterEvents:
            if event.trigger == trigger_type:
                if self.check_trigger_details(event, context):
                    if self.check_event_conditions(event.conditions, context):
                        self.execute_event(event, context)
                        event.has_triggered = True
                        return True
        return False
    
    def execute_end_scenario(self, reason: str) -> None:
        """
        Set a flag in the game state indicating the scenario is complete.
        
        Args:
            reason: The reason for ending the scenario
        """
        if self.gameStateManager and self.gameStateManager.current_game_state:
            # Set a special flag to indicate scenario completion
            self.gameStateManager.current_game_state.event_flags['scenario_complete'] = True
            # Store the reason for ending the scenario
            self.gameStateManager.current_game_state.event_flags['scenario_end_reason'] = reason
            logging.info(f"Scenario ended: {reason}")
    
    # --- Helper Methods ---
    
    def _convert_raw_events(self, raw_events: List[Dict]) -> List[EventData]:
        """
        Convert raw event data to EventData objects.
        
        Args:
            raw_events: List of raw event data
            
        Returns:
            List of EventData objects
        """
        events = []
        
        for raw_event in raw_events:
            # Convert conditions
            conditions = []
            for raw_condition in raw_event.get('conditions', []):
                condition_type = getattr(ConditionType, raw_condition.get('type'))
                conditions.append(EventCondition(condition_type, raw_condition.get('params', {})))
            
            # Convert actions
            actions = []
            for raw_action in raw_event.get('actions', []):
                action_type = getattr(EventActionType, raw_action.get('type'))
                actions.append(EventAction(action_type, raw_action.get('params', {})))
            
            # Create EventData
            event = EventData(
                raw_event.get('id'),
                getattr(EventTrigger, raw_event.get('trigger')),
                raw_event.get('trigger_params', {}),
                conditions,
                actions,
                raw_event.get('priority', 0),
                raw_event.get('is_repeatable', False)
            )
            
            events.append(event)
        
        return events
    
    def _is_location_match(self, position: Tuple[int, int], location) -> bool:
        """
        Check if a position matches a location (tile or region).
        
        Args:
            position: Position to check
            location: Location to match against (tile or region)
            
        Returns:
            True if the position matches the location, False otherwise
        """
        if isinstance(location, tuple):
            # Single tile
            return position == location
        elif isinstance(location, list):
            # List of tiles
            return position in location
        elif isinstance(location, dict) and 'region' in location:
            # Region (e.g., rectangle)
            region = location['region']
            if 'x1' in region and 'y1' in region and 'x2' in region and 'y2' in region:
                x, y = position
                return (region['x1'] <= x <= region['x2'] and region['y1'] <= y <= region['y2'])
        
        return False
    
    def _is_unit_alive(self, unit_id: str) -> bool:
        """
        Check if a unit is alive.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit is alive, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        return unit is not None and unit.disposition == 'ACTIVE'
    
    def _is_unit_in_region(self, unit_id: str, region) -> bool:
        """
        Check if a unit is in a region.
        
        Args:
            unit_id: ID of the unit
            region: Region to check
            
        Returns:
            True if the unit is in the region, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        return self._is_location_match(unit.position, {'region': region})
    
    def _unit_has_item(self, unit_id: str, item_type: str) -> bool:
        """
        Check if a unit has an item of a specific type.
        
        Args:
            unit_id: ID of the unit
            item_type: Type of item
            
        Returns:
            True if the unit has the item, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        for item in unit.inventory:
            item_data = self.dataProvider.get_item_data(item.item_id)
            if item_data and item_data.type == item_type:
                return True
        
        return False
    
    def _is_lord(self, unit_id: str) -> bool:
        """
        Check if a unit is the Lord (Leif).
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit is the Lord, False otherwise
        """
        # In Thracia 776, Leif is the Lord
        return unit_id == "LEIF"