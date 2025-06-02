# Specification: AI System

This document outlines the data structures and functionalities for the Artificial Intelligence (AI) system controlling enemy and Non-Player Character (NPC) units in the Fire Emblem Thracia 776 recreation. The AI must be capable of playing through levels for testing purposes.

## 1. Core Concepts

*   **AI Behavior**: A set of rules and priorities that dictate a unit's actions and movements.
*   **AI Script**: A predefined sequence of logic or a set of conditions that an AI unit follows. Thracia 776 uses distinct scripts for movement and actions, as seen in [`MovementAIPointers.csv`](FireEmblem5/TABLES/MovementAIPointers.csv:0) and [`ActionAIPointers.csv`](FireEmblem5/TABLES/ActionAIPointers.csv:0).
*   **AI Personality/Role**: Units can be assigned different AI behaviors based on their class, role (e.g., attacker, healer, thief), or specific chapter events.
*   **Targeting Priority**: Rules that determine which enemy unit an AI will prioritize attacking or interacting with.
*   **Movement Strategy**: Rules that determine how an AI unit will position itself on the map.
*   **Threat Assessment**: AI's evaluation of danger from player units and advantageous positions. This can be quantified by factors like potential damage output of enemies, their range, effective speed, specific abilities (e.g., siege tomes, status staves), and number of units threatening a tile.
*   **Objective-Driven Behavior**: AI may have specific objectives beyond combat, such as reaching a location, protecting another unit, or using an item on a tile.

## 2. AI Architecture

The AI system will be modular, consisting of:

1.  **AI Controller**: Manages the AI turn, iterating through active AI units.
2.  **Unit AI Component**: Attached to each AI-controlled `UnitInstance`, holding its assigned `UnitAIAssignment`.
3.  **Movement AI Module**: Contains a library of movement scripts/logics.
    *   Input: Current `UnitInstance`, `MapData`, list of player units and other AI units.
    *   Output: Target (X, Y) coordinate for movement.
4.  **Action AI Module**: Contains a library of action scripts/logics.
    *   Input: Current `UnitInstance` (after movement), `MapData`, list of player units and other AI units.
    *   Output: Chosen action (e.g., attack target, use staff on ally, wait).

## 3. Data Structures

### 3.1. AI Assignment

```pseudocode
// Defines the AI behavior assigned to a unit, often per chapter or unit type
CLASS UnitAIAssignment
    // PROPERTIES
    STRING AssignmentID // e.g., "Chapter1ArcherAI", "GenericHealerAI"
    MovementAIScriptID MovementScriptID // From MovementAIPointers.csv
    ActionAIScriptID ActionScriptID // From ActionAIPointers.csv
    TargetingParameters Parameters // Optional: Specific rules for this assignment

    // TEST: MovementScriptID and ActionScriptID must be valid script IDs.
    // TEST: Parameters, if present, must conform to expected structure.

    // METHODS
    CONSTRUCTOR(AssignmentID, MovementScriptID, ActionScriptID, Parameters OPTIONAL)
END CLASS

CLASS TargetingParameters
    // PROPERTIES
    PrioritizeUnitIDs: ARRAY<STRING> // List of Unit IDs to target above others
    IgnoreUnitIDs: ARRAY<STRING> // List of Unit IDs to never target
    PreferClassTypes: ARRAY<ClassID> // List of character classes to prioritize targeting
    AttackIfCanKill: BOOLEAN // Prioritize actions that defeat a target
    FleeThresholdHPPercentage: FLOAT // HP percentage below which to consider fleeing (e.g., 0.3 for 30%)
    // Further parameters can be added as needed by specific scripts
    // These parameters would be checked by individual movement/action scripts.
    // For example, a targeting script would first filter by IgnoreUnitIDs,
    // then check PrioritizeUnitIDs, then apply general logic.
END CLASS

// UnitInstance in 02_CharacterAndClassSystem.md should have a property:
// UnitAIAssignment CurrentAIBehavior; (if AI controlled)
```

### 3.2. Movement AI Scripts (Conceptual)

These correspond to entries like `aMovementAI00Script` from [`MovementAIPointers.csv`](FireEmblem5/TABLES/MovementAIPointers.csv:0).

```pseudocode
ENUM MovementAIScriptID
    Pursue_Closest // Example: MovementAI_Pursue_Identifier
    Pursue_Weakest
    Pursue_Lord // Example: Implied by TalkToLeif or specific targeting
    Stationary // Example: MovementAI_Stationary_Identifier
    Flee_FromStrongest
    Flee_WhenLowHP // Example: MovementAI_Flee_Identifier
    MoveTo_TargetCoordinates // For objectives like reaching an exit
    MoveTo_Ally // e.g., StayWithFred
    MoveTo_Item // e.g., Thief moving to chest
    Patrol_Points // Example: MovementAI_GroupPatrolUntilAlerted_Identifier
    Avoid_MultipleOpponents // Example: MovementAI_AvoidMultipleOpponents_Identifier
    // ... other specific scripts from the CSV
END ENUM

// Each script would be a function or a set of rules:
FUNCTION ExecuteMovementScript(CurrentUnit UnitInstance, ScriptID MovementAIScriptID, CurrentMap MapData, AllPlayerUnits ARRAY<UnitInstance>, AllAIUnits ARRAY<UnitInstance>) RETURNS TargetCoordinates
    // LOGIC based on ScriptID and CurrentUnit.CurrentAIBehavior.Parameters
    // - Calculate pathfinding using A* or similar algorithm.
    // - Evaluate terrain costs and safety (threat assessment of tiles).

    SWITCH ScriptID
        CASE Pursue_Closest
            // 1. Identify all valid enemy targets (not in IgnoreUnitIDs). Consider PreferClassTypes.
            // 2. For each target, calculate pathfinding distance from CurrentUnit's position.
            //    Consider terrain movement costs.
            // 3. Select the target with the shortest pathfinding distance.
            //    Tie-breaking: e.g., lowest current HP, PrioritizeUnitIDs, or a predefined priority.
            // 4. Determine all squares within CurrentUnit's movement range from which it can attack the selected target.
            // 5. From these attack squares, find the one reachable with the shortest path from CurrentUnit's current location.
            //    If multiple, pick the safest (e.g., fewest enemy attack ranges, best defensive terrain).
            // 6. If no attack square is reachable this turn, move towards the target along the shortest path,
            //    stopping at max movement range or a safe intermediate point.
            // TEST: AI_Movement_PursueClosest_CorrectTargetSelection: Unit selects the target with the shortest valid path according to parameters.
            // TEST: AI_Movement_PursueClosest_OptimalMoveToAttack: Unit moves to the best square to attack the chosen closest target.
            // TEST: AI_Movement_PursueClosest_AdvanceWhenNoAttack: Unit moves towards closest target if attack is not possible this turn.
            BREAK
        CASE Stationary
            RETURN CurrentUnit.Position
            // TEST: AI_Movement_Stationary_NoMove: Unit does not change position.
            BREAK
        CASE Flee_WhenLowHP
            // 1. Check if CurrentUnit.CurrentHP / CurrentUnit.MaxHP < Parameters.FleeThresholdHPPercentage.
            // 2. If true, identify all player units that can attack CurrentUnit.
            // 3. Find reachable tiles that maximize distance from threatening player units, prioritizing safety.
            // TEST: AI_Movement_Flee_ActivatesAtThreshold: Unit attempts to flee only when HP is below threshold.
            // TEST: AI_Movement_Flee_MovesAwayFromThreat: Unit moves to a safer location away from enemies.
            BREAK
        // ... other cases
    END SWITCH

    // Default: if no specific logic or target found, unit might hold position or move to a default safe spot.
    // This should ideally be handled by a specific "HoldPosition" or "CautiousAdvance" script.
    // TEST: AI_Movement_ValidMove: AI unit always selects a valid move within its movement range.
    // TEST: AI_Pathfinding_NavigatesTerrain: AI pathfinding correctly navigates terrain and obstacles.
END FUNCTION
```

### 3.3. Action AI Scripts (Conceptual)

These correspond to entries like `aActionAI00Script` from [`ActionAIPointers.csv`](FireEmblem5/TABLES/ActionAIPointers.csv:0).

```pseudocode
ENUM ActionAIScriptID
    Attack_StrongestAvailableWeapon // Example: ActionAI_IgnoreNone_Identifier
    Attack_EffectiveWeapon
    Attack_HighestHP // Example: ActionAI_TargetHighestHP_Identifier
    Attack_LowestDefense
    Attack_Lord // Example: ActionAI_TargetLord_Identifier
    UseStaff_HealLowestHPAlly
    UseStaff_StatusDebuffEnemy // e.g., Silence, Sleep
    UseStaff_SupportAlly // e.g., Barrier, Restore
    Dance_ForAlly // Example: ActionAI_Dance_Identifier
    Steal_FromTarget
    Open_ChestOrDoor
    NoAction // Example: ActionAI_NoAction_Identifier
    Ignore_SpecificUnits // Example: ActionAI_IgnoreLeif_Identifier (handled by TargetingParameters)
    Force_HealSelfOrAlly // Example: ActionAI_ForceHeal_Identifier
    // ... other specific scripts from the CSV
END ENUM

// Each script would be a function or a set of rules:
FUNCTION ExecuteActionScript(CurrentUnit UnitInstance, ScriptID ActionAIScriptID, CurrentMap MapData, AllPlayerUnits ARRAY<UnitInstance>, AllAIUnits ARRAY<UnitInstance>) RETURNS AIAction
    // LOGIC based on ScriptID and CurrentUnit.CurrentAIBehavior.Parameters
    // - Evaluate potential targets for attacks or staff uses from CurrentUnit's current position.

    SWITCH ScriptID
        CASE Attack_StrongestAvailableWeapon
            // 1. Identify all enemy units within attack range of CurrentUnit's equipped weapons (respecting IgnoreUnitIDs, PrioritizeUnitIDs).
            // 2. For each potential target and for each usable weapon:
            //    a. Calculate expected damage (considering weapon might, unit strength/magic, target defense/resistance, effective damage, hit rate, critical hit chance).
            //    b. Note if the attack would be lethal.
            // 3. If Parameters.AttackIfCanKill is true, prioritize lethal attacks.
            // 4. Otherwise, select the weapon-target combination that yields the highest expected damage.
            //    Tie-breaking: e.g., target with lowest HP, target that can't counter-attack, PrioritizeUnitIDs.
            // 5. If no attack is beneficial (e.g., 0 damage, very low hit rate), consider no action.
            // IF a target and weapon are selected THEN
            //     RETURN new AIAction(ActionType.Attack, SelectedTarget, SelectedWeapon, null)
            // END IF
            // TEST: AI_Action_AttackStrongest_CorrectWeaponAndTarget: Unit selects weapon and target for max expected damage according to parameters.
            // TEST: AI_Action_AttackStrongest_PrioritizesKill: Unit prioritizes lethal attacks if configured.
            BREAK
        CASE UseStaff_HealLowestHPAlly
            // 1. Identify all allied units (including self if applicable) within range of equipped healing staves.
            // 2. Select the ally with the lowest HP percentage (or highest absolute damage taken).
            // 3. If multiple, prioritize allies in more danger or key units.
            // IF an ally and staff are selected THEN
            //     RETURN new AIAction(ActionType.UseStaff, SelectedAlly, HealingStaff, null)
            // END IF
            // TEST: AI_Action_HealLowestHP_CorrectTarget: Unit heals the most wounded ally in range.
            BREAK
        // ... other cases
    END SWITCH

    // Default: If no beneficial action found by the script, return a "Wait" action.
    RETURN new AIAction(ActionType.Wait, null, null, null)
    // TEST: AI_Action_ValidAction: AI unit always selects a valid action.
END FUNCTION

CLASS AIAction
    ActionType Type // (Attack, UseStaff, UseItem, Wait, Dance, Steal, Open)
    UnitInstance TargetUnit // For attacks or single-target staves
    ItemID ItemToUse // Weapon, staff, or item
    Point TargetCoordinates // For area staves or movement-related actions like opening a door
END CLASS
```

## 4. AI Decision Process (Per AI Unit Turn)

1.  **Movement Phase**:
    a.  Retrieve the unit's `MovementAIScriptID` and `TargetingParameters` from `CurrentUnit.CurrentAIBehavior`.
    b.  Execute the corresponding movement script (`ExecuteMovementScript`), considering:
        i.  Unit's movement range.
        ii. Terrain.
        iii.Position of player units (threats, targets).
        iv. Position of other AI units (allies, objectives).
        v.  Script-specific goals (e.g., flee, reach point, guard area) and parameters.
        vi. Advanced Consideration: Some movement scripts might perform a preliminary evaluation
            of potential actions from candidate destination squares to choose a move
            that not only positions well but also enables a strong subsequent action.
    c.  Move the unit to the chosen `TargetCoordinates`.
    *   // TEST: AI_Movement_TacticalPositioning: AI unit moves to a tactically sound position based on its script.

2.  **Action Phase**:
    a.  Retrieve the unit's `ActionAIScriptID` and `TargetingParameters` from `CurrentUnit.CurrentAIBehavior`.
    b.  Execute the corresponding action script (`ExecuteActionScript`), considering:
        i.  Available weapons, staves, items.
        ii. Reachable targets from the new position.
        iii.Health of allies and enemies.
        iv. Script-specific goals (e.g., attack lord, heal ally, steal) and parameters.
    c.  Execute the chosen `AIAction`.
    d.  If no valid or beneficial action is determined by the script (i.e., `ExecuteActionScript` returns a "Wait" action), the unit will perform a "Wait" action.
    *   // TEST: AI_Action_TacticalAction: AI unit performs a tactically sound action based on its script.
    *   // TEST: AI_Action_DefaultsToWait: Unit waits if no better action is available or determined by its script.

## 5. Key AI Behaviors to Implement (based on CSVs and common FE patterns)

*   **Aggressive Attacker**: Moves to engage and attack the most suitable target (based on damage output, kill potential, or specific target priority like "Lord"). AC: Unit consistently moves to engage and attacks the target offering the best combat outcome (e.g., highest damage, KO potential, or specified priority target) within its capabilities and script parameters.
*   **Defensive/Stationary**: Holds a position, attacks enemies that come into range. May prioritize targets threatening a guarded unit or location. AC: Unit maintains its designated area and attacks any enemy entering its range, prioritizing threats to its guard target if applicable, according to its script.
*   **Healer/Support**: Prioritizes healing injured allies or using support staves. Will try to stay out of direct danger. AC: Unit prioritizes healing/supporting allies based on need (e.g., lowest HP, critical status) and positions safely, as per its script.
*   **Thief/Objective Rusher**: Prioritizes moving towards chests, doors, villages, or escape points, often avoiding combat unless necessary. AC: Unit prioritizes movement towards and interaction with objectives (chests, doors, escape points), avoiding combat where possible, according to its script.
*   **Dancer/Bard**: Moves to use "Dance" or "Play" on an allied unit that has already acted. AC: Unit successfully uses its special action on an eligible allied unit that has completed its turn, if such a target exists.
*   **Fleeing Unit**: Moves away from threats, especially when at low HP or dictated by script. AC: Unit moves away from the most significant threats when its HP is below the configured threshold or a script-defined condition is met.
*   **Specific Target Focus**: AI that ignores certain units or prioritizes others (e.g., "Ignore Leif", "Target Lord" via `TargetingParameters`). AC: Unit correctly prioritizes or ignores specified targets according to its assigned rules in `TargetingParameters`.
*   **Group Tactics**: Units that coordinate, such as staying near a leader or forming a defensive line. (More advanced, but `MovementAI_StayWithFred_Identifier` hints at this). AC: Units assigned group tactics maintain formation or support designated leader units as per their script.

## 6. AI for Testing

For the requirement "AI should be able to play levels for testing":
*   The AI must be robust enough to make valid moves and actions consistently.
*   A "Default Aggressive" AI profile (e.g., `MovementAIScriptID.Pursue_Closest` + `ActionAIScriptID.Attack_StrongestAvailableWeapon`) can be assigned to all enemy units for basic playthrough testing.
*   The AI should be able to complete simple map objectives like "defeat all enemies" or "defeat boss".
*   More complex objectives (e.g., seize throne, escape) will require more sophisticated AI scripts.
    *   // TEST: AI_Test_CompleteDefeatAllEnemiesMap: AI can complete a simple "Defeat All Enemies" map.
    *   // TEST: AI_Test_CompleteDefeatBossMap: AI can complete a simple "Defeat Boss" map.
    *   // TEST: AI_Test_VarietyOfActions: AI units use a variety of their available actions (attack, staff if applicable) during a test playthrough.

## 7. TDD Anchors

*   General & System Level:
    *   `// TEST: AI_System_UnitTakesTurn`: An AI-controlled unit successfully completes its movement and action phases.
    *   `// TEST: AI_System_AllAIUnitsAct`: All active AI units take their turns in sequence.
    *   `// TEST: AI_Pathfinding_NavigatesTerrain`: AI pathfinding correctly navigates various terrain types and obstacles.
    *   `// TEST: AI_Movement_ValidMove`: AI unit always selects a valid move within its movement range.
    *   `// TEST: AI_Action_ValidAction`: AI unit always selects a valid action (or waits).
    *   `// TEST: AI_Action_DefaultsToWait`: Unit waits if no better action is available or determined by its script.

*   Specific Script Logic (Examples):
    *   `// TEST: AI_Movement_PursueClosest_CorrectTargetSelection`: Unit selects the target with the shortest valid path according to parameters.
    *   `// TEST: AI_Movement_PursueClosest_OptimalMoveToAttack`: Unit moves to the best square to attack the chosen closest target.
    *   `// TEST: AI_Movement_PursueClosest_AdvanceWhenNoAttack`: Unit moves towards closest target if attack is not possible this turn.
    *   `// TEST: AI_Movement_Stationary_NoMove`: Stationary AI unit does not change position.
    *   `// TEST: AI_Movement_Flee_ActivatesAtThreshold`: Unit attempts to flee only when HP is below threshold.
    *   `// TEST: AI_Movement_Flee_MovesAwayFromThreat`: Unit moves to a safer location away from enemies when fleeing.
    *   `// TEST: AI_Action_AttackStrongest_CorrectWeaponAndTarget`: Unit selects weapon and target for max expected damage according to parameters.
    *   `// TEST: AI_Action_AttackStrongest_PrioritizesKill`: Unit prioritizes lethal attacks if configured.
    *   `// TEST: AI_Action_HealLowestHP_CorrectTarget`: AI healer correctly identifies and heals a wounded ally in range.

*   Behavioral & Objective Based:
    *   `// TEST: AI_Targeting_LordFocus`: AI with "Target Lord" script/parameter prioritizes attacking the designated Lord unit.
    *   `// TEST: AI_Targeting_IgnoreSpecific`: AI with "Ignore X" parameter does not target X.
    *   `// TEST: AI_Objective_ReachPoint`: AI (e.g., thief) moves towards a designated objective point (chest/exit).
    *   `// TEST: AI_StaffUsage_CorrectTargetAndEffect`: AI uses offensive/support staves on appropriate targets.
    *   `// TEST: AI_Dance_CorrectTarget`: AI dancer targets an ally who has already acted.
    *   `// TEST: AI_Playthrough_BasicMapCompletion`: AI can successfully complete a simple map from start to finish using default aggressive profiles.

This specification provides a framework for a modular and testable AI system. The specific logic within each referenced assembly script (`aMovementAI...`, `aActionAI...`) from the original game would need to be reverse-engineered or reimplemented based on observed behavior and these defined script structures.