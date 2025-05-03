# Specification: Save/Load System

**Module:** `core_engine.save_load_system`

**Version:** 1.0

**Author:** AI Assistant

**Date:** 2025-04-12

## 1. Overview

This document outlines the requirements, data structures, processes, and integration points for the game's Save/Load system. The system allows players to save their progress at specific points and resume playing later by loading a saved state.

## 2. Functional Requirements

*   The system must be able to capture the essential game state required to resume play accurately.
*   The system must support multiple save slots.
*   The system must provide mechanisms for saving the game state.
*   The system must provide mechanisms for loading a previously saved game state.
*   The system must handle potential errors during saving and loading (e.g., corrupted files, missing files).
*   The system should be reasonably performant, avoiding excessive delays during save/load operations.

## 3. Save Data Structure

The following data needs to be persisted to reconstruct the game state:

```
{
  "save_metadata": {
    "save_format_version": "1.0", // To handle future changes
    "timestamp": "YYYY-MM-DDTHH:MM:SSZ", // ISO 8601 format
    "playtime_seconds": 12345
  },
  "game_state": {
    "current_chapter_id": "chapter_1",
    "current_turn": 15,
    "current_phase": "PlayerPhase", // Or "EnemyPhase", "NPCPhase"
    "player_gold": 5000
  },
  "unit_state": [
    // List of all units (Player, Enemy, NPC) currently active
    {
      "unit_id": "player_unit_001", // Unique identifier for the instance
      "base_unit_id": "lyn", // Identifier from data/units.yaml
      "class_id": "lord",
      "level": 5,
      "experience": 30,
      "stats": { // Current stats, potentially modified by effects/items
        "max_hp": 25,
        "current_hp": 20,
        "strength": 8,
        "skill": 9,
        // ... other stats (speed, luck, defense, resistance, move, constitution)
      },
      "status_effects": [
        // List of active status effects
        {"id": "poison", "duration": 3},
        {"id": "boost_strength", "duration": 1}
      ],
      "inventory": [
        // List of item instances or IDs. Need to decide if items have unique state (e.g., durability)
        {"item_id": "iron_sword", "durability": 40},
        {"item_id": "vulnerary", "uses": 3}
        // ... potentially equipped flags
      ],
      "position": {"x": 5, "y": 10},
      "fatigue": 2,
      "has_acted": false, // Reset at start of turn usually, but needs saving mid-turn for suspend
      "rescued_unit_id": null // ID of the unit being rescued, if any
      "allegiance": "Player" // "Player", "Enemy", "NPC"
    },
    // ... more units
  ],
  "map_state": {
    "map_id": "chapter_1_map",
    "objects": [
      // List of map objects with persistent state
      {"object_id": "chest_01", "is_open": true},
      {"object_id": "ballista_01", "durability": 5},
      {"object_id": "destructible_wall_01", "current_hp": 10}
      // ... other objects like doors, bridges, etc.
    ],
    "fog_of_war": { // Optional: Only if FoW state needs to be saved precisely
      "enabled": true,
      "revealed_tiles": [ // List of coordinates {x, y}
        {"x": 0, "y": 0}, {"x": 1, "y": 0},
        // ... all revealed tiles
      ]
      // Alternative: Could use a bitmask or similar for efficiency
    }
  },
  "event_state": {
    "global_flags": [
      // List of flags that have been set
      "village_visited_01",
      "boss_appeared"
    ],
    "completed_talk_events": [
      // List of unique talk combinations completed
      {"talker_id": "player_unit_001", "listener_id": "npc_unit_005"}
    ],
    // Potentially other event-related state, like turn-based event counters
    "turn_event_counters": {
      "reinforcement_wave_1": 3 // e.g., 3 turns until wave 1 arrives
    }
  }
}
```

## 4. Save File Format

**JSON (JavaScript Object Notation)** will be used.

*   **Pros:** Human-readable (good for debugging), widely supported by libraries, relatively easy to parse.
*   **Cons:** Can be more verbose than binary formats, potentially slower parsing for very large states. (Consider compression if size/speed becomes an issue).

Save files will be named `save_slot_{N}.json`, where N is the slot number (e.g., `save_slot_1.json`, `save_slot_suspend.json`). They should be stored in a dedicated `saves/` directory within the user's application data folder or alongside the game executable (depending on platform conventions).

## 5. Save Triggers

Saving should be possible under the following conditions:

1.  **Start of Player Phase:** Allow manual saving from a menu option available at the beginning of the player's turn. An optional auto-save could also occur here.
2.  **Suspend Save:** Allow the player to save the current state *at any point* (even mid-action or during enemy phase) and quit the game. This save is typically temporary and loaded automatically on next launch, often overwriting itself or being deleted after loading.
3.  **Map Save Points:** (Optional) Designated tiles on the map where the player can choose to save.

## 6. Saving Process (Pseudocode)

```pseudocode
FUNCTION save_game(slot_id: Integer) -> Boolean:
  // TDD Anchor: test_save_data_serialization

  // 1. Gather Data
  save_data = {}
  save_data["save_metadata"] = gather_metadata() // Version, timestamp, playtime
  save_data["game_state"] = GameState.get_current_state() // Chapter, turn, phase, gold
  save_data["unit_state"] = UnitManager.get_all_unit_states() // Get structured data for all active units
  save_data["map_state"] = MapManager.get_map_state() // Get object states, FoW state
  save_data["event_state"] = EventManager.get_event_state() // Get flags, completed talks, counters

  // 2. Serialize Data
  TRY:
    json_string = serialize_to_json(save_data)
  CATCH SerializationError as e:
    log_error("Failed to serialize save data for slot " + slot_id + ": " + e)
    UIManager.show_error_message("Save failed: Could not prepare data.")
    RETURN False

  // 3. Write to File
  file_path = get_save_file_path(slot_id) // e.g., "saves/save_slot_{slot_id}.json"
  TRY:
    write_string_to_file(file_path, json_string)
    UIManager.show_confirmation("Game Saved to Slot " + slot_id)
    RETURN True
  CATCH FileWriteError as e:
    log_error("Failed to write save file " + file_path + ": " + e)
    UIManager.show_error_message("Save failed: Could not write file.")
    RETURN False
END FUNCTION

FUNCTION gather_metadata() -> Dictionary:
  metadata = {}
  metadata["save_format_version"] = "1.0"
  metadata["timestamp"] = get_current_iso_timestamp()
  metadata["playtime_seconds"] = GameState.get_total_playtime()
  RETURN metadata
END FUNCTION

// Helper functions assumed:
// serialize_to_json(data) -> String
// get_save_file_path(slot_id) -> String
// write_string_to_file(path, content)
// get_current_iso_timestamp() -> String
// GameState.get_total_playtime() -> Integer
// UIManager.show_error_message(message)
// UIManager.show_confirmation(message)
// log_error(message)
```

## 7. Loading Process (Pseudocode)

```pseudocode
FUNCTION load_game(slot_id: Integer) -> Boolean:
  file_path = get_save_file_path(slot_id)

  // 1. Read File
  TRY:
    json_string = read_string_from_file(file_path)
  CATCH FileNotFoundError:
    log_warning("Save file not found: " + file_path)
    UIManager.show_error_message("Load failed: Save file for slot " + slot_id + " not found.")
    RETURN False
  CATCH FileReadError as e:
    log_error("Failed to read save file " + file_path + ": " + e)
    UIManager.show_error_message("Load failed: Could not read save file.")
    RETURN False

  // 2. Deserialize Data
  TRY:
    loaded_data = deserialize_from_json(json_string)
  CATCH DeserializationError as e:
    log_error("Failed to parse save file " + file_path + ": " + e)
    UIManager.show_error_message("Load failed: Save file is corrupted or invalid.")
    // TDD Anchor: test_load_corrupted_file (Ensure this path is handled)
    RETURN False

  // 3. Validate Data
  // TDD Anchor: test_save_data_validation
  IF NOT validate_save_data(loaded_data):
    log_error("Save data validation failed for file: " + file_path)
    UIManager.show_error_message("Load failed: Save data is invalid or incompatible.")
    RETURN False

  // 4. Clear Current State (Prepare for loading)
  GameState.reset_state()
  UnitManager.clear_all_units()
  MapManager.reset_map()
  EventManager.reset_events()
  // ... reset other relevant systems

  // 5. Restore State
  TRY:
    // TDD Anchor: test_game_state_restoration (Implicitly tested by components)
    GameState.restore_state(loaded_data["game_state"])
    // TDD Anchor: test_unit_state_restoration
    UnitManager.restore_all_units(loaded_data["unit_state"])
    // TDD Anchor: test_map_state_restoration
    MapManager.restore_map_state(loaded_data["map_state"])
    // TDD Anchor: test_event_state_restoration
    EventManager.restore_event_state(loaded_data["event_state"])

    // If loading a suspend save, potentially delete it now
    IF is_suspend_slot(slot_id):
      delete_file(file_path)

    UIManager.show_confirmation("Game Loaded from Slot " + slot_id)
    // TDD Anchor: test_full_save_load_cycle (Verify state matches after this point)
    RETURN True
  CATCH StateRestorationError as e:
    log_critical("Critical error during state restoration from " + file_path + ": " + e)
    UIManager.show_error_message("Load failed: A critical error occurred while restoring game state. Returning to title screen.")
    // Attempt to return to a safe state (e.g., title screen)
    go_to_title_screen()
    RETURN False
END FUNCTION

FUNCTION validate_save_data(data: Dictionary) -> Boolean:
  // Basic checks - expand as needed
  IF "save_metadata" NOT IN data OR "save_format_version" NOT IN data["save_metadata"]:
    RETURN False
  // Check version compatibility (allow for backward compatibility if needed)
  IF data["save_metadata"]["save_format_version"] != "1.0":
     log_warning("Attempting to load incompatible save version: " + data["save_metadata"]["save_format_version"])
     // Decide on compatibility strategy - for now, reject different versions
     RETURN False
  IF "game_state" NOT IN data OR "unit_state" NOT IN data OR "map_state" NOT IN data OR "event_state" NOT IN data:
    RETURN False
  // Add more specific checks: e.g., ensure lists are lists, required fields exist
  IF TYPE(data["unit_state"]) IS NOT List:
      RETURN False
  // ... more validation ...
  RETURN True
END FUNCTION

// Helper functions assumed:
// read_string_from_file(path) -> String
// deserialize_from_json(string) -> Dictionary
// GameState.reset_state()
// UnitManager.clear_all_units()
// MapManager.reset_map()
// EventManager.reset_events()
// GameState.restore_state(data)
// UnitManager.restore_all_units(data)
// MapManager.restore_map_state(data)
// EventManager.restore_event_state(data)
// is_suspend_slot(slot_id) -> Boolean
// delete_file(path)
// go_to_title_screen()
// log_warning(message)
// log_critical(message)
```

## 8. Error Handling

*   **Missing Save File:** `load_game` should detect this (e.g., `FileNotFoundError`), inform the user via the UI, and return `False`. The UI should handle this by perhaps disabling the load button for that slot or showing an "Empty" status.
    *   **[TDD Anchor: test_load_missing_file]**
*   **Corrupted/Invalid Save File:** If JSON parsing fails or `validate_save_data` returns `False`, `load_game` should inform the user (e.g., "File is corrupted") and return `False`. The system might offer the user the option to delete the corrupted file.
    *   **[TDD Anchor: test_load_corrupted_file]**
*   **File I/O Errors:** Handle potential errors during file writing (`save_game`) or reading (`load_game`). Inform the user of the failure.
*   **State Restoration Errors:** If an error occurs *after* validation while trying to apply the loaded state (e.g., an invalid unit ID is encountered that passed basic validation but fails during instantiation), log a critical error. The game should ideally revert to a safe state (like the main menu/title screen) rather than continuing with partially loaded, potentially unstable state.

## 9. Integration Points

The `SaveLoadSystem` (or functions within it) will need to interact with:

*   **`GameState`:** To get/set global state like chapter, turn, phase, gold, playtime.
*   **`UnitManager`:** To get detailed state of all active units (stats, inventory, position, status, etc.) and to recreate units during load.
*   **`MapManager`:** To get/set the state of interactive map objects (chests, ballistae, doors) and potentially the Fog of War visibility map.
*   **`EventManager`:** To get/set the state of global event flags, completed conversations, and potentially active timed events or counters.
*   **`ItemManager`:** (Indirectly) Ensures item definitions are available. If items have unique instance data (like unique weapon IDs or modified stats), the `ItemManager` might need to be involved in saving/loading item instances, likely coordinated via the `UnitManager`'s inventory handling.
*   **`UIManager`:** To display save/load menus, provide feedback (saving..., loading..., success, failure messages), and potentially get user input for slot selection or confirmation.
*   **`InputHandler`:** To trigger save/load actions based on user input (e.g., pressing Start and selecting Save).

## 10. TDD Anchors

The following components should have dedicated tests:

*   **`test_save_data_serialization`**: Verify that calling `save_game` (or its internal data gathering logic) produces a correctly structured dictionary/JSON matching the expected format for a known game state.
*   **`test_save_data_validation`**: Test the `validate_save_data` function with valid data, corrupted data (missing keys, wrong types), and data from different (incompatible) versions.
*   **`test_unit_state_restoration`**: Create a set of units, save the state, load it, and verify that the `UnitManager` correctly restores all units with their exact HP, stats, inventory (including item durability/uses), status effects, position, fatigue, etc.
*   **`test_map_state_restoration`**: Set specific states for map objects (e.g., open chest, damaged ballista), save, load, and verify `MapManager` restores these states correctly. Test Fog of War restoration if implemented.
*   **`test_event_state_restoration`**: Set specific event flags/counters, complete a talk event, save, load, and verify `EventManager` restores this state accurately.
*   **`test_full_save_load_cycle`**: Perform a full save and load operation on a complex game state and verify key aspects across multiple systems (e.g., player gold, a specific unit's HP, an event flag, a chest's status) are correctly restored.
*   **`test_load_corrupted_file`**: Ensure `load_game` handles JSON parsing errors or validation failures gracefully (returns `False`, logs error, doesn't crash).
*   **`test_load_missing_file`**: Ensure `load_game` handles non-existent save files gracefully (returns `False`, logs warning/info).
*   **`test_suspend_save_behavior`**: If suspend save is implemented, test saving mid-turn (e.g., after one unit moved but before others), loading, and ensuring the game resumes exactly where it left off (correct unit has acted, phase is correct). Test that the suspend save file is handled correctly (e.g., deleted after successful load).

## 11. Future Considerations

*   **Compression:** If save files become very large, consider compressing the JSON data (e.g., using zlib or gzip).
*   **Backward Compatibility:** Implement robust version checking and potentially migration logic if the save format changes significantly in the future.
*   **Cloud Saves:** Integration with platform-specific cloud storage (Steam Cloud, etc.).
*   **Checksums:** Add checksums to save files to detect corruption more reliably than basic validation alone.