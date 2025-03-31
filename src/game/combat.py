# src/game/combat.py (Updated)

import random
import math # Need math for floor/ceil if halving stats
from typing import Optional, Tuple
from .models import Unit, GameState, Weapon, MoveType # Import MoveType for capture condition

# --- Combat Calculation Helpers ---

def calculate_attack_speed(unit: Unit) -> int:
    """Calculates Attack Speed (AS)."""
    # Thracia: AS = Speed – max( (Weapon Weight – Con), 0 ) for physical
    # Thracia: AS = Speed – Weapon Weight for magic
    # MVP Implementation: Include Con for physical, ignore magic distinction for now.
    if not unit.equipped_weapon or not unit.is_alive: # Check if alive
        return unit.speed # No weapon or dead, AS is just Speed

    weapon = unit.equipped_weapon
    weapon_weight = weapon.weight

    # TODO: Differentiate between physical and magical weapons later
    # Assuming all current weapons are physical for AS calc involving Con
    effective_weight = max(0, weapon_weight - unit.constitution) # Con is NOT halved
    attack_speed = unit.speed - effective_weight

    # Ensure AS doesn't go below 0
    return max(0, attack_speed)

def calculate_hit_rate(unit: Unit) -> int:
    """Calculates Hit Rate. Simplified: Weapon Hit + (2 * Skill) + Luck."""
    # Thracia: Hit = Weapon Hit + (2 * Skill) + Luck + Support + Leadership + Charisma + WTriangle
    # MVP Simplification: Ignore Support, Leadership, Charisma, WTriangle
    if not unit.is_alive: return 0
    weapon_hit = unit.equipped_weapon.hit if unit.equipped_weapon else 0
    # Ensure base hit isn't negative if stats are low
    return max(0, weapon_hit + (2 * unit.skill) + unit.luck)

def calculate_avoid(unit: Unit) -> int:
    """Calculates Avoid Rate. Simplified: (2 * AS) + Luck."""
    # Thracia: Avoid = (2 * Attack Speed) + Luck + Support + Leadership + Charisma + Terrain
    # MVP Simplification: Ignore Support, Leadership, Charisma, Terrain
    if not unit.is_alive: return 0
    attack_speed = calculate_attack_speed(unit)
    return max(0, (2 * attack_speed) + unit.luck)

def calculate_damage(
    attacker_str: int, # Pass stats explicitly
    attacker_weapon_might: int,
    defender_def: int
) -> int:
    """Calculates damage dealt using provided stats."""
    # MVP Simplification: Physical only, ignore effectiveness, terrain, M Up.
    attack_power = attacker_str + attacker_weapon_might
    defense_power = defender_def
    return max(0, attack_power - defense_power)

def does_double(attacker: Unit, defender: Unit) -> bool:
    """Checks if the attacker doubles the defender (using base stats)."""
    # Thracia: Double if Attacker AS >= Defender AS + 4
    if not attacker.is_alive or not defender.is_alive: return False
    attacker_as = calculate_attack_speed(attacker)
    defender_as = calculate_attack_speed(defender)
    return attacker_as >= defender_as + 4


def resolve_attack(
    attacker: Unit,
    defender: Unit,
    game_state: GameState,
    is_capture_attempt: bool = False,
    capture_penalty_active: bool = False # Is the penalty applied to *this* attacker?
) -> bool:
    """Resolves a single attack instance (hit check, damage application)."""
    # Ensure both units are alive at the start of this specific attack resolution
    if not attacker.is_alive or not defender.is_alive:
        return False

    # Apply capture penalties temporarily if needed for *this* attack
    temp_str = attacker.strength
    temp_skl = attacker.skill
    temp_spd = attacker.speed
    # Penalty also applies when being attacked while capturing/carrying
    temp_def = attacker.defense # Used if this unit is defending in the counter attack

    # Thracia: Str, Mag, Skl, Spd, Def halved (floor?) during capture attempt/carry
    if capture_penalty_active:
        temp_str = math.floor(temp_str / 2)
        # temp_mag = math.floor(attacker.magic / 2) # Add later
        temp_skl = math.floor(temp_skl / 2)
        temp_spd = math.floor(temp_spd / 2)
        temp_def = math.floor(temp_def / 2) # Penalty applies to Def too

    # --- Recalculate combat stats using potentially modified temp stats ---
    # AS (uses temp_spd, but also Con which isn't halved)
    weapon_weight = attacker.equipped_weapon.weight if attacker.equipped_weapon else 0
    # Physical weapon AS calculation using Con
    effective_weight = max(0, weapon_weight - attacker.constitution) # Con is NOT halved
    # TODO: Add check for magical weapon type later (doesn't use Con)
    temp_as = max(0, temp_spd - effective_weight)

    # Hit Rate (uses temp_skl)
    weapon_hit = attacker.equipped_weapon.hit if attacker.equipped_weapon else 0
    temp_hit_rate = max(0, weapon_hit + (2 * temp_skl) + attacker.luck) # Luck is NOT halved

    # Avoid (uses temp_as) - This attacker's avoid if they are attacked back
    # Note: This isn't directly used in hit calc, but reflects attacker's state
    # temp_avoid = max(0, (2 * temp_as) + attacker.luck) # Luck is NOT halved

    # --- Defender's Stats ---
    # Check if the DEFENDER has penalties because they are carrying someone
    defender_penalty_active = defender.is_capturing is not None
    defender_def_final = defender.defense
    defender_avoid_final = calculate_avoid(defender) # Base avoid

    if defender_penalty_active:
         defender_def_final = math.floor(defender.defense / 2)
         # Recalculate defender's avoid based on halved stats if they are carrying
         def_temp_spd = math.floor(defender.speed / 2)
         def_weapon_weight = defender.equipped_weapon.weight if defender.equipped_weapon else 0
         def_effective_weight = max(0, def_weapon_weight - defender.constitution)
         def_temp_as = max(0, def_temp_spd - def_effective_weight)
         defender_avoid_final = max(0, (2 * def_temp_as) + defender.luck)


    # --- Hit Calculation ---
    # Use attacker's temp hit rate vs defender's final avoid (potentially penalized)
    hit_chance = max(1, min(99, temp_hit_rate - defender_avoid_final))
    penalty_str = ""
    if is_capture_attempt: penalty_str += " [Capture]"
    # Show penalty if attacker is carrying OR if it's a capture attempt
    if capture_penalty_active: penalty_str += " [Penalty]"
    if defender_penalty_active: penalty_str += f" [vs Carry Penalty]"

    print(f"  {attacker.name} attacks {defender.name} (Hit%: {hit_chance}){penalty_str}")

    roll = random.randint(1, 100)
    if roll <= hit_chance:
        # --- Damage Calculation ---
        # Use attacker's temp strength vs defender's final defense (potentially penalized)
        weapon_might = attacker.equipped_weapon.might if attacker.equipped_weapon else 0
        damage = calculate_damage(temp_str, weapon_might, defender_def_final)

        # --- DEBUG ---
        print(f"  DEBUG: {defender.name} HP before damage: {defender.hp}, Damage calculated: {damage}")
        # -----------

        # Apply damage
        defender.hp = max(0, defender.hp - damage)
        print(f"  HIT! {defender.name} takes {damage} damage. (HP: {defender.hp}/{defender.max_hp})")

        # --- Check for Capture/Death ---
        if defender.hp == 0:
            if is_capture_attempt:
                # Check capture conditions
                # Thracia: Attacker Con > Target Con OR Attacker is Mounted (vs non-mounted)
                # Target Con >= 20 or Target Mounted -> Immune
                # MVP Simplification: Attacker Con > Target Con OR Attacker is Cavalry
                can_capture = False
                is_mounted_attacker = attacker.move_type == MoveType.CAVALRY # Basic mount check
                # is_mounted_defender = defender.move_type == MoveType.CAVALRY # Add later if needed

                # TODO: Add immunity checks (Con >= 20, Mounted target)

                if attacker.constitution > defender.constitution:
                    can_capture = True
                elif is_mounted_attacker: # Add mounted capture rule (simplified)
                    can_capture = True
                    print("  (Mounted capture bonus applied)")


                if can_capture:
                    game_state.handle_unit_capture(attacker, defender)
                    # Return True immediately after successful capture to prevent counter/follow-ups
                    return True # Indicate hit landed, but also signals capture occurred
                else:
                    print(f"  Capture failed (Check: AtkCon {attacker.constitution} vs TgtCon {defender.constitution}, AtkMounted {is_mounted_attacker}). {defender.name} is defeated.")
                    game_state.handle_unit_death(defender) # Treat as death if capture fails
            else:
                # Normal death
                game_state.handle_unit_death(defender)
        return True # Hit landed
    else:
        print(f"  MISS!")
        return False # Attack missed

# --- Main Combat Simulation (Updated) ---

def simulate_combat(
    attacker: Unit,
    defender: Unit,
    game_state: GameState,
    is_capture_attempt: bool = False # Add flag
):
    """Simulates a full round of combat between two units."""
    print(f"\n--- Combat: {attacker.name} vs {defender.name}{' (Capture Attempt)' if is_capture_attempt else ''} ---")

    if not attacker.equipped_weapon:
        print(f"  {attacker.name} cannot attack (no weapon equipped).")
        print(f"--- Combat End ---")
        return

    attacker_penalty = is_capture_attempt or (attacker.is_capturing is not None)
    defender_penalty = defender.is_capturing is not None

    # 1. Attacker's first strike
    hit_landed = resolve_attack(attacker, defender, game_state, is_capture_attempt, attacker_penalty)

    # Check if target was captured OR defeated by the first hit
    if defender.is_captured or not defender.is_alive:
        print(f"--- Combat End ---")
        return # End combat immediately

    # 2. Defender's counter-attack (if alive and in range)
    # Check aliveness *after* attacker's first strike AND capture check
    if defender.equipped_weapon: # Check weapon first
        dist_x = abs(attacker.position[0] - defender.position[0])
        dist_y = abs(attacker.position[1] - defender.position[1])
        distance = dist_x + dist_y
        weapon = defender.equipped_weapon
        if weapon.range_min <= distance <= weapon.range_max:
            # Check attacker aliveness again before counter
            if attacker.is_alive:
                print(f"  {defender.name} counters!")
                resolve_attack(defender, attacker, game_state, False, defender_penalty)
                # Check if attacker was defeated by counter
                if not attacker.is_alive:
                    print(f"--- Combat End ---")
                    return # End if attacker defeated
            # else: attacker already defeated, no counter possible
        # else: out of range for counter

    # 3. Attacker's follow-up attack (if doubling and both are alive)
    can_double = does_double(attacker, defender)
    # Check aliveness *after* potential counter-attack
    if attacker.is_alive and defender.is_alive and can_double:
        if is_capture_attempt:
             print(f"  (Doubling prevented during capture attempt)")
        else:
            print(f"  {attacker.name} performs a follow-up attack!")
            followup_attacker_penalty = attacker.is_capturing is not None
            resolve_attack(attacker, defender, game_state, False, followup_attacker_penalty)
            # Check if defender defeated by follow-up
            if not defender.is_alive:
                 print(f"--- Combat End ---")
                 return

    # 4. Defender's follow-up attack (Rare)
    can_defender_double = does_double(defender, attacker)
    # Check aliveness *after* potential attacker follow-up
    if defender.is_alive and attacker.is_alive and can_defender_double:
        if is_capture_attempt:
            pass
        else:
            print(f"  {defender.name} performs a follow-up counter-attack!")
            resolve_attack(defender, attacker, game_state, False, defender_penalty)
            # No need to check attacker death again, as combat ends after this sequence anyway

    print(f"--- Combat End ---")