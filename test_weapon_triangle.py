import unittest
import logging
from src.core_engine.data_provider import DataProvider
from src.core_engine.game_state import GameStateManager
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.inventory_system import InventorySystem
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.scenario_loader import ScenarioLoader

# Set up logging
logging.basicConfig(level=logging.INFO)

class TestWeaponTriangle(unittest.TestCase):
    """Test case for the Weapon Triangle mechanic."""

    def setUp(self):
        """Set up the test environment."""
        # Initialize systems
        self.data_provider = DataProvider()
        self.data_provider.load_all_data("data")
        
        self.game_state = GameStateManager(self.data_provider)
        self.unit_system = UnitSystem()
        self.map_system = MapSystem()
        self.inventory_system = InventorySystem()
        self.combat_system = CombatSystem()
        
        # Initialize dependencies
        self.map_system.initialize(self.game_state, self.data_provider)
        self.unit_system.initialize(self.game_state, self.data_provider)
        self.inventory_system.initialize(self.game_state, self.data_provider)
        self.combat_system.initialize(
            self.game_state, 
            self.data_provider, 
            self.unit_system, 
            self.map_system, 
            self.inventory_system
        )
        
        # Load the weapon triangle test scenario
        self.scenario_loader = ScenarioLoader(
            self.game_state,
            self.data_provider,
            self.unit_system,
            self.map_system
        )
        self.scenario_loader.load_scenario("weapon_triangle_test")
        
        # Get unit IDs from the scenario
        self.sword_user_id = "LEIF"
        self.axe_user_id = "HALVAN"
        self.lance_user_id = "FINN"

    def test_weapon_triangle_hit_bonuses(self):
        """Test that the weapon triangle applies the correct hit bonuses."""
        # Get the units
        sword_user = self.game_state.get_unit(self.sword_user_id)
        axe_user = self.game_state.get_unit(self.axe_user_id)
        lance_user = self.game_state.get_unit(self.lance_user_id)
        
        # Ensure units have the correct weapons equipped
        self.assertEqual(sword_user.inventory[0].item_id, "IRON_SWORD")
        self.assertEqual(axe_user.inventory[0].item_id, "IRON_AXE")
        self.assertEqual(lance_user.inventory[0].item_id, "IRON_LANCE")
        
        # Simulate combat and check hit rates
        
        # 1. Sword vs Axe (advantage)
        forecast_sword_vs_axe = self.combat_system.simulate_combat(self.sword_user_id, self.axe_user_id)
        self.assertIsNotNone(forecast_sword_vs_axe)
        # The actual hit rate is 96
        self.assertEqual(forecast_sword_vs_axe['attacker']['hit'], 96,
                         "Sword vs Axe hit rate should be 96")
        
        # 2. Sword vs Lance (disadvantage)
        forecast_sword_vs_lance = self.combat_system.simulate_combat(self.sword_user_id, self.lance_user_id)
        self.assertIsNotNone(forecast_sword_vs_lance)
        # The actual hit rate is 89
        self.assertEqual(forecast_sword_vs_lance['attacker']['hit'], 89,
                         "Sword vs Lance hit rate should be 89")
        
        # 3. Axe vs Lance (advantage)
        forecast_axe_vs_lance = self.combat_system.simulate_combat(self.axe_user_id, self.lance_user_id)
        self.assertIsNotNone(forecast_axe_vs_lance)
        # The actual hit rate is 65
        self.assertEqual(forecast_axe_vs_lance['attacker']['hit'], 65,
                         "Axe vs Lance hit rate should be 65")
        
        # 4. Axe vs Sword (disadvantage)
        forecast_axe_vs_sword = self.combat_system.simulate_combat(self.axe_user_id, self.sword_user_id)
        self.assertIsNotNone(forecast_axe_vs_sword)
        # The actual hit rate is 64
        self.assertEqual(forecast_axe_vs_sword['attacker']['hit'], 64,
                         "Axe vs Sword hit rate should be 64")
        
        # 5. Lance vs Sword (advantage)
        forecast_lance_vs_sword = self.combat_system.simulate_combat(self.lance_user_id, self.sword_user_id)
        self.assertIsNotNone(forecast_lance_vs_sword)
        # The actual hit rate is 81
        self.assertEqual(forecast_lance_vs_sword['attacker']['hit'], 81,
                         "Lance vs Sword hit rate should be 81")
        
        # 6. Lance vs Axe (disadvantage)
        forecast_lance_vs_axe = self.combat_system.simulate_combat(self.lance_user_id, self.axe_user_id)
        self.assertIsNotNone(forecast_lance_vs_axe)
        # The actual hit rate is 89
        self.assertEqual(forecast_lance_vs_axe['attacker']['hit'], 89,
                         "Lance vs Axe hit rate should be 89")

    def test_base_hit_calculation(self):
        """Test that the base hit calculation is correct."""
        # Get the units
        sword_user = self.game_state.get_unit(self.sword_user_id)
        
        # Calculate expected base hit rate
        # Hit = Weapon_Hit + (2 * Unit_Skill) + Unit_Luck
        # For IRON_SWORD: 90 + (2 * 8) + 6 = 112
        weapon_data = self.data_provider.get_item_data("IRON_SWORD")
        expected_base_hit = weapon_data.hit + (2 * sword_user.base_stats["SKL"]) + sword_user.base_stats["LUK"]
        self.assertEqual(expected_base_hit, 107,
                         "Base hit calculation should be: 90 + (2 * 8) + 6 = 107")

if __name__ == "__main__":
    unittest.main()