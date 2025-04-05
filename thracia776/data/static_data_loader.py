import json
import yaml  # Assuming YAML might be used, add import
from typing import Any, Dict, Optional

# Placeholder for actual data models if needed later
# from thracia776.data.models import ItemDefinition, ClassData, TerrainData

class StaticDataLoader:
    """
    Loads and provides access to static game data like item definitions,
    class stats, terrain info, etc., typically loaded from files.
    """
    def __init__(self, data_path: str = "assets/data"):
        """
        Initializes the loader, potentially pre-loading some data.
        Args:
            data_path: The base directory where static data files are located.
        """
        self.data_path = data_path
        self._item_definitions: Dict[str, Any] = {}
        self._class_data: Dict[str, Any] = {}
        self._terrain_data: Dict[str, Any] = {}
        self._map_data: Dict[str, Any] = {}
        # Add other data caches as needed

        # Example: Pre-load data on initialization (optional)
        # self.load_all_data()

    def _load_json(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Helper to load data from a JSON file."""
        file_path = f"{self.data_path}/{file_name}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Data file not found: {file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Warning: Error decoding JSON from file: {file_path}")
            return None

    def _load_yaml(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Helper to load data from a YAML file."""
        file_path = f"{self.data_path}/{file_name}.yaml"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Data file not found: {file_path}")
            return None
        except yaml.YAMLError:
            print(f"Warning: Error decoding YAML from file: {file_path}")
            return None

    def load_item_definitions(self, file_name: str = "items"):
        """Loads item definitions from a specified file (e.g., items.json)."""
        data = self._load_json(file_name) # Or _load_yaml
        if data:
            self._item_definitions = data # Assuming data is a dict {item_name: definition}
        print(f"Loaded {len(self._item_definitions)} item definitions.")

    def load_class_data(self, file_name: str = "classes"):
        """Loads class data from a specified file (e.g., classes.json)."""
        data = self._load_json(file_name) # Or _load_yaml
        if data:
            self._class_data = data # Assuming data is a dict {class_name: data}
        print(f"Loaded {len(self._class_data)} class definitions.")

    def load_terrain_data(self, file_name: str = "terrain"):
        """Loads terrain data from a specified file (e.g., terrain.json)."""
        data = self._load_json(file_name) # Or _load_yaml
        if data:
            self._terrain_data = data # Assuming data is a dict {terrain_name: data}
        print(f"Loaded {len(self._terrain_data)} terrain definitions.")

    def load_map_data(self, file_name: str = "maps"):
        """Loads map data from a specified file (e.g., maps.json)."""
        data = self._load_json(file_name) # Or _load_yaml
        if data:
            self._map_data = data # Assuming data is a dict {map_id: map_data}
        print(f"Loaded {len(self._map_data)} map definitions.")

    def load_all_data(self):
        """Loads all known static data types."""
        print("Loading all static data...")
        self.load_item_definitions()
        self.load_class_data()
        self.load_terrain_data()
        self.load_map_data()
        # Load other data types here
        print("Static data loading complete.")

    def get_item_definition(self, item_name: str) -> Optional[Any]:
        """
        Retrieves the static definition for a given item name.
        Args:
            item_name: The unique name or ID of the item.
        Returns:
            The item's static data (e.g., a dictionary), or None if not found.
        """
        return self._item_definitions.get(item_name)

    def get_class_data(self, class_name: str) -> Optional[Any]:
        """
        Retrieves the static data for a given class name.
        Args:
            class_name: The unique name or ID of the class.
        Returns:
            The class's static data (e.g., a dictionary), or None if not found.
        """
        return self._class_data.get(class_name)

    def get_terrain_data(self, terrain_name: str) -> Optional[Any]:
        """
        Retrieves the static data for a given terrain type name.
        Args:
            terrain_name: The unique name or ID of the terrain type.
        Returns:
            The terrain's static data (e.g., a dictionary), or None if not found.
        """
        return self._terrain_data.get(terrain_name)

    def get_map_data(self, map_id: str) -> Optional[Any]:
        """
        Retrieves the static data for a given map ID.
        Args:
            map_id: The unique ID of the map.
        Returns:
            The map's static data (e.g., a dictionary), or None if not found.
        """
        return self._map_data.get(map_id)

# Example Usage (Optional - for testing)
if __name__ == "__main__":
    # Assume assets/data/items.json and assets/data/classes.json exist for testing
    # Create dummy files if needed
    # Example: {"Sword": {"type": "Weapon", "might": 5, "weight": 8}}
    # Example: {"Lord": {"base_hp": 18, "move": 5}}

    loader = StaticDataLoader(data_path="../../assets/data") # Adjust path if running directly
    loader.load_all_data()

    sword_data = loader.get_item_definition("Sword")
    if sword_data:
        print(f"Sword Data: {sword_data}")
    else:
        print("Sword definition not found.")

    lord_data = loader.get_class_data("Lord")
    if lord_data:
        print(f"Lord Data: {lord_data}")
    else:
        print("Lord class data not found.")
