# src/cli.py (Updated)

import sys
import os
import random
import argparse # NEW: Import argparse
from typing import Optional, Set, Tuple, Dict
import math # Need math for floor/ceil if halving stats

# Ensure the 'src' directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import necessary components
from game.models import (GameState, GameMap, Unit, Weapon, Faction, MoveType,
                         TerrainType, Vulnerary, Item, StatusEffect, # Added StatusEffect
                         FATIGUE_COST_COMBAT, FATIGUE_COST_ITEM, CHARISMA_SKILL_NAME, Potion, # Import fatigue costs, Charisma skill name, Potion
                         TERRAIN_PROPERTIES, WEAPON_TRIANGLE_BONUS, PHYSICAL_TRIANGLE, ANIMA_TRIANGLE, # Triangle, Terrain
                         ANIMA_TYPES, LIGHT_DARK_TYPES, SUPPORTS) # Triangle helpers, Supports
from game.display import render_map
from game.movement import calculate_move_range
from game.combat import simulate_combat, calculate_attack_speed # Import AS calc
from game.ai import run_enemy_ai, run_npc_ai # Import AI functions
from game.ai import run_enemy_ai

# --- Helper Function ---
def get_attack_range(unit: Unit, game_state: GameState) -> Set[Tuple[int, int]]:
    """Calculates the set of tiles the unit can attack."""
    attack_range = set()
    # Cannot attack if capturing, no weapon, or not alive
    if unit.is_capturing is not None or not unit.equipped_weapon or not unit.is_alive:
        return attack_range

    if not unit.equipped_weapon: # Added check
        return attack_range

    min_r = unit.equipped_weapon.range_min
    max_r = unit.equipped_weapon.range_max
    ux, uy = unit.position

    # Iterate through a bounding box around the unit
    for x in range(max(0, ux - max_r), min(game_state.game_map.width, ux + max_r + 1)):
        for y in range(max(0, uy - max_r), min(game_state.game_map.height, uy + max_r + 1)):
            dist = abs(x - ux) + abs(y - uy)
            if min_r <= dist <= max_r:
                attack_range.add((x, y))
    return attack_range


# --- Test Setup Functions ---
def setup_effectiveness_test_state() -> GameState: # RENAMED
    """Creates a simple initial game state for testing fatigue with items."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)

    # Add some terrain features
    game_map.set_tile_terrain(3, 3, TerrainType.FOREST)
    game_map.set_tile_terrain(4, 3, TerrainType.FOREST)
    game_map.set_tile_terrain(5, 3, TerrainType.FOREST)
    game_map.set_tile_terrain(6, 3, TerrainType.MOUNTAIN)
    game_map.set_tile_terrain(6, 4, TerrainType.MOUNTAIN)
    game_map.set_tile_terrain(6, 5, TerrainType.MOUNTAIN)

    game_state = GameState(game_map=game_map)

    # Weapons & Items
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", damage_type="Physical", range_min=1, range_max=1, uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", damage_type="Physical", range_min=1, range_max=1, uses=50, max_uses=50) # Restore might=8
    fire_tome = Weapon(name="Fire Tome", might=6, hit=85, weight=4, wtype="Fire", damage_type="Magical", range_min=1, range_max=2, uses=40, max_uses=40)
    rapier = Weapon(name="Rapier", might=5, hit=95, weight=3, wtype="Sword", damage_type="Physical", range_min=1, range_max=1, uses=40, max_uses=40, effective_against=[MoveType.CAVALRY, MoveType.ARMOR]) # Effective vs Cavalry/Armor
    # Give enough vulneraries for 20 uses (7 items * 3 uses/item = 21 uses)
    leif_inventory = [iron_sword, fire_tome, rapier] + [Vulnerary() for _ in range(4)] # Add Rapier, reduce Vulneraries

    # Add Leif (Player - Lord, Cavalry) - Default setup
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4), # Default start (1,4)
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        leadership_stars=1, # Give Leif 1 leadership star
        movement_stars=20, # NEW: Give Leif 20 stars (100% chance) for testing
        skills=["Adept", "Nihil"], # Added skills for testing
        status_effect=StatusEffect.POISON, # Added for status test
        inventory=leif_inventory,
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Bandit removed for effectiveness test clarity
    # bandit_inventory = [iron_axe]
    # bandit = Unit(
    #     id=101, name="Bandit", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
    #     max_hp=200, hp=200, strength=1, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0, # Added pcc=0, Set HP to max
    #     skills=["Miracle"], # REMOVED Wrath skill
    #     status_effect=StatusEffect.SLEEP, # RE-ADD Sleep for testing status penalties
    #     inventory=[iron_axe] # Give Bandit Iron Axe back
    # )
    # game_state.add_unit(bandit)

    # Add Nanna (Player - Troubadour, Cavalry) for Support/Charisma testing
    nanna_inventory = [Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)] # Give her a basic staff
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(0, 0), # Moved away from Leif
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        leadership_stars=0,
        skills=[CHARISMA_SKILL_NAME], # Give Nanna Charisma
        inventory=nanna_inventory,
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    # Add Enemy Lance Knight (Cavalry) for Effectiveness Test
    enemy_cav = Unit(
        id=102, name="Enemy Knight", cls_name="Lance Knight", faction=Faction.ENEMY, move_type=MoveType.CAVALRY, position=(2, 4), # Moved closer for test
        max_hp=25, hp=25, strength=6, magic=1, skill=4, speed=5, luck=2, defense=5, constitution=9, mov=7, fatigue=0, pcc=0,
        inventory=[Weapon(name="Iron Lance", might=7, hit=80, weight=8, wtype="Lance")],
        growth_rates={'hp': 75, 'strength': 35, 'magic': 5, 'skill': 30, 'speed': 25, 'luck': 15, 'defense': 30, 'constitution': 8, 'mov': 1} # Generic Knight growths
    )
    game_state.add_unit(enemy_cav)

    return game_state

def setup_combat_test_state() -> GameState:
    """Creates the initial game state for the basic combat test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", damage_type="Physical", range_min=1, range_max=1, uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", damage_type="Physical", range_min=1, range_max=1, uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)

    # Leif (Player - Lord, Cavalry)
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        inventory=[iron_sword], # Only Iron Sword
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Nanna (Player - Troubadour, Cavalry) - Needed to end turn
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 3),
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[heal_staff],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    # Bandit (Enemy - Fighter, Infantry) - High HP, Asleep
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=200, hp=200, strength=1, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        status_effect=StatusEffect.SLEEP, # Start asleep
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    return game_state

def setup_fatigue_test_state() -> GameState:
    """Creates the initial game state for the fatigue test (v2)."""
    map_width = 5
    map_height = 5 # Smaller map is fine
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons & Staves
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", damage_type="Physical", range_min=1, range_max=1, uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)
    mend_staff = Weapon(name="Mend Staff", wtype="Staff", staff_rank='C', uses=20, max_uses=20) # Assume Mend is Rank C

    # Player Unit (Fatigue Tester - Fighter, Infantry)
    player_unit = Unit(
        id=1, name="FatigueTester", cls_name="Fighter", faction=Faction.PLAYER, move_type=MoveType.INFANTRY, position=(1, 1),
        max_hp=20, hp=20, strength=10, # Give enough strength to damage enemy
        magic=5, skill=5, speed=5, luck=5, defense=5, constitution=5, mov=5, fatigue=0, pcc=0,
        inventory=[iron_sword, heal_staff, mend_staff],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(player_unit)

    # Enemy Unit (Damage Sponge - Soldier, Infantry)
    enemy_unit = Unit(
        id=101, name="TrainingDummy", cls_name="Soldier", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(2, 1),
        max_hp=500, hp=500, # High HP to survive many hits
        strength=0, magic=0, skill=0, speed=0, luck=0, defense=0, constitution=10, mov=0, fatigue=0, pcc=0,
        inventory=[], # Unarmed
        growth_rates={'hp': 50, 'strength': 20, 'magic': 0, 'skill': 10, 'speed': 10, 'luck': 0, 'defense': 20, 'constitution': 5, 'mov': 0} # Generic Soldier growths
    )
    game_state.add_unit(enemy_unit)

    return game_state

def setup_staff_test_state() -> GameState:
    """Creates the initial game state for the staff test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons & Staves
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", damage_type="Physical", range_min=1, range_max=1, uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", damage_type="Physical", range_min=1, range_max=1, uses=50, max_uses=50)

    # Leif (Player - Lord, Cavalry) - Injured, Poisoned
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=10, # Start injured
        strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        status_effect=StatusEffect.POISON, # Start poisoned as implied by test
        inventory=[iron_sword],
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Nanna (Player - Troubadour, Cavalry) - Healer
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 3),
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[heal_staff], # Has Heal Staff
        # TODO: Need to represent Staff Rank E properly if not implicit
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    # Bandit (Enemy - Fighter, Infantry) - Just exists
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=20, hp=20, strength=1, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    return game_state

def setup_skills_test_state() -> GameState:
    """Creates the initial game state for the skills test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)

    # Leif (Player - Lord, Cavalry) - With Adept and Nihil
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6,
        speed=7, # Speed affects Adept chance (AS = Spd - Wt)
        luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        skills=["Adept", "Nihil"], # Skills to test
        inventory=[iron_sword],
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Bandit (Enemy - Fighter, Infantry) - With Wrath and Miracle, low HP
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=20, hp=10, # Start at low HP for Miracle test
        strength=4, magic=0, skill=2, speed=4,
        luck=5, # Luck affects Miracle chance
        defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        skills=["Wrath", "Miracle"], # Skills to test
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    # Add another player unit (Troubadour, Cavalry) to allow ending the turn if Leif acts
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(0, 0), # Out of the way
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)


    return game_state

def setup_steal_test_state() -> GameState:
    """Creates the initial game state for the steal test."""
    map_width = 5
    map_height = 5 # Small map is sufficient
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Items needed for the test
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50) # Thief needs a weapon
    vulnerary = Vulnerary() # Weight is now defined in the class (models.py)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)
    potion = Potion() # Uses weight=3 from models.py

    # Thief Unit (Player - Thief, Infantry)
    thief = Unit(
        id=1, name="Thief", cls_name="Thief", faction=Faction.PLAYER, move_type=MoveType.INFANTRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=0, skill=5,
        speed=10, # High speed for AS check
        luck=5, defense=2,
        constitution=5, # Low constitution for weight check
        mov=5, fatigue=0, pcc=0,
        can_steal=True, # Must be able to steal
        inventory=[iron_sword], # Start with just a sword
        growth_rates={'hp': 65, 'strength': 25, 'magic': 5, 'skill': 35, 'speed': 55, 'luck': 40, 'defense': 15, 'constitution': 2, 'mov': 1} # Generic Thief growths
    )
    game_state.add_unit(thief)

    # Target Unit (Enemy - Soldier, Infantry)
    target = Unit(
        id=101, name="Target", cls_name="Soldier", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(2, 4), # Adjacent to thief
        max_hp=20, hp=20, strength=5, magic=0, skill=5,
        speed=5, # Lower speed for AS check
        luck=5, defense=5,
        constitution=10, # Higher constitution
        mov=5, fatigue=0, pcc=0,
        inventory=[vulnerary, iron_axe, potion], # Specific inventory for testing steal indices/weights
        growth_rates={'hp': 50, 'strength': 20, 'magic': 0, 'skill': 10, 'speed': 10, 'luck': 0, 'defense': 20, 'constitution': 5, 'mov': 0} # Generic Soldier growths
    )
    game_state.add_unit(target)

    return game_state

def setup_terrain_test_state() -> GameState:
    """Creates the initial game state for the terrain movement test."""
    map_width = 6
    map_height = 7 # Need enough height for cavalry test
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Set specific terrain tiles
    game_map.set_tile_terrain(3, 1, TerrainType.FOREST)
    game_map.set_tile_terrain(4, 1, TerrainType.FOREST)
    game_map.set_tile_terrain(3, 5, TerrainType.MOUNTAIN)
    game_map.set_tile_terrain(4, 5, TerrainType.MOUNTAIN)
    # Add another forest for cavalry test pathing
    game_map.set_tile_terrain(3, 2, TerrainType.FOREST) # Added based on test commands

    # Player Infantry Unit (Fighter)
    infantry = Unit(
        id=1, name="Infantry", cls_name="Fighter", faction=Faction.PLAYER, move_type=MoveType.INFANTRY, position=(1, 1),
        max_hp=20, hp=20, strength=5, magic=0, skill=5, speed=5, luck=5, defense=5, constitution=10,
        mov=5, # As per test assumption
        fatigue=0, pcc=0,
        inventory=[], # No items needed
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(infantry)

    # Player Cavalry Unit (Lance Knight)
    cavalry = Unit(
        id=2, name="Cavalry", cls_name="Lance Knight", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 5),
        max_hp=25, hp=25, strength=7, magic=1, skill=6, speed=8, luck=6, defense=6, constitution=9,
        mov=7, # As per test assumption
        fatigue=0, pcc=0,
        inventory=[], # No items needed
        growth_rates={'hp': 75, 'strength': 35, 'magic': 5, 'skill': 30, 'speed': 25, 'luck': 15, 'defense': 30, 'constitution': 8, 'mov': 1} # Generic Knight growths
    )
    game_state.add_unit(cavalry)

    return game_state

def setup_status_test_state() -> GameState:
    """Creates the initial game state for the status effect test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)

    # Leif (Player - Lord, Cavalry) - Poisoned
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, # Start at full HP
        strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        status_effect=StatusEffect.POISON, # Start poisoned
        inventory=[iron_sword],
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Bandit (Enemy - Fighter, Infantry) - Sleeping
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=20, hp=20, # Start at full HP
        strength=4, magic=0, skill=2, speed=4, luck=0,
        defense=2, # Base defense for damage calculation check
        constitution=10, mov=4, fatigue=0, pcc=0,
        status_effect=StatusEffect.SLEEP, # Start asleep
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    # Add another player unit (Troubadour, Cavalry) to allow ending the turn
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(0, 0), # Out of the way
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    return game_state

def setup_movestars_test_state() -> GameState:
    """Creates the initial game state for the movement stars test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)

    # Leif (Player - Lord, Cavalry) - With 20 Movement Stars
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        movement_stars=20, # Guarantee activation
        inventory=[iron_sword],
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Bandit (Enemy - Fighter, Infantry) - Target for attack
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=20, hp=20, strength=4, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    # Add another player unit (Troubadour, Cavalry) to allow ending the turn
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(0, 0), # Out of the way
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    return game_state

def setup_triangle_test_state() -> GameState:
    """Creates the initial game state for the weapon triangle test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)

    # Leif (Player - Lord, Cavalry) - With Iron Sword
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        inventory=[iron_sword], # Ensure Iron Sword is equipped
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Nanna (Player - Troubadour, Cavalry) - To end turn
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 3),
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[heal_staff],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    # Bandit (Enemy - Fighter, Infantry) - With Iron Axe, Asleep
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=200, hp=200, strength=1, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        status_effect=StatusEffect.SLEEP, # Start asleep
        inventory=[iron_axe], # Ensure Iron Axe is equipped
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    return game_state

def setup_skills_test_state() -> GameState:
    """Creates the initial game state for the skills test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)

    # Leif (Player - Lord, Cavalry) - With Adept and Nihil
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6,
        speed=7, # Speed affects Adept chance (AS = Spd - Wt)
        luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        skills=["Adept", "Nihil"], # Skills to test
        inventory=[iron_sword],
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Bandit (Enemy - Fighter, Infantry) - With Wrath and Miracle, low HP
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=20, hp=10, # Start at low HP for Miracle test
        strength=4, magic=0, skill=2, speed=4,
        luck=5, # Luck affects Miracle chance
        defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        skills=["Wrath", "Miracle"], # Skills to test
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    # Add another player unit (Troubadour, Cavalry) to allow ending the turn if Leif acts
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(0, 0), # Out of the way
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)


    return game_state

def setup_item_test_state() -> GameState:
    """Creates the initial game state for the item/inventory test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons & Items
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    fire_tome = Weapon(name="Fire Tome", might=6, hit=85, weight=4, wtype="Fire", damage_type="Magical", range_min=1, range_max=2, uses=40, max_uses=40)
    # Inventory: Sword, Tome, 5x Vulnerary (Indices 0, 1, 2, 3, 4, 5, 6)
    leif_inventory = [iron_sword, fire_tome] + [Vulnerary() for _ in range(5)]

    # Leif (Player - Lord, Cavalry) - Damaged
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=1, # Start heavily damaged
        strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        inventory=leif_inventory,
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Add a dummy enemy (Soldier, Infantry) just so the map isn't empty
    enemy = Unit(
        id=101, name="Dummy", cls_name="Soldier", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=10, hp=10, strength=0, magic=0, skill=0, speed=0, luck=0, defense=0, constitution=10, mov=0, fatigue=0, pcc=0,
        inventory=[],
        growth_rates={'hp': 50, 'strength': 20, 'magic': 0, 'skill': 10, 'speed': 10, 'luck': 0, 'defense': 20, 'constitution': 5, 'mov': 0} # Generic Soldier growths
    )
    game_state.add_unit(enemy)

    return game_state

def setup_ai_test_state() -> GameState:
    """Creates the initial game state for the AI test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)

    # Leif (Player - Lord, Cavalry)
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        inventory=[iron_sword],
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Bandit (Enemy - Fighter, Infantry) - Standard, not asleep
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=20, hp=20, strength=4, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    return game_state

def setup_bonus_test_state() -> GameState:
    """Creates the initial game state for the bonus test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30) # Give Nanna something

    # Leif (Player - Lord, Cavalry) - With Leadership Star
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        leadership_stars=1, # Ensure Leif has 1 LS
        inventory=[iron_sword],
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Nanna (Player - Troubadour, Cavalry) - With Charisma
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 3), # Start near Leif
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        skills=[CHARISMA_SKILL_NAME], # Ensure Nanna has Charisma
        inventory=[heal_staff],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    # Bandit (Enemy - Fighter, Infantry)
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=20, hp=20, strength=4, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    return game_state

def setup_magic_crit_test_state() -> GameState:
    """Creates the initial game state for the magic crit/combat flow test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, crit=0, weight=5, wtype="Sword", uses=50, max_uses=50)
    fire_tome = Weapon(name="Fire Tome", might=6, hit=85, crit=0, weight=4, wtype="Fire", damage_type="Magical", range_min=1, range_max=2, uses=40, max_uses=40)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)

    # Leif (Player - Lord, Cavalry) - With Sword, Tome, and Movement Stars
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20,
        strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        movement_stars=20, # Guarantee activation for test flow
        inventory=[iron_sword, fire_tome], # Has both weapons
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif) # Leif will auto-equip Iron Sword (index 0)

    # Nanna (Player - Troubadour, Cavalry) - To end turn
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 3),
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[heal_staff],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    # Bandit (Enemy - Fighter, Infantry) - Asleep
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=200, hp=200, strength=1,
        magic=0, # Target for magic damage
        skill=2, speed=4, luck=0,
        defense=2, # Target for physical damage
        constitution=10, mov=4, fatigue=0, pcc=0,
        status_effect=StatusEffect.SLEEP, # Start asleep
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    return game_state

def setup_capture_test_state() -> GameState:
    """Creates the initial game state for the capture test (Case 1 & 7)."""
    map_width = 6
    map_height = 4 # Smaller map
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_lance = Weapon(name="Iron Lance", might=7, hit=80, weight=8, wtype="Lance", uses=50, max_uses=50)

    # Player Units (Fighter, Lance Knight)
    player1 = Unit(
        id=1, name="PlayerInf", cls_name="Fighter", faction=Faction.PLAYER, move_type=MoveType.INFANTRY, position=(1, 1),
        max_hp=20, hp=20, strength=10, skill=5, speed=5, luck=5, defense=5, constitution=10, mov=5, fatigue=0, pcc=0,
        inventory=[iron_sword],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(player1)

    player2 = Unit( # Needed for later tests, include for completeness
        id=2, name="PlayerCav", cls_name="Lance Knight", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 2),
        max_hp=20, hp=20, strength=10, skill=5, speed=8, luck=5, defense=5, constitution=8, mov=7, fatigue=0, pcc=0,
        inventory=[iron_lance],
        growth_rates={'hp': 75, 'strength': 35, 'magic': 5, 'skill': 30, 'speed': 25, 'luck': 15, 'defense': 30, 'constitution': 8, 'mov': 1} # Generic Knight growths
    )
    game_state.add_unit(player2)

    # Enemy Units (Soldier, Soldier, Soldier, Lance Knight)
    enemy1 = Unit( # Target for successful capture
        id=101, name="EnemyLowCon", cls_name="Soldier", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(2, 1),
        max_hp=1, hp=1, strength=1, skill=1, speed=1, luck=1, defense=1, constitution=5, mov=4, fatigue=0, pcc=0,
        inventory=[iron_sword],
        growth_rates={'hp': 50, 'strength': 20, 'magic': 0, 'skill': 10, 'speed': 10, 'luck': 0, 'defense': 20, 'constitution': 5, 'mov': 0} # Generic Soldier growths
    )
    game_state.add_unit(enemy1)

    enemy2 = Unit( # Target for failed capture (Con too high)
        id=102, name="EnemyHighCon", cls_name="Soldier", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(3, 1),
        max_hp=1, hp=1, strength=1, skill=1, speed=1, luck=1, defense=1, constitution=15, mov=4, fatigue=0, pcc=0,
        inventory=[iron_sword],
        growth_rates={'hp': 50, 'strength': 20, 'magic': 0, 'skill': 10, 'speed': 10, 'luck': 0, 'defense': 20, 'constitution': 5, 'mov': 0} # Generic Soldier growths
    )
    game_state.add_unit(enemy2)

    enemy3 = Unit( # Target for failed capture (Immune Con)
        id=103, name="EnemyImmuneCon", cls_name="Soldier", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(4, 1),
        max_hp=1, hp=1, strength=1, skill=1, speed=1, luck=1, defense=1, constitution=20, mov=4, fatigue=0, pcc=0,
        inventory=[iron_sword],
        growth_rates={'hp': 50, 'strength': 20, 'magic': 0, 'skill': 10, 'speed': 10, 'luck': 0, 'defense': 20, 'constitution': 5, 'mov': 0} # Generic Soldier growths
    )
    game_state.add_unit(enemy3)

    enemy4 = Unit( # Target for failed capture (Mounted)
        id=104, name="EnemyCavTarget", cls_name="Lance Knight", faction=Faction.ENEMY, move_type=MoveType.CAVALRY, position=(2, 2),
        max_hp=1, hp=1, strength=1, skill=1, speed=1, luck=1, defense=1, constitution=5, mov=7, fatigue=0, pcc=0,
        inventory=[iron_lance],
        growth_rates={'hp': 75, 'strength': 35, 'magic': 5, 'skill': 30, 'speed': 25, 'luck': 15, 'defense': 30, 'constitution': 8, 'mov': 1} # Generic Knight growths
    )
    game_state.add_unit(enemy4)

    return game_state

def setup_crit_test_state() -> GameState:
    """Creates the initial game state for the critical hit test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, crit=0, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)

    # Leif (Player - Lord, Cavalry) - Ensure PCC=1
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1, # Set PCC=1
        inventory=[iron_sword]
    )
    game_state.add_unit(leif)

    # Nanna (Player - Troubadour, Cavalry) - To end turn
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 3),
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[heal_staff],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    # Bandit (Enemy - Fighter, Infantry) - Asleep, Luk 0
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=200, hp=200, strength=1, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        status_effect=StatusEffect.SLEEP, # Start asleep,
        inventory=[iron_axe], # Need to re-add inventory line that was missing in read_file result
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    ) # Add closing parenthesis here and remove duplicate inventory line
    game_state.add_unit(bandit)

    return game_state

def setup_magic_attack_test_state() -> GameState:
    """Creates the initial game state for the magic attack test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    fire_tome = Weapon(name="Fire Tome", might=6, hit=85, crit=0, weight=4, wtype="Fire", damage_type="Magical", range_min=1, range_max=2, uses=40, max_uses=40)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)

    # Leif (Player - Lord, Cavalry) - With Fire Tome and guaranteed Movement Stars for this test
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        movement_stars=20, # Add stars to guarantee second action for test
        inventory=[iron_sword, fire_tome], # Add Fire Tome
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Nanna (Player - Troubadour, Cavalry) - To end turn
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 3),
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[heal_staff],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    # Bandit (Enemy - Fighter, Infantry) - Asleep, Mag 0
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=200, hp=200, strength=1, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        status_effect=StatusEffect.SLEEP, # Start asleep
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    return game_state

def setup_mvp_test_state() -> GameState:
    """Creates the initial game state for the MVP commands test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", damage_type="Physical", range_min=1, range_max=1, uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", damage_type="Physical", range_min=1, range_max=1, uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)

    # Leif (Player - Lord, Cavalry)
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        inventory=[iron_sword],
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Leif growths
    )
    game_state.add_unit(leif)

    # Nanna (Player - Troubadour, Cavalry)
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 3),
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[heal_staff],
        growth_rates={'hp': 60, 'strength': 20, 'magic': 35, 'skill': 45, 'speed': 50, 'luck': 60, 'defense': 15, 'constitution': 3, 'mov': 2} # Nanna growths
    )
    game_state.add_unit(nanna)

    # Bandit (Enemy - Fighter, Infantry) - Asleep
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=20, hp=20, strength=1, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        status_effect=StatusEffect.SLEEP, # Start asleep
        inventory=[iron_axe],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(bandit)

    return game_state

def setup_canto_test_state() -> GameState:
    """Creates the initial game state for the Canto test."""
    map_width = 10
    map_height = 8
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Weapons & Items
    iron_sword = Weapon(name="Iron Sword", might=5, hit=90, weight=5, wtype="Sword", uses=50, max_uses=50)
    iron_axe = Weapon(name="Iron Axe", might=8, hit=75, weight=10, wtype="Axe", uses=50, max_uses=50)
    heal_staff = Weapon(name="Heal Staff", wtype="Staff", staff_rank='E', uses=30, max_uses=30)
    vulnerary = Vulnerary()

    # Leif (Player - Lord, Cavalry), with Vulnerary
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 4),
        max_hp=20, hp=20, strength=5, magic=5, skill=6, speed=7, luck=6, defense=3, constitution=5, mov=7, fatigue=0, pcc=1,
        inventory=[iron_sword, vulnerary] # Need sword for attack test, vulnerary for use test
    )
    game_state.add_unit(leif)

    # Nanna (Player - Troubadour, Cavalry) - To end turn
    nanna = Unit(
        id=2, name="Nanna", cls_name="Troubadour", faction=Faction.PLAYER, move_type=MoveType.CAVALRY, position=(1, 3),
        max_hp=18, hp=18, strength=3, magic=6, skill=5, speed=8, luck=8, defense=2, constitution=4, mov=7, fatigue=0, pcc=2,
        inventory=[heal_staff]
    )
    game_state.add_unit(nanna)

    # Bandit (Enemy - Fighter, Infantry) - Target
    bandit = Unit(
        id=101, name="Bandit", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY, position=(5, 4),
        max_hp=20, hp=20, strength=4, magic=0, skill=2, speed=4, luck=0, defense=2, constitution=10, mov=4, fatigue=0, pcc=0,
        inventory=[iron_axe], # Need to re-add inventory
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    ) # Add closing parenthesis and remove duplicate inventory line
    game_state.add_unit(bandit)

    return game_state

def setup_staff_wexp_test_state() -> GameState:
    """Creates the initial game state for the staff WExp test."""
    map_width = 5
    map_height = 5
    game_map = GameMap(width=map_width, height=map_height)
    game_state = GameState(game_map=game_map)

    # Staves of different ranks
    heal_staff_e = Weapon(name="Heal Staff (E)", wtype="Staff", staff_rank='E', uses=50, max_uses=50) # Enough uses for rank up
    mend_staff_c = Weapon(name="Mend Staff (C)", wtype="Staff", staff_rank='C', uses=50, max_uses=50) # Enough uses for rank up
    physic_staff_b = Weapon(name="Physic Staff (B)", wtype="Staff", staff_rank='B', uses=50, max_uses=50) # For testing B rank gain

    # Player Unit (Healer) - Start with E rank Staff
    healer = Unit(
        id=1, name="Healer", cls_name="Priest", faction=Faction.PLAYER, move_type=MoveType.INFANTRY, position=(1, 1),
        max_hp=20, hp=10, # Start injured to test self-heal if needed
        strength=0, magic=10, skill=5, speed=5, luck=5, defense=2, constitution=4, mov=5, fatigue=0, pcc=0,
        inventory=[heal_staff_e, mend_staff_c, physic_staff_b], # Has all staves
        wexp={'Staff': 0}, # Start with 0 Staff WExp
        weapon_ranks={'Staff': 'E'}, # Start with E rank Staff
        growth_rates={'hp': 50, 'strength': 0, 'magic': 40, 'skill': 30, 'speed': 25, 'luck': 60, 'defense': 10, 'constitution': 1, 'mov': 1} # Generic Priest growths
    )
    game_state.add_unit(healer)
    healer.equipped_weapon_index = 0 # Equip Heal Staff (E)

    # Target Unit (Ally) - Needs healing
    target = Unit(
        id=2, name="Target", cls_name="Fighter", faction=Faction.PLAYER, move_type=MoveType.INFANTRY, position=(1, 2), # Adjacent
        max_hp=30, hp=1, # Start heavily injured
        strength=10, magic=0, skill=5, speed=5, luck=5, defense=5, constitution=10, mov=5, fatigue=0, pcc=0,
        inventory=[],
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Generic Fighter growths
    )
    game_state.add_unit(target)

    return game_state

def setup_mvp_phase1_state() -> GameState:
    """Creates a simple game state aligned with DESIGN_MVP_PHASE1.md goals."""
    map_width = 8
    map_height = 6
    game_map = GameMap(width=map_width, height=map_height) # All Plain tiles by default
    game_state = GameState(game_map=game_map)

    # Basic Player Unit (Leif) - Assuming Lord class for MVP
    leif = Unit(
        id=1, name="Leif", cls_name="Lord", faction=Faction.PLAYER, move_type=MoveType.INFANTRY, # Simple infantry for MVP
        position=(1, 1),
        max_hp=20, hp=20,
        mov=5, # Basic movement
        # MVP doesn't require other stats, skills, items yet
        inventory=[], # Start unarmed for simplicity or add basic sword
        growth_rates={'hp': 80, 'strength': 30, 'magic': 10, 'skill': 40, 'speed': 40, 'luck': 50, 'defense': 20, 'constitution': 5, 'mov': 2} # Example Leif-like growths
    )
    game_state.add_unit(leif)

    # Basic Enemy Unit (Stationary) - Assuming Fighter class for MVP
    enemy = Unit(
        id=101, name="Enemy", cls_name="Fighter", faction=Faction.ENEMY, move_type=MoveType.INFANTRY,
        position=(5, 3),
        max_hp=15, hp=15,
        mov=4,
        inventory=[], # Unarmed
        growth_rates={'hp': 70, 'strength': 40, 'magic': 5, 'skill': 30, 'speed': 20, 'luck': 10, 'defense': 30, 'constitution': 10, 'mov': 1} # Example Fighter growths
    )
    game_state.add_unit(enemy)

    return game_state

# --- Turn Start Effects ---
# --- Turn Start Effects ---
def apply_turn_start_effects(game_state: GameState):
    """Applies effects like poison damage at the start of a phase."""
    active_faction = game_state.active_faction
    print(f"Applying turn start effects for {active_faction}...")
    for unit in list(game_state.units.values()): # Iterate over copy
        if unit.faction == active_faction and unit.is_alive and not unit.is_captured:
            # Poison Damage
            if unit.status_effect == StatusEffect.POISON:
                poison_damage = 1 # Simplified poison damage
                print(f"  {unit.name} takes {poison_damage} damage from Poison.")
                unit.hp = max(0, unit.hp - poison_damage)
                print(f"  (HP: {unit.hp}/{unit.max_hp})")
                if unit.hp == 0:
                    game_state.handle_unit_death(unit)
                    print(f"  {unit.name} succumbed to poison!")
            # Add other start-of-turn effects here (e.g., healing terrain)

# --- Action Completion & Movement Star Check ---
def complete_action(unit: Unit, game_state: GameState) -> bool:
    """
    Handles post-action logic: fatigue, has_acted flag, and Movement Star check.
    Returns True if the unit gets another action due to Movement Stars, False otherwise.
    """
    # Fatigue is handled within specific actions (combat, use, steal, staff)

    # Movement Star Check (Thracia: 5% per star)
    if unit.movement_stars > 0:
        chance = unit.movement_stars * 5
        roll = random.randint(1, 100)
        print(f"  (Movement Star Check: Roll {roll} vs Chance {chance})") # Debug
        if roll <= chance:
            print(f"  Movement Star activated! {unit.name} can act again.")
            # Reset has_acted flag if it was set by the action
            unit.has_acted = False
            # Deselect unit so player must re-select to act again
            game_state.selected_unit_id = None
            return True # Unit gets another action
        elif setup_name == "crit": # ADDED
            game_state = setup_crit_test_state() # ADDED
        else:
            print(f"  (Movement Star did not activate)")

    # If no movement star activation, mark as acted
    unit.has_acted = True
    game_state.selected_unit_id = None # Deselect after action
    return False # Unit's turn ends

# --- Main CLI Loop (Updated) ---
def run_cli(setup_name: str = "effectiveness"): # MODIFIED: Accept setup name
    """Runs the main command-line interface loop."""
    random.seed(42) # Seed RNG for deterministic tests

    # Select the setup function based on the name
    if setup_name == "effectiveness":
        game_state = setup_effectiveness_test_state()
    # Add other setup functions here later
    elif setup_name == "combat":
        game_state = setup_combat_test_state()
    elif setup_name == "fatigue": # ADDED
        game_state = setup_fatigue_test_state() # ADDED
    elif setup_name == "staff":
        game_state = setup_staff_test_state()
    elif setup_name == "item":
        game_state = setup_item_test_state()
    elif setup_name == "ai": # ADDED
        game_state = setup_ai_test_state() # ADDED
    elif setup_name == "bonus":
        game_state = setup_bonus_test_state()
    elif setup_name == "canto":
        game_state = setup_canto_test_state()
    elif setup_name == "capture": # ADDED
        game_state = setup_capture_test_state() # ADDED
    elif setup_name == "crit":
        game_state = setup_crit_test_state()
    elif setup_name == "magic_attack":
        game_state = setup_magic_attack_test_state()
    elif setup_name == "magic_crit": # ADDED
        game_state = setup_magic_crit_test_state() # ADDED
    elif setup_name == "mvp": # ADDED
        game_state = setup_mvp_test_state() # ADDED
    elif setup_name == "steal": # ADDED
        game_state = setup_steal_test_state() # ADDED
    elif setup_name == "skills": # ADDED
        game_state = setup_skills_test_state() # ADDED
    elif setup_name == "status": # ADDED
        game_state = setup_status_test_state() # ADDED
    elif setup_name == "movestars": # ADDED
        game_state = setup_movestars_test_state() # ADDED
    elif setup_name == "triangle": # ADDED
        game_state = setup_triangle_test_state() # ADDED
    elif setup_name == "terrain": # ADDED
        game_state = setup_terrain_test_state() # ADDED
    else:
        print(f"Error: Unknown setup name '{setup_name}'. Defaulting to effectiveness.")
        game_state = setup_mvp_phase1_state() # Default to new MVP setup
    # Store move range as {pos: cost}
    current_move_range: Optional[Dict[Tuple[int, int], int]] = None
    current_attack_range: Optional[Set[Tuple[int, int]]] = None
    # Store remaining move points after a move for Canto calculation
    canto_move_points: Optional[int] = None
    is_canto_active: bool = False # Flag if currently in Canto state
    current_canto_range: Optional[Dict[Tuple[int, int], int]] = None # Store calculated canto range

    while True:
        # Pass canto range to render_map if active
        render_map(game_state, current_move_range if not is_canto_active else None, current_canto_range if is_canto_active else None)
        # Update prompt
        prompt = "Cmds: select|move|attack|capture|equip|inventory|use|promote|trade|release|wait|info|endturn|quit: " # Added promote
        command_str = input(prompt).strip() # Don't lowercase yet

        # Ignore empty lines and comments
        if not command_str or command_str.startswith("#"):
            continue

        # Remove trailing comments before splitting
        command_str = command_str.split('#', 1)[0].strip()
        # Re-check if the line became empty after removing the comment
        if not command_str:
            continue

        parts = command_str.lower().split() # Lowercase after comment check
        # Check if parts is empty after splitting (e.g., if input was just whitespace)
        if not parts:
            continue
        command = parts[0]
        args = parts[1:] # Arguments are now a list

        try:
            if command == "quit":
                print("Exiting game.")
                sys.exit(0)

            # --- Player Turn Commands ---
            if game_state.active_faction == Faction.PLAYER:
                if command == "select":
                    if len(args) != 2:
                        print("Usage: select <x> <y>")
                        continue
                    x, y = int(args[0]), int(args[1])
                    unit_id = game_state.game_map.get_unit_id_at(x, y)
                    if unit_id is not None:
                        unit = game_state.get_unit(unit_id)
                        # Check fatigue status first
                        is_fatigued = unit and unit.fatigue >= unit.max_hp
                        if is_fatigued and unit.faction == Faction.PLAYER:
                             print(f"{unit.name} is fatigued ({unit.fatigue}/{unit.max_hp}) and cannot act this chapter.")
                             game_state.selected_unit_id = None
                             current_move_range = None
                             current_attack_range = None
                        elif unit and unit.is_captured:
                            print(f"{unit.name} is captured and cannot be selected.")
                            game_state.selected_unit_id = None
                            current_move_range = None
                            current_attack_range = None
                        elif unit and unit.faction == Faction.PLAYER and unit.is_alive:
                            game_state.selected_unit_id = unit_id
                            if not unit.has_acted:
                                # Calculate and store move range with costs
                                current_move_range = calculate_move_range(game_state, unit)
                                current_attack_range = get_attack_range(unit, game_state)
                                canto_move_points = None # Reset canto potential
                                is_canto_active = False
                                current_canto_range = None
                            else:
                                current_move_range = None
                                current_attack_range = None
                            inventory_names = [(f"{item.name}" + (f" ({item.uses}/{item.max_uses})" if item.uses is not None else "")) for item in unit.inventory]
                            capture_status = f" | Capturing: {game_state.units.get(unit.is_capturing).name}" if unit.is_capturing is not None else ""
                            acted_status = " [Acted]" if unit.has_acted else ""
                            canto_status = " [Canto]" if is_canto_active else ""
                            fatigue_status = f" | Fatigue: {unit.fatigue}/{unit.max_hp}"
                            move_display = "Move(+)" if is_canto_active else "Move(*)"
                            print(f"Selected {unit.name}{acted_status}{canto_status}. {move_display}. Items: {inventory_names or ['None']}{capture_status}{fatigue_status}")
                        elif unit and unit.faction != Faction.PLAYER:
                            print("Cannot select non-player units.")
                            game_state.selected_unit_id = None
                            current_move_range = None
                            current_attack_range = None
                        elif unit and not unit.is_alive:
                             print(f"{unit.name} is defeated.")
                             game_state.selected_unit_id = None
                             current_move_range = None
                             current_attack_range = None
                        else:
                             game_state.selected_unit_id = None
                             current_move_range = None
                             current_attack_range = None
                    else:
                        print(f"No unit at ({x}, {y}).")
                        game_state.selected_unit_id = None
                        current_move_range = None
                        current_attack_range = None

                elif command == "move":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    if selected_unit.fatigue >= selected_unit.max_hp:
                         print(f"{selected_unit.name} is fatigued and cannot act.")
                         continue
                    if selected_unit.has_acted:
                        print(f"{selected_unit.name} has already acted.")
                        continue
                    if selected_unit.is_capturing is not None:
                        print(f"{selected_unit.name} cannot move while capturing (MVP limitation).")
                        continue
                    if len(args) != 2:
                        print("Usage: move <x> <y>")
                        continue

                    x, y = int(args[0]), int(args[1])
                    target_pos = (x, y)

                    # Determine which range to check (Canto or Normal)
                    active_range = current_canto_range if is_canto_active else current_move_range

                    if active_range is None:
                         print(f"Cannot move {selected_unit.name} (already acted or no range calculated).")
                         continue

                    # Check if target_pos is in the active range
                    if target_pos in active_range:
                        move_cost = active_range[target_pos]
                        if game_state.game_map.move_unit(selected_unit, x, y):
                            print(f"Moved {selected_unit.name} to ({x}, {y}) (Cost: {move_cost}).")

                            # --- Canto Logic ---
                            is_mounted = selected_unit.move_type in [MoveType.CAVALRY, MoveType.FLYING]
                            # Calculate remaining move based on original move allowance before capture penalty
                            # If it was a Canto move, use the stored canto_move_points
                            original_mov = canto_move_points if is_canto_active else selected_unit.mov
                            base_remaining_move = original_mov - move_cost

                            # Apply capture penalty *after* calculating base remaining
                            canto_mov = base_remaining_move
                            if selected_unit.is_capturing is not None:
                                canto_mov = math.floor(base_remaining_move / 2)

                            # If this was the *initial* move (not a Canto move)
                            if not is_canto_active:
                                if is_mounted and canto_mov > 0:
                                    print(f"  {selected_unit.name} has {canto_mov} movement remaining (Canto).")
                                    # Calculate and store Canto range
                                    current_canto_range = calculate_move_range(game_state, selected_unit, override_max_move=canto_mov)
                                    current_move_range = None # Clear normal move range
                                    current_attack_range = get_attack_range(selected_unit, game_state)
                                    canto_move_points = canto_mov # Store remaining points
                                    is_canto_active = True # Set Canto flag
                                    # Keep unit selected, don't set has_acted yet
                                    print(f"  (Select Canto move (+), action, or wait)")
                                else:
                                    # Not mounted or no move left after initial move, end action
                                    canto_move_points = None
                                    is_canto_active = False
                                    current_canto_range = None
                                    if not complete_action(selected_unit, game_state):
                                        # Action ended normally, clear ranges
                                        current_move_range = None
                                        current_attack_range = None
                                    else: # Movement star activated
                                        # Don't clear ranges, they will be recalculated on re-select
                                        pass
                            else:
                                # This was a Canto move, always end the turn now
                                print(f"  (Canto move completed)")
                                canto_move_points = None
                                is_canto_active = False
                                current_canto_range = None
                                if not complete_action(selected_unit, game_state):
                                    # Action ended normally, clear ranges
                                    current_move_range = None
                                    current_attack_range = None
                                else: # Movement star activated
                                    # Don't clear ranges, they will be recalculated on re-select
                                    pass
                            # -----------------

                        else:
                            print(f"Cannot move to ({x}, {y}) - tile might be occupied or invalid.")
                            # Do not end action here, allow player to try again
                    else: # Target not in active_range
                        print(f"Cannot move to ({x}, {y}) - not in range.")
                        # Do not end action here, allow player to try again

                elif command == "attack":
                    attacker = game_state.get_selected_unit()
                    if not attacker:
                        print("No unit selected.")
                        continue
                    if attacker.fatigue >= attacker.max_hp:
                         print(f"{attacker.name} is fatigued and cannot act.")
                         continue
                    if attacker.has_acted:
                        print(f"{attacker.name} has already acted.")
                        continue
                    if attacker.is_capturing is not None:
                        print(f"{attacker.name} cannot attack while capturing.")
                        continue
                    if not attacker.equipped_weapon:
                        print(f"{attacker.name} has no weapon equipped.")
                        continue
                    if len(args) != 2:
                        print("Usage: attack <x> <y>")
                        continue

                    x, y = int(args[0]), int(args[1])
                    target_pos = (x, y)

                    # Recalculate attack range based on current position if needed
                    # This is important if the unit moved before attacking
                    current_attack_range = get_attack_range(attacker, game_state)

                    if target_pos in current_attack_range:
                        defender_id = game_state.game_map.get_unit_id_at(x, y)
                        if defender_id is not None:
                            defender = game_state.get_unit(defender_id)
                            if defender and defender.is_alive and not defender.is_captured and defender.faction != attacker.faction:
                                simulate_combat(attacker, defender, game_state, is_capture_attempt=False)
                                # Fatigue is handled within simulate_combat now
                                # Attack prevents Canto, always end action
                                canto_move_points = None
                                is_canto_active = False
                                current_canto_range = None
                                if not complete_action(attacker, game_state):
                                    current_move_range = None
                                    current_attack_range = None
                                else:
                                    # Movement star activated, clear ranges
                                    current_move_range = None
                                    current_attack_range = None
                            elif defender and defender.faction == attacker.faction:
                                print("Cannot attack allied units.")
                            elif defender and not defender.is_alive:
                                print("Target is already defeated.")
                            elif defender and defender.is_captured:
                                print("Cannot attack captured units.")
                            else:
                                print(f"Invalid target unit at ({x}, {y}).")
                        else:
                            print(f"No unit to attack at ({x}, {y}).")
                    else:
                        print(f"Target ({x}, {y}) is out of attack range.")


                elif command == "capture":
                    attacker = game_state.get_selected_unit()
                    if not attacker:
                        print("No unit selected.")
                        continue
                    if attacker.fatigue >= attacker.max_hp:
                         print(f"{attacker.name} is fatigued and cannot act.")
                         continue
                    if attacker.has_acted:
                        print(f"{attacker.name} has already acted.")
                        continue
                    if attacker.is_capturing is not None:
                        print(f"{attacker.name} is already capturing someone.")
                        continue
                    if not attacker.equipped_weapon:
                        print(f"{attacker.name} has no weapon equipped (needed for capture attempt).")
                        continue
                    if len(args) != 2:
                        print("Usage: capture <x> <y>")
                        continue

                    x, y = int(args[0]), int(args[1])
                    target_pos = (x, y)

                    # Recalculate attack range based on current position if needed
                    current_attack_range = get_attack_range(attacker, game_state)

                    if target_pos in current_attack_range:
                        defender_id = game_state.game_map.get_unit_id_at(x, y)
                        if defender_id is not None:
                            defender = game_state.get_unit(defender_id)
                            if defender and defender.is_alive and not defender.is_captured and defender.faction == Faction.ENEMY:
                                simulate_combat(attacker, defender, game_state, is_capture_attempt=True)
                                # Fatigue is handled within simulate_combat now
                                # Capture prevents Canto, always end action
                                canto_move_points = None
                                is_canto_active = False
                                current_canto_range = None
                                if not complete_action(attacker, game_state):
                                    current_move_range = None
                                    current_attack_range = None
                                else:
                                    # Movement star activated, clear ranges
                                    current_move_range = None
                                    current_attack_range = None
                            elif defender and defender.faction != Faction.ENEMY:
                                print("Cannot capture non-enemy units.")
                            elif defender and not defender.is_alive:
                                print("Target is already defeated.")
                            elif defender and defender.is_captured:
                                print("Target is already captured.")
                            else:
                                print(f"Invalid target unit at ({x}, {y}).")
                        else:
                            print(f"No unit to capture at ({x}, {y}).")
                    else:
                        print(f"Target ({x}, {y}) is out of range for capture attempt.")

                elif command == "equip":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    if selected_unit.has_acted:
                         print(f"{selected_unit.name} has already acted, cannot change equipment.")
                         continue
                    if not args:
                        # List available weapons to equip
                        weapon_list = []
                        for i, item in enumerate(selected_unit.inventory):
                            if isinstance(item, Weapon):
                                equipped_marker = " (E)" if i == selected_unit.equipped_weapon_index else ""
                                weapon_list.append(f"{i}: {item.name}{equipped_marker}")
                        print(f"Equippable weapons for {selected_unit.name}: {weapon_list or ['None']}")
                        continue

                    try:
                        equip_index = int(args[0])
                        if 0 <= equip_index < len(selected_unit.inventory):
                            item_to_equip = selected_unit.inventory[equip_index]
                            if isinstance(item_to_equip, Weapon):
                                selected_unit.equipped_weapon_index = equip_index
                                print(f"{selected_unit.name} equipped {item_to_equip.name}.")
                                # Equipping doesn't end the turn
                                current_attack_range = get_attack_range(selected_unit, game_state) # Update attack range display
                            else:
                                print(f"Cannot equip '{item_to_equip.name}', it is not a weapon.")
                        else:
                            print(f"Invalid inventory index: {equip_index}")
                    except ValueError:
                        print("Invalid input. Please provide the inventory index number to equip.")

                elif command == "inventory":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    print(f"Inventory for {selected_unit.name}:")
                    if not selected_unit.inventory:
                        print("  (Empty)")
                    else:
                        for i, item in enumerate(selected_unit.inventory):
                            equipped_marker = " (E)" if i == selected_unit.equipped_weapon_index else ""
                            uses_str = f" ({item.uses}/{item.max_uses})" if item.uses is not None else ""
                            print(f"  {i}: {item.name}{uses_str}{equipped_marker}")

                elif command == "use": # Renamed from "item"
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    if selected_unit.fatigue >= selected_unit.max_hp:
                         print(f"{selected_unit.name} is fatigued and cannot act.")
                         continue
                    if selected_unit.has_acted:
                         print(f"{selected_unit.name} has already acted.")
                         continue
                    if selected_unit.is_capturing is not None:
                        print(f"{selected_unit.name} cannot use items while capturing.")
                        continue
                    if not args:
                        # List usable items with indices
                        print(f"Usable items for {selected_unit.name}:")
                        found_usable = False
                        for i, item in enumerate(selected_unit.inventory):
                            if not isinstance(item, Weapon) and item.is_usable():
                                print(f"  {i}: {item.name} ({item.uses}/{item.max_uses})")
                                found_usable = True
                        if not found_usable:
                            print("  (None)")
                        continue

                    try:
                        item_index_to_use = int(args[0])
                        if not (0 <= item_index_to_use < len(selected_unit.inventory)):
                            print(f"Invalid inventory index: {item_index_to_use}")
                            continue
                        item_to_use = selected_unit.inventory[item_index_to_use]
                    except (ValueError, IndexError):
                        print("Usage: use <item_index>")
                        continue

                    # No need for 'if not item_to_use:' check as index validation handles it

                    if isinstance(item_to_use, Weapon):
                        print(f"Cannot 'use' a weapon directly. Use 'attack' or 'capture'.")
                        continue
                    if not item_to_use.is_usable():
                         print(f"Cannot use {item_to_use.name}, no uses left.")
                         continue

                    item_used_successfully = False
                    if isinstance(item_to_use, Vulnerary):
                        if selected_unit.hp >= selected_unit.max_hp:
                            print(f"{selected_unit.name} is already at full HP.")
                        else:
                            if item_to_use.use():
                                healed_amount = min(item_to_use.heal_amount, selected_unit.max_hp - selected_unit.hp)
                                selected_unit.hp += healed_amount
                                print(f"{selected_unit.name} used {item_to_use.name}, recovered {healed_amount} HP. (HP: {selected_unit.hp}/{selected_unit.max_hp})")
                                item_used_successfully = True
                                if item_to_use.uses == 0:
                                    print(f"{item_to_use.name} broke.")
                                    selected_unit.remove_item(item_to_use)
                            else:
                                print(f"Failed to use {item_to_use.name} (no uses left).")
                    else:
                        print(f"Item type '{item_to_use.name}' use effect not implemented yet.")

                elif command == "promote":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    if selected_unit.fatigue >= selected_unit.max_hp:
                         print(f"{selected_unit.name} is fatigued and cannot act.")
                         continue
                    if selected_unit.has_acted:
                         print(f"{selected_unit.name} has already acted.")
                         continue
                    if selected_unit.is_capturing is not None:
                        print(f"{selected_unit.name} cannot promote while capturing.")
                        continue

                    # Check for Master Seal
                    master_seal_item = None
                    seal_index = -1
                    for i, item in enumerate(selected_unit.inventory):
                        # Need to import MasterSeal from models
                        from .models import MasterSeal
                        if isinstance(item, MasterSeal):
                            master_seal_item = item
                            seal_index = i
                            break

                    if not master_seal_item:
                        print(f"{selected_unit.name} does not have a Master Seal.")
                        continue

                    # Check if promotion path exists
                    # Need to import PROMOTION_PATHS from models
                    from .models import PROMOTION_PATHS
                    current_class = selected_unit.cls_name # Assuming cls_name attribute exists - NEED TO ADD THIS TO UNIT MODEL
                    if current_class not in PROMOTION_PATHS:
                        print(f"No promotion path defined for class '{current_class}'.")
                        continue

                    promo_data = PROMOTION_PATHS[current_class]
                    promoted_class = promo_data['promoted_class']
                    stat_gains = promo_data['gains']
                    wexp_bonus = promo_data.get('wexp_bonus', {}) # Use .get for safety

                    print(f"Promoting {selected_unit.name} from {current_class} to {promoted_class}...")

                    # Consume Master Seal
                    if master_seal_item.use():
                        if master_seal_item.uses == 0:
                            print(f"  Used {master_seal_item.name}.")
                            selected_unit.remove_item(master_seal_item)
                    else:
                        # Should not happen if check passed, but handle defensively
                        print(f"  Error: Could not use {master_seal_item.name}.")
                        continue

                    # Apply Stat Gains
                    print("  Applying stat gains:")
                    for stat, gain in stat_gains.items():
                        current_val = getattr(selected_unit, stat, 0)
                        # TODO: Check against class caps later
                        new_val = current_val + gain
                        setattr(selected_unit, stat, new_val)
                        print(f"    {stat.capitalize()}: {current_val} + {gain} -> {new_val}")

                    # Update Class Name
                    selected_unit.cls_name = promoted_class # NEED TO ADD cls_name attribute

                    # Update Weapon Ranks
                    print("  Updating weapon ranks:")
                    for wtype, new_rank_letter in wexp_bonus.items():
                        # Need WEAPON_RANKS from models
                        from .models import WEAPON_RANKS
                        if new_rank_letter in WEAPON_RANKS:
                             current_rank = selected_unit.weapon_ranks.get(wtype, 'E')
                             # Only update if the new rank is higher
                             if current_rank not in WEAPON_RANKS or WEAPON_RANKS.index(new_rank_letter) > WEAPON_RANKS.index(current_rank):
                                 selected_unit.weapon_ranks[wtype] = new_rank_letter
                                 print(f"    {wtype.capitalize()} rank set to {new_rank_letter}.")
                        else:
                             print(f"    Warning: Invalid target rank '{new_rank_letter}' for {wtype}.")


                    # Reset Level (Thracia rule)
                    selected_unit.level = 1 # NEED TO ADD level attribute
                    selected_unit.exp = 0 # NEED TO ADD exp attribute
                    print(f"  Level reset to 1.")

                    # Promotion consumes action, prevents Canto
                    canto_move_points = None
                    is_canto_active = False
                    if not complete_action(selected_unit, game_state):
                        current_move_range = None
                        current_attack_range = None
                    else: # Movement star activated
                        current_move_range = None
                        current_attack_range = None

                    if item_used_successfully:
                        # Apply fatigue for item use
                        selected_unit.fatigue += FATIGUE_COST_ITEM
                        print(f"  (+{FATIGUE_COST_ITEM} Fatigue for {selected_unit.name}. Total: {selected_unit.fatigue})")

                        # Item use allows Canto (check before completing action)
                        is_mounted = selected_unit.move_type in [MoveType.CAVALRY, MoveType.FLYING]
                        can_canto = is_mounted and canto_move_points is not None and canto_move_points > 0

                        if can_canto:
                             print(f"  {selected_unit.name} can Canto with {canto_move_points} movement.")
                             # Recalculate Canto range (position hasn't changed)
                             current_canto_range = calculate_move_range(game_state, selected_unit, override_max_move=canto_move_points)
                             current_move_range = None # Clear normal move range display
                             current_attack_range = get_attack_range(selected_unit, game_state)
                             is_canto_active = True
                             # Keep unit selected, don't call complete_action yet
                             print(f"  (Select Canto move (+), another action, or wait)")
                        else:
                             # End action if not mounted or no Canto points left
                             canto_move_points = None
                             is_canto_active = False
                             current_canto_range = None
                             # Call complete_action here to handle has_acted and movement stars
                             if not complete_action(selected_unit, game_state):
                                 current_move_range = None
                                 current_attack_range = None
                             else: # Movement star activated
                                 current_move_range = None
                                 current_attack_range = None


                elif command == "trade":
                    # ... (trade logic remains the same) ...
                    pass


                elif command == "release":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    if selected_unit.fatigue >= selected_unit.max_hp:
                         print(f"{selected_unit.name} is fatigued and cannot act.")
                         continue
                    # Allow release even if acted? Yes.

                    if selected_unit.is_capturing is not None:
                        captive_id = selected_unit.is_capturing
                        captive_unit = game_state.units.get(captive_id)
                        if captive_unit:
                            print(f"{selected_unit.name} releases {captive_unit.name}.")
                            captive_unit.is_captured = False
                        else:
                             print(f"Error: Captive unit ID {captive_id} not found.")

                        selected_unit.is_capturing = None
                        # Fatigue handled in action
                        # Check Canto after releasing
                        is_mounted = selected_unit.move_type in [MoveType.CAVALRY, MoveType.FLYING]
                        if is_mounted and canto_move_points is not None and canto_move_points > 0:
                             print(f"  {selected_unit.name} can Canto with {canto_move_points} movement.")
                             current_move_range = calculate_move_range(game_state, selected_unit, override_max_move=canto_move_points)
                             current_attack_range = get_attack_range(selected_unit, game_state)
                             is_canto_active = True
                             # Keep unit selected
                        else:
                             # End action if no Canto possible
                             canto_move_points = None
                             is_canto_active = False
                             if not complete_action(selected_unit, game_state):
                                 current_move_range = None
                                 current_attack_range = None
                             else:
                                 current_move_range = None
                                 current_attack_range = None
                    else:
                        print(f"{selected_unit.name} is not capturing anyone.")

                elif command == "steal":
                    thief = game_state.get_selected_unit()
                    if not thief:
                        print("No unit selected.")
                        continue
                    if not thief.can_steal: # Check if the unit has the steal ability
                        print(f"{thief.name} cannot steal.")
                        continue
                    if thief.fatigue >= thief.max_hp:
                         print(f"{thief.name} is fatigued and cannot act.")
                         continue
                    if thief.has_acted:
                         print(f"{thief.name} has already acted.")
                         continue
                    if thief.is_capturing is not None:
                        print(f"{thief.name} cannot steal while capturing.")
                        continue
                    if len(thief.inventory) >= 7: # Thracia inventory limit
                         print(f"{thief.name}'s inventory is full.")
                         continue

                    if len(args) < 2 or len(args) > 3:
                        print("Usage: steal <x> <y> [item_index]")
                        continue

                    try:
                        x, y = int(args[0]), int(args[1])
                        target_pos = (x, y)
                    except ValueError:
                        print("Invalid coordinates.")
                        continue

                    # Check adjacency
                    dist_x = abs(thief.position[0] - x)
                    dist_y = abs(thief.position[1] - y)
                    distance = dist_x + dist_y
                    if distance != 1:
                        print("Target is not adjacent.")
                        continue

                    target_id = game_state.game_map.get_unit_id_at(x, y)
                    if target_id is None:
                        print(f"No unit at ({x}, {y}).")
                        continue

                    target = game_state.get_unit(target_id)
                    if not target or not target.is_alive or target.is_captured:
                        print("Invalid target.")
                        continue
                    if target.faction == thief.faction:
                        print("Cannot steal from allies.")
                        continue

                    # Check Steal Conditions (AS and Item Weight)
                    # Need to import calculate_attack_speed from combat
                    # from game.combat import calculate_attack_speed # Import AS calc
                    from game.models import FATIGUE_COST_STEAL # Import fatigue cost from models
                    thief_as = calculate_attack_speed(thief, game_state)
                    target_as = calculate_attack_speed(target, game_state)

                    if thief_as <= target_as:
                        print(f"Cannot steal: {thief.name}'s AS ({thief_as}) must be greater than {target.name}'s AS ({target_as}).")
                        continue

                    # List stealable items if no index provided
                    if len(args) == 2:
                        print(f"Stealable items from {target.name} (Thief Con: {thief.constitution}, AS: {thief_as} > Tgt AS: {target_as}):")
                        found_stealable = False
                        for i, item in enumerate(target.inventory):
                            # Check weight condition
                            item_weight = getattr(item, 'weight', float('inf')) # Get weight or assume infinite if no weight attr
                            if item_weight <= thief.constitution:
                                print(f"  {i}: {item.name} (Wt: {item_weight})")
                                found_stealable = True
                        if not found_stealable:
                            print("  (None stealable - check weight/AS)")
                        continue # Wait for user to provide index

                    # Attempt to steal specific item index
                    if len(args) == 3:
                        try:
                            item_index_to_steal = int(args[2])
                            if not (0 <= item_index_to_steal < len(target.inventory)):
                                print(f"Invalid target inventory index: {item_index_to_steal}")
                                continue
                            item_to_steal = target.inventory[item_index_to_steal]
                        except ValueError:
                            print("Invalid item index.")
                            continue

                        # Final check: Item weight vs Thief Con
                        item_weight = getattr(item_to_steal, 'weight', float('inf'))
                        if item_weight > thief.constitution:
                             print(f"Cannot steal {item_to_steal.name}: Item weight ({item_weight}) exceeds {thief.name}'s Constitution ({thief.constitution}).")
                             continue

                        # Perform the steal
                        print(f"Attempting to steal {item_to_steal.name} from {target.name}...")
                        stolen_item = target.inventory.pop(item_index_to_steal)
                        thief.inventory.append(stolen_item)
                        print(f"Success! {thief.name} stole {stolen_item.name}.")

                        # Handle target potentially becoming unarmed
                        if target.equipped_weapon_index == item_index_to_steal:
                             print(f"  {target.name} is now unarmed!")
                             target.equipped_weapon_index = None
                             target._auto_equip_first_weapon() # Try to equip something else
                        elif target.equipped_weapon_index is not None and target.equipped_weapon_index > item_index_to_steal:
                             # Adjust equipped index if it was after the stolen item
                             target.equipped_weapon_index -= 1

                        # Fatigue handled in action
                        # Check Canto after stealing
                        is_mounted = thief.move_type in [MoveType.CAVALRY, MoveType.FLYING]
                        if is_mounted and canto_move_points is not None and canto_move_points > 0:
                             print(f"  {thief.name} can Canto with {canto_move_points} movement.")
                             current_move_range = calculate_move_range(game_state, thief, override_max_move=canto_move_points)
                             current_attack_range = get_attack_range(thief, game_state)
                             is_canto_active = True
                             # Keep unit selected
                        else:
                             # End action if no Canto possible
                             canto_move_points = None
                             is_canto_active = False
                             if not complete_action(thief, game_state):
                                 current_move_range = None
                                 current_attack_range = None
                             else:
                                 current_move_range = None
                                 current_attack_range = None

                elif command == "staff": # NEW command
                    caster = game_state.get_selected_unit()
                    if not caster:
                        print("No unit selected.")
                        continue
                    if caster.fatigue >= caster.max_hp:
                         print(f"{caster.name} is fatigued and cannot act.")
                         continue
                    if caster.has_acted:
                         print(f"{caster.name} has already acted.")
                         continue
                    if caster.is_capturing is not None:
                        print(f"{caster.name} cannot use staves while capturing.")
                        continue

                    equipped_staff = caster.equipped_weapon
                    if not equipped_staff or not isinstance(equipped_staff, Weapon) or equipped_staff.wtype != "Staff":
                        print(f"{caster.name} does not have a staff equipped.")
                        continue
                    # Ensure it has a rank for fatigue calculation later
                    if not equipped_staff.staff_rank:
                         print(f"Error: Equipped staff '{equipped_staff.name}' has no rank defined.")
                         continue

                    # Basic command structure, no actual effect yet
                    if len(args) != 2:
                        print("Usage: staff <target_x> <target_y>")
                        continue

                    try:
                        target_x, target_y = int(args[0]), int(args[1])
                        target_pos = (target_x, target_y)

                        # --- Staff Range Check ---
                        # Basic Heal staff is range 1
                        staff_range = 1 # Default for Heal/Mend
                        # TODO: Add logic for other staff ranges later (e.g., Physic, status staves)
                        dist_x = abs(caster.position[0] - target_x)
                        dist_y = abs(caster.position[1] - target_y)
                        distance = dist_x + dist_y

                        if distance > staff_range:
                            print(f"Target ({target_x}, {target_y}) is out of range for {equipped_staff.name} (Range: {staff_range}).")
                            continue

                        # --- Target Validation ---
                        target_unit_id = game_state.game_map.get_unit_id_at(target_x, target_y)
                        target_unit = game_state.get_unit(target_unit_id) if target_unit_id is not None else None

                        staff_used_successfully = False
                        staff_name = equipped_staff.name.lower() # Use lowercase for comparison
                        # --- Heal Staff Logic ---
                        if staff_name == "heal staff": # Check specifically for Heal staff
                            if not target_unit:
                                print(f"No unit at ({target_x}, {target_y}).")
                                continue
                            if target_unit.faction != caster.faction:
                                print(f"Cannot heal non-allied unit {target_unit.name}.")
                                continue
                            if not target_unit.is_alive or target_unit.is_captured:
                                print(f"Cannot heal defeated or captured unit {target_unit.name}.")
                                continue
                            if target_unit.hp >= target_unit.max_hp:
                                print(f"{target_unit.name} is already at full HP.")
                                continue

                            # Calculate Heal Amount (10 + User's Magic)
                            heal_amount = 10 + caster.magic
                            actual_healed = min(heal_amount, target_unit.max_hp - target_unit.hp)
                            target_unit.hp += actual_healed
                            print(f"{caster.name} used {equipped_staff.name} on {target_unit.name}, recovering {actual_healed} HP. (HP: {target_unit.hp}/{target_unit.max_hp})")
                            staff_used_successfully = True

                        # --- Restore Staff Logic ---
                        elif staff_name == "restore staff":
                            if not target_unit:
                                print(f"No unit at ({target_x}, {target_y}).")
                                continue
                            if target_unit.faction != caster.faction:
                                print(f"Cannot restore non-allied unit {target_unit.name}.")
                                continue
                            if not target_unit.is_alive or target_unit.is_captured:
                                print(f"Cannot restore defeated or captured unit {target_unit.name}.")
                                continue
                            if target_unit.status_effect == StatusEffect.NONE:
                                print(f"{target_unit.name} has no status condition to restore.")
                                continue

                            # Cure the status
                            old_status = target_unit.status_effect
                            target_unit.status_effect = StatusEffect.NONE
                            print(f"{caster.name} used {equipped_staff.name} on {target_unit.name}, curing {old_status}.")
                            staff_used_successfully = True

                        # --- Mend Staff Logic (Example) ---
                        elif staff_name == "mend staff":
                            if not target_unit:
                                print(f"No unit at ({target_x}, {target_y}).")
                                continue

                            # Calculate Heal Amount (10 + User's Magic)
                            heal_amount = 10 + caster.magic
                            actual_healed = min(heal_amount, target_unit.max_hp - target_unit.hp)
                            target_unit.hp += actual_healed
                            print(f"{caster.name} used {equipped_staff.name} on {target_unit.name}, recovering {actual_healed} HP. (HP: {target_unit.hp}/{target_unit.max_hp})")
                            staff_used_successfully = True
                        else:
                             # Placeholder for other staves
                             print(f"{caster.name} uses {equipped_staff.name} (Rank {equipped_staff.staff_rank}) on ({target_x}, {target_y})... (Effect for this staff not implemented yet)")
                             # Assume success for fatigue/use consumption for now if target exists
                             if target_unit:
                                 staff_used_successfully = True # Allow fatigue/use for unimplemented staves if target valid

                        # --- Apply WExp, Fatigue & Consume Use (if successful) ---
                        if staff_used_successfully:

                           # --- Grant Staff WExp ---
                           from .models import WEXP_THRESHOLDS, WEAPON_RANKS # Import WExp constants
                           staff_rank_wexp_gain = {'E': 1, 'D': 2, 'C': 3, 'B': 4, 'A': 5, '*': 5}
                           rank = equipped_staff.staff_rank
                           wexp_gain = staff_rank_wexp_gain.get(rank, 1) # Default to 1 if rank unknown
                           wtype = "Staff" # Staff WExp type
                           current_wexp = caster.wexp.get(wtype, 0)
                           new_total_wexp = current_wexp + wexp_gain
                           caster.wexp[wtype] = new_total_wexp
                           print(f"  ({caster.name} gained +{wexp_gain} WExp for {wtype}. Total: {new_total_wexp})")

                           # --- Check for Staff Rank Increase ---
                           current_staff_rank = caster.weapon_ranks.get(wtype, 'E') # Default to E
                           current_rank_index = WEAPON_RANKS.index(current_staff_rank) if current_staff_rank in WEAPON_RANKS else 0
                           if current_staff_rank != '*':
                               threshold_for_next_rank = WEXP_THRESHOLDS.get(current_staff_rank)
                               if threshold_for_next_rank is not None and new_total_wexp >= threshold_for_next_rank:
                                   next_rank_index = current_rank_index + 1
                                   if next_rank_index < len(WEAPON_RANKS):
                                       new_rank = WEAPON_RANKS[next_rank_index]
                                       caster.weapon_ranks[wtype] = new_rank
                                       print(f"  RANK UP! {caster.name}'s {wtype} rank increased to {new_rank}!")

                           # --- Apply Fatigue ---
                           from game.models import FATIGUE_COST_STAFF
                           cost = FATIGUE_COST_STAFF.get(rank, 1) # Default to 1 if rank not found
                           caster.fatigue += cost
                           print(f"  ({caster.name} fatigue increases by {cost} to {caster.fatigue})")

                           # Consume staff use
                           if equipped_staff.use(): # Use the item's use method
                               if equipped_staff.uses == 0:
                                   print(f"  {equipped_staff.name} broke.")
                                   caster.remove_item(equipped_staff) # Remove the broken staff
                           else:
                               # This case should ideally not be reached if is_usable was checked, but handle defensively
                               print(f"  Error: Failed to consume use for {equipped_staff.name}.")
                               continue # Skip action completion if use failed unexpectedly
                            # TODO: Add WExp gain for staff use (Already added above)

                        # Staff use prevents Canto, always end action
                        canto_move_points = None
                        is_canto_active = False
                        if not complete_action(caster, game_state):
                            current_move_range = None
                            current_attack_range = None
                        else:
                            # Movement star activated, clear ranges
                            current_move_range = None
                            current_attack_range = None

                    except ValueError:
                        print("Invalid coordinates.")
                        continue

                elif command == "wait":
                    selected_unit = game_state.get_selected_unit()
                    if not selected_unit:
                        print("No unit selected.")
                        continue
                    if selected_unit.fatigue >= selected_unit.max_hp:
                         print(f"{selected_unit.name} is fatigued and cannot act.")
                         continue
                    if selected_unit.has_acted:
                         print(f"{selected_unit.name} has already acted.")
                         continue
                    print(f"{selected_unit.name} waits.")
                    # Wait always ends the turn, regardless of Canto potential
                    canto_move_points = None
                    is_canto_active = False
                    if not complete_action(selected_unit, game_state):
                        current_move_range = None
                        current_attack_range = None
                    else:
                        # Movement star activated, clear ranges
                        current_move_range = None
                        current_attack_range = None

                elif command == "info":
                    target_unit = None # Initialize target_unit here
                    unit_found = False # Flag to track if unit was found

                    # PRIORITIZE checking for coordinate arguments
                    if len(args) == 2:
                        try:
                            x, y = int(args[0]), int(args[1])
                            unit_id = game_state.game_map.get_unit_id_at(x, y)
                            if unit_id is not None:
                                target_unit = game_state.units.get(unit_id) # Get directly from dict
                                if target_unit:
                                    unit_found = True # Mark as found
                                else:
                                     print(f"Error: Unit ID {unit_id} found on map but not in units dictionary.")
                            else:
                                print(f"No unit at ({x}, {y}).")
                                # target_unit remains None
                        except ValueError:
                             print("Invalid coordinates for info command.")
                             # target_unit remains None
                    elif len(args) == 0: # No coordinates provided, use selected unit
                        target_unit = game_state.get_selected_unit()
                        if target_unit:
                            unit_found = True
                        else:
                             print("No unit selected and no coordinates provided.")
                    else: # Incorrect number of arguments
                        print("Usage: info or info <x> <y>")

                    # Display info ONLY if a unit was found by either method
                    if unit_found and target_unit:
                         capture_status_str = ""
                         if target_unit.is_captured:
                             capture_status_str = " | Status: Captured"
                         elif target_unit.is_capturing is not None:
                             captive = game_state.units.get(target_unit.is_capturing)
                             captive_name = captive.name if captive else "Unknown"
                             capture_status_str = f" | Status: Capturing {captive_name}"
                         elif not target_unit.is_alive:
                              capture_status_str = " | Status: Defeated"
                         else:
                              capture_status_str = " | Status: Alive"

                         # Display Class, Level, Exp
                         print(f"Info: {target_unit.name} (ID: {target_unit.id}) | Class: {target_unit.cls_name} | Lvl: {target_unit.level} | Exp: {target_unit.exp}/100")
                         print(f"  Faction: {target_unit.faction} | MoveType: {target_unit.move_type}{capture_status_str}")
                         print(f"  Pos: {target_unit.position} | HP: {target_unit.hp}/{target_unit.max_hp} | Mov: {target_unit.mov}")
                         print(f"  Stats: Str:{target_unit.strength} Skl:{target_unit.skill} Spd:{target_unit.speed} Lck:{target_unit.luck} Def:{target_unit.defense} Con:{target_unit.constitution}")
                         print("  Inventory:")
                         if not target_unit.inventory:
                             print("    (Empty)")
                         else:
                             for i, item in enumerate(target_unit.inventory):
                                 equipped_marker = " (E)" if i == target_unit.equipped_weapon_index else ""
                                 uses_str = f" ({item.uses}/{item.max_uses})" if item.uses is not None else ""
                                 print(f"    {i}: {item.name}{uses_str}{equipped_marker}")
                         equipped_idx = target_unit.equipped_weapon_index
                         equipped_name = target_unit.inventory[equipped_idx].name if equipped_idx is not None and equipped_idx < len(target_unit.inventory) else "None"
                         acted_status = " [Acted]" if target_unit.has_acted else ""
                         print(f"  Equipped: {equipped_name} | Acted: {target_unit.has_acted}{acted_status}")
                         # Add fatigue display
                         print(f"  Fatigue: {target_unit.fatigue}/{target_unit.max_hp}")
                         # Display Skills
                         skills_str = ", ".join(target_unit.skills) if target_unit.skills else "None"
                         print(f"  Skills: {skills_str}")
                         # Display Status Effect
                         status_str = target_unit.status_effect if target_unit.status_effect != StatusEffect.NONE else "Normal"
                         print(f"  Status: {status_str}")


                elif command == "endturn":
                    if game_state.active_faction == Faction.PLAYER:
                        print("\n--- Ending Player Phase ---")

                        # --- Fatigue Check ---
                        print("Checking fatigue...")
                        for unit in list(game_state.units.values()): # Iterate over a copy in case units are modified
                             if unit.faction == Faction.PLAYER and unit.is_alive and not unit.is_captured:
                                 # Use unit.max_hp for the threshold check
                                 if unit.fatigue >= unit.max_hp:
                                     # TODO: Implement actual fatigue status effect / deployment restriction later
                                     print(f"  WARNING: {unit.name} is fatigued ({unit.fatigue}/{unit.max_hp})!")
                        # ---------------------

                        # --- Transition to Enemy Phase ---
                        game_state.active_faction = Faction.ENEMY
                        game_state.selected_unit_id = None
                        current_move_range = None
                        current_attack_range = None
                        print("\n--- Starting Enemy Phase ---")
                        render_map(game_state)
                        run_enemy_ai(game_state) # Run Enemy AI

                        # Check for Game Over after Enemy Phase
                        leif = game_state.units.get(1)
                        if leif and not leif.is_alive:
                            render_map(game_state)
                            print("\n--- GAME OVER ---")
                            print("Leif has been defeated!")
                            sys.exit(0)

                        # --- Transition to NPC Phase ---
                        # Check if there are any living Ally units
                        npc_units_exist = any(u.faction == Faction.ALLY and u.is_alive for u in game_state.units.values())
                        if npc_units_exist:
                            game_state.active_faction = Faction.ALLY # Use ALLY faction for NPC phase
                            game_state.selected_unit_id = None
                            current_move_range = None
                            current_attack_range = None
                            print("\n--- Starting NPC Phase ---")
                            render_map(game_state)
                            # Call the imported run_npc_ai function
                            run_npc_ai(game_state)
                            print("(NPC AI not implemented yet)")
                        else:
                            print("\n(Skipping NPC Phase - No Ally units)")


                        # --- Transition back to Player Phase ---
                        game_state.active_faction = Faction.PLAYER
                        game_state.turn += 1
                        game_state.reset_player_actions() # Resets actions and applies fatigue restriction
                        print(f"\n--- Starting Turn {game_state.turn} - Player Phase ---")
                        # Apply Player Phase start effects
                        apply_turn_start_effects(game_state)
                    else: # This else corresponds to `if game_state.active_faction == Faction.PLAYER:`
                        print("Cannot end turn now.")

                else:
                    print(f"Unknown command: {command}")

            elif game_state.active_faction == Faction.ENEMY:
                 print("Waiting for Enemy Phase to complete...")

        except ValueError:
            print("Invalid input. Please enter numbers for coordinates.")
        except IndexError:
             print("Invalid command arguments.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Run Fantasy Tactics CLI with specific test setup.")
    parser.add_argument(
        "--setup",
        type=str,
        default="mvp_phase1", # Default to the new MVP setup
        help="Name of the test setup to load (e.g., 'mvp_phase1', 'effectiveness', 'combat')."
    )
    args = parser.parse_args()
    # ----------------------

    src_dir = os.path.dirname(__file__)
    game_dir = os.path.join(src_dir, "game")
    if not os.path.exists(os.path.join(game_dir, "__init__.py")):
        open(os.path.join(game_dir, "__init__.py"), 'a').close()

    # Map the new default name to the function
    if args.setup == "mvp_phase1":
        run_cli(setup_name="mvp_phase1")
    else:
        # Add the new setup to the existing logic
        setup_functions = {
            "effectiveness": setup_effectiveness_test_state,
            "combat": setup_combat_test_state,
            "fatigue": setup_fatigue_test_state,
            "staff": setup_staff_test_state,
            "item": setup_item_test_state,
            "ai": setup_ai_test_state,
            "bonus": setup_bonus_test_state,
            "canto": setup_canto_test_state,
            "capture": setup_capture_test_state,
            "crit": setup_crit_test_state,
            "magic_attack": setup_magic_attack_test_state,
            "magic_crit": setup_magic_crit_test_state,
            "mvp": setup_mvp_test_state, # Keep old 'mvp' test setup distinct
            "steal": setup_steal_test_state,
            "skills": setup_skills_test_state,
            "status": setup_status_test_state,
            "movestars": setup_movestars_test_state,
            "triangle": setup_triangle_test_state,
            "terrain": setup_terrain_test_state,
            "mvp_phase1": setup_mvp_phase1_state, # Add the new one here
            "staff_wexp": setup_staff_wexp_test_state # Add Staff WExp setup
        }
        if args.setup in setup_functions:
             run_cli(setup_name=args.setup) # Pass the setup name
        elif args.setup in setup_functions: # Check if setup exists before calling
            run_cli(setup_name=args.setup) # Pass the setup name
        else:
             print(f"Error: Unknown setup name '{args.setup}'. Available: {list(setup_functions.keys())}. Using default 'mvp_phase1'.")
             run_cli(setup_name="mvp_phase1")