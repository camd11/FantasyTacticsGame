# Pseudocode for Two-Phase Goal-Oriented Utility AI (v2)

## Overview

This document provides pseudocode for the core components of the AI system described in `specs/ai_architecture_v2.md`. It outlines the structure and logic for Goal Representation, Utility Scoring, Strategic Evaluation, Tactical Execution, and the overall AI Management process.

---

## 1. Goal Representation

Goals represent high-level strategic objectives for an AI unit. They define the *what* the AI wants to achieve, not the *how*.

```pseudocode
// Base class/interface for all Goals
CLASS Goal:
    // Unique identifier for the goal type (e.g., "ATTACK_UNIT", "HEAL_ALLY")
    PROPERTY goal_type: String

    // Specific parameters for this goal instance (e.g., target unit, target position)
    PROPERTY parameters: Dictionary

    // Function to check if this goal is currently valid/possible given the game state
    // TDD_ANCHOR: test_goal_validity_various_states
    METHOD is_valid(unit, game_state): Boolean
        // Implementation varies per goal type
        // Example: ATTACK_UNIT is valid only if there are reachable enemies
        RETURN true // Placeholder

    // Function to generate potential actions that could fulfill this goal
    // TDD_ANCHOR: test_goal_action_generation_specific_goals
    METHOD generate_potential_actions(unit, game_state): List<Action>
        // Implementation varies per goal type
        // Example: ATTACK_UNIT generates Move+Attack actions towards valid targets
        RETURN [] // Placeholder

    // Function to provide goal-specific scoring considerations for tactical evaluation
    // TDD_ANCHOR: test_goal_tactical_scorers_retrieval
    METHOD get_tactical_scorers(persona): List<ScoringConsideration>
        // Returns a list of scorers relevant to achieving this specific goal,
        // potentially weighted or selected based on the persona.
        RETURN [] // Placeholder

// Example Concrete Goal: Attack a specific unit
CLASS Goal_AttackUnit(Goal):
    PROPERTY goal_type = "ATTACK_UNIT"
    PROPERTY parameters = { target_unit_id: null } // Specific enemy unit to target

    CONSTRUCTOR(target_unit_id):
        parameters.target_unit_id = target_unit_id

    METHOD is_valid(unit, game_state): Boolean
        target_unit = game_state.get_unit_by_id(parameters.target_unit_id)
        IF target_unit IS NULL OR target_unit.is_defeated() OR target_unit.faction == unit.faction:
            RETURN false
        // Check if target is potentially reachable/attackable (basic check)
        // More detailed checks happen in Tactical Execution
        RETURN game_state.pathfinding.can_potentially_reach(unit, target_unit.position)

    METHOD generate_potential_actions(unit, game_state): List<Action>
        actions = []
        target_unit = game_state.get_unit_by_id(parameters.target_unit_id)
        IF target_unit IS NULL: RETURN []

        // Find reachable tiles from which the target can be attacked
        reachable_attack_positions = game_state.get_reachable_attack_positions(unit, target_unit)

        FOR pos IN reachable_attack_positions:
            // Create Move+Attack action instances
            action = Action_MoveAttack(target_position=pos, attack_target_id=target_unit.id)
            actions.append(action)

        RETURN actions

    METHOD get_tactical_scorers(persona): List<ScoringConsideration>
        // Return scorers relevant to attacking: DamageDealt, KillPotential, SelfPreservation (counter-attack), etc.
        RETURN persona.get_scorers_for_goal(self.goal_type)


// Example Concrete Goal: Move to a safe position
CLASS Goal_MoveToSafety(Goal):
    PROPERTY goal_type = "MOVE_TO_SAFETY"
    PROPERTY parameters = {} // No specific target needed initially

    METHOD is_valid(unit, game_state): Boolean
        // Valid if unit is threatened or low health
        RETURN game_state.is_unit_threatened(unit) OR unit.current_hp < unit.max_hp * 0.5

    METHOD generate_potential_actions(unit, game_state): List<Action>
        actions = []
        safe_tiles = game_state.find_safe_tiles_for_unit(unit) // Tiles with low threat

        FOR tile IN safe_tiles:
            IF game_state.pathfinding.is_reachable(unit, tile):
                action = Action_MoveWait(target_position=tile)
                actions.append(action)
        RETURN actions

    METHOD get_tactical_scorers(persona): List<ScoringConsideration>
        // Return scorers relevant to safety: ThreatAvoidance, TerrainDefense, SelfPreservation
        RETURN persona.get_scorers_for_goal(self.goal_type)

// Other Goal examples: HealUnit, SeizeTile, SupportAlly, AdvanceToObjective, etc.
```

---

## 2. Utility Scorer

The Utility Scorer provides a framework for evaluating Goals and Actions using a set of weighted "Considerations".

```pseudocode
// Represents a single scoring factor (e.g., Damage Dealt, Threat Level)
CLASS ScoringConsideration:
    PROPERTY name: String // e.g., "DamageDealt"
    PROPERTY weight: Float // How important this factor is (often persona-dependent)

    // Function to calculate the raw score (0.0 to 1.0) for this consideration
    // The context object will differ for Strategic vs Tactical scoring
    // TDD_ANCHOR: test_consideration_scoring_various_contexts
    METHOD calculate_score(context): Float
        // Implementation specific to the consideration
        // Context might include: unit, game_state, target_goal, potential_action, etc.
        RETURN 0.0 // Placeholder

// The main Utility Scorer module/class
CLASS UtilityScorer:

    // Scores a potential Goal during the Strategic Phase
    // TDD_ANCHOR: test_strategic_goal_scoring_different_personas
    METHOD score_strategic_goal(unit, goal, game_state, persona): Float
        total_score = 0.0
        total_weight = 0.0

        // Get relevant strategic considerations from the persona
        strategic_considerations = persona.get_strategic_considerations()

        FOR consideration IN strategic_considerations:
            // Context for strategic scoring includes the goal itself
            context = { unit: unit, goal: goal, game_state: game_state, persona: persona }
            raw_score = consideration.calculate_score(context)
            weighted_score = raw_score * consideration.weight
            total_score += weighted_score
            total_weight += consideration.weight

        // Normalize score (optional, but good practice)
        IF total_weight > 0:
            RETURN total_score / total_weight
        ELSE:
            RETURN 0.0

    // Scores a potential Action during the Tactical Phase for a given Goal
    // TDD_ANCHOR: test_tactical_action_scoring_different_goals
    METHOD score_tactical_action(unit, action, current_goal, game_state, persona): Float
        total_score = 0.0
        total_weight = 0.0

        // Get relevant tactical considerations from the Goal and Persona
        tactical_considerations = current_goal.get_tactical_scorers(persona)

        FOR consideration IN tactical_considerations:
            // Context for tactical scoring includes the specific action being evaluated
            // May involve simulating the action's outcome
            context = { unit: unit, action: action, goal: current_goal, game_state: game_state, persona: persona }
            // Simulate action outcome if needed for scoring (using a temporary state copy)
            // simulated_state = game_state.simulate_action(action)
            // context.simulated_state = simulated_state
            raw_score = consideration.calculate_score(context)
            weighted_score = raw_score * consideration.weight
            total_score += weighted_score
            total_weight += consideration.weight

        // Normalize score
        IF total_weight > 0:
            RETURN total_score / total_weight
        ELSE:
            RETURN 0.0

// Example Consideration Implementation
CLASS Consideration_DamageDealt(ScoringConsideration):
    PROPERTY name = "DamageDealt"

    METHOD calculate_score(context): Float
        action = context.get("action")
        IF action IS NULL OR action.type != "MoveAttack":
            RETURN 0.0

        unit = context.unit
        target_unit = context.game_state.get_unit_by_id(action.attack_target_id)
        IF target_unit IS NULL: RETURN 0.0

        // Simulate combat preview
        combat_preview = context.game_state.simulate_combat(unit, target_unit, action.target_position)
        damage = combat_preview.attacker_damage

        // Normalize damage based on target's max HP
        normalized_score = damage / target_unit.max_hp
        RETURN clamp(normalized_score, 0.0, 1.0)

CLASS Consideration_ThreatLevel(ScoringConsideration):
    PROPERTY name = "ThreatLevel" // Used strategically

    METHOD calculate_score(context): Float
        goal = context.get("goal")
        IF goal IS NULL OR goal.goal_type != "ATTACK_UNIT":
             RETURN 0.0 // Only relevant for attack goals

        target_unit = context.game_state.get_unit_by_id(goal.parameters.target_unit_id)
        IF target_unit IS NULL: RETURN 0.0

        // Calculate threat based on target's potential damage, stats, etc.
        threat_value = context.game_state.calculate_unit_threat(target_unit)
        // Normalize threat (e.g., based on average unit threat in the scenario)
        normalized_threat = threat_value / context.game_state.get_average_threat()
        RETURN clamp(normalized_threat, 0.0, 1.0)

```

---

## 3. Strategic Evaluator

Selects the best high-level Goal for the unit's turn.

```pseudocode
CLASS StrategicEvaluator:
    PROPERTY utility_scorer: UtilityScorer
    PROPERTY goal_library: List<Goal> // All available goal *types*

    CONSTRUCTOR(utility_scorer, goal_library):
        self.utility_scorer = utility_scorer
        self.goal_library = goal_library

    // TDD_ANCHOR: test_strategic_evaluator_selects_highest_utility_goal
    // TDD_ANCHOR: test_strategic_evaluator_handles_no_valid_goals
    METHOD select_goal(unit, game_state, persona): Goal
        best_goal = null
        highest_score = -Infinity

        // 1. Goal Enumeration & Validation
        potential_goals = self.generate_valid_goal_instances(unit, game_state)

        // 2. Strategic Evaluation
        FOR goal IN potential_goals:
            score = self.utility_scorer.score_strategic_goal(unit, goal, game_state, persona)

            // Logging (Optional)
            // log(f"Goal: {goal.goal_type}, Params: {goal.parameters}, Score: {score}")

            IF score > highest_score:
                highest_score = score
                best_goal = goal
            // Add tie-breaking logic if necessary (e.g., based on persona defaults)

        // 3. Goal Selection
        IF best_goal IS NULL:
            // Default Goal (e.g., Wait or basic Move) if no other goal is suitable
            best_goal = Goal_Wait() // Or similar fallback
            // log("No suitable strategic goal found, defaulting to Wait.")

        // log(f"Selected Goal: {best_goal.goal_type}, Score: {highest_score}")
        RETURN best_goal

    // Helper to create specific, valid goal instances
    METHOD generate_valid_goal_instances(unit, game_state): List<Goal>
        valid_instances = []
        FOR GoalType IN self.goal_library:
            // Generate instances based on context (e.g., AttackUnit for each enemy)
            IF GoalType == Goal_AttackUnit:
                FOR enemy IN game_state.get_enemy_units(unit.faction):
                    goal_instance = Goal_AttackUnit(enemy.id)
                    IF goal_instance.is_valid(unit, game_state):
                        valid_instances.append(goal_instance)
            ELSE IF GoalType == Goal_HealAlly:
                 FOR ally IN game_state.get_allied_units(unit.faction):
                     IF ally.current_hp < ally.max_hp: // Basic condition
                         goal_instance = Goal_HealAlly(ally.id)
                         IF goal_instance.is_valid(unit, game_state):
                             valid_instances.append(goal_instance)
            // ... Add logic for other goal types (MoveToSafety, SeizeTile, etc.)
            ELSE: // For goals without specific targets (like MoveToSafety)
                goal_instance = GoalType()
                IF goal_instance.is_valid(unit, game_state):
                    valid_instances.append(goal_instance)

        RETURN valid_instances

```

---

## 4. Tactical Executor

Takes a selected Goal and finds the best concrete Action to achieve it.

```pseudocode
// Base class/interface for Actions
CLASS Action:
    PROPERTY type: String // e.g., "MoveAttack", "MoveWait", "UseItem"
    PROPERTY parameters: Dictionary // e.g., { target_position: (x,y), attack_target_id: id }

    // Function to check if the action is valid given the current state
    // (e.g., path exists, target in range, item available)
    // TDD_ANCHOR: test_action_validation_various_scenarios
    METHOD is_valid(unit, game_state): Boolean
        RETURN true // Placeholder

    // Function to execute the action on the game state
    // TDD_ANCHOR: test_action_execution_updates_state_correctly
    METHOD execute(unit, game_state):
        // Modify game_state based on the action
        PASS // Placeholder

// Example Concrete Action
CLASS Action_MoveAttack(Action):
    PROPERTY type = "MoveAttack"
    PROPERTY parameters = { target_position: null, attack_target_id: null }

    CONSTRUCTOR(target_position, attack_target_id):
        parameters.target_position = target_position
        parameters.attack_target_id = attack_target_id

    METHOD is_valid(unit, game_state): Boolean
        // Check path validity to target_position
        IF NOT game_state.pathfinding.is_reachable(unit, parameters.target_position):
            RETURN false
        // Check if attack_target_id exists and is attackable from target_position
        target_unit = game_state.get_unit_by_id(parameters.attack_target_id)
        IF target_unit IS NULL OR NOT game_state.can_attack_from(unit, parameters.target_position, target_unit):
            RETURN false
        RETURN true

    METHOD execute(unit, game_state):
        game_state.move_unit(unit, parameters.target_position)
        target_unit = game_state.get_unit_by_id(parameters.attack_target_id)
        IF target_unit IS NOT NULL:
            game_state.execute_combat(unit, target_unit)


CLASS TacticalExecutor:
    PROPERTY utility_scorer: UtilityScorer

    CONSTRUCTOR(utility_scorer):
        self.utility_scorer = utility_scorer

    // TDD_ANCHOR: test_tactical_executor_selects_highest_utility_action
    // TDD_ANCHOR: test_tactical_executor_handles_no_valid_actions
    METHOD select_action(unit, selected_goal, game_state, persona): Action
        best_action = null
        highest_score = -Infinity

        // 1. Action Space Pruning (Generate actions relevant to the goal)
        potential_actions = selected_goal.generate_potential_actions(unit, game_state)

        // 2. Tactical Evaluation
        FOR action IN potential_actions:
            // 2a. Validation (Double-check validity in current state)
            IF NOT action.is_valid(unit, game_state):
                CONTINUE // Skip invalid actions

            // 2b. Scoring
            score = self.utility_scorer.score_tactical_action(unit, action, selected_goal, game_state, persona)

            // Logging (Optional)
            // log(f"  Action: {action.type}, Params: {action.parameters}, Score: {score}")

            IF score > highest_score:
                highest_score = score
                best_action = action
            // Add tie-breaking logic if necessary

        // 3. Action Selection
        IF best_action IS NULL:
            // Fallback action if no goal-specific action is possible/valid
            // Usually a simple Move towards goal target or just Wait
            best_action = self.generate_fallback_action(unit, selected_goal, game_state)
            // log("No suitable tactical action found, using fallback.")

        // log(f"  Selected Action: {best_action.type}, Score: {highest_score}")
        RETURN best_action

    METHOD generate_fallback_action(unit, goal, game_state): Action
        // Simple fallback: Try to move closer to a target if applicable, otherwise wait.
        target_pos = goal.parameters.get("target_position") // Or derive from target_unit etc.
        IF target_pos AND game_state.pathfinding.can_potentially_reach(unit, target_pos):
            move_target = game_state.pathfinding.find_closest_reachable_tile(unit, target_pos)
            IF move_target:
                RETURN Action_MoveWait(target_position=move_target)

        // Default fallback: Wait in place
        RETURN Action_Wait(target_position=unit.position)

```

---

## 5. AI Manager / Orchestrator

Coordinates the overall AI decision process for a single unit's turn.

```pseudocode
CLASS AIManager:
    PROPERTY strategic_evaluator: StrategicEvaluator
    PROPERTY tactical_executor: TacticalExecutor
    PROPERTY state_manager: StateManager // Assumed to provide consistent game state access

    CONSTRUCTOR(strategic_evaluator, tactical_executor, state_manager):
        self.strategic_evaluator = strategic_evaluator
        self.tactical_executor = tactical_executor
        self.state_manager = state_manager

    // TDD_ANCHOR: test_ai_manager_full_turn_execution
    METHOD process_unit_turn(unit_id):
        // 0. Get Consistent State & Unit Info
        current_game_state = self.state_manager.get_current_state_snapshot()
        unit = current_game_state.get_unit_by_id(unit_id)
        IF unit IS NULL OR unit.has_acted() OR unit.faction != Faction.ENEMY: // Or AI-controlled faction
            RETURN // Skip if unit doesn't need processing

        persona = unit.get_ai_persona() // Load persona config for the unit

        // log(f"Processing Turn for Unit: {unit.name} (ID: {unit.id}), Persona: {persona.name}")

        // 1. Phase 1: Strategic Goal Selection
        selected_goal = self.strategic_evaluator.select_goal(unit, current_game_state, persona)
        IF selected_goal IS NULL:
            // log("Strategic Evaluator returned no goal. Ending turn.")
            // Optionally execute a default Wait action here
            default_action = Action_Wait(target_position=unit.position)
            default_action.execute(unit, current_game_state) // Execute on the *actual* game state via StateManager
            self.state_manager.commit_action(default_action)
            RETURN

        // log(f"Strategic Goal Selected: {selected_goal.goal_type} - {selected_goal.parameters}")

        // 2. Phase 2: Tactical Action Execution
        selected_action = self.tactical_executor.select_action(unit, selected_goal, current_game_state, persona)
        IF selected_action IS NULL:
            // log("Tactical Executor returned no action. Ending turn (Wait).")
            // Execute a default Wait action
            default_action = Action_Wait(target_position=unit.position)
            default_action.execute(unit, current_game_state)
            self.state_manager.commit_action(default_action)
            RETURN

        // log(f"Tactical Action Selected: {selected_action.type} - {selected_action.parameters}")

        // 3. Execute Action
        // The action execution should modify the *actual* game state,
        // potentially via the StateManager or directly if careful.
        // TDD_ANCHOR: test_ai_manager_commits_action_to_state
        self.state_manager.commit_action(unit, selected_action) // Preferred way
        // OR selected_action.execute(unit, self.state_manager.get_writable_state())

        // log(f"Unit {unit.id} executed action.")

```

---