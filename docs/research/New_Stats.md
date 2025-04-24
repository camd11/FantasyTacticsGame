# Thracia 776: Character Stats and Class Modifiers

This document contains data about character stats, class modifiers, and dismounting effects based on our research and implementation of Fire Emblem: Thracia 776 mechanics.

## 1. Dismounting Effects

When mounted units dismount, they experience several key changes:

1. **Visual appearance changes** to an infantry version of their class
2. **Movement type changes** from their mounted type (CAVALRY or FLYING) to INFANTRY
3. **Stat penalties** are applied, particularly affecting combat stats and movement
4. **Weapon restrictions** are applied (most mounted units can only use swords when dismounted)
5. **Susceptibility to effective weapons changes** (no longer weak to anti-cavalry/flier weapons)
6. **Terrain interaction changes** (can now benefit from terrain bonuses that mounted units don't get)

### 1.1 Stat Changes When Dismounting

The following table shows the typical stat penalties applied when a unit dismounts:

| Class Type       | STR  | MAG  | SKL  | SPD  | DEF  | MOV  | Notes                                  |
|------------------|------|------|------|------|------|------|----------------------------------------|
| Cavalier → Infantry | -2   | -2   | -2   | -2   | -2   | -2   | Typically MOV drops from 7 to 5        |
| Paladin → Infantry  | -2   | -2   | -2   | -2   | -2   | -3   | Typically MOV drops from 8 to 5        |
| Pegasus Knight → Infantry | -2   | -2   | -2   | -2   | -2   | -2   | Typically MOV drops from 7 to 5    |
| Wyvern Rider → Infantry  | -2   | -2   | -2   | -2   | -3   | -3   | Typically MOV drops from 8 to 5    |
| Bow Knight → Infantry    | -2   | -2   | -2   | -2   | -2   | -2   | Typically MOV drops from 7 to 5    |
| Lance Knight → Infantry  | -2   | -2   | -2   | -2   | -2   | -2   | Typically MOV drops from 7 to 5    |
| Great Knight → Infantry  | -2   | -2   | -2   | -2   | -3   | -3   | Typically MOV drops from 8 to 5    |
| Lord (Leif) → Infantry   | -1   | -1   | -1   | -1   | -1   | -1   | Special case with smaller penalties |

Note: HP, LCK, and CON are not affected by dismounting. The stats return to normal when remounting.

### 1.2 Weapon Restrictions When Dismounting

| Class Type       | Mounted Weapons               | Dismounted Weapons            | Notes                                  |
|------------------|-----------------------------|---------------------------|-----------------------------------------|
| Cavalier         | Swords, Lances              | Swords only               |                                         |
| Paladin          | Swords, Lances              | Swords only               |                                         |
| Pegasus Knight   | Lances                      | Swords, Lances            | One of few that retains Lance access    |
| Wyvern Rider     | Lances, Axes                | Swords only               |                                         |
| Bow Knight       | Bows                        | Bows only                 | Retains same weapon type when dismounted|
| Lance Knight     | Lances                      | Swords only               |                                         |
| Great Knight     | Swords, Lances, Axes        | Swords only               |                                         |
| Lord (Leif)      | Swords                      | Swords                    | No weapon restriction change            |

## 2. Class Base Stats

(This section would normally contain the base stats for each class, but those values are not available in the current documentation)

## 3. Character-Specific Stats

(This section would normally contain character-specific information like PCC, Movement Stars, Leadership Stars, and personal growth rates, but those values are not available in the current documentation)

## 4. Implementation Notes

In our implementation:

1. When a unit dismounts, the system references the `dismount_stat_modifiers` property of their class to apply stat changes, or directly sets certain stats like MOV based on the dismounted class value.

2. The dismounting and mounting actions are reversible - all stat changes applied during dismounting are reversed when mounting.

3. Automatic dismounting occurs when:
   - Units enter indoor maps
   - Units try to enter indoor tiles from outdoor tiles (they must dismount first)

4. Automatic mounting occurs when:
   - Units are on the preparation screen for an outdoor map after having been in an indoor map

5. When dismounting, the system automatically handles weapon restrictions by:
   - Checking if the currently equipped weapon is still usable
   - Unequipping invalid weapons
   - Attempting to equip a valid weapon from the unit's inventory 