from enum import Enum
from typing import Dict, Any # Using Any for MovementType for now

# Placeholder for actual MovementType enum if defined elsewhere
# from ..character_system.movement import MovementType # Example path
# For now, tests use a MockMovementType or direct string/enum keys.

class TerrainTypeID(Enum):
    """
    Unique identifiers for various terrain types in the game.

    These values are typically mapped from byte values found in game data files,
    as referenced in `FE5Tools/fe5py/maps.py`.

    Attributes:
        MapEdge: Edge of the map, usually impassable.
        Peak: Impassable mountain peak.
        Thicket: Dense vegetation, hinders movement.
        Cliff: Impassable cliff face.
        Plains: Open, flat land with standard movement cost.
        Forest: Wooded area, offers defensive bonuses and hinders some units.
        Sea: Large body of water, typically only passable by fliers or specific units.
        River: Waterway, may be passable with high movement cost or by fliers.
        Mountain: Difficult terrain, high movement cost.
        Sand: Sandy area, hinders mounted units.
        Castle: Fortified structure, often an objective or defensive point.
        Fort: Defensive structure, often provides healing and bonuses.
        House: Building, may be visitable for items or information.
        Gate: Entrance to a castle or fortified area.
        Wasteland: Barren land.
        Bridge: Structure spanning a river or chasm.
        Lake: Body of water, smaller than a sea.
        Village: Settlement, often visitable.
        Ruins: Dilapidated structures.
        Supply: Supply point or tent.
        Church: Religious building, may have special properties or be visitable.
        ClosedHouse: A house that cannot be entered.
        Road: Paved path, may reduce movement cost.
        Armory: Shop selling weapons.
        Vendor: Shop selling general items.
        Arena: Location for units to fight for experience and money.
        Floor: Standard indoor flooring.
        IndoorImpassable: Impassable terrain within an indoor setting.
        Throne: Special tile, often an objective for seizure.
        Door: Entrance/exit within a structure, may be openable.
        IndoorChest: Chest located indoors.
        Exit: Point to leave an indoor map or area.
        Pillar: Obstruction, typically impassable.
        Drawbridge: A bridge that can be raised or lowered.
        SecretShop: Hidden shop with rare items.
        BreakableWall: Wall that can be destroyed.
        SandySoil: Specific type of soil, possibly with unique properties.
        MagicFloor: Floor tile with magical properties or effects.
        MagicFloorCenter: Central part of a magic floor formation.
        ClosedChurch: A church that cannot be entered.
        OutdoorChest: Chest located outdoors.
    """
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
    # Unknown1 = 0x0E (Spec does not list 0x0E, FE5Tools/fe5py/maps.py has "Unknown1")
    Wasteland = 0x0F
    Bridge = 0x10
    Lake = 0x11
    Village = 0x12 # Spec: Village, FE5Tools: Village (Closed)
    Ruins = 0x13
    # Unknown2 = 0x14 (Spec: Unknown2, FE5Tools: "Unknown2")
    # Unknown3 = 0x15 (Spec does not list 0x15, FE5Tools: "Unknown3")
    Supply = 0x16
    Church = 0x17
    ClosedHouse = 0x18 # Spec: ClosedHouse, FE5Tools: Village (Closed) - assuming spec is primary for now
    Road = 0x19
    Armory = 0x1A
    Vendor = 0x1B
    Arena = 0x1C
    Floor = 0x1D
    IndoorImpassable = 0x1E # Spec: IndoorImpassable, FE5Tools: Wall (Indoor)
    Throne = 0x1F
    Door = 0x20
    IndoorChest = 0x21 # Spec: IndoorChest, FE5Tools: Chest (Indoor)
    Exit = 0x22 # Spec: Exit, FE5Tools: Stairs
    Pillar = 0x23
    Drawbridge = 0x24
    SecretShop = 0x25
    BreakableWall = 0x26 # Spec: BreakableWall, FE5Tools: Wall (Breakable)
    SandySoil = 0x27
    MagicFloor = 0x28
    MagicFloorCenter = 0x29
    ClosedChurch = 0x2A
    OutdoorChest = 0x2B # Spec: OutdoorChest, FE5Tools: Chest (Outdoor)

class TerrainType:
    """
    Represents a type of terrain and its associated game properties.

    As per spec `docs/spec/01_MapSystem.md#24-terrain-type-data`:
    CLASS TerrainType
        PROPERTIES
            TerrainTypeID ID
            STRING Name
            INTEGER MovementCost[MovementType]
            INTEGER DefenseBonus
            INTEGER AvoidBonus
            BOOLEAN IsImpassable[MovementType]
            BOOLEAN HealsUnits
        METHODS
            CONSTRUCTOR(ID, Name, MovementCosts, DefenseBonus, AvoidBonus, IsImpassableFlags, HealsUnits)
    """
    def __init__(self,
                 terrain_id: TerrainTypeID,
                 name: str,
                 movement_costs: Dict[Any, int], # Key: MovementType enum member (currently Any)
                 defense_bonus: int,
                 avoid_bonus: int,
                 is_impassable: Dict[Any, bool], # Key: MovementType enum member (currently Any)
                 heals_units: bool):
        """
        Initializes a TerrainType object.

        Args:
            terrain_id: The unique TerrainTypeID for this terrain.
            name: User-friendly name of the terrain (e.g., "Forest").
            movement_costs: A dictionary mapping MovementType to an integer movement cost.
                            Costs must be positive.
            defense_bonus: Integer defense bonus granted by this terrain.
            avoid_bonus: Integer avoid bonus granted by this terrain.
            is_impassable: A dictionary mapping MovementType to a boolean,
                           indicating if the terrain is impassable for that type.
            heals_units: Boolean indicating if units recover HP on this terrain.

        Raises:
            TypeError: If input arguments are of incorrect types.
            ValueError: If name is empty, or movement costs are not positive.
        """
        if not isinstance(terrain_id, TerrainTypeID):
            raise TypeError("terrain_id must be an instance of TerrainTypeID.")
        if not isinstance(name, str):
            raise TypeError("name must be a string.")
        if not name:
            raise ValueError("TerrainType name cannot be empty.")
        
        if not isinstance(movement_costs, dict):
            raise TypeError("movement_costs must be a dictionary.")
        for move_type, cost in movement_costs.items():
            # MovementType itself is not strictly validated here, as it's 'Any'
            if not isinstance(cost, int) or cost <= 0:
                raise ValueError(f"Movement cost for {move_type} must be a positive integer, got {cost}.")

        if not isinstance(defense_bonus, int):
            raise TypeError("defense_bonus must be an integer.")
        if not isinstance(avoid_bonus, int):
            raise TypeError("avoid_bonus must be an integer.")

        if not isinstance(is_impassable, dict):
            raise TypeError("is_impassable must be a dictionary.")
        for move_type, impassable_flag in is_impassable.items():
            # MovementType itself is not strictly validated here
            if not isinstance(impassable_flag, bool):
                raise TypeError(f"is_impassable flag for {move_type} must be a boolean, got {impassable_flag}.")

        if not isinstance(heals_units, bool):
            raise TypeError("heals_units must be a boolean.")

        self.id: TerrainTypeID = terrain_id
        self.name: str = name
        # Note: MovementType is currently 'Any'. When defined, keys should be validated against it.
        self.movement_costs: Dict[Any, int] = movement_costs
        self.defense_bonus: int = defense_bonus
        self.avoid_bonus: int = avoid_bonus
        self.is_impassable: Dict[Any, bool] = is_impassable
        self.heals_units: bool = heals_units

    def __repr__(self) -> str:
        return (f"TerrainType(id={self.id.name}, name='{self.name}', "
                f"costs={len(self.movement_costs)}, def={self.defense_bonus}, avo={self.avoid_bonus}, "
                f"impassable_count={sum(self.is_impassable.values())}, heals={self.heals_units})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TerrainType):
            return NotImplemented
        return (self.id == other.id and
                self.name == other.name and
                self.movement_costs == other.movement_costs and
                self.defense_bonus == other.defense_bonus and
                self.avoid_bonus == other.avoid_bonus and
                self.is_impassable == other.is_impassable and
                self.heals_units == other.heals_units)

# Global Terrain Registry
# As per spec: "// TEST: A global registry of TerrainTypes must be accessible."
# This registry would typically be populated from game data files.
# For now, we'll pre-populate a few common types for testing and basic functionality.

TERRAIN_REGISTRY: Dict[TerrainTypeID, TerrainType] = {}

def _populate_default_terrain_types():
    """Helper function to populate the TERRAIN_REGISTRY with some defaults."""
    
    # Define some generic movement costs and impassable flags for default population
    # Using string keys as MovementType enum is not yet integrated here.
    default_movement_costs = {
        "Infantry": 1, "Armored": 1, "Cavalry": 1, "Flier": 1
    }
    default_is_impassable = {
        "Infantry": False, "Armored": False, "Cavalry": False, "Flier": False
    }
    peak_is_impassable = {
        "Infantry": True, "Armored": True, "Cavalry": True, "Flier": False # Fliers can pass peaks
    }


    TERRAIN_REGISTRY[TerrainTypeID.Plains] = TerrainType(
        terrain_id=TerrainTypeID.Plains,
        name="Plains",
        movement_costs=default_movement_costs.copy(), # Use copy to avoid shared dict modification
        defense_bonus=0,
        avoid_bonus=0,
        is_impassable=default_is_impassable.copy(),
        heals_units=False
    )

    TERRAIN_REGISTRY[TerrainTypeID.Forest] = TerrainType(
        terrain_id=TerrainTypeID.Forest,
        name="Forest",
        movement_costs={**default_movement_costs, "Infantry": 1, "Cavalry": 2}, # Example: Cavalry slower in forest
        defense_bonus=1,
        avoid_bonus=20,
        is_impassable=default_is_impassable.copy(),
        heals_units=False
    )

    TERRAIN_REGISTRY[TerrainTypeID.Peak] = TerrainType(
        terrain_id=TerrainTypeID.Peak,
        name="Peak",
        movement_costs=default_movement_costs.copy(), # Movement cost is high, but handled by impassable usually
        defense_bonus=0, # Or could be high if somehow occupied
        avoid_bonus=0,
        is_impassable=peak_is_impassable.copy(),
        heals_units=False
    )
    
    # Add other terrain types as needed or load them from data.
    # For the test to pass, Plains, Forest, and Peak are required.

_populate_default_terrain_types()