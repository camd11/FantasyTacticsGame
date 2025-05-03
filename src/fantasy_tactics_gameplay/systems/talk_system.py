"""
Talk System Module

This module manages special conversations and interactions between specific units on the battlefield map.
These interactions can trigger various outcomes, such as dialogue display, item acquisition, unit recruitment,
or setting game state flags. It integrates with the Unit, Action, Event, Dialogue, Inventory, and UI systems.
"""

import logging
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Set, Union

from src.core_engine.game_state import GameStateManager, GameState, FactionEnum
from src.core_engine.data_provider import DataProvider


class TalkOutcomeType(Enum):
    """Enum representing the possible outcomes of a talk event."""
    DIALOGUE = auto()
    ITEM = auto()
    RECRUIT = auto()
    FLAG = auto()
    MULTIPLE = auto()


class Condition:
    """Represents a condition that must be met for a talk event to be available."""
    
    def __init__(self, condition_type: str, condition_data: Dict[str, Any]):
        """
        Initialize a condition.
        
        Args:
            condition_type: Type of condition (e.g., FLAG_CHECK, TURN_CHECK)
            condition_data: Data specific to the condition type
        """
        self.type = condition_type
        self.data = condition_data


class OutcomeSubEvent:
    """Represents a sub-event for a MULTIPLE outcome type."""
    
    def __init__(self, outcome_type: TalkOutcomeType, outcome_data: Dict[str, Any]):
        """
        Initialize an outcome sub-event.
        
        Args:
            outcome_type: Type of outcome
            outcome_data: Data specific to the outcome type
        """
        self.outcome_type = outcome_type
        self.outcome_data = outcome_data


class TalkEvent:
    """Represents a talk event between two units."""
    
    def __init__(self, event_id: str, initiator_unit_id: str, target_unit_id: str, 
                 outcome_type: Union[TalkOutcomeType, str], outcome_data: Dict[str, Any],
                 is_repeatable: bool = False, max_uses: int = 1, required_conditions: List[Condition] = None):
        """
        Initialize a talk event.
        
        Args:
            event_id: Unique identifier for this talk event
            initiator_unit_id: ID of the unit that must initiate the talk
            target_unit_id: ID of the unit that must be the target
            outcome_type: Type of outcome
            outcome_data: Data specific to the outcome type
            is_repeatable: Can this talk event occur multiple times?
            max_uses: If repeatable, how many times?
            required_conditions: Additional conditions that must be met
        """
        self.event_id = event_id
        self.initiator_unit_id = initiator_unit_id
        self.target_unit_id = target_unit_id
        
        # Handle string or enum for outcome_type
        if isinstance(outcome_type, str):
            self.outcome_type = getattr(TalkOutcomeType, outcome_type)
        else:
            self.outcome_type = outcome_type
            
        self.outcome_data = outcome_data
        self.is_repeatable = is_repeatable
        self.max_uses = max_uses
        self.required_conditions = required_conditions or []


class TalkSystem:
    """
    Manages special conversations and interactions between specific units on the battlefield map.
    """
    
    def __init__(self):
        """Initialize the TalkSystem."""
        self.gameStateManager = None
        self.dataProvider = None
        self.mapSystem = None
        self.actionSystem = None
        self.inventorySystem = None
        self.unitSystem = None
        self.scenarioLoader = None
        self.dialogueManager = None
        self.eventManager = None
    
    def initialize(self, gameStateManager_instance: GameStateManager, 
                  dataProvider_instance: DataProvider,
                  mapSystem_instance,
                  actionSystem_instance,
                  inventorySystem_instance,
                  unitSystem_instance,
                  scenarioLoader_instance,
                  dialogueManager_instance=None,
                  eventManager_instance=None) -> None:
        """
        Initialize the TalkSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
            mapSystem_instance: Instance of the MapSystem
            actionSystem_instance: Instance of the ActionSystem
            inventorySystem_instance: Instance of the InventorySystem
            unitSystem_instance: Instance of the UnitSystem
            scenarioLoader_instance: Instance of the ScenarioLoader
            dialogueManager_instance: Instance of the DialogueManager (optional)
            eventManager_instance: Instance of the EventManager (optional)
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        self.mapSystem = mapSystem_instance
        self.actionSystem = actionSystem_instance
        self.inventorySystem = inventorySystem_instance
        self.unitSystem = unitSystem_instance
        self.scenarioLoader = scenarioLoader_instance
        self.dialogueManager = dialogueManager_instance
        self.eventManager = eventManager_instance
        
        # Initialize ActiveTalkState in the game state if it doesn't exist
        if not hasattr(self.gameStateManager.current_game_state, 'ActiveTalkState'):
            self.gameStateManager.current_game_state.ActiveTalkState = type('ActiveTalkState', (), {
                'completed_talk_events': set(),
                'talk_event_uses': {}
            })
        
        logging.info("TalkSystem initialized.")
    
    def can_initiate_talk(self, selected_unit, target_unit, current_game_state: GameState) -> bool:
        """
        Check if a selected unit can initiate a talk with an adjacent target unit.
        
        Args:
            selected_unit: The unit that would initiate the talk
            target_unit: The potential target unit for the talk
            current_game_state: Current game state
            
        Returns:
            True if the selected unit can initiate a talk with the target unit, False otherwise
        """
        # 1. Basic Checks
        if not selected_unit or not target_unit:
            return False
        
        if selected_unit.faction != FactionEnum.PLAYER:
            return False
        
        if not self.mapSystem.are_units_adjacent(selected_unit.position, target_unit.position):
            return False
        
        if self.actionSystem.has_unit_acted_or_waited(selected_unit.id):
            return False
        
        # 2. Find Matching Talk Events
        possible_events = self.scenarioLoader.get_talk_events_for_pair(selected_unit.id, target_unit.id)
        if not possible_events:
            return False
        
        # 3. Check Event Conditions and Usage Limits
        for event in possible_events:
            # Check if already completed (non-repeatable)
            if not event.is_repeatable and event.event_id in current_game_state.ActiveTalkState.completed_talk_events:
                continue
            
            # Check usage limits (repeatable)
            if event.is_repeatable:
                current_uses = current_game_state.ActiveTalkState.talk_event_uses.get(event.event_id, 0)
                if current_uses >= event.max_uses:
                    continue
            
            # Check specific conditions (flags, turn number, etc.)
            all_conditions_met = True
            for condition in event.required_conditions:
                if not self.check_condition(condition, current_game_state):
                    all_conditions_met = False
                    break
            
            if not all_conditions_met:
                continue
            
            # If we reach here, at least one valid talk event exists
            return True
        
        # No valid, available talk events found for this pair under current conditions
        return False
    
    def check_condition(self, condition: Condition, game_state: GameState) -> bool:
        """
        Check if a condition is met.
        
        Args:
            condition: The condition to check
            game_state: Current game state
            
        Returns:
            True if the condition is met, False otherwise
        """
        if condition.type == "FLAG_CHECK":
            return game_state.event_flags.get(condition.data.get("flag_name"), False) == condition.data.get("expected_value", True)
        
        elif condition.type == "TURN_CHECK":
            current_turn = game_state.current_turn
            min_turn = condition.data.get("min_turn", 1)
            max_turn = condition.data.get("max_turn", float('inf'))
            return min_turn <= current_turn <= max_turn
        
        # Add other condition types as needed
        
        return False
    
    def initiate_talk(self, selected_unit, target_unit, current_game_state: GameState) -> bool:
        """
        Execute the talk action, consuming the unit's turn and triggering the outcome.
        
        Args:
            selected_unit: The unit initiating the talk
            target_unit: The target unit for the talk
            current_game_state: Current game state
            
        Returns:
            True if the talk was initiated successfully, False otherwise
        """
        # 1. Find the specific event to trigger
        valid_event = self.find_first_valid_talk_event(selected_unit, target_unit, current_game_state)
        if not valid_event:
            logging.error("Attempted to initiate talk, but no valid event found.")
            return False
        
        # 2. Consume Action
        self.actionSystem.mark_unit_action_taken(selected_unit.id)
        
        # 3. Process Outcome
        self.process_talk_outcome(valid_event, selected_unit, target_unit, current_game_state)
        
        # 4. Update Talk State Tracking
        if not valid_event.is_repeatable:
            current_game_state.ActiveTalkState.completed_talk_events.add(valid_event.event_id)
        else:
            current_uses = current_game_state.ActiveTalkState.talk_event_uses.get(valid_event.event_id, 0)
            current_game_state.ActiveTalkState.talk_event_uses[valid_event.event_id] = current_uses + 1
        
        return True
    
    def find_first_valid_talk_event(self, initiator, target, game_state: GameState) -> Optional[TalkEvent]:
        """
        Find the first valid talk event for a pair of units.
        
        Args:
            initiator: The unit initiating the talk
            target: The target unit for the talk
            game_state: Current game state
            
        Returns:
            The first valid talk event, or None if no valid event is found
        """
        possible_events = self.scenarioLoader.get_talk_events_for_pair(initiator.id, target.id)
        
        for event in possible_events:
            # Check if already completed (non-repeatable)
            if not event.is_repeatable and event.event_id in game_state.ActiveTalkState.completed_talk_events:
                continue
            
            # Check usage limits (repeatable)
            if event.is_repeatable:
                current_uses = game_state.ActiveTalkState.talk_event_uses.get(event.event_id, 0)
                if current_uses >= event.max_uses:
                    continue
            
            # Check specific conditions (flags, turn number, etc.)
            all_conditions_met = True
            for condition in event.required_conditions:
                if not self.check_condition(condition, game_state):
                    all_conditions_met = False
                    break
            
            if all_conditions_met:
                return event
        
        return None
    
    def process_talk_outcome(self, event: TalkEvent, initiator, target, game_state: GameState) -> None:
        """
        Process the outcome of a talk event.
        
        Args:
            event: The talk event to process
            initiator: The unit that initiated the talk
            target: The target unit for the talk
            game_state: Current game state
        """
        if event.outcome_type == TalkOutcomeType.DIALOGUE:
            # Handle dialogue outcome
            dialogue_id = event.outcome_data.get("dialogue_id")
            if dialogue_id and self.dialogueManager:
                self.dialogueManager.start_dialogue(dialogue_id, participants=[initiator, target])
        
        elif event.outcome_type == TalkOutcomeType.ITEM:
            # Handle item outcome
            item_id = event.outcome_data.get("item_id")
            quantity = event.outcome_data.get("quantity", 1)
            
            # Determine recipient (usually initiator, but could be specified)
            recipient_unit = initiator  # Default
            if "recipient_id" in event.outcome_data:
                recipient_unit = self.gameStateManager.get_unit(event.outcome_data["recipient_id"])
            
            if item_id and recipient_unit:
                success = self.inventorySystem.add_item_to_unit(recipient_unit.id, item_id, quantity)
                if not success:
                    logging.warning(f"Failed to add item {item_id} from talk event {event.event_id} to unit {recipient_unit.id} (inventory full?).")
                    # Handle fallback? Send to convoy? Display message?
        
        elif event.outcome_type == TalkOutcomeType.RECRUIT:
            # Handle recruitment outcome
            unit_id_to_recruit = event.outcome_data.get("unit_id_to_recruit")
            new_faction = event.outcome_data.get("new_faction")
            
            if unit_id_to_recruit and new_faction:
                self.unitSystem.change_unit_faction(unit_id_to_recruit, new_faction)
                # Optional: Trigger recruitment dialogue/confirmation message
                # if self.dialogueManager:
                #     self.dialogueManager.start_dialogue("generic_recruitment_confirmation", participants=[self.gameStateManager.get_unit(unit_id_to_recruit)])
        
        elif event.outcome_type == TalkOutcomeType.FLAG:
            # Handle flag outcome
            flag_name = event.outcome_data.get("flag_name")
            flag_value = event.outcome_data.get("flag_value", True)
            
            if flag_name:
                game_state.event_flags[flag_name] = flag_value
        
        elif event.outcome_type == TalkOutcomeType.MULTIPLE:
            # Handle multiple outcomes
            outcomes = event.outcome_data.get("outcomes", [])
            
            for sub_event_data in outcomes:
                # Create a temporary sub-event object
                sub_event = TalkEvent(
                    event_id=event.event_id + "_sub",
                    initiator_unit_id=event.initiator_unit_id,
                    target_unit_id=event.target_unit_id,
                    outcome_type=sub_event_data.outcome_type,
                    outcome_data=sub_event_data.outcome_data,
                    # Other fields not needed for sub-processing
                    is_repeatable=False,
                    max_uses=1,
                    required_conditions=[]
                )
                
                # Process the sub-event
                self.process_talk_outcome(sub_event, initiator, target, game_state)
        
        else:
            logging.error(f"Unknown talk outcome type: {event.outcome_type} for event {event.event_id}")