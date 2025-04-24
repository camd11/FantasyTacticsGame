# Thracia 776: Map Environment Specification

This document details map terrain, Fog of War, and objective types in Fire Emblem: Thracia 776.

## 1. Terrain

### 1.1. Terrain Effects
-   **Movement Costs:** Different terrain types impose varying movement costs depending on the unit's movement type (Infantry, Armor, Cavalry, Flier, Bandit, Pirate). See table below.
-   **Combat Bonuses:** Some terrain provides bonuses to Avoid (Avo) and Defense (Def) to units standing on them.
-   **HP Recovery:** Specific terrain types restore a percentage of Max HP at the start of the Player Phase (typically Forts, Gates, Thrones, Churches).
-   **Special Effects:** Some terrain might have unique effects (e.g., Magic Circles boosting Mag).

### 1.2. Terrain Types & Costs (Examples)

| Terrain     | Def Bonus | Avo Bonus | Heal % | Infantry Cost | Armor Cost | Cavalry Cost | Flier Cost | Notes                 |
| :---------- | :-------- | :-------- | :----- | :------------ | :--------- | :----------- | :--------- | :-------------------- |
| Plain       | 0         | 0         | 0      | 1             | 1          | 1            | 1          | Standard ground       |
| Forest      | 1         | 20        | 0      | 2             | 2          | 3            | 1          | Slows ground units    |
| Mountain    | 2         | 30        | 0      | 3             | 3          | 4            | 1          | Very slow, high bonus |
| Peak        | 3         | 40        | 0      | 4*            | 4*         | --           | 1          | *Brigand/Mtn Thief only |
| Sand        | 0         | 5         | 0      | 2             | 2          | 3            | 1          | Slows ground units    |
| River/Sea   | 0         | 10        | 0      | --            | --         | --           | 1          | Flier/Pirate only     |
| Fort        | 2         | 20        | 20%    | 1             | 1          | 1            | 1          | Defensive, Heals      |
| Gate/Throne | 3         | 30        | 20%    | 1             | 1          | 1            | 1          | Strong Defense, Heals |
| Pillar      | 1         | 20        | 0      | 1             | 1          | 1            | 1          | Indoor Forest         |
| Chest       | 0         | 0         | 0      | 1             | 1          | 1            | 1          | Can be opened         |
| Village     | 0         | 10        | 0      | 1             | 1          | 1            | 1          | Can be visited        |
| Wall        | --        | --        | --     | Impassable    | Impassable | Impassable   | 1          | Flier Only            |

*(This is a sample. Full terrain costs and effects should be verified from game data.)*

### 1.3. Flier Interaction
-   Flying units (Pegasus, Wyvern) **ignore all terrain movement costs**.
-   Fliers do **not** receive defensive bonuses (Avo/Def) from terrain, except for HP recovery on healing tiles (Forts, etc.).

## 2. Fog of War (FoW)

-   **Effect:** Obscures the map (terrain and units) beyond a unit's vision range on specific maps.
-   **Player Vision:**
    -   Standard vision range is typically **3 tiles**.
    -   Thief class units have an inherently larger vision radius (e.g., +2, total 5).
    -   **Torch Item/Staff:** Using a Torch temporarily increases vision significantly (e.g., 10 tile radius). This effect decays by 1 tile per turn until it expires.
-   **Enemy AI:** Critically, enemy AI in Thracia 776 largely **ignores** player FoW limitations for movement and targeting. They act as if they have full map visibility.
-   **Revealing Tiles:** Tiles within the vision range of any player unit (or active Torch effect) become visible.
-   **Memory:** Tiles that were previously visible but are no longer in vision range enter a "Fog" state (dimmed, terrain remembered, units hidden). Tiles never seen are "Unknown" (black).
-   **Bumping:** If a player unit attempts to move onto a tile occupied by an unseen enemy unit, their movement stops on the adjacent tile just before the enemy.

## 3. Map Objectives & Design Elements

-   **Common Objectives:**
    -   **Seize:** Main Lord (Leif) must move onto a specific tile (Throne, Gate) and use the Seize command.
    -   **Escape:** All player units must move onto designated Escape tiles. Leif *must* escape last; if he leaves first, any remaining player units are considered lost/captured.
    -   **Defend:** Survive for a set number of turns, or protect a specific tile/NPC unit for a duration.
-   **Gaiden Chapters (Side Chapters):** Optional chapters unlocked by meeting specific conditions (e.g., finishing quickly, saving NPCs, visiting locations).
-   **Reinforcements:** Enemy units appearing mid-chapter.
    -   **Triggers:** Can be based on turn number, player reaching a certain map area, or specific events.
    -   **Ambush Spawns:** Reinforcements that can move and act on the same turn they appear.
-   **Map Features:** Doors (opened by keys/lockpicks), Chests (opened by keys/lockpicks), Bridges (lowered by keys), Villages (visited for items/recruits), Secret Shops (accessed with Member Card). 