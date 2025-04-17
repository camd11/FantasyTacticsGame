# GUI Pseudocode - Fantasy Tactics Game

## Overview

This document outlines the pseudocode structure for the core GUI components based on `gui_specification.md`. It defines the main modules, their responsibilities, key functions, interaction logic, and integration points with the game engine. TDD anchors are included to guide test development.

## Core Modules/Classes

### 1. GUIManager

*   **Responsibility:** Orchestrates all GUI components, manages overall GUI state (e.g., selected unit, current action), and acts as the primary interface with the Game Engine.
*   **Dependencies:** MapView, UnitInfoPanel, TerrainInfoPanel, ActionMenu, CombatPreview, InventoryManager, SystemMenu, InputHandler, GameEngineAPI.

```pseudocode
CLASS GUIManager:
    // Properties
    PROPERTY game_engine_api  // Interface to send commands and receive updates
    PROPERTY map_view
    PROPERTY unit_info_panel
    PROPERTY terrain_info_panel
    PROPERTY action_menu
    PROPERTY combat_preview
    PROPERTY inventory_manager
    PROPERTY system_menu
    PROPERTY input_handler
    PROPERTY current_game_state // Holds data like unit positions, turn phase, etc.
    PROPERTY selected_unit_id
    PROPERTY current_action_context // e.g., 'MOVING', 'SELECTING_ACTION', 'SELECTING_TARGET', 'IDLE'
    PROPERTY available_moves // Cache for selected unit's move range
    PROPERTY available_actions // Cache for selected unit's actions
    PROPERTY action_range // Cache for selected action's range

    // Methods
    METHOD initialize(engine_api_instance):
        // TDD: Test GUIManager initialization with a mock engine API
        SET self.game_engine_api = engine_api_instance
        CREATE MapView instance -> self.map_view
        CREATE UnitInfoPanel instance -> self.unit_info_panel
        CREATE TerrainInfoPanel instance -> self.terrain_info_panel
        CREATE ActionMenu instance -> self.action_menu
        CREATE CombatPreview instance -> self.combat_preview
        CREATE InventoryManager instance -> self.inventory_manager
        CREATE SystemMenu instance -> self.system_menu
        CREATE InputHandler instance -> self.input_handler(self) // Pass self for callbacks

        // Subscribe to game engine updates
        self.game_engine_api.register_state_update_callback(self.update_game_state)
        // TDD: Test that the callback is registered correctly

        // Initial fetch of game state
        self.update_game_state(self.game_engine_api.get_initial_state())

    METHOD update_game_state(new_state):
        // TDD: Test updating GUI components based on a new game state
        SET self.current_game_state = new_state
        self.map_view.update_data(new_state.map_data, new_state.unit_list)
        // Potentially update other panels if needed based on state changes (e.g., turn change)
        self.render_all()

    METHOD render_all():
        // TDD: Test that all relevant components are called to render
        CLEAR screen or relevant areas
        self.map_view.render()
        self.unit_info_panel.render()
        self.terrain_info_panel.render()
        self.action_menu.render() // Renders only if visible
        self.combat_preview.render() // Renders only if visible
        self.inventory_manager.render() // Renders only if visible
        self.system_menu.render() // Renders only if visible
        DISPLAY rendered output

    METHOD handle_input_event(event_type, details):
        // TDD: Test routing map clicks to the correct handler based on state
        // TDD: Test routing menu clicks to the correct handler
        // Called by InputHandler
        SWITCH event_type:
            CASE 'MAP_CLICK':
                self.process_map_click(details.x, details.y)
            CASE 'ACTION_MENU_SELECT':
                self.process_action_selection(details.action)
            CASE 'SYSTEM_MENU_SELECT':
                self.process_system_menu_selection(details.option)
            CASE 'INVENTORY_ACTION':
                self.process_inventory_action(details.action, details.item_id)
            CASE 'KEY_PRESS':
                self.process_key_press(details.key)
            CASE 'CANCEL':
                self.process_cancel_action()
            // Add other event types as needed (e.g., HOVER)

    METHOD process_map_click(x, y):
        // TDD: Test selecting a unit when clicking on it
        // TDD: Test moving a selected unit when clicking within range
        // TDD: Test selecting a target after choosing an action
        // TDD: Test deselecting unit when clicking empty space (if applicable)
        LET target_tile = self.map_view.get_tile_at_coords(x, y)
        LET unit_on_tile = self.current_game_state.get_unit_at(target_tile.x, target_tile.y)

        SWITCH self.current_action_context:
            CASE 'IDLE':
                IF unit_on_tile IS NOT NULL AND unit_on_tile.is_player_controllable() AND unit_on_tile.can_act():
                    self.select_unit(unit_on_tile.id)
                ELSE:
                    // Update terrain info panel for the clicked tile
                    LET terrain_data = self.game_engine_api.get_terrain_info(target_tile.x, target_tile.y)
                    self.terrain_info_panel.display_terrain_info(terrain_data)
                    // Update unit info panel if a unit (any unit) is on the tile
                    IF unit_on_tile IS NOT NULL:
                        LET unit_data = self.game_engine_api.get_unit_details(unit_on_tile.id)
                        self.unit_info_panel.display_unit_info(unit_data)
                    ELSE:
                        self.unit_info_panel.clear_panel()
            CASE 'UNIT_SELECTED':
                IF target_tile IS IN self.available_moves:
                    self.send_command_to_engine('MOVE_UNIT', { unit_id: self.selected_unit_id, target_x: target_tile.x, target_y: target_tile.y })
                    // Engine should respond with state update including available actions at new location
                    SET self.current_action_context = 'AWAITING_POST_MOVE_STATE'
                ELSE:
                    // Clicked outside move range, potentially deselect or handle as map inspection
                    self.deselect_unit() // Or re-select if clicking another unit
                    self.process_map_click(x, y) // Re-process click in IDLE state
            CASE 'SELECTING_TARGET':
                IF target_tile IS IN self.action_range:
                    LET target_unit_id = unit_on_tile.id IF unit_on_tile IS NOT NULL ELSE NULL
                    // Validate if the target is valid for the action (e.g., enemy for attack, ally for heal)
                    IF self.is_valid_target(self.pending_action, unit_on_tile):
                        IF self.pending_action == 'ATTACK':
                             LET preview_data = self.game_engine_api.get_combat_preview(self.selected_unit_id, target_unit_id)
                             self.combat_preview.show_preview(preview_data)
                             SET self.current_action_context = 'CONFIRMING_ACTION'
                             SET self.pending_target = target_unit_id // Store target for confirmation
                        ELSE:
                             // Execute non-attack actions directly (or add confirmation step if needed)
                             self.send_command_to_engine('EXECUTE_ACTION', { unit_id: self.selected_unit_id, action_type: self.pending_action, target_id: target_unit_id })
                             self.reset_selection_state()
                    ELSE:
                        // Invalid target clicked, maybe provide feedback
                        PRINT "Invalid target"
                ELSE:
                    // Clicked outside action range, potentially cancel target selection
                    self.cancel_action_targeting()
            CASE 'CONFIRMING_ACTION':
                 // Clicking again on the target (or a confirm button) confirms
                 IF unit_on_tile AND unit_on_tile.id == self.pending_target:
                     self.send_command_to_engine('EXECUTE_ACTION', { unit_id: self.selected_unit_id, action_type: self.pending_action, target_id: self.pending_target })
                     self.reset_selection_state()
                 ELSE:
                     // Clicked elsewhere, cancel confirmation
                     self.cancel_action_targeting()

            // Add other states like 'TRADE_SELECT_PARTNER', 'INVENTORY_OPEN', etc.

    METHOD select_unit(unit_id):
        // TDD: Test selecting a unit updates state and fetches move/action data
        SET self.selected_unit_id = unit_id
        SET self.current_action_context = 'UNIT_SELECTED'
        LET unit_data = self.game_engine_api.get_unit_details(unit_id)
        self.unit_info_panel.display_unit_info(unit_data)
        // Fetch valid moves from engine
        SET self.available_moves = self.game_engine_api.get_valid_moves(unit_id)
        self.map_view.show_movement_overlay(self.available_moves)
        self.action_menu.hide_menu()
        self.combat_preview.hide_preview()
        self.render_all()

    METHOD deselect_unit():
        // TDD: Test deselecting a unit clears relevant state and overlays
        SET self.selected_unit_id = NULL
        SET self.current_action_context = 'IDLE'
        SET self.available_moves = []
        SET self.available_actions = []
        self.map_view.hide_overlays()
        self.unit_info_panel.clear_panel() // Or show info for tile under cursor
        self.action_menu.hide_menu()
        self.combat_preview.hide_preview()
        self.render_all()

    METHOD process_action_selection(action):
        // TDD: Test selecting 'Wait' action sends command immediately
        // TDD: Test selecting 'Attack' action changes state and shows range
        // TDD: Test selecting 'Item' action opens inventory screen/menu
        SET self.pending_action = action
        SWITCH action:
            CASE 'WAIT':
                self.send_command_to_engine('EXECUTE_ACTION', { unit_id: self.selected_unit_id, action_type: 'WAIT' })
                self.reset_selection_state()
            CASE 'ATTACK':
                SET self.current_action_context = 'SELECTING_TARGET'
                SET self.action_range = self.game_engine_api.get_action_range(self.selected_unit_id, 'ATTACK')
                self.map_view.show_action_overlay(self.action_range)
                self.action_menu.hide_menu()
                self.render_all()
            CASE 'ITEM':
                SET self.current_action_context = 'INVENTORY_OPEN'
                LET inventory_data = self.game_engine_api.get_unit_inventory(self.selected_unit_id)
                self.inventory_manager.show_inventory(inventory_data, self.selected_unit_id)
                self.action_menu.hide_menu()
                self.render_all()
            CASE 'TRADE':
                 SET self.current_action_context = 'TRADE_SELECT_PARTNER'
                 SET self.action_range = self.game_engine_api.get_action_range(self.selected_unit_id, 'TRADE') // Adjacent tiles
                 self.map_view.show_action_overlay(self.action_range)
                 self.action_menu.hide_menu()
                 self.render_all()
            // Add cases for Staff, Capture, Rescue, Dance, etc.
            DEFAULT:
                PRINT "Action not yet implemented: ", action

    METHOD process_system_menu_selection(option):
        // TDD: Test selecting 'End Turn' sends the correct command
        SWITCH option:
            CASE 'END_TURN':
                self.send_command_to_engine('END_PLAYER_PHASE', {})
                self.reset_selection_state() // Ensure no unit is selected
            CASE 'UNIT_LIST':
                // Show unit list screen (details TBD)
                PRINT "Show Unit List"
            CASE 'OPTIONS':
                // Show options screen (details TBD)
                PRINT "Show Options"
            // Add Save, Load, Quit etc.

    METHOD process_inventory_action(action, item_id):
        // TDD: Test using a consumable item sends the correct command
        // TDD: Test equipping an item sends the correct command
        SWITCH action:
            CASE 'USE':
                self.send_command_to_engine('EXECUTE_ACTION', { unit_id: self.selected_unit_id, action_type: 'USE_ITEM', item_id: item_id })
                self.reset_selection_state() // Using item usually ends turn
            CASE 'EQUIP':
                self.send_command_to_engine('EQUIP_ITEM', { unit_id: self.selected_unit_id, item_id: item_id })
                // Update unit info panel after equip potentially? Or wait for state update.
                self.inventory_manager.hide_inventory() // Close inventory after equipping
                SET self.current_action_context = 'IDLE' // Or back to 'UNIT_SELECTED' if equip doesn't end turn
            CASE 'CLOSE':
                 self.inventory_manager.hide_inventory()
                 // Return to previous state, likely 'ACTION_MENU' or 'UNIT_SELECTED'
                 // Need to restore context properly
                 SET self.current_action_context = 'ACTION_MENU' // Assume returning to action menu
                 self.action_menu.show_menu(self.selected_unit_id, self.available_actions) // Re-show menu


    METHOD process_key_press(key):
        // TDD: Test arrow keys move cursor when idle
        // TDD: Test cancel key triggers cancel action
        // TDD: Test confirm key triggers selection/confirmation
        SWITCH self.current_action_context:
            CASE 'IDLE':
                IF key IS ArrowKey:
                    self.map_view.move_cursor(key_direction)
                    // Update info panels based on new cursor position
                    LET tile_data = self.game_engine_api.get_terrain_info(cursor.x, cursor.y)
                    self.terrain_info_panel.display_terrain_info(tile_data)
                    LET unit_on_tile = self.current_game_state.get_unit_at(cursor.x, cursor.y)
                    IF unit_on_tile:
                         LET unit_data = self.game_engine_api.get_unit_details(unit_on_tile.id)
                         self.unit_info_panel.display_unit_info(unit_data)
                    ELSE:
                         self.unit_info_panel.clear_panel()

                ELSE IF key IS ConfirmKey: // e.g., Enter/Space
                    // Simulate a map click at the cursor position
                    self.process_map_click(cursor.x, cursor.y)
                ELSE IF key IS CancelKey: // e.g., Esc/Backspace
                    // No action to cancel when idle
                    PASS
                ELSE IF key IS EndTurnKey: // e.g., 'E'
                    self.send_command_to_engine('END_PLAYER_PHASE', {})

            CASE 'UNIT_SELECTED':
                 IF key IS ArrowKey:
                     // Move selection within available move tiles? Or move map cursor? Define behavior.
                     // Option 1: Move cursor within blue tiles
                     // Option 2: Move map cursor freely, deselect unit?
                     PRINT "Arrow key navigation during move selection TBD"
                 ELSE IF key IS ConfirmKey:
                     // Confirm move to cursor position if it's valid
                     IF self.map_view.cursor_pos IN self.available_moves:
                         self.process_map_click(cursor.x, cursor.y)
                 ELSE IF key IS CancelKey:
                     self.deselect_unit()

            CASE 'ACTION_MENU':
                 IF key IS ArrowKey:
                     self.action_menu.navigate(key_direction)
                 ELSE IF key IS ConfirmKey:
                     LET selected_action = self.action_menu.get_selected_action()
                     self.process_action_selection(selected_action)
                 ELSE IF key IS CancelKey:
                     // Go back from action menu to movement selection (if move is cancellable)
                     self.cancel_action_menu() // Needs logic to potentially revert move

            CASE 'SELECTING_TARGET':
                 IF key IS ArrowKey:
                     // Move cursor among valid targets? Or free cursor?
                     PRINT "Arrow key navigation during target selection TBD"
                 ELSE IF key IS ConfirmKey:
                     // Confirm target at cursor position if valid
                     LET unit_on_tile = self.current_game_state.get_unit_at(cursor.x, cursor.y)
                     IF self.map_view.cursor_pos IN self.action_range AND self.is_valid_target(self.pending_action, unit_on_tile):
                         self.process_map_click(cursor.x, cursor.y) // Will trigger preview or execution
                 ELSE IF key IS CancelKey:
                     self.cancel_action_targeting()

            // Add other contexts

    METHOD process_cancel_action():
        // TDD: Test cancelling target selection returns to action menu
        // TDD: Test cancelling action menu returns to movement phase (if possible)
        // TDD: Test cancelling movement deselects the unit
        SWITCH self.current_action_context:
            CASE 'UNIT_SELECTED':
                self.deselect_unit()
            CASE 'ACTION_MENU':
                self.cancel_action_menu()
            CASE 'SELECTING_TARGET':
                self.cancel_action_targeting()
            CASE 'CONFIRMING_ACTION':
                 self.cancel_action_targeting() // Go back to target selection
            CASE 'INVENTORY_OPEN':
                 self.inventory_manager.hide_inventory()
                 // Restore context (e.g., back to Action Menu)
                 SET self.current_action_context = 'ACTION_MENU'
                 self.action_menu.show_menu(self.selected_unit_id, self.available_actions)
            // Add other contexts

    METHOD cancel_action_menu():
         // Logic depends on whether moves are final once confirmed.
         // If moves can be undone before acting:
         // SET self.current_action_context = 'UNIT_SELECTED'
         // self.action_menu.hide_menu()
         // self.map_view.show_movement_overlay(self.available_moves)
         // ELSE (if move is final):
         self.action_menu.hide_menu()
         // Force 'Wait' action? Or just leave unit there? TBD based on game rules.
         // For now, assume we go back to unit selected state pre-move (needs engine support)
         PRINT "Cancel Action Menu logic TBD (depends on move confirmation rules)"
         // Simplest: just deselect unit if action menu is cancelled?
         self.deselect_unit()


    METHOD cancel_action_targeting():
        // TDD: Test cancelling targeting hides action overlay and shows action menu
        SET self.current_action_context = 'ACTION_MENU'
        SET self.pending_action = NULL
        SET self.pending_target = NULL
        self.map_view.hide_overlays() // Hide action range
        self.map_view.show_movement_overlay(self.available_moves) // Re-show move range (or just unit position)
        self.combat_preview.hide_preview()
        self.action_menu.show_menu(self.selected_unit_id, self.available_actions) // Re-show action menu
        self.render_all()

    METHOD reset_selection_state():
        // TDD: Test resetting state clears selection, overlays, and menus
        SET self.selected_unit_id = NULL
        SET self.current_action_context = 'IDLE'
        SET self.available_moves = []
        SET self.available_actions = []
        SET self.action_range = []
        SET self.pending_action = NULL
        SET self.pending_target = NULL
        self.map_view.hide_overlays()
        self.action_menu.hide_menu()
        self.combat_preview.hide_preview()
        self.inventory_manager.hide_inventory()
        // Don't necessarily clear info panels, they might show cursor info
        self.render_all() // Re-render in idle state

    METHOD send_command_to_engine(command, args):
        // TDD: Test that commands are correctly formatted and sent via the API
        self.game_engine_api.send_command(command, args)

    METHOD is_valid_target(action, target_unit):
        // TDD: Test target validation logic for attack, heal, etc.
        // Placeholder - Requires logic based on action type and target properties
        IF action == 'ATTACK':
            RETURN target_unit IS NOT NULL AND target_unit.is_enemy()
        ELSE IF action == 'STAFF_HEAL':
            RETURN target_unit IS NOT NULL AND target_unit.is_ally() AND target_unit.hp < target_unit.max_hp
        // ... other actions
        RETURN FALSE // Default deny


END CLASS GUIManager
```

### 2. MapView

*   **Responsibility:** Renders the map grid, terrain, units, cursor, and visual overlays (movement, attack range). Translates screen coordinates to map coordinates.
*   **Dependencies:** Graphics Library (e.g., Pygame), Asset Loader.

```pseudocode
CLASS MapView:
    // Properties
    PROPERTY map_data // Tile types, dimensions
    PROPERTY unit_list // Positions, sprites, status (acted?)
    PROPERTY terrain_tileset // Loaded terrain graphics
    PROPERTY unit_sprites // Loaded unit graphics
    PROPERTY overlays // Data for movement/action ranges { type: 'move'/'attack', tiles: [(x,y), ...] }
    PROPERTY cursor_pos // (x, y) map coordinates
    PROPERTY camera_offset // For scrolling (x, y) screen coordinates
    PROPERTY tile_size // Pixels per tile

    // Methods
    METHOD initialize(initial_map_data, initial_unit_list):
        // TDD: Test map initialization with specific dimensions and tiles
        self.load_assets() // Load terrain tileset, unit sprites
        self.update_data(initial_map_data, initial_unit_list)
        SET self.cursor_pos = (0, 0)
        SET self.camera_offset = (0, 0)
        SET self.overlays = []

    METHOD load_assets():
        // Load graphics for terrain and units
        // TDD: Test that required assets are loaded correctly
        PRINT "Loading map assets..."

    METHOD update_data(map_data, unit_list):
        // TDD: Test updating map view with new unit positions
        SET self.map_data = map_data
        SET self.unit_list = unit_list

    METHOD render():
        // TDD: Test rendering terrain tiles at correct positions
        // TDD: Test rendering units at correct positions, considering camera offset
        // TDD: Test rendering overlays correctly on top of terrain/units
        // TDD: Test rendering the cursor at its position
        FOR each tile (x, y) visible within camera view:
            LET screen_x, screen_y = self.map_to_screen_coords(x, y)
            LET tile_type = self.map_data.get_tile(x, y)
            DRAW terrain_tileset[tile_type] at screen_x, screen_y
            // TDD: Test rendering grid lines (optional)
            IF grid_enabled: DRAW grid line around tile

        FOR each overlay in self.overlays:
            FOR each tile_coord (tx, ty) in overlay.tiles:
                 IF tile is visible:
                     LET screen_x, screen_y = self.map_to_screen_coords(tx, ty)
                     DRAW overlay graphic (e.g., blue tint for move, red for attack) at screen_x, screen_y
                     // TDD: Test overlay rendering with different colors/styles

        FOR each unit in self.unit_list:
            IF unit is visible:
                LET screen_x, screen_y = self.map_to_screen_coords(unit.x, unit.y)
                LET sprite = self.get_unit_sprite(unit) // Consider faction, class, acted status
                DRAW sprite at screen_x, screen_y
                // TDD: Test rendering unit status indicators (e.g., HP bar, acted grey-out)
                IF unit.acted: DRAW acted indicator (e.g., greyscale)
                IF show_hp_bars: DRAW HP bar for unit

        // Draw cursor
        LET cursor_screen_x, cursor_screen_y = self.map_to_screen_coords(self.cursor_pos.x, self.cursor_pos.y)
        DRAW cursor graphic at cursor_screen_x, cursor_screen_y

    METHOD show_movement_overlay(move_tiles): // move_tiles = list of (x,y) tuples
        // TDD: Test showing movement overlay clears other overlays first
        self.hide_overlays()
        ADD { type: 'move', tiles: move_tiles } to self.overlays

    METHOD show_action_overlay(action_tiles): // action_tiles = list of (x,y) tuples
        // TDD: Test showing action overlay does NOT clear movement overlay (they might stack or replace, define behavior)
        // Option: Replace non-move overlays
        REMOVE overlays WHERE type != 'move' from self.overlays
        ADD { type: 'attack', tiles: action_tiles } to self.overlays // Assuming 'attack' type for now

    METHOD hide_overlays():
        // TDD: Test hiding overlays clears the overlay list
        SET self.overlays = []

    METHOD move_cursor(direction):
        // TDD: Test moving cursor stays within map boundaries
        LET new_x, new_y = self.cursor_pos
        IF direction == 'UP': new_y -= 1
        ELSE IF direction == 'DOWN': new_y += 1
        ELSE IF direction == 'LEFT': new_x -= 1
        ELSE IF direction == 'RIGHT': new_x += 1

        IF 0 <= new_x < self.map_data.width AND 0 <= new_y < self.map_data.height:
            SET self.cursor_pos = (new_x, new_y)
            // Optional: Adjust camera if cursor nears edge
            self.adjust_camera_for_cursor()

    METHOD set_cursor_pos(x, y):
        IF 0 <= x < self.map_data.width AND 0 <= y < self.map_data.height:
             SET self.cursor_pos = (x, y)
             self.adjust_camera_for_cursor()


    METHOD adjust_camera_for_cursor():
        // Logic to scroll map if cursor is near the edge of the screen view
        PRINT "Adjusting camera (logic TBD)"

    METHOD get_tile_at_coords(screen_x, screen_y): // Screen coordinates
        // TDD: Test converting screen coordinates to map coordinates accurately
        LET map_x = floor((screen_x - self.camera_offset.x) / self.tile_size)
        LET map_y = floor((screen_y - self.camera_offset.y) / self.tile_size)
        // Clamp to map boundaries
        map_x = max(0, min(map_x, self.map_data.width - 1))
        map_y = max(0, min(map_y, self.map_data.height - 1))
        RETURN { x: map_x, y: map_y }

    METHOD map_to_screen_coords(map_x, map_y):
        LET screen_x = (map_x * self.tile_size) + self.camera_offset.x
        LET screen_y = (map_y * self.tile_size) + self.camera_offset.y
        RETURN screen_x, screen_y

    METHOD get_unit_sprite(unit):
        // Logic to select correct sprite based on unit class, faction, status etc.
        // TDD: Test returning correct sprite for different unit states
        RETURN appropriate sprite from self.unit_sprites

END CLASS MapView
```

### 3. UnitInfoPanel

*   **Responsibility:** Displays detailed stats and information for a specific unit.
*   **Dependencies:** Graphics Library, Font Renderer.

```pseudocode
CLASS UnitInfoPanel:
    // Properties
    PROPERTY visible // Boolean
    PROPERTY position // On screen (x, y)
    PROPERTY dimensions // Width, height
    PROPERTY current_unit_data // Dict/Object holding info to display

    // Methods
    METHOD initialize(pos, dims):
        SET self.visible = FALSE
        SET self.position = pos
        SET self.dimensions = dims
        SET self.current_unit_data = NULL

    METHOD display_unit_info(unit_data):
        // TDD: Test displaying unit name, HP, and key stats correctly
        // TDD: Test displaying status effects
        SET self.current_unit_data = unit_data
        SET self.visible = TRUE

    METHOD clear_panel():
        // TDD: Test clearing the panel hides it and removes data
        SET self.current_unit_data = NULL
        SET self.visible = FALSE

    METHOD render():
        // TDD: Test rendering when visible shows formatted unit data
        // TDD: Test rendering when not visible draws nothing
        IF NOT self.visible OR self.current_unit_data IS NULL:
            RETURN

        DRAW panel background at self.position
        LET y_offset = 5 // Starting padding
        DRAW_TEXT(self.current_unit_data.name, position.x + 5, position.y + y_offset)
        y_offset += LINE_HEIGHT
        DRAW_TEXT(f"HP: {self.current_unit_data.hp} / {self.current_unit_data.max_hp}", position.x + 5, position.y + y_offset)
        y_offset += LINE_HEIGHT
        DRAW_TEXT(f"Fatigue: {self.current_unit_data.fatigue}", position.x + 5, position.y + y_offset)
        y_offset += LINE_HEIGHT
        // Draw other stats (Str, Mag, Skl, Spd, Lck, Def, Bld, Mov)
        // ...
        y_offset += LINE_HEIGHT
        // Draw Skills
        DRAW_TEXT("Skills: " + ", ".join(self.current_unit_data.skills), position.x + 5, position.y + y_offset)
        y_offset += LINE_HEIGHT
        // Draw Status Effects
        DRAW_TEXT("Status: " + ", ".join(self.current_unit_data.status_effects), position.x + 5, position.y + y_offset)
        y_offset += LINE_HEIGHT
        // Draw Equipped Item
        DRAW_TEXT("Equipped: " + self.current_unit_data.equipped_item_name, position.x + 5, position.y + y_offset)

END CLASS UnitInfoPanel
```

### 4. TerrainInfoPanel

*   **Responsibility:** Displays information about a specific map tile.
*   **Dependencies:** Graphics Library, Font Renderer.

```pseudocode
CLASS TerrainInfoPanel:
    // Properties
    PROPERTY visible // Boolean
    PROPERTY position // On screen (x, y)
    PROPERTY dimensions // Width, height
    PROPERTY current_terrain_data // Dict/Object holding info

    // Methods
    METHOD initialize(pos, dims):
        SET self.visible = FALSE
        SET self.position = pos
        SET self.dimensions = dims
        SET self.current_terrain_data = NULL

    METHOD display_terrain_info(terrain_data):
        // TDD: Test displaying terrain name and bonuses correctly
        SET self.current_terrain_data = terrain_data
        SET self.visible = TRUE

    METHOD clear_panel():
        // TDD: Test clearing the panel hides it
        SET self.current_terrain_data = NULL
        SET self.visible = FALSE

    METHOD render():
        // TDD: Test rendering terrain info when visible
        IF NOT self.visible OR self.current_terrain_data IS NULL:
            RETURN

        DRAW panel background at self.position
        LET y_offset = 5
        DRAW_TEXT(self.current_terrain_data.name, position.x + 5, position.y + y_offset)
        y_offset += LINE_HEIGHT
        DRAW_TEXT(f"Def Bonus: {self.current_terrain_data.defense_bonus}", position.x + 5, position.y + y_offset)
        y_offset += LINE_HEIGHT
        DRAW_TEXT(f"Avoid Bonus: {self.current_terrain_data.avoid_bonus}", position.x + 5, position.y + y_offset)
        y_offset += LINE_HEIGHT
        DRAW_TEXT(f"Move Cost: {self.current_terrain_data.movement_cost}", position.x + 5, position.y + y_offset) // Note: Cost might depend on selected unit, GUI Manager should provide context if needed.
        y_offset += LINE_HEIGHT
        IF self.current_terrain_data.special_effects:
            DRAW_TEXT("Effects: " + ", ".join(self.current_terrain_data.special_effects), position.x + 5, position.y + y_offset)

END CLASS TerrainInfoPanel
```

### 5. ActionMenu

*   **Responsibility:** Displays the context-sensitive list of actions available to the selected unit. Handles selection input.
*   **Dependencies:** Graphics Library, Font Renderer, GUIManager (for callbacks).

```pseudocode
CLASS ActionMenu:
    // Properties
    PROPERTY visible // Boolean
    PROPERTY position // On screen (x, y), often relative to the unit
    PROPERTY available_actions // List of strings (e.g., ["Attack", "Item", "Wait"])
    PROPERTY selected_index // Index of the currently highlighted action
    PROPERTY gui_manager // Reference to call back with selection

    // Methods
    METHOD initialize(gui_manager_ref):
        SET self.visible = FALSE
        SET self.available_actions = []
        SET self.selected_index = 0
        SET self.gui_manager = gui_manager_ref

    METHOD show_menu(unit_id, actions): // unit_id might be needed for positioning
        // TDD: Test showing the menu makes it visible and sets actions
        // TDD: Test menu position calculation based on unit position
        SET self.available_actions = actions
        SET self.selected_index = 0
        SET self.visible = TRUE
        // Calculate position based on unit_id's screen location (needs access to MapView or unit screen coords)
        SET self.position = calculate_menu_position(unit_id)

    METHOD hide_menu():
        // TDD: Test hiding the menu makes it invisible
        SET self.visible = FALSE
        SET self.available_actions = []

    METHOD navigate(direction): // 'UP' or 'DOWN'
        // TDD: Test navigating up/down wraps around the menu options
        IF NOT self.visible: RETURN
        IF direction == 'UP':
            SET self.selected_index = (self.selected_index - 1 + len(self.available_actions)) % len(self.available_actions)
        ELSE IF direction == 'DOWN':
            SET self.selected_index = (self.selected_index + 1) % len(self.available_actions)

    METHOD get_selected_action():
        IF NOT self.visible OR len(self.available_actions) == 0:
            RETURN NULL
        RETURN self.available_actions[self.selected_index]

    METHOD handle_click(click_pos): // Screen coordinates
        // TDD: Test clicking on a menu item triggers the correct action callback
        IF NOT self.visible: RETURN
        FOR index, action in enumerate(self.available_actions):
            LET item_rect = calculate_item_rect(index, self.position)
            IF click_pos IS INSIDE item_rect:
                SET self.selected_index = index
                self.gui_manager.handle_input_event('ACTION_MENU_SELECT', { action: self.get_selected_action() })
                BREAK

    METHOD render():
        // TDD: Test rendering menu items with highlight on the selected one
        IF NOT self.visible: RETURN
        DRAW menu background at self.position
        FOR index, action in enumerate(self.available_actions):
            LET item_pos_y = self.position.y + (index * ITEM_HEIGHT)
            LET text_color = HIGHLIGHT_COLOR if index == self.selected_index else NORMAL_COLOR
            DRAW_TEXT(action, self.position.x + PADDING, item_pos_y + PADDING, color=text_color)

END CLASS ActionMenu
```

### 6. CombatPreview

*   **Responsibility:** Displays the predicted outcome of a potential combat encounter.
*   **Dependencies:** Graphics Library, Font Renderer.

```pseudocode
CLASS CombatPreview:
    // Properties
    PROPERTY visible // Boolean
    PROPERTY position // On screen (x, y)
    PROPERTY preview_data // Dict/Object with attacker/defender stats, hit, dmg, crit, etc.

    // Methods
    METHOD initialize(pos):
        SET self.visible = FALSE
        SET self.position = pos
        SET self.preview_data = NULL

    METHOD show_preview(data):
        // TDD: Test showing preview makes it visible and stores data
        SET self.preview_data = data
        SET self.visible = TRUE

    METHOD hide_preview():
        // TDD: Test hiding preview makes it invisible
        SET self.visible = FALSE
        SET self.preview_data = NULL

    METHOD render():
        // TDD: Test rendering combat preview data correctly formatted
        IF NOT self.visible OR self.preview_data IS NULL:
            RETURN

        DRAW panel background at self.position
        // Attacker Info Side (e.g., Left)
        DRAW_TEXT(self.preview_data.attacker.name, ...)
        DRAW_TEXT(f"HP: {self.preview_data.attacker.hp}", ...)
        DRAW_TEXT(f"Dmg: {self.preview_data.attacker.damage}", ...)
        DRAW_TEXT(f"Hit: {self.preview_data.attacker.hit_chance}", ...)
        DRAW_TEXT(f"Crit: {self.preview_data.attacker.crit_chance}", ...)
        // Indicate weapon triangle if applicable
        // Indicate double attack if applicable

        // Defender Info Side (e.g., Right)
        DRAW_TEXT(self.preview_data.defender.name, ...)
        DRAW_TEXT(f"HP: {self.preview_data.defender.hp}", ...)
        DRAW_TEXT(f"Dmg: {self.preview_data.defender.damage}", ...)
        DRAW_TEXT(f"Hit: {self.preview_data.defender.hit_chance}", ...)
        DRAW_TEXT(f"Crit: {self.preview_data.defender.crit_chance}", ...)
        // Indicate weapon triangle if applicable
        // Indicate double attack if applicable

END CLASS CombatPreview
```

### 7. InventoryManager (Simplified)

*   **Responsibility:** Displays inventory, handles item use/equip actions. (Trade screen logic TBD).
*   **Dependencies:** Graphics Library, Font Renderer, GUIManager.

```pseudocode
CLASS InventoryManager:
    // Properties
    PROPERTY visible // Boolean
    PROPERTY position
    PROPERTY inventory_data // List of items {id, name, uses, equipped}
    PROPERTY owning_unit_id
    PROPERTY selected_item_index
    PROPERTY gui_manager

    // Methods
    METHOD initialize(gui_manager_ref):
        SET self.visible = FALSE
        SET self.gui_manager = gui_manager_ref
        // Define position, etc.

    METHOD show_inventory(inventory, unit_id):
        // TDD: Test showing inventory displays items correctly
        SET self.inventory_data = inventory
        SET self.owning_unit_id = unit_id
        SET self.selected_item_index = 0
        SET self.visible = TRUE

    METHOD hide_inventory():
        SET self.visible = FALSE

    METHOD navigate(direction):
        // TDD: Test navigating inventory items
        // Logic similar to ActionMenu.navigate

    METHOD handle_click(click_pos):
        // TDD: Test clicking an item selects it
        // TDD: Test clicking 'Use' or 'Equip' buttons triggers callback
        IF NOT self.visible: RETURN
        // Check if click is on an item -> update selected_item_index
        // Check if click is on a button (Use, Equip, Close) -> call gui_manager
        // Example for clicking 'Use' button:
        IF click_pos IS INSIDE USE_BUTTON_RECT:
             LET selected_item = self.inventory_data[self.selected_item_index]
             self.gui_manager.handle_input_event('INVENTORY_ACTION', { action: 'USE', item_id: selected_item.id })
        ELSE IF click_pos IS INSIDE EQUIP_BUTTON_RECT:
             LET selected_item = self.inventory_data[self.selected_item_index]
             self.gui_manager.handle_input_event('INVENTORY_ACTION', { action: 'EQUIP', item_id: selected_item.id })
        ELSE IF click_pos IS INSIDE CLOSE_BUTTON_RECT:
             self.gui_manager.handle_input_event('INVENTORY_ACTION', { action: 'CLOSE' })


    METHOD render():
        // TDD: Test rendering inventory list with selection highlight
        // TDD: Test rendering Use/Equip/Close buttons
        IF NOT self.visible: RETURN
        DRAW inventory background
        FOR index, item in enumerate(self.inventory_data):
            DRAW item name, uses (highlight if index == selected_item_index)
            IF item.equipped: DRAW equipped indicator
        // Draw buttons (Use, Equip, Close) - enable/disable based on selected item properties

END CLASS InventoryManager
```

### 8. SystemMenu (Simplified)

*   **Responsibility:** Displays options like End Turn, Options, Save, etc.
*   **Dependencies:** Graphics Library, Font Renderer, GUIManager.

```pseudocode
CLASS SystemMenu:
    // Properties
    PROPERTY visible
    PROPERTY options // ["End Turn", "Unit List", "Options", ...]
    PROPERTY selected_index
    PROPERTY gui_manager

    // Methods (Similar structure to ActionMenu)
    METHOD initialize(gui_manager_ref):
        // TDD: Test initialization
        SET self.visible = FALSE
        SET self.options = ["End Turn", "Unit List", "Options", "Suspend", "Quit Chapter"] // Example
        SET self.selected_index = 0
        SET self.gui_manager = gui_manager_ref

    METHOD show_menu():
        // TDD: Test showing system menu
        SET self.visible = TRUE
        SET self.selected_index = 0

    METHOD hide_menu():
        SET self.visible = FALSE

    METHOD navigate(direction):
        // TDD: Test navigating system menu options
        // Similar to ActionMenu.navigate

    METHOD get_selected_option():
        RETURN self.options[self.selected_index]

    METHOD handle_click(click_pos):
        // TDD: Test clicking system menu option triggers callback
        // Similar to ActionMenu.handle_click, calls gui_manager.handle_input_event('SYSTEM_MENU_SELECT', ...)

    METHOD render():
        // TDD: Test rendering system menu
        // Similar to ActionMenu.render

END CLASS SystemMenu
```

### 9. InputHandler

*   **Responsibility:** Captures raw input events (mouse clicks, key presses) from the underlying library (e.g., Pygame) and translates them into semantic GUI events for the GUIManager.
*   **Dependencies:** Graphics Library (for event loop), GUIManager.

```pseudocode
CLASS InputHandler:
    // Properties
    PROPERTY gui_manager // Reference to GUIManager to send events to

    // Methods
    METHOD initialize(gui_manager_ref):
        SET self.gui_manager = gui_manager_ref

    METHOD process_events(): // Called in the main game loop
        // TDD: Test processing a left mouse click event calls handle_map_click or menu click
        // TDD: Test processing a right mouse click event calls handle_cancel
        // TDD: Test processing a key press event calls handle_key_press
        FOR event in get_input_events_from_library(): // e.g., pygame.event.get()
            IF event.type == MOUSE_LEFT_CLICK:
                LET click_pos = event.pos
                // Check if click hit any active UI element (menus, buttons) first
                IF self.gui_manager.action_menu.visible AND click_pos IS INSIDE action_menu_rect:
                    self.gui_manager.action_menu.handle_click(click_pos)
                ELSE IF self.gui_manager.system_menu.visible AND click_pos IS INSIDE system_menu_rect:
                     self.gui_manager.system_menu.handle_click(click_pos)
                ELSE IF self.gui_manager.inventory_manager.visible AND click_pos IS INSIDE inventory_rect:
                     self.gui_manager.inventory_manager.handle_click(click_pos)
                // Add checks for Combat Preview confirmation buttons if any
                ELSE:
                    // Assume click is on the map if not on other UI
                    LET map_coords = self.gui_manager.map_view.get_tile_at_coords(click_pos.x, click_pos.y)
                    self.gui_manager.handle_input_event('MAP_CLICK', { x: map_coords.x, y: map_coords.y })

            ELSE IF event.type == MOUSE_RIGHT_CLICK:
                // TDD: Test right-click triggers cancel event
                self.gui_manager.handle_input_event('CANCEL', {})

            ELSE IF event.type == KEY_DOWN:
                LET key = event.key // Get the specific key pressed
                // Map library key codes to semantic keys (Confirm, Cancel, Arrows, Action shortcuts)
                LET semantic_key = self.map_key(key)
                IF semantic_key:
                     self.gui_manager.handle_input_event('KEY_PRESS', { key: semantic_key })

            ELSE IF event.type == QUIT_EVENT:
                // Handle quitting the game
                PRINT "Quit event received"
                // self.gui_manager.handle_input_event('QUIT_GAME', {})

    METHOD map_key(library_key):
        // TDD: Test mapping specific key codes (e.g., K_ESCAPE, K_RETURN) to semantic keys
        // Maps Pygame/other library key constants to abstract keys like 'UP', 'DOWN', 'CONFIRM', 'CANCEL', 'A', 'E', etc.
        IF library_key == K_UP: RETURN 'UP'
        IF library_key == K_DOWN: RETURN 'DOWN'
        IF library_key == K_LEFT: RETURN 'LEFT'
        IF library_key == K_RIGHT: RETURN 'RIGHT'
        IF library_key == K_RETURN OR library_key == K_SPACE: RETURN 'CONFIRM'
        IF library_key == K_ESCAPE OR library_key == K_BACKSPACE: RETURN 'CANCEL'
        IF library_key == K_e: RETURN 'END_TURN'
        // Add other mappings (A for Attack, I for Item, etc.)
        RETURN NULL

END CLASS InputHandler
```

## Game Engine API (Assumed Interface)

The GUI interacts with the game engine through an API object (`game_engine_api` in `GUIManager`). This API provides methods like:

*   `register_state_update_callback(callback_function)`
*   `get_initial_state()` -> Returns full map, unit, turn info.
*   `get_unit_details(unit_id)` -> Returns detailed stats, inventory, status for one unit.
*   `get_terrain_info(x, y)` -> Returns info for a tile.
*   `get_valid_moves(unit_id)` -> Returns list of (x, y) tuples.
*   `get_available_actions(unit_id, x, y)` -> Returns list of action strings available at location.
*   `get_action_range(unit_id, action_type, [item_id])` -> Returns list of (x, y) target tiles.
*   `get_combat_preview(attacker_id, defender_id, [weapon_id])` -> Returns predicted combat outcome data.
*   `get_unit_inventory(unit_id)` -> Returns list of item data.
*   `send_command(command_name, arguments)` -> Sends commands like 'MOVE_UNIT', 'EXECUTE_ACTION', 'END_PLAYER_PHASE', 'EQUIP_ITEM', etc.