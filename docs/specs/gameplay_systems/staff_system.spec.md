# Specification: Staff System [DRAFT V1]

## 1. Overview

This document outlines the design for the Staff System in the Fantasy Tactics game, based heavily on the mechanics of Fire Emblem: Thracia 776. This system governs the use of staff items for healing, applying/curing status effects, warping units, and other utility functions. It interacts closely with the Item, Unit, Status Effects, Map, Action, EXP, and AI systems.

## 2. Dependencies

- `ItemSystem`: For managing item data, durability, and inventory.
- `UnitSystem`: For accessing unit stats (Mag, Skl, HP, Con, etc.), applying healing, managing fatigue, and WExp.
- `StatusEffectsSystem`: For applying and removing status conditions.
- `MapSystem`: For determining unit positions, calculating range, checking Line of Sight (LoS), and moving units (Warp/Rescue).
- `ActionSystem`: For consuming unit actions.
- `EXPSystem`: For granting experience points for staff usage.
- `AISystem`: For controlling how AI units utilize staves.
- `CombatFormulas`: For accessing shared calculation logic if needed (though staff hit is unique).

## 3. Data Structures (`data/items.yaml`)

Staff items require specific attributes beyond standard weapons. The proposed structure within `data/items.yaml` is:

```yaml
STAFF_ID:
  id: "STAFF_ID"          # Unique identifier
  name: "Staff Name"      # Display name
  type: "STAFF"           # Item category
  weapon_type: "STAFF"    # Specific weapon category (for WExp)
  required_rank: "E/D/C/B/A" # Minimum staff rank to use
  weight: X               # Weight (affects AS if relevant, though staves aren't used in combat calc)
  max_durability: Y       # Number of uses
  value: Z                # Gold value (if applicable, Thracia has limited economy)

  # --- Staff Specific Attributes ---
  effect_type: "HEAL" | "STATUS_INFLICT" | "STATUS_CURE" | "WARP" | "RESCUE" | "UTILITY" # Primary function
  target_type: "ALLY" | "ENEMY" | "TILE" | "SELF" | "ITEM" # Who/what the staff targets
  range_type: "FIXED" | "MAG_DIV_2" | "USER_MAG" | "GLOBAL" # How range is determined
  range_min: A            # Minimum range (e.g., 0 for self, 1 for adjacent)
  range_max: B            # Maximum range (fixed value, or placeholder like 99 if formula-based)
  base_hit: 60 | 100 | null # Base hit% for accuracy calc (60 default, 100 Torch, null if auto-hit like Heal)

  # --- Effect Details (Conditional) ---
  # If effect_type == "HEAL":
  heal_formula: "POTENCY_ONLY" | "POTENCY_PLUS_USER_MAG" | "FULL_HEAL" # Formula string
  base_potency: P         # Base healing amount

  # If effect_type == "STATUS_INFLICT":
  status_inflicted: "POISON" | "SLEEP" | "SILENCE" | "BERSERK" | "PETRIFY" # Status to apply

  # If effect_type == "STATUS_CURE":
  status_cured: "NEGATIVE" | "POISON" | "SLEEP" | "SILENCE" | "BERSERK" | "PETRIFY" # Status(es) to remove ("NEGATIVE" for all standard ones)

  # If effect_type == "WARP" or "RESCUE":
  # (No extra fields needed, logic handles movement)

  # If effect_type == "UTILITY":
  utility_effect: "ILLUMINATE" | "REPAIR" | "UNLOCK" | "M_UP" # Specific utility action
  utility_potency: Q      # e.g., Vision radius for Torch, +Mag for M Up
  utility_duration: R     # e.g., Turns for M Up decay, Torch illumination

  # --- Thracia Specific ---
  fatigue_cost_override: F # Optional: If fatigue cost differs from standard rank-based cost
```

**Example (Heal Staff):**

```yaml
HEAL_STAFF:
  id: "HEAL_STAFF"
  name: "Heal"
  type: "STAFF"
  weapon_type: "STAFF"
  required_rank: "E"
  weight: 4
  max_durability: 30
  value: 600
  effect_type: "HEAL"
  target_type: "ALLY"
  range_type: "FIXED"
  range_min: 1
  range_max: 1
  base_hit: null # Auto-hits
  heal_formula: "POTENCY_PLUS_USER_MAG"
  base_potency: 10
```

**Example (Sleep Staff):**

```yaml
SLEEP_STAFF:
  id: "SLEEP_STAFF"
  name: "Sleep"
  type: "STAFF"
  weapon_type: "STAFF"
  required_rank: "C"
  weight: 6
  max_durability: 7
  value: 1500
  effect_type: "STATUS_INFLICT"
  target_type: "ENEMY"
  range_type: "USER_MAG" # Thracia range = User Mag
  range_min: 1
  range_max: 99 # Placeholder, calculated dynamically
  base_hit: 60 # Standard base hit for status staves
  status_inflicted: "SLEEP"
```

**Example (Physic Staff - Corrected based on Thracia):**

```yaml
PHYSIC_STAFF:
  id: "PHYSIC_STAFF"
  name: "Physic"
  type: "STAFF"
  weapon_type: "STAFF"
  required_rank: "C"
  weight: 6
  max_durability: 15
  value: 1000 # Example value
  effect_type: "HEAL"
  target_type: "ALLY"
  range_type: "MAG_DIV_2" # Thracia range = User Mag / 2
  range_min: 1
  range_max: 99 # Placeholder, calculated dynamically
  base_hit: null # Auto-hits
  heal_formula: "POTENCY_PLUS_USER_MAG"
  base_potency: 10
```

## 4. Core Functions

```pseudocode
MODULE StaffSystem

  // --- Dependencies ---
  IMPORT ItemSystem, UnitSystem, StatusEffectsSystem, MapSystem, ActionSystem, EXPSystem, AISystem

  // --- Constants ---
  // (Could define fatigue costs, WExp amounts per rank here if not in data)
  FATIGUE_COSTS = {"E": 1, "D": 2, "C": 3, "B": 4, "A": 5, "*": 5}
  WEXP_GAINS = {"E": 1, "D": 2, "C": 3, "B": 4, "A": 5, "*": 5} // Per research.md line 142
  BASE_STAFF_EXP = 10 // Placeholder base EXP gain

  // --- Public Functions ---

  FUNCTION can_use_staff(unit, staff_item, target_tile_or_unit): BOOLEAN
    // Checks if the unit can use the staff on the target
    // TDD Anchor: test_can_use_staff_rank_check
    // TDD Anchor: test_can_use_staff_durability_check
    // TDD Anchor: test_can_use_staff_target_validity
    // TDD Anchor: test_can_use_staff_range_check
    // TDD Anchor: test_can_use_staff_silenced_check

    IF unit IS NULL OR staff_item IS NULL OR staff_item.type != "STAFF" THEN RETURN FALSE
    IF UnitSystem.get_weapon_rank(unit, "STAFF") < ItemSystem.get_required_rank(staff_item) THEN RETURN FALSE
    IF ItemSystem.get_current_durability(staff_item) <= 0 THEN RETURN FALSE
    IF StatusEffectsSystem.has_status(unit, "SILENCE") THEN RETURN FALSE
    // Add checks for other conditions preventing staff use (e.g., Berserk?)

    valid_targets = get_valid_targets(unit, staff_item)
    IF target_tile_or_unit NOT IN valid_targets THEN RETURN FALSE

    RETURN TRUE
  END FUNCTION

  FUNCTION get_staff_range(unit, staff_item): (min_range, max_range)
    // Calculates the actual min/max range based on staff type and user stats
    // TDD Anchor: test_get_staff_range_fixed
    // TDD Anchor: test_get_staff_range_mag_div_2
    // TDD Anchor: test_get_staff_range_user_mag

    min_r = staff_item.range_min
    max_r = staff_item.range_max // Default to fixed value

    SWITCH staff_item.range_type
      CASE "MAG_DIV_2":
        max_r = floor(UnitSystem.get_stat(unit, "MAG") / 2)
      CASE "USER_MAG":
        max_r = UnitSystem.get_stat(unit, "MAG")
      CASE "GLOBAL":
        max_r = 99 // Or map dimensions
      // CASE "FIXED": // Already handled by default
    END SWITCH

    // Ensure min range isn't greater than max range
    IF min_r > max_r THEN min_r = max_r

    RETURN (min_r, max_r)
  END FUNCTION

  FUNCTION get_valid_targets(unit, staff_item): LIST[Tile | Unit | Item]
    // Determines all valid targets (tiles, units, or items) for a staff
    // TDD Anchor: test_get_valid_targets_heal_staff_ally_only
    // TDD Anchor: test_get_valid_targets_status_staff_enemy_only_los
    // TDD Anchor: test_get_valid_targets_warp_staff_ally_tile
    // TDD Anchor: test_get_valid_targets_rescue_staff_ally_unit
    // TDD Anchor: test_get_valid_targets_restore_staff_ally_status
    // TDD Anchor: test_get_valid_targets_torch_staff_tile
    // TDD Anchor: test_get_valid_targets_repair_staff_item

    valid_targets = []
    user_pos = UnitSystem.get_position(unit)
    (min_range, max_range) = get_staff_range(unit, staff_item)

    potential_target_coordinates = MapSystem.get_tiles_in_range(user_pos, min_range, max_range)

    FOR coord IN potential_target_coordinates
      target_unit = MapSystem.get_unit_at(coord)
      target_item = NULL // For Repair staff

      // --- Check Line of Sight (LoS) ---
      // Required for most non-adjacent targets, except maybe global range staves?
      // Heal/Restore are often adjacent only (Range 1) or Mag/2 (Physic), requiring LoS.
      // Status staves (Sleep, Silence, Berserk) require LoS.
      // Warp/Rescue target a unit and a destination tile; LoS needed for unit, maybe not tile?
      // Torch targets a tile, LoS likely not needed for the tile itself.
      // Let's assume LoS is needed unless range is 0 or 1, or target is TILE.
      needs_los = TRUE
      IF min_range <= 1 AND MapSystem.get_distance(user_pos, coord) <= 1 THEN needs_los = FALSE
      IF staff_item.target_type == "TILE" THEN needs_los = FALSE
      IF staff_item.range_type == "GLOBAL" THEN needs_los = FALSE // Assume global ignores LoS

      IF needs_los AND NOT MapSystem.has_line_of_sight(user_pos, coord) THEN CONTINUE // Skip if LoS blocked

      // --- Check Target Type ---
      SWITCH staff_item.target_type
        CASE "ALLY":
          IF target_unit IS NOT NULL AND UnitSystem.is_ally(unit, target_unit) THEN
            // Additional checks for specific effects (e.g., Heal needs damaged ally)
            IF staff_item.effect_type == "HEAL" AND UnitSystem.is_at_max_hp(target_unit) THEN CONTINUE
            IF staff_item.effect_type == "STATUS_CURE" AND NOT StatusEffectsSystem.has_negative_status(target_unit) THEN CONTINUE
            // Add Rescue specific checks (Con?) if Rescue targets unit directly
            valid_targets.append(target_unit)
          END IF
        CASE "ENEMY":
          IF target_unit IS NOT NULL AND UnitSystem.is_enemy(unit, target_unit) THEN
            // Add checks for specific effects (e.g., status immunity?)
            valid_targets.append(target_unit)
          END IF
        CASE "TILE":
          // Check if tile is valid for the effect (e.g., Warp needs empty, valid terrain)
          IF MapSystem.is_valid_tile(coord) AND target_unit IS NULL THEN
             // Warp might need additional checks based on destination terrain type
             valid_targets.append(MapSystem.get_tile(coord))
          END IF
        CASE "SELF":
          IF coord == user_pos THEN
            valid_targets.append(unit)
          END IF
        CASE "ITEM":
           // For Repair staff - check adjacent allies' inventories
           // This logic is more complex, might need helper
           // Simplified: Check own inventory for now
           FOR item IN UnitSystem.get_inventory(unit)
              IF ItemSystem.can_be_repaired(item) THEN
                 // Need a way to target specific items. Maybe list repairable items?
                 // For now, assume targeting the unit implies choosing item later.
                 IF coord == user_pos THEN valid_targets.append(unit) // Target self to repair own item
                 BREAK
              END IF
           END FOR
           // TODO: Extend to check adjacent allies for Repair
      END SWITCH
    END FOR

    RETURN unique(valid_targets) // Ensure no duplicates
  END FUNCTION

  FUNCTION calculate_staff_hit_chance(user, staff_item): INTEGER
    // Calculates hit chance based on Thracia formula: Base + 4*Skill
    // TDD Anchor: test_calculate_staff_hit_chance_standard
    // TDD Anchor: test_calculate_staff_hit_chance_torch
    // TDD Anchor: test_calculate_staff_hit_chance_capped_at_99

    IF staff_item.base_hit IS NULL THEN RETURN 100 // Auto-hit staves like Heal

    base_hit = staff_item.base_hit
    user_skill = UnitSystem.get_stat(user, "SKL")

    hit_chance = base_hit + (4 * user_skill)

    // Apply caps (1% to 99% as per research.md line 191, 195)
    hit_chance = max(1, hit_chance)
    hit_chance = min(99, hit_chance)

    RETURN hit_chance
  END FUNCTION

  FUNCTION use_staff(user, staff_item, target): BOOLEAN
    // Executes the staff usage, consuming resources and applying effects.
    // 'target' can be a Unit, Tile, or Item depending on the staff.
    // TDD Anchor: test_use_staff_success_flow
    // TDD Anchor: test_use_staff_failure_invalid_target
    // TDD Anchor: test_use_staff_failure_no_durability
    // TDD Anchor: test_use_staff_consumes_action
    // TDD Anchor: test_use_staff_consumes_durability
    // TDD Anchor: test_use_staff_adds_correct_fatigue
    // TDD Anchor: test_use_staff_grants_wexp
    // TDD Anchor: test_use_staff_grants_exp
    // TDD Anchor: test_use_staff_miss_status_effect

    IF NOT can_use_staff(user, staff_item, target) THEN
      // UI Feedback: Cannot use staff / Invalid target
      RETURN FALSE
    END IF

    // --- Consume Resources ---
    ActionSystem.consume_action(user)
    ItemSystem.decrease_durability(staff_item, 1)
    fatigue_gain = calculate_fatigue_cost(staff_item)
    UnitSystem.add_fatigue(user, fatigue_gain)

    // --- Check Hit Chance (if applicable) ---
    hit_chance = calculate_staff_hit_chance(user, staff_item)
    is_hit = TRUE
    IF hit_chance < 100 THEN
      roll = random_integer(1, 100) // Thracia uses 1 RN
      IF roll > hit_chance THEN
        is_hit = FALSE
        // UI Feedback: Staff missed!
      END IF
    END IF

    // --- Apply Effect (if hit or auto-hit) ---
    success = FALSE
    IF is_hit THEN
      success = apply_staff_effect(user, staff_item, target)
      IF success THEN
         // UI Feedback: Staff effect applied! (e.g., Healed X HP, Inflicted Sleep!)
      ELSE
         // UI Feedback: Staff effect failed? (e.g., Target immune?)
      END IF
    END IF

    // --- Grant Experience (only on successful application?) ---
    // Research.md doesn't specify if EXP/WEXP is granted on miss. Assume success needed.
    IF success THEN
      exp_gain = calculate_staff_exp(user, staff_item)
      EXPSystem.grant_exp(user, exp_gain)

      wexp_gain = calculate_staff_wexp(staff_item)
      UnitSystem.add_wexp(user, staff_item.weapon_type, wexp_gain)
    END IF

    RETURN success // Return true if the effect was successfully applied
  END FUNCTION

  // --- Private Helper Functions ---

  FUNCTION calculate_fatigue_cost(staff_item): INTEGER
    // Calculates fatigue based on staff rank (Thracia rules)
    // TDD Anchor: test_calculate_fatigue_cost_by_rank
    rank = staff_item.required_rank
    IF staff_item.fatigue_cost_override IS NOT NULL THEN
      RETURN staff_item.fatigue_cost_override
    ELSE IF rank IN FATIGUE_COSTS THEN
      RETURN FATIGUE_COSTS[rank]
    ELSE
      RETURN 1 // Default for unknown ranks?
    END IF
  END FUNCTION

  FUNCTION calculate_staff_wexp(staff_item): INTEGER
    // Calculates WExp gain based on staff rank (Thracia rules)
    // TDD Anchor: test_calculate_staff_wexp_by_rank
    rank = staff_item.required_rank
    IF rank IN WEXP_GAINS THEN
      RETURN WEXP_GAINS[rank]
    ELSE
      RETURN 1 // Default for unknown ranks?
    END IF
  END FUNCTION

  FUNCTION calculate_staff_exp(user, staff_item): INTEGER
    // Calculates EXP gain for successful staff use.
    // Formula needs refinement - placeholder: Base + bonus for rank/effect complexity.
    // TDD Anchor: test_calculate_staff_exp_base
    // TDD Anchor: test_calculate_staff_exp_rank_bonus

    exp_gain = BASE_STAFF_EXP
    rank = staff_item.required_rank
    IF rank == "C" THEN exp_gain += 5
    IF rank == "B" THEN exp_gain += 8
    IF rank == "A" THEN exp_gain += 12
    // Add bonus for complex effects like Warp, Restore?
    IF staff_item.effect_type IN ["WARP", "RESCUE", "STATUS_CURE"] THEN exp_gain += 5

    // Consider level difference? Thracia EXP formula is complex. Keep simple for now.
    RETURN exp_gain
  END FUNCTION

  FUNCTION calculate_heal_amount(user, staff_item, target): INTEGER
    // Calculates HP restored by a healing staff
    // TDD Anchor: test_calculate_heal_amount_potency_only
    // TDD Anchor: test_calculate_heal_amount_potency_plus_mag
    // TDD Anchor: test_calculate_heal_amount_full_heal

    amount = 0
    SWITCH staff_item.heal_formula
      CASE "POTENCY_ONLY":
        amount = staff_item.base_potency
      CASE "POTENCY_PLUS_USER_MAG":
        amount = staff_item.base_potency + UnitSystem.get_stat(user, "MAG")
      CASE "FULL_HEAL":
        amount = UnitSystem.get_max_hp(target) - UnitSystem.get_current_hp(target)
    END SWITCH

    // Ensure healing doesn't exceed max HP deficit
    max_heal = UnitSystem.get_max_hp(target) - UnitSystem.get_current_hp(target)
    amount = min(amount, max_heal)
    amount = max(0, amount) // Cannot heal negative HP

    RETURN amount
  END FUNCTION

  FUNCTION apply_staff_effect(user, staff_item, target): BOOLEAN
    // Dispatches to specific effect functions based on staff type
    // TDD Anchor: test_apply_heal_effect_updates_hp
    // TDD Anchor: test_apply_status_inflict_adds_status
    // TDD Anchor: test_apply_status_cure_removes_status
    // TDD Anchor: test_apply_warp_moves_unit
    // TDD Anchor: test_apply_rescue_moves_unit
    // TDD Anchor: test_apply_torch_illuminates_map
    // TDD Anchor: test_apply_repair_restores_durability
    // TDD Anchor: test_apply_m_up_adds_temp_stat

    success = FALSE
    SWITCH staff_item.effect_type
      CASE "HEAL":
        IF TYPE(target) == Unit THEN
          heal_amount = calculate_heal_amount(user, staff_item, target)
          IF heal_amount > 0 THEN
            UnitSystem.heal_unit(target, heal_amount)
            success = TRUE
          END IF
        END IF

      CASE "STATUS_INFLICT":
        IF TYPE(target) == Unit THEN
          // Check immunity? (e.g., Nihil doesn't block status, but specific flags might)
          status = staff_item.status_inflicted
          StatusEffectsSystem.apply_status(target, status) // Assumes system handles duration (infinite in Thracia until cured)
          success = TRUE
        END IF

      CASE "STATUS_CURE":
        IF TYPE(target) == Unit THEN
          status_to_cure = staff_item.status_cured
          IF status_to_cure == "NEGATIVE" THEN
             StatusEffectsSystem.remove_negative_statuses(target) // Remove Poison, Sleep, Silence, Berserk
             success = TRUE
          ELSE IF status_to_cure == "PETRIFY" THEN
             // Only Kia staff cures Petrify
             IF staff_item.id == "KIA_STAFF" THEN // Assuming Kia Staff ID
                StatusEffectsSystem.remove_status(target, "PETRIFY")
                success = TRUE
             END IF
          ELSE
             StatusEffectsSystem.remove_status(target, status_to_cure)
             success = TRUE
          END IF
        END IF

      CASE "WARP":
        // Target should be the destination TILE, user selects unit to warp separately?
        // Or target is the UNIT, and user selects destination TILE? Let's assume target is UNIT.
        IF TYPE(target) == Unit THEN
           // Requires UI interaction to select destination tile
           destination_tile = get_warp_destination_from_ui(user, staff_item) // Placeholder UI call
           IF destination_tile IS NOT NULL AND MapSystem.is_valid_tile(destination_tile.coord) AND MapSystem.get_unit_at(destination_tile.coord) IS NULL THEN
              MapSystem.move_unit(target, destination_tile.coord)
              success = TRUE
           END IF
        END IF

      CASE "RESCUE":
        // Target is the ALLY unit to rescue. Destination is adjacent to USER.
        IF TYPE(target) == Unit THEN
           // Requires UI interaction to select destination tile adjacent to user
           destination_tile = get_rescue_destination_from_ui(user) // Placeholder UI call
           IF destination_tile IS NOT NULL AND MapSystem.is_valid_tile(destination_tile.coord) AND MapSystem.get_unit_at(destination_tile.coord) IS NULL THEN
              MapSystem.move_unit(target, destination_tile.coord)
              success = TRUE
           END IF
        END IF

      CASE "UTILITY":
        SWITCH staff_item.utility_effect
          CASE "ILLUMINATE": // Torch Staff
            IF TYPE(target) == Tile THEN
              radius = staff_item.utility_potency
              duration = staff_item.utility_duration
              MapSystem.illuminate_area(target.coord, radius, duration)
              success = TRUE
            END IF
          CASE "REPAIR": // Hammerne Staff
            // Target is the UNIT whose item needs repair. Requires UI to select item.
            IF TYPE(target) == Unit THEN
               item_to_repair = get_item_to_repair_from_ui(target) // Placeholder UI call
               IF item_to_repair IS NOT NULL THEN
                  ItemSystem.repair_item(item_to_repair)
                  success = TRUE
               END IF
            END IF
          CASE "UNLOCK": // Unlock Staff
            IF TYPE(target) == Tile AND MapSystem.is_door(target.coord) OR MapSystem.is_chest(target.coord) THEN
               MapSystem.unlock_tile(target.coord)
               success = TRUE
            END IF
          CASE "M_UP": // M Up Staff
             IF TYPE(target) == Unit THEN
                bonus = staff_item.utility_potency
                duration = staff_item.utility_duration // Needs decay mechanism
                StatusEffectsSystem.apply_temporary_stat_boost(target, "MAG", bonus, duration, decay_rate=1)
                success = TRUE
             END IF
          // Add other utilities like Barrier, etc.
        END SWITCH
    END SWITCH

    RETURN success
  END FUNCTION

END MODULE
```

## 5. AI Considerations

The `AISystem` needs to incorporate logic for AI units (especially healers and status users) to utilize staves effectively.

- **Healer AI:**
    - **Priority:** Prioritize healing allies with low HP. The lower the HP percentage, the higher the priority.
    - **Staff Choice:** Use the most appropriate healing staff based on range and required healing amount (e.g., use Heal for adjacent, Physic for distant; use Mend if Heal isn't enough).
    - **Positioning:** Move within range of the target ally to perform the heal. Consider safety – avoid moving into enemy attack range if possible.
    - **Self-Heal:** AI should consider using healing items (Vulnerary) or staves on themselves if injured.
    - **TDD Anchor:** `test_ai_healer_prioritizes_lowest_hp_ally`
    - **TDD Anchor:** `test_ai_healer_uses_physic_for_distant_ally`
    - **TDD Anchor:** `test_ai_healer_avoids_danger_when_healing`

- **Status Staff AI:**
    - **Targeting:** Identify high-priority enemy targets based on the status effect:
        - `Silence`: Target enemy magic users (Mages, Priests, Bishops). Prioritize those with dangerous spells or high Mag.
        - `Sleep`: Target dangerous physical threats (high Str/Spd units, bosses) or units blocking strategic points.
        - `Berserk`: Target powerful enemies who are likely to damage their own allies significantly. Prioritize enemies near other enemies.
    - **Hit Chance:** Consider the staff hit chance (`calculate_staff_hit_chance`). May attempt even with lower hit rates if the target is critical. Thracia AI is known to be aggressive with status staves.
    - **Positioning:** Move within range and LoS of the target.
    - **TDD Anchor:** `test_ai_silence_targets_enemy_mage`
    - **TDD Anchor:** `test_ai_sleep_targets_high_threat_enemy`
    - **TDD Anchor:** `test_ai_berserk_targets_enemy_near_allies`

- **Utility Staff AI:**
    - `Restore`: Use on allies afflicted with negative status effects (Poison, Sleep, Silence, Berserk). High priority, especially for Sleep/Berserk.
    - `Warp/Rescue`: AI might use these for strategic repositioning, escaping, or bringing key units forward, but this requires complex tactical evaluation. Could be simplified initially (e.g., rescue a low-HP ally out of danger).
    - `Torch`: Use in Fog of War maps to reveal areas, potentially prioritizing areas with suspected enemies or objectives.
    - **TDD Anchor:** `test_ai_restore_cures_sleeping_ally`
    - **TDD Anchor:** `test_ai_torch_used_in_fog_of_war`

## 6. Integration Points

- **`ItemSystem`**: Provides staff data, manages durability consumption, handles repair effects.
- **`UnitSystem`**: Provides user stats (Mag, Skl) for calculations, target stats (HP, Con), applies healing, manages fatigue gain, manages WExp gain.
- **`StatusEffectsSystem`**: Applies inflicted statuses, removes cured statuses, checks for Silence/Berserk on user. Handles status duration (infinite until cured).
- **`MapSystem`**: Provides unit/tile locations, calculates distance, checks LoS, executes unit movement for Warp/Rescue, handles illumination for Torch, handles unlocking for Unlock staff.
- **`ActionSystem`**: Consumes the unit's action upon successful or attempted staff use.
- **`EXPSystem`**: Grants EXP upon successful staff application.
- **`AISystem`**: Implements the logic for AI units deciding when, where, and how to use staves.
- **`UI`**: Displays valid targets, staff range, hit chance (if applicable), prompts for target/destination selection (Warp/Rescue/Repair), provides feedback on success/failure/miss.

## 7. Open Questions / Future Considerations

- **EXP Formula:** Refine the EXP gain formula. Is it fixed, based on staff rank, effect type, target level, or a combination? Thracia's base EXP might be fixed per staff type.
- **WExp Formula:** Confirm WExp gain per rank matches `research.md`.
- **Repair Staff Targeting:** How should targeting items in an adjacent ally's inventory work via the UI?
- **Warp/Rescue UI:** How is the destination tile selected?
- **Status Immunity:** Are there specific units or items (besides Kia Staff for Petrify) that grant status immunity? Research.md suggests Saias might have temporary immunity.
- **Staff Effectiveness vs Magic:** Double-check if target Magic *ever* influences staff hit/effect chance in Thracia. Research.md suggests it doesn't for hit chance, but needs confirmation for effect application (e.g., does high Mag reduce chance of *being* silenced?). Assume no effect for now based on current info.
- **Canto Interaction:** Confirm staff use prevents Canto movement (`research.md` line 51). The `ActionSystem` should flag this.