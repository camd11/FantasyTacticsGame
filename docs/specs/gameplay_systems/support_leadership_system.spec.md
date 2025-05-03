# Specification: Support and Leadership System (Thracia 776 Style)

**Version:** 1.0
**Date:** 2025-04-06

## 1. Overview

This document outlines the specifications for the Support, Leadership, and Charisma systems, designed to replicate the mechanics found in Fire Emblem: Thracia 776. These systems provide passive combat bonuses to units based on their proximity to allies with specific relationships or skills.

**References:** `research.md` (Sections 5.1, 5.3, 12)

## 2. Functional Requirements

### 2.1. Support System
- **Predefined Bonds:** Support relationships are fixed between specific pairs of characters based on game data, not built dynamically through gameplay actions.
- **Range:** Support bonuses are active when the supporting and receiving units are within a 3-tile radius of each other.
- **Bonuses:** Active supports grant a bonus (typically +10, sometimes +20 for strong bonds) to the receiving unit's Hit, Avoid, Critical Hit rate, and Critical Evade rate.
- **Directionality:** Supports can be one-way (Unit A supports Unit B, but B does not support A) or mutual. The game data must define the direction and magnitude for each pair.
- **Stacking:** Bonuses from multiple supporting units stack, but the total bonus for each stat (Hit, Avoid, Crit, Crit Evade) is capped at +30.
- **Hidden Nature:** There is no in-game UI to view support levels or trigger conversations. Bonuses are applied passively.

### 2.2. Leadership System
- **Leadership Stars:** Certain units possess Leadership (Authority) stars, visible on their status screen.
- **Global Effect:** Each Leadership star grants a +3% bonus to Hit and Avoid to *all* allied units currently deployed on the map, regardless of distance.
- **Stacking:** Leadership stars from all deployed allied leaders stack additively. (e.g., Leif with 2 stars and Finn with 1 star provide a total +9% Hit/Avoid bonus to all player units).
- **Applies to All Factions:** Both player and enemy units can benefit from their respective leaders' stars.
- **Dynamic:** The bonus is recalculated if a leader is defeated or leaves the map.

### 2.3. Charisma Skill
- **Skill-Based:** Specific units possess the "Charisma" personal skill.
- **Local Aura:** Units with Charisma provide a +10 bonus to Hit and Avoid to all allied units within a 3-tile radius.
- **Stacking:** Bonuses from multiple Charisma units within range stack additively with each other and with Support/Leadership bonuses.

## 3. Modules and Pseudocode

### 3.1. Support Module (`support_calculator`)

**Purpose:** Calculates the total support bonus for a given unit based on nearby allies.

**Data Structures:**
- `SUPPORT_DATA`: A data structure (e.g., dictionary or list of tuples) mapping pairs of character IDs to their support bonus value and directionality.
  ```
  Example:
  SUPPORT_DATA = {
      ("LEIF_ID", "NANNA_ID"): {"bonus": 10, "mutual": True},
      ("FINN_ID", "LEIF_ID"): {"bonus": 10, "mutual": False}, # Finn supports Leif
      ("MAREETA_ID", "GALZUS_ID"): {"bonus": 20, "mutual": False} # Galzus supports Mareeta
      # ... other pairs
  }
  ```
- `Unit`: Represents a unit on the map, containing `unit_id`, `position` (x, y), `faction`.

**Pseudocode:**

```pseudocode
FUNCTION calculate_support_bonus(target_unit: Unit, all_units: List[Unit], support_data: Dict) -> Dict[str, int]:
    // TDD_ANCHOR: test_calculate_support_bonus_no_allies
    // TDD_ANCHOR: test_calculate_support_bonus_one_ally_in_range
    // TDD_ANCHOR: test_calculate_support_bonus_one_ally_out_of_range
    // TDD_ANCHOR: test_calculate_support_bonus_multiple_allies_stacking
    // TDD_ANCHOR: test_calculate_support_bonus_stacking_cap
    // TDD_ANCHOR: test_calculate_support_bonus_one_way_support
    // TDD_ANCHOR: test_calculate_support_bonus_mutual_support
    // TDD_ANCHOR: test_calculate_support_bonus_enemy_nearby_no_bonus

    DEFINE SUPPORT_RANGE = 3
    DEFINE MAX_BONUS_PER_STAT = 30

    total_bonus = {"hit": 0, "avoid": 0, "crit": 0, "crit_evade": 0}

    FOR other_unit IN all_units:
        IF other_unit IS target_unit:
            CONTINUE // Skip self

        IF other_unit.faction IS NOT target_unit.faction:
            CONTINUE // Skip units from different factions

        distance = calculate_distance(target_unit.position, other_unit.position)

        IF distance <= SUPPORT_RANGE:
            // Check if other_unit supports target_unit
            support_pair_key_1 = (other_unit.unit_id, target_unit.unit_id)
            IF support_pair_key_1 IN support_data:
                support_info = support_data[support_pair_key_1]
                bonus_value = support_info["bonus"]
                total_bonus["hit"] += bonus_value
                total_bonus["avoid"] += bonus_value
                total_bonus["crit"] += bonus_value
                total_bonus["crit_evade"] += bonus_value

            // Check if target_unit supports other_unit (for mutual supports)
            support_pair_key_2 = (target_unit.unit_id, other_unit.unit_id)
            IF support_pair_key_2 IN support_data:
                 support_info = support_data[support_pair_key_2]
                 IF support_info["mutual"] IS True:
                     bonus_value = support_info["bonus"]
                     // Avoid double counting if already added above
                     IF support_pair_key_1 NOT IN support_data OR support_data[support_pair_key_1]["bonus"] != bonus_value:
                         total_bonus["hit"] += bonus_value
                         total_bonus["avoid"] += bonus_value
                         total_bonus["crit"] += bonus_value
                         total_bonus["crit_evade"] += bonus_value

    // Apply caps
    total_bonus["hit"] = min(total_bonus["hit"], MAX_BONUS_PER_STAT)
    total_bonus["avoid"] = min(total_bonus["avoid"], MAX_BONUS_PER_STAT)
    total_bonus["crit"] = min(total_bonus["crit"], MAX_BONUS_PER_STAT)
    total_bonus["crit_evade"] = min(total_bonus["crit_evade"], MAX_BONUS_PER_STAT)

    RETURN total_bonus
ENDFUNCTION

FUNCTION calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    // Manhattan distance for grid
    RETURN abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
ENDFUNCTION
```

### 3.2. Leadership Module (`leadership_calculator`)

**Purpose:** Calculates the total leadership bonus for a given faction based on deployed leaders.

**Data Structures:**
- `Unit`: Contains `unit_id`, `faction`, `is_deployed`, `leadership_stars`.

**Pseudocode:**

```pseudocode
FUNCTION calculate_leadership_bonus(faction: FactionType, all_units: List[Unit]) -> Dict[str, int]:
    // TDD_ANCHOR: test_calculate_leadership_no_leaders
    // TDD_ANCHOR: test_calculate_leadership_one_leader
    // TDD_ANCHOR: test_calculate_leadership_multiple_leaders_stacking
    // TDD_ANCHOR: test_calculate_leadership_only_counts_deployed_units
    // TDD_ANCHOR: test_calculate_leadership_correct_faction

    total_stars = 0
    FOR unit IN all_units:
        IF unit.faction IS faction AND unit.is_deployed:
            total_stars += unit.leadership_stars

    bonus_per_star = 3
    total_bonus = {"hit": total_stars * bonus_per_star, "avoid": total_stars * bonus_per_star}

    RETURN total_bonus
ENDFUNCTION
```

### 3.3. Charisma Module (`charisma_calculator`)

**Purpose:** Calculates the total charisma bonus for a given unit based on nearby allies with the Charisma skill.

**Data Structures:**
- `Unit`: Contains `unit_id`, `position`, `faction`, `has_charisma_skill`.

**Pseudocode:**

```pseudocode
FUNCTION calculate_charisma_bonus(target_unit: Unit, all_units: List[Unit]) -> Dict[str, int]:
    // TDD_ANCHOR: test_calculate_charisma_no_allies
    // TDD_ANCHOR: test_calculate_charisma_no_charisma_allies_in_range
    // TDD_ANCHOR: test_calculate_charisma_one_charisma_ally_in_range
    // TDD_ANCHOR: test_calculate_charisma_one_charisma_ally_out_of_range
    // TDD_ANCHOR: test_calculate_charisma_multiple_charisma_allies_stacking
    // TDD_ANCHOR: test_calculate_charisma_enemy_charisma_no_bonus

    DEFINE CHARISMA_RANGE = 3
    DEFINE CHARISMA_BONUS_PER_UNIT = 10

    total_bonus = {"hit": 0, "avoid": 0}

    FOR other_unit IN all_units:
        IF other_unit IS target_unit:
            CONTINUE

        IF other_unit.faction IS NOT target_unit.faction:
            CONTINUE

        IF other_unit.has_charisma_skill:
            distance = calculate_distance(target_unit.position, other_unit.position)
            IF distance <= CHARISMA_RANGE:
                total_bonus["hit"] += CHARISMA_BONUS_PER_UNIT
                total_bonus["avoid"] += CHARISMA_BONUS_PER_UNIT

    // Note: Thracia 776 sources don't mention a cap for Charisma stacking, unlike Supports.
    // If multiple allies provide +10, it seems they stack fully.

    RETURN total_bonus
ENDFUNCTION
```

## 4. Integration with Combat Calculations

The bonuses calculated by these modules are integrated directly into the combat formulas:

- **Hit Rate:**
  `Hit = Weapon Hit + (2 * Skill) + Luck + Support_Bonus['hit'] + Leadership_Bonus['hit'] + Charisma_Bonus['hit'] + Weapon_Triangle_Bonus`
  *TDD_ANCHOR: test_combat_hit_includes_support*
  *TDD_ANCHOR: test_combat_hit_includes_leadership*
  *TDD_ANCHOR: test_combat_hit_includes_charisma*

- **Avoid Rate:**
  `Avoid = (2 * Attack Speed) + Luck + Support_Bonus['avoid'] + Leadership_Bonus['avoid'] + Charisma_Bonus['avoid'] + Terrain_Bonus`
  *TDD_ANCHOR: test_combat_avoid_includes_support*
  *TDD_ANCHOR: test_combat_avoid_includes_leadership*
  *TDD_ANCHOR: test_combat_avoid_includes_charisma*

- **Critical Hit Rate:**
  `Critical = (Weapon Critical + Skill + Support_Bonus['crit']) - Enemy_Crit_Evade`
  *TDD_ANCHOR: test_combat_crit_includes_support*
  *(Note: Leadership and Charisma do not affect Critical Rate in Thracia 776)*

- **Critical Evade Rate:**
  `Crit_Evade = (Luck / 2) + Support_Bonus['crit_evade']`
  *TDD_ANCHOR: test_combat_crit_evade_includes_support*
  *(Note: Leadership and Charisma do not affect Critical Evade in Thracia 776)*

These bonuses must be calculated dynamically before any combat forecast or execution, considering the current positions and status of all units on the map.

## 5. Edge Cases and Constraints

- **Unit Status:** Bonuses should only be calculated based on units that are currently deployed and active (not defeated, captured, petrified, etc.). Need to clarify if sleeping/silenced/berserk units still provide/receive bonuses (likely they still provide Leadership globally, but might not provide/receive proximity bonuses like Support/Charisma). Assume for now that only deployed and conscious units participate in proximity bonuses. Leadership likely persists as long as the leader is deployed, regardless of status.
- **Faction Alignment:** Bonuses only apply between units of the same faction (Player, Enemy, NPC).
- **Calculation Timing:** Bonuses must be recalculated whenever unit positions change or when units enter/leave the map, to ensure combat forecasts are accurate.
- **Data Management:** The `SUPPORT_DATA` needs to be accurately populated based on Thracia 776 character relationships. Unit data must correctly track `leadership_stars` and `has_charisma_skill`.

## 6. Future Considerations

- Verify the exact behavior of status effects on providing/receiving bonuses.
- Confirm if any specific skills interact with these systems (e.g., does Nihil negate enemy Leadership/Charisma? Unlikely, but worth checking).