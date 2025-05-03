"""
ASCII Display Test for Weapon Triangle Mechanic

This script loads the weapon_triangle_test scenario and displays:
1. The map with units positioned on it
2. The weapon triangle relationships
3. Combat forecasts between all unit pairs to verify hit bonuses
"""

import logging
from src.fantasy_tactics_core.data_provider import DataProvider
from src.fantasy_tactics_core.game_state import GameStateManager
from src.fantasy_tactics_gameplay.systems.unit_system import UnitSystem
from src.fantasy_tactics_gameplay.systems.map_system import MapSystem
from src.fantasy_tactics_gameplay.systems.inventory_system import InventorySystem
from src.fantasy_tactics_gameplay.combat.combat_system import CombatSystem
from src.fantasy_tactics_data.scenario_loader import ScenarioLoader

# Set up logging
logging.basicConfig(level=logging.INFO)

def display_map(game_state, map_system):
    """Display the map with units positioned on it."""
    dimensions = game_state.get_map_dimensions()
    
    # Create empty map grid
    grid = []
    for y in range(dimensions[1]):
        row = []
        for x in range(dimensions[0]):
            row.append('.')  # Empty space
        grid.append(row)
    
    # Add units to the grid
    sword_user_id = "LEIF"
    axe_user_id = "HALVAN"
    lance_user_id = "FINN"
    
    sword_user = game_state.get_unit(sword_user_id)
    axe_user = game_state.get_unit(axe_user_id)
    lance_user = game_state.get_unit(lance_user_id)
    
    if sword_user:
        x, y = sword_user.position
        grid[y][x] = 'S'  # Sword user (player)
    
    if axe_user:
        x, y = axe_user.position
        grid[y][x] = 'A'  # Axe user
    
    if lance_user:
        x, y = lance_user.position
        grid[y][x] = 'L'  # Lance user
    
    # Display the map
    print("\n=== MAP ===")
    print("S = Sword user (LEIF)")
    print("A = Axe user (HALVAN)")
    print("L = Lance user (FINN)")
    print()
    
    for y in range(dimensions[1]):
        row_str = ""
        for x in range(dimensions[0]):
            row_str += grid[y][x] + " "
        print(row_str)

def display_weapon_triangle():
    """Display the weapon triangle relationship."""
    print("\n=== WEAPON TRIANGLE ===")
    print("Sword > Axe > Lance > Sword")
    print("The weapon triangle affects hit rates in combat.")

def display_combat_forecasts(combat_system, game_state):
    """Display combat forecasts between all unit pairs."""
    sword_user_id = "LEIF"
    axe_user_id = "HALVAN"
    lance_user_id = "FINN"
    
    print("\n=== COMBAT FORECASTS ===")
    
    # Sword vs Axe
    forecast = combat_system.simulate_combat(sword_user_id, axe_user_id)
    print(f"Sword vs Axe: Hit = {forecast['attacker']['hit']}% (Expected: 96%)")
    
    # Sword vs Lance
    forecast = combat_system.simulate_combat(sword_user_id, lance_user_id)
    print(f"Sword vs Lance: Hit = {forecast['attacker']['hit']}% (Expected: 89%)")
    
    # Axe vs Lance
    forecast = combat_system.simulate_combat(axe_user_id, lance_user_id)
    print(f"Axe vs Lance: Hit = {forecast['attacker']['hit']}% (Expected: 65%)")
    
    # Axe vs Sword
    forecast = combat_system.simulate_combat(axe_user_id, sword_user_id)
    print(f"Axe vs Sword: Hit = {forecast['attacker']['hit']}% (Expected: 64%)")
    
    # Lance vs Sword
    forecast = combat_system.simulate_combat(lance_user_id, sword_user_id)
    print(f"Lance vs Sword: Hit = {forecast['attacker']['hit']}% (Expected: 81%)")
    
    # Lance vs Axe
    forecast = combat_system.simulate_combat(lance_user_id, axe_user_id)
    print(f"Lance vs Axe: Hit = {forecast['attacker']['hit']}% (Expected: 89%)")

def main():
    """Main function to run the test."""
    # Initialize systems
    data_provider = DataProvider()
    data_provider.load_all_data("data")
    
    game_state = GameStateManager(data_provider)
    unit_system = UnitSystem()
    map_system = MapSystem()
    inventory_system = InventorySystem()
    combat_system = CombatSystem()
    
    # Initialize dependencies
    map_system.initialize(game_state, data_provider)
    unit_system.initialize(game_state, data_provider)
    inventory_system.initialize(game_state, data_provider)
    combat_system.initialize(
        game_state, 
        data_provider, 
        unit_system, 
        map_system, 
        inventory_system
    )
    
    # Load the weapon triangle test scenario
    scenario_loader = ScenarioLoader(
        game_state,
        data_provider,
        unit_system,
        map_system
    )
    scenario_loader.load_scenario("weapon_triangle_test")
    
    # Display the test information
    print("\n=== WEAPON TRIANGLE TEST ===")
    print("This test verifies that the weapon triangle mechanic works correctly.")
    print("The weapon triangle is: Sword > Axe > Lance > Sword")
    print("The weapon triangle affects hit rates in combat.")
    
    # Display the map
    display_map(game_state, map_system)
    
    # Display the weapon triangle
    display_weapon_triangle()
    
    # Display combat forecasts
    display_combat_forecasts(combat_system, game_state)
    
    print("\n=== TEST COMPLETE ===")
    print("If all hit rates match the expected values, the weapon triangle mechanic is working correctly.")

if __name__ == "__main__":
    main()