# Specification: AI System

This document outlines the data structures and functionalities for the Artificial Intelligence (AI) system controlling enemy and Non-Player Character (NPC) units in the Fire Emblem Thracia 776 recreation. The AI must be capable of playing through levels for testing purposes.

## 1. Core Concepts

*   **AI Behavior**: A set of rules and priorities that dictate a unit's actions and movements.
*   **AI Script**: A predefined sequence of logic or a set of conditions that an AI unit follows. Thracia 776 uses distinct scripts for movement and actions, as seen in [`MovementAIPointers.csv`](FireEmblem5/TABLES/MovementAIPointers.csv:0) and [`ActionAIPointers.csv`](FireEmblem5/TABLES/ActionAIPointers.csv:0).
*   **AI Personality/Role**: Units can be assigned different AI behaviors based on their class, role (e.g., attacker, healer, thief), or specific chapter events.
*   **Targeting Priority**: Rules that determine which enemy unit an AI will prioritize attacking or interacting with.
*   **Movement Strategy**: Rules that determine how an AI unit will position itself on the map.
*   **Threat Assessment**: AI's evaluation of danger from player units and advantageous positions.
*   **Objective-Driven Behavior**: AI may have specific objectives beyond combat, such as reaching a location, protecting another unit, or using an item on a tile.

## 2. AI Architecture

The AI system will be modular, consisting of:

1.  **AI Controller**: Manages the AI turn, iterating through active AI units.
2.  **Unit AI Component**: Attached to each AI-controlled `UnitInstance`, holding its assigned movement and action AI script IDs.
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
    // Optional: Targeting parameters, specific unit IDs to prioritize/ignore
    // TEST: MovementScriptID and ActionScriptID must be valid script IDs.

    // METHODS
    CONSTRUCTOR(AssignmentID, MovementScriptID, ActionScriptID)
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
FUNCTION ExecuteMovementScript(UnitInstance, MovementAIScriptID, MapData, PlayerUnits, AIUnits) RETURNS TargetCoordinates
    // LOGIC based on MovementAIScriptID
    // - Calculate pathfinding using A* or similar algorithm.
    // - Evaluate terrain costs and safety.
    // TEST: AI unit selects a valid and logical move based on its script.
    // TEST: AI pathfinding correctly navigates terrain.
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
    Ignore_SpecificUnits // Example: ActionAI_IgnoreLeif_Identifier
    Force_HealSelfOrAlly // Example: ActionAI_ForceHeal_Identifier
    // ... other specific scripts from the CSV
END ENUM

// Each script would be a function or a set of rules:
FUNCTION ExecuteActionScript(UnitInstance, ActionAIScriptID, MapData, PlayerUnits, AIUnits) RETURNS AIAction
    // LOGIC based on ActionAIScriptID
    // - Evaluate potential targets for attacks or staff uses.
    // - Prioritize actions based on script goals.
    // TEST: AI unit selects a valid and logical action based on its script.
    // TEST: AI correctly prioritizes targets or support actions.
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
    a.  Retrieve the unit's `MovementAIScriptID`.
    b.  Execute the corresponding movement script, considering:
        i.  Unit's movement range.
        ii. Terrain.
        iii.Position of player units (threats, targets).
        iv. Position of other AI units (allies, objectives).
        v.  Script-specific goals (e.g., flee, reach point, guard area).
    c.  Move the unit to the chosen `TargetCoordinates`.
    *   // TEST: AI unit moves to a tactically sound position.

2.  **Action Phase**:
    a.  Retrieve the unit's `ActionAIScriptID`.
    b.  Execute the corresponding action script, considering:
        i.  Available weapons, staves, items.
        ii. Reachable targets from the new position.
        iii.Health of allies and enemies.
        iv. Script-specific goals (e.g., attack lord, heal ally, steal).
    c.  Execute the chosen `AIAction`.
    *   // TEST: AI unit performs a tactically sound action.

## 5. Key AI Behaviors to Implement (based on CSVs and common FE patterns)

*   **Aggressive Attacker**: Moves to engage and attack the most suitable target (based on damage output, kill potential, or specific target priority like "Lord").
*   **Defensive/Stationary**: Holds a position, attacks enemies that come into range. May prioritize targets threatening a guarded unit or location.
*   **Healer/Support**: Prioritizes healing injured allies or using support staves. Will try to stay out of direct danger.
*   **Thief/Objective Rusher**: Prioritizes moving towards chests, doors, villages, or escape points, often avoiding combat unless necessary.
*   **Dancer/Bard**: Moves to use "Dance" or "Play" on an allied unit that has already acted.
*   **Fleeing Unit**: Moves away from threats, especially when at low HP.
*   **Specific Target Focus**: AI that ignores certain units or prioritizes others (e.g., "Ignore Leif", "Target Lord").
*   **Group Tactics**: Units that coordinate, such as staying near a leader or forming a defensive line. (More advanced, but `MovementAI_StayWithFred_Identifier` hints at this).

## 6. AI for Testing

For the requirement "AI should be able to play levels for testing":
*   The AI must be robust enough to make valid moves and actions consistently.
*   A "Default Aggressive" AI profile (e.g., `MovementAI_Pursue_Identifier` + `ActionAI_IgnoreNone_Identifier`) can be assigned to all enemy units for basic playthrough testing.
*   The AI should be able to complete simple map objectives like "defeat all enemies" or "defeat boss".
*   More complex objectives (e.g., seize throne, escape) will require more sophisticated AI scripts.
    *   // TEST: AI can complete a simple "Defeat All Enemies" map.
    *   // TEST: AI can complete a simple "Defeat Boss" map.
    *   // TEST: AI units use a variety of their available actions (attack, staff if applicable).

## 7. TDD Anchors

*   `// TEST: AI_Movement_PursueTarget`: AI unit correctly moves towards the nearest/designated target.
*   `// TEST: AI_Movement_Stationary`: Stationary AI unit does not move from its position.
*   `// TEST: AI_Movement_Flee`: Low HP AI unit moves away from threats.
*   `// TEST: AI_Movement_PathfindingObstacles`: AI correctly navigates around obstacles.
*   `// TEST: AI_Action_AttackOptimalTarget`: AI selects and attacks the most strategically advantageous target.
*   `// TEST: AI_Action_HealAlly`: AI healer correctly identifies and heals a wounded ally.
*   `// TEST: AI_Action_NoActionWhenAppropriate`: AI correctly chooses to "Wait" if no beneficial action is available.
*   `// TEST: AI_Targeting_LordFocus`: AI with "Target Lord" script prioritizes attacking Leif.
*   `// TEST: AI_Targeting_IgnoreSpecific`: AI with "Ignore X" script does not target X.
*   `// TEST: AI_Objective_ReachPoint`: AI thief moves towards a designated chest/exit.
*   `// TEST: AI_Playthrough_BasicMapCompletion`: AI can successfully complete a simple map from start to finish.
*   `// TEST: AI_StaffUsage_CorrectTargetAndEffect`: AI uses staves (e.g., Silence, Sleep) on appropriate enemy targets.
*   `// TEST: AI_Dance_CorrectTarget`: AI dancer targets an ally who has already acted.

This specification provides a framework for a modular and testable AI system. The specific logic within each referenced assembly script (`aMovementAI...`, `aActionAI...`) would need to be reverse-engineered or reimplemented based on observed behavior in the original game.