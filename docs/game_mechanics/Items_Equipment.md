# Thracia 776: Items & Equipment Specification

This document covers inventory management, item types, and specific item effects in Fire Emblem: Thracia 776.

## 1. Inventory Management

-   **Unit Inventory:** Each unit can hold a maximum of **7** items/weapons.
-   **Trading:** Allows transferring items between adjacent allied units.
    -   Consumes the initiator's action for the turn.
    -   Can trade multiple items in one sequence.
    -   Can swap the equipped weapon of the target unit, even if the target has already acted.
-   **Convoy:** Central storage accessible during chapter preparations and via rare "Supply" tiles on the map.
    -   Capacity: 128 items.
-   **Item Durability:** Weapons and staves have limited uses. They break and become unusable at 0 uses. Broken items remain as placeholders until repaired or discarded.
-   **Repair:** Extremely limited. The primary method is the personal Repair staff (5 uses total). Broken weapons cannot be used in combat.

## 2. Item Categories & Effects

### 2.1. Consumables & Utility

| Item Name    | Uses | Effect                                                  |
| :----------- | :--- | :------------------------------------------------------ |
| Vulnerary    | 3    | Restores **all HP** to the user.                        |
| Holy Water   | 1    | Grants **+7 Magic**. Effect decays by 1 per turn.       |
| Torch (Item) | 1    | Increases Fog of War sight radius for a limited time. Initial radius is large (e.g., 10), decays each turn. |
| Antidote     | 3    | Cures **Poison** status.                                |
| Door Key     | 1    | Opens one locked door.                                  |
| Bridge Key   | 1    | Lowers one drawbridge.                                  |
| Chest Key    | 20   | Opens chests.                                           |
| Lockpick     | 30   | Opens doors/chests. **Usable only by Thief, Thief Fighter, Lara.** |
| S Drink      | 1    | Removes **Fatigue** status. Usable only during chapter preparations. |
| Knight Proof | 1    | Promotes most Lv 10+ base class units.                  |
| Member Card  | --   | Held item. Allows access to **Secret Shops**.           |

### 2.2. Stat Booster Items (Rings)

-   Consumed upon use for a permanent stat increase.

| Item Name   | Stat Increase |
| :---------- | :------------ |
| Life Ring   | +7 Max HP     |
| Power Ring  | +3 Strength   |
| Magic Ring  | +2 Magic      |
| Skill Ring  | +3 Skill      |
| Speed Ring  | +3 Speed      |
| Luck Ring   | +3 Luck       |
| Shield Ring | +2 Defense    |
| Body Ring   | +3 Build      |
| Leg Ring    | +2 Movement   |

### 2.3. Skill Manual Items

-   Consumed upon use to permanently teach the holder the specified skill.

| Item Name           | Skill Taught   |
| :------------------ | :------------- |
| Elite M.            | Elite (Paragon)|
| Charge M.           | Charge         |
| Ambush M. / Vantage M.| Ambush (Vantage)|
| Wrath M.            | Wrath          |
| Continue M. / Adept M.| Continue (Adept)|
| Awareness M. / Nihil M.| Awareness (Nihil)|
| Sun Sword M. / Sol M. | Sol (Sun Sword)|
| Moonlight Sw M. / Luna M.| Luna (Moonlight Sword)|
| *Bargain M.*        | *Bargain*      | *(Unused)*     |
| *Prayer M.*         | *Prayer*       | *(Unused)*     |

### 2.4. Crusader Scrolls

-   **Held items** (occupy an inventory slot).
-   **Effect 1: Growth Modification:** Modify the holder's growth rates when they level up. Each scroll has specific +/- bonuses to growth percentages (Refer to `docs/research/New_Stats.md` for the table).
-   **Effect 2: Critical Negation:** Negates all enemy critical hits against the holder, **except** those resulting from the enemy's Wrath skill.
-   Growth effects from multiple held scrolls stack.
-   There are 12 unique scrolls.

## 3. Weapon & Staff Effects Summary

*(Detailed stats like Mt, Hit, Wt, Crit, Rng, Uses, Rank should be sourced from database tables, e.g., in `docs/research/New_Stats.md` or external FE wikis)*

-   **Effectiveness:** Triples weapon Might (x3) against specific unit types (e.g., Armorslayer vs Armor, Hammer vs Armor, Bows vs Fliers, Rapier vs Armor/Cavalry).
-   **Brave Effect:** Allows 2 consecutive hits per attack initiation (before counter/follow-up). Found on Brave Sword, Hero Axe, Master Lance, Dime Thunder tome, etc.
-   **Magic Swords:** Deal magic damage (using Mag stat) when attacking at Range 2. Deal physical damage (Str) at Range 1. Examples: Light Brand, Flame Sword, Wind Sword.
-   **Status Weapons:** Inflict status effects (Poison, Sleep, Berserk) on hit.
-   **Personal Weapons ('*' Rank):** Usable only by specific characters. Often have unique effects or high stats. Examples: Pugi (Crit+, Wrath), Grafcalibur (High Mt/Crit), Light Brand (Magic, Eff vs Dark), Mareeta's Sword (Astra).
-   **Stat Bonuses:** Some weapons grant passive stat boosts while equipped (e.g., King Sword +10 Lck, Defender Sword +5 Def).
-   **Skill Bestowal:** Some weapons grant skills while equipped (e.g., King Sword grants Charisma).
-   **Staff Effects:** Wide range including healing (single, AoE, ranged), status inflict (Sleep, Silence, Berserk - requires Mag check), status cure (Restore, Kia), teleportation (Warp, Rescue staff, Rewarp), utility (Repair, Thief staff, Unlock, Torch staff). 