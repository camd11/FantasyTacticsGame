"""
Interactive Input Test Module

This module provides a simple test harness for the interactive player input system.
It demonstrates how to initialize and use the system with mock game components.
The test harness includes functions for setting up mock systems, creating mock units,
and running both automated and manual tests of the interactive input system.
"""

import logging
import platform
from unittest.mock import Mock

# Conditionally import curses
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False

from src.ui.interactive_input import InteractiveInput


def setup_mock_systems():
    """
    Set up mock game systems for testing the interactive input system.
    
    This function creates mock instances of all the game systems required by the
    interactive input system, including game state manager, unit system, movement system,
    map system, action system, targeting system, and display system. Each mock system
    is configured with appropriate return values for its methods.
    
    Returns:
        Tuple of mock systems (game_state_manager, unit_system, movement_system, map_system,
                              action_system, targeting_system, display_system)
    """
    # Create mock game state manager
    game_state_manager = Mock()
    game_state_manager.current_game_state = Mock()
    game_state_manager.current_game_state.current_turn = 1
    game_state_manager.current_game_state.current_phase = Mock(name="PLAYER")
    game_state_manager.current_game_state.unit_states = {}
    
    # Create mock unit system
    unit_system = Mock()
    unit_system.get_unit_details = Mock(return_value=None)
    unit_system.get_equipped_weapon_details = Mock(return_value=None)
    
    # Create mock movement system
    movement_system = Mock()
    movement_system.calculate_movement_range = Mock(return_value=set([(1, 1), (2, 2), (3, 3)]))
    movement_system.is_valid_destination = Mock(return_value=True)
    
    # Create mock map system
    map_system = Mock()
    map_system.get_width = Mock(return_value=10)
    map_system.get_height = Mock(return_value=10)
    map_system.get_terrain_type = Mock(return_value=Mock(name="PLAIN"))
    map_system.get_path = Mock(return_value=[(1, 1), (2, 2), (3, 3)])
    map_system.get_attackable_tiles = Mock(return_value=set([(4, 4), (5, 5)]))
    map_system.get_units_in_attack_range = Mock(return_value=["ENEMY1"])
    
    # Create mock action system
    action_system = Mock()
    action_system.get_available_actions = Mock(return_value=["Attack", "Staff", "Item", "Wait"])
    
    # Create mock targeting system
    targeting_system = Mock()
    targeting_system.get_valid_targets = Mock(return_value=["ENEMY1", "ENEMY2"])
    targeting_system.get_valid_staff_targets = Mock(return_value=["ALLY1", "ALLY2"])
    
    # Create mock display system
    display_system = Mock()
    display_system.display_map = Mock()
    display_system.display_movement_range = Mock()
    display_system.display_action_menu = Mock()
    display_system.display_attack_range = Mock()
    display_system.display_staff_range = Mock()
    display_system.display_targets = Mock()
    display_system.display_unit_details = Mock()
    display_system.display_active_units = Mock()
    
    return (
        game_state_manager,
        unit_system,
        movement_system,
        map_system,
        action_system,
        targeting_system,
        display_system
    )


def setup_mock_units(game_state_manager):
    """
    Set up mock units for testing the interactive input system.
    
    This function creates mock player and enemy units and adds them to the game state.
    It sets up one active player unit, one inactive player unit (that has already acted),
    and one enemy unit. It also configures the game_state_manager to return these units
    when queried.
    
    Args:
        game_state_manager: Mock game state manager to add the units to
    """
    # Create player units - one that has acted and one that hasn't
    player_unit_active = Mock()
    player_unit_active.id = "PLAYER1"
    player_unit_active.name = "Leif"
    player_unit_active.faction = "PLAYER"
    player_unit_active.has_acted = False
    player_unit_active.position = (1, 1)
    player_unit_active.status_effects = []
    
    player_unit_inactive = Mock()
    player_unit_inactive.id = "PLAYER2"
    player_unit_inactive.name = "Finn"
    player_unit_inactive.faction = "PLAYER"
    player_unit_inactive.has_acted = True
    player_unit_inactive.position = (2, 2)
    player_unit_inactive.status_effects = []
    
    enemy_unit = Mock()
    enemy_unit.id = "ENEMY1"
    enemy_unit.name = "Bandit"
    enemy_unit.faction = "ENEMY"
    enemy_unit.has_acted = False
    enemy_unit.position = (3, 3)
    
    # Add units to game state
    game_state_manager.current_game_state.unit_states = {
        "PLAYER1": player_unit_active,
        "PLAYER2": player_unit_inactive,
        "ENEMY1": enemy_unit
    }
    
    # Mock get_unit to return the appropriate unit based on ID
    game_state_manager.get_unit = lambda unit_id: game_state_manager.current_game_state.unit_states.get(unit_id)
    
    # Mock get_units_by_faction to return player units
    game_state_manager.get_units_by_faction = lambda faction: [
        unit for unit in game_state_manager.current_game_state.unit_states.values() 
        if unit.faction == faction
    ]


def run_interactive_test():
    """
    Run a simple test of the interactive input system.
    
    This function initializes the interactive input system with mock components
    and runs it in a curses-based terminal UI. It sets up logging to a file,
    initializes the mock systems and units, and then runs the player turn
    through the interactive input system.
    
    This test is useful for verifying the overall functionality of the interactive
    input system in an automated way.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO, filename='interactive_input_test.log')
    
    # Set up mock systems
    mock_systems = setup_mock_systems()
    game_state_manager = mock_systems[0]
    
    # Set up mock units
    setup_mock_units(game_state_manager)
    
    # Create interactive input system
    interactive_input = InteractiveInput(auto_end_turn=True)
    
    # Initialize with mock systems
    interactive_input.initialize(*mock_systems)
    
    # Run the interactive input system
    result = interactive_input.handle_player_turn()
    
    print(f"Result: {result}")


def run_manual_test():
    """
    Run a manual test of the interactive input system.
    
    This function initializes the interactive input system with mock components
    and allows manual testing of individual key presses. It processes a predefined
    sequence of key inputs and displays the results after each input, showing the
    current state of the system.
    
    This test is useful for debugging specific input handling scenarios and for
    demonstrating how the system responds to different inputs.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO, filename='interactive_input_test.log')
    
    # Set up mock systems
    mock_systems = setup_mock_systems()
    game_state_manager = mock_systems[0]
    
    # Set up mock units
    setup_mock_units(game_state_manager)
    
    # Create interactive input system
    interactive_input = InteractiveInput(auto_end_turn=True)
    
    # Initialize with mock systems
    interactive_input.initialize(*mock_systems)
    
    # Start the player phase
    interactive_input.handler.start_player_phase()
    
    # Process some test inputs
    keys = ['KEY_RIGHT', 'KEY_DOWN', 'KEY_ENTER', 'KEY_DOWN', 'KEY_ENTER', 'a', 'KEY_ENTER']
    
    for key in keys:
        print(f"Processing key: {key}")
        result = interactive_input.process_input(key)
        print(f"Result: {result}")
        print(f"Current state: {interactive_input.get_current_state()}")
        print()


if __name__ == "__main__":
    # Uncomment one of the following to run a test
    # run_interactive_test()  # Run the full interactive test
    run_manual_test()  # Run the manual test with predefined inputs