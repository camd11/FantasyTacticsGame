1. Introduction

This document describes the simplified design for the Artificial Intelligence (AI) system responsible for controlling non-player characters (NPCs) in our Fire Emblem-style turn-based tactical RPG (SRPG). The primary goal is to create a functional and predictable AI capable of executing basic tactics according to unit roles and objectives. This system must operate within the game's rules and utilize unit capabilities effectively. A key use case for this AI is automated testing, where the AI will control units on both sides of a conflict to test game mechanics and balance.

2. Goals

The AI system aims to achieve the following:

    Functional: AI units should perform valid actions according to game rules.

    Believable: AI actions should generally make tactical sense based on their role and the immediate situation. Avoid obviously illogical moves.

    Role-Based: Different unit types/roles (e.g., attacker, healer) should exhibit distinct, simple behaviors.

    Deterministic (Optional but helpful for testing): Given the same starting state, the AI should ideally make the same decisions, facilitating reproducible tests. (May require careful handling of tie-breaking).

    Performant: AI decision-making must be computationally efficient to allow for reasonably fast turn resolution, especially in AI vs AI scenarios with potentially many units.

    Testable: The AI's logic should be clear enough to debug and verify, supporting its use in automated testing.

3. Core Architecture: Utility-Based AI

We will utilize a Utility-Based AI architecture. This approach involves:

    Identify Potential Actions: Enumerate possible actions (Move+Attack, Move+Skill, Move+Item, Move+Wait).

    Score Actions: Evaluate each action using a set of weighted "Considerations" (scorers) that measure the desirability of outcomes (e.g., dealing damage, staying safe, healing).

    Select Best Action: Choose the action with the highest score.

Why Utility AI (Simplified)?

    Flexibility: Still allows tuning behavior by adjusting scorer weights for different roles.

    Structured Decision Making: Provides a clear framework for comparing different types of actions (attacking vs. healing vs. repositioning).

    Sufficient for Core Tactics: Can model essential behaviors like attacking, healing, and basic positioning.

4. Decision-Making Process (Per AI Unit Turn)

Step 1: Information Gathering

    Identify the unit's current state (HP, status, position, equipment, skills, items).

    Scan the map for:

        Enemy unit positions, HP, basic threat level.

        Ally unit positions, HP.

        Terrain features.

        Objective locations/status (if applicable, e.g., 'Defeat Commander X').

Step 2: Determine Role & Objective

    Identify the unit's AI Persona/Role (see Section 5).

    Identify the Scenario Objective (e.g., Rout Enemy, Defeat Specific Unit). This provides high-level context.

Step 3: Generate Potential Actions

    Enumerate valid possibilities:

        Move + Attack: All reachable squares + attackable targets.

        Move + Use Skill: All reachable squares + valid skill targets (healing, simple buffs/debuffs).

        Move + Use Item: All reachable squares + valid item uses (primarily self-healing).

        Move + Wait: All reachable squares.

Step 4: Score Potential Actions (Utility Calculation)

    For each generated (Move Target Square, Action Type, Action Target) tuple, calculate a score based on weighted Considerations (Scorers).

    Sum weighted scores for the final Utility Score.

    Simplified Considerations / Scorers:

        Offensive:

            DamageDealt: Estimated damage output (factor in basic combat rules).

            KillPotential: Bonus if the attack is likely to defeat the target.

            TargetPriority: Simple priority (e.g., lowest HP enemy, objective target > other enemies).

        Defensive:

            SelfPreservation: Score based on remaining HP after the action (including counterattack). Higher is better. Avoids actions leading to immediate death if possible.

            DamageTaken (Counter): Negative score based on expected counterattack damage.

        Positional:

            TerrainBonus: Small bonus for ending on favorable terrain (e.g., Fort, Forest).

            ObjectiveProximity: Score based on distance to the primary map objective location or target unit.

        Healing/Support:

            HealAllyAmount: Score based on HP restored to an allied unit.

            HealAllyPriority: Bonus for healing lower HP allies.

            SelfHealAmount: Score for using a self-healing item (e.g., Vulnerary). Crucial for retreat logic.

        Resource Management:

            ItemUsedCost: Small negative score for consuming a limited-use item.

    Weighting: Weights are primarily determined by the Unit Role/Persona. No dynamic difficulty scaling.

Step 5: Select and Execute Action

    Identify the action with the highest total Utility Score.

    Tie-Breaking: Use a simple, deterministic tie-breaker (e.g., Attack > Skill > Item > Wait; prioritize targets with lower ID if scores are identical) to ensure reproducibility for testing.

    Execute the chosen action.

5. AI Personas / Roles (Simplified)

Define a small set of core roles with distinct default weights:

    Aggressor: Prioritizes dealing damage. High weights for DamageDealt, KillPotential. Moderate weight for SelfPreservation. Will engage most targets.

    Defender/Guardian: Prioritizes survival and holding ground, often near objectives or other allies. High weights for SelfPreservation, TerrainBonus. Lower weight for initiating attacks unless threatened or a very high-value opportunity exists. Boss units can often use this persona.

    Healer: Prioritizes healing allies. High weights for HealAllyAmount, HealAllyPriority. Will try to stay out of direct danger, weighting SelfPreservation highly.

    ObjectiveFocused: Prioritizes moving towards objectives. High weight for ObjectiveProximity. Will only engage enemies if they directly block the path or present an extremely easy kill opportunity.

6. Performance Considerations

    Action Space Pruning: Limit evaluation to squares reasonably close to enemies, allies, or objectives.

    Caching: Cache pathfinding or range checks within a single unit's turn analysis.

    Optimization: Ensure scoring functions (especially combat previews) are efficient.

    Avoid Lookahead: No multi-turn prediction. Decisions are based on the current turn only.

7. Tools & Debugging

    AI Visualizer: In-game overlay showing movement/attack ranges, potential targets, and perhaps the chosen action's target/destination.

    AI Logger:

        Default: Minimal logging (e.g., Unit X moving to (Y,Z) and attacking Unit A). Use abbreviations (e.g., U:5 MV(10,12) ATK U:12).

        Detailed Mode (via command-line flag/console command): Output detailed logs for debugging specific scenarios. Show top N considered actions, their scores, and the breakdown by scorer (e.g., ACTION: MV(10,12) ATK U:12 | Score: 85 | DmgDealt:50(w:1.0) KillPot:20(w:0.5) SelfPrsv:15(w:1.0) ...). Terse format with abbreviations is still preferred even in detail mode to manage volume.

    Weight Editor: Tool to view and modify scorer weights for each AI persona.

    Scenario Tester: Ability to set up specific map states to test AI behavior reproducibly.

8. Specific Behaviors & Edge Cases

    Weapon Triangle/Effectiveness: Must be included in DamageDealt calculations.

    Skills/Items: AI needs basic logic to use available skills (healing, simple attacks) and items (primarily self-healing). Score actions involving limited resources appropriately (ItemUsedCost).

    Status Effects: Keep simple. AI might prioritize healing negative statuses if a Healer, but otherwise may largely ignore them unless they prevent action.

    Retreat Logic (Simplified):

        A unit will consider using a self-healing item (e.g., Vulnerary) if its HP is below a certain threshold (e.g., < 40%-50%).

        The SelfHealAmount scorer will give this action a high utility value in that situation.

        If the unit does not possess a self-healing item, it will not attempt to retreat based solely on low HP. It will follow its standard role logic (e.g., an Aggressor might fight to the death, a Defender might still prioritize safe positioning if possible).

    Target Selection: Primarily driven by TargetPriority (low HP, objective target) and KillPotential.

9. Conclusion

This simplified Utility-Based AI design provides a functional core for controlling units in our SRPG. By focusing on essential tactical considerations (damage, survival, healing, objectives) and defining distinct roles via scorer weights, we can achieve predictable and testable AI behavior suitable for core gameplay and automated AI vs AI testing. The emphasis is on clear logic, performance, and ease of debugging over complex, adaptive strategies.