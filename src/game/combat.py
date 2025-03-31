# src/game/combat.py

import random
from typing import Optional, Tuple
from .models import Unit, GameState, Weapon # Assuming Weapon is defined in models

# --- Combat Calculation Helpers ---

def calculate_attack_speed(unit: Unit) -> int:
    """Calculates Attack Speed (AS). Simplified: Spd - Weapon Weight."""
    # Thracia: AS = Speed – max( (Weapon Weight – Con), 0 ) for physical
    # Thracia: AS = Speed – Weapon Weight for magic
    # MVP Simplification: Ignore Con for now.
    weapon_weight = unit.equipped_weapon.weight if unit.equipped_weapon else 0
    # Ensure AS doesn't go below 0
    return max(0, unit.speed - weapon_weight)

def calculate_hit_rate(unit: Unit) -> int:
    """Calculates Hit Rate. Simplified: Weapon Hit + (2 * Skill) + Luck."""
    # Thracia: Hit = Weapon Hit + (2 * Skill) + Luck + Support + Leadership + Charisma + WTriangle
    # MVP Simplification: Ignore Support, Leadership, Charisma, WTriangle
    weapon_hit = unit.equipped_weapon.hit if unit.equipped_weapon else 0
    # Ensure base hit isn't negative if stats are low
    return max(0, weapon_hit + (2 * unit.skill) + unit.luck)

def calculate_avoid(unit: Unit) -> int:
    """Calculates Avoid Rate. Simplified: (2 * AS) + Luck."""
    # Thracia: Avoid = (2 * Attack Speed) + Luck + Support + Leadership + Charisma + Terrain
    # MVP Simplification: Ignore Support, Leadership, Charisma, Terrain
    attack_speed = calculate_attack_speed(unit)
    return max(0, (2 * attack_speed) + unit.luck)

def calculate_damage(attacker: Unit, defender: Unit) -> int:
    """Calculates damage dealt. Simplified: (Attacker Str + Weapon Mt) - Defender Def."""
    # Thracia: Physical Damage = (Attacker Str + Weapon Mt * Eff) - (Defender Def + Terrain Def)
    # Thracia: Magical Damage = (Attacker Mag + Weapon Mt * Eff) - (Defender Mag + Terrain Mag + M Up)
    # MVP Simplification: Physical only, ignore effectiveness, terrain, M Up.
    if not attacker.equipped_weapon:
        return 0 # Cannot attack without a weapon

    # TODO: Add magic calculation later based on weapon type or attacker class
    attack_power = attacker.strength + attacker.equipped_weapon.might
    defense_power = defender.defense
    # Ensure damage is not negative
    return max(0, attack_power - defense_power)

def does_double(attacker: Unit, defender: Unit) -> bool:
    """Checks if the attacker doubles the defender."""
    # Thracia: Double if Attacker AS >= Defender AS + 4
    attacker_as = calculate_attack_speed(attacker)
    defender_as = calculate_attack_speed(defender)
    return attacker_as >= defender_as + 4

def resolve_attack(attacker: Unit, defender: Unit, game_state: GameState) -> bool:
    """Resolves a single attack instance (hit check, damage application). Returns True if target was hit."""
    if not attacker.is_alive or not defender.is_alive:
        return False # Cannot attack or be attacked if not alive

    attacker_hit_rate = calculate_hit_rate(attacker)
    defender_avoid = calculate_avoid(defender)
    # Thracia: Hit Chance = clamp(Attacker Hit - Defender Avoid, 1, 99)
    # MVP Simplification: Clamp 0-100 for now. Use 1-99 later.
    hit_chance = max(0, min(100, attacker_hit_rate - defender_avoid))

    print(f"  {attacker.name} attacks {defender.name} (Hit%: {hit_chance})")

    # Roll for hit (1 RN system)
    roll = random.randint(1, 100)
    if roll <= hit_chance:
        damage = calculate_damage(attacker, defender)
        defender.hp = max(0, defender.hp - damage)
        print(f"  HIT! {defender.name} takes {damage} damage. (HP: {defender.hp}/{defender.max_hp})")
        if defender.hp == 0:
            game_state.handle_unit_death(defender) # Handle death state
        return True # Hit landed
    else:
        print(f"  MISS!")
        return False # Attack missed

# --- Main Combat Simulation ---

def simulate_combat(attacker: Unit, defender: Unit, game_state: GameState):
    """Simulates a full round of combat between two units."""
    print(f"\n--- Combat: {attacker.name} vs {defender.name} ---")

    # Check if attacker can attack (has weapon)
    if not attacker.equipped_weapon:
        print(f"  {attacker.name} cannot attack (no weapon equipped).")
        print(f"--- Combat End ---")
        return

    # 1. Attacker's first strike
    resolve_attack(attacker, defender, game_state)

    # 2. Defender's counter-attack (if alive and in range)
    if defender.is_alive and defender.equipped_weapon:
        # Check range for counter-attack
        dist_x = abs(attacker.position[0] - defender.position[0])
        dist_y = abs(attacker.position[1] - defender.position[1])
        distance = dist_x + dist_y # Manhattan distance for grid
        weapon = defender.equipped_weapon
        if weapon.range_min <= distance <= weapon.range_max:
            print(f"  {defender.name} counters!")
            resolve_attack(defender, attacker, game_state)
        else:
            print(f"  {defender.name} cannot counter (out of range).")

    # 3. Attacker's follow-up attack (if doubling and both are alive)
    if attacker.is_alive and defender.is_alive and does_double(attacker, defender):
        print(f"  {attacker.name} performs a follow-up attack!")
        resolve_attack(attacker, defender, game_state)

    # (Could add defender follow-up if they double, but less common in FE)

    print(f"--- Combat End ---")