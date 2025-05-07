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