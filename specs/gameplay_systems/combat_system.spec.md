# Specification: Combat System

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The Combat System orchestrates battles between units. It calculates the outcome of attacks based on unit stats, equipment, skills, terrain, and support bonuses, following the specific mechanics of Thracia 776. It determines hit rates, damage, critical hits, follow-up attacks (doubling), and applies the results, including HP changes, status effects, fatigue gain, and experience/weapon experience gain. It also handles the unique Capture combat mechanics. This system interacts heavily with `GameStateManager`, `DataProvider`, `UnitSystem`, `MapSystem`, and `InventorySystem`.

## 2. Functional Requirements

### 2.1. Combat Initiation
    - Triggered when a unit selects the "Attack" or "Capture" command targeting an adjacent or in-range enemy unit.
    - Triggered when a unit uses an offensive staff targeting another unit.
    - Triggered when an enemy unit attacks during the Enemy Phase.

### 2.2. Combat Simulation (Forecast)
    - Provide a function `simulate_combat(attacker_id, defender_id, is_capture=False)` that predicts the outcome without applying changes.
    - Calculate and return:
        - Attacker's predicted Damage per hit (DMG).
        - Attacker's predicted Hit Rate (HIT) against the defender (capped 1-99%).
        - Attacker's predicted Critical Rate (CRT) against the defender (considering PCC rules and 25% cap on first hit).
        - Defender's predicted Damage per hit (DMG).
        - Defender's predicted Hit Rate (HIT) against the attacker (capped 1-99%).
        - Defender's predicted Critical Rate (CRT) against the attacker (considering PCC rules and 25% cap on first hit).
        - Indication if attacker/defender will perform a follow-up attack (double).
    - This simulation uses the detailed calculation formulas (see Section 4).

### 2.3. Combat Execution
    - Provide a function `execute_combat(attacker_id, defender_id, is_capture=False)` that performs the combat round step-by-step.
    - **Order of Operations:** (Ref: `research.md`, Sec 1, 5.4)
        1.  **Attacker's First Strike:**
            - Roll for hit (1 RN vs calculated Hit Rate).
            - If hit, roll for critical (vs calculated Crit Rate, capped at 25%).
            - If hit, calculate damage (apply crit bonus if applicable).
            - Apply damage to defender (`GameStateManager.apply_damage`).
            - Check for skill activations (e.g., Sol, Luna, Pavise on hit/defense). Apply effects.
            - Check if defender is defeated. If so, end combat sequence early.
        2.  **Defender's Counterattack:** (If defender survived and is in range)
            - Roll for hit.
            - If hit, roll for critical (vs calculated Crit Rate, capped at 25%; Wrath skill overrides).
            - If hit, calculate damage.
            - Apply damage to attacker.
            - Check for skill activations.
            - Check if attacker is defeated. If so, end combat sequence early.
        3.  **Attacker's Follow-Up Strike:** (If attacker's AS >= defender's AS + 4)
            - Roll for hit.
            - If hit, roll for critical (vs calculated Crit Rate * PCC, no 25% cap).
            - If hit, calculate damage.
            - Apply damage to defender.
            - Check for skill activations.
            - Check if defender is defeated.
        4.  **Defender's Follow-Up Strike:** (If defender's AS >= attacker's AS + 4 and defender survived previous hits)
            - Roll for hit.
            - If hit, roll for critical (vs calculated Crit Rate * PCC, no 25% cap; Wrath overrides).
            - If hit, calculate damage.
            - Apply damage to attacker.
            - Check for skill activations.
            - Check if attacker is defeated.
        *Note: Brave weapons add an immediate second strike during the attacker's first action phase. Adept skill can add extra strikes.*
    - **Post-Combat Updates:**
        - Decrement weapon durability for attacker/defender for each strike made (`InventorySystem.decrement_item_durability`).
        - Award EXP/WExp (`GameStateManager.apply_exp`, `GameStateManager.apply_wexp`).
        - Apply status effects from weapons/skills (`GameStateManager.add_status_effect`).
        - Update fatigue for participants (`GameStateManager.update_fatigue`).
        - Handle unit death/capture state changes (`GameStateManager`).

### 2.4. Capture Combat
    - If `is_capture=True` during initiation:
        - Apply stat penalties to the *attacker* for the duration of the combat simulation/execution: Str, Mag, Skl, Spd, Def are halved (Ref: `research.md`, Sec 5.5). Luck, Con, Mov are unaffected.
        - Execute combat sequence as normal using the penalized stats for the attacker.
        - If the defender's HP reaches 0 during the capture attempt, the defender is marked as captured (`GameStateManager` sets state, attacker starts carrying). They are not marked as dead.

### 2.5. Staff Combat (Offensive)
    - Provide `execute_staff_attack(caster_id, target_id, staff_item_index)`.
    - Calculate Staff Hit Rate (Base + 4*Skill, capped 99%) (Ref: `research.md`, Sec 5.1).
    - Roll for hit (1 RN).
    - If hit, apply the staff's effect (e.g., status via `GameStateManager.add_status_effect`). Target's Magic/Resistance does not affect hit chance in Thracia.
    - Decrement staff durability (`InventorySystem.decrement_item_durability`).
    - Update caster's fatigue based on staff rank (`GameStateManager.update_fatigue`).
    - Award WExp to caster (`GameStateManager.apply_wexp`).

## 4. Combat Calculation Formulas (Thracia 776 Specific)

*References primarily from `research.md` Sections 2, 4, 5, 12.*

### 4.1. Attack Speed (AS)
    - `AS = Speed – Effective_Weapon_Weight`
    - `Effective_Weapon_Weight (Physical) = max(0, Weapon_Weight – Constitution)`
    - `Effective_Weapon_Weight (Magic Tome) = Weapon_Weight` (Con does not offset tome weight)
    - *Source: `research.md`, Sec 2*

### 4.2. Hit Rate (Displayed)
    - `Attacker_Base_Hit = Weapon_Hit + (2 * Skill) + Luck + Support_Bonus + Leadership_Bonus + Charisma_Bonus`
    - `Defender_Avoid = (2 * Defender_AS) + Defender_Luck + Support_Bonus + Leadership_Bonus + Charisma_Bonus + Terrain_Avoid_Bonus` (Terrain bonus only if applicable based on unit type/state)
    - `Weapon_Triangle_Bonus = +5 (Advantage), -5 (Disadvantage), 0 (Neutral)`
        - Swords > Axes > Lances > Swords
        - Fire > Wind > Thunder > Fire
        - Light/Dark > Anima (Effectively +5 vs Fire/Wind/Thunder)
    - `Displayed_Hit_Rate = Attacker_Base_Hit - Defender_Avoid + Weapon_Triangle_Bonus`
    - **Result capped between 1% and 99%.**
    - *Source: `research.md`, Sec 5.1*

### 4.3. Damage (DMG)
    - `Effective_Might = Weapon_Might * Effectiveness_Multiplier`
        - `Effectiveness_Multiplier = 3` if weapon is effective vs target type (e.g., Rapier vs Armor/Cav), else `1`.
    - `Physical_Damage = (Attacker_Strength + Effective_Might) - Defender_Physical_Defense`
        - `Defender_Physical_Defense = Defender_Defense + Terrain_Defense_Bonus`
    - `Magical_Damage = (Attacker_Magic + Effective_Might) - Defender_Magical_Defense`
        - `Defender_Magical_Defense = Defender_Magic + Terrain_Magic_Bonus + Temporary_Magic_Bonuses` (e.g., M Up/Holy Water)
    - Magic Swords (e.g., Light Brand) use Magical Damage formula when attacking at range 2. Melee usage might still use Magic stat (needs verification, assume Magic for now based on research note).
    - Minimum damage is 0.
    - *Source: `research.md`, Sec 5.2*

### 4.4. Critical Rate (CRT)
    - `Attacker_Base_Crit = Weapon_Crit + Attacker_Skill + Support_Bonus`
    - `Defender_Crit_Evade (Ddg) = floor(Defender_Luck / 2) + Support_Bonus`
    - `Calculated_Crit_Rate = Attacker_Base_Crit - Defender_Crit_Evade`
    - **Combat Critical Rate (First Hit):** `min(25, max(0, Calculated_Crit_Rate))`
    - **Combat Critical Rate (Follow-Up/Adept/Brave Hits > 1):** `min(100, max(0, Calculated_Crit_Rate * Attacker_PCC))` (PCC = Pursuit Critical Coefficient / FCM)
    - **Wrath Skill:** If active (defender counterattacking), CRT = 100%, overrides PCC and 25% cap.
    - **Scrolls:** If defender holds a scroll, Attacker's CRT becomes 0 (unless attacker has Wrath).
    - **Nihil Skill:** If defender has Nihil, Attacker's CRT becomes 0 (needs confirmation if Nihil blocks crits in FE5, assume yes for now).
    - *Source: `research.md`, Sec 5.3*

### 4.5. Critical Damage Bonus
    - If a critical hit occurs: `Final_Damage = Calculated_Damage * 2`
    - Damage is doubled *after* defense mitigation.
    - *Source: `research.md`, Sec 5.2, 5.3*

### 4.6. Follow-Up Attack (Doubling)
    - Attacker doubles if `Attacker_AS >= Defender_AS + 4`.
    - Defender doubles if `Defender_AS >= Attacker_AS + 4`.
    - Only one follow-up attack per unit per round from AS difference.
    - *Source: `research.md`, Sec 2, 5.4*

### 4.7. Staff Accuracy (Offensive)
    - `Staff_Hit_Rate = Base_Staff_Hit + (4 * Caster_Skill)`
    - Base_Staff_Hit = 60% for most, 100% for Torch.
    - **Result capped between 1% and 99%.**
    - Target's Magic/Resistance does *not* affect hit chance.
    - *Source: `research.md`, Sec 5.1*

## 5. Skill Integration

- **Wrath:** Check if defender has Wrath during counterattack phase. If so, force critical hit.
- **Adept (Continue):** After a unit completes their normal attack(s), roll `Skill%` chance for an extra attack. This extra attack uses follow-up critical rules (PCC applies). Can potentially trigger multiple times.
- **Miracle (Prayer):** Before applying damage, check if defender has Miracle and HP is below threshold (e.g., <= 10). If active, set attacker's hit chance to 0 for that strike. (Needs clarification on exact activation trigger/limit).
- **Nihil:** Check if defender has Nihil. If so, negate attacker's combat skills (Sol, Luna, etc.) and critical hits for that engagement.
- **Sol/Luna:** Check if attacker has skill. Roll activation chance (e.g., Skill%?). If Sol activates, heal attacker for damage dealt. If Luna activates, ignore defender's Def/Res for that strike.
- **Pavise:** Check if defender has skill. Roll activation chance (e.g., Level%?). If active, negate all damage from that hit.
- **Astra (Mareeta's Sword):** Special case. If attacker uses Mareeta's Sword, trigger 5 consecutive hits. Apply PCC rules after the first hit.
- **Scrolls (Passive):** Check defender's inventory. If scroll present, negate attacker's critical chance (unless attacker has Wrath). Growth boosts handled by UnitSystem/Level Up.
- **Charisma/Supports/Leadership:** Bonuses are factored directly into Hit/Avoid/Crit/Ddg calculations (see Section 4).

## 6. Post-Combat Updates

- **HP:** Update `current_hp` for attacker and defender via `GameStateManager.apply_damage`. Check for death/capture.
- **Durability:** Call `InventorySystem.decrement_item_durability` for weapons/staves used by attacker/defender.
- **Fatigue:** Call `GameStateManager.update_fatigue(unit_id, 1)` for both participants (attacker/defender) for each combat round they participated in (attacking or counterattacking). Staff usage fatigue handled separately. (Ref: `research.md`, Sec 7).
- **EXP:** Calculate and award EXP via `GameStateManager.apply_exp`. Base EXP depends on killing blow, damage dealt, level difference.
- **WExp:** Calculate and award WExp via `GameStateManager.apply_wexp`. Typically +1 WExp per hit landed with weapon/staff (staff WExp varies by rank). Trigger rank up checks via `UnitSystem`. (Ref: `research.md`, Sec 4).
- **Status:** Apply status effects from weapons (e.g., Poison Bow) via `GameStateManager.add_status_effect`.

## 7. Pseudocode (combat_system.py)

```python
# --- combat_system.py ---

import random # For RN rolls

# Import necessary modules (GameStateManager, DataProvider, UnitSystem, MapSystem, InventorySystem)
# Import enums, CombatResult data structure

class CombatSystem:
    gameStateManager = null
    dataProvider = null
    unitSystem = null
    mapSystem = null
    inventorySystem = null

    function initialize(gs_manager, d_provider, u_system, m_system, i_system):
        gameStateManager = gs_manager
        dataProvider = d_provider
        unitSystem = u_system
        mapSystem = m_system
        inventorySystem = i_system
        log("CombatSystem initialized.")

    # --- Combat Simulation (Forecast) ---

    # TDD: Test simulate_combat predicts correct Hit/Dmg/Crit/Double for various scenarios (WT, skills, terrain, stats)
    function simulate_combat(attacker_id, defender_id, is_capture=False):
        attacker = gameStateManager.get_unit(attacker_id)
        defender = gameStateManager.get_unit(defender_id)
        if not attacker or not defender: return None

        # Calculate stats for both units, considering capture penalty if applicable
        attacker_stats = unitSystem.calculate_current_combat_stats(attacker_id)
        defender_stats = unitSystem.calculate_current_combat_stats(defender_id)

        if is_capture:
            # Apply capture penalty to attacker's relevant stats for simulation
            # (Modify a copy of attacker_stats for the simulation)
            apply_capture_penalty_to_stats(attacker_stats) # Helper function

        # Get weapon data
        attacker_weapon = get_equipped_weapon_data(attacker)
        defender_weapon = get_equipped_weapon_data(defender) # Check if defender can counter

        # Calculate Attacker -> Defender forecast
        atk_hit, atk_dmg, atk_crit = calculate_single_attack_outcome(
            attacker, attacker_stats, attacker_weapon, 
            defender, defender_stats, defender_weapon, 
            is_first_hit=True, pcc_multiplier=attacker_stats['FCM']
        )

        # Calculate Defender -> Attacker forecast (if defender can counter)
        def_hit, def_dmg, def_crit = (0, 0, 0)
        if defender_can_counter(attacker, defender, defender_weapon):
             def_hit, def_dmg, def_crit = calculate_single_attack_outcome(
                 defender, defender_stats, defender_weapon, 
                 attacker, attacker_stats, attacker_weapon, 
                 is_first_hit=True, pcc_multiplier=defender_stats['FCM']
             )
        
        # Check doubling
        attacker_doubles = attacker_stats['AS'] >= defender_stats['AS'] + 4
        defender_doubles = defender_stats['AS'] >= attacker_stats['AS'] + 4

        forecast = {
            'attacker': {'dmg': atk_dmg, 'hit': atk_hit, 'crit': atk_crit, 'doubles': attacker_doubles},
            'defender': {'dmg': def_dmg, 'hit': def_hit, 'crit': def_crit, 'doubles': defender_doubles}
        }
        return forecast

    # --- Combat Execution ---

    # TDD: Test execute_combat applies correct damage, handles death/capture, updates fatigue/exp/wexp, decrements durability
    # TDD: Test combat flow respects doubling, skills (Wrath, Adept), brave weapons
    function execute_combat(attacker_id, defender_id, is_capture=False):
        attacker = gameStateManager.get_unit(attacker_id)
        defender = gameStateManager.get_unit(defender_id)
        if not attacker or not defender: return None

        log(f"Executing combat: {attacker.name} vs {defender.name} {'(Capture)' if is_capture else ''}")

        # Store initial state for EXP calculation etc.
        initial_attacker_hp = attacker.current_hp
        initial_defender_hp = defender.current_hp

        # Get base stats and weapon data
        attacker_stats_base = unitSystem.calculate_current_combat_stats(attacker_id)
        defender_stats_base = unitSystem.calculate_current_combat_stats(defender_id)
        attacker_weapon = get_equipped_weapon_data(attacker)
        defender_weapon = get_equipped_weapon_data(defender)

        # Apply capture penalty if needed (modify a working copy of stats)
        attacker_stats = dict(attacker_stats_base)
        defender_stats = dict(defender_stats_base)
        if is_capture:
            apply_capture_penalty_to_stats(attacker_stats)

        # Determine combat sequence parameters
        attacker_doubles = attacker_stats['AS'] >= defender_stats['AS'] + 4
        defender_doubles = defender_stats['AS'] >= attacker_stats['AS'] + 4
        defender_can_ctr = defender_can_counter(attacker, defender, defender_weapon)
        
        # --- Combat Round ---
        combat_log = [] # Store events for display/result processing

        # 1. Attacker's First Strike(s)
        num_attacker_hits = 1
        if attacker_weapon and attacker_weapon.is_brave: num_attacker_hits = 2 # Check for brave effect
        
        for i in range(num_attacker_hits):
             if attacker.current_hp > 0 and defender.current_hp > 0:
                  strike_result = perform_strike(attacker, attacker_stats, attacker_weapon, defender, defender_stats, defender_weapon, is_follow_up=(i > 0))
                  combat_log.append(strike_result)
                  if defender.current_hp <= 0: break # Stop if defender falls

        # 2. Defender's Counterattack(s)
        if defender.current_hp > 0 and attacker.current_hp > 0 and defender_can_ctr:
             num_defender_hits = 1 # Check for brave on counter? Unlikely. Check for Adept?
             # Check for Wrath activation
             has_wrath = dataProvider.unit_has_skill(defender_id, WRATH) # Need skill check

             for i in range(num_defender_hits):
                  if attacker.current_hp > 0 and defender.current_hp > 0:
                       strike_result = perform_strike(defender, defender_stats, defender_weapon, attacker, attacker_stats, attacker_weapon, is_follow_up=(i > 0), force_crit=has_wrath)
                       combat_log.append(strike_result)
                       if attacker.current_hp <= 0: break # Stop if attacker falls

        # 3. Attacker's Follow-Up Strike
        if attacker.current_hp > 0 and defender.current_hp > 0 and attacker_doubles:
             strike_result = perform_strike(attacker, attacker_stats, attacker_weapon, defender, defender_stats, defender_weapon, is_follow_up=True)
             combat_log.append(strike_result)

        # 4. Defender's Follow-Up Strike
        if defender.current_hp > 0 and attacker.current_hp > 0 and defender_can_ctr and defender_doubles:
             has_wrath = dataProvider.unit_has_skill(defender_id, WRATH) # Check Wrath again? Or assume it applies to all counters? Assume applies if countering.
             strike_result = perform_strike(defender, defender_stats, defender_weapon, attacker, attacker_stats, attacker_weapon, is_follow_up=True, force_crit=has_wrath)
             combat_log.append(strike_result)
             
        # --- Post-Combat Updates ---
        attacker_participated = any(r['attacker_id'] == attacker_id for r in combat_log if r['did_attack'])
        defender_participated = any(r['attacker_id'] == defender_id for r in combat_log if r['did_attack'])

        # Fatigue
        if attacker_participated: gameStateManager.update_fatigue(attacker_id, 1)
        if defender_participated: gameStateManager.update_fatigue(defender_id, 1)

        # Check final death/capture state
        attacker_survived = attacker.current_hp > 0
        defender_survived = defender.current_hp > 0

        if not defender_survived:
            if is_capture:
                 gameStateManager.set_unit_captured(defender_id, attacker_id)
                 log(f"{defender.name} captured by {attacker.name}!")
            else:
                 gameStateManager.set_unit_dead(defender_id)
                 log(f"{defender.name} defeated!")
        
        if not attacker_survived:
             # Can attacker be captured? Check rules. Assume death for now.
             gameStateManager.set_unit_dead(attacker_id)
             log(f"{attacker.name} defeated!")

        # Award EXP/WExp (based on combat_log, initial HPs, final states)
        award_exp_wexp(combat_log, initial_attacker_hp, initial_defender_hp, attacker_survived, defender_survived, is_capture)

        log(f"Combat finished between {attacker.name} and {defender.name}.")
        return combat_log # Return detailed log of events

    # --- Helper: Perform Single Strike ---
    function perform_strike(striker, striker_stats, striker_weapon, target, target_stats, target_weapon, is_follow_up, force_crit=False):
        strike_log = {'attacker_id': striker.id, 'target_id': target.id, 'did_attack': True, 'hit': False, 'crit': False, 'damage': 0, 'skills_activated': []}

        if not striker_weapon: 
             strike_log['did_attack'] = False
             return strike_log # Cannot attack without weapon

        # Calculate Hit/Dmg/Crit for this specific strike
        hit_chance, base_dmg, crit_chance = calculate_single_attack_outcome(
            striker, striker_stats, striker_weapon, 
            target, target_stats, target_weapon, 
            is_first_hit=(not is_follow_up), pcc_multiplier=striker_stats['FCM']
        )
        
        # Check defender skills (Miracle, Pavise) before hit roll? Assume Miracle checked here.
        if dataProvider.unit_has_skill(target.id, MIRACLE) and target.current_hp <= 10: # Check Miracle
             # Roll Miracle activation? Or assume it works? Assume works for now.
             log(f"{target.name}'s Miracle activated!")
             strike_log['skills_activated'].append(MIRACLE)
             hit_chance = 0 # Negates hit

        # Roll Hit (1 RN)
        if random.randint(1, 100) <= hit_chance:
            strike_log['hit'] = True
            
            # Check defender skills (Pavise) before damage calc
            if dataProvider.unit_has_skill(target.id, PAVISE):
                 # Roll Pavise activation (Level%?)
                 if random.randint(1, 100) <= target.level: # Placeholder activation
                      log(f"{target.name}'s Pavise activated!")
                      strike_log['skills_activated'].append(PAVISE)
                      base_dmg = 0 # Negates damage

            actual_dmg = base_dmg
            is_crit = False
            
            # Roll Crit (1 RN) - check Nihil first
            if base_dmg > 0 and not dataProvider.unit_has_skill(target.id, NIHIL):
                 if force_crit or random.randint(1, 100) <= crit_chance:
                      is_crit = True
                      actual_dmg *= 2 # Apply crit bonus
                      strike_log['crit'] = True
                      log("Critical Hit!")

            # Check attacker skills (Sol, Luna) - check Nihil first
            if base_dmg > 0 and not dataProvider.unit_has_skill(target.id, NIHIL):
                 if dataProvider.unit_has_skill(striker.id, LUNA):
                      # Roll Luna activation (Skill%?)
                      if random.randint(1, 100) <= striker_stats['SKL']: # Placeholder activation
                           log(f"{striker.name}'s Luna activated!")
                           strike_log['skills_activated'].append(LUNA)
                           # Recalculate damage ignoring defense
                           actual_dmg = calculate_damage_ignoring_defense(striker, striker_stats, striker_weapon, target, target_stats, is_crit)
                 
                 if dataProvider.unit_has_skill(striker.id, SOL):
                      # Roll Sol activation (Skill%?)
                      if random.randint(1, 100) <= striker_stats['SKL']: # Placeholder activation
                           log(f"{striker.name}'s Sol activated!")
                           strike_log['skills_activated'].append(SOL)
                           gameStateManager.apply_healing(striker.id, actual_dmg) # Heal for damage dealt

            # Apply final damage
            gameStateManager.apply_damage(target.id, actual_dmg)
            strike_log['damage'] = actual_dmg
            
            # Apply weapon status effects (e.g., Poison)
            apply_weapon_status_effects(striker_weapon, target.id)

        else: # Miss
            log("Attack missed.")
            strike_log['hit'] = False

        # Decrement weapon durability
        inventorySystem.decrement_item_durability(striker.id, striker.equipped_weapon_index)

        return strike_log

    # --- Helper: Calculate Single Attack Outcome ---
    # TDD: Test calculation reflects formulas for Hit/Dmg/Crit accurately
    function calculate_single_attack_outcome(striker, striker_stats, striker_weapon, target, target_stats, target_weapon, is_first_hit, pcc_multiplier):
        if not striker_weapon: return 0, 0, 0

        # 1. Calculate Base Hit vs Avoid
        base_hit = striker_stats['hit'] # Already calculated by UnitSystem
        target_avo = target_stats['avo'] # Already calculated by UnitSystem
        
        # 2. Weapon Triangle
        wt_bonus = dataProvider.get_weapon_triangle_bonus(striker_weapon.weapon_type, target_weapon.weapon_type if target_weapon else None)
        
        # 3. Final Hit Chance (Capped 1-99)
        hit_chance = max(1, min(99, base_hit - target_avo + wt_bonus))

        # 4. Calculate Base Damage
        effectiveness_mult = dataProvider.get_effectiveness_multiplier(striker_weapon.id, target.class_id) # Need DP helper
        effective_might = striker_weapon.might * effectiveness_mult
        
        target_def = 0
        if dataProvider.is_weapon_physical(striker_weapon.weapon_type):
             target_def = target_stats['DEF'] + mapSystem.get_terrain_bonus(target.position).get('def', 0) # Use calculated DEF + terrain
        else: # Magical
             target_def = target_stats['MAG'] # Use calculated MAG (includes MUp etc.) + terrain
             # Need to refine target_stats calculation in UnitSystem to include temp boosts

        base_dmg = max(0, (striker_stats['atk'] - target_def)) # Use calculated Atk

        # 5. Calculate Crit Chance
        base_crit = striker_stats['crit'] # From UnitSystem calc
        target_ddg = target_stats['ddg'] # From UnitSystem calc
        calculated_crit = max(0, base_crit - target_ddg)

        # Apply PCC / First Hit Cap / Scroll / Nihil rules
        crit_chance = 0
        if not dataProvider.unit_has_item_type(target.id, SCROLL) and not dataProvider.unit_has_skill(target.id, NIHIL):
             if is_first_hit:
                  crit_chance = min(25, calculated_crit)
             else: # Follow-up
                  crit_chance = min(100, calculated_crit * pcc_multiplier)
        
        # Wrath override handled in perform_strike

        return hit_chance, base_dmg, crit_chance

    # ... other helpers: apply_capture_penalty_to_stats, get_equipped_weapon_data, defender_can_counter, award_exp_wexp, apply_weapon_status_effects etc.

```

## 8. Integration Points

- **GameStateManager:** Reads unit states (HP, stats, position, status, fatigue, inventory, skills). Writes updates to HP, status, fatigue, EXP, WExp, unit disposition (dead/captured).
- **DataProvider:** Reads static data: item stats (Mt, Hit, Crit, Wt, Rng, Dur, Type, Rank, Effects, Effectiveness), class data (skills, movement type), terrain bonuses, skill effects, weapon triangle rules, support bonuses, leadership stars, PCC values.
- **UnitSystem:** Provides calculated base combat stats (`calculate_current_combat_stats`) considering equipment, status, terrain, supports etc. Handles level ups and rank ups triggered by EXP/WExp gain.
- **MapSystem:** Provides terrain bonus information (`get_terrain_bonus`) and adjacency checks (`are_units_adjacent`). Provides line-of-sight checks if needed.
- **InventorySystem:** Called to decrement weapon/staff durability (`decrement_item_durability`) and handle item breaking. Reads equipped weapon data.
- **EngineCore/ActionHandler:** Initiates combat simulation (`simulate_combat`) for forecasts and execution (`execute_combat`, `execute_staff_attack`) based on player/AI actions.

## 9. Open Questions/Future Considerations

- Finalize activation chances/conditions for skills (Adept, Miracle, Luna, Sol, Pavise).
- Confirm if Nihil negates critical hits in Thracia 776.
- Confirm exact EXP/WExp award formulas.
- Confirm if/how Magic Swords use Magic stat in melee.
- Refine `calculate_single_attack_outcome` to handle edge cases like 0 damage crits (should still be 0).
- Implement detailed EXP/WExp awarding logic in `award_exp_wexp`.
- Implement helper functions (`apply_capture_penalty...`, `get_equipped_weapon...`, `defender_can_counter...`, etc.).