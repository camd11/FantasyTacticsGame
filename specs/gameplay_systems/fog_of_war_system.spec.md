# Fog of War System Specification (Spec Pseudocode)

## 1. Overview

This document outlines the pseudocode specification for the Fog of War (FoW) system in the Fantasy Tactics Game, based on mechanics observed in Fire Emblem: Thracia 776. This system manages tile visibility on designated FoW maps, controlling what the player can see and when enemy units are displayed.

## 2. Goals

- Define how individual unit vision is calculated.
- Specify how the map tracks visibility state for each tile.
- Detail the triggers and process for updating map visibility.
- Describe how enemy units are handled and displayed within the fog.
- Outline the mechanics of items and staves that affect visibility.
- Clarify AI behavior in relation to Fog of War.
- Identify integration points with other game systems.

## 3. Data Structures

### 3.1. TileVisibilityState (Enum)

Defines the possible visibility states for a map tile from the player's perspective.

```pseudocode
ENUM TileVisibilityState:
  Unknown   // Tile has never been revealed. Rendered as black/obscured.
  Fog       // Tile was previously visible but is currently outside vision. Rendered as shrouded/dimmed.
  Visible   // Tile is currently within the vision range of a player unit or light source. Rendered normally.
```

### 3.2. MapVisibilityData

Stores the overall visibility state for the current map. Managed by the Map System.

```pseudocode
DATA_STRUCTURE MapVisibilityData:
  visibility_grid : 2D_Array[MapHeight][MapWidth] OF TileVisibilityState // Stores the state of each tile. Initialized to Unknown.
  light_sources   : List OF LightSource // Active temporary light sources (e.g., from Torch Staff).

DATA_STRUCTURE LightSource:
  source_position : Position(x, y) // Center of the light source.
  radius          : Integer        // Radius of illumination.
  duration        : Integer        // Turns remaining for this light source. Decremented each player phase start.
```

### 3.3. UnitVisibilityData (Component)

Added to each Unit entity to track its specific vision properties.

```pseudocode
DATA_STRUCTURE UnitVisibilityData:
  base_vision_range     : Integer // Default vision range (e.g., 3).
  class_vision_bonus    : Integer // Bonus vision from class (e.g., Thief +2). Default 0.
  temporary_vision_bonus: Integer // Bonus from temporary effects like Torch item. Default 0.
  bonus_duration        : Integer // Turns remaining for the temporary bonus. Default 0.
```

## 4. Core Logic Modules

### 4.1. Visibility Calculation Module

Determines the effective vision range of a unit and whether a specific tile is visible.

```pseudocode
FUNCTION get_unit_vision_range(unit):
  // Calculates the total current vision range for a given unit.
  // TDD Anchor: test_get_unit_vision_range
  //   - Test with default range.
  //   - Test with class bonus (e.g., Thief).
  //   - Test with active temporary bonus (Torch item).
  //   - Test with combined class and temporary bonuses.

  vis_data = unit.get_component(UnitVisibilityData)
  base_range = vis_data.base_vision_range
  class_bonus = vis_data.class_vision_bonus
  temp_bonus = 0
  IF vis_data.bonus_duration > 0:
    temp_bonus = vis_data.temporary_vision_bonus
  ENDIF

  RETURN base_range + class_bonus + temp_bonus
ENDFUNCTION

FUNCTION is_tile_visible_to_player(target_tile_pos, map_visibility_data, player_units, map_data):
  // Checks if a specific tile is currently visible to the player faction.
  // TDD Anchor: test_is_tile_visible_to_player
  //   - Test tile visible by one unit within range and LoS.
  //   - Test tile visible by multiple units.
  //   - Test tile not visible due to distance.
  //   - Test tile not visible due to LoS blockage (wall, mountain).
  //   - Test tile visible due to active Torch Staff light source.
  //   - Test tile not visible if only covered by expired light source.
  //   - Test tile visible if covered by unit AND light source.

  // Check vision from player units
  FOR each player_unit IN player_units:
    // Skip units being carried (rescued/captured) - they provide no vision
    IF player_unit.is_being_carried():
      CONTINUE
    ENDIF

    vision_range = get_unit_vision_range(player_unit)
    distance = calculate_manhattan_distance(player_unit.position, target_tile_pos) // Or other appropriate distance metric

    IF distance <= vision_range:
      IF has_line_of_sight(player_unit.position, target_tile_pos, map_data):
        RETURN TRUE
      ENDIF
    ENDIF
  ENDFOR

  // Check vision from temporary light sources (Torch Staff)
  FOR each light_source IN map_visibility_data.light_sources:
    IF light_source.duration > 0:
      distance = calculate_manhattan_distance(light_source.source_position, target_tile_pos)
      IF distance <= light_source.radius:
        // Assumption: Torch staff light ignores LoS blockers within its radius.
        RETURN TRUE
      ENDIF
    ENDIF
  ENDFOR

  RETURN FALSE
ENDFUNCTION

FUNCTION has_line_of_sight(start_pos, end_pos, map_data):
  // Determines if there is an unobstructed line of sight between two points.
  // TDD Anchor: test_has_line_of_sight
  //   - Test clear line on open terrain.
  //   - Test line blocked by a Wall tile.
  //   - Test line blocked by a Peak tile.
  //   - Test line not blocked by Forest tile (Forests typically don't block LoS in FE).
  //   - Test adjacent tiles always have LoS.
  //   - Test LoS across diagonal gaps.

  // Implementation uses a line-drawing algorithm (e.g., Bresenham's)
  // to check all intermediate tiles.
  intermediate_tiles = get_tiles_on_line(start_pos, end_pos)

  FOR each tile_pos IN intermediate_tiles:
    terrain = map_data.get_terrain_at(tile_pos)
    IF terrain.properties.blocks_vision == TRUE:
      RETURN FALSE
    ENDIF
  ENDFOR

  RETURN TRUE
ENDFUNCTION
```

### 4.2. Map State Update Module

Handles updating the `visibility_grid` based on current unit positions and light sources.

```pseudocode
FUNCTION update_map_visibility(map_visibility_data, player_units, map_data):
  // Iterates through the entire map and updates the visibility state of each tile.
  // TDD Anchor: test_update_map_visibility
  //   - Test initial map reveal around starting units.
  //   - Test tiles changing from Visible to Fog when units move away.
  //   - Test tiles changing from Fog/Unknown to Visible when units move closer.
  //   - Test tiles revealed by Torch Staff remain Visible while active.
  //   - Test tiles revealed by Torch Staff become Fog when it expires (if not seen by units).
  //   - Test Unknown tiles remain Unknown unless revealed.

  FOR y FROM 0 TO MapHeight - 1:
    FOR x FROM 0 TO MapWidth - 1:
      tile_pos = Position(x, y)
      current_state = map_visibility_data.visibility_grid[y][x]
      is_currently_visible = is_tile_visible_to_player(tile_pos, map_visibility_data, player_units, map_data)

      IF is_currently_visible:
        map_visibility_data.visibility_grid[y][x] = TileVisibilityState.Visible
      ELSE:
        // If it was visible before, transition to Fog (shroud)
        IF current_state == TileVisibilityState.Visible:
          map_visibility_data.visibility_grid[y][x] = TileVisibilityState.Fog
        // Otherwise (if Unknown or already Fog), it remains in its current state.
        // No change needed for Unknown -> Unknown or Fog -> Fog.
        ENDIF
      ENDIF
    ENDFOR
  ENDFOR
ENDFUNCTION

FUNCTION decrement_visibility_durations(map_visibility_data, player_units):
  // Decrements timers for temporary vision effects at the start of the player phase.
  // TDD Anchor: test_decrement_visibility_durations
  //   - Test Torch item duration decreases.
  //   - Test Torch Staff light source duration decreases.
  //   - Test bonus/source removed when duration reaches zero.

  // Decrement Torch item durations
  FOR each unit IN player_units:
    vis_data = unit.get_component(UnitVisibilityData)
    IF vis_data.bonus_duration > 0:
      vis_data.bonus_duration -= 1
      IF vis_data.bonus_duration == 0:
        vis_data.temporary_vision_bonus = 0 // Reset bonus when duration expires
      ENDIF
    ENDIF
  ENDFOR

  // Decrement Torch Staff light source durations
  // Iterate backwards or create new list to handle removal safely
  active_light_sources = []
  FOR each light_source IN map_visibility_data.light_sources:
    IF light_source.duration > 0:
      light_source.duration -= 1
      IF light_source.duration > 0:
        add light_source to active_light_sources
      ENDIF
    ENDIF
  ENDFOR
  map_visibility_data.light_sources = active_light_sources // Update list
ENDFUNCTION
```

## 5. Triggering Visibility Updates

Visibility needs to be recalculated at specific points in the game flow.

```pseudocode
PROCEDURE on_player_phase_start(game_state):
  // TDD Anchor: test_visibility_update_on_phase_start
  decrement_visibility_durations(game_state.map_visibility_data, game_state.player_units)
  update_map_visibility(game_state.map_visibility_data, game_state.player_units, game_state.map_data)
  // UI Refresh needed here
ENDPROCEDURE

PROCEDURE on_unit_action_finish(unit, action_type, action_details, game_state):
  // Called after any unit finishes an action that might affect visibility.
  // TDD Anchor: test_visibility_update_post_action
  //   - Test update after Move action.
  //   - Test update after Use Torch Item action.
  //   - Test update after Use Torch Staff action.
  //   - Test no unnecessary update after Attack action (unless Canto moves unit).

  visibility_needs_update = FALSE

  IF action_type == Action.Move OR action_type == Action.CantoMove:
    visibility_needs_update = TRUE
  ELSE IF action_type == Action.UseItem AND item_used_was_torch(action_details):
     apply_torch_item_effect(unit, action_details) // Sets temporary bonus and duration
     visibility_needs_update = TRUE
  ELSE IF action_type == Action.UseStaff AND staff_used_was_torch(action_details):
     apply_torch_staff_effect(game_state.map_visibility_data, action_details) // Adds light source
     visibility_needs_update = TRUE
  ENDIF

  IF visibility_needs_update:
     update_map_visibility(game_state.map_visibility_data, game_state.player_units, game_state.map_data)
     // UI Refresh needed here
  ENDIF
ENDPROCEDURE

PROCEDURE apply_torch_item_effect(unit, item_details):
  // TDD Anchor: test_apply_torch_item_effect
  vis_data = unit.get_component(UnitVisibilityData)
  vis_data.temporary_vision_bonus = item_details.vision_bonus // e.g., 5
  vis_data.bonus_duration = item_details.duration // e.g., 5
ENDPROCEDURE

PROCEDURE apply_torch_staff_effect(map_visibility_data, staff_details):
  // TDD Anchor: test_apply_torch_staff_effect
  // Assumes staff hit check and target position calculation happened before this call.
  new_light_source = LightSource(
    source_position = staff_details.target_position,
    radius = staff_details.radius, // e.g., 10
    duration = staff_details.duration // e.g., 5
  )
  add new_light_source to map_visibility_data.light_sources
ENDPROCEDURE
```

## 6. Enemy Units in Fog

Handling the display and behavior of enemies hidden by FoW.

```pseudocode
// 6.1. Enemy Position Tracking
// The core Map System ALWAYS tracks the true (x, y) position of every enemy unit,
// regardless of whether they are visible to the player. FoW is a display layer concept.

// 6.2. Enemy Display Logic (UI Interaction)
FUNCTION should_display_unit(unit, map_visibility_data):
  // Determines if a unit (typically an enemy) should be rendered on the map.
  // TDD Anchor: test_should_display_unit
  //   - Test enemy on Visible tile returns TRUE.
  //   - Test enemy on Fog tile returns FALSE.
  //   - Test enemy on Unknown tile returns FALSE.

  tile_state = map_visibility_data.visibility_grid[unit.position.y][unit.position.x]
  RETURN tile_state == TileVisibilityState.Visible
ENDFUNCTION

// The UI/Display System will call should_display_unit() for each enemy unit
// before rendering its sprite. If FALSE, the sprite is not drawn.
// When an enemy moves, the UI checks its new tile's visibility state to determine
// if it should appear or disappear.
```

## 7. AI Considerations

AI behavior in Thracia 776 is not hindered by player-side Fog of War.

```pseudocode
// 7.1. AI Vision Model
// The AI operates with perfect information regarding player unit positions.
// AI pathfinding and targeting algorithms should access the true positions
// stored in the game state (e.g., Map System's unit list), NOT the player's
// visibility grid.

// TDD Anchor: test_ai_behavior_in_fog
//   - Test AI unit paths correctly towards a player unit hidden in Fog/Unknown tiles.
//   - Test AI unit targets and attacks a player unit that is currently in Fog from the player's view.

// Example AI Targeting Snippet (Conceptual)
FUNCTION ai_select_target(ai_unit, player_units, map_data):
  best_target = NULL
  max_score = -Infinity

  // AI iterates through ALL player units, regardless of player visibility
  FOR each player_unit IN player_units:
    // AI calculates potential damage, hit chance, etc., using true positions and stats.
    // It does NOT check if player_unit is currently visible to the player.
    score = calculate_attack_score(ai_unit, player_unit, map_data)
    IF score > max_score:
      max_score = score
      best_target = player_unit
    ENDIF
  ENDFOR
  RETURN best_target
ENDFUNCTION
```

## 8. Integration Points

-   **Map System:** Owns `MapVisibilityData`, provides `visibility_grid`, terrain info (`blocks_vision`), unit positions.
-   **Unit System:** Units have `UnitVisibilityData` component, class info, inventory (for Torch item).
-   **Turn Manager:** Triggers `on_player_phase_start`.
-   **Action System:** Triggers `on_unit_action_finish` after Move, Use Item, Use Staff, CantoMove.
-   **UI/Display System:** Reads `visibility_grid` to render tiles, calls `should_display_unit` for enemy sprites, shows vision previews.
-   **Item/Staff System:** Defines properties of Torch item and Torch staff (bonus, duration, radius). Handles targeting and hit checks for Torch Staff.
-   **AI System:** Accesses true unit positions from Map System, ignoring player visibility state for decision-making.

## 9. Edge Cases & Notes

-   **Rescued/Carried Units:** Units being carried provide no vision. `is_tile_visible_to_player` should check for this status.
-   **Torch Staff Light Propagation:** Assumed to ignore Line of Sight blockers within its radius, illuminating all tiles within range regardless of walls/terrain. This matches typical FE behavior.
-   **Initial State:** On map load for a FoW map, `visibility_grid` is initialized to `Unknown`. The first call to `update_map_visibility` (likely during initial deployment or first player phase start) reveals the area around starting units.
-   **Performance:** Calculating visibility for every tile on every update trigger can be expensive on large maps. Optimizations might involve only updating tiles within a certain range of changed units/sources, or using dirty flags.