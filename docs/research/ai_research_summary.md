# AI Research Summary

This document consolidates AI research notes from several original files to provide a comprehensive reference on the AI system design, testing, and debugging for the Fantasy Tactics Game project.

## Table of Contents
1. [AI Design Overview](#ai-design-overview)
2. [AI vs AI Testing Framework](#ai-vs-ai-testing-framework)
3. [Execution Failure Analysis](#execution-failure-analysis)

---

<a id="ai-design-overview"></a>
# 1. AI Design Overview
*(From AI_LOGIC_RESEARCH.MD)*

## Introduction

This section describes the simplified design for the Artificial Intelligence (AI) system responsible for controlling non-player characters (NPCs) in our Fire Emblem-style turn-based tactical RPG (SRPG). The primary goal is to create a functional and predictable AI capable of executing basic tactics according to unit roles and objectives. This system must operate within the game's rules and utilize unit capabilities effectively. A key use case for this AI is automated testing, where the AI will control units on both sides of a conflict to test game mechanics and balance.

## Goals

The AI system aims to achieve the following:

- **Functional**: AI units should perform valid actions according to game rules.
- **Believable**: AI actions should generally make tactical sense based on their role and the immediate situation. Avoid obviously illogical moves.
- **Role-Based**: Different unit types/roles (e.g., attacker, healer) should exhibit distinct, simple behaviors.
- **Deterministic** (Optional but helpful for testing): Given the same starting state, the AI should ideally make the same decisions, facilitating reproducible tests. (May require careful handling of tie-breaking).
- **Performant**: AI decision-making must be computationally efficient to allow for reasonably fast turn resolution, especially in AI vs AI scenarios with potentially many units.
- **Testable**: The AI's logic should be clear enough to debug and verify, supporting its use in automated testing.

## Core Architecture: Utility-Based AI

We will utilize a Utility-Based AI architecture. This approach involves:

- **Identify Potential Actions**: Enumerate possible actions (Move+Attack, Move+Skill, Move+Item, Move+Wait).
- **Score Actions**: Evaluate each action using a set of weighted "Considerations" (scorers) that measure the desirability of outcomes (e.g., dealing damage, staying safe, healing).
- **Select Best Action**: Choose the action with the highest score.

Why Utility AI (Simplified)?

- **Flexibility**: Still allows tuning behavior by adjusting scorer weights for different roles.
- **Structured Decision Making**: Provides a clear framework for comparing different types of actions (attacking vs. healing vs. repositioning).
- **Sufficient for Core Tactics**: Can model essential behaviors like attacking, healing, and basic positioning.

## Decision-Making Process (Per AI Unit Turn)

### Step 1: Information Gathering

- Identify the unit's current state (HP, status, position, equipment, skills, items).
- Scan the map for:
  - Enemy unit positions, HP, basic threat level.
  - Ally unit positions, HP.
  - Terrain features.
  - Objective locations/status (if applicable, e.g., 'Defeat Commander X').

### Step 2: Determine Role & Objective

- Identify the unit's AI Persona/Role (see Section 5).
- Identify the Scenario Objective (e.g., Rout Enemy, Defeat Specific Unit). This provides high-level context.

### Step 3: Generate Potential Actions

- Enumerate valid possibilities:
  - Move + Attack: All reachable squares + attackable targets.
  - Move + Use Skill: All reachable squares + valid skill targets (healing, simple buffs/debuffs).
  - Move + Use Item: All reachable squares + valid item uses (primarily self-healing).
  - Move + Wait: All reachable squares.

### Step 4: Score Potential Actions (Utility Calculation)

- For each generated (Move Target Square, Action Type, Action Target) tuple, calculate a score based on weighted Considerations (Scorers).
- Sum weighted scores for the final Utility Score.
- Simplified Considerations / Scorers:
  - **Offensive**:
    - DamageDealt: Estimated damage output (factor in basic combat rules).
    - KillPotential: Bonus if the attack is likely to defeat the target.
    - TargetPriority: Simple priority (e.g., lowest HP enemy, objective target > other enemies).
  - **Defensive**:
    - SelfPreservation: Score based on remaining HP after the action (including counterattack). Higher is better. Avoids actions leading to immediate death if possible.
    - DamageTaken (Counter): Negative score based on expected counterattack damage.
  - **Positional**:
    - TerrainBonus: Small bonus for ending on favorable terrain (e.g., Fort, Forest).
    - ObjectiveProximity: Score based on distance to the primary map objective location or target unit.
  - **Healing/Support**:
    - HealAllyAmount: Score based on HP restored to an allied unit.
    - HealAllyPriority: Bonus for healing lower HP allies.
    - SelfHealAmount: Score for using a self-healing item (e.g., Vulnerary). Crucial for retreat logic.
  - **Resource Management**:
    - ItemUsedCost: Small negative score for consuming a limited-use item.
- Weighting: Weights are primarily determined by the Unit Role/Persona. No dynamic difficulty scaling.

### Step 5: Select and Execute Action

- Identify the action with the highest total Utility Score.
- Tie-Breaking: Use a simple, deterministic tie-breaker (e.g., Attack > Skill > Item > Wait; prioritize targets with lower ID if scores are identical) to ensure reproducibility for testing.
- Execute the chosen action.

## AI Personas / Roles (Simplified)

Define a small set of core roles with distinct default weights:

- **Aggressor**: Prioritizes dealing damage. High weights for DamageDealt, KillPotential. Moderate weight for SelfPreservation. Will engage most targets.
- **Defender/Guardian**: Prioritizes survival and holding ground, often near objectives or other allies. High weights for SelfPreservation, TerrainBonus. Lower weight for initiating attacks unless threatened or a very high-value opportunity exists. Boss units can often use this persona.
- **Healer**: Prioritizes healing allies. High weights for HealAllyAmount, HealAllyPriority. Will try to stay out of direct danger, weighting SelfPreservation highly.
- **ObjectiveFocused**: Prioritizes moving towards objectives. High weight for ObjectiveProximity. Will only engage enemies if they directly block the path or present an extremely easy kill opportunity.

## Performance Considerations

- **Action Space Pruning**: Limit evaluation to squares reasonably close to enemies, allies, or objectives.
- **Caching**: Cache pathfinding or range checks within a single unit's turn analysis.
- **Optimization**: Ensure scoring functions (especially combat previews) are efficient.
- **Avoid Lookahead**: No multi-turn prediction. Decisions are based on the current turn only.

## Tools & Debugging

- **AI Visualizer**: In-game overlay showing movement/attack ranges, potential targets, and perhaps the chosen action's target/destination.
- **AI Logger**:
  - Default: Minimal logging (e.g., Unit X moving to (Y,Z) and attacking Unit A). Use abbreviations (e.g., U:5 MV(10,12) ATK U:12).
  - Detailed Mode (via command-line flag/console command): Output detailed logs for debugging specific scenarios. Show top N considered actions, their scores, and the breakdown by scorer (e.g., ACTION: MV(10,12) ATK U:12 | Score: 85 | DmgDealt:50(w:1.0) KillPot:20(w:0.5) SelfPrsv:15(w:1.0) ...). Terse format with abbreviations is still preferred even in detail mode to manage volume.
- **Weight Editor**: Tool to view and modify scorer weights for each AI persona.
- **Scenario Tester**: Ability to set up specific map states to test AI behavior reproducibly.

## Specific Behaviors & Edge Cases

- **Weapon Triangle/Effectiveness**: Must be included in DamageDealt calculations.
- **Skills/Items**: AI needs basic logic to use available skills (healing, simple attacks) and items (primarily self-healing). Score actions involving limited resources appropriately (ItemUsedCost).
- **Status Effects**: Keep simple. AI might prioritize healing negative statuses if a Healer, but otherwise may largely ignore them unless they prevent action.
- **Retreat Logic (Simplified)**:
  - A unit will consider using a self-healing item (e.g., Vulnerary) if its HP is below a certain threshold (e.g., < 40%-50%).
  - The SelfHealAmount scorer will give this action a high utility value in that situation.
  - If the unit does not possess a self-healing item, it will not attempt to retreat based solely on low HP. It will follow its standard role logic (e.g., an Aggressor might fight to the death, a Defender might still prioritize safe positioning if possible).
- **Target Selection**: Primarily driven by TargetPriority (low HP, objective target) and KillPotential.

---

<a id="ai-vs-ai-testing-framework"></a>
# 2. AI vs AI Testing Framework
*(From AI_VS_AI_TESTING.md)*

This section describes the AI vs AI testing framework for the Fantasy Tactics Game, designed to facilitate automated testing and observation of AI behavior and interactions between AI-controlled units using the v2 Goal-Oriented AI system.

## Overview

The AI vs AI testing framework allows developers to:

1. Create scenarios where both factions are controlled by AI using different personas.
2. Observe and test different AI personas against each other in a dynamic environment.
3. Verify that AI units make appropriate strategic (Goal) and tactical (Action) decisions based on their personas and the game state.
4. Analyze emergent AI behavior in complex tactical situations over multiple turns.
5. Provide a basis for regression testing of the AI system.
6. **Confirmation:** Latest tests using this framework confirm improved behavior for `MoveToSafetyGoal` and `SeizeTileGoal`, particularly when targets are distant, significantly reducing scenarios where the AI previously failed to find a valid action.
7. **Debugging Success:** This framework was crucial in identifying and verifying fixes for the core AI action execution pipeline (Goal Selection -> Tactical Execution -> Action Handling -> System Execution -> Game State Update), resolving issues related to system initialization, phase validation, path validation, action data structures, and tactical reachability checks, as confirmed by `test_ai_vs_ai_fixed.py`.

## Components

### 1. AI vs AI Test Scenarios

Located in `data/scenarios/`, these YAML files define test scenarios specifically designed for AI vs AI testing.

* **Example:** `data/scenarios/ai_vs_ai_basic_test.yaml` (or similar) - A scenario designed to test fundamental interactions between different personas.

Each scenario typically includes:
* Map layout definition (`layout_path`).
* Unit placements (`units`) for both factions, specifying `team`, `class_id`, starting `position`, `level`, `items`, and crucially, the `ai_persona`.
* Optional event triggers (`events`).
* Game configuration (`config`), potentially including turn limits or specific objectives.

### 2. Test Execution Scripts

Located in the project root:

* **`run_ai_vs_ai_test.py`:** The primary script for running an AI vs AI simulation. It loads a specified scenario, sets both teams to AI control, and runs the game simulation, outputting detailed logs. This is ideal for observation and manual analysis.
* **`test_ai_vs_ai_fixed.py` (or similar pytest files):** Automated test scripts using `pytest`. These load specific scenarios, run simulations, and include assertions to programmatically verify expected outcomes or behaviors (e.g., checking if a certain goal was prioritized, if a unit survived, etc.). These are used for automated regression testing.

### 3. Logging System

* **`src/gameplay_systems/ai/ai_logger.py` (`AILogger`):** Integrated into the AI Manager, this logs detailed decision-making information during simulations.
* **Log Files:**
  * `ai_behavior.log`: Captures detailed turn-by-turn decisions for *individual* AI units, including goal evaluation scores, chosen goals, action generation, action evaluation scores, and chosen actions. Essential for deep dives into a specific unit's logic.
  * `ai_vs_ai_test.log`: Captures higher-level events and state changes during an AI vs AI simulation run via `run_ai_vs_ai_test.py`, such as turn progression, unit actions taken, combat results, and game end conditions. Useful for understanding the overall flow of the simulation.

## AI Personas (Examples)

The framework allows testing various AI personas defined in `data/ai_personas.yaml`:

1. **Aggressor**: Prioritizes attacking enemy units (High weight for `AttackUnitGoal`).
2. **Defender**: Prioritizes holding strategic positions (High weight for `SecurePositionGoal`).
3. **Support**: Prioritizes healing and assisting allies (High weight for `HealUnitGoal`).
4. **ObjectiveRusher**: Prioritizes advancing toward map objectives (High weight for `AdvanceToObjectiveGoal` or `SeizeTileGoal`).

## Running AI vs AI Tests

### Method 1: Observation & Manual Analysis

Use this method to watch a simulation unfold and analyze the detailed logs afterward.

1. **Run the Simulation Script:**
   ```bash
   python run_ai_vs_ai_test.py --scenario data/scenarios/your_ai_test_scenario.yaml [--max_turns 50] [--ascii-display]
   ```
   * Replace `your_ai_test_scenario.yaml` with the desired scenario file.
   * `--max_turns` (optional): Limits the simulation duration.
   * `--ascii-display` (optional): Shows a basic text-based representation of the map state in the console during the simulation.

2. **Observe:** Watch the console output (especially if using `--ascii-display`) or wait for the simulation to complete.

3. **Analyze Logs:** Examine `ai_behavior.log` and `ai_vs_ai_test.log` (see "Interpreting Logs" below).

### Method 2: Automated Regression Testing

Use this method to run predefined tests with automated checks.

1. **Run Pytest:**
   ```bash
   pytest test_ai_vs_ai_fixed.py -v
   ```
   * This will execute all test functions within the specified file.
   * `-v` provides verbose output, showing which tests passed or failed.

2. **Review Failures:** If any tests fail, examine the pytest output and the relevant logs (`ai_behavior.log`, `ai_vs_ai_test.log`) to diagnose the issue.

## Interpreting AI Behavior Logs

* **`ai_vs_ai_test.log`:**
  * **Purpose:** Provides a high-level overview of the simulation flow.
  * **Key Information:** Turn start/end markers, unit actions executed (Move, Attack, Wait, Use Skill/Item), combat results (damage dealt, unit defeated), game end conditions.
  * **Use Case:** Understanding the sequence of events, identifying major outcomes, tracking overall simulation progress.

* **`ai_behavior.log`:**
  * **Purpose:** Provides deep insight into the AI's decision-making process for each unit's turn.
  * **Key Information:**
    * `Evaluating Goals for Unit X`: Lists all valid goals considered.
    * `Goal Y Relevance Score: Z`: Shows the calculated score for each goal based on persona and game state.
    * `Selected Goal: Y`: Indicates the chosen strategic goal.
    * `Evaluating Actions for Goal Y`: Lists potential tactical actions generated for the chosen goal.
    * `Action Z Utility Score: W`: Shows the calculated score for each action.
    * `Selected Action Sequence: Z`: Indicates the chosen action(s) to execute.
  * **Use Case:** Debugging unexpected behavior, verifying goal/action scoring logic, tuning AI persona weights, understanding *why* an AI made a specific choice.

## Creating New AI Test Scenarios

1. **Define Objectives:** What specific AI behavior or interaction do you want to test? (e.g., How does a Defender react to an Aggressor? Does a Support unit correctly prioritize healing?)
2. **Create YAML File:** Create a new `.yaml` file in `data/scenarios/` (e.g., `data/scenarios/ai_test_flanking.yaml`).
3. **Design Map Layout:** Reference or create a map layout (`layout_path`) that facilitates the desired interaction. Consider terrain placement (chokepoints, defensive tiles, open ground).
4. **Place Units:**
   * Define units for both `player` and `enemy` teams.
   * Assign appropriate `class_id`.
   * Set starting `position`.
   * Assign the desired `ai_persona` to each AI unit.
   * Equip relevant `items`.
5. **Configure Simulation:** Set `config` options like `turn_limit` if needed.
6. **(Optional) Add Events:** Define simple `events` if necessary for the scenario setup.
7. **Document:** Add comments within the YAML file explaining the scenario's purpose and expected outcome.
8. **Test:** Run the scenario using `run_ai_vs_ai_test.py` for observation and consider creating a corresponding `pytest` function in `test_ai_vs_ai_fixed.py` for automated validation.

## Future Enhancements

* Automated analysis tools for logs (e.g., scripts to calculate goal frequency per persona).
* More sophisticated scenario definition options (e.g., complex win conditions).
* Integration with visualization tools beyond basic ASCII display.

---

<a id="execution-failure-analysis"></a>
# 3. Execution Failure Analysis
*(From AI_EXECUTION_FAILURE_ANALYSIS.MD)*

This section addresses a critical issue identified within the Fantasy Tactics Game project, specifically concerning the failure of AI-determined actions to correctly modify the game state during AI vs. AI simulations, as observed in test_ai_vs_ai.py.

## Introduction

While the AI decision-making components (AISystem, TacticalExecutor) appear to function correctly, generating appropriate action objects (e.g., MoveAction, AttackAction), these intended actions are not reflected in the simulation managed by the GameStateManager. This document provides a detailed analysis of the hypothesized action execution pipeline, identifies potential points of failure, and proposes a structured debugging approach with specific code-level recommendations to resolve the discrepancy.

## Understanding the Expected AI Action Flow

Based on the project context, the intended sequence for an AI unit's action involves several distinct stages, transitioning from decision to execution:

1. **Action Determination**: The AISystem, utilizing the TacticalExecutor, evaluates the game state from the perspective of a specific AI-controlled unit. It analyzes possible moves, attacks, or other abilities to determine the optimal action.

2. **Action Object Creation**: Upon selecting an action, the AI system instantiates a corresponding action object (e.g., MoveAction(unit_id='unit_A', target_pos=(5, 6)), AttackAction(unit_id='unit_A', target_id='unit_B')). This object encapsulates the intent and necessary parameters for the action.

3. **Action Communication**: The generated action object is passed from the AI system to the central GameEngine. This handoff is a critical interface point.

4. **Engine Reception & Processing**: The GameEngine, managing the main game loop and turn progression, receives the action object during the designated AI turn processing phase.

5. **Action Dispatch/Translation**: The GameEngine interprets the received action. It might directly instruct the relevant gameplay system (e.g., MovementSystem, CombatSystem) or translate the action into an internal command or event that these systems subscribe to. An intermediary ActionSystem could potentially handle this dispatch logic.

6. **System Execution & State Modification**: The targeted gameplay system (e.g., MovementSystem for MoveAction) validates the action based on game rules and the current state. If valid, it executes the action by invoking methods on the GameStateManager to update the relevant data (e.g., unit position, target HP).

7. **Simulation Reflection**: The changes made to the GameStateManager are now part of the canonical game state, and subsequent game logic, rendering, and AI decisions should reflect this updated state.

The current problem indicates a breakdown occurring between Step 3 and Step 6, where the action decided by the AI fails to trigger the corresponding state update.

## Analysis of Potential Failure Points

The discrepancy between the AI's intended action and the resulting game state points to a failure in the communication or execution pathway. Several key areas are suspect:

1. **AI to Engine Handoff (Step 3 -> 4)**: Is the action object generated by the AISystem actually being returned and successfully received by the GameEngine? Potential issues include the AI function returning None unexpectedly, the GameEngine not calling the AI function correctly, or the return value being lost or ignored.

2. **Engine Action Processing (Step 4 -> 5)**: Assuming the GameEngine receives the action object, does it correctly recognize and process it? The engine might lack the logic to handle the specific type of action object received, or the turn management logic might prematurely end the turn or skip the action processing phase for AI units.

3. **Action Dispatching (Step 5)**: If the GameEngine is supposed to dispatch the action to a specific system (e.g., MovementSystem, CombatSystem, or via an ActionSystem), is this dispatch mechanism working? The engine might not have references to the necessary systems, the dispatch logic might incorrectly map action types to systems, or an ActionSystem, if used, might not be correctly processing its queue.

4. **System Execution Logic (Step 6)**: Is the responsible gameplay system (e.g., MovementSystem) correctly receiving the action/command and executing it? The system might receive the action but fail validation checks silently (e.g., move target is invalid, attack target out of range), thus aborting the execution without error. Alternatively, the system might execute the logic but fail to call the correct GameStateManager update methods.

5. **GameStateManager Interaction (Step 6)**: Are the gameplay systems using the correct methods and parameters when attempting to update the GameStateManager? Mismatched function signatures, incorrect unit IDs, or issues within the GameStateManager's update methods themselves could prevent state changes.

6. **Test Environment Setup (test_ai_vs_ai.py)**: Is the simulation environment correctly configured? It's possible that essential components (like the MovementSystem or CombatSystem) are not instantiated or wired into the GameEngine within the test context, or the main loop/turn update mechanism isn't being invoked properly in the test script.

## Debugging Strategy

To systematically isolate the failure, implement verbose logging and potentially use a debugger, focusing on the transitions between components. The following checkpoints should be verified:

1. **AI Action Generation**: Confirm a non-None action object is created and returned by the AI for the active unit.

2. **Engine Receives Action**: Confirm the GameEngine receives the action object returned by the AISystem.

3. **Action Queuing/Dispatch Preparation**: Confirm the received action is added to a queue or prepared for immediate dispatch.

4. **Action Dispatch Attempt**: Confirm the code attempts to identify and call the correct handler/system for the action type.

5. **System Receives Action/Command**: Confirm the relevant gameplay system's execution method (e.g., execute, process) is called with the action.

6. **Action Validation (Within System)**: Check if the action passes internal validation rules (e.g., valid path, target in range).

7. **State Manager Update Call**: Confirm the system calls the appropriate GameStateManager method after successful validation/execution.

8. **State Manager State Change Confirmation**: Confirm the GameStateManager's internal data structures are actually modified.

9. **Test Environment Integrity**: Verify all required systems are instantiated and linked in the test setup. Ensure the game loop/turn update runs.

## Proposed Code Modifications

Based on the likely failure points, here are some conceptual code adjustments:

### Ensure AI Returns Action (in AISystem or TacticalExecutor)

```python
# Inside the AI action selection method (e.g., AISystem.get_action_for_unit)
def get_action_for_unit(self, unit_id, game_state_view):
    #... existing AI logic to determine best_action...
    best_action = self.tactical_executor.choose_action(unit_id, game_state_view) # Example call

    if best_action:
        log.debug(f"AI returning action for unit {unit_id}: {best_action}")
        return best_action
    else:
        # Explicitly handle the case where no action is found (e.g., WaitAction or log warning)
        log.warning(f"AI for unit {unit_id} could not determine a valid action. Returning None or WaitAction.")
        # return WaitAction(unit_id) # Consider adding a WaitAction if applicable
        return None
```

### Ensure Engine Processes Action (in GameEngine)

```python
# Inside GameEngine's AI turn processing logic
def _process_ai_turn(self, unit_id):
    log.debug(f"Processing AI turn for unit {unit_id}")
    # Ensure ai_system and game_state_manager are correctly referenced
    action = self.ai_system.get_action_for_unit(unit_id, self.game_state_manager.get_state_view())

    if action:
        log.info(f"Engine received action from AI for unit {unit_id}: {action}")
        # Ensure the action is actually processed or queued
        # Option A: Direct Dispatch (if simple)
        self.dispatch_action(action)
        # Option B: Queueing (if using an action queue)
        # self.action_queue.append(action) # Ensure queue is processed later
    else:
        log.warning(f"AI for unit {unit_id} returned no action. Ending turn or performing default action.")
    # Ensure turn progression logic happens AFTER action processing/queuing attempt
    # self.end_unit_turn(unit_id)
```

### Implement Robust Action Dispatching (in GameEngine or ActionSystem)

```python
# Conceptual dispatch logic (could be in GameEngine or a dedicated ActionSystem)
class GameEngine: # Or ActionSystem
    def __init__(self, game_state_manager, movement_system, combat_system,...):
        self.game_state_manager = game_state_manager
        # Ensure systems are passed in or retrieved correctly
        self.movement_system = movement_system
        self.combat_system = combat_system
        #... other systems

        # Option: Handler registry (more scalable)
        self.action_handlers = {
            MoveAction: self.movement_system,
            AttackAction: self.combat_system,
            # HealAction: self.healing_system, # Example
            #... register other handlers and ensure Action classes are imported
        }
        log.info("Action handlers initialized.")


    def dispatch_action(self, action):
        log.debug(f"Attempting to dispatch action: {action}")
        handler_system = self.action_handlers.get(type(action))

        if handler_system:
            try:
                # Assuming systems have a common method like 'execute' or 'process'
                log.debug(f"Dispatching action {type(action).__name__} to {handler_system.__class__.__name__}")
                handler_system.execute(action) # Pass the action object
            except AttributeError:
                log.error(f"Handler {handler_system.__class__.__name__} does not have an 'execute' method.")
            except Exception as e:
                log.exception(f"Error executing action {action} in handler {handler_system.__class__.__name__}: {e}")
        else:
            log.error(f"No handler registered for action type: {type(action).__name__}. Action ignored.")
```

### Ensure System Execution and State Update (in MovementSystem, CombatSystem, etc.)

```python
# Example in MovementSystem
class MovementSystem:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager # Ensure GSM is accessible

    def execute(self, action: MoveAction): # Ensure type hinting if possible
        log.debug(f"MovementSystem executing action: {action}")
        # Perform validation FIRST
        if self._is_valid_move(action.unit_id, action.target_pos):
            log.info(f"Executing valid move for unit {action.unit_id} to {action.target_pos}")
            # Call the correct GameStateManager method
            try:
                self.game_state_manager.update_unit_position(action.unit_id, action.target_pos)
                log.debug(f"Successfully updated position for unit {action.unit_id} via GameStateManager.")
            except Exception as e:
                 log.exception(f"Failed to update position via GameStateManager for action {action}: {e}")
        else:
            # Log clearly if validation fails
            log.warning(f"Invalid move attempted for unit {action.unit_id} to {action.target_pos}. Action aborted.")

    def _is_valid_move(self, unit_id, target_pos):
        #... implement actual validation logic using self.game_state_manager...
        # Example: Check pathfinding, terrain, occupation
        log.debug(f"Validating move for unit {unit_id} to {target_pos}...")
        # is_valid =...
        # log.debug(f"Move validation result: {is_valid}")
        # return is_valid
        return True # Placeholder - replace with real validation
```

### Verify Test Environment (test_ai_vs_ai.py)

```python
# Inside test_ai_vs_ai.py setup or test function
def test_ai_simulation():
    # Ensure all components are instantiated correctly
    gsm = GameStateManager(...)
    movement_system = MovementSystem(gsm)
    combat_system = CombatSystem(gsm)
    #... other systems

    # Ensure AISystem has access to necessary info/executors
    ai_system = AISystem(TacticalExecutor(...))

    # Ensure GameEngine gets references to ALL required components
    game_engine = GameEngine(
        game_state_manager=gsm,
        ai_system=ai_system,
        movement_system=movement_system,
        combat_system=combat_system,
        #... potentially action_system, other gameplay systems
    )
    log.info("Test environment components initialized and linked.")

    # Add initial units, setup board state via gsm

    # Simulate turns - ensure the engine's update/turn processing method is called
    for _ in range(MAX_TURNS): # Example loop
        log.debug(f"--- Starting Turn {_ + 1} ---")
        active_unit_id = game_engine.get_next_active_unit()
        if not active_unit_id:
            log.info("No active unit found, ending simulation.")
            break

        # CRITICAL: Ensure the engine processes the turn for the active unit
        game_engine.process_turn_for_unit(active_unit_id) # Or similar method call

        # Add assertions here to check if expected state changes occurred
        # e.g., assert gsm.get_unit_position(some_unit_id) == expected_pos_after_move
```

## Resolution Status

The AI action execution failure was successfully resolved using the above debugging approach. The primary issues identified were:

1. System initialization issues in the test environment
2. Phase validation errors preventing action processing
3. Path validation failures in the movement system
4. Inconsistent action data structures between AI and execution systems
5. Tactical reachability check issues when dealing with distant targets

The fixes were verified using the AI vs AI testing framework, which now shows correct behavior for all core goals, including `MoveToSafetyGoal` and `SeizeTileGoal`, particularly when targets are distant. 