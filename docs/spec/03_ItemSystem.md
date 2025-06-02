# Specification: Item System

This document outlines the data structures and functionalities for items, including weapons, staves, consumables, and special items like scrolls, in the Fire Emblem Thracia 776 recreation.

## 1. Core Concepts

*   **Item**: Any object a unit can hold in their inventory.
*   **Weapon**: An item used for attacking in combat (Swords, Lances, Axes, Bows, Tomes).
*   **Staff**: An item used by magic-users to perform support actions (healing, status effects, warping).
*   **Consumable**: An item that is used up to provide an effect (e.g., Vulnerary for healing, Keys for opening doors/chests).
*   **Scroll**: A special item that modifies a character's growth rates when held.
*   **Item Properties**: Attributes like Might (Mt), Hit Rate (Hit), Critical Rate (Crit), Weight (Wt), Range, Durability (Uses).
*   **Weapon Triangle**: A system where certain weapon types have an advantage or disadvantage against others (e.g., Swords > Axes > Lances > Swords). Thracia 776 has a more nuanced system, often tied to skills or specific weapon properties rather than a strict triangle.
*   **Magic System**: Different types of magic (Fire, Thunder, Wind, Light, Dark) with varying effects and potentially effectiveness against certain unit types.

## 2. Data Structures

### 2.1. Base Item Data

The exact source for comprehensive item data (Name, Type, Mt, Hit, Crit, Wt, Range, Uses, Cost, Weapon Rank, etc.) is still TBD. The following structure is a general representation.

ENUM ItemType
    Sword
    Lance
    Axe
    Bow
    Dagger // For Thieves/specific characters, if distinct from Swords
    FireTome
    ThunderTome
    WindTome
    LightTome
    DarkTome
    Staff
    Consumable // General category for items like Vulneraries, Elixirs, Stat Boosters
    Scroll // For growth rate modification
    Key // For doors, chests, bridges
    Valuable // Items primarily for selling (e.g., gems)
    // Ring // If rings with passive effects exist as a distinct category
    // Shield // If shields with defensive properties exist as a distinct category
END ENUM

```pseudocode
// Represents any item in the game
CLASS Item
    // PROPERTIES
    ItemID ID // Unique identifier (e.g., "IronSword", "Vulnerary", "OdosScroll")
    STRING Name // Display name
    ItemType Type // Enum defining the general category of the item
    INTEGER Uses // Durability; -1 for infinite, or max uses (Standardize to -1 for infinite)
    INTEGER MaxUses // Original number of uses for repair purposes
    INTEGER Cost // Purchase price
    IconID Icon // Identifier for its menu icon
    STRING Description // In-game description
    // TEST: ItemID must be unique.
    // TEST: Name must not be empty.
    // TEST: Uses must be non-negative (or special value for infinite).

    // METHODS
    CONSTRUCTOR(ID, Name, Type, Uses, Cost, Icon, Description)
    FUNCTION CanBeUsedBy(UnitInstance) RETURNS BOOLEAN // Checks if the unit can use/equip this item
                                                    // (e.g., weapon rank, class restrictions)
                                                    // TEST: Correctly determines usability based on unit.
END CLASS
```

### 2.2. Weapon Data (Extends Item)

```pseudocode
// Represents a weapon
CLASS Weapon EXTENDS Item
    // PROPERTIES
    WeaponTypeID WeaponType // Specific type of weapon, aligning with ItemType where applicable
    INTEGER Might
    INTEGER HitRate
    INTEGER CriticalRate // Base critical chance of the weapon
    INTEGER Weight
    RangeData Range // Min and Max range (e.g., 1-1, 1-2, 2-2)
    WeaponRankID RequiredRank // Minimum weapon rank to use (e.g., E, D, C, B, A)
    ARRAY<TargetAttribute> Effectiveness // List of attributes this weapon is effective against
    ARRAY<SkillID> GrantedSkills // Skills granted when this weapon is equipped (e.g., Vantage on Killer Axe)
    ItemStatBonuses StatBonuses // Direct stat boosts when equipped (from [`FireEmblem5/SRC/ItemData.asm:31-57`](FireEmblem5/SRC/ItemData.asm:31))
    BOOLEAN IsMagicDamage // True if it targets RES, false for DEF
    // Note: IsBrave, IsPoison are now covered by WeaponSpecialProperties
    ItemID TransformsToID // If it's a transforming item (e.g., PoisonSword -> IronSword after uses deplete or repair attempt, from [`FireEmblem5/SRC/ItemData.asm:15-22`](FireEmblem5/SRC/ItemData.asm:15))
    ARRAY<WeaponSpecialProperty> SpecialProperties // List of special attributes for the weapon
    // TEST: Weapon properties (Mt, Hit, Wt, Range) must be within reasonable game balance.
    // TEST: RequiredRank must be a valid WeaponRankID.
    // TEST: Uses should be -1 for unbreakable weapons, or a positive integer.

    // METHODS
    CONSTRUCTOR(ID, Name, Uses, Cost, Icon, Description, WeaponType, Might, Hit, Crit, Weight, Range, ReqRank, Effectiveness, GrantedSkills, StatBonuses, SpecialPropertiesArray)
END CLASS

CLASS RangeData
    INTEGER MinRange
    INTEGER MaxRange
    // TEST: MinRange must be > 0.
    // TEST: MaxRange must be >= MinRange.
END CLASS

ENUM WeaponTypeID // Corresponds to specific weapon categories, used for combat calculations and weapon rank checks.
    Sword
    Lance
    Axe
    Bow
    Dagger // Typically used by Thieves, may have unique properties.
    FireTome
    ThunderTome
    WindTome
    LightTome
    DarkTome
    Ballista // Siege weapon type, distinct from Bows for rank/usage purposes.
END ENUM

ENUM TargetAttribute // Attributes a unit or class can have, used for effectiveness checks.
    Armored
    Flying
    Mounted
    Dragon
    MagicalBeast // e.g., Manaketes, Laguz if applicable to this FE version
    Infantry // If specific weapons are effective against unmounted, non-armored units
    // Add other specific Thracia 776 effectiveness categories as identified
END ENUM

ENUM WeaponRankID // Numerical or E-S
    E_Rank
    D_Rank
    C_Rank
    B_Rank
    A_Rank
    S_Rank // Or PRF rank
END ENUM

CLASS ItemStatBonuses // From [`FireEmblem5/SRC/ItemData.asm:33-35`](FireEmblem5/SRC/ItemData.asm:33)
    // PROPERTIES
    INTEGER HP_Bonus
    INTEGER STR_Bonus
    INTEGER MAG_Bonus
    INTEGER SKL_Bonus
    INTEGER SPD_Bonus
    INTEGER DEF_Bonus
    INTEGER CON_Bonus
    INTEGER LUK_Bonus
    INTEGER MOV_Bonus
    // TEST: All bonus values must be integers.
END CLASS

ENUM WeaponSpecialProperty
    BraveEffect // Attacks twice if Attack Speed allows
    PoisonStrike // Applies poison status on hit
    DevilEffect // Chance to damage self instead of enemy
    Unbreakable // Item does not consume uses (Uses should be -1)
    NegatesCriticals // Prevents enemy critical hits when this weapon is used/equipped
    Eclipse // Reduces enemy HP to 1 (specific to certain tomes/staves if weaponized)
    StealsHP // Heals user for a portion of damage dealt
    CannotBeCountered // Weapon attacks without risk of counter-attack (e.g., some siege tomes)
    ReaverEffect // Reverses weapon triangle advantage (e.g. LanceReaver Sword)
    CriticalBoost // Higher base critical rate than normal for its type (often implicit in Crit stat, but can be explicit flag)
    MovementCostModifier // Affects unit movement when equipped (e.g. Knight Killer)
    EffectiveDamageOnly // Deals damage only if effectiveness applies (e.g. some anti-cavalry weapons in other FEs)
    // Add other specific Thracia 776 weapon properties as identified
END ENUM
```

### 2.3. Staff Data (Extends Item)

```pseudocode
// Represents a staff
CLASS Staff EXTENDS Item
    // PROPERTIES
    StaffEffectType Effect // (e.g., Heal, Recover, Warp, Silence, Sleep, Berserk, Unlock)
    INTEGER EffectPotency // (e.g., amount healed, duration of status)
    RangeData Range // Typically based on user's MAG stat or fixed
    WeaponRankID RequiredRank // Staff rank needed
    INTEGER ExperienceGain // EXP gained on successful use
    // TEST: Effect must be a valid StaffEffectType.
    // TEST: RequiredRank must be a valid WeaponRankID.

    // METHODS
    CONSTRUCTOR(ID, Name, Uses, Cost, Icon, Description, Effect, Potency, Range, ReqRank, ExpGain)
    FUNCTION CalculateRange(UserStats) RETURNS RangeData // Some staves have range based on Mag/2 etc.
                                                       // TEST: Range calculation must be correct.
END CLASS

ENUM StaffEffectType
    HealSingleFixed // e.g., Heal staff (Potency = fixed HP)
    HealSingleUserMag // e.g., Mend staff (Potency = User MAG + fixed amount)
    HealAreaFixed // e.g., Physic (fixed range, fixed heal amount)
    // HealAreaUserMag is less common for AoE, usually fixed. Replaced by Fortify.
    Fortify // Heal all allies in defined range (Potency = User MAG + fixed, or just fixed)
    RestoreSingle // Cures status ailments for a single target
    RestoreAllInRange // Heal and cure status for all allies in range (like original Restore)
    SilenceTarget // Prevents target from using magic for a duration
    SleepTarget // Puts target to sleep for a duration
    BerserkTarget // Makes target attack nearest unit (friend or foe) for a duration
    WarpAlly // Teleports an ally to a chosen tile within staff's range
    RescueAlly // Teleports an ally from staff's range to an adjacent tile to user
    RewarpSelf // Teleports user to a chosen tile within staff's range
    Unlock // Opens doors or chests (Potency might indicate lock level if applicable)
    RepairItem // Repairs a chosen item for the target (Potency = uses restored, or full repair)
    TorchStaff // Increases vision range in Fog of War for a number of turns (Potency = radius, Duration = turns)
    Barrier // Boosts target's Resistance temporarily (Potency = RES boost, Duration = turns)
    Hammerne // Fully repairs one item for an ally (Potency = N/A, always full)
    ThiefStaff // Allows user to steal a non-equipped item from an enemy within range (e.g., Thief, Steal staves)
    // TODO: Add any other specific Thracia 776 staff effects (e.g., status staves like Petrify, Enfeeble, specific PRF staff effects)
END ENUM
```

### 2.4. Usable Item Data (Extends Item)

```pseudocode
// Represents a consumable item
CLASS UsableItem EXTENDS Item
    // PROPERTIES
    UsableEffectType Effect // Defines the primary effect of the item
    INTEGER EffectPotency // Magnitude of the effect (e.g., HP healed, stat points gained)
    ARRAY<ClassID> PromotionTargetClasses // For PromotionItem: specifies the class(es) it can promote to. Empty if not a promotion item.
    INTEGER DurationTurns // For temporary effects (e.g., PureWater, TorchItem). 0 or -1 if permanent or instant.
    // TEST: Effect must be a valid UsableEffectType.
    // TEST: If Effect is PromotionItem, PromotionTargetClasses must not be empty and contain valid ClassIDs.
    // TEST: If DurationTurns > 0, effect should be temporary.

    // METHODS
    CONSTRUCTOR(ID, Name, Uses, Cost, Icon, Description, Effect, Potency, PromotionTargetClassesArray, DurationTurns)
    FUNCTION ApplyEffect(TargetUnit) // Consumes the item and applies its effect
                                   // TEST: Effect applies correctly and item is consumed.
                                   // TEST: Temporary effects apply for correct duration.
                                   // TEST: Promotion items correctly check class eligibility.
END CLASS

ENUM UsableEffectType
    HealFixedHP // e.g., Vulnerary (Potency = HP healed)
    HealMaxHP // e.g., Elixir (Potency is ignored, heals to full)
    Antitoxin // Cures poison (Potency might be ignored)
    PureWater // Temporary MAG boost (Potency = MAG increase, DurationTurns > 0)
    TorchItem // Increases vision in Fog of War around user (Potency = vision radius increase, DurationTurns > 0)
    Lockpick // Opens doors/chests, typically for Thieves (Potency might be number of uses if different from item uses, or quality of lock it can open)
    ChestKey // Opens chests
    DoorKey // Opens doors
    BridgeKey // Specific key for map interactions (e.g., repairing a bridge)
    StaminaDrink // Restores unit's stamina/fatigue if that mechanic is implemented (Potency = stamina restored)
    EnergyRing // Permanent STR boost (Potency = STR increase)
    SecretBook // Permanent SKL boost (Potency = SKL increase)
    SpeedRing // Permanent SPD boost (Potency = SPD increase)
    GoddessIcon // Permanent LCK boost (Potency = LCK increase)
    Dracoshield // Permanent DEF boost (Potency = DEF increase)
    BodyRing // Permanent CON/Build boost (Potency = CON increase)
    MagicRing // Permanent MAG boost (Potency = MAG increase)
    LifeRing // Permanent Max HP boost (Potency = Max HP increase)
    SkillBook // Permanent Weapon Rank EXP boost (Potency = EXP amount, may need a target WeaponTypeID property on UsableItem)
    PromotionItem // Promotes to one of the PromotionTargetClasses (Potency might be unused or indicate specific conditions)
    StatDropItem // Reduces an enemy stat (if usable by player, e.g. via a skill that creates a temporary item. Potency = stat decrease, DurationTurns > 0)
    MemberCard // Grants access to secret shops (Passive effect, or used at shop entrance)
    LightRune // Creates a temporary barrier that damages enemies passing through (Potency = damage, DurationTurns > 0)
    Mine // Placeable trap (Potency = damage)
    // TODO: Add other specific Thracia 776 consumables (e.g., specific quest items if they have direct "usable" effects, other stat boosters like Luck Ring, Move Ring if they exist)
END ENUM
```

### 2.5. Scroll Data (Extends Item)

Based on [`FireEmblem5/TABLES/ScrollTable.csv`](FireEmblem5/TABLES/ScrollTable.csv:0).

```pseudocode
// Represents a scroll that modifies growth rates
CLASS Scroll EXTENDS Item
    // PROPERTIES
    INTEGER GrowthHP_Modifier
    INTEGER GrowthStrength_Modifier
    INTEGER GrowthMagic_Modifier
    INTEGER GrowthSkill_Modifier
    INTEGER GrowthSpeed_Modifier
    INTEGER GrowthDefense_Modifier
    INTEGER GrowthConstitution_Modifier
    INTEGER GrowthLuck_Modifier
    INTEGER GrowthMovement_Modifier
    // TEST: All growth modifiers must be integers (can be 0, positive, or negative).

    // METHODS
    CONSTRUCTOR(ID, Name, Cost, Icon, Description, HP_Mod, Str_Mod, Mag_Mod, Skl_Mod, Spd_Mod, Def_Mod, Con_Mod, Luk_Mod, Mov_Mod)
    // Scrolls are typically always "equipped" if in inventory (their effect is passive).
    // The "Hold" mechanic in Thracia 776 means they simply need to be in the unit's personal inventory.
    // Their effect is applied during level-up calculations.
    // TEST: Scroll in inventory correctly modifies growth rates on level up.
END CLASS
```

## 3. Item Mechanics

*   **Inventory**: Units have a limited inventory space (e.g., 5-7 items).
    *   // TEST: Unit cannot hold more items than inventory limit.
*   **Trading**: Units can trade items with adjacent allies.
    *   // TEST: Trading items between units works correctly.
*   **Convoy/Storage**: Access to a shared storage for items not carried by units.
    *   // TEST: Items can be sent to and retrieved from convoy.
*   **Repairing**: Certain weapons (especially rare/powerful ones) might be repairable.
    *   // TEST: Repairing restores item uses correctly, consumes resources if any.
*   **Item Dropping**: Enemies may drop items upon defeat.
    *   // TEST: Correct item is dropped by defeated enemy.
*   **Shops**: Armories (weapons) and Vendors (items/staves) where items can be bought and sold.
    *   // TEST: Shop inventory is correct for the chapter/location.
    *   // TEST: Buying/selling items updates unit gold and inventory.
*   **Stealing**: Thieves can steal items from enemies if their SPD is higher and the item is not equipped (or other conditions).
    *   // TEST: Stealing conditions (SPD, item type) are checked correctly.
    *   // TEST: Item is transferred upon successful steal.

## 4. TDD Anchors

*   `// TEST: Item_Create_Valid`: Successfully creates an item with valid base data.
*   `// TEST: Weapon_Equip_ValidRank`: Unit can equip a weapon if they meet the rank requirement.
*   `// TEST: Weapon_Equip_InvalidRank`: Unit cannot equip a weapon if rank is too low.
*   `// TEST: Weapon_Combat_DamageCalculation`: Damage dealt by a weapon is calculated correctly (Mt + Str/Mag - Def/Res).
*   `// TEST: Weapon_Effectiveness_AppliesBonus`: Effective weapons deal bonus damage to appropriate targets.
*   `// TEST: Weapon_BraveEffect_AttacksTwice`: Brave weapons allow two consecutive attacks if AS permits.
*   `// TEST: Weapon_StatBonus_Applied`: Stat bonuses from equipped weapons are correctly applied to unit stats.
*   `// TEST: Staff_Heal_CorrectAmount`: Healing staff restores the correct amount of HP.
*   `// TEST: Staff_Range_MagBased`: Staff range is correctly calculated based on user's Magic stat.
*   `// TEST: UsableItem_Vulnerary_HealsHP`: Vulnerary correctly heals HP and is consumed.
*   `// TEST: UsableItem_StatBooster_PermanentIncrease`: Stat booster item permanently increases the target stat.
*   `// TEST: Scroll_GrowthModifier_Applied`: Character holding a scroll has their growth rates correctly modified for level-ups.
*   `// TEST: Item_Transform_PoisonToNormal`: Poisoned weapon transforms to its normal version under correct conditions (e.g., repair, specific event).
*   `// TEST: Inventory_AddItem_Full`: Cannot add item to a full inventory.
*   `// TEST: Shop_BuyItem_CorrectGoldCost`: Buying an item deducts the correct amount of gold.
*   `// TEST: Steal_Successful_ItemTransfer`: Successfully stealing an item moves it to the thief's inventory.

This specification will be updated as the exact format and location of the core item data table are discovered. The next step is to investigate combat mechanics.