# Specification: Game Flow and Event System

This document outlines the overall game progression, chapter structure, and the event system that drives narrative, unit placements, and dynamic occurrences within chapters in the Fire Emblem Thracia 776 recreation.

## 1. Core Concepts

*   **Game Flow**: The overall progression of the player through the game, from the title screen, to world map navigation (if applicable), chapter selection, chapter gameplay, and interlude sequences (story, preparations).
*   **Chapter**: A distinct segment of the game, typically involving one map, a set of objectives, and unique scripted events.
*   **Event System**: A mechanism for triggering scripted sequences based on various conditions (turn number, unit location, character interactions, unit death, etc.). This is primarily defined in `.event` files like [`Chapter01.event`](FireEmblem5/EVENTS/Chapter01.event:0).
*   **Event Flags**: Boolean variables used to track the state of events (e.g., if an event has occurred) to control flow and prevent re-triggering. Flags can be chapter-specific or global.
*   **Unit Groups**: Predefined sets of units (player, enemy, NPC) that are loaded onto the map by events, often as reinforcements or initial placements.
*   **Dialogue System**: Manages the display of character conversations and narrative text.
*   **World Map**: A map used for navigating between chapters and potentially accessing other game features. Thracia 776 has world map segments that play out between certain chapters.

## 2. Game States

The game will transition through several high-level states:

1.  **TitleScreen**: Initial screen with options like New Game, Load Game, Options.
    *   // TEST: Title screen displays options correctly.
2.  **WorldMap/ChapterSelect**: Player navigates a world map or a chapter list to choose the next chapter/mission. (FE5 has a linear progression with some branching via Gaiden chapters).
    *   // TEST: Player can select and start a chapter.
3.  **PreChapterSequence**: Cutscenes, story dialogue, or preparation menus before a chapter begins.
    *   // TEST: Pre-chapter dialogue plays correctly.
4.  **ChapterGameplay**: The main gameplay loop for a chapter.
    *   **PlayerPhase**: Player controls their units.
    *   **EnemyPhase**: AI controls enemy units.
    *   **NPCPhase (OtherPhase)**: AI controls neutral/allied NPC units.
    *   Events can trigger at the start/end of phases or turns.
    *   // TEST: Phase transitions occur correctly (Player -> Enemy -> NPC -> Player).
5.  **PostChapterSequence**: Cutscenes, story dialogue, results screen after a chapter ends.
    *   // TEST: Post-chapter results (turns taken, units lost) are displayed.
    *   // TEST: Post-chapter dialogue plays correctly.
6.  **GameOver**: If a game over condition is met (e.g., Leif is defeated).
    *   // TEST: Game over screen appears on Leif's defeat.
7.  **GameSave/Load**: System for saving and resuming game progress. Event flags and relevant game state must be persisted.
    *   // TEST: Game can be saved successfully, including event flag states.
    *   // TEST: Saved game can be loaded and resumes at correct state with correct event flags.

## 3. Event System Architecture

Based on [`Chapter01.event`](FireEmblem5/EVENTS/Chapter01.event:0). The event system must be robust enough to handle scripts parsed from these files.

### 3.1. Event Triggers

Events can be triggered by:

*   **Chapter Start**: Automatically at the beginning of a chapter (e.g., `_OpeningEventDefinitions`).
*   **Turn Number**: At the start of a specific turn or phase (e.g., `_TurnEventDefinitions`).
    *   `CMP_WORD wCurrentTurn, TurnValue`
    *   `CMP_WORD wCurrentPhase, PhaseType (Player, Enemy, Other)`
*   **Character Interaction (Talk)**: When two specific characters are adjacent and one uses the "Talk" command (e.g., `_TalkEventDefinitions`).
    *   `CHECK_CHARS2 CharacterID1, CharacterID2`
*   **Location Visit**: When a unit moves to specific coordinates (e.g., `_LocationEventDefinitions`).
    *   `macroECCheckCoordinates [X, Y]`
    *   Often combined with `CMP_WORD aSelectedCharacterBuffer.Character, CharacterID` to check *who* visited.
*   **Battle Quote**: When specific units engage in combat (e.g., `_BattleEventDefinitions`).
    *   `macroECBossQuote Flag, BossCharacterID`
*   **Shop Visit**: When a unit visits a shop tile (e.g., `_ShopEventDefinitions`).
    *   `macroECShop ShopDataPointer`
*   **Unit Death**: When a specific unit or any allied unit dies (e.g., `FlagAlliedDeath`).
    *   `TEST_FLAG_SET FlagPlayerDeath` (Note: This tests if a flag *related* to player death is set; direct trigger mechanism for unit death needs to be robust).
*   **Event Flags**: Events can be conditional on global or chapter-specific flags being set or unset.
    *   `TEST_FLAG_SET FlagID`
    *   `TEST_FLAG_UNSET FlagID`

### 3.2. Event Commands (Scripting Language Primitives)

A scripting engine will parse and execute commands found in `.event` files. Key commands include:
Basic error handling (e.g., logging warnings for unrecognized commands or missing resources, attempting to continue if non-critical) should be implemented. Critical errors (e.g., malformed essential commands) may halt event processing for the current event chain.

*   **Control Flow**:
    *   `EVENT FlagCondition, ScriptLabelToExecute`
    *   `END_DEFINITION`, `END_DEFINITION_ARRAY`
    *   `END1`, `END2`, `END3` (End of script block; specific behaviors like screen transitions or yielding control need to be replicated from original game or defined clearly).
    *   `JUMP_TRUE Label`, `JUMP Label` (conditional/unconditional jumps)
    *   `YIELD`: Pauses event execution until the current action (e.g., sound, movement, dialogue) completes.
    *   `HALT_UNTIL_BYTE_SKIPPABLE Register, Value`: Waits for a memory register to reach a value, skippable by player.
    *   `HALT_UNTIL_WORD_SKIPPABLE Register, Value`
*   **Unit Management**:
    *   `LOAD_GROUP UnitGroupPointer`: Loads a predefined group of units. (e.g., `LOAD_GROUP eventChapter01Data._LeifUnitGroup`)
        *   // TEST: Units from a group are loaded at correct positions with correct stats/items.
    *   `MOVE_CHAR CharacterID, [X,Y], SpeedConstant, OptionalMovePathScriptLabel`: Moves a character on the map.
        *   // TEST: Character moves along the specified path or to the target coordinates.
    *   `WAIT_MOVE`: Pauses event execution until all character movements are complete.
    *   `macroASMCRemoveUnit CharacterID`: Removes a unit from the map. This should not trigger standard "death" events unless specifically designed to.
        *   // TEST: Unit is correctly removed from the map.
    *   `macroASMCSetCharacterDataByte CharacterID, Property, Value`: Modifies a character's data (e.g., `LeadershipStars`).
        *   // TEST: Character data is correctly modified by event.
    *   `CALL_ASM_LOOP AssemblyRoutineLabel`: Calls a specific assembly routine (e.g., `rlASMCSetLordIndefatigable`). These will need to be reimplemented as high-level functions.
*   **Dialogue & Narrative**:
    *   `DIALOGUE DialogueID`: Displays a dialogue sequence.
        *   // TEST: Correct dialogue sequence is displayed.
    *   `macroDialogue DialogueID`: Simplified dialogue display.
    *   `macroDialogueWithBG DialogueID, BackgroundID`: Dialogue with a specific background.
    *   `macroChapterTitlePopup DialogueID`: Displays the chapter title.
*   **Map & Camera**:
    *   `SET_CAMERA_POSITION [X,Y]`
    *   `SCROLL_CAMERA_ADDRESS CoordinatePointer` or `SCROLL_CAMERA_COORDS [X,Y], Speed`
        *   // TEST: Camera moves to the correct position smoothly.
    *   `SET_CURSOR_POSITION`: Likely sets cursor to current camera focus or a specific unit.
*   **Audio/Visual**:
    *   `PLAY_SOUND_FORCED SoundEffectID`
    *   `SET_MUSIC MusicID`
        *   // TEST: Correct sound effect and music track play.
    *   `FADE_OUT Duration`, `FADE_IN Duration`
        *   // TEST: Screen fades in/out correctly.
    *   `PAUSE_SKIPPABLE Duration`
*   **Item & Shop**:
    *   `macroItemHouse DialogueID, ItemID, [X,Y], SoundEffectID`: Gives an item to the visiting unit.
        *   // TEST: Visiting a house grants the correct item.
    *   `SHOP [X,Y], [ItemIDsList]`: Defines a shop at coordinates with specific inventory.
        *   // TEST: Shop at the location has the correct inventory.
*   **Flags & State**:
    *   `SET_FLAG FlagID`: Sets the specified event flag to true.
        *   // TEST: `SET_FLAG` correctly sets a flag to true.
    *   `CLEAR_FLAG FlagID`: Sets the specified event flag to false.
        *   // TEST: `CLEAR_FLAG` correctly sets a flag to false.
    *   `STORE_BYTE Register, Value` (Internal engine state, not typically game event flags)

### 3.3. Unit Group Definition (from `.event` files)

As seen in [`Chapter01.event`](FireEmblem5/EVENTS/Chapter01.event:441):
`UNIT CharacterID, Allegiance, [DeployX, DeployY], [MoveTargetX, MoveTargetY], LeaderID, [ItemIDsList], Level, IsBossFlag, [AI_Movement?, AI_Action?, AI_Param1?, AI_Param2?]`

*   `CharacterID`: Identifier for the character data.
*   `Allegiance`: Player, Enemy, NPC.
*   `[DeployX, DeployY]`: Initial placement coordinates.
*   `[MoveTargetX, MoveTargetY]`: Coordinates the unit will move to upon loading (if different from deploy).
*   `LeaderID`: The leader of this unit (for AI grouping, retreat conditions, or specific event checks).
*   `[ItemIDsList]`: List of items in their inventory.
*   `Level`: Starting level.
*   `IsBossFlag`: Boolean.
*   `[AI_Params]`: Optional parameters likely defining AI behavior (Movement Script ID, Action Script ID, and specific parameters for those scripts).
    *   // TEST: Unit is created with correct CharacterID, Allegiance, Level, Items, and AI.

## 4. Chapter Lifecycle

1.  **Load World Map Data (if applicable)**: Display world map, handle world map events.
    *   // TEST: World map events trigger and execute correctly.
2.  **Select Chapter**.
3.  **Load Chapter Data**:
    a.  Load map tileset and layout ([`docs/spec/01_MapSystem.md`](docs/spec/01_MapSystem.md:0)).
    b.  Load character data ([`docs/spec/02_CharacterAndClassSystem.md`](docs/spec/02_CharacterAndClassSystem.md:0)) and item data ([`docs/spec/03_ItemSystem.md`](docs/spec/03_ItemSystem.md:0)).
    c.  Load chapter event file (`.event`).
    d.  Initialize event flags for the chapter (global flags persist, chapter-local flags reset unless specified otherwise).
    *   // TEST: All necessary chapter assets (map, units, items, events) are loaded.
4.  **Execute Opening Events**: Run events tagged for chapter start. This typically includes initial unit placements, camera pans, and opening dialogue.
    *   // TEST: Opening cutscene plays out correctly, initial units are placed.
5.  **Start Turn 1 (Player Phase)**.
6.  **Main Game Loop (per turn)**:
    a.  **Start of Turn Events**: Check and execute any events triggered by the current turn number/phase.
    b.  **Player Phase**:
        i.  Player controls their units (move, attack, staff, item, talk, visit, etc.).
        ii. Check for and execute events triggered by player actions (talk, location visit).
        iii.End phase.
    c.  **Enemy Phase**:
        i.  AI controls enemy units ([`docs/spec/05_AISystem.md`](docs/spec/05_AISystem.md:0)).
        ii. Check for and execute events triggered by enemy actions.
        iii.End phase.
    d.  **NPC/Other Phase**:
        i.  AI controls NPC units.
        ii. Check for and execute events triggered by NPC actions.
        iii.End phase.
    e.  **End of Turn Events**: Check and execute any events for end of turn.
    f.  Check Victory/Loss Conditions.
        *   Victory: (e.g., Seize throne, Defeat boss, Survive X turns, Escape).
            *   // TEST: Chapter victory condition is correctly detected.
        *   Loss: (e.g., Leif defeated, specific NPC defeated, objective failed).
            *   // TEST: Chapter loss condition (Leif defeated) is correctly detected.
    g.  Increment turn counter.
7.  **If Victory**: Execute chapter ending events (dialogue, character exits, map clear). Proceed to PostChapterSequence.
8.  **If Loss**: Proceed to GameOver state.

## 5. Event Flag Management

*   Flags are boolean values identified by a unique `FlagID`.
*   Flags can be **Chapter-Specific**: Reset at the beginning of each chapter (unless explicitly carried over by a game design choice for specific flags).
*   Flags can be **Global**: Persist across chapters and save/load cycles. The distinction should be clear from the `FlagID` range or a prefix/suffix.
*   The event system must provide `SET_FLAG FlagID` and `CLEAR_FLAG FlagID` commands.
*   Conditional event execution relies on `TEST_FLAG_SET FlagID` and `TEST_FLAG_UNSET FlagID`.
*   All active flags (both chapter and global) must be saved as part of the game state.
    *   // TEST: Chapter-specific flags reset on new chapter start.
    *   // TEST: Global flags persist across chapters.
    *   // TEST: All flags are correctly saved and loaded.

## 6. Unit Interaction with Events

*   Events can load new units (`LOAD_GROUP`).
*   Events can move existing units (`MOVE_CHAR`).
*   Events can remove units (`macroASMCRemoveUnit`). This is distinct from unit defeat; a removed unit might not trigger death-related flags or count as a casualty unless the event script explicitly sets such flags.
*   Events can modify unit properties (`macroASMCSetCharacterDataByte`).
*   Specific unit actions (Talk, Visit, Combat with specific enemies) can trigger events.
*   Unit death (player, enemy, or NPC) can trigger events or set flags that other events check.

## 7. Constraints and Assumptions

*   Event scripts (`.event` files) are assumed to be authored correctly according to the defined syntax. The system will attempt to be resilient to minor errors but is not expected to debug complex script logic errors.
*   No hard-coded secrets or environment variables will be present in event scripts or the event engine. Paths to resources like dialogue files or unit group definitions are relative to a known game data structure.
*   The event system operates sequentially within a given trigger block (e.g., all "Turn 3 Player Phase Start" events run one after another). The order of definition within the `.event` file for a specific trigger type dictates execution order.
*   Performance: The event system must process and execute events efficiently to avoid noticeable lag during gameplay, especially during phases with many potential triggers (e.g., enemy phase with many units moving and potentially triggering location or battle events).
*   Modularity: Event commands should be self-contained operations. The event engine itself will be a distinct module.
*   Testability: Individual event commands and trigger conditions must be testable in isolation.

## 8. Acceptance Criteria Summary

The Game Flow and Event System will be considered complete and correct when:
1.  The game correctly transitions between all defined game states (Title, World Map, Pre/Post Chapter, Gameplay, Game Over).
2.  The event engine can parse and execute all defined event commands from `.event` files.
3.  All specified event triggers (turn, location, talk, etc.) correctly activate their associated event scripts.
4.  Event flags (chapter-specific and global) are managed correctly, including setting, clearing, testing, and persistence through save/load.
5.  Unit groups are loaded and managed by events as specified.
6.  Dialogue, camera movements, sound/music, and visual effects are correctly controlled by events.
7.  Chapter lifecycle (load, opening events, main loop, victory/loss, ending events) functions as described.
8.  The system is robust to common non-critical errors in event scripts (e.g., by logging and skipping).
9.  All TDD anchors associated with game flow and events pass successfully.

## 9. Miscellaneous Mechanics to Specify Later

*   **Fog of War**: Limits visibility on certain maps. Events may be used to reveal areas.
*   **Shops/Armories**: Buying and selling items. Inventory defined in event files.
*   **Arenas**: Units can fight random enemies for EXP and gold.
*   **Support System**: Bonuses for units standing near allies they have support points with (data from `SupportData.csv`). Events might influence support points.
*   **Fatigue System**: Units accumulate fatigue, impacting performance or deployment. Events might cause or alleviate fatigue.
*   **Capture/Rescue/Steal**: Detailed mechanics. Events might be triggered by these actions or set up scenarios for them.
*   **Escape Maps**: Objective is to move units to specific escape tiles. Events will define escape points and conditions.
*   **Side Quests/Gaiden Chapters**: Unlocking conditions, often managed by global event flags.
*   **Game Configuration**: Options like animation speed, sound volume, etc. These are generally system-level, but events might temporarily override (e.g., force slow text for dramatic moments).

## 10. TDD Anchors (Consolidated)

*   `// TEST: Title screen displays options correctly.`
*   `// TEST: Player can select and start a chapter.`
*   `// TEST: Pre-chapter dialogue plays correctly.`
*   `// TEST: Phase transitions occur correctly (Player -> Enemy -> NPC -> Player).`
*   `// TEST: Post-chapter results (turns taken, units lost) are displayed.`
*   `// TEST: Post-chapter dialogue plays correctly.`
*   `// TEST: Game over screen appears on Leif's defeat.`
*   `// TEST: Game can be saved successfully, including event flag states.`
*   `// TEST: Saved game can be loaded and resumes at correct state with correct event flags.`
*   `// TEST: Units from a group are loaded at correct positions with correct stats/items.`
*   `// TEST: Character moves along the specified path or to the target coordinates.`
*   `// TEST: Unit is correctly removed from the map.`
*   `// TEST: Character data is correctly modified by event.`
*   `// TEST: Correct dialogue sequence is displayed.`
*   `// TEST: Camera moves to the correct position smoothly.`
*   `// TEST: Correct sound effect and music track play.`
*   `// TEST: Screen fades in/out correctly.`
*   `// TEST: Visiting a house grants the correct item.`
*   `// TEST: Shop at the location has the correct inventory.`
*   `// TEST: `SET_FLAG` correctly sets a flag to true.`
*   `// TEST: `CLEAR_FLAG` correctly sets a flag to false.`
*   `// TEST: Chapter-specific flags reset on new chapter start.`
*   `// TEST: Global flags persist across chapters.`
*   `// TEST: All flags are correctly saved and loaded.`
*   `// TEST: Unit is created with correct CharacterID, Allegiance, Level, Items, and AI.`
*   `// TEST: World map events trigger and execute correctly.`
*   `// TEST: All necessary chapter assets (map, units, items, events) are loaded.`
*   `// TEST: Opening cutscene plays out correctly, initial units are placed.`
*   `// TEST: Chapter victory condition is correctly detected.`
*   `// TEST: Chapter loss condition (Leif defeated) is correctly detected.`
*   `// TEST: Event_ChapterStart_OpeningScene`: Opening event sequence for a chapter plays correctly. (Redundant with more specific tests, can be high-level integration)
*   `// TEST: Event_TurnBased_Reinforcements`: Reinforcements appear on the correct turn.
*   `// TEST: Event_Location_HouseVisitItem`: Visiting a house grants the specified item and sets the event flag. (Covered by item house test)
*   `// TEST: Event_Talk_ConversationPlays`: Specified talk conversation occurs and sets its flag.
*   `// TEST: Event_BossQuote_TriggersInCombat`: Boss battle quote triggers when engaging the boss.
*   `// TEST: Event_UnitPlacement_CorrectInitialSetup`: All initial player and enemy units are placed correctly as per event file. (Covered by opening cutscene/unit load)
*   `// TEST: Event_Flag_PreventsReTrigger`: An event marked with a flag does not trigger again once the flag is set.
*   `// TEST: GameFlow_ChapterCompletion_ToWorldMapOrNextChapter`: Successfully completing a chapter transitions to the next appropriate game state.
*   `// TEST: GameFlow_PlayerPhase_UnitControl`: Player can select and command their units.
*   `// TEST: GameFlow_EnemyPhase_AIActivates`: Enemy units take actions during their phase.
*   `// TEST: GameFlow_Objective_SeizeThrone`: Chapter completes when Leif seizes the throne tile.
*   `// TEST: GameFlow_WorldMapEvent_PlaysCorrectly`: A world map event sequence between chapters executes. (Covered by world map event test)
*   `// TEST: UnitGroup_Load_CorrectUnitsAndItems`: `LOAD_GROUP` command correctly places units with their specified inventories and levels. (Covered by unit load test)

This specification covers the high-level game flow and the critical event system that drives chapter progression and dynamics.