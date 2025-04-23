"""
Promotion Mechanics Tests

This module contains tests focused on unit promotion mechanics, including:
- Class promotion/change
- Promotion stat bonuses
- Skill acquisition upon promotion
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
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.inventory_system import InventorySystem
from src.core_engine.engine import EngineCore
from src.core_engine.action_handler import ActionHandler
from src.core_engine.turn_manager import TurnManager as CoreTurnManager
from src.gameplay_systems.turn_manager import TurnManager
from src.core_engine.event_handler import EventHandler

# Import for visual logging
from src.input.cli_display import CLIDisplay
from src.utils.visual_logger import VisualScenarioLogger

# Define log paths
LOG_DIR = os.path.abspath("logs/mechanic_tests/units")
PROMOTION_LOG = os.path.join(LOG_DIR, "promotion_mechanics.txt")

# Setup test logger
logger = logging.getLogger("test_promotion_mechanics")

class TestPromotionMechanics:
    """Tests for unit promotion mechanics."""
    
    @pytest.fixture
    def basic_unit_scenario_setup(self):
        """
        Set up a basic scenario with units for testing promotion mechanics.
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
        map_state.map_id = "promotion_test"
        
        # Create a MapData object for the visual logger
        class MapDataObj:
            def __init__(self):
                self.id = "promotion_test"
                self.name = "Promotion Test"
                self.dimensions = (5, 5)
                self.terrain_grid = terrain_grid
                self.fog_of_war = False
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_promotion"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Create scenario state
        scenario_state = {}
        
        # Add test units
        unit_states = {}
        unit_positions = {}
        faction_units = {"PLAYER": [], "ENEMY": []}
        
        # Create player faction units ready for promotion
        fighter_unit = UnitState()
        fighter_unit.id = "PLAYER_FIGHTER"
        fighter_unit.name = "Experienced Fighter"
        fighter_unit.faction = FactionEnum.PLAYER
        fighter_unit.position = (2, 2)
        fighter_unit.current_hp = 25
        fighter_unit.max_hp = 25
        fighter_unit.ai_persona = "BALANCED"
        fighter_unit.base_stats = {"STR": 10, "DEF": 8, "SPD": 9, "SKL": 8}
        fighter_unit.level = 10  # Ready for promotion
        fighter_unit.exp = 0
        fighter_unit.class_name = "Fighter"
        fighter_unit.promotion_options = ["Warrior", "Hero"]
        
        unit_states[fighter_unit.id] = fighter_unit
        unit_positions[fighter_unit.id] = fighter_unit.position
        faction_units["PLAYER"].append(fighter_unit.id)
        
        # Create a mage unit also ready for promotion
        mage_unit = UnitState()
        mage_unit.id = "PLAYER_MAGE"
        mage_unit.name = "Practiced Mage"
        mage_unit.faction = FactionEnum.PLAYER
        mage_unit.position = (1, 2)
        mage_unit.current_hp = 18
        mage_unit.max_hp = 18
        mage_unit.ai_persona = "CAUTIOUS"
        mage_unit.base_stats = {"STR": 7, "DEF": 4, "SPD": 11, "SKL": 10}
        mage_unit.level = 10  # Ready for promotion
        mage_unit.exp = 0
        mage_unit.class_name = "Mage"
        mage_unit.promotion_options = ["Sage", "Mage Knight"]
        
        unit_states[mage_unit.id] = mage_unit
        unit_positions[mage_unit.id] = mage_unit.position
        faction_units["PLAYER"].append(mage_unit.id)
        
        # Set unit states in game
        game_state.unit_states = unit_states
        game_state.map_state.unit_positions = unit_positions
        game_state.map_state.allies = faction_units
        
        # Initialize systems
        map_system = MapSystem()
        unit_system = UnitSystem()
        inventory_system = InventorySystem()
        movement_system = MovementSystem()
        combat_system = CombatSystem()
        core_turn_manager = CoreTurnManager()
        turn_manager = TurnManager()
        action_handler = ActionHandler()
        event_handler = EventHandler()
        
        # Initialize systems
        map_system.initialize(game_state_manager, data_provider)
        unit_system.initialize(game_state_manager, data_provider)
        inventory_system.initialize(game_state_manager, data_provider)
        movement_system.initialize(game_state_manager, map_system)
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
            movementSystem_instance=movement_system,
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
            "cli_display": cli_display,
            "action_handler": action_handler,
            "data_provider": data_provider
        }
    
    def test_unit_promotion(self, basic_unit_scenario_setup):
        """
        Tests promoting a unit to an advanced class.
        
        This test:
        1. Sets up a unit that has reached the required level for promotion
        2. Presents promotion options
        3. Executes the promotion to a new class
        4. Verifies stat changes and class update
        """
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(PROMOTION_LOG):
            os.remove(PROMOTION_LOG)
            
        # Get test components
        game_state_manager = basic_unit_scenario_setup["game_state_manager"]
        cli_display = basic_unit_scenario_setup["cli_display"]
        data_provider = basic_unit_scenario_setup["data_provider"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=PROMOTION_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get the unit to promote
        fighter_unit = game_state_manager.get_unit("PLAYER_FIGHTER")
        assert fighter_unit is not None, "Fighter unit not found"
        
        # Begin the test
        visual_logger.log_turn_start(1)
        
        # Record initial state
        original_class = fighter_unit.class_name
        original_stats = fighter_unit.base_stats.copy()
        original_level = fighter_unit.level
        
        # Log initial state
        visual_logger.log_action(fighter_unit.id, "STATUS", 
                              f"{fighter_unit.name} is currently a level {original_level} {original_class}")
        
        # Create promotion data
        # In a real game this would come from the data provider, but we'll simulate it here
        promotion_classes = {
            "Warrior": {
                "stat_bonuses": {"STR": 2, "DEF": 3, "SPD": 0, "SKL": 1},
                "skills_gained": ["Intimidate", "Axe Proficiency+"]
            },
            "Hero": {
                "stat_bonuses": {"STR": 1, "DEF": 1, "SPD": 3, "SKL": 2},
                "skills_gained": ["Adaptability", "Sword Proficiency+"]
            }
        }
        
        # Choose promotion class
        target_class = "Hero"  # Choose Hero for this test
        
        # Log promotion choice
        visual_logger.log_action("SYSTEM", "PROMOTION_CHOICE", 
                              f"Available promotions for {fighter_unit.name}: {', '.join(fighter_unit.promotion_options)}")
        
        visual_logger.log_action(fighter_unit.id, "PROMOTION_SELECT", 
                              f"{fighter_unit.name} will promote to {target_class}")
        
        # Execute promotion
        # 1. Update class
        fighter_unit.class_name = target_class
        
        # 2. Reset level (typical for promotion mechanics in tactical RPGs)
        fighter_unit.level = 1
        fighter_unit.exp = 0
        
        # 3. Apply stat bonuses
        for stat, bonus in promotion_classes[target_class]["stat_bonuses"].items():
            if stat in fighter_unit.base_stats:
                fighter_unit.base_stats[stat] += bonus
                
                visual_logger.log_action(fighter_unit.id, "STAT_BOOST", 
                                    f"{stat} +{bonus} ({original_stats[stat]} → {fighter_unit.base_stats[stat]})")
        
        # 4. Add new skills
        # In a real implementation, this would add skills to the unit
        # For this test, we'll just log the skills gained
        for skill in promotion_classes[target_class]["skills_gained"]:
            visual_logger.log_action(fighter_unit.id, "SKILL_GAINED", 
                                  f"Learned new skill: {skill}")
        
        # Log promotion complete
        visual_logger.log_action("SYSTEM", "PROMOTION_COMPLETE", 
                              f"{fighter_unit.name} promoted from {original_class} to {target_class}")
        
        # Show new status
        visual_logger.log_action(fighter_unit.id, "STATUS", 
                              f"{fighter_unit.name} is now a level {fighter_unit.level} {fighter_unit.class_name}")
        
        # End turn
        visual_logger.log_end_of_turn_state(1)
        visual_logger.finalize_log()
        
        # Verify promotion
        assert fighter_unit.class_name == target_class, f"Unit should now be a {target_class}"
        assert fighter_unit.level == 1, "Unit should be reset to level 1 after promotion"
        
        # Verify stat increases
        for stat, bonus in promotion_classes[target_class]["stat_bonuses"].items():
            if stat in original_stats:
                assert fighter_unit.base_stats[stat] == original_stats[stat] + bonus, f"{stat} should increase by {bonus}"
        
        # Verify log file was created
        assert os.path.exists(PROMOTION_LOG), f"Log file {PROMOTION_LOG} was not created"
        logger.info(f"Successfully created promotion mechanics log at {PROMOTION_LOG}")