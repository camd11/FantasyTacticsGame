# Ballista System Specification

## 1. Overview
This document outlines the design for the Ballista system, stationary siege weapons found on certain maps. Based primarily on Fire Emblem: Thracia 776 mechanics.

## 2. Data Structures

### 2.1. Ballista Definition
```pseudocode
CLASS BallistaType:
    id: STRING              // Unique identifier (e.g., "ballista_regular", "ballista_iron", "ballista_killer")
    display_name: STRING    // Name shown in UI (e.g., "Ballista", "Iron Ballista")
    sprite_id: STRING       // Visual representation on map (base sprite)
    occupied_sprite_id: STRING // Sprite when manned (optional, could be handled by layering unit sprite)
    weapon_id: STRING       // Reference to the associated BallistaWeapon data
    allowed_classes: LIST<STRING> // Classes that can operate this ballista (e.g., ["Archer", "Sniper"])
    // TDD_ANCHOR: test_ballista_type_data_validation - Ensure required fields exist and lists are not empty.
```

### 2.2. Ballista Weapon Data (Linked from BallistaType)
```pseudocode
CLASS BallistaWeapon:
    id: STRING              // Matches BallistaType.weapon_id
    might: INTEGER          // Base attack power
    hit: INTEGER            // Base accuracy
    crit: INTEGER           // Base critical chance (often 0 for regular ballistae)
    min_range: INTEGER      // Minimum attack range (e.g., 3)
    max_range: INTEGER      // Maximum attack range (e.g., 10, 15 for Iron)
    durability: INTEGER     // Number of uses per map
    effectiveness: MAP<UnitProperty, Multiplier> // e.g., {UnitProperty.IS_FLYING: 3.0} - Use properties/tags instead of types for flexibility.
    // TDD_ANCHOR: test_ballista_weapon_data_validation - Ensure ranges are valid (min <= max), stats are non-negative.
```

### 2.3. Map Object: Ballista Instance
```pseudocode
CLASS BallistaInstance (inherits MapObject):
    position: TUPLE<INTEGER, INTEGER> // (x, y) coordinates
    ballista_type_id: STRING          // Reference to BallistaType
    current_durability: INTEGER       // Remaining uses for this instance
    occupying_unit_id: OPTIONAL<STRING> // ID of the unit currently manning the ballista
    is_enabled: BOOLEAN               // True if operational (has durability and potentially an operator), False if disabled.
    // TDD_ANCHOR: test_ballista_instance_initialization - Verify state matches scenario data.
    // TDD_ANCHOR: test_ballista_instance_state_changes - Test enabling/disabling, occupant assignment.
```

### 2.4. Unit Component: Ballista User State
```pseudocode
COMPONENT BallistaUserState (added to Units):
    is_manning_ballista: BOOLEAN // True if currently on a ballista tile AND eligible
    ballista_instance_id: OPTIONAL<STRING> // ID of the BallistaInstance they are manning
    // TDD_ANCHOR: test_unit_ballista_state_toggle - Ensure component added/removed correctly.
```

## 3. Map Representation

*   Ballistae are represented as specific `MapObject` instances (`BallistaInstance`) placed on the map during scenario setup. They are essentially interactive terrain features.
*   They occupy a single tile. The tile itself might have specific terrain properties (e.g., high defense, impassable for non-operators).
*   The `BallistaInstance` stores its type (`ballista_type_id`), remaining `current_durability`, and whether it's currently occupied (`occupying_unit_id`) and `is_enabled`.
*   Different `BallistaType` definitions (e.g., "ballista_regular", "ballista_iron", "ballista_killer", "ballista_poison") allow for variations with distinct stats, ranges, sprites, and potentially effects (like poison).

```pseudocode
FUNCTION load_map_scenario(scenario_data):
    // ... load terrain, units ...
    FOR ballista_data IN scenario_data.ballistae:
        ballista_type = GET_BALLISTA_TYPE(ballista_data.type_id) // Fetch definition
        IF ballista_type IS NULL:
            LOG_ERROR("Invalid ballista type in scenario: " + ballista_data.type_id)
            CONTINUE

        ballista_weapon = GET_BALLISTA_WEAPON(ballista_type.weapon_id)
        IF ballista_weapon IS NULL:
            LOG_ERROR("Invalid weapon ID for ballista type: " + ballista_type.weapon_id)
            CONTINUE
            
        instance = CREATE BallistaInstance(
            position = ballista_data.position,
            ballista_type_id = ballista_data.type_id,
            current_durability = ballista_weapon.durability,
            occupying_unit_id = ballista_data.initial_occupant_id, // Can be None
            is_enabled = (ballista_data.initial_occupant_id IS NOT None AND ballista_weapon.durability > 0)
        )
        MapSystem.add_map_object(instance)
        
        // Assign initial occupant state if provided
        IF instance.occupying_unit_id IS NOT None:
            unit = UnitSystem.get_unit(instance.occupying_unit_id)
            IF unit IS NOT None AND unit.class IN ballista_type.allowed_classes:
                unit.add_component(BallistaUserState(is_manning_ballista=True, ballista_instance_id=instance.id))
                unit.set_immobile(True) // Unit cannot move while manning
                // TDD_ANCHOR: test_map_load_assigns_initial_occupant_state - Verify unit has component and is immobile.
            ELSE:
                LOG_WARNING("Initial occupant " + instance.occupying_unit_id + " invalid or wrong class for ballista " + instance.id)
                instance.occupying_unit_id = None // Clear invalid occupant
                instance.is_enabled = False

        // TDD_ANCHOR: test_map_load_places_ballista - Check instance exists at correct position.
```

## 4. Usage Conditions

*   **Eligibility:** Only units whose class is listed in the `BallistaType.allowed_classes` (e.g., "Archer", "Sniper") can operate a ballista.
*   **Activation:** A unit uses a ballista by being on the `BallistaInstance` tile, belonging to an allowed class, and the ballista being `is_enabled`. The standard "Attack" command becomes contextually available as "Fire Ballista".
*   **State:** When an eligible unit occupies an enabled ballista:
    *   Their `BallistaUserState` component is activated/updated.
    *   They become immobile (`unit.set_immobile(True)`).
    *   Their standard attack options are replaced by the ballista's attack.
*   **Player Usage:** Per Thracia 776, player units cannot use enemy ballistae. This implementation assumes ballistae are primarily enemy tools. If player usage is desired, eligibility checks and action availability need to be adjusted for player units. Capturing an operator disables the ballista; players cannot simply hop on.

```pseudocode
FUNCTION check_unit_can_use_ballista(unit, ballista_instance):
    IF unit IS None OR ballista_instance IS None:
        RETURN False
    ballista_type = GET_BALLISTA_TYPE(ballista_instance.ballista_type_id)
    RETURN unit.class IN ballista_type.allowed_classes
    // TDD_ANCHOR: test_check_unit_can_use_ballista_allowed_class - Unit with allowed class returns True.
    // TDD_ANCHOR: test_check_unit_can_use_ballista_disallowed_class - Unit with disallowed class returns False.
    // TDD_ANCHOR: test_check_unit_can_use_ballista_null_input - Handles null unit/instance gracefully.

// Note: Entering/Leaving logic might be handled by general map movement validation.
// A unit shouldn't be able to move onto an occupied tile. If they defeat the occupant,
// the tile becomes empty, but the ballista is disabled (see Special Cases).
// If player usage is allowed, specific logic for moving onto an *empty* enabled ballista is needed.

FUNCTION get_unit_available_actions(unit):
    actions = // ... standard actions (Move, Item, Wait, etc.) ...
    
    // Check if unit is on a ballista tile
    ballista_instance = MapSystem.get_object_at(unit.position, type=BallistaInstance)
    
    IF ballista_instance IS NOT None AND ballista_instance.occupying_unit_id == unit.id AND ballista_instance.is_enabled:
        // Unit is manning an active ballista
        IF ballista_instance.current_durability > 0:
            // Replace standard Attack with Fire Ballista
            REMOVE "Attack" FROM actions IF present
            ADD Action("Fire Ballista", range_func=get_ballista_attack_range, target_func=get_valid_ballista_targets) TO actions
        ELSE:
             REMOVE "Attack" FROM actions IF present // Cannot fire if out of ammo
             
        REMOVE "Move" FROM actions // Cannot move while manning
        REMOVE "Trade" FROM actions // Typically cannot trade while manning siege
        REMOVE "Rescue" FROM actions // Typically cannot rescue while manning siege
        // ... potentially remove other actions incompatible with being stationary ...
        
        // Add "Dismount Ballista" action? Optional, allows voluntarily leaving.
        // ADD Action("Dismount Ballista") TO actions 
        
    RETURN actions
    // TDD_ANCHOR: test_get_actions_on_ballista_shows_fire - Correct action shown if durability > 0.
    // TDD_ANCHOR: test_get_actions_on_ballista_hides_move_trade_rescue - Immobile actions hidden.
    // TDD_ANCHOR: test_get_actions_on_empty_ballista_hides_fire - No fire action if durability is 0.
    // TDD_ANCHOR: test_get_actions_not_on_ballista - Standard actions shown if not on ballista.
    // TDD_ANCHOR: test_get_actions_on_disabled_ballista - No fire action if ballista disabled.
```

## 5. Targeting and Range

*   **Range Calculation:** Determined strictly by the `min_range` and `max_range` of the `BallistaWeapon` associated with the `BallistaInstance`. Range is calculated from the ballista's tile (`ballista_instance.position`).
*   **Target Types:** Can target both ground and air units within the calculated range and Line of Sight.
*   **Line of Sight (LoS):** Standard LoS rules apply. Obstacles like high walls or peaks block LoS. Forests might obscure LoS depending on game rules.
*   **Display:** When selecting a unit on a ballista, the attackable range (visualized, e.g., red tiles) must reflect the ballista's specific min/max range and LoS constraints.

```pseudocode
FUNCTION get_ballista_attack_range(ballista_instance):
    IF ballista_instance IS None OR NOT ballista_instance.is_enabled OR ballista_instance.current_durability <= 0:
        RETURN empty_set // Cannot attack
    
    ballista_type = GET_BALLISTA_TYPE(ballista_instance.ballista_type_id)
    weapon = GET_BALLISTA_WEAPON(ballista_type.weapon_id)
    
    valid_tiles = MapSystem.calculate_tiles_in_range(
        origin = ballista_instance.position,
        min_range = weapon.min_range,
        max_range = weapon.max_range,
        map_data = MapSystem.current_map,
        los_checker = MapSystem.get_los_checker() // Use standard LoS function
    )
    RETURN valid_tiles
    // TDD_ANCHOR: test_get_ballista_range_calculation_min_max - Correct tiles highlighted for min/max.
    // TDD_ANCHOR: test_get_ballista_range_respects_los - Blocked tiles are excluded.
    // TDD_ANCHOR: test_get_ballista_range_disabled_or_empty - Returns empty set if cannot fire.

FUNCTION get_valid_ballista_targets(unit, ballista_instance):
    attack_range_tiles = get_ballista_attack_range(ballista_instance)
    IF IS_EMPTY(attack_range_tiles):
        RETURN []

    potential_targets = UnitSystem.get_units_on_tiles(attack_range_tiles)
    
    valid_targets = []
    FOR target IN potential_targets:
        // Check faction hostility and if target is attackable (e.g., not phased out)
        IF UnitSystem.are_hostile(unit, target) AND target.is_attackable():
             // Check Line of Sight specifically to the target tile (redundant if range calc includes it, but good practice)
             IF MapSystem.has_line_of_sight(ballista_instance.position, target.position):
                valid_targets.append(target)
            
    RETURN valid_targets
    // TDD_ANCHOR: test_get_valid_ballista_targets_ground_and_air - Finds both types.
    // TDD_ANCHOR: test_get_valid_ballista_targets_excludes_allies_neutrals - Ignores non-hostile units.
    // TDD_ANCHOR: test_get_valid_ballista_targets_respects_range_and_los - Only units in valid range/LoS returned.
    // TDD_ANCHOR: test_get_valid_ballista_targets_empty_if_disabled - Returns empty list if ballista cannot fire.
```

## 6. Combat Calculation

*   **Initiation:** Occurs when the unit controlling the ballista executes the "Fire Ballista" action against a valid target.
*   **Attack Power (Atk):** Uses the `BallistaWeapon.might`. The operator's personal Str/Mag does **not** contribute. `Atk = BallistaWeapon.might`.
*   **Accuracy (Hit):** Base accuracy comes from `BallistaWeapon.hit`. The operator's stats **do** contribute: `Hit = BallistaWeapon.hit + (Operator.Skill * 2) + Operator.Luck + Bonuses`. Bonuses include Support, Leadership, Charisma, relevant operator skills (e.g., `Sure Shot`). Target's Avoid is subtracted as usual.
*   **Critical (Crit):** Base crit from `BallistaWeapon.crit`. Operator's Skill contributes: `Crit = BallistaWeapon.crit + Operator.Skill + Bonuses`. Bonuses include Support, relevant operator skills (e.g., `Crit+`). Target's Crit Evade is subtracted.
*   **Damage:** `Damage = MAX(0, (Ballista_Atk * EffectivenessMultiplier) - Target_Defense)`. Defense is the target's physical defense (Def + Terrain Def).
*   **Effectiveness:** Applies multiplier from `BallistaWeapon.effectiveness` based on target properties (e.g., x3 vs units with `IS_FLYING` property).
*   **Weapon Triangle:** Does not apply to ballista attacks.
*   **Operator Skills:** Combat skills of the operator that affect Hit/Crit (e.g., `Sure Shot`, `Crit+`) **do** apply. Skills that trigger additional actions or modify personal combat (e.g., `Adept`, `Wrath`, `Luna`, `Sol`, `Pavise`) likely do **not** apply to the ballista attack itself. PCC does **not** apply.
*   **Counterattack:** Ballistae typically attack from outside standard counter range. If the target *can* counter (e.g., another ballista, long-range magic), standard counter-attack rules apply after the ballista shot resolves.
*   **Durability:** `BallistaInstance.current_durability` is decremented by 1 after the attack is executed (whether it hits or misses). If durability reaches 0, the `BallistaInstance` is disabled (`is_enabled = False`).
*   **Status Effects:** Some ballista types (e.g., Poison Ballista) might apply status effects on hit. This requires additional data in `BallistaWeapon` and logic in `execute_ballista_attack`.

```pseudocode
FUNCTION calculate_ballista_combat_preview(attacker_unit, target_unit, ballista_instance):
    ballista_type = GET_BALLISTA_TYPE(ballista_instance.ballista_type_id)
    ballista_weapon = GET_BALLISTA_WEAPON(ballista_type.weapon_id)
    
    // --- Attacker Calculation ---
    ballista_base_atk = ballista_weapon.might 
    
    // Apply effectiveness
    effectiveness_multiplier = CombatSystem.get_effectiveness_multiplier(ballista_weapon.effectiveness, target_unit)
    attacker_effective_atk = ballista_base_atk * effectiveness_multiplier

    // Calculate Hit Rate
    hit_bonuses = CombatSystem.get_combat_stat_bonuses(attacker_unit, target_unit, stat="hit", context="ballista_attack") // Includes Support, Leadership, Skills etc.
    attacker_hit_rate = ballista_weapon.hit + (attacker_unit.stats.skl * 2) + attacker_unit.stats.luk + hit_bonuses
    
    // Calculate Crit Rate
    crit_bonuses = CombatSystem.get_combat_stat_bonuses(attacker_unit, target_unit, stat="crit", context="ballista_attack") // Includes Support, Skills etc.
    attacker_crit_rate = ballista_weapon.crit + attacker_unit.stats.skl + crit_bonuses

    // --- Defender Calculation ---
    target_avoid = CombatSystem.calculate_avoid(target_unit, attacker_unit, context="ballista_defense") // Standard avoid calculation
    target_crit_evade = CombatSystem.calculate_crit_evade(target_unit, attacker_unit, context="ballista_defense") // Standard crit evade
    target_defense = CombatSystem.calculate_defense(target_unit, attack_type="physical", context="ballista_defense") // Ballistae are physical

    // --- Final Battle Preview ---
    final_hit = CLAMP(attacker_hit_rate - target_avoid, 1, 99) // Apply 1-99 cap
    final_crit = CLAMP(attacker_crit_rate - target_crit_evade, 0, 100) // Apply 0-100 cap
    
    potential_damage = MAX(0, attacker_effective_atk - target_defense)
    
    preview = {
        "attacker_unit_id": attacker_unit.id,
        "defender_unit_id": target_unit.id,
        "ballista_instance_id": ballista_instance.id,
        "attacker_hp": attacker_unit.stats.current_hp,
        "defender_hp": target_unit.stats.current_hp,
        "attacker_potential_dmg": potential_damage,
        "attacker_hit": final_hit,
        "attacker_crit": final_crit,
        "can_defender_counter": CombatSystem.can_counter(target_unit, attacker_unit, distance=MapSystem.distance(attacker_unit.position, target_unit.position)),
        // Include counter-attack preview if defender can counter
        "defender_potential_dmg": 0, // Calculate if can_counter
        "defender_hit": 0,           // Calculate if can_counter
        "defender_crit": 0           // Calculate if can_counter
    }
    // TDD_ANCHOR: test_ballista_preview_damage_calc - Verify base damage, effectiveness, defense reduction.
    // TDD_ANCHOR: test_ballista_preview_hit_calc - Verify base hit, operator stats, bonuses, avoid reduction, caps.
    // TDD_ANCHOR: test_ballista_preview_crit_calc - Verify base crit, operator skill, bonuses, crit evade reduction, caps.
    // TDD_ANCHOR: test_ballista_preview_effectiveness_applied - Check multiplier vs flying targets.
    // TDD_ANCHOR: test_ballista_preview_operator_skills_affect_stats - Check skills like Sure Shot modify preview.
    // TDD_ANCHOR: test_ballista_preview_counter_check - Verify can_counter flag is correct based on range/target weapon.
    RETURN preview

FUNCTION execute_ballista_attack(attacker_unit, target_unit, ballista_instance):
    preview = calculate_ballista_combat_preview(attacker_unit, target_unit, ballista_instance)
    
    // 1. Decrement durability FIRST
    ballista_instance.current_durability -= 1
    LOG_COMBAT(f"Ballista {ballista_instance.id} durability now {ballista_instance.current_durability}")
    IF ballista_instance.current_durability <= 0:
        ballista_instance.is_enabled = False
        LOG_COMBAT(f"Ballista {ballista_instance.id} disabled (out of ammo).")
        // TDD_ANCHOR: test_ballista_attack_disables_on_zero_durability - Check is_enabled is false after last shot.

    // 2. Perform Attacker's Strike
    CombatSystem.display_attack_animation(attacker_unit, target_unit, weapon_type="ballista")
    did_hit = Random.roll_success(preview.attacker_hit)
    
    IF did_hit:
        is_crit = Random.roll_success(preview.attacker_crit)
        damage_dealt = preview.attacker_potential_dmg * (2 IF is_crit ELSE 1)
        
        LOG_COMBAT(f"Ballista hits target {target_unit.id} for {damage_dealt} damage" + (" (CRITICAL!)" IF is_crit ELSE ""))
        CombatSystem.apply_damage(target_unit, damage_dealt)
        CombatSystem.display_hit_effect(target_unit, damage_dealt, is_crit)

        // Apply status effects if any (e.g., Poison Ballista)
        // status_to_apply = GET_BALLISTA_WEAPON(GET_BALLISTA_TYPE(ballista_instance.ballista_type_id).weapon_id).status_effect
        // IF status_to_apply IS NOT None:
        //     StatusSystem.apply_status(target_unit, status_to_apply)
        //     // TDD_ANCHOR: test_poison_ballista_applies_status_on_hit

        // Check if target defeated
        IF target_unit.stats.current_hp <= 0:
             LOG_COMBAT(f"Target {target_unit.id} defeated by ballista.")
             CombatSystem.handle_unit_defeated(target_unit, attacker_unit) // Grant EXP, handle removal
             // TDD_ANCHOR: test_ballista_attack_grants_exp_on_kill - Verify EXP gain.
             ActionSystem.mark_unit_action_complete(attacker_unit) // Action ends after attack
             RETURN // No counter-attack if target defeated
        // TDD_ANCHOR: test_ballista_attack_deals_damage_on_hit - Check target HP reduced.
        // TDD_ANCHOR: test_ballista_attack_deals_crit_damage - Check damage doubled on crit.
    ELSE:
        // Attack missed
        LOG_COMBAT(f"Ballista misses target {target_unit.id}.")
        CombatSystem.display_miss_effect(target_unit)
        // TDD_ANCHOR: test_ballista_attack_misses - Check target HP unchanged on miss.

    // 3. Handle Counter-Attack (if applicable)
    IF preview.can_defender_counter AND target_unit.stats.current_hp > 0:
        LOG_COMBAT(f"Target {target_unit.id} can counter-attack.")
        CombatSystem.execute_standard_combat_round(target_unit, attacker_unit, is_counter=True) // Execute the counter portion
        // TDD_ANCHOR: test_ballista_target_can_counter - Verify counter logic triggers if in range.
        
    // 4. Mark attacker as having acted
    ActionSystem.mark_unit_action_complete(attacker_unit)
```

## 7. Ammunition/Uses

*   Ballistae have finite uses per map instance, tracked by `BallistaInstance.current_durability`. Initial durability is set from `BallistaWeapon.durability`.
*   Each firing attempt (regardless of hit or miss) consumes 1 durability point.
*   When `current_durability` reaches 0, the `BallistaInstance` becomes disabled (`is_enabled = False`) and cannot be fired again during the current map.
*   There is no mechanism for reloading ballistae during a map in standard Fire Emblem gameplay.

```pseudocode
// Logic is integrated within:
// - load_map_scenario (initialization)
// - get_unit_available_actions (checks durability > 0 for action availability)
// - execute_ballista_attack (decrements durability, disables at 0)

// TDD_ANCHOR: test_ballista_durability_decrements_on_fire - Check durability reduces by 1 after firing.
// TDD_ANCHOR: test_ballista_cannot_fire_at_zero_durability - Check "Fire Ballista" action is unavailable/fails if durability is 0.
// TDD_ANCHOR: test_ballista_initial_durability_set_correctly - Check instance starts with weapon's durability.
```

## 8. AI Considerations

*   **Target Selection:** AI controlling a ballista follows specific priorities:
    1.  Identify all valid targets within range and LoS using `get_valid_ballista_targets`.
    2.  Strongly prioritize **Flying units** due to effectiveness. Calculate potential damage against them.
    3.  Among non-fliers (or if no fliers), prioritize targets the ballista can deal the most damage to, especially if it results in a kill (damage >= target current HP).
    4.  Factor in hit rate: Avoid targets with extremely low hit probability (<10-20%?) unless they are the only option or a very high-value target (like a flier).
    5.  May consider target value: Prioritize healers, dancers, lords, or other high-threat units if damage/hit outcomes are similar against multiple targets.
*   **Decision Logic:**
    *   If one or more valid targets exist, the AI unit will almost always choose to "Fire Ballista" as its action, selecting the target deemed best by the scoring logic.
    *   Since the unit is immobile, movement is not part of the decision process.
    *   The AI uses `calculate_ballista_combat_preview` to evaluate potential outcomes for each target.

```pseudocode
FUNCTION decide_ai_ballista_action(ai_unit):
    // Find the ballista this unit is manning
    ballista_instance = None
    IF ai_unit.has_component(BallistaUserState):
        state = ai_unit.get_component(BallistaUserState)
        IF state.is_manning_ballista:
            ballista_instance = MapSystem.get_object_by_id(state.ballista_instance_id)

    IF ballista_instance IS None OR NOT ballista_instance.is_enabled OR ballista_instance.current_durability <= 0:
        RETURN Action("Wait", reason="Ballista unusable") // Cannot fire

    valid_targets = get_valid_ballista_targets(ai_unit, ballista_instance)
    IF IS_EMPTY(valid_targets):
        RETURN Action("Wait", reason="No targets in range") // No targets

    best_target = None
    best_score = -infinity

    FOR target IN valid_targets:
        preview = calculate_ballista_combat_preview(ai_unit, target, ballista_instance)
        # Check if the attack is actually possible (hit > 0)
        if preview.attacker_hit > 0:
            is_flying = target.has_property("IS_FLYING") # Check target property/tag
            score = calculate_ai_ballista_target_score(preview, target, is_flying)
            
            LOG_AI_DEBUG(f"Target {target.id}: Score {score}, Dmg {preview.attacker_potential_dmg}, Hit {preview.attacker_hit}, Flying {is_flying}")

            IF score > best_score:
                best_score = score
                best_target = target

    IF best_target IS NOT None:
        LOG_AI(f"AI Unit {ai_unit.id} firing ballista at {best_target.id} (Score: {best_score})")
        RETURN Action("Fire Ballista", target=best_target)
    ELSE:
        LOG_AI(f"AI Unit {ai_unit.id} found no suitable ballista targets.")
        RETURN Action("Wait", reason="No suitable targets")
    // TDD_ANCHOR: test_ai_ballista_prioritizes_fliers - Flier target chosen over ground target with similar/better raw damage/hit.
    // TDD_ANCHOR: test_ai_ballista_prioritizes_killable_targets - Target that can be killed chosen over one that survives, even if damage is slightly lower.
    // TDD_ANCHOR: test_ai_ballista_prioritizes_high_damage - Target taking more damage chosen if other factors equal.
    // TDD_ANCHOR: test_ai_ballista_avoids_zero_hit_targets - Ignores targets if hit chance is 0 (or below threshold).
    // TDD_ANCHOR: test_ai_ballista_waits_if_no_valid_targets - Waits if list is empty or all targets have score <= -infinity.

FUNCTION calculate_ai_ballista_target_score(preview, target, is_flying):
    # Base score: Expected damage (Damage * Hit Chance)
    score = preview.attacker_potential_dmg * (preview.attacker_hit / 100.0) 
    
    # Bonus for securing a kill
    is_kill = (preview.attacker_potential_dmg >= target.stats.current_hp)
    IF is_kill:
        score += 50 // Significant bonus for a kill

    # Large bonus for targeting fliers (effectiveness)
    IF is_flying:
        score *= 2.0 // Double score for preferred target type
        
    # Bonus for targeting high-priority units (requires role/threat assessment)
    target_priority = AI_System.assess_target_priority(target) // e.g., 0=low, 1=medium, 2=high (Healer/Dancer/Lord)
    score += target_priority * 15 

    # Slight penalty for overkill if not killing a high-priority target? (Optional)
    # IF NOT is_kill AND preview.attacker_potential_dmg > target.stats.current_hp * 2 AND target_priority < 2:
    #     score *= 0.9 

    # Ensure score is not negative unless intended (e.g. attacking an ally somehow)
    score = MAX(0, score) 
        
    RETURN score
    // TDD_ANCHOR: test_ai_ballista_target_score_kill_bonus - Verify kill significantly increases score.
    // TDD_ANCHOR: test_ai_ballista_target_score_flying_bonus - Verify flying significantly increases score.
    // TDD_ANCHOR: test_ai_ballista_target_score_priority_bonus - Verify high-priority target increases score.
    // TDD_ANCHOR: test_ai_ballista_target_score_expected_damage - Verify base score reflects damage and hit rate.
```

## 9. Integration Points

*   **Map System:** Manages `BallistaInstance` objects, position, state. Provides range/LoS calculations via `calculate_tiles_in_range` and `has_line_of_sight`. Handles map object interactions.
*   **Unit System:** Manages units, class, stats, skills, properties (like `IS_FLYING`), state (`BallistaUserState`, `is_immobile`, `is_attackable`). Provides functions like `get_unit`, `get_units_on_tiles`, `are_hostile`. Handles unit defeat/capture consequences.
*   **Combat System:** Provides core calculation functions (`get_effectiveness_multiplier`, `calculate_avoid`, `calculate_defense`, `calculate_crit_evade`, `get_combat_stat_bonuses`, `apply_damage`, `handle_unit_defeated`). Needs context parameters (`context="ballista_attack"`) to potentially adjust calculations or skill applicability if needed. Executes combat rounds/animations.
*   **Action System:** Determines available actions (`get_unit_available_actions`). Executes chosen actions, including triggering `execute_ballista_attack`. Marks actions complete.
*   **AI System:** Uses information from other systems to make decisions. Calls `decide_ai_ballista_action` for units manning ballistae. Includes functions like `assess_target_priority`.
*   **Scenario Loader:** Defines `BallistaType`, `BallistaWeapon` data. Places `BallistaInstance` objects on the map with initial state (occupant, durability) based on scenario files.
*   **Status System:** (If applicable) Applies status effects from specialized ballistae (e.g., Poison).

## 10. Special Cases & Edge Cases

*   **Operator Defeated/Captured:** If the unit specified by `occupying_unit_id` is defeated or captured:
    *   The standard defeat/capture logic removes the unit from the map.
    *   A system event (e.g., `UnitRemovedEvent`) should trigger a check.
    *   The handler finds the `BallistaInstance` the unit was manning (via `BallistaUserState` before removal or by searching instances for the unit ID).
    *   Set `BallistaInstance.occupying_unit_id = None`.
    *   Set `BallistaInstance.is_enabled = False`. The ballista becomes permanently unusable for the current map.
    *   The unit's `BallistaUserState` component is removed automatically upon unit removal.
*   **Ballista Destroyed:** Standard FE ballistae are not destructible. If this feature is added, `BallistaInstance` needs HP, defense stats, and logic for being targeted and destroyed, which would also set `is_enabled = False`.
*   **Player Capturing Operator:** If a player unit captures the enemy operator, the same logic as "Operator Defeated/Captured" applies: the ballista is disabled.
*   **Player Using Ballista:** If players *can* use ballistae:
    *   `check_unit_can_use_ballista` needs to work for player units.
    *   Movement logic needs to allow eligible players to move onto an *empty, enabled* ballista tile, which should then set `occupying_unit_id`, add `BallistaUserState`, and set `is_immobile = True`.
    *   `get_unit_available_actions` needs to correctly show "Fire Ballista" for eligible players manning one.
    *   An action to voluntarily leave the ballista ("Dismount Ballista"?) might be needed, which would clear the occupant, remove the component, and set `is_immobile = False`.
*   **Multiple Ballista Types:** The use of `ballista_type_id` and fetching `BallistaType`/`BallistaWeapon` data ensures different ballistae function correctly based on their defined stats and properties.

```pseudocode
// Event Handler Example
FUNCTION on_unit_removed_from_map(event):
    removed_unit_id = event.unit_id
    
    // Check if this unit was manning a ballista
    // Option 1: Check component before removal (if possible)
    // Option 2: Iterate through active ballistae
    FOR ballista_instance IN MapSystem.get_all_objects_of_type(BallistaInstance):
        IF ballista_instance.occupying_unit_id == removed_unit_id:
            LOG_SYSTEM(f"Operator {removed_unit_id} removed from Ballista {ballista_instance.id}. Disabling.")
            ballista_instance.occupying_unit_id = None
            ballista_instance.is_enabled = False
            // TDD_ANCHOR: test_ballista_disabled_when_operator_defeated - Verify is_enabled=False after occupant defeat.
            // TDD_ANCHOR: test_ballista_disabled_when_operator_captured - Verify is_enabled=False after occupant capture.
            BREAK // Unit can only man one ballista