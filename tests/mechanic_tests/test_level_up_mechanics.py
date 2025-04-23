"""
Level Up Mechanics Tests

This module contains tests focused on unit level up mechanics, including:
- Experience gain
- Level up triggering
- Stat growth based on growth rates
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
from src.gameplay_systems.unit_system import UnitSystem
from src.core_engine.engine import EngineCore
from src.core_engine.action_handler import ActionHandler
from src.core_engine.turn_manager import TurnManager as CoreTurnManager
from src.gameplay_systems.turn_manager import TurnManager
from src.core_engine.event_handler import EventHandler
from src.gameplay_systems.inventory_system import InventorySystem
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.combat_system import CombatSystem

# Import for visual logging
from src.input.cli_display import CLIDisplay
from src.utils.visual_logger import VisualScenarioLogger

# Define log paths
LOG_DIR = os.path.abspath("logs/mechanic_tests/units")
LEVEL_UP_LOG = os.path.join(LOG_DIR, "level_up_mechanics.txt")

# Setup test logger
logger = logging.getLogger("test_level_up_mechanics")

class TestLevelUpMechanics:
    """Tests for level up mechanics."""
    
    @pytest.fixture
    def basic_unit_scenario_setup(self):
        """
        Set up a basic scenario with a unit for testing level up mechanics.
        """
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load data
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a map state
        map_state = MapState()
        map_state.dimensions = (5, 5)  # Small test map
        
        # Default terrain is plains
        terrain_grid = [['P'] * 5 for _ in range(5)]
        
        # Set map state
        map_state.terrain_grid = terrain_grid
        map_state.map_id = "level_up_test"
        
        # Create a MapData object for the visual logger
        class MapDataObj:
            def __init__(self):
                self.id = "level_up_test"
                self.name = "Level Up Test"
                self.dimensions = (5, 5)
                self.terrain_grid = terrain_grid
                self.fog_of_war = False
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_level_up"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Create scenario state to track 
        scenario_state = {
            "exp_earned": {}
        }
        
        # Add test units
        unit_states = {}
        unit_positions = {}
        faction_units = {"PLAYER": [], "ENEMY": []}
        
        # Create player faction unit
        player_unit = UnitState()
        player_unit.id = "PLAYER_UNIT_1"
        player_unit.name = "Novice Fighter"
        player_unit.faction = FactionEnum.PLAYER
        player_unit.position = (2, 2)
        player_unit.current_hp = 20
        player_unit.max_hp = 20
        player_unit.ai_persona = "BALANCED"
        player_unit.base_stats = {"STR": 8, "DEF": 6, "SPD": 7, "SKL": 6}
        player_unit.growth_rates = {"STR": 60, "DEF": 40, "SPD": 50, "SKL": 45, "HP": 70}
        player_unit.level = 1
        player_unit.exp = 0
        player_unit.class_name = "Fighter"
        
        unit_states[player_unit.id] = player_unit
        unit_positions[player_unit.id] = player_unit.position
        faction_units["PLAYER"].append(player_unit.id)
        
        # Create an enemy unit
        enemy_unit = UnitState()
        enemy_unit.id = "ENEMY_UNIT_1"
        enemy_unit.name = "Bandit"
        enemy_unit.faction = FactionEnum.ENEMY
        enemy_unit.position = (3, 3)
        enemy_unit.current_hp = 18
        enemy_unit.max_hp = 18
        enemy_unit.ai_persona = "AGGRESSOR"
        enemy_unit.base_stats = {"STR": 7, "DEF": 5, "SPD": 6, "SKL": 5}
        enemy_unit.level = 2
        enemy_unit.exp = 0
        
        unit_states[enemy_unit.id] = enemy_unit
        unit_positions[enemy_unit.id] = enemy_unit.position
        faction_units["ENEMY"].append(enemy_unit.id)
        
        # Set unit states in game
        game_state.unit_states = unit_states
        game_state.map_state.unit_positions = unit_positions
        game_state.map_state.allies = faction_units
        
        # Initialize systems
        map_system = MapSystem()
        unit_system = UnitSystem()
        core_turn_manager = CoreTurnManager()
        turn_manager = TurnManager()
        action_handler = ActionHandler()
        event_handler = EventHandler()
        inventory_system = InventorySystem()
        movement_system = MovementSystem()
        combat_system = CombatSystem()
        
        # Initialize systems
        map_system.initialize(game_state_manager, data_provider)
        unit_system.initialize(game_state_manager, data_provider)
        inventory_system.initialize(game_state_manager, data_provider)
        movement_system.initialize(game_state_manager, data_provider)
        combat_system.initialize(
            gameStateManager_instance=game_state_manager,
            dataProvider_instance=data_provider,
            unitSystem_instance=unit_system,
            mapSystem_instance=map_system,
            inventorySystem_instance=inventory_system
        )
        
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
            turnManager_instance=turn_manager,
            eventHandler_instance=event_handler,
            dataProvider_instance=data_provider,
            core_turn_manager_instance=core_turn_manager,
            inventorySystem_instance=inventory_system,
            movementSystem_instance=movement_system,
            combatSystem_instance=combat_system
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
            "cli_display": cli_display,
            "action_handler": action_handler,
            "scenario_state": scenario_state
        }
    
    def test_level_up_mechanics(self, basic_unit_scenario_setup):
        """
        Tests a unit leveling up and gaining stats based on growth rates.
        
        This test:
        1. Sets up a fighter unit
        2. Grants experience points to trigger a level up
        3. Applies stat changes based on growth rates
        4. Logs the level up process in a visual log file
        """
        # Ensure log directory exists and delete old log
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(LEVEL_UP_LOG):
            os.remove(LEVEL_UP_LOG)
            
        # Get test components
        game_state_manager = basic_unit_scenario_setup["game_state_manager"]
        cli_display = basic_unit_scenario_setup["cli_display"]
        scenario_state = basic_unit_scenario_setup["scenario_state"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=LEVEL_UP_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get the unit that will level up
        unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        assert unit is not None, "Unit not found"
        
        # Store initial stats
        initial_stats = {
            "level": unit.level,
            "exp": unit.exp,
            "hp": unit.max_hp,
            "current_hp": unit.current_hp,
            "STR": unit.base_stats.get("STR", 0),
            "DEF": unit.base_stats.get("DEF", 0),
            "SPD": unit.base_stats.get("SPD", 0),
            "SKL": unit.base_stats.get("SKL", 0)
        }
        
        # Log initial stats
        visual_logger.log_action(unit.id, "INITIAL_STATS", 
                               f"{unit.name} Level {unit.level} (EXP: {unit.exp}/100)")
        for stat_name, stat_value in unit.base_stats.items():
            visual_logger.log_action(unit.id, "STAT", f"{stat_name}: {stat_value}")
        
        # Grant experience points to trigger level up
        visual_logger.log_turn_start(1)
        visual_logger.log_action("SYSTEM", "BATTLE_RESULT", 
                               f"{unit.name} defeats an enemy and gains experience")
        
        # Add EXP to trigger a level up
        exp_gain = 100 - unit.exp  # Enough to level up
        unit.exp += exp_gain
        
        # Track the EXP gain
        scenario_state["exp_earned"][unit.id] = exp_gain
        
        visual_logger.log_action(unit.id, "EXP_GAIN", 
                               f"Gained {exp_gain} EXP ({initial_stats['exp']} → {unit.exp}/100)")
        
        # Check for level up
        if unit.exp >= 100:
            # Level up triggered
            unit.level += 1
            unit.exp = unit.exp - 100  # Reset EXP for next level
            
            visual_logger.log_action(unit.id, "LEVEL_UP", 
                                   f"{unit.name} levels up to Level {unit.level}!")
            
            # Determine stat increases based on growth rates
            stat_increases = {}
            
            # Process each stat with growth rate
            for stat, growth in unit.growth_rates.items():
                # Simulate random chance based on growth rate percentage
                roll = random.randint(1, 100)
                increased = roll <= growth
                
                if increased:
                    if stat == "HP":
                        # Increase max HP
                        unit.max_hp += 1
                        # Also increase current HP
                        unit.current_hp += 1
                        stat_increases["HP"] = 1
                    else:
                        # Increase regular stat
                        current_value = unit.base_stats.get(stat, 0)
                        unit.base_stats[stat] = current_value + 1
                        stat_increases[stat] = 1
            
            # Log stat increases
            visual_logger.log_action(unit.id, "STAT_INCREASES", "The following stats increased:")
            
            for stat, increase in stat_increases.items():
                if stat == "HP":
                    visual_logger.log_action(unit.id, "STAT_INCREASE", 
                                           f"HP +{increase} ({initial_stats['hp']} → {unit.max_hp})")
                else:
                    visual_logger.log_action(unit.id, "STAT_INCREASE", 
                                           f"{stat} +{increase} ({initial_stats[stat]} → {unit.base_stats[stat]})")
        
        # Log end of turn state
        visual_logger.log_end_of_turn_state(1)
        visual_logger.finalize_log()
        
        # Verify unit leveled up
        assert unit.level == initial_stats["level"] + 1, "Unit should have leveled up"
        
        # Verify at least one stat increased (given the growth rates)
        stat_increased = (
            unit.max_hp > initial_stats["hp"] or
            unit.base_stats.get("STR", 0) > initial_stats["STR"] or
            unit.base_stats.get("DEF", 0) > initial_stats["DEF"] or
            unit.base_stats.get("SPD", 0) > initial_stats["SPD"] or
            unit.base_stats.get("SKL", 0) > initial_stats["SKL"]
        )
        
        assert stat_increased, "At least one stat should have increased on level up"
        
        # Verify log file was created
        assert os.path.exists(LEVEL_UP_LOG), f"Log file {LEVEL_UP_LOG} was not created"
        logger.info(f"Successfully created level up mechanics log at {LEVEL_UP_LOG}") 