# Rescue System Specification (`specs/gameplay_systems/rescue_system.spec.md`)

## 1. Overview
This document outlines the pseudocode for the Rescue, Drop, and Take mechanics, primarily based on Fire Emblem: Thracia 776 rules. These actions allow units to carry allies, reposition them, or transfer them between carriers.

## 2. Data Structures
- `Unit`:
    - `id`: Unique identifier
    - `name`: String
    - `stats`: { `hp`, `max_hp`, `str`, `mag`, `skl`, `spd`, `luk`, `def`, `con`, `mov` }
    - `current_hp`: Integer
    - `position`: (x, y) tuple
    - `is_mounted`: Boolean
    - `status`: Enum (Normal, Rescuing, Rescued, Captured, etc.) // `Rescuing` means carrying an ally or captive
    - `carried_unit_id`: Nullable Unit ID (ID of the unit being carried)
    - `carrier_unit_id`: Nullable Unit ID (ID of the unit carrying this unit)
    - `action_taken`: Boolean
    - `faction`: Enum (Player, Enemy, NPC)
    - `inventory`: List of Items
    - `temp_stats`: Dictionary // Stores original stats before carry penalties
- `Map`:
    - `grid`: 2D array representing map tiles
    - `get_unit_at(position)`: Returns Unit or null
    - `is_tile_empty(position)`: Returns Boolean
    - `is_adjacent(pos1, pos2)`: Returns Boolean
    - `get_adjacent_tiles(position)`: Returns list of positions
    - `is_passable(position, movement_type)`: Returns Boolean // Checks if terrain is passable for unit type

## 3. Core Functions

### 3.1. `can_rescue(rescuer: Unit, target: Unit) -> Boolean`
// Checks if 'rescuer' can initiate the Rescue command on 'target'.
// TDD: Test_can_rescue_valid_ally
// TDD: Test_can_rescue_valid_npc
// TDD: Test_can_rescue_invalid_con_too_low
// TDD: Test_can_rescue_invalid_enemy_target
// TDD: Test_can_rescue_invalid_target_already_carried
// TDD: Test_can_rescue_invalid_rescuer_already_carrying
// TDD: Test_can_rescue_invalid_self_target
// TDD: Test_can_rescue_invalid_target_is_carrier
// TDD: Test_can_rescue_dismounted_indoors_check (if Con changes or rules differ)
    IF rescuer IS NULL OR target IS NULL THEN RETURN FALSE
    IF rescuer.id == target.id THEN RETURN FALSE // Cannot rescue self

    // Check statuses: Rescuer cannot be carrying, Target cannot be carried or carrying
    IF rescuer.status == Rescuing THEN RETURN FALSE
    IF target.status == Rescued OR target.status == Captured OR target.status == Rescuing THEN RETURN FALSE

    // Check faction: Can rescue own faction (Player/Enemy) or NPCs
    IF rescuer.faction != target.faction AND target.faction != NPC THEN RETURN FALSE

    // Check Constitution: Rescuer's CON must be > Target's CON
    IF rescuer.stats.con <= target.stats.con THEN RETURN FALSE

    // Add specific checks for mounted/dismounted states if rules differ beyond Con
    // e.g., IF Map.is_indoors() AND rescuer.is_mounted THEN RETURN FALSE (must dismount first)

    RETURN TRUE

### 3.2. `initiate_rescue(rescuer: Unit, target: Unit)`
// Executes the Rescue action. Assumes adjacency is already confirmed by UI/caller.
// TDD: Test_initiate_rescue_success
// TDD: Test_initiate_rescue_updates_rescuer_status_and_carried_id
// TDD: Test_initiate_rescue_updates_target_status_and_carrier_id
// TDD: Test_initiate_rescue_applies_rescuer_penalties_correctly
// TDD: Test_initiate_rescue_removes_target_from_map_display
// TDD: Test_initiate_rescue_consumes_rescuer_action
// TDD: Test_initiate_rescue_failure_if_cannot_rescue
    IF NOT can_rescue(rescuer, target) THEN
        RETURN FAILURE("Conditions not met to rescue target.")
    END IF

    // Update states
    rescuer.status = Rescuing
    rescuer.carried_unit_id = target.id
    target.status = Rescued
    target.carrier_unit_id = rescuer.id

    // Apply penalties to rescuer
    apply_carry_penalties(rescuer, target) // See 3.7

    // Update map state (target is no longer visually on map)
    // Map.update_unit_visibility(target, visible=False)

    // Consume action
    rescuer.action_taken = TRUE

    // Handle Canto for mounted rescuers if applicable (integration with MovementSystem)
    // IF rescuer.is_mounted THEN MovementSystem.check_canto(rescuer)

    RETURN SUCCESS

### 3.3. `can_drop(rescuer: Unit, drop_position: Position) -> Boolean`
// Checks if 'rescuer' can drop their carried unit at 'drop_position'.
// TDD: Test_can_drop_valid
// TDD: Test_can_drop_invalid_not_rescuing
// TDD: Test_can_drop_invalid_position_not_adjacent
// TDD: Test_can_drop_invalid_position_occupied_by_unit
// TDD: Test_can_drop_invalid_position_impassable_terrain_for_dropped_unit
    IF rescuer IS NULL OR rescuer.status != Rescuing OR rescuer.carried_unit_id IS NULL THEN RETURN FALSE
    IF NOT Map.is_adjacent(rescuer.position, drop_position) THEN RETURN FALSE
    IF Map.get_unit_at(drop_position) IS NOT NULL THEN RETURN FALSE // Tile must be empty of units

    let carried_unit = get_unit(rescuer.carried_unit_id)
    // Check if drop_position terrain is passable for the *carried* unit
    IF NOT Map.is_passable(drop_position, carried_unit.movement_type) THEN RETURN FALSE

    RETURN TRUE

### 3.4. `initiate_drop(rescuer: Unit, drop_position: Position)`
// Executes the Drop action.
// TDD: Test_initiate_drop_success
// TDD: Test_initiate_drop_updates_rescuer_status_to_normal
// TDD: Test_initiate_drop_updates_dropped_unit_status_to_normal
// TDD: Test_initiate_drop_removes_rescuer_penalties
// TDD: Test_initiate_drop_places_dropped_unit_at_correct_position
// TDD: Test_initiate_drop_sets_dropped_unit_action_taken
// TDD: Test_initiate_drop_consumes_rescuer_action
// TDD: Test_initiate_drop_failure_if_cannot_drop
    IF NOT can_drop(rescuer, drop_position) THEN
        RETURN FAILURE("Cannot drop unit at specified position.")
    END IF

    let dropped_unit = get_unit(rescuer.carried_unit_id)

    // Update states
    rescuer.status = Normal
    rescuer.carried_unit_id = NULL
    dropped_unit.status = Normal
    dropped_unit.carrier_unit_id = NULL
    dropped_unit.position = drop_position
    dropped_unit.action_taken = TRUE // Dropped unit cannot act this turn

    // Remove penalties from rescuer
    remove_carry_penalties(rescuer) // See 3.8

    // Update map state (dropped unit is now visible at drop_position)
    // Map.update_unit_visibility(dropped_unit, visible=True)
    // Map.update_unit_position(dropped_unit, drop_position)

    // Consume action
    rescuer.action_taken = TRUE

    // Handle Canto for mounted rescuers if applicable
    // IF rescuer.is_mounted THEN MovementSystem.check_canto(rescuer)

    RETURN SUCCESS

### 3.5. `can_take(taker: Unit, current_rescuer: Unit) -> Boolean`
// Checks if 'taker' can take the unit carried by 'current_rescuer'.
// TDD: Test_can_take_valid
// TDD: Test_can_take_invalid_not_adjacent
// TDD: Test_can_take_invalid_rescuer_not_carrying
// TDD: Test_can_take_invalid_taker_already_carrying
// TDD: Test_can_take_invalid_taker_con_too_low
// TDD: Test_can_take_invalid_self_target (taker == current_rescuer)
    IF taker IS NULL OR current_rescuer IS NULL THEN RETURN FALSE
    IF taker.id == current_rescuer.id THEN RETURN FALSE // Cannot take from self
    IF NOT Map.is_adjacent(taker.position, current_rescuer.position) THEN RETURN FALSE
    IF current_rescuer.status != Rescuing OR current_rescuer.carried_unit_id IS NULL THEN RETURN FALSE // Must be carrying someone
    IF taker.status == Rescuing THEN RETURN FALSE // Taker cannot already be carrying

    let carried_unit = get_unit(current_rescuer.carried_unit_id)
    // Check Constitution: Taker's CON must be > Carried Unit's CON
    IF taker.stats.con <= carried_unit.stats.con THEN RETURN FALSE

    RETURN TRUE

### 3.6. `initiate_take(taker: Unit, current_rescuer: Unit)`
// Executes the Take action.
// TDD: Test_initiate_take_success
// TDD: Test_initiate_take_updates_statuses_correctly
// TDD: Test_initiate_take_removes_penalties_from_original_rescuer
// TDD: Test_initiate_take_applies_penalties_to_taker
// TDD: Test_initiate_take_updates_carried_unit_carrier_id
// TDD: Test_initiate_take_consumes_taker_action
// TDD: Test_initiate_take_failure_if_cannot_take
    IF NOT can_take(taker, current_rescuer) THEN
        RETURN FAILURE("Conditions not met to take the carried unit.")
    END IF

    let carried_unit = get_unit(current_rescuer.carried_unit_id)

    // Remove penalties from original rescuer
    remove_carry_penalties(current_rescuer)

    // Update states
    current_rescuer.status = Normal
    current_rescuer.carried_unit_id = NULL

    taker.status = Rescuing
    taker.carried_unit_id = carried_unit.id
    carried_unit.carrier_unit_id = taker.id // Rescued unit's carrier changes

    // Apply penalties to new rescuer (taker)
    apply_carry_penalties(taker, carried_unit)

    // Consume taker's action
    taker.action_taken = TRUE

    // Handle Canto for mounted takers if applicable
    // IF taker.is_mounted THEN MovementSystem.check_canto(taker)

    RETURN SUCCESS

### 3.7. `apply_carry_penalties(carrier: Unit, carried: Unit)`
// Applies stat and potentially movement penalties for carrying a unit.
// TDD: Test_apply_carry_penalties_stats_halved_correctly
// TDD: Test_apply_carry_penalties_mov_halved_when_condition_met
// TDD: Test_apply_carry_penalties_mov_not_halved_when_condition_not_met
// TDD: Test_apply_carry_penalties_mounted_mov_check_uses_bonus
// TDD: Test_apply_carry_penalties_stores_original_stats
    // Store original stats if not already done
    IF carrier.temp_stats IS EMPTY OR carrier.temp_stats IS NULL THEN
        carrier.temp_stats = {}
        carrier.temp_stats['original_str'] = carrier.stats.str
        carrier.temp_stats['original_mag'] = carrier.stats.mag
        carrier.temp_stats['original_skl'] = carrier.stats.skl
        carrier.temp_stats['original_spd'] = carrier.stats.spd
        carrier.temp_stats['original_def'] = carrier.stats.def
        carrier.temp_stats['original_mov'] = carrier.stats.mov
    END IF

    // Halve combat stats (floor division)
    carrier.stats.str = floor(carrier.temp_stats['original_str'] / 2)
    carrier.stats.mag = floor(carrier.temp_stats['original_mag'] / 2)
    carrier.stats.skl = floor(carrier.temp_stats['original_skl'] / 2)
    carrier.stats.spd = floor(carrier.temp_stats['original_spd'] / 2)
    carrier.stats.def = floor(carrier.temp_stats['original_def'] / 2)

    // Check for Movement penalty (based on research.md line 284/914)
    // "if carried unit’s Con > half of rescuer’s Con (plus 5 if rescuer is mounted) then Mov is cut in half"
    let mov_check_con = carrier.temp_stats['original_con'] // Use original Con for check
    IF carrier.is_mounted THEN
        mov_check_con += 5 // Add effective +5 Con for mounted check
    END IF

    IF carried.stats.con > floor(mov_check_con / 2) THEN
         carrier.stats.mov = floor(carrier.temp_stats['original_mov'] / 2) // Halve original Mov
    ELSE
         carrier.stats.mov = carrier.temp_stats['original_mov'] // Ensure Mov is restored if penalty no longer applies (e.g., taking a lighter unit)
    END IF

### 3.8. `remove_carry_penalties(carrier: Unit)`
// Restores stats to their original values when carrying stops.
// TDD: Test_remove_carry_penalties_restores_all_stats
// TDD: Test_remove_carry_penalties_clears_temp_stats
// TDD: Test_remove_carry_penalties_handles_no_penalties_applied
    IF carrier.temp_stats IS EMPTY OR carrier.temp_stats IS NULL THEN
        RETURN // No penalties were applied or already removed
    END IF

    // Restore original stats
    carrier.stats.str = carrier.temp_stats['original_str']
    carrier.stats.mag = carrier.temp_stats['original_mag']
    carrier.stats.skl = carrier.temp_stats['original_skl']
    carrier.stats.spd = carrier.temp_stats['original_spd']
    carrier.stats.def = carrier.temp_stats['original_def']
    carrier.stats.mov = carrier.temp_stats['original_mov']
    // Note: Con and Luk are not halved

    // Clear temporary storage
    carrier.temp_stats = {}

## 4. Constraints and Edge Cases
- **Action Cost:** Rescue, Drop, and Take consume the acting unit's turn.
- **Mounted Units:**
    - Can rescue/be rescued subject to Con rules (Rescuer Con > Target Con).
    - Must dismount indoors. If dismounted, they use infantry movement rules and stats, potentially affecting their ability to rescue based on Con.
    - Can use Canto (remaining movement) after performing Rescue, Drop, or Take actions if they are mounted and the action doesn't forbid Canto (Rescue/Drop/Take are non-combat actions allowing Canto).
    - Have an effective +5 Con added *only* for the Movement penalty check when carrying (see `apply_carry_penalties`).
- **Rescuing Unit Actions:**
    - Cannot Attack, use Staves, or perform most other standard actions while in `Rescuing` status.
    - Can Move (with potentially halved Mov), Trade, Take (another carried unit from an adjacent rescuer), Drop (the unit they are carrying).
    - Combat stats (Str, Mag, Skl, Spd, Def) are halved.
- **Rescued Unit State:**
    - Cannot act, gain EXP, be targeted by attacks/staves, or benefit from terrain/supports while being carried (`Rescued` status).
    - If the carrier unit is defeated, the rescued unit is dropped onto the tile the carrier occupied and becomes vulnerable (`Normal` status, `action_taken = True`).
- **Stacking:** A unit cannot rescue while already rescuing. A unit cannot be rescued if already rescued/carried.
- **Terrain:** Drop location must be an empty, passable tile for the dropped unit type.
- **Capture Interaction:** The `Rescuing` status and penalties apply identically whether carrying a rescued ally or a captured enemy. The `Take` and `Drop` commands function similarly for captives, but `Drop` might be labeled `Release` for captives, removing them from the map instead of placing them.

## 5. AI Considerations
- **Rescue Trigger Conditions (Utility Score Factors):**
    - Ally HP critically low (e.g., `< 25%` or `< incoming damage). High positive score.
    - Ally under lethal threat (multiple attackers, effective weapons). High positive score.
    - Ally has debilitating status (Sleep, Berserk) and needs removal from danger. Moderate positive score.
    - Repositioning a key unit (healer, slow armor, dancer) towards objective or away from danger. Moderate positive score based on strategic value.
    - Rescuer safety check (can rescuer survive with halved stats/mov?). High negative score if rescuer becomes too vulnerable.
    - `can_rescue` check must pass. Score = -Infinity if false.
- **Drop Trigger Conditions (Utility Score Factors):**
    - Rescued unit is safe at potential drop location. Low positive score (enabling action).
    - Rescued unit needs to act next turn (heal, attack key target). Moderate positive score.
    - Rescuer needs to perform another action (attack, seize, heal). Moderate positive score.
    - Drop position safety/strategic value. Score based on proximity to enemies/objectives.
    - `can_drop` check must pass. Score = -Infinity if false.
- **Take Trigger Conditions (Utility Score Factors):**
    - Transferring unit to a faster carrier for transport. Moderate positive score.
    - Transferring unit to a safer/sturdier carrier. Moderate positive score.
    - Freeing up the original rescuer for a critical action. High positive score if original rescuer has high immediate value.
    - Enabling a "Rescue chain" for long-distance movement. Score based on distance gained.
    - `can_take` check must pass. Score = -Infinity if false.
- **AI Evaluation Logic:**
    - For each potential action (Rescue, Drop, Take) available to an AI unit:
        1. Check validity (`can_rescue`, `can_drop`, `can_take`).
        2. If valid, calculate a utility score based on the factors above.
        3. Compare scores for Rescue/Drop/Take against other actions (Attack, Wait, Use Item).
        4. Select the action with the highest utility score that meets the AI's current objective/aggression level.

## 6. Integration Points
- **Turn Manager:**
    - Must restore `action_taken` flag for dropped units at the start of their next phase.
    - Must correctly apply/remove `Rescuing`/`Rescued` statuses and penalties.
- **Combat System:**
    - Must read the potentially halved stats (Str, Mag, Skl, Spd, Def) from `carrier.stats` when a unit in `Rescuing` status is involved in combat (e.g., if attacked).
- **Movement System:**
    - Must read the potentially halved `mov` stat from `carrier.stats` for pathfinding.
    - Must integrate Canto logic to allow remaining movement after Rescue/Drop/Take for mounted units.
- **AI System:**
    - Must incorporate the utility evaluation logic described in Section 5.
    - Must be able to query `can_rescue`, `can_drop`, `can_take`.
- **UI System:**
    - Display Rescue, Drop, Take commands contextually in the action menu.
    - Visually indicate which unit is carrying whom (e.g., overlay sprite, status icon).
    - Hide rescued units from the map grid.
    - Reflect halved stats/mov accurately in status screens and combat forecasts for carrying units.