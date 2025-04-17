# GUI Specification - Fantasy Tactics Game

## 1. Introduction

This document outlines the functional requirements and specifications for the Graphical User Interface (GUI) of the Fantasy Tactics Game, a project aiming to recreate gameplay elements inspired by Thracia 776. The GUI will replace the current Command-Line Interface (CLI) interaction detailed in `USAGE.md`, providing a more visual and intuitive experience for the player.

## 2. Core Requirements

The GUI *must* provide the following core functionalities:

*   **CR-01:** Display the game map, including terrain features and tile grid.
*   **CR-02:** Render units (player, enemy, NPC) on the map at their correct locations, indicating their allegiance and status (e.g., acted, current HP).
*   **CR-03:** Allow the player to select their units during the Player Phase.
*   **CR-04:** Visually indicate the movement range of a selected unit.
*   **CR-05:** Allow the player to choose a destination tile within the movement range and confirm the move.
*   **CR-06:** Display a context-sensitive action menu for a unit after moving (e.g., Attack, Staff, Item, Wait, Dance/Play, Capture, Rescue, Trade).
*   **CR-07:** Visually indicate the action range (e.g., attack range, staff range) for selected actions.
*   **CR-08:** Allow the player to select a target for actions that require one (e.g., attacking an enemy, healing an ally).
*   **CR-09:** Display essential unit information (stats, inventory, skills, status effects, fatigue).
*   **CR-10:** Display information about the terrain under the cursor or selected tile.
*   **CR-11:** Provide a visual preview of combat outcomes before confirming an attack.
*   **CR-12:** Allow the player to manage unit inventories (view, equip, use, trade items).
*   **CR-13:** Provide controls to manage the game flow (e.g., end Player Phase, view objectives, access system menu).
*   **CR-14:** Receive and display updates from the game engine (e.g., unit movement, HP changes, turn transitions, status effect applications).
*   **CR-15:** Handle cancellation of actions (e.g., backing out of movement or action selection).

## 3. Key Screens/Views

The GUI will be composed of several key visual components, which may overlap or be displayed concurrently:

*   **KV-01: Map View:**
    *   The primary view displaying the game board.
    *   Shows terrain tiles, unit sprites/icons, grid overlay (optional toggle).
    *   Displays visual overlays for movement range, attack range, staff range, etc.
    *   Includes a cursor for selecting tiles and units.
*   **KV-02: Unit Info Panel:**
    *   Displays detailed information about the currently selected unit or the unit under the cursor.
    *   Content: Name, Class, Level, HP (Current/Max), Fatigue, Stats (Str, Mag, Skl, Spd, Lck, Def, Bld, Mov), Skills, Status Effects, Equipped Weapon/Item, Portrait (optional).
*   **KV-03: Terrain Info Panel:**
    *   Displays information about the terrain tile currently under the cursor.
    *   Content: Terrain Name, Defense Bonus, Avoid Bonus, Movement Cost (for selected unit's class type), Special Effects (e.g., Heal, Obstructs Vision).
*   **KV-04: Action Menu:**
    *   A context-sensitive menu appearing when a player unit is selected after moving or in place.
    *   Lists available actions (Wait, Attack, Item, Staff, Trade, Rescue, Drop, Capture, Release, Dance/Play, etc.).
*   **KV-05: Combat Preview Window:**
    *   Appears when selecting an attack target.
    *   Displays predicted outcome: Attacker/Defender names, HP, equipped weapons, Hit %, Damage (Dmg), Critical % (Crit), Attack Speed (AS). May include weapon triangle indicators.
*   **KV-06: Inventory/Trade Screen:**
    *   A dedicated view or modal window for managing items.
    *   Allows viewing a unit's inventory, equipping weapons/items, using consumable items.
    *   Facilitates trading items between adjacent units.
*   **KV-07: System Menu:**
    *   Accessible via a button or key press.
    *   Options: End Turn, Unit List, Options (Sound, Graphics, Controls), Save, Load (if implemented), Quit Chapter, Suspend Game.
*   **KV-08: Status Screen:**
    *   A more detailed view of a unit's stats, growths, skills, weapon ranks, support partners, fatigue, etc. Accessible from the Unit Info Panel or Unit List.

## 4. User Interaction

Interaction will primarily be mouse-driven, with optional keyboard shortcuts mirroring CLI controls where appropriate.

*   **UI-01: Map Navigation:**
    *   Click and drag or edge scrolling to move the map view.
    *   Mouse wheel zoom (optional).
*   **UI-02: Selection:**
    *   Left-click on a tile: Move cursor, update Terrain Info Panel.
    *   Left-click on a player unit (not acted): Select the unit, display movement range, update Unit Info Panel.
    *   Left-click on any unit: Update Unit Info Panel.
    *   Right-click: Cancel current action/selection, deselect unit, or open context menu (TBD).
*   **UI-03: Movement:**
    *   After selecting a unit, left-click on a highlighted tile within movement range: Move the unit to that tile, display Action Menu.
*   **UI-04: Action Menu:**
    *   Left-click on an action button/item in the menu: Initiate that action (may lead to target selection).
*   **UI-05: Target Selection:**
    *   Hover over a potential target: Highlight target, potentially update Combat Preview.
    *   Left-click on a highlighted valid target: Confirm the action against that target.
*   **UI-06: Keyboard Shortcuts (Optional but Recommended):**
    *   Arrow Keys: Move map cursor.
    *   Enter/Space: Confirm selection/action (equivalent to left-click in many contexts).
    *   Esc/Backspace: Cancel action/selection (equivalent to right-click).
    *   Letter keys: Shortcuts for common actions (e.g., 'A' for Attack, 'W' for Wait, 'I' for Item).
    *   'E': End Player Phase (when no unit is selected).

## 5. Information Display

Specific data points required for key views:

*   **ID-01: Map View:**
    *   Unit Sprites/Icons: Differentiated by faction (Player, Enemy, NPC), potentially class type. Indicate if acted (e.g., greyed out). Show HP bar overlay (optional).
    *   Movement Range Overlay: Clearly distinct visual style (e.g., blue tiles).
    *   Attack/Action Range Overlay: Clearly distinct visual style (e.g., red tiles).
    *   Cursor: Visible indicator of the currently focused tile.
*   **ID-02: Unit Info Panel:**
    *   All stats listed in KV-02.
    *   Current HP / Max HP (e.g., "25 / 30").
    *   Fatigue level.
    *   Icons/Text for status effects (Poison, Sleep, Silence, Berserk, Fatigued).
    *   Equipped item name and uses (if applicable).
*   **ID-03: Terrain Info Panel:**
    *   Data listed in KV-03. Movement cost should reflect the *currently selected unit's* class type.
*   **ID-04: Combat Preview:**
    *   Data listed in KV-05. Clear indication of attacker vs. defender. Weapon icons/names. Weapon triangle advantage/disadvantage indicator. Potential for double attack indication.
*   **ID-05: Inventory Screen:**
    *   List of items (Icon, Name, Uses Current/Max). Indicate equipped item(s).

## 6. Integration Points

The GUI acts as a front-end client to the core game engine.

*   **IP-01: Game State Updates (Engine -> GUI):**
    *   The GUI must receive updates from the engine about the current game state. This includes:
        *   Initial chapter setup (map layout, unit placements, objectives).
        *   Unit positions, stats, status, inventory changes.
        *   Current turn and phase (Player, Enemy, NPC).
        *   Valid moves and actions for the selected unit.
        *   Combat results.
        *   Dialogue or event triggers.
    *   An event-based system or observer pattern is recommended, where the GUI subscribes to relevant game state changes.
*   **IP-02: User Commands (GUI -> Engine):**
    *   The GUI translates user interactions into commands sent to the game engine. Examples:
        *   `SELECT_UNIT(unit_id)`
        *   `MOVE_UNIT(unit_id, target_x, target_y)`
        *   `EXECUTE_ACTION(unit_id, action_type, [target_id], [item_id])` (e.g., `EXECUTE_ACTION(leif, ATTACK, enemy_soldier)`)
        *   `END_PLAYER_PHASE()`
        *   `GET_UNIT_DETAILS(unit_id)`
        *   `GET_TERRAIN_INFO(x, y)`
        *   `GET_COMBAT_PREVIEW(attacker_id, defender_id, [weapon_id])`
    *   A clear API or command queue between the GUI and engine is necessary.
*   **IP-03: Data Loading:**
    *   The GUI may need access to game data (unit stats, item properties, map tilesets, sprites) either directly or via requests to the engine.

## 7. Technology Considerations (Optional)

Several Python libraries could be used for the GUI. The choice depends on factors like ease of use, performance, cross-platform compatibility, and desired visual fidelity.

*   **Pygame:**
    *   **Pros:** Relatively simple API, good for 2D games, extensive tutorials available, good performance for sprite-based graphics.
    *   **Cons:** Can require more boilerplate code for UI elements (buttons, menus), less "native" look and feel. Might be suitable given the tile-based nature.
*   **Kivy:**
    *   **Pros:** Modern UI design, good touch support (though less relevant here), custom drawing capabilities, hardware acceleration.
    *   **Cons:** Steeper learning curve, different packaging process, might be overkill for a simple tactics game UI.
*   **PyQt / PySide (using Qt framework):**
    *   **Pros:** Mature, feature-rich, creates native-looking applications, powerful widget set, good designer tools (Qt Designer).
    *   **Cons:** Can be complex, licensing considerations (PyQt is GPL/Commercial, PySide is LGPL), potentially steeper learning curve than Pygame for basic graphics.
*   **Tkinter:**
    *   **Pros:** Built into Python standard library, simple for basic UIs.
    *   **Cons:** Looks dated, generally not recommended for graphically intensive applications or games.

**Recommendation:** Pygame is often a good starting point for 2D sprite/tile-based games in Python due to its focus on game development primitives. PyQt/PySide offers more robust UI features if complex menus, windows, and native look-and-feel are prioritized over direct graphical rendering simplicity. A final decision should involve prototyping or further research based on developer familiarity and specific visual goals.

## 8. Future Considerations (Out of Scope for Initial Spec)

*   Animation system (walking, combat, effects).
*   Sound effects and music integration.
*   Advanced configuration options.
*   Full dialogue system presentation.
*   Cutscene display.
*   Mouse-over tooltips for map elements or UI buttons.