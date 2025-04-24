# Thracia 776: Skills Specification

This document details the various skills present in Fire Emblem: Thracia 776, their effects, and activation methods.

## Skill Categories

-   **Combat Skills:** Activate during battle, often modifying attacks or defense.
-   **Command Skills:** Add new actions to the unit's command menu (e.g., Steal, Dance).
-   **Passive Skills:** Always active, providing constant bonuses or effects (e.g., Elite, Charisma, Canto).

## Skill List & Effects

| Skill Name          | Aliases           | Type    | Activation / Effect                                                                                              | Notes                                  |
| :------------------ | :---------------- | :------ | :--------------------------------------------------------------------------------------------------------------- | :------------------------------------- |
| **Adept**           | Continue          | Combat  | **(AS)% chance** for an immediate extra attack after the unit's initial attack.                                  | Can trigger on counter-attacks too.    |
| **Ambush**          | Vantage           | Combat  | Unit **attacks first** when initiated upon by an enemy during the enemy phase.                                   |                                        |
| **Astra**           | Shooting Star Swd | Combat  | **(Skl)% chance** to perform **5 consecutive hits** at **half damage** each.                                     | Replaces normal attack if activated.   |
| **Awareness**       | Nihil             | Combat  | **Negates** enemy combat skills (Adept, Luna, Sol, Astra, Pavise) and enemy critical hits (including Wrath). | Does not negate enemy passive skills.  |
| **Bargain**         |                   | Passive | Halves prices when buying from shops.                                                                            | Skill Manual is unused/unavailable.    |
| **Big Shield**      | Pavise            | Combat  | **(Level)% chance** to completely negate incoming damage from an attack.                                          |                                        |
| **Canto**           |                   | Passive | Allows unit to use **remaining movement** after performing an action (Attack, Staff, Item, etc.).                  | Innate for mounted units. Blocked after Capture/Rescue. |
| **Charge**          | Accost, Duel      | Combat  | If unit and enemy both survive a combat round and unit's HP > 25% Max HP, triggers **another round of combat**. | Can trigger multiple times.            |
| **Charisma**        | Charm             | Passive | Grants **+10 Hit** and **+10 Avoid** to all allied units within **3 tiles**.                                       | Aura stacks with other Charisma units. |
| **Dance**           |                   | Command | Allows Dancer class to refresh an adjacent allied unit's turn, allowing them to act again.                     |                                        |
| **Elite**           | Paragon           | Passive | **Doubles all EXP** gained by the unit.                                                                          |                                        |
| **Luna**            | Moonlight Sword   | Combat  | **(Skl)% chance** to **ignore enemy Def/Mag**. Guarantees the attack will hit (100% accuracy).                    | Replaces normal attack if activated.   |
| **Miracle**         | Prayer            | Combat  | **(Luck * 3)% chance** to guarantee dodging an attack that would otherwise be lethal.                            | May also trigger at low HP.            |
| **Sol**             | Sun Sword         | Combat  | **(Skl)% chance** to **absorb HP** equal to the damage dealt. Guarantees the attack will hit (100% accuracy).     | Replaces normal attack if activated.   |
| **Steal**           |                   | Command | Allows Thief/Thief Fighter class to steal eligible items from adjacent enemies.                                  | Requires `User Spd > Target Spd` and `User Bld >= Item Weight`. |
| **Wrath**           |                   | Combat  | Guarantees a **critical hit** on all **counter-attacks** initiated during the enemy phase.                       | Bypasses the 25% first-hit crit cap.   |

## Acquisition Methods

-   **Innate:** Some characters start with skills (e.g., Othin - Wrath, Lara - Steal).
-   **Class:** Some classes grant skills inherently (e.g., Mounted units - Canto, Thief Fighter - Ambush).
-   **Weapons:** Some weapons grant skills while equipped (e.g., King Sword - Charisma).
-   **Manuals:** Consumable items teach skills permanently (e.g., Elite M., Wrath M.). 