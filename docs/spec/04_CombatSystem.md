# Specification: Combat System

This document outlines the data structures and mechanics for combat encounters in the Fire Emblem Thracia 776 recreation.

## 1. Core Concepts

*   **Combat Encounter**: Occurs when a unit initiates an attack against an enemy unit, or when an enemy unit attacks a player unit.
*   **Attack Round**: A single exchange of blows. Typically, the initiator attacks first, and if the defender survives and can counter-attack, they do so.
*   **Follow-up Attack (Double Attack)**: If a unit's Attack Speed (AS) is sufficiently higher than their opponent's (typically by 4 or more), they may attack a second time.
*   **Attack Speed (AS)**: Calculated as `Speed - (WeaponWeight - Constitution)`. If `WeaponWeight < Constitution`, then `AS = Speed`.
*   **Hit Rate**: The chance of an attack successfully landing.
*   **Avoid Rate**: The chance of an attack being dodged.
*   **Critical Hit**: An attack that deals triple damage.
*   **Critical Evade**: The ability to negate enemy critical hits (e.g., Awareness skill, some items).
*   **Weapon Triangle/Effectiveness**: While Thracia 776 doesn't have a strict weapon triangle like later games, weapon effectiveness (e.g., bows vs. fliers, special weapons vs. armor) and skills play a significant role.
*   **Skills**: Abilities that can influence combat outcomes (e.g., Vantage, Wrath, Adept, Luna).
*   **Terrain Bonuses**: Terrain can provide Defense and Avoid bonuses to units, affecting combat calculations (from [`TerrainDefense.csv`](FireEmblem5/TABLES/TerrainDefense.csv:0) and [`TerrainAvoid.csv`](FireEmblem5/TABLES/TerrainAvoid.csv:0)). Terrain does not grant Hit bonuses ([`TerrainHitAvoid.csv`](FireEmblem5/TABLES/TerrainHitAvoid.csv:0)).
*   **Weapon Effects**: Special properties of weapons that trigger during combat (e.g., Poison, Lifesteal, Devil, from [`WeaponEffectTable.csv`](FireEmblem5/TABLES/WeaponEffectTable.csv:0)).

## 2. Combat Flow

1.  **Initiation**: Attacker selects a target within their weapon's range.
    *   // TEST: Target must be within valid weapon range.
2.  **Pre-Combat Calculations**:
    a.  Determine attacker's and defender's relevant stats (Atk, Def/Res, Skl, Spd, Luk, Con).
    b.  Calculate Attack Speed (AS) for both units.
    c.  Calculate Hit Rate for the attacker.
    d.  Calculate Avoid Rate for the defender.
    e.  Calculate Critical Hit Rate for the attacker.
    f.  Calculate Critical Evade for the defender.
    *   // TEST: All pre-combat stats (AS, Hit, Avoid, Crit) must be calculated correctly.
3.  **Attacker's First Strike**:
    a.  Check for skills that activate before attack (e.g., Vantage for defender).
    b.  Roll for hit: `Random(0-99) < AttackerHitRate - DefenderAvoidRate`.
    c.  If hit:
        i.  Roll for critical: `Random(0-99) < AttackerCritRate - DefenderCritEvade`.
        ii. Calculate damage: `(AttackerAtk - DefenderDefOrRes)`. If crit, `Damage * 3`. Apply weapon effects (e.g., Lifesteal).
        iii.Apply damage to defender.
        iv. Check for skills that activate on hit/damage (e.g., Sol, Luna for attacker; Pavise for defender).
    d.  If miss: No damage.
    *   // TEST: Hit roll correctly determines if attack lands.
    *   // TEST: Crit roll correctly determines if attack is critical.
    *   // TEST: Damage calculation is correct (including crits and defenses).
    *   // TEST: Weapon effects (Poison, Lifesteal) apply correctly on hit.
4.  **Defender's Counter-Attack** (if defender survived and can counter):
    a.  Defender must have a weapon that can target the attacker's range.
    b.  Repeat step 3 for the defender's attack.
    *   // TEST: Defender only counters if they survive and have a valid weapon/range.
5.  **Follow-up Attacks**:
    a.  If `AttackerAS >= DefenderAS + 4`, attacker strikes again (repeat step 3).
    b.  If defender survived and can counter, and `DefenderAS >= AttackerAS + 4`, defender strikes again (repeat step 4).
    *   // TEST: Follow-up attacks trigger correctly based on AS difference.
6.  **Post-Combat**:
    a.  Apply any post-combat skill effects or status effects.
    b.  Grant EXP to participants.
    c.  Check for unit death. If Lord dies, game over.
    *   // TEST: EXP is awarded correctly after combat.
    *   // TEST: Unit death is handled correctly.

## 3. Key Formulas and Calculations

### 3.1. Attack Power (Atk)
*   Physical: `UnitStrength + WeaponMight`
*   Magical: `UnitMagic + WeaponMight`
    *   // TEST: Attack Power calculation is correct for physical and magical.

### 3.2. Defense Power (Def) / Resistance Power (Res)
*   Physical Defense: `UnitDefense + TerrainDefenseBonus`
*   Magical Defense: `UnitMagic + TerrainDefenseBonus` (Note: In Thracia 776, the Magic stat is used for both magical attack and magical defense; there is no separate Resistance stat for units).
    *   // TEST: Defense/Resistance calculation includes terrain bonuses.

### 3.3. Attack Speed (AS)
*   `AS = UnitSpeed - MAX(0, WeaponWeight - UnitConstitution)`
    *   // TEST: Attack Speed calculation correctly factors in Wt and Con.

### 3.4. Hit Rate (Displayed)
*   `DisplayedHit = WeaponHitRate + (UnitSkill * 2) + UnitLuck + SupportBonuses + SkillBonuses`
    *   // TEST: Displayed Hit Rate calculation is correct.

### 3.5. Avoid Rate
*   `Avoid = (UnitAttackSpeed * 2) + UnitLuck + TerrainAvoidBonus + SupportBonuses + SkillBonuses`
    *   // TEST: Avoid Rate calculation is correct.

### 3.6. Actual Hit Chance (%)
*   `ActualHit = DisplayedHitRateOfAttacker - AvoidRateOfDefender`
*   Clamped between 0 and 100.
    *   // TEST: Actual Hit Chance calculation is correct.

### 3.7. Critical Hit Rate (%)
*   `CritRate = WeaponCriticalRate + (UnitSkill / 2) + SupportBonuses + SkillBonuses (e.g., Wrath)`
    *   // TEST: Critical Hit Rate calculation is correct.

### 3.8. Critical Evade (%)
*   `CritEvade = UnitLuck + SupportBonuses + SkillBonuses (e.g., Awareness)`
    *   // TEST: Critical Evade calculation is correct.

### 3.9. Actual Critical Chance (%)
*   `ActualCrit = CritRateOfAttacker - CritEvadeOfDefender`
*   Clamped between 0 and 100.
    *   // TEST: Actual Critical Chance calculation is correct.

### 3.10. Damage
*   `Damage = AttackerAttackPower - DefenderDefenseOrResistancePower`
*   If Critical Hit: `Damage = Damage * 3`
*   Minimum damage is typically 0 (cannot heal via normal attack).
    *   // TEST: Damage calculation (normal and critical) is correct.

## 4. Special Combat Mechanics

*   **Effectiveness**: Certain weapons deal bonus Might (often x2 or x3 total Mt) against specific unit types (e.g., Bows vs. Fliers, Hammers vs. Armored). This bonus Mt is added before defense calculation.
    *   // TEST: Weapon effectiveness applies bonus Might correctly.
*   **Devil Weapon Effect**: (`from WeaponEffectTable.csv`) Chance to damage the wielder instead of the target.
    *   // TEST: Devil weapon effect triggers correctly and damages wielder.
*   **Lifesteal Weapon Effect**: (`from WeaponEffectTable.csv`) Heals wielder for a portion of damage dealt.
    *   // TEST: Lifesteal weapon effect heals wielder for correct amount.
*   **Poison Weapon Effect**: (`from WeaponEffectTable.csv`) Inflicts poison status on hit.
    *   // TEST: Poison status is applied on hit by poison weapons.
*   **Petrify/Sleep/Berserk Weapon Effects**: (`from WeaponEffectTable.csv`) Inflict respective status effects on hit.
    *   // TEST: Petrify, Sleep, Berserk statuses are applied correctly.
*   **Hel Effect**: (`from WeaponEffectTable.csv`) Reduces target's current HP to 1. Does not kill.
    *   // TEST: Hel effect correctly reduces target HP.
*   **Capture Mechanic**:
    *   Units can attempt to "Capture" an enemy unit instead of dealing lethal damage.
    *   To initiate a Capture, the attacker must have higher Constitution (Con) and Speed (Spd) than the target.
    *   If the "Capture" command is selected and conditions are met, the attacker's damage is halved, but if the attack reduces the target's HP to 0, the target is "Captured" instead of killed.
    *   A unit carrying a captured enemy has their Skill, Speed, and Movement halved (rounded down).
    *   Captured units can be released, or their items can be taken. If a captured unit is released, they become an NPC/ally (needs verification for FE5 specifics on allegiance change).
    *   If the capturer is defeated, the captured unit is freed.
    *   // TEST: Capture command only available if Con and Spd are higher.
    *   // TEST: Damage is halved during a capture attempt.
    *   // TEST: Target is captured (not killed) if HP reaches 0 during capture.
    *   // TEST: Capturer's Skl, Spd, Mov are halved while carrying.
    *   // TEST: Items can be taken from a captured unit.
    *   // TEST: Captured unit is freed if capturer is defeated.
*   **Combat Skills**:
    *   **Adept**: Chance to attack again immediately.
        *   // TEST: Adept triggers based on skill chance and grants extra attack.
    *   **Vantage**: Attack first if HP is below a threshold (e.g., 50%).
        *   // TEST: Vantage allows low-HP unit to attack first.
    *   **Wrath**: Grants +50 Crit if HP is below a threshold (or always active if unit can counter and is attacked).
        *   // TEST: Wrath grants critical bonus correctly.
    *   **Luna**: Ignores half of the enemy's Defense/Resistance.
        *   // TEST: Luna correctly reduces enemy defense for damage calculation.
    *   **Sol**: Heals HP equal to half of the damage dealt.
        *   // TEST: Sol correctly heals user based on damage dealt.
    *   **Pavise**: Chance to negate all damage from an attack.
        *   // TEST: Pavise triggers based on skill chance and negates damage.
    *   **Awareness**: Negates enemy critical hits.
        *   // TEST: Awareness skill negates enemy criticals.
    *   **Charge**: If unit can still act after combat, may initiate another round of combat.
        *   // TEST: Charge skill triggers correctly and allows another combat round.
    *   **Miracle**: If HP > 1, survive a lethal hit with 1 HP (chance based on Luck).
        *   // TEST: Miracle allows unit to survive lethal hit based on Luck.
*   **Leadership Stars**: Provide Hit and Avoid bonuses to nearby allied units. Each star might grant +3 or +5.
    *   // TEST: Leadership stars provide correct Hit/Avoid bonus to allies in range.

## 5. TDD Anchors

*   `// TEST: Combat_BasicAttack_HitDamage`: Attacker hits and deals correct damage.
*   `// TEST: Combat_BasicAttack_Miss`: Attacker misses.
*   `// TEST: Combat_CounterAttack_HitDamage`: Defender survives and counter-attacks, dealing damage.
*   `// TEST: Combat_FollowUp_Attacker`: Attacker performs a follow-up attack.
*   `// TEST: Combat_FollowUp_Defender`: Defender performs a follow-up attack.
*   `// TEST: Combat_CriticalHit_TripleDamage`: Critical hit deals 3x damage.
*   `// TEST: Combat_NoCrit_WithAwareness`: Awareness skill prevents a critical hit.
*   `// TEST: Combat_TerrainBonus_Defense`: Defender on a fort takes less damage.
*   `// TEST: Combat_TerrainBonus_Avoid`: Attacker misses defender on a forest due to avoid bonus.
*   `// TEST: Combat_WeaponEffect_Poison`: Target is poisoned after being hit by a poison weapon.
*   `// TEST: Combat_WeaponEffect_Lifesteal`: Attacker heals after hitting with a lifesteal weapon.
*   `// TEST: Combat_WeaponEffect_Devil`: Wielder of a devil weapon takes damage.
*   `// TEST: Combat_Skill_Vantage`: Unit with Vantage and low HP attacks first.
*   `// TEST: Combat_Skill_Wrath`: Unit with Wrath gains bonus critical chance.
*   `// TEST: Combat_Skill_Luna`: Luna skill correctly bypasses portion of enemy defense.
*   `// TEST: Combat_Effectiveness_BowVsFlier`: Bow deals effective damage to a flying unit.
*   `// TEST: Combat_Death_UnitRemoved`: Unit is removed from map upon reaching 0 HP.
*   `// TEST: Combat_EXP_Awarded`: Correct EXP is awarded to attacker and defender.
*   `// TEST: Combat_LeadershipStars_BonusApplied`: Units near a leader receive Hit/Avoid bonuses.

*   `// TEST: Combat_Capture_Successful`: Unit successfully captures an enemy.
*   `// TEST: Combat_Capture_ConditionsNotMet`: Capture command is unavailable or fails if Con/Spd are too low.
*   `// TEST: Combat_Capture_DamageHalved`: Damage dealt during a capture attempt is halved.
*   `// TEST: Combat_Capture_StatPenalties`: Capturing unit has Skl/Spd/Mov halved.
*   `// TEST: Combat_Capture_TakeItems`: Items are successfully taken from a captured unit.
*   `// TEST: Combat_Capture_ReleaseCaptured`: Captured unit is released.
*   `// TEST: Combat_Capture_FreedOnCapturerDefeat`: Captured unit is freed when the capturer is defeated.
This specification covers the primary aspects of combat. Further details on specific skill interactions or unique boss mechanics will be added as they are discovered or designed.