import pytest
import os
from unittest.mock import Mock, patch

from src.core_engine.scenario_loader import ScenarioLoader
from src.core_engine.data_provider import DataProvider


class TestScenarioLoader:
    """Test suite for the ScenarioLoader class."""
    
    @pytest.fixture
    def mock_data_provider(self):
        """Create a mock DataProvider for testing."""
        mock_provider = Mock(spec=DataProvider)
        
        # Set up the mock to return a sample scenario when load_scenario is called
        sample_scenario = {
            'id': 'test_scenario',
            'name': 'Test Scenario',
            'dimensions': [5, 5],
            'terrain_grid': [
                ['P', 'P', 'P', 'P', 'P'],
                ['P', 'F', 'F', 'F', 'P'],
                ['P', 'F', 'M', 'F', 'P'],
                ['P', 'F', 'F', 'F', 'P'],
                ['P', 'P', 'P', 'P', 'P']
            ],
            'placements': [
                {
                    'unit_id': 'PLAYER_UNIT',
                    'faction': 'PLAYER',
                    'position': [1, 1],
                    'level': 1,
                    'start_inventory': ['IRON_SWORD'],
                    'ai_persona': None
                },
                {
                    'unit_id': 'ENEMY_UNIT',
                    'faction': 'ENEMY',
                    'position': [3, 3],
                    'level': 1,
                    'start_inventory': ['IRON_LANCE'],
                    'ai_persona': 'AGGRESSOR'
                }
            ],
            'objectives': [
                {
                    'type': 'SEIZE',
                    'position': [2, 2],
                    'faction': 'PLAYER'
                }
            ]
        }
        
        mock_provider.load_scenario.return_value = sample_scenario
        return mock_provider
    
    def test_load_scenario(self, mock_data_provider):
        """Test loading a scenario."""
        # Arrange
        loader = ScenarioLoader(mock_data_provider)
        
        # Act
        scenario = loader.load_scenario('test_scenario')
        
        # Assert
        assert scenario is not None
        assert scenario['id'] == 'test_scenario'
        assert scenario['name'] == 'Test Scenario'
        assert scenario['dimensions'] == [5, 5]
        assert len(scenario['terrain_grid']) == 5
        assert len(scenario['placements']) == 2
        assert len(scenario['objectives']) == 1
        
        # Verify the mock was called correctly
        mock_data_provider.load_scenario.assert_called_once_with('test_scenario')
    
    def test_get_map_data(self, mock_data_provider):
        """Test extracting map data from a scenario."""
        # Arrange
        loader = ScenarioLoader(mock_data_provider)
        scenario = loader.load_scenario('test_scenario')
        
        # Act
        map_data = loader.get_map_data(scenario)
        
        # Assert
        assert map_data['id'] == 'test_scenario'
        assert map_data['name'] == 'Test Scenario'
        assert map_data['dimensions'] == [5, 5]
        assert len(map_data['terrain_grid']) == 5
    
    def test_get_unit_placements(self, mock_data_provider):
        """Test extracting unit placements from a scenario."""
        # Arrange
        loader = ScenarioLoader(mock_data_provider)
        scenario = loader.load_scenario('test_scenario')
        
        # Act
        placements = loader.get_unit_placements(scenario)
        
        # Assert
        assert len(placements) == 2
        assert placements[0]['unit_id'] == 'PLAYER_UNIT'
        assert placements[0]['faction'] == 'PLAYER'
        assert placements[1]['unit_id'] == 'ENEMY_UNIT'
        assert placements[1]['faction'] == 'ENEMY'
    
    def test_get_objectives(self, mock_data_provider):
        """Test extracting objectives from a scenario."""
        # Arrange
        loader = ScenarioLoader(mock_data_provider)
        scenario = loader.load_scenario('test_scenario')
        
        # Act
        objectives = loader.get_objectives(scenario)
        
        # Assert
        assert len(objectives) == 1
        assert objectives[0]['type'] == 'SEIZE'
        assert objectives[0]['position'] == [2, 2]
        assert objectives[0]['faction'] == 'PLAYER'
    
    def test_get_ai_personas(self, mock_data_provider):
        """Test extracting AI personas from a scenario."""
        # Arrange
        loader = ScenarioLoader(mock_data_provider)
        scenario = loader.load_scenario('test_scenario')
        
        # Act
        ai_personas = loader.get_ai_personas(scenario)
        
        # Assert
        assert len(ai_personas) == 1
        assert 'ENEMY_UNIT' in ai_personas
        assert ai_personas['ENEMY_UNIT'] == 'AGGRESSOR'
        assert 'PLAYER_UNIT' not in ai_personas
    
    def test_validate_scenario_data_valid(self, mock_data_provider):
        """Test validating valid scenario data."""
        # Arrange
        loader = ScenarioLoader(mock_data_provider)
        scenario = loader.load_scenario('test_scenario')
        
        # Act & Assert
        # This should not raise an exception
        loader._validate_scenario_data(scenario)
    
    def test_validate_scenario_data_invalid(self, mock_data_provider):
        """Test validating invalid scenario data."""
        # Arrange
        loader = ScenarioLoader(mock_data_provider)
        
        # Missing required fields
        invalid_scenario = {
            'id': 'invalid_scenario',
            'name': 'Invalid Scenario'
            # Missing dimensions and terrain_grid
        }
        
        # Act & Assert
        with pytest.raises(ValueError):
            loader._validate_scenario_data(invalid_scenario)
    
    def test_validate_scenario_data_mismatched_dimensions(self, mock_data_provider):
        """Test validating scenario data with mismatched dimensions."""
        # Arrange
        loader = ScenarioLoader(mock_data_provider)
        
        # Mismatched dimensions
        invalid_scenario = {
            'id': 'invalid_scenario',
            'name': 'Invalid Scenario',
            'dimensions': [3, 3],
            'terrain_grid': [
                ['P', 'P', 'P'],
                ['P', 'F', 'P']
                # Missing a row
            ]
        }
        
        # Act & Assert
        with pytest.raises(ValueError):
            loader._validate_scenario_data(invalid_scenario)