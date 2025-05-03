"""
Chapter Loader Module

This module is responsible for loading and parsing chapter data files, including map layouts,
unit placements, objectives, events, and reinforcements. It validates the data and sets up
the game state accordingly.
"""

import os
import yaml
import logging
from typing import Dict, List, Tuple, Optional, Any, Union

from src.fantasy_tactics_core.data_provider import DataProvider
from src.fantasy_tactics_core.game_state import GameState, FactionEnum


class ChapterLoader:
    """
    Loads and processes chapter data files, initializing the game state with the chapter's
    map, units, objectives, events, and reinforcements.
    """
    
    def __init__(self, chapter_data_path: str, data_provider: DataProvider = None):
        """
        Initialize the ChapterLoader with a path to the chapter data file.
        
        Args:
            chapter_data_path: Path to the chapter data YAML file
            data_provider: Optional DataProvider instance for data validation
        """
        self.chapter_data_path = chapter_data_path
        self.data_provider = data_provider
        self.chapter_data = self.load_yaml_data(chapter_data_path)
        self.validate_chapter_data()
    
    def load_yaml_data(self, path: str) -> Dict:
        """
        Load YAML data from the specified file path.
        
        Args:
            path: Path to the YAML file
            
        Returns:
            Dictionary containing the loaded YAML data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the YAML is invalid
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Chapter data file not found: {path}")
        
        with open(path, 'r') as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as e:
                logging.error(f"Error parsing YAML file {path}: {str(e)}")
                raise
    
    def validate_chapter_data(self) -> None:
        """
        Validate the loaded chapter data for required fields and data integrity.
        
        Raises:
            ValueError: If required fields are missing or invalid
            FileNotFoundError: If referenced files don't exist
        """
        # Check for required keys
        required_keys = ['chapter_id', 'chapter_title', 'map_file', 'units', 'objectives']
        for key in required_keys:
            if key not in self.chapter_data:
                raise ValueError(f"Missing required key in chapter data: {key}")
        
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
        
        # Check if map file exists
        if not os.path.exists(self.chapter_data['map_file']):
            raise FileNotFoundError(f"Map file not found: {self.chapter_data['map_file']}")
        
        # Validate unit IDs if data_provider is available
        if self.data_provider:
            self._validate_unit_ids()
            self._validate_item_ids()
            self._validate_ai_archetypes()
            self._validate_event_data()
    
    def _validate_unit_ids(self) -> None:
        """
        Validate that all unit IDs in the chapter data exist in the data provider.
        
        Raises:
            ValueError: If a unit ID is not found in the data provider
        """
        for faction, units in self.chapter_data['units'].items():
            for unit in units:
                unit_id = unit['unit_id']
                if self.data_provider.get_unit_base_data(unit_id) is None:
                    raise ValueError(f"Unit ID not found in data provider: {unit_id}")
    
    def _validate_item_ids(self) -> None:
        """
        Validate that all item IDs in the chapter data exist in the data provider.
        
        Raises:
            ValueError: If an item ID is not found in the data provider
        """
        for faction, units in self.chapter_data['units'].items():
            for unit in units:
                if 'inventory' in unit:
                    for item_id in unit['inventory']:
                        if self.data_provider.get_item_data(item_id) is None:
                            raise ValueError(f"Item ID not found in data provider: {item_id}")
    
    def _validate_ai_archetypes(self) -> None:
        """
        Validate that all AI archetypes in the chapter data are supported.
        
        Raises:
            ValueError: If an AI archetype is not supported
        """
        # This is a placeholder. In a real implementation, we would check against
        # a list of supported AI archetypes from the data provider.
        supported_archetypes = [
            'aggressive_melee', 'stationary_ranged', 'civilian_flee', 'default_player'
        ]
        
        for faction, units in self.chapter_data['units'].items():
            for unit in units:
                if 'ai_archetype' in unit and unit['ai_archetype'] not in supported_archetypes:
                    raise ValueError(f"Unsupported AI archetype: {unit['ai_archetype']}")
    
    def _validate_event_data(self) -> None:
        """
        Validate event triggers and actions in the chapter data.
        
        Raises:
            ValueError: If an event trigger or action type is not supported
        """
        # Validate event triggers
        if 'event_triggers' in self.chapter_data:
            supported_trigger_types = [
                'turn_start', 'area_entered', 'talk_available', 'unit_defeated', 'village_visited'
            ]
            
            for trigger in self.chapter_data['event_triggers']:
                if 'type' not in trigger:
                    raise ValueError(f"Missing 'type' in event trigger: {trigger}")
                
                if trigger['type'] not in supported_trigger_types:
                    raise ValueError(f"Unsupported event trigger type: {trigger['type']}")
        
        # Validate event actions
        if 'events' in self.chapter_data:
            supported_action_types = [
                'spawn_reinforcements', 'show_dialogue', 'set_trigger_inactive',
                'enable_talk_option', 'drop_item_at', 'give_item_to_unit'
            ]
            
            for event in self.chapter_data['events']:
                if 'actions' not in event:
                    raise ValueError(f"Missing 'actions' in event: {event}")
                
                for action in event['actions']:
                    if 'type' not in action:
                        raise ValueError(f"Missing 'type' in event action: {action}")
                    
                    if action['type'] not in supported_action_types:
                        raise ValueError(f"Unsupported event action type: {action['type']}")
        
        # Validate reinforcement group references
        if 'events' in self.chapter_data and 'reinforcements' in self.chapter_data:
            reinforcement_groups = {group['group_id'] for group in self.chapter_data['reinforcements']}
            
            for event in self.chapter_data['events']:
                for action in event['actions']:
                    if action.get('type') == 'spawn_reinforcements' and 'group_id' in action:
                        if action['group_id'] not in reinforcement_groups:
                            raise ValueError(f"Referenced reinforcement group not found: {action['group_id']}")
    
    def setup_game_state(self, game_state: GameState) -> GameState:
        """
        Set up the game state with the chapter data.
        
        Args:
            game_state: The game state to set up
            
        Returns:
            The updated game state
        """
        # 1. Load Map
        map_data = self.load_map(self.chapter_data['map_file'])
        game_state.set_map(map_data)
        
        # 2. Place Units
        self.place_units(game_state, self.chapter_data['units'])
        
        # 3. Set Objectives
        game_state.set_objectives(self.chapter_data['objectives'])
        
        # 4. Register Events and Triggers
        event_manager = game_state.get_event_manager()
        if 'event_triggers' in self.chapter_data:
            event_manager.register_triggers(self.chapter_data['event_triggers'])
        
        if 'events' in self.chapter_data:
            event_manager.register_events(self.chapter_data['events'])
        
        # 5. Prepare Reinforcements
        game_state.set_reinforcement_definitions(self.chapter_data.get('reinforcements', []))
        
        return game_state
    
    def load_map(self, map_path: str) -> Any:
        """
        Load map data from the specified file path.
        
        Args:
            map_path: Path to the map file
            
        Returns:
            Map data object
        """
        # This is a placeholder. In a real implementation, we would load the map
        # data from the file, which could be in TMX, YAML, or another format.
        # For now, we'll just return a simple mock map data object.
        if self.data_provider:
            # If we have a data provider, use it to load the map
            chapter_id = self.chapter_data['chapter_id']
            return self.data_provider.get_map_data(chapter_id)
        else:
            # Create a simple mock map data object
            class MockMapData:
                def __init__(self, path):
                    self.id = os.path.basename(path).split('.')[0]
                    self.dimensions = (20, 20)  # Default dimensions
                    self.terrain_grid = [['P' for _ in range(20)] for _ in range(20)]  # All plains
            
            return MockMapData(map_path)
    
    def place_units(self, game_state: GameState, unit_definitions: Dict) -> None:
        """
        Place units on the map according to the unit definitions.
        
        Args:
            game_state: The game state to update
            unit_definitions: Dictionary of unit definitions by faction
        """
        # Convert unit definitions to a format expected by game_state.deploy_units
        unit_placements = []
        
        for faction_name, units in unit_definitions.items():
            faction = self._get_faction_enum(faction_name)
            
            for unit_def in units:
                placement = {
                    'unit_id': unit_def['unit_id'],
                    'faction': faction_name.upper(),  # Convert to uppercase for enum
                    'position': unit_def['position'],
                    'level': unit_def.get('level_override', 1),
                    'start_inventory': unit_def.get('inventory', []),
                    'starting_fatigue': 0,  # Default value
                    'needs_autolevel': False,  # Default value
                    'target_level': 1  # Default value
                }
                
                # Add class override if present
                if 'class_override' in unit_def:
                    placement['class_override'] = unit_def['class_override']
                
                # Add AI archetype if present
                if 'ai_archetype' in unit_def:
                    placement['ai_archetype'] = unit_def['ai_archetype']
                
                # Create a UnitPlacement-like object
                class UnitPlacement:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                unit_placements.append(UnitPlacement(placement))
        
        # Deploy the units
        if self.data_provider:
            game_state.deploy_units(unit_placements, self.data_provider)
    
    def _get_faction_enum(self, faction_name: str) -> FactionEnum:
        """
        Convert a faction name string to a FactionEnum value.
        
        Args:
            faction_name: The faction name as a string
            
        Returns:
            The corresponding FactionEnum value
        """
        faction_name = faction_name.upper()
        if faction_name == 'PLAYER':
            return FactionEnum.PLAYER
        elif faction_name == 'ENEMY':
            return FactionEnum.ENEMY
        elif faction_name == 'NPC':
            return FactionEnum.NPC
        else:
            logging.warning(f"Unknown faction name: {faction_name}, defaulting to PLAYER")
            return FactionEnum.PLAYER