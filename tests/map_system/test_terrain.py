import pytest
from enum import Enum

# Mock MovementType enum for testing purposes
class MockMovementType(Enum):
    INFANTRY = "Infantry"
    FLIER = "Flier"
    ARMORED = "Armored"
    CAVALRY = "Cavalry"

class TestTerrainTypeIDEnum:
    def test_terrain_type_id_exists_and_has_members(self):
        """Test that TerrainTypeID enum exists and has some expected values."""
        from src.map_system.terrain import TerrainTypeID # Fails if not exists
        
        assert hasattr(TerrainTypeID, "Plains")
        assert hasattr(TerrainTypeID, "Forest")
        assert hasattr(TerrainTypeID, "Peak")
        assert TerrainTypeID.Plains.value == 0x04 # Example value from spec
        assert TerrainTypeID.Forest.value == 0x05

    def test_all_terrain_type_ids_from_spec(self):
        """Test that all TerrainTypeID enum members from the spec exist and have correct values."""
        from src.map_system.terrain import TerrainTypeID

        # Based on docs/spec/01_MapSystem.md
        expected_terrain_ids = {
            "MapEdge": 0x00,
            "Peak": 0x01,
            "Thicket": 0x02,
            "Cliff": 0x03,
            "Plains": 0x04,
            "Forest": 0x05,
            "Sea": 0x06,
            "River": 0x07,
            "Mountain": 0x08,
            "Sand": 0x09,
            "Castle": 0x0A,
            "Fort": 0x0B,
            "House": 0x0C,
            "Gate": 0x0D,
            # "Unknown1": 0x0E, # Assuming Unknowns are not explicitly defined as named members
            "Wasteland": 0x0F,
            "Bridge": 0x10,
            "Lake": 0x11,
            "Village": 0x12,
            "Ruins": 0x13,
            # "Unknown2": 0x14,
            # "Unknown3": 0x15,
            "Supply": 0x16,
            "Church": 0x17,
            "ClosedHouse": 0x18,
            "Road": 0x19,
            "Armory": 0x1A,
            "Vendor": 0x1B,
            "Arena": 0x1C,
            "Floor": 0x1D,
            "IndoorImpassable": 0x1E,
            "Throne": 0x1F,
            "Door": 0x20,
            "IndoorChest": 0x21,
            "Exit": 0x22,
            "Pillar": 0x23,
            "Drawbridge": 0x24,
            "SecretShop": 0x25,
            "BreakableWall": 0x26,
            "SandySoil": 0x27,
            "MagicFloor": 0x28,
            "MagicFloorCenter": 0x29,
            "ClosedChurch": 0x2A,
            "OutdoorChest": 0x2B,
        }

        for name, value in expected_terrain_ids.items():
            assert hasattr(TerrainTypeID, name), f"TerrainTypeID missing member {name}"
            assert getattr(TerrainTypeID, name).value == value, \
                f"TerrainTypeID.{name} has value {getattr(TerrainTypeID, name).value}, expected {value}"

class TestTerrainTypeCreation:
    @pytest.fixture
    def sample_movement_costs(self):
        return {
            MockMovementType.INFANTRY: 1,
            MockMovementType.FLIER: 1,
            MockMovementType.ARMORED: 2,
            MockMovementType.CAVALRY: 1,
        }

    @pytest.fixture
    def sample_impassable_flags(self):
        return {
            MockMovementType.INFANTRY: False,
            MockMovementType.FLIER: False,
            MockMovementType.ARMORED: False,
            MockMovementType.CAVALRY: False,
        }

    def test_terrain_type_creation_valid(self, sample_movement_costs, sample_impassable_flags):
        """Test creating a TerrainType with valid properties."""
        from src.map_system.terrain import TerrainType, TerrainTypeID

        terrain_id = TerrainTypeID.Forest
        name = "Deep Forest"
        defense_bonus = 2
        avoid_bonus = 20
        heals_units = False

        terrain = TerrainType(
            terrain_id=terrain_id,
            name=name,
            movement_costs=sample_movement_costs,
            defense_bonus=defense_bonus,
            avoid_bonus=avoid_bonus,
            is_impassable=sample_impassable_flags,
            heals_units=heals_units
        )

        assert terrain.id == terrain_id
        assert terrain.name == name
        assert terrain.movement_costs == sample_movement_costs
        assert terrain.defense_bonus == defense_bonus
        assert terrain.avoid_bonus == avoid_bonus
        assert terrain.is_impassable == sample_impassable_flags
        assert terrain.heals_units == heals_units

    def test_terrain_type_creation_empty_name(self, sample_movement_costs, sample_impassable_flags):
        """TEST: Name must not be empty."""
        from src.map_system.terrain import TerrainType, TerrainTypeID
        with pytest.raises(ValueError, match="TerrainType name cannot be empty"):
            TerrainType(
                terrain_id=TerrainTypeID.Plains,
                name="",
                movement_costs=sample_movement_costs,
                defense_bonus=0,
                avoid_bonus=0,
                is_impassable=sample_impassable_flags,
                heals_units=False
            )

    def test_terrain_type_creation_non_positive_movement_cost(self, sample_impassable_flags):
        """TEST: MovementCost must be positive."""
        from src.map_system.terrain import TerrainType, TerrainTypeID
        
        invalid_costs_zero = {MockMovementType.INFANTRY: 0, MockMovementType.FLIER: 1}
        invalid_costs_negative = {MockMovementType.INFANTRY: -1, MockMovementType.FLIER: 1}

        with pytest.raises(ValueError, match=r"Movement cost for .* must be a positive integer"):
            TerrainType(
                terrain_id=TerrainTypeID.Plains,
                name="Bad Plains",
                movement_costs=invalid_costs_zero,
                defense_bonus=0,
                avoid_bonus=0,
                is_impassable=sample_impassable_flags,
                heals_units=False
            )
        
        with pytest.raises(ValueError, match=r"Movement cost for .* must be a positive integer"):
            TerrainType(
                terrain_id=TerrainTypeID.Plains,
                name="Worse Plains",
                movement_costs=invalid_costs_negative,
                defense_bonus=0,
                avoid_bonus=0,
                is_impassable=sample_impassable_flags,
                heals_units=False
            )

    def test_terrain_type_properties_defaults_if_applicable(self, sample_movement_costs, sample_impassable_flags):
        """Test that properties are correctly assigned (focus on a typical case)."""
        from src.map_system.terrain import TerrainType, TerrainTypeID
        
        fort_terrain = TerrainType(
            terrain_id=TerrainTypeID.Fort, # Assuming Fort exists in TerrainTypeID
            name="Fort",
            movement_costs=sample_movement_costs,
            defense_bonus=3,
            avoid_bonus=30,
            is_impassable=sample_impassable_flags,
            heals_units=True
        )
        assert fort_terrain.id == TerrainTypeID.Fort
        assert fort_terrain.name == "Fort"
        assert fort_terrain.defense_bonus == 3
        assert fort_terrain.avoid_bonus == 30
        assert fort_terrain.heals_units is True
        assert fort_terrain.movement_costs[MockMovementType.INFANTRY] == 1

class TestGlobalTerrainRegistry:
    def test_terrain_registry_accessible_and_contains_known_types(self):
        """
        TEST: A global registry of TerrainTypes must be accessible.
        Tests if a global registry (e.g., TERRAIN_REGISTRY) exists in the terrain module
        and contains instances of TerrainType for known TerrainTypeIDs.
        """
        from src.map_system.terrain import TerrainTypeID, TerrainType
        # Attempt to import a hypothetical registry. This will fail if it doesn't exist.
        from src.map_system.terrain import TERRAIN_REGISTRY

        assert TERRAIN_REGISTRY is not None, "TERRAIN_REGISTRY should exist."
        assert isinstance(TERRAIN_REGISTRY, dict), "TERRAIN_REGISTRY should be a dictionary."

        # Check for a few key terrain types
        # Ensure these names match what would be loaded/defined for the registry
        expected_terrains_to_check = {
            TerrainTypeID.Plains: "Plains",
            TerrainTypeID.Forest: "Forest",
            TerrainTypeID.Peak: "Peak"
        }

        for terrain_id_enum, expected_name in expected_terrains_to_check.items():
            assert terrain_id_enum in TERRAIN_REGISTRY, f"{expected_name} ({terrain_id_enum}) should be in the registry."
            terrain_instance = TERRAIN_REGISTRY[terrain_id_enum]
            assert isinstance(terrain_instance, TerrainType), \
                f"Registry entry for {expected_name} should be a TerrainType instance."
            assert terrain_instance.name == expected_name, \
                f"Terrain instance for {terrain_id_enum} should have name '{expected_name}'."
            assert terrain_instance.id == terrain_id_enum, \
                f"Terrain instance for {terrain_id_enum} should have matching ID."