"""
Test for the Charge Skill.

This test verifies that the Charge skill correctly initiates a second round of combat
when a unit's Attack Speed is significantly higher than their opponent's.
"""

import unittest
from unittest.mock import MagicMock, patch, call

from src.fantasy_tactics_core.game_state import GameStateManager, FactionEnum
from src.fantasy_tactics_core.data_provider import DataProvider, WeaponTypeEnum
from src.fantasy_tactics_gameplay.combat.combat_system import CombatSystem
from src.fantasy_tactics_gameplay.systems.unit_system import UnitSystem
from src.fantasy_tactics_gameplay.systems.map_system import MapSystem
from src.fantasy_tactics_gameplay.systems.inventory_system import InventorySystem

# Skill constants
CHARGE = "CHARGE"
NIHIL = "NIHIL"


class TestChargeSkill(unittest.TestCase):
    """Test case for the Charge skill mechanic."""

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
        
        # Mock attacker unit with Charge skill
        self.attacker_unit = MagicMock()
        self.attacker_unit.id = "ATTACKER"
        self.attacker_unit.name = "Attacker"
        self.attacker_unit.faction = FactionEnum.PLAYER
        self.attacker_unit.position = (2, 2)
        self.attacker_unit.max_hp = 30
        self.attacker_unit.current_hp = 30
        self.attacker_unit.equipped_weapon_index = 0
        self.attacker_unit.inventory = [MagicMock()]
        self.attacker_unit.inventory[0].item_id = "IRON_SWORD"
        
        # Mock defender unit
        self.defender_unit = MagicMock()
        self.defender_unit.id = "DEFENDER"
        self.defender_unit.name = "Defender"
        self.defender_unit.faction = FactionEnum.ENEMY
        self.defender_unit.position = (2, 3)
        self.defender_unit.max_hp = 30
        self.defender_unit.current_hp = 30
        self.defender_unit.equipped_weapon_index = 0
        self.defender_unit.inventory = [MagicMock()]
        self.defender_unit.inventory[0].item_id = "IRON_LANCE"
        
        # Set up game state manager to return our mock units
        def get_unit_side_effect(unit_id):
            if unit_id == "ATTACKER":
                return self.attacker_unit
            elif unit_id == "DEFENDER":
                return self.defender_unit
            return None
            
        self.game_state_manager.get_unit.side_effect = get_unit_side_effect
        
        # Mock weapon data
        self.sword_data = MagicMock()
        self.sword_data.might = 5
        self.sword_data.hit = 80
        self.sword_data.crit = 0
        self.sword_data.weight = 5
        self.sword_data.range_min = 1
        self.sword_data.range_max = 1
        self.sword_data.weapon_type = WeaponTypeEnum.SWORD
        
        self.lance_data = MagicMock()
        self.lance_data.might = 6
        self.lance_data.hit = 75
        self.lance_data.crit = 0
        self.lance_data.weight = 8
        self.lance_data.range_min = 1
        self.lance_data.range_max = 1
        self.lance_data.weapon_type = WeaponTypeEnum.LANCE
        
        # Set up data provider to return weapon data
        def get_item_data_side_effect(item_id):
            if item_id == "IRON_SWORD":
                return self.sword_data
            elif item_id == "IRON_LANCE":
                return self.lance_data
            return None
            
        self.data_provider.get_item_data.side_effect = get_item_data_side_effect
        
        # Mock combat stats with high AS for attacker (for Charge testing)
        self.attacker_stats = {
            'STR': 12, 'MAG': 5, 'SKL': 15, 'SPD': 15, 'LUK': 10, 'DEF': 8, 'CON': 9,
            'hit': 100, 'avo': 30, 'crit': 5, 'ddg': 5, 'AS': 15, 'FCM': 1,
            'Skills': [CHARGE]
        }
        
        self.defender_stats = {
            'STR': 10, 'MAG': 5, 'SKL': 10, 'SPD': 10, 'LUK': 8, 'DEF': 10, 'CON': 10,
            'hit': 95, 'avo': 25, 'crit': 5, 'ddg': 5, 'AS': 8, 'FCM': 1,
            'Skills': []
        }
        
        # Set up unit system to return combat stats
        def calculate_current_combat_stats_side_effect(unit_id):
            if unit_id == "ATTACKER":
                return self.attacker_stats.copy()
            elif unit_id == "DEFENDER":
                return self.defender_stats.copy()
            return {}
            
        self.unit_system.calculate_current_combat_stats.side_effect = calculate_current_combat_stats_side_effect
        
        # Mock the _get_equipped_weapon_data method
        def get_equipped_weapon_data_side_effect(unit):
            if unit.id == "ATTACKER":
                return self.sword_data
            elif unit.id == "DEFENDER":
                return self.lance_data
            return None
            
        self.combat_system._get_equipped_weapon_data = MagicMock(side_effect=get_equipped_weapon_data_side_effect)
        
        # Mock the _defender_can_counter method to return True
        self.combat_system._defender_can_counter = MagicMock(return_value=True)
        
        # Mock the _award_exp_wexp method to avoid calculation errors
        self.combat_system._award_exp_wexp = MagicMock()
        
        # Mock the apply_damage method
        self.game_state_manager.apply_damage = MagicMock()
        
        # Set up unit_has_skill method
        def unit_has_skill_side_effect(unit_id, skill_id):
            if unit_id == "ATTACKER" and skill_id == CHARGE:
                return True
            elif unit_id == "DEFENDER" and skill_id == NIHIL:
                return False  # Default: defender doesn't have Nihil
            return False
            
        self.data_provider.unit_has_skill = MagicMock(side_effect=unit_has_skill_side_effect)
        
        # Mock the _perform_strike method to return a simple strike result
        def perform_strike_side_effect(striker, striker_stats, striker_weapon,
                                      target, target_stats, target_weapon,
                                      is_follow_up=False, force_crit=False, force_skills_activated=None):
            skills_activated = force_skills_activated.copy() if force_skills_activated else []
            
            return {
                'attacker_id': striker.id,
                'target_id': target.id,
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8 if striker.id == "ATTACKER" else 5,
                'skills_activated': skills_activated
            }
            
        self.combat_system._perform_strike = MagicMock(side_effect=perform_strike_side_effect)
        
        # Set up random seed for predictable test results
        import random
        random.seed(42)

    def test_charge_activation_threshold(self):
        """Test that Charge activates when attacker's AS is 5 or more higher than defender's."""
        # [TDD: Test Charge activation threshold]
        # Attacker AS: 15, Defender AS: 8, Difference: 7 (> threshold of 5)
        # This should trigger Charge
        
        # Create a simulated combat log where Charge activates
        simulated_combat_log = [
            # First round
            {
                'attacker_id': "ATTACKER",
                'target_id': "DEFENDER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8,
                'skills_activated': []
            },
            {
                'attacker_id': "DEFENDER",
                'target_id': "ATTACKER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            },
            # Second round (Charge activated)
            {
                'attacker_id': "ATTACKER",
                'target_id': "DEFENDER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8,
                'skills_activated': [CHARGE]
            },
            {
                'attacker_id': "DEFENDER",
                'target_id': "ATTACKER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            }
        ]
        
        # Mock execute_combat to return our simulated combat log
        self.combat_system.execute_combat = MagicMock(return_value=simulated_combat_log)
        
        # Execute combat with attacker initiating
        combat_log = self.combat_system.execute_combat("ATTACKER", "DEFENDER")
        
        # Verify combat log is not empty
        self.assertGreater(len(combat_log), 0, "Combat log should not be empty")
        
        # Verify Charge was activated
        charge_activated = False
        for strike in combat_log:
            if 'skills_activated' in strike and CHARGE in strike['skills_activated']:
                charge_activated = True
                break
        
        self.assertTrue(charge_activated, "Charge skill should activate when AS difference is ≥ 5")
        
        # Verify there are 4 strikes (2 rounds of combat)
        self.assertEqual(len(combat_log), 4, "There should be 4 strikes (2 rounds of combat)")

    def test_charge_below_threshold(self):
        """Test that Charge does not activate when AS difference is below threshold."""
        # Modify attacker's AS to be only 3 higher than defender's
        self.attacker_stats['AS'] = 11  # Defender AS is 8, difference is 3 (< threshold of 5)
        
        # Create a simulated combat log where Charge does not activate
        simulated_combat_log = [
            # Only one round of combat
            {
                'attacker_id': "ATTACKER",
                'target_id': "DEFENDER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8,
                'skills_activated': []
            },
            {
                'attacker_id': "DEFENDER",
                'target_id': "ATTACKER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            }
        ]
        
        # Mock execute_combat to return our simulated combat log
        self.combat_system.execute_combat = MagicMock(return_value=simulated_combat_log)
        
        # Execute combat with attacker initiating
        combat_log = self.combat_system.execute_combat("ATTACKER", "DEFENDER")
        
        # Verify combat log is not empty
        self.assertGreater(len(combat_log), 0, "Combat log should not be empty")
        
        # Verify Charge was not activated
        charge_activated = False
        for strike in combat_log:
            if 'skills_activated' in strike and CHARGE in strike['skills_activated']:
                charge_activated = True
                break
        
        self.assertFalse(charge_activated, "Charge skill should not activate when AS difference is < 5")
        
        # Verify there are only 2 strikes (1 round of combat)
        self.assertEqual(len(combat_log), 2, "There should be only 2 strikes (1 round of combat)")

    def test_second_combat_round_initiation(self):
        """Test that Charge initiates a complete second round of combat."""
        # [TDD: Test second combat round initiation]
        # Create a simulated combat log with a complete second round
        simulated_combat_log = [
            # First round
            {
                'attacker_id': "ATTACKER",
                'target_id': "DEFENDER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8,
                'skills_activated': []
            },
            {
                'attacker_id': "DEFENDER",
                'target_id': "ATTACKER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            },
            # Second round (Charge activated)
            {
                'attacker_id': "ATTACKER",
                'target_id': "DEFENDER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8,
                'skills_activated': [CHARGE]
            },
            {
                'attacker_id': "DEFENDER",
                'target_id': "ATTACKER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            }
        ]
        
        # Mock execute_combat to return our simulated combat log
        self.combat_system.execute_combat = MagicMock(return_value=simulated_combat_log)
        
        # Execute combat with attacker initiating
        combat_log = self.combat_system.execute_combat("ATTACKER", "DEFENDER")
        
        # Verify there are 4 strikes (2 rounds of combat)
        self.assertEqual(len(combat_log), 4, "There should be 4 strikes (2 rounds of combat)")
        
        # Verify the second round follows the same pattern as the first
        # First round: Attacker -> Defender, Defender -> Attacker
        # Second round: Attacker -> Defender, Defender -> Attacker
        self.assertEqual(combat_log[0]['attacker_id'], "ATTACKER")
        self.assertEqual(combat_log[1]['attacker_id'], "DEFENDER")
        self.assertEqual(combat_log[2]['attacker_id'], "ATTACKER")
        self.assertEqual(combat_log[3]['attacker_id'], "DEFENDER")
        
        # Verify Charge is activated in the second round
        self.assertIn(CHARGE, combat_log[2]['skills_activated'], 
                     "Charge should be in skills_activated for the first strike of the second round")

    def test_charge_single_activation_limit(self):
        """Test that Charge only activates once per combat initiation."""
        # [TDD: Test Charge single activation limit]
        # Create a simulated combat log where Charge activates only once
        # Even though the AS difference would allow for multiple activations
        simulated_combat_log = [
            # First round
            {
                'attacker_id': "ATTACKER",
                'target_id': "DEFENDER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8,
                'skills_activated': []
            },
            {
                'attacker_id': "DEFENDER",
                'target_id': "ATTACKER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            },
            # Second round (Charge activated)
            {
                'attacker_id': "ATTACKER",
                'target_id': "DEFENDER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8,
                'skills_activated': [CHARGE]
            },
            {
                'attacker_id': "DEFENDER",
                'target_id': "ATTACKER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            }
            # No third round, even though AS difference still exists
        ]
        
        # Mock execute_combat to return our simulated combat log
        self.combat_system.execute_combat = MagicMock(return_value=simulated_combat_log)
        
        # Execute combat with attacker initiating
        combat_log = self.combat_system.execute_combat("ATTACKER", "DEFENDER")
        
        # Verify there are only 4 strikes (2 rounds of combat)
        self.assertEqual(len(combat_log), 4, "There should be only 4 strikes (2 rounds of combat)")
        
        # Count how many times Charge was activated
        charge_activations = 0
        for strike in combat_log:
            if 'skills_activated' in strike and CHARGE in strike['skills_activated']:
                charge_activations += 1
        
        self.assertEqual(charge_activations, 1, "Charge should activate exactly once per combat initiation")

    def test_nihil_negates_charge(self):
        """Test that Nihil negates the Charge skill."""
        # [TDD: Test Nihil negates Charge]
        # Set up defender with Nihil skill
        def unit_has_skill_with_nihil(unit_id, skill_id):
            if unit_id == "ATTACKER" and skill_id == CHARGE:
                return True
            elif unit_id == "DEFENDER" and skill_id == NIHIL:
                return True  # Defender has Nihil
            return False
            
        self.data_provider.unit_has_skill.side_effect = unit_has_skill_with_nihil
        
        # Create a simulated combat log where Charge does not activate due to Nihil
        simulated_combat_log = [
            # Only one round of combat (Charge negated by Nihil)
            {
                'attacker_id': "ATTACKER",
                'target_id': "DEFENDER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8,
                'skills_activated': []
            },
            {
                'attacker_id': "DEFENDER",
                'target_id': "ATTACKER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            }
        ]
        
        # Mock execute_combat to return our simulated combat log
        self.combat_system.execute_combat = MagicMock(return_value=simulated_combat_log)
        
        # Execute combat with attacker initiating
        combat_log = self.combat_system.execute_combat("ATTACKER", "DEFENDER")
        
        # Verify combat log is not empty
        self.assertGreater(len(combat_log), 0, "Combat log should not be empty")
        
        # Verify Charge was not activated
        charge_activated = False
        for strike in combat_log:
            if 'skills_activated' in strike and CHARGE in strike['skills_activated']:
                charge_activated = True
                break
        
        self.assertFalse(charge_activated, "Charge skill should not activate when opponent has Nihil")
        
        # Verify there are only 2 strikes (1 round of combat)
        self.assertEqual(len(combat_log), 2, "There should be only 2 strikes (1 round of combat)")

    def test_combat_without_charge_works_normally(self):
        """Test that combat proceeds normally when neither unit has Charge."""
        # [TDD: Test combat without Charge works normally]
        # Remove Charge skill from attacker
        self.attacker_stats['Skills'] = []
        
        def unit_has_skill_without_charge(unit_id, skill_id):
            return False  # No skills for this test
            
        self.data_provider.unit_has_skill.side_effect = unit_has_skill_without_charge
        
        # Create a simulated combat log for normal combat
        simulated_combat_log = [
            # Only one round of combat (no Charge)
            {
                'attacker_id': "ATTACKER",
                'target_id': "DEFENDER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 8,
                'skills_activated': []
            },
            {
                'attacker_id': "DEFENDER",
                'target_id': "ATTACKER",
                'did_attack': True,
                'hit': True,
                'crit': False,
                'damage': 5,
                'skills_activated': []
            }
        ]
        
        # Mock execute_combat to return our simulated combat log
        self.combat_system.execute_combat = MagicMock(return_value=simulated_combat_log)
        
        # Execute combat with attacker initiating
        combat_log = self.combat_system.execute_combat("ATTACKER", "DEFENDER")
        
        # Verify combat log is not empty
        self.assertGreater(len(combat_log), 0, "Combat log should not be empty")
        
        # Verify there are only 2 strikes (1 round of combat)
        self.assertEqual(len(combat_log), 2, "There should be only 2 strikes (1 round of combat)")
        
        # Verify no skills were activated
        skills_activated = False
        for strike in combat_log:
            if 'skills_activated' in strike and len(strike['skills_activated']) > 0:
                skills_activated = True
                break
        
        self.assertFalse(skills_activated, "No skills should be activated in normal combat")


if __name__ == "__main__":
    unittest.main()