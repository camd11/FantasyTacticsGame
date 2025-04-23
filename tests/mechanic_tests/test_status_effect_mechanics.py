"""
Status Effect Mechanics Tests

This module contains tests focused on status effect mechanics, including:
- Applying status effects to units
- Stat modifications from status effects
- Status effect duration and removal
- Damage over time effects
"""

import os
import pytest
import logging
from typing import Dict, Any, Tuple
import random

# Import necessary core modules
from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum, GameState, MapState, UnitState, DispositionEnum
from src.core_engine.data_provider import DataProvider
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.inventory_system import InventorySystem
from src.core_engine.engine import EngineCore
from src.core_engine.action_handler import ActionHandler
from src.core_engine.turn_manager import TurnManager as CoreTurnManager
from src.gameplay_systems.turn_manager import TurnManager
from src.core_engine.event_handler import EventHandler
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.combat_system import CombatSystem

# Import for visual logging
from src.input.cli_display import CLIDisplay
from src.utils.visual_logger import VisualScenarioLogger

# Define log paths
LOG_DIR = os.path.abspath("logs/mechanic_tests/units")
STATUS_EFFECT_LOG = os.path.join(LOG_DIR, "status_effect_mechanics.txt")

# Setup test logger
logger = logging.getLogger("test_status_effect_mechanics")

class TestStatusEffectMechanics:
    """Tests for status effect mechanics."""
    
    @pytest.fixture
    def basic_status_scenario_setup(self):
        """
        Set up a basic scenario with units for testing status effect mechanics.
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
        map_state.map_id = "status_effect_test"
        
        # Create a MapData object for the visual logger
        class MapDataObj:
            def __init__(self):
                self.id = "status_effect_test"
                self.name = "Status Effect Test"
                self.dimensions = (5, 5)
                self.terrain_grid = terrain_grid
                self.fog_of_war = False
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_status_effects"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Create scenario state to track 
        scenario_state = {
            "status_effects": {}
        }
        
        # Add test units
        unit_states = {}
        unit_positions = {}
        faction_units = {"PLAYER": [], "ENEMY": []}
        
        # Create player faction unit
        player_unit = UnitState()
        player_unit.id = "PLAYER_UNIT_1"
        player_unit.name = "Knight"
        player_unit.faction = FactionEnum.PLAYER
        player_unit.position = (2, 2)
        player_unit.current_hp = 20
        player_unit.max_hp = 20
        player_unit.ai_persona = "BALANCED"
        player_unit.base_stats = {"STR": 8, "DEF": 10, "SPD": 7, "SKL": 6}
        
        unit_states[player_unit.id] = player_unit
        unit_positions[player_unit.id] = player_unit.position
        faction_units["PLAYER"].append(player_unit.id)
        
        # Create an enemy unit
        enemy_unit = UnitState()
        enemy_unit.id = "ENEMY_UNIT_1"
        enemy_unit.name = "Dark Mage"
        enemy_unit.faction = FactionEnum.ENEMY
        enemy_unit.position = (3, 3)
        enemy_unit.current_hp = 18
        enemy_unit.max_hp = 18
        enemy_unit.ai_persona = "AGGRESSOR"
        enemy_unit.base_stats = {"STR": 9, "DEF": 5, "SPD": 8, "SKL": 7}
        
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
            "scenario_state": scenario_state,
            "inventory_system": inventory_system
        }
    
    def test_poison_status_effect(self, basic_status_scenario_setup):
        """
        Tests applying a poison status effect to a unit.
        
        This test:
        1. Applies a poison status effect to a unit
        2. Checks damage-over-time effects
        3. Verifies effect removal after duration expires
        """
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Define specific log file for poison test
        poison_log = os.path.join(LOG_DIR, "poison_status_effect.txt")
        if os.path.exists(poison_log):
            os.remove(poison_log)
            
        # Get test components
        game_state_manager = basic_status_scenario_setup["game_state_manager"]
        cli_display = basic_status_scenario_setup["cli_display"]
        scenario_state = basic_status_scenario_setup["scenario_state"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=poison_log
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get the unit to apply poison to
        unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        assert unit is not None, "Unit not found"
        
        # Store original stats
        original_hp = unit.current_hp
        
        # Define poison status effect
        poison_effect = {
            "name": "Poison",
            "duration": 3,
            "effect": "Deals 2 damage per turn",
            "stat_changes": {}
        }
        
        # Begin testing status effects
        visual_logger.log_turn_start(1)
        
        # Apply poison status
        visual_logger.log_action("SYSTEM", "STATUS_APPLIED", 
                               f"{poison_effect['name']} status applied to {unit.name}")
        visual_logger.log_action(unit.id, "STATUS_EFFECT", 
                               f"Affected by {poison_effect['name']} for {poison_effect['duration']} turns")
        
        # Store the status effect in scenario state
        if unit.id not in scenario_state["status_effects"]:
            scenario_state["status_effects"][unit.id] = {}
        
        scenario_state["status_effects"][unit.id][poison_effect["name"]] = {
            "duration": poison_effect["duration"],
            "effect": poison_effect["effect"],
            "stat_changes": poison_effect["stat_changes"].copy()
        }
        
        # Process end of turn effects for status effects
        visual_logger.log_phase_start(PhaseEnum.EVENT)
        visual_logger.log_action("SYSTEM", "STATUS_EFFECTS", "Processing end of turn status effects")
        
        # Apply poison damage
        if "Poison" in scenario_state["status_effects"].get(unit.id, {}):
            poison_damage = 2
            unit.current_hp = max(1, unit.current_hp - poison_damage)  # Prevent HP from going below 1
            
            visual_logger.log_action(unit.id, "POISON_DAMAGE", 
                                   f"{unit.name} takes {poison_damage} poison damage (HP: {unit.current_hp}/{unit.max_hp})")
        
        # Reduce status effect durations
        for unit_id, statuses in scenario_state["status_effects"].items():
            for status_name, status_info in list(statuses.items()):  # Use list() to allow dict modification during iteration
                status_info["duration"] -= 1
                
                target_unit = game_state_manager.get_unit(unit_id)
                visual_logger.log_action(unit_id, "STATUS_DURATION", 
                                       f"{status_name} duration: {status_info['duration']} turns remaining")
        
        # Log end of turn state
        visual_logger.log_end_of_turn_state(1)
        
        # Simulate another turn to show poison continuing
        visual_logger.log_turn_start(2)
        visual_logger.log_action("SYSTEM", "STATUS_EFFECTS", "Current status effects:")
        
        # Log active status effects
        for unit_id, statuses in scenario_state["status_effects"].items():
            target_unit = game_state_manager.get_unit(unit_id)
            
            if statuses:
                for status_name, status_info in statuses.items():
                    visual_logger.log_action(unit_id, "ACTIVE_STATUS", 
                                           f"{target_unit.name} is affected by {status_name} ({status_info['duration']} turns remaining)")
        
        # Apply poison damage for turn 2
        if "Poison" in scenario_state["status_effects"].get(unit.id, {}):
            hp_before = unit.current_hp
            poison_damage = 2
            unit.current_hp = max(1, unit.current_hp - poison_damage)  # Prevent HP from going below 1
            
            visual_logger.log_action(unit.id, "POISON_DAMAGE", 
                                   f"{unit.name} takes {poison_damage} poison damage (HP: {unit.current_hp}/{unit.max_hp})")
        
        # Reduce status effect durations again
        for unit_id, statuses in scenario_state["status_effects"].items():
            for status_name, status_info in list(statuses.items()):
                status_info["duration"] -= 1
                
                target_unit = game_state_manager.get_unit(unit_id)
                visual_logger.log_action(unit_id, "STATUS_DURATION", 
                                       f"{status_name} duration: {status_info['duration']} turns remaining")
                
                # Check if status effect has expired
                if status_info["duration"] <= 0:
                    # Remove the status effect
                    visual_logger.log_action(unit_id, "STATUS_REMOVED", 
                                           f"{status_name} effect has worn off")
                    
                    # Remove from status effects
                    del statuses[status_name]
        
        # Log end of second turn
        visual_logger.log_end_of_turn_state(2)
        visual_logger.finalize_log()
        
        # Verify poison damage was applied
        assert unit.current_hp < original_hp, "Poison should have reduced HP"
        assert unit.current_hp == original_hp - 4, "Unit should have taken 4 damage total (2 per turn for 2 turns)"
        
        # Verify log file was created
        assert os.path.exists(poison_log), f"Log file {poison_log} was not created"
        logger.info(f"Successfully created poison status effect log at {poison_log}")
        
    def test_stat_modifying_status_effect(self, basic_status_scenario_setup):
        """
        Tests applying a status effect that modifies unit stats.
        
        This test:
        1. Applies a weakness status effect that reduces a unit's strength
        2. Verifies stat modification 
        3. Tests stat restoration when the effect expires
        """
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Define specific log file for this test
        weakness_log = os.path.join(LOG_DIR, "weakness_status_effect.txt")
        if os.path.exists(weakness_log):
            os.remove(weakness_log)
            
        # Get test components
        game_state_manager = basic_status_scenario_setup["game_state_manager"]
        cli_display = basic_status_scenario_setup["cli_display"]
        scenario_state = basic_status_scenario_setup["scenario_state"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=weakness_log
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get the unit to apply weakness to
        unit = game_state_manager.get_unit("ENEMY_UNIT_1")
        assert unit is not None, "Enemy unit not found"
        
        # Store original stats
        original_stats = {
            "STR": unit.base_stats.get("STR", 0),
            "DEF": unit.base_stats.get("DEF", 0),
            "SPD": unit.base_stats.get("SPD", 0)
        }
        
        # Define weakness status effect
        weakness_effect = {
            "name": "Weakness",
            "duration": 2,
            "effect": "Reduces strength and speed",
            "stat_changes": {"STR": -2, "SPD": -1}
        }
        
        # Begin testing status effects
        visual_logger.log_turn_start(1)
        
        # Apply weakness status
        visual_logger.log_action("SYSTEM", "STATUS_APPLIED", 
                               f"{weakness_effect['name']} status applied to {unit.name}")
        visual_logger.log_action(unit.id, "STATUS_EFFECT", 
                               f"Affected by {weakness_effect['name']} for {weakness_effect['duration']} turns")
        
        # Apply stat changes from status effect
        for stat, change in weakness_effect["stat_changes"].items():
            current_value = unit.base_stats.get(stat, 0)
            unit.base_stats[stat] = max(1, current_value + change)  # Prevent stats from going below 1
            
            visual_logger.log_action(unit.id, "STAT_CHANGED", 
                                   f"{stat} {change:+d} ({current_value} → {unit.base_stats[stat]})")
        
        # Store the status effect in scenario state
        if unit.id not in scenario_state["status_effects"]:
            scenario_state["status_effects"][unit.id] = {}
        
        scenario_state["status_effects"][unit.id][weakness_effect["name"]] = {
            "duration": weakness_effect["duration"],
            "effect": weakness_effect["effect"],
            "stat_changes": weakness_effect["stat_changes"].copy()
        }
        
        # End turn 1
        visual_logger.log_end_of_turn_state(1)
        
        # Begin turn 2
        visual_logger.log_turn_start(2)
        
        # Reduce status effect durations
        for unit_id, statuses in scenario_state["status_effects"].items():
            for status_name, status_info in list(statuses.items()):
                status_info["duration"] -= 1
                
                target_unit = game_state_manager.get_unit(unit_id)
                visual_logger.log_action(unit_id, "STATUS_DURATION", 
                                       f"{status_name} duration: {status_info['duration']} turns remaining")
        
        # End turn 2
        visual_logger.log_end_of_turn_state(2)
        
        # Begin turn 3 - effect should expire
        visual_logger.log_turn_start(3)
        
        # Process status effects
        for unit_id, statuses in scenario_state["status_effects"].items():
            for status_name, status_info in list(statuses.items()):  # Use list to allow modification during iteration
                status_info["duration"] -= 1
                
                target_unit = game_state_manager.get_unit(unit_id)
                visual_logger.log_action(unit_id, "STATUS_DURATION", 
                                       f"{status_name} duration: {status_info['duration']} turns remaining")
                
                # Check if status effect has expired
                if status_info["duration"] <= 0:
                    # Remove the status effect
                    visual_logger.log_action(unit_id, "STATUS_REMOVED", 
                                           f"{status_name} effect has worn off")
                    
                    # Revert stat changes
                    for stat, change in status_info["stat_changes"].items():
                        current_value = target_unit.base_stats.get(stat, 0)
                        target_unit.base_stats[stat] = current_value - change  # Reverse the change
                        
                        visual_logger.log_action(unit_id, "STAT_RESTORED", 
                                               f"{stat} restored ({current_value} → {target_unit.base_stats[stat]})")
                    
                    # Remove from status effects
                    del statuses[status_name]
        
        # End turn 3
        visual_logger.log_end_of_turn_state(3)
        visual_logger.finalize_log()
        
        # Verify stats were modified and then restored
        assert unit.base_stats.get("STR", 0) == original_stats["STR"], "STR should be restored to original value"
        assert unit.base_stats.get("SPD", 0) == original_stats["SPD"], "SPD should be restored to original value"
        
        # Verify log file was created
        assert os.path.exists(weakness_log), f"Log file {weakness_log} was not created"
        logger.info(f"Successfully created weakness status effect log at {weakness_log}")
        
    def test_multiple_status_effects(self, basic_status_scenario_setup):
        """
        Tests applying multiple status effects to units simultaneously.
        
        This test:
        1. Applies multiple status effects to different units
        2. Verifies interactions between effects
        3. Tests different durations and removal timing
        """
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Define log file for this test
        if os.path.exists(STATUS_EFFECT_LOG):
            os.remove(STATUS_EFFECT_LOG)
            
        # Get test components
        game_state_manager = basic_status_scenario_setup["game_state_manager"]
        cli_display = basic_status_scenario_setup["cli_display"]
        scenario_state = basic_status_scenario_setup["scenario_state"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=STATUS_EFFECT_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get units for testing status effects
        player_unit = game_state_manager.get_unit("PLAYER_UNIT_1")
        enemy_unit = game_state_manager.get_unit("ENEMY_UNIT_1")
        assert player_unit is not None, "Player unit not found"
        assert enemy_unit is not None, "Enemy unit not found"
        
        # Define status effects to apply
        status_effects = {
            "Poison": {
                "target": player_unit.id,
                "duration": 3,
                "effect": "Deals 2 damage per turn",
                "stat_changes": {}
            },
            "Weaken": {
                "target": enemy_unit.id,
                "duration": 2,
                "effect": "Reduces strength",
                "stat_changes": {"STR": -2}
            }
        }
        
        # Store original stats
        original_stats = {
            player_unit.id: {
                "current_hp": player_unit.current_hp,
                "STR": player_unit.base_stats.get("STR", 0),
                "DEF": player_unit.base_stats.get("DEF", 0)
            },
            enemy_unit.id: {
                "current_hp": enemy_unit.current_hp,
                "STR": enemy_unit.base_stats.get("STR", 0),
                "DEF": enemy_unit.base_stats.get("DEF", 0)
            }
        }
        
        # Begin testing status effects
        visual_logger.log_turn_start(1)
        
        # Apply status effects
        for status_name, status_info in status_effects.items():
            target_id = status_info["target"]
            target_unit = game_state_manager.get_unit(target_id)
            
            visual_logger.log_action("SYSTEM", "STATUS_APPLIED", 
                                   f"{status_name} status applied to {target_unit.name}")
            visual_logger.log_action(target_id, "STATUS_EFFECT", 
                                   f"Affected by {status_name} for {status_info['duration']} turns")
            
            # Apply stat changes from status effect
            for stat, change in status_info["stat_changes"].items():
                current_value = target_unit.base_stats.get(stat, 0)
                target_unit.base_stats[stat] = max(1, current_value + change)  # Prevent stats from going below 1
                
                visual_logger.log_action(target_id, "STAT_CHANGED", 
                                       f"{stat} {change:+d} ({current_value} → {target_unit.base_stats[stat]})")
            
            # Store the status effect in scenario state
            if target_id not in scenario_state["status_effects"]:
                scenario_state["status_effects"][target_id] = {}
            
            scenario_state["status_effects"][target_id][status_name] = {
                "duration": status_info["duration"],
                "effect": status_info["effect"],
                "stat_changes": status_info["stat_changes"].copy()
            }
        
        # Process end of turn effects for status effects
        visual_logger.log_phase_start(PhaseEnum.EVENT)
        visual_logger.log_action("SYSTEM", "STATUS_EFFECTS", "Processing end of turn status effects")
        
        # Process poison damage
        if "Poison" in scenario_state["status_effects"].get(player_unit.id, {}):
            # Apply poison damage
            poison_damage = 2
            player_unit.current_hp = max(1, player_unit.current_hp - poison_damage)  # Prevent HP from going below 1
            
            visual_logger.log_action(player_unit.id, "POISON_DAMAGE", 
                                   f"{player_unit.name} takes {poison_damage} poison damage (HP: {player_unit.current_hp}/{player_unit.max_hp})")
        
        # Reduce status effect durations
        for unit_id, statuses in scenario_state["status_effects"].items():
            for status_name, status_info in list(statuses.items()):  # Use list() to allow dict modification during iteration
                status_info["duration"] -= 1
                
                unit = game_state_manager.get_unit(unit_id)
                visual_logger.log_action(unit_id, "STATUS_DURATION", 
                                       f"{status_name} duration: {status_info['duration']} turns remaining")
                
                # Check if status effect has expired
                if status_info["duration"] <= 0:
                    # Remove the status effect
                    visual_logger.log_action(unit_id, "STATUS_REMOVED", 
                                           f"{status_name} effect has worn off")
                    
                    # Revert stat changes
                    for stat, change in status_info["stat_changes"].items():
                        current_value = unit.base_stats.get(stat, 0)
                        unit.base_stats[stat] = current_value - change  # Reverse the change
                        
                        visual_logger.log_action(unit_id, "STAT_RESTORED", 
                                               f"{stat} restored ({current_value} → {unit.base_stats[stat]})")
                    
                    # Remove from status effects
                    del statuses[status_name]
        
        # Log end of turn state
        visual_logger.log_end_of_turn_state(1)
        
        # Log second turn to show status effects continuing
        visual_logger.log_turn_start(2)
        visual_logger.log_action("SYSTEM", "STATUS_EFFECTS", "Current status effects:")
        
        # Log active status effects
        for unit_id, statuses in scenario_state["status_effects"].items():
            unit = game_state_manager.get_unit(unit_id)
            
            if statuses:
                for status_name, status_info in statuses.items():
                    visual_logger.log_action(unit_id, "ACTIVE_STATUS", 
                                           f"{unit.name} is affected by {status_name} ({status_info['duration']} turns remaining)")
            else:
                visual_logger.log_action(unit_id, "NO_STATUS", 
                                       f"{unit.name} is not affected by any status effects")
        
        # Log end of second turn
        visual_logger.log_end_of_turn_state(2)
        visual_logger.finalize_log()
        
        # Verify status effects were applied correctly
        # Check poison damage
        assert player_unit.current_hp < original_stats[player_unit.id]["current_hp"], "Poison should have reduced HP"
        
        # Check stat reduction from Weaken
        assert enemy_unit.base_stats.get("STR", 0) < original_stats[enemy_unit.id]["STR"], "Weaken should have reduced STR"
        
        # Verify log file was created
        assert os.path.exists(STATUS_EFFECT_LOG), f"Log file {STATUS_EFFECT_LOG} was not created"
        logger.info(f"Successfully created status effect mechanics log at {STATUS_EFFECT_LOG}") 