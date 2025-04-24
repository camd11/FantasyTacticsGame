"""
AI Scenario 05: Complex Strategic Battle (Max 5 Turns)

This scenario tests multiple AI units with different personas
in a complex terrain with strategic objectives.

Features:
- Multiple terrain types with tactical advantages
- Choke points and strategic positions
- Special objectives (seize point, defend point)
- Mixed unit types with varied capabilities
- Asymmetric unit distribution
"""

import pytest
import logging
from typing import Dict, Any
from unittest.mock import Mock
import os
import random

# Import the required modules
from src.core_engine.game_state import GameStateManager, FactionEnum, GameState, MapState, UnitState, DispositionEnum
from src.core_engine.data_provider import DataProvider, TerrainTypeEnum

# Import gameplay systems
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

# Import AI components
from src.gameplay_systems.ai.ai_manager import AIManager
from src.gameplay_systems.ai.strategic_evaluator import StrategicEvaluator
from src.gameplay_systems.ai.tactical_executor import TacticalExecutor
from src.gameplay_systems.ai.utility_scorer import UtilityScorer

# Import for visual logging
from src.input.cli_display import CLIDisplay
from src.utils.visual_logger import VisualScenarioLogger

# Setup test logger
logger = logging.getLogger("test_ai_scenario_05")

class TestAIScenario05:
    """Test suite for AI Scenario 05: Complex Strategic Battle (Max 5 Turns)."""
    
    @pytest.fixture
    def scenario_setup(self):
        """Load the complex strategic AI test scenario and set up the game state."""
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load all data from the data directory
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a complex map state
        map_state = MapState()
        map_state.dimensions = (20, 15)  # Larger map
        
        # Default terrain is plains
        terrain_grid = [['P'] * 20 for _ in range(15)]
        
        # Create a river that winds through the map
        river_path = [(0, 7), (1, 7), (2, 7), (3, 8), (4, 9), (5, 10), (6, 10), 
                       (7, 10), (8, 10), (9, 9), (10, 8), (11, 7), (12, 6), 
                       (13, 6), (14, 6), (15, 6), (16, 7), (17, 8), (18, 9), (19, 10)]
        
        for x, y in river_path:
            terrain_grid[y][x] = 'R'  # River
        
        # Add bridges at strategic crossing points
        bridges = [(3, 7), (9, 10), (16, 6)]
        for x, y in bridges:
            terrain_grid[y][x] = 'B'  # Bridge
        
        # Add forests in clusters for tactical cover
        forest_clusters = [
            [(2, 2), (2, 3), (3, 2), (3, 3), (4, 2)],  # Top-left forest
            [(5, 5), (6, 5), (7, 5), (5, 6), (6, 6)],  # Central forest
            [(14, 3), (15, 3), (16, 3), (14, 4), (15, 4)],  # Top-right forest
            [(3, 12), (4, 12), (5, 12), (3, 13), (4, 13)],  # Bottom-left forest
            [(17, 12), (18, 12), (17, 13), (18, 13)]  # Bottom-right forest
        ]
        
        for cluster in forest_clusters:
            for x, y in cluster:
                terrain_grid[y][x] = 'F'  # Forest
        
        # Add mountains as impassable barriers
        mountain_ranges = [
            [(8, 2), (9, 2), (10, 2), (9, 3)],  # Northern mountains
            [(14, 11), (15, 11), (16, 11), (15, 12)]  # Southern mountains
        ]
        
        for mountain_range in mountain_ranges:
            for x, y in mountain_range:
                terrain_grid[y][x] = 'M'  # Mountain
        
        # Add strategic villages (healing/objectives)
        villages = [(2, 5), (17, 4), (5, 13), (12, 12)]
        for x, y in villages:
            terrain_grid[y][x] = 'V'  # Village
        
        # Add castle/throne (seize point objective)
        terrain_grid[10][10] = 'T'  # Throne (seize point)
        
        # Set map state
        map_state.terrain_grid = terrain_grid
        map_state.map_id = "complex_strategic_battle"
        
        # Create a MapData object for the visual logger
        class MapDataObj:
            def __init__(self):
                self.id = "complex_strategic_battle"
                self.name = "Complex Strategic Battle"
                self.dimensions = (20, 15)
                self.terrain_grid = terrain_grid
                self.fog_of_war = False
                self.seize_point = (10, 10)  # Throne position
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_chapter_ai_05"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Add units
        self._add_units(game_state_manager)
        
        # Initialize systems
        game_systems = self._initialize_systems(game_state_manager, data_provider)
        
        # Initialize CLIDisplay for visual logging
        cli_display = CLIDisplay()
        cli_display.game_state_manager = game_state_manager
        cli_display.map_system = game_systems["map_system"]
        cli_display.unit_system = game_systems["unit_system"]
        cli_display.data_provider = data_provider
        
        # Create visual logger
        abs_path = os.path.abspath(".")
        print(f"Current working directory: {abs_path}")
        
        # Try creating a simple text file directly in the current directory
        try:
            with open("test_writing_here.txt", "w") as f:
                f.write("Test file creation in current directory\n")
            print("Successfully wrote to current directory")
        except Exception as e:
            print(f"Failed to write to current directory: {e}")
        
        # Use an absolute path for logs
        log_dir = os.path.abspath("logs")
        print(f"Absolute logs path: {log_dir}")
        os.makedirs(log_dir, exist_ok=True)
        
        # Try writing a test file to the logs directory
        try:
            with open(os.path.join(log_dir, "test_file.txt"), "w") as f:
                f.write("Test log file\n")
            print(f"Successfully wrote test file to logs directory")
        except Exception as e:
            print(f"Failed to write test file to logs directory: {e}")
        
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            log_dir=log_dir,
            enabled=True
        )
        
        # Setup engine
        engine = EngineCore(
            game_state_manager=game_state_manager,
            data_provider=data_provider,
            turn_manager=game_systems["core_turn_manager"],
            action_handler=game_systems["action_handler"],
            event_handler=game_systems["event_handler"],
            ai_manager=game_systems["ai_manager"],
            combat_system=game_systems["combat_system"],
            map_system=game_systems["map_system"],
            movement_system=game_systems["movement_system"],
            unit_system=game_systems["unit_system"],
            input_handler=None,  # No input handler for AI vs AI
            ai_vs_ai=True,
            ascii_display=True,
            display=cli_display
        )
        
        # Set visual logger in engine
        engine.set_visual_logger(visual_logger)
        
        return {
            "game_state_manager": game_state_manager,
            "engine": engine,
            "visual_logger": visual_logger,
            "systems": game_systems,
            "cli_display": cli_display
        }
    
    def _add_units(self, game_state_manager):
        """Add units to the game state with various personas, positions, and specialties."""
        unit_states = {}
        unit_positions = {}
        
        # Player faction units (North side)
        player_units = [
            # Main attackers
            {
                "id": "PLAYER_LORD",
                "name": "Commander",
                "faction": FactionEnum.PLAYER,
                "position": (6, 2),
                "current_hp": 40,
                "max_hp": 40,
                "ai_persona": "AGGRESSOR",
                "stats": {"STR": 15, "DEF": 10, "SPD": 12, "SKL": 14}
            },
            {
                "id": "PLAYER_KNIGHT",
                "name": "Heavy Knight",
                "faction": FactionEnum.PLAYER,
                "position": (5, 3),
                "current_hp": 45,
                "max_hp": 45,
                "ai_persona": "DEFENDER",
                "stats": {"STR": 14, "DEF": 16, "SPD": 6, "SKL": 9}
            },
            {
                "id": "PLAYER_CAVALRY",
                "name": "Paladin",
                "faction": FactionEnum.PLAYER,
                "position": (7, 3),
                "current_hp": 38,
                "max_hp": 38,
                "ai_persona": "AGGRESSOR",
                "stats": {"STR": 13, "DEF": 11, "SPD": 14, "SKL": 12}
            },
            # Support units
            {
                "id": "PLAYER_ARCHER",
                "name": "Archer",
                "faction": FactionEnum.PLAYER,
                "position": (4, 4),
                "current_hp": 30,
                "max_hp": 30,
                "ai_persona": "OPPORTUNIST",
                "stats": {"STR": 11, "DEF": 7, "SPD": 10, "SKL": 15}
            },
            {
                "id": "PLAYER_CLERIC",
                "name": "Cleric",
                "faction": FactionEnum.PLAYER,
                "position": (6, 4),
                "current_hp": 25,
                "max_hp": 25,
                "ai_persona": "SUPPORT",
                "stats": {"STR": 6, "DEF": 5, "SPD": 11, "SKL": 8},
                "healing_capability": True
            },
            {
                "id": "PLAYER_MAGE",
                "name": "Mage",
                "faction": FactionEnum.PLAYER,
                "position": (8, 4),
                "current_hp": 28,
                "max_hp": 28,
                "ai_persona": "CAUTIOUS",
                "stats": {"STR": 14, "DEF": 6, "SPD": 10, "SKL": 13}
            },
            # Flanking units
            {
                "id": "PLAYER_PEGASUS",
                "name": "Pegasus Knight",
                "faction": FactionEnum.PLAYER,
                "position": (3, 1),
                "current_hp": 32,
                "max_hp": 32,
                "ai_persona": "OPPORTUNIST",
                "stats": {"STR": 10, "DEF": 8, "SPD": 16, "SKL": 14}
            },
            {
                "id": "PLAYER_THIEF",
                "name": "Rogue",
                "faction": FactionEnum.PLAYER,
                "position": (9, 1),
                "current_hp": 28,
                "max_hp": 28,
                "ai_persona": "OPPORTUNIST",
                "stats": {"STR": 9, "DEF": 7, "SPD": 17, "SKL": 16}
            }
        ]
        
        # Enemy faction units (defending the castle)
        enemy_units = [
            # Leader and main defenders
            {
                "id": "ENEMY_GENERAL",
                "name": "General",
                "faction": FactionEnum.ENEMY,
                "position": (10, 9),  # Near the throne
                "current_hp": 50,
                "max_hp": 50,
                "ai_persona": "DEFENDER",
                "stats": {"STR": 16, "DEF": 18, "SPD": 7, "SKL": 12}
            },
            {
                "id": "ENEMY_KNIGHT1",
                "name": "Knight",
                "faction": FactionEnum.ENEMY,
                "position": (9, 8),
                "current_hp": 42,
                "max_hp": 42,
                "ai_persona": "DEFENDER",
                "stats": {"STR": 13, "DEF": 15, "SPD": 6, "SKL": 10}
            },
            {
                "id": "ENEMY_KNIGHT2",
                "name": "Knight",
                "faction": FactionEnum.ENEMY,
                "position": (11, 8),
                "current_hp": 42,
                "max_hp": 42,
                "ai_persona": "DEFENDER",
                "stats": {"STR": 14, "DEF": 14, "SPD": 7, "SKL": 9}
            },
            # Ranged units
            {
                "id": "ENEMY_ARCHER1",
                "name": "Sniper",
                "faction": FactionEnum.ENEMY,
                "position": (9, 7),
                "current_hp": 35,
                "max_hp": 35,
                "ai_persona": "OPPORTUNIST",
                "stats": {"STR": 13, "DEF": 8, "SPD": 12, "SKL": 17}
            },
            {
                "id": "ENEMY_ARCHER2",
                "name": "Sniper",
                "faction": FactionEnum.ENEMY,
                "position": (11, 7),
                "current_hp": 35,
                "max_hp": 35,
                "ai_persona": "OPPORTUNIST",
                "stats": {"STR": 12, "DEF": 9, "SPD": 13, "SKL": 16}
            },
            {
                "id": "ENEMY_MAGE",
                "name": "Sage",
                "faction": FactionEnum.ENEMY,
                "position": (10, 7),
                "current_hp": 32,
                "max_hp": 32,
                "ai_persona": "OPPORTUNIST",
                "stats": {"STR": 16, "DEF": 7, "SPD": 11, "SKL": 14}
            },
            # Support unit
            {
                "id": "ENEMY_HEALER",
                "name": "Bishop",
                "faction": FactionEnum.ENEMY,
                "position": (10, 8),
                "current_hp": 30,
                "max_hp": 30,
                "ai_persona": "SUPPORT",
                "stats": {"STR": 8, "DEF": 6, "SPD": 10, "SKL": 12},
                "healing_capability": True
            },
            # Flanking units
            {
                "id": "ENEMY_CAVALRY1",
                "name": "Paladin",
                "faction": FactionEnum.ENEMY,
                "position": (14, 9),
                "current_hp": 40,
                "max_hp": 40,
                "ai_persona": "AGGRESSOR",
                "stats": {"STR": 15, "DEF": 12, "SPD": 13, "SKL": 14}
            },
            {
                "id": "ENEMY_CAVALRY2",
                "name": "Paladin",
                "faction": FactionEnum.ENEMY,
                "position": (6, 9),
                "current_hp": 40,
                "max_hp": 40,
                "ai_persona": "AGGRESSOR",
                "stats": {"STR": 14, "DEF": 13, "SPD": 14, "SKL": 13}
            },
            # Ambush units
            {
                "id": "ENEMY_FIGHTER1",
                "name": "Warrior",
                "faction": FactionEnum.ENEMY,
                "position": (17, 12),
                "current_hp": 38,
                "max_hp": 38,
                "ai_persona": "AGGRESSOR",
                "stats": {"STR": 17, "DEF": 9, "SPD": 12, "SKL": 13}
            },
            {
                "id": "ENEMY_FIGHTER2",
                "name": "Warrior",
                "faction": FactionEnum.ENEMY,
                "position": (3, 12),
                "current_hp": 38,
                "max_hp": 38,
                "ai_persona": "AGGRESSOR",
                "stats": {"STR": 16, "DEF": 10, "SPD": 11, "SKL": 14}
            }
        ]
        
        # Add a neutral NPC faction (villagers)
        npc_units = [
            {
                "id": "NPC_VILLAGER1",
                "name": "Villager",
                "faction": FactionEnum.NPC,
                "position": (2, 5),  # At a village
                "current_hp": 20,
                "max_hp": 20,
                "ai_persona": "CAUTIOUS",
                "stats": {"STR": 5, "DEF": 3, "SPD": 7, "SKL": 6}
            },
            {
                "id": "NPC_VILLAGER2",
                "name": "Villager",
                "faction": FactionEnum.NPC,
                "position": (17, 4),  # At a village
                "current_hp": 20,
                "max_hp": 20,
                "ai_persona": "CAUTIOUS",
                "stats": {"STR": 4, "DEF": 4, "SPD": 6, "SKL": 5}
            }
        ]
        
        # Create all units
        all_units = player_units + enemy_units + npc_units
        faction_units = {
            "PLAYER": [],
            "ENEMY": [],
            "NPC": []
        }
        
        for unit_data in all_units:
            unit = UnitState()
            unit.id = unit_data["id"]
            unit.name = unit_data["name"]
            unit.faction = unit_data["faction"]
            unit.position = unit_data["position"]
            unit.current_hp = unit_data["current_hp"]
            unit.max_hp = unit_data["max_hp"]
            unit.ai_persona = unit_data["ai_persona"]
            
            # Set stats if provided
            if "stats" in unit_data:
                unit.base_stats = unit_data["stats"]
            
            # Special properties
            unit.has_healing_capability = lambda: unit_data.get("healing_capability", False)
            
            # Add unit to collections
            unit_states[unit.id] = unit
            unit_positions[unit.id] = unit.position
            
            # Add to faction list
            faction_key = unit.faction.name
            if faction_key not in faction_units:
                faction_units[faction_key] = []
            faction_units[faction_key].append(unit.id)
        
        # Set unit states
        if game_state_manager.current_game_state:
            game_state = game_state_manager.current_game_state
            game_state.unit_states = unit_states
            game_state.map_state.unit_positions = unit_positions
            game_state.map_state.allies = faction_units
    
    def _initialize_systems(self, game_state_manager, data_provider):
        """Initialize all game systems needed for the test."""
        # Create systems
        map_system = MapSystem()
        unit_system = UnitSystem()
        movement_system = MovementSystem()
        combat_system = CombatSystem()
        inventory_system = InventorySystem()
        core_turn_manager = CoreTurnManager()
        turn_manager = TurnManager()
        action_handler = ActionHandler()
        event_handler = EventHandler()
        
        # Initialize map system first
        map_system.initialize(game_state_manager, data_provider)
        
        # Initialize unit system
        unit_system.initialize(game_state_manager, data_provider)
        
        # Initialize inventory system
        inventory_system.initialize(game_state_manager, data_provider)
        
        # Initialize movement system
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
        
        # Initialize AI components
        utility_scorer = UtilityScorer(game_state_manager)
        strategic_evaluator = StrategicEvaluator(utility_scorer)
        tactical_executor = TacticalExecutor()
        
        # Configure tactical executor
        tactical_executor.movement_system = movement_system
        tactical_executor.combat_system = combat_system
        
        # Create AI manager
        ai_manager = AIManager(strategic_evaluator, tactical_executor, game_state_manager)
        
        # Return all initialized systems
        return {
            "map_system": map_system,
            "unit_system": unit_system,
            "movement_system": movement_system,
            "combat_system": combat_system,
            "inventory_system": inventory_system,
            "core_turn_manager": core_turn_manager,
            "turn_manager": turn_manager,
            "action_handler": action_handler,
            "event_handler": event_handler,
            "ai_manager": ai_manager
        }
    
    def test_complex_strategic_battle(self, scenario_setup):
        """
        Test a 5-turn complex strategic battle with tactical terrain and mixed unit types.
        
        This test verifies:
        1. AI units adapt to complex terrain features
        2. Defensive units protect strategic locations
        3. Support units properly heal allies
        4. Offensive units target appropriate enemies
        5. Visual logging captures the full scenario
        """
        # Get setup data
        engine = scenario_setup["engine"]
        game_state_manager = scenario_setup["game_state_manager"]
        visual_logger = scenario_setup["visual_logger"]
        
        # Try to directly create and open a log file to verify permissions and path
        try:
            test_log_path = os.path.join("logs", "test_direct_write.txt") 
            with open(test_log_path, 'w') as f:
                f.write("Direct write test successful\n")
            print(f"Successfully wrote test file to {test_log_path}")
        except Exception as e:
            print(f"Error writing direct test file: {e}")
        
        # Log initial state
        print(f"Logging initial state to {visual_logger.log_file_path}")
        visual_logger.log_initial_state()
        print(f"After initial state, log path: {visual_logger.log_file_path}")
        logger.info("Starting 5-turn complex strategic battle scenario")
        
        # Set maximum turns (5 turns max)
        MAX_TURNS = 5
        current_turn = 1
        
        # Initial counts
        initial_player_units = len(game_state_manager.get_units_by_faction(FactionEnum.PLAYER))
        initial_enemy_units = len(game_state_manager.get_units_by_faction(FactionEnum.ENEMY))
        initial_npc_units = len(game_state_manager.get_units_by_faction(FactionEnum.NPC))
        
        logger.info(f"Initial state: {initial_player_units} player units, {initial_enemy_units} enemy units, {initial_npc_units} NPC units")
        
        # Log initial unit positions
        for faction in [FactionEnum.PLAYER, FactionEnum.ENEMY, FactionEnum.NPC]:
            units = game_state_manager.get_units_by_faction(faction)
            logger.info(f"--- {faction.name} UNITS ---")
            for unit in units:
                logger.info(f"{unit.name} ({unit.id}) at position {unit.position}, HP: {unit.current_hp}/{unit.max_hp}")
        
        # Run the simulation for specified number of turns
        while current_turn <= MAX_TURNS:
            # Log turn start
            logger.info(f"=== TURN {current_turn} ===")
            visual_logger.log_turn_start(current_turn)
            
            # Check win condition: Player unit on throne (seize point)
            throne_position = (10, 10)
            player_units = game_state_manager.get_units_by_faction(FactionEnum.PLAYER)
            if any(unit.position == throne_position for unit in player_units):
                logger.info(f"VICTORY: Player unit has seized the throne!")
                visual_logger.log_action("SYSTEM", "WIN_CONDITION", "Player seized the throne")
                break
            
            # Process player phase
            logger.info("Player Phase (AI-controlled)")
            visual_logger.log_phase_start(FactionEnum.PLAYER)
            self._process_ai_turn(engine, game_state_manager, visual_logger, FactionEnum.PLAYER)
            
            # Process enemy phase
            logger.info("Enemy Phase (AI-controlled)")
            visual_logger.log_phase_start(FactionEnum.ENEMY)
            self._process_ai_turn(engine, game_state_manager, visual_logger, FactionEnum.ENEMY)
            
            # Process NPC phase if applicable
            if game_state_manager.has_npc_units():
                logger.info("NPC Phase (AI-controlled)")
                visual_logger.log_phase_start(FactionEnum.NPC)
                self._process_ai_turn(engine, game_state_manager, visual_logger, FactionEnum.NPC)
            
            # Random events for added complexity (20% chance each turn)
            if random.random() < 0.2:
                self._trigger_random_event(game_state_manager, visual_logger)
            
            # Log end of turn state
            visual_logger.log_end_of_turn_state(current_turn)
            
            # Increment turn counter
            current_turn += 1
            
            # Check for total defeat
            player_units = game_state_manager.get_units_by_faction(FactionEnum.PLAYER)
            enemy_units = game_state_manager.get_units_by_faction(FactionEnum.ENEMY)
            
            if not player_units:
                logger.info("DEFEAT: All player units have been defeated")
                visual_logger.log_action("SYSTEM", "DEFEAT", "All player units defeated")
                break
                
            if not enemy_units:
                logger.info("VICTORY: All enemy units have been defeated")
                visual_logger.log_action("SYSTEM", "VICTORY", "All enemy units defeated")
                break
        
        # Final turn state if max turns reached
        if current_turn > MAX_TURNS:
            logger.info(f"Maximum turns ({MAX_TURNS}) reached - simulation ended")
            
        # Final unit counts
        final_player_units = len(game_state_manager.get_units_by_faction(FactionEnum.PLAYER))
        final_enemy_units = len(game_state_manager.get_units_by_faction(FactionEnum.ENEMY))
        final_npc_units = len(game_state_manager.get_units_by_faction(FactionEnum.NPC))
        
        # Log final stats
        logger.info(f"Simulation ended after {current_turn-1} turns")
        logger.info(f"Final state: {final_player_units} player units, {final_enemy_units} enemy units, {final_npc_units} NPC units")
        
        # Unit disposition count
        self._log_unit_disposition_counts(game_state_manager)
        
        # Finalize the log
        visual_logger.finalize_log()
        
        # Verify reasonable outcome
        assert current_turn > 1, "Simulation should run for at least one turn"
        
        # Log the path to the visual log file
        if visual_logger.log_file_path:
            logger.info(f"Visual log available at: {visual_logger.log_file_path}")
            print(f"\nVisual log generated at: {visual_logger.log_file_path}")
        
    def _process_ai_turn(self, engine, game_state_manager, visual_logger, faction):
        """Process a single AI turn for the specified faction with detailed action logging."""
        # Get all units for the faction
        units = game_state_manager.get_units_by_faction(faction)
        logger.info(f"Processing turn for {faction.name} faction with {len(units)} units")
        
        # Process each unit
        for unit in units:
            # Skip units that have already acted
            if hasattr(unit, 'has_acted') and unit.has_acted:
                continue
                
            # Get AI decision and execute it
            logger.info(f"AI processing for unit {unit.name} ({unit.id}) at {unit.position}")
            try:
                # Record the unit's position before action
                original_position = unit.position
                
                # Use the engine's AI processing
                engine.process_ai_unit_turn(unit)
                
                # Log the action based on position change
                if original_position != unit.position:
                    # Unit moved
                    visual_logger.log_action(unit.id, "MOVE", f"from {original_position} to {unit.position}")
                else:
                    # Unit may have attacked or waited
                    visual_logger.log_action(unit.id, "ACTION", "Attacked or waited")
                
            except Exception as e:
                logger.error(f"Error processing AI for unit {unit.id}: {e}")
                visual_logger.log_action(unit.id, "ERROR", f"Failed to process AI: {e}")
                
            # Mark the unit as having acted
            unit.has_acted = True
            
        # Reset acted flag after all units have moved (this would normally be done by the turn manager)
        for unit in units:
            unit.has_acted = False
    
    def _trigger_random_event(self, game_state_manager, visual_logger):
        """Trigger a random event to add unpredictability to the scenario."""
        events = [
            self._reinforcement_event,
            self._weather_effect_event,
            self._healing_event,
            self._village_event
        ]
        
        # Choose a random event
        event = random.choice(events)
        event(game_state_manager, visual_logger)
    
    def _reinforcement_event(self, game_state_manager, visual_logger):
        """Add a reinforcement unit to a random faction."""
        # Determine which faction gets reinforcements (70% enemy, 30% player)
        faction = FactionEnum.ENEMY if random.random() < 0.7 else FactionEnum.PLAYER
        
        # Choose a random spawn position based on faction
        if faction == FactionEnum.PLAYER:
            positions = [(0, 3), (0, 4), (0, 5)]
        else: 
            positions = [(19, 10), (19, 11), (19, 12)]
            
        position = random.choice(positions)
        
        # Create a new unit
        unit_type = random.choice(["Fighter", "Archer", "Cavalry"])
        unit_id = f"{faction.name}_REINFORCE_{unit_type}"
        
        unit = UnitState()
        unit.id = unit_id
        unit.name = f"Reinforcement {unit_type}"
        unit.faction = faction
        unit.position = position
        unit.current_hp = 35
        unit.max_hp = 35
        unit.ai_persona = "AGGRESSOR"
        
        # Add the unit to the game state
        game_state_manager.current_game_state.unit_states[unit_id] = unit
        game_state_manager.current_game_state.map_state.unit_positions[unit_id] = position
        
        # Log the event
        visual_logger.log_action("SYSTEM", "REINFORCEMENT", f"{faction.name} {unit_type} arrived at {position}")
        logger.info(f"Random event: {faction.name} reinforcement ({unit_type}) arrived at {position}")
    
    def _weather_effect_event(self, game_state_manager, visual_logger):
        """Apply a random weather effect that temporarily changes unit stats."""
        # Choose a random weather effect
        weather_types = ["Fog", "Rain", "Strong Winds"]
        weather = random.choice(weather_types)
        
        # Log the event
        visual_logger.log_action("SYSTEM", "WEATHER", f"{weather} has set in")
        logger.info(f"Random event: Weather changed to {weather}")
        
    def _healing_event(self, game_state_manager, visual_logger):
        """Randomly heal some units on the map."""
        # Choose a random number of units to heal
        num_to_heal = random.randint(2, 5)
        
        # Get all active units
        all_units = []
        for faction in [FactionEnum.PLAYER, FactionEnum.ENEMY, FactionEnum.NPC]:
            all_units.extend(game_state_manager.get_units_by_faction(faction))
        
        # Filter to damaged units
        damaged_units = [u for u in all_units if u.current_hp < u.max_hp]
        
        if not damaged_units:
            return
            
        # Select random damaged units to heal
        units_to_heal = random.sample(damaged_units, min(num_to_heal, len(damaged_units)))
        
        # Heal each unit by 5-15 HP
        for unit in units_to_heal:
            heal_amount = random.randint(5, 15)
            old_hp = unit.current_hp
            unit.current_hp = min(unit.max_hp, unit.current_hp + heal_amount)
            
            # Log the healing
            visual_logger.log_action("SYSTEM", "HEALING", f"{unit.name} ({unit.id}) healed {unit.current_hp - old_hp} HP")
            
        logger.info(f"Random event: {len(units_to_heal)} units received healing")
    
    def _village_event(self, game_state_manager, visual_logger):
        """Trigger an event at a random village."""
        # Find all village positions
        villages = [(2, 5), (17, 4), (5, 13), (12, 12)]
        
        if not villages:
            return
            
        # Choose a random village
        village_pos = random.choice(villages)
        
        # Determine which event occurs
        event_type = random.choice(["Item", "Recruit", "Information"])
        
        # Log the event
        visual_logger.log_action("SYSTEM", "VILLAGE", f"{event_type} event at village {village_pos}")
        logger.info(f"Random event: {event_type} event triggered at village {village_pos}")
    
    def _log_unit_disposition_counts(self, game_state_manager):
        """Log the final disposition counts of all units by faction."""
        # Initialize counters
        counts = {
            FactionEnum.PLAYER: {"ACTIVE": 0, "DEAD": 0, "OTHER": 0},
            FactionEnum.ENEMY: {"ACTIVE": 0, "DEAD": 0, "OTHER": 0},
            FactionEnum.NPC: {"ACTIVE": 0, "DEAD": 0, "OTHER": 0}
        }
        
        # Count by disposition
        for unit in game_state_manager.current_game_state.unit_states.values():
            if unit.faction not in counts:
                continue
                
            if unit.disposition == DispositionEnum.ACTIVE:
                counts[unit.faction]["ACTIVE"] += 1
            elif unit.disposition == DispositionEnum.DEAD:
                counts[unit.faction]["DEAD"] += 1
            else:
                counts[unit.faction]["OTHER"] += 1
        
        # Log the counts
        for faction, dispositions in counts.items():
            logger.info(f"{faction.name} units: {dispositions['ACTIVE']} active, {dispositions['DEAD']} defeated, {dispositions['OTHER']} other") 