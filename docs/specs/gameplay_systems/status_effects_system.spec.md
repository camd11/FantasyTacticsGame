# Status Effects System Specification

**Version:** 1.0
**Date:** 2025-04-06

## 1. Overview

This document outlines the specification for the Status Effects system in the Fantasy Tactics Game, based on the mechanics found in Fire Emblem: Thracia 776. This system manages the application, effects, duration, and curing of various status conditions that can afflict units during gameplay.

## 2. Core Concepts

### 2.1. Status Effect Definition

A status effect represents a temporary (within a chapter) condition applied to a unit, altering their stats, restricting their actions, or causing periodic damage.

**Data Structure:**

```pseudocode
CLASS StatusEffect:
    DEFINE PROPERTY name (String)         // e.g., "Poison", "Sleep"
    DEFINE PROPERTY description (String)    // User-facing description
    DEFINE PROPERTY effects (List<Effect>) // List of specific gameplay effects
    DEFINE PROPERTY duration_type (Enum)  // PERMANENT_UNTIL_CURED, SCRIPTED_TURNS
    DEFINE PROPERTY cure_methods (List<String>) // Methods to cure ("Restore Staff", "Antitoxin", "Kia Staff", "Chapter End")
    DEFINE PROPERTY icon (String)           // UI Icon identifier

CLASS Effect:
    DEFINE PROPERTY type (Enum)           // STAT_MODIFICATION, ACTION_RESTRICTION, PERIODIC_DAMAGE, AI_OVERRIDE
    DEFINE PROPERTY parameters (Dictionary) // Specifics, e.g., {"stat": "HP", "amount": -2}, {"action": "Magic", "allowed": false}
```

**TDD Anchor:** `test_status_effect_data_structure` - Verify structure and properties.

### 2.2. Duration

A key feature of Thracia 776's status effects is their persistence.

*   **Permanent Until Cured:** Most standard statuses (Poison, Sleep, Silence, Berserk, Petrify) **do not wear off automatically** during a chapter. They remain active until explicitly cured by an appropriate method (Restore Staff, Kia Staff, Antitoxin) or until the chapter ends.
*   **Scripted Turns:** Some conditions, typically related to story events or traps (like Paralysis), might have a specific turn duration defined by the event script. These are exceptions.
*   **Chapter End:** All active status effects are automatically cleared when a chapter concludes.

**TDD Anchor:** `test_status_effect_duration_persistence` - Verify statuses don't expire turn-to-turn unless scripted.
**TDD Anchor:** `test_status_effect_cleared_on_chapter_end` - Verify statuses are removed between chapters.

### 2.3. Stat Modifications

Certain statuses (notably Sleep, Berserk, Petrify) drastically reduce a unit's combat effectiveness by setting key stats to 0 for calculation purposes.

*   **Affected Stats:** Strength, Magic, Skill, Speed, and Defense are treated as 0 while the status is active.
*   **Consequences:** This results in 0 Avoid (due to 0 Speed/Skill), potentially 0 Defense (making them easy to damage), and inability to contribute effectively in combat.

**TDD Anchor:** `test_stat_modification_during_status` - Verify stats are correctly treated as 0 during relevant statuses.

## 3. Specific Status Effects

### 3.1. Poison

*   **Name:** Poison
*   **Description:** Unit takes damage at the start of their turn.
*   **Effects:**
    *   `PERIODIC_DAMAGE`: Deals a fixed amount of damage (e.g., 1-3 HP, configurable) at the start of the afflicted unit's phase.
    *   *Note:* Verify if poison can kill or leaves unit at 1 HP. Assume it can kill for now.
*   **Application:** Poison Weapons (Swords, Bows), specific enemy skills, map traps.
*   **Duration:** PERMANENT_UNTIL_CURED.
*   **Cure Methods:** "Restore Staff", "Antitoxin", "Chapter End".
*   **Icon:** `poison_icon`

**TDD Anchor:** `test_poison_application`
**TDD Anchor:** `test_poison_damage_at_turn_start`
**TDD Anchor:** `test_poison_curing`

### 3.2. Sleep

*   **Name:** Sleep
*   **Description:** Unit cannot perform any actions. Vulnerable to attack and capture.
*   **Effects:**
    *   `ACTION_RESTRICTION`: Cannot Move, Attack, Use Items, Use Staves, Trade, etc. (all actions forbidden).
    *   `STAT_MODIFICATION`: Str, Mag, Skl, Spd, Def treated as 0.
    *   `AI_OVERRIDE`: Unit performs no action.
    *   *Note:* If a mounted unit is put to sleep, they automatically dismount.
*   **Application:** Sleep Staff, map traps, specific events.
*   **Duration:** PERMANENT_UNTIL_CURED.
*   **Cure Methods:** "Restore Staff", "Chapter End".
*   **Icon:** `sleep_icon`

**TDD Anchor:** `test_sleep_application`
**TDD Anchor:** `test_sleep_action_restriction`
**TDD Anchor:** `test_sleep_stat_modification`
**TDD Anchor:** `test_sleep_dismount_effect`
**TDD Anchor:** `test_sleep_curing`

### 3.3. Silence

*   **Name:** Silence
*   **Description:** Unit cannot use magic or staves.
*   **Effects:**
    *   `ACTION_RESTRICTION`: Cannot use Magic Tomes or Staves.
    *   *Note:* Research suggests Skl/Spd might also be 0, but primary effect is blocking magic/staves. Assume only action restriction for now unless further evidence found.
*   **Application:** Silence Staff.
*   **Duration:** PERMANENT_UNTIL_CURED.
*   **Cure Methods:** "Restore Staff", "Chapter End".
*   **Icon:** `silence_icon`

**TDD Anchor:** `test_silence_application`
**TDD Anchor:** `test_silence_action_restriction`
**TDD Anchor:** `test_silence_curing`

### 3.4. Berserk

*   **Name:** Berserk
*   **Description:** Unit loses control and attacks the nearest unit, regardless of affiliation.
*   **Effects:**
    *   `AI_OVERRIDE`: Unit is controlled by AI, targets nearest unit (friend or foe) for attack. Player cannot issue commands.
    *   `STAT_MODIFICATION`: Str, Mag, Skl, Spd, Def treated as 0 (Needs confirmation if stats are zeroed *while* berserk or only for statuses like Sleep/Petrify. Assume stats remain for attack calculations but unit is AI controlled). Revisit this based on testing/further research. For now, assume AI override is the primary effect.
*   **Application:** Berserk Staff.
*   **Duration:** PERMANENT_UNTIL_CURED.
*   **Cure Methods:** "Restore Staff", "Chapter End".
*   **Icon:** `berserk_icon`

**TDD Anchor:** `test_berserk_application`
**TDD Anchor:** `test_berserk_ai_override`
**TDD Anchor:** `test_berserk_targeting`
**TDD Anchor:** `test_berserk_curing`

### 3.5. Petrify (Stone)

*   **Name:** Petrify / Stone
*   **Description:** Unit is turned to stone, completely immobilized and unable to act.
*   **Effects:**
    *   `ACTION_RESTRICTION`: Cannot perform any actions (similar to Sleep).
    *   `STAT_MODIFICATION`: Str, Mag, Skl, Spd, Def treated as 0.
    *   `AI_OVERRIDE`: Unit performs no action.
    *   *Note:* Unit likely cannot be rescued while petrified.
*   **Application:** Stone Staff (very rare, e.g., Veld).
*   **Duration:** PERMANENT_UNTIL_CURED.
*   **Cure Methods:** **"Kia Staff"**, "Chapter End". (Restore Staff does *not* work).
*   **Icon:** `petrify_icon`

**TDD Anchor:** `test_petrify_application`
**TDD Anchor:** `test_petrify_action_restriction`
**TDD Anchor:** `test_petrify_stat_modification`
**TDD Anchor:** `test_petrify_curing_kia_staff`
**TDD Anchor:** `test_petrify_curing_restore_staff_fails`

### 3.6. Paralysis (Scripted)

*   **Name:** Paralysis
*   **Description:** Unit cannot move or act for a set duration (event-specific).
*   **Effects:**
    *   `ACTION_RESTRICTION`: Cannot perform actions.
    *   *Note:* This is typically applied via events, not standard combat/staves.
*   **Application:** Chapter event scripts.
*   **Duration:** SCRIPTED_TURNS (defined by the event).
*   **Cure Methods:** Event trigger, duration expiry, potentially "Restore Staff" (needs verification if Restore works on scripted paralysis), "Chapter End".
*   **Icon:** `paralysis_icon`

**TDD Anchor:** `test_paralysis_application_scripted`
**TDD Anchor:** `test_paralysis_duration_scripted`

## 4. Status Effect Manager

A dedicated module, `StatusEffectManager`, will handle the logic for status effects. It interacts closely with the `UnitSystem`, `CombatSystem`, and `TurnManager`.

**Responsibilities:**

*   Track active status effects for each unit.
*   Provide functions to apply and cure status effects.
*   Interface with the `CombatSystem` to apply status effects from weapons/staves (checking accuracy for staves).
*   Interface with the `TurnManager` to trigger turn-based effects (e.g., Poison damage).
*   Interface with the `UnitSystem` to modify unit stats or restrict actions based on active statuses.
*   Clear all statuses at the end of a chapter.

**Pseudocode:**

```pseudocode
CLASS StatusEffectManager:
    DEFINE PROPERTY active_statuses (Dictionary<unit_id, List<StatusEffectInstance>>)

    // --- Initialization ---
    FUNCTION init():
        active_statuses = {}

    // --- Application ---
    FUNCTION apply_status(target_unit, status_effect_name, source=None):
        // TDD: test_apply_status_new
        // TDD: test_apply_status_already_active_no_stack
        // TDD: test_apply_status_immunity_check (Future: Check unit immunities)

        IF target_unit.id NOT IN active_statuses:
            active_statuses[target_unit.id] = []

        // Prevent stacking the same status effect
        IF status_effect_name IN [s.name FOR s IN active_statuses[target_unit.id]]:
            RETURN false // Already affected

        status_data = DataProvider.get_status_effect_data(status_effect_name)
        instance = CREATE StatusEffectInstance(status_data) // Includes duration logic if needed
        active_statuses[target_unit.id].append(instance)

        // Handle immediate effects (e.g., Dismount on Sleep for mounted units)
        IF status_effect_name == "Sleep" AND target_unit.is_mounted():
            UnitSystem.dismount_unit(target_unit) // TDD: test_apply_sleep_triggers_dismount

        // Log event
        EventSystem.publish("STATUS_APPLIED", {"unit": target_unit, "status": status_effect_name, "source": source})
        RETURN true

    // --- Curing ---
    FUNCTION cure_status(target_unit, status_name=None, cure_method="Unknown"):
        // TDD: test_cure_specific_status
        // TDD: test_cure_all_statuses (e.g., Restore Staff)
        // TDD: test_cure_non_existent_status
        // TDD: test_cure_petrify_requires_kia

        IF target_unit.id NOT IN active_statuses OR NOT active_statuses[target_unit.id]:
            RETURN false // No statuses to cure

        statuses_to_remove = []
        IF status_name: // Cure a specific status
            IF status_name == "Petrify" AND cure_method != "Kia Staff":
                 RETURN false // Petrify requires Kia Staff
            
            found = false
            FOR status IN active_statuses[target_unit.id]:
                IF status.name == status_name AND cure_method IN status.cure_methods:
                    statuses_to_remove.append(status)
                    found = true
                    BREAK
            IF NOT found:
                 RETURN false // Status not found or cure method invalid
        ELSE: // Cure all applicable statuses (e.g., Restore Staff)
            FOR status IN active_statuses[target_unit.id]:
                 // Restore staff doesn't cure Petrify
                IF status.name == "Petrify" AND cure_method == "Restore Staff":
                    CONTINUE 
                IF cure_method IN status.cure_methods:
                    statuses_to_remove.append(status)

        IF NOT statuses_to_remove:
            RETURN false // Nothing was cured

        FOR status IN statuses_to_remove:
            active_statuses[target_unit.id].remove(status)
            EventSystem.publish("STATUS_CURED", {"unit": target_unit, "status": status.name, "method": cure_method})

        IF NOT active_statuses[target_unit.id]: // Remove entry if list is empty
            DELETE active_statuses[target_unit.id]

        RETURN true

    // --- Turn Processing ---
    FUNCTION process_turn_start_effects(unit):
        // TDD: test_process_turn_start_poison_damage
        // TDD: test_process_turn_start_no_effect_for_sleep
        
        IF unit.id NOT IN active_statuses:
            RETURN

        FOR status IN active_statuses[unit.id]:
            IF status.name == "Poison":
                damage = status.get_effect_parameter("PERIODIC_DAMAGE", "amount", default=1)
                UnitSystem.apply_damage(unit, damage, source="Poison")
                EventSystem.publish("POISON_DAMAGE", {"unit": unit, "damage": damage})
            // Add other turn-start effects if any (e.g., scripted duration decrement)

    FUNCTION process_chapter_end():
        // TDD: test_process_chapter_end_clears_all_statuses
        active_statuses.clear()
        EventSystem.publish("ALL_STATUSES_CLEARED", {"reason": "Chapter End"})

    // --- Queries ---
    FUNCTION has_status(unit, status_name):
        // TDD: test_has_status_positive
        // TDD: test_has_status_negative
        RETURN unit.id IN active_statuses AND status_name IN [s.name FOR s in active_statuses[unit.id]]

    FUNCTION get_active_statuses(unit):
        // TDD: test_get_active_statuses
        RETURN active_statuses.get(unit.id, [])

    FUNCTION get_modified_stats(unit, base_stats):
        // TDD: test_get_modified_stats_sleep
        // TDD: test_get_modified_stats_no_status
        // TDD: test_get_modified_stats_berserk (confirm if stats are zeroed)
        
        modified_stats = base_stats.copy()
        IF unit.id NOT IN active_statuses:
            RETURN modified_stats

        zero_stats = False
        FOR status IN active_statuses[unit.id]:
            IF status.name IN ["Sleep", "Petrify"]: // Add Berserk if confirmed
                zero_stats = True
                BREAK
        
        IF zero_stats:
            modified_stats["str"] = 0
            modified_stats["mag"] = 0
            modified_stats["skl"] = 0
            modified_stats["spd"] = 0
            modified_stats["def"] = 0
            // Note: Luck, Con, Mov, HP are generally not zeroed by these statuses.

        RETURN modified_stats

    FUNCTION can_perform_action(unit, action_type):
        // TDD: test_can_perform_action_silence_magic
        // TDD: test_can_perform_action_sleep_any
        // TDD: test_can_perform_action_no_status

        IF unit.id NOT IN active_statuses:
            RETURN true

        FOR status IN active_statuses[unit.id]:
            IF status.name IN ["Sleep", "Petrify", "Paralysis"]: // Berserk handled by AI override
                RETURN false // Cannot perform any action

            IF status.name == "Silence" AND action_type IN ["Magic", "Staff"]:
                RETURN false

            // Check specific action restrictions from effects list if needed
            FOR effect IN status.effects:
                IF effect.type == "ACTION_RESTRICTION":
                    IF effect.parameters.get("action") == action_type AND effect.parameters.get("allowed") == false:
                        RETURN false
        
        RETURN true

    FUNCTION get_ai_override(unit):
        // TDD: test_get_ai_override_berserk
        // TDD: test_get_ai_override_sleep
        // TDD: test_get_ai_override_no_status
        
        IF unit.id NOT IN active_statuses:
            RETURN None // Standard AI

        FOR status IN active_statuses[unit.id]:
            IF status.name == "Berserk":
                RETURN "BERSERK_AI"
            IF status.name IN ["Sleep", "Petrify", "Paralysis"]:
                RETURN "NO_ACTION_AI"
        
        RETURN None

END CLASS

CLASS StatusEffectInstance: // Represents an active status on a unit
    DEFINE PROPERTY name (String)
    DEFINE PROPERTY description (String)
    DEFINE PROPERTY effects (List<Effect>)
    DEFINE PROPERTY duration_type (Enum)
    DEFINE PROPERTY cure_methods (List<String>)
    DEFINE PROPERTY icon (String)
    DEFINE PROPERTY turns_remaining (Integer, nullable) // For SCRIPTED_TURNS

    FUNCTION init(status_data):
        // Copy properties from status_data
        // Initialize turns_remaining if duration_type is SCRIPTED_TURNS

    FUNCTION decrement_turn():
        IF duration_type == SCRIPTED_TURNS AND turns_remaining IS NOT NULL:
            turns_remaining -= 1
            RETURN turns_remaining <= 0 // Returns true if duration expired
        RETURN false

    FUNCTION get_effect_parameter(effect_type, param_name, default=None):
        FOR effect IN effects:
            IF effect.type == effect_type:
                RETURN effect.parameters.get(param_name, default)
        RETURN default

END CLASS
```

## 5. Integration Points

*   **Combat System:**
    *   When calculating staff hit chance for status staves, use the formula: `Base Hit + (4 * User Skill) %`, capped 1-99%. Target's Magic does not affect hit chance.
    *   On successful hit with a status staff or weapon, call `StatusEffectManager.apply_status()`.
*   **Unit System:**
    *   When retrieving unit stats for combat or display, call `StatusEffectManager.get_modified_stats()` to account for status effects (e.g., zeroed stats during Sleep).
    *   Before allowing a unit action, call `StatusEffectManager.can_perform_action()` to check restrictions (e.g., Silence blocking magic).
*   **Turn Manager:**
    *   At the start of each unit's phase, call `StatusEffectManager.process_turn_start_effects()` for that unit (e.g., apply Poison damage).
    *   At the end of a chapter, call `StatusEffectManager.process_chapter_end()`.
*   **AI System:**
    *   Before determining a unit's action, check `StatusEffectManager.get_ai_override()`. If it returns an override (e.g., "BERSERK_AI", "NO_ACTION_AI"), use that behavior instead of the standard AI logic.
*   **Item System:**
    *   When using items like "Restore Staff", "Kia Staff", or "Antitoxin", call the appropriate `StatusEffectManager.cure_status()` function.
*   **UI System:**
    *   Display status effect icons on unit info panels or status screens.
    *   Show status effect descriptions when hovering or selecting.

## 6. Open Questions / Future Considerations

*   Confirm exact damage value for Poison.
*   Confirm if Berserk zeroes stats or just overrides AI. Assume AI override only for now.
*   Confirm if Restore Staff cures scripted Paralysis.
*   Implement unit-specific status immunities if required by character data.
*   Refine handling of multiple, potentially conflicting statuses if necessary (e.g., can a unit be both Asleep and Poisoned? Yes. Asleep and Berserk? Unlikely).