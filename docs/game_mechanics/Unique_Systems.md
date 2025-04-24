# Thracia 776: Unique Systems Specification

This document details systems unique or particularly characteristic to Fire Emblem: Thracia 776, such as Capture, Fatigue, Dismounting, Rescue, Supports, and Movement/Leadership Stars.

## 1. Capture

-   **Purpose:** Allows acquiring enemy items/weapons, crucial due to limited gold/shops.
-   **Action:** Player unit uses 'Capture' command against an adjacent, unmounted enemy.
-   **Condition:** Requires a melee weapon equipped. Also requires:
    -   If player unit is unmounted: `Player Bld > Enemy Bld`
    -   If player unit is mounted: Condition automatically met.
-   **Combat:** Initiator's combat stats (Str, Mag, Skl, Spd, Def) are **halved** during the capture attempt.
-   **Success:** If the enemy's HP reaches 0 during the capture combat, they are Captured (not killed).
-   **Carrying Captive:**
    -   Captor carries the enemy unit (occupies the same tile visually).
    -   Captor suffers **halved stats** (Str, Mag, Skl, Spd, Def).
    -   Captor's **Movement is halved** (rounded down) if `Captive Bld > Carrier Bld / 2` (adjust carrier Bld +5 if mounted).
-   **Item Seizure:** While carrying, use the Trade/Item command on the captive to access and take their inventory.
-   **Release:** Use the 'Release' command to free the captive. They are removed from the map. This counts as sparing them (relevant for some recruitment conditions).
-   **Enemy Capture:** Enemies can capture player units under the same Bld/Mount conditions. Captured player units lose their items and are removed from the map if the captor escapes.

## 2. Fatigue

-   **Mechanism:** A hidden counter tracking unit exertion.
-   **Applies To:** All player units **except** the main Lord (Leif).
-   **Accumulation:** Units gain Fatigue points for performing actions:
    -   Combat (attacking or being attacked): +1 Fatigue
    -   Staff Usage: +1 to +5 Fatigue (based on staff rank, similar to WExp gain)
    -   Dance: +1 Fatigue
    -   Steal: +1 Fatigue
-   **Fatigue Threshold:** At the end of a chapter, compare `Total Fatigue` vs `Unit's Max HP`.
-   **Consequence:** If `Fatigue > Max HP`, the unit becomes "Fatigued" and **cannot be deployed** in the next chapter.
-   **Recovery:**
    -   Fatigue resets to 0 if a unit sits out a chapter (is not deployed).
    -   Using a consumable **S Drink** item during chapter preparations instantly resets a unit's Fatigue to 0.
-   **Impact:** Encourages roster rotation and careful unit management.

## 3. Dismounting

-   **Trigger:**
    -   **Automatic:** Mounted units (Cavalry, Fliers) automatically dismount when entering indoor maps.
    -   **Voluntary:** Can use the 'Dismount' command on outdoor maps.
-   **Effects Upon Dismounting:**
    -   Unit visually changes to a corresponding infantry class.
    -   **Stats are reduced:** Loses the fixed "Mounting Gains" (refer to `docs/research/New_Stats.md` for specific stat losses per class).
    -   **Movement:** Movement type changes to Infantry (lower base Mov, affected by terrain costs).
    -   **Weapon Access:** Typically restricted to **Swords only**, regardless of original mounted proficiencies (Lances, Axes).
    -   **Skills:** Loses the innate **Canto** ability.
    -   **Weaknesses:** Loses mount-specific weaknesses (e.g., Horseslayer, Bows vs Fliers) but gains infantry vulnerabilities.
-   **Remounting:**
    -   Possible only on outdoor maps.
    -   Uses the 'Mount' command.
    -   Restores original mounted class, stats (re-applies Mounting Gains), movement type, weapon access, and Canto.

## 4. Rescue

-   **Action:** Unit uses 'Rescue' command on an adjacent allied unit.
-   **Condition:** `Rescuer Bld >= Target Bld / 2`.
    -   If the rescuer is mounted, add +5 to their Bld for this check.
-   **Rule:** Cannot rescue a unit that is already rescuing/carrying another unit.
-   **Effect:** Rescuer picks up the allied unit. Carried ally is removed from the map temporarily but remains associated with the rescuer.
-   **Penalties on Rescuer:**
    -   **Stats Halved:** Str, Mag, Skl, Spd, Def are halved.
    -   **Movement Halved:** Movement stat is halved (rounded down) if `Carried Unit Bld > Carrier Bld / 2` (adjust carrier Bld +5 if mounted).
-   **Commands:**
    -   **Take:** Transfer a carried unit from an adjacent ally to the current unit (if conditions met).
    -   **Give:** Transfer the currently carried unit to an adjacent ally (if conditions met).
    -   **Drop:** Place the carried unit on a valid adjacent, unoccupied tile. Consumes the action for the turn.

## 5. Support System

-   **Mechanism:** Fixed, hidden relationships between specific pairs or groups of characters.
-   **Activation:** Provides bonuses passively when supporting units are within **3 tiles** of each other.
-   **Bonuses:** Typically grants **+10 Hit, +10 Avoid, +10 Crit, +10 Crit Evade** per supporting unit in range. Some pairs might grant +20. Bonuses stack up to a maximum of +30 from all support sources.
-   **Directionality:** Supports can be one-way or two-way.
-   **No Growth:** Support relationships exist from the start; there are no support conversations or levels to build.

## 6. Movement Stars (MS / Re-Action)

-   **Trait:** Characters have an innate Movement Star rating (0-5 stars).
-   **Effect:** After completing an action (Move + Act), the unit has a **(5 * MS)% chance** to gain another full action (move and act again) in the same turn.
-   **Indication:** Often indicated by a musical note (♪) icon when activated.

## 7. Leadership Stars (LS)

-   **Trait:** Characters (usually leaders like Leif, key enemies) have an innate Leadership Star rating (0-5 stars).
-   **Effect:** Provides a **global passive bonus** to all allied units on the map.
-   **Calculation:** `(Sum of LS from all deployed allied leaders) * 3 = % Bonus`
-   **Bonus Applied:** Grants +X% Hit and +X% Avoid to all allies (where X is the calculated bonus). 