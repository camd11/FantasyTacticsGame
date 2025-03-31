# Fire Emblem: Thracia 776 Mechanics Reference

This document serves as a comprehensive reference for the game mechanics of Fire Emblem: Thracia 776. It is intended to be used by developers working on the recreation project who may not have access to the original research materials.

## Table of Contents

1. [Game Flow and Turn Structure](#1-game-flow-and-turn-structure)
2. [Unit Statistics](#2-unit-statistics)
3. [Classes and Promotions](#3-classes-and-promotions)
4. [Weapons and Items](#4-weapons-and-items)
5. [Combat System](#5-combat-system)
6. [AI Behavior](#6-ai-behavior)
7. [Fatigue System](#7-fatigue-system)
8. [Movement and Terrain](#8-movement-and-terrain)
9. [Status Effects and Conditions](#9-status-effects-and-conditions)
10. [Unit State and Deployment Rules](#10-unit-state-and-deployment-rules)
11. [Turn Events and Victory Conditions](#11-turn-events-and-victory-conditions)
12. [Support and Leadership Bonuses](#12-support-and-leadership-bonuses)
13. [Special Mechanics](#13-special-mechanics)

## 1. Game Flow and Turn Structure

### Turn Sequence

Thracia 776 follows a classic turn-based structure divided into distinct phases for each faction:
- **Player Phase**: Player controls all blue units
- **Enemy Phase**: AI controls red enemy units
- **Ally/NPC Phase**: AI controls green ally units (if present)

### Initiative and Combat Order

When combat occurs, the initiating unit strikes first. After the initiator's attack, if the defender survives and is in range to counterattack, the defender counterattacks. Follow-up attacks (doubling) are then handled if applicable.

### Canto (Mounted Unit Movement)

Mounted units can use leftover movement after certain actions. They cannot move again after attacking or using a staff, but they can move again after non-combat actions such as opening doors, rescuing, trading, or using items.

### Turn Start Effects

At the beginning of each side's phase, certain upkeep effects are processed:
- Units on healing terrain (Gates, Forts, Churches) recover HP
- Poison status deals damage at the start of the afflicted unit's phase

### Movement Stars (Extra Action mechanic)

Some units have Movement Stars visible on their status screen. Each Movement Star grants a 5% chance for that unit to gain another full turn after completing their action. The formula is:
```
ExtraActionChance = (Number of Movement Stars × 5)%
```

## 2. Unit Statistics

### Core Stats

- **HP (Hit Points)**: A unit's current and maximum health
- **Strength (Str)**: Governs physical attack power
- **Magic (Mag)**: Power for magical attacks and staves; also acts as resistance to magic damage
- **Skill (Skl)**: Affects hit rate and critical rate
- **Speed (Spd)**: Affects Attack Speed and evade
- **Luck (Luk)**: Adds to hit, avoid, and reduces enemy critical chances
- **Defense (Def)**: Reduces physical damage
- **Constitution (Con)**: Represents body size and weight; affects rescue/capture and weapon weight penalties
- **Movement (Mov)**: How many tiles a unit can move

### Derived Stats

- **Atk (Attack Power)**: Str/Mag + Weapon Mt
- **AS (Attack Speed)**: Spd - Effective Weapon Weight
- **Hit (Accuracy)**: Weapon Hit + 2*Skl + Luk + Bonuses
- **Avo (Avoid)**: 2*AS + Luk + Bonuses
- **Crit (Critical Rate)**: Weapon Crit + Skl + Bonuses
- **Ddg (Dodge / Crit Evade)**: Luck/2 + Bonuses
- **Rng (Range)**: Attack range of equipped weapon
- **FCM (Follow-up Critical Multiplier / PCC)**: Pursuit Critical Coefficient value

### Stat Growths and Caps

Each player character has personal growth rates for each stat. On leveling up, stats have a chance to increase based on these percentages. Thracia 776 uses a 1 RN system for growths (each stat independently rolls its chance).

Special cases:
- HP can exceed 80% growth
- Con and Movement have very low growths (around 5% or lower)
- Most stats cap at 20 for playable units

### Stat Interactions

- **Attack Speed (AS)**: For physical weapons: `AS = Speed – max((Weapon Weight – Con), 0)`. For magic: `AS = Speed – Weapon Weight`
- **Doubling Threshold**: A unit can perform a follow-up attack if their AS exceeds the enemy's AS by 4 or more points
- **Con in Rescuing/Capturing**: Con determines whether a unit can rescue or capture another

## 3. Classes and Promotions

### Class Attributes

Each class has defined base stats, stat caps, and weapon rank limits. Classes also define movement type (infantry, cavalry, flying, etc.) which affects terrain costs.

### Weapon Ranks by Class

Thracia uses lettered weapon ranks from E up to A (and a special "*" rank for legendary weapons). Each class has set initial ranks and maximum attainable ranks for weapon types.

### Promotion Rules

Most classes can promote to a higher-tier class using a promotion item (primarily the Master Seal/Knight's Proof). Uniquely, Thracia 776 does not require a minimum level to promote. Upon promotion:
- The unit receives fixed stat bonuses
- They may gain new weapon access or higher weapon ranks
- Their level is reset to 1
- They can continue leveling up to 20 again

### Dismounting

Mounted units can dismount, which affects their stats and weapon access:
- Indoors, all mounted units must dismount
- While dismounted, units lose the ability to use their primary lance/axe weapons (most cavalry can only use swords when dismounted)
- Dismounted units have reduced Movement
- Dismounted units are no longer considered "mounted" for weapon effectiveness

## 4. Weapons and Items

### Weapon Stats

Every weapon has attributes including:
- **Might (Mt)**: Added to Str/Mag for damage
- **Hit Rate**: Contributes to accuracy
- **Critical (Crit)%**: Base critical percentage
- **Weight (Wt)**: Can reduce Attack Speed if exceeds Con
- **Range**: Typically 1 for melee, 2 for bows, 1-2 for throwable weapons
- **Durability**: Number of uses before breaking
- **Weapon Rank**: Proficiency needed to wield it

### Weapon Types

- **Physical Weapons**: Swords, Lances, Axes, Bows
- **Magic**: Anima (Fire, Thunder, Wind), Light, Dark
- **Staves**: Healing and status
- **Throwing Weapons**: Javelins, Hand Axes, etc. (1-2 range)
- **Ballistae**: Enemy-only long-range weapons

### Weapon Triangle

- **Physical**: Swords > Axes > Lances > Swords
- **Anima Magic**: Fire > Wind > Thunder > Fire
- **Light/Dark**: Strong against Anima magic

When at advantage, the attacker gets +5 hit; at disadvantage, -5 hit.

### Weapon Rank and EXP

Units gain weapon experience (WExp) by using weapons in combat:
- Each successful combat round grants 1 WExp
- Staff WExp depends on rank: E=1, D=2, C=3, B=4, A=5
- Thresholds: E→D=50, D→C=50, C→B=50, B→A=50, A→*=50

### Special Items

- **Healing items**: Vulnerary (heals 20 HP, 3 uses)
- **Stat Boosters**: Permanently increase a stat
- **Scrolls**: Boost growth rates and prevent enemy criticals
- **Status Staves**: Sleep, Silence, Berserk, etc.
- **Torch**: Increases vision in Fog of War

## 5. Combat System

### Hit and Avoid

**Hit Formula**:
```
Hit = Weapon Hit + (2 × Skill) + Luck + Support bonuses + Leadership bonuses + Charisma bonus + Weapon Triangle bonus
```

**Avoid Formula**:
```
Avoid = (2 × Attack Speed) + Luck + Support bonus + Leadership bonus + Charisma bonus + Terrain bonus
```

The final hit chance is clamped between 1% and 99%.

### Damage Calculation

**Physical Damage**:
```
Physical Damage = (Strength + Weapon Might × Effective Bonus) - (Defense + Terrain defense bonus)
```

**Magical Damage**:
```
Magical Damage = (Magic + Weapon Might × Effective Bonus) - (Magic + Magic bonuses + Terrain bonus)
```

**Effective Bonus**: 3x Might if weapon is effective against the target, otherwise 1x

### Critical Rate and PCC

**Critical Rate**:
```
Critical Rate = (Weapon Critical + Skill + Support bonus) - (Luck/2 + Support bonus)
```

**PCC System**:
- On first attack: Critical rate capped at 25%
- On follow-up attacks: Critical rate multiplied by unit's PCC value

### Follow-Up Attacks

A unit can perform a follow-up attack if their Attack Speed exceeds the enemy's Attack Speed by 4 or more points.

### Combat Sequence

1. Attacker's first strike
2. Defender's counterattack (if in range)
3. Attacker's follow-up (if AS ≥ defender's AS + 4)
4. Defender's follow-up (if AS ≥ attacker's AS + 4)

**Brave Weapons** grant an immediate extra attack on initiation, potentially allowing 4 attacks if the unit can also follow-up.

### Experience Calculation

```
Base EXP = 10 + (Defender's Level + Class Bonus - Attacker's Level)
```

- If defender is defeated: Full EXP
- If not defeated: Half EXP
- Boss bonus: +40 EXP
- Thief bonus: +20 EXP

## 6. AI Behavior

### Aggression and Movement

- **Charge AI**: Moves toward player units and attacks whenever possible
- **Stationary (Guard) AI**: Does not move from position, but attacks any player that comes into range
- **Limited Pursuit**: Moves toward player only within a certain radius
- **Attack beyond range**: Will attack enemies slightly beyond normal aggression range

### Target Selection

- Enemies generally choose targets based on damage and hit chance
- Many enemies will choose to capture instead of kill if conditions are met
- Thieves prioritize stealing treasure and escaping
- Healers will use healing staves on injured allies
- Some enemies retreat when low on HP

### Capture and Item Trading

If an enemy successfully captures a player unit, they will immediately try to trade the captured unit's items to nearby allies to prevent the player from easily getting them back.

## 7. Fatigue System

### Accumulating Fatigue

When a unit takes certain actions in battle, they gain fatigue points:
- Combat: +1 fatigue
- Staves: +1 to +5 fatigue depending on staff rank
- Stealing/Dancing: +1 fatigue

### Threshold – Max HP

Each unit has a fatigue threshold equal to their current max HP. If fatigue meets or exceeds max HP, the unit becomes fatigued and cannot be deployed in the next chapter.

### Effects of Fatigue

- Fatigue itself during a chapter has no effect on stats
- Fatigued units cannot be deployed in the next chapter
- Leif (Lord) is exempt from the fatigue system
- The system begins in Chapter 8

### Resetting Fatigue

- When a unit sits out a chapter, their fatigue resets to 0
- S-Drink (Stamina Drink) can be used to restore fatigue to 0

## 8. Movement and Terrain

### Movement Types

- **Infantry**: Standard movement costs
- **Armored**: Heavy infantry, often slower on certain terrain
- **Cavalry**: Fast on plains, restricted in heavy terrain or indoors
- **Flying**: Ignore most terrain costs
- **Terrain-specialists**: Pirates (water), Brigands (mountains)

### Terrain Movement Cost Table

Each terrain type has a movement cost per unit type. Moving into a tile subtracts that cost from the unit's remaining movement points. Some terrain is impassable for certain types.

Examples:
- Plains: Cost 1 for all unit types
- Forest: Cost 3 for Cavalry, 1 for Fliers, 2 for others
- Mountain: Impassable to cavalry, cost 2 for Infantry
- Water: Only Pirates and Fliers can traverse

### Indoor/Outdoor Movement

Mounted units cannot be mounted indoors. When transitioning from an outdoor area to an indoor area, a mounted unit must dismount at the threshold.

### Fog of War (Vision)

Some maps have limited vision range (typically 3 tiles for most units, 5 for Thieves). Vision can be extended using Torch items or the Torch staff.

### Terrain Effects in Combat

Terrain can provide defensive bonuses:
- Forest: +20 Avoid, +2 Defense
- Mountain: +30 Avoid, +5 Defense
- Fort/Throne: +20 Avoid, +10 Defense, healing effect

## 9. Status Effects and Conditions

### No Automatic Recovery

In Thracia, status conditions do not wear off on their own over time. They persist until the chapter ends or the unit is healed via a staff.

### Status Types

- **Poison**: Unit takes 1-2 HP damage at the start of each turn
- **Sleep**: Unit cannot act at all, Str/Mag/Skl/Spd/Def considered 0
- **Silence**: Unit cannot use magic or staves
- **Berserk**: Unit turns hostile to allies
- **Petrify (Stone)**: Unit is completely immobilized

### Recovery

The primary method to remove a status is the Restore Staff. A single use will cure any and all negative statuses on the target (except petrify, which requires the Kia Staff).

## 10. Unit State and Deployment Rules

### Permanent Death

If a player unit's HP falls to 0 and they are not captured, they are considered dead and removed from the game's roster permanently.

### Capture State

If a player unit is captured by an enemy, they disappear from the current map. They can be recovered in Chapter 21x, which is a prison break mission.

### Escape Missions

In escape chapters, if Leif (the Lord) escapes before other units, any remaining units are considered captured and will be unavailable until Chapter 21x.

### Deployment Limits

Each chapter has a preset maximum number of units that can be deployed. Fatigue may force some units to sit out.

## 11. Turn Events and Victory Conditions

### Victory Conditions

- **Seize**: Leif must move to a specified tile and use the Seize command
- **Escape**: All units must escape from a point (with Leif last)
- **Defend/Survive**: Defend for a specific number of turns
- **Rout or Kill Boss**: Defeat all enemies or a specific boss

### Turn-based Events

- **Reinforcements**: Enemy units spawn at specific turn counts
- **Allied reinforcements**: Green or blue units may appear
- **NPC behavior changes**: NPCs may change AI behavior at certain turns
- **Conversation triggers**: Units talking to each other
- **Area triggers**: Stepping on specific tiles

## 12. Support and Leadership Bonuses

### Support Bonuses

When two compatible characters are within 3 tiles of each other, one or both may receive a combat bonus. Thracia's supports are typically one-way and provide bonuses to Hit, Avoid, Critical, and Crit Evade.

### Leadership Stars

Certain characters have Leadership stars visible on their status screen. Each star grants a +3% Hit and +3% Avoid boost to all allies in that army. This applies globally as long as that character is on the field.

### Charisma (Charm) Skill

The Charisma personal skill gives a +10 Hit/+10 Avoid bonus to all allied units within a 3-tile radius. This stacks with supports and leadership.

## 13. Special Mechanics

### Stealing

Units with the Steal ability can steal items from enemies if:
1. The thief's Attack Speed > enemy's Attack Speed
2. The item's weight ≤ thief's Con

Thieves can steal any item from the enemy's inventory, including equipped weapons.

### PCC (Pursuit Critical Coefficient)

Each unit has a PCC value that affects critical rates on follow-up attacks. On the first attack, critical rate is capped at 25%. On follow-up attacks, critical rate is multiplied by the unit's PCC.

### Scrolls

Scrolls provide two effects:
1. Boost growth rates for level-ups
2. Prevent the unit from being hit by enemy criticals

### Capture System

Player units can attempt to capture enemy units instead of killing them. When capturing:
- Strength, Magic, Skill, Speed, and Defense are all halved
- If the enemy's HP is reduced to 0, they are captured
- Captured enemies can be traded with to take their items
- Captured enemies can be released, removing them from the map

### Dismounting

Mounted units can dismount, which affects their stats and weapon access. Indoors, all mounted units must dismount.

### Fatigue

Units accumulate fatigue from combat and other actions. If fatigue exceeds max HP, the unit cannot be deployed in the next chapter.

### Movement Stars

Units have a chance to gain an extra turn based on their Movement Stars. Each star gives a 5% chance.

### Wrath Skill

The Wrath skill forces a critical hit when the unit is counterattacking.

### Adept (Continue) Skill

The Adept skill gives a chance (Skill%) to perform an extra attack after normal attacks.

### Prayer (Miracle) Skill

When HP is 10 or less, Prayer can activate, setting enemy hit rates to 0%.