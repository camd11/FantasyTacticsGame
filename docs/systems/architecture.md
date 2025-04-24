# System Architecture

This document provides an overview of the Fantasy Tactics Game architecture, showing how the major systems interact.

## High-Level Architecture

```
┌─────────────────────────────────────┐
│               Game                  │
│                                     │
│  ┌──────────┐       ┌──────────┐    │
│  │   UI     │◄──────►  Engine  │    │
│  └──────────┘       └────┬─────┘    │
│       ▲                  │          │
│       │                  ▼          │
│  ┌────┴─────┐      ┌───────────┐    │
│  │ Renderer │◄─────┤Game State │    │
│  └──────────┘      └─────┬─────┘    │
│                          │          │
│                          ▼          │
│  ┌──────────┐      ┌───────────┐    │
│  │   AI     │◄─────┤  Systems  │    │
│  └──────────┘      └───────────┘    │
└─────────────────────────────────────┘
```

## Core Components

### Game Engine (`src/core_engine/`)

The central controller that manages the game loop, updates, and coordinates between subsystems.

- **GameEngine**: Main game loop, system coordination
- **GameStateManager**: Maintains the central game state
- **EventSystem**: Dispatches game events between systems
- **PhaseManager**: Controls game turn phases

### Game State (`src/core_engine/game_state.py`)

The authoritative representation of the current game state.

- **GameState**: Top-level state container
- **MapState**: Map layout, terrain, and positions
- **UnitState**: Unit stats, position, and status
- **ObjectState**: Map objects and interactable elements

### Systems (`src/gameplay_systems/`)

Specialized subsystems that implement game mechanics.

- **MovementSystem**: Handles unit movement and pathfinding
- **CombatSystem**: Manages attacks and damage calculation
- **SkillSystem**: Processes special abilities and effects
- **ItemSystem**: Handles inventory and item usage
- **EnvironmentSystem**: Controls terrain effects and interactions
- **TurnSystem**: Manages turn order and execution

### AI (`src/gameplay_systems/ai/`)

Artificial intelligence that controls non-player units.

- **AIManager**: Orchestrates AI decision making
- **StrategicEvaluator**: Selects high-level goals
- **TacticalExecutor**: Determines specific actions
- **Goals**: Defines strategic objectives (attack, heal, etc.)
- **AILogger**: Records AI decision making for analysis

### UI (`src/ui/`)

User interface components and screens.

- **UIManager**: Controls active UI elements
- **Views**: Screen-specific UI layouts
- **InputManager**: Processes user input
- **UIEventSystem**: Handles UI-specific events

### Renderer (`src/renderer/`)

Visual representation of the game.

- **GameRenderer**: Manages rendering pipeline
- **SpriteManager**: Handles sprite loading and animation
- **TileRenderer**: Renders map tiles and overlays
- **UnitRenderer**: Renders units and their animations
- **EffectRenderer**: Handles visual effects

## Flow of Control

### Game Initialization

1. **GameEngine** initializes
2. **GameStateManager** loads initial state
3. **Systems** are registered with the engine
4. **UIManager** sets up initial UI
5. **Renderer** initializes display

### Game Loop

1. **GameEngine** orchestrates update cycle
2. **InputManager** processes user input
3. **ActiveSystem** (based on phase) updates game state
4. **EventSystem** dispatches state changes
5. **UIManager** updates UI based on state
6. **Renderer** draws updated state

### AI Turn Processing

1. **TurnSystem** determines AI unit to act
2. **AIManager** activates for unit
3. **StrategicEvaluator** selects goal
4. **TacticalExecutor** determines action
5. **ActionSystem** executes the action
6. **GameStateManager** updates state
7. **EventSystem** notifies systems of changes

## System Interactions

### State Modification Path

```
[User Input/AI] → ActionSystem → Gameplay System → GameStateManager → EventSystem → [UI/Renderer]
```

### Data Flow

```
┌───────────┐     ┌───────────┐      ┌────────────┐
│ Data Files│────►│ GameState │─────►│ Systems    │
└───────────┘     └───────────┘      └────────────┘
                       │                    │
                       ▼                    ▼
                  ┌────────┐          ┌────────┐
                  │ AI     │◄─────────┤ UI     │
                  └────────┘          └────────┘
```

## Testing Architecture

The testing architecture mirrors the system architecture but uses specialized test fixtures:

1. **Mechanic Tests**: Focus on individual gameplay systems using direct API calls
2. **Visual Tests**: Use the renderer to verify visual components
3. **AI Tests**: Validate AI decision making using specialized scenarios

## Implementation Notes

- **Loose Coupling**: Systems communicate primarily through the EventSystem
- **Single Source of Truth**: GameStateManager is the authoritative state representation
- **Composition Over Inheritance**: Game entities are composed of multiple components
- **Command Pattern**: Actions are represented as command objects with execute methods
- **Observer Pattern**: Systems observe state changes through the EventSystem 