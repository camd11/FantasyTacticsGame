# Specification: Map System

This document outlines the data structures and functionalities for the map system in the Fire Emblem Thracia 776 recreation.

## 1. Core Concepts

*   **Map Grid**: Each game map is represented as a 2D grid of tiles. Based on [`FE5Tools/fe5py/maps.py:300`](FE5Tools/fe5py/maps.py:300), maps are typically 64x64 tiles.
*   **Tile**: The smallest unit of a map. Each tile is 8x8 pixels.
*   **Metatile**: A 2x2 block of tiles (16x16 pixels). Terrain data appears to be associated with metatiles. (Inferred from [`FE5Tools/fe5py/maps.py:138-143`](FE5Tools/fe5py/maps.py:138) and [`FE5Tools/fe5py/maps.py:161-168`](FE5Tools/fe5py/maps.py:161))
*   **Terrain Type**: Each tile (or metatile) has an associated terrain type that affects unit movement, combat, and other game mechanics.
*   **Tileset**: A collection of graphical tiles, their palettes, and configuration data used to render a map.

## 2. Data Structures

### 2.1. Map Data

```pseudocode
// Represents a single game map
CLASS Map
    // PROPERTIES
    STRING MapID // Unique identifier for the map (e.g., "Chapter1", "PrologueArena")
    INTEGER Width // Map width in tiles (e.g., 64)
    INTEGER Height // Map height in tiles (e.g., 64)
    ARRAY<ARRAY<TileInstance>> TileGrid // 2D array representing the map layout
    Tileset MapTileset // The tileset used for this map
    ARRAY<UnitPlacement> InitialUnitPlacements // Starting positions for player and enemy units
    ARRAY<Event> MapEvents // Scripted events for this map (e.g., reinforcements, dialogue triggers)
    STRING Objective // Description of the map's objective
    // TEST: Map dimensions must be positive integers
    // TEST: TileGrid dimensions must match Width and Height

    // METHODS
    CONSTRUCTOR(MapID, Width, Height, Tileset)
    FUNCTION GetTile(X, Y) RETURNS TileInstance // TEST: Returns correct tile for valid coordinates
    FUNCTION SetTile(X, Y, TileInstance) // TEST: Updates tile at valid coordinates
    FUNCTION IsValidCoordinate(X, Y) RETURNS BOOLEAN // TEST: Checks if coordinates are within map bounds
    FUNCTION GetTerrainType(X, Y) RETURNS TerrainType // TEST: Returns correct terrain for tile
END CLASS
```

### 2.2. Tile Instance Data

```pseudocode
// Represents a specific tile on the map grid
CLASS TileInstance
    // PROPERTIES
    INTEGER TileID // Index of the tile graphic within the tileset (derived from config data, e.g., [`FE5Tools/fe5py/maps.py:149-152`](FE5Tools/fe5py/maps.py:149))
    INTEGER PaletteID // Index of the palette used for this tile (e.g., [`FE5Tools/fe5py/maps.py:150`](FE5Tools/fe5py/maps.py:150))
    BOOLEAN HorizontalFlip // Whether the tile graphic is flipped horizontally (e.g., [`FE5Tools/fe5py/maps.py:154`](FE5Tools/fe5py/maps.py:154))
    BOOLEAN VerticalFlip // Whether the tile graphic is flipped vertically (e.g., [`FE5Tools/fe5py/maps.py:155`](FE5Tools/fe5py/maps.py:155))
    TerrainType Terrain // The terrain type of this tile (derived from metatile data, e.g., [`FE5Tools/fe5py/maps.py:163-168`](FE5Tools/fe5py/maps.py:163))
    // TEST: TileID and PaletteID must be valid for the associated MapTileset

    // METHODS
    CONSTRUCTOR(TileID, PaletteID, HorizontalFlip, VerticalFlip, Terrain)
END CLASS
```

### 2.3. Tileset Data

Inspired by [`FE5Tools/fe5py/maps.py:58-75`](FE5Tools/fe5py/maps.py:58)

```pseudocode
// Represents a collection of tiles and their properties for rendering maps
CLASS Tileset
    // PROPERTIES
    STRING TilesetID // Unique identifier for the tileset
    ARRAY<GraphicTile> Tiles // Array of individual graphical tiles (e.g., 8x8 pixel data)
    ARRAY<Palette> Palettes // Array of color palettes (each palette typically 16 colors)
    // Config data (metatile definitions, tile indices, flips) would be processed during map loading
    // to populate TileInstance objects on the Map.
    // TEST: All referenced TileIDs and PaletteIDs in a map must exist in its Tileset

    // METHODS
    CONSTRUCTOR(TilesetID)
    FUNCTION LoadFromSource(PathToData) // Loads tiles, palettes from source (e.g., .bin files or TMX)
                                      // TEST: Successfully loads valid tileset data
                                      // TEST: Handles errors for invalid or missing data
    FUNCTION GetTileGraphic(TileID, PaletteID, HFlip, VFlip) RETURNS ImageData // TEST: Returns correct image data
END CLASS

CLASS GraphicTile
    // PROPERTIES
    INTEGER BitDepth // e.g., 4 for 4bpp
    RAWDATA PixelData // Raw pixel data for an 8x8 tile
    // TEST: PixelData length must match expected size for BitDepth
END CLASS

CLASS Palette
    // PROPERTIES
    ARRAY<Color> Colors // Array of 16 Color objects
    // TEST: Palette must contain exactly 16 colors
END CLASS

CLASS Color
    // PROPERTIES
    INTEGER R, G, B, A // Red, Green, Blue, Alpha components
    // TEST: Color components must be within valid range (e.g., 0-255)
END CLASS
```

### 2.4. Terrain Type Data

Based on [`FE5Tools/fe5py/maps.py:11-55`](FE5Tools/fe5py/maps.py:11)

```pseudocode
// Represents a type of terrain and its properties
ENUM TerrainTypeID // Mapped from byte values like in terrain_types
    MapEdge = 0x00
    Peak = 0x01
    Thicket = 0x02
    Cliff = 0x03
    Plains = 0x04
    Forest = 0x05
    Sea = 0x06
    River = 0x07
    Mountain = 0x08
    Sand = 0x09
    Castle = 0x0A
    Fort = 0x0B
    House = 0x0C
    Gate = 0x0D
    // ... (include all from the source)
    Wasteland = 0x0F
    Bridge = 0x10
    Lake = 0x11
    Village = 0x12
    Ruins = 0x13
    // Unknown2 = 0x14 (handle unknowns appropriately)
    Supply = 0x16
    Church = 0x17
    ClosedHouse = 0x18
    Road = 0x19
    Armory = 0x1A
    Vendor = 0x1B
    Arena = 0x1C
    Floor = 0x1D
    IndoorImpassable = 0x1E
    Throne = 0x1F
    Door = 0x20
    IndoorChest = 0x21
    Exit = 0x22
    Pillar = 0x23
    Drawbridge = 0x24
    SecretShop = 0x25
    BreakableWall = 0x26
    SandySoil = 0x27 // "Sand y Soil"
    MagicFloor = 0x28
    MagicFloorCenter = 0x29
    ClosedChurch = 0x2A
    OutdoorChest = 0x2B
END ENUM

CLASS TerrainType
    // PROPERTIES
    TerrainTypeID ID
    STRING Name // User-friendly name (e.g., "Forest")
    INTEGER MovementCost[MovementType] // Movement cost for different unit movement types (e.g., Infantry, Flier)
                                       // TEST: MovementCost must be positive
    INTEGER DefenseBonus // Defense bonus granted by this terrain
    INTEGER AvoidBonus // Avoid bonus granted by this terrain
    BOOLEAN IsImpassable[MovementType] // Whether units of a certain movement type can enter
    BOOLEAN HealsUnits // Whether units recover HP on this terrain (e.g., Forts)
    // Other special properties (e.g., triggers events, shop access)
    // TEST: Name must not be empty

    // METHODS
    CONSTRUCTOR(ID, Name, MovementCosts, DefenseBonus, AvoidBonus, IsImpassableFlags, HealsUnits)
END CLASS
```

## 3. Map Loading and Initialization

1.  Read map configuration data (tile layout, flips, palettes per tile).
    *   // TEST: Ensure map configuration data is parsed correctly.
2.  Read tileset data (graphics, base palettes).
    *   // TEST: Ensure tileset graphics and palettes are loaded.
3.  For each tile position on the map:
    a.  Determine its `TileID`, `PaletteID`, `HorizontalFlip`, `VerticalFlip` from the map configuration.
    b.  Determine its `TerrainType` from the metatile terrain data associated with its location.
    c.  Create a `TileInstance` object.
    *   // TEST: TileInstances must be correctly initialized with graphical and terrain data.
4.  Populate `InitialUnitPlacements`.
    *   // TEST: Units must be placed at correct starting locations.
5.  Load `MapEvents`.
    *   // TEST: Map events must be loaded and triggerable.

## 4. TDD Anchors

*   `// TEST: Map_Load_ValidData`: Successfully loads a map with valid configuration and tileset data.
*   `// TEST: Map_Load_InvalidData`: Handles errors gracefully when map data is corrupt or missing.
*   `// TEST: Map_GetTile_ValidCoordinates`: `Map.GetTile(x,y)` returns the correct `TileInstance`.
*   `// TEST: Map_GetTile_InvalidCoordinates`: `Map.GetTile(x,y)` handles out-of-bounds requests (e.g., returns null or throws error).
*   `// TEST: Map_GetTerrainType_Correct`: `Map.GetTerrainType(x,y)` returns the correct `TerrainType` for a given tile.
*   `// TEST: TerrainType_Properties`: `TerrainType` objects have correct movement costs, bonuses, and flags.
*   `// TEST: Tileset_Load_Valid`: `Tileset.LoadFromSource()` correctly loads graphical tile and palette data.
*   `// TEST: Tileset_GetTileGraphic_Correct`: `Tileset.GetTileGraphic()` returns the correct visual data for a tile, considering palette and flips.
*   `// TEST: Map_UnitPlacement_Correct`: Units are placed at their designated starting positions on map load.
*   `// TEST: Map_EventTriggering_Basic`: A simple map event (e.g., turn-based) triggers correctly.

This provides a solid base for the map system. Next, I will investigate files related to characters.