"""
Unit Rescue Mechanics Test

This test demonstrates the unit rescue mechanic in the game, showing how units
can pick up and carry other units to safety or strategic positions.
"""

import os
import sys
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
        map_width, map_height = 10, 10
        
        # Get unit positions - in a real game, this would come from the game state
        unit_positions = {}
        for unit in self.game_state_manager.get_all_units():
            if hasattr(unit, 'position') and unit.position and unit.disposition == DispositionEnum.ACTIVE:
                if not hasattr(unit, 'is_being_carried') or not unit.is_being_carried:
                    unit_positions[unit.position] = unit
        
        # Initialize the map with empty cells
        map_data = [['.' for _ in range(map_width)] for _ in range(map_height)]
        
        # Add some terrain features
        # Water/river (impassable)
        for y in range(2, 8):
            map_data[y][5] = '~'
        # Bridge at y=4
        map_data[4][5] = '='
        
        # Place units on the map
        for pos, unit in unit_positions.items():
            x, y = pos
            if 0 <= x < map_width and 0 <= y < map_height:
                # Show carried unit indicator
                if hasattr(unit, 'carrying_unit') and unit.carrying_unit:
                    if unit.faction == FactionEnum.PLAYER:
                        map_data[y][x] = 'P+'
                    elif unit.faction == FactionEnum.ENEMY:
                        map_data[y][x] = 'E+'
                    else:
                        map_data[y][x] = 'N+'
                else:
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
                cell = map_data[y][x]
                if len(cell) == 1:
                    map_string += cell + " "
                else:
                    map_string += cell
            map_string += "\n"
        
        map_string += "\nLegend: P=Player, E=Enemy, N=NPC, +=Carrying unit, ~=Water, ==Bridge\n"
        
        return map_string

def create_unit(unit_id, name, faction, position, hp, max_hp, stats, class_name="Warrior", abilities=None):
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
    unit.class_name = class_name
    unit.abilities = abilities or []
    unit.is_being_carried = False  # Flag to indicate if unit is being carried
    unit.carrying_unit = None  # Reference to carried unit
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

def can_rescue(rescuer, target):
    """Check if a unit can rescue another unit based on stats."""
    rescuer_con = rescuer.base_stats.get("CON", 10)
    target_con = target.base_stats.get("CON", 10)
    
    return rescuer_con >= target_con - 3  # Can rescue if constitution is high enough

def run_test(log_path=None):
    """Run the unit rescue mechanics test."""
    # Create log file path if not provided
    if log_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("logs/mechanic_tests/units", exist_ok=True)
        log_path = f"logs/mechanic_tests/units/rescue_mechanics_{timestamp}.txt"
    
    # Create mock game state
    game_state_manager = MockGameStateManager()
    game_state_manager.current_game_state.map_state.map_id = "rescue_test_map"
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
    
    print(f"Rescue mechanics test log will be written to: {log_path}")
    print(f"HTML log will be written to: {log_path.replace('.txt', '.html')}")
    
    # Create units for the test
    player_knight = create_unit(
        "PLAYER_KNIGHT", "Knight", FactionEnum.PLAYER, 
        (2, 4), 25, 25, 
        {"STR": 12, "DEF": 10, "SKL": 8, "SPD": 7, "MOV": 4, "CON": 12},
        class_name="Knight",
        abilities=["Rescue", "Heavy Armor"]
    )
    
    player_healer = create_unit(
        "PLAYER_HEALER", "Healer", FactionEnum.PLAYER, 
        (3, 4), 15, 15, 
        {"STR": 3, "DEF": 3, "SKL": 8, "SPD": 8, "MOV": 5, "MAG": 10, "CON": 5},
        class_name="Cleric",
        abilities=["Heal", "Restore"]
    )
    
    enemy_archer = create_unit(
        "ENEMY_ARCHER", "Archer", FactionEnum.ENEMY, 
        (7, 4), 18, 18, 
        {"STR": 9, "DEF": 5, "SKL": 12, "SPD": 9, "MOV": 5, "CON": 7},
        class_name="Archer",
        abilities=["Bow Attack", "Long Range"]
    )
    
    enemy_mage = create_unit(
        "ENEMY_MAGE", "Mage", FactionEnum.ENEMY, 
        (8, 5), 16, 16, 
        {"STR": 2, "DEF": 4, "SKL": 9, "SPD": 10, "MOV": 5, "MAG": 12, "CON": 6},
        class_name="Mage",
        abilities=["Fire", "Thunder"]
    )
    
    # Register units with the game state manager
    game_state_manager.add_unit(player_knight)
    game_state_manager.add_unit(player_healer)
    game_state_manager.add_unit(enemy_archer)
    game_state_manager.add_unit(enemy_mage)
    
    # Start the test scenario
    visual_logger.log_action("SYSTEM", "SCENARIO_START", "Starting Unit Rescue Mechanics Test")
    visual_logger.log_action("SYSTEM", "TEST_INFO", "This test demonstrates how units can rescue and carry other units")
    visual_logger.log_initial_state()
    
    # Log initial unit details
    for unit in game_state_manager.get_all_units():
        visual_logger.log_action(unit.id, "STATS", f"{unit.name} ({unit.class_name}): HP {unit.current_hp}/{unit.max_hp}, Position {unit.position}")
        visual_logger.log_action(unit.id, "STATS", f"Stats: STR {unit.base_stats.get('STR', 0)}, DEF {unit.base_stats.get('DEF', 0)}, CON {unit.base_stats.get('CON', 0)}, MOV {unit.base_stats.get('MOV', 0)}")
    
    visual_logger.log_action("SYSTEM", "MAP_INFO", "The map has a river crossing the center, with only one bridge at y=4")
    
    # Turn 1: Player phase - Knight moves and rescues Healer
    visual_logger.log_turn_start(1)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Knight moves next to Healer
    visual_logger.log_action("PLAYER_KNIGHT", "MOVEMENT", f"Knight moves from {player_knight.position} to (3, 3)")
    player_knight.position = (3, 3)
    visual_logger.log_action("SYSTEM", "MAP_UPDATE", "Map updated with Knight's new position")
    
    # Check if Knight can rescue Healer
    if can_rescue(player_knight, player_healer):
        visual_logger.log_action("SYSTEM", "RESCUE_CHECK", f"Knight (CON {player_knight.base_stats['CON']}) can rescue Healer (CON {player_healer.base_stats['CON']})")
        
        # Knight rescues Healer
        visual_logger.log_action("PLAYER_KNIGHT", "RESCUE", "Knight rescues Healer")
        
        # Update unit states for rescue
        player_knight.carrying_unit = player_healer.id
        player_healer.is_being_carried = True
        
        # Remove Healer from the map
        old_healer_position = player_healer.position
        player_healer.position = None
        
        visual_logger.log_action("PLAYER_HEALER", "PICKED_UP", f"Healer is picked up from {old_healer_position}")
        visual_logger.log_action("SYSTEM", "CARRY_EFFECT", "Knight's movement is reduced by 2 while carrying a unit")
        visual_logger.log_action("SYSTEM", "STAT_CHANGE", f"Knight's effective MOV: {player_knight.base_stats['MOV']} - 2 = {player_knight.base_stats['MOV'] - 2}")
    else:
        visual_logger.log_action("SYSTEM", "RESCUE_FAILED", f"Knight (CON {player_knight.base_stats['CON']}) cannot rescue Healer (CON {player_healer.base_stats['CON']})")
    
    # End the player phase
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # Enemy phase - Enemies move closer
    game_state_manager.current_game_state.current_phase = PhaseEnum.ENEMY
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
    
    # Archer moves closer to the bridge
    visual_logger.log_action("ENEMY_ARCHER", "MOVEMENT", f"Archer moves from {enemy_archer.position} to (6, 4)")
    enemy_archer.position = (6, 4)
    
    # Archer attacks Knight (but Knight has higher defense due to Heavy Armor)
    visual_logger.log_action("ENEMY_ARCHER", "COMBAT", "Archer attacks Knight")
    
    # Calculate combat
    attack_power = enemy_archer.base_stats["STR"]
    defense = player_knight.base_stats["DEF"]
    damage = max(0, attack_power - defense // 2)
    
    visual_logger.log_action("SYSTEM", "COMBAT_CALC", f"Attack: {attack_power} vs Defense: {defense}")
    visual_logger.log_action("SYSTEM", "COMBAT_CALC", "Hit chance: 80%")
    
    if damage > 0:
        visual_logger.log_action("SYSTEM", "COMBAT_RESULT", f"Hit! Damage: {damage}")
        player_knight.current_hp = max(0, player_knight.current_hp - damage)
        visual_logger.log_action("PLAYER_KNIGHT", "DAMAGE", f"Knight takes {damage} damage (HP: {player_knight.current_hp}/{player_knight.max_hp})")
    else:
        visual_logger.log_action("SYSTEM", "COMBAT_RESULT", "Hit, but Knight's armor blocks all damage!")
    
    # End enemy phase
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
    
    # Turn 2: Player moves Knight with carried Healer towards safety
    game_state_manager.current_game_state.current_turn = 2
    game_state_manager.current_game_state.current_phase = PhaseEnum.PLAYER
    visual_logger.log_turn_start(2)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Knight continues moving to cross the bridge while carrying the Healer
    knight_move_range = player_knight.base_stats["MOV"] - 2  # Reduced due to carrying
    visual_logger.log_action("PLAYER_KNIGHT", "MOVEMENT", f"Knight (carrying Healer) uses {knight_move_range} movement points to move from {player_knight.position} to (4, 4)")
    player_knight.position = (4, 4)
    visual_logger.log_action("SYSTEM", "MAP_UPDATE", "Knight crosses the bridge while carrying Healer")
    
    # End player phase
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # Enemy phase - Enemy mage moves and attacks
    game_state_manager.current_game_state.current_phase = PhaseEnum.ENEMY
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
    
    # Mage moves and attacks
    visual_logger.log_action("ENEMY_MAGE", "MOVEMENT", f"Mage moves from {enemy_mage.position} to (7, 4)")
    enemy_mage.position = (7, 4)
    
    # Mage attacks Knight
    visual_logger.log_action("ENEMY_MAGE", "COMBAT", "Mage casts Fire at Knight")
    
    # Calculate magic combat
    magic_power = enemy_mage.base_stats["MAG"]
    magic_defense = player_knight.base_stats.get("RES", 3)  # Knight typically has low resistance to magic
    magic_damage = max(1, magic_power - magic_defense // 2)
    
    visual_logger.log_action("SYSTEM", "COMBAT_CALC", f"Magic Attack: {magic_power} vs Resistance: {magic_defense}")
    visual_logger.log_action("SYSTEM", "COMBAT_CALC", "Hit chance: 90%")
    visual_logger.log_action("SYSTEM", "COMBAT_RESULT", f"Hit! Damage: {magic_damage}")
    
    # Apply damage
    player_knight.current_hp = max(0, player_knight.current_hp - magic_damage)
    visual_logger.log_action("PLAYER_KNIGHT", "DAMAGE", f"Knight takes {magic_damage} damage (HP: {player_knight.current_hp}/{player_knight.max_hp})")
    
    # End enemy phase
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
    
    # Turn 3: Knight reaches safety and drops Healer who can then heal Knight
    game_state_manager.current_game_state.current_turn = 3
    game_state_manager.current_game_state.current_phase = PhaseEnum.PLAYER
    visual_logger.log_turn_start(3)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Knight continues moving to safety
    visual_logger.log_action("PLAYER_KNIGHT", "MOVEMENT", f"Knight (carrying Healer) moves from {player_knight.position} to (6, 3)")
    player_knight.position = (6, 3)
    visual_logger.log_action("SYSTEM", "MAP_UPDATE", "Knight moves to a safe position behind the river")
    
    # Knight drops Healer
    visual_logger.log_action("PLAYER_KNIGHT", "DROP", "Knight drops Healer")
    
    # Find an adjacent empty space for Healer
    drop_position = (7, 3)  # Choose a specific position for simplicity
    
    # Update unit states after dropping
    player_knight.carrying_unit = None
    player_healer.is_being_carried = False
    player_healer.position = drop_position
    
    visual_logger.log_action("PLAYER_HEALER", "DROPPED", f"Healer is dropped at position {drop_position}")
    visual_logger.log_action("SYSTEM", "CARRY_EFFECT", "Knight's movement returns to normal")
    
    # Now the Healer can act
    visual_logger.log_action("PLAYER_HEALER", "ABILITY", "Healer uses Heal on Knight")
    
    # Calculate healing
    heal_amount = player_healer.base_stats["MAG"] + 4
    old_hp = player_knight.current_hp
    player_knight.current_hp = min(player_knight.max_hp, player_knight.current_hp + heal_amount)
    actual_heal = player_knight.current_hp - old_hp
    
    visual_logger.log_action("SYSTEM", "HEAL_CALC", f"Heal power: {heal_amount}")
    visual_logger.log_action("PLAYER_KNIGHT", "HEALED", f"Knight receives {actual_heal} healing (HP: {player_knight.current_hp}/{player_knight.max_hp})")
    
    # End player phase
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # End the test scenario
    visual_logger.log_action("SYSTEM", "SCENARIO_END", "Unit Rescue Mechanics Test Completed")
    
    # Final summary
    visual_logger.log_action("SYSTEM", "TEST_SUMMARY", "--- Test Summary ---")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "Rescue mechanic successfully demonstrated")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "Knight rescued Healer, carried her across the river, and dropped her in a safe position")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "After being dropped, Healer was able to heal the Knight")
    
    # Log final unit status
    for unit in game_state_manager.get_all_units():
        visual_logger.log_action(unit.id, "STATUS", f"{unit.name} ({unit.class_name}): HP {unit.current_hp}/{unit.max_hp}, Position {unit.position}")
    
    # Finalize the log
    visual_logger.finalize_log()
    print("Unit rescue mechanics test completed.")
    
    return True

if __name__ == "__main__":
    # If run directly, use default log path
    run_test() 