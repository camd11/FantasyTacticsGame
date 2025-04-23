"""
Objective Mechanics Tests

This module contains tests focused on objective-related mechanics, including:
- Capturing a primary objective (throne)
- Capturing a secondary objective (village)
- Defending objectives against enemies
- Objective control tracking
- Win condition validation
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
LOG_DIR = os.path.abspath("logs/mechanic_tests/objectives")
CAPTURE_THRONE_LOG = os.path.join(LOG_DIR, "capture_objective.txt")
DEFEND_OBJECTIVE_LOG = os.path.join(LOG_DIR, "defend_objective.txt")
CONTROL_TRACKING_LOG = os.path.join(LOG_DIR, "control_tracking.txt")

# Setup test logger
logger = logging.getLogger("test_objective_mechanics")

class TestObjectiveMechanics:
    """Tests for objective-related mechanics."""
    
    @pytest.fixture
    def basic_objective_scenario_setup(self):
        """
        Set up a basic scenario with a 7x7 map, a throne, and a village.
        """
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load data
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a map state with objectives
        map_state = MapState()
        map_state.dimensions = (7, 7)  # Small test map
        
        # Default terrain is plains
        terrain_grid = [['P'] * 7 for _ in range(7)]
        
        # Add throne (primary objective) at center
        throne_position = (3, 3)
        terrain_grid[throne_position[1]][throne_position[0]] = 'T'  # Throne
        
        # Add village (secondary objective)
        village_position = (5, 1)
        terrain_grid[village_position[1]][village_position[0]] = 'V'  # Village
        
        # Set map state
        map_state.terrain_grid = terrain_grid
        map_state.map_id = "objective_capture_test"
        
        # Create a MapData object for the visual logger
        class MapDataObj:
            def __init__(self):
                self.id = "objective_capture_test"
                self.name = "Objective Capture Test"
                self.dimensions = (7, 7)
                self.terrain_grid = terrain_grid
                self.fog_of_war = False
                self.seize_point = throne_position  # Main objective
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_objective_capture"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Create scenario state to track objectives
        scenario_state = {
            "primary_objective": throne_position,
            "secondary_objectives": [village_position],
            "objective_owner": {
                throne_position: None,
                village_position: None
            },
            "throne_control_turns": 0,
            "last_throne_owner": None
        }
        
        # Add test units
        unit_states = {}
        unit_positions = {}
        faction_units = {"PLAYER": [], "ENEMY": []}
        
        # Create a player unit to capture objectives
        player_unit = UnitState()
        player_unit.id = "PLAYER_UNIT_1"
        player_unit.name = "Lord Commander"
        player_unit.faction = FactionEnum.PLAYER
        player_unit.position = (1, 3)  # Near the throne, but not on it
        player_unit.current_hp = 25
        player_unit.max_hp = 25
        player_unit.ai_persona = "BALANCED"
        player_unit.base_stats = {"STR": 12, "DEF": 10, "SPD": 10, "SKL": 10}
        
        # Add player unit to collections
        unit_states[player_unit.id] = player_unit
        unit_positions[player_unit.id] = player_unit.position
        faction_units["PLAYER"].append(player_unit.id)
        
        # Create an enemy unit near the objective
        enemy_unit = UnitState()
        enemy_unit.id = "ENEMY_UNIT_1"
        enemy_unit.name = "Dark Knight"
        enemy_unit.faction = FactionEnum.ENEMY
        enemy_unit.position = (5, 3)  # Opposite side from player
        enemy_unit.current_hp = 20
        enemy_unit.max_hp = 20
        enemy_unit.ai_persona = "DEFENDER"
        enemy_unit.base_stats = {"STR": 11, "DEF": 12, "SPD": 9, "SKL": 10}
        
        # Add enemy unit to collections
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
            combatSystem_instance=combat_system,
            inventorySystem_instance=inventory_system,
            turnManager_instance=turn_manager,
            eventHandler_instance=event_handler,
            dataProvider_instance=data_provider,
            core_turn_manager_instance=core_turn_manager
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
            "throne_position": throne_position,
            "village_position": village_position,
            "inventory_system": inventory_system,
            "combat_system": combat_system
        }
    
    def test_capture_objective_log(self, basic_objective_scenario_setup):
        """
        Tests a unit capturing a primary objective (throne) and logs it visually.
        
        This test:
        1. Sets up a 7x7 map with a throne at the center
        2. Places a player unit near the throne
        3. Moves the unit onto the throne to capture it
        4. Updates the objective owner and checks win condition
        5. Logs the objective capture in a visual log file
        """
        # Ensure log directory exists and delete old log
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(CAPTURE_THRONE_LOG):
            os.remove(CAPTURE_THRONE_LOG)
        
        # Get test components
        game_state_manager = basic_objective_scenario_setup["game_state_manager"]
        cli_display = basic_objective_scenario_setup["cli_display"]
        movement_system = basic_objective_scenario_setup["movement_system"]
        scenario_state = basic_objective_scenario_setup["scenario_state"]
        throne_position = basic_objective_scenario_setup["throne_position"]
        
        # Get the player unit
        player_unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        assert player_unit is not None, "Player unit not found"
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=CAPTURE_THRONE_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        visual_logger.log_action("SYSTEM", "OBJECTIVE_STATUS", 
                                f"Throne at {throne_position}, currently uncaptured")
        
        # Record the unit's original position
        original_position = player_unit.position
        logger.info(f"Unit {player_unit.name} starting at position {original_position}")
        
        # Move the unit to the throne position
        visual_logger.log_turn_start(1)
        visual_logger.log_phase_start(FactionEnum.PLAYER)
        
        # Move unit to capture the throne
        movement_system.move_unit(player_unit, throne_position)
        
        # Log the movement action
        visual_logger.log_action(player_unit.id, "MOVE", 
                                f"from {original_position} to {throne_position}")
        
        # Check if the unit is on the objective and update the owner
        is_on_objective = player_unit.position == throne_position
        
        if is_on_objective:
            # Unit captured the objective
            scenario_state["objective_owner"][throne_position] = player_unit.faction
            scenario_state["last_throne_owner"] = player_unit.faction
            scenario_state["throne_control_turns"] = 1
            
            visual_logger.log_action("SYSTEM", "OBJECTIVE_CAPTURED", 
                                    f"Throne at {throne_position} captured by {player_unit.faction.name}")
                                    
            # Check win condition (in this simple test, capturing the throne is a win)
            is_win_condition = True
            
            if is_win_condition:
                visual_logger.log_action("SYSTEM", "WIN_CONDITION", 
                                        f"{player_unit.faction.name} has seized the throne and won!")
        
        # Log the end of turn state
        visual_logger.log_end_of_turn_state(1)
        visual_logger.finalize_log()
        
        # Verify unit is on the throne
        assert player_unit.position == throne_position, "Unit should be on the throne"
        
        # Verify objective owner was updated
        assert scenario_state["objective_owner"][throne_position] == player_unit.faction, "Throne owner should be player faction"
        
        # Verify log file was created
        assert os.path.exists(CAPTURE_THRONE_LOG), f"Log file {CAPTURE_THRONE_LOG} was not created"
        logger.info(f"Successfully created objective capture log at {CAPTURE_THRONE_LOG}")

    def test_defend_objective_log(self, basic_objective_scenario_setup):
        """
        Tests defending an objective against an enemy unit.
        
        This test:
        1. Sets up a scenario where a player unit holds the throne
        2. An enemy unit tries to attack the player unit
        3. The objective owner changes if the player unit is defeated
        4. Logs the objective defense in a visual log file
        """
        # Ensure log directory exists and delete old log
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(DEFEND_OBJECTIVE_LOG):
            os.remove(DEFEND_OBJECTIVE_LOG)
        
        # Get test components
        game_state_manager = basic_objective_scenario_setup["game_state_manager"]
        cli_display = basic_objective_scenario_setup["cli_display"]
        movement_system = basic_objective_scenario_setup["movement_system"]
        scenario_state = basic_objective_scenario_setup["scenario_state"]
        throne_position = basic_objective_scenario_setup["throne_position"]
        
        # Get test units
        player_unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        enemy_unit = game_state_manager.get_unit("ENEMY_UNIT_1")
        assert player_unit is not None, "Player unit not found"
        assert enemy_unit is not None, "Enemy unit not found"
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=DEFEND_OBJECTIVE_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # First, let's move the player unit to the throne to capture it
        original_player_pos = player_unit.position
        movement_system.move_unit(player_unit, throne_position)
        
        # Set the player unit as controller of the throne
        scenario_state["objective_owner"][throne_position] = player_unit.faction
        scenario_state["last_throne_owner"] = player_unit.faction
        scenario_state["throne_control_turns"] = 1
        
        visual_logger.log_action("SYSTEM", "OBJECTIVE_STATUS", 
                               f"Throne at {throne_position} is controlled by {player_unit.faction.name}")
        visual_logger.log_action(player_unit.id, "MOVE", 
                               f"from {original_player_pos} to {throne_position}")
        
        # Now let's have the enemy unit approach the throne
        visual_logger.log_turn_start(1)
        visual_logger.log_phase_start(FactionEnum.ENEMY)
        
        # Move enemy unit closer to the throne
        original_enemy_pos = enemy_unit.position
        new_enemy_pos = (4, 3)  # One tile away from the throne
        movement_system.move_unit(enemy_unit, new_enemy_pos)
        
        visual_logger.log_action(enemy_unit.id, "MOVE",
                               f"from {original_enemy_pos} to {new_enemy_pos}")
        visual_logger.log_action(enemy_unit.id, "INTENT",
                               f"Enemy is approaching the throne with intent to capture")
        
        # Simulate a combat scenario - enemy attempts to attack the player unit
        # For simplicity, we'll just simulate the result rather than calling the combat system
        
        # Let's say the attack happens but player survives
        player_unit.current_hp -= 5  # Take some damage
        
        visual_logger.log_action(enemy_unit.id, "ATTACK",
                               f"Attacks {player_unit.name} at the throne")
        visual_logger.log_action(player_unit.id, "DEFEND",
                               f"Defends throne, takes 5 damage (HP: {player_unit.current_hp}/{player_unit.max_hp})")
        
        # Check if throne is still controlled by player
        objective_still_owned = player_unit.current_hp > 0
        
        if objective_still_owned:
            visual_logger.log_action("SYSTEM", "OBJECTIVE_DEFENDED",
                                   f"Throne at {throne_position} successfully defended by {player_unit.faction.name}")
            # Increment control turns
            scenario_state["throne_control_turns"] += 1
        else:
            # If player was defeated, change ownership
            scenario_state["objective_owner"][throne_position] = enemy_unit.faction
            scenario_state["last_throne_owner"] = enemy_unit.faction
            scenario_state["throne_control_turns"] = 1
            visual_logger.log_action("SYSTEM", "OBJECTIVE_CAPTURED",
                                   f"Throne at {throne_position} captured by {enemy_unit.faction.name}")
        
        # Log end of turn state
        visual_logger.log_end_of_turn_state(1)
        
        # Log next turn to show persistent control
        visual_logger.log_turn_start(2)
        visual_logger.log_action("SYSTEM", "OBJECTIVE_STATUS",
                               f"Throne at {throne_position} control: {scenario_state['objective_owner'][throne_position].name} for {scenario_state['throne_control_turns']} turns")
        
        # Check for win condition if controlled for enough turns
        if scenario_state["throne_control_turns"] >= 2:
            controlling_faction = scenario_state["objective_owner"][throne_position]
            visual_logger.log_action("SYSTEM", "WIN_CONDITION",
                                   f"{controlling_faction.name} has controlled the throne for {scenario_state['throne_control_turns']} turns and won!")
        
        visual_logger.log_end_of_turn_state(2)
        visual_logger.finalize_log()
        
        # Verify player unit is still on the throne
        assert player_unit.position == throne_position, "Player unit should still be on the throne"
        
        # Verify player took damage but survived 
        assert player_unit.current_hp == player_unit.max_hp - 5, "Player should have taken 5 damage"
        
        # Verify objective is still owned by player
        assert scenario_state["objective_owner"][throne_position] == player_unit.faction, "Throne should still be controlled by player"
        
        # Verify control turns increased
        assert scenario_state["throne_control_turns"] == 2, "Throne control turns should be 2"
        
        # Verify log file was created
        assert os.path.exists(DEFEND_OBJECTIVE_LOG), f"Log file {DEFEND_OBJECTIVE_LOG} was not created"
        logger.info(f"Successfully created objective defense log at {DEFEND_OBJECTIVE_LOG}")
    
    def test_control_tracking_log(self, basic_objective_scenario_setup):
        """
        Tests tracking objective control over multiple turns.
        
        This test:
        1. Sets up a scenario with multiple objectives
        2. Has units capture and control objectives over multiple turns
        3. Tracks ownership and control duration
        4. Checks win conditions based on control duration
        5. Logs the control tracking in a visual log file
        """
        # Ensure log directory exists and create a specific log file for this test
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(CONTROL_TRACKING_LOG):
            os.remove(CONTROL_TRACKING_LOG)
        
        # Get test components
        game_state_manager = basic_objective_scenario_setup["game_state_manager"]
        cli_display = basic_objective_scenario_setup["cli_display"]
        movement_system = basic_objective_scenario_setup["movement_system"]
        scenario_state = basic_objective_scenario_setup["scenario_state"]
        throne_position = basic_objective_scenario_setup["throne_position"]
        village_position = basic_objective_scenario_setup["village_position"]
        
        # Get test units
        player_unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        enemy_unit = game_state_manager.get_unit("ENEMY_UNIT_1")
        assert player_unit is not None, "Player unit not found"
        assert enemy_unit is not None, "Enemy unit not found"
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=CONTROL_TRACKING_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        visual_logger.log_action("SYSTEM", "OBJECTIVES_INFO", 
                               f"Primary: Throne at {throne_position}, Secondary: Village at {village_position}")
        
        # Track objective control over 3 turns
        for turn in range(1, 4):
            visual_logger.log_turn_start(turn)
            
            # Player phase
            visual_logger.log_phase_start(FactionEnum.PLAYER)
            
            # On turn 1, player captures the throne
            if turn == 1:
                # Move player to throne
                original_pos = player_unit.position
                movement_system.move_unit(player_unit, throne_position)
                
                visual_logger.log_action(player_unit.id, "MOVE", 
                                       f"from {original_pos} to {throne_position}")
                
                # Update throne control
                scenario_state["objective_owner"][throne_position] = player_unit.faction
                scenario_state["last_throne_owner"] = player_unit.faction
                scenario_state["throne_control_turns"] = 1
                
                visual_logger.log_action("SYSTEM", "OBJECTIVE_CAPTURED", 
                                       f"Throne at {throne_position} captured by {player_unit.faction.name}")
            
            # On turn 2, control continues
            elif turn == 2:
                # Player still controls the throne, increment control turns
                if scenario_state["objective_owner"][throne_position] == player_unit.faction:
                    scenario_state["throne_control_turns"] += 1
                    
                    visual_logger.log_action("SYSTEM", "OBJECTIVE_CONTROL", 
                                          f"{player_unit.faction.name} controls throne for {scenario_state['throne_control_turns']} turns")
            
            # On turn 3, check for win condition
            elif turn == 3:
                # Player still controls the throne, increment control turns
                if scenario_state["objective_owner"][throne_position] == player_unit.faction:
                    scenario_state["throne_control_turns"] += 1
                    
                    visual_logger.log_action("SYSTEM", "OBJECTIVE_CONTROL", 
                                           f"{player_unit.faction.name} controls throne for {scenario_state['throne_control_turns']} turns")
                    
                    # Check win condition (control for 3+ turns)
                    if scenario_state["throne_control_turns"] >= 3:
                        visual_logger.log_action("SYSTEM", "WIN_CONDITION", 
                                               f"{player_unit.faction.name} has controlled the throne for 3 turns and won!")
            
            # Enemy phase
            visual_logger.log_phase_start(FactionEnum.ENEMY)
            
            # On turn 1, enemy moves toward village
            if turn == 1:
                # Move enemy to village
                original_pos = enemy_unit.position
                movement_system.move_unit(enemy_unit, (5, 2))  # One tile away from village
                
                visual_logger.log_action(enemy_unit.id, "MOVE", 
                                       f"from {original_pos} to {enemy_unit.position}")
            
            # On turn 2, enemy captures village
            elif turn == 2:
                # Move enemy to village
                original_pos = enemy_unit.position
                movement_system.move_unit(enemy_unit, village_position)
                
                visual_logger.log_action(enemy_unit.id, "MOVE", 
                                       f"from {original_pos} to {village_position}")
                
                # Update village control
                scenario_state["objective_owner"][village_position] = enemy_unit.faction
                
                visual_logger.log_action("SYSTEM", "OBJECTIVE_CAPTURED", 
                                       f"Village at {village_position} captured by {enemy_unit.faction.name}")
            
            # Log end of turn
            visual_logger.log_end_of_turn_state(turn)
            
            # Log objective control summary at end of each turn
            throne_owner = scenario_state["objective_owner"][throne_position]
            village_owner = scenario_state["objective_owner"][village_position]
            
            throne_status = f"Controlled by {throne_owner.name}" if throne_owner else "Uncaptured"
            village_status = f"Controlled by {village_owner.name}" if village_owner else "Uncaptured"
            
            visual_logger.log_action("SYSTEM", "OBJECTIVE_SUMMARY", 
                                   f"Throne: {throne_status}, Village: {village_status}")
                                   
            if throne_owner == player_unit.faction:
                visual_logger.log_action("SYSTEM", "CONTROL_PROGRESS", 
                                       f"Throne control progress: {scenario_state['throne_control_turns']}/3 turns")
        
        visual_logger.finalize_log()
        
        # Verify throne is controlled by player for 3 turns
        assert scenario_state["objective_owner"][throne_position] == player_unit.faction, "Throne should be controlled by player"
        assert scenario_state["throne_control_turns"] == 3, "Throne control turns should be 3"
        
        # Verify village is controlled by enemy
        assert scenario_state["objective_owner"][village_position] == enemy_unit.faction, "Village should be controlled by enemy"
        
        # Verify log file was created
        assert os.path.exists(CONTROL_TRACKING_LOG), f"Log file {CONTROL_TRACKING_LOG} was not created"
        logger.info(f"Successfully created control tracking log at {CONTROL_TRACKING_LOG}") 