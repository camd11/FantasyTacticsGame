# Specification: Pursuit Critical Coefficient (PCC / FCM)

**Status: Implemented**
## 1. Overview

This document specifies the implementation of the Pursuit Critical Coefficient (PCC) mechanic, also known as Follow-up Critical Multiplier (FCM), as found in Fire Emblem: Thracia 776. This mechanic modifies the critical hit rate calculation specifically for follow-up attacks during combat.

## 2. Goal

Modify the critical hit calculation within the `CombatSystem` to incorporate the PCC/FCM value, ensuring it only affects attacks subsequent to the initial strike in a combat round.

## 3. Definitions

*   **Pursuit Critical Coefficient (PCC) / Follow-up Critical Multiplier (FCM):** A unit-specific integer value (typically ranging from 0 to 5) that multiplies the unit's calculated critical hit chance during follow-up attacks. This value is inherent to the character/class data.
*   **Follow-up Attack (Pursuit Attack):** Any attack performed by a unit after their initial attack within the same combat round. This includes:
    *   The second attack granted by having sufficient Attack Speed (AS) difference (doubling).
    *   Extra attacks granted by skills like Adept (Continue).
    *   The second (and subsequent) hits from Brave-type weapons.
*   **Initial Attack:** The very first attack performed by a unit when initiating or countering in a combat round.
*   **Base Critical Rate:** The unit's critical chance before considering enemy evasion or PCC. Calculated as: `Weapon Critical + Skill + Support Bonuses`.
*   **Critical Evade (Dodge / Ddg):** The target's ability to negate critical hits. Calculated as: `(Target's Luck / 2) + Target's Support Bonuses`.

## 4. Calculation Logic

The critical hit chance calculation depends on whether the attack is the initial strike or a follow-up strike.

### 4.1. Initial Attack Critical Chance

*   The calculated critical chance is `max(0, Base Critical Rate - Target's Critical Evade)`.
*   This calculated chance is **capped at a maximum of 25%**.
*   The unit's PCC/FCM value is **ignored** for the initial attack.
*   **Formula:** `Initial Attack Crit% = min( max(0, Base Critical Rate - Target's Critical Evade), 25 )`
*   `[TDD: Test crit calculation for initial attack (respects 25% cap)]`
*   `[TDD: Test initial attack crit is unaffected by PCC value]`

### 4.2. Follow-up Attack Critical Chance

*   The calculated critical chance is `max(0, Base Critical Rate - Target's Critical Evade)`.
*   This calculated chance is then **multiplied by the attacker's PCC/FCM value**.
*   The final result is **capped at a maximum of 100%**.
*   The 25% cap from the initial attack does **not** apply here.
*   **Formula:** `Follow-up Attack Crit% = min( max(0, Base Critical Rate - Target's Critical Evade) * Attacker's PCC, 100 )`
*   `[TDD: Test crit calculation for follow-up attack (uses PCC multiplier)]`
*   `[TDD: Test follow-up attack crit ignores 25% cap (can exceed 25%)]`
*   `[TDD: Test follow-up attack crit calculation with PCC=0 results in 0% crit]`
*   `[TDD: Test follow-up attack crit calculation with high base crit and high PCC caps at 100%]`

## 5. Data Representation

*   **PCC/FCM Value:** This value should be stored as a base attribute for each unit, likely derived from their character definition data (`data/units.yaml` or `data/classes.yaml`). It is **not** dynamically calculated from the Skill stat during combat.
*   **Recommendation:** Add a `pcc` field (or `fcm`) to the `UnitData` structure loaded from YAML files and subsequently to the `UnitState` object used in gameplay.
*   `[TDD: Test PCC value loading from unit data]`

## 6. Integration with Combat System (Pseudocode)

The existing `CombatSystem` or equivalent combat calculation logic needs modification. Specifically, the function(s) responsible for calculating the critical hit chance for each attack in a sequence must be updated.

```pseudocode
FUNCTION calculate_combat_round(attacker: UnitState, defender: UnitState): CombatResult

  // ... (Initialize combat results, calculate AS, determine doubling, etc.)

  // --- Attacker's First Strike ---
  is_first_attack = TRUE
  attacker_crit_chance = calculate_crit_chance(attacker, defender, is_first_attack)
  // ... (Calculate hit chance, damage, resolve first attack)
  // ... (Add attack details to CombatResult)

  // --- Defender's Counterattack (if applicable) ---
  IF defender_can_counter:
    is_first_attack = TRUE // Defender's first attack in this round
    defender_crit_chance = calculate_crit_chance(defender, attacker, is_first_attack)
    // ... (Calculate hit chance, damage, resolve counterattack)
    // ... (Add attack details to CombatResult)

  // --- Attacker's Follow-up Strike (if applicable) ---
  IF attacker_doubles OR attacker_has_brave_effect_remaining OR attacker_adept_procs:
    is_first_attack = FALSE // This is a follow-up attack
    attacker_followup_crit_chance = calculate_crit_chance(attacker, defender, is_first_attack)
    // ... (Calculate hit chance, damage, resolve follow-up attack)
    // ... (Add attack details to CombatResult)
    // Handle potential further Adept/Brave hits similarly, setting is_first_attack = FALSE

  // --- Defender's Follow-up Strike (if applicable and defender also doubles) ---
  // (Less common, but handle symmetrically if needed)
  IF defender_doubles AND defender_can_counter: // Assuming defender survived initial hit
     is_first_attack = FALSE // Defender's follow-up
     defender_followup_crit_chance = calculate_crit_chance(defender, attacker, is_first_attack)
     // ... (Resolve defender's follow-up)
     // ... (Add attack details to CombatResult)

  RETURN CombatResult

END FUNCTION

FUNCTION calculate_crit_chance(attacker: UnitState, defender: UnitState, is_initial_attack: BOOLEAN): INTEGER

  base_crit = attacker.get_weapon_crit() + attacker.get_skill() + attacker.get_support_bonus_crit()
  target_crit_evade = floor(defender.get_luck() / 2) + defender.get_support_bonus_crit_evade()

  calculated_crit = max(0, base_crit - target_crit_evade)

  IF is_initial_attack:
    // Apply 25% cap for the first attack
    final_crit = min(calculated_crit, 25)
    `[TDD Anchor: Verify initial attack crit calculation]`
  ELSE:
    // Apply PCC multiplier for follow-up attacks
    attacker_pcc = attacker.get_pcc() // Fetch PCC value from UnitState
    final_crit = min(calculated_crit * attacker_pcc, 100)
    `[TDD Anchor: Verify follow-up attack crit calculation]`
  END IF

  RETURN final_crit

END FUNCTION

// Helper functions assumed to exist:
// attacker.get_weapon_crit()
// attacker.get_skill()
// attacker.get_support_bonus_crit() -> Needs support system integration
// defender.get_luck()
// defender.get_support_bonus_crit_evade() -> Needs support system integration
// attacker.get_pcc() -> Needs PCC value added to UnitState/UnitData

```

## 7. Edge Cases & Considerations

*   **Wrath Skill:** The Wrath skill guarantees a critical hit on counterattacks/enemy phase attacks. This overrides the standard critical calculation, including PCC and the 25% cap. The combat logic must check for Wrath activation *before* performing the standard crit calculation for the relevant attack. `[TDD: Test Wrath interaction (overrides PCC/caps)]`
*   **Scrolls:** Holding a Crusader Scroll negates enemy critical hits entirely (sets enemy crit chance to 0 against the holder), unless the enemy has Wrath. This check should occur before the standard crit calculation. `[TDD: Test Scroll interaction (negates enemy crit)]`
*   **Nihil Skill:** The Nihil skill also negates enemy critical hits (and skills). This should also be checked before standard crit calculation. `[TDD: Test Nihil interaction (negates enemy crit)]`
*   **Skills granting multiple attacks (Adept, Brave):** Ensure each attack *after the first* correctly uses the follow-up calculation (applies PCC, ignores 25% cap). `[TDD: Test PCC application on Adept/Brave hits]`
*   **PCC = 0:** Units with PCC=0 should never crit on follow-up attacks, regardless of their base crit rate. The formula handles this naturally.
*   **Displayed Crit vs. Battle Crit:** The UI displaying the critical rate in the forecast window should ideally reflect the calculated chance for the *first* hit (respecting the 25% cap). It might not be feasible or desirable to show the potentially much higher follow-up crit chance, as this was not standard FE UI practice.

## 8. TDD Anchors Summary

*   `[TDD: Test PCC value loading from unit data]`
*   `[TDD: Test crit calculation for initial attack (respects 25% cap)]`
*   `[TDD: Test initial attack crit is unaffected by PCC value]`
*   `[TDD: Test crit calculation for follow-up attack (uses PCC multiplier)]`
*   `[TDD: Test follow-up attack crit ignores 25% cap (can exceed 25%)]`
*   `[TDD: Test follow-up attack crit calculation with PCC=0 results in 0% crit]`
*   `[TDD: Test follow-up attack crit calculation with high base crit and high PCC caps at 100%]`
*   `[TDD: Test Wrath interaction (overrides PCC/caps)]`
*   `[TDD: Test Scroll interaction (negates enemy crit)]`
*   `[TDD: Test Nihil interaction (negates enemy crit)]`
*   `[TDD: Test PCC application on Adept/Brave hits]`