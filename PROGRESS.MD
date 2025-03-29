# Documentation: Python Text-Based Fire Emblem Clone (Thracia 776 Ch 1 Goal)

## Overview

This Python script implements a playable, text-based tactical RPG battle system inspired by Fire Emblem, specifically aiming to replicate core mechanics found in Thracia 776's Chapter 1. The game features a grid map, turn-based combat, player/enemy units with various stats, inventory management, and several Thracia-specific mechanics like Capture, Fatigue, PCC, and some Skills.

## Current State (Iteration 10)

The game is functional and simulates a battle scenario based on Chapter 1's units and general layout.

## Key Features Implemented

*   **Grid & Movement:** Units move on a 2D grid (`Game.map_layout`). Movement uses BFS pathfinding considering terrain costs (`Game.get_valid_moves`, `TERRAIN_DATA`).
*   **Units:** `Unit` class stores base stats (`_base_...`) and calculates effective stats based on status (e.g., capturing halves most stats). Includes HP, Str, Mag, Skl, Spd, Lck, Def, Res, Con, Mov, PCC, Leadership Stars.
*   **Combat System:**
    *   Initiated via `Game.perform_combat`.
    *   Handles attack sequence, counterattacks, follow-up attacks (based on Attack Speed `FOLLOW_UP_THRESHOLD`).
    *   Includes Critical Hits (`_resolve_attack` checks `crit_rate_base`, PCC bonus, `crit_avoid`). Crit damage is Damage * 3.
    *   Includes Weapon Triangle (Sword>Axe>Lance>Sword) for +/- Hit/Mt (`_resolve_attack`, `WT_BONUS_*`).
    *   Includes Terrain bonuses (Def/Avo) for the defender (`_resolve_attack` uses `game.get_terrain_props`).
    *   Basic Skill Integration:
        *   Vantage: Defender strikes first if HP <= 50% (`_resolve_normal_combat`).
        *   Adept: Chance (Speed%) for extra attack after hitting (`_resolve_normal_combat`).
        *   Wrath: Guaranteed crit on counter if HP <= 50% (`_resolve_attack`).
*   **Inventory & Items:**
    *   Units have a fixed-size inventory (`INVENTORY_SIZE`).
    *   `Weapon` (with durability/uses) and `Consumable` item types.
    *   Commands: `item`, `equip`, `use`, `drop`, `trade`.
*   **Capture:**
    *   `capture` command initiates capture combat (`perform_combat` with flag). Requires `Attacker CON >= Defender CON`.
    *   Capture combat uses halved stats for the captor (`_resolve_attack` with flag).
    *   Units have `is_capturing`, `captured_unit`, `is_captured` states.
    *   Captors have halved stats/move.
    *   Commands: `take` (steal from captive), `release`.
*   **Fatigue:**
    *   `Unit.fatigue` increments per action (`Unit.set_acted`).
    *   Units with `fatigue >= max_hp` are marked `is_exhausted` at the start of the player phase and `can_act()` returns False.
*   **PCC & Leadership:**
    *   Units have `pcc` and `leadership_stars` stats.
    *   PCC adds to crit chance based on AS difference (`_resolve_attack`).
    *   Leadership stars grant Hit/Avoid bonus to nearby allies (`calculate_leadership_bonus`, applied in `_resolve_attack` and display).
*   **AI:**
    *   `handle_enemy_turn` orchestrates AI actions.
    *   `decide_enemy_action` evaluates potential attacks from reachable squares using `predict_combat`.
    *   Uses a heuristic score considering damage, kills, risk, terrain, and basic skill avoidance (Wrath/Vantage).
    *   If no good attack, uses `find_best_move_towards_target` (simple distance heuristic) to move.
    *   AI movement uses `get_valid_moves` (BFS with terrain cost).
*   **Events:**
    *   Basic `EventManager` handles turn-based reinforcements and house visits.
    *   `Game._register_chapter_events` sets up events based on constants.
*   **Objective:** Win by having Leif `escape` on 'X' tiles. Lose if Leif is defeated/captured.

## Core Classes

*   **`Game`:** Main class orchestrating the game loop, map, unit list, turns, commands, combat initiation, AI turn. Holds `EventManager`.
*   **`Unit`:** Represents player and enemy units. Manages stats (base vs effective), status flags (acting, capturing, fatigue, etc.), inventory, skills. Contains action methods (`move_unit`, `wait`, `escape`, etc.) and combat-related properties.
*   **`Item` / `Weapon` / `Consumable`:** Define items, their properties (stats, uses, effects), and basic methods.
*   **`EventManager`:** Manages triggering time-based (reinforcements) or location-based (visits) events.

## Combat Flow (`perform_combat`, `_resolve_normal_combat`, `_resolve_attack`)

1.  `perform_combat`: Checks validity, sets attacker acted, determines normal vs capture, calls appropriate resolve function, handles post-combat death/capture checks (including dropping captives).
2.  `_resolve_normal_combat`: Checks Vantage -> Defender optional first strike (+ Adept) -> Attacker first strike (+ Adept) -> Defender counter (+ Adept) -> Attacker follow-up (+ Adept) -> Defender counter follow-up (+ Adept). Ensures units are alive/weapons okay between steps.
3.  `_resolve_attack`:
    *   Checks weapon use/break.
    *   Calculates effective stats for attacker/defender *including capture penalty if applicable*.
    *   Calculates Leadership bonus for both units.
    *   Calculates Weapon Triangle bonus (Hit/Mt).
    *   Calculates effective Hit (Base + WT + Ldr - Eff. Avoid [Base + Terrain + Ldr]).
    *   Rolls Hit.
    *   If Hit:
        *   Checks Wrath.
        *   Calculates PCC bonus.
        *   Calculates effective Crit (Base Crit + PCC - Crit Avoid).
        *   Rolls Crit.
        *   Calculates Damage (Attack Power [Base + Wpn Mt + WT Mt] - Effective Mitigation [Base Def/Res + Terrain Def]).
        *   Applies Crit multiplier (x3).
        *   Calls `defender.take_damage(final_damage)`.
    *   Returns `True` if weapon broke this attack.

## AI Logic (`handle_enemy_turn`, `decide_enemy_action`, `predict_combat`, `find_best_move_towards_target`)

1.  Iterate through enemy units that `can_act`.
2.  `decide_enemy_action`:
    *   Find all reachable squares via BFS (`get_valid_moves`).
    *   For each potential player target:
        *   Find all reachable squares from which an attack is possible.
        *   For each such attack: call `predict_combat`.
        *   Score the predicted outcome (prioritize kills, damage dealt; penalize damage taken, target on terrain, target with dangerous skills).
    *   If any valid, survivable attacks exist with score > threshold, choose the best one. Return attack details.
    *   If no good attack, call `find_best_move_towards_target`.
    *   `find_best_move_towards_target`: Identify priority target (Leif > closest). Find the unit's reachable square that has the minimum *Manhattan distance* to the target. Return this move.
    *   If no attack and no move, return None (wait).
3.  `handle_enemy_turn`: Execute the move and/or attack returned by `decide_enemy_action`.

## Known Limitations / Areas for Improvement

*   **AI Depth:** AI prediction is basic (ignores crits, complex skills, weapon breaking). No AI capturing, item usage, or complex coordination. Pathfinding for non-attack moves uses Manhattan distance, not true path cost.
*   **Skills:** Only Wrath, Vantage, Adept implemented simply. Many Thracia skills missing (Charge, Prayer, Nihil, etc.). No skill activation %s other than Adept=Speed.
*   **Fatigue:** Only prevents action; no stat penalties or specific recovery items (S Drink) yet.
*   **UI:** Purely text-based. No graphical map, limited combat forecast detail.
*   **Events:** Event system is basic; no complex triggers, dialogue, or map changes beyond house visits.
*   **Thracia Mechanics:** Missing Movement Stars, PCC implementation details might differ slightly, no Dismount/Mount, no detailed status effects (Sleep, Berserk), no specific weapon effects (Brave, effective damage, magic swords).
*   **Testing:** No automated tests. Functionality verified via simulation/manual play.
*   **Code Structure:** Becoming large; could benefit from splitting into multiple files (e.g., `units.py`, `items.py`, `game.py`, `ai.py`, `events.py`). Refactoring `_resolve_attack` might improve clarity.

## How to Run

Save the code as a `.py` file (e.g., `thracia_sim.py`) and run from the terminal:
`python thracia_sim.py`