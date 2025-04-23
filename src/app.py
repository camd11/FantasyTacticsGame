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
from src.gameplay_systems.ai.ai_manager import AIManager
from src.gameplay_systems.ai.strategic_evaluator import StrategicEvaluator
from src.gameplay_systems.ai.tactical_executor import TacticalExecutor
from src.gameplay_systems.ai.utility_scorer import UtilityScorer
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.inventory_system import InventorySystem
# Import input handler
from src.input.cli_input_handler import CommandLineInputHandler
from src.input.cli_display import CLIDisplay
from src.ui.input_handler import InputHandler
from src.ui.views.map_view import MapView
from src.ui.gui_manager import GUIManager
from src.utils.visual_logger import VisualScenarioLogger



class GameApplication:
    """
    Main application class that encapsulates the game setup and execution.
    
    This class is responsible for initializing all game components, setting up
    the game environment, and running the main game loop.
    """
    
    def __init__(self, ai_vs_ai: bool = False, ascii_display: bool = False, # scenario: Optional[str] = None,
                 chapter_id: str = '1', # Add chapter_id parameter with default
                 use_gui: bool = True, window_width: int = 800, window_height: int = 600):
        """
        Initialize the GameApplication with configuration options.
        
        Args:
            ai_vs_ai: Flag to enable AI vs AI mode (AI controls player units)
            ascii_display: Flag to enable ASCII map display in the console
            # scenario: Optional scenario name for testing (loads from data/scenarios/[name]) # Removed
            chapter_id: The ID of the chapter to load (default: '1')
            use_gui: Flag to enable GUI mode with Pygame
            window_width: Width of the game window in pixels
            window_height: Height of the game window in pixels
        """
        self.ai_vs_ai = ai_vs_ai
        self.ascii_display = ascii_display
        # self.scenario = scenario # Removed
        self.chapter_id = chapter_id # Store chapter_id
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
        # self.visual_logger = None # Remove initialization here
    
    def setup_logging(self):
        """Configure basic logging for the application."""
        # Create formatters
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create handlers
        console_handler = logging.StreamHandler()  # Output to console
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Create file handler for AI logs
        ai_file_handler = logging.FileHandler('ai_behavior.log', mode='w')
        ai_file_handler.setFormatter(file_formatter)
        ai_file_handler.setLevel(logging.DEBUG)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(ai_file_handler)
        
        # Configure AI-specific loggers to ensure they output to the file
        ai_logger = logging.getLogger('src.gameplay_systems.ai')
        ai_logger.setLevel(logging.DEBUG)
        
        logging.info("Logging initialized with AI behavior logging to ai_behavior.log")
    
    def initialize_components(self):
        """Create and initialize all game components."""
        logging.info("Initializing game components...")
        
        # Initialize Pygame if using GUI
        if self.use_gui:
            pygame.init()
            pygame.display.set_caption("Fantasy Tactics Game")
            self.display_surface = pygame.display.set_mode((self.window_width, self.window_height))
            self.clock = pygame.time.Clock()
            logging.info("Pygame initialized with display size %dx%d", self.window_width, self.window_height)
        
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
        # Create AI components
        utility_scorer = UtilityScorer(self.game_state_manager)
        strategic_evaluator = StrategicEvaluator(utility_scorer)
        tactical_executor = TacticalExecutor()
        self.ai_manager = AIManager(strategic_evaluator, tactical_executor, self.game_state_manager)
        self.combat_system = CombatSystem()
        self.map_system = MapSystem()
        self.movement_system = MovementSystem()
        self.unit_system = UnitSystem()
        self.inventory_system = InventorySystem()
        
        # Create CLIDisplay if needed for ASCII mode (even in AI vs AI)
        if self.ascii_display:
            self.display = CLIDisplay()
            logging.info("CLIDisplay created for ASCII mode.")

        # Skip input handler creation in AI vs AI mode
        if not self.ai_vs_ai:
            # Input handler (set interactive=True to enable user input prompts)
            if not self.use_gui:
                # Create CLIDisplay instance first if not already created for ASCII
                if not hasattr(self, 'display'):
                    self.display = CLIDisplay()
                self.input_handler = CommandLineInputHandler(display=self.display, interactive=True)
            else:
                # If using GUI but ASCII display is also enabled, create both
                if self.ascii_display:
                    # CLIDisplay should already be created above
                    if hasattr(self, 'display'):
                        self.input_handler = CommandLineInputHandler(display=self.display, interactive=True)
                    else:
                        # Fallback/Error case - should not happen if ascii_display is true
                        logging.error("CLIDisplay expected but not found for ASCII mode.")
                        self.display = CLIDisplay() # Create anyway?
                        self.input_handler = CommandLineInputHandler(display=self.display, interactive=True)
                else:
                    # Initialize GUI components only
                    self.game_engine_api = GameEngineAPI()
                    
                    # Configure map view
                    map_view_config = {
                        'tile_size': 32,
                        'grid_color': (100, 100, 100),
                        'highlight_color': (255, 255, 0),
                        'move_range_color': (0, 255, 0, 128),
                        'attack_range_color': (255, 0, 0, 128)
                    }
                    
                    self.map_view = MapView(self.display_surface, map_view_config)
                    self.gui_manager = GUIManager(self.game_engine_api)
                    
                    # Configure input handler for GUI
                    self.gui_input_handler = InputHandler(self.gui_manager)

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
            dataProvider_instance=self.data_provider,
            core_turn_manager_instance=self.turn_manager,
            visual_logger=getattr(self, 'visual_logger', None) # Use getattr safely
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
        # Initialize tactical executor with required systems
        tactical_executor = self.ai_manager.tactical_executor
        tactical_executor.movement_system = self.movement_system
        tactical_executor.combat_system = self.combat_system
        
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
        
        # Update the display module with required systems after they are initialized
        if hasattr(self, 'display') and isinstance(self.display, CLIDisplay):
            logging.info("Assigning required systems to CLIDisplay.")
            self.display.game_state_manager = self.game_state_manager
            self.display.unit_system = self.unit_system
            self.display.map_system = self.map_system
            self.display.movement_system = self.movement_system
            self.display.combat_system = self.combat_system
            self.display.data_provider = self.data_provider

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
            ascii_display=self.ascii_display,
            display=getattr(self, 'display', None),
            # visual_logger=self.visual_logger # Removed from here
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
        """Initializes the game engine systems and loads the scenario."""
        logging.info("Initializing engine systems and loading scenario...")
        if not self.engine:
            logging.error("EngineCore not created before initializing game.")
            return False

        # Corrected: Call initialize_chapter instead of initialize_systems
        # Determine scenario name for logging/loading purposes
        # scenario_name = self.scenario if self.scenario else None # Already have self.scenario
        chapter_id_to_use = self.chapter_id # Use the chapter ID provided at app init

        # Load the chapter/scenario data and initialize engine internal state
        try:
            self.engine.initialize_chapter(chapter_id=chapter_id_to_use, scenario_name=self.scenario)
            logging.info(f"EngineCore chapter/scenario initialized: Chapter '{chapter_id_to_use}', Scenario '{self.scenario}'")
        except Exception as e:
            logging.error(f"Failed during EngineCore.initialize_chapter: {e}", exc_info=True)
            return False

        # ---- NEW LOCATION for VisualScenarioLogger Initialization ----
        visual_logger = None # Default to None
        # Check if conditions for visual logger are met (requires CLIDisplay which should be ready now)
        if self.game_state_manager and hasattr(self, 'display') and isinstance(self.display, CLIDisplay):
            try:
                 # Try to initialize the logger
                 visual_logger = VisualScenarioLogger(self.game_state_manager, self.display, enabled=True)
                 logging.info("VisualScenarioLogger initialized successfully.")
            except Exception as e:
                 logging.error(f"Failed to initialize VisualScenarioLogger: {e}")
        else:
            # Refine warning/info message based on why it failed
            if not self.game_state_manager:
                 logging.warning("Cannot initialize VisualScenarioLogger: GameStateManager not ready.")
            elif not (hasattr(self, 'display') and isinstance(self.display, CLIDisplay)):
                 logging.info("VisualScenarioLogger not initialized (requires CLIDisplay, which was not created/ready).")
            else: # Should not be reached if logic is correct
                 logging.warning("Cannot initialize VisualScenarioLogger for unknown reason.")

        # Pass the logger (or None) to the engine and log initial state
        if self.engine:
            if visual_logger:
                self.engine.set_visual_logger(visual_logger)
                # Trigger initial state log *after* setting the logger in the engine
                self.engine.log_initial_visual_state()
            else:
                logging.info("Visual logger was not created, engine will run without it.")


        logging.info("Engine systems initialized and scenario loaded.")
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
        # Set up the game
        if not self.setup_game():
            logging.error("Failed to set up game. Exiting.")
            return False
        
        logging.info("Starting game loop...")
        
        # Run the appropriate game loop based on mode
        if self.use_gui:
            return self._run_gui_loop()
        else:
            return self._run_cli_loop()
    
    def _run_cli_loop(self):
        """Run the command-line interface game loop."""
        try:
            # Main game loop - continue until player quits or game ends
            while True:
                # Process the current turn
                current_turn = self.engine.get_current_turn()
                current_phase = self.engine.get_current_phase()
                logging.info(f"Processing turn {current_turn}, phase {current_phase}")
                
                # Get input based on the current phase
                if current_phase == PhaseEnum.PLAYER:
                    # In AI vs AI mode, delegate to AI
                    if self.ai_vs_ai:
                        logging.info("AI vs AI mode active: AI handling player phase")
                        self.engine.process_ai_turn(FactionEnum.PLAYER)
                    else:
                        # Otherwise, get player input
                        self.engine.process_player_input()
                        
                elif current_phase == PhaseEnum.ENEMY:
                    # Enemy phase handled by AI
                    logging.info("Processing enemy phase")
                    self.engine.process_ai_turn(FactionEnum.ENEMY)
                    
                elif current_phase == PhaseEnum.ALLY:
                    # Ally phase handled by AI or player depending on mode
                    if self.ai_vs_ai:
                        logging.info("AI handling ally phase")
                        self.engine.process_ai_turn(FactionEnum.ALLY)
                    else:
                        logging.info("Processing ally phase")
                        self.engine.process_ally_phase()
                        
                # Check if the game has ended
                if self.engine.is_game_over():
                    winner = self.engine.get_winner()
                    logging.info(f"Game over! Winner: {winner}")
                    break
                
                # Sleep briefly to prevent CPU overuse
                # time.sleep(0.05)
                
        except KeyboardInterrupt:
            logging.info("Game interrupted by user. Exiting.")
            
        except Exception as e:
            logging.exception(f"Error in game loop: {e}")
            
        finally:
            logging.info("Game loop ended.")
            
        return True
    
    def _run_gui_loop(self):
        """Run the graphical user interface game loop."""
        try:
            # Main game loop for GUI mode
            running = True
            while running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        # Handle keyboard input
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        # Add more key controls as needed
                        logging.info(f"Key pressed: {pygame.key.name(event.key)}")
                    # Add mouse event handling here
                
                # Update game state
                if not self.engine.is_game_over():
                    current_phase = self.engine.get_current_phase()
                    
                    # Process AI turns automatically
                    if current_phase == PhaseEnum.ENEMY:
                        self.engine.process_ai_turn(FactionEnum.ENEMY)
                    elif current_phase == PhaseEnum.ALLY and self.ai_vs_ai:
                        self.engine.process_ai_turn(FactionEnum.ALLY)
                    elif current_phase == PhaseEnum.PLAYER and self.ai_vs_ai:
                        self.engine.process_ai_turn(FactionEnum.PLAYER)
                    
                    # Player input is handled through the GUI events
                
                # Render the game
                self.display_surface.fill((0, 0, 0))  # Clear screen
                
                # Render map and units
                if self.map_view:
                    map_data = self.game_state_manager.get_map_data()
                    unit_data = self.game_state_manager.get_unit_data()
                    
                    self.map_view.render_map(map_data)
                    self.map_view.render_units(unit_data)
                
                # Update the display
                pygame.display.flip()
                
                # Control frame rate
                self.clock.tick(60)
                
                # Check game over condition
                if self.engine.is_game_over():
                    winner = self.engine.get_winner()
                    logging.info(f"Game over! Winner: {winner}")
                    # Display game over message
                    # Wait for user to close window
            
        except Exception as e:
            logging.exception(f"Error in GUI game loop: {e}")
            
        finally:
            pygame.quit()
            logging.info("GUI game loop ended.")
            
        return True

# --- Main Execution Block ---

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Fantasy Tactics Game.")
    parser.add_argument('--ai-vs-ai', action='store_true', help="Enable AI vs AI mode.")
    parser.add_argument('--ascii', action='store_true', help="Enable ASCII display mode.")
    parser.add_argument('--scenario', type=str, help="Load a specific scenario for testing.", default=None)
    parser.add_argument('--chapter', type=str, default='1', help="Specify the chapter ID to load.")
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level.")
    
    args = parser.parse_args()
    
    # Set log level based on arguments
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level)
    logging.getLogger('src').setLevel(log_level)

    app = GameApplication(
        ai_vs_ai=args.ai_vs_ai,
        ascii_display=args.ascii,
        scenario=args.scenario,
        chapter_id=args.chapter, # Pass chapter_id to constructor
        use_gui=False # GUI mode is currently disabled
    )
    
    if app.run():
        logging.info("Game finished successfully.")
    else:
        logging.error("Game exited with errors.")
        sys.exit(1)