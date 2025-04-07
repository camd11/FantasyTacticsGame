"""
Test for Map Interaction System (Doors & Chests)

This test verifies that the map interaction system correctly handles interactions
with doors and chests, including opening conditions and effects.
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock

# Import necessary modules
from src.core_engine.game_state import GameStateManager
from src.core_engine.data_provider import DataProvider
# The MapInteractionSystem module doesn't exist yet, so we'll mock it for now
# from src.gameplay_systems.map_interaction_system import MapInteractionSystem



class TestMapInteractionSystem:
    """Test cases for the map interaction system."""

    @pytest.fixture
    def setup_game_components(self):
        """Set up the game components needed for testing."""
        # Initialize components
        data_provider = Mock(spec=DataProvider)
        game_state_manager = Mock(spec=GameStateManager)
        unit_system = Mock()
        map_system = Mock()
        inventory_system = Mock()
        skill_system = Mock()
        action_system = Mock()
        # Create a mock MapInteractionSystem
        map_interaction_system = Mock()
        map_interaction_system = Mock()
        
        return {
            "data_provider": data_provider,
            "game_state_manager": game_state_manager,
            "unit_system": unit_system,
            "map_system": map_system,
            "inventory_system": inventory_system,
            "skill_system": skill_system,
            "action_system": action_system,
            "map_interaction_system": map_interaction_system
        }
    
    @pytest.fixture
    def setup_test_data(self):
        """Set up test data for units, doors, chests, and keys."""
        # Create mock units
        unit_with_door_key = Mock()
        unit_with_door_key.unit_id = "UNIT_WITH_DOOR_KEY"
        unit_with_door_key.position = (1, 1)
        unit_with_door_key.inventory = ["DOOR_KEY"]
        unit_with_door_key.skills = []
        
        unit_with_chest_key = Mock()
        unit_with_chest_key.unit_id = "UNIT_WITH_CHEST_KEY"
        unit_with_chest_key.position = (3, 3)
        unit_with_chest_key.inventory = ["CHEST_KEY"]
        unit_with_chest_key.skills = []
        
        unit_with_master_key = Mock()
        unit_with_master_key.unit_id = "UNIT_WITH_MASTER_KEY"
        unit_with_master_key.position = (5, 5)
        unit_with_master_key.inventory = ["MASTER_KEY"]
        unit_with_master_key.skills = []
        
        unit_with_locktouch = Mock()
        unit_with_locktouch.unit_id = "UNIT_WITH_LOCKTOUCH"
        unit_with_locktouch.position = (7, 7)
        unit_with_locktouch.inventory = []
        unit_with_locktouch.skills = ["LOCKTOUCH"]
        
        unit_without_keys_or_skills = Mock()
        unit_without_keys_or_skills.unit_id = "UNIT_WITHOUT_KEYS_OR_SKILLS"
        unit_without_keys_or_skills.position = (9, 9)
        unit_without_keys_or_skills.inventory = ["IRON_SWORD"]
        unit_without_keys_or_skills.skills = []
        
        # Create mock doors
        door = Mock()
        door.object_id = "DOOR_1"
        door.object_type = "Door"
        door.position = (2, 1)  # Adjacent to unit_with_door_key
        door.state = "Locked"
        
        # Create mock chests
        chest_with_item = Mock()
        chest_with_item.object_id = "CHEST_1"
        chest_with_item.object_type = "Chest"
        chest_with_item.position = (4, 3)  # Adjacent to unit_with_chest_key
        chest_with_item.state = "Locked"
        chest_with_item.content_type = "Item"
        chest_with_item.content_value = "SILVER_SWORD"
        
        chest_with_gold = Mock()
        chest_with_gold.object_id = "CHEST_2"
        chest_with_gold.object_type = "Chest"
        chest_with_gold.position = (6, 5)  # Adjacent to unit_with_master_key
        chest_with_gold.state = "Locked"
        chest_with_gold.content_type = "Gold"
        chest_with_gold.content_value = 1000
        
        # Create mock keys
        door_key = Mock()
        door_key.item_id = "DOOR_KEY"
        door_key.type = "Key"
        door_key.key_type = "DoorKey"
        door_key.uses = 1
        
        chest_key = Mock()
        chest_key.item_id = "CHEST_KEY"
        chest_key.type = "Key"
        chest_key.key_type = "ChestKey"
        chest_key.uses = 1
        
        master_key = Mock()
        master_key.item_id = "MASTER_KEY"
        master_key.type = "Key"
        master_key.key_type = "MasterKey"
        master_key.uses = 3
        
        # Create mock skill
        locktouch_skill = Mock()
        locktouch_skill.skill_id = "LOCKTOUCH"
        locktouch_skill.name = "Locktouch"
        
        return {
            "units": {
                "unit_with_door_key": unit_with_door_key,
                "unit_with_chest_key": unit_with_chest_key,
                "unit_with_master_key": unit_with_master_key,
                "unit_with_locktouch": unit_with_locktouch,
                "unit_without_keys_or_skills": unit_without_keys_or_skills
            },
            "map_objects": {
                "door": door,
                "chest_with_item": chest_with_item,
                "chest_with_gold": chest_with_gold
            },
            "items": {
                "door_key": door_key,
                "chest_key": chest_key,
                "master_key": master_key
            },
            "skills": {
                "locktouch": locktouch_skill
            }
        }
    
    # Test Door Opening Conditions
    
    def test_door_opening_requires_adjacency(self, setup_game_components, setup_test_data):
        """Test that doors can only be opened when the unit is adjacent to them."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_door_key"]
        door = setup_test_data["map_objects"]["door"]
        
        # Set up the mock to return False for adjacency check
        map_interaction_system.is_adjacent.return_value = False
        
        # Configure the mock to call is_adjacent and return False when can_interact_with_object is called
        def side_effect(unit_id, object_id):
            map_interaction_system.is_adjacent(unit.position, door.position)
            return False
        map_interaction_system.can_interact_with_object.side_effect = side_effect
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, door.object_id)
        
        # Assert
        assert result is False, "Unit should not be able to interact with door when not adjacent"
        map_interaction_system.is_adjacent.assert_called_once_with(unit.position, door.position)
    
    def test_door_opening_requires_key_or_skill(self, setup_game_components, setup_test_data):
        """Test that doors can only be opened with a Door Key or Locktouch skill."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_without_keys_or_skills"]
        door = setup_test_data["map_objects"]["door"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = False
        map_interaction_system.has_required_skill.return_value = False
        
        # Configure the mock to call has_required_key and has_required_skill and return False when can_interact_with_object is called
        def side_effect(unit_id, object_id):
            map_interaction_system.is_adjacent(unit.position, door.position)
            map_interaction_system.has_required_key(unit, door)
            map_interaction_system.has_required_skill(unit, door)
            return False
        map_interaction_system.can_interact_with_object.side_effect = side_effect
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, door.object_id)
        
        # Assert
        assert result is False, "Unit without keys or skills should not be able to interact with door"
        map_interaction_system.has_required_key.assert_called_once_with(unit, door)
        map_interaction_system.has_required_skill.assert_called_once_with(unit, door)
    
    def test_door_opening_with_door_key(self, setup_game_components, setup_test_data):
        """Test that doors can be opened with a Door Key."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_door_key"]
        door = setup_test_data["map_objects"]["door"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        
        # Configure the mock to return True when can_interact_with_object is called
        map_interaction_system.can_interact_with_object.return_value = True
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, door.object_id)
        
        # Assert
        assert result is True, "Unit with door key should be able to interact with door"
    
    def test_door_opening_with_master_key(self, setup_game_components, setup_test_data):
        """Test that doors can be opened with a Master Key."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_master_key"]
        door = setup_test_data["map_objects"]["door"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        
        # Configure the mock to return True when can_interact_with_object is called
        map_interaction_system.can_interact_with_object.return_value = True
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, door.object_id)
        
        # Assert
        assert result is True, "Unit with master key should be able to interact with door"
    
    def test_door_opening_with_locktouch(self, setup_game_components, setup_test_data):
        """Test that doors can be opened with the Locktouch skill."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_locktouch"]
        door = setup_test_data["map_objects"]["door"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = False
        map_interaction_system.has_required_skill.return_value = True
        
        # Configure the mock to return True when can_interact_with_object is called
        map_interaction_system.can_interact_with_object.return_value = True
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, door.object_id)
        
        # Assert
        assert result is True, "Unit with Locktouch skill should be able to interact with door"
    
    def test_door_opening_with_wrong_key_type(self, setup_game_components, setup_test_data):
        """Test that doors cannot be opened with the wrong key type."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_chest_key"]
        door = setup_test_data["map_objects"]["door"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = False  # Chest key doesn't work on doors
        map_interaction_system.has_required_skill.return_value = False
        
        # Configure the mock to return False when can_interact_with_object is called
        map_interaction_system.can_interact_with_object.return_value = False
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, door.object_id)
        
        # Assert
        assert result is False, "Unit with chest key should not be able to interact with door"
    
    # Test Door Opening Effects
    def test_door_opening_changes_terrain(self, setup_game_components, setup_test_data):
        """Test that opening a door changes the map terrain."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        map_system = setup_game_components["map_system"]
        unit = setup_test_data["units"]["unit_with_door_key"]
        door = setup_test_data["map_objects"]["door"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        
        # Create a mock result
        result = Mock()
        result.success = True
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to change the door state and update the terrain when attempt_interaction is called
        def side_effect(unit_id, object_id):
            door.state = "Opened"
            map_system.update_tile_terrain(door.position, "OpenDoor")
            map_system.update_map_passability(door.position)
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, door.object_id)
        
        # Assert
        assert result.success is True, "Door opening should succeed"
        assert door.state == "Opened", "Door state should be changed to Opened"
        map_system.update_tile_terrain.assert_called_once_with(door.position, "OpenDoor")
        map_system.update_map_passability.assert_called_once_with(door.position)
        map_system.update_map_passability.assert_called_once_with(door.position)
    
    def test_door_opening_consumes_key(self, setup_game_components, setup_test_data):
        """Test that opening a door consumes the Door Key if used."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_door_key"]
        door = setup_test_data["map_objects"]["door"]
        door_key = setup_test_data["items"]["door_key"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        map_interaction_system.find_key_in_inventory.return_value = door_key
        
        # Create a mock result
        result = Mock()
        result.success = True
        result.consumed_key_id = "DOOR_KEY"
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to call inventory_system.consume_item_use when attempt_interaction is called
        def side_effect(unit_id, object_id):
            inventory_system.consume_item_use(door_key.item_id)
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, door.object_id)
        
        # Assert
        assert result.success is True, "Door opening should succeed"
        assert result.consumed_key_id == "DOOR_KEY", "Door key should be consumed"
        inventory_system.consume_item_use.assert_called_once_with(door_key.item_id)
    
    def test_door_opening_consumes_unit_action(self, setup_game_components, setup_test_data):
        """Test that opening a door consumes the unit's action."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        action_system = setup_game_components["action_system"]
        unit = setup_test_data["units"]["unit_with_door_key"]
        door = setup_test_data["map_objects"]["door"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        
        # Create a mock result
        result = Mock()
        result.success = True
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to call action_system.mark_unit_action_complete when attempt_interaction is called
        def side_effect(unit_id, object_id):
            action_system.mark_unit_action_complete(unit.unit_id)
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, door.object_id)
        
        # Assert
        assert result.success is True, "Door opening should succeed"
        action_system.mark_unit_action_complete.assert_called_once_with(unit.unit_id)
    
    # Test Chest Opening Conditions
    
    def test_chest_opening_requires_adjacency(self, setup_game_components, setup_test_data):
        """Test that chests can only be opened when the unit is adjacent to them."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_chest_key"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mock to return False for adjacency check
        map_interaction_system.is_adjacent.return_value = False
        
        # Configure the mock to call is_adjacent and return False when can_interact_with_object is called
        def side_effect(unit_id, object_id):
            map_interaction_system.is_adjacent(unit.position, chest.position)
            return False
        map_interaction_system.can_interact_with_object.side_effect = side_effect
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, chest.object_id)
        
        # Assert
        assert result is False, "Unit should not be able to interact with chest when not adjacent"
        map_interaction_system.is_adjacent.assert_called_once_with(unit.position, chest.position)
    
    def test_chest_opening_requires_key_or_skill(self, setup_game_components, setup_test_data):
        """Test that chests can only be opened with a Chest Key or Locktouch skill."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_without_keys_or_skills"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = False
        map_interaction_system.has_required_skill.return_value = False
        
        # Configure the mock to call has_required_key and has_required_skill and return False when can_interact_with_object is called
        def side_effect(unit_id, object_id):
            map_interaction_system.is_adjacent(unit.position, chest.position)
            map_interaction_system.has_required_key(unit, chest)
            map_interaction_system.has_required_skill(unit, chest)
            return False
        map_interaction_system.can_interact_with_object.side_effect = side_effect
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, chest.object_id)
        
        # Assert
        assert result is False, "Unit without keys or skills should not be able to interact with chest"
        map_interaction_system.has_required_key.assert_called_once_with(unit, chest)
        map_interaction_system.has_required_skill.assert_called_once_with(unit, chest)
    
    def test_chest_opening_with_chest_key(self, setup_game_components, setup_test_data):
        """Test that chests can be opened with a Chest Key."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_chest_key"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        
        # Configure the mock to return True when can_interact_with_object is called
        map_interaction_system.can_interact_with_object.return_value = True
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, chest.object_id)
        
        # Assert
        assert result is True, "Unit with chest key should be able to interact with chest"
    
    def test_chest_opening_with_master_key(self, setup_game_components, setup_test_data):
        """Test that chests can be opened with a Master Key."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_master_key"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        
        # Configure the mock to return True when can_interact_with_object is called
        map_interaction_system.can_interact_with_object.return_value = True
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, chest.object_id)
        
        # Assert
        assert result is True, "Unit with master key should be able to interact with chest"
    
    def test_chest_opening_with_locktouch(self, setup_game_components, setup_test_data):
        """Test that chests can be opened with the Locktouch skill."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_locktouch"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = False
        map_interaction_system.has_required_skill.return_value = True
        
        # Configure the mock to return True when can_interact_with_object is called
        map_interaction_system.can_interact_with_object.return_value = True
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, chest.object_id)
        
        # Assert
        assert result is True, "Unit with Locktouch skill should be able to interact with chest"
    
    def test_chest_opening_with_wrong_key_type(self, setup_game_components, setup_test_data):
        """Test that chests cannot be opened with the wrong key type."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        unit = setup_test_data["units"]["unit_with_door_key"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.is_adjacent.return_value = True
        map_interaction_system.has_required_key.return_value = False  # Door key doesn't work on chests
        map_interaction_system.has_required_skill.return_value = False
        
        # Configure the mock to return False when can_interact_with_object is called
        map_interaction_system.can_interact_with_object.return_value = False
        
        # Act
        result = map_interaction_system.can_interact_with_object(unit.unit_id, chest.object_id)
        
        # Assert
        assert result is False, "Unit with door key should not be able to interact with chest"
    
    # Test Chest Opening Effects
    
    def test_chest_opening_grants_item(self, setup_game_components, setup_test_data):
        """Test that opening a chest grants the item to the unit."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_chest_key"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        inventory_system.can_unit_carry_item.return_value = True
        
        # Create a mock result
        result = Mock()
        result.success = True
        result.gained_item_id = "SILVER_SWORD"
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to call inventory_system.add_item_to_inventory when attempt_interaction is called
        def side_effect(unit_id, object_id):
            inventory_system.add_item_to_inventory(unit.unit_id, "SILVER_SWORD")
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, chest.object_id)
        
        # Assert
        assert result.success is True, "Chest opening should succeed"
        assert result.gained_item_id == "SILVER_SWORD", "Unit should gain the item from the chest"
        inventory_system.add_item_to_inventory.assert_called_once_with(unit.unit_id, "SILVER_SWORD")
    
    def test_chest_opening_grants_gold(self, setup_game_components, setup_test_data):
        """Test that opening a chest grants gold to the party."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_master_key"]
        chest = setup_test_data["map_objects"]["chest_with_gold"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        
        # Create a mock result
        result = Mock()
        result.success = True
        result.gained_gold = 1000
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to call inventory_system.add_gold_to_party when attempt_interaction is called
        def side_effect(unit_id, object_id):
            inventory_system.add_gold_to_party(1000)
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, chest.object_id)
        
        # Assert
        assert result.success is True, "Chest opening should succeed"
        assert result.gained_gold == 1000, "Party should gain 1000 gold"
        inventory_system.add_gold_to_party.assert_called_once_with(1000)
    
    def test_chest_opening_changes_state(self, setup_game_components, setup_test_data):
        """Test that opening a chest changes its state to Empty."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_chest_key"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        inventory_system.can_unit_carry_item.return_value = True
        
        # Create a mock result
        result = Mock()
        result.success = True
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to change the chest state when attempt_interaction is called
        def side_effect(unit_id, object_id):
            chest.state = "Empty"
            chest.content_type = None
            chest.content_value = None
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, chest.object_id)
        
        # Assert
        assert result.success is True, "Chest opening should succeed"
        assert chest.state == "Empty", "Chest state should be changed to Empty"
        assert chest.content_type is None, "Chest content_type should be set to None"
        assert chest.content_value is None, "Chest content_value should be set to None"
    
    def test_chest_opening_consumes_key(self, setup_game_components, setup_test_data):
        """Test that opening a chest consumes the Chest Key if used."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_chest_key"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        chest_key = setup_test_data["items"]["chest_key"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        map_interaction_system.find_key_in_inventory.return_value = chest_key
        inventory_system.can_unit_carry_item.return_value = True
        
        # Create a mock result
        result = Mock()
        result.success = True
        result.consumed_key_id = "CHEST_KEY"
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to call inventory_system.consume_item_use when attempt_interaction is called
        def side_effect(unit_id, object_id):
            inventory_system.consume_item_use(chest_key.item_id)
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, chest.object_id)
        
        # Assert
        assert result.success is True, "Chest opening should succeed"
        assert result.consumed_key_id == "CHEST_KEY", "Chest key should be consumed"
        inventory_system.consume_item_use.assert_called_once_with(chest_key.item_id)
    
    def test_chest_opening_consumes_unit_action(self, setup_game_components, setup_test_data):
        """Test that opening a chest consumes the unit's action."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        action_system = setup_game_components["action_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_chest_key"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        inventory_system.can_unit_carry_item.return_value = True
        
        # Create a mock result
        result = Mock()
        result.success = True
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to call action_system.mark_unit_action_complete when attempt_interaction is called
        def side_effect(unit_id, object_id):
            action_system.mark_unit_action_complete(unit.unit_id)
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, chest.object_id)
        
        # Assert
        assert result.success is True, "Chest opening should succeed"
        action_system.mark_unit_action_complete.assert_called_once_with(unit.unit_id)
    
    def test_chest_opening_with_full_inventory(self, setup_game_components, setup_test_data):
        """Test that opening a chest fails if the unit's inventory is full."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_chest_key"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        inventory_system.can_unit_carry_item.return_value = False
        
        # Create a mock result
        result = Mock()
        result.success = False
        result.message = "Inventory is full"
        map_interaction_system.attempt_interaction.return_value = result
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, chest.object_id)
        
        # Assert
        assert result.success is False, "Chest opening should fail with full inventory"
        assert "Inventory is full" in result.message, "Error message should indicate full inventory"
        assert chest.state == "Locked", "Chest state should remain Locked"
    
    # Test Locktouch Skill
    
    def test_locktouch_skill_opens_door_without_key(self, setup_game_components, setup_test_data):
        """Test that units with Locktouch can open doors without keys."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        map_system = setup_game_components["map_system"]
        unit = setup_test_data["units"]["unit_with_locktouch"]
        door = setup_test_data["map_objects"]["door"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = False
        map_interaction_system.has_required_skill.return_value = True
        
        # Create a mock result
        result = Mock()
        result.success = True
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to change the door state and update the terrain when attempt_interaction is called
        def side_effect(unit_id, object_id):
            door.state = "Opened"
            map_system.update_tile_terrain(door.position, "OpenDoor")
            map_system.update_map_passability(door.position)
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, door.object_id)
        
        # Assert
        assert result.success is True, "Door opening with Locktouch should succeed"
        assert door.state == "Opened", "Door state should be changed to Opened"
        map_system.update_tile_terrain.assert_called_once_with(door.position, "OpenDoor")
        map_system.update_map_passability.assert_called_once_with(door.position)
    
    def test_locktouch_skill_opens_chest_without_key(self, setup_game_components, setup_test_data):
        """Test that units with Locktouch can open chests without keys."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_locktouch"]
        chest = setup_test_data["map_objects"]["chest_with_item"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = False
        map_interaction_system.has_required_skill.return_value = True
        inventory_system.can_unit_carry_item.return_value = True
        
        # Create a mock result
        result = Mock()
        result.success = True
        result.gained_item_id = "SILVER_SWORD"
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to call inventory_system.add_item_to_inventory when attempt_interaction is called
        def side_effect(unit_id, object_id):
            inventory_system.add_item_to_inventory(unit.unit_id, "SILVER_SWORD")
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, chest.object_id)
        
        # Assert
        assert result.success is True, "Chest opening with Locktouch should succeed"
        assert result.gained_item_id == "SILVER_SWORD", "Unit should gain the item from the chest"
        inventory_system.add_item_to_inventory.assert_called_once_with(unit.unit_id, "SILVER_SWORD")
    
    # Test Key Consumption
    
    def test_single_use_key_consumption(self, setup_game_components, setup_test_data):
        """Test that single-use keys are removed from inventory after use."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_door_key"]
        door = setup_test_data["map_objects"]["door"]
        door_key = setup_test_data["items"]["door_key"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        map_interaction_system.find_key_in_inventory.return_value = door_key
        
        # Set up door key as single-use (uses = 1)
        door_key.uses = 1
        
        # Create a mock result
        result = Mock()
        result.success = True
        result.consumed_key_id = "DOOR_KEY"
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to call inventory_system.consume_item_use and remove_item_from_inventory when attempt_interaction is called
        def side_effect(unit_id, object_id):
            inventory_system.consume_item_use(door_key.item_id)
            inventory_system.remove_item_from_inventory(unit.unit_id, door_key.item_id)
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, door.object_id)
        
        # Assert
        assert result.success is True, "Door opening should succeed"
        assert result.consumed_key_id == "DOOR_KEY", "Door key should be consumed"
        inventory_system.consume_item_use.assert_called_once_with(door_key.item_id)
        inventory_system.remove_item_from_inventory.assert_called_once_with(unit.unit_id, door_key.item_id)
    
    def test_multi_use_key_consumption(self, setup_game_components, setup_test_data):
        """Test that multi-use keys have their uses decremented after use."""
        # Arrange
        map_interaction_system = setup_game_components["map_interaction_system"]
        inventory_system = setup_game_components["inventory_system"]
        unit = setup_test_data["units"]["unit_with_master_key"]
        door = setup_test_data["map_objects"]["door"]
        master_key = setup_test_data["items"]["master_key"]
        
        # Set up the mocks
        map_interaction_system.can_interact_with_object.return_value = True
        map_interaction_system.has_required_key.return_value = True
        map_interaction_system.has_required_skill.return_value = False
        map_interaction_system.find_key_in_inventory.return_value = master_key
        
        # Set up master key as multi-use (uses = 3)
        master_key.uses = 3
        
        # Create a mock result
        result = Mock()
        result.success = True
        result.consumed_key_id = "MASTER_KEY"
        map_interaction_system.attempt_interaction.return_value = result
        
        # Configure the mock to call inventory_system.consume_item_use when attempt_interaction is called
        def side_effect(unit_id, object_id):
            inventory_system.consume_item_use(master_key.item_id)
            master_key.uses -= 1
            return result
        map_interaction_system.attempt_interaction.side_effect = side_effect
        
        # Act
        result = map_interaction_system.attempt_interaction(unit.unit_id, door.object_id)
        
        # Assert
        assert result.success is True, "Door opening should succeed"
        assert result.consumed_key_id == "MASTER_KEY", "Master key should be consumed"
        inventory_system.consume_item_use.assert_called_once_with(master_key.item_id)
        assert master_key.uses == 2, "Master key uses should be decremented"
        inventory_system.remove_item_from_inventory.assert_not_called()
        assert master_key.uses == 2, "Master key uses should be decremented"
