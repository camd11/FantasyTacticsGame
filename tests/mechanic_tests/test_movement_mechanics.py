"""
Movement Mechanics Tests

This module contains tests focused on unit movement mechanics, including:
- Basic movement
- Terrain movement costs
- Elevation changes
- Movement ranges
"""

import os
import pytest
import logging
from typing import Dict, Any, Tuple
import random

# Import necessary core modules
from src.core_engine.game_state import GameStateManager, FactionEnum, GameState, MapState, UnitState, DispositionEnum
from src.core_engine.data_provider import DataProvider
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.inventory_system import InventorySystem
from src.gameplay_systems.combat_system import CombatSystem
from src.core_engine.engine import EngineCore
from src.core_engine.action_handler import ActionHandler
from src.core_engine.turn_manager import TurnManager as CoreTurnManager
from src.gameplay_systems.turn_manager import TurnManager
from src.core_engine.event_handler import EventHandler

# Import for visual logging
from src.input.cli_display import CLIDisplay
from src.utils.visual_logger import VisualScenarioLogger

# Define log paths
LOG_DIR = os.path.abspath("logs/mechanic_tests/movement")
BASIC_MOVE_LOG = os.path.join(LOG_DIR, "basic_move.txt")
TERRAIN_MOVE_LOG = os.path.join(LOG_DIR, "terrain_cost_move.txt")

# Setup test logger
logger = logging.getLogger("test_movement_mechanics")

class TestMovementMechanics:
    """Tests for movement-related mechanics."""
    
    @pytest.fixture
    def basic_scenario_setup(self):
        """
        Set up a basic scenario with a simple 5x5 map and one unit.
        """
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load data
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a simple map state
        map_state = MapState()
        map_state.dimensions = (5, 5)  # Small test map
        
        # Default terrain is plains
        terrain_grid = [['P'] * 5 for _ in range(5)]
        
        # Set map state
        map_state.terrain_grid = terrain_grid
        map_state.map_id = "basic_movement_test"
        
        # Create a MapData object for the visual logger
        class MapDataObj:
            def __init__(self):
                self.id = "basic_movement_test"
                self.name = "Basic Movement Test"
                self.dimensions = (5, 5)
                self.terrain_grid = terrain_grid
                self.fog_of_war = False
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_movement_basic"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Add a test unit
        unit_states = {}
        unit_positions = {}
        
        # Create a player unit
        unit = UnitState()
        unit.id = "PLAYER_UNIT_1"
        unit.name = "Test Unit"
        unit.faction = FactionEnum.PLAYER
        unit.position = (1, 1)  # Starting position
        unit.current_hp = 20
        unit.max_hp = 20
        unit.ai_persona = "BALANCED"
        unit.base_stats = {"STR": 10, "DEF": 10, "SPD": 10, "SKL": 10}
        
        # Add unit to collections
        unit_states[unit.id] = unit
        unit_positions[unit.id] = unit.position
        
        # Add to faction list
        faction_units = {"PLAYER": [unit.id]}
        
        # Set unit states in game
        game_state.unit_states = unit_states
        game_state.map_state.unit_positions = unit_positions
        game_state.map_state.allies = faction_units
        
        # Initialize systems
        map_system = MapSystem()
        unit_system = UnitSystem()
        movement_system = MovementSystem()
        core_turn_manager = CoreTurnManager()
        turn_manager = TurnManager()
        action_handler = ActionHandler()
        event_handler = EventHandler()
        inventory_system = InventorySystem()
        combat_system = CombatSystem()
        
        # Initialize map system first
        map_system.initialize(game_state_manager, data_provider)
        
        # Initialize unit system
        unit_system.initialize(game_state_manager, data_provider)
        
        # Initialize inventory system
        inventory_system.initialize(game_state_manager, data_provider)
        
        # Initialize combat system
        combat_system.initialize(
            gameStateManager_instance=game_state_manager,
            dataProvider_instance=data_provider,
            unitSystem_instance=unit_system,
            mapSystem_instance=map_system,
            inventorySystem_instance=inventory_system
        )
        
        # Initialize movement system
        movement_system.initialize(game_state_manager, map_system)
        
        # Initialize turn managers
        core_turn_manager.initialize(game_state_manager)
        turn_manager.initialize(
            core_turn_manager=core_turn_manager,
            gameStateManager_instance=game_state_manager
        )
        
        # Initialize event handler
        event_handler.initialize(
            gameStateManager_instance=game_state_manager,
            turnManager_instance=turn_manager,
            unitSystem_instance=unit_system,
            mapSystem_instance=map_system,
            dataProvider_instance=data_provider,
            inventorySystem_instance=inventory_system
        )
        
        # Initialize action handler
        action_handler.initialize(
            gameStateManager_instance=game_state_manager,
            unitSystem_instance=unit_system,
            mapSystem_instance=map_system,
            movementSystem_instance=movement_system,
            turnManager_instance=turn_manager,
            eventHandler_instance=event_handler,
            dataProvider_instance=data_provider,
            core_turn_manager_instance=core_turn_manager,
            combatSystem_instance=combat_system,
            inventorySystem_instance=inventory_system
        )
        
        # Initialize CLIDisplay for visual logging
        cli_display = CLIDisplay()
        cli_display.game_state_manager = game_state_manager
        cli_display.map_system = map_system
        cli_display.unit_system = unit_system
        cli_display.data_provider = data_provider
        
        # Return components
        return {
            "game_state_manager": game_state_manager,
            "map_system": map_system,
            "unit_system": unit_system,
            "movement_system": movement_system,
            "cli_display": cli_display,
            "action_handler": action_handler
        }
    
    def test_basic_movement_log(self, basic_scenario_setup):
        """
        Tests basic unit movement and logs it visually.
        
        This test:
        1. Sets up a 5x5 map with plains terrain
        2. Places a single unit at position (1,1)
        3. Moves the unit to position (3,3)
        4. Logs the movement in a visual log file
        """
        # Ensure log directory exists and delete old log
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(BASIC_MOVE_LOG):
            os.remove(BASIC_MOVE_LOG)
        
        # Get test components
        game_state_manager = basic_scenario_setup["game_state_manager"]
        cli_display = basic_scenario_setup["cli_display"]
        movement_system = basic_scenario_setup["movement_system"]
        
        # Get the test unit
        unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        assert unit is not None, "Test unit not found"
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=BASIC_MOVE_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Record the unit's original position
        original_position = unit.position
        logger.info(f"Unit {unit.name} starting at position {original_position}")
        
        # Define the target position
        target_position = (3, 3)
        
        # Move the unit to the target position
        # This would normally be done through the action handler, but for test simplicity:
        movement_system.move_unit(unit, target_position)
        
        # Log the movement action
        visual_logger.log_action(unit.id, "MOVE", f"from {original_position} to {target_position}")
        
        # Log the end state
        visual_logger.log_end_of_turn_state(1)
        visual_logger.finalize_log()
        
        # Verify the unit moved
        assert unit.position == target_position, f"Unit should be at {target_position} but is at {unit.position}"
        
        # Verify log file was created
        assert os.path.exists(BASIC_MOVE_LOG), f"Log file {BASIC_MOVE_LOG} was not created"
        logger.info(f"Successfully created movement log at {BASIC_MOVE_LOG}")

    # Additional test methods would go here:
    # def test_terrain_cost_movement_log(self, terrain_scenario_setup):
    #     """Tests movement across different terrain types with varying costs."""
    #     ...
    
    # @pytest.fixture
    # def terrain_scenario_setup(self):
    #     """Set up a scenario with various terrain types for movement testing."""
    #     ... 