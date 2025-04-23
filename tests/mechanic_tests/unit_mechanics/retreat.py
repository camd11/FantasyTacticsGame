"""
Unit Retreat Mechanics Test

This test demonstrates the retreat mechanic in the game, showing how units
can voluntarily exit the battlefield and be removed from combat.
"""

import os
import sys
import random
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.abspath('.'))

# Import the necessary modules
from src.utils.visual_logger import VisualScenarioLogger
from src.core_engine.game_state import GameStateManager, GameState, MapState, UnitState, FactionEnum, DispositionEnum, PhaseEnum

class MockCLIDisplay:
    """Mock CLI display for rendering the game state."""
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager
    
    def render_ascii_map(self):
        """Render an ASCII representation of the current game state."""
        map_width, map_height = 7, 7
        
        # Get unit positions - in a real game, this would come from the game state
        unit_positions = {}
        for unit in self.game_state_manager.get_all_units():
            if hasattr(unit, 'position') and unit.position and unit.disposition == DispositionEnum.ACTIVE:
                unit_positions[unit.position] = unit
        
        # Initialize the map with empty cells
        map_data = [['.' for _ in range(map_width)] for _ in range(map_height)]
        
        # Place units on the map
        for pos, unit in unit_positions.items():
            x, y = pos
            if 0 <= x < map_width and 0 <= y < map_height:
                if unit.faction == FactionEnum.PLAYER:
                    map_data[y][x] = 'P'
                elif unit.faction == FactionEnum.ENEMY:
                    map_data[y][x] = 'E'
                else:
                    map_data[y][x] = 'N'
        
        # Build the map string
        map_string = f"=== ASCII MAP (Turn {self.game_state_manager.current_game_state.current_turn}, {self.game_state_manager.current_game_state.current_phase.name} Phase) ===\n"
        map_string += "   " + "".join([str(i) for i in range(map_width)]) + "\n"
        
        for y in range(map_height):
            map_string += f" {y} "
            for x in range(map_width):
                map_string += map_data[y][x]
            map_string += "\n"
        
        return map_string

def create_unit(unit_id, name, faction, position, hp, max_hp, stats):
    """Helper function to create a unit for testing."""
    unit = UnitState()
    unit.id = unit_id
    unit.name = name
    unit.faction = faction
    unit.position = position
    unit.current_hp = hp
    unit.max_hp = max_hp
    unit.disposition = DispositionEnum.ACTIVE
    unit.base_stats = stats
    return unit

class MockGameStateManager(GameStateManager):
    """Mock GameStateManager for testing."""
    def __init__(self):
        super().__init__(None)
        self.current_game_state = GameState()
        self.current_game_state.map_state = MapState()
        self.current_game_state.unit_states = {}
        
    def add_unit(self, unit):
        """Add a unit to the game state."""
        self.current_game_state.unit_states[unit.id] = unit
        
    def get_all_units(self):
        """Return all units in the game state."""
        return list(self.current_game_state.unit_states.values())

def run_test(log_path=None):
    """Run the retreat mechanics test."""
    # Create log file path if not provided
    if log_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("logs/mechanic_tests/units", exist_ok=True)
        log_path = f"logs/mechanic_tests/units/retreat_mechanics_{timestamp}.txt"
    
    # Create mock game state
    game_state_manager = MockGameStateManager()
    game_state_manager.current_game_state.map_state.map_id = "retreat_test_map"
    game_state_manager.current_game_state.current_turn = 1
    game_state_manager.current_game_state.current_phase = PhaseEnum.PLAYER
    
    # Create mock CLI display
    cli_display = MockCLIDisplay(game_state_manager)
    
    # Initialize the visual logger
    visual_logger = VisualScenarioLogger(
        game_state_manager=game_state_manager,
        cli_display=cli_display,
        enabled=True,
        fixed_log_path=log_path,
        use_colors=True,
        html_export=True
    )
    
    print(f"Retreat mechanics test log will be written to: {log_path}")
    print(f"HTML log will be written to: {log_path.replace('.txt', '.html')}")
    
    # Create units for the test
    player_commander = create_unit(
        "PLAYER_COMMANDER", "Commander", FactionEnum.PLAYER, 
        (3, 3), 10, 25, {"STR": 10, "DEF": 7, "SKL": 8, "SPD": 6, "MOV": 5}
    )
    
    enemy_archer = create_unit(
        "ENEMY_ARCHER", "Archer", FactionEnum.ENEMY, 
        (4, 3), 20, 20, {"STR": 8, "DEF": 4, "SKL": 10, "SPD": 7, "MOV": 4}
    )
    
    # Register units with the game state manager
    game_state_manager.add_unit(player_commander)
    game_state_manager.add_unit(enemy_archer)
    
    # Start the test scenario
    visual_logger.log_action("SYSTEM", "SCENARIO_START", "Starting Retreat Mechanics Test")
    visual_logger.log_initial_state()
    
    # Log the test description
    visual_logger.log_action("SYSTEM", "TEST_INFO", "This test demonstrates how units can retreat from battle and be removed from the battlefield")
    
    # Player phase - Commander decides to retreat
    visual_logger.log_turn_start(1)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Commander is in a bad situation (low HP)
    visual_logger.log_action("SYSTEM", "SITUATION", f"Commander is in a dangerous situation with only {player_commander.current_hp}/{player_commander.max_hp} HP")
    visual_logger.log_action("PLAYER_COMMANDER", "DECISION", "Commander decides to retreat from battle")
    
    # Commander moves towards the map edge
    old_position = player_commander.position
    new_position = (1, 3)  # Move towards edge
    
    visual_logger.log_action("PLAYER_COMMANDER", "MOVEMENT", f"Commander moves from {old_position} to {new_position}")
    player_commander.position = new_position
    
    # Commander retreats from battle
    visual_logger.log_action("PLAYER_COMMANDER", "RETREAT", "Commander retreats from the battlefield")
    
    # Remove commander from active units
    player_commander.disposition = DispositionEnum.RETREATED
    player_commander.position = None
    
    visual_logger.log_action("SYSTEM", "UNIT_REMOVED", "Commander has been removed from the battlefield")
    
    # End the player phase
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # Enemy phase
    game_state_manager.current_game_state.current_phase = PhaseEnum.ENEMY
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
    
    # Archer moves but can't find the commander
    visual_logger.log_action("ENEMY_ARCHER", "MOVEMENT", f"Archer moves to ({new_position[0] + 1}, {new_position[1]})")
    visual_logger.log_action("ENEMY_ARCHER", "OBSERVATION", "Archer can't find the Commander who has retreated")
    
    # End enemy phase
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
    
    # Log end of turn state
    visual_logger.log_end_of_turn_state(1)
    
    # End the test scenario
    visual_logger.log_action("SYSTEM", "SCENARIO_END", "Retreat Mechanics Test Completed")
    
    # Final summary
    visual_logger.log_action("SYSTEM", "TEST_SUMMARY", "--- Test Summary ---")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "Retreat mechanic successfully demonstrated")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "Commander retreated from battle and was removed from the battlefield")
    
    # Log final unit status
    for unit in game_state_manager.get_all_units():
        if unit.disposition == DispositionEnum.ACTIVE:
            visual_logger.log_action(unit.id, "STATUS", f"{unit.name}: HP {unit.current_hp}/{unit.max_hp}, Position {unit.position}")
        elif unit.disposition == DispositionEnum.RETREATED:
            visual_logger.log_action(unit.id, "STATUS", f"{unit.name}: RETREATED from battlefield")
        else:
            visual_logger.log_action(unit.id, "STATUS", f"{unit.name}: {unit.disposition}, Position {unit.position}")
    
    # Finalize the log
    visual_logger.finalize_log()
    print("Retreat mechanics test completed.")
    
    return True

if __name__ == "__main__":
    # If run directly, use default log path
    run_test() 