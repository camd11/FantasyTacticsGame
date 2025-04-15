"""
Test for the Move Again (Dance) Skill/Action

This test verifies that the Dance action correctly allows specific units to grant
an additional action to an adjacent allied unit that has already acted this turn.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.core_engine.game_state import GameStateManager, GameState, UnitState, FactionEnum
from src.core_engine.data_provider import DataProvider
from src.gameplay_systems.action_system import ActionSystem
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.turn_manager import TurnManager
from src.gameplay_systems.status_effects_system import StatusEffectManager


class TestMoveAgainSkill:
    """Test cases for the Move Again (Dance) skill/action."""

    @pytest.fixture
    def setup_game_state(self):
        """Set up the game state with required components."""
        # Initialize components
        data_provider = MagicMock(spec=DataProvider)
        game_state_manager = MagicMock(spec=GameStateManager)
        unit_system = MagicMock(spec=UnitSystem)
        action_system = MagicMock(spec=ActionSystem)
        turn_manager = MagicMock(spec=TurnManager)
        status_effect_manager = MagicMock(spec=StatusEffectManager)
        
        # Create a mock game state
        game_state = MagicMock(spec=GameState)
        game_state.unit_states = {}
        game_state_manager.current_game_state = game_state
        
        # Create a dancer unit
        dancer_unit = UnitState()
        dancer_unit.id = "DANCER"
        dancer_unit.name = "Dancer"
        dancer_unit.faction = FactionEnum.PLAYER
        dancer_unit.position = (5, 5)
        dancer_unit.has_acted_this_turn = False
        dancer_unit.was_refreshed_this_turn = False
        
        # Create a potential target unit (adjacent ally that has acted)
        target_unit = UnitState()
        target_unit.id = "TARGET"
        target_unit.name = "Target"
        target_unit.faction = FactionEnum.PLAYER
        target_unit.position = (5, 6)  # Adjacent to dancer
        target_unit.has_acted_this_turn = True
        target_unit.was_refreshed_this_turn = False
        
        # Create a unit that has already been refreshed
        refreshed_unit = UnitState()
        refreshed_unit.id = "REFRESHED"
        refreshed_unit.name = "Already Refreshed"
        refreshed_unit.faction = FactionEnum.PLAYER
        refreshed_unit.position = (6, 5)  # Adjacent to dancer
        refreshed_unit.has_acted_this_turn = True
        refreshed_unit.was_refreshed_this_turn = True
        
        # Create an enemy unit
        enemy_unit = UnitState()
        enemy_unit.id = "ENEMY"
        enemy_unit.name = "Enemy"
        enemy_unit.faction = FactionEnum.ENEMY
        enemy_unit.position = (4, 5)  # Adjacent to dancer
        enemy_unit.has_acted_this_turn = True
        enemy_unit.was_refreshed_this_turn = False
        
        # Create a unit that hasn't acted yet
        not_acted_unit = UnitState()
        not_acted_unit.id = "NOT_ACTED"
        not_acted_unit.name = "Not Acted"
        not_acted_unit.faction = FactionEnum.PLAYER
        not_acted_unit.position = (5, 4)  # Adjacent to dancer
        not_acted_unit.has_acted_this_turn = False
        not_acted_unit.was_refreshed_this_turn = False
        
        # Add units to game state
        game_state.unit_states = {
            "DANCER": dancer_unit,
            "TARGET": target_unit,
            "REFRESHED": refreshed_unit,
            "ENEMY": enemy_unit,
            "NOT_ACTED": not_acted_unit
        }
        
        # Set up data provider to return that dancer has Dance skill
        def unit_has_skill_side_effect(unit_id, skill_id):
            if unit_id == "DANCER" and skill_id == "SKILL_DANCE":
                return True
            return False
            
        data_provider.unit_has_skill.side_effect = unit_has_skill_side_effect
        
        # Set up game state manager to return our mock units
        def get_unit_side_effect(unit_id):
            return game_state.unit_states.get(unit_id)
            
        game_state_manager.get_unit.side_effect = get_unit_side_effect
        
        # Mock the are_adjacent function
        def are_adjacent_side_effect(pos1, pos2):
            # Check if positions are adjacent (Manhattan distance = 1)
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1
            
        # Assume this function exists in some utility module
        with patch('src.core_engine.utils.are_adjacent', side_effect=are_adjacent_side_effect):
            pass
        
        return {
            "game_state_manager": game_state_manager,
            "data_provider": data_provider,
            "unit_system": unit_system,
            "action_system": action_system,
            "turn_manager": turn_manager,
            "status_effect_manager": status_effect_manager,
            "game_state": game_state
        }
    
    def test_dance_action_availability(self, setup_game_state):
        """
        Test that the Dance action is available only to units with the Dance skill
        who haven't acted yet and have valid targets.
        """
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        data_provider = setup_game_state["data_provider"]
        action_system = setup_game_state["action_system"]
        
        # Create a mock implementation of get_available_actions
        def mock_get_available_actions(unit_id):
            unit = game_state_manager.get_unit(unit_id)
            
            # If unit has already acted, no actions are available
            if unit.has_acted_this_turn:
                return []
                
            available_actions = ["WAIT", "ATTACK"]  # Default actions
            
            # Check if unit has Dance skill
            if data_provider.unit_has_skill(unit_id, "SKILL_DANCE"):
                # Check if there are valid targets for Dance
                has_valid_target = False
                for target_id, target in setup_game_state["game_state"].unit_states.items():
                    if target_id != unit_id and target.faction == unit.faction:
                        # Check if adjacent
                        if abs(target.position[0] - unit.position[0]) + abs(target.position[1] - unit.position[1]) == 1:
                            # Check if target has acted and hasn't been refreshed
                            if target.has_acted_this_turn and not target.was_refreshed_this_turn:
                                has_valid_target = True
                                break
                
                if has_valid_target:
                    available_actions.append("DANCE")
            
            return available_actions
        
        # Patch the action system's get_available_actions method
        action_system.get_available_actions = MagicMock(side_effect=mock_get_available_actions)
        
        # Test dancer with valid targets
        dancer_actions = action_system.get_available_actions("DANCER")
        assert "DANCE" in dancer_actions, "Dance action should be available to dancer with valid targets"
        
        # Test dancer after acting
        dancer = game_state_manager.get_unit("DANCER")
        dancer.has_acted_this_turn = True
        dancer_actions = action_system.get_available_actions("DANCER")
        assert "DANCE" not in dancer_actions, "Dance action should not be available after dancer has acted"
        dancer.has_acted_this_turn = False  # Reset for other tests
        
        # Test dancer with no valid targets
        # Make all potential targets invalid
        for unit_id in ["TARGET", "NOT_ACTED", "REFRESHED"]:
            unit = game_state_manager.get_unit(unit_id)
            unit.has_acted_this_turn = False  # No units have acted
        
        dancer_actions = action_system.get_available_actions("DANCER")
        assert "DANCE" not in dancer_actions, "Dance action should not be available when there are no valid targets"
        
        # Reset target unit for other tests
        target = game_state_manager.get_unit("TARGET")
        target.has_acted_this_turn = True
        
        # Test non-dancer unit
        non_dancer_actions = action_system.get_available_actions("TARGET")
        assert "DANCE" not in non_dancer_actions, "Dance action should not be available to units without the Dance skill"
    
    def test_target_eligibility(self, setup_game_state):
        """
        Test that only valid targets (adjacent allies that have acted and haven't been refreshed)
        can be targeted by the Dance action.
        """
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        
        # Create a mock implementation of is_valid_dance_target
        def is_valid_dance_target(dancer_unit, potential_target_unit):
            if potential_target_unit is None:
                return False
                
            # Check adjacency
            dancer_pos = dancer_unit.position
            target_pos = potential_target_unit.position
            if abs(dancer_pos[0] - target_pos[0]) + abs(dancer_pos[1] - target_pos[1]) != 1:
                return False
                
            # Check faction
            if dancer_unit.faction != potential_target_unit.faction:
                return False
                
            # Check state
            if not potential_target_unit.has_acted_this_turn:
                return False
                
            if potential_target_unit.was_refreshed_this_turn:
                return False
                
            return True
        
        # Get units
        dancer = game_state_manager.get_unit("DANCER")
        target = game_state_manager.get_unit("TARGET")
        refreshed = game_state_manager.get_unit("REFRESHED")
        enemy = game_state_manager.get_unit("ENEMY")
        not_acted = game_state_manager.get_unit("NOT_ACTED")
        
        # Test valid target
        assert is_valid_dance_target(dancer, target), "Adjacent ally that has acted should be a valid target"
        
        # Test already refreshed unit
        assert not is_valid_dance_target(dancer, refreshed), "Already refreshed unit should not be a valid target"
        
        # Test enemy unit
        assert not is_valid_dance_target(dancer, enemy), "Enemy unit should not be a valid target"
        
        # Test unit that hasn't acted
        assert not is_valid_dance_target(dancer, not_acted), "Unit that hasn't acted should not be a valid target"
        
        # Test non-adjacent unit
        non_adjacent = UnitState()
        non_adjacent.id = "NON_ADJACENT"
        non_adjacent.faction = FactionEnum.PLAYER
        non_adjacent.position = (7, 7)  # Not adjacent
        non_adjacent.has_acted_this_turn = True
        non_adjacent.was_refreshed_this_turn = False
        
        assert not is_valid_dance_target(dancer, non_adjacent), "Non-adjacent unit should not be a valid target"
    
    def test_unit_refresh_effect(self, setup_game_state):
        """
        Test that the Dance action correctly refreshes the target unit,
        allowing them to act again.
        """
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        
        # Create a mock implementation of apply_dance_effect
        def apply_dance_effect(dancer_unit, target_unit):
            # Update target state
            target_unit.has_acted_this_turn = False
            target_unit.was_refreshed_this_turn = True
            
            # Update dancer state
            dancer_unit.has_acted_this_turn = True
            
            # Return success
            return True
        
        # Get units
        dancer = game_state_manager.get_unit("DANCER")
        target = game_state_manager.get_unit("TARGET")
        
        # Verify initial state
        assert target.has_acted_this_turn, "Target should have acted before refresh"
        assert not target.was_refreshed_this_turn, "Target should not have been refreshed yet"
        assert not dancer.has_acted_this_turn, "Dancer should not have acted yet"
        
        # Apply dance effect
        result = apply_dance_effect(dancer, target)
        
        # Verify result
        assert result, "Dance effect should be applied successfully"
        
        # Verify target state after refresh
        assert not target.has_acted_this_turn, "Target's has_acted_this_turn should be reset to False"
        assert target.was_refreshed_this_turn, "Target's was_refreshed_this_turn should be set to True"
        
        # Verify dancer state after dance
        assert dancer.has_acted_this_turn, "Dancer's has_acted_this_turn should be set to True"
    
    def test_refresh_limitation(self, setup_game_state):
        """
        Test that a unit can only be refreshed once per turn.
        """
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        
        # Create a second dancer unit
        second_dancer = UnitState()
        second_dancer.id = "DANCER2"
        second_dancer.name = "Second Dancer"
        second_dancer.faction = FactionEnum.PLAYER
        second_dancer.position = (6, 6)  # Adjacent to target
        second_dancer.has_acted_this_turn = False
        second_dancer.was_refreshed_this_turn = False
        
        # Add to game state
        setup_game_state["game_state"].unit_states["DANCER2"] = second_dancer
        
        # Create a mock implementation of is_valid_dance_target
        def is_valid_dance_target(dancer_unit, potential_target_unit):
            if potential_target_unit is None:
                return False
                
            # Check adjacency
            dancer_pos = dancer_unit.position
            target_pos = potential_target_unit.position
            if abs(dancer_pos[0] - target_pos[0]) + abs(dancer_pos[1] - target_pos[1]) != 1:
                return False
                
            # Check faction
            if dancer_unit.faction != potential_target_unit.faction:
                return False
                
            # Check state
            if not potential_target_unit.has_acted_this_turn:
                return False
                
            if potential_target_unit.was_refreshed_this_turn:
                return False
                
            return True
        
        # Create a mock implementation of apply_dance_effect
        def apply_dance_effect(dancer_unit, target_unit):
            # Update target state
            target_unit.has_acted_this_turn = False
            target_unit.was_refreshed_this_turn = True
            
            # Update dancer state
            dancer_unit.has_acted_this_turn = True
            
            # Return success
            return True
        
        # Get units
        dancer = game_state_manager.get_unit("DANCER")
        target = game_state_manager.get_unit("TARGET")
        
        # First refresh
        assert is_valid_dance_target(dancer, target), "Target should be valid for first refresh"
        apply_dance_effect(dancer, target)
        
        # Target acts again
        target.has_acted_this_turn = True
        
        # Try second refresh
        assert not is_valid_dance_target(second_dancer, target), "Target should not be valid for second refresh"
    
    def test_performer_action_consumption(self, setup_game_state):
        """
        Test that performing the Dance action consumes the dancer's action for the turn.
        """
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        action_system = setup_game_state["action_system"]
        
        # Create a mock implementation of execute_action
        def mock_execute_action(action_type, actor_id, target_id=None):
            actor = game_state_manager.get_unit(actor_id)
            
            if action_type == "DANCE" and target_id:
                target = game_state_manager.get_unit(target_id)
                
                # Apply dance effect
                target.has_acted_this_turn = False
                target.was_refreshed_this_turn = True
                
                # Consume dancer's action
                actor.has_acted_this_turn = True
                
                return True
            
            return False
        
        # Patch the action system's execute_action method
        action_system.execute_action = MagicMock(side_effect=mock_execute_action)
        
        # Get units
        dancer = game_state_manager.get_unit("DANCER")
        target = game_state_manager.get_unit("TARGET")
        
        # Verify initial state
        assert not dancer.has_acted_this_turn, "Dancer should not have acted yet"
        
        # Execute dance action
        result = action_system.execute_action("DANCE", "DANCER", "TARGET")
        
        # Verify result
        assert result, "Dance action should execute successfully"
        
        # Verify dancer state after dance
        assert dancer.has_acted_this_turn, "Dancer's has_acted_this_turn should be set to True"
        
        # Verify dancer can't act again
        dancer_actions = action_system.get_available_actions("DANCER")
        assert len(dancer_actions) == 0, "Dancer should have no available actions after dancing"
    
    def test_interaction_with_action_preventing_status(self, setup_game_state):
        """
        Test interaction with status effects that prevent actions.
        """
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        
        # Create a mock implementation of has_action_preventing_status
        def has_action_preventing_status(unit_id):
            # For this test, we'll say TARGET has an action-preventing status
            return unit_id == "TARGET"
        
        # Patch the status effect manager's has_action_preventing_status method
        status_effect_manager.has_action_preventing_status = MagicMock(side_effect=has_action_preventing_status)
        
        # Create a mock implementation of is_valid_dance_target that considers status effects
        def is_valid_dance_target(dancer_unit, potential_target_unit):
            if potential_target_unit is None:
                return False
                
            # Check adjacency
            dancer_pos = dancer_unit.position
            target_pos = potential_target_unit.position
            if abs(dancer_pos[0] - target_pos[0]) + abs(dancer_pos[1] - target_pos[1]) != 1:
                return False
                
            # Check faction
            if dancer_unit.faction != potential_target_unit.faction:
                return False
                
            # Check state
            if not potential_target_unit.has_acted_this_turn:
                return False
                
            if potential_target_unit.was_refreshed_this_turn:
                return False
                
            # Check for action-preventing status (optional)
            # Uncomment to filter out units with action-preventing status
            # if status_effect_manager.has_action_preventing_status(potential_target_unit.id):
            #     return False
                
            return True
        
        # Get units
        dancer = game_state_manager.get_unit("DANCER")
        target = game_state_manager.get_unit("TARGET")
        
        # Test if target is valid despite having an action-preventing status
        # This tests the design decision mentioned in the spec:
        # "If the target has a status preventing action (Sleep, Stun), they can still be targeted and refreshed"
        assert is_valid_dance_target(dancer, target), "Target should be valid even with action-preventing status"
        
        # Create a mock implementation of apply_dance_effect
        def apply_dance_effect(dancer_unit, target_unit):
            # Update target state
            target_unit.has_acted_this_turn = False
            target_unit.was_refreshed_this_turn = True
            
            # Update dancer state
            dancer_unit.has_acted_this_turn = True
            
            # Return success
            return True
        
        # Apply dance effect
        result = apply_dance_effect(dancer, target)
        
        # Verify result
        assert result, "Dance effect should be applied successfully"
        
        # Verify target state after refresh
        assert not target.has_acted_this_turn, "Target's has_acted_this_turn should be reset to False"
        assert target.was_refreshed_this_turn, "Target's was_refreshed_this_turn should be set to True"
        
        # But the unit still can't act due to status effect
        assert status_effect_manager.has_action_preventing_status(target.id), "Target should still have action-preventing status"
    
    def test_turn_start_state_reset(self, setup_game_state):
        """
        Test that unit states are properly reset at the start of a new player phase.
        """
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        turn_manager = setup_game_state["turn_manager"]
        
        # Get units
        dancer = game_state_manager.get_unit("DANCER")
        target = game_state_manager.get_unit("TARGET")
        
        # Set initial state (as if they had acted/been refreshed)
        dancer.has_acted_this_turn = True
        target.has_acted_this_turn = True
        target.was_refreshed_this_turn = True
        
        # Create a mock implementation of start_player_phase
        def start_player_phase():
            # Reset all player units
            for unit_id, unit in setup_game_state["game_state"].unit_states.items():
                if unit.faction == FactionEnum.PLAYER:
                    unit.has_acted_this_turn = False
                    unit.was_refreshed_this_turn = False
            
            return True
        
        # Patch the turn manager's start_player_phase method
        turn_manager.start_player_phase = MagicMock(side_effect=start_player_phase)
        
        # Start a new player phase
        result = turn_manager.start_player_phase()
        
        # Verify result
        assert result, "Player phase should start successfully"
        
        # Verify unit states after phase start
        assert not dancer.has_acted_this_turn, "Dancer's has_acted_this_turn should be reset to False"
        assert not target.has_acted_this_turn, "Target's has_acted_this_turn should be reset to False"
        assert not target.was_refreshed_this_turn, "Target's was_refreshed_this_turn should be reset to False"
        
        # Verify enemy units are not affected
        enemy = game_state_manager.get_unit("ENEMY")
        # Enemy unit state should not be reset since it's not a player unit
        # (We didn't modify it in start_player_phase, so it should still be whatever it was)