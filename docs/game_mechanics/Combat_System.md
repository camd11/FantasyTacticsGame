# Thracia 776: Combat System Specification

This document details the combat formulas and mechanics of Fire Emblem: Thracia 776.

## 1. Combat Flow

1.  **Initiation:** Attacker strikes first (unless Ambush skill).
2.  **Counter-Attack:** Defender strikes back if possible (survived, has weapon for correct range).
3.  **Follow-up (Attacker):** If Attacker AS >= Defender AS + 4, attacker strikes again.
4.  **Follow-up (Defender):** If Defender AS >= Attacker AS + 4, defender strikes again (if survived).

-   **Skill Modifiers:** Skills like Ambush change attack order. Skills like Adept (Continue), Astra add extra hits. Brave weapons grant immediate extra hits. Wrath guarantees crit on counter.

## 2. Core Combat Formulas

### 2.1. Attack (Atk)
-   **Physical:** `Attacker Str + Weapon Might`
-   **Magical:** `Attacker Mag + Tome Might`
-   **Effectiveness:** If a weapon is effective (e.g., Armorslayer vs Armor), its Might is tripled (x3) before adding Str/Mag.

### 2.2. Attack Speed (AS)
-   **For All Weapons:** `AS = Spd - MAX(0, Weapon Weight - Bld)`
    -   Build (Bld) mitigates weapon weight penalty for all weapon types, including tomes.
    -   *Note: This is a custom implementation that deviates from Thracia 776, where Con only mitigates physical weapon weight.*
-   Used for follow-up attacks and Avoid calculation.

### 2.3. Hit Rate (Displayed Formula Components)
-   `Weapon Hit`
-   `+ (Attacker Skl * 2)`
-   `+ Attacker Lck`
-   `+ Support Bonus` (Typically +10 per supporting unit, max +30)
-   `+ Leadership Bonus` (Total LS stars * 3)
-   `+ Charisma Bonus` (+10 if near unit with Charisma skill/King Sword)
-   `+ Weapon Triangle Bonus` (+5 for advantage, -5 for disadvantage)
-   `- Target Avoid`
-   **Final Hit %:** The result is capped between 1% and 99%. Uses a 1 RN system (displayed hit is actual hit chance).

### 2.4. Avoid (Avo)
-   `(Target AS * 2)`
-   `+ Target Lck`
-   `+ Support Bonus`
-   `+ Leadership Bonus`
-   `+ Charisma Bonus`
-   `+ Terrain Avoid Bonus` (e.g., Forest, Fort, Throne)

### 2.5. Damage (Dmg)
-   `Attacker Calculated Atk - Target Defense Stat`
-   **Physical Defense:** `Target Def + Terrain Def Bonus`
-   **Magical Defense:** `Target Mag + Terrain Def Bonus`
-   **Damage Floor:** Minimum damage is 0.
-   **Critical Hit:** If a critical hit occurs, final calculated damage is doubled (x2).

### 2.6. Critical Rate (Crit %)
-   `(Weapon Crit + Attacker Skl + Support Bonus) - Target Crit Evade`
-   **Crit Cap (First Hit):** The calculated critical rate for the *first* attack in a combat round is capped at **25%**. (Exception: Wrath skill bypasses this cap).
-   **Crit Cap (Follow-up):** On follow-up attacks (doubles, Adept hits, Astra hits), the critical rate is calculated as: `MAX(0, (Weapon Crit + Skl + Supports - Target CEv)) * Attacker PCC`. The 25% cap does *not* apply here.

### 2.7. Critical Evade (CEv)
-   `(Target Lck / 2)` (Rounded down)
-   `+ Support Bonus`
-   Reduces the enemy's displayed critical rate.
-   **Crusader Scrolls:** Holding a Crusader Scroll negates non-Wrath critical hits entirely.

### 2.8. Follow-up Attack (Double Attack)
-   Occurs if a unit's **AS** is **4 or more** points higher than the opponent's AS.

## 3. Weapon Triangle

-   **Physical:** Swords > Axes > Lances > Swords.
    -   Advantage: +5 Hit
    -   Disadvantage: -5 Hit
-   **Magical (Anima):** Fire > Wind > Thunder > Fire.
    -   Advantage: +5 Hit
    -   Disadvantage: -5 Hit
-   **Light & Dark vs Anima:**
    -   Light/Dark have +5 Hit vs Fire/Wind/Thunder.
    -   Fire/Wind/Thunder have -5 Hit vs Light/Dark.
-   **Light vs Dark:** Neutral (+0 Hit).
-   **Outside Triangle:** Bows, Staves.

## 4. Staff Usage

### 4.1. Staff Accuracy
-   Staves can miss.
-   **Formula:** `MIN(99, MAX(1, Base Staff Hit + (User Skl * 4)))`
-   **Base Staff Hit:**
    -   100% for Torch staff.
    -   60% for most others (Heal, Mend, Warp, Restore, Status Staves, etc.).

### 4.2. Status Staff Condition
-   For staves like Sleep, Silence, Berserk, Thief:
    -   Requires `User Mag > Target Mag` to potentially hit.
    -   Automatically fails if `Target Mag >= User Mag`.
    -   Automatically fails if the target is standing on a Throne or Gate tile.

### 4.3. Staff Double-Casting
-   Applies only to Heal (Live), Mend (Relive), Physic (Reblow).
-   **Activation Chance:** `(User Spd + User Skl + User Lck) / 2 %`
-   Only occurs if the target is not fully healed by the first cast. 