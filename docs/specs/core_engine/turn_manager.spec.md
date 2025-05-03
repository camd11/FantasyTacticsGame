# Specification: Turn Manager (`TurnManager`)

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The `TurnManager` is responsible for controlling the overall flow of the game turn by turn. It manages the sequence of phases (Player, Enemy, NPC), tracks the current turn number, handles phase transitions, and orchestrates the execution of turn-based effects like status condition updates, terrain healing, and fatigue checks.

## 2. Responsibilities

-   Track the current turn number.
-   Manage the current active phase (Player, Enemy, NPC).
-   Transition between phases in the correct order (Player -> Enemy -> NPC -> Player).
-   Initiate start-of-phase effects (e.g., status damage/recovery, terrain healing).
-   Initiate end-of-phase effects (e.g., checking for Movement Star activation, fatigue accumulation).
-   Reset unit action states at the beginning of each phase.
-   Coordinate with the `EventHandler` to check for turn-based events.
-   Coordinate with the `GameStateManager` to update the game state regarding turns and phases.

## 3. Dependencies

-   `GameStateManager`: To get and update the current game state (turn, phase, unit statuses).
-   `UnitSystem`: To access unit data (HP, status effects, fatigue, Movement Stars, position, faction).
-   `MapSystem`: To check terrain properties (e.g., healing tiles).
-   `EventHandler`: To trigger checks for turn-based events.
-   `DataProvider`: To fetch game configuration (e.g., fatigue start chapter).

## 4. Core Concepts

-   **Phase:** Represents the period during which units of a specific faction can act. The standard sequence is Player -> Enemy -> NPC.
-   **Turn:** A full cycle through all active phases.
-   **Turn Start Effects:** Actions processed at the very beginning of a faction's phase (e.g., Poison damage for player units at Player Phase start).
-   **Turn End Effects:** Actions processed after a unit completes its action or at the end of a phase (e.g., Movement Star check, Fatigue accumulation).
-   **Movement Stars (Re-move):** A chance for a unit to act again after completing an action, checked at the end of their action.
-   **Fatigue:** A mechanic tracking unit exertion, checked and potentially applied at the end of a chapter based on actions taken during the chapter (starts from Chapter 8 as per `research.md`). The `TurnManager` increments fatigue counters during the turn.

## 5. Pseudocode

```pseudocode
class TurnManager:
    // Dependencies
    gameStateManager: GameStateManager
    unitSystem: UnitSystem
    mapSystem: MapSystem
    eventHandler: EventHandler
    dataProvider: DataProvider

    // State
    currentTurn: Integer = 0
    currentPhase: Phase = Phase.PLAYER // PLAYER, ENEMY, NPC
    fatigueEnabled: Boolean = false // Based on chapter

    // TDD Anchor: test_turn_manager_initialization
    function initialize(initialGameState):
        currentTurn = initialGameState.turn_number
        currentPhase = initialGameState.current_phase
        // Determine if fatigue system should be active based on chapter number
        fatigueStartChapter = dataProvider.get_config("fatigue_start_chapter", default=8)
        fatigueEnabled = currentTurn >= fatigueStartChapter // Or based on chapter ID if turns reset
        // Potentially load other turn-related state
        print("TurnManager initialized. Turn: ", currentTurn, ", Phase: ", currentPhase)

    // TDD Anchor: test_start_new_turn
    function start_new_turn():
        currentTurn += 1
        currentPhase = Phase.PLAYER
        gameStateManager.update_turn(currentTurn)
        gameStateManager.update_phase(currentPhase)
        print("Starting Turn: ", currentTurn)
        start_phase(currentPhase)

    // TDD Anchor: test_next_phase_transitions
    function next_phase():
        end_phase(currentPhase)

        if currentPhase == Phase.PLAYER:
            currentPhase = Phase.ENEMY
        elif currentPhase == Phase.ENEMY:
            // Check if NPC units exist
            if unitSystem.get_units_by_faction(Faction.NPC).size > 0:
                currentPhase = Phase.NPC
            else:
                // Skip NPC phase if no NPCs
                currentPhase = Phase.PLAYER
                start_new_turn() // Start next turn directly
                return // Exit early as start_phase is called by start_new_turn
        elif currentPhase == Phase.NPC:
            currentPhase = Phase.PLAYER
            start_new_turn() // Start next turn
            return // Exit early

        gameStateManager.update_phase(currentPhase)
        start_phase(currentPhase)

    // TDD Anchor: test_start_phase_resets_actions_and_triggers_events
    function start_phase(phase: Phase):
        print("Starting Phase: ", phase)
        // Reset action state for all units of the current phase's faction
        activeUnits = unitSystem.get_units_by_faction(phase.to_faction())
        for unit in activeUnits:
            unitSystem.reset_unit_action_state(unit.id)
            // Handle fatigued units (cannot act, except Leif)
            if fatigueEnabled and unitSystem.is_fatigued(unit.id) and not unitSystem.is_lord(unit.id):
                 unitSystem.mark_unit_as_acted(unit.id) // Prevent action

        // Apply start-of-phase effects for this faction's units
        apply_start_of_phase_effects(phase)

        // Check for events triggered by phase start or turn number
        eventHandler.check_turn_events(currentTurn, phase)

        // If AI phase, trigger AI Manager
        if phase == Phase.ENEMY or phase == Phase.NPC:
            // Signal AI Manager to start processing units for this phase
            // aiManager.process_phase(phase) // Responsibility might lie elsewhere (e.g., main game loop)

    // TDD Anchor: test_end_phase_triggers_events
    function end_phase(phase: Phase):
        print("Ending Phase: ", phase)
        // Check for end-of-phase events
        // eventHandler.check_phase_end_events(currentTurn, phase) // If any specific end-of-phase events exist

    // TDD Anchor: test_apply_start_of_phase_effects_handles_poison_and_healing
    function apply_start_of_phase_effects(phase: Phase):
        activeUnits = unitSystem.get_units_by_faction(phase.to_faction())
        for unit in activeUnits:
            // Apply Poison damage
            if unitSystem.has_status(unit.id, StatusEffect.POISON):
                poisonDamage = dataProvider.get_status_effect_param("poison", "damage", default=1)
                unitSystem.apply_damage(unit.id, poisonDamage)
                // Check if unit died from poison
                if unitSystem.get_unit(unit.id).current_hp <= 0:
                    // Handle unit death (e.g., mark as dead, trigger events)
                    print(unit.name, " succumbed to poison.")
                    // eventHandler.check_death_events(unit.id)

            // Apply Terrain Healing
            unitPosition = unitSystem.get_unit_position(unit.id)
            terrain = mapSystem.get_terrain_at(unitPosition)
            if terrain.provides_healing():
                healingAmount = terrain.get_healing_amount()
                unitSystem.apply_healing(unit.id, healingAmount)

            // Apply other status effect upkeep (e.g., temporary stat decay like M Up)
            unitSystem.process_status_upkeep(unit.id)

    // TDD Anchor: test_check_movement_star_activation
    function check_movement_star(unit_id: String):
        unit = unitSystem.get_unit(unit_id)
        if unit.movement_stars > 0:
            activationChance = unit.movement_stars * 5 // 5% per star
            randomNumber = generate_random_percentage() // 0-99
            if randomNumber < activationChance:
                print(unit.name, " activated Movement Star!")
                unitSystem.reset_unit_action_state(unit_id) // Allow unit to act again
                // Potentially trigger visual effect/sound
                return true // Star activated
        return false // Star did not activate

    // TDD Anchor: test_increment_fatigue_on_action
    function record_action_fatigue(unit_id: String, action_type: ActionType):
        if not fatigueEnabled:
            return

        unit = unitSystem.get_unit(unit_id)
        if unitSystem.is_lord(unit.id): // Leif is exempt
            return

        fatigueCost = 0
        if action_type == ActionType.COMBAT or action_type == ActionType.CAPTURE:
            fatigueCost = 1
        elif action_type == ActionType.STAFF:
            // Fatigue cost depends on staff rank (needs item info)
            // staffRank = inventorySystem.get_equipped_staff_rank(unit_id)
            // fatigueCost = dataProvider.get_staff_fatigue_cost(staffRank) // e.g., E=1, D=2, C=3, B=4, A=5
            fatigueCost = 1 // Placeholder
        elif action_type == ActionType.STEAL or action_type == ActionType.DANCE:
            fatigueCost = 1
        // Other actions might not cause fatigue

        if fatigueCost > 0:
            unitSystem.increase_fatigue(unit_id, fatigueCost)
            // Check if fatigue now exceeds Max HP (for potential UI indicators)
            // currentFatigue = unitSystem.get_fatigue(unit_id)
            // maxHP = unit.max_hp
            // if currentFatigue >= maxHP:
            //     gameStateManager.update_unit_state(unit_id, State.FATIGUED_PENDING) // Mark for UI

    // TDD Anchor: test_end_of_chapter_fatigue_application
    function apply_end_of_chapter_fatigue(deployed_unit_ids: List[String]):
        // This might be called by the main engine/game state manager at chapter end
        if not fatigueEnabled:
            return

        all_units = unitSystem.get_all_player_units()
        for unit in all_units:
            if unitSystem.is_lord(unit.id): // Leif exempt
                continue

            if unit.id in deployed_unit_ids:
                // Check if fatigue >= max HP
                if unitSystem.get_fatigue(unit.id) >= unit.max_hp:
                    unitSystem.set_unit_status(unit.id, Status.FATIGUED)
                    print(unit.name, " is fatigued and must rest.")
                else:
                    // Fatigue carries over if not rested, but not applied as status
                    pass
            else:
                // Unit was benched, reset fatigue
                unitSystem.reset_fatigue(unit.id)
                // Clear any FATIGUED status if they were previously fatigued
                if unitSystem.has_status(unit.id, Status.FATIGUED):
                    unitSystem.remove_status(unit.id, Status.FATIGUED)

end class

enum Phase:
    PLAYER
    ENEMY
    NPC

    function to_faction(self):
        if self == Phase.PLAYER: return Faction.PLAYER
        if self == Phase.ENEMY: return Faction.ENEMY
        if self == Phase.NPC: return Faction.NPC
```

## 6. Data Structures

-   `Phase` Enum: PLAYER, ENEMY, NPC.
-   Internal state tracking `currentTurn` (Integer) and `currentPhase` (Phase).

## 7. Edge Cases & Considerations

-   **Skipping Phases:** If no units of a certain faction exist (e.g., no NPCs on the map), their phase should be skipped automatically.
-   **Fatigue Start:** Fatigue mechanic only becomes active from a specific chapter (Chapter 8). The manager needs to know the current chapter or turn context to enable/disable fatigue tracking and application.
-   **Leif Exemption:** Leif (the Lord) is immune to being forced to sit out due to fatigue.
-   **Movement Star Interaction:** If a unit activates a Movement Star, their action state needs to be reset immediately, allowing them to perform another action within the same phase. The `TurnManager` needs a way to be notified or check for this after an action completes.
-   **End of Chapter Fatigue:** The final application of the "Fatigued" status happens *after* the chapter ends, affecting deployment in the *next* chapter. The `TurnManager` accumulates fatigue points during the chapter; another system (likely the main game loop or state manager) triggers the final check and status application based on deployment status. Benched units have fatigue reset.
-   **Events:** Turn-based events (reinforcements, AI changes) need to be checked at the correct point in the turn cycle (often start or end of a specific phase).

## 8. Future Enhancements

-   Support for more complex phase structures if needed (e.g., multiple allied factions).
-   More granular control over turn start/end effect timing.
-   Integration with a potential weather system affecting turns.