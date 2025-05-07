# 1. Map System Overview

## 1. Introduction

This document provides an overview of the core Map System implementation for the Fantasy Tactics game. The Map System is responsible for managing the game's spatial environment, including the structure of game maps, the properties of different terrain types, and the individual tiles that make up the map.

The core components of the Map System have been implemented and have successfully passed an initial suite of 64 automated tests, ensuring a stable foundation for further development.

## 2. Core Components and Classes

The Map System is built around several key classes that work together to define and manage game maps.

### 2.1. `TerrainType`

*   **Source**: [`src/map_system/terrain.py`](../../src/map_system/terrain.py:0)
*   **Description**: The `TerrainType` class defines the fundamental properties of a specific type of terrain. This includes:
    *   `name`: A human-readable name for the terrain (e.g., "Plains", "Forest", "Mountain").
    *   `movement_cost`: The cost for a standard unit to move through this terrain.
    *   `defense_bonus`: The defensive bonus a unit receives when standing on this terrain.
    *   `avoid_bonus`: The avoidance (dodge) bonus a unit receives.
    *   `vision_cost`: How much this terrain impedes line of sight (if applicable).
    *   `is_impassable`: A boolean indicating if units can enter this terrain at all.
    *   `graphics_id`: An identifier used by the rendering system to display the correct visuals for this terrain.
*   **Usage**: `TerrainType` objects are typically defined once and then referenced by `TileInstance` objects and `Tileset`s.

### 2.2. `Tileset`

*   **Source**: [`src/map_system/tileset.py`](../../src/map_system/tileset.py:0)
*   **Description**: The `Tileset` class acts as a collection or palette of `TerrainType`s that are used together to construct a map or a series of maps with a consistent theme (e.g., "Grassland Tileset", "Castle Interior Tileset").
*   **Key Responsibilities**:
    *   Manages a list of available `TerrainType`s.
    *   Provides a way to look up `TerrainType`s by name or ID.
    *   Can define default terrain types or other metadata relevant to the set.
*   **Usage**: A `Map` object will typically be associated with one or more `Tileset`s to define the types of terrain it can contain.

### 2.3. `TileInstance`

*   **Source**: [`src/map_system/tile.py`](../../src/map_system/tile.py:0)
*   **Description**: The `TileInstance` class represents a single, specific tile at a particular coordinate (X, Y) on a game map.
*   **Key Responsibilities**:
    *   Holds a reference to its `TerrainType`, which defines its base properties.
    *   Can store additional state specific to this individual tile, such as:
        *   Presence of special features (e.g., a chest, a breakable wall).
        *   Temporary effects (e.g., a magical ward).
        *   References to units or objects currently occupying the tile.
*   **Usage**: A `Map` is primarily composed of a 2D grid of `TileInstance` objects.

### 2.4. `Map`

*   **Source**: [`src/map_system/map.py`](../../src/map_system/map.py:0)
*   **Description**: The `Map` class is the central component that represents an entire game map or level.
*   **Key Responsibilities**:
    *   Stores the dimensions (width and height) of the map.
    *   Maintains a 2D grid (e.g., a list of lists) of `TileInstance` objects.
    *   Provides methods to access `TileInstance`s and their `TerrainType`s at specific coordinates (e.g., `get_tile(x, y)`, `get_terrain_type(x, y)`).
    *   Manages map-wide properties or metadata (e.g., map name, associated `Tileset`s, objective information).
    *   Interfaces with other systems, such as the Character System (for unit placement) and the AI System (for pathfinding data).
*   **Usage**: The `Map` object is the primary data structure used by the game engine to understand the current playable area.

## 3. Interactions and Data Flow

1.  **Initialization**: `TerrainType`s are defined. `Tileset`s are created, grouping various `TerrainType`s.
2.  **Map Loading**: A `Map` object is instantiated. Its grid is populated with `TileInstance`s. Each `TileInstance` is assigned a `TerrainType` (often looked up via the map's `Tileset`).
3.  **Gameplay**:
    *   The **Character System** queries the `Map` for `TerrainType` properties (e.g., movement cost) when units move.
    *   The **Combat System** queries the `Map` for defensive bonuses provided by the `TerrainType` of a `TileInstance`.
    *   The **AI System** uses data from the `Map` (traversability, movement costs) to perform pathfinding.
    *   The **UI System** reads `Map` data (tile graphics IDs from `TerrainType`s) to render the visual representation of the map.

## 4. Testing and Validation

The core Map System, encompassing the classes described above, has undergone initial testing. A suite of 64 automated tests has been successfully passed, covering functionalities such as:
*   Correct initialization of `TerrainType`, `Tileset`, `TileInstance`, and `Map` objects.
*   Accurate retrieval of terrain properties.
*   Proper functioning of map grid operations.
*   Basic pathfinding data provision.

This testing provides confidence in the stability and correctness of the implemented Map System.

## 5. Future Considerations

While the core system is in place, future enhancements could include:
*   Support for multi-layered tiles.
*   More complex tile interactions (e.g., destructible terrain).
*   Dynamic map changes triggered by events.
*   Integration with a map editor.