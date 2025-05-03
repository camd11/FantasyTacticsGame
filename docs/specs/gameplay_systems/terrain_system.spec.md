# Module: Terrain System Specification

## 1. Overview

This document specifies the implementation details for terrain effects beyond basic movement costs in the Fantasy Tactics Game. It covers how terrain data is stored, how combat bonuses are applied, how turn-based effects like healing or damage function, and how these effects interact with different unit movement types and other game systems. This is based on mechanics observed in Fire Emblem: Thracia 776 and adapted for this project.

## 2. Data Structure (`data/terrain.yaml`)

The existing `data/terrain.yaml` needs to be extended to store additional terrain properties.

**Proposed Structure:**

```yaml
TERRAIN_ID:
  id: "TERRAIN_ID"
  name: "Terrain Name"
  description: "Description of the terrain."
  movement_costs:
    INFANTRY: cost
    CAVALRY: cost
    ARMORED: cost
    FLYING: cost
    # ... other movement types
  combat_modifiers:
    defense: bonus_value  # Flat defense bonus
    resistance: bonus_value # Flat resistance bonus (NEW)
    avoid: bonus_value    # Flat avoid bonus (percentage points)
  turn_effects:           # (NEW Section)
    heal_percent: percentage # e.g., 10 for 10% max HP heal
    damage_percent: percentage # e.g., 5 for 5% max HP damage
    # status_inflict: STATUS_ID # Future: Inflict status?
    # status_cure: STATUS_ID   # Future: Cure status?
    timing: "start_of_unit_turn" # When effect applies ("start_of_unit_turn", "end_of_unit_turn", "start_of_player_phase", etc.)
  ignores_effects_by: ["FLYING", "CAVALRY"] # (NEW) List of movement types that ignore combat_modifiers and turn_effects for this terrain.
  passable: boolean
  passable_by: ["MOVEMENT_TYPE"] # Optional: Only these types can pass if passable=false
  graphic_id: "asset_name"
```

**Example (Fort):**

```yaml
FORT:
  id: "FORT"
  name: "Fort"
  description: "Defensive structure providing protection and recovery."
  movement_costs:
    INFANTRY: 1
    CAVALRY: 2 # Mounted units often slower on forts
    ARMORED: 1
    FLYING: 1
  combat_modifiers:
    defense: 3
    resistance: 1 # Example: Minor magic resistance
    avoid: 30
  turn_effects:
    heal_percent: 10 # Heals 10% of Max HP
    timing: "start_of_unit_turn" # Heal at the start of the unit's turn
  ignores_effects_by: ["FLYING"] # Fliers don't get fort bonuses/healing
  passable: true
  graphic_id: "fort_tile"
```

**Example (Lava - Hypothetical Damaging Terrain):**

```yaml
LAVA:
  id: "LAVA"
  name: "Lava"
  description: "Molten rock that damages units standing on it."
  movement_costs:
    INFANTRY: 5
    CAVALRY: 99
    ARMORED: 4
    FLYING: 1 # Fliers can fly over
  combat_modifiers:
    defense: -2 # Example: Makes unit more vulnerable
    resistance: -2
    avoid: -10
  turn_effects:
    damage_percent: 15 # Deals 15% of Max HP damage
    timing: "start_of_unit_turn"
  ignores_effects_by: ["FLYING"] # Fliers don't take damage or get debuffs
  passable: false
  passable_by: ["FLYING", "ARMORED", "INFANTRY"] # Only these can enter
  graphic_id: "lava_tile"
```

**TDD Anchors:**
*   `# TDD: Test loading terrain data with new resistance field.`
*   `# TDD: Test loading terrain data with new turn_effects structure (heal_percent, damage_percent, timing).`
*   `# TDD: Test loading terrain data with new ignores_effects_by field.`

## 3. Combat Integration

Terrain bonuses (Defense, Resistance, Avoid) must be applied during combat calculations, specifically affecting the defending unit.

**Module:** `CombatCalculator` (or relevant combat processing module)

**Dependencies:** `MapSystem`, `UnitSystem`, `TerrainDataService`

**Function:** `calculate_combat_outcome(attacker_unit, defender_unit)`

```pseudocode
FUNCTION calculate_combat_outcome(attacker_unit, defender_unit):
  // ... existing setup ...

  // Get Defender's Terrain Data
  defender_coords = defender_unit.get_coordinates()
  terrain_id = MapSystem.get_terrain_id_at(defender_coords)
  terrain_data = TerrainDataService.get_terrain_data(terrain_id)

  // Determine if Defender ignores terrain effects
  defender_movement_type = defender_unit.get_movement_type()
  ignores_terrain = FALSE
  IF terrain_data.ignores_effects_by CONTAINS defender_movement_type:
    ignores_terrain = TRUE
  // Add specific check for mounted units if needed (Thracia rule: mounted ignore unless dismounted)
  IF defender_movement_type == "CAVALRY" AND defender_unit.is_mounted(): // Assuming is_mounted() exists
      ignores_terrain = TRUE

  // Apply Terrain Bonuses (if not ignored)
  terrain_defense_bonus = 0
  terrain_resistance_bonus = 0
  terrain_avoid_bonus = 0

  IF NOT ignores_terrain:
    terrain_defense_bonus = terrain_data.combat_modifiers.get("defense", 0)
    terrain_resistance_bonus = terrain_data.combat_modifiers.get("resistance", 0)
    terrain_avoid_bonus = terrain_data.combat_modifiers.get("avoid", 0)

  // --- Hit/Avoid Calculation ---
  attacker_hit_rate = calculate_hit_rate(attacker_unit, defender_unit) // Existing function
  defender_avoid_rate = calculate_avoid_rate(defender_unit, attacker_unit) // Existing function

  // Add terrain avoid bonus to defender's base avoid
  final_defender_avoid = defender_avoid_rate + terrain_avoid_bonus
  // # TDD: Test defender_avoid_rate calculation includes terrain_avoid_bonus.
  // # TDD: Test flier avoid calculation ignores terrain_avoid_bonus.
  // # TDD: Test mounted avoid calculation ignores terrain_avoid_bonus.
  // # TDD: Test dismounted avoid calculation includes terrain_avoid_bonus.

  battle_hit_chance = clamp(attacker_hit_rate - final_defender_avoid, 1, 99) // Apply caps

  // --- Damage Calculation ---
  // Attacker calculates damage against defender
  attacker_damage_result = calculate_damage(attacker_unit, defender_unit, terrain_defense_bonus, terrain_resistance_bonus)
  // # TDD: Test physical damage calculation includes terrain_defense_bonus for defender.
  // # TDD: Test magical damage calculation includes terrain_resistance_bonus for defender.
  // # TDD: Test flier damage calculation ignores terrain bonuses for defender.

  // Defender calculates damage against attacker (if counterattacking)
  // Note: Attacker's terrain bonuses would apply if they are defending
  defender_damage_result = calculate_damage(defender_unit, attacker_unit, /* attacker's terrain def */, /* attacker's terrain res */)

  // ... rest of combat simulation (doubling, crits, etc.) ...

  RETURN combat_results
ENDFUNCTION

FUNCTION calculate_damage(attacker, defender, defender_terrain_def_bonus, defender_terrain_res_bonus):
  // ... get base attack, base defense/resistance ...

  IF is_physical_attack(attacker.equipped_weapon):
    final_defense = defender.get_defense() + defender_terrain_def_bonus
    damage = (attacker.get_attack_power() - final_defense)
  ELSE IF is_magical_attack(attacker.equipped_weapon):
    final_resistance = defender.get_resistance() + defender_terrain_res_bonus // Assuming base resistance exists
    damage = (attacker.get_attack_power() - final_resistance)
  ELSE:
    damage = 0 // Or handle other attack types

  damage = max(0, damage) // Damage cannot be negative
  RETURN damage
ENDFUNCTION
```

**TDD Anchors:**
*   `# TDD: Test combat forecast correctly displays effective Def/Res/Avo including terrain.`
*   `# TDD: Test combat outcome reflects damage reduction from terrain Def.`
*   `# TDD: Test combat outcome reflects damage reduction from terrain Res.`
*   `# TDD: Test combat outcome reflects reduced hit chance from terrain Avo.`
*   `# TDD: Test combat involving a flier on bonus terrain shows no bonus applied.`
*   `# TDD: Test combat involving a mounted unit on bonus terrain shows no bonus applied.`
*   `# TDD: Test combat involving a dismounted unit on bonus terrain shows bonus applied.`

## 4. Turn-Based Effects

Effects like healing (Forts) or damage (Lava) need to be applied systematically during the turn sequence.

**Module:** `TurnManager` or `TerrainEffectSystem`

**Dependencies:** `MapSystem`, `UnitSystem`, `TerrainDataService`, `ActiveUnitManager` (list of units on map)

**Proposed Logic:** Integrate into the phase transition logic.

```pseudocode
// Within TurnManager or similar module

FUNCTION process_turn_start_effects(current_phase_faction):
  // Get all units belonging to the current_phase_faction
  active_units = ActiveUnitManager.get_units_by_faction(current_phase_faction)

  FOR unit IN active_units:
    // Check for Status Effects (e.g., Poison damage) - Existing logic
    // ... apply status effects ...

    // Check for Terrain Effects
    unit_coords = unit.get_coordinates()
    terrain_id = MapSystem.get_terrain_id_at(unit_coords)
    terrain_data = TerrainDataService.get_terrain_data(terrain_id)

    IF terrain_data HAS turn_effects AND terrain_data.turn_effects.timing == "start_of_unit_turn": // Or relevant timing check
      // Check if unit ignores effects
      unit_movement_type = unit.get_movement_type()
      ignores_terrain = FALSE
      IF terrain_data.ignores_effects_by CONTAINS unit_movement_type:
        ignores_terrain = TRUE
      // Add specific check for mounted units if needed
      IF unit_movement_type == "CAVALRY" AND unit.is_mounted():
          ignores_terrain = TRUE

      IF NOT ignores_terrain:
        // Apply Healing
        IF terrain_data.turn_effects.heal_percent > 0:
          heal_amount = calculate_percent_heal(unit, terrain_data.turn_effects.heal_percent)
          unit.apply_heal(heal_amount)
          // Display healing animation/log
          // # TDD: Test unit on Fort heals correct % of max HP at turn start.
          // # TDD: Test flier on Fort does not heal.

        // Apply Damage
        IF terrain_data.turn_effects.damage_percent > 0:
          damage_amount = calculate_percent_damage(unit, terrain_data.turn_effects.damage_percent)
          unit.apply_damage(damage_amount, source="terrain") // Ensure damage source is clear
          // Display damage animation/log
          // Check if unit died from terrain damage
          // # TDD: Test unit on Lava takes correct % of max HP damage at turn start.
          // # TDD: Test flier on Lava does not take damage.
          // # TDD: Test terrain damage can defeat a unit.
          // # TDD: Test terrain damage leaves unit at 1 HP if it cannot defeat (if that's the rule).

        // Apply Status Effects (Future)
        // IF terrain_data.turn_effects.status_inflict:
        //   unit.apply_status(terrain_data.turn_effects.status_inflict)

  ENDFOR
ENDFUNCTION

FUNCTION calculate_percent_heal(unit, percentage):
  max_hp = unit.get_max_hp()
  heal_amount = floor(max_hp * (percentage / 100.0))
  RETURN max(1, heal_amount) // Heal at least 1 HP if percentage > 0

FUNCTION calculate_percent_damage(unit, percentage):
  max_hp = unit.get_max_hp()
  damage_amount = floor(max_hp * (percentage / 100.0))
  RETURN max(1, damage_amount) // Deal at least 1 damage if percentage > 0
```

**Considerations:**
*   **Timing:** Decide precisely when effects trigger (Start of Player Phase? Start of Enemy Phase? Start of each individual unit's turn before they can act?). "Start of unit's turn" seems most consistent with Thracia's Fort healing.
*   **Stacking:** How do terrain effects interact with status effects (e.g., Poison + Lava damage)? Assume they stack unless specified otherwise.
*   **Lethality:** Can terrain damage kill a unit, or does it leave them at 1 HP? Thracia's poison typically couldn't kill directly, but this needs confirmation/decision for this game. Assume it *can* kill for now unless decided otherwise.

**TDD Anchors:**
*   `# TDD: Test Fort healing occurs at the specified timing (e.g., start of unit turn).`
*   `# TDD: Test Lava damage occurs at the specified timing.`
*   `# TDD: Test unit with multiple turn effects (e.g., Poison status + Lava terrain) takes combined damage.`
*   `# TDD: Test healing calculation is correct based on unit max HP.`
*   `# TDD: Test damage calculation is correct based on unit max HP.`

## 5. Movement Type Interaction

The interaction between movement types and terrain effects needs to be consistently enforced.

*   **Movement Costs:** Already handled by the `movement_costs` structure in `terrain.yaml`.
*   **Combat & Turn Effects:** The `ignores_effects_by` list in the proposed `terrain.yaml` structure handles this explicitly.
    *   The logic in `calculate_combat_outcome` and `process_turn_start_effects` must check this list against the unit's movement type.
    *   A specific check for mounted units (ignoring effects unless dismounted) should be added if that rule is desired, potentially overriding or supplementing the `ignores_effects_by` list. This requires a way to check if a unit `is_mounted()` or `is_dismounted()`.

**Pseudocode Snippet (Checking Ignore):**

```pseudocode
FUNCTION should_ignore_terrain_effects(unit, terrain_data):
  unit_movement_type = unit.get_movement_type()

  // Check explicit ignore list
  IF terrain_data.ignores_effects_by CONTAINS unit_movement_type:
    RETURN TRUE

  // Check specific mounted rule (if applicable)
  IF unit_movement_type == "CAVALRY" AND unit.is_mounted(): // Assumes is_mounted() check
    RETURN TRUE // Mounted units ignore ground effects

  RETURN FALSE
ENDFUNCTION

// Usage:
IF NOT should_ignore_terrain_effects(defender_unit, terrain_data):
  // Apply combat bonuses...

IF NOT should_ignore_terrain_effects(unit, terrain_data):
  // Apply turn effects...
```

**TDD Anchors:**
*   `# TDD: Test should_ignore_terrain_effects returns TRUE for a flier on Fort.`
*   `# TDD: Test should_ignore_terrain_effects returns TRUE for a mounted cavalry on Forest.`
*   `# TDD: Test should_ignore_terrain_effects returns FALSE for a dismounted cavalry on Forest.`
*   `# TDD: Test should_ignore_terrain_effects returns FALSE for infantry on Forest.`

## 6. System Integration Points

*   **`TerrainDataService`:** Responsible for loading and providing access to the `terrain.yaml` data.
    *   `FUNCTION get_terrain_data(terrain_id)`
*   **`MapSystem`:** Stores the map layout, including the terrain ID for each tile.
    *   `FUNCTION get_terrain_id_at(coords)`
*   **`UnitSystem` / `Unit Class`:** Stores unit properties like current HP, max HP, stats (Def, Res), movement type, current coordinates, status effects, mounted/dismounted state. Provides methods to apply damage/healing.
    *   `METHOD get_coordinates()`
    *   `METHOD get_movement_type()`
    *   `METHOD get_defense()`
    *   `METHOD get_resistance()`
    *   `METHOD get_avoid()` // Base avoid before terrain
    *   `METHOD get_max_hp()`
    *   `METHOD get_current_hp()`
    *   `METHOD apply_heal(amount)`
    *   `METHOD apply_damage(amount, source)`
    *   `METHOD is_mounted()` // NEW or existing check
*   **`CombatCalculator`:** Integrates terrain bonuses into hit, avoid, and damage calculations (as detailed in Section 3).
*   **`TurnManager`:** Orchestrates turn phases and triggers the processing of turn-based terrain effects (as detailed in Section 4).
*   **`ActiveUnitManager`:** Provides lists of active units on the map, filterable by faction, needed by `TurnManager` for applying effects.

## 7. Future Considerations

*   **Status Effects:** Inflicting or curing status via terrain.
*   **Vision Effects:** Terrain blocking line of sight or affecting vision range (Fog of War).
*   **Special Interactions:** Terrain that interacts with specific skills or items (e.g., traversable only with specific boots).
*   **Destructible Terrain:** Walls or barriers that can be destroyed, changing their terrain type.