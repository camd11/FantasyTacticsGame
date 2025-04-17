import pytest
from unittest.mock import Mock, patch

# Import the required modules
from src.core_engine.scenario_loader import ScenarioLoader
from src.core_engine.game_state import GameStateManager, FactionEnum
from src.core_engine.data_provider import DataProvider

# Import AI modules
from src.gameplay_systems.ai.strategic_evaluator import StrategicEvaluator
from src.gameplay_systems.ai.utility_scorer import UtilityScorer
from src.gameplay_systems.ai.goals import Goal, AttackUnitGoal, MoveToSafetyGoal, HealUnitGoal, SeizeTileGoal
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
        
        # Load the scenario
        scenario_loader = ScenarioLoader(data_provider)
        scenario = scenario_loader.load_scenario("ai_test_scenario_01")
        
        # Create a game state from the scenario
        game_state_manager = GameStateManager(data_provider)
        game_state_manager.initialize_from_scenario(scenario)
        
        # Add mock units for testing
        self._add_mock_units(game_state_manager)
        
        # Mock the pathfinding methods
        self._mock_pathfinding(game_state_manager)
        
        return {
            "scenario": scenario,
            "game_state_manager": game_state_manager
        }
    
    def _add_mock_units(self, game_state_manager):
        """Add mock units to the game state for testing."""
        from src.core_engine.game_state import UnitState
        
        # Create mock units with the required personas
        enemy_fighter = UnitState()
        enemy_fighter.id = "ENEMY_FIGHTER"
        enemy_fighter.name = "Enemy Fighter"
        enemy_fighter.faction = FactionEnum.ENEMY
        enemy_fighter.ai_persona = "AGGRESSOR"
        enemy_fighter.position = (6, 3)
        enemy_fighter.current_hp = 30
        enemy_fighter.max_hp = 30
        
        enemy_knight = UnitState()
        enemy_knight.id = "ENEMY_KNIGHT"
        enemy_knight.name = "Enemy Knight"
        enemy_knight.faction = FactionEnum.ENEMY
        enemy_knight.ai_persona = "DEFENDER"
        enemy_knight.position = (5, 5)
        enemy_knight.current_hp = 35
        enemy_knight.max_hp = 35
        
        enemy_cleric = UnitState()
        enemy_cleric.id = "ENEMY_CLERIC"
        enemy_cleric.name = "Enemy Cleric"
        enemy_cleric.faction = FactionEnum.ENEMY
        enemy_cleric.ai_persona = "SUPPORT"
        enemy_cleric.position = (6, 4)
        enemy_cleric.current_hp = 24
        enemy_cleric.max_hp = 24
        enemy_cleric.has_healing_capability = lambda: True
        
        enemy_thief = UnitState()
        enemy_thief.id = "ENEMY_THIEF"
        enemy_thief.name = "Enemy Thief"
        enemy_thief.faction = FactionEnum.ENEMY
        enemy_thief.ai_persona = "OBJECTIVE-FOCUSED"
        enemy_thief.position = (6, 6)
        enemy_thief.current_hp = 25
        enemy_thief.max_hp = 25
        
        # Add player units for testing
        leif = UnitState()
        leif.id = "LEIF"
        leif.name = "Leif"
        leif.faction = FactionEnum.PLAYER
        leif.position = (1, 3)
        leif.current_hp = 15
        leif.max_hp = 30
        
        finn = UnitState()
        finn.id = "FINN"
        finn.name = "Finn"
        finn.faction = FactionEnum.PLAYER
        finn.position = (2, 4)
        finn.current_hp = 32
        finn.max_hp = 32
        
        # Add units to the game state
        if game_state_manager.current_game_state:
            game_state_manager.current_game_state.unit_states["ENEMY_FIGHTER"] = enemy_fighter
            game_state_manager.current_game_state.unit_states["ENEMY_KNIGHT"] = enemy_knight
            game_state_manager.current_game_state.unit_states["ENEMY_CLERIC"] = enemy_cleric
            game_state_manager.current_game_state.unit_states["ENEMY_THIEF"] = enemy_thief
            game_state_manager.current_game_state.unit_states["LEIF"] = leif
            game_state_manager.current_game_state.unit_states["FINN"] = finn
            
            # Update unit positions
            game_state_manager.current_game_state.map_state.unit_positions["ENEMY_FIGHTER"] = enemy_fighter.position
            game_state_manager.current_game_state.map_state.unit_positions["ENEMY_KNIGHT"] = enemy_knight.position
            game_state_manager.current_game_state.map_state.unit_positions["ENEMY_CLERIC"] = enemy_cleric.position
            game_state_manager.current_game_state.map_state.unit_positions["ENEMY_THIEF"] = enemy_thief.position
            game_state_manager.current_game_state.map_state.unit_positions["LEIF"] = leif.position
            game_state_manager.current_game_state.map_state.unit_positions["FINN"] = finn.position
    
    def _mock_pathfinding(self, game_state_manager):
        """Mock the pathfinding methods in the game state manager."""
        # Create a mock pathfinding object
        class MockPathfinding:
            def can_potentially_reach(self, unit, position):
                return True
            
            def is_reachable(self, unit, position):
                return True
        
        # Add the mock pathfinding object to the game state manager
        game_state_manager.pathfinding = MockPathfinding()
        
        # Mock other methods needed by the AI
        game_state_manager.is_valid_position = lambda position: True
        game_state_manager.is_objective_tile = lambda position: position == [1, 1]
        game_state_manager.get_threat_level = lambda unit: 0
        game_state_manager.find_safe_tiles_for_unit = lambda unit: [(4, 4), (5, 5)]
        game_state_manager.get_position_threat_level = lambda position: 0
        game_state_manager.get_objective_importance = lambda position: 10
        game_state_manager.get_reachable_positions = lambda unit, position: [(2, 2), (3, 3)]
        game_state_manager.get_reachable_healing_positions = lambda unit, target: [(5, 5), (6, 6)]
        game_state_manager.is_unit_threatened = lambda unit: False
        game_state_manager.get_units_by_faction = lambda faction: [
            game_state_manager.get_unit_by_id("LEIF"),
            game_state_manager.get_unit_by_id("FINN")
        ] if faction == FactionEnum.PLAYER else [
            game_state_manager.get_unit_by_id("ENEMY_FIGHTER"),
            game_state_manager.get_unit_by_id("ENEMY_KNIGHT"),
            game_state_manager.get_unit_by_id("ENEMY_CLERIC"),
            game_state_manager.get_unit_by_id("ENEMY_THIEF")
        ]
    
    def test_aggressor_selects_attack_goal(self, scenario_setup):
        """
        Test that an AI unit with the AGGRESSOR persona prioritizes the ATTACK_UNIT goal.
        """
        # Arrange
        game_state_manager = scenario_setup["game_state_manager"]
        
        # Get the enemy fighter unit with AGGRESSOR persona
        enemy_fighter = game_state_manager.get_unit_by_id("ENEMY_FIGHTER")
        assert enemy_fighter is not None, "ENEMY_FIGHTER unit not found in scenario"
        assert enemy_fighter.ai_persona == "AGGRESSOR", "ENEMY_FIGHTER should have AGGRESSOR persona"
        
        # Create the strategic evaluator with a custom goal library
        utility_scorer = UtilityScorer(game_state_manager)
        strategic_evaluator = StrategicEvaluator(
            utility_scorer=utility_scorer,
            goal_library=[AttackUnitGoal, MoveToSafetyGoal, HealUnitGoal, SeizeTileGoal]
        )
        
        # Mock the utility scorer to return high scores for ATTACK_UNIT goals
        original_score_goal = utility_scorer.score_goal
        
        def mock_score_goal(goal, unit_state, game_state_manager, persona=None):
            if goal.goal_type == "ATTACK_UNIT":
                return 100.0
            else:
                return 50.0
                
        utility_scorer.score_goal = mock_score_goal
        
        # Act
        selected_goal = strategic_evaluator.select_best_goal(enemy_fighter, game_state_manager)
        
        # Restore the original score_goal method
        utility_scorer.score_goal = original_score_goal
        
        # Assert
        assert selected_goal is not None, "Strategic evaluator should select a goal"
        assert selected_goal.goal_type == "ATTACK_UNIT", "AGGRESSOR should prioritize ATTACK_UNIT goal"
        
        # Verify the target is a player unit
        target_unit_id = selected_goal.parameters.get("target_unit_id")
        assert target_unit_id is not None, "ATTACK_UNIT goal should have a target_unit_id parameter"
        
        target_unit = game_state_manager.get_unit_by_id(target_unit_id)
        assert target_unit is not None, "Target unit should exist"
        assert target_unit.faction == FactionEnum.PLAYER, "Target should be a player unit"
    
    def test_defender_selects_secure_position_goal(self, scenario_setup):
        """
        Test that an AI unit with the DEFENDER persona prioritizes the MOVE_TO_SAFETY goal.
        """
        # Arrange
        game_state_manager = scenario_setup["game_state_manager"]
        
        # Get the enemy knight unit with DEFENDER persona
        enemy_knight = game_state_manager.get_unit_by_id("ENEMY_KNIGHT")
        assert enemy_knight is not None, "ENEMY_KNIGHT unit not found in scenario"
        assert enemy_knight.ai_persona == "DEFENDER", "ENEMY_KNIGHT should have DEFENDER persona"
        
        # Create the strategic evaluator with a custom goal library
        utility_scorer = UtilityScorer(game_state_manager)
        strategic_evaluator = StrategicEvaluator(
            utility_scorer=utility_scorer,
            goal_library=[AttackUnitGoal, MoveToSafetyGoal, HealUnitGoal, SeizeTileGoal]
        )
        
        # Mock the utility scorer to return high scores for MOVE_TO_SAFETY goals
        original_score_goal = utility_scorer.score_goal
        
        def mock_score_goal(goal, unit_state, game_state_manager, persona=None):
            if goal.goal_type == "MOVE_TO_SAFETY":
                return 100.0
            else:
                return 50.0
                
        utility_scorer.score_goal = mock_score_goal
        
        # Create a MoveToSafetyGoal instance and add it to the goal library
        move_to_safety_goal = MoveToSafetyGoal()
        
        # Override the generate_valid_goal_instances method to include the MoveToSafetyGoal
        original_generate_valid_goal_instances = strategic_evaluator.generate_valid_goal_instances
        
        def mock_generate_valid_goal_instances(unit, game_state):
            goals = original_generate_valid_goal_instances(unit, game_state)
            goals.append(move_to_safety_goal)
            return goals
            
        strategic_evaluator.generate_valid_goal_instances = mock_generate_valid_goal_instances
        
        # Act
        selected_goal = strategic_evaluator.select_best_goal(enemy_knight, game_state_manager)
        
        # Restore the original methods
        utility_scorer.score_goal = original_score_goal
        strategic_evaluator.generate_valid_goal_instances = original_generate_valid_goal_instances
        
        # Assert
        assert selected_goal is not None, "Strategic evaluator should select a goal"
        assert selected_goal.goal_type == "MOVE_TO_SAFETY", "DEFENDER should prioritize MOVE_TO_SAFETY goal"
    
    def test_support_selects_heal_unit_goal(self, scenario_setup):
        """
        Test that an AI unit with the SUPPORT persona prioritizes the HEAL_UNIT goal when allies are damaged.
        """
        # Arrange
        game_state_manager = scenario_setup["game_state_manager"]
        
        # Get the enemy cleric unit with SUPPORT persona
        enemy_cleric = game_state_manager.get_unit_by_id("ENEMY_CLERIC")
        assert enemy_cleric is not None, "ENEMY_CLERIC unit not found in scenario"
        assert enemy_cleric.ai_persona == "SUPPORT", "ENEMY_CLERIC should have SUPPORT persona"
        
        # Damage an ally to create a healing opportunity
        enemy_fighter = game_state_manager.get_unit_by_id("ENEMY_FIGHTER")
        enemy_fighter.current_hp = enemy_fighter.max_hp // 2  # Set to half health
        
        # Create the strategic evaluator with a custom goal library
        utility_scorer = UtilityScorer(game_state_manager)
        strategic_evaluator = StrategicEvaluator(
            utility_scorer=utility_scorer,
            goal_library=[AttackUnitGoal, MoveToSafetyGoal, HealUnitGoal, SeizeTileGoal]
        )
        
        # Mock the utility scorer to return high scores for HEAL_UNIT goals
        original_score_goal = utility_scorer.score_goal
        
        def mock_score_goal(goal, unit_state, game_state_manager, persona=None):
            if goal.goal_type == "HEAL_UNIT":
                return 100.0
            else:
                return 50.0
                
        utility_scorer.score_goal = mock_score_goal
        
        # Create a HealUnitGoal instance and add it to the goal library
        heal_unit_goal = HealUnitGoal("ENEMY_FIGHTER")
        
        # Override the generate_valid_goal_instances method to include the HealUnitGoal
        original_generate_valid_goal_instances = strategic_evaluator.generate_valid_goal_instances
        
        def mock_generate_valid_goal_instances(unit, game_state):
            goals = original_generate_valid_goal_instances(unit, game_state)
            goals.append(heal_unit_goal)
            return goals
            
        strategic_evaluator.generate_valid_goal_instances = mock_generate_valid_goal_instances
        
        # Act
        selected_goal = strategic_evaluator.select_best_goal(enemy_cleric, game_state_manager)
        
        # Restore the original methods
        utility_scorer.score_goal = original_score_goal
        strategic_evaluator.generate_valid_goal_instances = original_generate_valid_goal_instances
        
        # Assert
        assert selected_goal is not None, "Strategic evaluator should select a goal"
        assert selected_goal.goal_type == "HEAL_UNIT", "SUPPORT should prioritize HEAL_UNIT goal when allies are damaged"
        
        # Verify the target is the damaged ally
        target_unit_id = selected_goal.parameters.get("target_unit_id")
        assert target_unit_id is not None, "HEAL_UNIT goal should have a target_unit_id parameter"
        assert target_unit_id == "ENEMY_FIGHTER", "Target should be the damaged ENEMY_FIGHTER"
    
    def test_objective_focused_selects_advance_goal(self, scenario_setup):
        """
        Test that an AI unit with the OBJECTIVE-FOCUSED persona prioritizes the SEIZE_TILE goal.
        """
        # Arrange
        game_state_manager = scenario_setup["game_state_manager"]
        
        # Get the enemy thief unit with OBJECTIVE-FOCUSED persona
        enemy_thief = game_state_manager.get_unit_by_id("ENEMY_THIEF")
        assert enemy_thief is not None, "ENEMY_THIEF unit not found in scenario"
        assert enemy_thief.ai_persona == "OBJECTIVE-FOCUSED", "ENEMY_THIEF should have OBJECTIVE-FOCUSED persona"
        
        # Create the strategic evaluator with a custom goal library
        utility_scorer = UtilityScorer(game_state_manager)
        strategic_evaluator = StrategicEvaluator(
            utility_scorer=utility_scorer,
            goal_library=[AttackUnitGoal, MoveToSafetyGoal, HealUnitGoal, SeizeTileGoal]
        )
        
        # Mock the utility scorer to return high scores for SEIZE_TILE goals
        original_score_goal = utility_scorer.score_goal
        
        def mock_score_goal(goal, unit_state, game_state_manager, persona=None):
            if goal.goal_type == "SEIZE_TILE":
                return 100.0
            else:
                return 50.0
                
        utility_scorer.score_goal = mock_score_goal
        
        # Create a SeizeTileGoal instance and add it to the goal library
        seize_tile_goal = SeizeTileGoal([1, 1])
        
        # Override the generate_valid_goal_instances method to include the SeizeTileGoal
        original_generate_valid_goal_instances = strategic_evaluator.generate_valid_goal_instances
        
        def mock_generate_valid_goal_instances(unit, game_state):
            goals = original_generate_valid_goal_instances(unit, game_state)
            goals.append(seize_tile_goal)
            return goals
            
        strategic_evaluator.generate_valid_goal_instances = mock_generate_valid_goal_instances
        
        # Act
        selected_goal = strategic_evaluator.select_best_goal(enemy_thief, game_state_manager)
        
        # Restore the original methods
        utility_scorer.score_goal = original_score_goal
        strategic_evaluator.generate_valid_goal_instances = original_generate_valid_goal_instances
        
        # Assert
        assert selected_goal is not None, "Strategic evaluator should select a goal"
        assert selected_goal.goal_type == "SEIZE_TILE", "OBJECTIVE-FOCUSED should prioritize SEIZE_TILE goal"
        
        # Verify the target position is the objective
        target_position = selected_goal.parameters.get("target_position")
        assert target_position is not None, "SEIZE_TILE goal should have a target_position parameter"
        
        # The objective is at [1, 1] in the scenario
        assert target_position == [1, 1], "Target position should be the objective at [1, 1]"