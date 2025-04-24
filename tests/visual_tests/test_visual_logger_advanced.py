"""
Advanced Visual Logger Test Script

This script demonstrates advanced visualization techniques using the enhanced VisualScenarioLogger
to display terrain effects, weather impacts, and dynamic battle events.
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

# Mock classes for testing
class MockTerrainData:
    def __init__(self, type_name, defense_bonus=0, evasion_bonus=0, movement_cost=1):
        self.type = type_name
        self.defense_bonus = defense_bonus
        self.evasion_bonus = evasion_bonus
        self.movement_cost = movement_cost

class MockMapSystem:
    def __init__(self):
        self.terrain_data = {
            (1, 1): MockTerrainData("PLAIN", 0, 0, 1),
            (2, 1): MockTerrainData("FOREST", 2, 10, 2),
            (3, 1): MockTerrainData("MOUNTAIN", 3, 15, 3),
            (4, 1): MockTerrainData("RIVER", 0, 5, 2),
            (2, 2): MockTerrainData("BRIDGE", 0, 0, 1),
            (3, 3): MockTerrainData("VILLAGE", 1, 5, 1),
            (4, 4): MockTerrainData("CASTLE", 3, 10, 1),
        }
    
    def get_terrain_data_at(self, position):
        return self.terrain_data.get(position, MockTerrainData("PLAIN"))

class MockWeatherSystem:
    def __init__(self):
        self.current_weather = "CLEAR"
        self.weather_effects = {
            "CLEAR": {},
            "RAIN": {"accuracy": -10, "movement": -1},
            "FOG": {"visibility": -2, "accuracy": -15},
            "SNOW": {"movement": -2, "evasion": -5},
            "SANDSTORM": {"accuracy": -20, "damage": -1}
        }
    
    def get_current_weather(self):
        return self.current_weather
    
    def get_weather_effects(self):
        return self.weather_effects.get(self.current_weather, {})
    
    def change_weather(self, new_weather):
        if new_weather in self.weather_effects:
            self.current_weather = new_weather
            return True
        return False

class MockCliDisplay:
    def __init__(self):
        self.game_state_manager = None
        self.map_system = None
        self.terrain_chars = {
            "PLAIN": ".",
            "FOREST": "T",
            "MOUNTAIN": "^",
            "RIVER": "~",
            "BRIDGE": "=",
            "VILLAGE": "v",
            "CASTLE": "C",
        }
        self.unit_chars = {
            FactionEnum.PLAYER: "P",
            FactionEnum.ENEMY: "E",
            FactionEnum.NPC: "N",
        }
    
    def render_ascii_map(self):
        """Return a dynamic ASCII map based on current game state."""
        if not self.game_state_manager:
            return "Error: No game state manager"
        
        terrain_grid = [
            [".", ".", ".", ".", ".", ".", "."],
            [".", ".", "T", "^", "~", ".", "."],
            [".", ".", "=", ".", ".", ".", "."],
            [".", ".", ".", "v", ".", ".", "."],
            [".", ".", ".", ".", "C", ".", "."],
            [".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", "."],
        ]
        
        map_string = "=== ASCII MAP (Turn {}, {} Phase) ===\n".format(
            self.game_state_manager.current_game_state.current_turn,
            self.game_state_manager.current_game_state.current_phase.name
        )
        map_string += "   " + "".join([str(i) for i in range(7)]) + "\n"
        
        # Get unit positions
        units = {}
        for unit in self.game_state_manager.get_all_units():
            if hasattr(unit, 'position') and unit.position and unit.disposition == DispositionEnum.ACTIVE:
                units[unit.position] = unit
        
        # Generate map
        for y in range(7):
            map_string += f" {y} "
            for x in range(7):
                pos = (x, y)
                # Check if unit at this position
                if pos in units:
                    unit = units[pos]
                    map_string += self.unit_chars.get(unit.faction, "?")
                else:
                    # Otherwise show terrain
                    map_string += terrain_grid[y][x]
            map_string += "\n"
        
        return map_string

class MockGameStateManager:
    def __init__(self):
        self.current_game_state = GameState()
        self.current_game_state.map_state = MapState()
        self.current_game_state.map_state.map_id = "advanced_test_map"
        self.current_game_state.current_turn = 1
        self.current_game_state.current_phase = PhaseEnum.PLAYER
        self.units = {}
        self.all_units = []
    
    def get_unit(self, unit_id):
        """Return a unit for the given ID."""
        return self.units.get(unit_id)
    
    def get_all_units(self):
        """Return all units."""
        return self.all_units
    
    def register_unit(self, unit):
        """Register a unit with the game state manager."""
        self.units[unit.id] = unit
        if unit not in self.all_units:
            self.all_units.append(unit)

# Helper function to create a unit
def create_unit(unit_id, name, faction, position, hp, max_hp, stats):
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

def main():
    """Run the advanced visual logger test."""
    # Create output directory
    os.makedirs("logs/advanced", exist_ok=True)
    
    # Create log file paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join("logs/advanced", f"visual_log_advanced_{timestamp}.txt")
    
    # Create mock systems
    game_state_manager = MockGameStateManager()
    map_system = MockMapSystem()
    weather_system = MockWeatherSystem()
    cli_display = MockCliDisplay()
    cli_display.game_state_manager = game_state_manager
    
    # Create and register units
    # Player units
    commander = create_unit(
        "PLAYER_COMMANDER", "Commander", FactionEnum.PLAYER, 
        (1, 4), 25, 25, {"STR": 10, "DEF": 8, "SPD": 9, "SKL": 8, "MOV": 5}
    )
    knight = create_unit(
        "PLAYER_KNIGHT", "Knight", FactionEnum.PLAYER, 
        (2, 5), 30, 30, {"STR": 8, "DEF": 12, "SPD": 6, "SKL": 7, "MOV": 4}
    )
    mage = create_unit(
        "PLAYER_MAGE", "Mage", FactionEnum.PLAYER, 
        (3, 5), 18, 18, {"STR": 12, "DEF": 4, "SPD": 8, "SKL": 10, "MOV": 5}
    )
    
    # Enemy units
    bandit_leader = create_unit(
        "ENEMY_LEADER", "Bandit Leader", FactionEnum.ENEMY, 
        (4, 1), 28, 28, {"STR": 12, "DEF": 7, "SPD": 8, "SKL": 9, "MOV": 5}
    )
    archer = create_unit(
        "ENEMY_ARCHER", "Archer", FactionEnum.ENEMY, 
        (3, 2), 20, 20, {"STR": 9, "DEF": 5, "SPD": 10, "SKL": 12, "MOV": 5}
    )
    
    # NPC unit
    villager = create_unit(
        "NPC_VILLAGER", "Villager", FactionEnum.NPC, 
        (3, 3), 12, 12, {"STR": 5, "DEF": 4, "SPD": 7, "SKL": 6, "MOV": 4}
    )
    
    # Register all units
    for unit in [commander, knight, mage, bandit_leader, archer, villager]:
        game_state_manager.register_unit(unit)
    
    # Initialize the visual logger with HTML export enabled
    visual_logger = VisualScenarioLogger(
        game_state_manager=game_state_manager,
        cli_display=cli_display,
        enabled=True,
        fixed_log_path=log_path,
        use_colors=True,
        html_export=True
    )
    
    print(f"Advanced scenario log will be written to: {log_path}")
    print(f"HTML log will be written to: {log_path.replace('.txt', '.html')}")
    
    # Log initial scenario state
    visual_logger.log_action("SYSTEM", "SCENARIO_START", "Beginning Advanced Tactical Demonstration")
    visual_logger.log_action("SYSTEM", "WEATHER", f"Current Weather: {weather_system.get_current_weather()}")
    visual_logger.log_initial_state()
    
    # Log terrain effects
    visual_logger.log_action("SYSTEM", "TERRAIN_INFO", "--- Terrain Effects ---")
    for pos, terrain in map_system.terrain_data.items():
        effect_text = f"Terrain at {pos}: {terrain.type}, DEF+{terrain.defense_bonus}, EVA+{terrain.evasion_bonus}, Move Cost: {terrain.movement_cost}"
        visual_logger.log_action("SYSTEM", "TERRAIN_EFFECT", effect_text)
    
    # Simulate battle scenario over 3 turns
    for turn in range(1, 4):
        visual_logger.log_turn_start(turn)
        
        # Player Phase
        game_state_manager.current_game_state.current_phase = PhaseEnum.PLAYER
        visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
        
        # Handle weather change at start of turn 2
        if turn == 2:
            weather_system.change_weather("RAIN")
            visual_logger.log_action("SYSTEM", "WEATHER_CHANGE", f"Weather changes to: {weather_system.get_current_weather()}")
            weather_effects = weather_system.get_weather_effects()
            effect_text = ", ".join([f"{key}: {value}" for key, value in weather_effects.items()])
            visual_logger.log_action("SYSTEM", "WEATHER_EFFECT", f"Effects: {effect_text}")
            
            # Apply weather effects to units
            for unit in game_state_manager.get_all_units():
                if hasattr(unit, 'base_stats'):
                    unit.base_stats["MOV"] = max(1, unit.base_stats.get("MOV", 3) + weather_effects.get("movement", 0))
                    visual_logger.log_action(unit.id, "WEATHER_IMPACT", f"{unit.name}'s movement adjusted to {unit.base_stats['MOV']} due to rain")
        
        # Commander moves through different terrain
        if turn == 1:
            start_pos = commander.position
            commander.position = (2, 3)
            terrain = map_system.get_terrain_data_at(commander.position)
            move_cost = terrain.movement_cost
            visual_logger.log_action("PLAYER_COMMANDER", "MOVEMENT", f"Moving from {start_pos} to {commander.position} (Terrain: {terrain.type}, Move Cost: {move_cost})")
            
            # Combat with terrain effects
            target = archer
            terrain_bonus = terrain.defense_bonus
            attack_value = commander.base_stats["STR"]
            defense_value = target.base_stats["DEF"] + terrain_bonus
            damage = max(1, attack_value - defense_value // 2)
            
            visual_logger.log_action("PLAYER_COMMANDER", "COMBAT", f"Attacks {target.name} with terrain DEF bonus of +{terrain_bonus}")
            target.current_hp = max(0, target.current_hp - damage)
            visual_logger.log_action("ENEMY_ARCHER", "DAMAGE", f"Takes {damage} damage (HP: {target.current_hp}/{target.max_hp})")
            
            # Unit details
            visual_logger.log_action("SYSTEM", "UNIT_DETAILS", f"Commander stats: {commander.base_stats}")
            visual_logger.log_action("SYSTEM", "UNIT_DETAILS", f"Archer stats: {target.base_stats}")
        
        # Knight moves and rescues villager in turn 2
        if turn == 2:
            knight = game_state_manager.get_unit("PLAYER_KNIGHT")
            start_pos = knight.position
            end_pos = (3, 4)

            # Create a path for movement animation
            path = [start_pos, end_pos]
                    
            # Log the movement action
            visual_logger.log_action("PLAYER_KNIGHT", "MOVEMENT", f"Moving from {start_pos} to {end_pos}")
            
            # Update position - in a real game, this would be after animation completes
            knight.position = end_pos
            
            # Rescue villager
            visual_logger.log_action("PLAYER_KNIGHT", "RESCUE", f"Rescues {villager.name}")
            knight.rescuing_unit_id = villager.id
            villager.rescued_by_unit_id = knight.id
            villager.position = None  # Remove from map
        
        # Mage attacks with special ability in turn 3
        if turn == 3:
            # Weather changes to fog
            weather_system.change_weather("FOG")
            visual_logger.log_action("SYSTEM", "WEATHER_CHANGE", f"Weather changes to: {weather_system.get_current_weather()}")
            weather_effects = weather_system.get_weather_effects()
            effect_text = ", ".join([f"{key}: {value}" for key, value in weather_effects.items()])
            visual_logger.log_action("SYSTEM", "WEATHER_EFFECT", f"Effects: {effect_text}")
            
            start_pos = mage.position
            mage.position = (3, 4)
            visual_logger.log_action("PLAYER_MAGE", "MOVEMENT", f"Moving from {start_pos} to {mage.position}")
            
            # Cast special spell
            spell_name = "Fireball"
            spell_power = 15
            accuracy_penalty = weather_effects.get("accuracy", 0)
            hit_chance = mage.base_stats["SKL"] * 2 + accuracy_penalty
            
            visual_logger.log_action("PLAYER_MAGE", "SPECIAL_ABILITY", 
                                   f"Casts {spell_name} (Power: {spell_power}, Hit Chance: {hit_chance}%)")
            
            if bandit_leader.current_hp > 0:
                damage = spell_power - bandit_leader.base_stats["DEF"] // 3
                bandit_leader.current_hp = max(0, bandit_leader.current_hp - damage)
                visual_logger.log_action("ENEMY_LEADER", "DAMAGE", 
                                      f"Takes {damage} damage from {spell_name} (HP: {bandit_leader.current_hp}/{bandit_leader.max_hp})")
                
                # Check if defeated
                if bandit_leader.current_hp <= 0:
                    bandit_leader.disposition = DispositionEnum.DEAD
                    visual_logger.log_action("ENEMY_LEADER", "DEATH", f"{bandit_leader.name} has been defeated!")
        
        visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
        
        # Enemy Phase
        game_state_manager.current_game_state.current_phase = PhaseEnum.ENEMY
        visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
        
        # Enemy Leader attacks in turn 1
        if turn == 1 and bandit_leader.disposition == DispositionEnum.ACTIVE:
            start_pos = bandit_leader.position
            bandit_leader.position = (3, 1)
            visual_logger.log_action("ENEMY_LEADER", "MOVEMENT", f"Moving from {start_pos} to {bandit_leader.position}")
            
            # No target in range, end turn
            visual_logger.log_action("ENEMY_LEADER", "ACTION", "No targets in range, ending turn")
        
        # Archer attacks in turn 2 if still alive
        if turn == 2 and archer.disposition == DispositionEnum.ACTIVE and archer.current_hp > 0:
            # Archer attacks commander
            visual_logger.log_action("ENEMY_ARCHER", "COMBAT", f"Archer attacks Commander from distance")
            
            # Calculate hit chance with weather penalty
            accuracy_penalty = weather_system.get_weather_effects().get("accuracy", 0)
            archer_hit_chance = archer.base_stats["SKL"] * 2 + accuracy_penalty
            
            visual_logger.log_action("ENEMY_ARCHER", "COMBAT_DETAIL", 
                                   f"Hit chance: {archer_hit_chance}% (Weather penalty: {accuracy_penalty})")
            
            # Roll for hit
            hit_roll = random.randint(1, 100)
            if hit_roll <= archer_hit_chance:
                damage = max(1, archer.base_stats["STR"] - commander.base_stats["DEF"] // 2)
                commander.current_hp = max(0, commander.current_hp - damage)
                visual_logger.log_action("PLAYER_COMMANDER", "DAMAGE", 
                                      f"Takes {damage} damage (HP: {commander.current_hp}/{commander.max_hp})")
            else:
                visual_logger.log_action("ENEMY_ARCHER", "MISS", f"Attack misses due to weather conditions")
        
        # Special event in turn 3
        if turn == 3:
            visual_logger.log_action("SYSTEM", "SPECIAL_EVENT", "Reinforcements arrive!")
            
            # Create a new enemy unit
            reinforcement = create_unit(
                "ENEMY_CAVALRY", "Cavalry", FactionEnum.ENEMY, 
                (5, 1), 25, 25, {"STR": 11, "DEF": 8, "SPD": 12, "SKL": 8, "MOV": 7}
            )
            
            # Register the new unit
            game_state_manager.register_unit(reinforcement)
            
            visual_logger.log_action("ENEMY_CAVALRY", "SPAWN", f"Enemy Cavalry appears at {reinforcement.position}")
            
            # Apply effects of current weather to new unit
            weather_effects = weather_system.get_weather_effects()
            reinforcement.base_stats["MOV"] = max(1, reinforcement.base_stats["MOV"] + weather_effects.get("movement", 0))
            
            visual_logger.log_action("ENEMY_CAVALRY", "WEATHER_IMPACT", 
                                   f"Movement adjusted to {reinforcement.base_stats['MOV']} due to {weather_system.get_current_weather()}")
        
        visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
        
        # Log end of turn state
        visual_logger.log_end_of_turn_state(turn)
    
    # Log final battle summary
    visual_logger.log_action("SYSTEM", "BATTLE_SUMMARY", "--- Battle Summary ---")
    
    # Count units by faction and status
    faction_counts = {
        "PLAYER": {"active": 0, "defeated": 0},
        "ENEMY": {"active": 0, "defeated": 0},
        "NPC": {"active": 0, "defeated": 0}
    }
    
    for unit in game_state_manager.get_all_units():
        faction = unit.faction.name
        status = "defeated" if unit.disposition == DispositionEnum.DEAD else "active"
        if faction in faction_counts:
            faction_counts[faction][status] += 1
    
    # Log faction counts
    for faction, counts in faction_counts.items():
        visual_logger.log_action("SYSTEM", "FACTION_STATUS", 
                              f"{faction}: {counts['active']} active, {counts['defeated']} defeated")
    
    # Log individual unit status
    visual_logger.log_action("SYSTEM", "UNIT_STATUS", "--- Unit Status ---")
    for unit in game_state_manager.get_all_units():
        if unit.disposition == DispositionEnum.ACTIVE:
            visual_logger.log_action(unit.id, "STATUS", 
                                  f"{unit.name}: HP {unit.current_hp}/{unit.max_hp}, Position {unit.position}")
        else:
            visual_logger.log_action(unit.id, "STATUS", f"{unit.name}: DEFEATED")
    
    # Finalize log
    visual_logger.log_action("SYSTEM", "SCENARIO_END", "Advanced Tactical Demonstration Completed")
    visual_logger.finalize_log()
    
    print("Advanced scenario test completed.")
    print(f"Check {log_path} for the text log.")
    print(f"Check {log_path.replace('.txt', '.html')} for the HTML log.")

if __name__ == "__main__":
    main() 