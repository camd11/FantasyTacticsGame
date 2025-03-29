Design Document: Thracia 776 Text-Based Simulation

Version: 1.0 (Based on Iteration 10)
Date: 2023-10-27

1. Introduction

    1.1. Vision: To create a playable, text-based tactical RPG simulation that accurately replicates the core gameplay mechanics and feel of Fire Emblem: Thracia 776, initially focusing on Chapter 1.

    1.2. Goal: Develop a robust Python application allowing a user to command player units against AI-controlled enemies on a grid map, utilizing unique Thracia mechanics like Capture, Fatigue, PCC, and specific Skills, with the objective of completing Chapter 1 (Leif escapes).

    1.3. Scope:

        In Scope (Current): Turn-based combat, grid movement with terrain, player/enemy units, detailed stat system (HP, Str, Mag, Skl, Spd, Lck, Def, Res, Con, Mov, PCC, Ldr Stars), inventory management (weapons, consumables, durability), Capture/Carry/Release mechanics, basic Fatigue accumulation, Weapon Triangle, Critical Hits (incl. PCC), Skills (Wrath, Vantage, Adept), Leadership Star aura, basic AI (target prioritization, pathfinding heuristic), text-based command interface, event system (houses, reinforcements), Chapter 1 escape objective.

        In Scope (Future - for Ch 1+): Fatigue penalties, improved AI (A*, better heuristics, item use, capture attempts), more Skills (Charge, Prayer, Nihil, etc.), Movement Stars, advanced Event System (dialogue, map changes), Dismount/Mount, Status Effects, specific weapon effects (Brave, Effective Dmg), UI/UX improvements.

        Out of Scope (Initially): Full graphical interface, multiple chapters beyond Ch 1 structure, complex inter-chapter management (shops, arena, BEXP), support conversations, full story replication.

2. Core Gameplay

    2.1. Game Flow: The game proceeds in turns, alternating between Player Phase and Enemy Phase.

    2.2. Player Phase:

        The player selects their units one by one.

        Fatigue check occurs at the start: Units with Fatigue >= Max HP are marked 'Exhausted' and cannot act.

        Selectable units can perform actions: Move, Attack, Capture, Wait, Use Item, Equip Weapon, Trade, Visit House, Escape (on specific tile), Manage Captive (Take item, Release), Drop Item.

        Most actions (except viewing info/targets, equipping, moving without subsequent action) cost the unit's turn and increment Fatigue.

        The phase ends when all player units have acted/are exhausted, or the player chooses to end the turn early.

    2.3. Enemy Phase:

        Turn-based events (e.g., Reinforcements) are triggered via the Event Manager.

        AI controls each enemy unit sequentially.

        AI evaluates targets, potential moves, and attack outcomes to choose an action (Attack, Move towards target, Wait).

        Actions increment enemy Fatigue (though it currently has no effect on AI).

        The phase ends when all enemy units have acted.

    2.4. Objective:

        Win: The designated main character ("Leif") uses the escape command on an Escape Tile ('X').

        Lose: Leif is defeated (HP reaches 0) or captured.

3. Key Systems & Mechanics

    3.1. Map & Terrain:

        Represented by a 2D list (Game.map_layout).

        Terrain types defined in TERRAIN_DATA with move_cost, defense bonus, avoid bonus, and is_passable properties.

        Movement calculation (Game.get_valid_moves) uses BFS considering terrain costs.

        Combat calculations (_resolve_attack) incorporate terrain Def/Avo bonuses for the defender.

        Special tiles: 'H' (House), 'h' (Visited House), 'X' (Escape Point).

    3.2. Units & Stats:

        Unit class stores all unit data.

        Base Stats: Stored privately (_base_...) - MaxHP, Str, Mag, Skl, Spd, Lck, Def, Res, Con, Mov. Also stores PCC, Leadership Stars.

        Effective Stats: Calculated via properties, applying penalties if is_capturing (Str, Mag, Skl, Spd, Def, Res, Mov are halved). Luck, Con are not halved.

        Combat Stats: Calculated via properties (attack_speed, attack_power, hit_rate, avoid, crit_rate_base, crit_avoid) using effective stats, equipped weapon stats. Leadership/Terrain/WT/PCC bonuses are applied dynamically during combat resolution/display.

        Status: is_alive, has_moved, has_acted, is_capturing, captured_unit, is_captured, has_escaped, is_exhausted, fatigue, skills (set).

    3.3. Combat System:

        Managed by Game.perform_combat, _resolve_normal_combat, _resolve_capture_combat, _resolve_attack.

        Sequence (Normal): Vantage Check -> Defender First Strike? -> Attacker First Strike -> Adept? -> Defender Counter -> Adept? -> Attacker Follow-up -> Adept? -> Defender Counter Follow-up -> Adept? (Checks for alive/weapon status between steps).

        Hit Calculation: Effective Hit = Base Hit (Skl*2 + Lck/2 + Wpn Hit) + WT Bonus + Leadership Bonus - Effective Avoid (Defender AS*2 + Lck + Terrain Avo + Leadership Bonus). Clamped 0-100.

        Damage Calculation: Final Damage = max(0, Attack Power [Unit Stat + Wpn Mt + WT Mt] - Effective Mitigation [Unit Def/Res + Terrain Def]).

        Critical Hit: Crit Chance = max(0, min(100, Base Crit [Unit Skl/2 + Wpn Crit] + PCC Bonus - Defender Crit Avoid [Luck])). Damage multiplied by 3.

        PCC Bonus: max(0, Attacker AS - Defender AS) * Attacker PCC added to effective Crit Rate.

        Weapon Triangle: Sword > Axe > Lance > Sword grants +/- WT_BONUS_HIT and +/- WT_BONUS_MT. Applied in _resolve_attack.

    3.4. Skills:

        Stored in Unit.skills set.

        Implemented:

            Wrath: Guaranteed critical on counterattack if HP <= 50% (_resolve_attack).

            Vantage: Strikes first when attacked if HP <= 50% (_resolve_normal_combat).

            Adept: Chance (Speed%) for immediate extra attack after own attack connects (_resolve_normal_combat).

        Target (Examples): Charge, Prayer, Nihil, specific weapon skills.

    3.5. Inventory & Items:

        Unit.inventory (list, size INVENTORY_SIZE). _equipped_weapon_index.

        Weapon class: Mt, Wt, Hit, Crit, Range, Type, Uses. use(), is_broken().

        Consumable class: Effect type, power. apply_effect(). Currently handles 'heal' and basic 'stat_' boosts.

        Commands: item, equip, use, drop, trade. Trade allows give.

    3.6. Capture Mechanic:

        Triggered by capture command. Requires Melee, Attacker CON >= Defender CON.

        Uses special combat resolution (_resolve_capture_combat) where captor has halved stats (_resolve_attack flag use_capture_stats). No skills assumed active during capture combat.

        If defender HP <= 0, defender state set to is_captured, captor state set to is_capturing.

        Captor suffers stat/move penalties via effective stat properties.

        Commands (while capturing): take <slot> (steals item, costs action), release (drops captive on adjacent tile, costs action). Captive dropped automatically if captor defeated.

    3.7. Fatigue System:

        Unit.fatigue increases by 1 via Unit.set_acted() called by most actions.

        At start of Player Phase (Game.next_turn), units with fatigue >= max_hp have is_exhausted set to True.

        Unit.can_act() returns False if is_exhausted. Flag reset on next turn's reset_turn.

        No stat penalty currently implemented for exhaustion, only action denial.

    3.8. Leadership System:

        Units have leadership_stars.

        Game.calculate_leadership_bonus(unit) sums stars from allies within LEADERSHIP_RANGE.

        Bonus (Stars * LEADERSHIP_BONUS_PER_STAR) applied to Hit and Avoid during combat (_resolve_attack) and display (display_map, handle_targets_command, handle_info_command).

    3.9. Event System:

        EventManager class attached to Game. Stores events keyed by trigger (turn number, visit coordinate).

        Game._register_chapter_events populates manager.

        Game.next_turn calls event_manager.trigger_turn_events.

        handle_visit_command calls event_manager.trigger_visit_event. Handles item rewards, message display, marking visited status.

    3.10. AI:

        Enemy-controlled units act sequentially during Enemy Phase.

        decide_enemy_action: Primary decision logic.

        Evaluates potential attacks from all reachable squares against all player targets.

        Uses predict_combat to estimate outcomes.

        Scores actions based on damage dealt/taken, lethality, terrain (attacker/defender), basic skill avoidance (Wrath/Vantage).

        Selects highest-scoring valid attack where AI survives.

        If no suitable attack, uses find_best_move_towards_target (Manhattan distance heuristic) to move closer to priority target (Leif > closest).

        Movement uses get_valid_moves (BFS with terrain cost).

        Limitations: Prediction is simplified (no crit/skill effects factored); no item use, capture attempts, or complex tactical positioning. Pathfinding for non-attack moves is basic.

4. User Interface

    4.1. Input: Text commands entered via input(). Commands generally follow action [arg1] [arg2] format (e.g., move 5 5, attack 6 5, equip 1). Single-letter shortcuts provided for common actions.

    4.2. Output: Game state displayed via print() statements.

        display_map: Shows grid with terrain, unit symbols (case indicates acted status, '*' indicates selected, '+' indicates capturing).

        Unit lists show status (HP, Fatigue, Skills, Exhausted, Carrying, etc.) and location/terrain. Leadership bonus displayed.

        Selected unit info details stats (Base->Eff), combat forecast stats (incl. Ldr bonus), inventory.

        Combat log provides step-by-step resolution (attacks, counters, skills, WT, damage, misses, crits, breaks, defeats).

        Command feedback messages indicate success/failure/invalid input.

5. Target Platform & Technology

    Platform: Command Line / Terminal.

    Language: Python 3.x.

    Libraries: math, random, os, collections, copy. No external libraries required currently.

6. Future Considerations

    Graphical User Interface (Pygame, Kivy, etc.).

    Support for multiple chapters, inter-chapter management.

    More complex AI behavior (coordinated tactics, item use, capturing).

    Full implementation of all Thracia skills and mechanics (Move Stars, Dismount, Statuses).

    Save/Load functionality.

    Sound/Music cues.

    Configuration files for units, items, maps.

    Automated testing framework.