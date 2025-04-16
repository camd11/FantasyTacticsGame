# Specification: Charge Skill

**Status: Implemented**

## 1. Overview

This document outlines the specification for the **Charge** skill, inspired by its implementation in Fire Emblem: Thracia 776. The Charge skill allows a unit with significantly higher Attack Speed (AS) than their opponent to potentially initiate an immediate second round of combat after the first round concludes.

## 2. Skill Definition (`data/skills.yaml`)

The Charge skill is defined in `data/skills.yaml` as follows:

```yaml
CHARGE:
  id: "CHARGE"
  name: "Charge"
  description: "If unit's Attack Speed is 5 or more higher than the opponent's after a round of combat, initiates an immediate second round of combat. Activates only once per combat initiation."
  effects:
    - type: "INITIATE_SECOND_COMBAT_ROUND" # New effect type
      params:
        speed_difference_threshold: 5 # Assumed value
        activation_limit: 1 # Per combat initiation
  activation_condition: "POST_COMBAT_ROUND" # New condition type
  activation_chance: 100
```

**Note:** The `speed_difference_threshold` (5) and `activation_limit` (1) are based on common FE mechanics and the user request, as specific Thracia 776 data for this skill was not found in `research.md`. These values should be verified if possible.

## 3. Mechanics

### 3.1. Activation Condition

- Charge is checked *after* a complete standard round of combat has resolved. This includes:
    - Initiator's first attack(s) (e.g., Brave weapon hits).
    - Defender's counterattack(s) (if applicable).
    - Follow-up attacks (Pursuit/doubling) from either unit (if applicable).
    - Any skill activations within that round (e.g., Adept, Sol, Luna).
- The check occurs before control returns to the main game loop or before fatigue is calculated for the combat actions.

### 3.2. Attack Speed Threshold

- The skill activates if the unit possessing Charge (`attacker`) has an Attack Speed (AS) that is greater than or equal to the opponent's (`defender`) Attack Speed plus a defined threshold.
- **Formula:** `attacker.attack_speed >= defender.attack_speed + speed_difference_threshold`
- **Threshold:** 5 (Assumed value, defined in `data/skills.yaml`)
- `[TDD: Test Charge activation threshold]`

### 3.3. Effect: Second Combat Round

- If the activation condition and threshold are met, a *new, full round of combat* is initiated immediately between the same two units.
- This second round follows the standard combat sequence (initiator attacks first, potential counter, potential follow-ups based on AS).
- Skills can activate normally during this second round (e.g., Wrath, Adept, Sol, Luna).
- **Important:** This is *not* simply an extra attack like Adept; it's a complete re-run of the combat sequence.
- `[TDD: Test second combat round initiation]`

### 3.4. Activation Limit

- Charge is intended to activate only **once** per combat *initiation*.
- This means if Charge triggers a second round, the check for Charge does *not* happen again after that second round, even if the speed condition is still met. This prevents infinite combat loops.
- The `activation_limit: 1` parameter in the skill definition enforces this.
- `[TDD: Test Charge single activation limit]`

### 3.5. Nihil Interaction

- The Charge skill activation should be negated if the *opponent* possesses the **Nihil** skill.
- Nihil prevents enemy combat skills from activating.
- The check for Nihil should occur before attempting to activate Charge.
- `[TDD: Test Nihil negates Charge]`

### 3.6. Normal Combat

- Combat scenarios where neither unit has Charge, or where the Charge skill holder does not meet the AS threshold, should proceed normally without initiating a second round.
- `[TDD: Test combat without Charge works normally]`

## 4. Integration Points (`CombatSystem`)

### 4.1. Location of Check

- The logic for checking Charge activation must be placed within the main combat execution flow, specifically *after* the standard combat round loop/sequence has fully completed, but *before* finalizing the combat results (e.g., calculating EXP, fatigue, checking for death).

### 4.2. Required Data

- The checking function needs access to:
    - The `attacker` unit object.
    - The `defender` unit object.
    - Both units' calculated `attack_speed` for the combat.
    - Both units' list of `skills`.
    - A flag or state variable to track if Charge has already activated *in this specific combat initiation* (to respect the activation limit).

### 4.3. Re-initiating Combat

- If Charge activates, the `CombatSystem` needs a mechanism to re-execute the combat round logic. This could be:
    - A loop structure within the main combat function that continues as long as a "run another round" flag (set by Charge) is true.
    - A recursive call to the combat round execution function (care must be taken to manage state and prevent stack overflow, though the activation limit makes deep recursion unlikely).
- The state indicating Charge has already activated must persist across these rounds within the same initiation context.

## 5. Pseudocode

```pseudocode
FUNCTION execute_combat(attacker, defender):
  // --- Standard Combat Round ---
  combat_results = run_standard_combat_round(attacker, defender)
  
  // Check if either unit died during the standard round
  IF attacker.current_hp <= 0 OR defender.current_hp <= 0:
    RETURN combat_results // Combat ends if someone died

  // --- Charge Skill Check ---
  charge_activated_this_initiation = FALSE // Reset per initiation

  // Check if Attacker has Charge and Defender does NOT have Nihil
  IF attacker.has_skill("CHARGE") AND NOT defender.has_skill("NIHIL"):
    // Check AS threshold and activation limit
    threshold = get_skill_param(attacker, "CHARGE", "speed_difference_threshold", default=5)
    limit = get_skill_param(attacker, "CHARGE", "activation_limit", default=1) // Currently 1

    IF NOT charge_activated_this_initiation: // Check limit
      IF attacker.attack_speed >= defender.attack_speed + threshold:
        // [TDD: Test Charge activation threshold]
        // [TDD: Test Nihil negates Charge] - Implicitly tested by Nihil check above
        
        // Mark Charge as activated for this initiation
        charge_activated_this_initiation = TRUE 
        // [TDD: Test Charge single activation limit] - Tested by checking flag again if loop existed

        // Log or display Charge activation message

        // --- Initiate Second Combat Round ---
        // [TDD: Test second combat round initiation]
        second_round_results = run_standard_combat_round(attacker, defender) 
        
        // Combine results (e.g., add damage, log events)
        combat_results.append(second_round_results)

        // Check if either unit died during the second round
        IF attacker.current_hp <= 0 OR defender.current_hp <= 0:
           RETURN combat_results // Combat ends if someone died in the second round

  // Check if Defender has Charge and Attacker does NOT have Nihil (Symmetric Check)
  ELSE IF defender.has_skill("CHARGE") AND NOT attacker.has_skill("NIHIL"):
     threshold = get_skill_param(defender, "CHARGE", "speed_difference_threshold", default=5)
     limit = get_skill_param(defender, "CHARGE", "activation_limit", default=1)

     IF NOT charge_activated_this_initiation: // Check limit (shared flag for the initiation)
        IF defender.attack_speed >= attacker.attack_speed + threshold:
           charge_activated_this_initiation = TRUE
           // Log or display Charge activation message
           
           // --- Initiate Second Combat Round (Defender "initiates" this round) ---
           // Note: The 'run_standard_combat_round' needs to handle who attacks first based on context.
           // If Charge triggers for the original defender, they might attack first in the *second* round.
           // This needs clarification - typically the original initiator still goes first in FE.
           // Assuming original initiator still goes first for simplicity here.
           second_round_results = run_standard_combat_round(attacker, defender) 
           combat_results.append(second_round_results)

           IF attacker.current_hp <= 0 OR defender.current_hp <= 0:
              RETURN combat_results

  // --- Finalize Combat ---
  // Calculate EXP, fatigue, etc., based on combined combat_results
  // [TDD: Test combat without Charge works normally] - Tested if no Charge blocks execute

  RETURN combat_results

// Helper function (assumed existing)
FUNCTION run_standard_combat_round(initiator, target):
  // Executes the sequence:
  // 1. Initiator attacks (considers Brave, Adept, etc.)
  // 2. Target counterattacks (if possible, considers skills)
  // 3. Initiator follow-up (if Pursuit/AS allows)
  // 4. Target follow-up (if Pursuit/AS allows)
  // Returns results (damage dealt, hits, misses, skill activations in this round)
  ...

```

## 6. TDD Anchors

- `[TDD: Test Charge activation threshold]` - Verify Charge triggers only when AS difference is >= 5.
- `[TDD: Test second combat round initiation]` - Verify a full second round occurs when Charge activates.
- `[TDD: Test Charge single activation limit]` - Verify Charge triggers only once even if the AS condition remains true after the second round.
- `[TDD: Test Nihil negates Charge]` - Verify Charge does not trigger if the opponent has Nihil.
- `[TDD: Test combat without Charge works normally]` - Verify standard combat completes without a second round if Charge is not present or conditions aren't met.