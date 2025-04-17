"""
Fantasy Tactics Game - Application Class

This module contains the GameApplication class which encapsulates the core
application setup and main loop logic for the game.
"""

import logging
import pygame
from typing import Dict, Any, Optional

# Import core engine components
from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.core_engine.data_provider import DataProvider
from src.core_engine.turn_manager import TurnManager
from src.core_engine.action_handler import ActionHandler
from src.core_engine.event_handler import EventHandler
from src.core_engine.engine import EngineCore
from src.core_engine.engine_api import GameEngineAPI

# Import gameplay systems
from src.gameplay_systems.ai_manager import AIManager
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.inventory_system import InventorySystem
# Import input handler
from src.input.cli_input_handler import CommandLineInputHandler
from src.ui.input_handler import InputHandler
from src.ui.views.map_view import MapView
from src.ui.gui_manager import GUIManager



class GameApplication:
    """
    Main application class that encapsulates the game setup and execution.
    
    This class is responsible for initializing all game components, setting up
    the game environment, and running the main game loop.
    """
    
    def __init__(self, ai_vs_ai: bool = False, ascii_display: bool = False, scenario: Optional[str] = None,
                 use_gui: bool = True, window_width: int = 800, window_height: int = 600):
        """
        Initialize the GameApplication with configuration options.
        
        Args:
            ai_vs_ai: Flag to enable AI vs AI mode (AI controls player units)
            ascii_display: Flag to enable ASCII map display in the console
            scenario: Optional scenario name for testing (loads from data/scenarios/[name])
            use_gui: Flag to enable GUI mode with Pygame
            window_width: Width of the game window in pixels
            window_height: Height of the game window in pixels
        """
        self.ai_vs_ai = ai_vs_ai
        self.ascii_display = ascii_display
        self.scenario = scenario
        self.use_gui = use_gui
        self.window_width = window_width
        self.window_height = window_height
        
        # Core components will be initialized in setup_game()
        self.data_provider = None
        self.game_state_manager = None
        self.turn_manager = None
        self.action_handler = None
        self.event_handler = None
        
        # Gameplay systems
        self.ai_manager = None
        self.combat_system = None
        self.map_system = None
        self.movement_system = None
        self.unit_system = None
        self.inventory_system = None
        
        # Input handler
        self.input_handler = None
        self.gui_input_handler = None
        
        # Engine core
        self.engine = None
        self.game_engine_api = None
        
        # GUI components
        self.display_surface = None
        self.map_view = None
        self.gui_manager = None
        
        # Pygame clock for controlling frame rate
        self.clock = None
    
    def setup_logging(self):
        """Configure basic logging for the application."""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()  # Output to console
            ]
        )
        logging.info("Logging initialized")
    
    def initialize_components(self):
        """Create and initialize all game components."""
        logging.info("Initializing game components...")
        
        # Initialize Pygame if using GUI and not using ASCII display
        if False:  # Disabled Pygame GUI initialization
            # pygame.init()
            # pygame.display.set_caption("Fantasy Tactics Game")
            # self.display_surface = pygame.display.set_mode((self.window_width, self.window_height))
            # self.clock = pygame.time.Clock()
            pass
        
        # Core engine components
        self.data_provider = DataProvider()
        # Load data explicitly after instantiation
        if not self.data_provider.load_all_data("data"):
            logging.error("Failed to load game data. Exiting.")
            return False
        
        self.game_state_manager = GameStateManager(self.data_provider)
        self.turn_manager = TurnManager()
        self.action_handler = ActionHandler()
        self.event_handler = EventHandler()
        
        # Gameplay systems
        self.ai_manager = AIManager()
        self.combat_system = CombatSystem()
        self.map_system = MapSystem()
        self.movement_system = MovementSystem()
        self.unit_system = UnitSystem()
        self.inventory_system = InventorySystem()
        
        # Skip input handler creation in AI vs AI mode
        if not self.ai_vs_ai:
            # Input handler (set interactive=True to enable user input prompts)
            if not self.use_gui:
                self.input_handler = CommandLineInputHandler(interactive=True)
            else:
                # Skip GUI components if ascii_display is enabled
                if self.ascii_display:
                    self.input_handler = CommandLineInputHandler(interactive=True)
                else:
                    # GUI components disabled
                    if False:  # Disabled GUI component creation
                        # self.game_engine_api = GameEngineAPI()
                        #
                        # # Configure map view
                        # map_view_config = {
                        #     'tile_size': 32,
                        #     'grid_color': (100, 100, 100),
                        #     'highlight_color': (255, 255, 0)
                        # }
                        # self.map_view = MapView(self.display_surface, map_view_config)
                        #
                        # # Create GUI input handler
                        # self.gui_input_handler = InputHandler(self.game_engine_api)
                        #
                        # # Create GUI manager
                        # self.gui_manager = GUIManager(self.game_engine_api)
                        # self.gui_manager.map_view = self.map_view
                        # self.gui_manager.input_handler = self.gui_input_handler
                        #
                        # # Use the GUI input handler as the main input handler
                        # self.input_handler = self.gui_input_handler
                        pass
                    
                    # Fallback to CLI input handler when GUI is disabled
                    self.input_handler = CommandLineInputHandler(interactive=True)
        
        return True
    
    def initialize_dependencies(self):
        """Initialize system dependencies in the correct order."""
        logging.info("Initializing system dependencies...")
        
        # Initialize action handler with dependencies
        self.action_handler.initialize(
            gameStateManager_instance=self.game_state_manager,
            unitSystem_instance=self.unit_system,
            mapSystem_instance=self.map_system,
            movementSystem_instance=self.movement_system,
            combatSystem_instance=self.combat_system,
            inventorySystem_instance=self.inventory_system,
            turnManager_instance=self.turn_manager,
            eventHandler_instance=self.event_handler,
            dataProvider_instance=self.data_provider
        )
        
        # Initialize event handler with dependencies
        self.event_handler.initialize(
            gameStateManager_instance=self.game_state_manager,
            turnManager_instance=self.turn_manager,
            unitSystem_instance=self.unit_system,
            mapSystem_instance=self.map_system,
            inventorySystem_instance=self.inventory_system,
            dataProvider_instance=self.data_provider,
            # uiManager_instance=None, # Assuming no UI for now
            aiManager_instance=self.ai_manager
        )
        
        # Initialize inventory system before AI manager since AI manager needs it
        self.inventory_system.initialize(self.game_state_manager, self.data_provider)
        
        # Initialize AI manager with dependencies
        self.ai_manager.initialize(
            gameStateManager_instance=self.game_state_manager,
            unitSystem_instance=self.unit_system,
            mapSystem_instance=self.map_system,
            movementSystem_instance=self.movement_system,
            combatSystem_instance=self.combat_system,
            actionHandler_instance=self.action_handler,
            dataProvider_instance=self.data_provider,
            inventorySystem_instance=self.inventory_system
        )
        
        # Initialize systems in the correct order (dependencies first)
        # First, systems with fewer dependencies
        self.map_system.initialize(self.game_state_manager, self.data_provider)
        # inventory_system already initialized above
        
        # Then systems that depend on the above
        self.unit_system.initialize(self.game_state_manager, self.data_provider)
        self.movement_system.initialize(self.game_state_manager, self.map_system)
        
        # Finally, systems with the most dependencies
        self.combat_system.initialize(
            gameStateManager_instance=self.game_state_manager,
            dataProvider_instance=self.data_provider,
            unitSystem_instance=self.unit_system,
            mapSystem_instance=self.map_system,
            inventorySystem_instance=self.inventory_system
        )
        
        # Initialize the input handler only if not in AI vs AI mode
        if not self.ai_vs_ai and self.input_handler:
            self.input_handler.initialize(
                game_state_manager=self.game_state_manager,
                unit_system=self.unit_system,
                movement_system=self.movement_system,
                map_system=self.map_system,
                inventory_system=self.inventory_system,
                data_provider=self.data_provider
            )
        
        # Update the display module with combat_system after it's initialized (if input handler exists)
        if self.input_handler and hasattr(self.input_handler, 'display') and hasattr(self.input_handler.display, 'combat_system'):
            self.input_handler.display.combat_system = self.combat_system
            
        logging.info("System dependencies initialized.")
        return True
    
    def create_engine(self):
        """Create the engine core with all initialized components."""
        self.engine = EngineCore(
            game_state_manager=self.game_state_manager,
            data_provider=self.data_provider,
            turn_manager=self.turn_manager,
            action_handler=self.action_handler,
            event_handler=self.event_handler,
            ai_manager=self.ai_manager,
            combat_system=self.combat_system,
            map_system=self.map_system,
            movement_system=self.movement_system,
            unit_system=self.unit_system,
            input_handler=None if self.ai_vs_ai else self.input_handler,
            ai_vs_ai=self.ai_vs_ai,
            ascii_display=self.ascii_display
        )
        
        # Initialize game engine API with the engine if using GUI and not using ASCII display
        if False:  # Disabled game engine API initialization
            # if self.use_gui and not self.ascii_display and self.game_engine_api:
            #     self.game_engine_api.engine_core = self.engine
            #     self.game_engine_api.game_state_manager = self.game_state_manager
            #     self.game_engine_api.action_handler = self.action_handler
            pass
            
        return True
    
    def initialize_game(self):
        """Initialize the game with a chapter or scenario."""
        # Default chapter ID
        chapter_id = "test_chapter"
        
        # Initialize the engine with the default chapter or scenario
        if self.scenario:
            logging.info(f"Initializing scenario: {self.scenario}")
            self.engine.initialize_chapter(chapter_id, self.scenario)
        else:
            logging.info(f"Initializing chapter: {chapter_id}")
            self.engine.initialize_chapter(chapter_id)
        
        # Load AI profiles now that game state is initialized
        logging.info("Loading AI profiles...")
        self.ai_manager._load_ai_profiles()  # Call the private method to load profiles
        logging.info("AI profiles loaded.")
        
        return True
    
    def setup_game(self):
        """Set up the game by initializing all components and dependencies."""
        self.setup_logging()
        
        if not self.initialize_components():
            return False
        
        if not self.initialize_dependencies():
            return False
        
        if not self.create_engine():
            return False
        
        if not self.initialize_game():
            return False
        
        return True
    
    def run(self):
        """Run the main game loop."""
        if not self.setup_game():
            logging.error("Failed to set up the game. Exiting.")
            return False
        
        # Run the game loop
        logging.info("Starting game loop")
        
        # Always use the traditional engine game loop, GUI mode disabled
        self.engine.run_game_loop()
        
        if False:  # Disabled Pygame game loop
            # # Use Pygame game loop for GUI mode
            # running = True
            # while running:
            #     # Handle Pygame events
            #     for event in pygame.event.get():
            #         if event.type == pygame.QUIT:
            #             running = False
            #         elif not self.ai_vs_ai and self.gui_input_handler:
            #             # Pass the event to the input handler (if not in AI vs AI mode)
            #             self.gui_input_handler.process_event(event)
            #
            #     # Update game state (placeholder)
            #     # In a real implementation, this would update the game state based on elapsed time
            #
            #     # Render the current view (if GUI manager exists)
            #     if self.gui_manager:
            #         self.gui_manager.render_current_view()
            #
            #     # Update the display
            #     pygame.display.flip()
            #
            #     # Control the frame rate
            #     self.clock.tick(60)  # 60 FPS
            pass
        
        # Clean up Pygame resources
        if False:  # Disabled Pygame cleanup
            # if self.use_gui and not self.ascii_display:
            #     pygame.quit()
            pass
        
        logging.info("Game ended")
        return True