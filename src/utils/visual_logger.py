"""
Visual Scenario Logger Module

Provides a logger class to generate a turn-by-turn visual log
of a game scenario, including map states and action summaries.
"""

import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.core_engine.game_state import GameStateManager, PhaseEnum
    from src.input.cli_display import CLIDisplay # Assuming CLIDisplay for map rendering

# Use standard logging setup
logger = logging.getLogger(__name__)

class VisualScenarioLogger:
    """
    Logs a visual representation of a game scenario playthrough.
    """
    def __init__(self, game_state_manager: 'GameStateManager', cli_display: 'CLIDisplay', log_dir: str = "logs", enabled: bool = True):
        """
        Initialize the logger.

        Args:
            game_state_manager: Instance of the GameStateManager.
            cli_display: Instance of CLIDisplay (or similar) for map rendering.
            log_dir: Directory to save log files.
            enabled: Whether logging is active.
        """
        self.game_state_manager = game_state_manager
        self.cli_display = cli_display
        self.enabled = enabled
        self.log_dir = log_dir # Store log directory
        self.log_file_path = None
        self._log_buffer = [] # Store logs before writing to file

        if self.enabled:
            # Log that it's enabled, but don't create the file yet
            logger.info("Visual scenario logging enabled.")
        # Remove file creation and buffer writing from here
        # try:
        #     if not os.path.exists(log_dir):
        #         os.makedirs(log_dir)
        #     
        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     scenario_name = "scenario"
        #     if self.game_state_manager and self.game_state_manager.current_game_state:
        #         chapter_id = self.game_state_manager.current_game_state.chapter_id
        #         scenario_name = chapter_id if chapter_id else scenario_name
        #         
        #     self.log_file_path = os.path.join(log_dir, f"visual_log_{scenario_name}_{timestamp}.txt")
        #     logger.info(f"Log file will be: {self.log_file_path}")
        #     self._write_buffer_to_file() 
        # except Exception as e:
        #     logger.error(f"Failed to initialize visual scenario logger path: {e}")
        #     self.enabled = False

    def _create_log_file_path(self):
        """Creates the log file path based on current game state."""
        if not self.enabled or self.log_file_path:
            return # Only create once
            
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scenario_name = "scenario" # Default
            
            # Safely get chapter_id only if game state exists
            if self.game_state_manager and self.game_state_manager.current_game_state:
                map_state = getattr(self.game_state_manager.current_game_state, 'map_state', None)
                if map_state:
                    chapter_id = getattr(map_state, 'map_id', None) # map_id is on map_state
                    if chapter_id:
                        scenario_name = chapter_id
                        
            self.log_file_path = os.path.join(self.log_dir, f"visual_log_{scenario_name}_{timestamp}.txt")
            logger.info(f"Visual log file created: {self.log_file_path}")
        except Exception as e:
            logger.error(f"Failed to create visual scenario log file path: {e}")
            self.enabled = False # Disable logging if path creation fails

    def _write_log(self, message: str):
        """Internal method to handle writing to buffer or file."""
        if not self.enabled:
            return

        # Ensure log file path is created before first write
        if not self.log_file_path:
            self._create_log_file_path()
            # If path creation failed, self.enabled would be False now
            if not self.enabled:
                 return

        # If path is now set, write the buffer first
        if self._log_buffer:
            self._write_buffer_to_file() 

        # Write the current message
        if self.log_file_path: # Check again as _create_log_file_path might fail
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(message + "\n")
            except Exception as e:
                logger.error(f"Failed to write to visual log file {self.log_file_path}: {e}")
                # Consider disabling logging if file writing fails repeatedly
                # self.enabled = False 
        else:
            # Buffer message if file path still isn't set (shouldn't happen often)
            self._log_buffer.append(message)

    def _write_buffer_to_file(self):
        """Writes the content of the log buffer to the file and clears the buffer."""
        if not self.enabled or not self.log_file_path or not self._log_buffer:
            return
            
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                for msg in self._log_buffer:
                    f.write(msg + "\n")
            self._log_buffer = [] # Clear buffer after writing
        except Exception as e:
            logger.error(f"Failed to write buffered logs to visual log file {self.log_file_path}: {e}")
            # Decide if we should keep buffering or disable logging
            # self.enabled = False

    def log_initial_state(self):
        """Logs the initial map state."""
        if not self.enabled:
            return
            
        self._write_log("===== INITIAL STATE =====")
        # Check if display and its dependencies are ready
        if not self.cli_display:
            self._write_log("[Error: CLIDisplay object not available in logger]")
        elif not hasattr(self.cli_display, 'game_state_manager') or not self.cli_display.game_state_manager:
            self._write_log("[Error: CLIDisplay's GameStateManager not ready]")
        elif not hasattr(self.cli_display, 'map_system') or not self.cli_display.map_system:
             self._write_log("[Error: CLIDisplay's MapSystem not ready]")
        # Add checks for other essential systems if needed (e.g., unit_system)
        # elif not hasattr(self.cli_display, 'unit_system') or not self.cli_display.unit_system:
        #     self._write_log("[Error: CLIDisplay's UnitSystem not ready]")
        else:
            try:
                map_string = self.cli_display.render_ascii_map() # Use existing ASCII renderer
                if map_string is not None:
                    self._write_log(map_string)
                else:
                    self._write_log("[Error: render_ascii_map returned None]")
            except Exception as e:
                self._write_log(f"[Error rendering initial map: {e}]")
        self._write_log("=========================\n")
        self._write_buffer_to_file() # Ensure initial state is written

    def log_turn_start(self, turn_number: int):
        """Logs the beginning of a new turn."""
        if not self.enabled:
            return
        self._write_log(f"\n----- TURN {turn_number} START -----")

    def log_phase_start(self, phase: 'PhaseEnum'):
         """Logs the beginning of a new phase."""
         if not self.enabled:
             return
         phase_name = phase.name if hasattr(phase, 'name') else str(phase)
         self._write_log(f"--- {phase_name} PHASE ---")

    def log_action(self, unit_id: str, action_type: str, details: Optional[str] = None):
        """Logs a specific action taken by a unit."""
        if not self.enabled:
            return
            
        unit = self.game_state_manager.get_unit(unit_id)
        unit_name = unit.name if unit else f"Unit_{unit_id}"
        log_message = f"  - {unit_name} ({unit_id}) performs {action_type}"
        if details:
            log_message += f": {details}"
        self._write_log(log_message)

    def log_action_result(self, message: str):
         """Logs the result of an action (e.g., damage dealt, item used)."""
         if not self.enabled:
             return
         self._write_log(f"    -> {message}")

    def log_end_of_turn_state(self, turn_number: int):
        """Logs the map state at the end of a turn."""
        if not self.enabled:
            return
            
        self._write_log(f"\n===== END OF TURN {turn_number} STATE =====")
        try:
            map_string = self.cli_display.render_ascii_map()
            if map_string is not None:
                self._write_log(map_string)
            else:
                self._write_log("[Error: render_ascii_map returned None]")
        except Exception as e:
            self._write_log(f"[Error rendering end-of-turn map: {e}]")
        self._write_log("=============================\n")
        self._write_buffer_to_file() # Ensure turn state is written
        
    def finalize_log(self):
        """Writes any remaining buffered logs and adds a final message."""
        if not self.enabled:
            return
        self._write_buffer_to_file()
        self._write_log("\n===== SCENARIO LOG END =====")
        logger.info(f"Visual scenario log finalized: {self.log_file_path}") 