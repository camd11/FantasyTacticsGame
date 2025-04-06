# Specification: Data Provider

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The Data Provider is responsible for loading and providing access to all static game data. This data defines the fundamental rules, entities, and content of the game, such as unit base stats, item properties, class definitions, map layouts, terrain characteristics, support relationships, and event scripts. It abstracts the data source (e.g., YAML, JSON files) from the rest of the engine.

## 2. Functional Requirements

### 2.1. Data Loading
    - Load static game data from specified file sources (e.g., YAML, JSON) upon initialization or on demand.
    - Parse and store the data in an easily accessible internal format (e.g., dictionaries, custom objects).
    - Handle potential errors during file loading or parsing (e.g., file not found, invalid format).

### 2.2. Data Access Interfaces
    - Provide functions to retrieve specific data elements based on identifiers (IDs).
    - **Unit Data:**
        - `get_unit_base_data(unit_id)`: Returns base stats, growths, class, skills, leadership, PCC, etc. for a specific character.
    - **Item Data:**
        - `get_item_data(item_id)`: Returns Might, Hit, Crit, Weight, Range, Max Durability, Rank, Type, Effects (healing, stat boost, effectiveness), etc.
    - **Class Data:**
        - `get_class_data(class_id)`: Returns base stats, caps, weapon ranks, movement type, promotion options, class skills, dismount stats/rules.
    - **Map Data:**
        - `get_map_data(chapter_id)`: Returns dimensions, terrain grid layout.
        - `get_unit_placements(chapter_id)`: Returns initial unit positions, factions, levels, and inventories for a chapter.
    - **Terrain Data:**
        - `get_terrain_cost(terrain_type, movement_type)`: Returns the movement cost.
        - `get_terrain_bonuses(terrain_type)`: Returns Def/Avo/other bonuses.
        - `is_terrain_healing(terrain_type)`: Checks if terrain provides healing.
        - `is_terrain_indoor(terrain_type)`: Checks if terrain is considered indoors (for dismounting).
    - **Skill Data:**
        - `get_skill_data(skill_id)`: Returns the description and effects of a skill.
    - **Support Data:**
        - `get_support_partners(unit_id)`: Returns a list of units supported by or supporting the given unit, and the bonus amount.
    - **Event Data:**
        - `get_event_scripts(chapter_id)`: Returns the list of event triggers and associated actions for a chapter.
    - **Promotion Data:**
        - `get_promotion_gains(base_class_id, promoted_class_id)`: Returns the stat bonuses and rank changes for a specific promotion path.
    - **Weapon Triangle Data:**
        - `get_weapon_triangle_bonus(attacker_weapon_type, defender_weapon_type)`: Returns the Hit bonus/penalty (+5, -5, 0).

### 2.3. Data Validation (Optional)
    - Perform basic validation on loaded data to ensure consistency and correctness (e.g., check required fields, valid enum values).

## 3. Data Structures (Conceptual - Internal Representation)

```python
# --- data_provider_datastructures.py ---

# Example internal structures (could be classes or nested dictionaries)

class UnitBaseData:
    id: string
    name: string
    base_class_id: string
    stats: Dict[StatEnum, int]
    growths: Dict[StatEnum, int]
    base_weapon_ranks: Dict[WeaponTypeEnum, RankEnum]
    skills: List[string] # Skill IDs
    leadership_stars: int
    pcc: int
    # ... other inherent properties

class ItemData:
    id: string
    name: string
    type: ItemTypeEnum # WEAPON, STAFF, CONSUMABLE, SCROLL, KEY
    weapon_type: WeaponTypeEnum # If applicable
    might: int
    hit: int
    crit: int
    weight: int
    range_min: int
    range_max: int
    max_durability: int
    required_rank: RankEnum
    effects: List[EffectData] # e.g., HealEffect(amount=20), StatBoostEffect(stat=STR, amount=2), EffectiveVs(type=CAVALRY)
    # ...

class ClassData:
    id: string
    name: string
    base_stats: Dict[StatEnum, int]
    max_stats: Dict[StatEnum, int] # Caps
    max_weapon_ranks: Dict[WeaponTypeEnum, RankEnum]
    movement_type: MovementTypeEnum
    promotion_options: Dict[string, string] # item_id -> promoted_class_id
    class_skills: List[string] # Skill IDs
    dismount_class_id: string # ID of class when dismounted (if applicable)
    # ...

class TerrainData:
    type: TerrainTypeEnum
    name: string
    movement_costs: Dict[MovementTypeEnum, int] # movement_type -> cost (or IMPASSABLE)
    bonuses: Dict[BonusTypeEnum, int] # DEF: 2, AVO: 20
    is_healing: bool
    is_indoor: bool
    # ...

# ... structures for MapLayout, UnitPlacement, EventScript, SupportRelation, PromotionGains etc.
```

## 4. Pseudocode (data_provider.py)

```python
# --- data_provider.py ---

# Import necessary libraries (e.g., yaml, json)
# Import internal data structures

class DataProvider:
    _unit_data = {}
    _item_data = {}
    _class_data = {}
    _terrain_data = {}
    _map_layouts = {}
    _unit_placements = {}
    _event_scripts = {}
    _support_relations = {}
    _promotion_data = {}
    _skill_data = {}
    # ... other data caches

    # TDD: Test loading data populates internal caches correctly from sample files
    function load_all_data(data_directory):
        try:
            _unit_data = load_yaml_or_json(data_directory + "/units.yaml")
            _item_data = load_yaml_or_json(data_directory + "/items.yaml")
            _class_data = load_yaml_or_json(data_directory + "/classes.yaml")
            _terrain_data = load_yaml_or_json(data_directory + "/terrain.yaml")
            _map_layouts = load_yaml_or_json(data_directory + "/maps/layouts.yaml") # Example structure
            _unit_placements = load_yaml_or_json(data_directory + "/maps/placements.yaml")
            _event_scripts = load_yaml_or_json(data_directory + "/maps/events.yaml")
            _support_relations = load_yaml_or_json(data_directory + "/supports.yaml")
            _promotion_data = load_yaml_or_json(data_directory + "/promotions.yaml")
            _skill_data = load_yaml_or_json(data_directory + "/skills.yaml")
            log("Static data loaded successfully.")
            # Perform validation if needed
            validate_loaded_data()
        except Exception as e:
            log("Error loading static data: " + str(e))
            # Handle error appropriately (e.g., raise exception, exit)

    # --- Accessor Functions ---

    # TDD: Test get_unit_base_data returns correct data object or null
    function get_unit_base_data(unit_id):
        return _unit_data.get(unit_id, None) # Return a copy to prevent modification?

    # TDD: Test get_item_data returns correct data object or null
    function get_item_data(item_id):
        return _item_data.get(item_id, None)

    # TDD: Test get_class_data returns correct data object or null
    function get_class_data(class_id):
        return _class_data.get(class_id, None)

    # TDD: Test get_map_data returns correct layout for a chapter
    function get_map_data(chapter_id):
        # Maps might be stored per chapter ID
        return _map_layouts.get(chapter_id, None)

    # TDD: Test get_unit_placements returns correct placements for a chapter
    function get_unit_placements(chapter_id):
        return _unit_placements.get(chapter_id, [])

    # TDD: Test get_terrain_cost returns correct cost based on type and movement
    function get_terrain_cost(terrain_type, movement_type):
        terrain_info = _terrain_data.get(terrain_type, None)
        if terrain_info:
            return terrain_info.movement_costs.get(movement_type, IMPASSABLE) # Default to impassable if type not listed
        return IMPASSABLE

    # TDD: Test get_terrain_bonuses returns correct def/avo bonuses
    function get_terrain_bonuses(terrain_type):
        terrain_info = _terrain_data.get(terrain_type, None)
        if terrain_info:
            return terrain_info.bonuses # e.g., {'def': 0, 'avo': 5}
        return {'def': 0, 'avo': 0}

    # TDD: Test get_support_partners returns correct list of partners and bonuses
    function get_support_partners(unit_id):
        # Need to parse _support_relations based on unit_id
        partners = []
        # Example: _support_relations = {'Leif': [{'target': 'Finn', 'bonus': 10}, {'target': 'Nanna', 'bonus': 10}], 'Finn': [{'target': 'Leif', 'bonus': 10}]}
        # Iterate through relations to find who supports/is supported by unit_id
        return partners # Return list of {'partner_id': X, 'bonus': Y}

    # TDD: Test get_event_scripts returns correct scripts for a chapter
    function get_event_scripts(chapter_id):
        return _event_scripts.get(chapter_id, [])

    # TDD: Test get_promotion_gains returns correct stat/rank changes
    function get_promotion_gains(base_class_id, promoted_class_id):
        # Find the specific promotion path in _promotion_data
        pass

    # TDD: Test get_weapon_triangle_bonus calculates bonus correctly
    function get_weapon_triangle_bonus(attacker_type, defender_type):
        # Implement logic based on Thracia rules (Swords > Axes > Lances > Swords; Fire > Wind > Thunder > Fire; Light/Dark > Anima)
        # Return +5, -5, or 0
        pass

    # ... other accessor functions for skills, etc.

    # --- Helper Functions ---
    function load_yaml_or_json(filepath):
        # Logic to load file based on extension
        pass

    function validate_loaded_data():
        # Optional: Check data integrity
        pass