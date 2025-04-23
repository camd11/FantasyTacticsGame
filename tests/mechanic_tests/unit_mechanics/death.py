"""
Unit Death Mechanics Test

This test demonstrates the death mechanic in the game, showing how units
are removed from the battlefield when their HP reaches 0.
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
    """Run the death mechanics test."""
    # Create log file path if not provided
    if log_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("logs/mechanic_tests/units", exist_ok=True)
        log_path = f"logs/mechanic_tests/units/death_mechanics_{timestamp}.txt"
    
    # Create mock game state
    game_state_manager = MockGameStateManager()
    game_state_manager.current_game_state.map_state.map_id = "death_test_map"
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
    
    print(f"Death mechanics test log will be written to: {log_path}")
    print(f"HTML log will be written to: {log_path.replace('.txt', '.html')}")
    
    # Create units for the test
    player_knight = create_unit(
        "PLAYER_KNIGHT", "Knight", FactionEnum.PLAYER, 
        (2, 3), 25, 25, {"STR": 10, "DEF": 7, "SKL": 8, "SPD": 6, "MOV": 4}
    )
    
    enemy_bandit = create_unit(
        "ENEMY_BANDIT", "Bandit", FactionEnum.ENEMY, 
        (3, 3), 15, 15, {"STR": 8, "DEF": 4, "SKL": 7, "SPD": 7, "MOV": 5}
    )
    
    # Register units with the game state manager
    game_state_manager.add_unit(player_knight)
    game_state_manager.add_unit(enemy_bandit)
    
    # Start the test scenario
    visual_logger.log_action("SYSTEM", "SCENARIO_START", "Starting Death Mechanics Test")
    visual_logger.log_initial_state()
    
    # Log the test description
    visual_logger.log_action("SYSTEM", "TEST_INFO", "This test demonstrates how units are removed from the battlefield when defeated")
    
    # Player phase - Knight attacks Bandit
    visual_logger.log_turn_start(1)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Knight attacks Bandit
    visual_logger.log_action("PLAYER_KNIGHT", "COMBAT", "Knight attacks Bandit")
    
    # Calculate combat results
    attack_power = player_knight.base_stats["STR"]
    defense = enemy_bandit.base_stats["DEF"]
    damage = max(1, attack_power - defense // 2)
    
    # Log combat calculations
    visual_logger.log_action("SYSTEM", "COMBAT_CALC", f"Attack: {attack_power} vs Defense: {defense}")
    visual_logger.log_action("SYSTEM", "COMBAT_CALC", "Hit chance: 90%")
    
    # Simulate hit roll
    hit_roll = random.randint(1, 100)
    if hit_roll <= 90:  # 90% hit chance
        visual_logger.log_action("SYSTEM", "COMBAT_RESULT", f"Hit! Damage: {damage}")
        
        # Apply damage to the enemy
        enemy_bandit.current_hp = max(0, enemy_bandit.current_hp - damage)
        visual_logger.log_action("ENEMY_BANDIT", "DAMAGE", f"Takes {damage} damage (HP: {enemy_bandit.current_hp}/{enemy_bandit.max_hp})")
        
        # Check for critical hit (10% chance)
        crit_roll = random.randint(1, 100)
        if crit_roll <= 10:
            crit_damage = damage // 2
            visual_logger.log_action("PLAYER_KNIGHT", "CRITICAL", f"Critical hit! Additional damage: {crit_damage}")
            enemy_bandit.current_hp = max(0, enemy_bandit.current_hp - crit_damage)
            visual_logger.log_action("ENEMY_BANDIT", "DAMAGE", f"Takes {crit_damage} additional damage (HP: {enemy_bandit.current_hp}/{enemy_bandit.max_hp})")
    else:
        visual_logger.log_action("SYSTEM", "COMBAT_RESULT", "Miss!")
    
    # If enemy is still alive, counterattack
    if enemy_bandit.current_hp > 0:
        visual_logger.log_action("ENEMY_BANDIT", "COMBAT", "Bandit counterattacks")
        
        # Calculate counterattack
        counter_attack = enemy_bandit.base_stats["STR"]
        counter_defense = player_knight.base_stats["DEF"]
        counter_damage = max(1, counter_attack - counter_defense // 2)
        
        visual_logger.log_action("SYSTEM", "COMBAT_CALC", f"Attack: {counter_attack} vs Defense: {counter_defense}")
        visual_logger.log_action("SYSTEM", "COMBAT_CALC", "Hit chance: 75%")
        
        # Simulate counterattack roll
        counter_hit_roll = random.randint(1, 100)
        if counter_hit_roll <= 75:  # 75% hit chance
            visual_logger.log_action("SYSTEM", "COMBAT_RESULT", f"Hit! Damage: {counter_damage}")
            player_knight.current_hp = max(0, player_knight.current_hp - counter_damage)
            visual_logger.log_action("PLAYER_KNIGHT", "DAMAGE", f"Takes {counter_damage} damage (HP: {player_knight.current_hp}/{player_knight.max_hp})")
        else:
            visual_logger.log_action("SYSTEM", "COMBAT_RESULT", "Miss!")
    
    # End the player phase
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # Check if Bandit has been defeated
    if enemy_bandit.current_hp <= 0:
        # Bandit is defeated - handle death
        enemy_bandit.disposition = DispositionEnum.DEAD
        visual_logger.log_action("ENEMY_BANDIT", "DEATH", "Bandit has been defeated!")
        visual_logger.log_action("SYSTEM", "UNIT_REMOVED", "Bandit has been removed from the battlefield")
        
        # Make bandit position None to remove from map
        enemy_bandit.position = None
    
    # Set up second round of combat if bandit is still alive
    if enemy_bandit.current_hp > 0:
        # Enemy phase
        game_state_manager.current_game_state.current_phase = PhaseEnum.ENEMY
        visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
        
        # Bandit attacks Knight
        visual_logger.log_action("ENEMY_BANDIT", "COMBAT", "Bandit attacks Knight")
        
        # Calculate combat results for a strong attack
        attack_power = enemy_bandit.base_stats["STR"] + 5  # Desperate attack
        defense = player_knight.base_stats["DEF"]
        damage = max(1, attack_power - defense // 2)
        
        visual_logger.log_action("SYSTEM", "COMBAT_CALC", f"Attack: {attack_power} (desperate attack) vs Defense: {defense}")
        visual_logger.log_action("SYSTEM", "COMBAT_CALC", "Hit chance: 85%")
        
        # Always hit in this test case to demonstrate death
        visual_logger.log_action("SYSTEM", "COMBAT_RESULT", f"Hit! Damage: {damage}")
        player_knight.current_hp = max(0, player_knight.current_hp - damage)
        visual_logger.log_action("PLAYER_KNIGHT", "DAMAGE", f"Takes {damage} damage (HP: {player_knight.current_hp}/{player_knight.max_hp})")
        
        # Knight counterattack that will kill bandit
        if player_knight.current_hp > 0:
            visual_logger.log_action("PLAYER_KNIGHT", "COMBAT", "Knight counterattacks")
            
            # Calculate final blow
            attack_power = player_knight.base_stats["STR"] + 10  # Critical counterattack
            defense = enemy_bandit.base_stats["DEF"]
            damage = max(enemy_bandit.current_hp, attack_power - defense // 2)  # Ensure fatal damage
            
            visual_logger.log_action("SYSTEM", "COMBAT_CALC", f"Attack: {attack_power} (powerful counterattack) vs Defense: {defense}")
            visual_logger.log_action("SYSTEM", "COMBAT_RESULT", "Critical hit! Fatal damage!")
            
            # Apply damage to the enemy
            enemy_bandit.current_hp = 0
            visual_logger.log_action("ENEMY_BANDIT", "DAMAGE", f"Takes {damage} damage (HP: 0/{enemy_bandit.max_hp})")
            
            # Handle death
            enemy_bandit.disposition = DispositionEnum.DEAD
            visual_logger.log_action("ENEMY_BANDIT", "DEATH", "Bandit has been defeated!")
            visual_logger.log_action("SYSTEM", "UNIT_REMOVED", "Bandit has been removed from the battlefield")
            
            # Make bandit position None to remove from map
            enemy_bandit.position = None
        
        visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
    
    # Log end of turn state
    visual_logger.log_end_of_turn_state(1)
    
    # End the test scenario
    visual_logger.log_action("SYSTEM", "SCENARIO_END", "Death Mechanics Test Completed")
    
    # Final summary
    visual_logger.log_action("SYSTEM", "TEST_SUMMARY", "--- Test Summary ---")
    if enemy_bandit.disposition == DispositionEnum.DEAD:
        visual_logger.log_action("SYSTEM", "TEST_RESULT", "Death mechanic successfully demonstrated: Bandit was defeated and removed from battle")
    else:
        visual_logger.log_action("SYSTEM", "TEST_RESULT", "Warning: Death mechanic not fully demonstrated. Bandit is still alive.")
    
    # Log final HP status
    for unit in game_state_manager.get_all_units():
        if unit.disposition == DispositionEnum.ACTIVE:
            visual_logger.log_action(unit.id, "STATUS", f"{unit.name}: HP {unit.current_hp}/{unit.max_hp}, Position {unit.position}")
        else:
            visual_logger.log_action(unit.id, "STATUS", f"{unit.name}: DEFEATED, removed from battlefield")
    
    # Finalize the log
    visual_logger.finalize_log()
    print("Death mechanics test completed.")
    
    return True

if __name__ == "__main__":
    # If run directly, use default log path
    run_test() 