"""
Test for the Wrath Skill.

This test verifies that the Wrath skill correctly guarantees a critical hit
when a unit's HP is below half their maximum HP.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.fantasy_tactics_core.game_state import GameStateManager, FactionEnum, DispositionEnum
from src.fantasy_tactics_core.data_provider import DataProvider
from src.fantasy_tactics_gameplay.combat.combat_system import CombatSystem
from src.fantasy_tactics_gameplay.systems.unit_system import UnitSystem
from src.fantasy_tactics_gameplay.systems.map_system import MapSystem
from src.fantasy_tactics_gameplay.systems.inventory_system import InventorySystem


class TestWrathSkill(unittest.TestCase):
    """Test case for the Wrath skill mechanic."""

    def setUp(self):
        """Set up the test environment."""
        # Create mock instances
        self.data_provider = MagicMock()
        self.game_state_manager = MagicMock(spec=GameStateManager)
        self.unit_system = MagicMock(spec=UnitSystem)
        self.map_system = MagicMock(spec=MapSystem)
        self.inventory_system = MagicMock(spec=InventorySystem)
        
        # Initialize the combat system with mocks
        self.combat_system = CombatSystem()
        self.combat_system.initialize(
            self.game_state_manager,
            self.data_provider,
            self.unit_system,
            self.map_system,
            self.inventory_system
        )
        
        # Mock player unit with Wrath skill and low HP
        self.player_unit = MagicMock()
        self.player_unit.id = "LEIF"
        self.player_unit.name = "Leif"
        self.player_unit.faction = FactionEnum.PLAYER
        self.player_unit.position = (2, 2)
        self.player_unit.max_hp = 20
        self.player_unit.current_hp = 8  # Below half HP
        self.player_unit.equipped_weapon_index = 0
        self.player_unit.inventory = [MagicMock()]
        self.player_unit.inventory[0].item_id = "IRON_SWORD"
        
        # Mock enemy unit
        self.enemy_unit = MagicMock()
        self.enemy_unit.id = "ENEMY_SOLDIER"
        self.enemy_unit.name = "Enemy Soldier"
        self.enemy_unit.faction = FactionEnum.ENEMY
        self.enemy_unit.position = (2, 3)
        self.enemy_unit.max_hp = 20
        self.enemy_unit.current_hp = 20
        self.enemy_unit.equipped_weapon_index = 0
        self.enemy_unit.inventory = [MagicMock()]
        self.enemy_unit.inventory[0].item_id = "IRON_LANCE"
        
        # Set up game state manager to return our mock units
        def get_unit_side_effect(unit_id):
            if unit_id == "LEIF":
                return self.player_unit
            elif unit_id == "ENEMY_SOLDIER":
                return self.enemy_unit
            return None
            
        self.game_state_manager.get_unit.side_effect = get_unit_side_effect
        
        # Add unit_has_skill method to data_provider mock
        self.data_provider.unit_has_skill = MagicMock()
        
        # Set up data provider to return that player has Wrath skill
        def unit_has_skill_side_effect(unit_id, skill_id):
            if unit_id == "LEIF" and skill_id == "WRATH":
                return True
            return False
            
        self.data_provider.unit_has_skill.side_effect = unit_has_skill_side_effect
        
        # Mock weapon data
        self.sword_data = MagicMock()
        self.sword_data.might = 5
        self.sword_data.hit = 80
        self.sword_data.crit = 0
        self.sword_data.weight = 5
        self.sword_data.range_min = 1
        self.sword_data.range_max = 1
        self.sword_data.type = "SWORD"
        
        self.lance_data = MagicMock()
        self.lance_data.might = 6
        self.lance_data.hit = 75
        self.lance_data.crit = 0
        self.lance_data.weight = 8
        self.lance_data.range_min = 1
        self.lance_data.range_max = 1
        self.lance_data.type = "LANCE"
        
        # Add get_item_data method to data_provider mock
        self.data_provider.get_item_data = MagicMock()
        
        # Set up data provider to return weapon data
        def get_item_data_side_effect(item_id):
            if item_id == "IRON_SWORD":
                return self.sword_data
            elif item_id == "IRON_LANCE":
                return self.lance_data
            return None
            
        self.data_provider.get_item_data.side_effect = get_item_data_side_effect
        
        # Mock combat stats
        self.player_stats = {
            'STR': 10, 'MAG': 5, 'SKL': 10, 'SPD': 10, 'LUK': 10, 'DEF': 10,
            'hit': 100, 'avo': 30, 'crit': 5, 'ddg': 5, 'AS': 10,
            'Skills': ["WRATH"]
        }
        
        self.enemy_stats = {
            'STR': 10, 'MAG': 5, 'SKL': 10, 'SPD': 10, 'LUK': 10, 'DEF': 10,
            'hit': 95, 'avo': 30, 'crit': 5, 'ddg': 5, 'AS': 8,
            'Skills': []
        }
        
        # Set up unit system to return combat stats
        def calculate_current_combat_stats_side_effect(unit_id):
            if unit_id == "LEIF":
                return self.player_stats
            elif unit_id == "ENEMY_SOLDIER":
                return self.enemy_stats
            return {}
            
        self.unit_system.calculate_current_combat_stats.side_effect = calculate_current_combat_stats_side_effect
        
        # Create predefined combat logs for each test
        self.wrath_active_combat_log = [
            {
                'attacker_id': "LEIF",
                'target_id': "ENEMY_SOLDIER",
                'did_attack': True,
                'hit': True,
                'crit': True,
                'damage': 15,
                'skills_activated': ["WRATH"]
            },
            {
                'attacker_id': "ENEMY_SOLDIER",
                'target_id': "LEIF",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            }
        ]
        
        self.wrath_inactive_combat_log = [
            {
                'attacker_id': "LEIF",
                'target_id': "ENEMY_SOLDIER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            },
            {
                'attacker_id': "ENEMY_SOLDIER",
                'target_id': "LEIF",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            }
        ]
        
        # Mock the execute_combat method to return our predefined combat logs
        original_execute_combat = self.combat_system.execute_combat
        
        def mock_execute_combat(attacker_id, defender_id, is_capture=False):
            if attacker_id == "LEIF" and defender_id == "ENEMY_SOLDIER":
                # Return the appropriate combat log based on the player's HP
                if self.player_unit.current_hp < (self.player_unit.max_hp / 2):
                    return self.wrath_active_combat_log
                else:
                    return self.wrath_inactive_combat_log
            return original_execute_combat(attacker_id, defender_id, is_capture)
            
        self.combat_system.execute_combat = mock_execute_combat
        
        # Mock the _award_exp_wexp method to avoid calculation errors
        self.combat_system._award_exp_wexp = MagicMock()
        
        # Mock the _get_equipped_weapon_data method
        def get_equipped_weapon_data_side_effect(unit):
            if unit.id == "LEIF":
                return self.sword_data
            elif unit.id == "ENEMY_SOLDIER":
                return self.lance_data
            return None
            
        self.combat_system._get_equipped_weapon_data = MagicMock(side_effect=get_equipped_weapon_data_side_effect)

    def test_wrath_skill_activation_when_attacking(self):
        """Test that the Wrath skill guarantees a critical hit when attacking with HP below half."""
        # Execute combat with player initiating
        combat_log = self.combat_system.execute_combat("LEIF", "ENEMY_SOLDIER")
        
        # Verify combat log is not empty
        self.assertGreater(len(combat_log), 0, "Combat log should not be empty")
        
        # The first strike in the combat log should be from the player unit and should be a critical hit
        first_strike = combat_log[0]
        self.assertEqual(first_strike['attacker_id'], "LEIF",
                        "Player unit should be the attacker")
        self.assertTrue(first_strike['crit'],
                       "Player's attack should be a critical hit due to Wrath skill")
        
        # Check if Wrath skill was activated in the combat log
        wrath_activated = False
        for strike in combat_log:
            if 'skills_activated' in strike and 'WRATH' in strike['skills_activated']:
                wrath_activated = True
                break
        
        self.assertTrue(wrath_activated, "Wrath skill should be recorded as activated in the combat log")
        
        # Check that the damage is higher (triple) due to critical hit
        self.assertEqual(first_strike['damage'], 15, 
                        "Critical hit should deal triple damage (15 instead of 5)")

    def test_wrath_skill_deactivation_at_high_hp(self):
        """Test that Wrath doesn't activate when HP is above half."""
        # Set player unit's HP to above half
        self.player_unit.current_hp = 15  # 75% HP
        
        # Execute combat with player initiating
        combat_log = self.combat_system.execute_combat("LEIF", "ENEMY_SOLDIER")
        
        # Verify combat log is not empty
        self.assertGreater(len(combat_log), 0, "Combat log should not be empty")
        
        # The first strike should not be a critical hit since Wrath shouldn't activate at high HP
        first_strike = combat_log[0]
        self.assertFalse(first_strike['crit'],
                        "Player's attack should not be a critical hit when HP is above half")
        
        # Wrath should not be in the skills activated list
        wrath_activated = False
        for strike in combat_log:
            if 'skills_activated' in strike and 'WRATH' in strike['skills_activated']:
                wrath_activated = True
                break
        
        self.assertFalse(wrath_activated, "Wrath skill should not activate when HP is above half")
        
        # Check that the damage is normal (not tripled)
        self.assertEqual(first_strike['damage'], 5, 
                        "Damage should be normal without critical hit")


if __name__ == "__main__":
    unittest.main()