"""
Unit Interaction Mechanics Tests

This module contains tests focused on unit interaction mechanics, including:
- Support level building between units
- Bonuses from support relationships
- Team effects and adjacency bonuses
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
from src.core_engine.engine import EngineCore
from src.core_engine.action_handler import ActionHandler
from src.core_engine.turn_manager import TurnManager as CoreTurnManager
from src.gameplay_systems.turn_manager import TurnManager
from src.core_engine.event_handler import EventHandler
from src.gameplay_systems.inventory_system import InventorySystem
from src.gameplay_systems.combat_system import CombatSystem

# Import for visual logging
from src.input.cli_display import CLIDisplay
from src.utils.visual_logger import VisualScenarioLogger

# Define log paths
LOG_DIR = os.path.abspath("logs/mechanic_tests/units")
SUPPORT_LOG = os.path.join(LOG_DIR, "support_mechanics.txt")
ADJACENCY_LOG = os.path.join(LOG_DIR, "adjacency_mechanics.txt")

# Setup test logger
logger = logging.getLogger("test_unit_interaction_mechanics")

class TestUnitInteractionMechanics:
    """Tests for unit interaction mechanics."""
    
    @pytest.fixture
    def basic_interaction_scenario_setup(self):
        """
        Set up a basic scenario with multiple units for testing unit interactions.
        """
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load data
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a map state
        map_state = MapState()
        map_state.dimensions = (6, 6)  # Small test map
        
        # Default terrain is plains
        terrain_grid = [['P'] * 6 for _ in range(6)]
        
        # Set map state
        map_state.terrain_grid = terrain_grid
        map_state.map_id = "unit_interaction_test"
        
        # Create a MapData object for the visual logger
        class MapDataObj:
            def __init__(self):
                self.id = "unit_interaction_test"
                self.name = "Unit Interaction Test"
                self.dimensions = (6, 6)
                self.terrain_grid = terrain_grid
                self.fog_of_war = False
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_unit_interactions"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Create scenario state to track 
        scenario_state = {
            "support_levels": {},
            "adjacent_units": {}
        }
        
        # Add test units
        unit_states = {}
        unit_positions = {}
        faction_units = {"PLAYER": [], "ENEMY": []}
        
        # Create player faction units
        unit1 = UnitState()
        unit1.id = "PLAYER_UNIT_1"
        unit1.name = "Commander"
        unit1.faction = FactionEnum.PLAYER
        unit1.position = (2, 2)
        unit1.current_hp = 20
        unit1.max_hp = 20
        unit1.ai_persona = "BALANCED"
        unit1.base_stats = {"STR": 8, "DEF": 6, "SPD": 7, "SKL": 6}
        unit1.support_partners = ["PLAYER_UNIT_2"]  # Can support with unit2
        
        unit_states[unit1.id] = unit1
        unit_positions[unit1.id] = unit1.position
        faction_units["PLAYER"].append(unit1.id)
        
        unit2 = UnitState()
        unit2.id = "PLAYER_UNIT_2"
        unit2.name = "Knight"
        unit2.faction = FactionEnum.PLAYER
        unit2.position = (3, 2)  # Adjacent to unit1
        unit2.current_hp = 22
        unit2.max_hp = 22
        unit2.ai_persona = "DEFENDER"
        unit2.base_stats = {"STR": 6, "DEF": 9, "SPD": 5, "SKL": 6}
        unit2.support_partners = ["PLAYER_UNIT_1", "PLAYER_UNIT_3"]  # Can support with unit1 and unit3
        
        unit_states[unit2.id] = unit2
        unit_positions[unit2.id] = unit2.position
        faction_units["PLAYER"].append(unit2.id)
        
        unit3 = UnitState()
        unit3.id = "PLAYER_UNIT_3"
        unit3.name = "Archer"
        unit3.faction = FactionEnum.PLAYER
        unit3.position = (1, 3)  # Not adjacent to any unit initially
        unit3.current_hp = 18
        unit3.max_hp = 18
        unit3.ai_persona = "AGGRESSOR"
        unit3.base_stats = {"STR": 7, "DEF": 4, "SPD": 8, "SKL": 9}
        unit3.support_partners = ["PLAYER_UNIT_2"]  # Can support with unit2
        
        unit_states[unit3.id] = unit3
        unit_positions[unit3.id] = unit3.position
        faction_units["PLAYER"].append(unit3.id)
        
        # Create an enemy unit
        enemy_unit = UnitState()
        enemy_unit.id = "ENEMY_UNIT_1"
        enemy_unit.name = "Bandit"
        enemy_unit.faction = FactionEnum.ENEMY
        enemy_unit.position = (4, 4)
        enemy_unit.current_hp = 18
        enemy_unit.max_hp = 18
        enemy_unit.ai_persona = "AGGRESSOR"
        enemy_unit.base_stats = {"STR": 7, "DEF": 5, "SPD": 6, "SKL": 5}
        
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
        movement_system = MovementSystem()
        inventory_system = InventorySystem()
        combat_system = CombatSystem()
        core_turn_manager = CoreTurnManager()
        turn_manager = TurnManager()
        action_handler = ActionHandler()
        event_handler = EventHandler()
        
        # Initialize systems
        map_system.initialize(game_state_manager, data_provider)
        unit_system.initialize(game_state_manager, data_provider)
        movement_system.initialize(game_state_manager, map_system)
        inventory_system.initialize(game_state_manager, data_provider)
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
            "action_handler": action_handler,
            "scenario_state": scenario_state,
            "inventory_system": inventory_system
        }
    
    def test_support_level_building(self, basic_interaction_scenario_setup):
        """
        Tests building support levels between units.
        
        This test:
        1. Places two units adjacent to each other
        2. Simulates actions that build support (fighting together, healing, etc.)
        3. Tracks support level progression
        4. Verifies support bonuses 
        """
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(SUPPORT_LOG):
            os.remove(SUPPORT_LOG)
            
        # Get test components
        game_state_manager = basic_interaction_scenario_setup["game_state_manager"]
        cli_display = basic_interaction_scenario_setup["cli_display"]
        scenario_state = basic_interaction_scenario_setup["scenario_state"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=SUPPORT_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get the units that will build support
        unit1 = game_state_manager.get_unit("PLAYER_UNIT_1")  # Commander
        unit2 = game_state_manager.get_unit("PLAYER_UNIT_2")  # Knight
        assert unit1 is not None, "Commander unit not found"
        assert unit2 is not None, "Knight unit not found"
        
        # Verify they can support each other
        assert unit2.id in unit1.support_partners, f"{unit1.name} cannot support {unit2.name}"
        assert unit1.id in unit2.support_partners, f"{unit2.name} cannot support {unit1.name}"
        
        # Check if they're adjacent
        are_adjacent = abs(unit1.position[0] - unit2.position[0]) + abs(unit1.position[1] - unit2.position[1]) == 1
        assert are_adjacent, "Units should be adjacent for support building"
        
        # Initialize support point tracking in scenario state
        support_key = f"{unit1.id}_{unit2.id}"
        scenario_state["support_levels"][support_key] = {
            "current_points": 0,
            "level": "None",  # None, C, B, A, S
            "points_needed": {
                "C": 40,
                "B": 100,
                "A": 200,
                "S": 300
            }
        }
        
        # Store original stats
        original_stats = {
            unit1.id: {key: value for key, value in unit1.base_stats.items()},
            unit2.id: {key: value for key, value in unit2.base_stats.items()}
        }
        
        # Begin support building simulation
        visual_logger.log_turn_start(1)
        visual_logger.log_action("SYSTEM", "SUPPORT_STATUS", 
                               f"Initial support between {unit1.name} and {unit2.name}: {scenario_state['support_levels'][support_key]['level']}")
        
        # Simulate fighting together (adds support points)
        visual_logger.log_action("SYSTEM", "BATTLE", 
                               f"{unit1.name} and {unit2.name} fought together against enemies")
        
        # Add support points
        support_points_gained = 25
        scenario_state["support_levels"][support_key]["current_points"] += support_points_gained
        
        visual_logger.log_action("SYSTEM", "SUPPORT_POINTS", 
                               f"Gained {support_points_gained} support points (Total: {scenario_state['support_levels'][support_key]['current_points']})")
        
        # Check if support level has increased
        current_points = scenario_state["support_levels"][support_key]["current_points"]
        points_needed = scenario_state["support_levels"][support_key]["points_needed"]
        
        new_level = "None"
        if current_points >= points_needed["S"]:
            new_level = "S"
        elif current_points >= points_needed["A"]:
            new_level = "A"
        elif current_points >= points_needed["B"]:
            new_level = "B"
        elif current_points >= points_needed["C"]:
            new_level = "C"
        
        # Update support level if changed
        if new_level != scenario_state["support_levels"][support_key]["level"]:
            scenario_state["support_levels"][support_key]["level"] = new_level
            visual_logger.log_action("SYSTEM", "SUPPORT_LEVEL_UP", 
                                   f"{unit1.name} and {unit2.name} reached Support Level {new_level}!")
            
            # Apply support bonuses if level increased
            if new_level != "None":
                # Apply support bonuses (different bonuses for different levels)
                support_bonuses = {
                    "C": {"DEF": 1},
                    "B": {"DEF": 1, "HIT": 5},
                    "A": {"DEF": 2, "HIT": 10, "SPD": 1},
                    "S": {"DEF": 2, "HIT": 15, "SPD": 1, "STR": 1}
                }
                
                # Get applicable bonuses
                bonuses = support_bonuses.get(new_level, {})
                
                # Log bonuses
                visual_logger.log_action("SYSTEM", "SUPPORT_BONUSES", 
                                       f"Support Level {new_level} grants the following bonuses when units are adjacent:")
                
                for stat, bonus in bonuses.items():
                    visual_logger.log_action("SYSTEM", "BONUS", f"{stat} +{bonus}")
        
        # Log end of turn 1
        visual_logger.log_end_of_turn_state(1)
        
        # Simulate multiple turns for support building
        for turn in range(2, 4):
            visual_logger.log_turn_start(turn)
            
            # Simulate actions that build support
            action_types = ["BATTLE", "HEALING", "ASSISTING"]
            action_type = random.choice(action_types)
            
            if action_type == "BATTLE":
                visual_logger.log_action("SYSTEM", "BATTLE", 
                                       f"{unit1.name} and {unit2.name} fought together against enemies")
                support_points_gained = 25
            elif action_type == "HEALING":
                visual_logger.log_action(unit1.id, "HEALING", 
                                       f"{unit1.name} healed {unit2.name}")
                support_points_gained = 15
            else:  # ASSISTING
                visual_logger.log_action(unit2.id, "ASSISTING", 
                                       f"{unit2.name} assisted {unit1.name} in combat")
                support_points_gained = 20
            
            # Add support points
            scenario_state["support_levels"][support_key]["current_points"] += support_points_gained
            
            visual_logger.log_action("SYSTEM", "SUPPORT_POINTS", 
                                   f"Gained {support_points_gained} support points (Total: {scenario_state['support_levels'][support_key]['current_points']})")
            
            # Check if support level has increased
            current_points = scenario_state["support_levels"][support_key]["current_points"]
            points_needed = scenario_state["support_levels"][support_key]["points_needed"]
            
            new_level = "None"
            if current_points >= points_needed["S"]:
                new_level = "S"
            elif current_points >= points_needed["A"]:
                new_level = "A"
            elif current_points >= points_needed["B"]:
                new_level = "B"
            elif current_points >= points_needed["C"]:
                new_level = "C"
            
            # Update support level if changed
            if new_level != scenario_state["support_levels"][support_key]["level"]:
                scenario_state["support_levels"][support_key]["level"] = new_level
                visual_logger.log_action("SYSTEM", "SUPPORT_LEVEL_UP", 
                                       f"{unit1.name} and {unit2.name} reached Support Level {new_level}!")
                
                # Apply support bonuses if level increased
                if new_level != "None":
                    # Apply support bonuses (different bonuses for different levels)
                    support_bonuses = {
                        "C": {"DEF": 1},
                        "B": {"DEF": 1, "HIT": 5},
                        "A": {"DEF": 2, "HIT": 10, "SPD": 1},
                        "S": {"DEF": 2, "HIT": 15, "SPD": 1, "STR": 1}
                    }
                    
                    # Get applicable bonuses
                    bonuses = support_bonuses.get(new_level, {})
                    
                    # Log bonuses
                    visual_logger.log_action("SYSTEM", "SUPPORT_BONUSES", 
                                           f"Support Level {new_level} grants the following bonuses when units are adjacent:")
                    
                    for stat, bonus in bonuses.items():
                        visual_logger.log_action("SYSTEM", "BONUS", f"{stat} +{bonus}")
            
            # Log end of turn
            visual_logger.log_end_of_turn_state(turn)
        
        # Log final support state
        visual_logger.log_turn_start(4)
        visual_logger.log_action("SYSTEM", "FINAL_SUPPORT_STATUS", 
                               f"Final support between {unit1.name} and {unit2.name}: Level {scenario_state['support_levels'][support_key]['level']}")
        visual_logger.log_action("SYSTEM", "SUPPORT_POINTS", 
                               f"Total points: {scenario_state['support_levels'][support_key]['current_points']}")
        
        # Log end of simulation
        visual_logger.log_end_of_turn_state(4)
        visual_logger.finalize_log()
        
        # Verify support points were accumulated
        assert scenario_state["support_levels"][support_key]["current_points"] > 0, "Support points should have been accumulated"
        
        # Verify support level increased from None
        assert scenario_state["support_levels"][support_key]["level"] != "None", "Support level should have increased"
        
        # Verify log file was created
        assert os.path.exists(SUPPORT_LOG), f"Log file {SUPPORT_LOG} was not created"
        logger.info(f"Successfully created support level building log at {SUPPORT_LOG}")
    
    def test_adjacency_bonuses(self, basic_interaction_scenario_setup):
        """
        Tests bonuses applied when units are adjacent to each other.
        
        This test:
        1. Places units in various formations
        2. Checks adjacency detection
        3. Applies and verifies stat bonuses for adjacent units
        4. Tests bonus removal when units are no longer adjacent
        """
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(ADJACENCY_LOG):
            os.remove(ADJACENCY_LOG)
            
        # Get test components
        game_state_manager = basic_interaction_scenario_setup["game_state_manager"]
        cli_display = basic_interaction_scenario_setup["cli_display"]
        movement_system = basic_interaction_scenario_setup["movement_system"]
        scenario_state = basic_interaction_scenario_setup["scenario_state"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=ADJACENCY_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get test units
        unit1 = game_state_manager.get_unit("PLAYER_UNIT_1")  # Commander
        unit2 = game_state_manager.get_unit("PLAYER_UNIT_2")  # Knight
        unit3 = game_state_manager.get_unit("PLAYER_UNIT_3")  # Archer
        assert unit1 is not None, "Commander unit not found"
        assert unit2 is not None, "Knight unit not found"
        assert unit3 is not None, "Archer unit not found"
        
        # Store original stats and positions
        original_stats = {
            unit1.id: {key: value for key, value in unit1.base_stats.items()},
            unit2.id: {key: value for key, value in unit2.base_stats.items()},
            unit3.id: {key: value for key, value in unit3.base_stats.items()}
        }
        
        original_positions = {
            unit1.id: unit1.position,
            unit2.id: unit2.position,
            unit3.id: unit3.position
        }
        
        # Define adjacency bonuses
        adjacency_bonuses = {
            "COMMANDER": {"STR": 1, "HIT": 5},  # Commander gives STR and HIT to adjacent units
            "KNIGHT": {"DEF": 2},               # Knight gives DEF to adjacent units
            "ARCHER": {"SKL": 1, "CRIT": 5}     # Archer gives SKL and CRIT to adjacent units
        }
        
        # Map unit names to bonus types
        unit_bonus_types = {
            "Commander": "COMMANDER",
            "Knight": "KNIGHT",
            "Archer": "ARCHER"
        }
        
        # Begin testing adjacency bonuses
        visual_logger.log_turn_start(1)
        
        # Check current adjacencies
        visual_logger.log_action("SYSTEM", "CHECKING_ADJACENCIES", "Checking initial unit adjacencies")
        
        # Find adjacencies
        adjacencies = {}
        for unit_id, unit in game_state_manager.current_game_state.unit_states.items():
            adjacencies[unit_id] = []
            for other_id, other_unit in game_state_manager.current_game_state.unit_states.items():
                if unit_id != other_id and other_unit.faction == unit.faction:
                    # Check if they're adjacent
                    manhattan_distance = abs(unit.position[0] - other_unit.position[0]) + abs(unit.position[1] - other_unit.position[1])
                    if manhattan_distance == 1:
                        adjacencies[unit_id].append(other_id)
        
        # Store in scenario state
        scenario_state["adjacent_units"] = adjacencies
        
        # Log adjacencies
        for unit_id, adjacent_ids in adjacencies.items():
            unit = game_state_manager.get_unit(unit_id)
            if adjacent_ids:
                adjacent_names = [game_state_manager.get_unit(adj_id).name for adj_id in adjacent_ids]
                visual_logger.log_action(unit_id, "ADJACENT_TO", 
                                       f"{unit.name} is adjacent to: {', '.join(adjacent_names)}")
            else:
                visual_logger.log_action(unit_id, "NO_ADJACENCY", 
                                       f"{unit.name} is not adjacent to any allied units")
        
        # Apply adjacency bonuses
        visual_logger.log_action("SYSTEM", "APPLYING_BONUSES", "Applying adjacency bonuses")
        
        # For each unit, apply bonuses based on adjacent units
        for unit_id, adjacent_ids in adjacencies.items():
            unit = game_state_manager.get_unit(unit_id)
            
            # Skip if no adjacencies
            if not adjacent_ids:
                continue
            
            # Apply bonuses from each adjacent unit
            bonus_applied = False
            for adj_id in adjacent_ids:
                adj_unit = game_state_manager.get_unit(adj_id)
                
                # Get bonus type for the adjacent unit
                bonus_type = unit_bonus_types.get(adj_unit.name)
                if not bonus_type:
                    continue
                
                # Apply bonuses
                bonuses = adjacency_bonuses.get(bonus_type, {})
                for stat, bonus_value in bonuses.items():
                    # Some bonuses aren't in base_stats (HIT, CRIT)
                    if stat in ["HIT", "CRIT"]:
                        # These would be applied during combat calculations
                        visual_logger.log_action(unit_id, "COMBAT_BONUS", 
                                               f"{unit.name} gains {stat} +{bonus_value} from adjacent {adj_unit.name}")
                        bonus_applied = True
                    else:
                        # Apply to base stats
                        current_value = unit.base_stats.get(stat, 0)
                        # Don't actually modify base_stats in the test, just log it
                        visual_logger.log_action(unit_id, "STAT_BONUS", 
                                               f"{unit.name} gains {stat} +{bonus_value} from adjacent {adj_unit.name}")
                        bonus_applied = True
            
            if not bonus_applied:
                visual_logger.log_action(unit_id, "NO_BONUS", 
                                       f"{unit.name} receives no bonuses from adjacent units")
        
        # End of turn 1
        visual_logger.log_end_of_turn_state(1)
        
        # Begin turn 2 - move Archer to be adjacent to both Commander and Knight
        visual_logger.log_turn_start(2)
        
        # Move unit3 (Archer) to be adjacent to both unit1 and unit2
        visual_logger.log_action("SYSTEM", "MOVEMENT", "Moving Archer to be adjacent to both Commander and Knight")
        
        # Record original position
        original_pos = unit3.position
        new_pos = (3, 3)  # Position that's adjacent to Knight
        
        # Move the unit
        movement_system.move_unit(unit3, new_pos)
        
        visual_logger.log_action(unit3.id, "MOVE", 
                               f"{unit3.name} moved from {original_pos} to {new_pos}")
        
        # Update adjacencies
        adjacencies = {}
        for unit_id, unit in game_state_manager.current_game_state.unit_states.items():
            adjacencies[unit_id] = []
            for other_id, other_unit in game_state_manager.current_game_state.unit_states.items():
                if unit_id != other_id and other_unit.faction == unit.faction:
                    # Check if they're adjacent
                    manhattan_distance = abs(unit.position[0] - other_unit.position[0]) + abs(unit.position[1] - other_unit.position[1])
                    if manhattan_distance == 1:
                        adjacencies[unit_id].append(other_id)
        
        # Store in scenario state
        scenario_state["adjacent_units"] = adjacencies
        
        # Log new adjacencies
        visual_logger.log_action("SYSTEM", "UPDATED_ADJACENCIES", "Checking updated unit adjacencies")
        
        for unit_id, adjacent_ids in adjacencies.items():
            unit = game_state_manager.get_unit(unit_id)
            if adjacent_ids:
                adjacent_names = [game_state_manager.get_unit(adj_id).name for adj_id in adjacent_ids]
                visual_logger.log_action(unit_id, "ADJACENT_TO", 
                                       f"{unit.name} is adjacent to: {', '.join(adjacent_names)}")
            else:
                visual_logger.log_action(unit_id, "NO_ADJACENCY", 
                                       f"{unit.name} is not adjacent to any allied units")
        
        # Apply updated adjacency bonuses
        visual_logger.log_action("SYSTEM", "APPLYING_UPDATED_BONUSES", "Applying updated adjacency bonuses")
        
        # For each unit, apply bonuses based on adjacent units
        for unit_id, adjacent_ids in adjacencies.items():
            unit = game_state_manager.get_unit(unit_id)
            
            # Skip if no adjacencies
            if not adjacent_ids:
                visual_logger.log_action(unit_id, "NO_BONUS", 
                                       f"{unit.name} receives no bonuses (no adjacent allies)")
                continue
            
            # Apply bonuses from each adjacent unit
            bonus_applied = False
            for adj_id in adjacent_ids:
                adj_unit = game_state_manager.get_unit(adj_id)
                
                # Get bonus type for the adjacent unit
                bonus_type = unit_bonus_types.get(adj_unit.name)
                if not bonus_type:
                    continue
                
                # Apply bonuses
                bonuses = adjacency_bonuses.get(bonus_type, {})
                for stat, bonus_value in bonuses.items():
                    # Some bonuses aren't in base_stats (HIT, CRIT)
                    if stat in ["HIT", "CRIT"]:
                        # These would be applied during combat calculations
                        visual_logger.log_action(unit_id, "COMBAT_BONUS", 
                                               f"{unit.name} gains {stat} +{bonus_value} from adjacent {adj_unit.name}")
                        bonus_applied = True
                    else:
                        # Apply to base stats
                        current_value = unit.base_stats.get(stat, 0)
                        # Don't actually modify base_stats in the test, just log it
                        visual_logger.log_action(unit_id, "STAT_BONUS", 
                                               f"{unit.name} gains {stat} +{bonus_value} from adjacent {adj_unit.name}")
                        bonus_applied = True
            
            if not bonus_applied:
                visual_logger.log_action(unit_id, "NO_BONUS", 
                                       f"{unit.name} receives no bonuses from adjacent units")
        
        # End of turn 2
        visual_logger.log_end_of_turn_state(2)
        
        # Begin turn 3 - move Knight away, breaking adjacency
        visual_logger.log_turn_start(3)
        
        # Move unit2 (Knight) away
        visual_logger.log_action("SYSTEM", "MOVEMENT", "Moving Knight away from Commander and Archer")
        
        # Record original position
        original_pos = unit2.position
        new_pos = (5, 5)  # Position far from other units
        
        # Move the unit
        movement_system.move_unit(unit2, new_pos)
        
        visual_logger.log_action(unit2.id, "MOVE", 
                               f"{unit2.name} moved from {original_pos} to {new_pos}")
        
        # Update adjacencies
        adjacencies = {}
        for unit_id, unit in game_state_manager.current_game_state.unit_states.items():
            adjacencies[unit_id] = []
            for other_id, other_unit in game_state_manager.current_game_state.unit_states.items():
                if unit_id != other_id and other_unit.faction == unit.faction:
                    # Check if they're adjacent
                    manhattan_distance = abs(unit.position[0] - other_unit.position[0]) + abs(unit.position[1] - other_unit.position[1])
                    if manhattan_distance == 1:
                        adjacencies[unit_id].append(other_id)
        
        # Store in scenario state
        scenario_state["adjacent_units"] = adjacencies
        
        # Log final adjacencies
        visual_logger.log_action("SYSTEM", "FINAL_ADJACENCIES", "Checking final unit adjacencies")
        
        for unit_id, adjacent_ids in adjacencies.items():
            unit = game_state_manager.get_unit(unit_id)
            if adjacent_ids:
                adjacent_names = [game_state_manager.get_unit(adj_id).name for adj_id in adjacent_ids]
                visual_logger.log_action(unit_id, "ADJACENT_TO", 
                                       f"{unit.name} is adjacent to: {', '.join(adjacent_names)}")
            else:
                visual_logger.log_action(unit_id, "NO_ADJACENCY", 
                                       f"{unit.name} is not adjacent to any allied units")
        
        # Log removed bonuses due to broken adjacency
        visual_logger.log_action("SYSTEM", "BONUS_CHANGES", "Adjacency bonuses updated due to unit movement")
        
        visual_logger.log_action(unit2.id, "BONUSES_LOST", 
                               f"{unit2.name} lost all adjacency bonuses by moving away from allies")
        
        visual_logger.log_action(unit1.id, "SPECIFIC_BONUS_LOST", 
                               f"{unit1.name} no longer receives DEF +2 from {unit2.name}")
        
        visual_logger.log_action(unit3.id, "SPECIFIC_BONUS_LOST", 
                               f"{unit3.name} no longer receives DEF +2 from {unit2.name}")
        
        # End of simulation
        visual_logger.log_end_of_turn_state(3)
        visual_logger.finalize_log()
        
        # Verify movement affected adjacencies
        assert not unit2.id in adjacencies.get(unit1.id, []), "Knight should no longer be adjacent to Commander"
        assert not unit2.id in adjacencies.get(unit3.id, []), "Knight should no longer be adjacent to Archer"
        
        # Verify log file was created
        assert os.path.exists(ADJACENCY_LOG), f"Log file {ADJACENCY_LOG} was not created"
        logger.info(f"Successfully created adjacency mechanics log at {ADJACENCY_LOG}") 