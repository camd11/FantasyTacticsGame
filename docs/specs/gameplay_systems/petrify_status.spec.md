# Specification: Petrify Status Effect

**Version:** 1.0
**Date:** 2025-04-15
**Status:** Implemented

## 1. Overview

This document outlines the design and implementation details for the "Petrify" status effect in the Fantasy Tactics Game. Petrify renders a unit completely inactive, turning them into stone, unable to perform any actions but potentially gaining defensive bonuses.

## 2. Status Effect Definition

*   **ID:** `PETRIFY` (To be defined in `data/status_effects.yaml`)
*   **Name:** Petrify
*   **Description:** Unit is turned to stone, cannot act, and has altered defensive stats.
*   **Duration:** Indefinite. The status persists until explicitly cured. It does not wear off over time. `[TDD: Test Petrify application/duration]`
*   **Application:**
    *   Primarily applied by specific means, such as a 'Stone' staff.
    *   Other potential sources (future scope): specific skills, weapon effects, map events.
*   **Curing:**
    *   Can *only* be cured by the 'Restore' staff or equivalent status-clearing effect.
    *   Taking damage does *not* cure Petrify.
    *   Does *not* wear off naturally at the start or end of a turn/phase. `[TDD: Test Petrify curing mechanism]`

## 3. Effects

### 3.1. Action Restriction

*   A unit afflicted with Petrify cannot perform *any* action. This includes, but is not limited to:
    *   Move
    *   Attack
    *   Use Staff
    *   Use Item
    *   Wait
    *   Trade
    *   Talk
    *   Any other special commands (e.g., Rescue, Shove, Capture).
*   The unit's turn is immediately skipped if they are petrified at the start of their activation.
*   Player input for selecting actions for a petrified unit is disabled. `[TDD: Test Petrify blocks all actions]`

### 3.2. Stat Modifications

*   **Avoid:** Set to 0. Petrified units cannot evade attacks.
*   **Defense (Def):** Increased by a significant flat amount (e.g., +10).
*   **Resistance (Res):** Increased by a significant flat amount (e.g., +10).
*   These changes make the unit very durable but unable to dodge. `[TDD: Test Petrify affects Def/Avoid]`

## 4. System Integration Points

### 4.1. `StatusEffectSystem`

*   **Responsibility:** Manages the application, tracking, and removal of the Petrify status.
*   **Logic:**
    *   Add `PETRIFY` to the list of known status effects, loading its definition from `data/status_effects.yaml`.
    *   Provide functions `apply_status(unit, status_id, duration)` and `remove_status(unit, status_id)`.
    *   `apply_status` for `PETRIFY` should set duration to indefinite (e.g., -1 or a specific constant).
    *   `remove_status` should be triggered by curing effects (e.g., Restore staff usage).
    *   Provide a function `has_status(unit, status_id)` to check if a unit is petrified.
    *   Provide a function `get_status_effects(unit)` which includes Petrify if active.

```pseudocode
// StatusEffectSystem Module

function apply_status(unit, status_id, duration):
    if status_id == PETRIFY:
        unit.status_effects[PETRIFY] = { duration: INDEFINITE }
        // Potentially trigger visual effect update
    else:
        // Handle other statuses
    [TDD: Test Petrify application/duration]

function remove_status(unit, status_id):
    if status_id == PETRIFY and unit.has_status(PETRIFY):
        delete unit.status_effects[PETRIFY]
        // Potentially trigger visual effect update
    else:
        // Handle other statuses
    [TDD: Test Petrify curing mechanism]

function has_status(unit, status_id):
    return status_id in unit.status_effects

function get_stat_modification(unit, stat_name):
    total_mod = 0
    if has_status(unit, PETRIFY):
        if stat_name == 'Avoid':
            // Special handling needed in CombatCalculator to force 0
            pass
        elif stat_name == 'Def':
            total_mod += PETRIFY_DEF_BONUS // e.g., +10
        elif stat_name == 'Res':
            total_mod += PETRIFY_RES_BONUS // e.g., +10
    // Add mods from other statuses/skills
    return total_mod

```

### 4.2. `TurnManager` / `Engine`

*   **Responsibility:** Control turn flow and unit activation.
*   **Logic:**
    *   Before activating a unit (player or AI), check if they have the `PETRIFY` status using `StatusEffectSystem.has_status`.
    *   If petrified, skip the unit's entire turn and proceed to the next unit.

```pseudocode
// TurnManager Module

function activate_next_unit():
    current_unit = get_next_unit_in_order()
    if StatusEffectSystem.has_status(current_unit, PETRIFY):
        print_message(f"{current_unit.name} is petrified and cannot act.")
        // Trigger visual indication (e.g., greyed out, status icon flash)
        end_unit_turn(current_unit) // Skips action phase
        activate_next_unit() // Move to the next unit
    else:
        // Proceed with normal unit activation (player input or AI)
```

### 4.3. `ActionSystem` / `InteractiveInputHandler`

*   **Responsibility:** Handle player input and available actions for a selected unit.
*   **Logic:**
    *   When a player selects a unit, check if the unit has the `PETRIFY` status.
    *   If petrified, disable all action buttons/menu options (Move, Attack, Item, Wait, etc.). Display only the unit's info panel, perhaps with a clear "Petrified" indicator. Do not allow the player to enter the action selection phase.

```pseudocode
// InteractiveInputHandler Module

function on_unit_selected(unit):
    display_unit_info(unit)
    if StatusEffectSystem.has_status(unit, PETRIFY):
        disable_all_action_commands()
        show_status_indicator("Petrified")
        // Prevent moving cursor or opening action menu
    else:
        enable_available_action_commands(unit)
        // Allow normal interaction
    [TDD: Test Petrify blocks all actions]
```

### 4.4. `AI System`

*   **Responsibility:** Determine actions for AI-controlled units.
*   **Logic:**
    *   The `TurnManager` check (Section 4.2) already handles skipping the turn for petrified AI units. `[TDD: Test AI skips turn when petrified]`
    *   **Targeting Consideration (Optional Enhancement):** AI units might adjust their targeting priorities based on Petrify.
        *   Petrified units are immobile and cannot counter-attack (implicitly, as they cannot act).
        *   However, their high Def/Res might make them low-priority targets unless they are blocking a critical path or are easy to finish off despite defenses.
        *   AI logic should query `StatusEffectSystem.has_status` when evaluating potential targets.

```pseudocode
// AI System (Target Evaluation Snippet)

function evaluate_target(potential_target):
    score = calculate_base_target_score(potential_target)
    if StatusEffectSystem.has_status(potential_target, PETRIFY):
        // Target cannot move, act, or counter-attack.
        // Target has high Def/Res.
        score = adjust_score_for_petrified(score, potential_target) // Likely decrease score unless specific objective
    return score
```

### 4.5. `CombatSystem` / `CombatCalculator`

*   **Responsibility:** Calculate combat outcomes, including hit rates and damage.
*   **Logic:**
    *   When calculating combat stats, check if the defender has the `PETRIFY` status.
    *   If petrified:
        *   Override the defender's Avoid calculation, setting effective Avoid to 0.
        *   Add the flat Def bonus (+10) to the defender's base Def before calculating damage.
        *   Add the flat Res bonus (+10) to the defender's base Res before calculating damage.

```pseudocode
// CombatCalculator Module

function calculate_hit_rate(attacker, defender):
    // ... standard hit calculation ...
    base_hit = attacker.accuracy - defender.avoid
    // ... other modifiers ...

    if StatusEffectSystem.has_status(defender, PETRIFY):
        defender_effective_avoid = 0 // Override avoid calculation
    else:
        defender_effective_avoid = calculate_avoid(defender) // Normal calculation

    final_hit_rate = attacker.accuracy - defender_effective_avoid // Adjust calculation
    // Apply other modifiers (terrain, skills, support)
    return clamp(final_hit_rate, 0, 100)

function calculate_damage(attacker, defender):
    // ... determine attack stat (physical/magical) ...
    attack_stat = get_attack_stat(attacker)
    defense_stat = get_defense_stat(defender, attacker.weapon.damage_type) // Gets Def or Res

    if StatusEffectSystem.has_status(defender, PETRIFY):
        if attacker.weapon.damage_type == PHYSICAL:
            defense_stat += PETRIFY_DEF_BONUS
        elif attacker.weapon.damage_type == MAGICAL:
            defense_stat += PETRIFY_RES_BONUS

    // ... calculate base damage ...
    damage = attack_stat - defense_stat
    // Apply other modifiers (weapon triangle, effectiveness, skills)
    return max(0, damage)
    [TDD: Test Petrify affects Def/Avoid]

```

## 5. Data Structure (`data/status_effects.yaml`)

A new entry should be added to `data/status_effects.yaml`:

```yaml
- id: PETRIFY
  name: Petrify
  description: "Unit is turned to stone. Cannot act. Avoid set to 0. Def/Res increased."
  duration: -1 # Indicates indefinite duration
  effects:
    - type: ACTION_BLOCK # Prevents all actions
      value: ALL
    - type: STAT_MODIFIER_FLAT
      stat: Def
      value: 10 # Example value, tune as needed
    - type: STAT_MODIFIER_FLAT
      stat: Res
      value: 10 # Example value, tune as needed
    - type: STAT_OVERRIDE # Special type to force a value
      stat: Avoid
      value: 0
  cure_conditions:
    - CURE_BY_RESTORE # Only cured by specific actions/items like Restore
  # Optional: Visual effect ID, sound effect ID
  # visual_effect: petrify_sprite_overlay
  # icon: petrify_icon.png
```

## 6. TDD Anchors Summary

*   `[TDD: Test Petrify application/duration]`: Verify Petrify is applied correctly and persists indefinitely.
*   `[TDD: Test Petrify blocks all actions]`: Ensure a petrified unit cannot select or perform any actions and their turn is skipped.
*   `[TDD: Test Petrify affects Def/Avoid]`: Check that combat calculations correctly use Avoid=0 and increased Def/Res for petrified units.
*   `[TDD: Test Petrify curing mechanism]`: Confirm Petrify is only removed by 'Restore' and not by time or damage.
*   `[TDD: Test AI skips turn when petrified]`: Verify AI units correctly skip their turn when petrified.