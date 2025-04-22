import pytest
from unittest.mock import Mock, patch

# Import the required modules
# from src.core_engine.scenario_loader import ScenarioLoader # Removed
from src.core_engine.game_state import GameStateManager, FactionEnum, GameState, MapState # Added GameState, MapState
from src.core_engine.data_provider import DataProvider

# Import AI modules
from src.gameplay_systems.ai.strategic_evaluator import StrategicEvaluator
from src.gameplay_systems.ai.tactical_executor import TacticalExecutor
from src.gameplay_systems.ai.utility_scorer import UtilityScorer
from src.gameplay_systems.ai.goals import Goal, AttackUnitGoal, MoveToSafetyGoal, HealUnitGoal
from src.gameplay_systems.ai.ai_persona import AIPersona


class TestAIScenario01:
    """Test suite for the AI Test Scenario 01: Strategic Goal Selection."""
    
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
        map_state.dimensions = (10, 10)
        map_state.terrain_grid = [['P'] * 10 for _ in range(10)]
        game_state = GameState("test_chapter_ai_01", map_state)
        game_state_manager.set_current_game_state(game_state)
        
        # Add mock units for testing (same as scenario 02 for simplicity)
        self._add_mock_units(game_state_manager)
        
        # Mock the pathfinding methods
        self._mock_pathfinding(game_state_manager)
        
        # Create the AI components
        utility_scorer = UtilityScorer(game_state_manager)
        strategic_evaluator = StrategicEvaluator(utility_scorer)
        
        return {
            "game_state_manager": game_state_manager,
            "strategic_evaluator": strategic_evaluator,
            "data_provider": data_provider
        }
    
    # Copying mock methods from test_ai_scenario_02.py for setup
    def _add_mock_units(self, game_state_manager):
        """Add mock units to the game state for testing."""
        from src.core_engine.game_state import UnitState
        
        # Create mock units with the required personas
        enemy_fighter = UnitState()
        enemy_fighter.id = "ENEMY_FIGHTER"
        enemy_fighter.name = "Enemy Fighter"
        enemy_fighter.faction = FactionEnum.ENEMY
        enemy_fighter.ai_persona = "AGGRESSOR"
        enemy_fighter.position = (2, 2)
        enemy_fighter.current_hp = 30
        enemy_fighter.max_hp = 30
        
        enemy_knight = UnitState()
        enemy_knight.id = "ENEMY_KNIGHT"
        enemy_knight.name = "Enemy Knight"
        enemy_knight.faction = FactionEnum.ENEMY
        enemy_knight.ai_persona = "DEFENDER"
        enemy_knight.position = (3, 3)
        enemy_knight.current_hp = 10 # Low HP for MoveToSafetyGoal
        enemy_knight.max_hp = 35
        
        enemy_cleric = UnitState()
        enemy_cleric.id = "ENEMY_CLERIC"
        enemy_cleric.name = "Enemy Cleric"
        enemy_cleric.faction = FactionEnum.ENEMY
        enemy_cleric.ai_persona = "SUPPORT"
        enemy_cleric.position = (1, 1)
        enemy_cleric.current_hp = 24
        enemy_cleric.max_hp = 24
        enemy_cleric.has_healing_capability = lambda: True
        
        enemy_archer = UnitState() # Injured ally for cleric
        enemy_archer.id = "ENEMY_ARCHER"
        enemy_archer.name = "Enemy Archer"
        enemy_archer.faction = FactionEnum.ENEMY
        enemy_archer.position = (1, 0) # Adjacent to cleric
        enemy_archer.current_hp = 5
        enemy_archer.max_hp = 28
        
        # Add units to the game state
        if game_state_manager.current_game_state:
            game_state = game_state_manager.current_game_state
            game_state.unit_states = {
                "ENEMY_FIGHTER": enemy_fighter,
                "ENEMY_KNIGHT": enemy_knight,
                "ENEMY_CLERIC": enemy_cleric,
                "ENEMY_ARCHER": enemy_archer
            }
            game_state.map_state.unit_positions = {
                "ENEMY_FIGHTER": enemy_fighter.position,
                "ENEMY_KNIGHT": enemy_knight.position,
                "ENEMY_CLERIC": enemy_cleric.position,
                "ENEMY_ARCHER": enemy_archer.position
            }
            game_state.map_state.allies["ENEMY"] = ["ENEMY_FIGHTER", "ENEMY_KNIGHT", "ENEMY_CLERIC", "ENEMY_ARCHER"]
    
    def _mock_pathfinding(self, game_state_manager):
        # Mock necessary GameStateManager methods used by UtilityScorer/Goals
        game_state_manager.get_units_by_faction = lambda faction: list(game_state_manager.current_game_state.unit_states.values()) if faction == FactionEnum.ENEMY else []
        game_state_manager.get_allies_within_range = lambda unit, range_val: [game_state_manager.get_unit_by_id("ENEMY_ARCHER")] if unit.id == "ENEMY_CLERIC" else []
        game_state_manager.get_enemies_within_range = lambda unit, range_val: [] # Assume no enemies nearby for goal selection focus
        game_state_manager.is_unit_threatened = lambda unit: unit.id == "ENEMY_KNIGHT" # Knight is threatened
        game_state_manager.find_safe_tiles_for_unit = lambda unit: [(5, 5)] # Provide a safe tile
        game_state_manager.can_unit_heal_target = lambda healer, target: healer.id == "ENEMY_CLERIC" and target.id == "ENEMY_ARCHER"
    
    def test_aggressor_selects_attack_goal(self, scenario_setup):
        """Test that an AI unit with the AGGRESSOR persona selects the AttackUnitGoal."""
        evaluator = scenario_setup["strategic_evaluator"]
        game_state_manager = scenario_setup["game_state_manager"]
        unit = game_state_manager.get_unit_by_id("ENEMY_FIGHTER")
        
        # Mock get_enemies_within_range to return a potential target
        mock_player_unit = Mock(id="PLAYER_1", position=(3,2), current_hp=20, max_hp=20)
        game_state_manager.get_enemies_within_range = lambda u, r: [mock_player_unit]
        
        selected_goal = evaluator.determine_best_goal(unit)
        assert isinstance(selected_goal, AttackUnitGoal), "Aggressor should select AttackUnitGoal"
    
    def test_defender_selects_move_to_safety_goal(self, scenario_setup):
        """Test that a threatened AI unit with the DEFENDER persona selects the MoveToSafetyGoal."""
        evaluator = scenario_setup["strategic_evaluator"]
        game_state_manager = scenario_setup["game_state_manager"]
        unit = game_state_manager.get_unit_by_id("ENEMY_KNIGHT") # Knight is threatened
        
        selected_goal = evaluator.determine_best_goal(unit)
        assert isinstance(selected_goal, MoveToSafetyGoal), "Threatened Defender should select MoveToSafetyGoal"

    def test_support_selects_heal_goal(self, scenario_setup):
        """Test that an AI unit with the SUPPORT persona selects the HealUnitGoal when an ally needs healing."""
        evaluator = scenario_setup["strategic_evaluator"]
        game_state_manager = scenario_setup["game_state_manager"]
        unit = game_state_manager.get_unit_by_id("ENEMY_CLERIC")
        
        selected_goal = evaluator.determine_best_goal(unit)
        assert isinstance(selected_goal, HealUnitGoal), "Support should select HealUnitGoal when ally is injured nearby"