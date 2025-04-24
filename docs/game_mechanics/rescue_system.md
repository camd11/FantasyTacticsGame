# Rescue System

This document outlines the implementation of the Rescue mechanic based on Fire Emblem: Thracia 776, with some custom adjustments.

## Overview

The Rescue System allows units to pick up and carry other units across the battlefield. This mechanic has been implemented with nuanced Build/Constitution mechanics:

1. **Build/Constitution Check**: A unit can rescue another if "Rescuer Build >= Target Build / 2"
2. **Mounted Unit Bonus**: Mounted units receive a +5 effective Build bonus for rescue checks
3. **Movement Penalty**: Movement is halved when "Carried Build > Carrier Build / 2" (with mounted bonus applied)
4. **Stat Penalties**: The rescuer's stats (Str/Mag/Skl/Spd/Def) are halved while carrying a unit

## Implementation Details

### Can Rescue Check

```python
# Check Constitution/Build: Rescuer's Build/Con >= Target's Build/Con / 2
rescuer_build = rescuer.stats.get("bld", rescuer.stats.get("con", 0))
target_build = target.stats.get("bld", target.stats.get("con", 0))

# Mounted units get +5 effective Build for rescue checks
effective_rescuer_build = rescuer_build
if hasattr(rescuer, 'is_mounted') and rescuer.is_mounted and not rescuer.is_dismounted:
    effective_rescuer_build += 5
    
# The actual Build check: effective_rescuer_build >= target_build / 2
if effective_rescuer_build < (target_build / 2):
    return False
```

### Movement Penalty Check

```python
# Use bld if available, otherwise fall back to con for backward compatibility
carrier_build = carrier.stats.get('bld', carrier.stats.get('con', 0))
carried_build = carried.stats.get('bld', carried.stats.get('con', 0))

# Apply mounted bonus to carrier's effective build
effective_carrier_build = carrier_build
if hasattr(carrier, 'is_mounted') and carrier.is_mounted and not carrier.is_dismounted:
    effective_carrier_build += 5

# Calculate the threshold (half of carrier's effective build)
half_carrier_build = effective_carrier_build / 2

# Apply movement penalty if carried unit is too heavy
if carried_build > half_carrier_build:
    carrier.stats['mov'] = carrier.temp_stats['original_mov'] // 2
else:
    carrier.stats['mov'] = carrier.temp_stats['original_mov']
```

## Rescue Actions

The Rescue System supports several actions:

1. **Rescue**: Pick up an adjacent ally (subject to Build checks)
2. **Drop**: Place a carried ally on an adjacent tile
3. **Take**: Take a carried unit from an adjacent ally
4. **Give**: Hand a carried unit to an adjacent ally

## Rules and Restrictions

1. **Build Requirement**: Rescuer's Build (+ mounted bonus if applicable) must be >= Target's Build / 2
2. **Cannot Rescue if Rescuing**: A unit already carrying someone cannot be rescued
3. **Stat Penalties**: Rescuer's stats (Str/Mag/Skl/Spd/Def) are halved while carrying
4. **Movement Penalty**: Rescuer's Mov is halved if Carried Build > Carrier Build / 2
5. **Actions**: Carried units cannot take actions (attack, use items, etc.)
6. **Positioning**: Carried units do not occupy a tile for movement or combat calculations

## Interaction with Other Systems

### Interaction with Dismounting

- Mounted units receive a +5 effective Build bonus for rescue calculations
- This bonus is lost when dismounted (indoors or voluntarily)
- Movement penalties still apply based on effective Build after dismounting

### Interaction with Combat

- Units carrying others have their combat stats (Str/Mag/Skl/Spd/Def) halved
- Carried units cannot be targeted directly in combat

## Testing

The Rescue System has been thoroughly tested with:

1. **Basic Rescue Tests**: Units with varying Build values
2. **Mounted Bonus Tests**: Verifying the +5 Build bonus for mounted units
3. **Dismounted Unit Tests**: Testing behavior of dismounted mounted units
4. **Movement Penalty Tests**: Ensuring movement penalties are applied correctly
5. **Edge Cases**: Testing exact threshold values for rescue checks and movement penalties

## Example Scenarios

- Infantry (Build 8) rescuing Mage (Build 5): Can rescue, no movement penalty
- Infantry (Build 8) rescuing Knight (Build 13): Cannot rescue (8 < 13/2)
- Mounted Paladin (Build 10 + 5 bonus) rescuing Knight (Build 13): Can rescue, no movement penalty
- Dismounted Cavalier (Build 9, no bonus) trying to rescue General (Build 16): Cannot rescue (9 < 16/2)

## Historical Note

This implementation combines the Build-based rescue mechanics from Fire Emblem: Thracia 776 with some custom adjustments to balance gameplay and accommodate the existing codebase. The system replaces a simpler implementation that used a direct "Rescuer CON > Target CON" check. 