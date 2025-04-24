# Thracia 776: Enemy AI Behavior Specification

This document outlines the typical AI behaviors observed in Fire Emblem: Thracia 776.

## 1. General Behavior Routines

-   **Aggressive:** Moves towards and attacks the nearest player unit within range.
-   **Stationary Guard:** Does not move unless a player unit enters its attack range.
-   **Pursuit:** Targets a specific unit or type of unit, potentially ignoring closer threats.
-   **Flee:** Moves away from player units, especially when HP is low.
-   *(Specific routines may be assigned per enemy unit or group in chapter data)*

## 2. Targeting Priorities

-   Prioritizes units they can **defeat in one round**.
-   Prioritizes units they can **damage significantly**.
-   Prioritizes units that **cannot counter-attack**.
-   Prioritizes units with **low HP** or **low Def/Mag**.
-   May target specific units based on chapter objectives (e.g., targeting Leif, villagers).

## 3. Capture AI

-   Will attempt to **Capture** vulnerable player units instead of killing them if conditions are met (`AI Bld > Target Bld` or AI mounted).
-   Prioritizes units that are **unarmed**, **low HP**, or have **low Build**.
-   After capturing, AI unit suffers halved stats and may have halved movement.
-   AI will attempt to **take items** from captured player units.
-   AI will attempt to move towards **escape points** while carrying a captured unit.

## 4. Steal AI

-   Enemy Thieves prioritize opening **treasure chests**.
-   May attempt to **Steal** items from player units if `AI Spd > Target Spd` and `AI Bld >= Item Weight`. Prioritizes valuable items.

## 5. Staff & Siege AI

-   Uses **status staves** (Sleep, Silence, Berserk) on vulnerable player targets (typically low Mag). Requires `AI Mag > Target Mag`.
-   Uses **healing staves** on nearby damaged allies.
-   Uses **siege tomes / ballistae** to attack targets at maximum range.
-   **Important:** AI targeting for staves and siege weapons **ignores player Fog of War**.

## 6. Skill Usage

-   Uses innate or equipped combat skills automatically when conditions are met (e.g., Wrath on counter-attack, Charge if conditions met).
-   Does not typically use skills strategically (e.g., holding back a Charge unit).

## 7. Fog of War Interaction

-   Enemy units generally **ignore player Fog of War** limitations for movement and targeting. They behave as if they can see all player units regardless of the player's vision.
-   This means enemies can target units outside the player's current vision and move directly towards unseen units. 