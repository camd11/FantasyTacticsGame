# Specification: Move Again Skill/Action

**Status: Implemented**
## 1. Overview

**Goal:** Introduce a mechanism allowing specific units (e.g., Dancers, Bards) to grant an additional action to an adjacent allied unit that has already completed its action within the current player phase. This mirrors the functionality of Dancer/Bard units in games like Fire Emblem.

## 2. Functional Requirements

### 2.1. Trigger Mechanism

*   **Action Type:** A new action, tentatively named `Dance` (or `Play`, `Sing`, etc., configurable per class/skill), will be available to units possessing the required skill (e.g., `Skill_Dance`).
*   **Availability:** The `Dance` action should appear in the unit's action menu if:
    *   The unit has the `Skill_Dance` (or equivalent).
    *   The unit has not yet performed its action this turn.
    *   There is at least one valid target adjacent to the unit. `[TDD: Test Dance action availability]`

### 2.2. Target Eligibility

*   **Conditions:** A unit can be targeted by the `Dance` action if it meets all the following criteria: `[TDD: Test target eligibility]`
    *   **Adjacent:** The target unit must be directly adjacent (up, down, left, or right) to the unit performing the `Dance` action.
    *   **Ally:** The target unit must belong to the same faction (e.g., Player).
    *   **Acted:** The target unit must have already completed its action in the current player phase (i.e., `UnitState.has_acted_this_turn` is true).
    *   **Not Refreshed:** The target unit must not have already been refreshed by a `Dance` (or similar) action during the current player phase (i.e., `UnitState.was_refreshed_this_turn` is false).
    *   **Action Capable (Optional but Recommended):** The target unit should ideally not be under a status effect that prevents actions (e.g., Sleep, Stun). While the refresh might still occur, they wouldn't be able to use the granted action. Targeting logic might filter these units out or allow targeting but with no effective action granted.

*   **Pseudocode: Target Validation**
    ```pseudocode
    FUNCTION is_valid_dance_target(dancer_unit, potential_target_unit):
        IF potential_target_unit IS NULL:
            RETURN FALSE
        ENDIF

        // Check Adjacency
        IF NOT are_adjacent(dancer_unit.position, potential_target_unit.position):
            RETURN FALSE
        ENDIF

        // Check Faction
        IF dancer_unit.faction != potential_target_unit.faction:
            RETURN FALSE
        ENDIF

        // Check State
        target_state = potential_target_unit.state
        IF NOT target_state.has_acted_this_turn:
            RETURN FALSE
        ENDIF
        IF target_state.was_refreshed_this_turn:
            RETURN FALSE
        ENDIF

        // Optional: Check Action-Preventing Status
        // IF has_action_preventing_status(potential_target_unit):
        //     RETURN FALSE // Or allow targeting but warn player? Design decision needed.
        // ENDIF

        RETURN TRUE
    ENDFUNCTION
    ```

### 2.3. Effect of the Action

*   **Target Refresh:** When the `Dance` action is successfully performed on a valid target:
    *   The target unit's `has_acted_this_turn` flag is reset to `false`.
    *   The target unit's `was_refreshed_this_turn` flag is set to `true`.
    *   The target unit immediately becomes available to perform another full action (Move + Action) in the current player phase. `[TDD: Test unit refresh effect]`
*   **Dancer State:** The unit performing the `Dance` action consumes its own action for the turn.
    *   The dancer's `has_acted_this_turn` flag is set to `true`.

*   **Pseudocode: Apply Dance Effect**
    ```pseudocode
    FUNCTION apply_dance_effect(dancer_unit, target_unit):
        // Update Target State
        target_state = target_unit.state
        target_state.has_acted_this_turn = FALSE
        target_state.was_refreshed_this_turn = TRUE

        // Update Dancer State
        dancer_state = dancer_unit.state
        dancer_state.has_acted_this_turn = TRUE

        // Trigger UI/Game State Update (e.g., allow target selection again)
        game_state.notify_unit_refreshed(target_unit)
    ENDFUNCTION
    ```

### 2.4. Limitations

*   **Single Refresh:** A unit can only be refreshed by a `Dance` (or similar) action once per player phase. The `was_refreshed_this_turn` flag prevents multiple refreshes. `[TDD: Test refresh limitation]`
*   **Dancer Action Cost:** Performing the `Dance` action consumes the dancer's action for the turn. They cannot perform other actions (Attack, Wait, etc.) after dancing in the same turn segment.
*   **No Self-Dance:** A unit cannot target itself with the `Dance` action. (Implicit in target eligibility checks).
*   **Canto Interaction:** Units performing the `Dance` action typically cannot use Canto movement afterwards, even if they have the Canto skill and remaining movement. The `Dance` action concludes their turn immediately after execution. `[TDD: Test Canto interaction]`

### 2.5. Interactions

*   **Status Effects:**
    *   **Dancer:** If the dancer has a status preventing action (Sleep, Stun), they cannot perform the `Dance` action.
    *   **Target:** If the target has a status preventing action (Sleep, Stun), they can still be *targeted* and *refreshed* (i.e., `has_acted_this_turn` reset, `was_refreshed_this_turn` set). However, they will still be unable to perform an action due to the status effect when their turn comes again. The refresh essentially "wastes" the dance in this scenario unless the status wears off before the phase ends. `[TDD: Test interaction with action-preventing status]`
*   **Other Skills:** Interactions with other skills should be considered on a case-by-case basis. Generally, the refresh resets the unit to an "ready-to-act" state, subject to existing statuses and terrain effects.

## 3. Integration with Existing Systems

### 3.1. `UnitState` Component

*   **New Flags:** Add the following boolean flags to the `UnitState` data structure or class:
    *   `has_acted_this_turn`: Tracks if the unit has performed its primary action(s) this phase.
    *   `was_refreshed_this_turn`: Tracks if the unit has been granted an extra action via `Dance` (or similar) this phase.
*   **Initialization:** Both flags should default to `false`.

### 3.2. `TurnManager`

*   **Phase Start Reset:** At the beginning of each *Player Phase*, the `TurnManager` must iterate through all player-controlled units and reset:
    *   `UnitState.has_acted_this_turn` to `false`.
    *   `UnitState.was_refreshed_this_turn` to `false`. `[TDD: Test turn start state reset]`
*   **Phase End:** No specific changes needed for phase end related to this skill, beyond normal state cleanup if any.

### 3.3. `ActionSystem`

*   **Action Definition:** Define a new action type (e.g., `ActionType.DANCE`).
*   **Action Menu Population:** Modify the logic that generates the action menu to include `Dance` if the unit meets the criteria in section 2.1. This involves checking the unit's skills and potentially scanning adjacent tiles for valid targets.
*   **Action Execution:** Implement the execution logic for the `Dance` action:
    1.  Prompt user to select an adjacent, valid target (using `is_valid_dance_target`).
    2.  If a valid target is selected and confirmed:
        *   Call `apply_dance_effect(dancer_unit, target_unit)`.
        *   Update game state to reflect the dancer has acted.
        *   Update game state/UI to allow the refreshed unit to act again.
    3.  If cancelled or no valid target, return to the action menu or previous state.

## 4. Edge Cases

*   **Multiple Dancers:** Multiple dancers can refresh different units in the same turn, provided each target hasn't been refreshed yet.
*   **Dancer Refresh:** Can a dancer be refreshed by another dancer *after* they have danced? Yes, if they meet the target eligibility criteria (acted, not refreshed). They could then act again (e.g., Attack or Wait, but likely not Dance again unless specifically designed).
*   **Turn End:** If a refreshed unit does not use its granted action before the player phase ends, the action is lost.

## 5. Future Considerations

*   **Area of Effect Dance:** Could a future skill allow dancing multiple units?
*   **Stat Buff Dance:** Could dances also grant temporary stat boosts?
*   **Special Dance Effects:** Dances that clear negative statuses?