# Specification: Nihil Skill (Thracia 776)

**Status: Implemented**

## 1. Overview

The Nihil skill is a passive personal skill that negates the effects of certain enemy combat skills and critical hits during battle when equipped by a unit.

## 2. Functional Requirements

### 2.1. Skill Effect

- When a unit possessing the Nihil skill engages in combat (either initiating or being attacked), specific combat-related skills possessed by the opponent **do not activate** against the Nihil user for that round of combat.
- Additionally, the opponent's critical hit chance against the Nihil user is reduced to 0% for that round of combat.

### 2.2. Negated Skills

Nihil specifically negates skills that activate *during* combat to provide an offensive or defensive advantage related to the attack exchange itself. Based on `research.md` and common Fire Emblem mechanics, the following types of skills **are negated** by Nihil:

- **Offensive Activation Skills:**
    - Wrath (Forces critical on counterattack)
    - Adept/Continue (Grants extra attack chance)
    - Sol (Heals user based on damage dealt)
    - Luna (Negates enemy defense/resistance)
    - Astra/Shooting Star (Allows multiple consecutive attacks)
    - Vantage (Allows unit to attack first when attacked at low HP)
- **Defensive Activation Skills:**
    - Pavise (Chance to negate physical damage)
    - *Note: Other similar defensive procs would also be negated.*
- **Critical Hits:**
    - Any critical hit chance the opponent would normally have against the Nihil user is nullified. This includes base critical chance, critical bonuses from skills (like Wrath), and PCC-boosted criticals on follow-up attacks.

The following types of skills **are NOT negated** by Nihil:

- **Passive Stat Modifiers:** Skills that provide flat stat bonuses (e.g., +Str, +Def) are not negated.
- **Aura Skills:** Skills like Leadership (Authority) or Charisma that provide bonuses to nearby allies are not negated.
- **Movement Skills:** Skills like Canto are not negated.
- **Utility Skills:** Skills like Steal, Dance, or Locktouch are not negated.
- **Status Effects:** Status conditions inflicted by staves (Sleep, Silence, Berserk, Poison) are not negated by Nihil.
- **Defensive Skills (Conditional Avoid/Survival):** Skills like Prayer/Miracle (which boost Avoid at low HP) are generally *not* negated as they affect the unit's base stats/state rather than modifying the combat exchange directly.

### 2.3. Activation

- Nihil is a passive skill.
- It is always active for any unit possessing it.
- The check for Nihil occurs during the combat calculation phase, specifically *before* checking if any of the opponent's negatable skills would activate, and *before* calculating the opponent's critical hit chance against the Nihil user.

## 3. Integration Points

The implementation of Nihil requires modifications within the `CombatSystem` or `CombatCalculator` module(s):

1.  **Combat Initialization/Setup:** Before initiating the sequence of attacks in a combat round, check if the defender possesses the Nihil skill.
2.  **Opponent Skill Activation Checks:** Modify the logic that checks for opponent skill activations (e.g., `_check_vantage`, `_check_wrath`, `_check_luna`, `_check_critical_hit`, etc.). These checks should first verify if the *target* of the skill's effect (the Nihil user) possesses Nihil. If they do, the skill activation check should be skipped or return false for that specific interaction.
    ```pseudocode
    FUNCTION check_opponent_skill_activation(attacker, defender, skill_to_check):
        // Check if the defender (target of the skill) has Nihil
        IF defender.has_skill("Nihil"):
            // Check if the skill is one negated by Nihil
            IF skill_to_check IN ["Vantage", "Wrath", "Luna", "Sol", "Adept", "Pavise", "Astra"]:
                RETURN FALSE // Nihil negates this skill
            ENDIF
        ENDIF

        // Proceed with normal skill activation check
        result = perform_standard_skill_check(attacker, skill_to_check)
        RETURN result
    ENDFUNCTION

    FUNCTION calculate_critical_chance(attacker, defender):
        // Check if the defender has Nihil
        IF defender.has_skill("Nihil"):
            RETURN 0 // Nihil negates critical hits
        ENDIF

        // Proceed with normal critical chance calculation
        crit_chance = perform_standard_crit_calculation(attacker, defender)
        RETURN crit_chance
    ENDFUNCTION
    ```
3.  **Combat Loop:** Ensure that within the loop handling attacks and counterattacks, the checks for opponent skills and critical hits incorporate the Nihil check against the target of each potential skill activation or critical hit.

## 4. Data Definition (`data/skills.yaml`)

```yaml
Nihil:
  name: Nihil
  description: Negates enemy combat skills (like Wrath, Luna) and critical hits.
  type: Passive
  effects:
    - type: NEGATE_ENEMY_SKILLS
      skills: [Wrath, Adept, Sol, Luna, Astra, Pavise, Vantage] # List of skill IDs negated
    - type: NEGATE_ENEMY_CRITICAL
```

## 5. Pseudocode Logic

```pseudocode
MODULE CombatCalculator

  FUNCTION calculate_combat_outcome(attacker, defender):
    // ... (Initial setup, determine attack order, etc.)

    // Check for Nihil on both units
    attacker_has_nihil = attacker.has_skill("Nihil")
    defender_has_nihil = defender.has_skill("Nihil")

    // --- Attacker's First Strike ---
    // Check Vantage (only if defender attacks first normally)
    vantage_activates = FALSE
    IF should_check_vantage(defender, attacker) AND NOT attacker_has_nihil: // Check Nihil on attacker (target of Vantage)
        vantage_activates = check_skill_activation(defender, "Vantage")
    ENDIF
    // (Adjust attack order if vantage_activates)

    // Calculate attacker's hit, damage, crit
    attacker_crit_chance = 0
    IF NOT defender_has_nihil: // Check Nihil on defender (target of crit)
        attacker_crit_chance = calculate_critical_chance(attacker, defender)
        // Apply PCC cap if first hit
        IF is_first_hit(attacker):
             attacker_crit_chance = min(attacker_crit_chance, 25)
        ENDIF
    ENDIF
    // Check attacker skills (Sol, Luna, Adept, etc.) - only if defender does NOT have Nihil
    attacker_skill_procs = {}
    IF NOT defender_has_nihil:
        IF check_skill_activation(attacker, "Sol"): attacker_skill_procs["Sol"] = TRUE
        IF check_skill_activation(attacker, "Luna"): attacker_skill_procs["Luna"] = TRUE
        // etc. for other negatable skills
    ENDIF

    // Perform attack roll, apply damage, handle skill effects (if any)
    // ...

    // --- Defender's Counterattack (if applicable) ---
    IF defender.can_counterattack():
        // Calculate defender's hit, damage, crit
        defender_crit_chance = 0
        IF NOT attacker_has_nihil: // Check Nihil on attacker (target of crit)
            defender_crit_chance = calculate_critical_chance(defender, attacker)
            // Check Wrath - only if attacker does NOT have Nihil
            IF check_skill_activation(defender, "Wrath"):
                 defender_crit_chance = 100 // Wrath forces crit
            ENDIF
            // Apply PCC cap if first hit (counter is defender's first hit)
             IF is_first_hit(defender):
                 defender_crit_chance = min(defender_crit_chance, 25)
            ENDIF
        ENDIF

        // Check defender skills (Sol, Luna, Adept, Pavise etc.) - only if attacker does NOT have Nihil
        defender_skill_procs = {}
        IF NOT attacker_has_nihil:
            IF check_skill_activation(defender, "Sol"): defender_skill_procs["Sol"] = TRUE
            IF check_skill_activation(defender, "Luna"): defender_skill_procs["Luna"] = TRUE
            IF check_skill_activation(defender, "Pavise"): defender_skill_procs["Pavise"] = TRUE
            // etc.
        ENDIF

        // Perform counterattack roll, apply damage (check Pavise), handle skill effects
        // ...
    ENDIF

    // --- Follow-up Attacks (if applicable) ---
    // Check if attacker doubles
    IF attacker_doubles(attacker, defender):
        // Calculate attacker's hit, damage, crit for follow-up
        attacker_followup_crit_chance = 0
        IF NOT defender_has_nihil: // Check Nihil on defender
            attacker_followup_crit_chance = calculate_critical_chance(attacker, defender)
            // Apply PCC multiplier (no cap on follow-up)
            attacker_followup_crit_chance *= attacker.get_pcc()
            attacker_followup_crit_chance = min(attacker_followup_crit_chance, 100)
        ENDIF
        // Check attacker skills for follow-up (Sol, Luna, Adept) - only if defender does NOT have Nihil
        // ... (similar checks as first strike)

        // Perform follow-up attack roll, apply damage, handle skills
        // ...
    ENDIF

    // Check if defender doubles (less common, but possible)
    // ... (Similar logic, checking Nihil on attacker for crit/skills)

    // Check Adept activations (if not negated by Nihil)
    // ...

    // Finalize combat results (HP changes, EXP gain, etc.)
    // ...

    RETURN combat_results
  END FUNCTION

ENDMODULE
```

## 6. Test-Driven Development (TDD) Anchors

-   `[TDD: Test Nihil negates Vantage]` - Setup: Attacker (low HP) vs Defender (Nihil). Expected: Defender attacks first (Vantage negated).
-   `[TDD: Test Nihil negates Wrath]` - Setup: Attacker vs Defender (Nihil, low HP). Defender counterattacks. Expected: Defender's counterattack is not a critical hit (Wrath negated).
-   `[TDD: Test Nihil negates Luna]` - Setup: Attacker (Luna) vs Defender (Nihil, high Def). Expected: Attacker's damage is calculated using Defender's full Def (Luna negated).
-   `[TDD: Test Nihil negates Sol]` - Setup: Attacker (Sol) vs Defender (Nihil). Attacker hits. Expected: Attacker does not heal HP (Sol negated).
-   `[TDD: Test Nihil negates Adept]` - Setup: Attacker (Adept, high Skl) vs Defender (Nihil). Expected: Attacker only performs standard attacks (1 or 2 based on AS), no extra Adept attack occurs.
-   `[TDD: Test Nihil negates Pavise]` - Setup: Attacker vs Defender (Nihil, Pavise). Attacker hits. Expected: Defender takes full damage (Pavise negated).
-   `[TDD: Test Nihil negates Critical Hit]` - Setup: Attacker (high Crit weapon/Skl) vs Defender (Nihil). Expected: Attacker's critical hit chance displayed in forecast and used in calculation is 0%.
-   `[TDD: Test Nihil negates PCC Critical]` - Setup: Attacker (high Crit, high PCC, doubles) vs Defender (Nihil). Expected: Attacker's second hit has 0% critical chance (PCC boost negated by Nihil).
-   `[TDD: Test Nihil does not negate passive stat skill]` - Setup: Attacker vs Defender (Nihil, has skill like +5 Str). Expected: Defender's stats reflect the +5 Str bonus during combat.
-   `[TDD: Test Nihil does not negate Leadership]` - Setup: Attacker vs Defender (Nihil). Enemy leader with Leadership stars nearby. Expected: Defender receives Hit/Avo bonus from Leadership.
-   `[TDD: Test Nihil does not negate status staff]` - Setup: Enemy uses Sleep staff on Unit (Nihil). Expected: Unit can be put to sleep if staff hits (Nihil does not block).
-   `[TDD: Test combat without Nihil works normally (Vantage)]` - Setup: Attacker (low HP) vs Defender (No Nihil). Expected: Attacker attacks first (Vantage activates).
-   `[TDD: Test combat without Nihil works normally (Wrath)]` - Setup: Attacker vs Defender (Wrath, low HP, No Nihil). Defender counterattacks. Expected: Defender's counterattack is a critical hit.
-   `[TDD: Test combat without Nihil works normally (Critical)]` - Setup: Attacker (high Crit) vs Defender (No Nihil). Expected: Attacker has a non-zero critical chance.