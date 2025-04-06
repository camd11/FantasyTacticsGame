# Specification: Engine Core

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The Engine Core is the central orchestrator of the game. It manages the main game loop, controls turn and phase transitions, processes player input and AI actions, triggers events, and checks for victory or defeat conditions. It interacts heavily with the Game State Manager to read and update game data, and with the Data Provider to access static game definitions.

## 2. Functional Requirements

### 2.1. Game Initialization
    - Initialize game state for a new chapter (load map, units, events via Data Provider and Game State Manager).
    - Set initial turn number and phase (usually Player Phase, Turn 1).

### 2.2. Game Loop Management
    - Continuously execute the main game loop until a victory or loss condition is met.
    - The loop progresses through defined phases: Player -> Enemy -> NPC -> Player.

### 2.3. Phase Management
    - **Start Phase:**
        - Increment turn number if transitioning back to Player Phase.
        - Identify the active faction (Player, Enemy, NPC).
        - Reset action states for all units belonging to the active faction (e.g., `has_acted = false`).
        - Apply start-of-phase effects (e.g., terrain healing, poison damage) for the active faction's units (Ref: `research.md`, Sec 1, 9).
        - Check for turn-based events (Ref: `research.md`, Sec 11).
    - **Execute Phase:**
        - **Player Phase:** Wait for and process player input (unit selection, movement, action commands).
        - **Enemy/NPC Phase:** Iterate through active AI units, execute AI logic to determine and perform actions.
    - **End Phase:**
        - Check for end-of-phase events.
        - Check for victory/loss conditions (Ref: `research.md`, Sec 11).
        - Transition to the next phase in the sequence.

### 2.4. Action Processing
    - Receive action requests (from player input or AI).
    - Validate the action based on game rules and unit state (e.g., can move, has weapon uses, meets capture conditions).
    - Execute the action, updating the Game State Manager (e.g., move unit, calculate combat, apply status, update fatigue, use item durability).
    - Handle post-action effects:
        - Canto movement for mounted units after non-combat actions (Ref: `research.md`, Sec 1).
        - Check for Movement Star activation (Ref: `research.md`, Sec 1). If activated, allow the unit another action in the same phase.
        - Update unit fatigue based on action performed (Ref: `research.md`, Sec 7).
        - Mark the unit as having acted (`has_acted = true`).

### 2.5. Event System Interaction
    - Check for event triggers at appropriate times (start/end of turn/phase, unit moves to location, unit performs specific action like Talk/Visit).
    - Execute triggered event scripts (obtained via Data Provider), which may involve dialogue, unit spawning, item rewards, AI changes, state updates, etc. (Ref: `research.md`, Sec 11).

### 2.6. Victory/Loss Condition Checking
    - Continuously check for loss conditions (e.g., Leif's HP <= 0).
    - Check for victory conditions at appropriate times (e.g., end of phase, after Seize/Escape action). Conditions include Seize, Escape, Defend Turns, Rout (Ref: `research.md`, Sec 11).
    - Handle game end sequence (victory screen, save prompt, transition to next chapter/game over screen).

## 3. Pseudocode (engine_core.py)

```python
# --- engine_core.py ---

# Import necessary modules/classes (GameStateManager, DataProvider, AIController, InputHandler, EventSystem, CombatCalculator, etc.)

class EngineCore:
    gameStateManager = null
    dataProvider = null
    aiController = null
    inputHandler = null
    eventSystem = null
    combatCalculator = null
    # ... other necessary components

    current_turn = 0
    current_phase = PHASE_PLAYER # Enum: PHASE_PLAYER, PHASE_ENEMY, PHASE_NPC
    active_faction_units = []
    game_over = False
    victory = False

    # TDD: Test EngineCore initialization with a starting chapter state
    function initialize_chapter(chapter_id):
        log("Initializing Chapter: " + chapter_id)
        # Load static data via DataProvider
        map_data = dataProvider.get_map_data(chapter_id)
        unit_placements = dataProvider.get_unit_placements(chapter_id)
        event_scripts = dataProvider.get_event_scripts(chapter_id)

        # Initialize Game State via GameStateManager
        gameStateManager.load_map(map_data)
        gameStateManager.deploy_units(unit_placements, dataProvider) # Pass dataProvider to resolve unit base stats etc.
        eventSystem.load_scripts(event_scripts)

        current_turn = 1
        current_phase = PHASE_PLAYER
        game_over = False
        victory = False
        log("Chapter Initialized. Turn 1, Player Phase.")
        start_phase()

    # TDD: Test the main game loop progresses through phases correctly
    function run_game_loop():
        while not game_over and not victory:
            execute_phase()
            if not game_over and not victory: # Check again in case phase execution ended the game
                end_phase()
        
        if victory:
            handle_victory()
        elif game_over:
            handle_game_over()

    # TDD: Test start_phase resets unit actions and applies start-of-turn effects (poison, healing)
    function start_phase():
        log("Starting Phase: " + current_phase + " (Turn: " + current_turn + ")")
        active_faction_units = gameStateManager.get_units_by_faction(current_phase)

        # Reset action states and apply phase start effects
        for unit in active_faction_units:
            if not gameStateManager.is_unit_fatigued_for_deployment(unit.id): # Check fatigue status (relevant for player phase start)
                 unit.has_acted = False
                 unit.has_moved = False # Track movement separately if needed for Canto etc.
                 apply_start_of_phase_unit_effects(unit) # Handles poison, terrain heal, etc.
            else:
                 unit.has_acted = True # Fatigued units cannot act (except Leif) - handled here or in action validation

        # Check for turn-based events
        eventSystem.check_turn_events(current_turn, current_phase)
        check_game_end_conditions() # Events might trigger game end

    # TDD: Test player phase waits for input and processes valid actions
    # TDD: Test AI phase iterates units and executes AI actions
    function execute_phase():
        if current_phase == PHASE_PLAYER:
            # Player control loop
            while not all_player_units_acted() and not game_over and not victory:
                player_input = inputHandler.get_input()
                if player_input.type == INPUT_END_TURN:
                    break # Player chose to end phase early
                elif player_input.type == INPUT_ACTION:
                    process_action(player_input.unit_id, player_input.action_data)
                # ... handle other input types (select unit, view map, open menu etc.)
                check_game_end_conditions() # Action might trigger game end

        elif current_phase == PHASE_ENEMY or current_phase == PHASE_NPC:
            # AI control loop
            # Determine unit order (e.g., based on deployment list or initiative)
            ordered_units = sort_units_for_ai(active_faction_units)
            for unit in ordered_units:
                 if not unit.has_acted and not game_over and not victory:
                     # Check status effects like Sleep/Berserk that prevent AI control
                     if can_unit_act(unit):
                         ai_action = aiController.determine_action(unit, gameStateManager)
                         if ai_action:
                             process_action(unit.id, ai_action)
                         else:
                             # AI decides to wait or cannot act
                             unit.has_acted = True 
                 check_game_end_conditions() # Action might trigger game end
                 if game_over or victory: break # Stop processing AI if game ended

    # TDD: Test end_phase transitions correctly (Player -> Enemy -> NPC -> Player)
    # TDD: Test end_phase increments turn number correctly
    function end_phase():
        log("Ending Phase: " + current_phase)
        eventSystem.check_phase_end_events(current_turn, current_phase)
        check_game_end_conditions() # Check again after end-phase events

        if game_over or victory: return

        # Transition to next phase
        if current_phase == PHASE_PLAYER:
            current_phase = PHASE_ENEMY
        elif current_phase == PHASE_ENEMY:
            if gameStateManager.has_npc_units():
                current_phase = PHASE_NPC
            else:
                current_phase = PHASE_PLAYER
                current_turn += 1
        elif current_phase == PHASE_NPC:
            current_phase = PHASE_PLAYER
            current_turn += 1
        
        start_phase() # Start the next phase

    # TDD: Test process_action validates and executes various actions (Move, Attack, Capture, Use Item, Talk, Visit, Seize, Escape)
    # TDD: Test process_action updates fatigue correctly based on action type
    # TDD: Test process_action handles Canto movement
    # TDD: Test process_action checks for Movement Star activation
    function process_action(unit_id, action_data):
        unit = gameStateManager.get_unit(unit_id)
        if not can_unit_act(unit) or unit.has_acted:
             log("Warning: Unit " + unit_id + " cannot act or has already acted.")
             return

        is_valid = validate_action(unit, action_data)
        if not is_valid:
            log("Warning: Invalid action requested for unit " + unit_id)
            # Provide feedback to player or log for AI
            return

        log("Processing action for unit " + unit_id + ": " + action_data.type)
        
        # --- Execute Action ---
        action_result = null
        requires_extra_action_check = True # Most actions allow for Movement Star check
        allows_canto = False # Only specific non-combat actions allow Canto

        if action_data.type == ACTION_MOVE:
            gameStateManager.move_unit(unit_id, action_data.target_pos)
            unit.has_moved = True
            # Note: Move itself doesn't end the turn, usually followed by another action or Wait
            requires_extra_action_check = False # Moving alone doesn't trigger star check? Verify FE5 rule. Assume only *after* full action.
        
        elif action_data.type == ACTION_ATTACK:
            action_result = combatCalculator.resolve_combat(unit_id, action_data.target_id, is_capture=False)
            gameStateManager.apply_combat_results(action_result)
            gameStateManager.update_fatigue(unit_id, FATIGUE_COMBAT)
            unit.has_acted = True
            allows_canto = False # Cannot Canto after attack

        elif action_data.type == ACTION_CAPTURE:
            action_result = combatCalculator.resolve_combat(unit_id, action_data.target_id, is_capture=True) # Combat calc needs to handle halved stats for capture
            gameStateManager.apply_combat_results(action_result) # Includes setting captured state if successful
            gameStateManager.update_fatigue(unit_id, FATIGUE_COMBAT) # Capturing counts as combat for fatigue
            unit.has_acted = True
            allows_canto = False # Cannot Canto after capture attempt

        elif action_data.type == ACTION_USE_ITEM:
            item_result = gameStateManager.use_item(unit_id, action_data.item_index, action_data.target_id) # Target might be self or ally
            # TDD: Test fatigue update for staff usage based on rank
            if item_result.is_staff:
                 fatigue_cost = calculate_staff_fatigue(item_result.item_rank)
                 gameStateManager.update_fatigue(unit_id, fatigue_cost)
            # TDD: Test fatigue update for Dance/Steal (if implemented as item use)
            # elif item_result.is_dance_or_steal: gameStateManager.update_fatigue(unit_id, FATIGUE_SPECIAL_ACTION)
            unit.has_acted = True
            allows_canto = True # Can Canto after using item (Ref: research.md Sec 1)

        elif action_data.type == ACTION_TRADE:
            gameStateManager.trade_items(unit_id, action_data.partner_id, action_data.item_transfers)
            # Trading is free and doesn't end the action (Ref: research.md Sec 4)
            requires_extra_action_check = False # Trading itself doesn't end the action or trigger star
            unit.has_acted = False # Can still act after trading
            return # Exit early, don't proceed to post-action checks yet

        elif action_data.type == ACTION_VISIT or action_data.type == ACTION_TALK:
            eventSystem.check_action_event(unit_id, action_data.type, action_data.target_pos_or_id)
            unit.has_acted = True
            allows_canto = True # Can Canto after Visit/Talk? Assume yes for non-combat. Verify FE5 rule.

        elif action_data.type == ACTION_WAIT:
            unit.has_acted = True
            allows_canto = True # Can Canto after Wait (effectively just moving)

        elif action_data.type == ACTION_SEIZE:
            if unit_id == LEIF_ID and gameStateManager.is_tile_seize_point(unit.position):
                 victory = True # Set victory flag
                 log("Victory Condition Met: Seize!")
            unit.has_acted = True
            allows_canto = False # Seizing ends the chapter

        # ... handle other actions: Rescue, Drop, Release, Dismount, Mount, Steal, Dance etc.
        # Each should update fatigue appropriately and set allows_canto flag.

        # --- Post-Action Processing ---
        if unit.has_acted and not game_over and not victory:
            # 1. Canto Check (only if action allowed it and unit is mounted)
            if allows_canto and gameStateManager.is_unit_mounted(unit_id) and unit.has_moved: # Check if unit moved this turn
                 remaining_movement = calculate_remaining_movement(unit) # Based on path taken vs Mov stat
                 if remaining_movement > 0:
                     # Allow player/AI to input Canto movement
                     canto_move = get_canto_input_or_ai(unit, remaining_movement)
                     if canto_move:
                         gameStateManager.move_unit(unit_id, canto_move.target_pos) # Apply Canto move

            # 2. Movement Star Check (only if action completed, not just trade/move)
            # TDD: Test Movement Star check triggers correctly based on unit stars
            if requires_extra_action_check:
                 num_stars = gameStateManager.get_unit_movement_stars(unit_id)
                 if num_stars > 0:
                     chance = num_stars * 5 # 5% per star
                     if random_chance(chance):
                         log("Movement Star activated for unit " + unit_id + "!")
                         unit.has_acted = False # Allow another action
                         # Maybe add visual indicator/sound effect trigger here
                         # Need to handle potential infinite loops? FE5 likely allows multiple procs.

        # Check events triggered by action result (e.g., enemy defeated event)
        if action_result:
             eventSystem.check_result_events(action_result)

        check_game_end_conditions()

    # TDD: Test victory/loss condition checks trigger correctly
    function check_game_end_conditions():
        if game_over or victory: return # Already decided

        # Loss Conditions
        leif = gameStateManager.get_unit(LEIF_ID)
        if leif and leif.current_hp <= 0:
            game_over = True
            log("Game Over: Leif has fallen!")
            return
        # Add other loss conditions (e.g., defend point captured, required NPC dies)
        if eventSystem.check_loss_conditions(gameStateManager):
             game_over = True
             log("Game Over: Loss condition met.")
             return

        # Victory Conditions (Seize handled in process_action, check others here)
        if eventSystem.check_victory_conditions(gameStateManager, current_turn):
             victory = True
             log("Victory Condition Met!")
             return

    function all_player_units_acted():
        player_units = gameStateManager.get_units_by_faction(PHASE_PLAYER)
        for unit in player_units:
            # Check if unit is deployable and hasn't acted
            if not gameStateManager.is_unit_fatigued_for_deployment(unit.id) and not unit.has_acted:
                 # Also consider units under status effects like Sleep
                 if can_unit_act(unit):
                     return False
        return True # All active, non-fatigued, non-slept units have acted

    function can_unit_act(unit):
        # Check for statuses like Sleep, Petrify, Berserk (handled by AI), etc.
        return not unit.has_status(STATUS_SLEEP) and not unit.has_status(STATUS_PETRIFY) # etc.

    function handle_victory():
        log("Chapter Cleared!")
        # Show victory screen, save game state, proceed to next chapter logic...
        # Handle fatigue updates for deployed units at chapter end
        gameStateManager.finalize_chapter_fatigue()
        # Handle escape map unit capture if Leif escaped early
        gameStateManager.finalize_escape_map_captures()

    function handle_game_over():
        log("Game Over!")
        # Show game over screen, offer retry/load options...

    # ... other helper functions (validate_action, apply_start_of_phase_unit_effects, calculate_staff_fatigue, etc.)