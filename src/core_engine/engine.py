"""
Engine Core Module

This module is the central orchestrator of the game. It manages the main game loop,
controls turn and phase transitions, processes player input and AI actions, triggers events,
and checks for victory or defeat conditions.
"""

import logging
import random
from typing import Dict, List, Tuple, Optional, Any, Callable

# Core Engine Components
from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum, StatusEffectEnum
from src.core_engine.data_provider import DataProvider
from src.core_engine.turn_manager import TurnManager
from src.core_engine.action_handler import ActionHandler
from src.core_engine.event_handler import EventHandler

# Gameplay Systems
from src.gameplay_systems.ai_manager import AIManager
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.inventory_system import InventorySystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.movement_system import MovementSystem
from src.gameplay_systems.unit_system import UnitSystem

# Input Handling (Assuming an InputHandler class exists or will be provided)
# from src.input.input_handler import InputHandler # Example import

# Enums and Constants
PHASE_PLAYER = PhaseEnum.PLAYER
PHASE_ENEMY = PhaseEnum.ENEMY
PHASE_NPC = PhaseEnum.NPC

STATUS_SLEEP = StatusEffectEnum.SLEEP
STATUS_PETRIFY = StatusEffectEnum.SLEEP  # Using SLEEP as placeholder for PETRIFY

LEIF_ID = "LEIF"  # ID for the main character

# Action types
ACTION_MOVE = "MOVE"
ACTION_ATTACK = "ATTACK"
ACTION_CAPTURE = "CAPTURE"
ACTION_USE_ITEM = "USE_ITEM"
ACTION_TRADE = "TRADE"
ACTION_VISIT = "VISIT"
ACTION_TALK = "TALK"
ACTION_WAIT = "WAIT"
ACTION_SEIZE = "SEIZE"

# Fatigue constants
FATIGUE_COMBAT = 1
FATIGUE_SPECIAL_ACTION = 2

class EngineCore:
    """
    The central orchestrator of the game. Manages the main game loop, controls turn and phase transitions,
    processes player input and AI actions, triggers events, and checks for victory or defeat conditions.
    Relies on injected dependencies for specific functionalities.
    """
    def __init__(self,
                 game_state_manager: GameStateManager,
                 data_provider: DataProvider,
                 turn_manager: TurnManager,
                 action_handler: ActionHandler,
                 event_handler: EventHandler,
                 ai_manager: AIManager,
                 combat_system: CombatSystem,
                 # inventory_system: InventorySystem, # Might be primarily used by ActionHandler/GameStateManager
                 map_system: MapSystem,
                 movement_system: MovementSystem,
                 unit_system: UnitSystem, # Uncommented - needed for TurnManager initialization
                 input_handler: Optional[Any] = None, # Keep optional for now if UI/Input is separate
                 ai_vs_ai: bool = False, # Flag for AI vs AI mode
                 ascii_display: bool = False, # Flag for ASCII display mode
                 **kwargs): # Keep kwargs for flexibility
        """
        Initializes the EngineCore with all necessary system components.
        
        Args:
            game_state_manager: Instance of the GameStateManager
            data_provider: Instance of the DataProvider
            turn_manager: Instance of the TurnManager
            action_handler: Instance of the ActionHandler
            event_handler: Instance of the EventHandler
            ai_manager: Instance of the AIManager
            combat_system: Instance of the CombatSystem
            map_system: Instance of the MapSystem
            movement_system: Instance of the MovementSystem
            input_handler: Instance of the InputHandler (optional)
            ai_vs_ai: Flag to enable AI vs AI mode (default: False)
            **kwargs: Additional keyword arguments for flexibility
        """
        self.game_state_manager = game_state_manager
        self.data_provider = data_provider
        self.turn_manager = turn_manager
        self.action_handler = action_handler
        self.event_handler = event_handler
        self.ai_manager = ai_manager
        self.combat_system = combat_system
        # self.inventory_system = inventory_system
        self.map_system = map_system
        self.movement_system = movement_system
        self.unit_system = unit_system  # Uncommented - store the unit_system
        self.input_handler = input_handler
        self.ai_vs_ai = ai_vs_ai  # Store the AI vs AI flag
        self.ascii_display = ascii_display  # Store the ASCII display flag
        
        # Game loop state - consider if TurnManager should own these
        # self.current_turn = 0 # Managed by TurnManager
        # self.current_phase = PHASE_PLAYER # Managed by TurnManager
        self.active_faction_units = [] # Units for the current phase's faction
        self.game_over = False
        self.victory = False
        self.turn_limit = 10  # Maximum number of turns for AI vs AI mode (reduced for testing)
    
    def initialize_chapter(self, chapter_id: str, scenario_name: Optional[str] = None) -> None:
        """
        Initialize a new chapter with the specified ID or a test scenario.
        
        Args:
            chapter_id: The ID of the chapter to initialize
            scenario_name: Optional name of a test scenario to load instead of a chapter
        """
        if scenario_name:
            logging.info(f"Initializing Scenario: {scenario_name} (based on chapter: {chapter_id})")
        else:
            logging.info(f"Initializing Chapter: {chapter_id}")
        
        # Load static data via DataProvider
        map_data = self.data_provider.get_map_data(chapter_id, scenario_name)
        unit_placements = self.data_provider.get_unit_placements(chapter_id, scenario_name)
        event_scripts = self.data_provider.get_event_scripts(chapter_id, scenario_name)
        
        # Initialize Game State via GameStateManager
        self.game_state_manager.load_map(map_data)
        # Assuming deploy_units needs DataProvider to fetch unit base stats etc.
        self.game_state_manager.deploy_units(unit_placements, self.data_provider)
        
        # Initialize event handler
        if self.event_handler:
            # Correct method name is load_chapter_events
            self.event_handler.load_chapter_events(chapter_id, scenario_name)
            
        # Initialize turn manager now that game state is loaded
        self.turn_manager.initialize(
            gameStateManager_instance=self.game_state_manager,
            eventHandler_instance=self.event_handler,
            unitSystem_instance=self.unit_system,
            aiManager_instance=self.ai_manager,
            mapSystem_instance=self.map_system,
            dataProvider_instance=self.data_provider
        )
        
        # Set AI vs AI flag in turn manager
        if hasattr(self.turn_manager, 'ai_vs_ai'):
            self.turn_manager.ai_vs_ai = self.ai_vs_ai

        # Initialize Turn Manager for the start of the chapter
        self.turn_manager.start_new_chapter()
        # self.current_turn = 1 # Handled by TurnManager
        # self.current_phase = PHASE_PLAYER # Handled by TurnManager
        self.game_over = False
        self.victory = False
        
        logging.info(f"Chapter Initialized. Turn {self.turn_manager.get_current_turn()}, {self.turn_manager.get_current_phase().name} Phase.")
        self.start_phase() # Start the first phase
    
    def run_game_loop(self) -> None:
        """
        Run the main game loop until the game ends.
        """
        # Debug log to check if AI vs AI mode is enabled
        logging.info(f"Starting game loop with AI vs AI mode: {self.ai_vs_ai}")
        
        while not self.game_over and not self.victory:
            # Process AI actions for the current phase
            current_phase = self.turn_manager.get_current_phase()
            current_turn = self.turn_manager.get_current_turn()
            
            logging.info(f"RUN_GAME_LOOP: Processing phase {current_phase.name} (Turn: {current_turn}, AI vs AI: {self.ai_vs_ai}")
            logging.info(f"RUN_GAME_LOOP: current_phase == PHASE_PLAYER: {current_phase == PHASE_PLAYER}")
            logging.info(f"RUN_GAME_LOOP: PHASE_PLAYER: {PHASE_PLAYER}")
            logging.info(f"RUN_GAME_LOOP: current_phase: {current_phase}")
            
            # Start the phase to initialize units and check events
            self.start_phase()
            
            # Force AI vs AI mode for player phase
            if current_phase.name == 'PLAYER_PHASE' and self.ai_vs_ai:
                # Process AI actions for player units in AI vs AI mode
                logging.info(f"RUN_GAME_LOOP: Calling _process_ai_actions_for_player_units")
                self._process_ai_actions_for_player_units()
            elif current_phase.name == 'ENEMY_PHASE' or current_phase.name == 'NPC_PHASE':
                # Process AI actions for enemy/NPC units
                logging.info(f"RUN_GAME_LOOP: Calling _process_ai_actions_for_enemy_units for {current_phase.name}")
                self._process_ai_actions_for_enemy_units(current_phase)
            else:
                # Normal player phase - execute phase as usual
                logging.info(f"RUN_GAME_LOOP: Calling execute_phase")
                self.execute_phase()
            
            # Check if scenario is marked as complete
            if self.game_state_manager.current_game_state.event_flags.get('scenario_complete', False):
                reason = self.game_state_manager.current_game_state.event_flags.get('scenario_end_reason', 'Scenario completed')
                logging.info(f"Scenario complete: {reason}")
                self.victory = True
                break
            
            if not self.game_over and not self.victory:  # Check again in case phase execution ended the game
                self.end_phase()
        
        if self.victory:
            self.handle_victory()
        elif self.game_over:
            self.handle_game_over()
    
    def start_phase(self) -> None:
        """
        Start the current phase, resetting unit actions and applying start-of-phase effects.
        """
        current_phase = self.turn_manager.get_current_phase()
        current_turn = self.turn_manager.get_current_turn()
        logging.info(f"Starting Phase: {current_phase.name} (Turn: {current_turn})")
        
        # Display ASCII map at the start of each phase if enabled
        if self.ascii_display and hasattr(self.input_handler, 'display'):
            self.input_handler.display.render_ascii_map(self.game_state_manager)
        
        # Get active faction units
        faction = self._get_faction_for_phase(current_phase)
        self.active_faction_units = self.game_state_manager.get_units_by_faction(faction)
        
        # Debug log to check active units
        logging.info(f"Active units for {current_phase.name} phase: {len(self.active_faction_units)}")
        for i, unit in enumerate(self.active_faction_units):
            logging.info(f"Active unit {i+1}: {unit.name} at {unit.position}, faction={unit.faction}")
        
        # Reset action states and apply phase start effects
        for unit in self.active_faction_units:
            if not self.game_state_manager.is_unit_fatigued_for_deployment(unit.id):
                unit.has_acted = False
                unit.has_moved = False
                self._apply_start_of_phase_unit_effects(unit)
            else:
                unit.has_acted = True  # Fatigued units cannot act (except Leif)
        
        # Check for turn-based events via EventHandler
        if self.event_handler:
            self.event_handler.check_turn_events(current_turn, current_phase)
        
        self.check_game_end_conditions()  # Events might trigger game end
    
    def execute_phase(self) -> None:
        """
        Execute the current phase (player input or AI actions).
        """
        current_phase = self.turn_manager.get_current_phase()
        current_turn = self.turn_manager.get_current_turn()
        
        # Debug log at the start of each phase execution
        logging.info(f"Executing phase: {current_phase.name} (Turn: {current_turn}, AI vs AI: {self.ai_vs_ai})")
        logging.info(f"ENGINE DEBUGGING: self.active_faction_units = {self.active_faction_units}")
        
        # Check if active_faction_units is empty
        if not self.active_faction_units:
            logging.warning(f"ENGINE DEBUGGING: No active units for phase {current_phase.name}")
            
        # Check turn limit for AI vs AI mode
        if self.ai_vs_ai and current_turn > self.turn_limit:
            logging.info(f"Turn limit of {self.turn_limit} turns reached in AI vs AI mode. Ending game.")
            self.victory = True
            return

        if current_phase == PHASE_PLAYER:
            if self.ai_vs_ai:
                # AI controls player units in AI vs AI mode
                logging.info("=== AI vs AI mode: AI controlling PLAYER units (Turn: {}) ===".format(current_turn))
                logging.info(f"ENGINE DEBUGGING: self.active_faction_units = {len(self.active_faction_units)}")
                logging.info(f"ENGINE DEBUGGING: _sort_units_for_ai = {hasattr(self, '_sort_units_for_ai')}")
                
                # Display ASCII map at the start of AI vs AI player phase if enabled
                if self.ascii_display and hasattr(self.input_handler, 'display'):
                    self.input_handler.display.render_ascii_map(self.game_state_manager)
                
                # Debug information about active units
                logging.info(f"ENGINE DEBUGGING: AI vs AI mode active for PLAYER phase")
                logging.info(f"ENGINE DEBUGGING: self.ai_vs_ai = {self.ai_vs_ai}")
                
                # Determine unit order (similar to enemy phase)
                ordered_units = self._sort_units_for_ai(self.active_faction_units)
                
                logging.info(f"ENGINE DEBUGGING: Processing {len(ordered_units)} player units in AI vs AI mode")
                for i, unit in enumerate(ordered_units):
                    logging.info(f"ENGINE DEBUGGING: Player unit {i+1}: {unit.name} at {unit.position}, has_acted={unit.has_acted}")
                
                for unit in ordered_units:
                    logging.info(f"ENGINE DEBUGGING: Processing unit {unit.name}, has_acted={unit.has_acted}, game_over={self.game_over}, victory={self.victory}")
                    if not unit.has_acted and not self.game_over and not self.victory:
                        # Check status effects like Sleep/Berserk that prevent AI control
                        can_act = self._can_unit_act(unit)
                        logging.info(f"ENGINE DEBUGGING: Unit {unit.name} can act: {can_act}")
                        if can_act:
                            logging.info(f"ENGINE DEBUGGING: AI determining action for player unit: {unit.name} at {unit.position}")
                            
                            # Get action from AIManager
                            ai_action = self.ai_manager.determine_action(unit, self.game_state_manager)
                            
                            if ai_action:
                                logging.info(f"ENGINE DEBUGGING: AI selected action: {ai_action['type']} for {unit.name}")
                                logging.info(f"ENGINE DEBUGGING: Action details: {ai_action}")
                                
                                # Delegate action processing to ActionHandler
                                try:
                                    action_success = self.action_handler.process_action(
                                        unit.id,
                                        ai_action,
                                    )
                                    
                                    if action_success:
                                        logging.info(f"ENGINE DEBUGGING: AI action executed successfully for {unit.name}")
                                    else:
                                        logging.warning(f"ENGINE DEBUGGING: AI action failed for {unit.name}")
                                        logging.warning(f"ENGINE DEBUGGING: Action data: {ai_action}")
                                        # Mark unit as acted even if action failed to prevent infinite loops
                                        unit.has_acted = True
                                except Exception as e:
                                    logging.error(f"ENGINE DEBUGGING: Exception during AI action: {e}")
                                    action_success = False
                                    # Mark unit as acted even if action failed to prevent infinite loops
                                    unit.has_acted = True
                                
                                # Display ASCII map after each AI action in AI vs AI mode if enabled
                                if self.ascii_display and hasattr(self.input_handler, 'display'):
                                    self.input_handler.display.render_ascii_map(self.game_state_manager)
                            else:
                                # AI decides to wait or cannot act
                                logging.info(f"ENGINE DEBUGGING: AI decided to wait for {unit.name} (no action returned)")
                                unit.has_acted = True
                        else:
                            logging.info(f"ENGINE DEBUGGING: Unit {unit.name} cannot act due to status effects")
                            unit.has_acted = True
                        
                        self.check_game_end_conditions()  # Action might trigger game end
                        
                        if self.game_over or self.victory:
                            break  # Stop processing AI if game ended
            else:
                # Normal player control loop - wait for input
                while not self._all_player_units_acted() and not self.game_over and not self.victory:
                    if not self.input_handler:
                        logging.error("Input handler not initialized for Player Phase")
                        break # Cannot proceed without input
                    
                    # Display the current map state before getting input
                    if hasattr(self.input_handler, 'display'):
                        self.input_handler.display.display_map()
                    
                    # Get player input (this will pause and wait for user command)
                    player_input = self.input_handler.get_input() # Blocking call
                    
                    if player_input['type'] == "END_TURN":
                        break  # Player chose to end phase early
                    elif player_input['type'] in ["MOVE", "WAIT", "ATTACK", "CAPTURE", "ITEM", "TRADE", "VISIT", "SEIZE"]:
                        # Delegate action processing to ActionHandler
                        self.action_handler.process_action(
                            player_input['unit_id'],
                            player_input,
                        )
                        
                        # After each action, pause to let the player see the result
                        # and prepare for the next action
                        logging.info("Action completed. Waiting for next command...")
                    
                    self.check_game_end_conditions()  # Action might trigger game end
        
        elif current_phase == PHASE_ENEMY or current_phase == PHASE_NPC:
            # AI control loop
            if not self.ai_manager:
                logging.error(f"AI Manager not initialized for {current_phase.name} Phase")
                return # Cannot proceed without AI
            
            # Log the start of AI phase with clear indication
            logging.info(f"=== AI controlling {current_phase.name} units (Turn: {current_turn}) ===")
            
            # Display ASCII map at the start of enemy/NPC phase if enabled
            if self.ascii_display and hasattr(self.input_handler, 'display'):
                self.input_handler.display.render_ascii_map(self.game_state_manager)
            
            # Determine unit order (e.g., based on deployment list or initiative)
            ordered_units = self._sort_units_for_ai(self.active_faction_units)
            
            logging.info(f"Processing {len(ordered_units)} {current_phase.name} units")
            
            for unit in ordered_units:
                if not unit.has_acted and not self.game_over and not self.victory:
                    # Check status effects like Sleep/Berserk that prevent AI control
                    if self._can_unit_act(unit):
                        logging.info(f"AI determining action for {current_phase.name} unit: {unit.name} at {unit.position}")
                        
                        # Get action from AIManager
                        ai_action = self.ai_manager.determine_action(unit, self.game_state_manager)

                        if ai_action:
                            logging.info(f"AI selected action: {ai_action['type']} for {unit.name}")
                            
                            # Delegate action processing to ActionHandler
                            action_success = self.action_handler.process_action(
                                unit.id,
                                ai_action,
                            )
                            
                            if action_success:
                                logging.info(f"AI action executed successfully for {unit.name}")
                            else:
                                logging.warning(f"AI action failed for {unit.name}")
                                # Mark unit as acted even if action failed to prevent infinite loops
                                unit.has_acted = True
                            
                            # Display ASCII map after each AI action if enabled
                            if self.ascii_display and hasattr(self.input_handler, 'display'):
                                self.input_handler.display.render_ascii_map(self.game_state_manager)
                        else:
                            # AI decides to wait or cannot act
                            logging.info(f"AI decided to wait for {unit.name}")
                            unit.has_acted = True
                    else:
                        logging.info(f"Unit {unit.name} cannot act due to status effects")
                        unit.has_acted = True
                
                self.check_game_end_conditions()  # Action might trigger game end
                
                if self.game_over or self.victory:
                    break  # Stop processing AI if game ended
    
    def end_phase(self) -> None:
        """
        End the current phase and transition to the next phase.
        """
        current_phase = self.turn_manager.get_current_phase()
        current_turn = self.turn_manager.get_current_turn()
        logging.info(f"Ending Phase: {current_phase.name}")

        # Check phase end events via EventHandler
        if self.event_handler:
            self.event_handler.check_phase_end_events(current_turn, current_phase)
        
        self.check_game_end_conditions()  # Check again after end-phase events
        
        if self.game_over or self.victory:
            return
        
        # Delegate phase transition to TurnManager
        self.turn_manager.advance_phase(self.game_state_manager.has_npc_units())

        self.start_phase() # Start the new phase
    
    # Note: process_action logic is likely better suited within ActionHandler.
    # This method might be removed or simplified if ActionHandler takes full responsibility.
    # Keeping it temporarily for reference during refactoring.
    # def process_action(self, unit_id: str, action_data: Dict[str, Any]) -> None:
    #     """
    #     DEPRECATED: Use self.action_handler.process_action instead.
    #     Processes an action for a unit.
    #     """
    #     logging.warning("EngineCore.process_action is deprecated. Use ActionHandler.")
    #     # Delegate to ActionHandler
    #     self.action_handler.process_action(
    #         unit_id,
    #         action_data,
    #         # Pass dependencies if ActionHandler needs them directly
    #         # game_state_manager=self.game_state_manager,
    #         # combat_system=self.combat_system,
    #         # event_handler=self.event_handler,
    #         # movement_system=self.movement_system
    #     )
    #     # ActionHandler should internally call check_game_end_conditions if necessary
    #     # or return a status that EngineCore checks. Let's assume ActionHandler handles it.
    #     # self.check_game_end_conditions() # Potentially redundant if ActionHandler does it.

    # check_game_end_conditions remains important for EngineCore to manage the loop
    
    def check_game_end_conditions(self) -> None:
        """
        Check if any victory or loss conditions have been met.
        """
        if self.game_over or self.victory:
            return  # Already decided
        
        # Check if scenario is marked as complete
        if self.game_state_manager.current_game_state.event_flags.get('scenario_complete', False):
            reason = self.game_state_manager.current_game_state.event_flags.get('scenario_end_reason', 'Scenario completed')
            logging.info(f"Scenario complete: {reason}")
            self.victory = True
            return
        
        # Turn limit check
        current_turn = self.turn_manager.get_current_turn()
        if current_turn > (self.turn_limit if self.ai_vs_ai else 20):
            self.victory = True
            logging.info(f"Turn limit of {self.turn_limit if self.ai_vs_ai else 20} turns reached. Ending game.")
            return
        
        # Loss Conditions - Check via GameStateManager
        leif = self.game_state_manager.get_unit(LEIF_ID)
        
        if leif and leif.current_hp <= 0:
            self.game_over = True
            logging.info("Game Over: Leif has fallen!")
            return
        
        # Check event-based loss conditions via EventHandler
        if self.event_handler and self.event_handler.check_loss_conditions(self.game_state_manager):
            self.game_over = True
            logging.info("Game Over: Loss condition met.")
            return
        
        # Check event-based victory conditions via EventHandler
        # Seize condition might be better handled by ActionHandler triggering an event
        # that EventHandler checks here, or ActionHandler directly setting a flag
        # that GameStateManager exposes.
        if self.event_handler and self.event_handler.check_victory_conditions(self.game_state_manager, current_turn):
            self.victory = True
            logging.info("Victory Condition Met!")
            return
    
    def handle_victory(self) -> None:
        """
        Handle the end of a chapter when victory conditions are met.
        """
        logging.info("Chapter Cleared!")
        
        # Show victory screen, save game state, proceed to next chapter logic...
        
        # Finalize chapter state via GameStateManager
        self.game_state_manager.finalize_chapter_fatigue()
        self.game_state_manager.finalize_escape_map_captures()
    
    def handle_game_over(self) -> None:
        """
        Handle game over when loss conditions are met.
        """
        logging.info("Game Over!")
        
        # Show game over screen, offer retry/load options...
    
    # --- Helper Functions ---
    
    def _all_player_units_acted(self) -> bool:
        """
        Check if all player units have acted or cannot act.
        
        Returns:
            True if all units have acted, False otherwise
        """
        player_units = self.game_state_manager.get_units_by_faction(PHASE_PLAYER)
        
        for unit in player_units:
            # Check if unit is deployable (not fatigued) and hasn't acted
            if not self.game_state_manager.is_unit_fatigued_for_deployment(unit.id) and not unit.has_acted:
                # Also consider units under status effects like Sleep
                if self._can_unit_act(unit):
                    return False
        
        return True  # All active, non-fatigued, non-slept units have acted
    
    def _can_unit_act(self, unit: Any) -> bool:
        """
        Check if a unit can act (not affected by disabling status effects).
        
        Args:
            unit: The unit to check
            
        Returns:
            True if the unit can act, False otherwise
        """
        # Check for statuses like Sleep, Petrify, etc.
        return not unit.has_status(STATUS_SLEEP) and not unit.has_status(STATUS_PETRIFY)
    
    def _validate_action(self, unit: Any, action_data: Dict[str, Any]) -> bool:
        """
        Validate if an action is legal for a unit.
        
        Args:
            unit: The unit performing the action
            action_data: Data describing the action
            
        Returns:
            True if the action is valid, False otherwise
        """
        # This would contain logic to validate different action types
        # For example, checking if a unit can attack a target, if a tile is in range, etc.
        # For now, we'll just return True as a placeholder
        return True
    
    def _apply_start_of_phase_unit_effects(self, unit: Any) -> None:
        """
        Apply start-of-phase effects to a unit (healing, poison, etc.).
        
        Args:
            unit: The unit to apply effects to
        """
        # Delegate status effect application/checks to GameStateManager or a dedicated effect system?
        # For now, keep simple logic here, but consider refactoring later.
        if unit.has_status(StatusEffectEnum.POISON):
            self.game_state_manager.apply_damage(unit.id, 1) # Example damage
        
        # Check for terrain effects via MapSystem/GameStateManager?
        terrain_type = self.game_state_manager.get_terrain_type(unit.position)

        # Use DataProvider to check terrain properties
        if self.data_provider.is_terrain_healing(terrain_type):
            heal_amount = self.data_provider.get_terrain_heal_amount(terrain_type) # Example
            self.game_state_manager.apply_healing(unit.id, heal_amount)
    
    def _sort_units_for_ai(self, units: List[Any]) -> List[Any]:
        """
        Sort units for AI processing order.
        
        Args:
            units: List of units to sort
            
        Returns:
            Sorted list of units
        """
        # This would contain logic to determine the order in which AI units act
        # For now, we'll just return the units in their original order
        return units
    
    # This logic might belong in ActionHandler or GameStateManager when fatigue is updated
    # def _calculate_staff_fatigue(self, staff_rank: str) -> int: ... (Removed - should be handled elsewhere)
    
    # This logic should likely use MovementSystem and be called by ActionHandler
    # def _calculate_remaining_movement(self, unit: Any) -> int: ... (Removed - should be handled elsewhere)
    
    # This logic should be part of the input/AI loop within ActionHandler or EngineCore's phase execution
    # def _get_canto_input_or_ai(self, unit: Any, remaining_movement: int) -> Optional[Dict[str, Any]]: ... (Removed - should be handled elsewhere)
    
    def _random_chance(self, percentage: int) -> bool:
        """
        Check if a random chance succeeds.
        
        Args:
            percentage: The percentage chance of success (0-100)
            
        Returns:
            True if successful, False otherwise
        """
        return random.randint(1, 100) <= percentage
        
    def _get_faction_for_phase(self, phase):
        """
        Convert a TurnPhase to the corresponding FactionEnum.
        
        Args:
            phase: The TurnPhase to convert
            
        Returns:
            The corresponding FactionEnum
        """
        if phase.name == 'PLAYER_PHASE':
            return FactionEnum.PLAYER
        elif phase.name == 'ENEMY_PHASE':
            return FactionEnum.ENEMY
        elif phase.name == 'NPC_PHASE':
            return FactionEnum.NPC
        else:
            logging.warning(f"Unknown phase: {phase}, defaulting to PLAYER faction")
            return FactionEnum.PLAYER
            
    def _process_ai_actions_for_player_units(self):
        """
        Process AI actions for player units in AI vs AI mode.
        """
        logging.info("=== AI vs AI mode: Processing AI actions for PLAYER units ===")
        
        # Determine unit order
        ordered_units = self._sort_units_for_ai(self.active_faction_units)
        
        logging.info(f"Processing {len(ordered_units)} player units in AI vs AI mode")
        for i, unit in enumerate(ordered_units):
            logging.info(f"Player unit {i+1}: {unit.name} at {unit.position}, has_acted={unit.has_acted}")
        
        for unit in ordered_units:
            logging.info(f"Processing unit {unit.name}, has_acted={unit.has_acted}, game_over={self.game_over}, victory={self.victory}")
            if not unit.has_acted and not self.game_over and not self.victory:
                # Check status effects like Sleep/Berserk that prevent AI control
                can_act = self._can_unit_act(unit)
                logging.info(f"Unit {unit.name} can act: {can_act}")
                if can_act:
                    logging.info(f"AI determining action for player unit: {unit.name} at {unit.position}")
                    
                    # Get action from AIManager
                    ai_action = self.ai_manager.determine_action(unit, self.game_state_manager)
                    
                    if ai_action:
                        logging.info(f"AI selected action: {ai_action['type']} for {unit.name}")
                        logging.info(f"Action details: {ai_action}")
                        
                        # Delegate action processing to ActionHandler
                        try:
                            action_success = self.action_handler.process_action(
                                unit.id,
                                ai_action,
                            )
                            
                            if action_success:
                                logging.info(f"AI action executed successfully for {unit.name}")
                            else:
                                logging.warning(f"AI action failed for {unit.name}")
                                logging.warning(f"Action data: {ai_action}")
                                # Mark unit as acted even if action failed to prevent infinite loops
                                unit.has_acted = True
                        except Exception as e:
                            logging.error(f"Exception during AI action: {e}")
                            action_success = False
                            # Mark unit as acted even if action failed to prevent infinite loops
                            unit.has_acted = True
                        
                        # Display ASCII map after each AI action in AI vs AI mode if enabled
                        if self.ascii_display and hasattr(self.input_handler, 'display'):
                            self.input_handler.display.render_ascii_map(self.game_state_manager)
                    else:
                        # AI decides to wait or cannot act
                        logging.info(f"AI decided to wait for {unit.name} (no action returned)")
                        unit.has_acted = True
                else:
                    logging.info(f"Unit {unit.name} cannot act due to status effects")
                    unit.has_acted = True
                
                self.check_game_end_conditions()  # Action might trigger game end
                
                if self.game_over or self.victory:
                    break  # Stop processing AI if game ended
    
    def _process_ai_actions_for_enemy_units(self, current_phase):
        """
        Process AI actions for enemy/NPC units.
        
        Args:
            current_phase: The current phase (ENEMY or NPC)
        """
        logging.info(f"=== Processing AI actions for {current_phase.name} units ===")
        
        # Determine unit order
        ordered_units = self._sort_units_for_ai(self.active_faction_units)
        
        logging.info(f"Processing {len(ordered_units)} {current_phase.name} units")
        
        for unit in ordered_units:
            if not unit.has_acted and not self.game_over and not self.victory:
                # Check status effects like Sleep/Berserk that prevent AI control
                if self._can_unit_act(unit):
                    logging.info(f"AI determining action for {current_phase.name} unit: {unit.name} at {unit.position}")
                    
                    # Get action from AIManager
                    ai_action = self.ai_manager.determine_action(unit, self.game_state_manager)
                    
                    if ai_action:
                        logging.info(f"AI selected action: {ai_action['type']} for {unit.name}")
                        
                        # Delegate action processing to ActionHandler
                        action_success = self.action_handler.process_action(
                            unit.id,
                            ai_action,
                        )
                        
                        if action_success:
                            logging.info(f"AI action executed successfully for {unit.name}")
                        else:
                            logging.warning(f"AI action failed for {unit.name}")
                            # Mark unit as acted even if action failed to prevent infinite loops
                            unit.has_acted = True
                        
                        # Display ASCII map after each AI action if enabled
                        if self.ascii_display and hasattr(self.input_handler, 'display'):
                            self.input_handler.display.render_ascii_map(self.game_state_manager)
                    else:
                        # AI decides to wait or cannot act
                        logging.info(f"AI decided to wait for {unit.name}")
                        unit.has_acted = True
                else:
                    logging.info(f"Unit {unit.name} cannot act due to status effects")
                    unit.has_acted = True
            
            self.check_game_end_conditions()  # Action might trigger game end
            
            if self.game_over or self.victory:
                break  # Stop processing AI if game ended