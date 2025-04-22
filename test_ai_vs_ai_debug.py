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
from src.app import GameApplication
from unittest.mock import Mock

# Configure logging
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
# Create a test-specific logger and add a file handler
logger = logging.getLogger("AI_VS_AI_DEBUG_TEST")
logger.setLevel(logging.DEBUG) # Set the logger level to DEBUG

# Create a file handler and set its level to DEBUG
file_handler = logging.FileHandler("ai_vs_ai_debug.log")
file_handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
# Prevent adding duplicate handlers if the test is run multiple times in the same process
if not logger.handlers:
    logger.addHandler(file_handler)

# Optionally, add a stream handler for console output
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO) # Keep console output less verbose
stream_handler.setFormatter(formatter)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
     logger.addHandler(stream_handler)

logger.info("Log files purged and logging initialized")

class TestAIvsAIDebug:
    """Test class for debugging AI vs AI interactions."""
    
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
    
    def test_ai_vs_ai_debug(self, game_state):
        """Run a short simulation of AI vs AI combat with detailed debugging."""
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
        mock_turn_manager = Mock(spec=TurnManager)
        action_handler.initialize(
            gameStateManager_instance=game_state,
            mapSystem_instance=map_system,
            unitSystem_instance=unit_system,
            combatSystem_instance=combat_system,
            eventHandler_instance=None,
            core_turn_manager_instance=mock_turn_manager,
            movementSystem_instance=None,
            inventorySystem_instance=None,
            turnManager_instance=None,
            dataProvider_instance=game_state.data_provider
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
        
        # Run simulation for a limited number of turns
        max_turns = 3  # Limit to 3 turns to avoid overwhelming logs
        current_turn = 1
        
        # Print initial state
        player_units = game_state.get_units_by_faction("PLAYER")
        enemy_units = game_state.get_units_by_faction("ENEMY")
        logger.info(f"Initial state: {len(player_units)} player units, {len(enemy_units)} enemy units")
        
        # Print unit details
        logger.info("Player units:")
        for unit in player_units:
            logger.info(f"  {unit.name} ({unit.id}) at {unit.position}")
        
        logger.info("Enemy units:")
        for unit in enemy_units:
            logger.info(f"  {unit.name} ({unit.id}) at {unit.position}")
        
        # Add a monkey patch to the _is_correct_phase_for_faction method to log its inputs and outputs
        original_is_correct_phase = action_handler._is_correct_phase_for_faction
        
        def patched_is_correct_phase(self, phase, faction):
            ai_vs_ai_value = self.ai_vs_ai
            if not ai_vs_ai_value and hasattr(self, 'turnManager') and self.turnManager and hasattr(self.turnManager, 'ai_vs_ai'):
                ai_vs_ai_value = self.turnManager.ai_vs_ai
                
            result = original_is_correct_phase(phase, faction)
            logger.debug(f"PHASE CHECK: phase={phase}, faction={faction}, ai_vs_ai={ai_vs_ai_value}, result={result}")
            return result
            
        action_handler._is_correct_phase_for_faction = patched_is_correct_phase.__get__(action_handler, ActionHandler)
        
        # Continue until one side is defeated or max turns reached
        while (current_turn <= max_turns and 
               len(game_state.get_units_by_faction("PLAYER")) > 0 and 
               len(game_state.get_units_by_faction("ENEMY")) > 0):
            
            logger.info(f"=== Turn {current_turn} ===")
            
            # Player phase (AI-controlled)
            logger.info("Player Phase (AI-controlled)")
            game_state.current_game_state.current_phase = PhaseEnum.PLAYER
            logger.debug(f"Set current phase to {game_state.current_game_state.current_phase}")
            self._execute_faction_turn(game_state, ai_system, "PLAYER")
            
            # Check if enemy units are all defeated
            if len(game_state.get_units_by_faction("ENEMY")) == 0:
                logger.info("All enemy units defeated")
                break
                
            # Enemy phase (AI-controlled)
            logger.info("Enemy Phase (AI-controlled)")
            game_state.current_game_state.current_phase = PhaseEnum.ENEMY
            logger.debug(f"Set current phase to {game_state.current_game_state.current_phase}")
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
        """Execute a turn for all units of a faction with detailed logging."""
        units = game_state.get_units_by_faction(faction)
        logger.info(f"Found {len(units)} units for faction {faction}")
        
        for unit in units:
            logger.info(f"Processing unit {unit.name} ({unit.id}) with faction {unit.faction}")
            
            # Check if the unit has a can_act method
            if not hasattr(unit, 'can_act'):
                logger.info(f"Unit {unit.name} does not have a can_act method, assuming it can act")
                can_act = True
            else:
                can_act = unit.can_act()
                logger.info(f"Unit {unit.name} can_act() returned {can_act}")
                
            if can_act:
                logger.info(f"AI processing for {unit.name} ({unit.id}) with persona {unit.ai_persona}")
                
                # Log unit's current state
                logger.info(f"  Position: {unit.position}, HP: {unit.current_hp}/{unit.base_stats.get('HP', 0)}")
                
                # AI makes decisions and executes actions
                ai_system.process_unit_turn(unit)
                
                # Log unit's actions (would be captured in AI system logs)
                logger.info(f"  Unit {unit.name} finished actions")
                
                # Mark unit as acted
                if hasattr(unit, 'end_turn'):
                    unit.end_turn()
                    logger.info(f"Unit {unit.name} marked as acted")
                else:
                    logger.info(f"Unit {unit.name} does not have an end_turn method")


if __name__ == "__main__":
    # This allows running the test directly (not through pytest)
    test = TestAIvsAIDebug()
    
    # Create game state directly instead of using the fixture
    scenario_name = "ai_vs_ai_scenario_01"
    data_provider = DataProvider()
    data_provider.load_all_data("data")
    game_state_manager = GameStateManager(data_provider)
    loader = ScenarioLoader()
    scenario_data = loader.load_scenario(scenario_name)
    game_state_manager.initialize_from_scenario(scenario_data)
    
    # Run the debug test
    result = test.test_ai_vs_ai_debug(game_state_manager)
    print(f"Debug test completed: {result}")