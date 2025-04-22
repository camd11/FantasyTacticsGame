"""
ASCII Display Test for Weapon Triangle Mechanic

This script loads the weapon_triangle_test scenario and displays:
1. The map with units positioned on it
2. The weapon triangle relationships
3. Combat forecasts between all unit pairs to verify hit bonuses
"""

import logging
from src.core_engine.data_provider import DataProvider
from src.core_engine.game_state import GameStateManager, GameState, MapState
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.inventory_system import InventorySystem
from src.gameplay_systems.combat_system import CombatSystem

# Set up logging
logging.basicConfig(level=logging.INFO)

def display_map(game_state_manager, map_system):
    """Display the map with units positioned on it."""
    dimensions = game_state_manager.get_map_dimensions()
    
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
    
    sword_user = game_state_manager.get_unit(sword_user_id)
    axe_user = game_state_manager.get_unit(axe_user_id)
    lance_user = game_state_manager.get_unit(lance_user_id)
    
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

def display_combat_forecasts(combat_system, game_state_manager):
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
    
    game_state_manager = GameStateManager(data_provider)
    unit_system = UnitSystem()
    map_system = MapSystem()
    inventory_system = InventorySystem()
    combat_system = CombatSystem()
    
    # Initialize dependencies
    map_system.initialize(game_state_manager, data_provider)
    unit_system.initialize(game_state_manager, data_provider)
    inventory_system.initialize(game_state_manager, data_provider)
    combat_system.initialize(
        game_state_manager, 
        data_provider, 
        unit_system, 
        map_system, 
        inventory_system
    )
    
    # Manually set up the game state instead of using ScenarioLoader
    map_state = MapState()
    map_state.dimensions = (10, 10) # Simple 10x10 map
    map_state.terrain_grid = [['P'] * 10 for _ in range(10)] # All plains
    
    game_state = GameState("test_chapter", map_state)
    game_state_manager.set_current_game_state(game_state)
    
    # Define unit placements
    placements = [
        {'unit_id': 'LEIF', 'faction': 'PLAYER', 'position': [1, 1], 'level': 1, 'start_inventory': ['IRON_SWORD']},
        {'unit_id': 'HALVAN', 'faction': 'PLAYER', 'position': [1, 2], 'level': 1, 'start_inventory': ['IRON_AXE']},
        {'unit_id': 'FINN', 'faction': 'PLAYER', 'position': [2, 1], 'level': 1, 'start_inventory': ['IRON_LANCE']}
    ]
    
    # Deploy units using GameStateManager
    game_state_manager.deploy_units_from_list(placements, data_provider)

    # Display the test information
    print("\n=== WEAPON TRIANGLE TEST ===")
    print("This test verifies that the weapon triangle mechanic works correctly.")
    print("The weapon triangle is: Sword > Axe > Lance > Sword")
    print("The weapon triangle affects hit rates in combat.")
    
    # Display the map
    display_map(game_state_manager, map_system)
    
    # Display the weapon triangle
    display_weapon_triangle()
    
    # Display combat forecasts
    display_combat_forecasts(combat_system, game_state_manager)
    
    print("\n=== TEST COMPLETE ===")
    print("If all hit rates match the expected values, the weapon triangle mechanic is working correctly.")

if __name__ == "__main__":
    main()