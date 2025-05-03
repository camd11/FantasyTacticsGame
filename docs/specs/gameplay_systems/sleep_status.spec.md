# Specification: Sleep Status Effect

**Status: Implemented**

## 1. Overview

This document outlines the functional requirements and implementation details for the 'Sleep' status effect. Sleep prevents affected units from taking any action for a set duration or until cured.

## 2. Goal

Implement the Sleep status effect, preventing affected units from performing any actions and potentially making them more vulnerable.

## 3. Scope

### 3.1. Status Effect Definition

*   **ID:** `SLEEP`
*   **Name:** Sleep
*   **Description:** The unit is asleep and cannot perform any actions. Their Avoid stat is reduced to 0. The effect lasts for a specific number of turns or until the unit takes damage.
*   **Type:** Debilitating
*   **Default Duration:** 3 turns (can be overridden by the source applying the effect).
*   **Effects:**
    *   Prevents all actions (Move, Attack, Staff, Item, Wait, etc.).
    *   Sets the unit's Avoid stat to 0.
    *   Cured when the unit takes damage.
    *   Cured when the duration expires.

### 3.2. Application

*   Sleep can be applied by specific sources, such as:
    *   Items (e.g., 'Sleep Staff').
    *   Skills (Potentially).
*   The `StatusEffectSystem` will handle the application logic when triggered by an item use or skill activation.
    *   `[TDD: Test Sleep application via Sleep Staff]`
    *   `[TDD: Test Sleep application respects immunity (if any)]`

### 3.3. Effect on Unit

*   **Action Prevention:** A unit afflicted with Sleep cannot perform *any* action during their turn. Their turn is effectively skipped.
    *   `[TDD: Test Sleep blocks Move action]`
    *   `[TDD: Test Sleep blocks Attack action]`
    *   `[TDD: Test Sleep blocks Staff action]`
    *   `[TDD: Test Sleep blocks Item action]`
    *   `[TDD: Test Sleep blocks Wait action]`
    *   `[TDD: Test Sleep blocks other potential actions (Trade, Rescue, etc.)]`
*   **Stat Modification:** The unit's Avoid stat is reduced to 0 while asleep, making them easier to hit.
    *   `[TDD: Test Sleep reduces Avoid to 0 in combat calculations]`
    *   `[TDD: Test Avoid returns to normal after Sleep is cured]`
*   **Targeting:** Sleeping units can still be targeted by allies and enemies.

### 3.4. Curing Sleep

*   **Duration:** Sleep wears off naturally at the start of the unit's turn after its duration expires. The duration countdown occurs at the start of the afflicted unit's turn.
    *   `[TDD: Test Sleep duration decrements each turn]`
    *   `[TDD: Test Sleep wears off after specified duration]`
*   **Taking Damage:** If a sleeping unit takes any amount of damage (HP > 0) from an attack or other source, the Sleep status is immediately cured *after* the damage calculation but *before* any potential counter-attack (which they couldn't do anyway while asleep).
    *   `[TDD: Test taking damage cures Sleep]`
    *   `[TDD: Test taking 0 damage does not cure Sleep]`
*   **Restoration:** Specific actions like the 'Restore' staff can cure Sleep.
    *   `[TDD: Test Restore staff cures Sleep]`

### 3.5. Data Definition

The Sleep status effect will be defined in `data/status_effects.yaml`:

```yaml
# data/status_effects.yaml (Example Entry)
- id: SLEEP
  name: Sleep
  description: Unit cannot perform actions. Avoid becomes 0. Cured by taking damage or after duration expires.
  type: debilitating
  duration: 3 # Default duration
  effects:
    - type: PREVENT_ACTION # Generic flag to prevent any action
    - type: SET_STAT
      stat: Avoid # The stat to modify
      value: 0    # The value to set it to
    - type: CURE_ON_DAMAGE # Flag indicating damage cures this status
    - type: CURE_ON_DURATION_END # Flag indicating duration expiration cures this status
  # Optional: Add icon/visual effect identifiers later
```

## 4. System Integration and Pseudocode

### 4.1. `StatusEffectSystem`

*   **Responsibilities:** Manages status effect data, application, duration tracking, removal, and querying status effects on units. Provides stat modifications based on active statuses.

```pseudocode
class StatusEffectSystem:
    statuses_data: Map<StatusID, StatusData>
    active_statuses: Map<UnitID, List<ActiveStatus>>

    function load_status_effects(data_file):
        // Load from data/status_effects.yaml into statuses_data

    function apply_status(target_unit: Unit, status_id: StatusID, duration_override: Optional<Int>):
        if target_unit is immune to status_id:
            return // Or handle resistance logic

        data = statuses_data[status_id]
        duration = duration_override if duration_override is not None else data.default_duration

        // Remove existing instance if stackable rules apply (assume Sleep doesn't stack, just resets duration)
        remove_status(target_unit, status_id)

        active_status = ActiveStatus(status_id, duration)
        active_statuses[target_unit.id].append(active_status)
        // Trigger UI update/event

    function remove_status(target_unit: Unit, status_id: StatusID):
        if target_unit.id in active_statuses:
            active_statuses[target_unit.id] = [s for s in active_statuses[target_unit.id] if s.id != status_id]
            // Trigger UI update/event

    function has_status(unit: Unit, status_id: StatusID) -> Bool:
        return unit.id in active_statuses and any(s.id == status_id for s in active_statuses[unit.id])

    function decrement_durations_on_turn_start(unit: Unit):
        if unit.id in active_statuses:
            statuses_to_remove = []
            for status in active_statuses[unit.id]:
                if status.duration > 0:
                    status.duration -= 1
                    if status.duration == 0 and statuses_data[status.id].has_effect('CURE_ON_DURATION_END'):
                        statuses_to_remove.append(status.id)
            for status_id in statuses_to_remove:
                remove_status(unit, status_id)

    function handle_damage_taken(unit: Unit, damage: Int):
        if damage > 0 and unit.id in active_statuses:
            statuses_to_remove = []
            for status in active_statuses[unit.id]:
                 if statuses_data[status.id].has_effect('CURE_ON_DAMAGE'):
                     statuses_to_remove.append(status.id)
            for status_id in statuses_to_remove:
                remove_status(unit, status_id)

    function get_stat_modification(unit: Unit, stat_name: String) -> Modifier:
        modifier = StatModifier() // e.g., additive=0, multiplicative=1, set_value=None
        if unit.id in active_statuses:
            for status in active_statuses[unit.id]:
                data = statuses_data[status.id]
                for effect in data.effects:
                    if effect.type == 'SET_STAT' and effect.stat == stat_name:
                        // Assuming SET_STAT overrides others for simplicity here
                        modifier.set_value = effect.value
                        return modifier // Return immediately as SET overrides
                    // Add logic for ADD_STAT, MULTIPLY_STAT if needed
        return modifier

    function can_unit_act(unit: Unit) -> Bool:
        if unit.id in active_statuses:
            for status in active_statuses[unit.id]:
                data = statuses_data[status.id]
                if any(effect.type == 'PREVENT_ACTION' for effect in data.effects):
                    return False
        return True

```

### 4.2. `TurnManager` / `Engine`

*   **Responsibilities:** Manages turn order, starts/ends unit turns, checks if a unit can act.

```pseudocode
class TurnManager:
    status_effect_system: StatusEffectSystem

    function process_unit_turn(unit: Unit):
        status_effect_system.decrement_durations_on_turn_start(unit)

        if not status_effect_system.can_unit_act(unit):
            // Unit has a status like Sleep preventing action
            log(f"{unit.name} is asleep and cannot act.")
            // Optionally show a visual indicator (e.g., "Zzz")
            end_unit_turn(unit) // Skip directly to end of turn
            return

        // Proceed with normal turn logic (Player Input or AI)
        if unit.is_player_controlled():
            wait_for_player_action(unit)
        else:
            ai_system.determine_and_execute_action(unit)

    function end_unit_turn(unit: Unit):
        // Standard end-of-turn cleanup
        // Advance to next unit in turn order
```

### 4.3. `ActionSystem` / `InteractiveInputHandler`

*   **Responsibilities:** Determines available actions for a unit, handles player input for selecting actions.

```pseudocode
class ActionSystem:
    status_effect_system: StatusEffectSystem

    function get_available_actions(unit: Unit) -> List<Action>:
        if not status_effect_system.can_unit_act(unit):
            return [] // No actions available if asleep

        // Calculate normal available actions (Move, Attack, Staff, Item, etc.)
        actions = calculate_standard_actions(unit)
        return actions

class InteractiveInputHandler:
    action_system: ActionSystem
    ui_system: UISystem

    function display_action_menu(unit: Unit):
        available_actions = action_system.get_available_actions(unit)
        if not available_actions:
            // Optionally display "Sleeping" status instead of menu
            ui_system.show_status_message(unit, "Sleeping")
            // Do not show action menu, maybe return control or wait
        else:
            ui_system.show_action_menu(unit, available_actions)

```

### 4.4. `AI System`

*   **Responsibilities:** Determines actions for AI-controlled units, evaluates targets.

```pseudocode
class AISystem:
    status_effect_system: StatusEffectSystem
    action_system: ActionSystem
    combat_calculator: CombatCalculator

    function determine_and_execute_action(unit: Unit):
        if not status_effect_system.can_unit_act(unit):
            log(f"AI unit {unit.name} is asleep. Skipping turn.")
            // AI does nothing, turn ends via TurnManager logic
            return

        // Normal AI logic: Evaluate threats, targets, support actions etc.
        chosen_action = find_best_action(unit)
        execute_action(unit, chosen_action)

    function evaluate_target_priority(attacker: Unit, target: Unit) -> Float:
        base_priority = calculate_base_priority(attacker, target)

        if status_effect_system.has_status(target, 'SLEEP'):
            // Increase priority significantly as target is helpless
            base_priority *= 1.5 // Example multiplier

        // Consider other factors (threat, potential damage, etc.)
        return base_priority

```
*   `[TDD: Test AI unit skips turn when afflicted with Sleep]`
*   `[TDD: Test AI prioritizes attacking sleeping targets]`

### 4.5. `CombatSystem` / `CombatCalculator`

*   **Responsibilities:** Calculates combat outcomes (hit rate, damage, etc.), applies damage and effects.

```pseudocode
class CombatCalculator:
    status_effect_system: StatusEffectSystem

    function calculate_hit_rate(attacker: Unit, defender: Unit) -> Int:
        // Base Hit = Attacker Hit Stat + Weapon Hit
        base_hit = attacker.get_stat('Hit') + attacker.equipped_weapon.hit

        // Avoid = Defender Speed + Terrain Bonus + Support Bonus + Stat Modifications
        defender_avoid_stat = defender.get_stat('Avoid') // Base Avoid from Speed etc.
        terrain_bonus = get_terrain_avoid_bonus(defender.position)
        support_bonus = get_support_avoid_bonus(defender)

        // Check for status effect modifications on Avoid
        avoid_modifier = status_effect_system.get_stat_modification(defender, 'Avoid')
        if avoid_modifier.set_value is not None:
            final_avoid = avoid_modifier.set_value
        else:
            final_avoid = defender_avoid_stat # Apply additive/multiplicative mods if they exist
            final_avoid += terrain_bonus + support_bonus

        hit_rate = base_hit - final_avoid
        return clamp(hit_rate, 0, 100)

class CombatSystem:
    status_effect_system: StatusEffectSystem
    combat_calculator: CombatCalculator

    function execute_combat(attacker: Unit, defender: Unit):
        // ... calculate damage, crits, etc. ...
        hit_landed = perform_attack_roll(attacker, defender)

        if hit_landed:
            damage = combat_calculator.calculate_damage(...)
            apply_damage(defender, damage)
            // ... other effects ...
        // ... handle counter attack if defender can ...

    function apply_damage(unit: Unit, damage: Int):
        unit.current_hp -= damage
        log(f"{unit.name} takes {damage} damage.")

        // Check if taking damage cures Sleep
        status_effect_system.handle_damage_taken(unit, damage)

        if unit.current_hp <= 0:
            handle_unit_death(unit)

```

## 5. TDD Anchors Summary

*   `[TDD: Test Sleep application via Sleep Staff]`
*   `[TDD: Test Sleep application respects immunity (if any)]`
*   `[TDD: Test Sleep blocks Move action]`
*   `[TDD: Test Sleep blocks Attack action]`
*   `[TDD: Test Sleep blocks Staff action]`
*   `[TDD: Test Sleep blocks Item action]`
*   `[TDD: Test Sleep blocks Wait action]`
*   `[TDD: Test Sleep blocks other potential actions (Trade, Rescue, etc.)]`
*   `[TDD: Test Sleep reduces Avoid to 0 in combat calculations]`
*   `[TDD: Test Avoid returns to normal after Sleep is cured]`
*   `[TDD: Test Sleep duration decrements each turn]`
*   `[TDD: Test Sleep wears off after specified duration]`
*   `[TDD: Test taking damage cures Sleep]`
*   `[TDD: Test taking 0 damage does not cure Sleep]`
*   `[TDD: Test Restore staff cures Sleep]`
*   `[TDD: Test AI unit skips turn when afflicted with Sleep]`
*   `[TDD: Test AI prioritizes attacking sleeping targets]`