# Thracia 776: Progression Systems Specification

This document outlines unit progression via Experience, Leveling, Promotion, and Weapon Ranks in Fire Emblem: Thracia 776.

## 1. Experience (EXP) and Leveling

-   **EXP Gain Sources:**
    -   **Combat:** Awarded for hitting an enemy, defeating an enemy (bonus EXP), attacking bosses (bonus EXP), defeating thieves (bonus EXP).
    -   **Staves:** Awarded *only* Weapon Experience (WExp), no level EXP.
    -   **Other:** Dancing (for Dancer class), Stealing (for Thief class).
-   **EXP Formula:** The exact formula is complex, depending on relative levels, class power values, and action type. Generally, defeating higher-level/stronger enemies yields more EXP.
-   **Level Up:** Occurs automatically when a unit reaches 100 EXP. EXP resets to 0.
-   **Stat Gains:** Upon level up, each stat has a percentage chance to increase by 1, based on the character's individual growth rates.
    -   Growable Stats: HP, Str, Mag, Skl, Spd, Lck, Def, Bld, Mov.
    -   Build (Bld) and Movement (Mov) growths are typically very low (1-5%).
-   **Stat Caps:** Universal cap of 20 for Str, Mag, Skl, Spd, Lck, Def, Bld, Mov. HP cap is 80.
-   **Growth Modification:**
    -   **Elite Skill:** Doubles all EXP gained.
    -   **Crusader Scrolls:** Holding a scroll modifies the unit's growth rates for that level-up (see `docs/game_mechanics/Items_Equipment.md` and `docs/research/New_Stats.md`).

## 2. Promotion (Class Change)

-   **Method:** Most base classes can promote after reaching Level 10.
-   **Item:** Promotion is triggered by using a consumable **Knight Proof** item on an eligible unit.
-   **Universality:** The Knight Proof works for almost all standard promotable classes (e.g., Social Knight, Axe Fighter, Mage, Priest, Pegasus Rider).
-   **Exceptions:**
    -   Lord (Leif) promotes via story event.
    -   Sister (Linoan) promotes via story event.
    -   Thief (Lara) changes to Dancer class via story event (not a standard promotion).
    -   Units already in an advanced/promoted class cannot promote further.
-   **Promotion Gains:**
    -   Grants fixed base stat increases specific to the class change (see `docs/research/New_Stats.md` for table).
    -   Increases weapon ranks by one level (adds 50 WExp) in currently proficient weapon types.
    -   May grant proficiency (Rank E, 0 WExp) in new weapon types associated with the promoted class.
    -   Stats cannot exceed the universal caps (20/80).

## 3. Weapon Experience (WExp) & Ranks

-   **Ranks:** Determine which weapons/staves a unit can equip.
    -   Levels: E (lowest) -> D -> C -> B -> A (highest).
    -   '*' (Star): Personal Rank for character-locked weapons.
-   **WExp Gain:**
    -   **Weapons/Tomes:** +1 WExp per use (hit, miss, or kill).
    -   **Staves:** Variable WExp gain per use based on the *staff's rank* (not the user's rank):
        -   E-Rank Staff: +1 WExp
        -   D-Rank Staff: +2 WExp
        -   C-Rank Staff: +3 WExp
        -   B-Rank Staff: +4 WExp
        -   A-Rank Staff: +5 WExp
        -   *-Rank Staff: +10 WExp
-   **Rank Up:** Automatically occurs when WExp for a weapon type reaches 50. Resets WExp to 0 for the new rank.
    -   Example: E rank (0 WExp) -> Use 50 times -> D rank (0 WExp).
-   **Effect:** Higher ranks unlock the ability to use stronger equipment. Rank itself provides no direct combat bonuses. 