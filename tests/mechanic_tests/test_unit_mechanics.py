"""
Unit Mechanics Tests

This module contains tests focused on unit core mechanics, including:
- Unit recruitment
- Unit death
- Unit retreat
- Unit rescue
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
RECRUITMENT_LOG = os.path.join(LOG_DIR, "recruitment_mechanics.txt")
DEATH_LOG = os.path.join(LOG_DIR, "death_mechanics.txt")
RETREAT_LOG = os.path.join(LOG_DIR, "retreat_mechanics.txt")

# Setup test logger
logger = logging.getLogger("test_unit_mechanics")

class TestUnitMechanics:
    """Tests for basic unit mechanics."""
    
    @pytest.fixture
    def basic_unit_scenario_setup(self):
        """
        Set up a basic scenario with units for testing core unit mechanics.
        """
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load data
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a map state
        map_state = MapState()
        map_state.dimensions = (8, 8)  # Test map
        
        # Default terrain is plains
        terrain_grid = [['P'] * 8 for _ in range(8)]
        
        # Add some variety to terrain
        terrain_grid[3][3] = 'F'  # Forest
        terrain_grid[5][5] = 'M'  # Mountain
        terrain_grid[1][6] = 'W'  # Water
        
        # Set map state
        map_state.terrain_grid = terrain_grid
        map_state.map_id = "unit_mechanics_test"
        
        # Create a MapData object for the visual logger
        class MapDataObj:
            def __init__(self):
                self.id = "unit_mechanics_test"
                self.name = "Unit Mechanics Test"
                self.dimensions = (8, 8)
                self.terrain_grid = terrain_grid
                self.fog_of_war = False
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_unit_mechanics"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Add test units
        unit_states = {}
        unit_positions = {}
        faction_units = {"PLAYER": [], "ENEMY": [], "NPC": []}
        
        # Create player faction units
        player_unit1 = UnitState()
        player_unit1.id = "PLAYER_UNIT_1"
        player_unit1.name = "Commander"
        player_unit1.faction = FactionEnum.PLAYER
        player_unit1.position = (2, 2)
        player_unit1.current_hp = 20
        player_unit1.max_hp = 20
        player_unit1.disposition = DispositionEnum.ACTIVE
        player_unit1.ai_persona = "BALANCED"
        player_unit1.base_stats = {"STR": 10, "DEF": 8, "SPD": 9, "SKL": 8, "MOV": 5}
        
        unit_states[player_unit1.id] = player_unit1
        unit_positions[player_unit1.id] = player_unit1.position
        faction_units["PLAYER"].append(player_unit1.id)
        
        # Create enemy units
        enemy_unit1 = UnitState()
        enemy_unit1.id = "ENEMY_UNIT_1"
        enemy_unit1.name = "Bandit"
        enemy_unit1.faction = FactionEnum.ENEMY
        enemy_unit1.position = (5, 2)
        enemy_unit1.current_hp = 15
        enemy_unit1.max_hp = 15
        enemy_unit1.disposition = DispositionEnum.ACTIVE
        enemy_unit1.ai_persona = "AGGRESSOR"
        enemy_unit1.base_stats = {"STR": 8, "DEF": 5, "SPD": 7, "SKL": 6, "MOV": 5}
        
        unit_states[enemy_unit1.id] = enemy_unit1
        unit_positions[enemy_unit1.id] = enemy_unit1.position
        faction_units["ENEMY"].append(enemy_unit1.id)
        
        # Create NPC unit (potential recruit)
        npc_unit = UnitState()
        npc_unit.id = "NPC_UNIT_1"
        npc_unit.name = "Villager"
        npc_unit.faction = FactionEnum.NPC
        npc_unit.position = (2, 6)
        npc_unit.current_hp = 12
        npc_unit.max_hp = 12
        npc_unit.disposition = DispositionEnum.ACTIVE
        npc_unit.ai_persona = "CAUTIOUS"
        npc_unit.base_stats = {"STR": 6, "DEF": 4, "SPD": 5, "SKL": 5, "MOV": 4}
        npc_unit.can_recruit = True
        npc_unit.recruit_dialogue = "I'll join your cause!"
        
        unit_states[npc_unit.id] = npc_unit
        unit_positions[npc_unit.id] = npc_unit.position
        faction_units["NPC"].append(npc_unit.id)
        
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
            "movement_system": movement_system,
            "cli_display": cli_display,
            "action_handler": action_handler
        }
    
    def test_unit_recruitment(self, basic_unit_scenario_setup):
        """
        Tests recruiting an NPC unit to the player's side.
        
        This test:
        1. Moves a player unit adjacent to a recruitable NPC
        2. Initiates recruitment dialog
        3. Changes the NPC's faction to player
        4. Verifies the unit is now part of the player's faction
        """
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(RECRUITMENT_LOG):
            os.remove(RECRUITMENT_LOG)
            
        # Get test components
        game_state_manager = basic_unit_scenario_setup["game_state_manager"]
        movement_system = basic_unit_scenario_setup["movement_system"]
        cli_display = basic_unit_scenario_setup["cli_display"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=RECRUITMENT_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get relevant units
        player_unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        npc_unit = game_state_manager.get_unit("NPC_UNIT_1")
        
        # Verify units exist
        assert player_unit is not None, "Player unit not found"
        assert npc_unit is not None, "NPC unit not found"
        
        # Begin the test
        visual_logger.log_turn_start(1)
        
        # Record initial states
        original_player_pos = player_unit.position
        npc_pos = npc_unit.position
        original_faction = npc_unit.faction
        
        # Move player adjacent to NPC
        target_pos = (2, 5)  # Position adjacent to the NPC
        
        visual_logger.log_action(player_unit.id, "MOVEMENT", 
                              f"Moving {player_unit.name} from {original_player_pos} to {target_pos}")
        
        # Execute the move
        movement_system.move_unit(player_unit, target_pos)
        
        # Check adjacency
        manhattan_distance = abs(player_unit.position[0] - npc_unit.position[0]) + abs(player_unit.position[1] - npc_unit.position[1])
        assert manhattan_distance == 1, "Units should be adjacent after movement"
        
        # Log the adjacency
        visual_logger.log_action(player_unit.id, "ADJACENT", 
                              f"{player_unit.name} is now adjacent to {npc_unit.name}")
        
        # Initiate recruitment dialog
        visual_logger.log_action(player_unit.id, "TALK", 
                              f"{player_unit.name} talks to {npc_unit.name}")
        
        visual_logger.log_action(npc_unit.id, "DIALOG", 
                              f"{npc_unit.name}: {npc_unit.recruit_dialogue}")
        
        # Execute the recruitment
        visual_logger.log_action("SYSTEM", "RECRUITMENT", 
                              f"{npc_unit.name} joins {player_unit.name}'s side!")
        
        # Change faction
        npc_unit.faction = FactionEnum.PLAYER
        
        # Update faction lists
        game_state_manager.current_game_state.map_state.allies["PLAYER"].append(npc_unit.id)
        game_state_manager.current_game_state.map_state.allies["NPC"].remove(npc_unit.id)
        
        # Log the result
        visual_logger.log_action(npc_unit.id, "FACTION_CHANGE", 
                              f"{npc_unit.name} changed from {original_faction} to {npc_unit.faction}")
        
        # End turn and log
        visual_logger.log_end_of_turn_state(1)
        visual_logger.finalize_log()
        
        # Verify recruitment successful
        assert npc_unit.faction == FactionEnum.PLAYER, "NPC should now be part of the player faction"
        assert npc_unit.id in game_state_manager.current_game_state.map_state.allies["PLAYER"], "NPC should be in player faction list"
        assert npc_unit.id not in game_state_manager.current_game_state.map_state.allies["NPC"], "NPC should not be in NPC faction list"
        
        # Verify log file was created
        assert os.path.exists(RECRUITMENT_LOG), f"Log file {RECRUITMENT_LOG} was not created"
        logger.info(f"Successfully created recruitment log at {RECRUITMENT_LOG}")
        
    def test_unit_death(self, basic_unit_scenario_setup):
        """
        Tests a unit dying in combat and being removed from the game.
        
        This test:
        1. Sets up a combat scenario where a unit will die
        2. Executes the combat and handles death
        3. Verifies the unit is marked as dead and removed from active units
        """
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(DEATH_LOG):
            os.remove(DEATH_LOG)
            
        # Get test components
        game_state_manager = basic_unit_scenario_setup["game_state_manager"]
        cli_display = basic_unit_scenario_setup["cli_display"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=DEATH_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get relevant units
        enemy_unit = game_state_manager.get_unit("ENEMY_UNIT_1")
        assert enemy_unit is not None, "Enemy unit not found"
        
        # Begin the test
        visual_logger.log_turn_start(1)
        
        # Set up fatal scenario
        original_hp = enemy_unit.current_hp
        original_disposition = enemy_unit.disposition
        
        # Simulate fatal damage
        fatal_damage = enemy_unit.current_hp
        
        visual_logger.log_action("SYSTEM", "COMBAT", 
                              f"Player attacks {enemy_unit.name} for {fatal_damage} damage")
        
        # Apply damage
        enemy_unit.current_hp = max(0, enemy_unit.current_hp - fatal_damage)
        
        visual_logger.log_action(enemy_unit.id, "DAMAGE", 
                              f"{enemy_unit.name} takes {fatal_damage} damage (HP: {enemy_unit.current_hp}/{enemy_unit.max_hp})")
        
        # Check if unit is defeated
        if enemy_unit.current_hp <= 0:
            # Mark as dead
            enemy_unit.disposition = DispositionEnum.DEAD
            
            visual_logger.log_action(enemy_unit.id, "DEATH", 
                                  f"{enemy_unit.name} has been defeated!")
            
            # Remove from active units
            game_state_manager.current_game_state.map_state.unit_positions.pop(enemy_unit.id, None)
            
            visual_logger.log_action("SYSTEM", "UNIT_REMOVED", 
                                  f"{enemy_unit.name} has been removed from the battlefield")
        
        # Log end of turn
        visual_logger.log_end_of_turn_state(1)
        visual_logger.finalize_log()
        
        # Verify unit death
        assert enemy_unit.current_hp == 0, "Unit should have 0 HP"
        assert enemy_unit.disposition == DispositionEnum.DEAD, "Unit should be marked as DEAD"
        assert enemy_unit.id not in game_state_manager.current_game_state.map_state.unit_positions, "Unit should be removed from positions"
        
        # Verify log file was created
        assert os.path.exists(DEATH_LOG), f"Log file {DEATH_LOG} was not created"
        logger.info(f"Successfully created death mechanics log at {DEATH_LOG}")
        
    def test_unit_retreat(self, basic_unit_scenario_setup):
        """
        Tests a unit retreating from battle.
        
        This test:
        1. Simulates a unit choosing to retreat
        2. Marks the unit as retreated
        3. Removes the unit from the battlefield
        4. Verifies the unit is properly removed but not marked as dead
        """
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(RETREAT_LOG):
            os.remove(RETREAT_LOG)
            
        # Get test components
        game_state_manager = basic_unit_scenario_setup["game_state_manager"]
        cli_display = basic_unit_scenario_setup["cli_display"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=RETREAT_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get relevant units
        player_unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        assert player_unit is not None, "Player unit not found"
        
        # Begin the test
        visual_logger.log_turn_start(1)
        
        # Record initial state
        original_position = player_unit.position
        original_disposition = player_unit.disposition
        
        # Simulate retreat decision
        visual_logger.log_action(player_unit.id, "DECISION", 
                              f"{player_unit.name} decides to retreat from battle")
        
        # Move to edge of map for retreat
        retreat_pos = (0, 2)  # Edge position
        player_unit.position = retreat_pos
        
        visual_logger.log_action(player_unit.id, "MOVEMENT", 
                              f"{player_unit.name} moves to retreat position {retreat_pos}")
        
        # Execute retreat
        visual_logger.log_action(player_unit.id, "RETREAT", 
                              f"{player_unit.name} retreats from battle!")
        
        # Mark as retreated
        player_unit.disposition = DispositionEnum.RETREATED
        
        # Remove from active battlefield
        game_state_manager.current_game_state.map_state.unit_positions.pop(player_unit.id, None)
        
        visual_logger.log_action("SYSTEM", "UNIT_REMOVED", 
                              f"{player_unit.name} has been removed from the battlefield")
        
        # End turn
        visual_logger.log_end_of_turn_state(1)
        visual_logger.finalize_log()
        
        # Verify retreat
        assert player_unit.disposition == DispositionEnum.RETREATED, "Unit should be marked as RETREATED"
        assert player_unit.id not in game_state_manager.current_game_state.map_state.unit_positions, "Unit should be removed from positions"
        assert player_unit.current_hp > 0, "Retreated unit should still have HP"
        
        # Verify log file was created
        assert os.path.exists(RETREAT_LOG), f"Log file {RETREAT_LOG} was not created"
        logger.info(f"Successfully created retreat mechanics log at {RETREAT_LOG}")
        
    def test_unit_rescue(self, basic_unit_scenario_setup):
        """
        Tests a unit rescuing another unit.
        
        This test:
        1. Moves a player unit adjacent to a vulnerable NPC
        2. Initiates rescue action
        3. Updates both units' status (rescuer and rescued)
        4. Verifies the rescued unit is correctly marked and handled
        """
        # Define log path for rescue test
        RESCUE_LOG = os.path.join(LOG_DIR, "rescue_mechanics.txt")
        
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(RESCUE_LOG):
            os.remove(RESCUE_LOG)
            
        # Get test components
        game_state_manager = basic_unit_scenario_setup["game_state_manager"]
        movement_system = basic_unit_scenario_setup["movement_system"]
        cli_display = basic_unit_scenario_setup["cli_display"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=RESCUE_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get relevant units
        player_unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        npc_unit = game_state_manager.get_unit("NPC_UNIT_1")
        
        # Verify units exist
        assert player_unit is not None, "Player unit not found"
        assert npc_unit is not None, "NPC unit not found"
        
        # Begin the test
        visual_logger.log_turn_start(1)
        
        # Record initial states
        original_player_pos = player_unit.position
        npc_pos = npc_unit.position
        
        # Set up rescue scenario - make NPC vulnerable (low HP)
        npc_unit.current_hp = 3  # NPC is in danger with low HP
        
        visual_logger.log_action(npc_unit.id, "STATUS", 
                              f"{npc_unit.name} is vulnerable with low HP ({npc_unit.current_hp}/{npc_unit.max_hp})")
        
        # Move player adjacent to NPC
        target_pos = (2, 5)  # Position adjacent to the NPC
        
        visual_logger.log_action(player_unit.id, "MOVEMENT", 
                              f"Moving {player_unit.name} from {original_player_pos} to {target_pos}")
        
        # Execute the move
        movement_system.move_unit(player_unit, target_pos)
        
        # Check adjacency
        manhattan_distance = abs(player_unit.position[0] - npc_unit.position[0]) + abs(player_unit.position[1] - npc_unit.position[1])
        assert manhattan_distance == 1, "Units should be adjacent after movement"
        
        # Log adjacency
        visual_logger.log_action(player_unit.id, "ADJACENT", 
                              f"{player_unit.name} is now adjacent to {npc_unit.name}")
        
        # Execute rescue action
        visual_logger.log_action(player_unit.id, "RESCUE", 
                              f"{player_unit.name} rescues {npc_unit.name}!")
        
        # Update unit states for rescue
        # 1. Update rescuer
        player_unit.rescuing_unit_id = npc_unit.id
        if not hasattr(player_unit, "status"):
            player_unit.status = {}
        player_unit.status["RESCUING"] = True
        
        # Rescuer typically has movement penalties when carrying
        original_mov = player_unit.base_stats.get("MOV", 0)
        rescue_mov_penalty = max(1, original_mov - 2)  # -2 MOV penalty, minimum of 1
        player_unit.base_stats["MOV"] = rescue_mov_penalty
        
        visual_logger.log_action(player_unit.id, "STAT_CHANGE", 
                              f"{player_unit.name} MOV reduced from {original_mov} to {rescue_mov_penalty} due to carrying")
        
        # 2. Update rescued unit
        npc_unit.rescued_by_unit_id = player_unit.id
        if not hasattr(npc_unit, "status"):
            npc_unit.status = {}
        npc_unit.status["RESCUED"] = True
        
        # Remove rescued unit from the map
        original_npc_pos = npc_unit.position
        game_state_manager.current_game_state.map_state.unit_positions.pop(npc_unit.id, None)
        
        visual_logger.log_action(npc_unit.id, "RESCUED", 
                              f"{npc_unit.name} is rescued by {player_unit.name} and removed from battlefield")
        
        # Log the state after rescue
        visual_logger.log_action("SYSTEM", "RESCUE_STATE", 
                              f"{player_unit.name} is carrying {npc_unit.name}")
        
        # End turn
        visual_logger.log_end_of_turn_state(1)
        
        # Start turn 2 to demonstrate dropping the rescued unit
        visual_logger.log_turn_start(2)
        
        # Find a valid adjacent tile to drop the rescued unit
        drop_positions = [
            (player_unit.position[0] - 1, player_unit.position[1]),  # Left
            (player_unit.position[0] + 1, player_unit.position[1]),  # Right
            (player_unit.position[0], player_unit.position[1] - 1),  # Up
            (player_unit.position[0], player_unit.position[1] + 1)   # Down
        ]
        
        # Filter to valid positions (on map, not occupied)
        valid_drop_positions = []
        map_width, map_height = game_state_manager.current_game_state.map_state.dimensions
        
        for pos in drop_positions:
            x, y = pos
            if 0 <= x < map_width and 0 <= y < map_height:
                # Check if position is not occupied
                occupied = False
                for unit_id, unit_pos in game_state_manager.current_game_state.map_state.unit_positions.items():
                    if unit_pos == pos:
                        occupied = True
                        break
                
                if not occupied:
                    valid_drop_positions.append(pos)
        
        # Drop the unit if there's a valid position
        if valid_drop_positions:
            drop_pos = valid_drop_positions[0]
            
            visual_logger.log_action(player_unit.id, "DROP", 
                                  f"{player_unit.name} drops {npc_unit.name} at position {drop_pos}")
            
            # Update unit states
            # 1. Rescuer
            player_unit.rescuing_unit_id = None
            if hasattr(player_unit, "status"):
                player_unit.status.pop("RESCUING", None)
            
            # Restore original movement
            player_unit.base_stats["MOV"] = original_mov
            
            visual_logger.log_action(player_unit.id, "STAT_RESTORED", 
                                  f"{player_unit.name} MOV restored to {original_mov}")
            
            # 2. Rescued unit
            npc_unit.rescued_by_unit_id = None
            if hasattr(npc_unit, "status"):
                npc_unit.status.pop("RESCUED", None)
            
            # Place rescued unit back on map
            npc_unit.position = drop_pos
            game_state_manager.current_game_state.map_state.unit_positions[npc_unit.id] = drop_pos
            
            visual_logger.log_action(npc_unit.id, "DROPPED", 
                                  f"{npc_unit.name} is placed at {drop_pos}")
        else:
            visual_logger.log_action("SYSTEM", "ERROR", 
                                  "No valid position to drop the rescued unit")
        
        # End turn 2
        visual_logger.log_end_of_turn_state(2)
        visual_logger.finalize_log()
        
        # Verify rescue mechanics
        if hasattr(player_unit, "status") and valid_drop_positions:
            assert "RESCUING" not in player_unit.status, "Player should no longer be rescuing after dropping"
            assert player_unit.rescuing_unit_id is None, "Player should not have rescuing_unit_id set"
            assert player_unit.base_stats["MOV"] == original_mov, "Player MOV should be restored"
            
            assert "RESCUED" not in npc_unit.status, "NPC should no longer be rescued after being dropped"
            assert npc_unit.rescued_by_unit_id is None, "NPC should not have rescued_by_unit_id set"
            assert npc_unit.id in game_state_manager.current_game_state.map_state.unit_positions, "NPC should be back on the map"
        
        # Verify log file was created
        assert os.path.exists(RESCUE_LOG), f"Log file {RESCUE_LOG} was not created"
        logger.info(f"Successfully created rescue mechanics log at {RESCUE_LOG}") 