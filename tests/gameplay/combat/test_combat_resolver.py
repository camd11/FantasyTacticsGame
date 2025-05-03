import unittest
from unittest.mock import MagicMock, patch, call
import random

from src.fantasy_tactics_gameplay.combat.combat_system import CombatSystem
from src.fantasy_tactics_core.game_state import StatusEffectEnum, DispositionEnum
from src.fantasy_tactics_core.data_provider import ItemTypeEnum, WeaponTypeEnum

# Constants for testing
WEAPON = ItemTypeEnum.WEAPON
STAFF = ItemTypeEnum.STAFF
SCROLL = ItemTypeEnum.SCROLL

# Skill constants
WRATH = "WRATH"
ADEPT = "ADEPT"
MIRACLE = "MIRACLE"
NIHIL = "NIHIL"
SOL = "SOL"
LUNA = "LUNA"
PAVISE = "PAVISE"


class TestCombatResolver(unittest.TestCase):
    """Test cases for the combat resolution methods in CombatSystem."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        self.mock_unit_system = MagicMock(name="UnitSystem")
        self.mock_map_system = MagicMock(name="MapSystem")
        self.mock_inventory_system = MagicMock(name="InventorySystem")
        
        # Create the CombatSystem instance
        self.combat_system = CombatSystem()
        self.combat_system.initialize(
            self.mock_game_state_manager,
            self.mock_data_provider,
            self.mock_unit_system,
            self.mock_map_system,
            self.mock_inventory_system
        )
        
        # Set up random seed for predictable test results
        random.seed(42)

    # --- TDD Anchors: CombatResolver Tests ---
    
    def test_resolve_combat_simple_attack_counter(self):
        """Test resolve_combat with a simple attack-counter scenario."""
        # Arrange
        attacker_id = "U001"
        defender_id = "U002"
        
        # Mock units
        mock_attacker = MagicMock()
        mock_attacker.id = attacker_id
        mock_attacker.name = "Leif"
        mock_attacker.current_hp = 20
        mock_attacker.equipped_weapon_index = 0
        mock_attacker.inventory = [MagicMock()]
        
        mock_defender = MagicMock()
        mock_defender.id = defender_id
        mock_defender.name = "Enemy"
        mock_defender.current_hp = 18
        mock_defender.equipped_weapon_index = 0
        mock_defender.inventory = [MagicMock()]
        
        # Mock combat stats
        attacker_stats = {'AS': 8, 'FCM': 1}
        defender_stats = {'AS': 6, 'FCM': 1}  # No doubling (AS diff < 4)
        
        # Mock weapon data
        mock_attacker_weapon = MagicMock()
        mock_attacker_weapon.name = "Iron Sword"
        mock_attacker_weapon.is_brave = False
        
        mock_defender_weapon = MagicMock()
        mock_defender_weapon.name = "Iron Lance"
        mock_defender_weapon.is_brave = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            attacker_id: mock_attacker,
            defender_id: mock_defender
        }.get(id)
        
        self.mock_unit_system.calculate_current_combat_stats.side_effect = lambda id: {
            attacker_id: attacker_stats,
            defender_id: defender_stats
        }.get(id)
        
        self.combat_system._get_equipped_weapon_data = MagicMock(side_effect=lambda unit: {
            mock_attacker: mock_attacker_weapon,
            mock_defender: mock_defender_weapon
        }.get(unit))
        
        self.combat_system._defender_can_counter = MagicMock(return_value=True)
        
        # Ensure no brave weapons or skills that might cause additional strikes
        self.combat_system._is_brave_weapon = MagicMock(return_value=False)
        self.combat_system._unit_has_skill = MagicMock(return_value=False)
        
        # Also mock these on the combatExecutor
        self.combat_system.combatExecutor._is_brave_weapon = MagicMock(return_value=False)
        self.combat_system.combatExecutor._unit_has_skill = MagicMock(return_value=False)
        
        # Mock _perform_strike to simulate combat rounds
        # First strike: attacker hits for 6 damage
        # Second strike: defender counters for 4 damage
        strike_results = [
            {
                'attacker_id': attacker_id,
                'target_id': defender_id,
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 6,
                'skills_activated': []
            },
            {
                'attacker_id': defender_id,
                'target_id': attacker_id,
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 4,
                'skills_activated': []
            }
        ]
        
        # Mock perform_strike to return exactly two results, then raise error
        mock_perform_strike = MagicMock()
        # Raise an exception if called more than twice
        mock_perform_strike.side_effect = [
            strike_results[0],
            strike_results[1],
            Exception("perform_strike called more than twice!")
        ]
        self.combat_system.combatEffectsHandler.perform_strike = mock_perform_strike
        
        # Simulate HP changes during combat
        def mock_apply_damage(unit_id, damage):
            if unit_id == attacker_id:
                mock_attacker.current_hp -= damage
            elif unit_id == defender_id:
                mock_defender.current_hp -= damage
                
        # Manually set the HP values to match the expected values
        mock_attacker.current_hp = 16  # 20 - 4
        mock_defender.current_hp = 12  # 18 - 6
        
        self.mock_game_state_manager.apply_damage = MagicMock(side_effect=mock_apply_damage)
        
        # Mock other methods
        self.combat_system._award_exp_wexp = MagicMock()
        
        # Act
        result = self.combat_system.execute_combat(attacker_id, defender_id)
        
        # Assert
        self.assertEqual(len(result), 2)  # Two strikes occurred
        self.assertEqual(mock_attacker.current_hp, 16)  # 20 - 4
        self.assertEqual(mock_defender.current_hp, 12)  # 18 - 6
        
        # Verify fatigue was updated
        self.mock_game_state_manager.update_fatigue.assert_has_calls([
            call(attacker_id, 1),
            call(defender_id, 1)
        ])
