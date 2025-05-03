"""
Test for Ballista System

This test verifies that the ballista system correctly handles ballista mechanics,
including data loading, usage conditions, targeting, combat calculations, durability,
and action costs.
"""

import pytest
import os
import yaml
from unittest.mock import Mock, MagicMock, patch

# Import necessary modules
from src.fantasy_tactics_core.game_state import GameStateManager
from src.fantasy_tactics_core.data_provider import DataProvider
from src.fantasy_tactics_gameplay.systems.map_system import MapSystem
from src.fantasy_tactics_gameplay.systems.unit_system import UnitSystem
from src.fantasy_tactics_gameplay.combat.combat_system import CombatSystem
from src.fantasy_tactics_gameplay.systems.action_system import ActionSystem
from src.fantasy_tactics_gameplay.systems.ballista_system import BallistaSystem, BallistaInstance, BallistaUserState

class TestBallistaSystem:
    """Test cases for the ballista system."""
    
    @pytest.fixture
    def setup_systems(self):
        """Set up the game systems needed for testing."""
        # Initialize components
        data_provider = DataProvider()
        game_state_manager = GameStateManager(data_provider)
        
        # Load test data
        data_provider._ballista_type_data = self._load_yaml_file("data/ballista_types.yaml")
        data_provider._ballista_weapon_data = self._load_yaml_file("data/ballista_weapons.yaml")
        
        # Create systems
        map_system = MapSystem()
        unit_system = UnitSystem()
        combat_system = CombatSystem()
        action_system = ActionSystem()
        ballista_system = BallistaSystem()
        
        # Initialize systems
        map_system.initialize(game_state_manager, data_provider)
        unit_system.initialize(game_state_manager, data_provider)
        combat_system.initialize(game_state_manager, data_provider, unit_system, map_system, None)
        action_system.initialize(game_state_manager, data_provider, map_system, None, combat_system)
        
        # Initialize ballista system
        ballista_system.initialize(
            game_state_manager,
            data_provider,
            map_system,
            unit_system,
            combat_system,
            action_system
        )
        
        return {
            "data_provider": data_provider,
            "game_state_manager": game_state_manager,
            "map_system": map_system,
            "unit_system": unit_system,
            "combat_system": combat_system,
            "action_system": action_system,
            "ballista_system": ballista_system
        }
    
    def _load_yaml_file(self, filepath):
        """Load data from a YAML file."""
        if not os.path.exists(filepath):
            return {}
        
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
    
    def test_ballista_type_validation(self, setup_systems):
        """Test that ballista type validation works correctly."""
        ballista_system = setup_systems["ballista_system"]
        
        # Valid ballista type
        assert ballista_system.validate_ballista_type("BALLISTA_REGULAR") is True
        
        # Invalid ballista type (non-existent)
        assert ballista_system.validate_ballista_type("NONEXISTENT_BALLISTA") is False
    
    def test_ballista_weapon_validation(self, setup_systems):
        """Test that ballista weapon validation works correctly."""
        ballista_system = setup_systems["ballista_system"]
        
        # Valid ballista weapon
        assert ballista_system.validate_ballista_weapon("BALLISTA_WEAPON_REGULAR") is True
        
        # Create an invalid weapon with min_range > max_range
        invalid_weapon = MagicMock()
        invalid_weapon.id = "INVALID_WEAPON"
        invalid_weapon.min_range = 10
        invalid_weapon.max_range = 5
        invalid_weapon.might = 8
        invalid_weapon.hit = 70
        invalid_weapon.crit = 0
        invalid_weapon.durability = 5
        
        # Mock get_ballista_weapon to return our invalid weapon
        ballista_system.get_ballista_weapon = MagicMock(return_value=invalid_weapon)
        
        # Test validation
        assert ballista_system.validate_ballista_weapon("INVALID_WEAPON") is False
    
    def test_check_unit_can_use_ballista(self, setup_systems):
        """Test that check_unit_can_use_ballista works correctly."""
        ballista_system = setup_systems["ballista_system"]
        
        # Create mock units and ballista
        archer = MagicMock()
        archer.class_id = "ARCHER"
        
        knight = MagicMock()
        knight.class_id = "KNIGHT"
        
        ballista = MagicMock()
        ballista.ballista_type_id = "BALLISTA_REGULAR"
        
        # Mock get_ballista_type
        ballista_type = MagicMock()
        ballista_type.allowed_classes = ["ARCHER", "SNIPER"]
        ballista_system.get_ballista_type = MagicMock(return_value=ballista_type)
        
        # Test with allowed class
        assert ballista_system.check_unit_can_use_ballista(archer, ballista) is True
        
        # Test with disallowed class
        assert ballista_system.check_unit_can_use_ballista(knight, ballista) is False
        
        # Test with null inputs
        assert ballista_system.check_unit_can_use_ballista(None, ballista) is False
        assert ballista_system.check_unit_can_use_ballista(archer, None) is False
    
    def test_get_ballista_attack_range(self, setup_systems):
        """Test that get_ballista_attack_range works correctly."""
        ballista_system = setup_systems["ballista_system"]
        map_system = setup_systems["map_system"]
        
        # Create mock ballista instance
        ballista = MagicMock()
        ballista.ballista_type_id = "BALLISTA_REGULAR"
        ballista.is_enabled = True
        ballista.current_durability = 5
        ballista.position = (5, 5)
        
        # Mock get_ballista_type and get_ballista_weapon
        ballista_type = MagicMock()
        ballista_type.weapon_id = "BALLISTA_WEAPON_REGULAR"
        ballista_system.get_ballista_type = MagicMock(return_value=ballista_type)
        
        ballista_weapon = MagicMock()
        ballista_weapon.min_range = 3
        ballista_weapon.max_range = 10
        ballista_system.get_ballista_weapon = MagicMock(return_value=ballista_weapon)
        
        # Mock map_system.calculate_tiles_in_range
        expected_tiles = {(2, 5), (3, 5), (4, 5), (6, 5), (7, 5), (8, 5)}
        map_system.calculate_tiles_in_range = MagicMock(return_value=expected_tiles)
        map_system.get_los_checker = MagicMock(return_value=lambda x, y: True)
        
        # Test range calculation
        result = ballista_system.get_ballista_attack_range(ballista)
        assert result == expected_tiles
        
        # Test with disabled ballista
        ballista.is_enabled = False
        result = ballista_system.get_ballista_attack_range(ballista)
        assert result == set()
        
        # Test with empty ballista
        ballista.is_enabled = True
        ballista.current_durability = 0
        result = ballista_system.get_ballista_attack_range(ballista)
        assert result == set()
    
    def test_get_valid_ballista_targets(self, setup_systems):
        """Test that get_valid_ballista_targets works correctly."""
        ballista_system = setup_systems["ballista_system"]
        unit_system = setup_systems["unit_system"]
        map_system = setup_systems["map_system"]
        
        # Create mock units and ballista
        archer = MagicMock()
        archer.id = "ARCHER_UNIT"
        archer.faction = "PLAYER"
        
        enemy_archer = MagicMock()
        enemy_archer.id = "ENEMY_ARCHER"
        enemy_archer.faction = "ENEMY"
        enemy_archer.position = (12, 12)
        enemy_archer.is_attackable = MagicMock(return_value=True)
        
        pegasus = MagicMock()
        pegasus.id = "PEGASUS_UNIT"
        pegasus.faction = "ENEMY"
        pegasus.position = (10, 10)
        pegasus.is_attackable = MagicMock(return_value=True)
        
        ballista = MagicMock()
        ballista.ballista_type_id = "BALLISTA_REGULAR"
        ballista.is_enabled = True
        ballista.current_durability = 5
        ballista.position = (5, 5)
        
        # Mock get_ballista_attack_range
        attack_range = {(10, 10), (12, 12)}
        ballista_system.get_ballista_attack_range = MagicMock(return_value=attack_range)
        
        # Mock unit_system.get_units_on_tiles
        unit_system.get_units_on_tiles = MagicMock(return_value=[enemy_archer, pegasus])
        
        # Mock unit_system.are_hostile
        unit_system.are_hostile = MagicMock(return_value=True)
        
        # Mock map_system.has_line_of_sight
        map_system.has_line_of_sight = MagicMock(return_value=True)
        
        # Test target selection
        result = ballista_system.get_valid_ballista_targets(archer, ballista)
        assert len(result) == 2
        assert enemy_archer in result
        assert pegasus in result
        
        # Test with no line of sight to one target
        def mock_has_line_of_sight(pos1, pos2):
            return pos2 == (10, 10)  # Only pegasus is visible
            
        map_system.has_line_of_sight.side_effect = mock_has_line_of_sight
        
        result = ballista_system.get_valid_ballista_targets(archer, ballista)
        assert len(result) == 1
        assert pegasus in result
        assert enemy_archer not in result
        
        # Test with disabled ballista
        ballista.is_enabled = False
        ballista_system.get_ballista_attack_range = MagicMock(return_value=set())
        
        result = ballista_system.get_valid_ballista_targets(archer, ballista)
        assert result == []
    
    def test_calculate_ballista_combat_preview(self, setup_systems):
        """Test that calculate_ballista_combat_preview works correctly."""
        ballista_system = setup_systems["ballista_system"]
        combat_system = setup_systems["combat_system"]
        map_system = setup_systems["map_system"]
        
        # Create mock units and ballista
        archer = MagicMock()
        archer.id = "ARCHER_UNIT"
        archer.stats = MagicMock()
        archer.stats.skl = 8
        archer.stats.luk = 6
        archer.stats.current_hp = 20
        
        enemy_archer = MagicMock()
        enemy_archer.id = "ENEMY_ARCHER"
        enemy_archer.stats = MagicMock()
        enemy_archer.stats.current_hp = 15
        
        ballista = MagicMock()
        ballista.id = "BALLISTA_INSTANCE_1"
        ballista.ballista_type_id = "BALLISTA_REGULAR"
        
        # Mock get_ballista_type and get_ballista_weapon
        ballista_type = MagicMock()
        ballista_type.weapon_id = "BALLISTA_WEAPON_REGULAR"
        ballista_system.get_ballista_type = MagicMock(return_value=ballista_type)
        
        ballista_weapon = MagicMock()
        ballista_weapon.might = 8
        ballista_weapon.hit = 70
        ballista_weapon.crit = 0
        ballista_weapon.effectiveness = {"IS_FLYING": 3.0}
        ballista_system.get_ballista_weapon = MagicMock(return_value=ballista_weapon)
        
        # Mock combat_system methods
        combat_system.get_effectiveness_multiplier = MagicMock(return_value=1.0)
        combat_system.get_combat_stat_bonuses = MagicMock(return_value=5)
        combat_system.calculate_avoid = MagicMock(return_value=20)
        combat_system.calculate_crit_evade = MagicMock(return_value=10)
        combat_system.calculate_defense = MagicMock(return_value=3)
        
        # Mock map_system.distance
        map_system.distance = MagicMock(return_value=8)
        
        # Mock combat_system.can_counter
        combat_system.can_counter = MagicMock(return_value=False)
        
        # Test combat preview calculation
        result = ballista_system.calculate_ballista_combat_preview(archer, enemy_archer, ballista)
        
        # Verify result
        assert result["attacker_unit_id"] == archer.id
        assert result["defender_unit_id"] == enemy_archer.id
        assert result["ballista_instance_id"] == ballista.id
        assert result["attacker_potential_dmg"] == 5  # 8 (might) - 3 (defense)
        assert result["attacker_hit"] == 77  # 70 (base) + 16 (skill*2) + 6 (luck) + 5 (bonuses) - 20 (avoid)
        assert result["attacker_crit"] == 0  # 0 (base) + 8 (skill) + 5 (bonuses) - 10 (crit evade) = 3, but capped at 0
        assert result["can_defender_counter"] is False
        
        # Test with effectiveness against flying unit
        pegasus = MagicMock()
        pegasus.id = "PEGASUS_UNIT"
        pegasus.stats = MagicMock()
        pegasus.stats.current_hp = 18
        
        combat_system.get_effectiveness_multiplier = MagicMock(return_value=3.0)
        combat_system.calculate_defense = MagicMock(return_value=5)
        
        result = ballista_system.calculate_ballista_combat_preview(archer, pegasus, ballista)
        assert result["attacker_potential_dmg"] == 19  # (8 (might) * 3 (effectiveness)) - 5 (defense)
    
    def test_execute_ballista_attack(self, setup_systems):
        """Test that execute_ballista_attack works correctly."""
        ballista_system = setup_systems["ballista_system"]
        game_state_manager = setup_systems["game_state_manager"]
        combat_system = setup_systems["combat_system"]
        action_system = setup_systems["action_system"]
        
        # Create mock units and ballista
        archer = MagicMock()
        archer.id = "ARCHER_UNIT"

        enemy_archer = MagicMock()
        enemy_archer.id = "ENEMY_ARCHER"
        enemy_archer.stats = MagicMock()
        enemy_archer.stats.current_hp = 15

        ballista = MagicMock()
        ballista.id = "BALLISTA_INSTANCE_1"
        ballista.current_durability = 5
        
        # Mock combat_system methods
        combat_system.display_miss_effect = MagicMock()
        combat_system.display_hit_effect = MagicMock()
        combat_system.handle_unit_defeated = MagicMock()

        # Mock calculate_ballista_combat_preview
        preview = {
            "attacker_unit_id": archer.id,
            "defender_unit_id": enemy_archer.id,
            "ballista_instance_id": ballista.id,
            "attacker_potential_dmg": 5,
            "attacker_hit": 80,
            "attacker_crit": 0,
            "can_defender_counter": False
        }
        ballista_system.calculate_ballista_combat_preview = MagicMock(return_value=preview)
        
        # Mock action_system.mark_unit_action_complete
        action_system.mark_unit_action_complete = MagicMock()
        
        # Mock game_state_manager.apply_damage
        game_state_manager.apply_damage = MagicMock()
        
        # Mock random.random to ensure hit
        with patch('random.random', return_value=0.1):  # 0.1 < 0.8 (80% hit chance)
            ballista_system.execute_ballista_attack(archer, enemy_archer, ballista)
        
        # Verify durability decremented
        assert ballista.current_durability == 4
        
        # Verify damage applied
        game_state_manager.apply_damage.assert_called_once_with(enemy_archer.id, 5)
        
        # Verify action marked complete
        action_system.mark_unit_action_complete.assert_called_once_with(archer)
        
        # Verify action marked complete
        action_system.mark_unit_action_complete.assert_called_once_with(archer)
        
        # Test with miss
        ballista.current_durability = 4  # Reset from previous test
        
        # Mock random.random to ensure miss
        with patch('random.random', return_value=0.9):  # 0.9 > 0.8 (80% hit chance)
            ballista_system.execute_ballista_attack(archer, enemy_archer, ballista)
        
        # Verify durability still decremented
        assert ballista.current_durability == 3
        
        # Verify miss effect displayed
        combat_system.display_miss_effect.assert_called_once_with(enemy_archer)
        
        # Test with zero durability
        ballista.current_durability = 0
        
        # Verify exception raised
        with pytest.raises(ValueError, match="Cannot fire ballista with 0 durability"):
            ballista_system.execute_ballista_attack(archer, enemy_archer, ballista)
    
    def test_on_unit_removed_from_map(self, setup_systems):
        """Test that on_unit_removed_from_map works correctly."""
        ballista_system = setup_systems["ballista_system"]
        map_system = setup_systems["map_system"]
        
        # Create mock ballista instance
        ballista = MagicMock()
        ballista.id = "BALLISTA_INSTANCE_1"
        ballista.occupying_unit_id = "ARCHER_UNIT"
        ballista.is_enabled = True
        
        # Mock map_system.get_all_objects_of_type
        map_system.get_all_objects_of_type = MagicMock(return_value=[ballista])
        
        # Create mock event
        event = MagicMock()
        event.unit_id = "ARCHER_UNIT"
        
        # Test event handler
        ballista_system.on_unit_removed_from_map(event)
        
        # Verify ballista state updated
        assert ballista.occupying_unit_id is None
        assert ballista.is_enabled is False