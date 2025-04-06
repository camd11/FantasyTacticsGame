# Specification: Event Handler (`EventHandler`)

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The `EventHandler` manages scripted events within a chapter. It monitors the game state for specific trigger conditions (e.g., reaching a certain turn, a unit moving to a specific tile, a 'Talk' action occurring between specific units) and executes predefined sequences of actions (e.g., displaying dialogue, spawning reinforcements, giving items, changing unit AI, modifying the map, setting game flags, ending the chapter).

## 2. Responsibilities

-   Load chapter-specific event data at the start of a chapter.
-   Continuously monitor the game state for event trigger conditions.
-   Check for events triggered by:
    -   Turn number (start/end of specific turns).
    -   Phase start/end.
    -   Unit location (entering/standing on specific tiles/regions).
    -   Unit actions (Visit, Talk, Seize, potentially others).
    -   Combat outcomes (e.g., a specific unit defeating another).
    -   Unit death/escape.
    -   Game state flags being set/unset.
-   Validate event conditions before execution (e.g., required unit is alive, flag is set).
-   Execute the sequence of actions defined for a triggered event:
    -   Display dialogue boxes with portraits.
    -   Spawn new units (player, enemy, NPC) at specified locations.
    -   Give items or gold (if applicable) to units.
    -   Change unit properties (AI behavior, faction, stats).
    -   Modify map state (open doors, change terrain, reveal areas).
    -   Set/unset global or chapter-specific flags (e.g., for Gaiden chapter requirements).
    -   Initiate chapter end (victory/loss).
    -   Move units programmatically (cutscenes).
-   Manage event persistence (e.g., ensuring an event only triggers once unless specified otherwise).
-   Coordinate with other systems to query state and execute actions (`GameStateManager`, `UnitSystem`, `MapSystem`, `InventorySystem`, `TurnManager`, `AIManager`).

## 3. Dependencies

-   `GameStateManager`: To query current game state (turn, phase, flags) and potentially update flags or trigger chapter end.
-   `TurnManager`: To get current turn and phase information.
-   `UnitSystem`: To get unit data (ID, position, faction, status, stats), spawn units, change unit properties, check unit existence/status.
-   `MapSystem`: To check unit locations, get tile/feature data, modify map state.
-   `InventorySystem`: To give items to units.
-   `DataProvider`: To load event definitions for the current chapter.
-   `UIManager` (Conceptual): To display dialogue boxes, cutscenes, and other visual event elements.
-   `AIManager` (Conceptual): To change AI behavior of units as part of an event.

## 4. Core Concepts

-   **Event:** A predefined sequence of actions triggered by specific conditions.
-   **Trigger:** The specific condition that causes an event check to occur (e.g., `TURN_START`, `UNIT_MOVE`, `ACTION_TALK`).
-   **Condition:** Additional requirements that must be met for a triggered event to actually execute (e.g., `UNIT_ALIVE('Leif')`, `FLAG_IS_SET('Village_Saved')`).
-   **Action:** A single step within an event sequence (e.g., `SHOW_DIALOGUE(...)`, `SPAWN_UNIT(...)`, `GIVE_ITEM(...)`).
-   **Event Data:** Structured data defining all events for a chapter, including triggers, conditions, and actions. Loaded at chapter start.
-   **Event Flags:** Boolean variables stored in the game state used to track event progress or conditions across turns/events (e.g., `has_visited_shrine`, `gaiden_chapter_unlocked`).

## 5. Pseudocode

```pseudocode
class EventHandler:
    // Dependencies
    gameStateManager: GameStateManager
    turnManager: TurnManager
    unitSystem: UnitSystem
    mapSystem: MapSystem
    inventorySystem: InventorySystem
    dataProvider: DataProvider
    uiManager: UIManager // For displaying dialogue, etc.
    aiManager: AIManager // For changing AI

    // State
    chapterEvents: List[EventData] = []
    activeEventFlags: Set[String] = {} // Flags set during the current chapter

    // TDD Anchor: test_event_handler_initialization_and_load
    function initialize(chapter_id: String):
        // Load event definitions for the chapter
        chapterEvents = dataProvider.get_chapter_event_data(chapter_id)
        // Load initial flags from game state
        activeEventFlags = gameStateManager.get_active_flags()
        print("EventHandler initialized for chapter ", chapter_id, " with ", chapterEvents.size, " event definitions.")

    // --- Event Checking Methods ---
    // Called by TurnManager or main loop

    // TDD Anchor: test_check_turn_events_trigger_correctly
    function check_turn_events(turn: Integer, phase: Phase):
        triggerType = None
        if phase == Phase.PLAYER: // Assuming turn events trigger at Player Phase start
             triggerType = EventTrigger.TURN_START
        // Or potentially PHASE_START, PHASE_END triggers

        if triggerType:
            find_and_execute_events(triggerType, {'turn': turn, 'phase': phase})

    // TDD Anchor: test_check_location_events_trigger_on_move
    function check_location_events(unit_id: String, new_position: Coordinate):
        triggerData = {'unit_id': unit_id, 'position': new_position}
        find_and_execute_events(EventTrigger.LOCATION_ENTER, triggerData)
        find_and_execute_events(EventTrigger.LOCATION_STAND, triggerData) // If events trigger by standing

    // TDD Anchor: test_check_action_events_trigger_talk_visit_seize
    // Called potentially by ActionHandler after successful action
    function check_action_event(action_type: ActionType, unit_id: String, target_data: Dict):
        triggerType = None
        triggerData = {'unit_id': unit_id, **target_data} // Combine data

        match action_type:
            case ActionType.TALK:
                triggerType = EventTrigger.ACTION_TALK
            case ActionType.VISIT:
                triggerType = EventTrigger.ACTION_VISIT
            case ActionType.SEIZE:
                triggerType = EventTrigger.ACTION_SEIZE
            // Add other actions if they trigger events

        if triggerType:
            find_and_execute_events(triggerType, triggerData)

    // TDD Anchor: test_check_death_event_triggers
    function check_death_event(unit_id: String):
         find_and_execute_events(EventTrigger.UNIT_DEATH, {'unit_id': unit_id})

    // --- Core Event Logic ---

    // TDD Anchor: test_find_and_execute_events_filters_correctly
    function find_and_execute_events(trigger: EventTrigger, context: Dict):
        triggeredEvents = []
        for event in chapterEvents:
            if event.has_triggered and not event.is_repeatable:
                continue // Already triggered

            if event.trigger == trigger:
                // Check specific trigger conditions (e.g., turn number matches context['turn'])
                if check_trigger_details(event, context):
                    // Check additional conditions (unit alive, flags set, etc.)
                    if check_event_conditions(event.conditions, context):
                        triggeredEvents.append(event)

        // Sort events by priority if needed
        // triggeredEvents.sort(key=lambda e: e.priority)

        for event in triggeredEvents:
            execute_event(event, context)
            event.has_triggered = True // Mark as triggered

    // TDD Anchor: test_check_trigger_details_match_context
    function check_trigger_details(event: EventData, context: Dict) -> Boolean:
        match event.trigger:
            case EventTrigger.TURN_START:
                return event.trigger_params['turn'] == context['turn']
            case EventTrigger.LOCATION_ENTER | EventTrigger.LOCATION_STAND:
                # Check if context['position'] matches event.trigger_params['location'] (tile or region)
                # Check if context['unit_id'] matches event.trigger_params['unit_id'] (if specific unit)
                return mapSystem.is_location_match(context['position'], event.trigger_params['location']) and \
                       (event.trigger_params.get('unit_id') is None or event.trigger_params['unit_id'] == context['unit_id'])
            case EventTrigger.ACTION_TALK:
                # Check if context['unit_id'] and context['target_unit_id'] match event params
                return (event.trigger_params['talker_id'] == context['unit_id'] and \
                        event.trigger_params['listener_id'] == context['target_unit_id']) or \
                       (event.trigger_params['talker_id'] == context['target_unit_id'] and \
                        event.trigger_params['listener_id'] == context['unit_id']) # Allow either direction
            case EventTrigger.ACTION_VISIT:
                 # Check if context['unit_id'] matches and context['target_tile'] matches
                 return event.trigger_params['visitor_id'] == context['unit_id'] and \
                        event.trigger_params['location'] == context['target_tile']
            case EventTrigger.ACTION_SEIZE:
                 # Check if context['unit_id'] (must be Lord) matches and context['target_tile'] matches
                 return unitSystem.is_lord(context['unit_id']) and \
                        event.trigger_params['location'] == context['target_tile']
            case EventTrigger.UNIT_DEATH:
                 return event.trigger_params['unit_id'] == context['unit_id']
            // ... other triggers
            case _:
                return False

    // TDD Anchor: test_check_event_conditions_evaluates_correctly
    function check_event_conditions(conditions: List[EventCondition], context: Dict) -> Boolean:
        for condition in conditions:
            match condition.type:
                case ConditionType.UNIT_ALIVE:
                    if not unitSystem.is_unit_alive(condition.params['unit_id']): return False
                case ConditionType.FLAG_SET:
                    if condition.params['flag_name'] not in activeEventFlags: return False
                case ConditionType.FLAG_NOT_SET:
                    if condition.params['flag_name'] in activeEventFlags: return False
                case ConditionType.UNIT_HAS_ITEM:
                    if not inventorySystem.has_item(condition.params['unit_id'], condition.params['item_type']): return False
                // ... other conditions (unit in region, specific stats, etc.)
                case _:
                    print("Warning: Unknown condition type: ", condition.type)
                    return False // Fail safe on unknown condition
        return True // All conditions passed

    // TDD Anchor: test_execute_event_performs_actions
    function execute_event(event: EventData, context: Dict):
        print("Executing Event: ", event.id)
        for action in event.actions:
            execute_event_action(action, context)

    // TDD Anchor: test_execute_event_action_handles_all_types
    function execute_event_action(action: EventAction, context: Dict):
        match action.type:
            case ActionType.SHOW_DIALOGUE:
                uiManager.show_dialogue(action.params['dialogue_id'], action.params.get('speaker_unit_id'))
            case ActionType.SPAWN_UNIT:
                unitSystem.spawn_unit(action.params['unit_data'], action.params['location'], action.params.get('ai_override'))
            case ActionType.GIVE_ITEM:
                inventorySystem.give_item(action.params['recipient_unit_id'], action.params['item_type'])
            case ActionType.SET_FLAG:
                flag_name = action.params['flag_name']
                activeEventFlags.add(flag_name)
                gameStateManager.set_flag(flag_name) # Persist flag if needed globally
            case ActionType.CLEAR_FLAG:
                 flag_name = action.params['flag_name']
                 activeEventFlags.discard(flag_name)
                 gameStateManager.clear_flag(flag_name)
            case ActionType.CHANGE_AI:
                 aiManager.change_unit_ai(action.params['unit_id'], action.params['new_ai_profile'])
            case ActionType.MODIFY_MAP:
                 mapSystem.modify_tile(action.params['location'], action.params['new_tile_type'])
            case ActionType.MOVE_UNIT:
                 # Animate unit moving along a path
                 movementSystem.execute_scripted_move(action.params['unit_id'], action.params['path'])
            case ActionType.END_CHAPTER:
                 gameStateManager.end_chapter(action.params.get('outcome', 'victory'))
            // ... other actions (change faction, add status effect, play sound/music)
            case _:
                print("Warning: Unknown event action type: ", action.type)

    // --- Public helpers for ActionHandler ---

    // TDD Anchor: test_has_talk_event_finds_existing
    function has_talk_event(unit1_id: String, unit2_id: String) -> Boolean:
        for event in chapterEvents:
            if event.trigger == EventTrigger.ACTION_TALK:
                 # Check if this pair matches the event params (either direction)
                 p = event.trigger_params
                 if (p['talker_id'] == unit1_id and p['listener_id'] == unit2_id) or \
                    (p['talker_id'] == unit2_id and p['listener_id'] == unit1_id):
                     # Check if conditions are currently met (optional, maybe check later)
                     # if check_event_conditions(event.conditions, {'unit_id': unit1_id, 'target_unit_id': unit2_id}):
                     return True # Found a potential talk event
        return False

    // TDD Anchor: test_trigger_talk_event_executes
    function trigger_talk_event(unit1_id: String, unit2_id: String) -> Boolean:
        # Called by ActionHandler after confirming adjacency and talk command
        context = {'unit_id': unit1_id, 'target_unit_id': unit2_id}
        # Find the specific event again and execute it
        for event in chapterEvents:
             if event.trigger == EventTrigger.ACTION_TALK:
                 p = event.trigger_params
                 if (p['talker_id'] == unit1_id and p['listener_id'] == unit2_id) or \
                    (p['talker_id'] == unit2_id and p['listener_id'] == unit1_id):
                      if check_event_conditions(event.conditions, context):
                          execute_event(event, context)
                          event.has_triggered = True
                          return True # Event executed
        return False # Should not happen if has_talk_event was true and conditions met

    // Similar public helpers for trigger_map_event (Visit, Seize) may be needed

end class

// --- Data Structures ---

enum EventTrigger:
    TURN_START, PHASE_START, PHASE_END, LOCATION_ENTER, LOCATION_STAND,
    ACTION_VISIT, ACTION_TALK, ACTION_SEIZE, ACTION_ATTACK, // etc.
    UNIT_DEATH, FLAG_SET_EXTERNALLY

enum ConditionType:
    UNIT_ALIVE, UNIT_DEAD, FLAG_SET, FLAG_NOT_SET, UNIT_IN_REGION,
    UNIT_HAS_ITEM, TURN_GE, TURN_LE, RANDOM_CHANCE

enum EventActionType:
    SHOW_DIALOGUE, SPAWN_UNIT, GIVE_ITEM, SET_FLAG, CLEAR_FLAG, CHANGE_AI,
    MODIFY_MAP, MOVE_UNIT, END_CHAPTER, PLAY_SOUND, PLAY_MUSIC, CHANGE_FACTION

class EventData:
    id: String // Unique identifier for the event
    trigger: EventTrigger
    trigger_params: Dict // e.g., {'turn': 5}, {'location': Coordinate(10, 5)}, {'talker_id': 'Leif', 'listener_id': 'Finn'}
    conditions: List[EventCondition] // Additional conditions to check
    actions: List[EventAction] // Sequence of actions to perform
    priority: Integer = 0 // For resolving simultaneous events
    is_repeatable: Boolean = False
    has_triggered: Boolean = False // Runtime state

class EventCondition:
    type: ConditionType
    params: Dict // e.g., {'unit_id': 'Leif'}, {'flag_name': 'Village_Saved'}

class EventAction:
    type: EventActionType
    params: Dict // e.g., {'dialogue_id': 'CH1_INTRO'}, {'unit_data': {...}, 'location': ...}

```

## 6. Data Structures

-   `EventData`: Represents a single event definition, containing trigger, conditions, actions, and metadata.
-   `EventTrigger` Enum: Defines the types of triggers that can initiate an event check.
-   `EventCondition`: Defines a specific condition that must be true for an event to execute.
-   `ConditionType` Enum: Types of conditions (e.g., `UNIT_ALIVE`, `FLAG_SET`).
-   `EventAction`: Defines a single action performed during an event sequence.
-   `EventActionType` Enum: Types of actions (e.g., `SHOW_DIALOGUE`, `SPAWN_UNIT`).
-   `activeEventFlags`: A set holding the names of flags currently active in the chapter state.

## 7. Edge Cases & Considerations

-   **Event Priority:** If multiple events trigger simultaneously (e.g., two location triggers on the same move), a priority system might be needed to determine execution order.
-   **Event Atomicity:** Should event actions be atomic? If one action fails (e.g., inventory full when giving an item), should the rest of the event sequence continue or halt?
-   **Repeatable Events:** Some events might need to trigger multiple times (e.g., a trap that resets). The `is_repeatable` flag handles this.
-   **Condition Checking Timing:** When should complex conditions be checked? Checking only when the trigger occurs might miss changes that happen between the trigger and execution. Checking right before execution is safer.
-   **Performance:** Continuously checking location triggers for every unit move could be performance-intensive on large maps with many events. Optimization might be needed (e.g., spatial partitioning).
-   **Loading/Saving State:** Event state (which events have triggered, active flags) needs to be saved and loaded correctly with the game state (especially for suspend/resume).
-   **Gaiden Chapter Logic:** Setting flags for Gaiden chapters needs careful implementation. The check for unlocking the Gaiden chapter likely happens *after* the main chapter ends, based on flags set by the `EventHandler` during the chapter.
-   **Cutscene Control:** Complex cutscenes involving multiple unit movements, dialogues, and camera controls require a robust event action system.

## 8. Future Enhancements

-   Support for region-based triggers (not just single tiles).
-   More sophisticated condition logic (AND/OR combinations).
-   Visual event editor integration.
-   Support for conditional branching within an event action sequence.
-   Integration with a dedicated Cutscene Manager for complex sequences.
-   Event logging/debugging tools.