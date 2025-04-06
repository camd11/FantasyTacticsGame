import unittest
from unittest.mock import MagicMock, patch, call
from typing import Dict, List, Tuple, Optional, Any

# Import the classes to be tested
from src.core_engine.game_state import (
    GameStateManager, GameState, MapState, UnitState, ItemInstance, StatusEffectInstance,
    FactionEnum, PhaseEnum, StatusEffectEnum, DispositionEnum, ObjectStateEnum,
    LEIF_ID, CHAPTER_8_ID, FATIGUE_COMBAT
)
from src.core_engine.data_provider import (
    DataProvider, TerrainTypeEnum, MovementTypeEnum
)

class TestGameStateManager(unittest.TestCase):
    """Test cases for the GameStateManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock DataProvider
        self.mock_data_provider = MagicMock(spec=DataProvider)
        
        # Create the GameStateManager with the mock DataProvider
        self.game_state_manager = GameStateManager(self.mock_data_provider)

    # TDD Anchor: Test loading map data populates terrain_grid and dimensions (Spec Line 167)
    def test_load_map_populates_terrain_grid_and_dimensions(self):
        """Test that load_map correctly initializes a new game state with map data."""
        # Create mock map data
        mock_map_data = MagicMock()
        mock_map_data.id = "CH1"
        mock_map_data.dimensions = (10, 8)
        mock_map_data.terrain_grid = [
            [TerrainTypeEnum.PLAIN for _ in range(10)] for _ in range(8)
        ]
        
        # Call the method under test
        self.game_state_manager.load_map(mock_map_data)
        
        # Assertions
        self.assertIsNotNone(self.game_state_manager.current_game_state)
        self.assertEqual(self.game_state_manager.current_game_state.chapter_id, "CH1")
        self.assertEqual(self.game_state_manager.current_game_state.map_state.map_id, "CH1")
        self.assertEqual(self.game_state_manager.current_game_state.map_state.dimensions, (10, 8))
        self.assertEqual(len(self.game_state_manager.current_game_state.map_state.terrain_grid), 8)
        self.assertEqual(len(self.game_state_manager.current_game_state.map_state.terrain_grid[0]), 10)
        self.assertEqual(self.game_state_manager.current_game_state.map_state.unit_positions, {})
        self.assertEqual(self.game_state_manager.current_game_state.map_state.object_states, {})
        self.assertEqual(self.game_state_manager.current_game_state.unit_states, {})
        self.assertEqual(self.game_state_manager.current_game_state.event_flags, {})

    # TDD Anchor: Test deploying units creates UnitState objects with correct initial data (Spec Line 181)
    def test_deploy_units_creates_unit_states_with_correct_data(self):
        """Test that deploy_units correctly creates UnitState objects with the right initial data."""
        # First, load a map to initialize the game state
        mock_map_data = MagicMock()
        mock_map_data.id = "CH1"
        mock_map_data.dimensions = (10, 8)
        mock_map_data.terrain_grid = [
            [TerrainTypeEnum.PLAIN for _ in range(10)] for _ in range(8)
        ]
        self.game_state_manager.load_map(mock_map_data)
        
        # Create mock unit placements
        mock_unit_placement = MagicMock()
        mock_unit_placement.unit_id = "LEIF"
        mock_unit_placement.faction = FactionEnum.PLAYER
        mock_unit_placement.position = (2, 3)
        mock_unit_placement.level = 5
        mock_unit_placement.start_inventory = ["IRON_SWORD", "VULNERARY"]
        mock_unit_placement.starting_fatigue = 0
        mock_unit_placement.needs_autolevel = False
        mock_unit_placement.target_level = 5
        
        # Create mock unit base data
        mock_base_data = MagicMock()
        mock_base_data.name = "Leif"
        mock_base_data.class_id = "LORD"
        mock_base_data.stats = {"HP": 20, "STR": 5, "MAG": 2, "SKL": 6, "SPD": 7, "LUK": 4, "DEF": 4, "CON": 5, "MOV": 5}
        mock_base_data.growths = {"HP": 70, "STR": 35, "MAG": 15, "SKL": 40, "SPD": 45, "LUK": 30, "DEF": 25}
        mock_base_data.base_weapon_ranks = {"SWORD": "C", "LANCE": "E"}
        mock_base_data.leadership_stars = 2
        mock_base_data.pcc = 1
        
        # Create mock item data
        mock_iron_sword = MagicMock()
        mock_iron_sword.max_durability = 46
        
        mock_vulnerary = MagicMock()
        mock_vulnerary.max_durability = 3
        
        # Configure mock data provider
        self.mock_data_provider.get_unit_base_data.return_value = mock_base_data
        self.mock_data_provider.get_item_data.side_effect = lambda item_id: {
            "IRON_SWORD": mock_iron_sword,
            "VULNERARY": mock_vulnerary
        }.get(item_id)
        self.mock_data_provider.get_support_partners.return_value = [{"partner_id": "FINN", "bonus": 5}]
        
        # Mock the _find_initial_equipped_weapon method
        self.game_state_manager._find_initial_equipped_weapon = MagicMock(return_value=0)
        
        # Call the method under test
        self.game_state_manager.deploy_units([mock_unit_placement], self.mock_data_provider)
        
        # Assertions
        self.assertIn("LEIF", self.game_state_manager.current_game_state.unit_states)
        unit = self.game_state_manager.current_game_state.unit_states["LEIF"]
        
        # Check unit properties
        self.assertEqual(unit.id, "LEIF")
        self.assertEqual(unit.name, "Leif")
        self.assertEqual(unit.class_id, "LORD")
        self.assertEqual(unit.faction, FactionEnum.PLAYER)
        self.assertEqual(unit.position, (2, 3))
        self.assertEqual(unit.current_hp, 20)
        self.assertEqual(unit.max_hp, 20)
        self.assertEqual(unit.base_stats, mock_base_data.stats)
        self.assertEqual(unit.growth_rates, mock_base_data.growths)
        self.assertEqual(unit.level, 5)
        self.assertEqual(unit.experience, 0)
        
        # Check inventory
        self.assertEqual(len(unit.inventory), 2)
        self.assertEqual(unit.inventory[0].item_id, "IRON_SWORD")
        self.assertEqual(unit.inventory[0].current_durability, 46)
        self.assertEqual(unit.inventory[1].item_id, "VULNERARY")
        self.assertEqual(unit.inventory[1].current_durability, 3)
        self.assertEqual(unit.equipped_weapon_index, 0)
        
        # Check weapon ranks and other properties
        self.assertEqual(unit.weapon_ranks, {"SWORD": "C", "LANCE": "E"})
        self.assertEqual(unit.weapon_exp, {"SWORD": 0, "LANCE": 0})
        self.assertEqual(unit.current_fatigue, 0)
        self.assertEqual(unit.status_effects, [])
        self.assertFalse(unit.has_moved)
        self.assertFalse(unit.has_acted)
        self.assertEqual(unit.support_partner_ids, [{"partner_id": "FINN", "bonus": 5}])
        self.assertEqual(unit.leadership_stars, 2)
        self.assertEqual(unit.pcc, 1)
        self.assertFalse(unit.is_captured)
        self.assertIsNone(unit.carrying_unit_id)
        self.assertEqual(unit.disposition, DispositionEnum.ACTIVE)
        
        # Check unit position is registered in map state
        self.assertEqual(self.game_state_manager.current_game_state.map_state.unit_positions["LEIF"], (2, 3))
        
        # Verify method calls
        self.mock_data_provider.get_unit_base_data.assert_called_once_with("LEIF")
        self.mock_data_provider.get_item_data.assert_any_call("IRON_SWORD")
        self.mock_data_provider.get_item_data.assert_any_call("VULNERARY")
        self.mock_data_provider.get_support_partners.assert_called_once_with("LEIF")
        self.game_state_manager._find_initial_equipped_weapon.assert_called_once()

    # TDD Anchor: Test get_unit returns correct UnitState object (Spec Line 235)
    def test_get_unit_returns_correct_unit_state(self):
        """Test that get_unit returns the correct UnitState object."""
        # First, load a map and deploy a unit
        self._setup_game_state_with_units()
        
        # Call the method under test
        unit = self.game_state_manager.get_unit("LEIF")
        
        # Assertions
        self.assertIsNotNone(unit)
        self.assertEqual(unit.id, "LEIF")
        self.assertEqual(unit.name, "Leif")
        
        # Test with non-existent unit
        unit = self.game_state_manager.get_unit("NONEXISTENT")
        self.assertIsNone(unit)
        
        # Test with no game state
        self.game_state_manager.current_game_state = None
        unit = self.game_state_manager.get_unit("LEIF")
        self.assertIsNone(unit)

    # TDD Anchor: Test get_units_by_faction returns correct list of units (Spec Line 239)
    def test_get_units_by_faction_returns_correct_units(self):
        """Test that get_units_by_faction returns the correct list of units."""
        # First, load a map and deploy units of different factions
        self._setup_game_state_with_units()
        
        # Call the method under test
        player_units = self.game_state_manager.get_units_by_faction(FactionEnum.PLAYER)
        enemy_units = self.game_state_manager.get_units_by_faction(FactionEnum.ENEMY)
        npc_units = self.game_state_manager.get_units_by_faction(FactionEnum.NPC)
        
        # Assertions
        self.assertEqual(len(player_units), 2)  # We have both Leif and Finn as player units
        self.assertTrue(any(unit.id == "LEIF" for unit in player_units))
        self.assertTrue(any(unit.id == "FINN" for unit in player_units))
        
        self.assertEqual(len(enemy_units), 1)
        self.assertEqual(enemy_units[0].id, "ENEMY1")
        
        self.assertEqual(len(npc_units), 1)
        self.assertEqual(npc_units[0].id, "NPC1")
        
        # Test with no game state
        self.game_state_manager.current_game_state = None
        units = self.game_state_manager.get_units_by_faction(FactionEnum.PLAYER)
        self.assertEqual(units, [])
        
        # Test with inactive units
        self._setup_game_state_with_units()
        # Mark both player units as dead
        self.game_state_manager.current_game_state.unit_states["LEIF"].disposition = DispositionEnum.DEAD
        self.game_state_manager.current_game_state.unit_states["FINN"].disposition = DispositionEnum.DEAD
        player_units = self.game_state_manager.get_units_by_faction(FactionEnum.PLAYER)
        self.assertEqual(len(player_units), 0, "Should return no player units when all are inactive")

    # TDD Anchor: Test get_terrain_type returns correct type for a coordinate (Spec Line 248)
    def test_get_terrain_type_returns_correct_type(self):
        """Test that get_terrain_type returns the correct terrain type for a coordinate."""
        # Create a map with different terrain types
        mock_map_data = MagicMock()
        mock_map_data.id = "CH1"
        mock_map_data.dimensions = (3, 3)
        mock_map_data.terrain_grid = [
            [TerrainTypeEnum.PLAIN, TerrainTypeEnum.FOREST, TerrainTypeEnum.MOUNTAIN],
            [TerrainTypeEnum.RIVER, TerrainTypeEnum.BRIDGE, TerrainTypeEnum.ROAD],
            [TerrainTypeEnum.WALL, TerrainTypeEnum.DOOR, TerrainTypeEnum.HOUSE]
        ]
        self.game_state_manager.load_map(mock_map_data)
        
        # Call the method under test for different coordinates
        terrain_00 = self.game_state_manager.get_terrain_type((0, 0))
        terrain_12 = self.game_state_manager.get_terrain_type((1, 2))
        terrain_21 = self.game_state_manager.get_terrain_type((2, 1))
        
        # Assertions
        self.assertEqual(terrain_00, TerrainTypeEnum.PLAIN)
        self.assertEqual(terrain_12, TerrainTypeEnum.DOOR)
        self.assertEqual(terrain_21, TerrainTypeEnum.ROAD)
        
        # Test with out-of-bounds coordinates
        terrain_invalid = self.game_state_manager.get_terrain_type((5, 5))
        self.assertEqual(terrain_invalid, TerrainTypeEnum.INVALID)
        
        # Test with no game state
        self.game_state_manager.current_game_state = None
        terrain = self.game_state_manager.get_terrain_type((0, 0))
        self.assertEqual(terrain, TerrainTypeEnum.INVALID)

    # TDD Anchor: Test is_unit_fatigued_for_deployment checks fatigue vs max HP (Spec Line 283)
    def test_is_unit_fatigued_for_deployment(self):
        """Test that is_unit_fatigued_for_deployment correctly checks fatigue against max HP."""
        # First, load a map and deploy units
        self._setup_game_state_with_units()
        
        # Set up test conditions
        leif = self.game_state_manager.current_game_state.unit_states["LEIF"]
        finn = self.game_state_manager.current_game_state.unit_states["FINN"]
        
        # Set fatigue levels
        leif.current_fatigue = 25  # Above max_hp (20)
        finn.current_fatigue = 15  # Below max_hp (25)
        
        # Set chapter ID to trigger fatigue checks
        self.game_state_manager.current_game_state.chapter_id = CHAPTER_8_ID
        
        # Call the method under test
        leif_fatigued = self.game_state_manager.is_unit_fatigued_for_deployment("LEIF")
        finn_fatigued = self.game_state_manager.is_unit_fatigued_for_deployment("FINN")
        
        # Assertions
        self.assertFalse(leif_fatigued, "Leif should never be fatigued regardless of fatigue level")
        self.assertFalse(finn_fatigued, "Finn should not be fatigued as his fatigue is below max HP")
        
        # Increase Finn's fatigue above max HP
        finn.current_fatigue = 30  # Above max_hp (25)
        finn_fatigued = self.game_state_manager.is_unit_fatigued_for_deployment("FINN")
        self.assertTrue(finn_fatigued, "Finn should be fatigued as his fatigue is above max HP")
        
        # Test with chapter before fatigue is implemented
        self.game_state_manager.current_game_state.chapter_id = "CH1"
        finn_fatigued = self.game_state_manager.is_unit_fatigued_for_deployment("FINN")
        self.assertFalse(finn_fatigued, "No units should be fatigued before Chapter 8")
        
        # Test with non-existent unit
        fatigued = self.game_state_manager.is_unit_fatigued_for_deployment("NONEXISTENT")
        self.assertFalse(fatigued, "Non-existent unit should not be considered fatigued")
        
        # Test with no game state
        self.game_state_manager.current_game_state = None
        fatigued = self.game_state_manager.is_unit_fatigued_for_deployment("LEIF")
        self.assertFalse(fatigued, "Should return False when no game state exists")

    # TDD Anchor: Test move_unit updates unit position and map state (Spec Line 294)
    def test_move_unit_updates_position_and_map_state(self):
        """Test that move_unit correctly updates the unit's position and the map state."""
        # First, load a map and deploy units
        self._setup_game_state_with_units()
        
        # Get initial position
        leif = self.game_state_manager.current_game_state.unit_states["LEIF"]
        initial_position = leif.position
        
        # Call the method under test
        result = self.game_state_manager.move_unit("LEIF", (5, 5))
        
        # Assertions
        self.assertTrue(result, "move_unit should return True on success")
        self.assertEqual(leif.position, (5, 5), "Unit position should be updated")
        self.assertEqual(
            self.game_state_manager.current_game_state.map_state.unit_positions["LEIF"], 
            (5, 5), 
            "Map state unit position should be updated"
        )
        
        # Test with non-existent unit
        result = self.game_state_manager.move_unit("NONEXISTENT", (7, 7))
        self.assertFalse(result, "move_unit should return False for non-existent unit")
        
        # Test with no game state
        self.game_state_manager.current_game_state = None
        result = self.game_state_manager.move_unit("LEIF", (7, 7))
        self.assertFalse(result, "move_unit should return False when no game state exists")

    # TDD Anchor: Test apply_damage reduces HP correctly, handles death/capture state (Spec Line 304)
    def test_apply_damage_reduces_hp_and_handles_death(self):
        """Test that apply_damage correctly reduces HP and handles death/capture state."""
        # First, load a map and deploy units
        self._setup_game_state_with_units()
        
        # Get initial HP
        leif = self.game_state_manager.current_game_state.unit_states["LEIF"]
        initial_hp = leif.current_hp
        
        # Call the method under test with damage less than current HP
        result = self.game_state_manager.apply_damage("LEIF", 5)
        
        # Assertions
        self.assertTrue(result, "apply_damage should return True on success")
        self.assertEqual(leif.current_hp, initial_hp - 5, "HP should be reduced by damage amount")
        self.assertEqual(leif.disposition, DispositionEnum.ACTIVE, "Unit should remain active")
        
        # Call the method with damage that reduces HP to 0
        result = self.game_state_manager.apply_damage("LEIF", leif.current_hp)
        
        # Assertions
        self.assertTrue(result, "apply_damage should return True on success")
        self.assertEqual(leif.current_hp, 0, "HP should be reduced to 0")
        self.assertEqual(leif.disposition, DispositionEnum.DEAD, "Unit should be marked as dead")
        self.assertNotIn("LEIF", self.game_state_manager.current_game_state.map_state.unit_positions, 
                        "Unit should be removed from map positions")
        
        # Test capture attempt
        self._setup_game_state_with_units()  # Reset the game state
        enemy = self.game_state_manager.current_game_state.unit_states["ENEMY1"]
        result = self.game_state_manager.apply_damage("ENEMY1", enemy.current_hp, is_capture_attempt=True)
        
        # Assertions
        self.assertTrue(result, "apply_damage should return True on success")
        self.assertEqual(enemy.current_hp, 0, "HP should be reduced to 0")
        self.assertEqual(enemy.disposition, DispositionEnum.CAPTURED_BY_ENEMY, "Unit should be marked as captured")
        
        # Test with non-existent unit
        result = self.game_state_manager.apply_damage("NONEXISTENT", 5)
        self.assertFalse(result, "apply_damage should return False for non-existent unit")
        
        # Test with no game state
        self.game_state_manager.current_game_state = None
        result = self.game_state_manager.apply_damage("LEIF", 5)
        self.assertFalse(result, "apply_damage should return False when no game state exists")

    # TDD Anchor: Test apply_healing increases HP correctly, respects max HP (Spec Line 321)
    def test_apply_healing_increases_hp_respects_max_hp(self):
        """Test that apply_healing correctly increases HP and respects max HP."""
        # First, load a map and deploy units
        self._setup_game_state_with_units()
        
        # Reduce HP first
        leif = self.game_state_manager.current_game_state.unit_states["LEIF"]
        leif.current_hp = 10  # Assuming max_hp is 20
        
        # Call the method under test
        result = self.game_state_manager.apply_healing("LEIF", 5)
        
        # Assertions
        self.assertTrue(result, "apply_healing should return True on success")
        self.assertEqual(leif.current_hp, 15, "HP should be increased by healing amount")
        
        # Test healing beyond max HP
        result = self.game_state_manager.apply_healing("LEIF", 10)
        
        # Assertions
        self.assertTrue(result, "apply_healing should return True on success")
        self.assertEqual(leif.current_hp, leif.max_hp, "HP should not exceed max HP")
        
        # Test with non-existent unit
        result = self.game_state_manager.apply_healing("NONEXISTENT", 5)
        self.assertFalse(result, "apply_healing should return False for non-existent unit")
        
        # Test with no game state
        self.game_state_manager.current_game_state = None
        result = self.game_state_manager.apply_healing("LEIF", 5)
        self.assertFalse(result, "apply_healing should return False when no game state exists")

    # TDD Anchor: Test update_fatigue increases fatigue correctly (Spec Line 341)
    def test_update_fatigue_increases_fatigue_correctly(self):
        """Test that update_fatigue correctly increases a unit's fatigue."""
        # First, load a map and deploy units
        self._setup_game_state_with_units()
        
        # Get initial fatigue
        leif = self.game_state_manager.current_game_state.unit_states["LEIF"]
        initial_fatigue = leif.current_fatigue
        
        # Call the method under test
        result = self.game_state_manager.update_fatigue("LEIF", FATIGUE_COMBAT)
        
        # Assertions
        self.assertTrue(result, "update_fatigue should return True on success")
        self.assertEqual(leif.current_fatigue, initial_fatigue + FATIGUE_COMBAT, 
                        "Fatigue should be increased by the specified amount")
        
        # Test with non-existent unit
        result = self.game_state_manager.update_fatigue("NONEXISTENT", FATIGUE_COMBAT)
        self.assertFalse(result, "update_fatigue should return False for non-existent unit")
        
        # Test with no game state
        self.game_state_manager.current_game_state = None
        result = self.game_state_manager.update_fatigue("LEIF", FATIGUE_COMBAT)
        self.assertFalse(result, "update_fatigue should return False when no game state exists")

    # Helper method to set up a game state with units for testing
    def _setup_game_state_with_units(self):
        """Set up a game state with units for testing."""
        # Create a map
        mock_map_data = MagicMock()
        mock_map_data.id = "CH1"
        mock_map_data.dimensions = (10, 8)
        mock_map_data.terrain_grid = [
            [TerrainTypeEnum.PLAIN for _ in range(10)] for _ in range(8)
        ]
        self.game_state_manager.load_map(mock_map_data)
        
        # Create units
        leif = UnitState()
        leif.id = "LEIF"
        leif.name = "Leif"
        leif.class_id = "LORD"
        leif.faction = FactionEnum.PLAYER
        leif.position = (2, 3)
        leif.current_hp = 20
        leif.max_hp = 20
        leif.current_fatigue = 0
        leif.disposition = DispositionEnum.ACTIVE
        
        finn = UnitState()
        finn.id = "FINN"
        finn.name = "Finn"
        finn.class_id = "PALADIN"
        finn.faction = FactionEnum.PLAYER
        finn.position = (3, 3)
        finn.current_hp = 25
        finn.max_hp = 25
        finn.current_fatigue = 0
        finn.disposition = DispositionEnum.ACTIVE
        
        enemy = UnitState()
        enemy.id = "ENEMY1"
        enemy.name = "Enemy Soldier"
        enemy.class_id = "SOLDIER"
        enemy.faction = FactionEnum.ENEMY
        enemy.position = (5, 5)
        enemy.current_hp = 15
        enemy.max_hp = 15
        enemy.disposition = DispositionEnum.ACTIVE
        
        npc = UnitState()
        npc.id = "NPC1"
        npc.name = "Villager"
        npc.class_id = "CIVILIAN"
        npc.faction = FactionEnum.NPC
        npc.position = (7, 7)
        npc.current_hp = 10
        npc.max_hp = 10
        npc.disposition = DispositionEnum.ACTIVE
        
        # Add units to game state
        self.game_state_manager.current_game_state.unit_states = {
            "LEIF": leif,
            "FINN": finn,
            "ENEMY1": enemy,
            "NPC1": npc
        }
        
        # Update unit positions in map state
        self.game_state_manager.current_game_state.map_state.unit_positions = {
            "LEIF": (2, 3),
            "FINN": (3, 3),
            "ENEMY1": (5, 5),
            "NPC1": (7, 7)
        }


if __name__ == '__main__':
    unittest.main()