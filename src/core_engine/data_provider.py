"""
Data Provider Module

This module is responsible for loading and providing access to all static game data.
It abstracts the data source (YAML/JSON files) from the rest of the engine.
"""

import os
import yaml
import json
import random # Added import
import logging
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Union

# Enums
class StatEnum(Enum):
    HP = auto()
    STR = auto()
    MAG = auto()
    SKL = auto()
    SPD = auto()
    LUK = auto()
    DEF = auto()
    CON = auto()
    MOV = auto()
    MOV_STARS = auto()  # Movement stars

class WeaponTypeEnum(Enum):
    SWORD = auto()
    LANCE = auto()
    AXE = auto()
    BOW = auto()
    FIRE = auto()
    THUNDER = auto()
    WIND = auto()
    LIGHT = auto()
    DARK = auto()
    STAFF = auto()

class RankEnum(Enum):
    E = 1
    D = 2
    C = 3
    B = 4
    A = 5
    S = 6

class ItemTypeEnum(Enum):
    WEAPON = auto()
    STAFF = auto()
    CONSUMABLE = auto()
    SCROLL = auto()
    KEY = auto()

class MovementTypeEnum(Enum):
    INFANTRY = auto()
    CAVALRY = auto()
    ARMORED = auto()
    FLYING = auto()
    MAGE = auto()

class TerrainTypeEnum(Enum):
    PLAIN = auto()
    FOREST = auto()
    MOUNTAIN = auto()
    RIVER = auto()
    SEA = auto()
    BRIDGE = auto()
    ROAD = auto()
    WALL = auto()
    DOOR = auto()
    HOUSE = auto()
    CASTLE = auto()
    GATE = auto()
    THRONE = auto()
    VILLAGE = auto()
    RUINS = auto()
    INVALID = auto()

class BonusTypeEnum(Enum):
    DEF = auto()
    AVO = auto()

# Constants
IMPASSABLE = 99  # Value to represent impassable terrain

# Data Structures
class UnitBaseData:
    """Represents the static data for a unit/character."""
    def __init__(self, data_dict: Dict):
        self.id = data_dict.get('id', '')
        self.name = data_dict.get('name', '')
        self.base_class_id = data_dict.get('base_class_id', '')
        self.stats = data_dict.get('stats', {})
        self.growths = data_dict.get('growths', {})
        self.base_weapon_ranks = data_dict.get('base_weapon_ranks', {})
        self.skills = data_dict.get('skills', [])
        self.leadership_stars = data_dict.get('leadership_stars', 0)
        self.pcc = data_dict.get('pcc', 0)  # Pursuit Critical Coefficient

class ItemData:
    """Represents the static data for an item."""
    def __init__(self, data_dict: Dict):
        self.id = data_dict.get('id', '')
        self.name = data_dict.get('name', '')
        self.type = data_dict.get('type', ItemTypeEnum.CONSUMABLE)
        self.weapon_type = data_dict.get('weapon_type', None)
        self.might = data_dict.get('might', 0)
        self.hit = data_dict.get('hit', 0)
        self.crit = data_dict.get('crit', 0)
        self.weight = data_dict.get('weight', 0)
        self.range_min = data_dict.get('range_min', 1)
        self.range_max = data_dict.get('range_max', 1)
        self.max_durability = data_dict.get('max_durability', 0)
        self.required_rank = data_dict.get('required_rank', RankEnum.E)
        self.effects = data_dict.get('effects', [])

class ClassData:
    """Represents the static data for a class."""
    def __init__(self, data_dict: Dict):
        self.id = data_dict.get('id', '')
        self.name = data_dict.get('name', '')
        self.base_stats = data_dict.get('base_stats', {})
        self.max_stats = data_dict.get('max_stats', {})
        self.max_weapon_ranks = data_dict.get('max_weapon_ranks', {})
        # Convert movement_type string to MovementTypeEnum
        movement_type_string = data_dict.get('movement_type', 'INFANTRY')
        try:
            self.movement_type = MovementTypeEnum[movement_type_string]
        except (KeyError, TypeError) as e:
            logging.error(f"Invalid movement type '{movement_type_string}' for class {data_dict.get('id', 'unknown')}: {str(e)}")
            self.movement_type = MovementTypeEnum.INFANTRY
        self.promotion_options = data_dict.get('promotion_options', {})
        self.class_skills = data_dict.get('class_skills', [])
        self.dismount_class_id = data_dict.get('dismount_class_id', None)

class TerrainData:
    """Represents the static data for a terrain type."""
    def __init__(self, data_dict: Dict):
        self.type = data_dict.get('type', TerrainTypeEnum.PLAIN)
        self.name = data_dict.get('name', '')
        self.movement_costs = data_dict.get('movement_costs', {})
        self.bonuses = data_dict.get('bonuses', {})
        self.is_healing = data_dict.get('is_healing', False)
        self.is_indoor = data_dict.get('is_indoor', False)

class MapData:
    """Represents the static data for a map layout."""
    def __init__(self, data_dict: Dict):
        self.id = data_dict.get('id', '')
        self.name = data_dict.get('name', '')
        self.dimensions = data_dict.get('dimensions', (0, 0))
        self.terrain_grid = data_dict.get('terrain_grid', [])
        self.seize_point = data_dict.get('seize_point', None)
        self.escape_points = data_dict.get('escape_points', [])

class UnitPlacement:
    """Represents the placement of a unit on a map."""
    def __init__(self, data_dict: Dict):
        self.unit_id = data_dict.get('unit_id', '')
        self.faction = data_dict.get('faction', '')
        self.position = data_dict.get('position', (0, 0))
        self.level = data_dict.get('level', 1)
        self.start_inventory = data_dict.get('start_inventory', [])
        self.starting_fatigue = data_dict.get('starting_fatigue', 0)
        self.needs_autolevel = data_dict.get('needs_autolevel', False)
        self.target_level = data_dict.get('target_level', 1)

class SupportRelation:
    """Represents a support relationship between two units."""
    def __init__(self, data_dict: Dict):
        self.unit_id = data_dict.get('unit_id', '')
        self.partner_id = data_dict.get('partner_id', '')
        self.bonus = data_dict.get('bonus', 0)

class SkillData:
    """Represents the static data for a skill."""
    def __init__(self, data_dict: Dict):
        self.id = data_dict.get('id', '')
        self.name = data_dict.get('name', '')
        self.description = data_dict.get('description', '')
        self.effects = data_dict.get('effects', [])

class PromotionGains:
    """Represents the stat and rank changes for a promotion path."""
    def __init__(self, data_dict: Dict):
        self.base_class_id = data_dict.get('base_class_id', '')
        self.promoted_class_id = data_dict.get('promoted_class_id', '')
        self.stat_gains = data_dict.get('stat_gains', {})
        self.rank_gains = data_dict.get('rank_gains', {})

class DataProvider:
    """
    Provides access to all static game data.
    Loads data from YAML/JSON files and provides interfaces to access it.
    """
    
    def __init__(self):
        self._unit_data: Dict[str, UnitBaseData] = {}
        self._item_data: Dict[str, ItemData] = {}
        self._class_data: Dict[str, ClassData] = {}
        self._terrain_data: Dict[str, TerrainData] = {}
        self._map_layouts: Dict[str, MapData] = {}
        self._unit_placements: Dict[str, List[UnitPlacement]] = {}
        self._event_scripts: Dict[str, List] = {}
        self._support_relations: Dict[str, List[SupportRelation]] = {}
        self._promotion_data: Dict[str, PromotionGains] = {}
        self._skill_data: Dict[str, SkillData] = {}
        
        # Weapon triangle data (could be loaded from file but hardcoded for simplicity)
        self._weapon_triangle = {
            WeaponTypeEnum.SWORD: {WeaponTypeEnum.AXE: 5, WeaponTypeEnum.LANCE: -5},
            WeaponTypeEnum.AXE: {WeaponTypeEnum.LANCE: 5, WeaponTypeEnum.SWORD: -5},
            WeaponTypeEnum.LANCE: {WeaponTypeEnum.SWORD: 5, WeaponTypeEnum.AXE: -5},
            WeaponTypeEnum.FIRE: {WeaponTypeEnum.WIND: 5, WeaponTypeEnum.THUNDER: -5},
            WeaponTypeEnum.WIND: {WeaponTypeEnum.THUNDER: 5, WeaponTypeEnum.FIRE: -5},
            WeaponTypeEnum.THUNDER: {WeaponTypeEnum.FIRE: 5, WeaponTypeEnum.WIND: -5},
            WeaponTypeEnum.LIGHT: {WeaponTypeEnum.FIRE: 5, WeaponTypeEnum.THUNDER: 5, WeaponTypeEnum.WIND: 5},
            WeaponTypeEnum.DARK: {WeaponTypeEnum.FIRE: 5, WeaponTypeEnum.THUNDER: 5, WeaponTypeEnum.WIND: 5},
        }
    
    def load_all_data(self, data_directory: str) -> bool:
        """
        Load all static game data from the specified directory.
        
        Args:
            data_directory: Path to the directory containing data files
            
        Returns:
            bool: True if data was loaded successfully, False otherwise
        """
        try:
            logging.info(f"Loading static data from {data_directory}")
            
            # Load unit data
            self._unit_data = self._load_data_to_objects(
                os.path.join(data_directory, "units.yaml"),
                UnitBaseData
            )
            
            # Load item data
            self._item_data = self._load_data_to_objects(
                os.path.join(data_directory, "items.yaml"),
                ItemData
            )
            
            # Load class data
            self._class_data = self._load_data_to_objects(
                os.path.join(data_directory, "classes.yaml"),
                ClassData
            )
            
            # Load terrain data
            self._terrain_data = self._load_data_to_objects(
                os.path.join(data_directory, "terrain.yaml"),
                TerrainData
            )
            
            # Initialize empty collections for map data, placements, and events
            # These will be loaded on demand by get_map_data, get_unit_placements, and get_event_scripts
            self._map_layouts = {}
            self._unit_placements = {}
            self._event_scripts = {}
            
            # Load support relations
            self._support_relations = self._load_data_to_objects(
                os.path.join(data_directory, "supports.yaml"), 
                SupportRelation,
                is_list=True
            )
            
            # Load promotion data
            self._promotion_data = self._load_data_to_objects(
                os.path.join(data_directory, "promotions.yaml"), 
                PromotionGains
            )
            
            # Load skill data
            self._skill_data = self._load_data_to_objects(
                os.path.join(data_directory, "skills.yaml"), 
                SkillData
            )
            
            logging.info("Static data loaded successfully")
            
            # Validate loaded data
            self._validate_loaded_data()
            
            return True
            
        except Exception as e:
            logging.error(f"Error loading static data: {str(e)}")
            return False
    
    def get_unit_base_data(self, unit_id: str) -> Optional[UnitBaseData]:
        """
        Get the base data for a specific unit.
        
        Args:
            unit_id: The ID of the unit
            
        Returns:
            UnitBaseData object or None if not found
        """
        return self._unit_data.get(unit_id)
        
    def get_unit_ai_profile(self, unit_id: str) -> Optional[Dict]:
        """
        Get the AI profile for a specific unit.
        
        Args:
            unit_id: The ID of the unit
            
        Returns:
            Dictionary containing AI profile data or None if not found
        """
        # For now, return a default AI profile
        # In a real implementation, this would load from a file or database
        return {
            'behavior_type': 'AGGRESSIVE',
            'target_priority': 'CLOSEST',
            'aggression': 50
        }
    
    def get_item_data(self, item_id: str) -> Optional[ItemData]:
        """
        Get the data for a specific item.
        
        Args:
            item_id: The ID of the item
            
        Returns:
            ItemData object or None if not found
        """
        return self._item_data.get(item_id)
    
    def get_class_data(self, class_id: str) -> Optional[ClassData]:
        """
        Get the data for a specific class.
        
        Args:
            class_id: The ID of the class
            
        Returns:
            ClassData object or None if not found
        """
        return self._class_data.get(class_id)
    
    # This method is replaced by the implementation below at line 535
    
    # This method is replaced by the implementation below at line 564
    
    def get_terrain_data(self, terrain_type: Union[TerrainTypeEnum, str]) -> Optional[TerrainData]:
        """
        Get the data for a specific terrain type.
        
        Args:
            terrain_type: The type of terrain (TerrainTypeEnum or string)
            
        Returns:
            TerrainData object or None if not found
        """
        logging.debug(f"DataProvider.get_terrain_data: Received TerrainType: {terrain_type}")
        
        # Determine the lookup key based on the type of terrain_type
        if isinstance(terrain_type, TerrainTypeEnum):
            # Case 1 & 3: Handle enum values
            if terrain_type == TerrainTypeEnum.PLAIN:
                # Case 1: TerrainTypeEnum.PLAIN -> "PLAINS"
                lookup_key = "PLAINS"
                logging.debug(f"DataProvider.get_terrain_data: Case 1 - Converting TerrainTypeEnum.PLAIN to 'PLAINS' for lookup")
            else:
                # Case 3: Other TerrainTypeEnum -> terrain_type.name
                lookup_key = terrain_type.name
                logging.debug(f"DataProvider.get_terrain_data: Case 3 - Using enum name '{lookup_key}' for lookup")
        elif isinstance(terrain_type, str):
            # Case 2: String input
            if terrain_type == "PLAINS":
                # Case 2: "PLAINS" string -> "PLAINS"
                lookup_key = terrain_type
                logging.debug(f"DataProvider.get_terrain_data: Case 2 - Using string 'PLAINS' directly for lookup")
            else:
                # Handle other string inputs
                lookup_key = terrain_type
                logging.debug(f"DataProvider.get_terrain_data: Using string '{lookup_key}' directly for lookup")
        else:
            # Case 5: Invalid type
            lookup_key = str(terrain_type)
            logging.error(f"DataProvider.get_terrain_data: Invalid terrain_type type: {type(terrain_type)}. Expected TerrainTypeEnum or string.")
            
        logging.debug(f"DataProvider.get_terrain_data: Final Lookup Key: '{lookup_key}'")
        
        return self._terrain_data.get(lookup_key)
    
    def get_terrain_cost(self, terrain_type: Union[TerrainTypeEnum, str], movement_type: MovementTypeEnum) -> int:
        """
        Get the movement cost for a specific terrain and movement type.
        
        Args:
            terrain_type: The type of terrain (TerrainTypeEnum or string)
            movement_type: The type of movement
            
        Returns:
            Movement cost (IMPASSABLE if terrain is impassable for the movement type)
        """
        logging.debug(f"DataProvider.get_terrain_cost: Received TerrainType: {terrain_type}, MovementType: {movement_type}")
        
        # Determine the lookup key based on the type of terrain_type
        if isinstance(terrain_type, TerrainTypeEnum):
            # Case 1 & 3: Handle enum values
            if terrain_type == TerrainTypeEnum.PLAIN:
                # Case 1: TerrainTypeEnum.PLAIN -> "PLAINS"
                lookup_key = "PLAINS"
                logging.debug(f"DataProvider.get_terrain_cost: Case 1 - Converting TerrainTypeEnum.PLAIN to 'PLAINS' for lookup")
            else:
                # Case 3: Other TerrainTypeEnum -> terrain_type.name
                lookup_key = terrain_type.name
                logging.debug(f"DataProvider.get_terrain_cost: Case 3 - Using enum name '{lookup_key}' for lookup")
        elif isinstance(terrain_type, str):
            # Case 2: String input
            if terrain_type == "PLAINS":
                # Case 2: "PLAINS" string -> "PLAINS"
                lookup_key = terrain_type
                logging.debug(f"DataProvider.get_terrain_cost: Case 2 - Using string 'PLAINS' directly for lookup")
            else:
                # Handle other string inputs
                lookup_key = terrain_type
                logging.debug(f"DataProvider.get_terrain_cost: Using string '{lookup_key}' directly for lookup")
        else:
            # Case 5: Invalid type
            lookup_key = str(terrain_type)
            logging.error(f"DataProvider.get_terrain_cost: Invalid terrain_type type: {type(terrain_type)}. Expected TerrainTypeEnum or string.")
            
        logging.debug(f"DataProvider.get_terrain_cost: Final Lookup Key: '{lookup_key}'")
        
        # Log the available keys in terrain_data
        logging.debug(f"DataProvider.get_terrain_cost: Terrain Data Keys: {list(self._terrain_data.keys())}")
        
        terrain_info = self._terrain_data.get(lookup_key)
        if terrain_info:
            # Ensure movement_type is an enum and get its name
            if isinstance(movement_type, MovementTypeEnum):
                movement_type_name = movement_type.name
            else:
                # If it's not an enum, try to convert it to a string
                movement_type_name = str(movement_type)
                
            cost = terrain_info.movement_costs.get(movement_type_name, IMPASSABLE)
            logging.debug(f"DataProvider.get_terrain_cost: Lookup Result: {cost}")
            return cost
        
        logging.debug(f"DataProvider.get_terrain_cost: No terrain info found for key '{lookup_key}', returning IMPASSABLE")
        return IMPASSABLE
    
    def get_terrain_bonuses(self, terrain_type: Union[TerrainTypeEnum, str]) -> Dict[str, int]:
        """
        Get the defensive bonuses for a specific terrain type.
        
        Args:
            terrain_type: The type of terrain (TerrainTypeEnum or string)
            
        Returns:
            Dictionary of bonuses (e.g., {'def': 0, 'avo': 5})
        """
        logging.debug(f"DataProvider.get_terrain_bonuses: Received TerrainType: {terrain_type}")
        
        # Determine the lookup key based on the type of terrain_type
        if isinstance(terrain_type, TerrainTypeEnum):
            # Case 1 & 3: Handle enum values
            if terrain_type == TerrainTypeEnum.PLAIN:
                # Case 1: TerrainTypeEnum.PLAIN -> "PLAINS"
                lookup_key = "PLAINS"
                logging.debug(f"DataProvider.get_terrain_bonuses: Case 1 - Converting TerrainTypeEnum.PLAIN to 'PLAINS' for lookup")
            else:
                # Case 3: Other TerrainTypeEnum -> terrain_type.name
                lookup_key = terrain_type.name
                logging.debug(f"DataProvider.get_terrain_bonuses: Case 3 - Using enum name '{lookup_key}' for lookup")
        elif isinstance(terrain_type, str):
            # Case 2: String input
            if terrain_type == "PLAINS":
                # Case 2: "PLAINS" string -> "PLAINS"
                lookup_key = terrain_type
                logging.debug(f"DataProvider.get_terrain_bonuses: Case 2 - Using string 'PLAINS' directly for lookup")
            else:
                # Handle other string inputs
                lookup_key = terrain_type
                logging.debug(f"DataProvider.get_terrain_bonuses: Using string '{lookup_key}' directly for lookup")
        else:
            # Case 5: Invalid type
            lookup_key = str(terrain_type)
            logging.error(f"DataProvider.get_terrain_bonuses: Invalid terrain_type type: {type(terrain_type)}. Expected TerrainTypeEnum or string.")
            
        logging.debug(f"DataProvider.get_terrain_bonuses: Final Lookup Key: '{lookup_key}'")
        
        terrain_info = self._terrain_data.get(lookup_key)
        if terrain_info:
            return terrain_info.bonuses
        return {'def': 0, 'avo': 0}
    
    def is_terrain_healing(self, terrain_type: Union[TerrainTypeEnum, str]) -> bool:
        """
        Check if a terrain type provides healing.
        
        Args:
            terrain_type: The type of terrain (TerrainTypeEnum or string)
            
        Returns:
            True if the terrain provides healing, False otherwise
        """
        logging.debug(f"DataProvider.is_terrain_healing: Received TerrainType: {terrain_type}")
        
        # Determine the lookup key based on the type of terrain_type
        if isinstance(terrain_type, TerrainTypeEnum):
            # Case 1 & 3: Handle enum values
            if terrain_type == TerrainTypeEnum.PLAIN:
                # Case 1: TerrainTypeEnum.PLAIN -> "PLAINS"
                lookup_key = "PLAINS"
                logging.debug(f"DataProvider.is_terrain_healing: Case 1 - Converting TerrainTypeEnum.PLAIN to 'PLAINS' for lookup")
            else:
                # Case 3: Other TerrainTypeEnum -> terrain_type.name
                lookup_key = terrain_type.name
                logging.debug(f"DataProvider.is_terrain_healing: Case 3 - Using enum name '{lookup_key}' for lookup")
        elif isinstance(terrain_type, str):
            # Case 2: String input
            if terrain_type == "PLAINS":
                # Case 2: "PLAINS" string -> "PLAINS"
                lookup_key = terrain_type
                logging.debug(f"DataProvider.is_terrain_healing: Case 2 - Using string 'PLAINS' directly for lookup")
            else:
                # Handle other string inputs
                lookup_key = terrain_type
                logging.debug(f"DataProvider.is_terrain_healing: Using string '{lookup_key}' directly for lookup")
        else:
            # Case 5: Invalid type
            lookup_key = str(terrain_type)
            logging.error(f"DataProvider.is_terrain_healing: Invalid terrain_type type: {type(terrain_type)}. Expected TerrainTypeEnum or string.")
            
        logging.debug(f"DataProvider.is_terrain_healing: Final Lookup Key: '{lookup_key}'")
        
        terrain_info = self._terrain_data.get(lookup_key)
        if terrain_info:
            return terrain_info.is_healing
        return False
    
    def get_terrain_heal_amount(self, terrain_type: Union[TerrainTypeEnum, str]) -> int:
        """
        Get the healing amount provided by a terrain type.
        
        Args:
            terrain_type: The type of terrain (TerrainTypeEnum or string)
            
        Returns:
            Healing amount (0 if the terrain doesn't provide healing)
        """
        logging.debug(f"DataProvider.get_terrain_heal_amount: Received TerrainType: {terrain_type}")
        
        # Determine the lookup key based on the type of terrain_type
        if isinstance(terrain_type, TerrainTypeEnum):
            # Case 1 & 3: Handle enum values
            if terrain_type == TerrainTypeEnum.PLAIN:
                # Case 1: TerrainTypeEnum.PLAIN -> "PLAINS"
                lookup_key = "PLAINS"
                logging.debug(f"DataProvider.get_terrain_heal_amount: Case 1 - Converting TerrainTypeEnum.PLAIN to 'PLAINS' for lookup")
            else:
                # Case 3: Other TerrainTypeEnum -> terrain_type.name
                lookup_key = terrain_type.name
                logging.debug(f"DataProvider.get_terrain_heal_amount: Case 3 - Using enum name '{lookup_key}' for lookup")
        elif isinstance(terrain_type, str):
            # Case 2: String input
            if terrain_type == "PLAINS":
                # Case 2: "PLAINS" string -> "PLAINS"
                lookup_key = terrain_type
                logging.debug(f"DataProvider.get_terrain_heal_amount: Case 2 - Using string 'PLAINS' directly for lookup")
            else:
                # Handle other string inputs
                lookup_key = terrain_type
                logging.debug(f"DataProvider.get_terrain_heal_amount: Using string '{lookup_key}' directly for lookup")
        else:
            # Case 5: Invalid type
            lookup_key = str(terrain_type)
            logging.error(f"DataProvider.get_terrain_heal_amount: Invalid terrain_type type: {type(terrain_type)}. Expected TerrainTypeEnum or string.")
            
        logging.debug(f"DataProvider.get_terrain_heal_amount: Final Lookup Key: '{lookup_key}'")
        
        terrain_info = self._terrain_data.get(lookup_key)
        if terrain_info and terrain_info.is_healing:
            # Default to 10% healing if not specified
            return terrain_info.get('heal_amount', 10)
        return 0
    
    def is_terrain_indoor(self, terrain_type: Union[TerrainTypeEnum, str]) -> bool:
        """
        Check if a terrain type is considered indoors (for dismounting).
        
        Args:
            terrain_type: The type of terrain (TerrainTypeEnum or string)
            
        Returns:
            True if the terrain is indoors, False otherwise
        """
        logging.debug(f"DataProvider.is_terrain_indoor: Received TerrainType: {terrain_type}")
        
        # Determine the lookup key based on the type of terrain_type
        if isinstance(terrain_type, TerrainTypeEnum):
            # Case 1 & 3: Handle enum values
            if terrain_type == TerrainTypeEnum.PLAIN:
                # Case 1: TerrainTypeEnum.PLAIN -> "PLAINS"
                lookup_key = "PLAINS"
                logging.debug(f"DataProvider.is_terrain_indoor: Case 1 - Converting TerrainTypeEnum.PLAIN to 'PLAINS' for lookup")
            else:
                # Case 3: Other TerrainTypeEnum -> terrain_type.name
                lookup_key = terrain_type.name
                logging.debug(f"DataProvider.is_terrain_indoor: Case 3 - Using enum name '{lookup_key}' for lookup")
        elif isinstance(terrain_type, str):
            # Case 2: String input
            if terrain_type == "PLAINS":
                # Case 2: "PLAINS" string -> "PLAINS"
                lookup_key = terrain_type
                logging.debug(f"DataProvider.is_terrain_indoor: Case 2 - Using string 'PLAINS' directly for lookup")
            else:
                # Handle other string inputs
                lookup_key = terrain_type
                logging.debug(f"DataProvider.is_terrain_indoor: Using string '{lookup_key}' directly for lookup")
        else:
            # Case 5: Invalid type
            lookup_key = str(terrain_type)
            logging.error(f"DataProvider.is_terrain_indoor: Invalid terrain_type type: {type(terrain_type)}. Expected TerrainTypeEnum or string.")
            
        logging.debug(f"DataProvider.is_terrain_indoor: Final Lookup Key: '{lookup_key}'")
        
        terrain_info = self._terrain_data.get(lookup_key)
        if terrain_info:
            return terrain_info.is_indoor
        return False
    
    def get_support_partners(self, unit_id: str) -> List[Dict[str, Union[str, int]]]:
        """
        Get the support partners for a specific unit.
        
        Args:
            unit_id: The ID of the unit
            
        Returns:
            List of dictionaries with partner_id and bonus
        """
        partners = []
        
        # Find all support relations where this unit is involved
        for support_list in self._support_relations.values():
            for support in support_list:
                if support.unit_id == unit_id:
                    partners.append({
                        'partner_id': support.partner_id,
                        'bonus': support.bonus
                    })
                elif support.partner_id == unit_id:
                    partners.append({
                        'partner_id': support.unit_id,
                        'bonus': support.bonus
                    })
        
        return partners
    
    # This method is replaced by the implementation below at line 603
    
    def get_promotion_gains(self, base_class_id: str, promoted_class_id: str) -> Optional[PromotionGains]:
        """
        Get the stat and rank changes for a specific promotion path.
        
        Args:
            base_class_id: The ID of the base class
            promoted_class_id: The ID of the promoted class
            
        Returns:
            PromotionGains object or None if not found
        """
        # Create a key to look up the promotion data
        key = f"{base_class_id}_{promoted_class_id}"
        return self._promotion_data.get(key)
    
    def get_weapon_triangle_bonus(self, attacker_type: WeaponTypeEnum, defender_type: WeaponTypeEnum) -> int:
        """
        Get the weapon triangle hit bonus/penalty.
        
        Args:
            attacker_type: The weapon type of the attacker
            defender_type: The weapon type of the defender
            
        Returns:
            Hit bonus/penalty (+5, -5, or 0)
        """
        if attacker_type in self._weapon_triangle:
            return self._weapon_triangle[attacker_type].get(defender_type, 0)
        return 0
    
    def get_skill_data(self, skill_id: str) -> Optional[SkillData]:
        """
        Get the data for a specific skill.
        
        Args:
            skill_id: The ID of the skill
            
        Returns:
            SkillData object or None if not found
        """
        return self._skill_data.get(skill_id)
        
    def get_config(self, config_key: str, default: Any = None) -> Any:
        """
        Get a configuration value with a default fallback.
        
        Args:
            config_key: The key for the configuration value
            default: The default value to return if the key is not found
            
        Returns:
            The configuration value or the default if not found
        """
        # For now, just return the default value since we don't have actual config data
        # In a real implementation, this would look up values from a config file or database
        return default
    def get_map_data(self, chapter_id: str, scenario_name: Optional[str] = None) -> Optional[MapData]:
        """
        Load and return the map layout data for a specific chapter or scenario.
        
        Args:
            chapter_id: The ID of the chapter
            scenario_name: Optional name of a test scenario
            
        Returns:
            MapData object or None if not found
        """
        # Determine the filepath based on whether we're loading a scenario or a chapter
        if scenario_name:
            filepath = os.path.join("data", "scenarios", scenario_name, "map.json")
            # Try YAML if JSON doesn't exist
            if not os.path.exists(filepath):
                filepath = os.path.join("data", "scenarios", scenario_name, "map.yaml")
        else:
            filepath = os.path.join("data", "chapters", chapter_id, "map.json")
            # Try YAML if JSON doesn't exist
            if not os.path.exists(filepath):
                filepath = os.path.join("data", "chapters", chapter_id, "map.yaml")
                
        map_dict = self._load_yaml_or_json(filepath)
        if map_dict:
            # Convert dict to MapData object
            return MapData(map_dict)
        return None

    def get_unit_placements(self, chapter_id: str, scenario_name: Optional[str] = None) -> List[UnitPlacement]:
        """
        Load and return the unit placements for a specific chapter or scenario.
        
        Args:
            chapter_id: The ID of the chapter
            scenario_name: Optional name of a test scenario
            
        Returns:
            List of UnitPlacement objects (empty list if none found)
        """
        # Determine the filepath based on whether we're loading a scenario or a chapter
        if scenario_name:
            filepath = os.path.join("data", "scenarios", scenario_name, "placements.json")
            # Try YAML if JSON doesn't exist
            if not os.path.exists(filepath):
                filepath = os.path.join("data", "scenarios", scenario_name, "placements.yaml")
        else:
            filepath = os.path.join("data", "chapters", chapter_id, "placements.json")
            # Try YAML if JSON doesn't exist
            if not os.path.exists(filepath):
                filepath = os.path.join("data", "chapters", chapter_id, "placements.yaml")
                
        placements_data = self._load_yaml_or_json(filepath)
        
        # Handle both formats: direct list or dictionary with "placements" key
        if isinstance(placements_data, dict) and "placements" in placements_data:
            placements_list = placements_data["placements"]
            if isinstance(placements_list, list):
                return [UnitPlacement(p) for p in placements_list]
        elif isinstance(placements_data, list):
            return [UnitPlacement(p) for p in placements_data]
        
        if placements_data:
            logging.warning(f"Expected a list or dict with 'placements' key in {filepath}, but got {type(placements_data)}")
        
        return []

    # Overwrite the existing get_event_scripts to load from chapter JSON
    def get_event_scripts(self, chapter_id: str, scenario_name: Optional[str] = None) -> List:
        """
        Load and return the event scripts for a specific chapter or scenario.
        
        Args:
            chapter_id: The ID of the chapter
            scenario_name: Optional name of a test scenario
            
        Returns:
            List of event scripts (empty list if none found)
        """
        # Determine the filepath based on whether we're loading a scenario or a chapter
        if scenario_name:
            filepath = os.path.join("data", "scenarios", scenario_name, "events.json")
            # Try YAML if JSON doesn't exist
            if not os.path.exists(filepath):
                filepath = os.path.join("data", "scenarios", scenario_name, "events.yaml")
        else:
            filepath = os.path.join("data", "chapters", chapter_id, "events.json")
            # Try YAML if JSON doesn't exist
            if not os.path.exists(filepath):
                filepath = os.path.join("data", "chapters", chapter_id, "events.yaml")
                
        # Return the raw list/dict loaded from JSON/YAML, as EventHandler expects this format
        return self._load_yaml_or_json(filepath) or []
    
    def _load_yaml_or_json(self, filepath: str) -> Dict:
        """
        Load data from a YAML or JSON file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dictionary containing the loaded data
        """
        if not os.path.exists(filepath):
            logging.warning(f"File not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r') as file:
                if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    return yaml.safe_load(file)
                elif filepath.endswith('.json'):
                    return json.load(file)
                else:
                    logging.warning(f"Unsupported file format: {filepath}")
                    return {}
        except Exception as e:
            logging.error(f"Error loading file {filepath}: {str(e)}")
            return {}
    
    def _load_data_to_objects(self, filepath: str, class_type, is_list: bool = False) -> Dict:
        """
        Load data from a file and convert it to objects of the specified type.
        
        Args:
            filepath: Path to the file
            class_type: The class to instantiate for each data entry
            is_list: Whether the data is organized as lists by key
            
        Returns:
            Dictionary of objects keyed by ID
        """
        data = self._load_yaml_or_json(filepath)
        result = {}
        
        if not data:
            return result
        
        if is_list:
            # Data is organized as lists by key (e.g., chapter_id -> list of placements)
            for key, items in data.items():
                result[key] = [class_type(item) for item in items]
        else:
            # Data is organized as individual entries with IDs
            for key, item_data in data.items():
                result[key] = class_type(item_data)
        
        return result
    
    def _validate_loaded_data(self) -> None:
        """
        Validate the loaded data for consistency and correctness.
        """
        # This would contain validation logic to ensure data integrity
        # For example, checking that all referenced IDs exist, required fields are present, etc.
        # For now, we'll just log that validation is complete
        logging.info("Data validation complete")