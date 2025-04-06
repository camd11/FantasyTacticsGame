# Specification: Event System

## 1. Overview

The Event System is responsible for managing and executing scripted events within a chapter based on various conditions. It provides the mechanism for triggering reinforcements, dialogues, map changes, victory/loss conditions, and other dynamic gameplay elements crucial to the Fire Emblem experience, particularly the complex scenarios found in Thracia 776. The system is designed to be data-driven, allowing chapter-specific events to be defined externally.

## 2. Core Concepts

*   **Event:** A container defining a set of conditions and corresponding actions. Events are typically defined per chapter in data files.
*   **Condition:** A specific check that must evaluate to true for an event to trigger. Multiple conditions usually need to be met simultaneously (AND logic).
*   **Action:** An operation performed by the game engine when an event's conditions are met. Multiple actions can be executed sequentially for a single event.
*   **Event Manager:** A central component that loads event definitions for the current chapter, monitors game state, evaluates conditions at appropriate times, and orchestrates the execution of actions.
*   **Trigger Point:** Defines *when* the Event Manager should check the conditions for a specific event (e.g., `StartPlayerPhase`, `EndEnemyPhase`, `AfterUnitAction`, `UnitDeath`). This optimizes performance by avoiding constant checks.
*   **Flags:** Boolean variables stored in the Game State, used to track event occurrences (e.g., preventing repeatable events) or represent narrative states influencing other events.

## 3. Functional Requirements

*   **FR1:** Load chapter-specific event definitions from the Data Provider at the start of a chapter.
*   **FR2:** Monitor game state changes relevant to event conditions (turn number, unit positions, unit deaths, flags, specific actions like Talk/Visit/Seize/Escape).
*   **FR3:** Evaluate event conditions at defined trigger points.
*   **FR4:** Execute the associated actions sequentially if all conditions for an event are met.
*   **FR5:** Support one-time events (using flags to prevent re-triggering).
*   **FR6:** Support repeatable events (if no flag condition is set).
*   **FR7:** Handle event priority if multiple events trigger simultaneously (e.g., chapter end events should likely take precedence).
*   **FR8:** Provide a mechanism for defining various condition types (see Section 5).
*   **FR9:** Provide a mechanism for defining various action types (see Section 6).
*   **FR10:** Integrate with Game State Manager for flag management and state queries.
*   **FR11:** Integrate with other systems (Unit Manager, Map System, UI) to execute actions.
*   **FR12:** Support Thracia 776 specific event patterns like reinforcements at the end of Enemy Phase, Escape map rules (Leif escaping ends chapter, potentially capturing remaining units), Talk/Visit triggers, and location-based triggers.

## 4. Data Structures (Conceptual)

Event data will likely be stored in YAML/JSON files per chapter (e.g., `data/chapters/chapter_id/events.yaml`).

```yaml
# Example Event Definition
events:
  - event_id: UniqueEventIdentifier # e.g., ReinforcementsTurn5South
    trigger_point: EndEnemyPhase # When to check conditions
    repeatable: false # Default: false (uses internal flag or requires explicit SetFlag action)
    conditions: # List of conditions (AND logic)
      - type: TurnNumber
        turn: 5
      # - type: FlagNotSet # Implicit if repeatable=false, or explicit via flag
      #   flag_id: ReinforcementsTurn5Triggered
      # - type: RegionOccupied
      #   region_id: SouthEntranceZone
      #   affiliation: Player
    actions: # List of actions executed sequentially
      - type: SpawnUnit
        unit_template_id: EnemyBrigand
        location: [x, y] # Specific coordinate or region name
        count: 3
        ai_settings: # Optional AI override
          behavior: ChargePlayer
      - type: DisplayMessage
        message_key: ReinforcementAmbushQuote
      # - type: SetFlag # Implicit if repeatable=false
      #   flag_id: ReinforcementsTurn5Triggered
```

## 5. Condition Types

The system must support various condition types, checked at appropriate `trigger_point`s:

*   **`TurnNumber`**: True if the current turn number matches. (Check: StartPlayerPhase, StartEnemyPhase, etc.)
*   **`Phase`**: True if the current phase matches (Player, Enemy, NPC). (Check: StartPhase, EndPhase)
*   **`Location`**: True if a specific unit (by ID or type) is at a specific coordinate or within a defined region. (Check: AfterUnitAction, StartTurn, EndTurn)
*   **`UnitDeath`**: True if a specific unit (by ID or type/affiliation) has died this turn/phase or is currently dead. (Check: AfterCombat, EndPhase)
*   **`FlagSet` / `FlagNotSet`**: True if a specific game state flag is true/false. (Check: Any trigger point)
*   **`TalkBetweenUnits`**: True if a specific pair of units just used the Talk command. (Check: AfterUnitAction)
*   **`VisitLocation`**: True if a unit just visited a specific location (village, house). (Check: AfterUnitAction)
*   **`SeizeLocation`**: True if the Lord unit just used the Seize command on a specific tile. (Check: AfterUnitAction)
*   **`EscapeAction`**: True if a specific unit just used the Escape command. (Check: AfterUnitAction)
*   **`UnitExists`**: True if a specific unit is currently present on the map. (Check: Any trigger point)
*   **`UnitHasItem`**: True if a specific unit possesses a certain item. (Check: Any trigger point)
*   **`UnitsInRegion`**: True if a certain number of units of a specific affiliation are within a defined region. (Check: StartPhase, EndPhase)
*   **`ChapterObjectiveComplete`**: True if the main objective (besides this event) is met (e.g., for triggering epilogues before formal end). (Check: EndPhase)
*   **`IsIndoors` / `IsOutdoors`**: True if the current map type matches. (Check: ChapterStart)

## 6. Action Types

The system must support various actions to be executed:

*   **`SpawnUnit`**: Create and place one or more units on the map. Parameters: unit template ID, location(s), count, initial state (AI, affiliation, level offset).
*   **`DisplayMessage`**: Show dialogue or narrative text to the player. Parameters: message content or ID, associated portrait(s).
*   **`SetFlag` / `ClearFlag`**: Modify a game state flag. Parameters: flag ID.
*   **`EndChapter`**: Terminate the current chapter. Parameters: outcome (Victory, Defeat, GoToGaiden), next chapter ID.
*   **`ChangeTile`**: Modify map terrain (e.g., open a door, destroy a wall, create a bridge). Parameters: location, new tile type.
*   **`GiveItem`**: Add an item to a unit's inventory. Parameters: target unit (triggering unit, specific ID), item ID.
*   **`RemoveItem`**: Remove an item from a unit's inventory. Parameters: target unit, item ID.
*   **`MoveUnit`**: Force a unit to move to a specific location (used for cutscenes). Parameters: unit ID, target location, pathfinding type.
*   **`ChangeUnitAI`**: Modify the AI behavior of one or more units. Parameters: target unit(s), new AI settings.
*   **`ChangeUnitAffiliation`**: Change a unit's side (e.g., recruit NPC, enemy betrays). Parameters: unit ID, new affiliation.
*   **`PlaySound` / `PlayMusic`**: Trigger sound effects or change background music. Parameters: sound/music ID.
*   **`ScreenFade`**: Fade the screen in/out (for transitions). Parameters: direction (in/out), speed, color.
*   **`CameraFocus`**: Move the camera view to a specific location or unit. Parameters: target location/unit ID.
*   **`Wait`**: Pause event execution for a short duration. Parameters: duration (ms or frames).
*   **`MarkUnitsLeftBehind`**: (Thracia Specific) Identify units still on map when Leif escapes and flag them as captured. Parameters: None (operates on current state).
*   **`ModifyUnitStats`**: Temporarily or permanently change a unit's stats (e.g., story promotion). Parameters: unit ID, stat changes, duration.
*   **`HealUnit`**: Restore HP or cure status for a unit. Parameters: unit ID, amount/status type.

## 7. Pseudocode: Event Manager

```pseudocode
CLASS EventManager
    // Properties
    chapter_events: LIST<EventDefinition>
    active_events: LIST<EventInstance> // Events currently being processed
    game_state: GameState // Reference to game state (flags, turn, etc.)
    data_provider: DataProvider // To load event definitions
    action_executor: ActionExecutor // Handles executing specific actions

    // TDD: Test EventManager initialization
    METHOD initialize(game_state, data_provider, action_executor)
        this.game_state = game_state
        this.data_provider = data_provider
        this.action_executor = action_executor
        this.chapter_events = []
        this.active_events = []
    END METHOD

    // TDD: Test loading events for a chapter
    METHOD load_chapter_events(chapter_id)
        this.chapter_events = data_provider.get_events_for_chapter(chapter_id)
        // Initialize internal flags for non-repeatable events if needed
        FOR event_def IN this.chapter_events
            IF NOT event_def.repeatable
                // Ensure a flag exists to track execution, e.g., "event_{event_id}_triggered"
                // game_state.ensure_flag_exists("event_" + event_def.event_id + "_triggered", false)
            END IF
        END FOR
    END METHOD

    // TDD: Test checking events at a specific trigger point
    METHOD check_events(trigger_point, context) // context contains relevant data like unit_id, location, etc.
        triggered_events = []
        FOR event_def IN this.chapter_events
            IF event_def.trigger_point == trigger_point
                IF check_conditions(event_def, context)
                    // Check if already triggered (for non-repeatable)
                    IF event_def.repeatable OR NOT game_state.get_flag("event_" + event_def.event_id + "_triggered")
                        triggered_events.APPEND(event_def)
                    END IF
                END IF
            END IF
        END FOR

        // Handle priority if needed (e.g., EndChapter first)
        // Sort triggered_events based on priority rules

        FOR event_def IN triggered_events
            execute_event(event_def, context)
            IF NOT event_def.repeatable
                game_state.set_flag("event_" + event_def.event_id + "_triggered", true)
            END IF
        END FOR
    END METHOD

    // TDD: Test condition checking logic for various condition types
    PRIVATE METHOD check_conditions(event_def, context)
        FOR condition IN event_def.conditions
            result = evaluate_condition(condition, context)
            IF NOT result
                RETURN false // AND logic: all conditions must pass
            END IF
        END FOR
        RETURN true
    END METHOD

    // TDD: Test individual condition evaluation (mock game state)
    PRIVATE METHOD evaluate_condition(condition, context)
        // Delegate to specific condition checker based on condition.type
        // Example:
        IF condition.type == "TurnNumber"
            RETURN game_state.current_turn == condition.turn
        ELSE IF condition.type == "FlagSet"
            RETURN game_state.get_flag(condition.flag_id) == true
        ELSE IF condition.type == "Location"
            // Check unit position from context or game_state
            RETURN check_unit_location(condition.unit_id, condition.location)
        // ... other condition types
        ELSE
            log_warning("Unsupported condition type: " + condition.type)
            RETURN false
        END IF
    END METHOD

    // TDD: Test event execution flow (mock action executor)
    PRIVATE METHOD execute_event(event_def, context)
        log_info("Executing event: " + event_def.event_id)
        // Could create an EventInstance and add to active_events for complex/timed events
        FOR action IN event_def.actions
            action_executor.execute(action, context) // ActionExecutor handles the specifics
        END FOR
    END METHOD

END CLASS

CLASS ActionExecutor
    // References to other game systems (UnitManager, MapSystem, UIManager, GameStateManager)

    // TDD: Test execution of each action type (mock game systems)
    METHOD execute(action, context)
        // Delegate to specific action handler based on action.type
        // Example:
        IF action.type == "SpawnUnit"
            unit_manager.spawn_unit(action.unit_template_id, action.location, ...)
        ELSE IF action.type == "DisplayMessage"
            ui_manager.show_dialogue(action.message_key, ...)
        ELSE IF action.type == "SetFlag"
            game_state_manager.set_flag(action.flag_id, true)
        ELSE IF action.type == "EndChapter"
            game_state_manager.end_chapter(action.outcome, action.next_chapter_id)
        ELSE IF action.type == "MarkUnitsLeftBehind"
            // Thracia specific logic
            units_left = unit_manager.get_player_units_on_map()
            FOR unit IN units_left
                IF unit.id != "Leif" // Assuming Leif is the one escaping
                    unit_manager.set_unit_status(unit.id, "CapturedLeftBehind")
                    log_info("Unit left behind: " + unit.id)
                END IF
            END FOR
        // ... other action types
        ELSE
            log_warning("Unsupported action type: " + action.type)
        END IF
    END METHOD
END CLASS

// --- Condition Evaluation Helper Functions (Examples) ---

// TDD: Test check_unit_location function
FUNCTION check_unit_location(unit_id, location_condition)
    unit = unit_manager.get_unit(unit_id)
    IF unit IS NULL OR NOT unit.is_on_map
        RETURN false
    END IF

    IF location_condition is Coordinate
        RETURN unit.position == location_condition
    ELSE IF location_condition is RegionID
        region_tiles = map_system.get_region_tiles(location_condition)
        RETURN unit.position IN region_tiles
    END IF
    RETURN false
END FUNCTION

// TDD: Test check_talk_condition function
FUNCTION check_talk_condition(condition, context)
    IF context.action_type != "Talk"
        RETURN false
    END IF
    RETURN context.talker_id == condition.talker_id AND context.listener_id == condition.listener_id
END FUNCTION

// ... other helper functions for evaluating conditions
```

## 8. Integration Points

*   **Game Loop:** The `EventManager.check_events` method needs to be called at appropriate points in the main game loop (e.g., start/end of phases, after unit actions).
*   **Game State Manager:** Provides access to turn number, phase info, flags, and chapter objectives. Receives commands to set/clear flags and end the chapter.
*   **Data Provider:** Loads event definitions (`events.yaml`) for the current chapter.
*   **Unit Manager:** Queried for unit positions, status, deaths, affiliations. Receives commands to spawn, move, modify, or remove units.
*   **Map System:** Queried for region definitions and tile types. Receives commands to change tiles.
*   **UI Manager:** Receives commands to display messages, focus camera, fade screen.
*   **Combat System:** May notify the Event Manager upon unit death.
*   **Input Handler:** May notify the Event Manager when specific commands (Talk, Visit, Seize, Escape) are performed.

## 9. Thracia 776 Considerations

*   **Reinforcement Timing:** Ensure `EndEnemyPhase` trigger point works correctly, spawning units *after* all enemies have moved but *before* the next phase starts.
*   **Escape Rule:** The `MarkUnitsLeftBehind` action is crucial for Escape maps. It must be triggered specifically by Leif's Escape action and correctly identify/flag remaining player units.
*   **Capture Recruitment:** Some events might change an enemy's affiliation to Player if they are captured and specific flags are set (e.g., capturing Shiva). This requires conditions checking unit status (Captured) and flags.
*   **Talk/Visit Events:** These are common triggers and need reliable checking via the `AfterUnitAction` trigger point and appropriate conditions (`TalkBetweenUnits`, `VisitLocation`).
*   **Fatigue:** While not directly an event *trigger*, events *could* modify fatigue (e.g., a special action reducing fatigue), although the primary mechanism is handled by the Fatigue System itself.
*   **Gaiden Chapter Logic:** The `EndChapter` action needs to support branching to a Gaiden chapter based on flags set by preceding events/actions.

## 10. Future Considerations / Edge Cases

*   **Event Conflicts:** Define clear priority rules if multiple events trigger simultaneously. Chapter End events should generally have the highest priority.
*   **Performance:** For maps with many events or complex conditions, optimize condition checking, especially location/region checks. Use trigger points effectively.
*   **Event Debugging:** Implement logging and potentially in-game tools to visualize event states and triggers for easier debugging.
*   **Complex Event Chains:** Consider if events need to trigger other events directly or if flag-setting is sufficient for chaining.
*   **Mid-Action Triggers:** Are there events that need to trigger *during* an action (e.g., stepping on a trap tile mid-movement)? Current design focuses on triggers *after* actions or at phase boundaries. Mid-action triggers would require finer-grained checks.