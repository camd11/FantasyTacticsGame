# Specification: Character and Class System

This document outlines the data structures and functionalities for characters, classes, and related mechanics in the Fire Emblem Thracia 776 recreation.

## 1. Core Concepts

*   **Unit**: A generic term for any character (player, enemy, NPC) on the battlefield.
*   **Character**: A specific, named individual with unique base stats, growth rates, skills, and potentially a unique class or portrait.
*   **Class (Job)**: Defines a unit's role, base stats, maximum stats, weapon proficiencies, skills, movement type, and promotion options.
*   **Stats**: Attributes that determine a unit's combat prowess and capabilities (e.g., HP, Strength, Magic, Skill, Speed, Luck, Defense, Constitution, Movement).
*   **Growth Rates**: Percentages determining the chance of a stat increasing upon level-up.
*   **Skills**: Special abilities that provide passive bonuses or active commands.
*   **Weapon Rank**: Proficiency level with different weapon types (Sword, Lance, Axe, Bow, Fire, Thunder, Wind, Light, Dark, Staff).
*   **Movement Type**: Categorizes how a unit moves on the map and interacts with terrain (e.g., Infantry, Armored, Flying, Mounted).
*   **Mounted/Dismounted**: A key mechanic where mounted units can dismount, changing their class, stats, and movement type.

## 2. Data Structures

### 2.1. Character Data

```pseudocode
// Represents a specific character in the game
CLASS Character
    // PROPERTIES
    STRING CharacterID // Unique identifier (e.g., "Leif", "EnemySwordfighter1")
    STRING Name // Display name
    PortraitID Portrait // Identifier for their portrait graphic
    ClassID InitialClassID // Starting class
    INTEGER Level
    INTEGER ExperiencePoints

    // Base Stats (overrides or adds to class bases)
    INTEGER BaseHP
    INTEGER BaseStrength
    INTEGER BaseMagic
    INTEGER BaseSkill
    INTEGER BaseSpeed
    INTEGER BaseLuck
    INTEGER BaseDefense
    INTEGER BaseConstitution // Build in Thracia 776
    INTEGER BaseMovement // Can be modified by class, skills, items

    // Growth Rates (percentages, 0-100 scale, e.g., 30 means 30%)
    INTEGER GrowthHP
    INTEGER GrowthStrength
    INTEGER GrowthMagic
    INTEGER GrowthSkill
    INTEGER GrowthSpeed
    INTEGER GrowthLuck
    INTEGER GrowthDefense
    INTEGER GrowthConstitution
    // Movement growth is typically 0, but included for completeness if needed

    ARRAY<SkillID> InnateSkills // Skills inherent to this character
    ARRAY<ItemID> InitialInventory // Starting items
    SupportData CharacterSupportData // Who they can support with and bonuses
    // Other unique flags or properties (e.g., Lord, Thief, Dancer)
    // TEST: CharacterID must be unique.
    // TEST: InitialClassID must be a valid ClassID.
    // TEST: Base stats and growths must be non-negative.

    // METHODS
    CONSTRUCTOR(CharacterID, Name, Portrait, InitialClassID, Level, BaseStats, GrowthRates, InnateSkills, InitialInventory, SupportData)
    FUNCTION GetCurrentStats() RETURNS UnitStats // Calculates current stats based on class, level, items, etc.
                                              // TEST: Stat calculation must be accurate.
    FUNCTION LevelUp() // Applies growth rates to stats
                       // TEST: Level up applies growths correctly.
                       // TEST: Stats do not exceed class maximums.
END CLASS
```

### 2.2. Class Data

Based on findings in [`FireEmblem5/SRC/ClassData.asm`](FireEmblem5/SRC/ClassData.asm:0) and general FE knowledge. The exact structure for `aClassData` is TBD.

```pseudocode
// Represents a unit class (job)
CLASS GameClass // Renamed from "Class" to avoid keyword clash
    // PROPERTIES
    ClassID ID // Unique identifier (e.g., "Lord", "Swordfighter")
    STRING Name // Display name
    ClassID PromotesToClassID // Class this class promotes to (if any)
                               // TEST: PromotesToClassID must be a valid ClassID or null.
    ItemID PromotionItem // Item required for promotion (if any)
                         // TEST: PromotionItem must be a valid ItemID or null.

    // Base Stats for the Class
    INTEGER BaseHP
    INTEGER BaseStrength
    INTEGER BaseMagic
    INTEGER BaseSkill
    INTEGER BaseSpeed
    INTEGER BaseLuck
    INTEGER BaseDefense
    INTEGER BaseConstitution
    INTEGER BaseMovement

    // Maximum Stats for the Class
    INTEGER MaxHP
    INTEGER MaxStrength
    INTEGER MaxMagic
    INTEGER MaxSkill
    INTEGER MaxSpeed
    INTEGER MaxLuck
    INTEGER MaxDefense
    INTEGER MaxConstitution
    INTEGER MaxMovement
    // TEST: Max stats must be >= base stats.

    // Class Growth Rates (bonus to character growths, or used for generic enemies)
    INTEGER GrowthHP
    INTEGER GrowthStrength
    INTEGER GrowthMagic
    INTEGER GrowthSkill
    INTEGER GrowthSpeed
    INTEGER GrowthLuck
    INTEGER GrowthDefense
    INTEGER GrowthConstitution

    ARRAY<SkillID> ClassSkills // Skills granted by this class
    MovementTypeID MovementType // Defines how the class interacts with terrain (e.g., Infantry, Flier)
                                // TEST: MovementType must be a valid MovementTypeID.
    ARRAY<WeaponRankEntry> WeaponRanks // Proficiency with weapon types
    ClassID DismountedClassID // If this is a mounted class, the class it becomes when dismounted
                              // (from [`FireEmblem5/SRC/ClassData.asm:15-43`](FireEmblem5/SRC/ClassData.asm:15))
                              // TEST: DismountedClassID must be valid if class is mounted.
    BOOLEAN IsMounted
    // Other class properties (e.g., can use magic, can steal, canto)
    // TEST: ClassID must be unique.
    // TEST: Name must not be empty.

    // METHODS
    CONSTRUCTOR(ID, Name, PromotionInfo, BaseStats, MaxStats, ClassGrowths, ClassSkills, MovementType, WeaponRanks, MountedInfo)
END CLASS

ENUM RankLevel
    None // No proficiency
    E
    D
    C
    B
    A
    S // Or equivalent highest rank for Thracia (Prf/SS)
END ENUM

CLASS WeaponRankEntry
    // PROPERTIES
    WeaponTypeID WeaponType
    RankLevel InitialRank
    RankLevel MaxRankInClass // Max rank achievable in this class for this weapon type
    // TEST: InitialRank and MaxRankInClass must be valid RankLevel values.
    // TEST: MaxRankInClass must be >= InitialRank if InitialRank is not None.
END CLASS
```

### 2.3. Unit Instance Data (On-Map Representation)

```pseudocode
// Represents a unit currently active on the game map
CLASS UnitInstance
    // PROPERTIES
    Character CharacterData // Link to the base Character object
    GameClass CurrentClass // Current class of the unit (can change due to promotion/dismounting)
    INTEGER CurrentHP
    INTEGER CurrentLevel
    INTEGER CurrentExperience
    UnitStats CurrentStats // Actual stats after all modifiers (items, status, etc.)
    Point Position // (X, Y) coordinates on the map
    UnitState State // (e.g., Active, Moved, Waiting, Rescued)
    ARRAY<ItemID> Inventory // Current items held
    ARRAY<StatusEffect> ActiveStatusEffects
    BOOLEAN IsPlayerUnit // True if player-controlled, false for enemy/NPC
    // TEST: CurrentHP must not exceed CurrentStats.MaxHP.
    // TEST: Position must be a valid map coordinate.

    // METHODS
    CONSTRUCTOR(Character, InitialPosition)
    FUNCTION TakeDamage(Amount) // TEST: HP correctly reduced, death handled.
    FUNCTION Heal(Amount) // TEST: HP correctly increased, not exceeding max.
    FUNCTION AddExperience(Amount) // TEST: XP added, level up triggered if threshold met.
    FUNCTION CanMoveTo(TargetX, TargetY) RETURNS BOOLEAN // Checks terrain and movement points
                                                       // TEST: Correctly identifies valid/invalid moves.
    FUNCTION GetAttackRange(Weapon) RETURNS ARRAY<Point> // TEST: Calculates correct attack range.
    FUNCTION GetMovementRange() RETURNS ARRAY<Point> // TEST: Calculates correct movement range.
    FUNCTION Dismount() // If mounted, changes to dismounted class and stats
                       // TEST: Correctly changes class and updates stats on dismount.
    FUNCTION Mount() // If dismounted and eligible, changes to mounted class
                    // TEST: Correctly changes class and updates stats on mount.
END CLASS

CLASS UnitStats // Helper structure for current/max stats
    INTEGER MaxHP, CurrentHP
    INTEGER Strength, Magic, Skill, Speed, Luck, Defense, Constitution, Movement
    // Derived stats
    INTEGER AttackPower
    INTEGER MagicAttackPower
    INTEGER HitRate
    INTEGER AvoidRate
    INTEGER CriticalRate
    INTEGER AttackSpeed
END CLASS

ENUM UnitState
    Idle // Has not acted this turn
    Moved // Has moved but not acted
    Acted // Has completed their action for the turn
    GreyedOut // Cannot act (e.g. status effect, already acted)
    Rescued
    Rescuing
END ENUM
```

### 2.4. Movement Types and Costs

From [`MovementType.csv`](FireEmblem5/TABLES/MovementType.csv:0) and [`docs/spec/01_MapSystem.md`](docs/spec/01_MapSystem.md:0).

```pseudocode
ENUM MovementTypeID
    Tier1Mounted
    Tier2Mounted
    Flying
    Infantry
    Armor
    // UnusedMove (handle appropriately)
    Brigand
    Berserker
    Pirate
    LightInfantry
    Mage
    Thief
    Civilian
    Ballistician
    DarkPrince
END ENUM

// Terrain movement costs are defined in TerrainType class in 01_MapSystem.md
// TerrainType.MovementCost[MovementTypeID] -> INTEGER cost
// -1 implies impassable for that MovementTypeID on that TerrainType.
// TEST: All MovementTypeIDs must have defined costs for all TerrainTypes.
```

### 2.5. Autolevel Schemes (Growth Rate Groups)

From [`AutolevelData.csv`](FireEmblem5/TABLES/AutolevelData.csv:0). Used for generic units or potentially as a base for some characters.

```pseudocode
CLASS AutolevelScheme
    // PROPERTIES
    STRING SchemeID // e.g., "AutolevelScheme1"
    INTEGER GrowthHP
    INTEGER GrowthStrength
    INTEGER GrowthMagic
    INTEGER GrowthSkill
    INTEGER GrowthSpeed
    INTEGER GrowthDefense
    INTEGER GrowthConstitution
    INTEGER GrowthLuck
    INTEGER GrowthMovement // Typically 0
    // TEST: SchemeID must be unique.
    // TEST: Growth rates must be non-negative.

    // METHODS
    CONSTRUCTOR(SchemeID, GrowthsArray)
END CLASS
```

### 2.6. Skills

```pseudocode
ENUM SkillID
    // Examples - actual list TBD from game data
    Vantage
    Wrath
    Adept
    Critical
    Nihil
    Pavise
    Luna
    Sol
    Astra
    Awareness // FE5 specific - negates enemy criticals
    Charge
    Prayer
    Steal
    Dance
    Continue // Pursuit in other FEs
    Ambush
    Miracle
    Elite // Paragon in other FEs
    Bargain
    // Weapon specific skills like WrathSword, etc.
    // Leadership Stars (multiple levels)
END ENUM

CLASS Skill
    // PROPERTIES
    SkillID ID
    STRING Name
    STRING Description
    // Effects: Defines the skill's impact (e.g., passive stat boosts, combat activation chance, special commands).
    //          Implementation may involve a strategy pattern or a registry of effect handlers.
    // ActivationCondition: Defines when/how the skill triggers (e.g., OnCombatStart, OnHit, Passive, Command).
    //                      Similar to Effects, this may require a flexible system.
    // TEST: SkillID must be unique.
    // TEST: Name and Description must not be empty.

    // METHODS
    CONSTRUCTOR(ID, Name, Description, Effects)
    FUNCTION ApplyEffect(TargetUnit, Context) // Applies the skill's effect
                                            // TEST: Skill effects apply correctly in various contexts.
END CLASS
```

## 3. Key Mechanics

*   **Leveling Up**: Units gain EXP from combat, healing, dancing, etc. Upon reaching 100 EXP, they level up. Each stat has a chance to increase based on the character's personal growth rate plus their class's growth rate.
    *   // TEST: EXP gain calculation is correct.
    *   // TEST: Level up occurs at 100 EXP, EXP resets.
    *   // TEST: Stat increases follow combined growth rates.
*   **Promotion**: Certain classes can promote to an advanced class at a certain level (e.g., Level 10 or 20), sometimes requiring a specific promotion item. Promotion grants significant stat boosts and may change weapon ranks or grant new skills.
    *   // TEST: Promotion eligibility is correctly determined.
    *   // TEST: Promotion applies correct stat bonuses and class changes.
*   **Mounting/Dismounting**: Mounted units can dismount to become an infantry version of their class, and vice-versa if outdoors. This changes their stats (often a penalty when dismounted), movement type, and sometimes weapon access.
    *   // TEST: Dismounting changes class, stats, movement type correctly.
    *   // TEST: Mounting changes class, stats, movement type correctly.
    *   // TEST: Dismounting/Mounting restrictions (indoors/outdoors) are enforced.
*   **Fatigue**: Units accumulate fatigue after actions. High fatigue can lead to stat penalties or inability to deploy. (Details TBD)
    *   // TEST: Fatigue accumulates correctly.
    *   // TEST: Fatigue penalties apply as expected.
*   **Capture/Rescue**: Units can capture weaker enemy units (taking their items) or rescue allied units. This imparts stat penalties on the rescuing/capturing unit.
    *   // TEST: Capture conditions (CON vs enemy CON) are correct.
    *   // TEST: Captured units' items are transferred.
    *   // TEST: Rescue mechanics work as expected.
    *   // TEST: Stat penalties for carrying units are applied.
*   **Supports**: Adjacent characters with support affinities can grant bonuses to each other. (Details from `SupportData.csv` TBD)
    *   // TEST: Support bonuses apply correctly when units are in range.

## 4. TDD Anchors

*   `// TEST: Character_Create_Valid`: Successfully creates a character with valid initial data.
*   `// TEST: Character_LevelUp_StatGain`: Character stats increase according to growth rates upon level up.
*   `// TEST: Character_LevelUp_MaxStats`: Character stats do not exceed class maximums.
*   `// TEST: Class_Create_Valid`: Successfully creates a game class with valid base data.
*   `// TEST: Class_Promotion_Valid`: Unit promotes to the correct class with correct stat gains.
*   `// TEST: Class_Promotion_Invalid`: Unit cannot promote if conditions (level, item) are not met.
*   `// TEST: UnitInstance_Initialize_CorrectStats`: `UnitInstance` is created with stats derived correctly from Character and Class.
*   `// TEST: UnitInstance_Movement_TerrainCosts`: Unit movement range correctly reflects terrain costs for its movement type.
*   `// TEST: UnitInstance_Dismount`: Unit correctly transitions to dismounted class, stats, and movement.
*   `// TEST: UnitInstance_Mount`: Unit correctly transitions to mounted class, stats, and movement.
*   `// TEST: UnitInstance_CannotMountIndoors`: Unit cannot use Mount command if map is indoors.
*   `// TEST: Skill_Effect_Vantage`: Vantage skill correctly allows unit to attack first.
*   `// TEST: Skill_Effect_Elite`: Elite skill correctly doubles EXP gain.
*   `// TEST: AutolevelScheme_AppliesCorrectGrowths`: Generic units using an autolevel scheme gain stats appropriately.
*   `// TEST: Capture_Successful`: Unit successfully captures an eligible enemy.
*   `// TEST: Capture_TransferItems`: Captured enemy's items are transferred to captor.
*   `// TEST: Rescue_StatPenalty`: Rescuing unit receives correct stat penalties.

This specification will be refined as more data source details (especially for `aClassData` and individual character stats/growths) are uncovered. Next, I will look into [`ItemData.asm`](FireEmblem5/SRC/ItemData.asm:0).