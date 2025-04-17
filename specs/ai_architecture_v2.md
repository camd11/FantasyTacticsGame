# Two-Phase Goal-Oriented Utility AI Architecture

## 1. Overview and Justification

### 1.1 Core Concept

The Two-Phase Goal-Oriented Utility AI architecture represents an evolution of our previous utility-based approach, designed to address key limitations while maintaining computational efficiency. This architecture separates AI decision-making into two distinct phases:

1. **Strategic Goal Selection**: High-level decision-making that determines the AI's primary objective for the current turn
2. **Tactical Action Execution**: Low-level decision-making that determines the specific actions to achieve the selected goal

### 1.2 Justification for the New Approach

Our previous utility-based approach suffered from several limitations:

- **State Discrepancy Issues**: The AI would sometimes make decisions based on an incomplete or inconsistent view of the game state, leading to suboptimal or illogical actions
- **Tactical Myopia**: By evaluating all possible actions with a single utility function, the AI often made locally optimal but strategically poor decisions
- **Lack of Context Awareness**: The AI struggled to maintain consistent behavior across turns, often appearing erratic or indecisive
- **Computational Inefficiency**: Evaluating all possible action combinations led to exponential growth in decision space

The Two-Phase approach addresses these issues by:

- **Maintaining State Consistency**: By separating strategic and tactical decisions, we ensure each phase works with a consistent view of the game state
- **Enabling Strategic Planning**: The goal selection phase provides context for tactical decisions, ensuring actions align with broader objectives
- **Reducing Computational Complexity**: By pruning the decision space through goal selection before evaluating specific actions
- **Supporting Role-Based Behavior**: Goals can be weighted differently based on AI personas, creating more distinct and believable behavior patterns

## 2. Two-Phase Process

### 2.1 Phase 1: Strategic Goal Selection

In this phase, the AI evaluates potential high-level goals and selects the most appropriate one based on the current game state, unit capabilities, and AI persona.

#### Process Flow:

1. **Goal Enumeration**: Generate all valid goals for the current unit
2. **Strategic Evaluation**: Score each goal using weighted considerations specific to the unit's AI persona
3. **Goal Selection**: Choose the highest-scoring goal to pursue

#### Example Goals:

- `ELIMINATE_THREAT`: Focus on attacking and defeating a specific enemy unit
- `SUPPORT_ALLY`: Provide healing or buffs to a specific allied unit
- `SECURE_POSITION`: Move to and hold a strategically valuable location
- `RETREAT_AND_RECOVER`: Move to safety and use healing items if available
- `ADVANCE_TO_OBJECTIVE`: Move toward the primary mission objective

### 2.2 Phase 2: Tactical Action Execution

Once a strategic goal is selected, the AI identifies and evaluates specific actions that would accomplish this goal.

#### Process Flow:

1. **Action Space Pruning**: Generate only actions relevant to the selected goal
2. **Tactical Evaluation**: Score each action using goal-specific utility considerations
3. **Action Selection**: Choose the highest-scoring action to execute

#### Example Action Types:

- `Move + Attack`: Move to a position and attack an enemy
- `Move + Skill`: Move to a position and use a skill (healing, buff, etc.)
- `Move + Item`: Move to a position and use an item
- `Move + Wait`: Move to a position and end turn

## 3. Component Definitions

### 3.1 Goal Library

A collection of predefined strategic goals that AI units can pursue. Each goal includes:

- **Validity Function**: Determines if the goal is valid in the current game state
- **Relevance Scorers**: Evaluate how appropriate the goal is for the current situation
- **Action Generators**: Produce the set of actions that could fulfill this goal
- **Action Evaluators**: Specialized utility functions for scoring actions within this goal's context

```
GoalLibrary = {
    ELIMINATE_THREAT: {
        validity_fn: (unit, game_state) => boolean,
        relevance_scorers: [...],
        action_generators: [...],
        action_evaluators: [...]
    },
    SUPPORT_ALLY: { ... },
    ...
}
```

### 3.2 Strategic Evaluator

Responsible for scoring and selecting the most appropriate goal based on the current game state and AI persona.

**Key Components:**
- **Goal Scorer**: Evaluates each goal's relevance using weighted considerations
- **Persona Weights**: Different weights for each consideration based on AI persona
- **Selection Logic**: Deterministic selection of the highest-scoring goal (with tie-breaking)

### 3.3 Tactical Executor

Responsible for identifying, evaluating, and selecting specific actions to accomplish the chosen goal.

**Key Components:**
- **Action Generator**: Creates valid actions relevant to the current goal
- **Action Scorer**: Evaluates actions using goal-specific utility considerations
- **Execution Logic**: Translates the selected action into game commands

### 3.4 Utility Scorer

A modular system of scoring functions (considerations) used by both the Strategic Evaluator and Tactical Executor.

**Scorer Categories:**
- **Offensive**: DamageDealt, KillPotential, TargetPriority
- **Defensive**: SelfPreservation, DamageTaken, TerrainDefense
- **Positional**: TerrainBonus, ObjectiveProximity, AlliedFormation
- **Support**: HealAllyAmount, HealAllyPriority, BuffValue
- **Resource**: ItemUsedCost, SkillUsageEfficiency

### 3.5 State Manager

Ensures consistent state representation throughout the decision-making process.

**Key Responsibilities:**
- Captures a snapshot of the game state at the beginning of a unit's turn
- Provides methods for simulating potential actions without modifying the actual game state
- Maintains derived data (e.g., threat maps, ally status summaries) for efficient decision-making

## 4. AI Persona Integration

AI personas define the behavioral characteristics of different unit types through weighted preferences for different goals and considerations.

### 4.1 Core Personas

#### Aggressor
- **Primary Goals**: ELIMINATE_THREAT > ADVANCE_TO_OBJECTIVE > SECURE_POSITION
- **Key Weights**: High DamageDealt, KillPotential; Moderate SelfPreservation
- **Behavior Pattern**: Actively seeks combat, prioritizes defeating enemies over positioning

#### Defender
- **Primary Goals**: SECURE_POSITION > ELIMINATE_THREAT > SUPPORT_ALLY
- **Key Weights**: High SelfPreservation, TerrainBonus; Moderate DamageDealt
- **Behavior Pattern**: Holds strategic positions, engages enemies that approach

#### Support
- **Primary Goals**: SUPPORT_ALLY > RETREAT_AND_RECOVER > SECURE_POSITION
- **Key Weights**: High HealAllyAmount, BuffValue; High SelfPreservation
- **Behavior Pattern**: Prioritizes healing and buffing allies, avoids direct combat

#### Objective-Focused
- **Primary Goals**: ADVANCE_TO_OBJECTIVE > ELIMINATE_THREAT > SECURE_POSITION
- **Key Weights**: High ObjectiveProximity; Moderate DamageDealt, SelfPreservation
- **Behavior Pattern**: Moves toward objectives, only engages enemies that block progress

### 4.2 Persona Implementation

Personas are implemented as configuration files defining:
- Goal priority weights
- Consideration weights for strategic evaluation
- Consideration weights for tactical evaluation

```yaml
# Example persona definition (YAML format)
AGGRESSOR:
  goal_weights:
    ELIMINATE_THREAT: 1.0
    ADVANCE_TO_OBJECTIVE: 0.7
    SECURE_POSITION: 0.4
    RETREAT_AND_RECOVER: 0.3
    SUPPORT_ALLY: 0.2
  
  strategic_weights:
    ThreatLevel: 1.0
    KillOpportunity: 0.9
    ObjectiveProgress: 0.7
    # ...
  
  tactical_weights:
    DamageDealt: 1.0
    KillPotential: 0.9
    SelfPreservation: 0.6
    # ...
```

## 5. Implementation and Testing Plan

### 5.1 Implementation Phases

1. **Core Framework (Sprint 1)**
   - State Manager implementation
   - Basic Goal Library with 2-3 fundamental goals
   - Strategic Evaluator with simple scoring
   - Tactical Executor with basic action generation

2. **Expanded Capabilities (Sprint 2)**
   - Complete Goal Library implementation
   - Advanced scoring functions for both phases
   - Persona configuration system
   - Initial integration with game systems

3. **Refinement and Optimization (Sprint 3)**
   - Performance optimization
   - Behavior tuning and balancing
   - Debugging tools and visualization
   - Full game integration

### 5.2 Testing Strategy

#### Dedicated Test Maps

Create specialized test scenarios to validate specific AI behaviors:

1. **Combat Decision Test**: Simple map with varied enemy types to test target selection
2. **Positioning Test**: Map with strategic terrain features to test positional decision-making
3. **Support Logic Test**: Scenario with injured allies to test healing and buff priorities
4. **Objective Test**: Map with clear objectives to test goal-oriented behavior
5. **Full Integration Test**: Complex scenario combining all elements

#### Automated Testing Framework

Implement an automated testing system that:
- Runs AI vs. AI simulations on test maps
- Captures decision logs and outcome metrics
- Compares results against expected behavior patterns
- Identifies regressions or unexpected behaviors

#### Logging System

Implement a concise, configurable logging system:

```
# Default (Terse) Format
[U:5][GOAL:ELIMINATE_THREAT][ACT:MV(10,12)+ATK(U:12)]

# Detailed Format (Debug Mode)
[Unit:Knight_5][Turn:3]
  Selected Goal: ELIMINATE_THREAT(U:12) | Score: 0.85
    - ThreatLevel: 0.9 (w:1.0)
    - KillOpportunity: 0.8 (w:0.9)
    - ...
  Selected Action: MOVE(10,12)+ATTACK(U:12) | Score: 0.78
    - DamageDealt: 0.8 (w:1.0)
    - SelfPreservation: 0.7 (w:0.6)
    - ...
```

### 5.3 Performance Considerations

- **Action Space Pruning**: The two-phase approach naturally reduces the action space by filtering through goal relevance
- **Caching**: Cache pathfinding results and derived state data within a single unit's turn
- **Lazy Evaluation**: Only compute expensive metrics (like combat simulations) for high-potential actions
- **Parallel Processing**: Where possible, evaluate goals and actions in parallel

## 6. Conclusion

The Two-Phase Goal-Oriented Utility AI architecture provides a robust framework for creating believable, efficient, and testable AI behavior in our tactical RPG. By separating strategic goal selection from tactical action execution, we address the limitations of our previous approach while maintaining computational efficiency.

This architecture supports:
- Clear, role-based behavior through AI personas
- Consistent decision-making across turns
- Efficient evaluation of complex action spaces
- Straightforward testing and debugging

The implementation plan provides a clear path forward, with incremental development phases and comprehensive testing strategies to ensure the AI meets our gameplay and testing requirements.