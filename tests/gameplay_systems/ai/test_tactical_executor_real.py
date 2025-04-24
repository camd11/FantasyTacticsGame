import sys
import os
import logging
import pytest
from unittest.mock import MagicMock, call
from typing import Tuple

# Add the current directory to the path to ensure src is importable
sys.path.append(os.path.abspath('.'))

# Import the real implementations directly
from src.gameplay_systems.ai.tactical_executor import TacticalExecutor
from src.gameplay_systems.ai.goals import SecurePositionGoal, Goal
from src.gameplay_systems.ai.ai_types import AIAction

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# ========== Fixtures ==========

@pytest.fixture
def mock_unit_state():
    """Provides a mock UnitState for secure position tests."""
    mock_unit = MagicMock()
    mock_unit.id = "secure_ai_unit_1"
    mock_unit.unit_id = "secure_ai_unit_1"
    mock_unit.position = (5, 5)
    mock_unit.movement_range = 3
    mock_unit.faction = "enemy"
    mock_unit.get_terrain_movement_cost = MagicMock(return_value=1)
    return mock_unit

@pytest.fixture
def mock_game_state_manager(mock_unit_state):
    """Provides a mock GameStateManager with basic setup for secure position tests."""
    mock_gsm = MagicMock()
    mock_gsm.current_game_state = MagicMock()
    mock_gsm.current_game_state.map_state = MagicMock()
    
    # Explicitly mock unit_positions, starting with only the AI unit
    mock_gsm.current_game_state.map_state.unit_positions = {
        mock_unit_state.position: mock_unit_state.id
    }
    
    # Mock get_unit_by_id to return the AI unit
    mock_gsm.get_unit_by_id.return_value = mock_unit_state
    
    # Set up mock data provider
    mock_data_provider = MagicMock()
    terrain_data = {
        'plains': {'defense_bonus': 0, 'avoid_bonus': 0, 'movement_cost': 1},
        'forest': {'defense_bonus': 1, 'avoid_bonus': 10, 'movement_cost': 2},
        'fort': {'defense_bonus': 2, 'avoid_bonus': 20, 'movement_cost': 1},
    }
    mock_data_provider.get_terrain_data.side_effect = lambda terrain_name: terrain_data.get(terrain_name)
    mock_gsm.data_provider = mock_data_provider
    
    # Mock map_system
    mock_gsm.map_system = MagicMock()
    mock_gsm.map_system.get_terrain_properties.return_value = {"defense_bonus": 1, "avoid_bonus": 0}
    mock_gsm.map_system.get_terrain_id_at = MagicMock(return_value="PLAINS")
    mock_gsm.map_system.get_movement_cost = MagicMock(return_value=1)
    
    # Mock pathfinder
    mock_gsm.pathfinding = MagicMock()
    mock_gsm.pathfinding.find_path.return_value = None
    mock_gsm.get_pathfinding.return_value = mock_gsm.pathfinding
    
    # Mock get_unit_at
    mock_gsm.get_unit_at = MagicMock(return_value=None)
    
    # Unit acted status
    mock_gsm.get_unit_acted_status = MagicMock(return_value=False)
    
    return mock_gsm

@pytest.fixture
def mock_movement_system(mock_game_state_manager):
    """Provides a mock MovementSystem linked to the secure GSM."""
    mock_ms = MagicMock()
    mock_ms.gameStateManager = mock_game_state_manager
    
    # Default reachable tiles for secure position tests
    mock_ms.calculate_movement_range.return_value = {
        (5, 5), (5, 6), (6, 5), (4, 5), (5, 4)
    }
    
    return mock_ms

@pytest.fixture
def mock_pathfinder(mock_game_state_manager):
    """Provides the mock PathfinderSystem already attached to mock_game_state_manager_secure."""
    return mock_game_state_manager.pathfinding

@pytest.fixture
def tactical_executor(mock_movement_system):
    """Provides a TacticalExecutor instance with mocks."""
    # Create a real TacticalExecutor
    executor = TacticalExecutor(
        movement_system=mock_movement_system,
        combat_system=None,
        healing_system=None
    )
    
    return executor

# ========== Tests ==========

def test_secure_position_goal_success(tactical_executor, mock_unit_state, mock_game_state_manager, mock_movement_system, mock_pathfinder):
    """Test securing a position when a better, reachable, unoccupied tile exists."""
    # Debug info
    print(f"\nDEBUG: TacticalExecutor class: {type(tactical_executor)}")
    print(f"DEBUG: Is TacticalExecutor from src: {tactical_executor.__class__.__module__ == 'src.gameplay_systems.ai.tactical_executor'}")
    
    # Create a SecurePositionGoal
    goal = SecurePositionGoal()
    print(f"DEBUG: Goal class: {type(goal)}")
    print(f"DEBUG: Goal type: {goal.goal_type}")
    print(f"DEBUG: Goal parameters: {goal.parameters}")
    
    ai_unit_state = mock_unit_state
    game_state_manager = mock_game_state_manager

    # --- Mocking Setup ---
    start_pos = ai_unit_state.position
    reachable_tiles = {
        (5, 5), (5, 6), (6, 5), (4, 5), (5, 4)
    }
    best_tile = (6, 5)
    path_to_best = [start_pos, best_tile]

    mock_movement_system.calculate_movement_range.return_value = reachable_tiles
    mock_pathfinder.find_path.return_value = path_to_best

    game_state_manager.map_system.get_terrain_properties.side_effect = lambda pos: {
        "defense_bonus": 2 if pos == best_tile else 1,
        "avoid_bonus": 0
    }

    # Explicitly set unit_positions with only the AI unit at start_pos
    game_state_manager.current_game_state.map_state.unit_positions = {
        start_pos: ai_unit_state.id
    }

    game_state_manager.get_unit_at.side_effect = lambda pos: ai_unit_state if pos == start_pos else None

    # --- Execution ---
    try:
        action = tactical_executor.determine_action_for_goal(goal, ai_unit_state, game_state_manager)
        print(f"DEBUG: Action result: {action}")
    except Exception as e:
        print(f"DEBUG: Exception during determine_action_for_goal: {e}")
        raise

    # --- Assertions ---
    assert action is not None
    assert action.action_type == "MOVE"
    assert action.unit_id == ai_unit_state.id
    assert action.target_data["path"] == path_to_best
    
    mock_movement_system.calculate_movement_range.assert_called_once_with(ai_unit_state.id)
    mock_pathfinder.find_path.assert_called_with(start_pos, best_tile, ai_unit_state.id)
    
    calls = [call(pos) for pos in reachable_tiles]
    game_state_manager.map_system.get_terrain_properties.assert_has_calls(calls, any_order=True)
    game_state_manager.get_unit_at.assert_any_call(best_tile)


def test_secure_position_goal_stay_put(tactical_executor, mock_unit_state, mock_game_state_manager, mock_movement_system):
    """Test securing a position when the current tile is the best."""
    goal = SecurePositionGoal()
    ai_unit_state = mock_unit_state
    game_state_manager = mock_game_state_manager

    # --- Mocking Setup ---
    start_pos = ai_unit_state.position
    reachable_tiles = {
        (5, 5), (5, 6), (6, 5), (4, 5), (5, 4)
    }

    mock_movement_system.calculate_movement_range.return_value = reachable_tiles
    
    game_state_manager.map_system.get_terrain_properties.side_effect = lambda pos: {
        "defense_bonus": 5 if pos == start_pos else 1,
        "avoid_bonus": 0
    }
    
    # Explicitly set unit_positions with only the AI unit at start_pos
    game_state_manager.current_game_state.map_state.unit_positions = {
        start_pos: ai_unit_state.id
    }
    
    game_state_manager.get_unit_at.side_effect = lambda pos: ai_unit_state if pos == start_pos else None

    # --- Execution ---
    action = tactical_executor.determine_action_for_goal(goal, ai_unit_state, game_state_manager)

    # --- Assertions ---
    assert action is not None
    assert action.action_type == "WAIT"
    assert action.unit_id == ai_unit_state.id
    
    mock_movement_system.calculate_movement_range.assert_called_once_with(ai_unit_state.id)
    
    calls = [call(pos) for pos in reachable_tiles]
    game_state_manager.map_system.get_terrain_properties.assert_has_calls(calls, any_order=True)


def test_secure_position_goal_move_to_best_occupied(tactical_executor, mock_unit_state, mock_game_state_manager, mock_movement_system, mock_pathfinder):
    """Test securing a position when the best tile is occupied, should choose the next best."""
    goal = SecurePositionGoal()
    ai_unit_state = mock_unit_state
    game_state_manager = mock_game_state_manager

    # --- Mocking Setup ---
    start_pos = ai_unit_state.position
    reachable_tiles = {
        (5, 5), (5, 6), (6, 5), (4, 5), (5, 4)
    }
    best_tile_occupied = (6, 5)
    next_best_tile_unoccupied = (5, 6)
    path_to_next_best = [start_pos, next_best_tile_unoccupied]

    mock_movement_system.calculate_movement_range.return_value = reachable_tiles
    mock_pathfinder.find_path.return_value = path_to_next_best
    
    game_state_manager.map_system.get_terrain_properties.side_effect = lambda pos: {
        "defense_bonus": 3 if pos == best_tile_occupied else (2 if pos == next_best_tile_unoccupied else 1),
        "avoid_bonus": 0
    }
    
    # Explicitly set unit_positions with AI unit at start_pos and another unit at best_tile
    other_unit_id = "other_unit_1"
    game_state_manager.current_game_state.map_state.unit_positions = {
        start_pos: ai_unit_state.id,
        best_tile_occupied: other_unit_id
    }
    
    mock_other_unit = MagicMock()
    mock_other_unit.id = other_unit_id
    mock_other_unit.unit_id = other_unit_id
    game_state_manager.get_unit_at.side_effect = lambda pos: (
        ai_unit_state if pos == start_pos else
        mock_other_unit if pos == best_tile_occupied else
        None
    )

    # --- Execution ---
    action = tactical_executor.determine_action_for_goal(goal, ai_unit_state, game_state_manager)

    # --- Assertions ---
    assert action is not None
    assert action.action_type == "MOVE"
    assert action.unit_id == ai_unit_state.id
    assert action.target_data["path"] == path_to_next_best
    
    mock_movement_system.calculate_movement_range.assert_called_once_with(ai_unit_state.id)
    mock_pathfinder.find_path.assert_called_with(start_pos, next_best_tile_unoccupied, ai_unit_state.id) 