# Specification: Berserk Status Effect

**Status: Implemented**

## 1. Overview

The Berserk status effect causes an affected unit to lose control and attack the nearest unit within its range, regardless of allegiance. This specification outlines the definition, application, behavior, curing mechanism, and integration points for the Berserk status.

## 2. Data Definition

The Berserk status effect will be defined within the game's data structures, likely managed by the `StatusEffectSystem`.

*   **ID:** `BERSERK` (Unique identifier)
*   **Name:** "Berserk" (Display name)
*   **Description:** "Unit uncontrollably attacks the nearest unit."
*   **Default Duration:** 3 turns (Configurable per application source, e.g., a specific staff might inflict a longer duration).
*   **Type:** Negative Status Effect
*   **Attribute:** Control Loss

```python
# Example Data Structure (Conceptual)
STATUS_EFFECTS = {
    "BERSERK": {
        "name": "Berserk",
        "description": "Unit uncontrollably attacks the nearest unit.",
        "default_duration": 3,
        "type": "negative",
        "attribute": "control_loss",
        # Potential icon/visual effect references
    }
    # ... other status effects
}
```

## 3. Application

Berserk status can be applied to units through various means:

*   **Items:** Specific staves (e.g., "Berserk Staff"). [TDD: Test Berserk Staff application]
*   **Skills:** Certain character or class skills might inflict Berserk under specific conditions (less common, but possible).
*   **Traps/Events:** Scenario-specific map traps or events could trigger Berserk.

The `StatusEffectSystem` will handle the application logic, adding the 'Berserk' status to the target unit's active effects list along with its duration. [TDD: Test Berserk application/duration]

## 4. Effect Logic (Turn Behavior)

When a unit afflicted with Berserk begins its turn:

1.  **Control Loss:** The unit cannot be controlled by the player or the standard AI. Player input via `InteractiveInputHandler` is disabled for this unit. Available actions in the UI are hidden or greyed out, except potentially a "Status" view. [TDD: Test Berserk blocks player control]
2.  **Target Acquisition:**
    *   Identify all units (allies, enemies, neutrals) on the map.
    *   Calculate the distance (e.g., Manhattan distance) from the berserk unit to all other units.
    *   Find the unit(s) with the minimum distance.
    *   Filter this list to only include units within the berserk unit's equipped weapon's attack range.
3.  **Action Execution:**
    *   **Attack Nearest:** If one or more units are within attack range:
        *   If only one unit is nearest and in range, attack that unit.
        *   If multiple units are equidistant and in range, randomly select one of the equidistant units to attack. [TDD: Test Berserk targets allies/enemies] [TDD: Test Berserk forces attack nearest]
        *   The attack is executed via the `CombatSystem` or equivalent.
    *   **Move Towards Nearest:** If no units are within attack range, but units exist elsewhere on the map:
        *   Identify the absolute nearest unit (regardless of attack range).
        *   Calculate a path towards that nearest unit using the unit's available movement points.
        *   Move the unit as far as possible along that path.
        *   If multiple units are equidistant, the target for movement can be chosen randomly or based on the first one found.
    *   **Wait:** If no other units are on the map, or if the unit cannot move closer to the nearest unit (e.g., blocked path, already adjacent but out of range), the unit performs no action (effectively waits).
4.  **Turn End:** The unit's turn ends immediately after the attack or movement/wait action. No other actions (Item, Staff, Trade, Wait manually, etc.) can be performed.

## 5. Curing / Removal

Berserk status can be removed through:

*   **Duration Expiry:** The primary method. At the start of the unit's turn, if the duration counter reaches zero, the status is removed *before* the Berserk logic takes effect. The unit then proceeds with its normal turn under player/AI control. [TDD: Test Berserk wears off]
*   **Restorative Effects:** Items like a "Restore" staff or specific skills can cleanse the Berserk status effect. This would be handled by the `StatusEffectSystem`. [TDD: Test Restore Staff cures Berserk]

## 6. Integration Points

Implementing Berserk requires modifications or interactions with several systems:

*   **`StatusEffectSystem`:**
    *   Needs to define the Berserk status data.
    *   Handle application of Berserk with duration.
    *   Handle decrementing duration each turn.
    *   Handle removal upon expiry or curing.
*   **`TurnManager` / `Engine`:**
    *   At the start of a unit's turn, check if the unit has the Berserk status *after* checking for duration expiry.
    *   If Berserk is active, bypass normal player (`InteractiveInputHandler`) or AI (`AISystem`) control flow.
    *   Invoke the specific Berserk turn logic routine.
*   **`BerserkTurnLogic` (New Module/Functionality):**
    *   Encapsulates the target acquisition and action execution logic described in Section 4.
    *   Requires access to unit positions, stats, attack ranges, movement capabilities, and map data.
    *   Needs to interact with the `MovementSystem` and `CombatSystem` (or equivalents) to execute actions.
*   **`ActionSystem` / `InteractiveInputHandler` / `UI`:**
    *   Must check for the Berserk status when determining available actions for a selected unit.
    *   Prevent player input and restrict available commands for berserk units.
    *   Display the Berserk status clearly on the unit's UI panel/status screen.
*   **`AISystem`:**
    *   Standard AI logic should be bypassed for berserk units. The `TurnManager` ensures the `AISystem` doesn't process berserk units.

## 7. TDD Anchors Summary

*   `[TDD: Test Berserk Staff application]`
*   `[TDD: Test Berserk application/duration]`
*   `[TDD: Test Berserk blocks player control]`
*   `[TDD: Test Berserk targets allies/enemies]`
*   `[TDD: Test Berserk forces attack nearest]`
*   `[TDD: Test Berserk wears off]`
*   `[TDD: Test Restore Staff cures Berserk]`