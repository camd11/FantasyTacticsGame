# Build/Constitution (Bld/Con) Mechanics Research

## Overview
Build/Constitution is a core stat in the Fantasy Tactics Game that affects several key mechanics:

1. **Attack Speed (AS) Calculation**
2. **Rescue/Capture System**
3. **Stealing System**

## Attack Speed (AS) Calculation

### Custom Implementation
The game uses a custom implementation that deviates from Fire Emblem: Thracia 776:

```
AS = Spd - MAX(0, Weapon Weight - Bld)
```

- Build/Constitution mitigates weapon weight penalties for **ALL** weapon types, including tomes
- This differs from Thracia 776, where Con only mitigated physical weapon weight penalties

### Implementation Details
- In `combat_calculator.py`, the `calculate_attack_speed` method implements this formula
- The code first checks for the `bld` attribute, falling back to `con` for backward compatibility
- For any weapon type (physical or magical), the formula subtracts the effective weight penalty from Speed
- Effective weight penalty = MAX(0, weapon.weight - unit.bld)

## Rescue System

### Rescue Check
To rescue another unit, the following condition must be met:
```
Rescuer's Build >= Target's Build / 2
```

- Mounted units receive a +5 effective Build bonus for rescue checks
- Implemented in `rescue_system.py` in the `can_rescue` method
- This prevents smaller units from rescuing larger units

### Take Check
When taking a rescued unit from another unit:
```
Taker's Build > Carried Unit's Build / 2
```

- Mounted units receive a +5 effective Build bonus for this check as well
- Implemented in `rescue_system.py` in the `can_take` method

### Penalties
Rescuing a unit applies the following penalties:
- Rescuer's stats (Str/Mag/Skl/Spd/Def) are halved
- Movement penalties apply when: `Carried Build > Carrier Build / 2` (with mounted bonus applied)

## Stealing System

### Weight Condition
To steal an item:
```
Item Weight <= Attacker Build
```

- Implemented in `stealing_system.py`
- Prevents stealing items that are too heavy for the thief to carry

## Implementation History

The Build/Constitution mechanics have been refined throughout development:

1. **Initial Implementation**: Simple "Rescuer Con > Target Con" check for rescue system
2. **Current Implementation**: More nuanced "Rescuer Build >= Target Build / 2" with mounted bonuses
3. **Attack Speed Integration**: Build now mitigates weapon weight penalties for all weapon types

## Comparison with Source Material

| Mechanic | Thracia 776 | Our Implementation |
|----------|-------------|-------------------|
| Attack Speed | Con only mitigates physical weapon weight | Build mitigates ALL weapon weight (physical and magical) |
| Rescue Check | Rescuer Build >= Target Build / 2 | Same, with +5 Build bonus for mounted units |
| Movement Penalty | Applied when carrying | Applied when Carried Build > Carrier Build / 2 |
| Stat Penalties | Halved stats when carrying | Same |

## Conclusion

The Build/Constitution stat plays a crucial role in:
- Combat mechanics (by affecting Attack Speed)
- Unit interactions (through the Rescue system)
- Item acquisition (through the Stealing system)

This stat creates strategic depth by requiring players to consider unit sizes and equipment weights when planning their tactics. The custom implementation enhances gameplay by making Build relevant for both physical and magical units. 