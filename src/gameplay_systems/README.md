# Gameplay Systems

This directory contains all the core gameplay systems and mechanics for the Fantasy Tactics Game.

## Key Statistics

### Primary Stats
- **Str (Strength)**: Determines physical attack power
- **Mag (Magic)**: Determines magical attack power
- **Skl (Skill)**: Affects hit rate and critical hit chance
- **Spd (Speed)**: Affects avoid rate and ability to perform follow-up attacks
- **Lck (Luck)**: Affects various random chances and critical hit avoidance
- **Def (Defense)**: Reduces physical damage taken
- **Res (Resistance)**: Reduces magical damage taken
- **Con (Constitution)**: Determines physical build, affects rescue mechanics and weapon weight penalties
  - Formerly called "Build/Bld" in previous versions
  - Mounted units are considered to have 20 Con for rescue/capture purposes only
  - Units with 20 or more Con cannot be captured or rescued
- **Mov (Movement)**: Determines how far a unit can move each turn

### Secondary Stats
- **Hit**: Chance to successfully land an attack
- **Avoid**: Chance to dodge an incoming attack
- **Crit**: Chance to deal a critical hit (3x damage)
- **Crit Avoid**: Chance to avoid receiving a critical hit

## Systems Overview

- **Capture System**: Allows units to capture enemies with lower Con values using melee weapons
  - Requires a weapon usable at range 1 (melee weapon)
  - Attacker suffers 50% penalty to combat stats during capture attempt
  - Captured units are carried and can have their items seized
- **Fatigue System**: Tracks unit stamina across chapters, encouraging army rotation
- **Support System**: Provides combat bonuses based on unit relationships
- **Leadership System**: Provides faction-wide bonuses based on deployed leaders
- **Inventory System**: Manages unit equipment and items
- **Combat System**: Handles battle calculations and outcomes
- **Map System**: Manages terrain, movement, and positioning

## Implementation Notes

- The Fatigue System begins tracking fatigue from Chapter 8 onward (this value is configurable)
- Constitution (Con) is a critical stat for determining rescue mechanics
- Mounted units have special handling in several systems, particularly for Con-related checks
- When carrying a captured unit, the carrier suffers 50% penalty to combat stats
- Movement penalties apply when carrying units based on Con thresholds
- Units can steal items from captured enemies even if they lack the Steal skill 