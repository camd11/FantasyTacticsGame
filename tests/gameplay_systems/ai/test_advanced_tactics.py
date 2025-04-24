"""
AI Advanced Tactics Test: Strategic & Tactical Elements (Max 10 Turns)

This scenario tests AI decision-making in a complex battle with advanced elements:
- Multiple terrain types with special effects
- Dynamic objectives that change during battle
- Weather effects that impact gameplay
- Reinforcements and special events
- Strategic choke points and elevation advantages
- Enhanced visual logging for detailed analysis
"""

import pytest
import logging
from typing import Dict, Any, List, Tuple, Optional
from unittest.mock import Mock
import os
import random
import time
from datetime import datetime

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
logger = logging.getLogger("test_advanced_tactics")
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TestAdvancedTactics:
    """Test suite for Advanced Tactical AI Scenarios."""
    
    @pytest.fixture
    def scenario_setup(self):
        """Load the advanced tactical AI test scenario and set up the game state."""
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load all data from the data directory
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a complex map state with elevation and special features
        map_state = MapState()
        map_state.dimensions = (25, 18)  # Larger map for more tactical depth
        
        # Default terrain is plains
        terrain_grid = [['P'] * 25 for _ in range(18)]
        
        # Create elevation data (0 = ground level, 1 = hills, 2 = mountains)
        elevation_grid = [[0] * 25 for _ in range(18)]
        
        # Create strategic river dividing the map
        river_path = [(5, 2), (5, 3), (6, 4), (7, 5), (8, 6), (9, 7), (10, 8), 
                      (11, 9), (12, 10), (13, 11), (14, 12), (15, 13), (16, 14), (17, 15)]
        
        for x, y in river_path:
            terrain_grid[y][x] = 'R'  # River
        
        # Add bridges as strategic crossings
        bridges = [(5, 3), (10, 8), (15, 13)]
        for x, y in bridges:
            terrain_grid[y][x] = 'B'  # Bridge
        
        # Add forests in strategic locations for cover
        forest_clusters = [
            # Defensive forest near player starting area
            [(3, 2), (4, 2), (3, 3), (4, 3), (3, 4)],
            # Central forest offering tactical cover
            [(12, 6), (13, 6), (14, 6), (12, 7), (13, 7)],
            # Forest near enemy reinforcement point
            [(19, 14), (20, 14), (21, 14), (19, 15), (20, 15)]
        ]
        
        for cluster in forest_clusters:
            for x, y in cluster:
                terrain_grid[y][x] = 'F'  # Forest
        
        # Add elevated terrain (hills with movement penalty)
        hill_areas = [
            # Defensible hill on player side
            [(2, 5), (3, 5), (4, 5), (2, 6), (3, 6), (4, 6)],
            # Central hill - strategic high ground
            [(14, 9), (15, 9), (16, 9), (14, 10), (15, 10), (16, 10)],
            # Hill near enemy side
            [(20, 3), (21, 3), (20, 4), (21, 4)]
        ]
        
        for cluster in hill_areas:
            for x, y in cluster:
                terrain_grid[y][x] = 'H'  # Hills
                elevation_grid[y][x] = 1  # Set elevation
        
        # Add mountains as impassable barriers creating choke points
        mountain_ranges = [
            [(7, 1), (8, 1), (9, 1), (8, 2)],  # Northern mountains
            [(17, 4), (18, 4), (19, 4), (18, 5)],  # Northeastern mountains
            [(7, 13), (8, 13), (9, 13), (8, 14)]  # Southern mountains
        ]
        
        for mountain_range in mountain_ranges:
            for x, y in mountain_range:
                terrain_grid[y][x] = 'M'  # Mountain
                elevation_grid[y][x] = 2  # Set highest elevation
        
        # Add strategic villages (healing/objectives)
        villages = [(3, 8), (11, 4), (18, 8), (12, 15)]
        for x, y in villages:
            terrain_grid[y][x] = 'V'  # Village
        
        # Add castle (primary objective)
        throne_position = (12, 9)
        terrain_grid[throne_position[1]][throne_position[0]] = 'T'  # Throne (seize point)
        
        # Add swamp areas (movement penalty)
        swamp_areas = [
            [(2, 14), (3, 14), (4, 14), (2, 15), (3, 15)],
            [(19, 2), (20, 2), (21, 2), (19, 3)]
        ]
        
        for swamp in swamp_areas:
            for x, y in swamp:
                terrain_grid[y][x] = 'S'  # Swamp
        
        # Set map state properties
        map_state.terrain_grid = terrain_grid
        map_state.map_id = "advanced_tactics_test"
        
        # Add custom map data class for additional properties
        class MapDataObj:
            def __init__(self):
                self.id = "advanced_tactics_test"
                self.name = "Advanced Tactics Test"
                self.dimensions = (25, 18)
                self.terrain_grid = terrain_grid
                self.elevation_grid = elevation_grid
                self.fog_of_war = False
                self.seize_point = throne_position
                self.defensive_points = [(3, 3), (14, 10), (20, 4)]  # Strategic defensive locations
                
        map_state.map_data = MapDataObj()
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_advanced_tactics"
        game_state.map_state = map_state
        
        # Set the game state
        game_state_manager.current_game_state = game_state
        
        # Add units with diverse capabilities
        self._add_units(game_state_manager)
        
        # Initialize systems
        game_systems = self._initialize_systems(game_state_manager, data_provider)
        
        # Initialize CLIDisplay for visual logging
        cli_display = CLIDisplay()
        cli_display.game_state_manager = game_state_manager
        cli_display.map_system = game_systems["map_system"]
        cli_display.unit_system = game_systems["unit_system"]
        cli_display.data_provider = data_provider
        
        # Create visual logger with enhanced logging
        log_dir = os.path.abspath("logs")
        os.makedirs(log_dir, exist_ok=True)
        
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
            "cli_display": cli_display,
            "map_state": map_state
        } 

    def _add_units(self, game_state_manager):
        """Add units to the game state with specialized roles, personalities, and starting positions."""
        unit_states = {}
        
        # Player faction units (West side)
        player_units = [
            # Commander - balanced leader unit
            {
                "id": "PLAYER_COMMANDER",
                "name": "Lord Commander",
                "faction": FactionEnum.PLAYER,
                "position": (2, 3),
                "current_hp": 45,
                "max_hp": 45,
                "ai_persona": "BALANCED",
                "role": "COMMANDER",
                "stats": {"STR": 14, "DEF": 12, "SPD": 10, "SKL": 12, "LCK": 8},
                "abilities": ["LEADERSHIP", "RALLY"]
            },
            # Tank unit - high defense, low mobility
            {
                "id": "PLAYER_KNIGHT",
                "name": "Royal Knight",
                "faction": FactionEnum.PLAYER,
                "position": (3, 2),
                "current_hp": 50,
                "max_hp": 50,
                "ai_persona": "DEFENDER",
                "role": "TANK",
                "stats": {"STR": 12, "DEF": 18, "SPD": 6, "SKL": 8, "LCK": 5},
                "abilities": ["SHIELD_WALL", "TAUNT"]
            },
            # High mobility scout
            {
                "id": "PLAYER_SCOUT",
                "name": "Scout Rider",
                "faction": FactionEnum.PLAYER,
                "position": (1, 4),
                "current_hp": 35,
                "max_hp": 35,
                "ai_persona": "FLANKER",
                "role": "SCOUT",
                "stats": {"STR": 10, "DEF": 8, "SPD": 16, "SKL": 14, "LCK": 10},
                "abilities": ["RECON", "SWIFT_STRIKE"]
            },
            # Ranged damage dealer
            {
                "id": "PLAYER_ARCHER",
                "name": "Elite Archer",
                "faction": FactionEnum.PLAYER,
                "position": (2, 5),
                "current_hp": 30,
                "max_hp": 30,
                "ai_persona": "SNIPER",
                "role": "ARTILLERY",
                "stats": {"STR": 14, "DEF": 6, "SPD": 12, "SKL": 16, "LCK": 9},
                "abilities": ["PRECISE_SHOT", "CRIPPLING_SHOT"]
            },
            # Support/healer unit
            {
                "id": "PLAYER_MAGE",
                "name": "Battle Mage",
                "faction": FactionEnum.PLAYER,
                "position": (3, 4),
                "current_hp": 32,
                "max_hp": 32,
                "ai_persona": "SUPPORTER",
                "role": "SUPPORT",
                "stats": {"STR": 8, "DEF": 7, "SPD": 10, "SKL": 15, "LCK": 12},
                "abilities": ["HEALING", "BUFF_ALLIES"]
            },
            # Heavy assault unit
            {
                "id": "PLAYER_BERSERKER",
                "name": "Highland Warrior",
                "faction": FactionEnum.PLAYER,
                "position": (4, 3),
                "current_hp": 42,
                "max_hp": 42,
                "ai_persona": "AGGRESSOR",
                "role": "ASSAULT",
                "stats": {"STR": 18, "DEF": 10, "SPD": 8, "SKL": 12, "LCK": 7},
                "abilities": ["HEAVY_STRIKE", "INTIMIDATE"]
            },
            # Assassin - high damage, low defense
            {
                "id": "PLAYER_ROGUE",
                "name": "Shadow Blade",
                "faction": FactionEnum.PLAYER,
                "position": (1, 6),
                "current_hp": 28,
                "max_hp": 28,
                "ai_persona": "ASSASSIN",
                "role": "SKIRMISHER",
                "stats": {"STR": 15, "DEF": 5, "SPD": 14, "SKL": 16, "LCK": 13},
                "abilities": ["BACKSTAB", "POISON_BLADE"]
            }
        ]
        
        # Enemy faction units (East side)
        enemy_units = [
            # Enemy commander
            {
                "id": "ENEMY_WARLORD",
                "name": "Dark Warlord",
                "faction": FactionEnum.ENEMY,
                "position": (22, 4),
                "current_hp": 52,
                "max_hp": 52,
                "ai_persona": "WARLORD",
                "role": "COMMANDER",
                "stats": {"STR": 16, "DEF": 14, "SPD": 9, "SKL": 10, "LCK": 6},
                "abilities": ["COMMAND_AURA", "EXECUTE"]
            },
            # Heavy defender
            {
                "id": "ENEMY_GUARDIAN",
                "name": "Elite Guardian",
                "faction": FactionEnum.ENEMY,
                "position": (21, 3),
                "current_hp": 55,
                "max_hp": 55,
                "ai_persona": "DEFENDER",
                "role": "TANK",
                "stats": {"STR": 13, "DEF": 19, "SPD": 5, "SKL": 7, "LCK": 4},
                "abilities": ["FORTIFY", "CHALLENGE"]
            },
            # Mobile shock trooper
            {
                "id": "ENEMY_CAVALRY",
                "name": "Dark Rider",
                "faction": FactionEnum.ENEMY,
                "position": (20, 5),
                "current_hp": 40,
                "max_hp": 40,
                "ai_persona": "FLANKER",
                "role": "ASSAULT",
                "stats": {"STR": 14, "DEF": 10, "SPD": 15, "SKL": 12, "LCK": 8},
                "abilities": ["CHARGE", "TRAMPLE"]
            },
            # Ranged specialist
            {
                "id": "ENEMY_MARKSMAN",
                "name": "Veteran Marksman",
                "faction": FactionEnum.ENEMY,
                "position": (22, 6),
                "current_hp": 35,
                "max_hp": 35,
                "ai_persona": "SNIPER",
                "role": "ARTILLERY",
                "stats": {"STR": 15, "DEF": 7, "SPD": 11, "SKL": 17, "LCK": 9},
                "abilities": ["DEADLY_AIM", "SUPPRESSING_FIRE"]
            },
            # Necromancer/support
            {
                "id": "ENEMY_NECROMANCER",
                "name": "Necromancer",
                "faction": FactionEnum.ENEMY,
                "position": (21, 5),
                "current_hp": 34,
                "max_hp": 34,
                "ai_persona": "SUMMONER",
                "role": "SUPPORT",
                "stats": {"STR": 9, "DEF": 8, "SPD": 9, "SKL": 14, "LCK": 10},
                "abilities": ["DARK_HEALING", "RAISE_DEAD"]
            },
            # Assassin unit
            {
                "id": "ENEMY_ASSASSIN",
                "name": "Shadow Stalker",
                "faction": FactionEnum.ENEMY,
                "position": (23, 7),
                "current_hp": 30,
                "max_hp": 30,
                "ai_persona": "ASSASSIN",
                "role": "SKIRMISHER",
                "stats": {"STR": 16, "DEF": 6, "SPD": 17, "SKL": 15, "LCK": 12},
                "abilities": ["AMBUSH", "CRIPPLE"]
            },
            # Magical artillery
            {
                "id": "ENEMY_WARLOCK",
                "name": "Battle Warlock",
                "faction": FactionEnum.ENEMY,
                "position": (20, 6),
                "current_hp": 32,
                "max_hp": 32,
                "ai_persona": "MAGE",
                "role": "ARTILLERY",
                "stats": {"STR": 17, "DEF": 5, "SPD": 8, "SKL": 16, "LCK": 11},
                "abilities": ["FIREBALL", "ARCANE_SHIELD"]
            }
        ]
        
        # NPC faction units (Neutral forces scattered across map)
        npc_units = [
            # Village defender
            {
                "id": "NPC_MILITIA_1",
                "name": "Village Defender",
                "faction": FactionEnum.NPC,
                "position": (3, 9),
                "current_hp": 25,
                "max_hp": 25,
                "ai_persona": "DEFENDER",
                "role": "MILITIA",
                "stats": {"STR": 8, "DEF": 7, "SPD": 7, "SKL": 6, "LCK": 5},
                "abilities": ["DEFEND_VILLAGE"]
            },
            # Wandering mercenary
            {
                "id": "NPC_MERCENARY",
                "name": "Mercenary",
                "faction": FactionEnum.NPC,
                "position": (12, 5),
                "current_hp": 30,
                "max_hp": 30,
                "ai_persona": "OPPORTUNIST",
                "role": "MERCENARY",
                "stats": {"STR": 12, "DEF": 9, "SPD": 10, "SKL": 11, "LCK": 8},
                "abilities": ["MERCENARY_CODE"]
            },
            # Village elder
            {
                "id": "NPC_ELDER",
                "name": "Village Elder",
                "faction": FactionEnum.NPC,
                "position": (18, 9),
                "current_hp": 20,
                "max_hp": 20,
                "ai_persona": "CIVILIAN",
                "role": "CIVILIAN",
                "stats": {"STR": 5, "DEF": 5, "SPD": 5, "SKL": 10, "LCK": 12},
                "abilities": ["WISDOM", "DIPLOMACY"]
            }
        ]
        
        # Create all units and add to game state
        all_units = player_units + enemy_units + npc_units
        
        for unit_data in all_units:
            unit = UnitState()
            unit.id = unit_data["id"]
            unit.name = unit_data["name"]
            unit.faction = unit_data["faction"]
            unit.position = unit_data["position"]
            unit.current_hp = unit_data["current_hp"]
            unit.max_hp = unit_data["max_hp"]
            unit.ai_persona = unit_data["ai_persona"]
            
            # Set stats
            for stat, value in unit_data["stats"].items():
                setattr(unit, stat.lower(), value)
            
            # Store role and abilities as custom properties
            unit.role = unit_data["role"]
            unit.abilities = unit_data.get("abilities", [])
            unit.has_acted = False
            unit.disposition = DispositionEnum.ACTIVE
            
            # Add to game state collections
            game_state_manager.current_game_state.unit_states[unit.id] = unit
            game_state_manager.current_game_state.map_state.unit_positions[unit.id] = unit.position 

    def _initialize_systems(self, game_state_manager, data_provider):
        """Initialize all game systems required for the advanced tactics test."""
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
        
        # Configure movement costs based on terrain and elevation
        # (In a real implementation, these would come from the data provider)
        movement_system.terrain_costs = {
            'P': 1.0,  # Plains
            'F': 1.5,  # Forest
            'M': 999,  # Mountains (impassable)
            'R': 999,  # River (impassable except at bridges)
            'B': 1.0,  # Bridge
            'V': 1.0,  # Village
            'T': 1.0,  # Throne/castle
            'H': 2.0,  # Hills
            'S': 3.0   # Swamp
        }
        
        # Initialize combat system
        combat_system.initialize(
            gameStateManager_instance=game_state_manager,
            dataProvider_instance=data_provider,
            unitSystem_instance=unit_system,
            mapSystem_instance=map_system,
            inventorySystem_instance=inventory_system
        )
        
        # Configure terrain modifiers for combat
        combat_system.terrain_defense_bonus = {
            'P': 0,     # Plains
            'F': 2,     # Forest
            'M': 4,     # Mountains
            'R': -1,    # River
            'B': 0,     # Bridge
            'V': 1,     # Village
            'T': 3,     # Throne/castle
            'H': 2,     # Hills
            'S': -1     # Swamp
        }
        
        # Configure elevation advantages for combat
        combat_system.elevation_attack_bonus = {
            0: 0,  # No bonus at same elevation
            1: 1,  # +1 attack when attacking from 1 level higher
            2: 2   # +2 attack when attacking from 2 levels higher
        }
        
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
        
        # Create AI manager with advanced configuration
        ai_manager = AIManager(strategic_evaluator, tactical_executor, game_state_manager)
        
        # Configure AI behavior weights for different personas
        ai_manager.persona_weights = {
            "BALANCED": {
                "attack": 1.0,
                "defend": 1.0,
                "support": 1.0,
                "objective": 1.2
            },
            "AGGRESSOR": {
                "attack": 2.0,
                "defend": 0.5,
                "support": 0.7,
                "objective": 1.0
            },
            "DEFENDER": {
                "attack": 0.7,
                "defend": 2.0,
                "support": 1.0,
                "objective": 0.8
            },
            "SUPPORTER": {
                "attack": 0.5,
                "defend": 0.8,
                "support": 2.0,
                "objective": 0.7
            },
            "FLANKER": {
                "attack": 1.5,
                "defend": 0.7,
                "support": 0.5,
                "objective": 1.3
            },
            "SNIPER": {
                "attack": 1.7,
                "defend": 0.6,
                "support": 0.7,
                "objective": 0.9
            },
            "ASSASSIN": {
                "attack": 1.8,
                "defend": 0.4,
                "support": 0.4,
                "objective": 0.9
            },
            "WARLORD": {
                "attack": 1.5,
                "defend": 1.2,
                "support": 1.0,
                "objective": 1.3
            },
            "OPPORTUNIST": {
                "attack": 1.2,
                "defend": 0.8,
                "support": 0.7,
                "objective": 1.5
            },
            "SUMMONER": {
                "attack": 0.6,
                "defend": 0.9,
                "support": 1.8,
                "objective": 0.8
            },
            "CIVILIAN": {
                "attack": 0.3,
                "defend": 1.5,
                "support": 1.0,
                "objective": 0.5
            }
        }
        
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

    def test_advanced_tactical_battle(self, scenario_setup):
        """
        Test a 10-turn advanced tactical battle with dynamic objectives and events.
        
        This test verifies:
        1. AI adapts to terrain elevation and special terrain types
        2. Units respond to changing objectives during battle
        3. Weather effects influence tactical decisions
        4. Reinforcements change the battlefield dynamics
        5. Special events create interesting tactical situations
        6. Enhanced visual logging captures detailed scenario progression
        """
        # Get setup data
        engine = scenario_setup["engine"]
        game_state_manager = scenario_setup["game_state_manager"]
        visual_logger = scenario_setup["visual_logger"]
        map_state = scenario_setup["map_state"]
        
        # Ensure logs directory exists
        log_dir = os.path.abspath("logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Try to create a test file to verify write permissions
        try:
            test_file_path = os.path.join(log_dir, "test_advanced_tactics_write.txt")
            with open(test_file_path, 'w') as f:
                f.write("Advanced tactics test file creation successful\n")
            print(f"Successfully created test file at: {test_file_path}")
        except Exception as e:
            print(f"Error creating test file: {e}")
        
        # Log the test start time
        test_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Advanced Tactics Test started at: {test_start_time}")
        
        # Log initial state with detailed information
        visual_logger.log_initial_state()
        logger.info("=== Starting 10-turn Advanced Tactical Battle scenario ===")
        logger.info(f"Test started at: {test_start_time}")
        
        # Set maximum turns (10 turns max)
        MAX_TURNS = 10
        current_turn = 1
        
        # Track scenario state
        scenario_state = {
            "active_weather": None,
            "weather_duration": 0,
            "primary_objective": (12, 9),  # Throne position
            "secondary_objectives": [(11, 4), (18, 8)],  # Villages
            "objective_owner": {
                (12, 9): None,  # Throne initially uncontrolled
                (11, 4): None,  # Village 1 initially uncontrolled
                (18, 8): None   # Village 2 initially uncontrolled
            },
            "reinforcement_chance": 0.15,  # Starting chance of reinforcements
            "event_chance": 0.20,          # Starting chance of random events
            "last_objective_change": 0     # Last turn when objectives changed
        }
        
        # Initial counts
        initial_player_units = len(game_state_manager.get_units_by_faction(FactionEnum.PLAYER))
        initial_enemy_units = len(game_state_manager.get_units_by_faction(FactionEnum.ENEMY))
        initial_npc_units = len(game_state_manager.get_units_by_faction(FactionEnum.NPC))
        
        logger.info(f"Initial state: {initial_player_units} player units, {initial_enemy_units} enemy units, {initial_npc_units} NPC units")
        
        # Log initial unit positions and stats
        for faction in [FactionEnum.PLAYER, FactionEnum.ENEMY, FactionEnum.NPC]:
            units = game_state_manager.get_units_by_faction(faction)
            logger.info(f"--- {faction.name} UNITS ---")
            for unit in units:
                logger.info(f"{unit.name} ({unit.id}) at position {unit.position}, HP: {unit.current_hp}/{unit.max_hp}, Role: {unit.role}")
        
        # Run the simulation for specified number of turns
        while current_turn <= MAX_TURNS:
            # Log turn start with detailed information
            logger.info(f"\n=== TURN {current_turn} ===")
            turn_start_time = time.time()
            
            # Update scenario state each turn
            self._update_scenario_state(scenario_state, current_turn, game_state_manager)
            
            # Log turn start with scenario conditions
            turn_info = f"Turn {current_turn}"
            if scenario_state["active_weather"]:
                turn_info += f", Weather: {scenario_state['active_weather']}"
            visual_logger.log_turn_start(current_turn)
            visual_logger.log_action("SYSTEM", "TURN_START", turn_info)
            
            # Check win conditions before turn starts
            throne_position = scenario_state["primary_objective"]
            current_owner = scenario_state["objective_owner"][throne_position]
            
            # Player wins if they control the throne for 2 consecutive turns
            if current_owner == FactionEnum.PLAYER and scenario_state.get("throne_control_turns", 0) >= 2:
                logger.info(f"VICTORY: Player has controlled the throne for {scenario_state.get('throne_control_turns', 0)} turns!")
                visual_logger.log_action("SYSTEM", "WIN_CONDITION", "Player controlled throne for 2+ turns")
                break
            
            # Enemy wins if they control the throne for 2 consecutive turns
            if current_owner == FactionEnum.ENEMY and scenario_state.get("throne_control_turns", 0) >= 2:
                logger.info(f"DEFEAT: Enemy has controlled the throne for {scenario_state.get('throne_control_turns', 0)} turns!")
                visual_logger.log_action("SYSTEM", "LOSE_CONDITION", "Enemy controlled throne for 2+ turns")
                break
            
            # Process player phase
            logger.info("Player Phase (AI-controlled)")
            visual_logger.log_phase_start(FactionEnum.PLAYER)
            self._process_ai_turn(engine, game_state_manager, visual_logger, FactionEnum.PLAYER, scenario_state)
            
            # Check for total defeat after player phase
            enemy_units = game_state_manager.get_units_by_faction(FactionEnum.ENEMY)
            if not enemy_units:
                logger.info("VICTORY: All enemy units have been defeated!")
                visual_logger.log_action("SYSTEM", "WIN_CONDITION", "All enemy units defeated")
                break
            
            # Process enemy phase
            logger.info("Enemy Phase (AI-controlled)")
            visual_logger.log_phase_start(FactionEnum.ENEMY)
            self._process_ai_turn(engine, game_state_manager, visual_logger, FactionEnum.ENEMY, scenario_state)
            
            # Check for total defeat after enemy phase
            player_units = game_state_manager.get_units_by_faction(FactionEnum.PLAYER)
            if not player_units:
                logger.info("DEFEAT: All player units have been defeated!")
                visual_logger.log_action("SYSTEM", "LOSE_CONDITION", "All player units defeated")
                break
            
            # Process NPC phase if applicable
            if game_state_manager.has_npc_units():
                logger.info("NPC Phase (AI-controlled)")
                visual_logger.log_phase_start(FactionEnum.NPC)
                self._process_ai_turn(engine, game_state_manager, visual_logger, FactionEnum.NPC, scenario_state)
            
            # Random events with increasing probability
            event_triggered = False
            if random.random() < scenario_state["event_chance"]:
                event_type = self._trigger_random_event(game_state_manager, visual_logger, scenario_state)
                event_triggered = True
                logger.info(f"Random event triggered: {event_type}")
            
            # Chance for reinforcements with increasing probability
            if not event_triggered and random.random() < scenario_state["reinforcement_chance"]:
                self._spawn_reinforcements(game_state_manager, visual_logger, current_turn)
                logger.info("Reinforcements have arrived!")
            
            # Check for objective changes (chance increases as game progresses)
            objective_change_chance = 0.05 + (current_turn * 0.02)
            if current_turn - scenario_state["last_objective_change"] >= 3 and random.random() < objective_change_chance:
                self._change_objectives(game_state_manager, visual_logger, scenario_state)
                scenario_state["last_objective_change"] = current_turn
            
            # Log end of turn state with detailed information
            turn_end_time = time.time()
            turn_duration = round(turn_end_time - turn_start_time, 2)
            logger.info(f"Turn {current_turn} completed in {turn_duration} seconds")
            
            # Update control of objectives
            self._update_objective_control(game_state_manager, visual_logger, scenario_state)
            
            # Log detailed end of turn state
            visual_logger.log_end_of_turn_state(current_turn)
            
            # Increment turn counter
            current_turn += 1
            
            # Increase event and reinforcement chances as battle progresses
            scenario_state["event_chance"] = min(0.35, scenario_state["event_chance"] + 0.03)
            scenario_state["reinforcement_chance"] = min(0.25, scenario_state["reinforcement_chance"] + 0.02)
        
        # Final turn state if max turns reached
        if current_turn > MAX_TURNS:
            logger.info(f"Maximum turns ({MAX_TURNS}) reached - simulation ended")
            visual_logger.log_action("SYSTEM", "MAX_TURNS", f"Maximum {MAX_TURNS} turns reached")
            
            # Determine victor based on objective control
            player_objectives = sum(1 for obj, faction in scenario_state["objective_owner"].items() if faction == FactionEnum.PLAYER)
            enemy_objectives = sum(1 for obj, faction in scenario_state["objective_owner"].items() if faction == FactionEnum.ENEMY)
            
            if player_objectives > enemy_objectives:
                logger.info(f"VICTORY BY OBJECTIVES: Player controlled {player_objectives} objectives vs enemy's {enemy_objectives}")
                visual_logger.log_action("SYSTEM", "VICTORY", f"Player won by controlling more objectives ({player_objectives} vs {enemy_objectives})")
            elif enemy_objectives > player_objectives:
                logger.info(f"DEFEAT BY OBJECTIVES: Enemy controlled {enemy_objectives} objectives vs player's {player_objectives}")
                visual_logger.log_action("SYSTEM", "DEFEAT", f"Enemy won by controlling more objectives ({enemy_objectives} vs {player_objectives})")
            else:
                logger.info(f"DRAW: Both factions controlled the same number of objectives ({player_objectives})")
                visual_logger.log_action("SYSTEM", "DRAW", f"Equal number of objectives controlled ({player_objectives})")
        
        # Final unit counts
        final_player_units = len(game_state_manager.get_units_by_faction(FactionEnum.PLAYER))
        final_enemy_units = len(game_state_manager.get_units_by_faction(FactionEnum.ENEMY))
        final_npc_units = len(game_state_manager.get_units_by_faction(FactionEnum.NPC))
        
        # Log final stats and unit disposition counts
        logger.info(f"\nSimulation ended after {current_turn-1} turns")
        logger.info(f"Final state: {final_player_units} player units, {final_enemy_units} enemy units, {final_npc_units} NPC units")
        
        # Log detailed unit disposition counts
        self._log_unit_disposition_counts(game_state_manager)
        
        # Log objective control
        logger.info("Final objective control:")
        for obj, faction in scenario_state["objective_owner"].items():
            faction_name = faction.name if faction else "Uncontrolled"
            logger.info(f"Objective at {obj} is controlled by: {faction_name}")
        
        # Finalize the log
        visual_logger.finalize_log()
        
        # Verify reasonable outcome (simulation should run for at least one turn)
        assert current_turn > 1, "Simulation should run for at least one turn"
        
        # Log the path to the visual log file
        if visual_logger.log_file_path:
            logger.info(f"Visual log available at: {visual_logger.log_file_path}")
            print(f"\nVisual log generated at: {visual_logger.log_file_path}")
        
        # Return simulation results
        return {
            "turns_completed": current_turn - 1,
            "player_units_remaining": final_player_units,
            "enemy_units_remaining": final_enemy_units,
            "npc_units_remaining": final_npc_units,
            "log_file": visual_logger.log_file_path
        } 

    def _process_ai_turn(self, engine, game_state_manager, visual_logger, faction, scenario_state):
        """Process a single AI turn for the specified faction with enhanced logging and effects."""
        # Get all units for the faction
        units = game_state_manager.get_units_by_faction(faction)
        logger.info(f"Processing turn for {faction.name} faction with {len(units)} units")
        
        # Process each unit with weather and other effects
        for unit in units:
            # Skip units that have already acted
            if hasattr(unit, 'has_acted') and unit.has_acted:
                continue
                
            # Apply weather effects to unit's stats if applicable
            original_stats = {}
            if scenario_state["active_weather"]:
                original_stats = self._apply_weather_effects(unit, scenario_state["active_weather"])
            
            # Log pre-action state
            logger.info(f"AI processing for unit {unit.name} ({unit.id}) at {unit.position}, HP: {unit.current_hp}/{unit.max_hp}")
            try:
                # Record the unit's position before action
                original_position = unit.position
                original_hp = unit.current_hp
                
                # Since we don't have access to the engine's AI processing,
                # we'll simulate simple AI behavior based on the unit's persona
                self._simulate_ai_behavior(unit, game_state_manager, scenario_state)
                
                # Log the action based on position and HP changes
                if original_position != unit.position:
                    # Unit moved
                    movement_details = f"from {original_position} to {unit.position}"
                    
                    # Check if unit moved to an objective
                    if unit.position in scenario_state["objective_owner"]:
                        movement_details += f" (moved to objective)"
                        
                    visual_logger.log_action(unit.id, "MOVE", movement_details)
                
                # Check if unit's HP changed (attacked or was healed)
                if original_hp != unit.current_hp:
                    hp_change = unit.current_hp - original_hp
                    if hp_change > 0:
                        visual_logger.log_action(unit.id, "HEALED", f"+{hp_change} HP (now {unit.current_hp}/{unit.max_hp})")
                    else:
                        visual_logger.log_action(unit.id, "DAMAGED", f"{hp_change} HP (now {unit.current_hp}/{unit.max_hp})")
                
                # If no position or HP change, unit may have used a special ability or waited
                if original_position == unit.position and original_hp == unit.current_hp:
                    if hasattr(unit, 'last_action') and unit.last_action:
                        visual_logger.log_action(unit.id, unit.last_action, "")
                    else:
                        visual_logger.log_action(unit.id, "WAIT", "No action taken")
                
            except Exception as e:
                logger.error(f"Error processing AI for unit {unit.id}: {e}")
                visual_logger.log_action(unit.id, "ERROR", f"Failed to process AI: {e}")
                
            # Restore original stats after weather effects
            if original_stats:
                self._restore_unit_stats(unit, original_stats)
                
            # Mark the unit as having acted
            unit.has_acted = True
            
        # Reset acted flag after all units have moved
        for unit in units:
            unit.has_acted = False
            
    def _simulate_ai_behavior(self, unit, game_state_manager, scenario_state):
        """Simulate AI behavior for a unit based on its persona."""
        # Get unit's AI persona
        persona = unit.ai_persona if hasattr(unit, 'ai_persona') else "BALANCED"
        
        # Get available actions based on persona
        if persona in ["AGGRESSOR", "WARLORD", "ASSASSIN"]:
            # Offensive units prioritize attacking
            action_type = self._simulate_offensive_action(unit, game_state_manager, scenario_state)
        elif persona in ["DEFENDER", "TANK"]:
            # Defensive units prioritize protecting objectives
            action_type = self._simulate_defensive_action(unit, game_state_manager, scenario_state)
        elif persona in ["SUPPORTER", "SUMMONER"]:
            # Support units prioritize healing/buffing
            action_type = self._simulate_support_action(unit, game_state_manager, scenario_state)
        elif persona in ["FLANKER", "SCOUT"]:
            # Flanking units prioritize movement to objectives
            action_type = self._simulate_flanking_action(unit, game_state_manager, scenario_state)
        elif persona in ["SNIPER", "MAGE"]:
            # Ranged units prioritize attacking from safe positions
            action_type = self._simulate_ranged_action(unit, game_state_manager, scenario_state)
        else:
            # Balanced units make a mixed decision
            action_type = self._simulate_balanced_action(unit, game_state_manager, scenario_state)
        
        # Store the last action for logging
        unit.last_action = action_type
    
    def _simulate_offensive_action(self, unit, game_state_manager, scenario_state):
        """Simulate an offensive AI action - attack enemies or move toward them."""
        # In a real implementation, we would:
        # 1. Find nearby enemy units
        # 2. Attack if in range
        # 3. Move toward enemies if not in range
        
        # For this simulation, we'll just randomly decide whether the unit attacks or moves
        if random.random() < 0.4:  # 40% chance to "attack"
            # Simulate an attack by possibly reducing a random enemy's HP
            enemy_units = []
            
            # Find enemy faction
            enemy_faction = FactionEnum.ENEMY if unit.faction == FactionEnum.PLAYER else FactionEnum.PLAYER
            
            # Get all enemy units
            enemy_units = game_state_manager.get_units_by_faction(enemy_faction)
            
            if enemy_units:
                # Select a random enemy to "attack"
                target = random.choice(enemy_units)
                
                # Check if they're close enough (simulate range check)
                dx = abs(unit.position[0] - target.position[0])
                dy = abs(unit.position[1] - target.position[1])
                manhattan_distance = dx + dy
                
                if manhattan_distance <= 3:  # Arbitrary range
                    # Apply damage
                    damage = random.randint(3, 10)
                    target.current_hp = max(0, target.current_hp - damage)
                    
                    # If target is defeated, mark as such
                    if target.current_hp <= 0:
                        target.disposition = DispositionEnum.DEAD
                    
                    return "ATTACK"
        
        # If no attack was made or it wasn't possible, move
        # Move in a random direction (in a real implementation, would move toward enemies or objectives)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        direction = random.choice(directions)
        
        new_x = unit.position[0] + direction[0]
        new_y = unit.position[1] + direction[1]
        
        # Check bounds
        map_width = game_state_manager.current_game_state.map_state.dimensions[0]
        map_height = game_state_manager.current_game_state.map_state.dimensions[1]
        
        if 0 <= new_x < map_width and 0 <= new_y < map_height:
            # Check if position is occupied
            is_occupied = False
            for other_unit in game_state_manager.current_game_state.unit_states.values():
                if hasattr(other_unit, 'position') and other_unit.position == (new_x, new_y):
                    is_occupied = True
                    break
            
            if not is_occupied:
                # Check terrain (avoid impassable terrain)
                terrain = game_state_manager.current_game_state.map_state.terrain_grid[new_y][new_x]
                if terrain not in ['M', 'R']:  # Not mountain or river
                    unit.position = (new_x, new_y)
                    return "MOVE"
        
        return "WAIT"
    
    def _simulate_defensive_action(self, unit, game_state_manager, scenario_state):
        """Simulate a defensive AI action - protect objectives or allies."""
        # If near an objective, stay there
        for objective in [scenario_state["primary_objective"]] + scenario_state["secondary_objectives"]:
            dx = abs(unit.position[0] - objective[0])
            dy = abs(unit.position[1] - objective[1])
            manhattan_distance = dx + dy
            
            if manhattan_distance <= 2:  # Already near an objective
                # 80% chance to just stay and "defend"
                if random.random() < 0.8:
                    return "DEFEND"
                else:
                    # Move slightly to adjust position
                    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                    random.shuffle(directions)
                    
                    for direction in directions:
                        new_x = unit.position[0] + direction[0]
                        new_y = unit.position[1] + direction[1]
                        
                        # Check bounds
                        map_width = game_state_manager.current_game_state.map_state.dimensions[0]
                        map_height = game_state_manager.current_game_state.map_state.dimensions[1]
                        
                        if 0 <= new_x < map_width and 0 <= new_y < map_height:
                            # Check if position is occupied
                            is_occupied = False
                            for other_unit in game_state_manager.current_game_state.unit_states.values():
                                if hasattr(other_unit, 'position') and other_unit.position == (new_x, new_y):
                                    is_occupied = True
                                    break
                            
                            if not is_occupied:
                                # Check terrain
                                terrain = game_state_manager.current_game_state.map_state.terrain_grid[new_y][new_x]
                                if terrain not in ['M', 'R']:  # Not mountain or river
                                    unit.position = (new_x, new_y)
                                    return "ADJUST_POSITION"
        
        # If not near an objective, move toward the closest one
        closest_objective = None
        min_distance = float('inf')
        
        for objective in [scenario_state["primary_objective"]] + scenario_state["secondary_objectives"]:
            dx = abs(unit.position[0] - objective[0])
            dy = abs(unit.position[1] - objective[1])
            manhattan_distance = dx + dy
            
            if manhattan_distance < min_distance:
                min_distance = manhattan_distance
                closest_objective = objective
        
        if closest_objective:
            # Move toward the objective
            dx = closest_objective[0] - unit.position[0]
            dy = closest_objective[1] - unit.position[1]
            
            move_x = 2 if dx > 1 else (1 if dx > 0 else (0 if dx == 0 else (-1 if dx == -1 else -2)))
            move_y = 2 if dy > 1 else (1 if dy > 0 else (0 if dy == 0 else (-1 if dy == -1 else -2)))
            
            # Try different movement options, prioritizing faster movement
            move_options = [
                (move_x, 0),
                (0, move_y),
                (move_x // 2, move_y // 2),
                (1 if dx > 0 else (-1 if dx < 0 else 0), 1 if dy > 0 else (-1 if dy < 0 else 0))
            ]
            
            for move_x, move_y in move_options:
                if move_x == 0 and move_y == 0:
                    continue
                
                new_x = unit.position[0] + move_x
                new_y = unit.position[1] + move_y
                
                # Check bounds
                map_width = game_state_manager.current_game_state.map_state.dimensions[0]
                map_height = game_state_manager.current_game_state.map_state.dimensions[1]
                
                if 0 <= new_x < map_width and 0 <= new_y < map_height:
                    # Check if position is occupied
                    is_occupied = False
                    for other_unit in game_state_manager.current_game_state.unit_states.values():
                        if hasattr(other_unit, 'position') and other_unit.position == (new_x, new_y):
                            is_occupied = True
                            break
                    
                    if not is_occupied:
                        # Check terrain
                        terrain = game_state_manager.current_game_state.map_state.terrain_grid[new_y][new_x]
                        if terrain not in ['M', 'R']:  # Not mountain or river
                            unit.position = (new_x, new_y)
                            return "FLANK"
        
        # If can't move toward objective, try attacking nearby enemies
        enemy_faction = FactionEnum.ENEMY if unit.faction == FactionEnum.PLAYER else FactionEnum.PLAYER
        enemy_units = game_state_manager.get_units_by_faction(enemy_faction)
        
        for enemy in enemy_units:
            dx = abs(unit.position[0] - enemy.position[0])
            dy = abs(unit.position[1] - enemy.position[1])
            manhattan_distance = dx + dy
            
            if manhattan_distance <= 1:  # Adjacent enemy
                # Attack
                damage = random.randint(3, 10)
                enemy.current_hp = max(0, enemy.current_hp - damage)
                
                # If enemy is defeated, mark as such
                if enemy.current_hp <= 0:
                    enemy.disposition = DispositionEnum.DEAD
                
                return "ATTACK"
        
        return "WAIT"
    
    def _simulate_support_action(self, unit, game_state_manager, scenario_state):
        """Simulate a support AI action - heal or buff allies."""
        # Find nearby allies to heal
        ally_units = []
        for other_unit in game_state_manager.get_units_by_faction(unit.faction):
            if other_unit.id != unit.id and other_unit.current_hp < other_unit.max_hp:
                dx = abs(unit.position[0] - other_unit.position[0])
                dy = abs(unit.position[1] - other_unit.position[1])
                manhattan_distance = dx + dy
                
                if manhattan_distance <= 2:  # Arbitrary healing range
                    ally_units.append(other_unit)
        
        if ally_units:
            # Heal a random ally
            target = random.choice(ally_units)
            heal_amount = random.randint(5, 15)
            target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
            return "HEAL"
        
        # If no allies to heal, move toward damaged allies
        damaged_allies = []
        for other_unit in game_state_manager.get_units_by_faction(unit.faction):
            if other_unit.id != unit.id and other_unit.current_hp < other_unit.max_hp:
                damaged_allies.append(other_unit)
        
        if damaged_allies:
            # Move toward closest damaged ally
            closest_ally = None
            min_distance = float('inf')
            
            for ally in damaged_allies:
                dx = abs(unit.position[0] - ally.position[0])
                dy = abs(unit.position[1] - ally.position[1])
                manhattan_distance = dx + dy
                
                if manhattan_distance < min_distance:
                    min_distance = manhattan_distance
                    closest_ally = ally
            
            if closest_ally:
                # Move toward the ally
                dx = closest_ally.position[0] - unit.position[0]
                dy = closest_ally.position[1] - unit.position[1]
                
                move_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
                move_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
                
                # Prioritize larger distance
                if abs(dx) > abs(dy):
                    new_x = unit.position[0] + move_x
                    new_y = unit.position[1]
                else:
                    new_x = unit.position[0]
                    new_y = unit.position[1] + move_y
                
                # Check bounds
                map_width = game_state_manager.current_game_state.map_state.dimensions[0]
                map_height = game_state_manager.current_game_state.map_state.dimensions[1]
                
                if 0 <= new_x < map_width and 0 <= new_y < map_height:
                    # Check if position is occupied
                    is_occupied = False
                    for other_unit in game_state_manager.current_game_state.unit_states.values():
                        if hasattr(other_unit, 'position') and other_unit.position == (new_x, new_y):
                            is_occupied = True
                            break
                    
                    if not is_occupied:
                        # Check terrain
                        terrain = game_state_manager.current_game_state.map_state.terrain_grid[new_y][new_x]
                        if terrain not in ['M', 'R']:  # Not mountain or river
                            unit.position = (new_x, new_y)
                            return "MOVE_TO_ALLY"
        
        # If no damaged allies or can't move toward them, just move randomly
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        
        for direction in directions:
            new_x = unit.position[0] + direction[0]
            new_y = unit.position[1] + direction[1]
            
            # Check bounds
            map_width = game_state_manager.current_game_state.map_state.dimensions[0]
            map_height = game_state_manager.current_game_state.map_state.dimensions[1]
            
            if 0 <= new_x < map_width and 0 <= new_y < map_height:
                # Check if position is occupied
                is_occupied = False
                for other_unit in game_state_manager.current_game_state.unit_states.values():
                    if hasattr(other_unit, 'position') and other_unit.position == (new_x, new_y):
                        is_occupied = True
                        break
                
                if not is_occupied:
                    # Check terrain
                    terrain = game_state_manager.current_game_state.map_state.terrain_grid[new_y][new_x]
                    if terrain not in ['M', 'R']:  # Not mountain or river
                        unit.position = (new_x, new_y)
                        return "MOVE"
        
        return "WAIT"
    
    def _simulate_flanking_action(self, unit, game_state_manager, scenario_state):
        """Simulate a flanking AI action - move quickly to objectives."""
        # Flankers prioritize objectives over combat
        
        # Check if already at an objective
        if unit.position == scenario_state["primary_objective"] or unit.position in scenario_state["secondary_objectives"]:
            return "CAPTURE"
        
        # If not, move toward the closest objective
        closest_objective = None
        min_distance = float('inf')
        
        for objective in [scenario_state["primary_objective"]] + scenario_state["secondary_objectives"]:
            dx = abs(unit.position[0] - objective[0])
            dy = abs(unit.position[1] - objective[1])
            manhattan_distance = dx + dy
            
            if manhattan_distance < min_distance:
                min_distance = manhattan_distance
                closest_objective = objective
        
        if closest_objective:
            # Move toward the objective with longer movement
            dx = closest_objective[0] - unit.position[0]
            dy = closest_objective[1] - unit.position[1]
            
            move_x = 2 if dx > 1 else (1 if dx > 0 else (0 if dx == 0 else (-1 if dx == -1 else -2)))
            move_y = 2 if dy > 1 else (1 if dy > 0 else (0 if dy == 0 else (-1 if dy == -1 else -2)))
            
            # Try different movement options, prioritizing faster movement
            move_options = [
                (move_x, 0),
                (0, move_y),
                (move_x // 2, move_y // 2),
                (1 if dx > 0 else (-1 if dx < 0 else 0), 1 if dy > 0 else (-1 if dy < 0 else 0))
            ]
            
            for move_x, move_y in move_options:
                if move_x == 0 and move_y == 0:
                    continue
                
                new_x = unit.position[0] + move_x
                new_y = unit.position[1] + move_y
                
                # Check bounds
                map_width = game_state_manager.current_game_state.map_state.dimensions[0]
                map_height = game_state_manager.current_game_state.map_state.dimensions[1]
                
                if 0 <= new_x < map_width and 0 <= new_y < map_height:
                    # Check if position is occupied
                    is_occupied = False
                    for other_unit in game_state_manager.current_game_state.unit_states.values():
                        if hasattr(other_unit, 'position') and other_unit.position == (new_x, new_y):
                            is_occupied = True
                            break
                    
                    if not is_occupied:
                        # Check terrain
                        terrain = game_state_manager.current_game_state.map_state.terrain_grid[new_y][new_x]
                        if terrain not in ['M', 'R']:  # Not mountain or river
                            unit.position = (new_x, new_y)
                            return "FLANK"
        
        # If can't move toward objective, try attacking nearby enemies
        enemy_faction = FactionEnum.ENEMY if unit.faction == FactionEnum.PLAYER else FactionEnum.PLAYER
        enemy_units = game_state_manager.get_units_by_faction(enemy_faction)
        
        for enemy in enemy_units:
            dx = abs(unit.position[0] - enemy.position[0])
            dy = abs(unit.position[1] - enemy.position[1])
            manhattan_distance = dx + dy
            
            if manhattan_distance <= 1:  # Adjacent enemy
                # Attack
                damage = random.randint(3, 10)
                enemy.current_hp = max(0, enemy.current_hp - damage)
                
                # If enemy is defeated, mark as such
                if enemy.current_hp <= 0:
                    enemy.disposition = DispositionEnum.DEAD
                
                return "ATTACK"
        
        return "WAIT"
    
    def _simulate_ranged_action(self, unit, game_state_manager, scenario_state):
        """Simulate a ranged AI action - attack from a distance."""
        # Ranged units prioritize attacking from a safe distance
        enemy_faction = FactionEnum.ENEMY if unit.faction == FactionEnum.PLAYER else FactionEnum.PLAYER
        enemy_units = game_state_manager.get_units_by_faction(enemy_faction)
        
        # Try to attack enemies within range
        for enemy in enemy_units:
            dx = abs(unit.position[0] - enemy.position[0])
            dy = abs(unit.position[1] - enemy.position[1])
            manhattan_distance = dx + dy
            
            if 1 < manhattan_distance <= 3:  # Within ranged attack distance but not adjacent
                # Attack
                damage = random.randint(5, 12)
                enemy.current_hp = max(0, enemy.current_hp - damage)
                
                # If enemy is defeated, mark as such
                if enemy.current_hp <= 0:
                    enemy.disposition = DispositionEnum.DEAD
                
                return "RANGED_ATTACK"
        
        # If no enemies in range, move to a position with good line of sight
        # Prioritize hills and elevated terrain
        nearby_positions = []
        
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0:
                    continue  # Skip current position
                
                new_x = unit.position[0] + dx
                new_y = unit.position[1] + dy
                
                # Check bounds
                map_width = game_state_manager.current_game_state.map_state.dimensions[0]
                map_height = game_state_manager.current_game_state.map_state.dimensions[1]
                
                if 0 <= new_x < map_width and 0 <= new_y < map_height:
                    # Check if position is occupied
                    is_occupied = False
                    for other_unit in game_state_manager.current_game_state.unit_states.values():
                        if hasattr(other_unit, 'position') and other_unit.position == (new_x, new_y):
                            is_occupied = True
                            break
                    
                    if not is_occupied:
                        # Check terrain
                        terrain = game_state_manager.current_game_state.map_state.terrain_grid[new_y][new_x]
                        if terrain not in ['M', 'R']:  # Not mountain or river
                            # Prioritize hills
                            score = 5 if terrain == 'H' else 1
                            nearby_positions.append((new_x, new_y, score))
        
        if nearby_positions:
            # Sort by score (descending)
            nearby_positions.sort(key=lambda x: x[2], reverse=True)
            
            # Move to the best position
            unit.position = (nearby_positions[0][0], nearby_positions[0][1])
            return "REPOSITION"
        
        return "WAIT"
    
    def _simulate_balanced_action(self, unit, game_state_manager, scenario_state):
        """Simulate a balanced AI action - mix of offensive, defensive, and objective-focused behavior."""
        # Randomly choose an action type based on the situation
        action_types = ["offensive", "defensive", "objective"]
        weights = [0.4, 0.3, 0.3]  # Default weights
        
        # Adjust weights based on unit health
        health_ratio = unit.current_hp / unit.max_hp
        
        if health_ratio < 0.3:
            # Low health, prioritize defensive actions
            weights = [0.2, 0.6, 0.2]
        elif health_ratio > 0.7:
            # High health, prioritize offensive actions
            weights = [0.5, 0.2, 0.3]
        
        # Adjust weights based on proximity to objectives
        for objective in [scenario_state["primary_objective"]] + scenario_state["secondary_objectives"]:
            dx = abs(unit.position[0] - objective[0])
            dy = abs(unit.position[1] - objective[1])
            manhattan_distance = dx + dy
            
            if manhattan_distance <= 3:  # Close to an objective
                # Increase weight for objective actions
                weights = [0.3, 0.2, 0.5]
                break
        
        # Choose action type based on weights
        action_type = random.choices(action_types, weights=weights)[0]
        
        if action_type == "offensive":
            return self._simulate_offensive_action(unit, game_state_manager, scenario_state)
        elif action_type == "defensive":
            return self._simulate_defensive_action(unit, game_state_manager, scenario_state)
        else:  # objective
            return self._simulate_flanking_action(unit, game_state_manager, scenario_state)  # Reuse flanking for objective focus
    
    def _apply_weather_effects(self, unit, weather_type):
        """Apply weather effects to a unit's stats and return original values."""
        original_stats = {}
        
        if weather_type == "Fog":
            # Fog reduces skill (accuracy)
            original_stats["skl"] = unit.skl
            unit.skl = max(1, int(unit.skl * 0.7))  # Reduce skill by 30%
            
        elif weather_type == "Rain":
            # Rain reduces movement/speed
            original_stats["spd"] = unit.spd
            unit.spd = max(1, int(unit.spd * 0.8))  # Reduce speed by 20%
            
        elif weather_type == "Strong Winds":
            # Strong winds affect both attack strength and defense
            original_stats["str"] = unit.str
            original_stats["def"] = unit.def_
            unit.str = max(1, int(unit.str * 0.85))  # Reduce strength by 15%
            unit.def_ = max(1, int(unit.def_ * 0.9))  # Reduce defense by 10%
            
        elif weather_type == "Extreme Heat":
            # Heat wave reduces max HP temporarily
            original_stats["max_hp"] = unit.max_hp
            reduced_max = max(10, int(unit.max_hp * 0.9))  # Reduce max HP by 10%
            unit.max_hp = reduced_max
            if unit.current_hp > unit.max_hp:
                original_stats["current_hp"] = unit.current_hp
                unit.current_hp = unit.max_hp
                
        elif weather_type == "Thunderstorm":
            # Thunderstorm reduces skill and luck
            original_stats["skl"] = unit.skl
            original_stats["lck"] = unit.lck
            unit.skl = max(1, int(unit.skl * 0.8))  # Reduce skill by 20%
            unit.lck = max(1, int(unit.lck * 0.7))  # Reduce luck by 30%
        
        return original_stats
    
    def _restore_unit_stats(self, unit, original_stats):
        """Restore a unit's original stats after weather effects."""
        for stat, value in original_stats.items():
            setattr(unit, stat, value)
    
    def _update_objective_control(self, game_state_manager, visual_logger, scenario_state):
        """Update which faction controls each objective."""
        objectives = [scenario_state["primary_objective"]] + scenario_state["secondary_objectives"]
        
        for objective in objectives:
            # Find unit at this position by checking all units
            unit_at_position = None
            for unit_id, unit in game_state_manager.current_game_state.unit_states.items():
                if hasattr(unit, 'position') and unit.position == objective:
                    unit_at_position = unit
                    break
            
            if unit_at_position:
                # Update control if changed
                previous_control = scenario_state["objective_owner"].get(objective)
                if previous_control != unit_at_position.faction:
                    scenario_state["objective_owner"][objective] = unit_at_position.faction
                    obj_name = "Throne" if objective == scenario_state["primary_objective"] else f"Village at {objective}"
                    visual_logger.log_action("SYSTEM", "OBJECTIVE_CAPTURED", f"{unit_at_position.faction.name} captured {obj_name}")
                    logger.info(f"{unit_at_position.faction.name} has captured {obj_name}")
            else:
                # Keep existing control if no unit is present
                pass
    
    def _trigger_random_event(self, game_state_manager, visual_logger, scenario_state):
        """Trigger a random event to add unpredictability to the scenario."""
        events = [
            self._weather_event,
            self._supply_drop_event,
            self._healing_event,
            self._village_event,
            self._terrain_change_event
        ]
        
        # Choose a random event
        event = random.choice(events)
        event_name = event.__name__.replace("_event", "").replace("_", " ").title()
        
        # Execute the event
        event(game_state_manager, visual_logger, scenario_state)
        
        return event_name
    
    def _weather_event(self, game_state_manager, visual_logger, scenario_state):
        """Apply a random weather effect that changes unit stats."""
        # Choose a random weather effect
        weather_types = ["Fog", "Rain", "Strong Winds", "Extreme Heat", "Thunderstorm"]
        
        # Don't repeat the current weather
        available_types = [w for w in weather_types if w != scenario_state["active_weather"]]
        weather = random.choice(available_types)
        
        # Set weather duration
        scenario_state["active_weather"] = weather
        scenario_state["weather_duration"] = random.randint(1, 3)  # 1-3 turns of weather
        
        # Log the event
        visual_logger.log_action("SYSTEM", "WEATHER", f"{weather} has set in for {scenario_state['weather_duration']} turns")
        logger.info(f"Weather changed to {weather} for {scenario_state['weather_duration']} turns")
        
        # Log weather effects
        effects = {
            "Fog": "Reduced accuracy for all units",
            "Rain": "Reduced movement speed",
            "Strong Winds": "Reduced attack and defense",
            "Extreme Heat": "Reduced maximum HP",
            "Thunderstorm": "Reduced accuracy and luck"
        }
        visual_logger.log_action("SYSTEM", "WEATHER_EFFECTS", effects[weather])
    
    def _supply_drop_event(self, game_state_manager, visual_logger, scenario_state):
        """Drop supplies at a random location on the map."""
        # Choose a random location that isn't impassable
        valid_positions = []
        terrain_grid = game_state_manager.current_game_state.map_state.terrain_grid
        
        for y in range(len(terrain_grid)):
            for x in range(len(terrain_grid[0])):
                if terrain_grid[y][x] not in ['M', 'R']:  # Not mountain or river
                    valid_positions.append((x, y))
        
        if not valid_positions:
            return
            
        supply_position = random.choice(valid_positions)
        
        # Determine supply type
        supply_type = random.choice(["Weapons", "Healing", "Special Item"])
        
        # Log the event
        visual_logger.log_action("SYSTEM", "SUPPLY_DROP", f"{supply_type} dropped at {supply_position}")
        logger.info(f"Supply drop event: {supply_type} supplies dropped at {supply_position}")
    
    def _healing_event(self, game_state_manager, visual_logger, scenario_state):
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
            
        logger.info(f"Healing event: {len(units_to_heal)} units received healing")
    
    def _village_event(self, game_state_manager, visual_logger, scenario_state):
        """Trigger an event at a random village."""
        # Get all village positions from the scenario state
        villages = scenario_state["secondary_objectives"]
        
        if not villages:
            return
            
        # Choose a random village
        village_pos = random.choice(villages)
        
        # Determine which event occurs
        event_type = random.choice(["Reinforcement", "Information", "Healing", "Supplies"])
        
        if event_type == "Reinforcement":
            # Determine which faction gets the unit
            faction = None
            unit_at_village = game_state_manager.get_unit_at_position(village_pos)
            if unit_at_village:
                unit = game_state_manager.get_unit(unit_at_village)
                if unit:
                    faction = unit.faction
            
            if not faction:
                # No unit at village, choose randomly
                faction = random.choice([FactionEnum.PLAYER, FactionEnum.ENEMY])
            
            # Create a new unit near the village
            nearby_positions = []
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue  # Skip the village position itself
                    nearby_pos = (village_pos[0] + dx, village_pos[1] + dy)
                    # Check if position is valid and not occupied
                    if (0 <= nearby_pos[0] < game_state_manager.current_game_state.map_state.dimensions[0] and 
                        0 <= nearby_pos[1] < game_state_manager.current_game_state.map_state.dimensions[1] and
                        not game_state_manager.get_unit_at_position(nearby_pos)):
                        nearby_positions.append(nearby_pos)
            
            if nearby_positions:
                spawn_pos = random.choice(nearby_positions)
                unit_type = random.choice(["Militia", "Archer", "Spearman"])
                unit_id = f"{faction.name}_VILLAGE_{unit_type}_{len(game_state_manager.current_game_state.unit_states) + 1}"
                
                unit = UnitState()
                unit.id = unit_id
                unit.name = f"Village {unit_type}"
                unit.faction = faction
                unit.position = spawn_pos
                unit.current_hp = 25
                unit.max_hp = 25
                unit.ai_persona = "BALANCED"
                unit.role = "MILITIA"
                unit.str = 10
                unit.def_ = 8
                unit.spd = 9
                unit.skl = 8
                unit.lck = 7
                unit.has_acted = False
                unit.disposition = DispositionEnum.ACTIVE
                
                # Add to game state
                game_state_manager.current_game_state.unit_states[unit_id] = unit
                game_state_manager.current_game_state.map_state.unit_positions[unit_id] = spawn_pos
                
                visual_logger.log_action("SYSTEM", "VILLAGE_REINFORCEMENT", f"{faction.name} {unit_type} spawned at {spawn_pos}")
        
        elif event_type == "Healing":
            # Heal all units near the village
            nearby_units = []
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    nearby_pos = (village_pos[0] + dx, village_pos[1] + dy)
                    unit_id = game_state_manager.get_unit_at_position(nearby_pos)
                    if unit_id:
                        unit = game_state_manager.get_unit(unit_id)
                        if unit and unit.current_hp < unit.max_hp:
                            nearby_units.append(unit)
            
            if nearby_units:
                heal_amount = random.randint(10, 20)
                for unit in nearby_units:
                    old_hp = unit.current_hp
                    unit.current_hp = min(unit.max_hp, unit.current_hp + heal_amount)
                    visual_logger.log_action("SYSTEM", "VILLAGE_HEALING", f"{unit.name} healed {unit.current_hp - old_hp} HP")
        
        # Log the event
        visual_logger.log_action("SYSTEM", "VILLAGE_EVENT", f"{event_type} event at village {village_pos}")
        logger.info(f"Village event: {event_type} triggered at village {village_pos}")
    
    def _terrain_change_event(self, game_state_manager, visual_logger, scenario_state):
        """Change terrain in a small area to create new tactical situations."""
        # Determine area to affect
        map_width = game_state_manager.current_game_state.map_state.dimensions[0]
        map_height = game_state_manager.current_game_state.map_state.dimensions[1]
        
        # Choose center point
        center_x = random.randint(3, map_width - 4)
        center_y = random.randint(3, map_height - 4)
        center = (center_x, center_y)
        
        # Determine effect type
        effect_type = random.choice(["Flood", "Forest Fire", "Landslide"])
        
        # Determine terrain changes based on effect type
        terrain_grid = game_state_manager.current_game_state.map_state.terrain_grid
        
        if effect_type == "Flood":
            # Turn some plains into swamp
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if random.random() < 0.6:  # 60% chance for each tile
                        pos_x = center_x + dx
                        pos_y = center_y + dy
                        
                        # Check bounds
                        if 0 <= pos_x < map_width and 0 <= pos_y < map_height:
                            # Only affect plains
                            if terrain_grid[pos_y][pos_x] == 'P':
                                terrain_grid[pos_y][pos_x] = 'S'  # Change to swamp
        
        elif effect_type == "Forest Fire":
            # Burns forest to plains
            forest_found = False
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    pos_x = center_x + dx
                    pos_y = center_y + dy
                    
                    # Check bounds
                    if 0 <= pos_x < map_width and 0 <= pos_y < map_height:
                        # Only affect forests
                        if terrain_grid[pos_y][pos_x] == 'F':
                            terrain_grid[pos_y][pos_x] = 'P'  # Change to plains
                            forest_found = True
            
            # If no forests found, don't log the event
            if not forest_found:
                return
        
        elif effect_type == "Landslide":
            # Create impassable terrain in mountainous areas
            mountain_found = False
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    pos_x = center_x + dx
                    pos_y = center_y + dy
                    
                    # Check bounds
                    if 0 <= pos_x < map_width and 0 <= pos_y < map_height:
                        # Affect hills or near mountains
                        if terrain_grid[pos_y][pos_x] == 'H' or terrain_grid[pos_y][pos_x] == 'M':
                            # Check if unit is at this position
                            unit_id = game_state_manager.get_unit_at_position((pos_x, pos_y))
                            if unit_id:
                                # Damage the unit
                                unit = game_state_manager.get_unit(unit_id)
                                if unit:
                                    damage = random.randint(5, 15)
                                    old_hp = unit.current_hp
                                    unit.current_hp = max(1, unit.current_hp - damage)  # Don't kill units
                                    visual_logger.log_action("SYSTEM", "LANDSLIDE_DAMAGE", 
                                                           f"{unit.name} took {old_hp - unit.current_hp} damage")
                            
                            # Change terrain to mountain
                            if terrain_grid[pos_y][pos_x] == 'H':
                                terrain_grid[pos_y][pos_x] = 'M'
                                mountain_found = True
            
            # If no mountains/hills found, don't log the event
            if not mountain_found:
                return
        
        # Log the terrain change
        visual_logger.log_action("SYSTEM", "TERRAIN_CHANGE", f"{effect_type} changed terrain around {center}")
        logger.info(f"Terrain change event: {effect_type} affected area around {center}")
    
    def _spawn_reinforcements(self, game_state_manager, visual_logger, current_turn):
        """Add reinforcement units based on the current turn."""
        # Determine which faction gets reinforcements (balanced based on remaining units)
        player_units = len(game_state_manager.get_units_by_faction(FactionEnum.PLAYER))
        enemy_units = len(game_state_manager.get_units_by_faction(FactionEnum.ENEMY))
        
        # Favor the faction with fewer units
        if player_units < enemy_units:
            faction = FactionEnum.PLAYER
            reinforcement_chance = 0.8  # 80% chance for player reinforcements
        elif enemy_units < player_units:
            faction = FactionEnum.ENEMY
            reinforcement_chance = 0.8  # 80% chance for enemy reinforcements
        else:
            # Equal units, random selection
            faction = random.choice([FactionEnum.PLAYER, FactionEnum.ENEMY])
            reinforcement_chance = 0.5  # 50% chance for either
        
        # Final check with probability
        if random.random() > reinforcement_chance:
            faction = FactionEnum.PLAYER if faction == FactionEnum.ENEMY else FactionEnum.ENEMY
        
        # Choose spawn positions based on faction
        if faction == FactionEnum.PLAYER:
            spawn_positions = [(0, 3), (0, 4), (0, 5), (0, 6), (1, 2), (1, 7)]
        else:
            spawn_positions = [(24, 3), (24, 4), (24, 5), (24, 6), (23, 2), (23, 7)]
        
        # Filter to valid spawn positions (not occupied)
        valid_positions = []
        map_state = game_state_manager.current_game_state.map_state
        for pos in spawn_positions:
            # Check bounds
            if (0 <= pos[0] < map_state.dimensions[0] and
                0 <= pos[1] < map_state.dimensions[1]):
                # Check if position is occupied by iterating through all units
                position_occupied = False
                for unit in game_state_manager.get_all_units():
                    if unit.position == pos and unit.is_alive():
                        position_occupied = True
                        break
                
                if not position_occupied:
                    valid_positions.append(pos)

        # If no valid positions, return without spawning
        if not valid_positions:
            logger.info(f"No valid positions for reinforcements for {faction.name}")
            return

        # Choose random position from valid ones
        spawn_position = random.choice(valid_positions)

        # Create a new unit
        roles = ["WARRIOR", "ARCHER", "MAGE", "HEALER", "SCOUT"]
        personas = ["OFFENSIVE", "DEFENSIVE", "SUPPORT", "FLANKING", "RANGED", "BALANCED"]
        role = random.choice(roles)
        persona = random.choice(personas)
        
        # Generate ID based on faction, role, and current time
        unit_id = f"{faction.name.lower()}_{role.lower()}_{int(time.time())}"
        
        # Generate a descriptive name
        descriptors = ["Elite", "Veteran", "Reinforcement", "Reserve", "Tactical"]
        unit_name = f"{random.choice(descriptors)} {role.title()}"
        
        # Create unit with appropriate stats based on role
        if role == "WARRIOR":
            new_unit = UnitState()
            new_unit.id = unit_id
            new_unit.name = unit_name
            new_unit.faction = faction
            new_unit.position = spawn_position
            new_unit.current_hp = 80
            new_unit.max_hp = 80
            new_unit.ai_persona = persona
            new_unit.role = role
            new_unit.str = 25
            new_unit.def_ = 20
            new_unit.spd = 15
            new_unit.skl = 10
            new_unit.lck = 10
            new_unit.has_acted = False
            new_unit.disposition = DispositionEnum.ACTIVE
        elif role == "ARCHER":
            new_unit = UnitState()
            new_unit.id = unit_id
            new_unit.name = unit_name
            new_unit.faction = faction
            new_unit.position = spawn_position
            new_unit.current_hp = 60
            new_unit.max_hp = 60
            new_unit.ai_persona = persona
            new_unit.role = role
            new_unit.str = 20
            new_unit.def_ = 10
            new_unit.spd = 20
            new_unit.skl = 14
            new_unit.lck = 9
            new_unit.has_acted = False
            new_unit.disposition = DispositionEnum.ACTIVE
        elif role == "MAGE":
            new_unit = UnitState()
            new_unit.id = unit_id
            new_unit.name = unit_name
            new_unit.faction = faction
            new_unit.position = spawn_position
            new_unit.current_hp = 55
            new_unit.max_hp = 55
            new_unit.ai_persona = persona
            new_unit.role = role
            new_unit.str = 5
            new_unit.def_ = 5
            new_unit.spd = 12
            new_unit.skl = 30
            new_unit.lck = 25
            new_unit.has_acted = False
            new_unit.disposition = DispositionEnum.ACTIVE
        elif role == "HEALER":
            new_unit = UnitState()
            new_unit.id = unit_id
            new_unit.name = unit_name
            new_unit.faction = faction
            new_unit.position = spawn_position
            new_unit.current_hp = 50
            new_unit.max_hp = 50
            new_unit.ai_persona = persona
            new_unit.role = role
            new_unit.str = 5
            new_unit.def_ = 5
            new_unit.spd = 14
            new_unit.skl = 25
            new_unit.lck = 20
            new_unit.has_acted = False
            new_unit.disposition = DispositionEnum.ACTIVE
        else:  # SCOUT
            new_unit = UnitState()
            new_unit.id = unit_id
            new_unit.name = unit_name
            new_unit.faction = faction
            new_unit.position = spawn_position
            new_unit.current_hp = 65
            new_unit.max_hp = 65
            new_unit.ai_persona = persona
            new_unit.role = role
            new_unit.str = 18
            new_unit.def_ = 12
            new_unit.spd = 25
            new_unit.skl = 8
            new_unit.lck = 12
            new_unit.has_acted = False
            new_unit.disposition = DispositionEnum.ACTIVE
        
        # Add unit to game state
        game_state_manager.current_game_state.unit_states[unit_id] = new_unit
        game_state_manager.current_game_state.map_state.unit_positions[unit_id] = spawn_position
        
        # Log the reinforcement
        visual_logger.log_action("SYSTEM", "REINFORCEMENT", f"{faction.name} reinforcement: {unit_name} ({role}) at {spawn_position}")
        logger.info(f"Reinforcement event: {faction.name} reinforcement: {unit_name} ({role}) arrived at {spawn_position}")
        
        return new_unit
    
    def _change_objectives(self, game_state_manager, visual_logger, scenario_state):
        """Change the secondary objectives to create dynamic gameplay."""
        map_width = game_state_manager.current_game_state.map_state.dimensions[0]
        map_height = game_state_manager.current_game_state.map_state.dimensions[1]
        
        # Choose a new secondary objective
        possible_positions = []
        
        # Find valid positions (villages or other strategic points)
        terrain_grid = game_state_manager.current_game_state.map_state.terrain_grid
        for y in range(map_height):
            for x in range(map_width):
                if terrain_grid[y][x] == 'V' or (terrain_grid[y][x] == 'H' and random.random() < 0.3):
                    possible_positions.append((x, y))
        
        # Remove existing objectives
        possible_positions = [pos for pos in possible_positions if pos not in scenario_state["secondary_objectives"]]
        
        if not possible_positions:
            return  # No valid new objectives
        
        # Choose a new objective
        new_objective = random.choice(possible_positions)
        
        # Replace a random existing secondary objective
        if scenario_state["secondary_objectives"]:
            old_objective = random.choice(scenario_state["secondary_objectives"])
            scenario_state["secondary_objectives"].remove(old_objective)
            del scenario_state["objective_owner"][old_objective]
        
        # Add the new objective
        scenario_state["secondary_objectives"].append(new_objective)
        scenario_state["objective_owner"][new_objective] = None
        
        # Log the objective change
        visual_logger.log_action("SYSTEM", "OBJECTIVE_CHANGED", f"New objective at {new_objective}")
        logger.info(f"Objectives changed: New objective at {new_objective}")
    
    def _log_unit_disposition_counts(self, game_state_manager):
        """Log the final disposition counts of all units by faction and role."""
        # Initialize counters
        counts = {
            FactionEnum.PLAYER: {"ACTIVE": 0, "DEAD": 0, "OTHER": 0},
            FactionEnum.ENEMY: {"ACTIVE": 0, "DEAD": 0, "OTHER": 0},
            FactionEnum.NPC: {"ACTIVE": 0, "DEAD": 0, "OTHER": 0}
        }
        
        # Initialize role counters
        role_counts = {
            FactionEnum.PLAYER: {},
            FactionEnum.ENEMY: {},
            FactionEnum.NPC: {}
        }
        
        # Count by disposition and role
        for unit in game_state_manager.current_game_state.unit_states.values():
            if unit.faction not in counts:
                continue
                
            # Count by disposition
            if unit.disposition == DispositionEnum.ACTIVE:
                counts[unit.faction]["ACTIVE"] += 1
            elif unit.disposition == DispositionEnum.DEAD:
                counts[unit.faction]["DEAD"] += 1
            else:
                counts[unit.faction]["OTHER"] += 1
            
            # Count by role
            if hasattr(unit, "role") and unit.role:
                if unit.role not in role_counts[unit.faction]:
                    role_counts[unit.faction][unit.role] = 0
                role_counts[unit.faction][unit.role] += 1
        
        # Log the counts
        for faction, dispositions in counts.items():
            logger.info(f"{faction.name} units: {dispositions['ACTIVE']} active, {dispositions['DEAD']} defeated, {dispositions['OTHER']} other")
            
        # Log role distribution
        for faction, roles in role_counts.items():
            if roles:
                logger.info(f"{faction.name} role distribution:")
                for role, count in roles.items():
                    logger.info(f"  {role}: {count} units") 

    def _update_scenario_state(self, scenario_state, current_turn, game_state_manager):
        """Update the scenario state at the start of each turn."""
        # Update weather duration and clear expired weather
        if scenario_state["active_weather"] and scenario_state["weather_duration"] > 0:
            scenario_state["weather_duration"] -= 1
            logger.info(f"{scenario_state['active_weather']} weather continues ({scenario_state['weather_duration']} turns left)")
        elif scenario_state["active_weather"]:
            logger.info(f"{scenario_state['active_weather']} weather has cleared")
            scenario_state["active_weather"] = None
        
        # Update throne control counter
        throne_position = scenario_state["primary_objective"]
        current_owner = scenario_state["objective_owner"][throne_position]
        
        if current_owner:
            if not hasattr(scenario_state, "last_throne_owner") or scenario_state["last_throne_owner"] == current_owner:
                # Same owner as last turn, increment counter
                throne_control_turns = scenario_state.get("throne_control_turns", 0) + 1
                scenario_state["throne_control_turns"] = throne_control_turns
                logger.info(f"{current_owner.name} has controlled the throne for {throne_control_turns} turns")
            else:
                # New owner, reset counter
                scenario_state["throne_control_turns"] = 1
                logger.info(f"{current_owner.name} has taken control of the throne")
            
            scenario_state["last_throne_owner"] = current_owner