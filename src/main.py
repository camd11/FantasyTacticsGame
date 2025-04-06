"""
Fantasy Tactics Game - Main Entry Point

This script serves as the main entry point for the game. It initializes all necessary
components, loads the game data, and starts the game loop.
"""

import logging
from typing import Dict, Any, Optional

# Import core engine components
from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.core_engine.data_provider import DataProvider
from src.core_engine.turn_manager import TurnManager
from src.core_engine.action_handler import ActionHandler
from src.core_engine.event_handler import EventHandler
from src.core_engine.engine import EngineCore

# Import gameplay systems
from src.gameplay_systems.ai_manager import AIManager
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.inventory_system import InventorySystem


# Import input handler
from src.input.cli_input_handler import CommandLineInputHandler


def setup_logging():
    """Configure basic logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Output to console
        ]
    )
    logging.info("Logging initialized")


def main():
    """Main entry point for the game."""
    # Set up logging
    setup_logging()
    
    # Create all necessary components
    logging.info("Initializing game components...")
    
    # Core engine components
    data_provider = DataProvider()
    # Load data explicitly after instantiation
    if not data_provider.load_all_data("data"):
        logging.error("Failed to load game data. Exiting.")
        return
    game_state_manager = GameStateManager(data_provider)
    turn_manager = TurnManager()
    action_handler = ActionHandler()
    event_handler = EventHandler()
    
    # Gameplay systems
    ai_manager = AIManager()
    combat_system = CombatSystem()
    map_system = MapSystem()
    movement_system = MovementSystem()
    unit_system = UnitSystem()
    inventory_system = InventorySystem()
    
    # Input handler (set interactive=True to enable user input prompts)
    input_handler = CommandLineInputHandler(interactive=False)

    # --- Initialize systems with dependencies ---
    # Order might matter depending on specific initialize implementations
    logging.info("Initializing system dependencies...")
    # GameStateManager takes dependencies in __init__, no initialize method needed here
    turn_manager.initialize(game_state_manager, event_handler) # Assuming TurnManager needs these
    action_handler.initialize(
        gameStateManager_instance=game_state_manager,
        unitSystem_instance=unit_system,
        mapSystem_instance=map_system,
        movementSystem_instance=movement_system,
        combatSystem_instance=combat_system,
        inventorySystem_instance=inventory_system,
        turnManager_instance=turn_manager,
        eventHandler_instance=event_handler,
        dataProvider_instance=data_provider
    )
    event_handler.initialize(
        gameStateManager_instance=game_state_manager,
        turnManager_instance=turn_manager,
        unitSystem_instance=unit_system,
        mapSystem_instance=map_system,
        inventorySystem_instance=inventory_system,
        dataProvider_instance=data_provider,
        # uiManager_instance=None, # Assuming no UI for now
        aiManager_instance=ai_manager
    )
    ai_manager.initialize(
        gameStateManager_instance=game_state_manager,
        unitSystem_instance=unit_system,
        mapSystem_instance=map_system,
        movementSystem_instance=movement_system,
        combatSystem_instance=combat_system,
        actionHandler_instance=action_handler,
        dataProvider_instance=data_provider
    )
    # Initialize systems in the correct order (dependencies first)
    # First, systems with fewer dependencies
    map_system.initialize(game_state_manager, data_provider)
    inventory_system.initialize(game_state_manager, data_provider) # Assuming similar pattern
    
    # Then systems that depend on the above
    unit_system.initialize(game_state_manager, data_provider) # Correct parameters
    movement_system.initialize(game_state_manager, map_system)
    
    # Finally, systems with the most dependencies
    combat_system.initialize(
        gameStateManager_instance=game_state_manager,
        dataProvider_instance=data_provider,
        unitSystem_instance=unit_system,
        mapSystem_instance=map_system,
        inventorySystem_instance=inventory_system
    )
    logging.info("System dependencies initialized.")

    # Create the engine core
    engine = EngineCore(
        game_state_manager=game_state_manager,
        data_provider=data_provider,
        turn_manager=turn_manager,
        action_handler=action_handler,
        event_handler=event_handler,
        ai_manager=ai_manager,
        combat_system=combat_system,
        map_system=map_system,
        movement_system=movement_system,
        input_handler=input_handler
    )
    
    # Default chapter ID
    chapter_id = "chapter1"
    # Initialize the engine with the default chapter
    logging.info(f"Initializing chapter: {chapter_id}")
    engine.initialize_chapter(chapter_id)

    # Load AI profiles now that game state is initialized
    logging.info("Loading AI profiles...")
    ai_manager._load_ai_profiles() # Call the private method to load profiles
    logging.info("AI profiles loaded.")
    
    # Run the game loop
    logging.info("Starting game loop")
    engine.run_game_loop()
    
    logging.info("Game ended")


if __name__ == "__main__":
    main()