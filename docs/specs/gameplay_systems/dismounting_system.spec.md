# Specification: Dismounting System

**Version:** 1.0
**Author:** AI Assistant
**Date:** 2025-04-06

## 1. Overview

This document outlines the specifications for the Dismounting system in the game, based on the mechanics observed in Fire Emblem: Thracia 776. This system allows mounted units to switch between mounted and dismounted states, affecting their stats, movement, weapon usability, and interactions with terrain and certain weapons.

## 2. Functional Requirements

### 2.1. Eligibility
- **FR2.1.1:** Only units belonging to specific mounted classes (e.g., Lance Knight, Pegasus Knight, Wyvern Rider, Lord [Leif]) shall have the ability to Mount and Dismount.
- **FR2.1.2:** Units must possess the `CanMount` class attribute to be eligible.

### 2.2. Commands
- **FR2.2.1:** Eligible mounted units shall have a "Dismount" command available in their action menu when outdoors or on specific transition tiles.
- **FR2.2.2:** Eligible dismounted units (originally mounted class) shall have a "Mount" command available in their action menu when outdoors or on specific transition tiles.
- **FR2.2.3:** Using either the "Mount" or "Dismount" command shall consume the unit's action for the turn.

### 2.3. Automatic Dismounting (Indoors)
- **FR2.3.1:** All mounted units shall be automatically dismounted at the start of any chapter designated as "Indoor".
- **FR2.3.2:** Mounted units attempting to move onto an "Indoor" terrain tile from an "Outdoor" tile must first use the "Dismount" command. They cannot enter indoor tiles while mounted.

### 2.4. Automatic Mounting (Prep Screen)
- **FR2.4.1:** Units that were dismounted during an indoor chapter shall automatically be mounted during the preparation screen for the subsequent outdoor chapter (behavior noted from Forseti's Cut patch, potentially applicable).

### 2.5. State Changes (Dismounting)
- **FR2.5.1:** Upon dismounting, the unit's class shall effectively change to its designated dismounted counterpart (e.g., Knight -> Dismounted Knight).
- **FR2.5.2:** The unit's current stats shall be adjusted based on the difference between mounted and dismounted class base stats or specific dismount modifiers. (Exact stat changes need data definition, often involves slight reduction in some stats).
- **FR2.5.3:** The unit's Movement (Mov) stat shall be reduced to the value defined for their dismounted class.
- **FR2.5.4:** The unit's movement type shall change from their mounted type (e.g., Cavalry, Flying) to Infantry. This affects terrain movement costs.
- **FR2.5.5:** The unit shall gain the ability to benefit from terrain bonuses (Avoid, Defense) applicable to Infantry units (e.g., Forests, Forts).
- **FR2.5.6:** The unit shall lose susceptibility to weapons effective against mounted units (e.g., Horseslayer, Anti-Air bows).

### 2.6. Weapon Restrictions (Dismounted)
- **FR2.6.1:** Dismounted units shall lose the ability to equip or use their primary mounted weapons (typically Lances and Axes for most cavalry).
- **FR2.6.2:** Most dismounted cavalry units shall only be able to equip and use Swords. If they possess no swords, they may become unarmed.
- **FR2.6.3:** Specific class exceptions exist (e.g., Bow Knights continue using Bows when dismounted). These exceptions must be defined per class.
- **FR2.6.4:** The game must automatically unequip restricted weapons and attempt to equip a valid weapon (e.g., a sword) if available upon dismounting.

### 2.7. State Changes (Mounting)
- **FR2.7.1:** Upon mounting, the unit's class shall revert to their original mounted class.
- **FR2.7.2:** The unit's stats shall revert to their normal mounted values (adjusting for any changes that occurred while dismounted, like level-ups).
- **FR2.7.3:** The unit's Movement (Mov) stat shall be restored to their mounted value.
- **FR2.7.4:** The unit's movement type shall revert to their mounted type.
- **FR2.7.5:** The unit shall lose the ability to benefit from Infantry-specific terrain bonuses.
- **FR2.7.6:** The unit shall regain susceptibility to weapons effective against mounted units.
- **FR2.7.7:** The unit shall regain the ability to equip and use their primary mounted weapons (Lances, Axes, etc.). The game may attempt to re-equip the previously equipped mounted weapon if still available.

## 3. Data Structures

### 3.1. Unit Data
- `unit.is_mounted`: Boolean (True/False)
- `unit.mounted_class_id`: Identifier for the unit's original mounted class.
- `unit.dismounted_class_id`: Identifier for the unit's dismounted class counterpart.
- `unit.current_stats`: Dictionary holding current HP, Str, Mag, Skl, Spd, Luk, Def, Con, Mov.
- `unit.current_movement_type`: Enum (Infantry, Cavalry, Flying, etc.)

### 3.2. Class Data
- `class.can_mount`: Boolean
- `class.mounted_equivalent_id`: (For dismounted classes) ID of the corresponding mounted class.
- `class.dismounted_equivalent_id`: (For mounted classes) ID of the corresponding dismounted class.
- `class.base_stats`: Dictionary of base stats for the class.
- `class.movement_type`: Enum
- `class.mov`: Base movement points.
- `class.usable_weapon_types_mounted`: List of weapon types usable when mounted.
- `class.usable_weapon_types_dismounted`: List of weapon types usable when dismounted.
- `class.dismount_stat_modifiers`: Optional dictionary defining specific stat changes upon dismounting (e.g., `{ "Mov": -2 }`).

### 3.3. Map Data
- `map.is_indoor`: Boolean

## 4. Pseudocode Modules

### 4.1. `DismountingSystem`

```pseudocode
CLASS DismountingSystem

  // --- Properties ---
  PROPERTY game_state_manager
  PROPERTY unit_system
  PROPERTY map_system
  PROPERTY data_provider // Access to class data

  // --- Methods ---

  METHOD can_dismount(unit_id) -> Boolean
    // TDD_ANCHOR: test_can_dismount_eligibility
    unit = unit_system.get_unit(unit_id)
    IF NOT unit OR NOT unit.is_mounted THEN RETURN FALSE

    mounted_class = data_provider.get_class(unit.mounted_class_id)
    IF NOT mounted_class.can_mount THEN RETURN FALSE

    // Optional: Check if on valid terrain for dismounting (e.g., not mid-air for fliers?)
    // Optional: Check if indoors (dismount is mandatory, not optional command)
    current_tile = map_system.get_tile(unit.position)
    IF map_system.is_tile_indoors(current_tile) THEN RETURN FALSE // Cannot use command if already forced dismount

    RETURN TRUE
  END METHOD

  METHOD can_mount(unit_id) -> Boolean
    // TDD_ANCHOR: test_can_mount_eligibility
    unit = unit_system.get_unit(unit_id)
    IF NOT unit OR unit.is_mounted THEN RETURN FALSE

    // Check if the unit *was* originally a mounted class
    original_class = data_provider.get_class(unit.mounted_class_id)
    IF NOT original_class OR NOT original_class.can_mount THEN RETURN FALSE

    // Check if on valid terrain for mounting (outdoors)
    current_tile = map_system.get_tile(unit.position)
    IF map_system.is_tile_indoors(current_tile) THEN RETURN FALSE

    RETURN TRUE
  END METHOD

  METHOD execute_dismount(unit_id)
    // TDD_ANCHOR: test_execute_dismount_state_changes
    IF NOT can_dismount(unit_id) THEN RETURN FAILURE("Unit cannot dismount")

    unit = unit_system.get_unit(unit_id)
    mounted_class = data_provider.get_class(unit.mounted_class_id)
    dismounted_class = data_provider.get_class(mounted_class.dismounted_equivalent_id)

    // 1. Update State Flag
    unit.is_mounted = FALSE

    // 2. Apply Stat Changes (adjust based on class bases or modifiers)
    // TDD_ANCHOR: test_dismount_stat_adjustment
    // Example: Apply specific modifiers if defined
    IF mounted_class.dismount_stat_modifiers THEN
        FOR stat, change IN mounted_class.dismount_stat_modifiers
            unit.current_stats[stat] += change
        END FOR
    ELSE // Or adjust based on difference in class bases (more complex)
        // Calculate difference between mounted_class.base_stats and dismounted_class.base_stats
        // Apply difference to unit.current_stats (careful not to overwrite growths/current values)
        // Simpler: Just set Mov directly
        unit.current_stats["Mov"] = dismounted_class.mov
    END IF
    // Ensure stats don't go below minimums (e.g., 0 or 1)

    // 3. Update Movement Type
    // TDD_ANCHOR: test_dismount_movement_type_change
    unit.current_movement_type = dismounted_class.movement_type

    // 4. Handle Weapon Restrictions
    // TDD_ANCHOR: test_dismount_weapon_restriction
    handle_weapon_restriction(unit, dismounted_class.usable_weapon_types_dismounted)

    // 5. Consume Action
    unit_system.set_unit_action_taken(unit_id)

    // 6. Update Visuals (sprite change, etc.)
    game_state_manager.notify_visual_update(unit_id, "dismounted")

    RETURN SUCCESS
  END METHOD

  METHOD execute_mount(unit_id)
    // TDD_ANCHOR: test_execute_mount_state_changes
    IF NOT can_mount(unit_id) THEN RETURN FAILURE("Unit cannot mount")

    unit = unit_system.get_unit(unit_id)
    mounted_class = data_provider.get_class(unit.mounted_class_id)
    dismounted_class = data_provider.get_class(mounted_class.dismounted_equivalent_id) // Need this for reversing changes

    // 1. Update State Flag
    unit.is_mounted = TRUE

    // 2. Revert Stat Changes
    // TDD_ANCHOR: test_mount_stat_reversion
    // Example: Reverse specific modifiers if defined
    IF mounted_class.dismount_stat_modifiers THEN
        FOR stat, change IN mounted_class.dismount_stat_modifiers
            unit.current_stats[stat] -= change // Reverse the change
        END FOR
    ELSE // Or revert based on class bases
        // Recalculate stats based on mounted class (complex)
        // Simpler: Just set Mov directly
        unit.current_stats["Mov"] = mounted_class.mov
    END IF
    // Ensure stats don't exceed caps

    // 3. Revert Movement Type
    // TDD_ANCHOR: test_mount_movement_type_reversion
    unit.current_movement_type = mounted_class.movement_type

    // 4. Handle Weapon Access Restoration
    // TDD_ANCHOR: test_mount_weapon_access_restored
    // Allow equipping mounted weapons again. Optionally try to re-equip previous weapon.
    // This might be handled implicitly by allowing access, or explicitly re-equip here.
    // Let InventorySystem handle equipping based on available types.

    // 5. Consume Action
    unit_system.set_unit_action_taken(unit_id)

    // 6. Update Visuals
    game_state_manager.notify_visual_update(unit_id, "mounted")

    RETURN SUCCESS
  END METHOD

  METHOD handle_automatic_dismount_on_map_load(map_id)
    // TDD_ANCHOR: test_auto_dismount_indoor_map
    map_data = data_provider.get_map(map_id)
    IF map_data.is_indoor THEN
      all_units = unit_system.get_all_player_units()
      FOR unit IN all_units
        IF unit.is_mounted AND data_provider.get_class(unit.mounted_class_id).can_mount THEN
          // Apply dismount state changes WITHOUT consuming action
          // Similar logic to execute_dismount but without action cost/command check
          apply_dismount_state(unit.id, FALSE) // FALSE indicates no action cost
        END IF
      END FOR
    END IF
  END METHOD

  METHOD handle_automatic_mount_on_prep_load(map_id)
      // TDD_ANCHOR: test_auto_mount_prep_screen_outdoor
      map_data = data_provider.get_map(map_id)
      IF NOT map_data.is_indoor THEN
          all_units = unit_system.get_all_player_units_in_roster() // Or however roster is accessed
          FOR unit IN all_units
              original_class = data_provider.get_class(unit.mounted_class_id)
              IF NOT unit.is_mounted AND original_class AND original_class.can_mount THEN
                  // Apply mount state changes
                  apply_mount_state(unit.id)
              END IF
          END FOR
      END IF
  END METHOD

  PRIVATE METHOD apply_dismount_state(unit_id, consumes_action)
      // Internal logic shared by execute_dismount and automatic dismount
      // Applies state changes (stats, movement, weapons)
      // If consumes_action is TRUE, mark action as taken
      unit = unit_system.get_unit(unit_id)
      mounted_class = data_provider.get_class(unit.mounted_class_id)
      dismounted_class = data_provider.get_class(mounted_class.dismounted_equivalent_id)

      unit.is_mounted = FALSE
      // Apply stat changes (Mov, etc.)
      unit.current_stats["Mov"] = dismounted_class.mov
      // Apply other potential stat adjustments based on class diff or modifiers
      unit.current_movement_type = dismounted_class.movement_type
      handle_weapon_restriction(unit, dismounted_class.usable_weapon_types_dismounted)

      IF consumes_action THEN
          unit_system.set_unit_action_taken(unit_id)
      END IF
      game_state_manager.notify_visual_update(unit_id, "dismounted")
  END METHOD

  PRIVATE METHOD apply_mount_state(unit_id)
      // Internal logic shared by execute_mount and automatic mount
      unit = unit_system.get_unit(unit_id)
      mounted_class = data_provider.get_class(unit.mounted_class_id)

      unit.is_mounted = TRUE
      // Revert stat changes (Mov, etc.)
      unit.current_stats["Mov"] = mounted_class.mov
      // Revert other potential stat adjustments
      unit.current_movement_type = mounted_class.movement_type
      // Weapon access restored implicitly by state change

      game_state_manager.notify_visual_update(unit_id, "mounted")
  END METHOD

  PRIVATE METHOD handle_weapon_restriction(unit, allowed_weapon_types)
    // TDD_ANCHOR: test_weapon_auto_unequip_on_dismount
    equipped_item = unit_system.get_equipped_item(unit.id)
    IF equipped_item AND data_provider.get_item(equipped_item.id).type NOT IN allowed_weapon_types THEN
      unit_system.unequip_item(unit.id)
      // Attempt to equip a valid weapon (e.g., first sword found)
      // TDD_ANCHOR: test_weapon_auto_equip_valid_on_dismount
      FOR item IN unit.inventory
        item_data = data_provider.get_item(item.id)
        IF item_data.type IN allowed_weapon_types THEN
          unit_system.equip_item(unit.id, item.id)
          BREAK
        END IF
      END FOR
    END IF
  END METHOD

END CLASS
```

## 5. Integration Points

- **Unit System:** Needs to store `is_mounted` state, mounted/dismounted class IDs, apply stat changes, manage action consumption.
- **Class System (Data Provider):** Needs to define `can_mount`, mounted/dismounted equivalents, movement types, Mov stats, weapon type restrictions per state, and potentially dismount stat modifiers.
- **Map System:** Needs to identify indoor/outdoor tiles and chapters.
- **Action Handler:** Needs to add "Mount" and "Dismount" commands to the menu for eligible units.
- **Inventory System:** Needs to handle weapon equipping/unequipping based on allowed types for the current mounted state.
- **Combat System:** Needs to consider the unit's current mounted state for weapon effectiveness (e.g., Horseslayer) and terrain bonuses.
- **Turn Manager / Game State:** Needs to trigger automatic dismounting/mounting on map/prep load.
- **UI:** Needs to display the correct unit sprite, stats, and available commands based on the mounted state.

## 6. Open Questions / Future Considerations

- **Stat Adjustment Details:** Precisely how are stats adjusted? Is it based purely on class base differences, or are there fixed modifiers? Needs specific data from Thracia 776. For now, assuming Mov changes based on class definition is the primary effect.
- **Flying Units:** Do flying units have specific dismount rules (e.g., cannot dismount over impassable terrain)? Assumed they follow general rules for now.
- **Canto Interaction:** Does dismounting/mounting interact with Canto? (Research suggests Canto is generally disabled after combat actions, Mount/Dismount are actions, so likely no Canto after using them).
- **Forseti's Cut Specifics:** Is auto-mounting on prep screen a vanilla feature or specific to the patch? Assuming it's intended behavior for now.
- **Rescue Interaction:** How does mounted/dismounted state affect Rescue/Aid calculations? (Research suggests Aid is based on Con, but mounted state might influence penalties when carrying). This spec focuses on the Mount/Dismount action itself.