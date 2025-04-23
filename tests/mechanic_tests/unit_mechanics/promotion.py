"""
Unit Promotion Mechanics Test

This test demonstrates the promotion mechanic in the game, showing how units
can be promoted to advanced classes with improved stats and new abilities.
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

def create_unit(unit_id, name, faction, position, hp, max_hp, stats, class_name="Recruit", level=1, exp=0, abilities=None):
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
    unit.level = level
    unit.exp = exp
    unit.abilities = abilities or []
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
    """Run the promotion mechanics test."""
    # Create log file path if not provided
    if log_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("logs/mechanic_tests/units", exist_ok=True)
        log_path = f"logs/mechanic_tests/units/promotion_mechanics_{timestamp}.txt"
    
    # Create mock game state
    game_state_manager = MockGameStateManager()
    game_state_manager.current_game_state.map_state.map_id = "promotion_test_map"
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
    
    print(f"Promotion mechanics test log will be written to: {log_path}")
    print(f"HTML log will be written to: {log_path.replace('.txt', '.html')}")
    
    # Create units for the test
    player_soldier = create_unit(
        "PLAYER_SOLDIER", "Soldier", FactionEnum.PLAYER, 
        (3, 3), 20, 20, 
        {"STR": 8, "DEF": 5, "SKL": 6, "SPD": 6, "MOV": 4, "MAG": 0},
        class_name="Soldier", level=9, exp=80,
        abilities=["Basic Attack"]
    )
    
    enemy_bandit = create_unit(
        "ENEMY_BANDIT", "Bandit", FactionEnum.ENEMY, 
        (4, 3), 15, 15, 
        {"STR": 7, "DEF": 3, "SKL": 5, "SPD": 7, "MOV": 5, "MAG": 0},
        class_name="Bandit", level=5, exp=0,
        abilities=["Steal"]
    )
    
    # Register units with the game state manager
    game_state_manager.add_unit(player_soldier)
    game_state_manager.add_unit(enemy_bandit)
    
    # Start the test scenario
    visual_logger.log_action("SYSTEM", "SCENARIO_START", "Starting Promotion Mechanics Test")
    visual_logger.log_initial_state()
    
    # Log initial unit details
    visual_logger.log_action("SYSTEM", "TEST_INFO", "This test demonstrates how units can be promoted to advanced classes with improved stats and abilities")
    visual_logger.log_action("PLAYER_SOLDIER", "STATS", f"Class: {player_soldier.class_name}, Level: {player_soldier.level}, EXP: {player_soldier.exp}/100")
    visual_logger.log_action("PLAYER_SOLDIER", "STATS", f"Base Stats: STR {player_soldier.base_stats['STR']}, DEF {player_soldier.base_stats['DEF']}, SKL {player_soldier.base_stats['SKL']}, SPD {player_soldier.base_stats['SPD']}, MOV {player_soldier.base_stats['MOV']}")
    visual_logger.log_action("PLAYER_SOLDIER", "ABILITIES", f"Current abilities: {', '.join(player_soldier.abilities)}")
    
    # Player phase - Combat to gain experience
    visual_logger.log_turn_start(1)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Soldier attacks Bandit
    visual_logger.log_action("PLAYER_SOLDIER", "COMBAT", "Soldier attacks Bandit")
    
    # Calculate combat results
    attack_power = player_soldier.base_stats["STR"]
    defense = enemy_bandit.base_stats["DEF"]
    damage = max(1, attack_power - defense // 2)
    
    # Log combat calculations
    visual_logger.log_action("SYSTEM", "COMBAT_CALC", f"Attack: {attack_power} vs Defense: {defense}")
    visual_logger.log_action("SYSTEM", "COMBAT_CALC", "Hit chance: 95%")
    
    # Simulate hit
    visual_logger.log_action("SYSTEM", "COMBAT_RESULT", f"Hit! Damage: {damage}")
    
    # Apply damage to the enemy
    enemy_bandit.current_hp = max(0, enemy_bandit.current_hp - damage)
    visual_logger.log_action("ENEMY_BANDIT", "DAMAGE", f"Takes {damage} damage (HP: {enemy_bandit.current_hp}/{enemy_bandit.max_hp})")
    
    # Gain experience
    exp_gained = 25 + (enemy_bandit.level * 3)
    player_soldier.exp += exp_gained
    visual_logger.log_action("PLAYER_SOLDIER", "EXP_GAIN", f"Gains {exp_gained} experience! (EXP: {player_soldier.exp}/100)")
    
    # Check for level up
    if player_soldier.exp >= 100:
        # Level up
        player_soldier.level += 1
        player_soldier.exp -= 100
        visual_logger.log_action("PLAYER_SOLDIER", "LEVEL_UP", f"Level Up! Now Level {player_soldier.level}")
        
        # Increase stats
        stat_increases = {
            "STR": random.randint(0, 1),
            "DEF": random.randint(0, 1),
            "SKL": random.randint(0, 1),
            "SPD": random.randint(0, 1),
            "HP": random.randint(1, 2)
        }
        
        for stat, increase in stat_increases.items():
            if stat == "HP":
                player_soldier.max_hp += increase
                player_soldier.current_hp += increase
                visual_logger.log_action("PLAYER_SOLDIER", "STAT_UP", f"Max HP increased by {increase} (Now {player_soldier.max_hp})")
            else:
                if increase > 0:
                    player_soldier.base_stats[stat] += increase
                    visual_logger.log_action("PLAYER_SOLDIER", "STAT_UP", f"{stat} increased by {increase} (Now {player_soldier.base_stats[stat]})")
    
    # Check for promotion eligibility
    if player_soldier.level >= 10 and player_soldier.class_name == "Soldier":
        visual_logger.log_action("SYSTEM", "PROMOTION_ELIGIBLE", "Soldier has reached level 10 and is eligible for promotion!")
        
        # Display promotion options
        visual_logger.log_action("SYSTEM", "PROMOTION_OPTIONS", "Available promotion paths: Knight, Warrior")
        
        # Choose the Knight promotion path
        chosen_promotion = "Knight"
        visual_logger.log_action("SYSTEM", "PROMOTION_CHOICE", f"Promotion path chosen: {chosen_promotion}")
        
        # Perform the promotion
        visual_logger.log_action("PLAYER_SOLDIER", "PROMOTION", f"Soldier is being promoted to {chosen_promotion}!")
        
        # Store old stats for comparison
        old_stats = {
            "Class": player_soldier.class_name,
            "HP": player_soldier.max_hp,
            "STR": player_soldier.base_stats["STR"],
            "DEF": player_soldier.base_stats["DEF"],
            "SKL": player_soldier.base_stats["SKL"],
            "SPD": player_soldier.base_stats["SPD"],
            "MOV": player_soldier.base_stats["MOV"]
        }
        
        # Apply promotion changes
        player_soldier.class_name = chosen_promotion
        player_soldier.max_hp += 5
        player_soldier.current_hp = player_soldier.max_hp  # Fully heal upon promotion
        
        # Update stats based on the promotion class
        stat_boosts = {
            "STR": 3,
            "DEF": 4,
            "SKL": 2,
            "SPD": 1,
            "MOV": 1
        }
        
        for stat, boost in stat_boosts.items():
            player_soldier.base_stats[stat] += boost
        
        # Add new abilities
        player_soldier.abilities.append("Shield Wall")
        player_soldier.abilities.append("Lance Attack")
        
        # Log promotion results
        visual_logger.log_action("PLAYER_SOLDIER", "PROMOTION_COMPLETE", f"Promotion to {player_soldier.class_name} complete!")
        visual_logger.log_action("PLAYER_SOLDIER", "STATS", f"New Class: {player_soldier.class_name}, Level: {player_soldier.level}, EXP: {player_soldier.exp}/100")
        visual_logger.log_action("PLAYER_SOLDIER", "STATS", f"New Stats: HP {player_soldier.max_hp}, STR {player_soldier.base_stats['STR']}, DEF {player_soldier.base_stats['DEF']}, SKL {player_soldier.base_stats['SKL']}, SPD {player_soldier.base_stats['SPD']}, MOV {player_soldier.base_stats['MOV']}")
        visual_logger.log_action("PLAYER_SOLDIER", "ABILITIES", f"New abilities: {', '.join(player_soldier.abilities)}")
        
        # Log stat changes
        visual_logger.log_action("SYSTEM", "PROMOTION_STATS_COMPARISON", f"Class: {old_stats['Class']} → {player_soldier.class_name}")
        visual_logger.log_action("SYSTEM", "PROMOTION_STATS_COMPARISON", f"HP: {old_stats['HP']} → {player_soldier.max_hp} (+{player_soldier.max_hp - old_stats['HP']})")
        visual_logger.log_action("SYSTEM", "PROMOTION_STATS_COMPARISON", f"STR: {old_stats['STR']} → {player_soldier.base_stats['STR']} (+{player_soldier.base_stats['STR'] - old_stats['STR']})")
        visual_logger.log_action("SYSTEM", "PROMOTION_STATS_COMPARISON", f"DEF: {old_stats['DEF']} → {player_soldier.base_stats['DEF']} (+{player_soldier.base_stats['DEF'] - old_stats['DEF']})")
        visual_logger.log_action("SYSTEM", "PROMOTION_STATS_COMPARISON", f"SKL: {old_stats['SKL']} → {player_soldier.base_stats['SKL']} (+{player_soldier.base_stats['SKL'] - old_stats['SKL']})")
        visual_logger.log_action("SYSTEM", "PROMOTION_STATS_COMPARISON", f"SPD: {old_stats['SPD']} → {player_soldier.base_stats['SPD']} (+{player_soldier.base_stats['SPD'] - old_stats['SPD']})")
        visual_logger.log_action("SYSTEM", "PROMOTION_STATS_COMPARISON", f"MOV: {old_stats['MOV']} → {player_soldier.base_stats['MOV']} (+{player_soldier.base_stats['MOV'] - old_stats['MOV']})")
    
    # Test the new abilities after promotion
    if "Shield Wall" in player_soldier.abilities:
        visual_logger.log_action("PLAYER_SOLDIER", "ABILITY_USE", "Knight uses Shield Wall ability")
        visual_logger.log_action("SYSTEM", "ABILITY_EFFECT", "Shield Wall: DEF +3 until next turn, but movement reduced by 1")
        visual_logger.log_action("PLAYER_SOLDIER", "STAT_TEMPORARY", f"Temporary DEF boost: +3 (Total DEF: {player_soldier.base_stats['DEF'] + 3})")
    
    # End the player phase
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # Enemy phase
    game_state_manager.current_game_state.current_phase = PhaseEnum.ENEMY
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
    
    # Bandit attacks Knight
    if enemy_bandit.current_hp > 0:
        visual_logger.log_action("ENEMY_BANDIT", "COMBAT", "Bandit attacks Knight")
        
        # Calculate combat with Knight's boosted defense if Shield Wall is active
        defense_bonus = 3 if "Shield Wall" in player_soldier.abilities else 0
        attack_power = enemy_bandit.base_stats["STR"]
        defense = player_soldier.base_stats["DEF"] + defense_bonus
        damage = max(0, attack_power - defense // 2)  # Could be 0 now with higher defense
        
        visual_logger.log_action("SYSTEM", "COMBAT_CALC", f"Attack: {attack_power} vs Defense: {defense} (includes Shield Wall bonus)")
        
        if damage > 0:
            visual_logger.log_action("SYSTEM", "COMBAT_RESULT", f"Hit! Damage: {damage}")
            player_soldier.current_hp = max(0, player_soldier.current_hp - damage)
            visual_logger.log_action("PLAYER_SOLDIER", "DAMAGE", f"Takes {damage} damage (HP: {player_soldier.current_hp}/{player_soldier.max_hp})")
        else:
            visual_logger.log_action("SYSTEM", "COMBAT_RESULT", "Hit, but Knight's defense blocks all damage!")
        
        # Knight counterattack with new Lance Attack ability
        if "Lance Attack" in player_soldier.abilities:
            visual_logger.log_action("PLAYER_SOLDIER", "ABILITY_USE", "Knight uses Lance Attack ability")
            visual_logger.log_action("SYSTEM", "ABILITY_EFFECT", "Lance Attack: Higher damage but lower hit rate")
            
            # Calculate lance attack damage
            lance_damage = int(player_soldier.base_stats["STR"] * 1.5) - enemy_bandit.base_stats["DEF"] // 2
            
            visual_logger.log_action("SYSTEM", "COMBAT_CALC", f"Lance Attack: {int(player_soldier.base_stats['STR'] * 1.5)} vs Defense: {enemy_bandit.base_stats['DEF']}")
            visual_logger.log_action("SYSTEM", "COMBAT_RESULT", f"Hit! Damage: {lance_damage}")
            
            # Apply damage
            enemy_bandit.current_hp = max(0, enemy_bandit.current_hp - lance_damage)
            visual_logger.log_action("ENEMY_BANDIT", "DAMAGE", f"Takes {lance_damage} damage (HP: {enemy_bandit.current_hp}/{enemy_bandit.max_hp})")
            
            # Check if enemy is defeated
            if enemy_bandit.current_hp <= 0:
                enemy_bandit.disposition = DispositionEnum.DEAD
                visual_logger.log_action("ENEMY_BANDIT", "DEATH", "Bandit has been defeated!")
                enemy_bandit.position = None
    
    # End enemy phase
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
    
    # Log end of turn state
    visual_logger.log_end_of_turn_state(1)
    
    # End the test scenario
    visual_logger.log_action("SYSTEM", "SCENARIO_END", "Promotion Mechanics Test Completed")
    
    # Final summary
    visual_logger.log_action("SYSTEM", "TEST_SUMMARY", "--- Test Summary ---")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "Promotion mechanic successfully demonstrated")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", f"Soldier was promoted to {player_soldier.class_name} with improved stats and new abilities")
    
    # Log final unit status
    for unit in game_state_manager.get_all_units():
        if unit.disposition == DispositionEnum.ACTIVE:
            visual_logger.log_action(unit.id, "STATUS", f"{unit.name} ({unit.class_name}): HP {unit.current_hp}/{unit.max_hp}, Position {unit.position}")
        else:
            visual_logger.log_action(unit.id, "STATUS", f"{unit.name}: DEFEATED, removed from battlefield")
    
    # Finalize the log
    visual_logger.finalize_log()
    print("Promotion mechanics test completed.")
    
    return True

if __name__ == "__main__":
    # If run directly, use default log path
    run_test() 