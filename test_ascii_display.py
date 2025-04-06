"""
Test script to verify the ASCII display update bug fix.
This script directly moves a unit and checks if the ASCII display updates correctly.
"""

import logging
from src.core_engine.game_state import GameStateManager
from src.core_engine.data_provider import DataProvider
from src.input.cli_display import CLIDisplay

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize components
data_provider = DataProvider()
data_provider.load_all_data("data")
game_state_manager = GameStateManager(data_provider)

# Initialize a scenario
print("Loading scenario: basic_movement")
map_data = data_provider.get_map_data("test_chapter", "basic_movement")
unit_placements = data_provider.get_unit_placements("test_chapter", "basic_movement")
game_state_manager.load_map(map_data)
game_state_manager.deploy_units(unit_placements, data_provider)

# Create a display
display = CLIDisplay()
display.initialize(game_state_manager, None, None, None, data_provider)

# Display the initial state
print("\nInitial state:")
display.render_ascii_map(game_state_manager)

# Move a unit
player_unit_id = "LEIF"
original_position = game_state_manager.get_unit(player_unit_id).position
new_position = (2, 2)  # Move to the forest tile
print(f"\nMoving {player_unit_id} from {original_position} to {new_position}")
game_state_manager.move_unit(player_unit_id, new_position)

# Display the state after moving
print("\nAfter move:")
display.render_ascii_map(game_state_manager)

# Move the enemy unit too
enemy_unit_id = "ENEMY_SOLDIER_1"
original_position = game_state_manager.get_unit(enemy_unit_id).position
new_position = (3, 3)  # Move to a different tile
print(f"\nMoving {enemy_unit_id} from {original_position} to {new_position}")
game_state_manager.move_unit(enemy_unit_id, new_position)

# Display the state after moving both units
print("\nAfter moving both units:")
display.render_ascii_map(game_state_manager)

print("\nTest completed.")