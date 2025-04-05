#!/usr/bin/env python3
"""
Thracia 776 Recreation - Main Entry Point
This file serves as the entry point for the Thracia 776 recreation project.
It initializes the game components and runs the game loop.
"""

import os
import sys
from typing import Dict, Any

# Import core components
from thracia776.data.static_data_loader import StaticDataLoader
from thracia776.data.unit_manager import UnitManager
from thracia776.data.item_manager import ItemManager
from thracia776.data.map_manager import MapManager
from thracia776.data.models import Affiliation, TerrainType, MovementType

def setup_test_data(data_path: str) -> None:
    """
    Creates test data files for development purposes.
    Args:
        data_path: Path to the data directory.
    """
    import json
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs(data_path, exist_ok=True)
    
    # Create test item definitions
    items = {
        "iron_sword": {
            "name": "Iron Sword",
            "type": "WEAPON",
            "weapon_type": "SWORD",
            "might": 5,
            "hit": 90,
            "crit": 0,
            "weight": 5,
            "range_min": 1,
            "range_max": 1,
            "uses": 46,
            "max_uses": 46,
            "rank_req": "E",
            "value": 460
        },
        "iron_lance": {
            "name": "Iron Lance",
            "type": "WEAPON",
            "weapon_type": "LANCE",
            "might": 7,
            "hit": 80,
            "crit": 0,
            "weight": 8,
            "range_min": 1,
            "range_max": 1,
            "uses": 45,
            "max_uses": 45,
            "rank_req": "E",
            "value": 450
        },
        "vulnerary": {
            "name": "Vulnerary",
            "type": "USABLE",
            "might": 0,
            "hit": 0,
            "crit": 0,
            "weight": 1,
            "uses": 3,
            "max_uses": 3,
            "value": 300
        }
    }
    
    # Create test class definitions
    classes = {
        "lord": {
            "name": "Lord",
            "movement_type": "INFANTRY",
            "is_mounted": False,
            "base_stats": {
                "hp": 20,
                "max_hp": 20,
                "strength": 5,
                "magic": 0,
                "skill": 5,
                "speed": 6,
                "luck": 5,
                "defense": 4,
                "constitution": 6,
                "movement": 6
            },
            "growths": {
                "hp": 70,
                "strength": 35,
                "magic": 10,
                "skill": 40,
                "speed": 40,
                "luck": 25,
                "defense": 25,
                "constitution": 5,
                "movement": 2
            },
            "weapon_ranks": {
                "sword": "D",
                "lance": "E"
            }
        },
        "cavalier": {
            "name": "Cavalier",
            "movement_type": "CAVALRY",
            "is_mounted": True,
            "base_stats": {
                "hp": 22,
                "max_hp": 22,
                "strength": 6,
                "magic": 0,
                "skill": 4,
                "speed": 5,
                "luck": 2,
                "defense": 6,
                "constitution": 9,
                "movement": 7
            },
            "growths": {
                "hp": 75,
                "strength": 40,
                "magic": 5,
                "skill": 35,
                "speed": 35,
                "luck": 20,
                "defense": 30,
                "constitution": 5,
                "movement": 1
            },
            "weapon_ranks": {
                "sword": "D",
                "lance": "D"
            }
        }
    }
    
    # Create test terrain definitions
    terrain = {
        "plain": {
            "type": "PLAIN",
            "def_bonus": 0,
            "avo_bonus": 0,
            "movement_costs": {
                "INFANTRY": 1,
                "CAVALRY": 1,
                "ARMOR": 1,
                "FLIER": 1
            },
            "blocks_vision": False,
            "is_impassable": False
        },
        "forest": {
            "type": "FOREST",
            "def_bonus": 1,
            "avo_bonus": 20,
            "movement_costs": {
                "INFANTRY": 2,
                "CAVALRY": 3,
                "ARMOR": 2,
                "FLIER": 1
            },
            "blocks_vision": True,
            "is_impassable": False
        },
        "mountain": {
            "type": "MOUNTAIN",
            "def_bonus": 2,
            "avo_bonus": 30,
            "movement_costs": {
                "INFANTRY": 4,
                "CAVALRY": 99,  # Impassable
                "ARMOR": 99,    # Impassable
                "FLIER": 1
            },
            "blocks_vision": True,
            "is_impassable": False
        },
        "wall": {
            "type": "WALL",
            "def_bonus": 0,
            "avo_bonus": 0,
            "movement_costs": {
                "INFANTRY": 99,  # Impassable
                "CAVALRY": 99,   # Impassable
                "ARMOR": 99,     # Impassable
                "FLIER": 99      # Impassable
            },
            "blocks_vision": True,
            "is_impassable": True
        }
    }
    
    # Create test map data
    map_data = {
        "ch1": {
            "name": "Chapter 1: The Warrior of Fiana",
            "width": 15,
            "height": 10,
            "terrain_layout": [
                ["plain", "plain", "plain", "plain", "plain", "forest", "forest", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"],
                ["plain", "plain", "plain", "plain", "forest", "forest", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"],
                ["plain", "plain", "plain", "forest", "forest", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"],
                ["plain", "plain", "forest", "forest", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"],
                ["plain", "forest", "forest", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"],
                ["forest", "forest", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"],
                ["forest", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"],
                ["plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "mountain", "mountain", "plain", "plain", "plain", "plain"],
                ["plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "mountain", "mountain", "plain", "plain", "plain", "plain", "plain"],
                ["plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain", "plain"]
            ]
        }
    }
    
    # Write test data to files
    with open(os.path.join(data_path, "items.json"), "w") as f:
        json.dump(items, f, indent=2)
        
    with open(os.path.join(data_path, "classes.json"), "w") as f:
        json.dump(classes, f, indent=2)
        
    with open(os.path.join(data_path, "terrain.json"), "w") as f:
        json.dump(terrain, f, indent=2)
        
    with open(os.path.join(data_path, "maps.json"), "w") as f:
        json.dump(map_data, f, indent=2)
        
    print(f"Test data created in {data_path}")

def initialize_game() -> Dict[str, Any]:
    """
    Initializes the game components.
    Returns:
        A dictionary containing the initialized game components.
    """
    # Set up data path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "assets", "data")
    
    # Create test data if it doesn't exist
    if not os.path.exists(data_path) or not os.listdir(data_path):
        print("No data found. Creating test data...")
        setup_test_data(data_path)
    
    # Initialize static data loader
    static_loader = StaticDataLoader(data_path=data_path)
    static_loader.load_all_data()
    
    # Initialize managers
    unit_manager = UnitManager(static_loader)
    item_manager = ItemManager(static_loader)
    map_manager = MapManager(static_loader)
    
    # Return initialized components
    return {
        "static_loader": static_loader,
        "unit_manager": unit_manager,
        "item_manager": item_manager,
        "map_manager": map_manager
    }

def run_test_scenario(components: Dict[str, Any]) -> None:
    """
    Runs a simple test scenario to verify that the game components are working correctly.
    Args:
        components: Dictionary containing the initialized game components.
    """
    static_loader = components["static_loader"]
    unit_manager = components["unit_manager"]
    item_manager = components["item_manager"]
    map_manager = components["map_manager"]
    
    print("\n=== Running Test Scenario ===\n")
    
    # Load the test map
    print("Loading map...")
    map_manager.load_map("ch1")
    map_width, map_height = map_manager.get_map_dimensions()
    print(f"Map dimensions: {map_width}x{map_height}")
    
    # Create test units
    print("\nCreating units...")
    leif = unit_manager.create_unit("leif", "Leif", "lord", Affiliation.PLAYER)
    finn = unit_manager.create_unit("finn", "Finn", "cavalier", Affiliation.PLAYER)
    
    if leif and finn:
        print(f"Created {leif.name} (Level {leif.level} {leif.cls_name})")
        print(f"Created {finn.name} (Level {finn.level} {finn.cls_name})")
        
        # Create test items
        print("\nCreating items...")
        iron_sword = item_manager.create_item("iron_sword")
        iron_lance = item_manager.create_item("iron_lance")
        vulnerary = item_manager.create_item("vulnerary")
        
        if iron_sword and iron_lance and vulnerary:
            print(f"Created {iron_sword.name} (Might: {iron_sword.might}, Uses: {iron_sword.uses})")
            print(f"Created {iron_lance.name} (Might: {iron_lance.might}, Uses: {iron_lance.uses})")
            print(f"Created {vulnerary.name} (Uses: {vulnerary.uses})")
            
            # Place units on the map
            print("\nPlacing units on the map...")
            map_manager.set_unit_on_tile("leif", 2, 2)
            map_manager.set_unit_on_tile("finn", 3, 2)
            
            # Display unit positions
            leif_pos = map_manager.get_unit_position("leif")
            finn_pos = map_manager.get_unit_position("finn")
            print(f"{leif.name} is at position {leif_pos}")
            print(f"{finn.name} is at position {finn_pos}")
            
            # Test level up
            print("\nTesting level up...")
            success, increases = unit_manager.level_up("leif")
            if success:
                print(f"{leif.name} leveled up to Level {leif.level}!")
                print(f"Stat increases: {increases}")
            
            # Test movement range
            print("\nCalculating movement range...")
            leif_movement = map_manager.get_movement_range(leif)
            print(f"{leif.name} can move to {len(leif_movement)} different tiles.")
            
            # Display a simple ASCII map
            print("\nSimple ASCII Map:")
            for y in range(map_height):
                row = ""
                for x in range(map_width):
                    tile = map_manager.get_tile(x, y)
                    if tile:
                        if tile.occupying_unit_id == "leif":
                            row += "L "
                        elif tile.occupying_unit_id == "finn":
                            row += "F "
                        elif tile.terrain_type == TerrainType.PLAIN:
                            row += ". "
                        elif tile.terrain_type == TerrainType.FOREST:
                            row += "T "
                        elif tile.terrain_type == TerrainType.MOUNTAIN:
                            row += "^ "
                        else:
                            row += "? "
                print(row)
    
    print("\n=== Test Scenario Complete ===\n")

def main() -> None:
    """
    Main entry point for the game.
    """
    print("=== Thracia 776 Recreation ===")
    print("Initializing game components...")
    
    try:
        # Initialize game components
        components = initialize_game()
        
        # Run test scenario
        run_test_scenario(components)
        
        print("Game initialization successful!")
        print("This is a placeholder for the actual game loop.")
        print("Future development will implement the full game mechanics.")
        
    except Exception as e:
        print(f"Error initializing game: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())