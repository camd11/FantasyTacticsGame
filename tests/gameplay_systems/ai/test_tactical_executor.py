import pytest
from unittest.mock import Mock, MagicMock, patch, call, ANY
from typing import Tuple, List, Dict, Any, Optional, Set, Union

# Add the project root to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import necessary modules and classes
# Placeholder classes if real implementation is not available
try:
    from src.gameplay_systems.ai.tactical_executor import TacticalExecutor
    from src.gameplay_systems.ai.goals import (
        AttackUnitGoal, HealUnitGoal, MoveToSafetyGoal, SeizeTileGoal,
        SecurePositionGoal, AdvanceToObjectiveGoal
    )
    from src.gameplay_systems.ai.ai_types import AIAction
    from src.utilities.position import Position # Import Position from its actual location
    from src.gameplay_systems.map_system import MapSystem, PathfindingAlgorithm # Re-add MapSystem import
    print("Using real implementation of TacticalExecutor and related classes")
    using_real_implementation = True
except ImportError:
    print("Falling back to placeholder classes due to import error")

# Dependencies to mock
from src.core_engine.game_state import GameStateManager, GameState, UnitState, MapState
from src.core_engine.data_provider import DataProvider
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.healing_system import HealingSystem

# Helper function to create a mock unit
def create_mock_unit(unit_id, position: Tuple[int, int], hp=20, max_hp=30, faction="ENEMY", mov=5, can_heal=False):
    mock_unit = MagicMock()  # Remove spec=UnitState
    mock_unit.id = unit_id
    mock_unit.unit_id = unit_id
    mock_unit.position = position
    mock_unit.current_hp = hp
    mock_unit.max_hp = max_hp
    mock_unit.faction = faction
    mock_unit.movement_range = mov # Used by some simple checks
    # Mock methods that might be called by the executor
    mock_unit.get_terrain_movement_cost.return_value = 1
    mock_unit.has_healing_capability.return_value = can_heal
    mock_unit.can_use_item.return_value = True # Assume can use items
    mock_unit.get_equipped_weapon_range.return_value = (1, 1) # Default range
    mock_unit.get_healing_range.return_value = (1, 1) # Default range
    return mock_unit

# Fixtures

@pytest.fixture
def mock_unit_state():
    """Provides a mock UnitState for tests."""
    return create_mock_unit("ai_unit_1", (5, 5), can_heal=True)

@pytest.fixture
def mock_game_state_manager():
    # ... existing setup ...
    # Setup map state with units
    mock_gsm.current_game_state.map_state.unit_positions = {
        (5, 5): "ai_unit_1", 
        (10, 10): "target_unit_1",
        (5, 6): "ally_unit_1" 
    }

    # Mock units
    mock_ai_unit = create_mock_unit("ai_unit_1", (5, 5), can_heal=True)
    mock_target_unit = create_mock_unit("target_unit_1", (10, 10), faction="PLAYER")
    mock_ally_unit = create_mock_unit("ally_unit_1", (5, 6), hp=5) # Injured ally

    # Mock get_unit_by_id and get_unit_at
    units = {u.id: u for u in [mock_ai_unit, mock_target_unit, mock_ally_unit]}
    mock_gsm.get_unit_by_id.side_effect = lambda unit_id: units.get(unit_id)
    mock_gsm.get_unit_at.side_effect = lambda pos: units.get(mock_gsm.current_game_state.map_state.unit_positions.get(pos))
    
    # Mock pathfinding
    mock_pathfinder = MagicMock(spec=PathfindingAlgorithm)
    mock_pathfinder.find_path.side_effect = lambda start, end, unit_id: [(5,5), (6,6), (7,7), (8,8), (9,9), end] if end==(10,10) else [(5,5), (5,4), (4,4)] if end==(4,4) else [(5,5), (5,6)]
    mock_pathfinder.find_path_to_attack_position.return_value = [(5,5), (6,6), (7,7), (8,8), (9,9)]
    mock_pathfinder.find_path_to_healing_position.return_value = [(5,5), (5,6)]
    mock_pathfinder.get_reachable_tiles.return_value = {(5, 5), (5, 6), (6, 5), (4, 5), (5, 4), (6,6)}
    mock_gsm.get_pathfinding.return_value = mock_pathfinder

    # Mock map system
    mock_map_system = MagicMock(spec=MapSystem)
    mock_map_system.get_terrain_properties.return_value = {"defense_bonus": 1, "avoid_bonus": 0}
    mock_map_system.get_terrain_id_at = MagicMock(return_value="PLAINS")
    mock_map_system.get_movement_cost = MagicMock(return_value=1)
    # Mock the pathfinder *attribute* of the map system
    mock_map_system.pathfinder = MagicMock(spec=PathfindingAlgorithm) 
    mock_map_system.pathfinder.find_path_to_nearest_attack_position = MagicMock(return_value=None)
    mock_map_system.pathfinder.find_path_towards_target = MagicMock(return_value=None)
    mock_map_system.pathfinder.reconstruct_path = MagicMock(return_value=None)
    mock_gsm.map_system = mock_map_system

    # Mock pathfinder separately if needed by other parts of the test
    # (Often GSM holds a pathfinder reference, or it's part of MapSystem)
    mock_pathfinder = MagicMock(spec=PathfindingAlgorithm)
    mock_pathfinder.find_path.return_value = None
    mock_gsm.pathfinding = mock_pathfinder
    mock_gsm.get_pathfinding.return_value = mock_pathfinder

    # Mock other GSM methods
    mock_gsm.find_safe_tiles_for_unit.return_value = [(4, 4)]
    mock_gsm.is_valid_position.return_value = True
    mock_gsm.get_units_within_range.return_value = [mock_target_unit] # For Attack
    mock_gsm.get_allies_within_range.return_value = [mock_ally_unit] # For Heal
    return mock_gsm

# ... other fixtures ...

# ============ Tests for determine_action_for_goal ============ 

# --- Secure Position --- 

@pytest.fixture
def mock_game_state_manager_secure(mock_unit_state):
    """Fixture specifically for secure position tests."""
    mock_gsm = MagicMock()  # Remove spec=GameStateManager
    mock_gsm.current_game_state = MagicMock()  # Remove spec=GameState
    mock_gsm.current_game_state.map_state = MagicMock()  # Remove spec=MapState
    mock_gsm.current_game_state.map_state.unit_positions = { (5, 5): "ai_unit_1" } # Start with only the AI unit
    mock_gsm.get_unit_by_id.return_value = mock_unit_state
    mock_gsm.get_unit_at.side_effect = lambda pos: mock_unit_state if pos == (5, 5) else None

    mock_pathfinder = MagicMock()  # Remove spec=PathfindingAlgorithm
    mock_gsm.get_pathfinding.return_value = mock_pathfinder

    mock_map_system = MagicMock()  # Remove spec=PathfindingAlgorithm
    mock_map_system.get_terrain_properties.return_value = {"defense_bonus": 1, "avoid_bonus": 0}
    mock_gsm.map_system = mock_map_system
    return mock_gsm

@pytest.fixture
def mock_movement_system_secure(mock_game_state_manager_secure):
    mock_ms = MagicMock()  # Remove spec=MovementSystem
    mock_ms.gameStateManager = mock_game_state_manager_secure
    mock_ms.calculate_movement_range.return_value = {(5, 5), (5, 6), (6, 5), (4, 5), (5, 4)}
    return mock_ms

@pytest.fixture
def tactical_executor_secure(mock_movement_system_secure):
    return TacticalExecutor(movement_system=mock_movement_system_secure)


def test_determine_action_for_secure_position_goal_move(
    tactical_executor_secure, mock_game_state_manager_secure, mock_movement_system_secure
):
    goal = SecurePositionGoal()
    ai_unit = mock_game_state_manager_secure.get_unit_by_id("ai_unit_1")
    
    # Mock: Best tile is (6, 5) with higher defense
    best_tile = (6, 5)
    mock_game_state_manager_secure.map_system.get_terrain_properties.side_effect = lambda pos: {"defense_bonus": 2, "avoid_bonus": 0} if pos == best_tile else {"defense_bonus": 1, "avoid_bonus": 0}
    mock_game_state_manager_secure.get_pathfinding().find_path.return_value = [(5, 5), best_tile]
    
    action = tactical_executor_secure.determine_action_for_goal(goal, ai_unit, mock_game_state_manager_secure)
    
    assert action is not None
    assert action.action_type == 'MOVE'
    assert action.target_data["path"] == [(5, 5), best_tile]

def test_determine_action_for_secure_position_goal_stay(
    tactical_executor_secure, mock_game_state_manager_secure, mock_movement_system_secure
):
    goal = SecurePositionGoal()
    ai_unit = mock_game_state_manager_secure.get_unit_by_id("ai_unit_1")
    start_pos = (5, 5)

    # Mock: Current tile (5, 5) is the best
    mock_game_state_manager_secure.map_system.get_terrain_properties.side_effect = lambda pos: {"defense_bonus": 3, "avoid_bonus": 0} if pos == start_pos else {"defense_bonus": 1, "avoid_bonus": 0}
    
    action = tactical_executor_secure.determine_action_for_goal(goal, ai_unit, mock_game_state_manager_secure)
    
    assert action is not None
    assert action.action_type == 'WAIT'
    assert action.unit_id == "ai_unit_1"

# --- Advance To Objective --- 

def test_determine_action_for_advance_to_objective_goal_move(
    tactical_executor, mock_game_state_manager
):
    goal = AdvanceToObjectiveGoal(target_position=(15, 15))
    ai_unit = mock_game_state_manager.get_unit_by_id("ai_unit_1")
    path_to_furthest = [(5, 5), (6, 6), (7, 7)] # Assume only part is reachable
    mock_game_state_manager.get_pathfinding().find_path.return_value = path_to_furthest # Mock _find_furthest_reachable...

    action = tactical_executor.determine_action_for_goal(goal, ai_unit, mock_game_state_manager)
    
    assert action is not None
    assert action.action_type == 'MOVE'
    assert action.target_data["path"] == path_to_furthest
    assert action.unit_id == "ai_unit_1"

def test_determine_action_for_advance_to_objective_goal_stay(
    tactical_executor, mock_game_state_manager
):
    goal = AdvanceToObjectiveGoal(target_position=(15, 15))
    ai_unit = mock_game_state_manager.get_unit_by_id("ai_unit_1")
    start_pos = (5, 5)

    # Mock: Current tile (5, 5) is the best
    mock_game_state_manager.map_system.get_terrain_properties.side_effect = lambda pos: {"defense_bonus": 3, "avoid_bonus": 0} if pos == start_pos else {"defense_bonus": 1, "avoid_bonus": 0}
    
    action = tactical_executor.determine_action_for_goal(goal, ai_unit, mock_game_state_manager)
    
    assert action is not None
    assert action.action_type == 'WAIT'
    assert action.unit_id == "ai_unit_1"

# --- Seize Tile --- 

def test_determine_action_for_seize_tile_goal_move(
    tactical_executor, mock_game_state_manager, mock_movement_system
):
    target_tile = (6, 6)
    goal = SeizeTileGoal(target_tile=target_tile)
    ai_unit = mock_game_state_manager.get_unit_by_id("ai_unit_1")
    path = [(5, 5), target_tile]

    # Mock movement system to say target is reachable
    mock_movement_system.can_move_to.return_value = True
    mock_movement_system.get_path.return_value = path

    action = tactical_executor.determine_action_for_goal(goal, ai_unit, mock_game_state_manager)
    
    assert action is not None
    assert action.action_type == 'MOVE'
    assert action.target_data["path"] == path
    assert action.unit_id == "ai_unit_1"

def test_determine_action_for_seize_tile_goal_seize(mock_tactical_executor_components):
    # ... existing code ...
    assert action is not None
    assert action.action_type == 'SEIZE'
    assert action.unit_id == "ai_unit_1"
    # ... other assertions ...

# --- Move To Safety --- 

def test_determine_action_for_move_to_safety_goal_move(
    tactical_executor, mock_game_state_manager
):
    goal = MoveToSafetyGoal()
    ai_unit = mock_game_state_manager.get_unit_by_id("ai_unit_1")
    safe_tile = (4, 4)
    path = [(5, 5), safe_tile]
    mock_game_state_manager.get_pathfinding().find_path.return_value = path

    action = tactical_executor.determine_action_for_goal(goal, ai_unit, mock_game_state_manager)
    
    assert action is not None
    assert action.action_type == 'MOVE'
    assert action.target_data["path"] == path
    assert action.unit_id == "ai_unit_1"

def test_determine_action_for_move_to_safety_goal(mock_tactical_executor_components):
    # ... existing code ...
    assert action is not None
    assert action.action_type == 'MOVE'
    assert action.unit_id == "ai_unit_1"
    # ... other assertions ...

# ... other goal tests ...
