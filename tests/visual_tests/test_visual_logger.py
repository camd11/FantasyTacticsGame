"""
Test script to verify Visual Logger's HTML export functionality.
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.abspath('.'))

# Import the necessary modules
from src.utils.visual_logger import VisualScenarioLogger
from src.core_engine.game_state import GameStateManager, GameState, MapState, UnitState, FactionEnum, DispositionEnum, PhaseEnum

# Mock objects for testing
class MockCliDisplay:
    def __init__(self):
        self.game_state_manager = None
        self.map_system = None
    
    def render_ascii_map(self):
        """Return a simple ASCII map for testing."""
        return """=== ASCII MAP (Turn 1, PLAYER Phase) ===
   01234
 0 .....
 1 .P...
 2 ..E..
 3 ...N.
 4 .....
"""

class MockGameStateManager:
    def __init__(self):
        self.current_game_state = GameState()
        self.current_game_state.map_state = MapState()
        self.current_game_state.map_state.map_id = "test_map"
        self.current_game_state.current_turn = 1
        self.current_game_state.current_phase = PhaseEnum.PLAYER
    
    def get_unit(self, unit_id):
        """Return a mock unit for the given ID."""
        if unit_id == "PLAYER_UNIT":
            unit = UnitState()
            unit.id = "PLAYER_UNIT"
            unit.name = "Player Unit"
            unit.faction = FactionEnum.PLAYER
            unit.position = (1, 1)
            unit.current_hp = 20
            unit.max_hp = 25
            return unit
        elif unit_id == "ENEMY_UNIT":
            unit = UnitState()
            unit.id = "ENEMY_UNIT"
            unit.name = "Enemy Unit"
            unit.faction = FactionEnum.ENEMY
            unit.position = (2, 2)
            unit.current_hp = 15
            unit.max_hp = 20
            return unit
        elif unit_id == "NPC_UNIT":
            unit = UnitState()
            unit.id = "NPC_UNIT"
            unit.name = "NPC Unit"
            unit.faction = FactionEnum.NPC
            unit.position = (3, 3)
            unit.current_hp = 10
            unit.max_hp = 12
            return unit
        elif unit_id == "SYSTEM":
            unit = UnitState()
            unit.id = "SYSTEM"
            unit.name = "System"
            return unit
        return None

def main():
    """Test the Visual Logger HTML export functionality."""
    # Create output directory
    os.makedirs("logs/test", exist_ok=True)
    
    # Create log and HTML file paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join("logs/test", f"visual_log_test_{timestamp}.txt")
    
    # Create mock objects
    game_state_manager = MockGameStateManager()
    cli_display = MockCliDisplay()
    cli_display.game_state_manager = game_state_manager
    
    # Initialize the visual logger with HTML export enabled
    visual_logger = VisualScenarioLogger(
        game_state_manager=game_state_manager,
        cli_display=cli_display,
        enabled=True,
        fixed_log_path=log_path,
        use_colors=True,
        html_export=True
    )
    
    print(f"Log will be written to: {log_path}")
    print(f"HTML log will be written to: {log_path.replace('.txt', '.html')}")
    
    # Log test scenario
    visual_logger.log_initial_state()
    visual_logger.log_turn_start(1)
    
    # Log some actions
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    visual_logger.log_action("PLAYER_UNIT", "MOVEMENT", "Moving from (1, 1) to (2, 1)")
    visual_logger.log_action("PLAYER_UNIT", "COMBAT", "Attacks Enemy Unit")
    visual_logger.log_action("ENEMY_UNIT", "DAMAGE", "Takes 5 damage (HP: 15/20)")
    visual_logger.log_action("ENEMY_UNIT", "COMBAT", "Counterattacks Player Unit")
    visual_logger.log_action("PLAYER_UNIT", "DAMAGE", "Takes 3 damage (HP: 17/25)")
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # Log enemy phase
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
    visual_logger.log_action("ENEMY_UNIT", "MOVEMENT", "Moving from (2, 2) to (2, 3)")
    visual_logger.log_action("ENEMY_UNIT", "STATUS_EFFECT", "Applies poison to NPC Unit")
    visual_logger.log_action("NPC_UNIT", "STATUS_DAMAGE", "Takes 2 poison damage (HP: 8/12)")
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
    
    # Log end of turn
    visual_logger.log_end_of_turn_state(1)
    
    # Finalize log
    visual_logger.finalize_log()
    
    print("Test completed.")
    print(f"Check {log_path} for the text log.")
    print(f"Check {log_path.replace('.txt', '.html')} for the HTML log.")

if __name__ == "__main__":
    main() 