import sys
import os

# Add the project root directory (parent of 'tests') to the Python path.
# This allows tests to correctly import modules from the 'src' directory
# as 'src.module_name'.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

@pytest.fixture(scope="function", autouse=True)
def clear_tileset_registry_globally():
    """
    Clears the global TILESET_REGISTRY from src.map_system.tileset
    before and after each test function. This ensures test isolation when
    Tileset instances are created, preventing ID collision errors.
    """
    try:
        import src.map_system.tileset as tileset_module
        if hasattr(tileset_module, 'TILESET_REGISTRY'):
            tileset_module.TILESET_REGISTRY.clear()
    except ImportError:
        # If the module or registry doesn't exist for some reason,
        # this fixture shouldn't cause tests to fail.
        pass
    
    yield # Test runs here
    
    try:
        import src.map_system.tileset as tileset_module # Re-import in case of module manipulation
        if hasattr(tileset_module, 'TILESET_REGISTRY'):
            tileset_module.TILESET_REGISTRY.clear() # Clear after test too
    except ImportError:
        pass

@pytest.fixture(scope="function", autouse=True)
def clear_map_registry_globally():
    """
    Clears the global MAP_REGISTRY from src.map_system.map
    before and after each test function. This ensures test isolation when
    Map instances are created, preventing ID collision errors.
    """
    try:
        import src.map_system.map as map_module
        if hasattr(map_module, 'MAP_REGISTRY'):
            map_module.MAP_REGISTRY.clear()
    except ImportError:
        pass # Module or registry might not exist yet, fixture shouldn't fail tests

    yield # Test runs here

    try:
        import src.map_system.map as map_module # Re-import
        if hasattr(map_module, 'MAP_REGISTRY'):
            map_module.MAP_REGISTRY.clear()
    except ImportError:
        pass