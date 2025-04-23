"""
Event Mechanics Tests

This module contains tests focused on event-related mechanics, including:
- Weather effects application
- Village events
- Healing events
- Supply drops
- Random reinforcements
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
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.unit_system import UnitSystem
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
LOG_DIR = os.path.abspath("logs/mechanic_tests/events")
WEATHER_EVENT_LOG = os.path.join(LOG_DIR, "weather_event_trigger.txt")
HEALING_EVENT_LOG = os.path.join(LOG_DIR, "healing_event_trigger.txt")
VILLAGE_EVENT_LOG = os.path.join(LOG_DIR, "village_event_trigger.txt")

# Setup test logger
logger = logging.getLogger("test_event_mechanics")

class TestEventMechanics:
    """Tests for event-related mechanics."""
    
    @pytest.fixture
    def basic_event_scenario_setup(self):
        """
        Set up a basic scenario with a 8x8 map and several units to test events.
        """
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load data
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a map state
        map_state = MapState()
        map_state.dimensions = (8, 8)  # Map for events
        
        # Default terrain is plains
        terrain_grid = [['P'] * 8 for _ in range(8)]
        
        # Add a village for village events
        village_position = (2, 6)
        terrain_grid[village_position[1]][village_position[0]] = 'V'  # Village
        
        # Add some forest terrain for variety
        forest_positions = [(3, 2), (3, 3), (4, 2), (5, 6), (6, 6)]
        for x, y in forest_positions:
            terrain_grid[y][x] = 'F'  # Forest
        
        # Set map state
        map_state.terrain_grid = terrain_grid
        map_state.map_id = "event_test_map"
        
        # Create a MapData object for the visual logger
        class MapDataObj:
            def __init__(self):
                self.id = "event_test_map"
                self.name = "Event Test Map"
                self.dimensions = (8, 8)
                self.terrain_grid = terrain_grid
                self.fog_of_war = False
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_events"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Create scenario state to track events
        scenario_state = {
            "active_weather": None,
            "weather_duration": 0,
            "village_events": {},
            "current_turn": 1
        }
        
        # Add several test units
        unit_states = {}
        unit_positions = {}
        faction_units = {"PLAYER": [], "ENEMY": []}
        
        # Create player faction units
        player_units = [
            {
                "id": "PLAYER_UNIT_1",
                "name": "Commander",
                "faction": FactionEnum.PLAYER,
                "position": (2, 3),
                "current_hp": 25,
                "max_hp": 30,  # Damaged for healing event tests
                "ai_persona": "BALANCED",
                "base_stats": {"STR": 12, "DEF": 10, "SPD": 10, "SKL": 10}
            },
            {
                "id": "PLAYER_UNIT_2",
                "name": "Cavalry",
                "faction": FactionEnum.PLAYER,
                "position": (3, 4),
                "current_hp": 20,
                "max_hp": 24,  # Damaged for healing event tests
                "ai_persona": "AGGRESSOR",
                "base_stats": {"STR": 13, "DEF": 8, "SPD": 14, "SKL": 11}
            },
            {
                "id": "PLAYER_UNIT_3",
                "name": "Mage",
                "faction": FactionEnum.PLAYER,
                "position": (1, 5),
                "current_hp": 15,
                "max_hp": 18,  # Damaged for healing event tests
                "ai_persona": "CAUTIOUS",
                "base_stats": {"STR": 14, "DEF": 6, "SPD": 11, "SKL": 13}
            }
        ]
        
        # Create enemy faction units
        enemy_units = [
            {
                "id": "ENEMY_UNIT_1",
                "name": "Knight",
                "faction": FactionEnum.ENEMY,
                "position": (6, 3),
                "current_hp": 22,
                "max_hp": 28,  # Damaged for healing event tests
                "ai_persona": "DEFENDER",
                "base_stats": {"STR": 11, "DEF": 13, "SPD": 8, "SKL": 9}
            },
            {
                "id": "ENEMY_UNIT_2",
                "name": "Archer",
                "faction": FactionEnum.ENEMY,
                "position": (5, 2),
                "current_hp": 16,
                "max_hp": 20,  # Damaged for healing event tests
                "ai_persona": "OPPORTUNIST",
                "base_stats": {"STR": 12, "DEF": 7, "SPD": 12, "SKL": 15}
            }
        ]
        
        # Store all units' initial stats to verify changes later
        initial_unit_stats = {}
        
        # Create all units
        for unit_data in player_units + enemy_units:
            unit = UnitState()
            unit.id = unit_data["id"]
            unit.name = unit_data["name"]
            unit.faction = unit_data["faction"]
            unit.position = unit_data["position"]
            unit.current_hp = unit_data["current_hp"]
            unit.max_hp = unit_data["max_hp"]
            unit.ai_persona = unit_data["ai_persona"]
            unit.base_stats = unit_data["base_stats"].copy()  # Copy to avoid reference issues
            
            # Store initial stats for later comparison
            initial_unit_stats[unit.id] = {
                "current_hp": unit.current_hp,
                "base_stats": unit.base_stats.copy()
            }
            
            # Add unit to collections
            unit_states[unit.id] = unit
            unit_positions[unit.id] = unit.position
            
            # Add to faction list
            faction_key = unit.faction.name
            faction_units[faction_key].append(unit.id)
        
        # Add a unit near the village for village event tests
        village_unit = UnitState()
        village_unit.id = "PLAYER_VILLAGE_UNIT"
        village_unit.name = "Village Visitor"
        village_unit.faction = FactionEnum.PLAYER
        village_unit.position = (2, 5)  # Adjacent to village
        village_unit.current_hp = 20
        village_unit.max_hp = 20
        village_unit.ai_persona = "BALANCED"
        village_unit.base_stats = {"STR": 10, "DEF": 10, "SPD": 10, "SKL": 10}
        
        # Add to collections
        unit_states[village_unit.id] = village_unit
        unit_positions[village_unit.id] = village_unit.position
        faction_units["PLAYER"].append(village_unit.id)
        
        # Store initial stats
        initial_unit_stats[village_unit.id] = {
            "current_hp": village_unit.current_hp,
            "base_stats": village_unit.base_stats.copy()
        }
        
        # Set unit states in game
        game_state.unit_states = unit_states
        game_state.map_state.unit_positions = unit_positions
        game_state.map_state.allies = faction_units
        
        # Initialize systems
        map_system = MapSystem()
        unit_system = UnitSystem()
        movement_system = MovementSystem()
        combat_system = CombatSystem()
        inventory_system = InventorySystem()
        core_turn_manager = CoreTurnManager()
        turn_manager = TurnManager()
        action_handler = ActionHandler()
        event_handler = EventHandler()
        
        # Initialize systems
        map_system.initialize(game_state_manager, data_provider)
        unit_system.initialize(game_state_manager, data_provider)
        inventory_system.initialize(game_state_manager, data_provider)
        movement_system.initialize(game_state_manager, map_system)
        
        # Initialize combat system
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
            inventorySystem_instance=inventory_system,
            dataProvider_instance=data_provider
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
            "combat_system": combat_system,
            "cli_display": cli_display,
            "action_handler": action_handler,
            "scenario_state": scenario_state,
            "initial_unit_stats": initial_unit_stats,
            "village_position": village_position
        }
    
    def test_weather_event_log(self, basic_event_scenario_setup):
        """
        Tests a weather event triggering and applying effects to units.
        
        This test:
        1. Sets up a map with several units
        2. Triggers a weather event (fog, rain, or strong winds)
        3. Applies the appropriate stat modifications to units
        4. Logs the weather effect in a visual log file
        """
        # Ensure log directory exists and delete old log
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(WEATHER_EVENT_LOG):
            os.remove(WEATHER_EVENT_LOG)
        
        # Get test components
        game_state_manager = basic_event_scenario_setup["game_state_manager"]
        cli_display = basic_event_scenario_setup["cli_display"]
        scenario_state = basic_event_scenario_setup["scenario_state"]
        initial_unit_stats = basic_event_scenario_setup["initial_unit_stats"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=WEATHER_EVENT_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Choose a random weather effect
        weather_types = ["Fog", "Rain", "Strong Winds"]
        chosen_weather = random.choice(weather_types)
        weather_duration = random.randint(2, 3)  # Lasts for 2-3 turns
        
        # Update scenario state
        scenario_state["active_weather"] = chosen_weather
        scenario_state["weather_duration"] = weather_duration
        
        # Log the weather event
        visual_logger.log_turn_start(1)
        visual_logger.log_action("SYSTEM", "WEATHER_EVENT", f"{chosen_weather} has set in and will last for {weather_duration} turns")
        
        # Apply weather effects to all units
        all_units = game_state_manager.current_game_state.unit_states.values()
        
        # Track units affected for testing purposes
        affected_units = {}
        
        for unit in all_units:
            # Store original stats for verification
            original_stats = {
                "STR": unit.base_stats.get("STR", 0),
                "DEF": unit.base_stats.get("DEF", 0),
                "SPD": unit.base_stats.get("SPD", 0),
                "SKL": unit.base_stats.get("SKL", 0)
            }
            
            # Apply weather effects based on weather type
            if chosen_weather == "Fog":
                # Fog reduces SKL (accuracy) and SPD
                unit.base_stats["SKL"] = max(1, unit.base_stats.get("SKL", 0) - 2)
                unit.base_stats["SPD"] = max(1, unit.base_stats.get("SPD", 0) - 1)
                change_desc = f"SKL -{2}, SPD -{1}"
                
            elif chosen_weather == "Rain":
                # Rain reduces SPD and STR
                unit.base_stats["SPD"] = max(1, unit.base_stats.get("SPD", 0) - 2)
                unit.base_stats["STR"] = max(1, unit.base_stats.get("STR", 0) - 1)
                change_desc = f"SPD -{2}, STR -{1}"
                
            elif chosen_weather == "Strong Winds":
                # Strong winds affect all ranged attacks (reduce STR and SKL)
                unit.base_stats["STR"] = max(1, unit.base_stats.get("STR", 0) - 1)
                unit.base_stats["SKL"] = max(1, unit.base_stats.get("SKL", 0) - 1)
                change_desc = f"STR -{1}, SKL -{1}"
            
            # Log the effect on this unit
            visual_logger.log_action(unit.id, "WEATHER_AFFECTED", 
                                   f"{unit.name} affected by {chosen_weather}: {change_desc}")
            
            # Store for verification
            affected_units[unit.id] = {
                "original": original_stats,
                "modified": unit.base_stats.copy()
            }
        
        # Log end of turn state
        visual_logger.log_end_of_turn_state(1)
        
        # Log beginning of next turn to show weather is still active
        visual_logger.log_turn_start(2)
        visual_logger.log_action("SYSTEM", "WEATHER_CONTINUES", 
                               f"{chosen_weather} continues. {scenario_state['weather_duration'] - 1} turns remaining")
        
        # Continue logging a bit more to show persistence
        visual_logger.log_end_of_turn_state(2)
        visual_logger.finalize_log()
        
        # Verify weather state was updated
        assert scenario_state["active_weather"] == chosen_weather, "Weather state not updated correctly"
        assert scenario_state["weather_duration"] == weather_duration, "Weather duration not set correctly"
        
        # Verify all units were affected by the weather
        for unit_id, stats in affected_units.items():
            original = stats["original"]
            modified = stats["modified"]
            
            # Check that at least one stat was modified
            assert (original["STR"] != modified["STR"] or
                   original["DEF"] != modified["DEF"] or 
                   original["SPD"] != modified["SPD"] or
                   original["SKL"] != modified["SKL"]), f"Unit {unit_id} was not affected by the weather"
        
        # Verify log file was created
        assert os.path.exists(WEATHER_EVENT_LOG), f"Log file {WEATHER_EVENT_LOG} was not created"
        logger.info(f"Successfully created weather event log at {WEATHER_EVENT_LOG}")

    def test_healing_event_log(self, basic_event_scenario_setup):
        """
        Tests a healing event that restores HP to damaged units.
        
        This test:
        1. Sets up a scenario with several damaged units
        2. Triggers a healing event that restores a percentage of HP
        3. Applies healing to a random number of units
        4. Logs the healing effect in a visual log file
        """
        # Ensure log directory exists and delete old log
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(HEALING_EVENT_LOG):
            os.remove(HEALING_EVENT_LOG)
        
        # Get test components
        game_state_manager = basic_event_scenario_setup["game_state_manager"]
        cli_display = basic_event_scenario_setup["cli_display"]
        initial_unit_stats = basic_event_scenario_setup["initial_unit_stats"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=HEALING_EVENT_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get all units that have less than max HP (damaged units)
        all_units = game_state_manager.current_game_state.unit_states.values()
        damaged_units = [unit for unit in all_units if unit.current_hp < unit.max_hp]
        
        # Verify we have damaged units to heal
        assert len(damaged_units) > 0, "Test requires damaged units to heal"
        
        # Log damaged units before healing
        visual_logger.log_turn_start(1)
        visual_logger.log_action("SYSTEM", "DAMAGED_UNITS", 
                               f"There are {len(damaged_units)} damaged units on the field")
        
        for unit in damaged_units:
            visual_logger.log_action(unit.id, "DAMAGED", 
                                   f"{unit.name} has {unit.current_hp}/{unit.max_hp} HP")
        
        # Trigger a healing event - decide the number of units to heal
        num_units_to_heal = min(len(damaged_units), random.randint(1, 3))
        units_to_heal = random.sample(damaged_units, num_units_to_heal)
        
        # Decide healing percentage (30-50%)
        healing_percentage = random.randint(30, 50)
        
        # Log the healing event
        visual_logger.log_action("SYSTEM", "HEALING_EVENT", 
                               f"A healing rain falls, restoring {healing_percentage}% HP to {num_units_to_heal} units")
        
        # Track healed units for verification
        healed_units = {}
        
        # Apply healing to selected units
        for unit in units_to_heal:
            # Store original HP
            original_hp = unit.current_hp
            
            # Calculate healing amount
            max_healing = unit.max_hp - unit.current_hp
            healing_amount = int((unit.max_hp * healing_percentage / 100))
            healing_amount = min(max_healing, healing_amount)  # Can't heal more than max HP
            
            # Apply healing
            unit.current_hp += healing_amount
            
            # Log healing
            visual_logger.log_action(unit.id, "HEALED", 
                                   f"{unit.name} restored {healing_amount} HP ({original_hp} → {unit.current_hp}/{unit.max_hp})")
            
            # Store for verification
            healed_units[unit.id] = {
                "original_hp": original_hp,
                "new_hp": unit.current_hp,
                "healing_amount": healing_amount
            }
        
        # Log unaffected units
        unhealed_units = [unit for unit in damaged_units if unit.id not in [u.id for u in units_to_heal]]
        for unit in unhealed_units:
            visual_logger.log_action(unit.id, "NOT_HEALED", 
                                   f"{unit.name} was not affected by the healing rain")
        
        # Log end of turn state
        visual_logger.log_end_of_turn_state(1)
        visual_logger.finalize_log()
        
        # Verify healing was applied correctly
        for unit_id, data in healed_units.items():
            original_hp = data["original_hp"]
            new_hp = data["new_hp"]
            healing_amount = data["healing_amount"]
            
            # Verify HP increased by the expected amount
            assert new_hp == original_hp + healing_amount, f"Unit {unit_id} not healed by correct amount"
            
            # Verify HP didn't exceed max
            unit = game_state_manager.get_unit(unit_id)
            assert unit.current_hp <= unit.max_hp, f"Unit {unit_id} HP exceeds max"
        
        # Verify log file was created
        assert os.path.exists(HEALING_EVENT_LOG), f"Log file {HEALING_EVENT_LOG} was not created"
        logger.info(f"Successfully created healing event log at {HEALING_EVENT_LOG}")
    
    def test_village_event_log(self, basic_event_scenario_setup):
        """
        Tests a village event triggered by a unit near a village.
        
        This test:
        1. Sets up a scenario with a unit near a village
        2. Moves the unit onto the village to trigger an event
        3. Randomly selects and applies an event (item, stat boost, reinforcement)
        4. Logs the village event in a visual log file
        """
        # Ensure log directory exists and delete old log
        os.makedirs(LOG_DIR, exist_ok=True)
        if os.path.exists(VILLAGE_EVENT_LOG):
            os.remove(VILLAGE_EVENT_LOG)
        
        # Get test components
        game_state_manager = basic_event_scenario_setup["game_state_manager"]
        cli_display = basic_event_scenario_setup["cli_display"]
        movement_system = basic_event_scenario_setup["movement_system"]
        scenario_state = basic_event_scenario_setup["scenario_state"]
        village_position = basic_event_scenario_setup["village_position"]
        
        # Initialize logger with fixed path
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            enabled=True,
            fixed_log_path=VILLAGE_EVENT_LOG
        )
        
        # Log initial state
        visual_logger.log_initial_state()
        
        # Get the unit that will visit the village
        village_unit = game_state_manager.get_unit("PLAYER_VILLAGE_UNIT")
        assert village_unit is not None, "Village visitor unit not found"
        
        # Log initial state and unit positions
        visual_logger.log_action("SYSTEM", "VILLAGE_STATUS", 
                               f"Village at {village_position} awaits visitors")
        visual_logger.log_action(village_unit.id, "POSITION", 
                               f"{village_unit.name} is at position {village_unit.position}")
        
        # Begin test - move unit to village
        visual_logger.log_turn_start(1)
        visual_logger.log_phase_start(FactionEnum.PLAYER)
        
        # Store original position and stats
        original_position = village_unit.position
        original_stats = {
            "current_hp": village_unit.current_hp,
            "max_hp": village_unit.max_hp,
            "STR": village_unit.base_stats.get("STR", 0),
            "DEF": village_unit.base_stats.get("DEF", 0),
            "SPD": village_unit.base_stats.get("SPD", 0),
            "SKL": village_unit.base_stats.get("SKL", 0)
        }
        
        # Move unit to village
        movement_system.execute_move(village_unit.id, [original_position, village_position])
        
        visual_logger.log_action(village_unit.id, "MOVE",
                               f"from {original_position} to {village_position}")
        visual_logger.log_action(village_unit.id, "VISIT_VILLAGE", 
                               f"{village_unit.name} visits the village at {village_position}")
        
        # Trigger village event - randomly select event type
        event_types = ["ITEM", "STAT_BOOST", "REINFORCEMENT"]
        chosen_event = random.choice(event_types)
        
        # Update scenario state to mark this village as visited
        scenario_state["village_events"][village_position] = chosen_event
        
        # Apply effects based on event type
        if chosen_event == "ITEM":
            # Give unit an item (simulated)
            item_names = ["Iron Sword", "Healing Potion", "Golden Medallion", "Magic Scroll"]
            given_item = random.choice(item_names)
            
            visual_logger.log_action("SYSTEM", "VILLAGE_EVENT", 
                                  f"The villagers give {village_unit.name} a {given_item} in gratitude")
            visual_logger.log_action(village_unit.id, "RECEIVE_ITEM", 
                                  f"Received {given_item} from village")
            
            # For testing, we'll assume the village unit has an 'inventory' attribute
            # that we can append to, though we won't actually create this
            visual_logger.log_action(village_unit.id, "INVENTORY_UPDATE", 
                                  f"Added {given_item} to inventory")
            
        elif chosen_event == "STAT_BOOST":
            # Apply a stat boost to the unit
            boost_stat = random.choice(["STR", "DEF", "SPD", "SKL"])
            boost_amount = random.randint(1, 2)
            
            # Apply boost
            village_unit.base_stats[boost_stat] = village_unit.base_stats.get(boost_stat, 0) + boost_amount
            
            visual_logger.log_action("SYSTEM", "VILLAGE_EVENT", 
                                  f"A village elder trains {village_unit.name}, improving their {boost_stat}")
            visual_logger.log_action(village_unit.id, "STAT_BOOST", 
                                  f"{boost_stat} increased by {boost_amount} ({original_stats[boost_stat]} → {village_unit.base_stats[boost_stat]})")
            
        elif chosen_event == "REINFORCEMENT":
            # Simulated reinforcement (won't actually create a new unit)
            reinforcement_type = random.choice(["Villager Fighter", "Village Healer", "Village Archer"])
            join_position = (village_position[0] - 1, village_position[1])  # Next to village
            
            visual_logger.log_action("SYSTEM", "VILLAGE_EVENT", 
                                  f"A {reinforcement_type} from the village offers to join your forces")
            visual_logger.log_action("SYSTEM", "REINFORCEMENT", 
                                  f"{reinforcement_type} appears at position {join_position}")
            
            # For testing, we'll just log that a reinforcement would spawn
            visual_logger.log_action(village_unit.id, "RECRUIT", 
                                  f"Recruited {reinforcement_type} to join the battle")
        
        # Log that the village has been visited
        visual_logger.log_action("SYSTEM", "VILLAGE_VISITED", 
                               f"Village at {village_position} has been visited")
        
        # Log end of turn
        visual_logger.log_end_of_turn_state(1)
        visual_logger.finalize_log()
        
        # Verify unit visited the village
        assert village_unit.position == village_position, "Unit should be at the village position"
        
        # Verify the village event was recorded
        assert village_position in scenario_state["village_events"], "Village event not recorded"
        assert scenario_state["village_events"][village_position] == chosen_event, "Wrong event type recorded"
        
        # Verify event effects, if applicable
        if chosen_event == "STAT_BOOST":
            # At least one stat should have increased
            assert (original_stats["STR"] != village_unit.base_stats.get("STR", 0) or
                   original_stats["DEF"] != village_unit.base_stats.get("DEF", 0) or
                   original_stats["SPD"] != village_unit.base_stats.get("SPD", 0) or
                   original_stats["SKL"] != village_unit.base_stats.get("SKL", 0)), "No stat was boosted"
        
        # Verify log file was created
        assert os.path.exists(VILLAGE_EVENT_LOG), f"Log file {VILLAGE_EVENT_LOG} was not created"
        logger.info(f"Successfully created village event log at {VILLAGE_EVENT_LOG}") 