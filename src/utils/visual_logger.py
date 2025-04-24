"""
Visual Scenario Logger Module

Provides a logger class to generate a turn-by-turn visual log
of a game scenario, including map states and action summaries.
Supports both plain text and colored output formats.
"""

import logging
import os
import re
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, List, Tuple, Set

if TYPE_CHECKING:
    from src.core_engine.game_state import GameStateManager, PhaseEnum, FactionEnum
    from src.input.cli_display import CLIDisplay # Assuming CLIDisplay for map rendering

# Use standard logging setup
logger = logging.getLogger(__name__)

# ANSI color codes for console and log file
class LogColors:
    """ANSI color codes for colored log output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

# Faction colors for logs
FACTION_COLORS = {
    'PLAYER': LogColors.CYAN,
    'ENEMY': LogColors.RED,
    'NPC': LogColors.YELLOW,
}

# Action type colors
ACTION_COLORS = {
    'MOVEMENT': LogColors.GREEN,
    'COMBAT': LogColors.RED,
    'DAMAGE': LogColors.RED + LogColors.BOLD,
    'HEAL': LogColors.GREEN + LogColors.BOLD,
    'HEALED': LogColors.GREEN + LogColors.BOLD,
    'STATUS_EFFECT': LogColors.MAGENTA,
    'STATUS_CURE': LogColors.GREEN,
    'STATUS_DAMAGE': LogColors.MAGENTA + LogColors.BOLD,
    'DIALOG': LogColors.YELLOW,
    'DEATH': LogColors.RED + LogColors.BOLD,
    'RESCUE': LogColors.BLUE,
    'RESCUED': LogColors.BLUE,
    'DROP': LogColors.BLUE,
    'DROPPED': LogColors.BLUE,
    'PHASE': LogColors.CYAN + LogColors.BOLD,
    'SCENARIO_END': LogColors.CYAN + LogColors.BOLD,
    'FINAL_STATUS': LogColors.CYAN,
    'STATUS': LogColors.WHITE,
    'SYSTEM': LogColors.WHITE,
    'UNIT_REMOVED': LogColors.RED,
    'DEFAULT': LogColors.WHITE,
}

class VisualScenarioLogger:
    """
    Logs a visual representation of a game scenario playthrough.
    Supports plain text, ANSI-colored text, and HTML export formats.
    """
    def __init__(self, game_state_manager: 'GameStateManager', cli_display: 'CLIDisplay', 
                 log_dir: str = "logs", enabled: bool = True, fixed_log_path: Optional[str] = None,
                 use_colors: bool = True, html_export: bool = False):
        """
        Initialize the logger.

        Args:
            game_state_manager: Instance of the GameStateManager.
            cli_display: Instance of CLIDisplay (or similar) for map rendering.
            log_dir: Directory to save log files.
            enabled: Whether logging is active.
            fixed_log_path: If provided, uses this exact path instead of generating one.
                           This is useful for mechanic tests that need consistent file locations.
            use_colors: Whether to use ANSI colors in log files.
            html_export: Whether to generate an HTML version of the log with formatting.
        """
        self.game_state_manager = game_state_manager
        self.cli_display = cli_display
        self.enabled = enabled
        self.log_dir = log_dir # Store log directory
        self.fixed_log_path = fixed_log_path # Store fixed log path if provided
        self.log_file_path = None
        self.html_file_path = None
        self._log_buffer = [] # Store logs before writing to file
        self.use_colors = use_colors
        self.html_export = html_export
        self.html_buffer = [] # Buffer for HTML content
        self.action_history = [] # Track actions for replay

        if self.enabled:
            # Log that it's enabled, but don't create the file yet
            logger.info("Visual scenario logging enabled.")

    def _create_log_file_path(self):
        """Creates the log file path based on current game state or uses fixed path if provided."""
        if not self.enabled or self.log_file_path:
            print("Visual logger not enabled or log file path already set")
            return # Only create once
            
        try:
            # If a fixed log path is provided, use it directly
            if self.fixed_log_path:
                print(f"Using fixed log file path: {self.fixed_log_path}")
                # Ensure directory exists for the fixed path
                fixed_log_dir = os.path.dirname(self.fixed_log_path)
                if fixed_log_dir and not os.path.exists(fixed_log_dir):
                    print(f"Creating directory for fixed log path: {fixed_log_dir}")
                    logging.info(f"Creating directory for fixed log path: {fixed_log_dir}")
                    os.makedirs(fixed_log_dir, exist_ok=True)
                
                self.log_file_path = self.fixed_log_path
                if self.html_export:
                    self.html_file_path = self.log_file_path.replace('.txt', '.html')
                print(f"Visual log file path set to fixed path: {self.log_file_path}")
                logging.info(f"Visual log file created at fixed path: {self.log_file_path}")
                return
            
            # Otherwise, use the standard dynamic path generation
            print(f"Visual logger creating log file path in directory: {self.log_dir}")
            print(f"Directory exists: {os.path.exists(self.log_dir)}")
            
            if not os.path.exists(self.log_dir):
                print(f"Creating directory: {self.log_dir}")
                logging.info(f"Creating log directory: {self.log_dir}")
                os.makedirs(self.log_dir, exist_ok=True)
                print(f"Directory created successfully: {os.path.exists(self.log_dir)}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scenario_name = "scenario" # Default
            
            # Safely get chapter_id only if game state exists
            if self.game_state_manager and self.game_state_manager.current_game_state:
                map_state = getattr(self.game_state_manager.current_game_state, 'map_state', None)
                if map_state:
                    chapter_id = getattr(map_state, 'map_id', None) # map_id is on map_state
                    if chapter_id:
                        scenario_name = chapter_id
                        print(f"Using scenario name: {scenario_name}")
                        
            self.log_file_path = os.path.join(self.log_dir, f"visual_log_{scenario_name}_{timestamp}.txt")
            if self.html_export:
                self.html_file_path = os.path.join(self.log_dir, f"visual_log_{scenario_name}_{timestamp}.html")
            print(f"Visual log file path set to: {self.log_file_path}")
            logging.info(f"Visual log file created: {self.log_file_path}")
        except Exception as e:
            print(f"Error creating log file path: {e}")
            logging.error(f"Failed to create visual scenario log file path: {e}")
            self.enabled = False # Disable logging if path creation fails

    def _write_log(self, message: str, html_format: Optional[str] = None):
        """Internal method to handle writing to buffer or file."""
        if not self.enabled:
            print("Visual logger not enabled, skipping write")
            return

        # Ensure log file path is created before first write
        if not self.log_file_path:
            print("Log file path not set, creating...")
            self._create_log_file_path()
            # If path creation failed, self.enabled would be False now
            if not self.enabled:
                 print("Failed to create log file path, logger now disabled")
                 return

        # If path is now set, write the buffer first
        if self._log_buffer and self.log_file_path:
            print(f"Writing {len(self._log_buffer)} buffered entries to file")
            self._write_buffer_to_file() 

        # Write the current message
        if self.log_file_path: # Check again as _create_log_file_path might fail
            try:
                # Ensure the directory exists
                log_dir = os.path.dirname(self.log_file_path)
                print(f"Checking log directory: {log_dir}")
                if not os.path.exists(log_dir):
                    print(f"Log directory does not exist, creating: {log_dir}")
                    os.makedirs(log_dir, exist_ok=True)
                    
                print(f"Writing log message to file: {self.log_file_path}")
                print(f"File path exists: {os.path.exists(os.path.dirname(self.log_file_path))}")
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(message + "\n")
                print(f"Successfully wrote log message")
                logging.debug(f"Wrote message to log file: {self.log_file_path}")
                
                # Store HTML formatted content if enabled
                if self.html_export:
                    html_content = html_format if html_format else self._convert_to_html(message)
                    self.html_buffer.append(html_content)
            except Exception as e:
                print(f"Error writing to log file: {e}")
                logging.error(f"Failed to write to visual log file {self.log_file_path}: {e}")
                # Consider disabling logging if file writing fails repeatedly
                # self.enabled = False 
        else:
            # Buffer message if file path still isn't set (shouldn't happen often)
            print(f"Log file path not available, buffering message")
            self._log_buffer.append(message)
            # Store HTML formatted content if enabled
            if self.html_export:
                html_content = html_format if html_format else self._convert_to_html(message)
                self.html_buffer.append(html_content)
            logging.debug(f"Buffered message (log file path not set): {message[:50]}...")

    def _convert_to_html(self, message: str) -> str:
        """Convert ANSI colored text to HTML formatted content."""
        # Replace ANSI color codes with HTML span elements
        html = message
        
        # Replace special ASCII characters
        html = html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Map ANSI color codes to CSS classes
        ansi_to_css = {
            LogColors.RED: '<span class="red">',
            LogColors.GREEN: '<span class="green">',
            LogColors.YELLOW: '<span class="yellow">',
            LogColors.BLUE: '<span class="blue">',
            LogColors.MAGENTA: '<span class="magenta">',
            LogColors.CYAN: '<span class="cyan">',
            LogColors.WHITE: '<span class="white">',
            LogColors.GRAY: '<span class="gray">',
            LogColors.BOLD: '<span class="bold">',
            LogColors.RESET: '</span>'
        }
        
        # Replace ANSI codes with HTML tags
        for ansi, html_tag in ansi_to_css.items():
            html = html.replace(ansi, html_tag)
        
        # Replace newlines with <br> tags
        html = html.replace('\n', '<br>\n')
        
        return html

    def _write_buffer_to_file(self):
        """Writes the content of the log buffer to the file and clears the buffer."""
        if not self.enabled or not self.log_file_path or not self._log_buffer:
            return
            
        try:
            # Ensure the directory exists
            log_dir = os.path.dirname(self.log_file_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                for msg in self._log_buffer:
                    f.write(msg + "\n")
            logging.debug(f"Wrote {len(self._log_buffer)} buffered messages to log file: {self.log_file_path}")
            self._log_buffer = [] # Clear buffer after writing
            
            # Write HTML buffer if needed
            if self.html_export and self.html_buffer and self.html_file_path:
                self._write_html_file()
                self.html_buffer = [] # Clear HTML buffer
        except Exception as e:
            logging.error(f"Failed to write buffered logs to visual log file {self.log_file_path}: {e}")

    def _write_html_file(self):
        """Writes the HTML buffer to an HTML file with proper formatting."""
        if not self.html_export or not self.html_file_path or not self.html_buffer:
            return
            
        try:
            # Ensure the directory exists
            html_dir = os.path.dirname(self.html_file_path)
            if not os.path.exists(html_dir):
                os.makedirs(html_dir, exist_ok=True)
                
            # Create HTML file with header and CSS
            with open(self.html_file_path, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Tactical Scenario Log</title>
    <style>
        body { 
            background-color: #1e1e1e; 
            color: #f0f0f0; 
            font-family: 'Courier New', monospace;
            padding: 20px;
            line-height: 1.4;
        }
        .map {
            font-family: 'Courier New', monospace;
            white-space: pre;
            background-color: #2d2d2d;
            border: 1px solid #555;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .red { color: #ff6b6b; }
        .green { color: #7bcc70; }
        .yellow { color: #ffcb6b; }
        .blue { color: #6bafff; }
        .magenta { color: #dd78f6; }
        .cyan { color: #76e3ea; }
        .white { color: #f0f0f0; }
        .gray { color: #9e9e9e; }
        .bold { font-weight: bold; }
        h1, h2, h3 { color: #76e3ea; }
        .phase { 
            color: #76e3ea;
            font-weight: bold;
            border-bottom: 1px solid #555;
            padding-bottom: 5px;
            margin-top: 15px;
        }
        .turn-header {
            background-color: #333;
            padding: 5px 10px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .action-entry {
            margin: 5px 0;
            padding: 5px;
            border-left: 3px solid #555;
        }
        .player-action { border-left-color: #6bafff; }
        .enemy-action { border-left-color: #ff6b6b; }
        .npc-action { border-left-color: #ffcb6b; }
        .system-action { border-left-color: #76e3ea; }
    </style>
</head>
<body>
    <h1>Tactical Scenario Log</h1>
""")
                
                # Write the content
                for html_content in self.html_buffer:
                    f.write(html_content)
                
                # Close the HTML
                f.write("</body></html>")
                
            logging.debug(f"Wrote HTML log file: {self.html_file_path}")
            
        except Exception as e:
            logging.error(f"Failed to write HTML log file {self.html_file_path}: {e}")

    def _format_action_message(self, unit_id: str, action_type: str, details: Optional[str] = None) -> Tuple[str, str]:
        """
        Formats an action message with colors and returns both plain text and HTML versions.
        
        Returns:
            Tuple of (text_message, html_message)
        """
        unit = self.game_state_manager.get_unit(unit_id)
        unit_name = unit.name if unit else f"Unit_{unit_id}"
        faction = unit.faction.name if unit and hasattr(unit, 'faction') else "SYSTEM"
        
        # Get colors based on faction and action type
        faction_color = FACTION_COLORS.get(faction, LogColors.WHITE) if self.use_colors else ""
        action_color = ACTION_COLORS.get(action_type, ACTION_COLORS["DEFAULT"]) if self.use_colors else ""
        reset = LogColors.RESET if self.use_colors else ""
        
        # Format text message
        text_message = f"  - {faction_color}{unit_name} ({unit_id}){reset} performs {action_color}{action_type}{reset}"
        if details:
            text_message += f": {details}"
            
        # Format HTML message
        faction_class = faction.lower() if faction in FACTION_COLORS else "system"
        html_message = f'<div class="action-entry {faction_class}-action">'
        html_message += f'<span class="{faction_class}">{unit_name} ({unit_id})</span> performs '
        html_message += f'<span class="{action_type.lower() if action_type.lower() in ["combat", "movement", "heal"] else "default"}">{action_type}</span>'
        if details:
            html_message += f': {details}'
        html_message += '</div>'
        
        return text_message, html_message

    def log_initial_state(self):
        """Logs the initial map state."""
        if not self.enabled:
            return
            
        # Format header with colors
        header = "===== INITIAL STATE ====="
        header_colored = f"{LogColors.CYAN}{LogColors.BOLD}{header}{LogColors.RESET}" if self.use_colors else header
        self._write_log(header_colored, f'<h2>{header}</h2>')
        
        # Check if display and its dependencies are ready
        if not self.cli_display:
            self._write_log("[Error: CLIDisplay object not available in logger]")
        elif not hasattr(self.cli_display, 'game_state_manager') or not self.cli_display.game_state_manager:
            self._write_log("[Error: CLIDisplay's GameStateManager not ready]")
        elif not hasattr(self.cli_display, 'map_system') or not self.cli_display.map_system:
             self._write_log("[Error: CLIDisplay's MapSystem not ready]")
        else:
            try:
                map_string = self.cli_display.render_ascii_map() # Use existing ASCII renderer
                if map_string is not None:
                    # Format map with colors
                    if self.html_export:
                        html_map = f'<div class="map">{self._convert_to_html(map_string)}</div>'
                        self._write_log(map_string, html_map)
                    else:
                        self._write_log(map_string)
                else:
                    self._write_log("[Error: render_ascii_map returned None]")
            except Exception as e:
                self._write_log(f"[Error rendering initial map: {e}]")
                
        footer = "========================="
        footer_colored = f"{LogColors.CYAN}{footer}{LogColors.RESET}" if self.use_colors else footer
        self._write_log(footer_colored, f'<div>{footer}</div><br>')
        self._write_buffer_to_file() # Ensure initial state is written

    def log_turn_start(self, turn_number: int):
        """Logs the beginning of a new turn."""
        if not self.enabled:
            return
            
        # Format with colors
        message = f"\n----- TURN {turn_number} START -----"
        colored_message = f"\n{LogColors.YELLOW}{LogColors.BOLD}{message}{LogColors.RESET}" if self.use_colors else message
        html_message = f'<div class="turn-header"><h3>{message}</h3></div>'
        
        self._write_log(colored_message, html_message)

    def log_phase_start(self, phase: 'PhaseEnum'):
         """Logs the beginning of a new phase."""
         if not self.enabled:
             return
         phase_name = phase.name if hasattr(phase, 'name') else str(phase)
         
         # Format with colors
         message = f"--- {phase_name} PHASE ---"
         colored_message = f"{LogColors.CYAN}{message}{LogColors.RESET}" if self.use_colors else message
         html_message = f'<div class="phase">{message}</div>'
         
         self._write_log(colored_message, html_message)

    def log_action(self, unit_id: str, action_type: str, details: Optional[str] = None):
        """Logs a specific action taken by a unit."""
        if not self.enabled:
            return
            
        # Store action for history
        action_data = {"unit_id": unit_id, "action_type": action_type, "details": details}
        self.action_history.append(action_data)
        
        # Format message with colors and HTML
        text_message, html_message = self._format_action_message(unit_id, action_type, details)
        self._write_log(text_message, html_message)

    def log_action_result(self, message: str):
         """Logs the result of an action (e.g., damage dealt, item used)."""
         if not self.enabled:
             return
         
         # Format with colors
         colored_message = f"    -> {LogColors.WHITE}{message}{LogColors.RESET}" if self.use_colors else f"    -> {message}"
         html_message = f'<div style="margin-left: 20px; color: #f0f0f0;">→ {message}</div>'
         
         self._write_log(colored_message, html_message)

    def log_end_of_turn_state(self, turn_number: int):
        """Logs the map state at the end of a turn."""
        if not self.enabled:
            return
            
        # Format header with colors
        header = f"\n===== END OF TURN {turn_number} STATE ====="
        header_colored = f"\n{LogColors.CYAN}{LogColors.BOLD}{header}{LogColors.RESET}" if self.use_colors else header
        html_header = f'<h3>{header}</h3>'
        
        self._write_log(header_colored, html_header)
        
        try:
            map_string = self.cli_display.render_ascii_map()
            if map_string is not None:
                # Format map with colors for HTML
                if self.html_export:
                    html_map = f'<div class="map">{self._convert_to_html(map_string)}</div>'
                    self._write_log(map_string, html_map)
                else:
                    self._write_log(map_string)
            else:
                self._write_log("[Error: render_ascii_map returned None]")
        except Exception as e:
            self._write_log(f"[Error rendering end-of-turn map: {e}]")
            
        footer = "============================="
        footer_colored = f"{LogColors.CYAN}{footer}{LogColors.RESET}" if self.use_colors else footer
        html_footer = f'<div>{footer}</div><br>'
        
        self._write_log(footer_colored, html_footer)
        self._write_buffer_to_file() # Ensure turn state is written
        
    def finalize_log(self):
        """Writes any remaining buffered logs and adds a final message."""
        if not self.enabled:
            return
            
        # Format with colors
        end_message = "\n===== SCENARIO LOG END ====="
        colored_end_message = f"\n{LogColors.CYAN}{LogColors.BOLD}{end_message}{LogColors.RESET}" if self.use_colors else end_message
        html_end_message = f'<h2>{end_message}</h2>'
        
        self._write_log(colored_end_message, html_end_message)
        self._write_buffer_to_file()
        
        # Write HTML file if enabled
        if self.html_export and self.html_file_path:
            self._write_html_file()
            
        logger.info(f"Visual scenario log finalized: {self.log_file_path}")
        if self.html_export and self.html_file_path:
            logger.info(f"HTML scenario log created: {self.html_file_path}") 