"""
Terrain Effect System Module

This module is responsible for applying terrain effects to units, such as healing or damage,
at the appropriate time during the turn sequence.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional, Any

from src.core_engine.game_state import GameStateManager, FactionEnum
from src.core_engine.data_provider import DataProvider
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.unit_system import UnitSystem


class TerrainEffectSystem:
    """
    Manages the application of terrain effects to units during the turn sequence.
    """
    
    def __init__(self):
        """Initialize the TerrainEffectSystem."""
        self.gameStateManager = None
        self.dataProvider = None
        self.mapSystem = None
        self.unitSystem = None
    
    def initialize(self, gameStateManager_instance: GameStateManager, dataProvider_instance: DataProvider,
                  mapSystem_instance: MapSystem, unitSystem_instance: UnitSystem) -> None:
        """
        Initialize the TerrainEffectSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
            mapSystem_instance: Instance of the MapSystem
            unitSystem_instance: Instance of the UnitSystem
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        self.mapSystem = mapSystem_instance
        self.unitSystem = unitSystem_instance
        logging.info("TerrainEffectSystem initialized.")
    
    def process_turn_start_effects(self, faction: FactionEnum) -> Dict[str, Dict[str, int]]:
        """
        Process terrain effects at the start of a faction's turn.
        
        Args:
            faction: The faction whose turn is starting
            
        Returns:
            Dictionary mapping unit IDs to effect results (e.g., {'unit_id': {'heal': 2, 'damage': 0}})
        """
        results = {}
        
        # Get all units belonging to the current faction
        units = self.gameStateManager.get_units_by_faction(faction)
        
        for unit in units:
            # Skip units that are not active
            if unit.disposition != "ACTIVE":
                continue
            
            # Get terrain data at unit's position
            terrain_data = self.mapSystem.get_terrain_data_at(unit.position)
            if not terrain_data or not terrain_data.turn_effects:
                continue
            
            # Check if timing matches
            if terrain_data.turn_effects.get('timing') != "start_of_unit_turn":
                continue
            
            # Check if unit should ignore terrain effects
            if self._should_ignore_terrain_effects(unit, terrain_data):
                continue
            
            # Apply effects
            effect_results = self._apply_terrain_effects(unit, terrain_data)
            if effect_results:
                results[unit.id] = effect_results
        
        return results
    
    def process_turn_end_effects(self, faction: FactionEnum) -> Dict[str, Dict[str, int]]:
        """
        Process terrain effects at the end of a faction's turn.
        
        Args:
            faction: The faction whose turn is ending
            
        Returns:
            Dictionary mapping unit IDs to effect results (e.g., {'unit_id': {'heal': 2, 'damage': 0}})
        """
        results = {}
        
        # Get all units belonging to the current faction
        units = self.gameStateManager.get_units_by_faction(faction)
        
        for unit in units:
            # Skip units that are not active
            if unit.disposition != "ACTIVE":
                continue
            
            # Get terrain data at unit's position
            terrain_data = self.mapSystem.get_terrain_data_at(unit.position)
            if not terrain_data or not terrain_data.turn_effects:
                continue
            
            # Check if timing matches
            if terrain_data.turn_effects.get('timing') != "end_of_unit_turn":
                continue
            
            # Check if unit should ignore terrain effects
            if self._should_ignore_terrain_effects(unit, terrain_data):
                continue
            
            # Apply effects
            effect_results = self._apply_terrain_effects(unit, terrain_data)
            if effect_results:
                results[unit.id] = effect_results
        
        return results
    
    def _apply_terrain_effects(self, unit, terrain_data) -> Dict[str, int]:
        """
        Apply terrain effects to a unit.
        
        Args:
            unit: The unit to apply effects to
            terrain_data: The terrain data
            
        Returns:
            Dictionary of effect results (e.g., {'heal': 2, 'damage': 0})
        """
        results = {}
        
        # Apply healing
        if 'heal_percent' in terrain_data.turn_effects and terrain_data.turn_effects['heal_percent'] > 0:
            heal_amount = self._calculate_percent_heal(unit, terrain_data.turn_effects['heal_percent'])
            if heal_amount > 0:
                # Apply healing (capped at max HP)
                old_hp = unit.current_hp
                unit.current_hp = min(unit.max_hp, unit.current_hp + heal_amount)
                actual_heal = unit.current_hp - old_hp
                results['heal'] = actual_heal
                logging.info(f"Unit {unit.name} healed {actual_heal} HP from terrain effect.")
        
        # Apply damage
        if 'damage_percent' in terrain_data.turn_effects and terrain_data.turn_effects['damage_percent'] > 0:
            damage_amount = self._calculate_percent_damage(unit, terrain_data.turn_effects['damage_percent'])
            if damage_amount > 0:
                # Apply damage (capped at 1 HP)
                old_hp = unit.current_hp
                unit.current_hp = max(1, unit.current_hp - damage_amount)
                actual_damage = old_hp - unit.current_hp
                results['damage'] = actual_damage
                logging.info(f"Unit {unit.name} took {actual_damage} damage from terrain effect.")
        
        return results
    
    def _calculate_percent_heal(self, unit, percentage: int) -> int:
        """
        Calculate healing amount based on a percentage of max HP.
        
        Args:
            unit: The unit
            percentage: Percentage of max HP to heal
            
        Returns:
            Healing amount (at least 1 if percentage > 0)
        """
        if percentage <= 0:
            return 0
        
        heal_amount = max(1, int(unit.max_hp * (percentage / 100.0)))
        return heal_amount
    
    def _calculate_percent_damage(self, unit, percentage: int) -> int:
        """
        Calculate damage amount based on a percentage of max HP.
        
        Args:
            unit: The unit
            percentage: Percentage of max HP to damage
            
        Returns:
            Damage amount (at least 1 if percentage > 0)
        """
        if percentage <= 0:
            return 0
        
        damage_amount = max(1, int(unit.max_hp * (percentage / 100.0)))
        return damage_amount
    
    def _should_ignore_terrain_effects(self, unit, terrain_data) -> bool:
        """
        Check if a unit should ignore terrain effects.
        
        Args:
            unit: The unit
            terrain_data: The terrain data
            
        Returns:
            True if the unit should ignore terrain effects, False otherwise
        """
        # Check if unit's movement type is in the ignores_effects_by list
        if hasattr(unit, 'movement_type') and unit.movement_type in terrain_data.ignores_effects_by:
            return True
        
        # Check if unit is flying
        if hasattr(unit, 'is_flying') and unit.is_flying:
            return True
        
        # Check if unit is mounted (and not dismounted)
        if hasattr(unit, 'is_mounted') and unit.is_mounted:
            if not hasattr(unit, 'is_dismounted') or not unit.is_dismounted:
                return True
        
        return False