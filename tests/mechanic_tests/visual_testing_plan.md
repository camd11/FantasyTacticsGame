# Game Mechanic Visual Testing Plan

## 1. Introduction

This document outlines the visual testing strategy for core game mechanics. Visual tests utilize the `VisualScenarioLogger` to generate human-readable text logs of mechanic execution flows. These logs serve several purposes:

*   **Debugging:** Provide a step-by-step trace to identify issues in complex interactions.
*   **Validation:** Offer a clear view of mechanic outcomes for comparison against expected behavior.
*   **Understanding:** Help developers and testers understand how mechanics function in practice.

## 2. General Approach

*   **Tool:** `src.utils.visual_logger.VisualScenarioLogger` is used within Pytest fixtures or test functions.
*   **Logging:** Key state changes, actions, events, and their parameters are logged using `visual_logger.log_action()`, `visual_logger.log_initial_state()`, etc.
*   **Output:** Logs are generated in the `logs/mechanic_tests/` directory, typically organized into subdirectories corresponding to the mechanic being tested (e.g., `logs/mechanic_tests/units/` for unit-related mechanics).
*   **Granularity:** Each specific mechanic test (or group of related tests within a file) should ideally generate its own distinct log file (e.g., `level_up_mechanics.txt`, `promotion_mechanics.txt`).

## 3. Mechanic-Specific Visual Test Plans

### 3.1 Movement Mechanics

*   **Test File:** `tests/mechanic_tests/test_movement_mechanics.py`
*   **Log File(s):** `logs/mechanic_tests/movement/move_*.txt`, `terrain_cost_*.txt`, etc.
*   **Key Visual Log Points:**
    *   Initial unit position.
    *   Movement action trigger (unit, target coordinates).
    *   Pathfinding results (if applicable/logged, e.g., calculated path).
    *   Terrain type and movement cost encountered during movement.
    *   Final unit position after movement.
    *   Blocked movement attempts and reason.
*   **Verification Goal:** Visually trace unit movement paths, confirm terrain costs are applied correctly, and verify pathfinding logic produces expected results.

### 3.2 Combat Mechanics

*   **Test File:** `tests/mechanic_tests/test_combat_mechanics.py`
*   **Log File(s):** `logs/mechanic_tests/combat/combat_*.txt`, `weapon_triangle_*.txt`, etc.
*   **Key Visual Log Points:**
    *   Combat initiation (attacker, defender).
    *   Pre-combat stats (HP, STR, DEF, SPD, SKL, weapon equipped, relevant skills).
    *   Attack sequence (weapon triangle effects, hit calculation, crit calculation, damage calculation).
    *   Damage dealt and resulting HP for the defender.
    *   Counter-attack sequence (if applicable), including calculations.
    *   Damage dealt and resulting HP for the initial attacker.
    *   Post-combat stats (final HP).
    *   Unit defeat event if HP drops to 0.
*   **Verification Goal:** Visually follow the entire combat sequence, verify damage, hit rate, and critical hit calculations, confirm weapon triangle and skill effects, and track HP changes and unit defeat.

### 3.3 AI Mechanics

*   **Test File:** `tests/mechanic_tests/test_ai_mechanics.py`
*   **Log File(s):** `logs/mechanic_tests/ai/ai_decision_*.txt`, `ai_targeting_*.txt`, etc.
*   **Key Visual Log Points:**
    *   AI unit's turn start.
    *   AI persona/goal assessment (e.g., Aggressor seeking target, Defender protecting area).
    *   Evaluation of potential actions (move, attack, wait, use item).
    *   Target selection process (enemy prioritization, objective focus).
    *   Chosen action and target.
    *   Execution of the chosen action (linking to movement/combat logs if possible).
*   **Verification Goal:** Visually understand the AI's decision-making process based on its persona, the game state, and available actions. Verify that the AI executes its chosen actions correctly.

### 3.4 Objective Mechanics

*   **Test File:** `tests/mechanic_tests/test_objective_mechanics.py`
*   **Log File(s):** `logs/mechanic_tests/objectives/capture_objective.txt`, `defend_objective.txt`, `control_tracking.txt`.
*   **Key Visual Log Points:**
    *   Initial state of objectives (location, current owner).
    *   Unit movement towards an objective.
    *   Objective capture event (capturing unit, objective ID, new owning faction).
    *   Objective defense attempts (attacking unit, defending unit on objective).
    *   Tracking of objective control over multiple turns (owner, turns held).
    *   Win condition checks related to objective control.
*   **Verification Goal:** Visually track the status of objectives throughout a scenario, confirm capture/defense mechanics, and verify win condition logic based on objective control.

### 3.5 Event Mechanics

*   **Test File:** `tests/mechanic_tests/test_event_mechanics.py`
*   **Log File(s):** `logs/mechanic_tests/events/weather_event_trigger.txt`, `healing_event_trigger.txt`, `village_event_trigger.txt`.
*   **Key Visual Log Points:**
    *   Event trigger condition met (e.g., turn number, unit position).
    *   Specific event type triggered (Weather, Village Visit, Healing Rain, Reinforcement).
    *   Detailed event parameters (e.g., Weather type, Village location, Item found).
    *   Effects on units (stat changes with before/after values, HP restored, item added to inventory).
    *   Event duration and countdown (for temporary effects like weather).
    *   Event resolution or expiry.
*   **Verification Goal:** Visually confirm that events trigger under the correct conditions, apply their intended effects accurately, and expire correctly.

### 3.6 Level Up Mechanics

*   **Test File:** `tests/mechanic_tests/test_level_up_mechanics.py`
*   **Log File(s):** `logs/mechanic_tests/units/level_up_mechanics.txt`.
*   **Key Visual Log Points:**
    *   Initial unit state (Level, EXP, HP, Base Stats).
    *   Experience gain event (source, amount gained, new EXP total).
    *   Level up trigger (EXP reaching >= 100).
    *   New level and EXP reset.
    *   Stat increase rolls based on growth rates.
    *   Specific stats increased, showing before and after values.
    *   Final unit state after level up.
*   **Verification Goal:** Visually confirm the EXP gain and level-up trigger logic, and trace the stat increase process based on growth rates.

### 3.7 Promotion Mechanics

*   **Test File:** `tests/mechanic_tests/test_promotion_mechanics.py`
*   **Log File(s):** `logs/mechanic_tests/units/promotion_mechanics.txt`, `mage_promotion_mechanics.txt`.
*   **Key Visual Log Points:**
    *   Initial unit state (Level, Class, Stats).
    *   Promotion eligibility check (Level >= 10).
    *   Chosen promotion class from available options.
    *   Class change event.
    *   Application of promotion stat bonuses (showing stat name, bonus amount, before/after values).
    *   Level reset to 1 and EXP reset to 0.
    *   Acquisition of new skills (if applicable).
    *   Final unit state after promotion.
*   **Verification Goal:** Visually track the entire promotion sequence, verifying class change, correct stat bonuses application, level/EXP reset, and skill acquisition.

### 3.8 Status Effect Mechanics

*   **Test File:** `tests/mechanic_tests/test_status_effect_mechanics.py`
*   **Log File(s):** `logs/mechanic_tests/units/status_effect_mechanics.txt`, `poison_status_effect.txt`, `weakness_status_effect.txt`.
*   **Key Visual Log Points:**
    *   Status effect application event (unit affected, status name, duration).
    *   Immediate stat changes (if any), showing before/after values.
    *   Periodic effects at turn start/end (e.g., Poison damage dealt, HP change).
    *   Status duration countdown each turn.
    *   Status effect expiry event when duration reaches 0.
    *   Reversal of stat changes upon expiry.
*   **Verification Goal:** Visually track the lifecycle of status effects: application, periodic effects, duration countdown, expiry, and stat restoration.

### 3.9 Unit Interaction Mechanics

*   **Test File:** `tests/mechanic_tests/test_unit_interaction_mechanics.py`
*   **Log File(s):** `logs/mechanic_tests/units/support_mechanics.txt`, `adjacency_mechanics.txt`.
*   **Key Visual Log Points:**
    *   Initial unit positions and support partner definitions.
    *   Adjacency detection results between units.
    *   Application of adjacency bonuses (unit gaining, unit providing, bonus details - e.g., DEF +2).
    *   Support point gain events (triggering action like fighting together, points gained, total points, support pair).
    *   Support level increase event (pair, new level C/B/A/S).
    *   Description of bonuses granted by the new support level.
    *   Loss of adjacency and removal of associated bonuses when units move.
*   **Verification Goal:** Visually verify adjacency checks, the application and removal of adjacency-based bonuses, the accumulation of support points, and the progression through support levels.

## 4. Future Mechanics

All future game mechanics added must include corresponding visual tests following the approach outlined above. This ensures maintainability, aids debugging, and provides clear documentation of mechanic behavior. 