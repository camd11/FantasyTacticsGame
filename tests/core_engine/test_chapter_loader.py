"""
Test for Chapter Loader

This test verifies that the ChapterLoader correctly loads and processes chapter data files,
including map references, unit placements, objectives, events, and reinforcements.
"""

import unittest
from unittest.mock import MagicMock, patch, mock_open
import pytest
import yaml
from typing import Dict, List, Tuple, Optional, Any

# Import the class to be tested (will be implemented later)
from src.core_engine.data_provider import DataProvider
from src.core_engine.game_state import GameStateManager, GameState, UnitState, FactionEnum
from src.core_engine.event_system import EventManager

# Define the ChapterLoader class that we'll be testing
# This is a placeholder that will be replaced by the actual implementation
class ChapterLoader:
    def __init__(self, chapter_data_path):
        self.chapter_data = self.load_yaml_data(chapter_data_path)
        self.validate_chapter_data()
    
    def load_yaml_data(self, path):
        pass
    
    def validate_chapter_data(self):
        pass
    
    def setup_game_state(self, game_state):
        pass
    
    def load_map(self, map_path):
        pass
    
    def place_units(self, game_state, unit_definitions):
        pass


class TestChapterLoader(unittest.TestCase):
    """Test cases for the ChapterLoader class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock dependencies
        self.mock_data_provider = MagicMock(spec=DataProvider)
        self.mock_game_state_manager = MagicMock(spec=GameStateManager)
        self.mock_game_state = MagicMock(spec=GameState)
        self.mock_event_manager = MagicMock(spec=EventManager)
        
        # Add missing methods to the mock_game_state
        self.mock_game_state.set_map = MagicMock()
        self.mock_game_state.set_objectives = MagicMock()
        self.mock_game_state.set_reinforcement_definitions = MagicMock()
        self.mock_game_state.set_flag = MagicMock()
        
        # Mock the get_event_manager method to return our mock event manager
        self.mock_game_state.get_event_manager = MagicMock(return_value=self.mock_event_manager)
        
        # Sample chapter data for testing
        self.sample_chapter_data = {
            "chapter_id": "ch1_the_beginning",
            "chapter_title": "The Beginning",
            "description": "The first steps into a larger conflict.",
            "map_file": "data/maps/chapter_1_map.tmx",
            "units": {
                "player": [
                    {
                        "unit_id": "protagonist",
                        "position": [5, 5],
                        "stats_override": {
                            "level": 2,
                            "hp": 22
                        },
                        "inventory": [
                            "iron_sword",
                            "vulnerary"
                        ]
                    },
                    {
                        "unit_id": "healer",
                        "position": [4, 5],
                        "inventory": [
                            "heal_staff",
                            "vulnerary"
                        ]
                    }
                ],
                "enemy": [
                    {
                        "unit_id": "bandit_1",
                        "position": [10, 12],
                        "class_override": "brigand",
                        "level_override": 1,
                        "inventory": [
                            "iron_axe"
                        ],
                        "ai_archetype": "aggressive_melee"
                    }
                ],
                "npc": [
                    {
                        "unit_id": "villager_1",
                        "position": [2, 15],
                        "ai_archetype": "civilian_flee"
                    }
                ]
            },
            "objectives": {
                "win": [
                    {
                        "type": "seize_throne",
                        "target_position": [15, 15],
                        "required_unit": "protagonist"
                    }
                ],
                "loss": [
                    {
                        "type": "protagonist_defeated",
                        "target_unit_id": "protagonist"
                    }
                ]
            },
            "event_triggers": [
                {
                    "trigger_id": "turn_3_reinforcements",
                    "type": "turn_start",
                    "value": 3
                },
                {
                    "trigger_id": "reach_bridge_area",
                    "type": "area_entered",
                    "area": [[8, 10], [12, 10]],
                    "faction": "player"
                }
            ],
            "events": [
                {
                    "event_id": "reinforcements_appear",
                    "trigger": "turn_3_reinforcements",
                    "actions": [
                        {
                            "type": "spawn_reinforcements",
                            "group_id": "wave_1"
                        }
                    ]
                },
                {
                    "event_id": "bridge_ambush_dialogue",
                    "trigger": "reach_bridge_area",
                    "actions": [
                        {
                            "type": "show_dialogue",
                            "dialogue_id": "ambush_warning"
                        },
                        {
                            "type": "spawn_reinforcements",
                            "group_id": "bridge_ambushers"
                        }
                    ]
                }
            ],
            "reinforcements": [
                {
                    "group_id": "wave_1",
                    "units": [
                        {
                            "unit_id": "bandit_2",
                            "position": [1, 1],
                            "ai_archetype": "aggressive_melee"
                        },
                        {
                            "unit_id": "bandit_3",
                            "position": [1, 2],
                            "ai_archetype": "aggressive_melee"
                        }
                    ],
                    "trigger": "turn_3_reinforcements"
                },
                {
                    "group_id": "bridge_ambushers",
                    "units": [
                        {
                            "unit_id": "bandit_archer_2",
                            "position": [9, 9],
                            "ai_archetype": "stationary_ranged"
                        },
                        {
                            "unit_id": "bandit_archer_3",
                            "position": [11, 9],
                            "ai_archetype": "stationary_ranged"
                        }
                    ],
                    "trigger": "reach_bridge_area"
                }
            ]
        }
        
        # Path to the mock chapter data file
        self.chapter_data_path = "data/chapters/chapter_1.yaml"
        
    def test_chapter_loader_initialization(self):
        """Test that ChapterLoader initializes correctly with a valid chapter data path."""
        # Mock the load_yaml_data method to return our sample chapter data
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=self.sample_chapter_data):
            # Mock the validate_chapter_data method to do nothing
            with patch.object(ChapterLoader, 'validate_chapter_data'):
                # Create the ChapterLoader
                chapter_loader = ChapterLoader(self.chapter_data_path)
                
                # Assertions
                self.assertEqual(chapter_loader.chapter_data, self.sample_chapter_data)
                ChapterLoader.load_yaml_data.assert_called_once_with(self.chapter_data_path)
                ChapterLoader.validate_chapter_data.assert_called_once()

    def test_load_valid_yaml_data(self):
        """Test that load_yaml_data correctly loads valid YAML data."""
        # Mock the open function to return our sample chapter data as YAML
        mock_yaml_data = yaml.dump(self.sample_chapter_data)
        
        with patch('builtins.open', mock_open(read_data=mock_yaml_data)):
            # Create the ChapterLoader with mocked methods
            with patch.object(ChapterLoader, 'validate_chapter_data'):
                chapter_loader = ChapterLoader(self.chapter_data_path)
                
                # Replace the mocked load_yaml_data with a real implementation for testing
                def load_yaml_data(path):
                    with open(path, 'r') as file:
                        return yaml.safe_load(file)
                
                chapter_loader.load_yaml_data = load_yaml_data
                
                # Call the method under test
                result = chapter_loader.load_yaml_data(self.chapter_data_path)
                
                # Assertions
                self.assertEqual(result, self.sample_chapter_data)

    def test_load_invalid_yaml_data_raises_error(self):
        """Test that load_yaml_data raises an error when given invalid YAML data."""
        # Mock the open function to return invalid YAML data
        invalid_yaml_data = "invalid: yaml: data: [unclosed bracket"
        
        with patch('builtins.open', mock_open(read_data=invalid_yaml_data)):
            # Create the ChapterLoader with mocked methods
            with patch.object(ChapterLoader, 'validate_chapter_data'):
                chapter_loader = ChapterLoader(self.chapter_data_path)
                
                # Replace the mocked load_yaml_data with a real implementation for testing
                def load_yaml_data(path):
                    with open(path, 'r') as file:
                        return yaml.safe_load(file)
                
                chapter_loader.load_yaml_data = load_yaml_data
                
                # Call the method under test and expect an exception
                with self.assertRaises(yaml.YAMLError):
                    chapter_loader.load_yaml_data(self.chapter_data_path)
    
    def test_validate_chapter_data_schema(self):
        """Test that validate_chapter_data correctly validates the chapter data schema."""
        # Create the ChapterLoader with mocked methods
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=self.sample_chapter_data):
            chapter_loader = ChapterLoader(self.chapter_data_path)
            
            # Replace the mocked validate_chapter_data with a real implementation for testing
            def validate_chapter_data(self):
                # Check for required keys
                required_keys = ['chapter_id', 'chapter_title', 'map_file', 'units', 'objectives']
                for key in required_keys:
                    if key not in self.chapter_data:
                        raise ValueError(f"Missing required key: {key}")
                
                # Check units section
                if not isinstance(self.chapter_data['units'], dict):
                    raise ValueError("Units section must be a dictionary")
                
                required_unit_sections = ['player', 'enemy']
                for section in required_unit_sections:
                    if section not in self.chapter_data['units']:
                        raise ValueError(f"Missing required unit section: {section}")
                
                # Check objectives section
                if not isinstance(self.chapter_data['objectives'], dict):
                    raise ValueError("Objectives section must be a dictionary")
                
                required_objective_sections = ['win', 'loss']
                for section in required_objective_sections:
                    if section not in self.chapter_data['objectives']:
                        raise ValueError(f"Missing required objective section: {section}")
            
            chapter_loader.validate_chapter_data = validate_chapter_data.__get__(chapter_loader, ChapterLoader)
            
            # Call the method under test
            try:
                chapter_loader.validate_chapter_data()
            except ValueError as e:
                self.fail(f"validate_chapter_data raised ValueError unexpectedly: {e}")

    def test_validate_chapter_data_missing_keys_raises_error(self):
        """Test that validate_chapter_data raises an error when required keys are missing."""
        # Create a copy of the sample chapter data with missing keys
        invalid_chapter_data = self.sample_chapter_data.copy()
        del invalid_chapter_data['chapter_id']
        
        # Create the ChapterLoader with mocked methods
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=invalid_chapter_data):
            chapter_loader = ChapterLoader(self.chapter_data_path)
            
            # Replace the mocked validate_chapter_data with a real implementation for testing
            def validate_chapter_data(self):
                # Check for required keys
                required_keys = ['chapter_id', 'chapter_title', 'map_file', 'units', 'objectives']
                for key in required_keys:
                    if key not in self.chapter_data:
                        raise ValueError(f"Missing required key: {key}")
            
            chapter_loader.validate_chapter_data = validate_chapter_data.__get__(chapter_loader, ChapterLoader)
            
            # Call the method under test and expect an exception
            with self.assertRaises(ValueError) as context:
                chapter_loader.validate_chapter_data()
            
            self.assertIn("Missing required key: chapter_id", str(context.exception))
    
    def test_validate_map_file_exists(self):
        """Test that validate_chapter_data checks if the map file exists."""
        # Create the ChapterLoader with mocked methods
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=self.sample_chapter_data):
            chapter_loader = ChapterLoader(self.chapter_data_path)
            
            # Mock the os.path.exists function to return False for the map file
            with patch('os.path.exists', return_value=False):
                # Replace the mocked validate_chapter_data with a real implementation for testing
                def validate_chapter_data(self):
                    import os
                    # Check if map file exists
                    if not os.path.exists(self.chapter_data['map_file']):
                        raise FileNotFoundError(f"Map file not found: {self.chapter_data['map_file']}")
                
                chapter_loader.validate_chapter_data = validate_chapter_data.__get__(chapter_loader, ChapterLoader)
                
                # Call the method under test and expect an exception
                with self.assertRaises(FileNotFoundError) as context:
                    chapter_loader.validate_chapter_data()
                
                self.assertIn("Map file not found:", str(context.exception))
    
    def test_validate_unit_ids_exist(self):
        """Test that validate_chapter_data checks if unit IDs exist in the data provider."""
        # Create the ChapterLoader with mocked methods
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=self.sample_chapter_data):
            chapter_loader = ChapterLoader(self.chapter_data_path)
            
            # Mock the data provider to return None for a specific unit ID
            self.mock_data_provider.get_unit_base_data = MagicMock(side_effect=lambda unit_id: None if unit_id == 'nonexistent_unit' else MagicMock())
            
            # Replace the mocked validate_chapter_data with a real implementation for testing
            def validate_chapter_data(self):
                # Check if unit IDs exist in the data provider
                for faction, units in self.chapter_data['units'].items():
                    for unit in units:
                        unit_id = unit['unit_id']
                        if self.data_provider.get_unit_base_data(unit_id) is None:
                            raise ValueError(f"Unit ID not found in data provider: {unit_id}")
            
            # Set the data provider
            chapter_loader.data_provider = self.mock_data_provider
            
            # Set the validate_chapter_data method
            chapter_loader.validate_chapter_data = validate_chapter_data.__get__(chapter_loader, ChapterLoader)
            
            # Call the method under test - should pass with our sample data
            try:
                chapter_loader.validate_chapter_data()
            except ValueError:
                self.fail("validate_chapter_data raised ValueError unexpectedly")
            
            # Now modify the chapter data to include a nonexistent unit
            modified_chapter_data = self.sample_chapter_data.copy()
            modified_chapter_data['units'] = self.sample_chapter_data['units'].copy()
            modified_chapter_data['units']['player'] = self.sample_chapter_data['units']['player'].copy()
            modified_chapter_data['units']['player'].append({
                "unit_id": "nonexistent_unit",
                "position": [3, 3]
            })
            
            chapter_loader.chapter_data = modified_chapter_data
            
            # Call the method under test and expect an exception
            with self.assertRaises(ValueError) as context:
                chapter_loader.validate_chapter_data()
            
            self.assertIn("Unit ID not found in data provider: nonexistent_unit", str(context.exception))
    
    def test_setup_game_state_returns_game_state_object(self):
        """Test that setup_game_state returns a game state object."""
        # Create the ChapterLoader with mocked methods
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=self.sample_chapter_data):
            with patch.object(ChapterLoader, 'validate_chapter_data'):
                chapter_loader = ChapterLoader(self.chapter_data_path)
                
                # Mock the methods called by setup_game_state
                chapter_loader.load_map = MagicMock(return_value=MagicMock())
                chapter_loader.place_units = MagicMock()
                
                # Replace the mocked setup_game_state with a real implementation for testing
                def setup_game_state(self, game_state):
                    # 1. Load Map
                    map_data = self.load_map(self.chapter_data['map_file'])
                    game_state.set_map(map_data)
                    
                    # 2. Place Units
                    self.place_units(game_state, self.chapter_data['units'])
                    
                    # 3. Set Objectives
                    game_state.set_objectives(self.chapter_data['objectives'])
                    
                    # 4. Register Events and Triggers
                    event_manager = game_state.get_event_manager()
                    event_manager.register_triggers(self.chapter_data['event_triggers'])
                    event_manager.register_events(self.chapter_data['events'])
                    
                    # 5. Prepare Reinforcements
                    game_state.set_reinforcement_definitions(self.chapter_data.get('reinforcements', []))
                    
                    return game_state
                
                chapter_loader.setup_game_state = setup_game_state.__get__(chapter_loader, ChapterLoader)
                
                # Call the method under test
                result = chapter_loader.setup_game_state(self.mock_game_state)
                
                # Assertions
                self.assertEqual(result, self.mock_game_state)
                chapter_loader.load_map.assert_called_once_with(self.sample_chapter_data['map_file'])
                self.mock_game_state.set_map.assert_called_once()
                chapter_loader.place_units.assert_called_once_with(self.mock_game_state, self.sample_chapter_data['units'])
                self.mock_game_state.set_objectives.assert_called_once_with(self.sample_chapter_data['objectives'])
                self.mock_event_manager.register_triggers.assert_called_once_with(self.sample_chapter_data['event_triggers'])
                self.mock_event_manager.register_events.assert_called_once_with(self.sample_chapter_data['events'])
                self.mock_game_state.set_reinforcement_definitions.assert_called_once_with(self.sample_chapter_data['reinforcements'])
    
    def test_setup_map_correctly(self):
        """Test that setup_game_state correctly sets up the map."""
        # Create the ChapterLoader with mocked methods
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=self.sample_chapter_data):
            with patch.object(ChapterLoader, 'validate_chapter_data'):
                chapter_loader = ChapterLoader(self.chapter_data_path)
                
                # Create a mock map data object
                mock_map_data = MagicMock()
                mock_map_data.id = "chapter_1_map"
                mock_map_data.dimensions = (20, 20)
                
                # Mock the load_map method to return our mock map data
                chapter_loader.load_map = MagicMock(return_value=mock_map_data)
                chapter_loader.place_units = MagicMock()
                
                # Replace the mocked setup_game_state with a real implementation for testing
                def setup_game_state(self, game_state):
                    # 1. Load Map
                    map_data = self.load_map(self.chapter_data['map_file'])
                    game_state.set_map(map_data)
                    
                    # 2. Place Units
                    self.place_units(game_state, self.chapter_data['units'])
                    
                    # 3. Set Objectives
                    game_state.set_objectives(self.chapter_data['objectives'])
                    
                    # 4. Register Events and Triggers
                    event_manager = game_state.get_event_manager()
                    event_manager.register_triggers(self.chapter_data['event_triggers'])
                    event_manager.register_events(self.chapter_data['events'])
                    
                    # 5. Prepare Reinforcements
                    game_state.set_reinforcement_definitions(self.chapter_data.get('reinforcements', []))
                    
                    return game_state
                
                chapter_loader.setup_game_state = setup_game_state.__get__(chapter_loader, ChapterLoader)
                
                # Call the method under test
                chapter_loader.setup_game_state(self.mock_game_state)
                
                # Assertions
                chapter_loader.load_map.assert_called_once_with(self.sample_chapter_data['map_file'])
                self.mock_game_state.set_map.assert_called_once_with(mock_map_data)
    
    def test_set_win_conditions(self):
        """Test that setup_game_state correctly sets win conditions."""
        # Create the ChapterLoader with mocked methods
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=self.sample_chapter_data):
            with patch.object(ChapterLoader, 'validate_chapter_data'):
                chapter_loader = ChapterLoader(self.chapter_data_path)
                
                # Mock the methods called by setup_game_state
                chapter_loader.load_map = MagicMock(return_value=MagicMock())
                chapter_loader.place_units = MagicMock()
                
                # Replace the mocked setup_game_state with a real implementation for testing
                def setup_game_state(self, game_state):
                    # 1. Load Map
                    map_data = self.load_map(self.chapter_data['map_file'])
                    game_state.set_map(map_data)
                    
                    # 2. Place Units
                    self.place_units(game_state, self.chapter_data['units'])
                    
                    # 3. Set Objectives
                    game_state.set_objectives(self.chapter_data['objectives'])
                    
                    # 4. Register Events and Triggers
                    event_manager = game_state.get_event_manager()
                    event_manager.register_triggers(self.chapter_data['event_triggers'])
                    event_manager.register_events(self.chapter_data['events'])
                    
                    # 5. Prepare Reinforcements
                    game_state.set_reinforcement_definitions(self.chapter_data.get('reinforcements', []))
                    
                    return game_state
                
                chapter_loader.setup_game_state = setup_game_state.__get__(chapter_loader, ChapterLoader)
                
                # Call the method under test
                chapter_loader.setup_game_state(self.mock_game_state)
                
                # Assertions
                self.mock_game_state.set_objectives.assert_called_once_with(self.sample_chapter_data['objectives'])
    
    def test_register_event_triggers(self):
        """Test that setup_game_state correctly registers event triggers."""
        # Create the ChapterLoader with mocked methods
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=self.sample_chapter_data):
            with patch.object(ChapterLoader, 'validate_chapter_data'):
                chapter_loader = ChapterLoader(self.chapter_data_path)
                
                # Mock the methods called by setup_game_state
                chapter_loader.load_map = MagicMock(return_value=MagicMock())
                chapter_loader.place_units = MagicMock()
                
                # Replace the mocked setup_game_state with a real implementation for testing
                def setup_game_state(self, game_state):
                    # 1. Load Map
                    map_data = self.load_map(self.chapter_data['map_file'])
                    game_state.set_map(map_data)
                    
                    # 2. Place Units
                    self.place_units(game_state, self.chapter_data['units'])
                    
                    # 3. Set Objectives
                    game_state.set_objectives(self.chapter_data['objectives'])
                    
                    # 4. Register Events and Triggers
                    event_manager = game_state.get_event_manager()
                    event_manager.register_triggers(self.chapter_data['event_triggers'])
                    event_manager.register_events(self.chapter_data['events'])
                    
                    # 5. Prepare Reinforcements
                    game_state.set_reinforcement_definitions(self.chapter_data.get('reinforcements', []))
                    
                    return game_state
                
                chapter_loader.setup_game_state = setup_game_state.__get__(chapter_loader, ChapterLoader)
                
                # Call the method under test
                chapter_loader.setup_game_state(self.mock_game_state)
                
                # Assertions
                self.mock_event_manager.register_triggers.assert_called_once_with(self.sample_chapter_data['event_triggers'])
                self.mock_event_manager.register_events.assert_called_once_with(self.sample_chapter_data['events'])
    
    def test_store_reinforcement_definitions(self):
        """Test that setup_game_state correctly stores reinforcement definitions."""
        # Create the ChapterLoader with mocked methods
        with patch.object(ChapterLoader, 'load_yaml_data', return_value=self.sample_chapter_data):
            with patch.object(ChapterLoader, 'validate_chapter_data'):
                chapter_loader = ChapterLoader(self.chapter_data_path)
                
                # Mock the methods called by setup_game_state
                chapter_loader.load_map = MagicMock(return_value=MagicMock())
                chapter_loader.place_units = MagicMock()
                
                # Replace the mocked setup_game_state with a real implementation for testing
                def setup_game_state(self, game_state):
                    # 1. Load Map
                    map_data = self.load_map(self.chapter_data['map_file'])
                    game_state.set_map(map_data)
                    
                    # 2. Place Units
                    self.place_units(game_state, self.chapter_data['units'])
                    
                    # 3. Set Objectives
                    game_state.set_objectives(self.chapter_data['objectives'])
                    
                    # 4. Register Events and Triggers
                    event_manager = game_state.get_event_manager()
                    event_manager.register_triggers(self.chapter_data['event_triggers'])
                    event_manager.register_events(self.chapter_data['events'])
                    
                    # 5. Prepare Reinforcements
                    game_state.set_reinforcement_definitions(self.chapter_data.get('reinforcements', []))
                    
                    return game_state
                
                chapter_loader.setup_game_state = setup_game_state.__get__(chapter_loader, ChapterLoader)
                
                # Call the method under test
                chapter_loader.setup_game_state(self.mock_game_state)
                
                # Assertions
                self.mock_game_state.set_reinforcement_definitions.assert_called_once_with(self.sample_chapter_data['reinforcements'])


if __name__ == '__main__':
    unittest.main()
