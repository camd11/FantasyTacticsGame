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

```pseudocode
// Represents any item in the game
CLASS Item
    // PROPERTIES
    ItemID ID // Unique identifier (e.g., "IronSword", "Vulnerary", "OdosScroll")
    STRING Name // Display name
    ItemType Type // (e.g., Sword, Lance, Axe, Bow, FireTome, Staff, Usable, Scroll, Key, Valuables)
    INTEGER Uses // Durability; 0 or -1 for infinite, or max uses
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
    WeaponTypeID WeaponType // (e.g., Sword, Lance, Axe, Bow, Fire, Thunder, Wind, Light, Dark)
    INTEGER Might
    INTEGER HitRate
    INTEGER CriticalRate // Base critical chance of the weapon
    INTEGER Weight
    RangeData Range // Min and Max range (e.g., 1-1, 1-2, 2-2)
    WeaponRankID RequiredRank // Minimum weapon rank to use (e.g., E, D, C, B, A)
    EffectivenessFlags Effectiveness // Against whom this weapon is effective (e.g., Armored, Flying, Mounted)
    ARRAY<SkillID> GrantedSkills // Skills granted when this weapon is equipped (e.g., Vantage on Killer Axe)
    ItemStatBonuses StatBonuses // Direct stat boosts when equipped (from [`FireEmblem5/SRC/ItemData.asm:31-57`](FireEmblem5/SRC/ItemData.asm:31))
    BOOLEAN IsMagicDamage // True if it targets RES, false for DEF
    BOOLEAN IsBrave // Attacks twice if AS allows
    BOOLEAN IsPoison // Applies poison status
    ItemID TransformsToID // If it's a transforming item (e.g., PoisonSword -> IronSword, from [`FireEmblem5/SRC/ItemData.asm:15-22`](FireEmblem5/SRC/ItemData.asm:15))
    // Other special properties (e.g., Devil effect, unbreakable, negates criticals)
    // TEST: Weapon properties (Mt, Hit, Wt, Range) must be within reasonable game balance.
    // TEST: RequiredRank must be a valid WeaponRankID.

    // METHODS
    CONSTRUCTOR(ID, Name, Uses, Cost, Icon, Description, WeaponType, Might, Hit, Crit, Weight, Range, ReqRank, Effectiveness, GrantedSkills, StatBonuses, SpecialProperties)
END CLASS

CLASS RangeData
    INTEGER MinRange
    INTEGER MaxRange
    // TEST: MinRange must be > 0.
    // TEST: MaxRange must be >= MinRange.
END CLASS

ENUM WeaponTypeID
    Sword
    Lance
    Axe
    Bow
    Dagger // For Thieves if distinct from swords
    Fire
    Thunder
    Wind
    Light
    Dark
    Ballista // Siege weapon type
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
    HealSingleTarget
    HealAreaOfEffect
    CureStatusSingleTarget
    CureStatusAreaOfEffect
    ApplyDebuffSingleTarget // Silence, Sleep, Berserk
    ApplyDebuffAreaOfEffect
    WarpAlly
    RescueAlly
    UnlockDoorChest
    RepairItem
    Fortify // Heal all allies in range
    Restore // Heal and cure status for all allies in range
    Torch // Increase vision range
    Rewarp // Warp self
    // etc.
END ENUM
```

### 2.4. Usable Item Data (Extends Item)

```pseudocode
// Represents a consumable item
CLASS UsableItem EXTENDS Item
    // PROPERTIES
    UsableEffectType Effect // (e.g., HealHP, CurePoison, StatBoostPermanent, KeyOpen)
    INTEGER EffectPotency // (e.g., amount healed, which stat boosted, key type)
    // TEST: Effect must be a valid UsableEffectType.

    // METHODS
    CONSTRUCTOR(ID, Name, Uses, Cost, Icon, Description, Effect, Potency)
    FUNCTION ApplyEffect(TargetUnit) // Consumes the item and applies its effect
                                   // TEST: Effect applies correctly and item is consumed.
END CLASS

ENUM UsableEffectType
    HealFixedHP // Vulnerary
    HealMaxHP // Elixir
    CurePoison
    CureAllStatus
    PermanentStatBoostHP
    PermanentStatBoostStr
    PermanentStatBoostMag
    // ... other stat boosts (Skill, Speed, Luck, Def, Con, Mov)
    PromotionItem // For specific class promotions
    Key // Opens doors/chests
    ChestKey
    DoorKey
    BridgeKey
    Antitoxin
    PureWater // Temp Mag Res boost
    TorchItem // Lights up FoW
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
    // TEST: All growth modifiers must be integers.

    // METHODS
    CONSTRUCTOR(ID, Name, Cost, Icon, Description, GrowthModifiersArray)
    // Scrolls are typically always "equipped" if in inventory, or need a specific "Hold" mechanic.
    // Their effect is passive on the character's growth calculations.
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