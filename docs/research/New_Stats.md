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

### 1.1. Mounting Gains / Dismount Penalties

When a mounted unit mounts, they gain stats. When they dismount, they lose these stats. The following table shows the accurate stat changes for mounting (conversely, these are the penalties when dismounting):

| Base Class        | Mounted Class     | Str | Skl | Spd | Def | Con | Mov | Weapon Change (Dismount) |
| :---------------- | :---------------- | :-: | :-: | :-: | :-: | :-: | :-: | :----------------------- |
| Social Knight     | Paladin           | +1  | +1  | +1  | +2  | +0  | +3  | Lance -> Sword           |
| Lance Knight      | Duke Knight       | +1  | +1  | +1  | +2  | +0  | +3  | Lance -> Sword           |
| Axe Knight        | Great Knight      | +1  | +1  | +1  | +2  | +0  | +3  | Axe -> Sword             |
| Arch Knight       | Bow Knight        | +1  | +1  | +1  | +2  | +0  | +3  | Bow -> Sword             |
| Free Knight       | Forrest Knight    | +1  | +1  | +1  | +2  | +0  | +3  | Sword only               |
| Troubadour        | Paladin (F)       | +1  | +0  | +1  | +1  | +0  | +3  | Staff -> Sword/Staff     |
| Mage (Dismounted) | Mage Knight       | +0  | +1  | +1  | +1  | +0  | +3  | Tomes only               |
| Pegasus Rider     | Pegasus Knight    | +1  | +1  | +1  | +1  | +0  | +3  | Lance -> Sword           |
| Dragon Rider      | Dragon/Wyvern Knight | +3  | +2  | +2  | +5  | +0  | +3  | Lance -> Sword        |

*Note: These are the bonuses gained upon mounting. Dismounting removes these bonuses. The 'Weapon Change' column indicates the weapon type typically restricted to when dismounted.*

### 1.2. Weapon Restrictions When Dismounting

| Class Type            | Mounted Weapons               | Dismounted Weapons          | Notes                                  |
| :-------------------- | :---------------------------- | :--------------------------- | :------------------------------------- |
| Social Knight/Paladin | Swords, Lances               | Swords only                  |                                        |
| Lance Knight/Duke Knight | Lances                     | Swords only                  |                                        |
| Axe Knight/Great Knight | Axes                        | Swords only                  |                                        |
| Arch Knight/Bow Knight | Bows                         | Bows only                    | Retains same weapon type when dismounted|
| Free Knight/Forrest Knight | Swords                   | Swords only                  | No weapon restriction change           |
| Troubadour/Paladin (F) | Swords, Staves              | Swords, Staves               | Retains staff access                   |
| Mage Knight           | Tomes                         | Tomes only                   | No weapon restriction change           |
| Pegasus Rider/Knight  | Lances                       | Swords, Lances               | One of few that retains Lance access   |
| Dragon/Wyvern Rider/Knight | Lances                  | Swords only                  |                                        |
| Lord (Leif)           | Swords                       | Swords                       | No weapon restriction change           |

## 2. Class Base Stats

(This section would normally contain the base stats for each class, but those values are available in the supplementary_data.md file under section 2.1)

## 3. Character-Specific Stats

(This section would normally contain character-specific information like PCC, Movement Stars, Leadership Stars, and personal growth rates, which are available in the supplementary_data.md file under section 1.1)

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

6. Special terrain interactions:
   - Mounted units generally can't navigate certain terrain types like Mountains or Thickets
   - Mounted units don't receive terrain bonuses that infantry do
   - Flying units ignore terrain movement costs but don't receive terrain Avoid/Defense bonuses
   - When dismounted, units can utilize terrain bonuses that their mounted forms cannot 