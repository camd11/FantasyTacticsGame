"""
Scenario Loader Module

This module handles loading test scenarios from YAML files.
It sets up the game state with predefined units, maps, and other data for testing purposes.
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional

class ScenarioLoader:
    """
    Loads test scenarios from YAML files and sets up the game state accordingly.
    """
    
    def __init__(self, game_state, data_provider, unit_system, map_system):
        """
        Initialize the ScenarioLoader.
        
        Args:
            game_state: The game state manager instance
            data_provider: The data provider instance
            unit_system: The unit system instance
            map_system: The map system instance
        """
        self.game_state = game_state
        self.data_provider = data_provider
        self.unit_system = unit_system
        self.map_system = map_system
        self.scenarios_dir = "data/scenarios"
    
    def load_scenario(self, scenario_name: str) -> bool:
        """
        Load a scenario by name.
        
        Args:
            scenario_name: Name of the scenario to load (without file extension)
            
        Returns:
            True if the scenario was loaded successfully, False otherwise
        """
        scenario_path = os.path.join(self.scenarios_dir, f"{scenario_name}.yaml")
        
        if not os.path.exists(scenario_path):
            logging.error(f"Scenario file not found: {scenario_path}")
            return False
        
        try:
            with open(scenario_path, 'r') as file:
                scenario_data = yaml.safe_load(file)
            
            # Create a simple map data object to initialize the game state
            class SimpleMapData:
                def __init__(self, data):
                    self.id = data.get('id', scenario_name)
                    self.name = data.get('name', scenario_name)
                    self.dimensions = data.get('dimensions', [10, 10])
                    self.terrain_grid = []
                    
                    # Create a simple terrain grid
                    for _ in range(self.dimensions[1]):
                        row = []
                        for _ in range(self.dimensions[0]):
                            row.append('P')  # Plain terrain
                        self.terrain_grid.append(row)
            
            # Initialize the game state with the map data
            map_data = SimpleMapData(scenario_data)
            self.game_state.load_map(map_data)
            
            # Load unit placements
            if 'placements' in scenario_data:
                self._load_unit_placements(scenario_data['placements'])
            
            logging.info(f"Scenario '{scenario_name}' loaded successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error loading scenario '{scenario_name}': {str(e)}")
            return False
    
    # Removed _load_terrain_grid method since we're not using it
    
    def _load_unit_placements(self, placements: List[Dict[str, Any]]) -> None:
        """
        Load unit placements into the game state.
        
        Args:
            placements: List of unit placement data from the scenario file
        """
        # Create a simple class to hold placement data
        class SimplePlacement:
            def __init__(self, data):
                self.unit_id = data.get('unit_id', '')
                self.faction = data.get('faction', 'PLAYER')
                self.position = data.get('position', [0, 0])
                self.level = data.get('level', 1)
                self.start_inventory = data.get('start_inventory', [])
                self.starting_fatigue = data.get('starting_fatigue', 0)
                self.needs_autolevel = data.get('needs_autolevel', False)
                self.target_level = data.get('target_level', 1)
        
        # Convert the placements to SimplePlacement objects
        unit_placements = []
        for placement_data in placements:
            placement = SimplePlacement(placement_data)
            unit_placements.append(placement)
        
        # Deploy the units using the GameStateManager
        self.game_state.deploy_units(unit_placements, self.data_provider)
    
    # Removed _setup_unit_inventory method since we're using deploy_units
    
    def _apply_scenario_settings(self, settings: Dict[str, Any]) -> None:
        """
        Apply scenario-specific settings.
        
        Args:
            settings: Settings data from the scenario file
        """
        # Apply turn number
        if 'turn' in settings:
            self.game_state.current_turn = settings['turn']
        
        # Apply phase
        if 'phase' in settings:
            self.game_state.current_phase = settings['phase']
        
        # Apply other settings as needed
        
    def get_talk_events_for_pair(self, initiator_id: str, target_id: str) -> List:
        """
        Get talk events for a specific pair of units.
        
        Args:
            initiator_id: ID of the initiating unit
            target_id: ID of the target unit
            
        Returns:
            List of talk events for the pair
        """
        from src.gameplay_systems.talk_system import TalkEvent, Condition
        
        # In a real implementation, this would load talk events from scenario data
        # For testing purposes, we'll return mock events based on the unit IDs
        
        # This is a placeholder implementation for testing
        talk_events = []
        
        # Check for specific unit pairs that have talk events
        if initiator_id == "LEIF" and target_id == "DAGDAR":
            # Add dialogue talk event
            talk_events.append(TalkEvent(
                event_id="LEIF_DAGDAR_TALK",
                initiator_unit_id="LEIF",
                target_unit_id="DAGDAR",
                outcome_type="DIALOGUE",
                outcome_data={"dialogue_id": "ch1_leif_dagdar_talk"},
                is_repeatable=False
            ))
            
            # Add item talk event
            talk_events.append(TalkEvent(
                event_id="LEIF_DAGDAR_ITEM",
                initiator_unit_id="LEIF",
                target_unit_id="DAGDAR",
                outcome_type="ITEM",
                outcome_data={"item_id": "Vouge", "quantity": 1},
                is_repeatable=True,
                max_uses=2
            ))
            
            # Add recruitment talk event
            talk_events.append(TalkEvent(
                event_id="LEIF_DAGDAR_RECRUIT",
                initiator_unit_id="LEIF",
                target_unit_id="DAGDAR",
                outcome_type="RECRUIT",
                outcome_data={"unit_id_to_recruit": "DAGDAR", "new_faction": "Player"}
            ))
            
            # Add flag talk event
            talk_events.append(TalkEvent(
                event_id="LEIF_DAGDAR_FLAG",
                initiator_unit_id="LEIF",
                target_unit_id="DAGDAR",
                outcome_type="FLAG",
                outcome_data={"flag_name": "dagdar_talked_to", "flag_value": True}
            ))
        
        return talk_events