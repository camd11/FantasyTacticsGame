# AI System Architecture: Two-Phase Goal-Oriented Utility AI (v2)

This directory contains the components for the **Two-Phase Goal-Oriented Utility AI**, which replaces the previous archetype-based system. This architecture separates AI decision-making into distinct strategic and tactical phases to improve coherence, context awareness, and performance.

## 1. Core Concept: Two Phases

The AI operates in two main phases for each unit's turn:

1.  **Phase 1: Strategic Goal Selection:** The AI evaluates high-level objectives (Goals) based on the game state, unit capabilities, and its assigned Persona. It selects the single most relevant Goal to pursue for the turn.
2.  **Phase 2: Tactical Action Execution:** Based on the chosen Goal, the AI identifies, evaluates, and selects the specific sequence of actions (e.g., move, attack, use skill/item) that best achieves that Goal.

## 2. Key Components

*   **`ai_manager.py` (`AIManager`):**
    *   **Responsibility:** Orchestrates the overall two-phase decision-making process for an AI unit's turn. It coordinates calls to the Strategic Evaluator and Tactical Executor. Likely manages the game state snapshot needed for consistent decision-making within a turn.
*   **`goals.py` (Goal Library & Definitions):**
    *   **Responsibility:** Defines the available strategic Goals. Each goal definition includes logic for determining validity, scoring relevance, generating actions, and evaluating actions within its context.
    *   **Implemented Goals (Examples):**
        *   `HealUnitGoal`: Focuses on restoring HP to allied units.
        *   `MoveToSafetyGoal`: Prioritizes moving the unit away from immediate threats.
        *   `SeizeTileGoal`: Aims to capture a specific objective tile (e.g., throne, gate).
        *   `AttackUnitGoal`: Focuses on attacking enemy units.
        *   `AdvanceToObjectiveGoal`: Moves towards a designated map objective (Note: Currently uses placeholder logic; full implementation pending).
        *   `SecurePositionGoal`: Holds a defensive position (Note: Currently uses placeholder logic; full implementation pending).
    *   **Goal Logic:** Each goal includes methods for:
        *   `is_valid(unit, state)`: Checks if the goal is applicable.
        *   `calculate_relevance(unit, state, persona)`: Scores the goal's importance.
        *   `generate_actions(unit, state)`: Creates potential action sequences.
        *   `evaluate_action(action, unit, state, persona)`: Scores a specific action for this goal.
*   **`strategic_evaluator.py` (`StrategicEvaluator`):**
    *   **Responsibility:** Implements Phase 1. It enumerates valid Goals from the Goal Library for the current unit, scores their relevance using weighted considerations (influenced by the AI Persona), and selects the highest-scoring Goal.
    *   **Dependencies:** `goals.py`, `utility_scorer.py`, AI Persona configurations.
*   **`tactical_executor.py` (`TacticalExecutor`):**
    *   **Responsibility:** Implements Phase 2. Given the selected Goal, it generates relevant action sequences (move, attack, skill, item use). **Crucially, if no direct action (like attack or skill use) is immediately feasible but the goal involves a target (e.g., ATTACK_UNIT, ADVANCE_TO_OBJECTIVE), the `TacticalExecutor` will generate a 'move-towards-target' action sequence to close the distance.** This now includes improved handling for `MoveToSafetyGoal` and `SeizeTileGoal`, ensuring the AI moves towards the objective even if it's not reachable within a single turn. Actions are scored using goal-specific utility considerations (factoring in Persona weights via `UtilityScorer`), the optimal sequence is selected, and translated into game commands.
    *   **Dependencies:** `goals.py`, `utility_scorer.py`, AI Persona configurations, various game systems (Movement, Combat, Skill, Item, etc.).
*   **`utility_scorer.py` (`UtilityScorer` / Scoring Functions):**
    *   **Responsibility:** Provides a modular library of scoring functions (Considerations) used by both the `StrategicEvaluator` (for Goals) and the `TacticalExecutor` (for Actions). These functions evaluate factors like damage potential, risk, healing, positioning, etc. Crucially, the *weights* applied to these considerations are influenced by the unit's assigned **AI Persona**, allowing for varied behavior.
*   **`ai_logger.py` (`AILogger`):**
    *   **Responsibility:** Provides a dedicated logging system for detailed insights into the AI's decision-making process. Logs strategic goal selection (including scores) and tactical action evaluation (including considered actions and their scores). This is invaluable for debugging and tuning AI behavior. Log output is typically directed to `ai_behavior.log`.
*   **AI Personas (Configuration):**
    *   **Responsibility:** Defined externally (likely in YAML or similar data files, managed perhaps by `AIProfileManager` or loaded directly). Personas define behavioral tendencies by assigning different weights to Goals and utility considerations for different unit types (e.g., Aggressor, Defender, Support).

*(Note: Some components from the previous system like `ai_profile_manager.py` might still be used for loading Persona configurations, while others like `ai_action_evaluator.py`, `ai_action_scoring.py`, and the specific `archetype_handlers/` are superseded by the new components.)*

## 3. Flow of Control (AI Unit Turn)

1.  **Initiation:** The `AIManager` (or equivalent orchestrator) starts the AI turn for a unit. A consistent snapshot of the game state is likely established.
2.  **Phase 1: Goal Selection (via `StrategicEvaluator`)**
    *   Valid Goals are identified from `goals.py`.
    *   Each Goal is scored based on the current state, unit capabilities, and Persona weights, using functions from `utility_scorer.py`.
    *   The highest-scoring Goal is selected.
3.  **Phase 2: Action Execution (via `TacticalExecutor`)**
    *   Actions relevant *only* to the selected Goal are generated (using logic within the Goal definition and game systems). This includes move-towards-target actions if direct actions aren't possible.
    *   These actions are scored using goal-specific utility considerations (from `utility_scorer.py` and the Goal definition).
    *   The highest-scoring action sequence is chosen.
4.  **Execution:** The `AIManager` translates the chosen action sequence into commands for the game engine.
5.  **Status:** The core execution pipeline (Goal Selection -> Tactical Execution -> Action Handling -> System Execution -> Game State Update) has been successfully debugged and is functional, as verified by AI vs AI testing (`test_ai_vs_ai_fixed.py`).

This two-phase approach aims to create more strategically sound and contextually appropriate AI behavior compared to the previous system, while also offering potential performance benefits by pruning the action space early.

## 4. Testing and Observation

### 4.1 Scenario-Based Testing
The AI system's core logic (goal selection, action evaluation) is tested using specific game scenarios defined in YAML files (e.g., `data/scenarios/ai_test_*.yaml`). These scenarios set up controlled situations to verify behavior under specific conditions.

### 4.2 AI vs AI Testing Framework
A dedicated framework (`run_ai_vs_ai_test.py`, `test_ai_vs_ai_fixed.py`) allows for running full simulations where AI controls units on opposing teams. This provides a dynamic environment to observe emergent behaviors and interactions between different AI personas or configurations over multiple turns.
*   **Purpose:** Useful for identifying high-level strategic flaws, balancing personas, and observing long-term goal pursuit.
*   **Output:** Generates detailed logs (`ai_vs_ai_test.log`) capturing the state and decisions turn-by-turn.
*   **Further Details:** See `AI_VS_AI_TESTING.md` for instructions on running tests, interpreting logs, and creating new scenarios.

Both scenario-based tests and the AI vs AI framework, combined with the detailed logging system (`ai_logger.py`), are crucial for iterating on AI logic, tuning Persona weights, and ensuring robust and intended behavior.