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
    *   **Goal Logic:** Each goal includes methods for:
        *   `is_valid(unit, state)`: Checks if the goal is applicable.
        *   `calculate_relevance(unit, state, persona)`: Scores the goal's importance.
        *   `generate_actions(unit, state)`: Creates potential action sequences.
        *   `evaluate_action(action, unit, state, persona)`: Scores a specific action for this goal.
        *   Evaluating actions specifically within the goal's context.
*   **`strategic_evaluator.py` (`StrategicEvaluator`):**
    *   **Responsibility:** Implements Phase 1. It enumerates valid Goals from the Goal Library for the current unit, scores their relevance using weighted considerations (influenced by the AI Persona), and selects the highest-scoring Goal.
    *   **Dependencies:** `goals.py`, `utility_scorer.py`, AI Persona configurations.
*   **`tactical_executor.py` (`TacticalExecutor`):**
    *   **Responsibility:** Implements Phase 2. Given the selected Goal, it generates relevant action sequences (move, attack, skill, item use), scores them using goal-specific utility considerations (factoring in Persona weights via `UtilityScorer`), selects the optimal sequence, and translates it into game commands.
    *   **Dependencies:** `goals.py`, `utility_scorer.py`, AI Persona configurations, various game systems (Movement, Combat, Skill, Item, etc.).
*   **`utility_scorer.py` (`UtilityScorer` / Scoring Functions):**
    *   **Responsibility:** Provides a modular library of scoring functions (Considerations) used by both the `StrategicEvaluator` (for Goals) and the `TacticalExecutor` (for Actions). These functions evaluate factors like damage potential, risk, healing, positioning, etc. Crucially, the *weights* applied to these considerations are influenced by the unit's assigned **AI Persona**, allowing for varied behavior.
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
    *   Actions relevant *only* to the selected Goal are generated (using logic within the Goal definition and game systems).
    *   These actions are scored using goal-specific utility considerations (from `utility_scorer.py` and the Goal definition).
    *   The highest-scoring action sequence is chosen.
4.  **Execution:** The `AIManager` translates the chosen action sequence into commands for the game engine.

This two-phase approach aims to create more strategically sound and contextually appropriate AI behavior compared to the previous system, while also offering potential performance benefits by pruning the action space early.

## 4. Testing and Scenarios

The AI system's behavior is tested using specific game scenarios defined in YAML files. These scenarios set up controlled situations to verify goal selection and action execution under different conditions.

*   **`data/scenarios/ai_test_scenario_01.yaml`:** Tests basic combat goal prioritization and target selection.
*   **`data/scenarios/ai_test_scenario_02.yaml`:** Tests support goals like healing (`HealUnitGoal`) and defensive positioning (`MoveToSafetyGoal`).

These scenarios are crucial for iterating on AI logic, tuning Persona weights, and ensuring robust behavior.