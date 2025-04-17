"""
Scenario Loader Module

This module is responsible for loading and parsing scenario YAML files,
including map data, unit placements, and objectives.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple, Union

from src.core_engine.data_provider import DataProvider


class ScenarioLoader:
    """
    Loads and parses scenario YAML files for testing and gameplay.
    
    This class is responsible for loading scenario data from YAML files,
    parsing the data, and providing methods to set up the game state
    based on the loaded scenario.
    """
    
    def __init__(self, data_provider: Optional[DataProvider] = None):
        """
        Initialize the ScenarioLoader.
        
        Args:
            data_provider: Optional DataProvider instance. If not provided,
                           a new instance will be created.
        """
        self.data_provider = data_provider if data_provider else DataProvider()
        
    def load_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        Load a scenario from a YAML file.
        
        Args:
            scenario_name: The name of the scenario file (without extension)
            
        Returns:
            A dictionary containing the parsed scenario data
            
        Raises:
            FileNotFoundError: If the scenario file doesn't exist
            ValueError: If the scenario data is invalid
        """
        # Use the DataProvider to load the scenario data
        scenario_data = self.data_provider.load_scenario(scenario_name)
        
        if not scenario_data:
            raise FileNotFoundError(f"Scenario '{scenario_name}' not found")
        
        # Validate the scenario data
        self._validate_scenario_data(scenario_data)
        
        return scenario_data
    
    def _validate_scenario_data(self, scenario_data: Dict[str, Any]) -> None:
        """
        Validate the scenario data to ensure it has the required fields.
        
        Args:
            scenario_data: The scenario data to validate
            
        Raises:
            ValueError: If the scenario data is missing required fields
        """
        required_fields = ['id', 'name', 'dimensions', 'terrain_grid']
        
        for field in required_fields:
            if field not in scenario_data:
                raise ValueError(f"Scenario data is missing required field: {field}")
        
        # Validate terrain grid dimensions
        dimensions = scenario_data['dimensions']
        terrain_grid = scenario_data['terrain_grid']
        
        if len(terrain_grid) != dimensions[1]:
            raise ValueError(f"Terrain grid height ({len(terrain_grid)}) does not match dimensions[1] ({dimensions[1]})")
        
        for row in terrain_grid:
            if len(row) != dimensions[0]:
                raise ValueError(f"Terrain grid width ({len(row)}) does not match dimensions[0] ({dimensions[0]})")
    
    def get_map_data(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract map data from the scenario data.
        
        Args:
            scenario_data: The scenario data
            
        Returns:
            A dictionary containing the map data
        """
        return {
            'id': scenario_data['id'],
            'name': scenario_data['name'],
            'dimensions': scenario_data['dimensions'],
            'terrain_grid': scenario_data['terrain_grid']
        }
    
    def get_unit_placements(self, scenario_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract unit placements from the scenario data.
        
        Args:
            scenario_data: The scenario data
            
        Returns:
            A list of unit placement dictionaries
        """
        if 'placements' not in scenario_data:
            return []
        
        return scenario_data['placements']
    
    def get_objectives(self, scenario_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract objectives from the scenario data.
        
        Args:
            scenario_data: The scenario data
            
        Returns:
            A list of objective dictionaries
        """
        if 'objectives' not in scenario_data:
            return []
        
        return scenario_data['objectives']
    
    def get_ai_personas(self, scenario_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract AI personas from the scenario data.
        
        Args:
            scenario_data: The scenario data
            
        Returns:
            A dictionary mapping unit IDs to AI persona types (only includes units with non-None personas)
        """
        ai_personas = {}
        
        if 'placements' in scenario_data:
            for placement in scenario_data['placements']:
                if 'ai_persona' in placement and placement['ai_persona'] is not None:
                    ai_personas[placement['unit_id']] = placement['ai_persona']
        
        return ai_personas