"""
Test for Ballista System

This test verifies that the ballista system correctly handles ballista mechanics,
including data loading, usage conditions, targeting, combat calculations, durability,
and action costs.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call

# Import necessary modules
from src.fantasy_tactics_core.game_state import GameStateManager
from src.fantasy_tactics_core.data_provider import DataProvider, ItemTypeEnum, WeaponTypeEnum
from src.fantasy_tactics_gameplay.systems.map_system import MapSystem
from src.fantasy_tactics_gameplay.combat.combat_system import CombatSystem
from src.fantasy_tactics_gameplay.systems.action_system import ActionSystem
from src.fantasy_tactics_gameplay.systems.unit_system import UnitSystem
from src.fantasy_tactics_gameplay.systems.ballista_system import BallistaSystem, BallistaInstance, BallistaUserState

class TestBallistaSystem:
    """Test cases for the ballista system."""

    @pytest.fixture
    def setup_game_components(self):
        """Set up the game components needed for testing."""
        # Initialize components with proper specs
        data_provider = Mock(spec=DataProvider)
        game_state_manager = Mock(spec=GameStateManager)
        unit_system = Mock(spec=UnitSystem)
        map_system = Mock(spec=MapSystem)
        map_system.current_map = Mock()
        map_system.get_los_checker = Mock(return_value=Mock())
        
        # Create a comprehensive combat system mock with all required methods
        combat_system = Mock(spec=CombatSystem)
        combat_system.display_hit_effect = Mock()
        combat_system.display_miss_effect = Mock()
        combat_system.execute_standard_combat_round = Mock()
        combat_system.get_effectiveness_multiplier = Mock(return_value=1.0)
        combat_system.get_combat_stat_bonuses = Mock(return_value=0)
        combat_system.calculate_defense = Mock(return_value=3)
        combat_system.calculate_avoid = Mock(return_value=0)
        combat_system.calculate_crit_evade = Mock(return_value=0)
        combat_system.can_counter = Mock(return_value=False)
        combat_system.handle_unit_defeated = Mock()
        
        action_system = Mock(spec=ActionSystem)
        action_system.mark_unit_action_complete = Mock()
        
        inventory_system = Mock()
        
        # Set up default behaviors for common methods
        game_state_manager.apply_damage = Mock()
        unit_system.get_unit = Mock()
        unit_system.get_units_on_tiles = Mock(return_value=[])
        unit_system.are_hostile = Mock(return_value=False)
        map_system.distance = Mock(return_value=8)
        map_system.has_line_of_sight = Mock(return_value=True)
        map_system.calculate_tiles_in_range = Mock(return_value=set())
        map_system.get_all_objects_of_type = Mock(return_value=[])
        
        # Create an actual BallistaSystem instance
        ballista_system = BallistaSystem()
        ballista_system.initialize(
            game_state_manager,
            data_provider,
            map_system,
            unit_system,
            combat_system,
            action_system,
            inventory_system
        )
        
        return {
            "data_provider": data_provider,
            "game_state_manager": game_state_manager,
            "unit_system": unit_system,
            "map_system": map_system,
            "combat_system": combat_system,
            "action_system": action_system,
            "inventory_system": inventory_system,
            "ballista_system": ballista_system
        }
    
    @pytest.fixture
    def setup_test_data(self):
        """Set up test data for units, ballista types, and map objects."""
        # Create mock units with all necessary methods and attributes
        archer_unit = self._create_mock_unit(
            id="ARCHER_UNIT",
            name="Archer",
            position=(5, 5),
            class_id="ARCHER",
            faction="PLAYER",
            stats={"skl": 8, "luk": 6, "current_hp": 20},
            is_flying=False
        )
        
        knight_unit = self._create_mock_unit(
            id="KNIGHT_UNIT",
            name="Knight",
            position=(7, 7),
            class_id="KNIGHT",
            faction="PLAYER",
            stats={"skl": 5, "luk": 4, "current_hp": 25},
            is_flying=False
        )
        
        pegasus_unit = self._create_mock_unit(
            id="PEGASUS_UNIT",
            name="Pegasus Knight",
            position=(10, 10),
            class_id="PEGASUS_KNIGHT",
            faction="ENEMY",
            stats={"skl": 7, "luk": 8, "current_hp": 18, "defense": 5},
            is_flying=True
        )
        
        enemy_archer = self._create_mock_unit(
            id="ENEMY_ARCHER",
            name="Enemy Archer",
            position=(12, 12),
            class_id="ARCHER",
            faction="ENEMY",
            stats={"skl": 6, "luk": 5, "current_hp": 15, "defense": 3},
            is_flying=False
        )
        
        # Create mock ballista types
        regular_ballista_type = self._create_mock_ballista_type(
            id="BALLISTA_REGULAR",
            display_name="Ballista",
            weapon_id="BALLISTA_WEAPON_REGULAR",
            allowed_classes=["ARCHER", "SNIPER"]
        )
        
        iron_ballista_type = self._create_mock_ballista_type(
            id="BALLISTA_IRON",
            display_name="Iron Ballista",
            weapon_id="BALLISTA_WEAPON_IRON",
            allowed_classes=["ARCHER", "SNIPER"]
        )
        
        killer_ballista_type = self._create_mock_ballista_type(
            id="BALLISTA_KILLER",
            display_name="Killer Ballista",
            weapon_id="BALLISTA_WEAPON_KILLER",
            allowed_classes=["ARCHER", "SNIPER"]
        )
        
        # Create mock ballista weapons
        regular_ballista_weapon = self._create_mock_ballista_weapon(
            id="BALLISTA_WEAPON_REGULAR",
            might=8,
            hit=70,
            crit=0,
            min_range=3,
            max_range=10,
            durability=5,
            effectiveness={"IS_FLYING": 3.0}
        )
        
        iron_ballista_weapon = self._create_mock_ballista_weapon(
            id="BALLISTA_WEAPON_IRON",
            might=10,
            hit=60,
            crit=0,
            min_range=3,
            max_range=15,
            durability=3,
            effectiveness={"IS_FLYING": 3.0}
        )
        
        killer_ballista_weapon = self._create_mock_ballista_weapon(
            id="BALLISTA_WEAPON_KILLER",
            might=6,
            hit=65,
            crit=30,
            min_range=3,
            max_range=8,
            durability=3,
            effectiveness={"IS_FLYING": 3.0}
        )
        
        # Create ballista instances using the actual class
        regular_ballista_instance = BallistaInstance(
            position=(5, 5),
            ballista_type_id="BALLISTA_REGULAR",
            current_durability=5
        )
        regular_ballista_instance.id = "BALLISTA_INSTANCE_1"
        
        iron_ballista_instance = BallistaInstance(
            position=(8, 8),
            ballista_type_id="BALLISTA_IRON",
            current_durability=3
        )
        iron_ballista_instance.id = "BALLISTA_INSTANCE_2"
        
        killer_ballista_instance = BallistaInstance(
            position=(12, 5),
            ballista_type_id="BALLISTA_KILLER",
            current_durability=0
        )
        killer_ballista_instance.id = "BALLISTA_INSTANCE_3"
        killer_ballista_instance.is_enabled = False
        
        return {
            "units": {
                "archer_unit": archer_unit,
                "knight_unit": knight_unit,
                "pegasus_unit": pegasus_unit,
                "enemy_archer": enemy_archer
            },
            "ballista_types": {
                "regular": regular_ballista_type,
                "iron": iron_ballista_type,
                "killer": killer_ballista_type
            },
            "ballista_weapons": {
                "regular": regular_ballista_weapon,
                "iron": iron_ballista_weapon,
                "killer": killer_ballista_weapon
            },
            "ballista_instances": {
                "regular": regular_ballista_instance,
                "iron": iron_ballista_instance,
                "killer": killer_ballista_instance
            }
        }
    
    def _create_mock_unit(self, id, name, position, class_id, faction, stats, is_flying):
        """Helper method to create a mock unit with consistent attributes."""
        unit = Mock()
        unit.id = id
        unit.name = name
        unit.position = position
        unit.class_id = class_id
        unit.faction = faction
        
        # Create stats object
        unit.stats = MagicMock()
        for stat_name, stat_value in stats.items():
            setattr(unit.stats, stat_name, stat_value)
        
        # Set up common methods
        unit.is_attackable = MagicMock(return_value=True)
        unit.add_component = Mock()
        unit.set_immobile = Mock()
        unit.has_property = MagicMock(side_effect=lambda prop: prop == "IS_FLYING" and is_flying)
        
        return unit
    
    def _create_mock_ballista_type(self, id, display_name, weapon_id, allowed_classes):
        """Helper method to create a mock ballista type."""
        ballista_type = Mock()
        ballista_type.id = id
        ballista_type.display_name = display_name
        ballista_type.sprite_id = f"{id.lower()}_sprite"
        ballista_type.occupied_sprite_id = f"{id.lower()}_occupied_sprite"
        ballista_type.weapon_id = weapon_id
        ballista_type.allowed_classes = allowed_classes
        return ballista_type
    
    def _create_mock_ballista_weapon(self, id, might, hit, crit, min_range, max_range, durability, effectiveness):
        """Helper method to create a mock ballista weapon."""
        weapon = Mock()
        weapon.id = id
        weapon.might = might
        weapon.hit = hit
        weapon.crit = crit
        weapon.min_range = min_range
        weapon.max_range = max_range
        weapon.durability = durability
        weapon.effectiveness = effectiveness
        return weapon
    
    def _create_combat_preview(self, attacker_id, defender_id, ballista_id, damage=5, hit=80, crit=0, can_counter=False):
        """Helper method to create a consistent combat preview object."""
        return {
            "attacker_unit_id": attacker_id,
            "defender_unit_id": defender_id,
            "ballista_instance_id": ballista_id,
            "attacker_potential_dmg": damage,
            "attacker_hit": hit,
            "attacker_crit": crit,
            "can_defender_counter": can_counter
        }
    
    # Test Ballista Data Loading
    def test_ballista_type_data_validation(self, setup_game_components, setup_test_data):
        """Test that ballista type data is loaded and validated correctly."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        
        # Configure mocks
        ballista_system.get_ballista_type = Mock(return_value=regular_ballista_type)
        
        # Act
        result = ballista_system.validate_ballista_type("BALLISTA_REGULAR")
        
        # Assert
        assert result is True, "Valid ballista type should pass validation"
        ballista_system.get_ballista_type.assert_called_once_with("BALLISTA_REGULAR")
        
        # Test with invalid data (missing required fields)
        invalid_ballista_type = Mock()
        invalid_ballista_type.id = "BALLISTA_INVALID"
        invalid_ballista_type.display_name = "Invalid Ballista"
        invalid_ballista_type.sprite_id = "invalid_ballista_sprite"
        invalid_ballista_type.weapon_id = None
        invalid_ballista_type.allowed_classes = []
        
        ballista_system.get_ballista_type.return_value = invalid_ballista_type
        
        # Act
        result = ballista_system.validate_ballista_type("BALLISTA_INVALID")
        
        # Assert
        assert result is False, "Invalid ballista type should fail validation"
    
    def test_ballista_weapon_data_validation(self, setup_game_components, setup_test_data):
        """Test that ballista weapon data is loaded and validated correctly."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        
        # Configure mocks
        ballista_system.get_ballista_weapon = Mock(return_value=regular_ballista_weapon)
        
        # Act
        result = ballista_system.validate_ballista_weapon("BALLISTA_WEAPON_REGULAR")
        
        # Assert
        assert result is True, "Valid ballista weapon should pass validation"
        ballista_system.get_ballista_weapon.assert_called_once_with("BALLISTA_WEAPON_REGULAR")
        
        # Test with invalid data (min_range > max_range)
        invalid_ballista_weapon = self._create_mock_ballista_weapon(
            id="BALLISTA_WEAPON_INVALID",
            might=8,
            hit=70,
            crit=0,
            min_range=10,  # Invalid: min > max
            max_range=5,
            durability=5,
            effectiveness={}
        )
        
        ballista_system.get_ballista_weapon.return_value = invalid_ballista_weapon
        
        # Act
        result = ballista_system.validate_ballista_weapon("BALLISTA_WEAPON_INVALID")
        
        # Assert
        assert result is False, "Ballista weapon with min_range > max_range should fail validation"
    
    # Test Usage Conditions
    def test_check_unit_can_use_ballista(self, setup_game_components, setup_test_data):
        """Test that check_unit_can_use_ballista works correctly for different cases."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        knight_unit = setup_test_data["units"]["knight_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        
        # Configure mocks
        ballista_system.get_ballista_type = Mock(return_value=regular_ballista_type)
        
        # Test with allowed class
        result = ballista_system.check_unit_can_use_ballista(archer_unit, regular_ballista_instance)
        assert result is True, "Archer should be able to use ballista"
        
        # Test with disallowed class
        result = ballista_system.check_unit_can_use_ballista(knight_unit, regular_ballista_instance)
        assert result is False, "Knight should not be able to use ballista"
        
        # Test with null inputs
        result = ballista_system.check_unit_can_use_ballista(None, regular_ballista_instance)
        assert result is False, "Null unit should not be able to use ballista"
        
        result = ballista_system.check_unit_can_use_ballista(archer_unit, None)
        assert result is False, "Unit should not be able to use null ballista"
    
    def test_get_ballista_attack_range(self, setup_game_components, setup_test_data):
        """Test that get_ballista_attack_range works correctly."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        
        # Configure mocks
        ballista_system.get_ballista_type = Mock(return_value=regular_ballista_type)
        ballista_system.get_ballista_weapon = Mock(return_value=regular_ballista_weapon)
        
        # Mock map_system.calculate_tiles_in_range
        expected_tiles = {
            (2, 5), (3, 5), (4, 5), (6, 5), (7, 5), (8, 5),
            (5, 2), (5, 3), (5, 4), (5, 6), (5, 7), (5, 8)
        }
        map_system.calculate_tiles_in_range.return_value = expected_tiles
        
        # Act
        result = ballista_system.get_ballista_attack_range(regular_ballista_instance)
        
        # Assert
        assert result == expected_tiles, "Range calculation should return the expected tiles"
        map_system.calculate_tiles_in_range.assert_called_once()
        call_args = map_system.calculate_tiles_in_range.call_args[1]
        assert call_args['origin'] == regular_ballista_instance.position
        assert call_args['min_range'] == regular_ballista_weapon.min_range
        assert call_args['max_range'] == regular_ballista_weapon.max_range
        
        # Test with disabled ballista
        regular_ballista_instance.is_enabled = False
        result = ballista_system.get_ballista_attack_range(regular_ballista_instance)
        assert result == set(), "Disabled ballista should have no attack range"
        
        # Test with empty ballista
        regular_ballista_instance.is_enabled = True
        regular_ballista_instance.current_durability = 0
        result = ballista_system.get_ballista_attack_range(regular_ballista_instance)
        assert result == set(), "Empty ballista should have no attack range"
    
    def test_get_valid_ballista_targets(self, setup_game_components, setup_test_data):
        """Test that get_valid_ballista_targets works correctly."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        unit_system = setup_game_components["unit_system"]
        map_system = setup_game_components["map_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        pegasus_unit = setup_test_data["units"]["pegasus_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        
        # Configure mocks
        mock_range_tiles = {(10, 10), (12, 12)}
        
        with patch.object(ballista_system, 'get_ballista_attack_range', return_value=mock_range_tiles):
            # Mock unit system to return units at those positions
            unit_system.get_units_on_tiles.return_value = [pegasus_unit, enemy_archer]
            unit_system.are_hostile.return_value = True
            
            # Mock map system for line of sight
            map_system.has_line_of_sight.return_value = True
            
            # Act
            result = ballista_system.get_valid_ballista_targets(archer_unit, regular_ballista_instance)
            
            # Assert
            assert len(result) == 2, "Should find both ground and flying enemy units"
            assert pegasus_unit in result, "Should include flying unit"
            assert enemy_archer in result, "Should include ground unit"
            
            # Test with no line of sight to one target
            def mock_has_line_of_sight(pos1, pos2):
                return pos2 == (10, 10)  # Only pegasus is visible
                
            map_system.has_line_of_sight.side_effect = mock_has_line_of_sight
            
            # Act again
            result = ballista_system.get_valid_ballista_targets(archer_unit, regular_ballista_instance)
            
            # Assert
            assert len(result) == 1, "Should only find units with line of sight"
            assert pegasus_unit in result, "Should include unit with line of sight"
            assert enemy_archer not in result, "Should exclude unit without line of sight"
    
    def test_calculate_ballista_combat_preview(self, setup_game_components, setup_test_data):
        """Test that calculate_ballista_combat_preview works correctly."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        combat_system = setup_game_components["combat_system"]
        map_system = setup_game_components["map_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        pegasus_unit = setup_test_data["units"]["pegasus_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        regular_ballista_type = setup_test_data["ballista_types"]["regular"]
        regular_ballista_weapon = setup_test_data["ballista_weapons"]["regular"]
        
        # Configure mocks
        ballista_system.get_ballista_type = Mock(return_value=regular_ballista_type)
        ballista_system.get_ballista_weapon = Mock(return_value=regular_ballista_weapon)
        
        # Test case 1: Standard attack against ground unit
        combat_system.get_effectiveness_multiplier.return_value = 1.0
        combat_system.get_combat_stat_bonuses.return_value = 5
        combat_system.calculate_avoid.return_value = 20
        combat_system.calculate_crit_evade.return_value = 10
        combat_system.calculate_defense.return_value = 3
        map_system.distance.return_value = 8
        combat_system.can_counter.return_value = False
        
        # Act
        result = ballista_system.calculate_ballista_combat_preview(archer_unit, enemy_archer, regular_ballista_instance)
        
        # Assert
        assert result["attacker_unit_id"] == archer_unit.id
        assert result["defender_unit_id"] == enemy_archer.id
        assert result["ballista_instance_id"] == regular_ballista_instance.id
        assert result["attacker_potential_dmg"] == 5  # 8 (might) - 3 (defense)
        assert result["attacker_hit"] == 77  # 70 (base) + 16 (skill*2) + 6 (luck) + 5 (bonuses) - 20 (avoid)
        assert result["attacker_crit"] == 0  # 0 (base) + 8 (skill) + 5 (bonuses) - 10 (crit evade) = 3, but capped at 0
        assert result["can_defender_counter"] is False
        
        # Test case 2: Attack against flying unit (effectiveness)
        combat_system.get_effectiveness_multiplier.return_value = 3.0
        combat_system.calculate_defense.return_value = 5
        
        # Act
        result = ballista_system.calculate_ballista_combat_preview(archer_unit, pegasus_unit, regular_ballista_instance)
        
        # Assert
        assert result["attacker_potential_dmg"] == 19  # (8 (might) * 3 (effectiveness)) - 5 (defense)
    
    def test_execute_ballista_attack(self, setup_game_components, setup_test_data):
        """Test that execute_ballista_attack works correctly."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        game_state_manager = setup_game_components["game_state_manager"]
        combat_system = setup_game_components["combat_system"]
        action_system = setup_game_components["action_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        enemy_archer = setup_test_data["units"]["enemy_archer"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Set up ballista with durability
        regular_ballista_instance.current_durability = 5
        regular_ballista_instance.is_enabled = True
        
        # Mock combat preview
        preview = self._create_combat_preview(
            attacker_id=archer_unit.id,
            defender_id=enemy_archer.id,
            ballista_id=regular_ballista_instance.id,
            damage=5,
            hit=80,
            crit=0,
            can_counter=False
        )
        
        with patch.object(ballista_system, 'calculate_ballista_combat_preview', return_value=preview):
            # Test case 1: Hit
            with patch('random.random', return_value=0.1):  # 0.1 < 0.8 (80% hit chance)
                # Act
                ballista_system.execute_ballista_attack(archer_unit, enemy_archer, regular_ballista_instance)
                
                # Assert
                assert regular_ballista_instance.current_durability == 4, "Durability should be decremented"
                game_state_manager.apply_damage.assert_called_once_with(enemy_archer.id, 5)
                action_system.mark_unit_action_complete.assert_called_once_with(archer_unit)
                
                # Reset mocks
                game_state_manager.apply_damage.reset_mock()
                action_system.mark_unit_action_complete.reset_mock()
            
            # Test case 2: Miss
            regular_ballista_instance.current_durability = 4  # Reset from previous test
            
            with patch('random.random', return_value=0.9):  # 0.9 > 0.8 (80% hit chance)
                # Act
                ballista_system.execute_ballista_attack(archer_unit, enemy_archer, regular_ballista_instance)
                
                # Assert
                assert regular_ballista_instance.current_durability == 3, "Durability should still be decremented"
                combat_system.display_miss_effect.assert_called_once_with(enemy_archer)
                game_state_manager.apply_damage.assert_not_called()
                action_system.mark_unit_action_complete.assert_called_once_with(archer_unit)
            
            # Test case 3: Zero durability
            regular_ballista_instance.current_durability = 0
            
            # Verify exception raised
            with pytest.raises(ValueError, match="Cannot fire ballista with 0 durability"):
                ballista_system.execute_ballista_attack(archer_unit, enemy_archer, regular_ballista_instance)
    
    def test_on_unit_removed_from_map(self, setup_game_components, setup_test_data):
        """Test that on_unit_removed_from_map works correctly."""
        # Arrange
        ballista_system = setup_game_components["ballista_system"]
        map_system = setup_game_components["map_system"]
        archer_unit = setup_test_data["units"]["archer_unit"]
        regular_ballista_instance = setup_test_data["ballista_instances"]["regular"]
        
        # Set up ballista with operator
        regular_ballista_instance.occupying_unit_id = archer_unit.id
        regular_ballista_instance.is_enabled = True
        
        # Mock event for unit removal
        event = Mock()
        event.unit_id = archer_unit.id
        
        # Mock map_system.get_all_objects_of_type
        map_system.get_all_objects_of_type.return_value = [regular_ballista_instance]
        
        # Act
        ballista_system.on_unit_removed_from_map(event)
        
        # Assert
        assert regular_ballista_instance.occupying_unit_id is None, "Operator reference should be cleared"
        assert regular_ballista_instance.is_enabled is False, "Ballista should be disabled"
        map_system.get_all_objects_of_type.assert_called_once_with(BallistaInstance)