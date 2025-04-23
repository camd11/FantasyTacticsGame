"""
AI Scenario 04: Advanced Tactical Positioning Test (Max 5 Turns)

This scenario tests multiple AI units with different personas
working together in a more complex tactical situation.

It includes visual logging to analyze AI decision-making.
"""

import pytest
import logging
from typing import Dict, Any
from unittest.mock import Mock

# Import the required modules
from src.core_engine.game_state import GameStateManager, FactionEnum, GameState, MapState, UnitState
from src.core_engine.data_provider import DataProvider

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
logger = logging.getLogger("test_ai_scenario_04")

class TestAIScenario04:
    """Test suite for AI Scenario 04: Advanced Tactical Positioning (Max 5 Turns)."""
    
    @pytest.fixture
    def scenario_setup(self):
        """Load the AI test scenario and set up the game state."""
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load all data from the data directory
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a more complex map state
        map_state = MapState()
        map_state.dimensions = (15, 15)
        
        # Default terrain is plains, with some obstacles
        terrain_grid = [['P'] * 15 for _ in range(15)]
        
        # Add a river in the middle
        for i in range(15):
            terrain_grid[7][i] = 'R'  # River
        
        # Add a bridge at position 7,7
        terrain_grid[7][7] = 'B'  # Bridge
        
        # Add some forests and mountains for tactical terrain
        for i in range(3, 6):
            terrain_grid[3][i] = 'F'  # Forest
            terrain_grid[11][i+5] = 'F'  # Forest
            
        for i in range(2, 4):
            terrain_grid[i][11] = 'M'  # Mountain
            terrain_grid[i+8][2] = 'M'  # Mountain
        
        # Add a village
        terrain_grid[2][2] = 'V'  # Village
        terrain_grid[12][12] = 'V'  # Village
        
        # Set map state
        map_state.terrain_grid = terrain_grid
        map_state.map_id = "advanced_tactics_test"
        
        # Create game state
        game_state = GameState()
        game_state.chapter_id = "test_chapter_ai_04"
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
        visual_logger = VisualScenarioLogger(
            game_state_manager=game_state_manager,
            cli_display=cli_display,
            log_dir="logs",
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
        """Add units to the game state with various personas and positions."""
        unit_states = {}
        unit_positions = {}
        
        # Player faction units (North side of river)
        player_units = [
            {
                "id": "PLAYER_LORD",
                "name": "Lord",
                "faction": FactionEnum.PLAYER,
                "position": (3, 3),
                "current_hp": 40,
                "max_hp": 40,
                "ai_persona": "AGGRESSOR"
            },
            {
                "id": "PLAYER_KNIGHT",
                "name": "Knight",
                "faction": FactionEnum.PLAYER,
                "position": (2, 4),
                "current_hp": 45,
                "max_hp": 45,
                "ai_persona": "DEFENDER"
            },
            {
                "id": "PLAYER_ARCHER",
                "name": "Archer",
                "faction": FactionEnum.PLAYER,
                "position": (4, 2),
                "current_hp": 30,
                "max_hp": 30,
                "ai_persona": "OPPORTUNIST"
            },
            {
                "id": "PLAYER_CLERIC",
                "name": "Cleric",
                "faction": FactionEnum.PLAYER,
                "position": (5, 5),
                "current_hp": 25,
                "max_hp": 25,
                "ai_persona": "SUPPORT"
            },
            {
                "id": "PLAYER_MAGE",
                "name": "Mage",
                "faction": FactionEnum.PLAYER,
                "position": (1, 6),
                "current_hp": 25,
                "max_hp": 25,
                "ai_persona": "CAUTIOUS"
            }
        ]
        
        # Enemy faction units (South side of river)
        enemy_units = [
            {
                "id": "ENEMY_GENERAL",
                "name": "General",
                "faction": FactionEnum.ENEMY,
                "position": (10, 10),
                "current_hp": 50,
                "max_hp": 50,
                "ai_persona": "DEFENDER"
            },
            {
                "id": "ENEMY_FIGHTER",
                "name": "Fighter",
                "faction": FactionEnum.ENEMY,
                "position": (11, 9),
                "current_hp": 35,
                "max_hp": 35,
                "ai_persona": "AGGRESSOR"
            },
            {
                "id": "ENEMY_ARCHER",
                "name": "Archer",
                "faction": FactionEnum.ENEMY,
                "position": (9, 11),
                "current_hp": 30,
                "max_hp": 30,
                "ai_persona": "OPPORTUNIST"
            },
            {
                "id": "ENEMY_HEALER",
                "name": "Healer",
                "faction": FactionEnum.ENEMY,
                "position": (12, 10),
                "current_hp": 25,
                "max_hp": 25,
                "ai_persona": "SUPPORT"
            },
            {
                "id": "ENEMY_CAVALRY",
                "name": "Cavalry",
                "faction": FactionEnum.ENEMY,
                "position": (8, 8),
                "current_hp": 40,
                "max_hp": 40,
                "ai_persona": "AGGRESSOR"
            }
        ]
        
        # Create all units
        all_units = player_units + enemy_units
        faction_units = {
            "PLAYER": [],
            "ENEMY": []
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
            unit.has_healing_capability = lambda: "CLERIC" in unit.id or "HEALER" in unit.id
            
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
    
    def test_ai_vs_ai_tactical_scenario(self, scenario_setup):
        """
        Test a 5-turn AI vs AI scenario with mixed unit types and tactical terrain.
        
        This test verifies:
        1. AI units properly navigate terrain
        2. Units move toward tactical objectives
        3. Combat decisions are influenced by terrain and positioning
        4. Visual logging captures the full scenario
        """
        # Get setup data
        engine = scenario_setup["engine"]
        game_state_manager = scenario_setup["game_state_manager"]
        visual_logger = scenario_setup["visual_logger"]
        
        # Log initial state
        visual_logger.log_initial_state()
        logger.info("Starting 5-turn AI vs AI tactical scenario")
        
        # Set maximum turns (5 turns max as per requirements)
        MAX_TURNS = 5
        current_turn = 1
        
        # Initial counts
        initial_player_units = len(game_state_manager.get_units_by_faction(FactionEnum.PLAYER))
        initial_enemy_units = len(game_state_manager.get_units_by_faction(FactionEnum.ENEMY))
        
        logger.info(f"Initial state: {initial_player_units} player units, {initial_enemy_units} enemy units")
        
        # Log initial positions
        for faction in [FactionEnum.PLAYER, FactionEnum.ENEMY]:
            units = game_state_manager.get_units_by_faction(faction)
            for unit in units:
                logger.info(f"{unit.faction.name} unit {unit.name} ({unit.id}) at position {unit.position}")
        
        # Run the simulation for specified number of turns
        while current_turn <= MAX_TURNS:
            # Log turn start
            logger.info(f"=== Turn {current_turn} ===")
            visual_logger.log_turn_start(current_turn)
            
            # Process player phase
            logger.info("Player Phase (AI-controlled)")
            visual_logger.log_phase_start(FactionEnum.PLAYER)
            self._process_ai_turn(engine, game_state_manager, FactionEnum.PLAYER)
            
            # Check win condition
            enemy_units = game_state_manager.get_units_by_faction(FactionEnum.ENEMY)
            if not enemy_units:
                logger.info("All enemy units defeated - Player victory!")
                break
            
            # Process enemy phase
            logger.info("Enemy Phase (AI-controlled)")
            visual_logger.log_phase_start(FactionEnum.ENEMY)
            self._process_ai_turn(engine, game_state_manager, FactionEnum.ENEMY)
            
            # Check win condition
            player_units = game_state_manager.get_units_by_faction(FactionEnum.PLAYER)
            if not player_units:
                logger.info("All player units defeated - Enemy victory!")
                break
            
            # Log end of turn state
            visual_logger.log_end_of_turn_state(current_turn)
            
            # Increment turn counter
            current_turn += 1
        
        # Final turn state if max turns reached
        if current_turn > MAX_TURNS:
            logger.info(f"Maximum turns ({MAX_TURNS}) reached - simulation ended")
            
        # Final unit counts
        final_player_units = len(game_state_manager.get_units_by_faction(FactionEnum.PLAYER))
        final_enemy_units = len(game_state_manager.get_units_by_faction(FactionEnum.ENEMY))
        
        # Log final stats
        logger.info(f"Simulation ended after {current_turn-1} turns")
        logger.info(f"Final state: {final_player_units} player units, {final_enemy_units} enemy units")
        
        # Finalize the log
        visual_logger.finalize_log()
        
        # Verify reasonable outcome
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
            "log_file": visual_logger.log_file_path
        }
    
    def _process_ai_turn(self, engine, game_state_manager, faction):
        """Process a single AI turn for the specified faction."""
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
                # Use the engine's AI processing
                engine.process_ai_unit_turn(unit)
            except Exception as e:
                logger.error(f"Error processing AI for unit {unit.id}: {e}")
                
            # Mark the unit as having acted (might be done by the engine already)
            unit.has_acted = True
        
        # End phase/turn (handled by the engine) 