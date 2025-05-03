# Specification: Chapter Data Structure

## 1. Overview

This document defines the data structure for individual chapters within the game. Each chapter will have its own data file (or set of files within a directory, e.g., `data/chapters/chapter_1/`) containing all necessary information to set up and run the chapter scenario. This includes map details, unit placements, objectives, events, and reinforcement schedules.

## 2. File Structure (Proposed)

A chapter's data could be contained within a single YAML file (e.g., `data/chapters/chapter_1.yaml`) or distributed across multiple files within a dedicated directory (e.g., `data/chapters/chapter_1/`). For simplicity and initial implementation, a single YAML file per chapter is proposed.

Example: `data/chapters/chapter_1.yaml`

## 3. Data Schema

```yaml
# --- Chapter Metadata ---
chapter_id: ch1_the_beginning
chapter_title: "The Beginning"
description: "The first steps into a larger conflict."

# --- Map Information ---
map_file: "data/maps/chapter_1_map.tmx" # Or map.yaml, etc. Reference to the map layout file.

# --- Unit Placement ---
# Defines initial unit positions, stats overrides, inventory, and AI.
units:
  player:
    - unit_id: protagonist # References unit_id from data/units.yaml
      position: [5, 5]     # Coordinates (x, y) or (col, row)
      # Optional overrides for base stats from units.yaml
      stats_override:
        level: 2
        hp: 22
      inventory:
        - iron_sword
        - vulnerary
      # AI archetype (relevant if player unit can be AI controlled, e.g., auto-battle)
      # ai_archetype: default_player # Usually not needed for player units

    - unit_id: healer
      position: [4, 5]
      inventory:
        - heal_staff
        - vulnerary

  enemy:
    - unit_id: bandit_1
      position: [10, 12]
      class_override: brigand # Optional: Specify class if different from base unit definition
      level_override: 1        # Optional: Specify level
      inventory:
        - iron_axe
      ai_archetype: aggressive_melee # Defines AI behavior

    - unit_id: bandit_archer
      position: [15, 8]
      inventory:
        - iron_bow
      ai_archetype: stationary_ranged

  npc: # Neutral or allied units not controlled by the player
    - unit_id: villager_1
      position: [2, 15]
      ai_archetype: civilian_flee # AI controls their behavior
      # NPCs might have specific dialogue triggers or be objectives
      # TDD_ANCHOR: test_npc_ai_behavior(villager_1, civilian_flee)

# --- Chapter Objectives ---
objectives:
  win:
    - type: seize_throne # Example win condition
      target_position: [15, 15]
      required_unit: protagonist # Optional: Specific unit needed
      # TDD_ANCHOR: test_win_condition_seize_throne(target_position, required_unit)

    # Other potential win conditions:
    # - type: defeat_boss
    #   target_unit_id: boss_bandit
    # - type: rout_enemy
    # - type: survive_turns
    #   turn_count: 10
    # - type: reach_area
    #   target_area: [[20, 20], [22, 22]] # Top-left, bottom-right corners
    #   required_unit: any # or specific unit_id

  loss:
    - type: protagonist_defeated
      target_unit_id: protagonist
      # TDD_ANCHOR: test_loss_condition_protagonist_defeated(target_unit_id)

    # Other potential loss conditions:
    # - type: turn_limit_exceeded
    #   turn_count: 15 # If win condition is not met by this turn
    # - type: npc_defeated
    #   target_unit_id: villager_1 # If a specific NPC must survive

# --- Event Triggers ---
# Defines conditions that can trigger events.
event_triggers:
  - trigger_id: turn_3_reinforcements
    type: turn_start
    value: 3
    # TDD_ANCHOR: test_event_trigger_turn_start(value)

  - trigger_id: reach_bridge_area
    type: area_entered
    area: [[8, 10], [12, 10]] # Coordinates defining the area
    faction: player # Which faction entering triggers it (player, enemy, npc, any)
    # TDD_ANCHOR: test_event_trigger_area_entered(area, faction)

  - trigger_id: boss_talk_trigger
    type: talk_available # Becomes available when conditions met
    unit1_id: protagonist
    unit2_id: boss_bandit
    condition: # Optional: Further conditions, e.g., only after turn 5
      type: turn_ge # Greater than or equal
      value: 5
    # TDD_ANCHOR: test_event_trigger_talk_available(unit1_id, unit2_id, condition)

  - trigger_id: bandit_defeated_trigger
    type: unit_defeated
    target_unit_id: bandit_1
    # TDD_ANCHOR: test_event_trigger_unit_defeated(target_unit_id)

  - trigger_id: village_visited_trigger
    type: village_visited # Specific interaction type
    target_position: [2, 15]
    visiting_unit_faction: player
    # TDD_ANCHOR: test_event_trigger_village_visited(target_position, visiting_unit_faction)

# --- Event Definitions ---
# Links triggers to specific outcomes/actions.
events:
  - event_id: reinforcements_appear
    trigger: turn_3_reinforcements # References trigger_id
    actions:
      - type: spawn_reinforcements
        group_id: wave_1 # References reinforcement group_id
        # TDD_ANCHOR: test_event_action_spawn_reinforcements(group_id)

  - event_id: bridge_ambush_dialogue
    trigger: reach_bridge_area
    actions:
      - type: show_dialogue
        dialogue_id: ambush_warning # References dialogue data (potentially separate file or section)
        # TDD_ANCHOR: test_event_action_show_dialogue(dialogue_id)
      - type: spawn_reinforcements
        group_id: bridge_ambushers
      - type: set_trigger_inactive # Prevent re-triggering
        target_trigger_id: reach_bridge_area

  - event_id: boss_conversation
    trigger: boss_talk_trigger # This trigger just makes the talk *possible*
    actions: # The actual talk action is initiated by the player
      - type: enable_talk_option # Makes the 'Talk' command appear in UI
        unit1_id: protagonist
        unit2_id: boss_bandit
        dialogue_id: boss_recruitment_convo # Dialogue to show if Talk is chosen
        # TDD_ANCHOR: test_event_action_enable_talk_option(unit1_id, unit2_id, dialogue_id)

  - event_id: bandit_drops_item
    trigger: bandit_defeated_trigger
    actions:
      - type: drop_item_at # Item appears on the map where unit died
        item_id: gem
        position_from_trigger: true # Use the position from the unit_defeated trigger
        # TDD_ANCHOR: test_event_action_drop_item_at(item_id, position)

  - event_id: visit_village_reward
    trigger: village_visited_trigger
    actions:
      - type: give_item_to_unit
        item_id: elixir
        recipient_unit_triggering: true # Give to the unit that visited
        # TDD_ANCHOR: test_event_action_give_item_to_unit(item_id, recipient)
      - type: show_dialogue
        dialogue_id: village_thanks
      - type: set_trigger_inactive
        target_trigger_id: village_visited_trigger

# --- Reinforcements ---
reinforcements:
  - group_id: wave_1
    units:
      - unit_id: bandit_2
        position: [1, 1]
        ai_archetype: aggressive_melee
      - unit_id: bandit_3
        position: [1, 2]
        ai_archetype: aggressive_melee
    trigger: turn_3_reinforcements # Can also be triggered directly by events

  - group_id: bridge_ambushers
    units:
      - unit_id: bandit_archer_2
        position: [9, 9]
        ai_archetype: stationary_ranged
      - unit_id: bandit_archer_3
        position: [11, 9]
        ai_archetype: stationary_ranged
    trigger: reach_bridge_area # Triggered by the event

# --- Talk System Integration ---
# Dialogue data itself might be in a separate file (e.g., data/dialogue/chapter_1_dialogue.yaml)
# referenced by dialogue_id. The structure would follow the Talk system spec.
# Example reference:
# dialogue:
#   ambush_warning:
#     - speaker: protagonist
#       line: "Wait... it's quiet. Too quiet."
#     - speaker: bandit_leader # A generic ID or specific unit_id
#       line: "Heh, walked right into it!"

```

## 4. Integration with Game Engine (`ChapterLoader`)

A dedicated `ChapterLoader` module (or an extended `ScenarioLoader`) will be responsible for parsing these chapter data files.

**Pseudocode for `ChapterLoader`:**

```python
class ChapterLoader:
    # TDD_ANCHOR: test_chapter_loader_initialization()
    def __init__(self, chapter_data_path):
        self.chapter_data = self.load_yaml_data(chapter_data_path)
        # TDD_ANCHOR: test_load_valid_yaml_data(chapter_data_path)
        # TDD_ANCHOR: test_load_invalid_yaml_data_raises_error(invalid_path)
        self.validate_chapter_data()
        # TDD_ANCHOR: test_validate_chapter_data_schema(valid_data)
        # TDD_ANCHOR: test_validate_chapter_data_missing_keys_raises_error(invalid_data)

    def load_yaml_data(self, path):
        # Implementation to load YAML file
        pass # Placeholder

    def validate_chapter_data(self):
        # Use a schema validation library (like Cerberus or Pydantic)
        # or manual checks to ensure all required fields exist and have correct types.
        # TDD_ANCHOR: test_validate_map_file_exists()
        # TDD_ANCHOR: test_validate_unit_ids_exist()
        # TDD_ANCHOR: test_validate_item_ids_exist()
        # TDD_ANCHOR: test_validate_ai_archetypes_exist()
        # TDD_ANCHOR: test_validate_objective_types_supported()
        # TDD_ANCHOR: test_validate_event_trigger_types_supported()
        # TDD_ANCHOR: test_validate_event_action_types_supported()
        # TDD_ANCHOR: test_validate_reinforcement_group_references()
        # TDD_ANCHOR: test_validate_dialogue_id_references() # If dialogue is separate
        pass # Placeholder

    # TDD_ANCHOR: test_setup_game_state_returns_game_state_object()
    def setup_game_state(self, game_state):
        # 1. Load Map
        map_data = self.load_map(self.chapter_data['map_file'])
        game_state.set_map(map_data)
        # TDD_ANCHOR: test_setup_map_correctly(game_state, map_file)

        # 2. Place Units
        self.place_units(game_state, self.chapter_data['units'])
        # TDD_ANCHOR: test_place_player_units_correctly(game_state, unit_data)
        # TDD_ANCHOR: test_place_enemy_units_correctly(game_state, unit_data)
        # TDD_ANCHOR: test_place_npc_units_correctly(game_state, unit_data)
        # TDD_ANCHOR: test_apply_unit_stat_overrides(game_state, unit_data)
        # TDD_ANCHOR: test_assign_unit_inventory(game_state, unit_data)
        # TDD_ANCHOR: test_assign_unit_ai(game_state, unit_data)

        # 3. Set Objectives
        game_state.set_objectives(self.chapter_data['objectives'])
        # TDD_ANCHOR: test_set_win_conditions(game_state, objective_data)
        # TDD_ANCHOR: test_set_loss_conditions(game_state, objective_data)

        # 4. Register Events and Triggers
        event_manager = game_state.get_event_manager()
        event_manager.register_triggers(self.chapter_data['event_triggers'])
        event_manager.register_events(self.chapter_data['events'])
        # TDD_ANCHOR: test_register_event_triggers(event_manager, trigger_data)
        # TDD_ANCHOR: test_register_events_and_actions(event_manager, event_data)

        # 5. Prepare Reinforcements (Store definitions, don't spawn yet)
        game_state.set_reinforcement_definitions(self.chapter_data.get('reinforcements', []))
        # TDD_ANCHOR: test_store_reinforcement_definitions(game_state, reinforcement_data)

        # 6. Load Dialogue (if applicable)
        # dialogue_manager = game_state.get_dialogue_manager()
        # dialogue_manager.load_chapter_dialogue(...) # Load from separate file or section

        return game_state

    def load_map(self, map_path):
        # Logic to load map data (from TMX, YAML, etc.)
        pass # Placeholder

    def place_units(self, game_state, unit_definitions):
        # Logic to create Unit objects and place them on the game_state map
        pass # Placeholder

# --- Game Loop Integration ---
# During the game loop:
# - Turn Start: Check turn-based triggers.
# - Unit Movement: Check area-based triggers.
# - Unit Action (Talk): Check talk availability triggers/conditions.
# - Unit Defeat: Check unit defeated triggers.
# - Village Visit: Check visit triggers.
# - Event Manager processes triggered events and executes actions.
# - Check win/loss conditions at appropriate times (e.g., end of player/enemy phase).

```

## 5. Considerations & Future Enhancements

*   **Data Validation:** Robust validation is crucial. Using a schema library is highly recommended.
*   **Modularity:** Consider splitting very large chapters into multiple files (e.g., `units.yaml`, `events.yaml`) within the chapter directory.
*   **Dialogue Management:** Define how `dialogue_id` references are resolved (e.g., separate global or chapter-specific dialogue files).
*   **Map Format:** Support for different map formats (TMX, simple YAML grid) might be needed.
*   **Extensibility:** Design trigger and action types to be easily extensible.

This structure provides a comprehensive foundation for defining chapter content and logic in a data-driven way.