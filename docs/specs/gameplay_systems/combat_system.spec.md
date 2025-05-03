# Combat System Specification

## 1. Overview

The Combat System manages all direct confrontations between units on the map. It calculates the outcome of attacks, including hit rates, damage, critical hits, follow-up attacks, and incorporates special mechanics like the weapon triangle, skills, terrain effects, support bonuses, leadership, fatigue, and the unique Capture mechanic from Thracia 776.

## 2. Dependencies

*   **Unit System (`unit_system.spec.md`):** Provides unit stats (HP, Str, Mag, Skl, Spd, Luk, Def, Con, Mov), skills, status effects, fatigue level, weapon ranks, PCC (FCM), leadership stars, and inventory.
*   **Item System (`item_system.spec.md`):** Provides weapon stats (Mt, Hit, Crit, Wt, Rng, Durability, Rank, Type, Effectiveness), scroll effects (crit negation), and staff properties.
*   **Map System (`map_system.spec.md`):** Provides terrain information (Avoid bonus, Defense bonus, movement costs affecting positioning).
*   **AI Manager (`ai_manager.spec.md`):** Determines enemy target selection and action choices (Attack, Capture, Staff).
*   **Event System (`event_handler.spec.md`):** May trigger specific combat scenarios or apply unique effects based on map events.
*   **Game State Manager (`game_state_manager.spec.md`):** Provides access to the overall game state, including unit positions, turn count, and active bonuses.

## 3. Core Combat Flow

Combat is initiated when a unit selects the "Attack" or "Capture" command against a valid target in range.

1.  **Initiation:** The initiating unit attacks first.
2.  **Counterattack:** If the defending unit survives the initial attack(s) and has a weapon capable of attacking back at the engagement range, they counterattack.
3.  **Follow-up Attacks (Doubling):**
    *   If the initiator's Attack Speed (AS) is 4 or more points higher than the defender's AS, the initiator performs a follow-up attack after the counterattack (if any).
    *   If the defender's AS is 4 or more points higher than the initiator's AS, the defender performs a follow-up attack after their initial counterattack (if they initiated one).
    *   Brave weapons grant an immediate second attack *before* any counterattack. If the wielder also meets the AS threshold for doubling, they can potentially attack four times (Initial Hit -> Brave Hit -> Counterattack -> Follow-up Hit -> Follow-up Brave Hit).

**Combat Sequence Example (Attacker Doubles):**

1.  Attacker's First Strike
2.  Defender's Counterattack (if possible and survives)
3.  Attacker's Follow-up Strike

**Combat Sequence Example (Attacker with Brave Weapon, also Doubles):**

1.  Attacker's First Strike
2.  Attacker's Brave Strike
3.  Defender's Counterattack (if possible and survives)
4.  Attacker's Follow-up Strike
5.  Attacker's Follow-up Brave Strike

## 4. Combat Calculations

These calculations determine the outcome of each individual strike within a combat round.

### 4.1. Attack Speed (AS)

*   **Purpose:** Determines follow-up attacks and contributes to Avoid.
*   **Formula:**
    *   For Physical Weapons: `AS = Unit_Speed - MAX(0, Weapon_Weight - Unit_Constitution)`
    *   For Magical Weapons (Tomes): `AS = Unit_Speed - Weapon_Weight` (Con does not offset tome weight in Thracia 776)
*   **Inputs:** Unit Speed (Spd), Unit Constitution (Con), Weapon Weight (Wt).
*   **Output:** Attack Speed value (integer).

### 4.2. Hit Rate (Accuracy)

*   **Purpose:** Base chance for an attack to connect before considering enemy evasion.
*   **Formula:** `Hit = Weapon_Hit + (2 * Unit_Skill) + Unit_Luck + Support_Bonus + Leadership_Bonus + Charisma_Bonus + Weapon_Triangle_Bonus`
*   **Inputs:** Weapon Hit, Unit Skill (Skl), Unit Luck (Luk), Sum of active Support Bonuses (capped at +30), Total Allied Leadership Stars * 3, Sum of active Charisma Bonuses (+10 per source within 3 tiles), Weapon Triangle Bonus (+5 advantage, -5 disadvantage, 0 neutral).
*   **Output:** Base Hit Rate (integer).

### 4.3. Avoid Rate (Evasion)

*   **Purpose:** Base chance for a unit to evade an incoming attack.
*   **Formula:** `Avoid = (2 * Unit_Attack_Speed) + Unit_Luck + Support_Bonus + Leadership_Bonus + Charisma_Bonus + Terrain_Avoid_Bonus`
*   **Inputs:** Unit Attack Speed (AS), Unit Luck (Luk), Sum of active Support Bonuses (capped at +30), Total Allied Leadership Stars * 3, Sum of active Charisma Bonuses (+10 per source within 3 tiles), Terrain Avoid Bonus (%).
*   **Note:** Mounted units only gain terrain bonuses when dismounted. Flying units gain 0 terrain bonus.
*   **Output:** Base Avoid Rate (integer).

### 4.4. Battle Hit Chance

*   **Purpose:** The actual displayed chance for an attack to hit in combat.
*   **Formula:** `Battle_Hit_Chance = Attacker_Hit_Rate - Defender_Avoid_Rate`
*   **Constraints:** Capped between 1% and 99%. Thracia 776 uses 1 RN system (displayed = actual).
*   **Inputs:** Attacker's calculated Hit Rate, Defender's calculated Avoid Rate.
*   **Output:** Final Hit Chance percentage (1-99).

### 4.5. Damage

*   **Purpose:** Calculates HP reduction upon a successful hit.
*   **Physical Damage Formula:** `Damage = (Attacker_Strength + (Weapon_Might * Effective_Bonus)) - Defender_Physical_Defense`
    *   `Defender_Physical_Defense = Defender_Defense + Terrain_Defense_Bonus`
*   **Magical Damage Formula:** `Damage = (Attacker_Magic + (Weapon_Might * Effective_Bonus)) - Defender_Magical_Defense`
    *   `Defender_Magical_Defense = Defender_Magic + Terrain_Defense_Bonus + Temporary_Magic_Bonuses` (e.g., M Up/Pure Water)
*   **Effective Bonus:** 3 if the weapon is effective against the defender's class/type, 1 otherwise.
*   **Magic Swords (e.g., Light Brand, Flame Sword):**
    *   At Range 1: Typically uses **Physical Damage** formula (Attacker_Strength vs Defender_Defense). *[Needs confirmation if some use Magic stat at Range 1]*.
    *   At Range 2: Uses **Magical Damage** formula (Attacker_Magic vs Defender_Magic).
*   **Minimum Damage:** Damage cannot be less than 0. If calculation results in negative, damage is 0.
*   **Inputs:** Attacker Str/Mag, Weapon Mt, Effective Bonus multiplier, Defender Def/Mag, Terrain Def Bonus, Temporary Magic Bonuses.
*   **Output:** Damage value (integer, >= 0).

### 4.6. Critical Rate (Base)

*   **Purpose:** Base chance for an attack to be a critical hit before considering PCC and enemy evasion.
*   **Formula:** `Base_Crit_Rate = Weapon_Crit + Unit_Skill + Support_Bonus`
*   **Inputs:** Weapon Critical (%), Unit Skill (Skl), Sum of active Support Bonuses (capped at +30).
*   **Output:** Base Critical Rate (integer).

### 4.7. Critical Evade (Dodge / Ddg)

*   **Purpose:** Reduces the enemy's chance to land a critical hit.
*   **Formula:** `Crit_Evade = FLOOR(Unit_Luck / 2) + Support_Bonus`
*   **Inputs:** Unit Luck (Luk), Sum of active Support Bonuses (capped at +30).
*   **Output:** Critical Evade value (integer).

### 4.8. Battle Critical Chance

*   **Purpose:** The actual chance for an attack to be a critical hit in combat.
*   **Formula:**
    1.  Calculate Potential Crit: `Potential_Crit = Attacker_Base_Crit_Rate - Defender_Crit_Evade`
    2.  Apply PCC and Caps:
        *   **First Attack in Round:** `Battle_Crit_Chance = MIN(25, MAX(0, Potential_Crit))` (Capped at 25%)
        *   **Subsequent Attacks (Follow-up, Brave, Adept):** `Battle_Crit_Chance = MIN(100, MAX(0, Potential_Crit * Attacker_PCC))` (PCC multiplier applied, capped at 100%)
*   **Special Cases:**
    *   **Wrath Skill:** If active (counterattacking/enemy phase), `Battle_Crit_Chance = 100`. Overrides Scrolls.
    *   **Scrolls:** If the defender holds a Crusader Scroll, `Battle_Crit_Chance = 0` (unless Wrath is active).
    *   **Nihil Skill:** If the defender has Nihil, `Battle_Crit_Chance = 0`.
*   **Inputs:** Attacker Base Crit Rate, Defender Crit Evade, Attacker PCC (FCM value 0-5), Attack sequence position (first or subsequent), Defender holding Scroll, Defender has Nihil, Attacker has Wrath.
*   **Output:** Final Critical Chance percentage (0-100).

### 4.9. Critical Damage

*   **Purpose:** Calculates damage dealt on a successful critical hit.
*   **Formula:** `Critical_Damage = Calculated_Normal_Damage * 2`
*   **Note:** Doubles the final damage *after* defense mitigation. If normal damage is 0 or 1, crit damage is 0 or 2 respectively.
*   **Inputs:** Calculated Normal Damage.
*   **Output:** Critical Damage value (integer).

## 5. Special Combat Mechanics

### 5.1. Weapon Triangle

*   **Physical:** Swords > Axes > Lances > Swords (+5 Hit advantage, -5 Hit disadvantage).
*   **Anima Magic:** Fire > Wind > Thunder > Fire (+5 Hit advantage, -5 Hit disadvantage).
*   **Light/Dark Magic:** Strong against Anima (effectively +5 Hit vs Fire/Wind/Thunder). No specific Light vs Dark interaction.
*   **Implementation:** Apply bonus/penalty to Attacker's Hit Rate based on Attacker's and Defender's equipped weapon types.

### 5.2. Effective Damage

*   **Mechanic:** Certain weapons deal bonus damage to specific unit types (e.g., Rapier vs Armor/Cavalry, Hammer vs Armor, Horseslayer vs Cavalry).
*   **Calculation:** Weapon Might is multiplied by 3 (`Effective_Bonus = 3`) before adding Attacker's Str/Mag in the damage formula.
*   **Implementation:** Check weapon's effectiveness list against defender's class tags.

### 5.3. Brave Weapons

*   **Mechanic:** Weapons like Brave Sword/Lance/Axe/Bow grant an immediate second attack on initiation, before the enemy counterattacks.
*   **Interaction with Doubling:** If the wielder also meets the AS threshold (>= 4 AS difference), they attack four times in total (Hit1, Hit2(Brave), Counter, Hit3(Follow-up), Hit4(Follow-up Brave)).
*   **Interaction with PCC:** The second Brave hit (and subsequent follow-up hits) benefit from the PCC multiplier.
*   **Implementation:** Modify the combat sequence generator to insert the extra Brave strike(s).

### 5.4. Combat Skills

*   **Wrath:** Guarantees a critical hit (100% Crit Chance) when counterattacking or attacking during the enemy phase. Overrides Scrolls/Nihil.
*   **Adept (Continue):** Grants a chance (`Unit_Skill %` or `Unit_AS %` - *confirm exact Thracia formula*) to perform an additional attack immediately after a normal attack/follow-up. Can trigger multiple times. Subsequent Adept hits benefit from PCC.
*   **Miracle (Prayer):** If unit HP <= 10, grants massive Avoid boost (effectively 100% Avoid, making enemy Hit = 0%). *[Confirm activation limit/conditions]*.
*   **Nihil:** Negates enemy combat skills (Sol, Luna, Pavise, etc.) and prevents the enemy from landing critical hits on the Nihil user.
*   **Sol:** Chance on attack to heal HP equal to damage dealt.
*   **Luna:** Chance on attack to ignore enemy Def/Res.
*   **Pavise:** Chance on being hit to negate all damage from that attack.
*   **Astra (Mareeta's Sword):** Guarantees 5 consecutive attacks on initiation. PCC applies after the first hit.
*   **Implementation:** Check for skills on both units before and during combat simulation. Apply effects based on trigger conditions (e.g., HP threshold, % chance, attack sequence).

### 5.5. Scrolls (Crusader Scrolls)

*   **Mechanic:** Holding a scroll in inventory negates all enemy critical hits against the holder (sets enemy `Battle_Crit_Chance` to 0). Does not stack (one scroll is enough). Does not prevent criticals from Wrath. Also boosts growth rates (handled by Level Up system).
*   **Implementation:** Check defender's inventory for any item flagged as a "Scroll" before calculating final Battle Critical Chance.

### 5.6. Support Bonuses

*   **Mechanic:** Predefined character pairs grant bonuses (+10 or +20) to Hit, Avoid, Crit, and Crit Evade when within 3 tiles. Bonuses can be one-way or mutual. Total bonus capped at +30 per stat.
*   **Implementation:** Before combat calculations, check relative positions of all allied units. Look up support pairs in a data table and sum applicable bonuses for the attacker and defender, applying the +30 cap.

### 5.7. Leadership Bonuses (Authority Stars)

*   **Mechanic:** Each Leadership star (★) on a deployed allied leader grants +3 Hit and +3 Avoid to *all* units on their side, globally. Stars from multiple leaders stack.
*   **Implementation:** Before combat calculations, sum the Leadership stars of all active leaders on each side. Multiply the total by 3 to get the bonus, applied in Hit/Avoid formulas.

### 5.8. Charisma Bonuses (Charm Skill)

*   **Mechanic:** Units with the Charisma skill grant +10 Hit and +10 Avoid to all allies within a 3-tile radius. Effects from multiple Charisma units stack.
*   **Implementation:** Before combat calculations, check distance from attacker/defender to any allies with Charisma. Add +10 for each applicable source to Hit/Avoid formulas.

### 5.9. Terrain Effects

*   **Mechanic:** Standing on certain tiles grants bonuses to Avoid (%) and/or Defense (+flat value).
*   **Implementation:** Fetch terrain bonuses from the Map System based on the defender's current tile. Apply `Terrain_Avoid_Bonus` in the Avoid formula and `Terrain_Defense_Bonus` in the Damage formula. Remember mount/flyer exceptions.

## 6. Capture Mechanic

*   **Initiation:** Player selects "Capture" command instead of "Attack".
*   **Conditions:**
    *   Attacker must be able to initiate combat (have a weapon, target in range).
    *   Attacker's Con > Target's Con, **OR** Attacker is mounted.
    *   Target is not mounted.
    *   Target's Con < 20.
    *   Target is not immune to capture (e.g., specific bosses).
*   **Capture Battle:** Combat proceeds as normal, BUT the **initiator's Str, Mag, Skl, Spd, and Def are halved** (rounded down) for the duration of the capture battle. Luck, Con, Mov, HP are unaffected.
*   **Outcome:**
    *   If initiator reduces target's HP to 0: Target is Captured. Initiator enters "Carrying" state with the captured unit. Target's inventory becomes accessible via Trade.
    *   If target survives or initiator is defeated: Capture fails, combat ends.
    *   If target is unarmed or incapacitated (e.g., Sleep): Capture succeeds automatically without combat.
*   **Post-Capture:**
    *   **Carrying State:** Unit carrying a captive suffers the same stat halving (Str, Mag, Skl, Spd, Def halved) and potential Mov penalty as rescuing.
    *   **Trade:** Allies can trade with the carrying unit to access the captive's inventory and take items.
    *   **Release:** Carrying unit can use "Release" command (uses action) to remove the captive from the map permanently (no EXP gained for release). Unit exits Carrying state.
    *   **Take/Drop:** Allies can "Take" the captive from the carrier, or the carrier can "Drop" the captive onto an adjacent tile (like rescue).
*   **Enemy Capture:** Enemies with appropriate AI and meeting Con/Mount conditions may attempt to capture player units (especially if unarmed/weak). Captured player units are carried; if the enemy escapes, the player unit is lost until Ch 21x. Enemy AI may immediately trade captured unit's items to other enemies.
*   **EXP:** EXP is gained for the damage dealt during the capture battle, same as a normal kill if HP reaches 0. No extra EXP for the act of capturing or releasing.

## 7. Staff Usage

*   **Accuracy Formula:** `Staff_Hit = Base_Staff_Hit + (4 * User_Skill)` (Capped at 99%).
    *   Base_Staff_Hit is typically 60% for status staves, 100% for Torch staff.
    *   Target's Magic/Resistance does *not* affect staff hit chance in Thracia 776.
*   **Effects:**
    *   **Healing:** Restore HP (e.g., Heal, Mend). Typically 1-range.
    *   **Status:** Inflict Poison, Sleep, Silence, Berserk. Range varies. Statuses persist until cured by Restore staff or chapter end. Petrify requires Kia staff.
    *   **Utility:** Torch (increase FoW vision), Repair (restore weapon durability), Warp/Rescue (teleport units).
*   **Fatigue:** Using a staff increases user's fatigue based on staff rank (E:+1, D:+2, C:+3, B:+4, A:+5).
*   **Implementation:** Requires dedicated handler for staff targeting, accuracy check, effect application, and fatigue update.

## 8. Fatigue Interaction

*   **Gain:**
    *   Participating in any combat round (attacking or defending): +1 Fatigue.
    *   Using a staff: +1 to +5 Fatigue based on rank.
    *   Stealing: +1 Fatigue per successful steal.
    *   Dancing: +1 Fatigue per dance.
*   **Threshold:** If `Unit_Fatigue >= Unit_Max_HP` at chapter end, unit cannot be deployed next chapter (unless Leif or S-Drink used).
*   **Implementation:** Increment fatigue counter on relevant actions. Check threshold during deployment phase.

## 9. Experience Gain

*   Combat actions (hitting, defeating an enemy, staff usage) grant EXP.
*   The exact EXP formula depends on relative levels, damage dealt, kill bonus, staff type, etc. (Refer to specific EXP formula documentation/research).
*   Capturing provides EXP equivalent to defeating the enemy.
*   Escaping an escape map grants a small EXP bonus (e.g., 10 EXP).
*   *Note: Detailed EXP calculation is likely handled by a separate EXP/Level Up System, but triggered by Combat System events.*

## 10. Pseudocode Modules

```pseudocode
MODULE CombatResolver

  // --- Main Entry Point ---
  FUNCTION resolve_combat(attacker_unit, defender_unit, is_capture_attempt = FALSE):
    // 1. Initialization
    combat_log = CREATE CombatLog()
    attacker_stats = GET_combat_stats(attacker_unit, defender_unit, is_capture_attempt)
    defender_stats = GET_combat_stats(defender_unit, attacker_unit, FALSE) // Defender never initiates capture

    // 2. Determine Combat Sequence (Handles Brave, Doubling)
    sequence = DETERMINE_combat_sequence(attacker_stats, defender_stats)
    combat_log.add_sequence(sequence)

    // 3. Execute Combat Sequence
    current_attacker = attacker_unit
    current_defender = defender_unit
    attacker_hp = attacker_unit.current_hp
    defender_hp = defender_unit.current_hp
    round_num = 0

    FOR each action_type IN sequence:
      round_num += 1
      round_result = CREATE RoundResult(round_num, action_type)

      // Determine who is attacking this round
      IF action_type involves attacker:
        active_attacker_unit = attacker_unit
        active_defender_unit = defender_unit
        active_attacker_stats = attacker_stats
        active_defender_stats = defender_stats
        attacker_current_hp_ref = &attacker_hp
        defender_current_hp_ref = &defender_hp
      ELSE: // action_type involves defender (counter-attack)
        active_attacker_unit = defender_unit
        active_defender_unit = attacker_unit
        active_attacker_stats = defender_stats
        active_defender_stats = attacker_stats
        attacker_current_hp_ref = &defender_hp
        defender_current_hp_ref = &attacker_hp

      // Check if attacker can act (not dead)
      IF *attacker_current_hp_ref <= 0:
        round_result.set_skipped("Attacker defeated")
        combat_log.add_round(round_result)
        CONTINUE // Skip this action

      // Check if defender can be attacked (not dead)
      IF *defender_current_hp_ref <= 0:
         // If capture attempt, check if capture succeeds now
         IF is_capture_attempt AND active_attacker_unit == attacker_unit:
             CaptureHandler.process_capture_success(attacker_unit, defender_unit, combat_log)
             BREAK // Combat ends on successful capture
         ELSE:
             round_result.set_skipped("Defender already defeated")
             combat_log.add_round(round_result)
             CONTINUE // Skip this action


      // Calculate Hit Chance
      hit_chance = CombatCalculator.calculate_battle_hit_chance(active_attacker_stats, active_defender_stats)
      round_result.set_hit_chance(hit_chance)

      // Roll for Hit
      hit_roll = ROLL_RN(1, 100)
      IF hit_roll > hit_chance:
        round_result.set_outcome("Miss")
        combat_log.add_round(round_result)
        // Apply Fatigue for participating
        APPLY_fatigue(active_attacker_unit, "combat")
        APPLY_fatigue(active_defender_unit, "combat")
        CONTINUE // Attack missed

      // Calculate Damage
      damage = CombatCalculator.calculate_damage(active_attacker_stats, active_defender_stats)
      round_result.set_potential_damage(damage)

      // Check for Pavise Skill on Defender
      IF CombatCalculator.check_skill_activation(active_defender_unit, "Pavise", active_defender_stats):
          round_result.set_outcome("Hit (Pavise Negated)")
          round_result.set_damage_dealt(0)
          combat_log.add_round(round_result)
          // Apply Fatigue
          APPLY_fatigue(active_attacker_unit, "combat")
          APPLY_fatigue(active_defender_unit, "combat")
          CONTINUE // Damage negated

      // Calculate Critical Chance
      is_first_attack = (round_num == 1) // Or more complex logic for Brave
      crit_chance = CombatCalculator.calculate_battle_crit_chance(active_attacker_stats, active_defender_stats, is_first_attack)
      round_result.set_crit_chance(crit_chance)

      // Roll for Critical
      is_crit = FALSE
      IF crit_chance > 0:
        crit_roll = ROLL_RN(1, 100)
        IF crit_roll <= crit_chance:
          is_crit = TRUE
          damage = CombatCalculator.calculate_crit_damage(damage)
          round_result.set_outcome("Critical Hit")
        ELSE:
          round_result.set_outcome("Hit")
      ELSE:
          round_result.set_outcome("Hit")


      // Apply Damage
      actual_damage = MIN(damage, *defender_current_hp_ref) // Damage cannot exceed current HP
      *defender_current_hp_ref -= actual_damage
      round_result.set_damage_dealt(actual_damage)

      // Check for Sol Skill on Attacker
      IF CombatCalculator.check_skill_activation(active_attacker_unit, "Sol", active_attacker_stats):
          heal_amount = MIN(actual_damage, active_attacker_unit.max_hp - *attacker_current_hp_ref)
          *attacker_current_hp_ref += heal_amount
          round_result.add_effect("Sol activated, healed " + heal_amount)

      combat_log.add_round(round_result)

      // Apply Fatigue
      APPLY_fatigue(active_attacker_unit, "combat")
      APPLY_fatigue(active_defender_unit, "combat")

      // Check if defender was defeated or captured
      IF *defender_current_hp_ref <= 0:
        IF is_capture_attempt AND active_attacker_unit == attacker_unit:
          CaptureHandler.process_capture_success(attacker_unit, defender_unit, combat_log)
          BREAK // Combat ends on successful capture
        ELSE:
          // Mark defender as defeated (handled by caller?)
          combat_log.set_defender_defeated()
          // Check if combat should end (e.g., defender defeated before counter/follow-up)
          IF action_type prevents further actions (e.g. defender defeated before counter):
              BREAK


    // 4. Finalize Combat
    // Apply final HP changes, grant EXP (handled by caller using combat_log), update weapon durability
    UPDATE_unit_hp(attacker_unit, attacker_hp)
    UPDATE_unit_hp(defender_unit, defender_hp)
    UPDATE_weapon_durability(attacker_unit, combat_log.get_attacker_hits())
    UPDATE_weapon_durability(defender_unit, combat_log.get_defender_hits())
    // Grant WEXP (handled by caller?)

    RETURN combat_log
  END FUNCTION

  // --- Helper Functions ---
  FUNCTION GET_combat_stats(unit, opponent, is_capture_attempt):
    // Fetch base stats, weapon stats, terrain bonuses, support, leadership, charisma
    // Apply capture penalties if applicable
    stats = CREATE CombatStats()
    // ... populate stats object ...
    stats.AS = CombatCalculator.calculate_attack_speed(unit, unit.equipped_weapon)
    stats.Hit = CombatCalculator.calculate_hit_rate(unit, unit.equipped_weapon, opponent)
    stats.Avoid = CombatCalculator.calculate_avoid_rate(unit, opponent)
    stats.BaseCrit = CombatCalculator.calculate_base_crit_rate(unit, unit.equipped_weapon)
    stats.CritEvade = CombatCalculator.calculate_crit_evade(unit)
    stats.PCC = unit.pcc
    stats.HasScroll = CHECK_inventory_for_scroll(unit)
    stats.Skills = unit.skills

    IF is_capture_attempt:
        stats.Str = FLOOR(stats.Str / 2)
        stats.Mag = FLOOR(stats.Mag / 2)
        stats.Skl = FLOOR(stats.Skl / 2)
        stats.Spd = FLOOR(stats.Spd / 2)
        stats.Def = FLOOR(stats.Def / 2)
        // Recalculate AS based on halved Spd if capture penalty applies
        stats.AS = CombatCalculator.calculate_attack_speed(unit, unit.equipped_weapon, stats.Spd, stats.Con) // Pass potentially halved Spd

    RETURN stats
  END FUNCTION

  FUNCTION DETERMINE_combat_sequence(attacker_stats, defender_stats):
    sequence = []
    attacker_AS = attacker_stats.AS
    defender_AS = defender_stats.AS
    attacker_weapon = attacker_stats.weapon
    defender_weapon = defender_stats.weapon

    can_attacker_double = (attacker_AS - defender_AS >= 4)
    can_defender_double = (defender_AS - attacker_AS >= 4)
    attacker_is_brave = attacker_weapon.is_brave
    defender_is_brave = defender_weapon.is_brave // Relevant if defender initiates? Less common.

    // Attacker's first hit(s)
    sequence.append("Attacker_Hit1")
    IF attacker_is_brave:
      sequence.append("Attacker_BraveHit")

    // Defender's counter-attack(s)
    IF defender_can_attack_back(defender_weapon, attacker_weapon.range):
      sequence.append("Defender_Counter1")
      // Brave counter? Very rare, but possible.
      // IF defender_is_brave: sequence.append("Defender_BraveCounter")
      IF can_defender_double:
        sequence.append("Defender_FollowUp")
        // IF defender_is_brave: sequence.append("Defender_FollowUpBrave")

    // Attacker's follow-up hit(s)
    IF can_attacker_double:
      sequence.append("Attacker_FollowUp1")
      IF attacker_is_brave:
        sequence.append("Attacker_FollowUpBrave")

    RETURN sequence
  END FUNCTION

  FUNCTION APPLY_fatigue(unit, action_type):
      IF GameState.current_chapter >= 8 AND unit != GameState.main_lord:
          fatigue_gain = 0
          IF action_type == "combat":
              fatigue_gain = 1
          ELSE IF action_type == "staff":
              // Determine gain based on staff rank (1-5)
              fatigue_gain = GET_staff_fatigue_cost(unit.equipped_staff)
          ELSE IF action_type == "steal":
              fatigue_gain = 1
          ELSE IF action_type == "dance":
              fatigue_gain = 1
          // ... other actions ...

          unit.fatigue += fatigue_gain
  END FUNCTION

END MODULE

MODULE CombatCalculator

  FUNCTION calculate_attack_speed(unit, weapon, override_spd = NULL, override_con = NULL):
      spd = override_spd IF override_spd IS NOT NULL ELSE unit.spd
      con = override_con IF override_con IS NOT NULL ELSE unit.con
      wt = weapon.weight
      IF weapon.type IS Magical:
          RETURN spd - wt
      ELSE:
          RETURN spd - MAX(0, wt - con)
      // TEST_CASE: Physical weapon, Wt > Con
      // TEST_CASE: Physical weapon, Wt <= Con
      // TEST_CASE: Magical weapon
      // TEST_CASE: Capture penalty halving Spd
  END FUNCTION

  FUNCTION calculate_hit_rate(unit, weapon, opponent):
      support_bonus = GET_support_bonus(unit, "Hit") // Capped at 30
      leadership_bonus = GET_leadership_bonus(unit.faction) // Stars * 3
      charisma_bonus = GET_charisma_bonus(unit, "Hit")
      triangle_bonus = GET_weapon_triangle_bonus(weapon, opponent.equipped_weapon)
      RETURN weapon.hit + (2 * unit.skl) + unit.luk + support_bonus + leadership_bonus + charisma_bonus + triangle_bonus
      // TEST_CASE: Base calculation, no bonuses
      // TEST_CASE: With max support bonus
      // TEST_CASE: With leadership bonus
      // TEST_CASE: With charisma bonus
      // TEST_CASE: With weapon triangle advantage
      // TEST_CASE: With weapon triangle disadvantage
  END FUNCTION

  FUNCTION calculate_avoid_rate(unit, opponent):
      support_bonus = GET_support_bonus(unit, "Avoid") // Capped at 30
      leadership_bonus = GET_leadership_bonus(unit.faction) // Stars * 3
      charisma_bonus = GET_charisma_bonus(unit, "Avoid")
      terrain_bonus = GET_terrain_avoid_bonus(unit) // Check mount/flyer status

      // Need AS first
      unit_as = calculate_attack_speed(unit, unit.equipped_weapon)

      RETURN (2 * unit_as) + unit.luk + support_bonus + leadership_bonus + charisma_bonus + terrain_bonus
      // TEST_CASE: Base calculation, no bonuses, no terrain
      // TEST_CASE: High AS contribution
      // TEST_CASE: With max support bonus
      // TEST_CASE: With leadership bonus
      // TEST_CASE: With charisma bonus
      // TEST_CASE: With terrain bonus (infantry on forest)
      // TEST_CASE: Mounted unit on forest (should get 0 terrain bonus)
      // TEST_CASE: Flying unit on forest (should get 0 terrain bonus)
  END FUNCTION

  FUNCTION calculate_battle_hit_chance(attacker_stats, defender_stats):
      raw_hit = attacker_stats.Hit - defender_stats.Avoid
      // Apply Miracle skill effect if defender HP is low
      IF defender_stats.Skills contains "Miracle" AND defender_stats.current_hp <= 10: // Assuming current HP is in stats
          RETURN 1 // Miracle makes hit chance effectively 0, but game shows 1% min
      RETURN MAX(1, MIN(99, raw_hit))
      // TEST_CASE: High hit, low avoid -> 99
      // TEST_CASE: Low hit, high avoid -> 1
      // TEST_CASE: Moderate hit/avoid -> calculated value
      // TEST_CASE: Defender Miracle active -> 1
  END FUNCTION

  FUNCTION calculate_damage(attacker_stats, defender_stats):
      weapon = attacker_stats.weapon
      effective_bonus = GET_effective_bonus(weapon, defender_stats.unit_type_tags) // 1 or 3

      IF weapon.type IS Magical OR (weapon.is_magic_sword AND attacker_stats.attack_range == 2):
          defender_magic_defense = defender_stats.Mag + defender_stats.TerrainDefBonus // + Temp bonuses
          damage = (attacker_stats.Mag + (weapon.might * effective_bonus)) - defender_magic_defense
      ELSE: // Physical or Magic Sword at Range 1
          defender_physical_defense = defender_stats.Def + defender_stats.TerrainDefBonus
          damage = (attacker_stats.Str + (weapon.might * effective_bonus)) - defender_physical_defense

      // Apply Luna skill effect if attacker has Luna
      IF attacker_stats.Skills contains "Luna" AND check_skill_activation(attacker_stats.unit, "Luna", attacker_stats):
          // Rerun calculation ignoring defense (or apply effect post-hoc)
          IF weapon.type IS Magical OR (weapon.is_magic_sword AND attacker_stats.attack_range == 2):
              damage = (attacker_stats.Mag + (weapon.might * effective_bonus)) // Ignore defender Mag
          ELSE:
              damage = (attacker_stats.Str + (weapon.might * effective_bonus)) // Ignore defender Def
          // Add flag that Luna activated

      RETURN MAX(0, damage)
      // TEST_CASE: Physical damage, no effectiveness, no terrain
      // TEST_CASE: Magical damage, no effectiveness, no terrain
      // TEST_CASE: Physical effective (x3 Mt)
      // TEST_CASE: Magical effective (x3 Mt)
      // TEST_CASE: Defender on Fort (+Def)
      // TEST_CASE: Damage calculation results in < 0 -> 0
      // TEST_CASE: Attacker Luna activates vs high Def enemy
      // TEST_CASE: Magic Sword Range 1 (confirm Str vs Def)
      // TEST_CASE: Magic Sword Range 2 (Mag vs Mag)
  END FUNCTION

  FUNCTION calculate_base_crit_rate(unit, weapon):
      support_bonus = GET_support_bonus(unit, "Crit") // Capped at 30
      RETURN weapon.crit + unit.skl + support_bonus
      // TEST_CASE: Base calculation
      // TEST_CASE: With support bonus
  END FUNCTION

  FUNCTION calculate_crit_evade(unit):
      support_bonus = GET_support_bonus(unit, "CritEvade") // Capped at 30
      RETURN FLOOR(unit.luk / 2) + support_bonus
      // TEST_CASE: Base calculation
      // TEST_CASE: With support bonus
  END FUNCTION

  FUNCTION calculate_battle_crit_chance(attacker_stats, defender_stats, is_first_attack):
      // Check defender immunities first
      IF defender_stats.HasScroll: RETURN 0
      IF defender_stats.Skills contains "Nihil": RETURN 0

      // Check attacker guarantees
      IF attacker_stats.Skills contains "Wrath" AND attacker_stats.is_countering_or_enemy_phase: RETURN 100

      potential_crit = attacker_stats.BaseCrit - defender_stats.CritEvade

      IF is_first_attack:
          RETURN MAX(0, MIN(25, potential_crit))
      ELSE: // Subsequent attack
          RETURN MAX(0, MIN(100, potential_crit * attacker_stats.PCC))
      // TEST_CASE: Base crit > evade, first attack -> MIN(25, result)
      // TEST_CASE: Base crit > evade, second attack, PCC=3 -> result * 3 (capped 100)
      // TEST_CASE: Base crit <= evade -> 0
      // TEST_CASE: Defender has Scroll -> 0
      // TEST_CASE: Defender has Nihil -> 0
      // TEST_CASE: Attacker has Wrath (on counter) -> 100
      // TEST_CASE: Attacker has Wrath (on initiation) -> Normal calc
      // TEST_CASE: High potential crit * high PCC > 100 -> 100
      // TEST_CASE: High potential crit > 25, first attack -> 25
  END FUNCTION

  FUNCTION calculate_crit_damage(normal_damage):
      RETURN normal_damage * 2
      // TEST_CASE: Normal damage > 1
      // TEST_CASE: Normal damage = 1 -> 2
      // TEST_CASE: Normal damage = 0 -> 0
  END FUNCTION

  FUNCTION check_skill_activation(unit, skill_name, unit_stats):
      // Check % chance based on skill (e.g., Adept=Skl%, Sol/Luna=Skl%?, Pavise=Lvl%?)
      // Check conditions (e.g., Miracle HP threshold)
      // Return TRUE if skill activates, FALSE otherwise
      // TEST_CASE: Adept activation roll success/fail
      // TEST_CASE: Miracle HP threshold met/not met
      // TEST_CASE: Pavise activation roll success/fail
      RETURN FALSE // Placeholder
  END FUNCTION

END MODULE

MODULE CaptureHandler

  FUNCTION check_capture_conditions(attacker_unit, target_unit):
      IF target_unit.is_mounted OR target_unit.con >= 20 OR target_unit.is_capture_immune:
          RETURN FALSE
      IF attacker_unit.con > target_unit.con OR attacker_unit.is_mounted:
          RETURN TRUE
      RETURN FALSE
      // TEST_CASE: Attacker Con > Target Con -> TRUE
      // TEST_CASE: Attacker Con <= Target Con, Attacker Mounted -> TRUE
      // TEST_CASE: Attacker Con <= Target Con, Attacker Not Mounted -> FALSE
      // TEST_CASE: Target Mounted -> FALSE
      // TEST_CASE: Target Con >= 20 -> FALSE
  END FUNCTION

  FUNCTION process_capture_success(attacker_unit, captured_unit, combat_log):
      attacker_unit.set_state("Carrying", captured_unit)
      captured_unit.set_state("Captured", by=attacker_unit)
      // Make captured unit's inventory accessible
      captured_unit.inventory.set_accessible(TRUE)
      combat_log.set_capture_success()
      // Grant EXP for the "kill" (handled by caller)
  END FUNCTION

  FUNCTION release_captive(carrier_unit):
      IF carrier_unit.state IS "Carrying":
          captive = carrier_unit.carried_unit
          captive.remove_from_map() // Or set state to "Released"
          carrier_unit.set_state("Idle")
          // Apply fatigue for action? (Check if Release costs action/fatigue)
          RETURN TRUE
      RETURN FALSE
  END FUNCTION

END MODULE

MODULE StaffHandler

  FUNCTION resolve_staff_use(staff_user, target_unit_or_tile, staff_item):
      // 1. Check Range, Target Validity, Staff Rank vs User WEXP
      // 2. Calculate Staff Hit Chance
      hit_chance = calculate_staff_hit_chance(staff_user, staff_item)
      // 3. Roll for Hit
      IF ROLL_RN(1, 100) <= hit_chance:
          // 4. Apply Staff Effect (Heal, Status, Utility)
          APPLY_staff_effect(staff_user, target_unit_or_tile, staff_item)
          // 5. Apply Fatigue
          APPLY_fatigue(staff_user, "staff")
          // 6. Update Staff Durability
          staff_item.uses -= 1
          // 7. Grant WEXP
          GRANT_wexp(staff_user, staff_item.rank)
          RETURN "Success"
      ELSE:
          // Apply Fatigue even on miss? Check Thracia rules. Assume yes for now.
          APPLY_fatigue(staff_user, "staff")
          staff_item.uses -= 1 // Durability used even on miss
          // Grant WEXP on miss? Check Thracia rules. Assume no for now.
          RETURN "Miss"
      // TEST_CASE: Heal staff success
      // TEST_CASE: Sleep staff success
      // TEST_CASE: Sleep staff miss
      // TEST_CASE: Restore staff curing status
      // TEST_CASE: Repair staff restoring durability
      // TEST_CASE: Torch staff increasing vision
      // TEST_CASE: Fatigue gain matches staff rank
  END FUNCTION

  FUNCTION calculate_staff_hit_chance(staff_user, staff_item):
      base_hit = staff_item.base_hit // e.g., 60 or 100
      hit = base_hit + (4 * staff_user.skl)
      RETURN MAX(1, MIN(99, hit)) // Staff hit also capped 1-99? Assume yes.
      // TEST_CASE: Base calculation
      // TEST_CASE: High skill -> 99
  END FUNCTION

END MODULE
```

## 11. TDD Anchors

*   **CombatCalculator:**
    *   `TEST_CASE(calculate_attack_speed)`: Physical Wt > Con, Wt <= Con, Magical Wt, Capture penalty applied.
    *   `TEST_CASE(calculate_hit_rate)`: Base, Support, Leadership, Charisma, Triangle+, Triangle-.
    *   `TEST_CASE(calculate_avoid_rate)`: Base, High AS, Support, Leadership, Charisma, Terrain (Infantry, Mount, Flyer).
    *   `TEST_CASE(calculate_battle_hit_chance)`: Cap 99, Cap 1, Mid-range, Miracle active.
    *   `TEST_CASE(calculate_damage)`: Physical, Magical, Effective (Phys/Mag), Terrain Def, Negative Dmg -> 0, Luna activation, Magic Sword R1/R2.
    *   `TEST_CASE(calculate_base_crit_rate)`: Base, Support.
    *   `TEST_CASE(calculate_crit_evade)`: Base, Support.
    *   `TEST_CASE(calculate_battle_crit_chance)`: First attack (cap 25), Subsequent attack (PCC applied, cap 100), Crit < Evade -> 0, Scroll -> 0, Nihil -> 0, Wrath (counter) -> 100, Wrath (initiation) -> normal.
    *   `TEST_CASE(calculate_crit_damage)`: Dmg > 1, Dmg = 1, Dmg = 0.
    *   `TEST_CASE(check_skill_activation)`: Adept, Miracle, Pavise, Sol, Luna (ensure % chance logic).
*   **CombatResolver:**
    *   `TEST_CASE(resolve_combat)`: Simple attack-counter.
    *   `TEST_CASE(resolve_combat)`: Attacker doubles.
    *   `TEST_CASE(resolve_combat)`: Defender doubles.
    *   `TEST_CASE(resolve_combat)`: Both double (verify sequence).
    *   `TEST_CASE(resolve_combat)`: Attacker Brave weapon.
    *   `TEST_CASE(resolve_combat)`: Attacker Brave + Doubles.
    *   `TEST_CASE(resolve_combat)`: Attacker misses first hit.
    *   `TEST_CASE(resolve_combat)`: Defender misses counter.
    *   `TEST_CASE(resolve_combat)`: Attacker lands critical (first hit vs subsequent).
    *   `TEST_CASE(resolve_combat)`: Defender lands critical.
    *   `TEST_CASE(resolve_combat)`: Attacker kills defender on first hit (no counter/follow-up).
    *   `TEST_CASE(resolve_combat)`: Attacker kills defender on brave hit (no counter/follow-up).
    *   `TEST_CASE(resolve_combat)`: Attacker kills defender on follow-up hit.
    *   `TEST_CASE(resolve_combat)`: Defender kills attacker on counter (no follow-up).
    *   `TEST_CASE(resolve_combat)`: Pavise negates damage.
    *   `TEST_CASE(resolve_combat)`: Sol heals attacker.
    *   `TEST_CASE(resolve_combat)`: Fatigue applied correctly per combat round participation.
    *   `TEST_CASE(resolve_combat)`: Capture attempt success (combat).
    *   `TEST_CASE(resolve_combat)`: Capture attempt failure (combat).
    *   `TEST_CASE(resolve_combat)`: Capture attempt success (no combat - sleep/unarmed).
    *   `TEST_CASE(resolve_combat)`: Capture penalties applied correctly.
*   **CaptureHandler:**
    *   `TEST_CASE(check_capture_conditions)`: All condition variations (Con, Mount, Target state).
    *   `TEST_CASE(process_capture_success)`: Verify state changes, inventory access.
    *   `TEST_CASE(release_captive)`: Verify state changes, captive removal.
*   **StaffHandler:**
    *   `TEST_CASE(resolve_staff_use)`: Heal success, Status success/miss, Utility success, Fatigue applied, Durability update, WEXP gain (on success).
    *   `TEST_CASE(calculate_staff_hit_chance)`: Base, High skill -> 99.

## 12. Edge Cases and Considerations

*   **Stat Caps:** Ensure calculations respect Thracia's stat caps (mostly 20).
*   **Temporary Stat Boosts:** How are temporary boosts (like M Up/Pure Water) tracked and applied, especially their decay?
*   **Simultaneous Effects:** How are multiple skill activations handled in one round (e.g., Adept + Crit)?
*   **Range Ambiguity:** Confirm damage type for magic swords at Range 1.
*   **Skill Formulae:** Verify exact activation rates for skills like Adept, Sol, Luna, Pavise in Thracia 776.
*   **Fatigue on Miss/No Damage:** Does combat participation grant fatigue even if the attack misses or deals 0 damage? (Assume yes). Does staff use grant fatigue/WEXP on miss? (Assume yes for fatigue/durability, no for WEXP).
*   **Capture Immunity:** Maintain a list of specific units/classes immune to capture.
*   **Broken Weapons:** How are broken weapons represented and used (1 Mt, low Hit)? Can they trigger skills?
*   **RNG:** Ensure use of a 1 RN system for all chance-based events (Hit, Crit, Skills).
*   **Integration:** How does the Combat Resolver receive all necessary context (support bonuses, leadership, terrain) efficiently? How does it report results (HP changes, EXP gain triggers, status changes, state changes like capture)?