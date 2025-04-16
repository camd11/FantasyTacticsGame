# Specification: Silence Status Effect

**Status:** Implemented & Tested
*(Note: Implementation pre-dated this specification and associated tests)*

## 1. Overview & Goal

**Goal:** Implement the 'Silence' status effect, which prevents affected units from using magic tomes and staves for a set duration.

## 2. Status Effect Definition

- **ID:** `SILENCE`
- **Name:** "Silence"
- **Default Duration:** 5 turns (configurable per application source)
- **Description:** "Unit cannot use magic tomes or staves."
- **Type:** Negative Status Effect

## 3. Application Mechanism

- Silence can be applied to a unit through various means, primarily:
    - **Staves:** Specific staves like a 'Silence Staff'. The staff's properties would define the application chance, range, and duration. `[TDD: Test Silence Staff application]`
    - **Skills:** Certain character or class skills might inflict Silence under specific conditions (Future Scope).
    - **Traps:** Environmental traps could potentially inflict Silence (Future Scope).
- The `StatusEffectSystem` will handle the application logic, adding the 'SILENCE' status with its duration to the target unit's active statuses. `[TDD: Test Silence application/duration]`

## 4. Effect Details

- **Restriction:** While silenced, a unit is prohibited from performing actions that require the use of:
    - Magic Tomes (`ItemType.TOME`)
    - Staves (`ItemType.STAFF`)
- **Affected Actions:**
    - `Attack` action using a magic tome.
    - `Use Staff` action.
    - Any other future actions explicitly requiring magic/staff usage.
- **Allowed Actions:** Silenced units can still perform actions not reliant on magic tomes or staves, including but not limited to:
    - `Wait`
    - `Item` (using non-staff items like vulneraries)
    - `Attack` using physical weapons (Swords, Lances, Axes, Bows, etc.)
    - `Trade`
    - `Rescue` / `Drop`
    - Using skills that don't involve casting magic or using staves.
    `[TDD: Test magic/staff action restriction]`
    `[TDD: Test non-magic actions allowed]`

## 5. Curing Mechanism

- **Primary:** Silence wears off naturally after its duration expires. The `StatusEffectSystem` will decrement the duration at the start or end of each turn (consistent with other status effects). `[TDD: Test Silence wears off]`
- **Secondary:** Specific 'Restore' staves or items can be used to immediately remove the Silence status effect, along with other negative statuses. `[TDD: Test Restore Staff curing Silence]`
- **Tertiary (Future Scope):** Waiting on specific terrain types (e.g., a 'Sanctuary' tile) might cure Silence.

## 6. Integration Points

- **`StatusEffectSystem`:**
    - `apply_status(unit, status_id, duration)`: Adds 'SILENCE' to the unit's status list.
    - `update_unit_statuses(unit)`: Called each turn phase (e.g., start of player phase) to decrement the duration of 'SILENCE'. Removes the status if duration reaches 0.
    - `has_status(unit, status_id)`: Method to check if a unit currently has the 'SILENCE' status.
    - `remove_status(unit, status_id)`: Method for explicitly removing 'SILENCE' (e.g., via Restore staff).
- **`ActionSystem` / `InteractiveInputHandler`:**
    - When generating the list of available actions for a selected unit (`get_available_actions(unit)`):
        - Check if `unit.has_status('SILENCE')`.
        - If true, filter out any `Action` objects that require `ItemType.TOME` or `ItemType.STAFF`. This might involve checking the equipped weapon or the nature of the action itself (e.g., a dedicated `UseStaffAction`).
- **`CombatSystem` / `AI`:**
    - **AI Action Planning:** When the AI evaluates potential actions for its units:
        - If considering an action involving a tome or staff, it must check if the acting unit `has_status('SILENCE')`. If silenced, this action path should be discarded or heavily penalized.
    - **AI Target Evaluation:** When evaluating potential targets for magic/staff attacks/effects:
        - The AI should be aware that silenced *enemy* units cannot retaliate with magic/staves, potentially making them safer targets for certain units. (Less critical for initial implementation but important for robust AI). `[TDD: Test AI recognizes Silence]`
- **`Unit` Object:**
    - Needs a way to store active status effects, including their remaining duration (likely already exists for other statuses like Poison).
- **`UI`:**
    - Display a visual indicator (e.g., an icon) on silenced units.
    - When viewing a silenced unit's stats or available actions, clearly indicate the Silence status and potentially grey out or hide unavailable magic/staff actions. `[TDD: Test UI indication for Silence]`

## 7. Data Representation

- The 'SILENCE' status effect definition should be stored consistently with other status effects. This could be:
    - A dedicated data file (e.g., `data/status_effects.yaml`):
      ```yaml
      SILENCE:
        name: "Silence"
        description: "Prevents use of magic tomes and staves."
        type: "negative"
        # Default duration might be defined here or by the application source
      ```
    - Constants within the `StatusEffectSystem` module.
- The *instance* of an active status effect on a unit needs to store:
    - `status_id`: `SILENCE`
    - `remaining_duration`: integer

## 8. TDD Anchors

- `[TDD: Test Silence application/duration]` - Verify Silence is added with correct duration.
- `[TDD: Test Silence Staff application]` - Verify a Silence Staff correctly applies the status.
- `[TDD: Test magic/staff action restriction]` - Verify silenced units cannot select/perform Tome/Staff actions.
- `[TDD: Test non-magic actions allowed]` - Verify silenced units *can* perform other actions (Wait, Attack (phys), Item).
- `[TDD: Test Silence wears off]` - Verify Silence is removed after its duration expires.
- `[TDD: Test Restore Staff curing Silence]` - Verify Restore Staff removes Silence.
- `[TDD: Test AI recognizes Silence]` - Verify AI doesn't attempt magic/staff actions with silenced units.
- `[TDD: Test UI indication for Silence]` - Verify UI shows Silence status and restricts actions visually.