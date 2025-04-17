import unittest
from unittest.mock import Mock, MagicMock

# Import the GUIManager class
from src.ui.gui_manager import GUIManager


class TestGUIManager(unittest.TestCase):
    """Test cases for the GUIManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for all the dependencies
        self.mock_game_engine_api = Mock()
        self.mock_game_engine_api.get_initial_state.return_value = {
            'map_data': {'width': 10, 'height': 10, 'tiles': []},
            'unit_list': []
        }
        
        # Since the module doesn't exist yet, we'll create mock objects directly
        # instead of patching the imports
        self.mock_map_view_class = Mock()
        self.mock_unit_info_panel_class = Mock()
        self.mock_terrain_info_panel_class = Mock()
        self.mock_action_menu_class = Mock()
        self.mock_combat_preview_class = Mock()
        self.mock_inventory_manager_class = Mock()
        self.mock_system_menu_class = Mock()
        self.mock_input_handler_class = Mock()
        
        # Create mock instances that will be returned when the classes are instantiated
        self.mock_map_view_instance = Mock()
        self.mock_unit_info_panel_instance = Mock()
        self.mock_terrain_info_panel_instance = Mock()
        self.mock_action_menu_instance = Mock()
        self.mock_combat_preview_instance = Mock()
        self.mock_inventory_manager_instance = Mock()
        self.mock_system_menu_instance = Mock()
        self.mock_input_handler_instance = Mock()
        
        # Configure the mocks to return the mock instances
        self.mock_map_view_class.return_value = self.mock_map_view_instance
        self.mock_unit_info_panel_class.return_value = self.mock_unit_info_panel_instance
        self.mock_terrain_info_panel_class.return_value = self.mock_terrain_info_panel_instance
        self.mock_action_menu_class.return_value = self.mock_action_menu_instance
        self.mock_combat_preview_class.return_value = self.mock_combat_preview_instance
        self.mock_inventory_manager_class.return_value = self.mock_inventory_manager_instance
        self.mock_system_menu_class.return_value = self.mock_system_menu_instance
        self.mock_input_handler_class.return_value = self.mock_input_handler_instance

    def test_gui_manager_initialization(self):
        """Test that GUIManager can be instantiated with the required dependencies."""
        # Import the GUIManager class now that it's implemented
        from src.ui.gui_manager import GUIManager
        
        # Create a GUIManager instance
        gui_manager = GUIManager(self.mock_game_engine_api)
        
        # Assert that GUIManager was initialized with the mock game engine API
        self.assertEqual(gui_manager.game_engine_api, self.mock_game_engine_api)
        
        # Assert that GUIManager initialized its components
        self.assertIsNotNone(gui_manager.map_view)
        self.assertIsNotNone(gui_manager.unit_info_panel)
        self.assertIsNotNone(gui_manager.terrain_info_panel)
        self.assertIsNotNone(gui_manager.action_menu)
        self.assertIsNotNone(gui_manager.combat_preview)
        self.assertIsNotNone(gui_manager.inventory_manager)
        self.assertIsNotNone(gui_manager.system_menu)
        self.assertIsNotNone(gui_manager.input_handler)
        
        # Assert that the callback was registered with the game engine API
        self.mock_game_engine_api.register_state_update_callback.assert_called_once()

    def test_update_game_state(self):
        """Test that GUIManager updates its components when the game state changes."""
        # Import the GUIManager class
        from src.ui.gui_manager import GUIManager
        
        # Create a GUIManager instance
        gui_manager = GUIManager(self.mock_game_engine_api)
        
        # Replace the map_view with our mock
        gui_manager.map_view = self.mock_map_view_instance
        
        # Create a mock game state
        mock_game_state = {
            'map_data': {'width': 10, 'height': 10, 'tiles': []},
            'unit_list': [{'id': 1, 'x': 5, 'y': 5}]
        }
        
        # Call update_game_state
        gui_manager.update_game_state(mock_game_state)
        
        # Assert that the map_view was updated with the new state
        self.mock_map_view_instance.update_data.assert_called_once_with(
            mock_game_state['map_data'], mock_game_state['unit_list']
        )
        
        # Assert that render_all was called
        self.assertTrue(self.mock_map_view_instance.render.called)

    def test_handle_input_event(self):
        """Test that GUIManager correctly routes input events to the appropriate handlers."""
        # Import the GUIManager class
        from src.ui.gui_manager import GUIManager
        
        # Create a GUIManager instance
        gui_manager = GUIManager(self.mock_game_engine_api)
        
        # Mock the process_map_click method
        gui_manager.process_map_click = Mock()
        
        # Create a map click event
        event_type = 'MAP_CLICK'
        details = {'x': 5, 'y': 5}
        
        # Call handle_input_event
        gui_manager.handle_input_event(event_type, details)
        
        # Assert that process_map_click was called with the correct arguments
        gui_manager.process_map_click.assert_called_once_with(5, 5)

    def test_gui_manager_renders_view(self):
        """Test that GUIManager correctly renders the current view by calling appropriate methods."""
        # Create mock objects for the dependencies
        mock_game_engine_api = Mock()
        mock_view = Mock()
        mock_input_handler = Mock()
        
        # Configure the mock game_engine_api to return mock data
        mock_map_data = {'width': 10, 'height': 10, 'tiles': [['grass' for _ in range(10)] for _ in range(10)]}
        mock_unit_data = [{'id': 1, 'position': (3, 4)}, {'id': 2, 'position': (7, 8)}]
        mock_game_engine_api.get_map_data.return_value = mock_map_data
        mock_game_engine_api.get_unit_data.return_value = mock_unit_data
        
        # Configure get_initial_state to return a properly structured dictionary
        mock_game_engine_api.get_initial_state.return_value = {
            'map_data': {'width': 10, 'height': 10, 'tiles': []},
            'unit_list': []
        }
        
        # Import the GUIManager class
        from src.ui.gui_manager import GUIManager
        
        # Create a GUIManager instance with our mocks
        gui_manager = GUIManager(mock_game_engine_api)
        
        # Replace the map_view with our mock view
        gui_manager.map_view = mock_view
        
        # Call the render_current_view method (which doesn't exist yet, so this should fail)
        gui_manager.render_current_view()
        
        # Assert that the game_engine_api was queried for map and unit data
        mock_game_engine_api.get_map_data.assert_called_once()
        mock_game_engine_api.get_unit_data.assert_called_once()
        
        # Assert that the view's render_map method was called with the map data
        mock_view.render_map.assert_called_once_with(mock_map_data)
        
        # Assert that the view's render_units method was called with the unit data
        mock_view.render_units.assert_called_once_with(mock_unit_data)


if __name__ == "__main__":
    unittest.main()