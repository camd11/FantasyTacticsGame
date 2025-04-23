#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for combat mechanics.
This test covers basic attack, damage calculation, critical hits, weapon advantages, and terrain effects.
"""

import os
import sys
import random
import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, PROJECT_ROOT)

# Define enums
class FactionEnum(Enum):
    PLAYER = 1
    ENEMY = 2
    NPC = 3

class DispositionEnum(Enum):
    ACTIVE = 1
    DEAD = 2
    ESCAPED = 3
    RETREATED = 4

class TerrainType(Enum):
    PLAIN = 1
    FOREST = 2
    MOUNTAIN = 3
    RIVER = 4
    FORT = 5

class WeaponType(Enum):
    SWORD = 1
    LANCE = 2
    AXE = 3
    BOW = 4
    MAGIC = 5

# Define simplified state classes
class ItemState:
    """Simplified item state for testing."""
    def __init__(self):
        self.id = ""
        self.name = ""
        self.type = ""  # WeaponType
        self.might = 0
        self.hit = 0
        self.crit = 0
        self.range = (1, 1)  # (min_range, max_range)
        self.uses = 0
        self.position = None
        self.owner_id = None
        self.weight = 0
        self.effects = {}

class UnitState:
    """Simplified unit state for testing."""
    def __init__(self):
        self.id = ""
        self.name = ""
        self.faction = None
        self.position = (0, 0)
        self.current_hp = 0
        self.max_hp = 0
        self.base_stats = {}
        self.inventory = []
        self.equipped_weapon_index = -1
        self.status_effects = []
        self.disposition = DispositionEnum.ACTIVE
    
    def get_stat(self, stat_name):
        """Get a unit's stat, including effects from items and status effects."""
        return self.base_stats.get(stat_name, 0)
    
    def get_equipped_weapon(self):
        """Get the unit's equipped weapon."""
        if 0 <= self.equipped_weapon_index < len(self.inventory):
            return self.inventory[self.equipped_weapon_index]
        return None

class GameStateManager:
    """Simplified game state manager for testing."""
    def __init__(self):
        self.units = {}
        self.items = {}
        self.map_grid = [[0 for _ in range(10)] for _ in range(10)]
        self.terrain_grid = [[TerrainType.PLAIN for _ in range(10)] for _ in range(10)]
    
    def get_terrain_at(self, position):
        """Get the terrain type at a position."""
        x, y = position
        if 0 <= x < 10 and 0 <= y < 10:
            return self.terrain_grid[y][x]
        return TerrainType.PLAIN
    
    def get_terrain_defense_bonus(self, terrain_type):
        """Get the defense bonus for a terrain type."""
        terrain_bonuses = {
            TerrainType.PLAIN: 0,
            TerrainType.FOREST: 2,
            TerrainType.MOUNTAIN: 3,
            TerrainType.RIVER: 0,
            TerrainType.FORT: 4
        }
        return terrain_bonuses.get(terrain_type, 0)
    
    def get_terrain_avoid_bonus(self, terrain_type):
        """Get the avoid bonus for a terrain type."""
        terrain_bonuses = {
            TerrainType.PLAIN: 0,
            TerrainType.FOREST: 20,
            TerrainType.MOUNTAIN: 30,
            TerrainType.RIVER: 5,
            TerrainType.FORT: 20
        }
        return terrain_bonuses.get(terrain_type, 0)

class CombatSystem:
    """Simplified combat system for testing."""
    def __init__(self):
        self.game_state_manager = None
        self.random = random.Random(42)  # Fixed seed for deterministic tests
    
    def initialize(self, game_state_manager):
        """Initialize the combat system with a game state manager."""
        self.game_state_manager = game_state_manager
    
    def calculate_attack_stats(self, attacker, defender, is_counterattack=False):
        """Calculate stats for an attack."""
        attacker_weapon = attacker.get_equipped_weapon()
        defender_weapon = defender.get_equipped_weapon()
        
        if not attacker_weapon:
            return None
        
        # Calculate base damage
        weapon_might = attacker_weapon.might
        attacker_strength = attacker.get_stat("STR")
        defender_defense = defender.get_stat("DEF")
        
        # Check for weapon triangle advantage
        triangle_bonus = self._get_weapon_triangle_bonus(attacker_weapon, defender_weapon)
        
        # Terrain defense bonus
        terrain_type = self.game_state_manager.get_terrain_at(defender.position)
        terrain_def_bonus = self.game_state_manager.get_terrain_defense_bonus(terrain_type)
        
        # Calculate damage
        damage = max(0, weapon_might + attacker_strength + triangle_bonus - defender_defense - terrain_def_bonus)
        
        # Calculate hit chance
        weapon_hit = attacker_weapon.hit
        attacker_skill = attacker.get_stat("SKL")
        attacker_luck = attacker.get_stat("LCK")
        defender_speed = defender.get_stat("SPD")
        defender_luck = defender.get_stat("LCK")
        
        # Terrain avoid bonus
        terrain_avoid_bonus = self.game_state_manager.get_terrain_avoid_bonus(terrain_type)
        
        hit_chance = min(100, max(0, weapon_hit + attacker_skill*2 + attacker_luck//2 + triangle_bonus*5 - defender_speed*2 - defender_luck//2 - terrain_avoid_bonus))
        
        # Calculate critical hit chance
        crit_chance = max(0, attacker_weapon.crit + attacker_skill//2 + triangle_bonus*5 - defender_luck)
        
        # Calculate attack speed and doubles
        attacker_speed = attacker.get_stat("SPD")
        weapon_weight = attacker_weapon.weight
        attacker_con = attacker.get_stat("CON")
        attack_speed = max(0, attacker_speed - max(0, weapon_weight - attacker_con))
        
        can_double = not is_counterattack and (attack_speed >= defender_speed + 4)
        
        return {
            "damage": damage,
            "hit_chance": hit_chance,
            "crit_chance": crit_chance,
            "can_double": can_double,
            "weapon_triangle_bonus": triangle_bonus
        }
    
    def execute_combat(self, attacker_id, defender_id):
        """Execute combat between two units."""
        attacker = self.game_state_manager.units.get(attacker_id)
        defender = self.game_state_manager.units.get(defender_id)
        
        if not attacker or not defender:
            return {"success": False, "error": "Invalid unit ID"}
        
        attacker_weapon = attacker.get_equipped_weapon()
        defender_weapon = defender.get_equipped_weapon()
        
        if not attacker_weapon:
            return {"success": False, "error": "Attacker has no weapon equipped"}
        
        # Get attack and range info
        attacker_range = attacker_weapon.range
        attack_distance = self._calculate_distance(attacker.position, defender.position)
        
        if not (attacker_range[0] <= attack_distance <= attacker_range[1]):
            return {"success": False, "error": "Target out of range"}
        
        # Calculate initial stats
        attacker_stats = self.calculate_attack_stats(attacker, defender)
        
        if not attacker_stats:
            return {"success": False, "error": "Could not calculate attack stats"}
        
        # Initial log data
        combat_log = {
            "attacker_id": attacker_id,
            "defender_id": defender_id,
            "rounds": [],
            "attacker_initial_hp": attacker.current_hp,
            "defender_initial_hp": defender.current_hp,
            "success": True
        }
        
        # First attack
        first_hit = self._roll_hit(attacker_stats["hit_chance"])
        first_round = {"attacker": attacker_id, "hit": first_hit}
        
        if first_hit:
            critical = self._roll_critical(attacker_stats["crit_chance"])
            damage = attacker_stats["damage"]
            if critical:
                damage *= 3
                first_round["critical"] = True
            
            defender.current_hp = max(0, defender.current_hp - damage)
            first_round["damage"] = damage
            first_round["defender_hp_remaining"] = defender.current_hp
            
            if defender.current_hp == 0:
                defender.disposition = DispositionEnum.DEAD
                first_round["defender_died"] = True
        
        combat_log["rounds"].append(first_round)
        
        # Check for counterattack
        can_counterattack = (defender.current_hp > 0 and 
                            defender_weapon and 
                            defender_weapon.range[0] <= attack_distance <= defender_weapon.range[1])
        
        if can_counterattack:
            defender_stats = self.calculate_attack_stats(defender, attacker, is_counterattack=True)
            
            counter_hit = self._roll_hit(defender_stats["hit_chance"])
            counter_round = {"attacker": defender_id, "hit": counter_hit}
            
            if counter_hit:
                critical = self._roll_critical(defender_stats["crit_chance"])
                damage = defender_stats["damage"]
                if critical:
                    damage *= 3
                    counter_round["critical"] = True
                
                attacker.current_hp = max(0, attacker.current_hp - damage)
                counter_round["damage"] = damage
                counter_round["defender_hp_remaining"] = attacker.current_hp
                
                if attacker.current_hp == 0:
                    attacker.disposition = DispositionEnum.DEAD
                    counter_round["defender_died"] = True
            
            combat_log["rounds"].append(counter_round)
        
        # Check for double attack
        if attacker.current_hp > 0 and defender.current_hp > 0 and attacker_stats["can_double"]:
            double_hit = self._roll_hit(attacker_stats["hit_chance"])
            double_round = {"attacker": attacker_id, "hit": double_hit}
            
            if double_hit:
                critical = self._roll_critical(attacker_stats["crit_chance"])
                damage = attacker_stats["damage"]
                if critical:
                    damage *= 3
                    double_round["critical"] = True
                
                defender.current_hp = max(0, defender.current_hp - damage)
                double_round["damage"] = damage
                double_round["defender_hp_remaining"] = defender.current_hp
                
                if defender.current_hp == 0:
                    defender.disposition = DispositionEnum.DEAD
                    double_round["defender_died"] = True
            
            combat_log["rounds"].append(double_round)
        
        # Record final state
        combat_log["attacker_final_hp"] = attacker.current_hp
        combat_log["defender_final_hp"] = defender.current_hp
        combat_log["attacker_status"] = attacker.disposition.name
        combat_log["defender_status"] = defender.disposition.name
        
        # Use up weapon durability
        attacker_weapon.uses -= 1
        if attacker_weapon.uses <= 0:
            attacker.inventory.remove(attacker_weapon)
            attacker.equipped_weapon_index = -1
        
        if can_counterattack and defender_weapon:
            defender_weapon.uses -= 1
            if defender_weapon.uses <= 0:
                defender.inventory.remove(defender_weapon)
                defender.equipped_weapon_index = -1
        
        return combat_log
    
    def _get_weapon_triangle_bonus(self, attacker_weapon, defender_weapon):
        """Get weapon triangle advantage bonus."""
        if not defender_weapon:
            return 0
            
        # Weapon triangle: Sword > Axe > Lance > Sword
        weapon_triangle = {
            (WeaponType.SWORD, WeaponType.AXE): 1,
            (WeaponType.AXE, WeaponType.LANCE): 1,
            (WeaponType.LANCE, WeaponType.SWORD): 1,
            (WeaponType.AXE, WeaponType.SWORD): -1,
            (WeaponType.LANCE, WeaponType.AXE): -1,
            (WeaponType.SWORD, WeaponType.LANCE): -1,
        }
        
        return weapon_triangle.get((attacker_weapon.type, defender_weapon.type), 0)
    
    def _calculate_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _roll_hit(self, hit_chance):
        """Roll for hit success."""
        roll = self.random.randint(1, 100)
        return roll <= hit_chance
    
    def _roll_critical(self, crit_chance):
        """Roll for critical hit."""
        roll = self.random.randint(1, 100)
        return roll <= crit_chance

class MockGameStateManager(GameStateManager):
    """Mock game state manager for testing combat mechanics."""
    def __init__(self):
        super().__init__()
        self.units = {}
        self.items = {}
        
    def add_unit(self, unit):
        """Add a unit to the game state."""
        self.units[unit.id] = unit
        return unit.id
        
    def get_all_units(self):
        """Return all units in the game state."""
        return list(self.units.values())
    
    def get_unit(self, unit_id):
        """Get a unit by ID."""
        return self.units.get(unit_id)
    
    def add_item(self, item):
        """Add an item to the game state."""
        self.items[item.id] = item
        return item.id
    
    def setup_terrain(self, terrain_grid):
        """Set up terrain for testing."""
        self.terrain_grid = terrain_grid

class VisualScenarioLogger:
    """Simplified logger for tests."""
    def __init__(self, game_state_manager, log_dir=None):
        self.game_state_manager = game_state_manager
        self.log_dir = log_dir
        self.log_file = None
        self.log_buffer = []
    
    def set_log_file(self, log_path):
        """Set the log file path and write any buffered logs."""
        self.log_file = log_path
        # Write any buffered logs
        if self.log_buffer:
            with open(self.log_file, 'w') as f:
                f.write('\n'.join(self.log_buffer))
            self.log_buffer = []
    
    def log(self, message):
        """Log a message."""
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"{message}\n")
        else:
            self.log_buffer.append(message)
    
    def log_initial_state(self, title):
        """Log the initial state of the game."""
        self.log(f"=== {title} ===")
        self.log(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("")
    
    def log_combat(self, combat_log):
        """Log combat results."""
        self.log("\n----- COMBAT LOG -----")
        attacker = self.game_state_manager.get_unit(combat_log["attacker_id"])
        defender = self.game_state_manager.get_unit(combat_log["defender_id"])
        
        self.log(f"Combat: {attacker.name} vs {defender.name}")
        self.log(f"Initial HP: {attacker.name} {combat_log['attacker_initial_hp']}/{attacker.max_hp}, {defender.name} {combat_log['defender_initial_hp']}/{defender.max_hp}")
        
        for i, round_data in enumerate(combat_log["rounds"]):
            round_attacker = self.game_state_manager.get_unit(round_data["attacker"])
            round_defender = attacker if round_attacker.id == defender.id else defender
            
            self.log(f"\nRound {i+1}: {round_attacker.name} attacks")
            if round_data["hit"]:
                crit_text = " (CRITICAL HIT!)" if round_data.get("critical", False) else ""
                self.log(f"  HIT{crit_text} for {round_data['damage']} damage")
                self.log(f"  {round_defender.name} HP: {round_data['defender_hp_remaining']}/{round_defender.max_hp}")
                if round_data.get("defender_died", False):
                    self.log(f"  {round_defender.name} was defeated!")
            else:
                self.log("  MISS!")
        
        self.log(f"\nFinal Result:")
        self.log(f"  {attacker.name}: {combat_log['attacker_final_hp']}/{attacker.max_hp} HP, Status: {combat_log['attacker_status']}")
        self.log(f"  {defender.name}: {combat_log['defender_final_hp']}/{defender.max_hp} HP, Status: {combat_log['defender_status']}")
    
    def close(self):
        """Close the logger."""
        pass

def create_unit(unit_id, name, faction, position, hp=20, max_hp=20, stats=None):
    """Helper function to create a unit for testing."""
    unit = UnitState()
    unit.id = unit_id
    unit.name = name
    unit.faction = faction
    unit.position = position
    unit.current_hp = hp
    unit.max_hp = max_hp
    unit.inventory = []
    unit.disposition = DispositionEnum.ACTIVE
    unit.base_stats = stats or {"STR": 5, "DEF": 3, "SKL": 4, "SPD": 3, "LCK": 2, "CON": 5}
    unit.status_effects = []
    return unit

def create_weapon(weapon_id, name, weapon_type, might=5, hit=80, crit=0, weight=5, uses=30, range=(1, 1)):
    """Helper function to create a weapon for testing."""
    weapon = ItemState()
    weapon.id = weapon_id
    weapon.name = name
    weapon.type = weapon_type
    weapon.might = might
    weapon.hit = hit
    weapon.crit = crit
    weapon.range = range
    weapon.uses = uses
    weapon.weight = weight
    return weapon

def test_combat_mechanics():
    """Test combat mechanics."""
    # Setup game state and systems
    game_state_manager = MockGameStateManager()
    combat_system = CombatSystem()
    combat_system.initialize(game_state_manager)
    
    # Create log directory if it doesn't exist
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../logs/mechanic_tests/combat'))
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a log file
    log_path = os.path.join(log_dir, f"combat_mechanics.txt")
    
    visual_logger = VisualScenarioLogger(game_state_manager, log_dir)
    visual_logger.set_log_file(log_path)
    
    # Log initial state
    visual_logger.log_initial_state("Combat Mechanics Test")
    
    # Test 1: Basic Combat
    visual_logger.log("\n=== TEST 1: BASIC COMBAT ===")
    # Create units
    knight = create_unit("PLAYER_KNIGHT", "Knight", FactionEnum.PLAYER, (3, 3), hp=25, max_hp=25, 
                         stats={"STR": 8, "DEF": 7, "SKL": 6, "SPD": 5, "LCK": 4, "CON": 8})
    
    bandit = create_unit("ENEMY_BANDIT", "Bandit", FactionEnum.ENEMY, (4, 3), hp=22, max_hp=22, 
                        stats={"STR": 7, "DEF": 3, "SKL": 4, "SPD": 6, "LCK": 1, "CON": 6})
    
    # Create and equip weapons
    iron_lance = create_weapon("IRON_LANCE", "Iron Lance", WeaponType.LANCE, might=7, hit=80, crit=0)
    iron_axe = create_weapon("IRON_AXE", "Iron Axe", WeaponType.AXE, might=8, hit=70, crit=0)
    
    knight.inventory.append(iron_lance)
    knight.equipped_weapon_index = 0
    
    bandit.inventory.append(iron_axe)
    bandit.equipped_weapon_index = 0
    
    # Add units to game state
    game_state_manager.add_unit(knight)
    game_state_manager.add_unit(bandit)
    
    # Set up terrain (all plains for basic test)
    terrain_grid = [[TerrainType.PLAIN for _ in range(10)] for _ in range(10)]
    game_state_manager.setup_terrain(terrain_grid)
    
    # Log units
    visual_logger.log("Units:")
    visual_logger.log(f"  Knight: HP {knight.current_hp}/{knight.max_hp}, Pos {knight.position}, Weapon: {knight.get_equipped_weapon().name}")
    visual_logger.log(f"  Bandit: HP {bandit.current_hp}/{bandit.max_hp}, Pos {bandit.position}, Weapon: {bandit.get_equipped_weapon().name}")
    
    # Execute combat
    visual_logger.log("\nKnight attacks Bandit:")
    combat_result = combat_system.execute_combat(knight.id, bandit.id)
    visual_logger.log_combat(combat_result)
    
    # Test 2: Weapon Triangle Advantage
    visual_logger.log("\n=== TEST 2: WEAPON TRIANGLE ADVANTAGE ===")
    
    # Create new units
    swordsman = create_unit("PLAYER_SWORDSMAN", "Swordsman", FactionEnum.PLAYER, (5, 5), hp=20, max_hp=20,
                            stats={"STR": 6, "DEF": 4, "SKL": 8, "SPD": 9, "LCK": 5, "CON": 5})
    
    lancer = create_unit("ENEMY_LANCER", "Lancer", FactionEnum.ENEMY, (6, 5), hp=22, max_hp=22,
                        stats={"STR": 7, "DEF": 5, "SKL": 6, "SPD": 5, "LCK": 3, "CON": 7})
    
    # Create and equip weapons
    iron_sword = create_weapon("IRON_SWORD", "Iron Sword", WeaponType.SWORD, might=6, hit=90, crit=0)
    steel_lance = create_weapon("STEEL_LANCE", "Steel Lance", WeaponType.LANCE, might=8, hit=75, crit=0)
    
    swordsman.inventory.append(iron_sword)
    swordsman.equipped_weapon_index = 0
    
    lancer.inventory.append(steel_lance)
    lancer.equipped_weapon_index = 0
    
    # Add units to game state
    game_state_manager.add_unit(swordsman)
    game_state_manager.add_unit(lancer)
    
    # Log units
    visual_logger.log("Units:")
    visual_logger.log(f"  Swordsman: HP {swordsman.current_hp}/{swordsman.max_hp}, Pos {swordsman.position}, Weapon: {swordsman.get_equipped_weapon().name}")
    visual_logger.log(f"  Lancer: HP {lancer.current_hp}/{lancer.max_hp}, Pos {lancer.position}, Weapon: {lancer.get_equipped_weapon().name}")
    
    # Calculate and log weapon triangle
    attacker_weapon = swordsman.get_equipped_weapon()
    defender_weapon = lancer.get_equipped_weapon()
    triangle_bonus = combat_system._get_weapon_triangle_bonus(attacker_weapon, defender_weapon)
    visual_logger.log(f"Weapon Triangle: {attacker_weapon.name} vs {defender_weapon.name}, Bonus: {triangle_bonus}")
    
    # Execute combat
    visual_logger.log("\nSwordsman attacks Lancer (disadvantage):")
    combat_result = combat_system.execute_combat(swordsman.id, lancer.id)
    visual_logger.log_combat(combat_result)
    
    # Execute combat in reverse to show advantage
    if lancer.current_hp > 0 and swordsman.current_hp > 0:
        visual_logger.log("\nLancer attacks Swordsman (advantage):")
        combat_result = combat_system.execute_combat(lancer.id, swordsman.id)
        visual_logger.log_combat(combat_result)
    
    # Test 3: Terrain Effects
    visual_logger.log("\n=== TEST 3: TERRAIN EFFECTS ===")
    
    # Create new units
    archer = create_unit("PLAYER_ARCHER", "Archer", FactionEnum.PLAYER, (2, 2), hp=18, max_hp=18,
                        stats={"STR": 5, "DEF": 3, "SKL": 7, "SPD": 6, "LCK": 4, "CON": 4})
    
    fighter = create_unit("ENEMY_FIGHTER", "Fighter", FactionEnum.ENEMY, (2, 4), hp=24, max_hp=24,
                         stats={"STR": 8, "DEF": 4, "SKL": 5, "SPD": 4, "LCK": 2, "CON": 7})
    
    # Create and equip weapons
    iron_bow = create_weapon("IRON_BOW", "Iron Bow", WeaponType.BOW, might=6, hit=85, crit=0, range=(2, 2))
    hand_axe = create_weapon("HAND_AXE", "Hand Axe", WeaponType.AXE, might=7, hit=65, crit=0, range=(1, 2))
    
    archer.inventory.append(iron_bow)
    archer.equipped_weapon_index = 0
    
    fighter.inventory.append(hand_axe)
    fighter.equipped_weapon_index = 0
    
    # Add units to game state
    game_state_manager.add_unit(archer)
    game_state_manager.add_unit(fighter)
    
    # Set up terrain (forest for fighter)
    terrain_grid = [[TerrainType.PLAIN for _ in range(10)] for _ in range(10)]
    terrain_grid[4][2] = TerrainType.FOREST  # Fighter's position
    game_state_manager.setup_terrain(terrain_grid)
    
    # Log units and terrain
    visual_logger.log("Units:")
    visual_logger.log(f"  Archer: HP {archer.current_hp}/{archer.max_hp}, Pos {archer.position}, Weapon: {archer.get_equipped_weapon().name}")
    visual_logger.log(f"  Fighter: HP {fighter.current_hp}/{fighter.max_hp}, Pos {fighter.position}, Weapon: {fighter.get_equipped_weapon().name}")
    
    terrain_type = game_state_manager.get_terrain_at(fighter.position)
    defense_bonus = game_state_manager.get_terrain_defense_bonus(terrain_type)
    avoid_bonus = game_state_manager.get_terrain_avoid_bonus(terrain_type)
    visual_logger.log(f"Fighter is on {terrain_type.name} terrain (Defense +{defense_bonus}, Avoid +{avoid_bonus})")
    
    # Execute combat
    visual_logger.log("\nArcher attacks Fighter (on forest terrain):")
    combat_result = combat_system.execute_combat(archer.id, fighter.id)
    visual_logger.log_combat(combat_result)
    
    # Test 4: Critical Hits
    visual_logger.log("\n=== TEST 4: CRITICAL HITS ===")
    
    # Create new units
    myrmidon = create_unit("PLAYER_MYRMIDON", "Myrmidon", FactionEnum.PLAYER, (7, 3), hp=19, max_hp=19,
                          stats={"STR": 6, "DEF": 4, "SKL": 11, "SPD": 10, "LCK": 7, "CON": 5})
    
    soldier = create_unit("ENEMY_SOLDIER", "Soldier", FactionEnum.ENEMY, (7, 4), hp=22, max_hp=22,
                         stats={"STR": 7, "DEF": 6, "SKL": 6, "SPD": 5, "LCK": 4, "CON": 6})
    
    # Create and equip weapons with high crit
    killing_edge = create_weapon("KILLING_EDGE", "Killing Edge", WeaponType.SWORD, might=7, hit=85, crit=30)
    slim_lance = create_weapon("SLIM_LANCE", "Slim Lance", WeaponType.LANCE, might=6, hit=90, crit=5)
    
    myrmidon.inventory.append(killing_edge)
    myrmidon.equipped_weapon_index = 0
    
    soldier.inventory.append(slim_lance)
    soldier.equipped_weapon_index = 0
    
    # Add units to game state
    game_state_manager.add_unit(myrmidon)
    game_state_manager.add_unit(soldier)
    
    # Set up terrain (all plains)
    terrain_grid = [[TerrainType.PLAIN for _ in range(10)] for _ in range(10)]
    game_state_manager.setup_terrain(terrain_grid)
    
    # Log units
    visual_logger.log("Units:")
    visual_logger.log(f"  Myrmidon: HP {myrmidon.current_hp}/{myrmidon.max_hp}, Pos {myrmidon.position}, Weapon: {myrmidon.get_equipped_weapon().name} (Crit: {myrmidon.get_equipped_weapon().crit})")
    visual_logger.log(f"  Soldier: HP {soldier.current_hp}/{soldier.max_hp}, Pos {soldier.position}, Weapon: {soldier.get_equipped_weapon().name} (Crit: {soldier.get_equipped_weapon().crit})")
    
    # Calculate and log crit chances
    myrmidon_stats = combat_system.calculate_attack_stats(myrmidon, soldier)
    visual_logger.log(f"Myrmidon critical chance: {myrmidon_stats['crit_chance']}%")
    
    # Execute combat
    visual_logger.log("\nMyrmidon attacks Soldier (high crit chance):")
    combat_result = combat_system.execute_combat(myrmidon.id, soldier.id)
    visual_logger.log_combat(combat_result)
    
    # Test 5: Doubling Attacks
    visual_logger.log("\n=== TEST 5: DOUBLING ATTACKS ===")
    
    # Create new units
    cavalier = create_unit("PLAYER_CAVALIER", "Cavalier", FactionEnum.PLAYER, (8, 7), hp=24, max_hp=24,
                          stats={"STR": 7, "DEF": 6, "SKL": 7, "SPD": 9, "LCK": 5, "CON": 8})
    
    knight2 = create_unit("ENEMY_KNIGHT", "Armored Knight", FactionEnum.ENEMY, (8, 8), hp=28, max_hp=28,
                         stats={"STR": 8, "DEF": 10, "SKL": 5, "SPD": 3, "LCK": 3, "CON": 11})
    
    # Create and equip weapons
    iron_sword2 = create_weapon("IRON_SWORD2", "Iron Sword", WeaponType.SWORD, might=6, hit=90, crit=0, weight=4)
    iron_lance2 = create_weapon("IRON_LANCE2", "Iron Lance", WeaponType.LANCE, might=7, hit=80, crit=0, weight=6)
    
    cavalier.inventory.append(iron_sword2)
    cavalier.equipped_weapon_index = 0
    
    knight2.inventory.append(iron_lance2)
    knight2.equipped_weapon_index = 0
    
    # Add units to game state
    game_state_manager.add_unit(cavalier)
    game_state_manager.add_unit(knight2)
    
    # Log units
    visual_logger.log("Units:")
    visual_logger.log(f"  Cavalier: HP {cavalier.current_hp}/{cavalier.max_hp}, SPD {cavalier.get_stat('SPD')}, CON {cavalier.get_stat('CON')}")
    visual_logger.log(f"  Armored Knight: HP {knight2.current_hp}/{knight2.max_hp}, SPD {knight2.get_stat('SPD')}, CON {knight2.get_stat('CON')}")
    
    cavalier_weapon = cavalier.get_equipped_weapon()
    knight_weapon = knight2.get_equipped_weapon()
    
    visual_logger.log(f"  Cavalier weapon: {cavalier_weapon.name} (Weight: {cavalier_weapon.weight})")
    visual_logger.log(f"  Knight weapon: {knight_weapon.name} (Weight: {knight_weapon.weight})")
    
    # Calculate attack speed
    cavalier_speed = cavalier.get_stat("SPD")
    cavalier_con = cavalier.get_stat("CON")
    cavalier_as = max(0, cavalier_speed - max(0, cavalier_weapon.weight - cavalier_con))
    
    knight_speed = knight2.get_stat("SPD")
    knight_con = knight2.get_stat("CON")
    knight_as = max(0, knight_speed - max(0, knight_weapon.weight - knight_con))
    
    visual_logger.log(f"  Cavalier AS: {cavalier_as}, Knight AS: {knight_as}")
    
    can_double = cavalier_as >= knight_as + 4
    visual_logger.log(f"  Can Cavalier double? {can_double}")
    
    # Execute combat
    visual_logger.log("\nCavalier attacks Armored Knight (speed advantage):")
    combat_result = combat_system.execute_combat(cavalier.id, knight2.id)
    visual_logger.log_combat(combat_result)
    
    # Final summary
    visual_logger.log("\n=== FINAL STATE ===")
    for unit in game_state_manager.get_all_units():
        visual_logger.log(f"{unit.name} (ID: {unit.id}): HP {unit.current_hp}/{unit.max_hp}, Disposition: {unit.disposition.name}")
    
    visual_logger.log("\nCOMBAT_MECHANICS_TEST_COMPLETE")
    visual_logger.close()

if __name__ == "__main__":
    test_combat_mechanics() 