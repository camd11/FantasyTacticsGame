# Specification: Combat Skills (Astra, Sol, Luna, Pavise)

**Version:** 1.0
**Date:** 2025-04-07
**Author:** AI Assistant

## 1. Overview

This document specifies the implementation details for four combat skills within the Fantasy Tactics Game engine, based on their behavior in Fire Emblem: Thracia 776:
- Astra (Shooting Star)
- Sol (Sun Sword)
- Luna (Moon Sword)
- Pavise (Big Shield)

These skills introduce unique effects and activation chances during combat, requiring careful integration into the existing `CombatSystem` and `CombatCalculator`.

## 2. Skill Definitions and Activation

All skills listed here activate based on the unit's **Skill (SKL)** stat percentage, unless otherwise noted. Activation checks occur at specific points within the combat sequence. The `Nihil` skill on an opponent negates the activation of these skills.

**TEST:** `test_nihil_negates_offensive_skills`
**TEST:** `test_nihil_negates_defensive_skills`

### 2.1. Astra (ID: ASTRA)
- **Description:** Allows unit to strike 5 consecutive attacks at half damage.
- **Trigger:** Activates when the unit initiates an attack (`COMBAT` condition in YAML).
- **Activation Chance:** `Skill %` (e.g., `random(1, 100) <= unit.stats.SKL`).
- **Effect Type:** `MULTI_ATTACK`
- **Parameters:** `num_attacks: 5`, `damage_multiplier: 0.5`

**TEST:** `test_astra_activation_chance`

### 2.2. Sol (ID: SOL)
- **Description:** Heals the user by the amount of damage dealt to the enemy.
- **Trigger:** Activates when the unit lands a hit during combat (`COMBAT` condition in YAML).
- **Activation Chance:** `Skill %` (e.g., `random(1, 100) <= unit.stats.SKL`).
- **Effect Type:** `HEAL_FROM_DAMAGE`
- **Parameters:** `heal_percent: 100`

**TEST:** `test_sol_activation_chance`

### 2.3. Luna (ID: LUNA)
- **Description:** Ignores enemy's defense/resistance when calculating damage for a single strike.
- **Trigger:** Activates when the unit lands a hit during combat (`COMBAT` condition in YAML).
- **Activation Chance:** `Skill %` (e.g., `random(1, 100) <= unit.stats.SKL`).
- **Effect Type:** `IGNORE_DEFENSE`
- **Parameters:** `{}`

**TEST:** `test_luna_activation_chance`

### 2.4. Pavise (ID: PAVISE)
- **Description:** Completely negates an incoming attack's damage for a single strike.
- **Trigger:** Activates when the unit is hit by an attack (`WHEN_ATTACKED` condition in YAML).
- **Activation Chance:** `Skill %` (e.g., `random(1, 100) <= unit.stats.SKL`). **Note:** This standardizes based on research/YAML, overriding the Level% implementation seen in `combat_system.py`.
- **Effect Type:** `NEGATE_DAMAGE`
- **Parameters:** `{}`

**TEST:** `test_pavise_activation_chance_skill_based`
**TEST:** `test_pavise_activation_chance_level_based` (Mark as deprecated/incorrect if Skill% is chosen)

## 3. Skill Effect Details and Interactions

### 3.1. Astra
- **Effect:** Replaces the standard attack sequence (initial hit, counter, follow-up) with 5 consecutive hits from the Astra user.
    - Each hit deals damage calculated as `(Normal Damage Formula Result) * 0.5`, rounded down.
    - The opponent does *not* get to counterattack between Astra hits.
    - If the target is defeated before all 5 hits land, the sequence stops.
- **Interaction with Follow-up Attacks (Pursuit):** Astra activation overrides standard Pursuit checks. The unit performs 5 hits regardless of Attack Speed difference.
- **Interaction with Critical Hits:**
    - Each of the 5 Astra hits can critically hit independently.
    - The standard critical hit rules apply:
        - First hit: Crit chance capped at 25%.
        - Hits 2-5: Crit chance calculated as `(Base Crit Rate) * PCC`, no 25% cap.
    - Critical damage is applied *after* the 0.5 damage multiplier (e.g., `(Normal Damage * 0.5) * 2`).
- **Interaction with Other Skills:**
    - **Nihil:** If the *defender* has Nihil, Astra cannot activate.
    - **Sol/Luna:** Sol or Luna can potentially activate on *each* of the 5 Astra hits independently, provided the Astra user has those skills and the defender does not have Nihil. Activation is rolled separately for each hit.
    - **Pavise:** If the *defender* has Pavise, it can potentially activate against *each* of the 5 incoming Astra hits independently (rolled separately for each hit), negating the damage for that specific hit.
    - **Adept:** Adept does not activate during an Astra sequence.
    - **Wrath:** Wrath does not apply to Astra hits, as Astra only triggers on initiation, not counterattack.

**TEST:** `test_astra_replaces_normal_combat_flow`
**TEST:** `test_astra_five_hits_half_damage`
**TEST:** `test_astra_stops_if_target_defeated`
**TEST:** `test_astra_overrides_pursuit`
**TEST:** `test_astra_crit_chance_per_hit_pcc_applies`
**TEST:** `test_astra_crit_damage_calculation`
**TEST:** `test_astra_negated_by_defender_nihil`
**TEST:** `test_astra_sol_activates_on_hit`
**TEST:** `test_astra_luna_activates_on_hit`
**TEST:** `test_astra_pavise_activates_on_hit`
**TEST:** `test_astra_adept_does_not_activate`

### 3.2. Sol
- **Effect:** When Sol activates on a successful hit, the user is healed for an amount equal to the final damage dealt *by that specific hit*.
- **Activation Timing:** Activates *after* damage for the hit is calculated (including potential Luna modification) but *before* the damage is negated by Pavise (if Pavise also activates). If Pavise negates the damage, Sol still "activates" (consumes the proc chance for that hit) but heals for 0.
- **Damage Basis:** Heals based on the damage calculated *after* accounting for enemy Def/Res (or after Luna negates Def/Res), but *before* potential Pavise negation.
- **Interaction:**
    - Can activate on any hit (initial, counter, follow-up, Astra hits, Adept hits).
    - If both Sol and Luna activate on the same hit, Luna modifies the damage first, then Sol heals based on that Luna-modified damage.
    - If Pavise activates against the same hit Sol activates on, Sol heals 0.

**TEST:** `test_sol_heals_damage_dealt_by_hit`
**TEST:** `test_sol_activates_after_luna_modifies_damage`
**TEST:** `test_sol_heals_zero_if_pavise_negates_damage`
**TEST:** `test_sol_can_activate_on_followup`
**TEST:** `test_sol_can_activate_on_adept_hit`

### 3.3. Luna
- **Effect:** When Luna activates on a successful hit, the damage calculation for *that specific hit* ignores the target's Defense (for physical attacks) or Magic (for magical attacks).
- **Scope:** Applies only to the single hit on which it activates. If a unit doubles or uses Astra, Luna must activate separately for each hit to apply its effect multiple times.
- **Interaction:**
    - Can activate on any hit (initial, counter, follow-up, Astra hits, Adept hits).
    - If Luna activates, the damage calculation uses `Target Def/Mag = 0` for that strike.
    - If Sol also activates, Sol heals based on the Luna-modified damage.

**TEST:** `test_luna_ignores_defense_physical`
**TEST:** `test_luna_ignores_resistance_magical`
**TEST:** `test_luna_applies_only_to_activating_hit`
**TEST:** `test_luna_can_activate_on_followup`
**TEST:** `test_luna_can_activate_on_adept_hit`

### 3.4. Pavise
- **Effect:** When Pavise activates against an incoming hit, the damage from *that specific hit* is reduced to 0.
- **Activation Timing:** Checked *after* determining that an attack hits, but *before* calculating critical hit bonus or applying damage.
- **Scope:** Negates damage from the single hit it activates against. Does not prevent status effects applied by the weapon. Applies to both physical and magical attacks. No specific weapon type restrictions mentioned in research/YAML.
- **Interaction:**
    - Can activate against any incoming hit (initial, counter, follow-up, Astra hits, Adept hits).
    - If Pavise activates, any potential critical hit damage is also negated (since base damage becomes 0).
    - If Pavise activates against a hit where the attacker's Sol also activates, Sol heals 0.

**TEST:** `test_pavise_negates_physical_damage`
**TEST:** `test_pavise_negates_magical_damage`
**TEST:** `test_pavise_negates_crit_damage`
**TEST:** `test_pavise_does_not_negate_status_effects`
**TEST:** `test_pavise_applies_only_to_activating_hit`
**TEST:** `test_pavise_can_activate_on_followup`
**TEST:** `test_pavise_can_activate_on_adept_hit`

## 4. Skill Interaction Priority (Within a Single Strike)

The following order should be used when checking and applying skills for a single strike instance where an attack successfully hits:

1.  **Defender Nihil Check:** If the defender has Nihil, skip offensive skill checks (Luna, Sol, Astra activation for the round) for the attacker.
2.  **Attacker Nihil Check:** If the attacker has Nihil, skip defensive skill checks (Pavise, Miracle) for the defender.
3.  **Defender Defensive Skill Check (Pavise/Miracle):**
    - Check if Miracle activates (HP threshold). If yes, set hit chance to 0 for this strike -> Strike misses. End strike processing.
    - Check if Pavise activates (Skill % roll). If yes, set incoming damage to 0. Mark Pavise as activated.
    **TEST:** `test_miracle_priority_over_pavise` (If Miracle activates, Pavise check is irrelevant)
    **TEST:** `test_pavise_checked_before_offensive_skills`
4.  **Attacker Offensive Skill Check (Luna):**
    - Check if Luna activates (Skill % roll). If yes, recalculate damage ignoring Def/Res. Mark Luna as activated.
    **TEST:** `test_luna_checked_after_defensive_skills`
5.  **Critical Hit Check:**
    - Check if the hit is critical (Crit % roll, considering PCC/caps, unless defender has Nihil or Scroll).
    - If critical and damage > 0, apply critical damage multiplier (x2).
6.  **Damage Application:**
    - Apply the final calculated damage (potentially 0 if Pavise activated) to the defender.
7.  **Attacker Healing Skill Check (Sol):**
    - Check if Sol activates (Skill % roll). If yes, heal the attacker for the final damage calculated *before* Pavise negation but *after* Luna modification and crit multiplication. Mark Sol as activated.
    **TEST:** `test_sol_checked_after_damage_application`

**Note:** Astra activation happens *before* the first strike is initiated and replaces the entire combat round structure. Adept activation happens *after* a strike resolves successfully.

## 5. Integration into `CombatSystem`

The `CombatSystem`'s `_perform_strike` method needs modification to handle these skills and their priority. Astra requires special handling outside the standard strike loop.

### 5.1. `execute_combat` Modifications
- Before initiating the first strike, check if the attacker has Astra and if the defender *does not* have Nihil.
- If Astra can activate, roll for activation (Skill %).
- If Astra activates:
    - Log Astra activation.
    - Enter a dedicated Astra loop:
        - Perform 5 strikes consecutively using `_perform_strike_astra_hit`.
        - Pass the hit index (1 to 5) to `_perform_strike_astra_hit` for correct PCC/crit cap application.
        - Apply the 0.5 damage multiplier within `_perform_strike_astra_hit`.
        - Check if the target is defeated after each hit; break loop if so.
    - Skip the standard counterattack and follow-up logic.
    - Proceed to post-combat updates (Fatigue, EXP/WExp based on Astra hits).
- If Astra does not activate (or cannot), proceed with the normal combat sequence (Vantage check, initial strike, counter, follow-up).

**TEST:** `test_execute_combat_calls_astra_loop_on_activation`
**TEST:** `test_execute_combat_skips_normal_flow_if_astra_activates`

### 5.2. `_perform_strike` Modifications
- Implement the skill interaction priority defined in Section 4.
- Add checks for attacker/defender Nihil at the start.
- Modify Pavise activation check to use Skill % instead of Level %.
- Ensure Sol healing calculation uses damage *before* Pavise negation.
- Ensure Luna damage recalculation happens correctly within the strike logic.
- Adept check remains at the end of a successful strike.

```python
# Pseudocode for _perform_strike incorporating skill priority

FUNCTION _perform_strike(striker, striker_stats, striker_weapon, target, target_stats, target_weapon, is_follow_up, is_astra_hit=False, astra_hit_index=0, force_crit=False):
    
    strike_log = initialize_strike_log(striker, target)
    
    IF NOT striker_weapon:
        strike_log.did_attack = False
        RETURN strike_log

    # --- Pre-Hit Checks ---
    defender_has_nihil = check_skill(target, NIHIL)
    attacker_has_nihil = check_skill(striker, NIHIL)

    # --- Hit Calculation ---
    hit_chance = calculate_hit_chance(...) # Base calculation

    # Defender Defensive Skills (Pre-Hit Modification)
    IF NOT attacker_has_nihil:
        IF check_skill(target, MIRACLE) AND target.current_hp <= 10:
            log_skill_activation(strike_log, MIRACLE)
            hit_chance = 0 # Miracle negates hit

    # --- Hit Roll ---
    IF random(1, 100) > hit_chance:
        log_miss(strike_log)
        decrement_durability(striker, striker_weapon)
        RETURN strike_log # Miss

    # --- Attack Hits ---
    log_hit(strike_log)
    
    base_dmg = calculate_base_damage(...) # Initial damage calculation
    actual_dmg = base_dmg
    is_crit = False
    
    # --- Post-Hit Skill Checks ---
    
    # 1. Defender Defensive Skills (Damage Negation)
    pavise_activated = False
    IF NOT attacker_has_nihil:
        IF check_skill(target, PAVISE) AND random(1, 100) <= target_stats.SKL: # Use SKL%
            log_skill_activation(strike_log, PAVISE)
            pavise_activated = True
            # Damage is negated later, but we note activation now

    # 2. Attacker Offensive Skills (Damage Modification)
    luna_activated = False
    IF NOT defender_has_nihil:
        IF check_skill(striker, LUNA) AND random(1, 100) <= striker_stats.SKL:
            log_skill_activation(strike_log, LUNA)
            luna_activated = True
            # Recalculate base_dmg ignoring defense/res
            base_dmg = calculate_damage_ignoring_defense(striker, striker_stats, striker_weapon, target, target_stats)
            actual_dmg = base_dmg # Update actual_dmg for potential crit/Sol

    # 3. Critical Hit Calculation
    IF base_dmg > 0 AND NOT defender_has_nihil AND NOT check_item_type(target, SCROLL):
        crit_chance = calculate_crit_chance(..., is_first_hit=(not is_follow_up and not is_astra_hit), pcc_multiplier=striker_stats.FCM, astra_hit_index=astra_hit_index)
        IF force_crit OR random(1, 100) <= crit_chance:
            is_crit = True
            log_crit(strike_log)
            # Crit multiplier applied after potential Pavise check

    # 4. Final Damage Calculation (Apply Pavise Negation)
    IF pavise_activated:
        actual_dmg = 0
    ELIF is_crit:
         actual_dmg = base_dmg * 2 # Apply crit multiplier only if Pavise didn't negate

    # Ensure damage is non-negative
    actual_dmg = max(0, actual_dmg)

    # Store damage before applying it, for Sol calculation
    damage_for_sol = actual_dmg 

    # Apply Pavise negation if it activated
    if pavise_activated:
        damage_to_apply = 0
    else:
        damage_to_apply = actual_dmg

    # 5. Damage Application
    apply_damage(target, damage_to_apply)
    strike_log.damage = damage_to_apply

    # 6. Attacker Healing Skills (Sol)
    sol_activated = False
    IF damage_for_sol > 0 AND NOT defender_has_nihil: # Check damage *before* Pavise negation
        IF check_skill(striker, SOL) AND random(1, 100) <= striker_stats.SKL:
            log_skill_activation(strike_log, SOL)
            sol_activated = True
            heal_amount = damage_for_sol # Heal based on damage before Pavise
            apply_healing(striker, heal_amount)

    # --- Post-Strike ---
    decrement_durability(striker, striker_weapon)
    apply_status_effects(striker_weapon, target)

    # Adept Check (Only if not an Astra hit)
    adept_strike = None
    IF NOT is_astra_hit AND strike_log.hit AND striker.current_hp > 0 AND target.current_hp > 0:
        IF check_skill(striker, ADEPT) AND NOT defender_has_nihil:
            IF random(1, 100) <= striker_stats.SKL:
                 log_skill_activation(strike_log, ADEPT) # Log Adept on the *original* strike
                 # Perform extra strike recursively (will be handled in execute_combat loop)
                 # Need a way to signal back to execute_combat to perform another strike
                 strike_log.adept_triggered = True # Flag for execute_combat

    RETURN strike_log

# Need a separate function for Astra hits to handle damage multiplier
FUNCTION _perform_strike_astra_hit(striker, striker_stats, striker_weapon, target, target_stats, target_weapon, hit_index):
    # Call _perform_strike with is_astra_hit=True, astra_hit_index=hit_index
    strike_result = _perform_strike(..., is_astra_hit=True, astra_hit_index=hit_index)
    
    # Apply Astra damage multiplier
    IF strike_result.hit:
        original_damage = strike_result.damage
        # Apply multiplier to the base damage *before* crit, then reapply crit if needed?
        # Let's recalculate based on base_dmg from the strike function for clarity
        
        # Need access to the base_dmg calculated *within* the _perform_strike call for this hit
        # Assume _perform_strike returns base_dmg before crit/pavise for this purpose
        base_damage_this_hit = strike_result.internal_base_dmg # Hypothetical return value
        
        astra_base_damage = floor(base_damage_this_hit * 0.5)
        
        # Recalculate final damage based on halved base, considering crit/pavise again
        final_astra_damage = astra_base_damage
        if strike_result.crit: # Check if crit was determined for this hit
            final_astra_damage *= 2
        if strike_result.skills_activated contains PAVISE: # Check if pavise activated
             final_astra_damage = 0
             
        final_astra_damage = max(0, final_astra_damage)

        # Correct the applied damage
        damage_diff = strike_result.damage - final_astra_damage
        apply_healing(target, damage_diff) # Undo the difference
        strike_result.damage = final_astra_damage 
        
        # Adjust Sol healing? If Sol activated, it should heal based on final_astra_damage
        if strike_result.skills_activated contains SOL:
             # Re-apply healing based on the correct damage? Requires careful state tracking.
             # Simpler: Assume Sol heals based on the final damage dealt (final_astra_damage).
             # The initial apply_healing in _perform_strike might need adjustment or re-triggering here.
             pass # Revisit Sol interaction with Astra multiplier


    RETURN strike_result

```

**TEST:** `test_perform_strike_skill_priority_order`
**TEST:** `test_perform_strike_pavise_uses_skill_stat`
**TEST:** `test_perform_strike_sol_heals_before_pavise_negation`
**TEST:** `test_perform_strike_adept_flag`
**TEST:** `test_perform_strike_astra_hit_damage_multiplier`

## 6. Open Questions / Considerations
- **Astra Damage Multiplier Application Point:** Does the 0.5x multiplier apply to the base damage *before* defense/crit, or to the final damage *after* defense/crit? The pseudocode was updated to apply it to the base damage before crit/pavise for potentially more accurate interaction, but this needs verification against Thracia 776 behavior.
- **Sol Healing Basis with Astra:** If Sol activates on an Astra hit, does it heal based on the pre-multiplier damage or the final 0.5x damage? The updated pseudocode implies it should heal based on the final (halved) damage dealt.
- **Status Effects:** Confirm if Pavise negates status effects applied by weapons, or only damage. Spec assumes only damage is negated.

This specification provides a detailed plan for implementing these skills. The pseudocode outlines the necessary logic changes within the combat system.