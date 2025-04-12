# Specification: Enhanced ASCII Display System

## 1. Overview

This document outlines the requirements and design for an enhanced ASCII-based display system for the command-line interface (CLI) of the Fantasy Tactics Game. It aims to provide a clear, informative, and visually distinct representation of the game state, including the map, units, terrain, fog of war, and relevant status information. This system builds upon the existing `cli_display.py` but addresses known limitations and adds features.

## 2. Requirements

### Functional Requirements

*   **FR1: Map Rendering:** Display the game map grid using ASCII characters.
*   **FR2: Terrain Representation:** Visually distinguish different terrain types using unique characters and/or colors.
*   **FR3: Unit Representation:** Display units on the map according to their faction (Player, Enemy, NPC).
*   **FR4: Unit Status Indication:** Optionally indicate unit status (e.g., low HP, mounted, captured, specific status effects) visually.
*   **FR5: Fog of War Display:** Represent different visibility levels (Visible, Fog, Shroud/Unknown).
*   **FR6: Unit Visibility in Fog:** Hide enemy/NPC units in Fog/Shroud tiles unless detected by specific mechanics (e.g., Torch staff, Thief vision). Player units should always be visible if the tile itself is visible.
*   **FR7: Cursor/Selection Highlight:** Indicate the current cursor position and/or selected unit/tile.
*   **FR8: Status Information Panel:** Display key game state information alongside the map (Current Turn, Current Phase, Selected Unit Info).
*   **FR9: Refresh Logic:** Update the display automatically after significant game state changes (e.g., unit moves, action completes, phase changes).
*   **FR10: Color Support (Optional but Recommended):** Utilize terminal colors (ANSI escape codes) for better distinction if the terminal supports it. Provide a fallback for non-color terminals.

### Non-Functional Requirements

*   **NFR1: Performance:** Rendering should be reasonably fast and not significantly slow down gameplay loops.
*   **NFR2: Clarity:** The display should be easily understandable.
*   **NFR3: Modularity:** The display system should be relatively decoupled from core game logic, interacting primarily through defined interfaces/systems (`GameState`, `MapSystem`, `UnitSystem`, `FogOfWarSystem`).
*   **NFR4: Configurability:** Allow easy modification of characters/colors used for representation.

### Known Issues to Address

*   **BUG-ASCII-UPDATE:** The previous implementation had issues updating unit positions correctly between turns/actions. The new implementation must fetch the *current* unit positions from the `GameState` or `UnitSystem` *each time* it renders.

## 3. Design & Pseudocode

### 3.1 Data Structures & Constants

```pseudocode
// Constants for Factions
FACTION_PLAYER = "Player"
FACTION_ENEMY = "Enemy"
FACTION_NPC = "NPC"
FACTION_ALLY = "Ally" // Potentially distinct from Player

// Constants for Fog of War Status
VISIBILITY_VISIBLE = "Visible"
VISIBILITY_FOG = "Fog"
VISIBILITY_SHROUD = "Shroud" // Or Unknown

// Representation Mapping (Configurable)
// Structure: { 'KEY': (Character, ForegroundColor, BackgroundColor) }
// Colors are optional, use defaults if not supported/defined.
TERRAIN_REPRESENTATION = {
    "Plain": ('.', Color.GREEN, Color.BG_BLACK),
    "Forest": ('&', Color.DARK_GREEN, Color.BG_BLACK),
    "Mountain": ('^', Color.WHITE, Color.BG_GRAY),
    "Fort": ('#', Color.YELLOW, Color.BG_DARK_GRAY),
    "Peak": ('▲', Color.WHITE, Color.BG_DARK_GRAY),
    "River": ('~', Color.BLUE, Color.BG_CYAN),
    "Sea": ('≈', Color.DARK_BLUE, Color.BG_BLUE),
    "Road": ('=', Color.WHITE, Color.BG_DARK_GRAY),
    "Village": ('V', Color.YELLOW, Color.BG_GREEN),
    "Gate": ('G', Color.YELLOW, Color.BG_DARK_GRAY),
    "Throne": ('T', Color.YELLOW, Color.BG_MAGENTA),
    "Wall": ('|', Color.WHITE, Color.BG_GRAY), // Or '-' for horizontal
    "Pillar": ('O', Color.WHITE, Color.BG_GRAY),
    "Chest": ('C', Color.YELLOW, Color.BG_BROWN),
    "Door": ('D', Color.YELLOW, Color.BG_BROWN),
    "Bridge": ('=', Color.YELLOW, Color.BG_BLUE),
    "INVALID": ('?', Color.RED, Color.BG_BLACK)
}

UNIT_REPRESENTATION = {
    FACTION_PLAYER: ('P', Color.BLUE, None), // Background determined by terrain/fog
    FACTION_ENEMY: ('E', Color.RED, None),
    FACTION_NPC: ('N', Color.GREEN, None),
    FACTION_ALLY: ('A', Color.CYAN, None)
    // Potentially add class-specific characters later if needed
}

// Status Indicators (Applied on top of unit character/color)
// Could be prefix/suffix character, or color modification
STATUS_INDICATORS = {
    "LowHP": (None, Color.YELLOW, None), // Modify foreground color
    "Mounted": ('^', None, None), // Add prefix/suffix (or different base char)
    "Captured": ('c', None, None), // Add prefix/suffix
    "Poison": (None, Color.PURPLE, None), // Modify foreground color
    "Sleep": (None, Color.GRAY, None), // Modify foreground color
    // ... other statuses
}

FOG_REPRESENTATION = {
    VISIBILITY_FOG: ('░', Color.GRAY, Color.BG_BLACK), // Light shade
    VISIBILITY_SHROUD: ('█', Color.BLACK, Color.BG_BLACK) // Full block or just black background
    // Visible tiles use terrain/unit representation directly
}

HIGHLIGHT_REPRESENTATION = {
    "Cursor": (None, None, Color.BG_YELLOW), // Change background color
    "SelectedUnit": (None, None, Color.BG_CYAN),
    "MovementRange": (None, None, Color.BG_BLUE),
    "AttackRange": (None, None, Color.BG_RED)
}

// Color Definitions (Example using a hypothetical Color library)
class Color:
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"
    DARK_GRAY = "dark_gray"
    DARK_GREEN = "dark_green"
    // ... etc
    BG_BLACK = "bg_black"
    BG_RED = "bg_red"
    // ... etc
```

### 3.2 Core Rendering Function

```pseudocode
FUNCTION render_enhanced_ascii_map(gameState, mapSystem, unitSystem, fogSystem, displayConfig, cursorPosition, selectedUnitId, highlightTiles):
    // Args:
    //  gameState: Current game state object
    //  mapSystem: Provides map dimensions and terrain data
    //  unitSystem: Provides unit data and positions
    //  fogSystem: Provides visibility data for the current player
    //  displayConfig: Contains representation mappings (TERRAIN_REPRESENTATION, etc.)
    //  cursorPosition: (x, y) tuple for cursor highlight
    //  selectedUnitId: ID of the currently selected unit for highlight
    //  highlightTiles: Dictionary { 'type': set((x,y)), ... } e.g., {'MovementRange': {(1,1), (1,2)}}

    mapWidth = mapSystem.get_width()
    mapHeight = mapSystem.get_height()
    visibilityGrid = fogSystem.get_visibility_grid() // Assumes returns 2D array/dict of VISIBILITY_* status
    allUnits = gameState.get_all_units() // Or unitSystem.get_all_units_with_position() -> { (x,y): unit_object }
    unitPositions = {unit.position: unit for unit in allUnits} // Create a quick lookup

    outputBuffer = [] // List of strings, one per row

    FOR y FROM 0 TO mapHeight - 1:
        rowString = ""
        FOR x FROM 0 TO mapWidth - 1:
            position = (x, y)
            visibility = visibilityGrid[x][y] // Get visibility status for this tile

            // Default representation: Shroud
            char, fgColor, bgColor = displayConfig.FOG_REPRESENTATION[VISIBILITY_SHROUD]

            IF visibility == VISIBILITY_FOG:
                char, fgColor, bgColor = displayConfig.FOG_REPRESENTATION[VISIBILITY_FOG]
                // Check if any *player* unit is here (player units visible in fog)
                IF position IN unitPositions:
                    unit = unitPositions[position]
                    IF unit.faction == FACTION_PLAYER: // Or ALLY
                        unitChar, unitFg, _ = displayConfig.UNIT_REPRESENTATION[unit.faction]
                        // Apply status indicators if needed
                        unitChar, unitFg = apply_status_indicators(unit, unitChar, unitFg, displayConfig.STATUS_INDICATORS)
                        // Render unit char on fog background
                        char, fgColor = unitChar, unitFg
                        // Keep fog background color (bgColor)

            ELSE IF visibility == VISIBILITY_VISIBLE:
                // Get terrain
                terrainType = mapSystem.get_terrain_type(position)
                char, fgColor, bgColor = displayConfig.TERRAIN_REPRESENTATION.get(terrainType, displayConfig.TERRAIN_REPRESENTATION["INVALID"])

                // Check for unit
                IF position IN unitPositions:
                    unit = unitPositions[position]
                    // Check if unit should be displayed (enemies/NPCs might be hidden by skills/effects even if tile is visible)
                    // This check might belong in FogOfWarSystem or be simpler here
                    IF fogSystem.should_display_unit(unit, visibilityGrid): // Assumes such a method exists
                        unitChar, unitFg, _ = displayConfig.UNIT_REPRESENTATION[unit.faction]
                        // Apply status indicators
                        unitChar, unitFg = apply_status_indicators(unit, unitChar, unitFg, displayConfig.STATUS_INDICATORS)
                        // Override terrain char/color with unit char/color
                        char, fgColor = unitChar, unitFg
                        // Keep terrain background color (bgColor)

            // Apply Highlights (Cursor > Selected > Attack > Move)
            highlightType = None
            IF position == cursorPosition:
                highlightType = "Cursor"
            ELSE IF selectedUnitId AND unitPositions.get(position)?.id == selectedUnitId:
                 highlightType = "SelectedUnit"
            ELSE IF position IN highlightTiles.get("AttackRange", {}):
                highlightType = "AttackRange"
            ELSE IF position IN highlightTiles.get("MovementRange", {}):
                highlightType = "MovementRange"

            IF highlightType:
                _, _, highlightBg = displayConfig.HIGHLIGHT_REPRESENTATION[highlightType]
                IF highlightBg IS NOT None:
                    bgColor = highlightBg // Override background for highlight

            // Format the character with colors (using hypothetical format_color function)
            formattedChar = format_color(char, fgColor, bgColor)
            rowString += formattedChar

        outputBuffer.append(rowString)

    // Combine rows and print/return
    fullMapString = "\n".join(outputBuffer)
    RETURN fullMapString

FUNCTION apply_status_indicators(unit, baseChar, baseFgColor, statusConfig):
    // Applies status modifications based on priority
    // Example: Low HP overrides color, Mounted adds prefix
    finalChar = baseChar
    finalFgColor = baseFgColor

    // Check Low HP (e.g., < 25% HP)
    IF unit.current_hp / unit.max_hp < 0.25:
        _, lowHpFg, _ = statusConfig.get("LowHP", (None, None, None))
        IF lowHpFg IS NOT None:
            finalFgColor = lowHpFg

    // Check Mounted
    IF unit.is_mounted: // Assuming a boolean flag exists
        mountChar, _, _ = statusConfig.get("Mounted", (None, None, None))
        IF mountChar IS NOT None:
            finalChar = mountChar // Or prefix/suffix: finalChar = mountChar + finalChar

    // Check Captured
    IF unit.is_captured: // Assuming a boolean flag exists
        captureChar, _, _ = statusConfig.get("Captured", (None, None, None))
        IF captureChar IS NOT None:
            finalChar = captureChar // Or prefix/suffix

    // Check other statuses (Poison, Sleep, etc.) - potentially modify color
    activeStatus = unit.get_primary_visual_status() // Need logic to decide which status is most important visually
    IF activeStatus IN statusConfig:
        _, statusFg, _ = statusConfig[activeStatus]
        IF statusFg IS NOT None:
             // Decide if status color overrides LowHP color or vice-versa
             finalFgColor = statusFg # Example: Status overrides LowHP

    RETURN finalChar, finalFgColor

FUNCTION format_color(char, fgColor, bgColor):
    // Placeholder: Generates ANSI escape codes or returns plain char if colors disabled/unavailable
    IF colors_enabled:
        // Construct ANSI string: e.g., "\x1b[<fg_code>;<bg_code>m{char}\x1b[0m"
        RETURN generate_ansi_code(char, fgColor, bgColor)
    ELSE:
        RETURN char
```

### 3.3 Status Information Panel

```pseudocode
FUNCTION render_status_panel(gameState, selectedUnitId, unitSystem, displayConfig):
    // Renders information typically displayed alongside the map

    turn = gameState.get_current_turn()
    phase = gameState.get_current_phase()
    panelLines = []

    panelLines.append(f"Turn: {turn}  Phase: {phase}")
    panelLines.append("-" * 20) // Separator

    IF selectedUnitId:
        unit = unitSystem.get_unit_details(selectedUnitId) // Fetch detailed info
        IF unit:
            // Format unit info (Name, Class, HP, MP/Fatigue, Status)
            hpStr = f"HP: {unit.current_hp}/{unit.max_hp}"
            // Apply LowHP color if needed
            IF unit.current_hp / unit.max_hp < 0.25:
                 _, lowHpFg, _ = displayConfig.STATUS_INDICATORS.get("LowHP", (None, None, None))
                 hpStr = format_color(hpStr, lowHpFg, None)

            panelLines.append(f"Selected: {unit.name} ({unit.class_name})")
            panelLines.append(hpStr)
            IF unit.current_fatigue IS NOT None: # Check if fatigue exists
                 panelLines.append(f"Fatigue: {unit.current_fatigue}")
            IF unit.status_effects:
                 statusStr = ", ".join(unit.status_effects)
                 panelLines.append(f"Status: {statusStr}")
            // Add equipped weapon?
            equippedWeapon = unitSystem.get_equipped_weapon_details(selectedUnitId)
            IF equippedWeapon:
                panelLines.append(f"Weapon: {equippedWeapon.name} ({equippedWeapon.current_durability}/{equippedWeapon.max_durability})")
            ELSE:
                panelLines.append("Weapon: None")
        ELSE:
            panelLines.append("Selected: None")
    ELSE:
        panelLines.append("Selected: None")

    panelLines.append("-" * 20) // Separator

    // Combine lines and return/print
    fullPanelString = "\n".join(panelLines)
    RETURN fullPanelString

```

### 3.4 Update Logic

The `render_enhanced_ascii_map` and `render_status_panel` functions should be called by the main game loop or input handler whenever the display needs refreshing. This typically occurs:

1.  **After Player Action:** When a player unit finishes moving, attacking, waiting, using an item, etc.
2.  **After AI Action:** When an AI unit completes its action.
3.  **Phase Change:** At the beginning of Player Phase, Enemy Phase, NPC Phase.
4.  **Selection Change:** When the player selects a different unit or moves the cursor.
5.  **Menu Navigation:** Before displaying a menu and after closing it.
6.  **Event Execution:** After events that might change unit positions, stats, or map state.

The game engine or input handler is responsible for triggering these updates.

### 3.5 Integration Points

*   **`GameState` / `GameStateManager`:** Source for current turn, phase, list of all units, potentially global flags.
*   **`MapSystem`:** Provides map dimensions, terrain type for each tile.
*   **`UnitSystem` / `GameStateManager`:** Provides detailed unit information (ID, name, class, stats, HP, status effects, inventory, faction, position, mounted/captured status, weapon ranks). Needs methods like `get_unit_details(unit_id)`, `get_all_units_with_position()`, `get_equipped_weapon_details(unit_id)`.
*   **`FogOfWarSystem`:** Provides the visibility status (Visible, Fog, Shroud) for each tile based on the current player's perspective. Needs `get_visibility_grid()` and potentially `should_display_unit(unit, grid)`.
*   **`InputHandler` (e.g., `cli_input_handler.py`):** Manages cursor position, selected unit ID, and triggers display updates. It will call the rendering functions.
*   **`Engine`:** Orchestrates turns and phases, signaling the `InputHandler` or `DisplaySystem` when updates are needed.

### 3.6 Color Handling

*   Use a library like `colorama` (Python) or similar to handle cross-platform ANSI color codes.
*   Include a global flag `COLORS_ENABLED` that can be set based on terminal capabilities or user preference.
*   The `format_color` function should check this flag.

## 4. TDD Anchors

*   **`test_render_empty_map()`:** Verify rendering an empty map with correct dimensions and default terrain.
*   **`test_render_terrain_types()`:** Verify different terrain types render with correct characters/colors.
*   **`test_render_unit_factions()`:** Verify Player, Enemy, NPC units render with correct characters/colors on plain terrain.
*   **`test_render_unit_on_terrain()`:** Verify unit representation correctly overrides terrain character but uses terrain background.
*   **`test_render_fog_of_war()`:** Verify Shroud and Fog tiles render correctly.
*   **`test_render_unit_visibility_in_fog()`:** Verify player units are visible in Fog, while enemies are hidden (unless specific conditions met - requires mocking FogSystem).
*   **`test_render_unit_status_indicators()`:** Verify Low HP, Mounted, Captured statuses are visually indicated (color change, character prefix/suffix). Prioritize testing the most common/important statuses.
*   **`test_render_highlights()`:** Verify Cursor, Selected Unit, Movement Range, Attack Range highlights apply correct background colors and override appropriately.
*   **`test_render_status_panel_no_selection()`:** Verify the panel shows turn/phase correctly when no unit is selected.
*   **`test_render_status_panel_with_selection()`:** Verify the panel shows correct details (Name, HP, Status, Weapon) for a selected unit.
*   **`test_render_no_color_fallback()`:** Verify rendering works correctly with colors disabled (plain ASCII characters).
*   **`test_render_update_after_move()`:** Simulate a unit move and verify the map re-renders with the unit in the new position (addresses BUG-ASCII-UPDATE).