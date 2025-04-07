# Specification: Talk System

## 1. Overview

The Talk System manages special conversations and interactions between specific units on the battlefield map. These interactions can trigger various outcomes, such as dialogue display, item acquisition, unit recruitment, or setting game state flags. It integrates with the Unit, Action, Event, Dialogue, Inventory, and UI systems.

## 2. Data Structures

### 2.1. Talk Event Definition

```pseudocode
// Defined within Scenario/Chapter Data (e.g., loaded by ScenarioLoader)
// TDD_ANCHOR: test_talk_event_data_loading
TalkEvent {
  event_id: String // Unique identifier for this talk event
  initiator_unit_id: String // ID of the unit that must initiate the talk
  target_unit_id: String // ID of the unit that must be the target
  required_conditions: List<Condition> // Optional: Additional conditions (e.g., game flag set, specific turn)
  is_repeatable: Boolean // Can this talk event occur multiple times? (Default: False)
  max_uses: Integer // If repeatable, how many times? (Default: 1)
  outcome_type: Enum // Type of outcome (DIALOGUE, ITEM, RECRUIT, FLAG, MULTIPLE)
  outcome_data: Dictionary // Data specific to the outcome type
    // Example for DIALOGUE: { dialogue_id: "ch1_leif_dagdar_talk" }
    // Example for ITEM: { item_id: "Vouge", quantity: 1 }
    // Example for RECRUIT: { unit_id_to_recruit: "Dagdar", new_faction: "Player" }
    // Example for FLAG: { flag_name: "dagdar_talked_to", flag_value: true }
    // Example for MULTIPLE: { outcomes: List<OutcomeSubEvent> } // Where OutcomeSubEvent has type/data
  // TDD_ANCHOR: test_talk_event_definition_parsing
}

Condition {
  type: Enum // e.g., FLAG_CHECK, TURN_CHECK, UNIT_STATUS_CHECK
  data: Dictionary // e.g., { flag_name: "event_started", expected_value: true }, { min_turn: 5, max_turn: 10 }
}

OutcomeSubEvent {
  outcome_type: Enum // As above, but cannot be MULTIPLE
  outcome_data: Dictionary // As above
}
```

### 2.2. Active Talk State (Runtime)

```pseudocode
// Managed potentially by GameState or ScenarioManager
ActiveTalkState {
  talk_event_uses: Dictionary<event_id, current_uses: Integer> // Tracks uses for repeatable events
  completed_talk_events: Set<event_id> // Tracks completed non-repeatable events for the current map/scenario
  // TDD_ANCHOR: test_active_talk_state_tracking
}
```

## 3. Core Logic Modules

### 3.1. Talk Eligibility Checker (`TalkSystem.can_initiate_talk`)

```pseudocode
// Checks if a selected unit can initiate a talk with an adjacent target unit.
// TDD_ANCHOR: test_can_initiate_talk_eligibility
FUNCTION can_initiate_talk(selected_unit: Unit, target_unit: Unit, current_game_state: GameState): Boolean

  // 1. Basic Checks
  IF NOT selected_unit OR NOT target_unit THEN RETURN FALSE
  IF selected_unit.faction IS NOT "Player" THEN RETURN FALSE // Only player units initiate standard talks
  IF NOT MapSystem.are_units_adjacent(selected_unit.position, target_unit.position) THEN RETURN FALSE
  IF ActionSystem.has_unit_acted_or_waited(selected_unit.id) THEN RETURN FALSE // Unit must not have finished their turn

  // 2. Find Matching Talk Events
  // TDD_ANCHOR: test_find_matching_talk_events
  possible_events = ScenarioLoader.get_talk_events_for_pair(selected_unit.id, target_unit.id)
  IF possible_events IS EMPTY THEN RETURN FALSE

  // 3. Check Event Conditions and Usage Limits
  // TDD_ANCHOR: test_talk_event_condition_checking
  FOR event IN possible_events:
    // Check if already completed (non-repeatable)
    IF NOT event.is_repeatable AND current_game_state.ActiveTalkState.completed_talk_events.contains(event.event_id) THEN CONTINUE

    // Check usage limits (repeatable)
    IF event.is_repeatable:
      current_uses = current_game_state.ActiveTalkState.talk_event_uses.get(event.event_id, 0)
      IF current_uses >= event.max_uses THEN CONTINUE

    // Check specific conditions (flags, turn number, etc.)
    // TDD_ANCHOR: test_talk_event_specific_conditions
    all_conditions_met = TRUE
    FOR condition IN event.required_conditions:
      IF NOT check_condition(condition, current_game_state) THEN
        all_conditions_met = FALSE
        BREAK
    IF NOT all_conditions_met THEN CONTINUE

    // If we reach here, at least one valid talk event exists
    RETURN TRUE

  // No valid, available talk events found for this pair under current conditions
  RETURN FALSE

ENDFUNCTION

FUNCTION check_condition(condition: Condition, game_state: GameState): Boolean
  // Implementation depends on condition types (e.g., check FlagSystem, TurnManager)
  // TDD_ANCHOR: test_talk_condition_evaluation
  CASE condition.type:
    WHEN FLAG_CHECK:
      RETURN FlagSystem.get_flag(condition.data.flag_name) == condition.data.expected_value
    WHEN TURN_CHECK:
      current_turn = TurnManager.get_current_turn()
      RETURN current_turn >= condition.data.min_turn AND current_turn <= condition.data.max_turn
    // ... other condition types
    DEFAULT:
      RETURN FALSE
  ENDCASE
ENDFUNCTION
```

### 3.2. Talk Initiator (`TalkSystem.initiate_talk`)

```pseudocode
// Executes the talk action, consuming the unit's turn and triggering the outcome.
// TDD_ANCHOR: test_initiate_talk_execution
FUNCTION initiate_talk(selected_unit: Unit, target_unit: Unit, current_game_state: GameState)

  // 1. Find the specific event to trigger (assuming UI allows selection if multiple are possible, or takes the first valid one)
  // TDD_ANCHOR: test_select_talk_event_to_trigger
  valid_event = find_first_valid_talk_event(selected_unit, target_unit, current_game_state) // Uses logic similar to can_initiate_talk
  IF NOT valid_event THEN
    Log.error("Attempted to initiate talk, but no valid event found.")
    RETURN // Should not happen if can_initiate_talk was checked first

  // 2. Consume Action
  // TDD_ANCHOR: test_talk_consumes_action
  ActionSystem.mark_unit_action_taken(selected_unit.id)
  // NOTE: Based on research.md line 51, non-combat actions like trade/rescue allow Canto.
  // However, Talk feels more significant like Attack. Assume Talk consumes the action fully and does NOT allow Canto unless specified otherwise.
  // If Canto *is* allowed after Talk: ActionSystem.mark_unit_action_taken(selected_unit.id, allows_canto=True)

  // 3. Process Outcome
  // TDD_ANCHOR: test_talk_outcome_processing
  process_talk_outcome(valid_event, selected_unit, target_unit, current_game_state)

  // 4. Update Talk State Tracking
  // TDD_ANCHOR: test_update_talk_state_after_execution
  IF NOT valid_event.is_repeatable:
    current_game_state.ActiveTalkState.completed_talk_events.add(valid_event.event_id)
  ELSE:
    current_uses = current_game_state.ActiveTalkState.talk_event_uses.get(valid_event.event_id, 0)
    current_game_state.ActiveTalkState.talk_event_uses[valid_event.event_id] = current_uses + 1

ENDFUNCTION

FUNCTION find_first_valid_talk_event(initiator: Unit, target: Unit, game_state: GameState): TalkEvent OR Null
  // Similar logic to can_initiate_talk, but returns the actual event object
  possible_events = ScenarioLoader.get_talk_events_for_pair(initiator.id, target.id)
  FOR event IN possible_events:
    // Check usage limits and conditions again (robustness)
    IF NOT event.is_repeatable AND game_state.ActiveTalkState.completed_talk_events.contains(event.event_id) THEN CONTINUE
    IF event.is_repeatable:
      current_uses = game_state.ActiveTalkState.talk_event_uses.get(event.event_id, 0)
      IF current_uses >= event.max_uses THEN CONTINUE
    all_conditions_met = TRUE
    FOR condition IN event.required_conditions:
      IF NOT check_condition(condition, game_state) THEN
        all_conditions_met = FALSE
        BREAK
    IF all_conditions_met THEN RETURN event
  RETURN Null
ENDFUNCTION
```

### 3.3. Outcome Processor (`TalkSystem.process_talk_outcome`)

```pseudocode
// Handles the consequences of a talk event based on its type.
// TDD_ANCHOR: test_process_talk_outcome_dispatch
FUNCTION process_talk_outcome(event: TalkEvent, initiator: Unit, target: Unit, game_state: GameState)

  CASE event.outcome_type:
    WHEN DIALOGUE:
      // TDD_ANCHOR: test_talk_outcome_dialogue
      dialogue_id = event.outcome_data.dialogue_id
      DialogueSystem.start_dialogue(dialogue_id, participants=[initiator, target])
    WHEN ITEM:
      // TDD_ANCHOR: test_talk_outcome_item
      item_id = event.outcome_data.item_id
      quantity = event.outcome_data.quantity
      // Determine recipient (usually initiator, but could be specified)
      recipient_unit = initiator // Default
      // IF event.outcome_data.recipient_id: recipient_unit = UnitSystem.get_unit(event.outcome_data.recipient_id)
      success = InventorySystem.add_item_to_unit(recipient_unit.id, item_id, quantity)
      IF NOT success:
        Log.warning(f"Failed to add item {item_id} from talk event {event.event_id} to unit {recipient_unit.id} (inventory full?).")
        // Handle fallback? Send to convoy? Display message?
    WHEN RECRUIT:
      // TDD_ANCHOR: test_talk_outcome_recruit
      unit_id_to_recruit = event.outcome_data.unit_id_to_recruit
      new_faction = event.outcome_data.new_faction // e.g., "Player"
      UnitSystem.change_unit_faction(unit_id_to_recruit, new_faction)
      // Optional: Trigger recruitment dialogue/confirmation message
      // DialogueSystem.start_dialogue("generic_recruitment_confirmation", participants=[UnitSystem.get_unit(unit_id_to_recruit)])
    WHEN FLAG:
      // TDD_ANCHOR: test_talk_outcome_flag
      flag_name = event.outcome_data.flag_name
      flag_value = event.outcome_data.flag_value
      FlagSystem.set_flag(flag_name, flag_value)
    WHEN MULTIPLE:
      // TDD_ANCHOR: test_talk_outcome_multiple
      FOR sub_event_data IN event.outcome_data.outcomes:
        // Create a temporary sub-event object to pass to this function recursively (or handle inline)
        sub_event = TalkEvent { // Simplified structure for recursion/handling
          outcome_type: sub_event_data.outcome_type,
          outcome_data: sub_event_data.outcome_data
          // Other fields not needed for sub-processing
        }
        process_talk_outcome(sub_event, initiator, target, game_state) // Recursive call or inline handling
    DEFAULT:
      Log.error(f"Unknown talk outcome type: {event.outcome_type} for event {event.event_id}")
  ENDCASE

ENDFUNCTION
```

## 4. Integration Points

*   **UI System:**
    *   When a player unit is selected and the cursor is over an adjacent unit, call `TalkSystem.can_initiate_talk`.
    *   If `True`, display the "Talk" command in the unit's action menu.
    *   If multiple talk events are possible between the pair, the UI might need to present a choice or default to the first valid one.
    *   On selecting "Talk", call `TalkSystem.initiate_talk`.
*   **Action System:**
    *   `TalkSystem` calls `ActionSystem.mark_unit_action_taken` to consume the unit's action.
    *   `ActionSystem.has_unit_acted_or_waited` is checked by `TalkSystem` to prevent talking after acting.
*   **Scenario Loader / Event System:**
    *   Loads `TalkEvent` definitions as part of chapter/scenario data.
    *   Provides `get_talk_events_for_pair` to retrieve potential events.
    *   May be involved in checking complex conditions or triggering chained events post-talk.
*   **Unit System:**
    *   Provides unit data (ID, position, faction, stats).
    *   Called by `TalkSystem` via `change_unit_faction` for recruitment outcomes.
*   **Dialogue System:**
    *   Called by `TalkSystem` via `start_dialogue` for dialogue outcomes.
*   **Inventory System:**
    *   Called by `TalkSystem` via `add_item_to_unit` for item outcomes.
*   **Flag System:**
    *   Called by `TalkSystem` via `set_flag` for flag outcomes.
    *   Checked by `TalkSystem` via `get_flag` for condition evaluation.
*   **Map System:**
    *   Called by `TalkSystem` via `are_units_adjacent` for eligibility checks.
*   **Game State / Scenario Manager:**
    *   Holds the `ActiveTalkState` (usage counts, completed events).

## 5. AI Considerations

*   Standard enemy AI typically does not initiate 'Talk' actions.
*   Specific scripted events or unique NPC AI routines might trigger talk-like interactions.
    *   Example: An allied NPC (green unit) might have an AI goal to move adjacent to a specific player unit (e.g., Leif) and then trigger a specific event (which could be defined similarly to a TalkEvent but initiated by AI logic).
    *   `AIManager` could potentially call a function like `TalkSystem.trigger_scripted_talk(npc_unit, player_unit, event_id)` if conditions are met by AI.
    *   This requires specific AI scripting capabilities beyond standard attack/move logic.
    *   // TDD_ANCHOR: test_ai_triggered_talk_event

## 6. Edge Cases & Considerations

*   **Multiple Valid Talks:** If multiple distinct `TalkEvent` definitions exist for the same pair under current conditions (e.g., one for recruitment, one for an item), how does the UI handle selection? (Assume first valid found, or UI presents choice).
*   **Inventory Full:** What happens if an item outcome occurs but the recipient's inventory is full? (Log warning, potentially send to convoy if available, display message to player).
*   **Target Dies/Moves:** What happens if the target unit moves away or dies between the player selecting 'Talk' and confirming the action? (The action should fail or become invalid). `initiate_talk` should re-validate adjacency and target existence.
*   **Repeatable Talks:** Ensure `ActiveTalkState` correctly tracks uses per map/scenario. Does the count reset between maps? (Assume yes, state is per-map).
*   **Conditional Talks:** Ensure `check_condition` handles various game states correctly (flags, turn numbers, unit status like 'is_captured').
*   **Talk after Canto:** Confirm if Canto is allowed after Talk. Current assumption is NO. If yes, update `ActionSystem.mark_unit_action_taken` call.