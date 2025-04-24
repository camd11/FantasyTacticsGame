import pytest
from unittest.mock import Mock, patch

# Import the required modules
from src.core_engine.game_state import GameStateManager, FactionEnum, GameState, MapState
from src.core_engine.data_provider import DataProvider

# Import AI modules
from src.gameplay_systems.ai.strategic_evaluator import StrategicEvaluator
from src.gameplay_systems.ai.tactical_executor import TacticalExecutor
from src.gameplay_systems.ai.ai_types import AIAction, AIActionType

class TestAIScenario03:
    """Test suite for the AI Test Scenario 03: Interaction with Multiple Systems."""
    
    @pytest.fixture
    def scenario_setup(self):
        """Load the AI test scenario and set up the game state."""
        # Create a DataProvider instance
        data_provider = DataProvider()
        
        # Load all data from the data directory
        data_provider.load_all_data("data")
        
        # Create a game state manager
        game_state_manager = GameStateManager(data_provider)
        
        # Create a simple GameState instead of loading from scenario
        map_state = MapState()
        map_state.dimensions = (15, 15)
        map_state.terrain_grid = [['P'] * 15 for _ in range(15)]
        game_state = GameState()
        game_state.chapter_id = "test_chapter_ai_03"
        game_state.map_state = map_state
        
        # Directly set the current_game_state rather than using a non-existent method
        game_state_manager.current_game_state = game_state
        
        # Add mock systems
        mock_combat_system = Mock()
        mock_healing_system = Mock()
        mock_movement_system = Mock()
        
        # Add mock units for testing
        self._add_mock_units(game_state_manager)
        
        # Mock the necessary methods
        self._mock_methods(game_state_manager, mock_combat_system, mock_healing_system, mock_movement_system)
        
        # Create the AI components
        strategic_evaluator = StrategicEvaluator(game_state_manager)
        tactical_executor = TacticalExecutor(game_state_manager)
        
        return {
            "game_state_manager": game_state_manager,
            "strategic_evaluator": strategic_evaluator,
            "tactical_executor": tactical_executor,
            "combat_system": mock_combat_system,
            "healing_system": mock_healing_system,
            "movement_system": mock_movement_system
        }
    
    def _add_mock_units(self, game_state_manager):
        """Add mock units to the game state for testing."""
        from src.core_engine.game_state import UnitState
        
        # Create mock units
        enemy_fighter = UnitState()
        enemy_fighter.id = "ENEMY_FIGHTER_1"
        enemy_fighter.name = "Enemy Fighter 1"
        enemy_fighter.faction = FactionEnum.ENEMY
        enemy_fighter.position = (2, 2)
        enemy_fighter.current_hp = 30
        enemy_fighter.max_hp = 30
        
        enemy_fighter_2 = UnitState()
        enemy_fighter_2.id = "ENEMY_FIGHTER_2"
        enemy_fighter_2.name = "Enemy Fighter 2"
        enemy_fighter_2.faction = FactionEnum.ENEMY
        enemy_fighter_2.position = (3, 3)
        enemy_fighter_2.current_hp = 30
        enemy_fighter_2.max_hp = 30
        
        player_knight = UnitState()
        player_knight.id = "PLAYER_KNIGHT"
        player_knight.name = "Player Knight"
        player_knight.faction = FactionEnum.PLAYER
        player_knight.position = (10, 10)
        player_knight.current_hp = 40
        player_knight.max_hp = 40
        
        player_archer = UnitState()
        player_archer.id = "PLAYER_ARCHER"
        player_archer.name = "Player Archer"
        player_archer.faction = FactionEnum.PLAYER
        player_archer.position = (11, 11)
        player_archer.current_hp = 25
        player_archer.max_hp = 25
        
        # Add units to the game state
        if game_state_manager.current_game_state:
            game_state = game_state_manager.current_game_state
            game_state.unit_states = {
                "ENEMY_FIGHTER_1": enemy_fighter,
                "ENEMY_FIGHTER_2": enemy_fighter_2,
                "PLAYER_KNIGHT": player_knight,
                "PLAYER_ARCHER": player_archer
            }
            game_state.map_state.unit_positions = {
                "ENEMY_FIGHTER_1": enemy_fighter.position,
                "ENEMY_FIGHTER_2": enemy_fighter_2.position,
                "PLAYER_KNIGHT": player_knight.position,
                "PLAYER_ARCHER": player_archer.position
            }
            game_state.map_state.allies = {
                "ENEMY": ["ENEMY_FIGHTER_1", "ENEMY_FIGHTER_2"], 
                "PLAYER": ["PLAYER_KNIGHT", "PLAYER_ARCHER"]
            }
    
    def _mock_methods(self, game_state_manager, mock_combat_system, mock_healing_system, mock_movement_system):
        """Mock the necessary methods for the test scenario."""
        # Mock get_unit_by_id
        game_state_manager.get_unit_by_id = lambda unit_id: game_state_manager.current_game_state.unit_states.get(unit_id, None)
        
        # Mock pathfinding methods
        mock_movement_system.get_path_to_position = lambda start, end: [(2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)] if start == (2,2) and end == (10,10) else []
        mock_movement_system.get_movement_cost = lambda unit, path: len(path) - 1
        mock_movement_system.get_reachable_tiles = lambda unit: [(2,2), (3,3), (4,4)]
        
        # Mock combat methods
        mock_combat_system.can_unit_attack = lambda attacker, target: True
        mock_combat_system.get_attack_damage = lambda attacker, target: 10
        
        # Mock healing methods
        mock_healing_system.can_unit_heal = lambda healer, target: True
        mock_healing_system.get_heal_amount = lambda healer, target: 15
        
        # Set up the mock systems as attributes on the game_state_manager
        game_state_manager.combat_system = mock_combat_system
        game_state_manager.healing_system = mock_healing_system
        game_state_manager.movement_system = mock_movement_system
    
    def test_multiple_system_interaction(self, scenario_setup):
        """Test that the AI can interact with multiple game systems."""
        from src.gameplay_systems.ai.goals import AttackUnitGoal
        
        executor = scenario_setup["tactical_executor"]
        game_state_manager = scenario_setup["game_state_manager"]
        unit = game_state_manager.get_unit_by_id("ENEMY_FIGHTER_1")
        target = game_state_manager.get_unit_by_id("PLAYER_KNIGHT")
        
        # Create an AttackUnitGoal
        goal = AttackUnitGoal(target.id)
        
        # Execute the goal
        action = executor.determine_action_for_goal(goal, unit, game_state_manager)
        
        # Verify the action is of the correct type
        assert action is not None
        assert action.action_type == AIActionType.MOVE
        assert action.target_data.get("path", [])[-1] == (4, 4)  # Should move toward the player knight
        
        # Mock the movement update
        unit.position = (4, 4)
        game_state_manager.current_game_state.map_state.unit_positions[unit.id] = (4, 4)
        
        # Re-evaluate goal after movement (should now be closer to target)
        action = executor.determine_action_for_goal(goal, unit, game_state_manager)
        
        # Verify second action
        assert action is not None
        assert action.action_type in [AIActionType.MOVE, AIActionType.WAIT]  # Either continue moving or wait 