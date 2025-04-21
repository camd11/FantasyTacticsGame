"""
Game State Manager Module

This module is responsible for holding and managing all dynamic data related to the current game session.
It provides interfaces for the Engine Core and other components to query and modify this data safely and consistently.
"""

import logging
import random
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Set, Union

# Import the data provider for accessing static data
from src.core_engine.data_provider import DataProvider, TerrainTypeEnum, MovementTypeEnum

# Enums
class FactionEnum(Enum):
    PLAYER = auto()
    ENEMY = auto()
    NPC = auto()

class StatusEnum(Enum):
    """Enum representing the status of a unit."""
    NORMAL = auto()
    RESCUING = auto()  # Unit is carrying another unit
    RESCUED = auto()   # Unit is being carried
    CAPTURED = auto()  # Unit has been captured by an enemy

class PhaseEnum(Enum):
    PLAYER = auto()
    ENEMY = auto()
    NPC = auto()
    EVENT = auto()  # Added for event phase

class StatusEffectEnum(Enum):
    POISON = auto()
    SLEEP = auto()
    SILENCE = auto()
    BERSERK = auto()
    PETRIFY = auto()  # Added for petrify status
    STAT_BOOST = auto()  # For temporary stat boosts

class DispositionEnum(Enum):
    ACTIVE = auto()  # Unit is active in the current chapter
    DEAD = auto()    # Unit has been killed
    ESCAPED = auto() # Unit has escaped the map
    CAPTURED_BY_ENEMY = auto()  # Unit has been captured by an enemy
    BENCHED = auto() # Unit is not deployed in the current chapter

class ObjectStateEnum(Enum):
    NORMAL = auto()
    VISITED = auto()  # For villages
    OPENED = auto()   # For doors
    LOOTED = auto()   # For chests

# Constants
LEIF_ID = "LEIF"  # ID for the main character
CHAPTER_8_ID = "CH8"  # Chapter where fatigue starts to matter

# Fatigue costs for different actions
FATIGUE_COMBAT = 1
FATIGUE_STAFF_E = 1
FATIGUE_STAFF_D = 2
FATIGUE_STAFF_C = 3
FATIGUE_STAFF_B = 4
FATIGUE_STAFF_A = 5
FATIGUE_SPECIAL_ACTION = 2  # For actions like Dance, Steal

# Data Structures
class ItemInstance:
    """Represents an item instance in a unit's inventory."""
    def __init__(self, item_id: str, current_durability: int):
        self.item_id = item_id
        self.current_durability = current_durability

class StatusEffectInstance:
    """Represents an active status effect on a unit."""
    def __init__(self, type: StatusEffectEnum, duration: int, magnitude: int = 0):
        self.type = type
        self.duration = duration  # Turns remaining, -1 for permanent until cured/chapter end
        self.magnitude = magnitude  # For stat boosts

class UnitState:
    """Represents the current state of a unit on the map."""
    
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.class_id: str = ""
        self.faction: FactionEnum = FactionEnum.PLAYER
        self.position: Tuple[int, int] = (0, 0)
        
        self.current_hp: int = 0
        self.max_hp: int = 0
        
        # Base Stats
        self.base_stats: Dict[str, int] = {}
        
        # Growths
        self.growth_rates: Dict[str, int] = {}
        
        self.level: int = 1
        self.experience: int = 0
        
        self.inventory: List[ItemInstance] = []
        self.equipped_weapon_index: int = -1  # -1 if none
        
        self.weapon_ranks: Dict[str, str] = {}  # WeaponType -> Rank
        self.weapon_exp: Dict[str, int] = {}    # WeaponType -> Experience points
        
        self.current_fatigue: int = 0
        
        self.status_effects: List[StatusEffectInstance] = []
        
        # Action state for current turn
        self.has_moved: bool = False
        self.has_acted: bool = False
        self.is_immobile: bool = False  # Added for ballista system
        
        # Relationships/Bonuses
        self.support_partner_ids: List[str] = []
        self.leadership_stars: int = 0
        self.pcc: int = 0  # Pursuit Critical Coefficient
        
        # Capture/Rescue State
        self.is_captured: bool = False
        self.carrying_unit_id: Optional[str] = None
        
        # Overall Status
        self.disposition: DispositionEnum = DispositionEnum.ACTIVE
        
        # Component system
        self.components: Dict[str, Any] = {}
    
    def has_status(self, status_type: StatusEffectEnum) -> bool:
        """Check if the unit has a specific status effect."""
        return any(status.type == status_type for status in self.status_effects)
    
    def add_component(self, component) -> None:
        """
        Add a component to the unit.
        
        Args:
            component: The component to add
        """
        component_type = component.__class__.__name__
        self.components[component_type] = component
    
    def remove_component(self, component_type: str) -> None:
        """
        Remove a component from the unit.
        
        Args:
            component_type: Type of component to remove
        """
        if component_type in self.components:
            del self.components[component_type]
    
    def get_component(self, component_type: str) -> Optional[Any]:
        """
        Get a component from the unit.
        
        Args:
            component_type: Type of component to get
            
        Returns:
            The component if found, None otherwise
        """
        return self.components.get(component_type)
    
    def has_component(self, component_type: str) -> bool:
        """
        Check if the unit has a component.
        
        Args:
            component_type: Type of component to check for
            
        Returns:
            True if the unit has the component, False otherwise
        """
        return component_type in self.components
    
    @property
    def unit_id(self) -> str:
        """
        Alias for id to maintain compatibility with tests.
        
        Returns:
            The unit's ID
        """
        return self.id
    
    def set_immobile(self, immobile: bool) -> None:
        """
        Set whether the unit is immobile.
        
        Args:
            immobile: True if the unit should be immobile, False otherwise
        """
        self.is_immobile = immobile
    
    def is_attackable(self) -> bool:
        """
        Check if the unit can be attacked.
        
        Returns:
            True if the unit can be attacked, False otherwise
        """
        return self.disposition == DispositionEnum.ACTIVE
    
    def has_property(self, property_name: str) -> bool:
        """
        Check if the unit has a specific property.
        
        Args:
            property_name: Name of the property to check for
            
        Returns:
            True if the unit has the property, False otherwise
        """
        # For now, just handle IS_FLYING property
        if property_name == "IS_FLYING":
            # Check if the unit's class has the FLYING movement type
            from src.core_engine.data_provider import MovementTypeEnum
            return hasattr(self, 'movement_type') and self.movement_type == MovementTypeEnum.FLYING
        
        return False

class MapState:
    """Represents the current state of the map."""
    
    def __init__(self):
        self.map_id: str = ""
        self.dimensions: Tuple[int, int] = (0, 0)  # width, height
        self.terrain_grid: List[List[TerrainTypeEnum]] = []
        self.unit_positions: Dict[str, Tuple[int, int]] = {}  # unit_id -> (x, y)
        self.object_states: Dict[Tuple[int, int], ObjectStateEnum] = {}  # (x, y) -> state

class GameState:
    """Main container for all dynamic game state data."""
    
    def __init__(self):
        self.chapter_id: str = ""
        self.current_turn: int = 1
        self.current_phase: PhaseEnum = PhaseEnum.PLAYER
        
        self.map_state: MapState = MapState()
        self.unit_states: Dict[str, UnitState] = {}  # unit_id -> UnitState
        
        self.event_flags: Dict[str, bool] = {}  # flag_name -> triggered_status
        
        # Player convoy/gold if applicable
        self.player_gold: int = 0
        self.player_convoy: List[ItemInstance] = []
        
        # Currently selected unit (for player phase)
        self.selected_unit_id: Optional[str] = None

class GameStateManager:
    """
    Manages all dynamic game state data.
    Provides interfaces to query and modify this data safely and consistently.
    """
    
    def __init__(self, data_provider: DataProvider):
        self.current_game_state: Optional[GameState] = None
        self.data_provider = data_provider
        self.ai_vs_ai = False  # Flag for AI vs AI mode
        
        # Mock pathfinding for AI testing
        class MockPathfinding:
            def find_path_to_attack_position(self, unit, target):
                # Check if the target is within attack range
                if hasattr(unit, 'position') and hasattr(target, 'position'):
                    # Calculate Manhattan distance
                    distance = abs(unit.position[0] - target.position[0]) + abs(unit.position[1] - target.position[1])
                    
                    # If the target is within attack range (assuming range 1 for simplicity)
                    if distance <= 1:
                        # Return a path that's just the unit's current position
                        return [unit.position]
                    
                    # If the target is within movement range
                    if hasattr(unit, 'movement_range') and distance <= unit.movement_range + 1:
                        # Generate a simple path towards the target
                        path = self._generate_path_towards(unit.position, target.position, unit.movement_range)
                        
                        # Check if any position in the path is occupied by another unit
                        # Only do this check if we have access to the game state
                        if path and len(path) > 1 and hasattr(self, 'current_game_state') and self.current_game_state:
                            valid_path = [path[0]]  # Start with just the starting position
                            
                            # Check each subsequent position in the path
                            for i in range(1, len(path)):
                                pos = path[i]
                                is_occupied = False
                                
                                # Check if this position is occupied by a unit other than the target
                                for unit_id, unit_pos in self.current_game_state.map_state.unit_positions.items():
                                    if unit_pos == pos and unit_id != unit.id and unit_id != target.id:
                                        # Position is occupied by another unit (not the target)
                                        logging.debug(f"Attack path position {pos} is occupied by unit {unit_id}, stopping path here")
                                        is_occupied = True
                                        break
                                
                                if is_occupied:
                                    # Stop the path at the last valid position
                                    break
                                else:
                                    # Add this position to the valid path
                                    valid_path.append(pos)
                            
                            path = valid_path
                        
                        return path
                
                return None
                
            def find_path_to_approach_target(self, unit, position):
                # Generate a path towards the target position
                if hasattr(unit, 'position') and position:
                    # Calculate Manhattan distance
                    distance = abs(unit.position[0] - position[0]) + abs(unit.position[1] - position[1])
                    
                    # If the target is already at the position, return just the current position
                    if distance == 0:
                        return [unit.position]
                    
                    # Generate a simple path towards the target
                    movement_range = getattr(unit, 'movement_range', 5)  # Default to 5 if not specified
                    path = self._generate_path_towards(unit.position, position, movement_range)
                    
                    # Check if any position in the path is occupied by another unit
                    # Only do this check if we have access to the game state
                    if path and len(path) > 1 and hasattr(self, 'current_game_state') and self.current_game_state:
                        valid_path = [path[0]]  # Start with just the starting position
                        
                        # Check each subsequent position in the path
                        for i in range(1, len(path)):
                            pos = path[i]
                            is_occupied = False
                            
                            # Check if this position is occupied
                            for unit_id, unit_pos in self.current_game_state.map_state.unit_positions.items():
                                if unit_pos == pos and unit_id != unit.id:
                                    # Position is occupied by another unit
                                    logging.debug(f"Path position {pos} is occupied by unit {unit_id}, stopping path here")
                                    is_occupied = True
                                    break
                            
                            if is_occupied:
                                # Stop the path at the last valid position
                                break
                            else:
                                # Add this position to the valid path
                                valid_path.append(pos)
                        
                        path = valid_path
                    
                    return path
                
                return None
                
            def can_potentially_reach(self, unit, position):
                return True
                
            def _generate_path_towards(self, start_pos, end_pos, max_steps):
                """Generate a simple path from start_pos towards end_pos, limited by max_steps."""
                path = [start_pos]
                current_pos = start_pos
                steps_taken = 0
                
                while current_pos != end_pos and steps_taken < max_steps:
                    # Move one step towards the target in either x or y direction
                    x, y = current_pos
                    target_x, target_y = end_pos
                    
                    # Decide whether to move in x or y direction
                    if abs(x - target_x) > abs(y - target_y):
                        # Move in x direction
                        x += 1 if target_x > x else -1
                    else:
                        # Move in y direction
                        y += 1 if target_y > y else -1
                    
                    current_pos = (x, y)
                    path.append(current_pos)
                    steps_taken += 1
                
                return path
                
        self.pathfinding = MockPathfinding()
    
    def load_map(self, map_data: Any) -> None:
        """Initialize a new game state with the specified map data."""
        state = GameState()
        state.map_state = MapState()
        state.map_state.map_id = map_data.id
        state.map_state.dimensions = map_data.dimensions
        
        # Convert string terrain codes to TerrainTypeEnum values
        terrain_grid = []
        for row in map_data.terrain_grid:
            terrain_row = []
            for terrain_code in row:
                # Try to convert the string code to TerrainTypeEnum
                try:
                    # If it's already a TerrainTypeEnum, use it directly
                    if isinstance(terrain_code, TerrainTypeEnum):
                        terrain_row.append(terrain_code)
                    else:
                        # Map string codes to TerrainTypeEnum values
                        code_to_enum = {
                            'P': TerrainTypeEnum.PLAIN,
                            'F': TerrainTypeEnum.FOREST,
                            'W': TerrainTypeEnum.RIVER,
                            'R': TerrainTypeEnum.RIVER,  # Added 'R' for River
                            'D': TerrainTypeEnum.BRIDGE,
                            'B': TerrainTypeEnum.BRIDGE,  # Added 'B' for Bridge
                            'V': TerrainTypeEnum.VILLAGE,
                            'S': TerrainTypeEnum.THRONE,  # Seize point is represented as throne
                            'M': TerrainTypeEnum.MOUNTAIN,
                            'H': TerrainTypeEnum.CASTLE,
                            'T': TerrainTypeEnum.THRONE
                        }
                        
                        if terrain_code in code_to_enum:
                            terrain_row.append(code_to_enum[terrain_code])
                        else:
                            # If code not found in mapping, try direct enum lookup
                            try:
                                terrain_row.append(TerrainTypeEnum[terrain_code])
                            except (KeyError, ValueError):
                                # If all conversion attempts fail, use INVALID as fallback
                                logging.warning(f"Invalid terrain code '{terrain_code}', using INVALID")
                                terrain_row.append(TerrainTypeEnum.INVALID)
                except Exception as e:
                    logging.warning(f"Error converting terrain code '{terrain_code}': {str(e)}, using INVALID")
                    terrain_row.append(TerrainTypeEnum.INVALID)
            terrain_grid.append(terrain_row)
            
        state.map_state.terrain_grid = terrain_grid
        state.map_state.unit_positions = {}
        state.map_state.object_states = {}
        state.unit_states = {}
        state.event_flags = {}
        state.chapter_id = map_data.id  # Assuming map_id is the same as chapter_id
        
        self.current_game_state = state
        logging.info(f"Map loaded: {map_data.id}")
        
    def initialize_from_scenario(self, scenario_data: Dict[str, Any]) -> None:
        """
        Initialize the game state from a scenario.
        
        Args:
            scenario_data: The scenario data loaded from a YAML file
        """
        if not scenario_data:
            logging.error("Cannot initialize from scenario: No scenario data provided")
            return
            
        # Create a map data object from the scenario data
        map_data_dict = {
            'id': scenario_data.get('id', ''),
            'name': scenario_data.get('name', ''),
            'dimensions': scenario_data.get('dimensions', (0, 0)),
            'terrain_grid': scenario_data.get('terrain_grid', [])
        }
        
        # Create a simple object with the necessary attributes for load_map
        class MapDataObj:
            def __init__(self, data_dict):
                self.id = data_dict['id']
                self.name = data_dict['name']
                self.dimensions = data_dict['dimensions']
                self.terrain_grid = data_dict['terrain_grid']
        
        map_data = MapDataObj(map_data_dict)
        
        # Load the map
        self.load_map(map_data)
        
        # Deploy units
        if 'placements' in scenario_data:
            # Create UnitPlacement objects from the placement dictionaries
            class UnitPlacementObj:
                def __init__(self, data_dict):
                    self.unit_id = data_dict.get('unit_id', '')
                    self.faction = data_dict.get('faction', '')
                    self.position = data_dict.get('position', (0, 0))
                    self.level = data_dict.get('level', 1)
                    self.start_inventory = data_dict.get('start_inventory', [])
                    self.starting_fatigue = data_dict.get('starting_fatigue', 0)
                    self.needs_autolevel = data_dict.get('needs_autolevel', False)
                    self.target_level = data_dict.get('target_level', 1)
                    
                    # Handle stats_override if present
                    if 'stats_override' in data_dict:
                        self.stats_override = data_dict['stats_override']
            
            unit_placements = [UnitPlacementObj(p) for p in scenario_data['placements']]
            self.deploy_units(unit_placements, self.data_provider)
            
            # Apply stats overrides if present
            for placement in scenario_data['placements']:
                if 'stats_override' in placement:
                    unit_id = placement['unit_id']
                    unit = self.get_unit(unit_id)
                    if unit:
                        for stat, value in placement['stats_override'].items():
                            if stat == 'current_hp':
                                unit.current_hp = value
                            else:
                                unit.base_stats[stat] = value
                
                # Set AI persona if present
                if 'ai_persona' in placement:
                    unit_id = placement['unit_id']
                    unit = self.get_unit(unit_id)
                    if unit:
                        unit.ai_persona = placement['ai_persona']
        
        # Set up objectives
        if 'objectives' in scenario_data:
            # Store objectives in the game state for reference
            if not hasattr(self.current_game_state, 'objectives'):
                self.current_game_state.objectives = []
                
            self.current_game_state.objectives = scenario_data['objectives']
            
            # Set seize point if there's a SEIZE objective
            for objective in scenario_data['objectives']:
                if objective.get('type') == 'SEIZE' and 'position' in objective:
                    self.current_game_state.map_state.seize_point = tuple(objective['position'])
        
        logging.info(f"Game state initialized from scenario: {scenario_data.get('id', 'unknown')}")
    
    def deploy_units(self, unit_placements: List, data_provider: DataProvider) -> None:
        """Deploy units on the map based on the provided placements."""
        if not self.current_game_state:
            logging.error("Cannot deploy units: No game state initialized")
            return
        
        for placement in unit_placements:
            unit_id = placement.unit_id
            base_data = data_provider.get_unit_base_data(unit_id)
            
            if not base_data:
                logging.warning(f"Unit base data not found for {unit_id}")
                continue
            
            unit = UnitState()
            unit.id = unit_id
            unit.name = base_data.name
            unit.class_id = base_data.base_class_id
            
            # Convert string faction to FactionEnum
            if placement.faction == 'PLAYER':
                unit.faction = FactionEnum.PLAYER
            elif placement.faction == 'ENEMY':
                unit.faction = FactionEnum.ENEMY
            elif placement.faction == 'NPC':
                unit.faction = FactionEnum.NPC
            else:
                logging.warning(f"Unknown faction '{placement.faction}' for unit {unit_id}, defaulting to PLAYER")
                unit.faction = FactionEnum.PLAYER
                
            unit.position = tuple(placement.position)
            
            unit.max_hp = base_data.stats.get("HP", 0)
            unit.current_hp = unit.max_hp
            
            unit.base_stats = base_data.stats
            unit.growth_rates = base_data.growths
            unit.level = placement.level
            unit.experience = 0
            
            # Initialize inventory
            unit.inventory = []
            for item_id in placement.start_inventory:
                item_data = data_provider.get_item_data(item_id)
                if item_data:
                    unit.inventory.append(ItemInstance(
                        item_id=item_id,
                        current_durability=item_data.max_durability
                    ))
            
            # Find initial equipped weapon
            unit.equipped_weapon_index = self._find_initial_equipped_weapon(unit.inventory, data_provider)
            
            unit.weapon_ranks = base_data.base_weapon_ranks
            unit.weapon_exp = {wt: 0 for wt in unit.weapon_ranks}
            
            unit.current_fatigue = placement.starting_fatigue
            unit.status_effects = []
            
            unit.has_moved = False
            unit.has_acted = False
            
            unit.support_partner_ids = data_provider.get_support_partners(unit_id)
            unit.leadership_stars = base_data.leadership_stars
            unit.pcc = base_data.pcc
            
            unit.is_captured = False
            unit.carrying_unit_id = None
            unit.disposition = DispositionEnum.ACTIVE
            
            # Handle autoleveling if needed
            if placement.needs_autolevel:
                self._autolevel_unit(unit, placement.target_level, data_provider)
            
            self.current_game_state.unit_states[unit_id] = unit
            self.current_game_state.map_state.unit_positions[unit_id] = tuple(unit.position)
        
        logging.info("Units deployed")
    
    # --- Query Functions ---
    
    def get_unit(self, unit_id: str) -> Optional[UnitState]:
        """Get a unit by ID."""
        if not self.current_game_state:
            return None
        return self.current_game_state.unit_states.get(unit_id)
        
    def get_unit_by_id(self, unit_id: str) -> Optional[UnitState]:
        """Alias for get_unit to maintain compatibility with tests."""
        return self.get_unit(unit_id)
    
    def get_units_by_faction(self, faction: Union[FactionEnum, str]) -> List[UnitState]:
        """Get all active units of a specific faction."""
        if not self.current_game_state:
            return []
        
        # Convert string faction to FactionEnum if needed
        faction_enum = faction
        if isinstance(faction, str):
            if faction == 'PLAYER':
                faction_enum = FactionEnum.PLAYER
            elif faction == 'ENEMY':
                faction_enum = FactionEnum.ENEMY
            elif faction == 'NPC':
                faction_enum = FactionEnum.NPC
            else:
                logging.warning(f"Unknown faction string '{faction}', defaulting to PLAYER")
                faction_enum = FactionEnum.PLAYER
        
        return [
            unit for unit in self.current_game_state.unit_states.values()
            if unit.faction == faction_enum and unit.disposition == DispositionEnum.ACTIVE
        ]
    
    def get_units_within_range(self, position: Tuple[int, int], range_val: int, include_faction: Optional[FactionEnum] = None) -> List[UnitState]:
        """Get all units within a certain range of a position."""
        if not self.current_game_state:
            return []
        
        result = []
        x, y = position
        
        for unit in self.current_game_state.unit_states.values():
            if unit.disposition != DispositionEnum.ACTIVE:
                continue
            
            if include_faction and unit.faction != include_faction:
                continue
            
            unit_x, unit_y = unit.position
            distance = abs(x - unit_x) + abs(y - unit_y)  # Manhattan distance
            
            if distance <= range_val:
                result.append(unit)
        
        return result
    
    def get_terrain_type(self, position: Tuple[int, int]) -> TerrainTypeEnum:
        """Get the terrain type at a specific position."""
        if not self.current_game_state:
            return TerrainTypeEnum.INVALID
        
        x, y = position
        dimensions = self.current_game_state.map_state.dimensions
        
        if 0 <= x < dimensions[0] and 0 <= y < dimensions[1]:
            return self.current_game_state.map_state.terrain_grid[y][x]
        
        return TerrainTypeEnum.INVALID
        
    def get_terrain_at(self, position: Tuple[int, int]) -> str:
        """
        Get the terrain type at a specific position as a string code.
        This is an alias for get_terrain_type to maintain compatibility with tests.
        
        Returns:
            String code representing the terrain (e.g., "P" for plain, "F" for forest)
        """
        terrain_type = self.get_terrain_type(position)
        
        # Map TerrainTypeEnum values to string codes
        enum_to_code = {
            TerrainTypeEnum.PLAIN: "P",
            TerrainTypeEnum.FOREST: "F",
            TerrainTypeEnum.MOUNTAIN: "M",
            TerrainTypeEnum.RIVER: "W",
            TerrainTypeEnum.BRIDGE: "D",
            TerrainTypeEnum.VILLAGE: "V",
            TerrainTypeEnum.THRONE: "T",
            TerrainTypeEnum.CASTLE: "H"
        }
        
        return enum_to_code.get(terrain_type, "?")
    
    def get_terrain_movement_cost(self, position: Tuple[int, int], unit_id: str) -> int:
        """Get the movement cost for a unit to move to a specific position."""
        if not self.current_game_state:
            return 99  # IMPASSABLE
        
        unit = self.get_unit(unit_id)
        if not unit:
            return 99  # IMPASSABLE
        
        terrain_type = self.get_terrain_type(position)
        class_data = self.data_provider.get_class_data(unit.class_id)
        
        if not class_data:
            return 99  # IMPASSABLE
        
        movement_type = class_data.movement_type
        
        # Handle dismount: if unit is mounted and terrain is indoor, use infantry movement type
        if self.is_unit_mounted(unit_id) and self.data_provider.is_terrain_indoor(terrain_type):
            movement_type = MovementTypeEnum.INFANTRY
        
        cost = self.data_provider.get_terrain_cost(terrain_type, movement_type)
        return cost
    
    def get_terrain_bonus(self, position: Tuple[int, int]) -> Dict[str, int]:
        """Get the defensive bonuses for a specific position."""
        if not self.current_game_state:
            return {'def': 0, 'avo': 0}
        
        terrain_type = self.get_terrain_type(position)
        return self.data_provider.get_terrain_bonuses(terrain_type)
    
    def is_tile_occupied(self, position: Tuple[int, int]) -> bool:
        """Check if a tile is occupied by a unit."""
        if not self.current_game_state:
            return False
        
        return position in self.current_game_state.map_state.unit_positions.values()
    
    def is_tile_seize_point(self, position: Tuple[int, int]) -> bool:
        """Check if a tile is a seize point."""
        if not self.current_game_state:
            return False
        
        map_data = self.data_provider.get_map_data(self.current_game_state.chapter_id)
        if not map_data:
            return False
        
        return map_data.seize_point == position
    
    def get_unit_movement_stars(self, unit_id: str) -> int:
        """Get the number of movement stars for a unit."""
        unit = self.get_unit(unit_id)
        if not unit:
            return 0
        
        return unit.base_stats.get("MOV_STARS", 0)
    
    def is_unit_fatigued_for_deployment(self, unit_id: str) -> bool:
        """Check if a unit is too fatigued to be deployed."""
        if not self.current_game_state:
            return False
        
        # Leif is exempt from fatigue
        if unit_id == LEIF_ID:
            return False
        
        # Fatigue check only applies from Chapter 8 onwards
        if self.current_game_state.chapter_id < CHAPTER_8_ID:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        return unit.current_fatigue >= unit.max_hp
    
    def is_unit_mounted(self, unit_id: str) -> bool:
        """Check if a unit is mounted."""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        class_data = self.data_provider.get_class_data(unit.class_id)
        if not class_data:
            return False
        
        # A class is considered mounted if it has a dismount_class_id
        return class_data.dismount_class_id is not None
    
    def get_map_dimensions(self) -> Tuple[int, int]:
        """Get the dimensions of the current map (width, height)."""
        if not self.current_game_state:
            return (0, 0)
        
        return self.current_game_state.map_state.dimensions
    
    def has_npc_units(self) -> bool:
        """Check if there are any active NPC units on the map."""
        if not self.current_game_state:
            return False
        
        return any(
            unit.faction == FactionEnum.NPC and unit.disposition == DispositionEnum.ACTIVE
            for unit in self.current_game_state.unit_states.values()
        )
    
    # --- Modification Functions ---
    
    def move_unit(self, unit_id: str, new_position: Tuple[int, int]) -> bool:
        """Move a unit to a new position."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        old_position = unit.position
        unit.position = tuple(new_position)
        
        # Update map_state.unit_positions dictionary
        self.current_game_state.map_state.unit_positions[unit_id] = tuple(new_position)
        
        # Log detailed information about the position change
        logging.info(f"Unit {unit_id} moved from {old_position} to {new_position}")
        logging.debug(f"GAMESTATE: Updated position for unit {unit_id} ({unit.name}) from {old_position} to {new_position}")
        
        return True
    
    def apply_damage(self, unit_id: str, damage: int, is_capture_attempt: bool = False, status_effect_manager=None) -> bool:
        """
        Apply damage to a unit and handle status effects.
        
        Args:
            unit_id: ID of the unit
            damage: Amount of damage to apply
            is_capture_attempt: Whether this is a capture attempt
            status_effect_manager: Optional StatusEffectManager to handle status effects
            
        Returns:
            True if damage was applied successfully, False otherwise
        """
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        old_hp = unit.current_hp
        unit.current_hp = max(0, unit.current_hp - damage)
        
        # Log detailed information about the HP change
        logging.info(f"Unit {unit_id} takes {damage} damage. HP: {unit.current_hp}/{unit.max_hp}")
        logging.debug(f"GAMESTATE: Updated HP for unit {unit_id} ({unit.name}) from {old_hp} to {unit.current_hp}")
        
        # Handle status effects that should be removed when taking damage
        if status_effect_manager and damage > 0:
            status_effect_manager.handle_damage_taken(unit_id, damage)
            logging.debug(f"GAMESTATE: Processed status effects for unit {unit_id} after taking damage")
        
        if unit.current_hp <= 0:
            old_disposition = unit.disposition
            
            if is_capture_attempt:
                # Unit is captured by the attacker
                logging.info(f"Unit {unit_id} was captured!")
                unit.disposition = DispositionEnum.CAPTURED_BY_ENEMY
                logging.debug(f"GAMESTATE: Changed unit {unit_id} disposition from {old_disposition} to {unit.disposition} (captured)")
            else:
                unit.disposition = DispositionEnum.DEAD
                logging.info(f"Unit {unit_id} has fallen!")
                logging.debug(f"GAMESTATE: Changed unit {unit_id} disposition from {old_disposition} to {unit.disposition} (defeated)")
                
                # Remove unit from map positions
                if unit_id in self.current_game_state.map_state.unit_positions:
                    old_position = self.current_game_state.map_state.unit_positions[unit_id]
                    del self.current_game_state.map_state.unit_positions[unit_id]
                    logging.debug(f"GAMESTATE: Removed unit {unit_id} from map position {old_position}")
        
        return True
    
    def apply_healing(self, unit_id: str, amount: int) -> bool:
        """Apply healing to a unit."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        old_hp = unit.current_hp
        unit.current_hp = min(unit.max_hp, unit.current_hp + amount)
        
        # Log detailed information about the HP change
        logging.info(f"Unit {unit_id} healed for {amount}. HP: {unit.current_hp}/{unit.max_hp}")
        logging.debug(f"GAMESTATE: Updated HP for unit {unit_id} ({unit.name}) from {old_hp} to {unit.current_hp} (healing)")
        
        return True
    
    def add_status_effect(self, unit_id: str, status_type: StatusEffectEnum, duration: int, magnitude: int = 0) -> bool:
        """Add a status effect to a unit."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        # Check if already present, maybe refresh duration
        existing_status = next((s for s in unit.status_effects if s.type == status_type), None)
        
        if existing_status:
            # Update existing status
            old_duration = existing_status.duration
            old_magnitude = existing_status.magnitude
            existing_status.duration = duration
            existing_status.magnitude = magnitude
            
            # Log detailed information about the status effect update
            logging.info(f"Unit {unit_id} status effect {status_type.name} refreshed")
            logging.debug(f"GAMESTATE: Updated status effect {status_type.name} for unit {unit_id} ({unit.name}): "
                         f"duration {old_duration}->{duration}, magnitude {old_magnitude}->{magnitude}")
        else:
            # Add new status
            unit.status_effects.append(StatusEffectInstance(
                type=status_type,
                duration=duration,
                magnitude=magnitude
            ))
            
            # Log detailed information about the new status effect
            logging.info(f"Unit {unit_id} afflicted with {status_type.name}")
            logging.debug(f"GAMESTATE: Added new status effect {status_type.name} to unit {unit_id} ({unit.name}): "
                         f"duration={duration}, magnitude={magnitude}")
        
        return True
    
    def remove_status_effect(self, unit_id: str, status_type: StatusEffectEnum) -> bool:
        """Remove a status effect from a unit."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        # Check if the status effect exists before removing
        has_status = any(s.type == status_type for s in unit.status_effects)
        
        unit.status_effects = [s for s in unit.status_effects if s.type != status_type]
        
        # Log detailed information about the status effect removal
        if has_status:
            logging.info(f"Unit {unit_id} cured of {status_type.name}")
            logging.debug(f"GAMESTATE: Removed status effect {status_type.name} from unit {unit_id} ({unit.name})")
        else:
            logging.debug(f"GAMESTATE: Attempted to remove status effect {status_type.name} from unit {unit_id}, but it wasn't present")
            
        return True
    
    def update_fatigue(self, unit_id: str, amount: int) -> bool:
        """Update the fatigue level of a unit."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        old_fatigue = unit.current_fatigue
        unit.current_fatigue += amount
        
        # Log detailed information about the fatigue change
        logging.info(f"Unit {unit_id} fatigue increased by {amount}. Current: {unit.current_fatigue}")
        logging.debug(f"GAMESTATE: Updated fatigue for unit {unit_id} ({unit.name}) from {old_fatigue} to {unit.current_fatigue}")
        
        return True
    
    def apply_combat_results(self, combat_result: Dict[str, Any]) -> bool:
        """Apply the results of combat to the units involved."""
        if not self.current_game_state:
            return False
        
        # Extract data from combat_result
        attacker_id = combat_result.get('attacker_id')
        defender_id = combat_result.get('defender_id')
        attacker_damage = combat_result.get('attacker_damage', 0)
        defender_damage = combat_result.get('defender_damage', 0)
        attacker_exp = combat_result.get('attacker_exp', 0)
        defender_exp = combat_result.get('defender_exp', 0)
        attacker_wexp = combat_result.get('attacker_wexp', 0)
        defender_wexp = combat_result.get('defender_wexp', 0)
        is_capture = combat_result.get('is_capture', False)
        
        # Apply damage
        if attacker_id:
            self.apply_damage(attacker_id, defender_damage)
        
        if defender_id:
            self.apply_damage(defender_id, attacker_damage, is_capture)
        
        # Apply experience
        if attacker_id:
            self._apply_experience(attacker_id, attacker_exp)
        
        if defender_id:
            self._apply_experience(defender_id, defender_exp)
        
        # Apply weapon experience
        if attacker_id and attacker_wexp > 0:
            self._apply_weapon_experience(attacker_id, combat_result.get('attacker_weapon_type'), attacker_wexp)
        
        if defender_id and defender_wexp > 0:
            self._apply_weapon_experience(defender_id, combat_result.get('defender_weapon_type'), defender_wexp)
        
        # Apply fatigue
        if attacker_id:
            self.update_fatigue(attacker_id, FATIGUE_COMBAT)
        
        if defender_id:
            self.update_fatigue(defender_id, FATIGUE_COMBAT)
        
        return True
    
    def finalize_chapter_fatigue(self) -> None:
        """Update fatigue status for all units at the end of a chapter."""
        if not self.current_game_state:
            return
        
        for unit in self.current_game_state.unit_states.values():
            if unit.faction == FactionEnum.PLAYER and unit.disposition == DispositionEnum.ACTIVE:
                # Check if unit is fatigued for next deployment
                if unit.id != LEIF_ID and unit.current_fatigue >= unit.max_hp:
                    logging.info(f"Unit {unit.id} is fatigued for next deployment")
        
        logging.info("Chapter fatigue finalized")
    
    def finalize_escape_map_captures(self) -> None:
        """Mark units left on an escape map as captured if Leif escaped."""
        if not self.current_game_state:
            return
        
        # Check if this is an escape map and if Leif escaped
        leif = self.get_unit(LEIF_ID)
        if not leif or leif.disposition != DispositionEnum.ESCAPED:
            return
        
        # Mark remaining player units as captured
        for unit in self.current_game_state.unit_states.values():
            if unit.faction == FactionEnum.PLAYER and unit.disposition == DispositionEnum.ACTIVE:
                unit.disposition = DispositionEnum.CAPTURED_BY_ENEMY
                logging.info(f"Unit {unit.id} was left behind and captured")
        
        logging.info("Escape map captures finalized")
        
    def get_unit_acted_status(self, unit_id: str) -> bool:
        """
        Get whether a unit has already acted in the current turn.
        
        Args:
            unit_id: ID of the unit to check
            
        Returns:
            True if the unit has acted, False otherwise or if the unit doesn't exist
        """
        unit = self.get_unit(unit_id)
        if not unit:
            logging.debug(f"get_unit_acted_status: Unit {unit_id} not found")
            return False
            
        return unit.has_acted
    
    # --- Helper Functions ---
    
    def _find_initial_equipped_weapon(self, inventory: List[ItemInstance], data_provider: DataProvider) -> int:
        """Find the index of the first equippable weapon in the inventory."""
        for i, item in enumerate(inventory):
            item_data = data_provider.get_item_data(item.item_id)
            if item_data and item_data.type == "WEAPON":
                return i
        return -1
    
    def _autolevel_unit(self, unit: UnitState, target_level: int, data_provider: DataProvider) -> None:
        """Apply automatic level ups to a unit to reach the target level."""
        if unit.level >= target_level:
            return
        
        levels_to_gain = target_level - unit.level
        
        for _ in range(levels_to_gain):
            # Apply growths to stats
            for stat, growth in unit.growth_rates.items():
                if stat == "HP":
                    continue  # Handle HP separately if needed
                
                # Check if growth triggers (e.g., 60% = 0.6 chance)
                if random.random() < (growth / 100.0):
                    unit.base_stats[stat] = unit.base_stats.get(stat, 0) + 1
            
            unit.level += 1
        
        logging.info(f"Unit {unit.id} autoleveled to level {unit.level}")
    
    def _apply_experience(self, unit_id: str, exp_amount: int) -> None:
        """Apply experience to a unit, handling level ups if necessary."""
        unit = self.get_unit(unit_id)
        if not unit:
            return
        
        unit.experience += exp_amount
        
        # Check for level up
        if unit.experience >= 100:
            unit.level += 1
            unit.experience -= 100
            
            # Apply stat growths for level up
            self._apply_level_up_growths(unit)
            
            logging.info(f"Unit {unit_id} leveled up to {unit.level}")
    
    def _apply_level_up_growths(self, unit: UnitState) -> None:
        """Apply random stat growths for a level up."""
        for stat, growth in unit.growth_rates.items():
            if stat == "HP":
                continue  # Handle HP separately if needed
            
            # Check if growth triggers (e.g., 60% = 0.6 chance)
            if random.random() < (growth / 100.0):
                unit.base_stats[stat] = unit.base_stats.get(stat, 0) + 1
    
    def _apply_weapon_experience(self, unit_id: str, weapon_type: str, wexp_amount: int) -> None:
        """Apply weapon experience to a unit, handling rank ups if necessary."""
        unit = self.get_unit(unit_id)
        if not unit or not weapon_type:
            return
        
        if weapon_type not in unit.weapon_exp:
            return
        
        unit.weapon_exp[weapon_type] += wexp_amount
        
        # Check for rank up (simplified, would need actual WExp thresholds)
        # This is just a placeholder for the actual rank up logic
        logging.info(f"Unit {unit_id} gained {wexp_amount} WExp in {weapon_type}")
