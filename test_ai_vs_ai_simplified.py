import pytest
import os
import logging
from src.core_engine.game_state import GameState, GameStateManager, PhaseEnum, FactionEnum
from src.core_engine.data_provider import DataProvider
from src.core_engine.scenario_loader import ScenarioLoader
from src.core_engine.action_handler import ActionHandler
from src.core_engine.turn_manager import TurnManager
from src.gameplay_systems.ai_system import AISystem
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.healing_system import HealingSystem
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.ai.tactical_executor import TacticalExecutor

# Purge relevant log files at the beginning of the test run
log_files_to_purge = [
    'ai_behavior.log',
    'ai_vs_ai_debug.log',
    'ai_vs_ai_simplified.log',
    'ai_vs_ai_test.log'
]
for log_file in log_files_to_purge:
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
            print(f"Purged existing log file: {log_file}")
        except OSError as e:
            print(f"Error removing file {log_file}: {e}") # Optional: log error

# Configure logging
# Configure root logger to INFO level (reduced from DEBUG)
logging.basicConfig(
    level=logging.DEBUG, # Set to DEBUG to capture all detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_vs_ai_simplified.log"), # Use the specific log file for this test
        logging.StreamHandler()
    ]
)

# Create a test-specific logger
logger = logging.getLogger("AI_VS_AI_SIMPLIFIED_TEST")
logger.info("Log files purged and logging initialized")

class TestAIvsAISimplified:
    """Test class for running a simplified AI vs AI simulation for 3 turns."""
    
    @pytest.fixture
    def game_state(self):
        """Set up the game state with the AI vs AI scenario."""
        scenario_name = "ai_vs_ai_scenario_01"
        
        # Create a data provider and load all data
        data_provider = DataProvider()
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Load the scenario data
        loader = ScenarioLoader()
        scenario_data = loader.load_scenario(scenario_name)
        
        # Initialize the game state from the scenario data
        game_state_manager.initialize_from_scenario(scenario_data)
        
        return game_state_manager
    
    def test_ai_vs_ai_simplified(self, game_state):
        """Run a short simulation of AI vs AI combat for exactly 3 turns."""
        # Initialize systems
        combat_system = CombatSystem()
        movement_system = MovementSystem()
        healing_system = HealingSystem()
        unit_system = UnitSystem()
        action_handler = ActionHandler()
        turn_manager = TurnManager()
        
        # Create and initialize map system first (required by movement system)
        map_system = MapSystem()
        map_system.initialize(game_state, game_state.data_provider)
        
        # Initialize the systems with necessary dependencies
        combat_system.initialize(game_state, game_state.data_provider, unit_system, None, None)
        movement_system.initialize(game_state, map_system)
        healing_system.initialize(game_state, game_state.data_provider, unit_system, None)
        
        # Initialize turn manager
        turn_manager.initialize(
            gameStateManager_instance=game_state,
            unitSystem_instance=unit_system,
            dataProvider_instance=game_state.data_provider
        )
        
        # Initialize action handler with dependencies
        action_handler.initialize(
            gameStateManager_instance=game_state,
            unitSystem_instance=unit_system,
            mapSystem_instance=map_system,
            movementSystem_instance=movement_system,
            combatSystem_instance=combat_system,
            inventorySystem_instance=None,
            turnManager_instance=turn_manager,
            eventHandler_instance=None,
            dataProvider_instance=game_state.data_provider,
            core_turn_manager_instance=None
        )
        
        # Enable AI vs AI mode
        action_handler.ai_vs_ai = True
        game_state.ai_vs_ai = True  # Set the flag on the GameStateManager as well
        logger.info(f"AI vs AI mode enabled: {action_handler.ai_vs_ai}")
        
        # Create a tactical executor with real systems
        tactical_executor = TacticalExecutor(movement_system, combat_system, healing_system)
        
        # Initialize AI system with the tactical executor and action handler
        ai_system = AISystem(game_state, action_handler)
        ai_system.tactical_executor = tactical_executor
        
        # Set both factions to be AI-controlled
        if hasattr(game_state, 'set_faction_ai_controlled'):
            game_state.set_faction_ai_controlled("PLAYER", True)
            game_state.set_faction_ai_controlled("ENEMY", True)
        
        # Fixed number of turns - exactly 3
        max_turns = 3
        current_turn = 1
        
        # Print initial state
        player_units = game_state.get_units_by_faction("PLAYER")
        enemy_units = game_state.get_units_by_faction("ENEMY")
        logger.info(f"Initial state: {len(player_units)} player units, {len(enemy_units)} enemy units")
        
        # Run simulation for exactly 3 turns
        while current_turn <= max_turns:
            logger.info(f"=== Turn {current_turn} ===")
            
            # Player phase (AI-controlled)
            logger.info("Player Phase (AI-controlled)")
            game_state.current_game_state.current_phase = PhaseEnum.PLAYER
            self._execute_faction_turn(game_state, ai_system, "PLAYER")
            
            # Check if enemy units are all defeated
            if len(game_state.get_units_by_faction("ENEMY")) == 0:
                logger.info("All enemy units defeated")
                break
                
            # Enemy phase (AI-controlled)
            logger.info("Enemy Phase (AI-controlled)")
            game_state.current_game_state.current_phase = PhaseEnum.ENEMY
            self._execute_faction_turn(game_state, ai_system, "ENEMY")
            
            # Check if player units are all defeated
            if len(game_state.get_units_by_faction("PLAYER")) == 0:
                logger.info("All player units defeated")
                break
                
            # End of turn processing
            if hasattr(game_state, 'end_turn'):
                game_state.end_turn()
            elif hasattr(game_state.current_game_state, 'end_turn'):
                game_state.current_game_state.end_turn()
            
            current_turn += 1
        
        # Log final state
        player_units_count = len(game_state.get_units_by_faction("PLAYER"))
        enemy_units_count = len(game_state.get_units_by_faction("ENEMY"))
        
        logger.info(f"Simulation ended after {current_turn-1} turns")
        logger.info(f"Final state: {player_units_count} player units, {enemy_units_count} enemy units")
        
        # Return final state for manual inspection if needed
        return {
            "turns_completed": current_turn - 1,
            "player_units_remaining": player_units_count,
            "enemy_units_remaining": enemy_units_count
        }
    
    def _execute_faction_turn(self, game_state, ai_system, faction):
        """Execute a turn for all units of a faction with simplified logging."""
        units = game_state.get_units_by_faction(faction)
        logger.info(f"Processing {len(units)} units for faction {faction}")
        
        for unit in units:
            # Determine if unit can act
            can_act = True
            if hasattr(unit, 'can_act'):
                can_act = unit.can_act()
                
            if can_act:
                logger.info(f"AI processing for {unit.name} ({unit.id}) at {unit.position}")
                
                # AI makes decisions and executes actions
                ai_system.process_unit_turn(unit)
                
                # Mark unit as acted
                if hasattr(unit, 'end_turn'):
                    unit.end_turn()


if __name__ == "__main__":
    # This allows running the test directly (not through pytest)
    test = TestAIvsAISimplified()
    
    # Create game state directly instead of using the fixture
    scenario_name = "ai_vs_ai_scenario_01"
    data_provider = DataProvider()
    data_provider.load_all_data("data")
    game_state_manager = GameStateManager(data_provider)
    loader = ScenarioLoader()
    scenario_data = loader.load_scenario(scenario_name)
    game_state_manager.initialize_from_scenario(scenario_data)
    
    # Run the simplified test
    result = test.test_ai_vs_ai_simplified(game_state_manager)
    print(f"Simplified test completed: {result}")