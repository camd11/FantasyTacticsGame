# src/game/combat.py (Updated)

import random
import math # Need math for floor/ceil if halving stats
from typing import Optional, Tuple
from .models import (Unit, GameState, Weapon, MoveType, FATIGUE_COST_COMBAT, # Existing
                      TERRAIN_PROPERTIES, TerrainType, # Terrain
                      WEAPON_TRIANGLE_BONUS, PHYSICAL_TRIANGLE, ANIMA_TRIANGLE, # Triangle
                      ANIMA_TYPES, LIGHT_DARK_TYPES) # Triangle helpers

# --- Combat Calculation Helpers ---

def calculate_attack_speed(unit: Unit, game_state: GameState) -> int: # Add game_state
    """Calculates Attack Speed (AS)."""
    # Thracia: AS = Speed – max( (Weapon Weight – Con), 0 ) for physical
    # Thracia: AS = Speed – Weapon Weight for magic
    # MVP Implementation: Include Con for physical, ignore magic distinction for now.
    if not unit.equipped_weapon or not unit.is_alive: # Check if alive
        return unit.speed # No weapon or dead, AS is just Speed

    weapon = unit.equipped_weapon
    weapon_weight = weapon.weight

    # Check weapon damage type for AS calculation
    if weapon.damage_type == "Magical":
        # Thracia: Magic AS = Speed - Weapon Weight (Con does not apply)
        effective_weight = weapon_weight
    else:
        # Physical AS = Speed - max(0, Weapon Weight - Con)
        effective_weight = max(0, weapon_weight - unit.constitution) # Con is NOT halved

    attack_speed = unit.speed - effective_weight

    # Ensure AS doesn't go below 0
    return max(0, attack_speed)

def calculate_hit_rate(unit: Unit, game_state: GameState) -> int: # Add game_state
    """Calculates Hit Rate. Simplified: Weapon Hit + (2 * Skill) + Luck."""
    # Thracia: Hit = Weapon Hit + (2 * Skill) + Luck + Support + Leadership + Charisma + WTriangle
    # MVP Simplification: Ignore Support, Leadership, Charisma, WTriangle
    if not unit.is_alive: return 0
    weapon_hit = unit.equipped_weapon.hit if unit.equipped_weapon else 0
    # Ensure base hit isn't negative if stats are low
    return max(0, weapon_hit + (2 * unit.skill) + unit.luck)

def calculate_avoid(unit: Unit, game_state: GameState) -> int: # Add game_state
    """Calculates Avoid Rate. Includes terrain bonus."""
    # Thracia: Avoid = (2 * Attack Speed) + Luck + Support + Leadership + Charisma + Terrain
    # MVP Simplification: Ignore Support, Leadership, Charisma. Include Terrain.
    if not unit.is_alive: return 0

    attack_speed = calculate_attack_speed(unit, game_state) # Pass game_state
    base_avoid = max(0, (2 * attack_speed) + unit.luck)

    # Add terrain bonus (skip for Flying)
    terrain_avo_bonus = 0
    if unit.move_type != MoveType.FLYING:
        tile = game_state.game_map.get_tile(unit.position[0], unit.position[1])
        if tile:
            terrain_props = TERRAIN_PROPERTIES.get(tile.terrain_type, {})
            terrain_avo_bonus = terrain_props.get('avo', 0)

    return base_avoid + terrain_avo_bonus

def calculate_damage(
    attacker_stat: int, # Can be Str or Mag
    attacker_weapon_might: int,
    defender_resistance_stat: int, # Can be Def or Mag
    is_magical_attack: bool # Flag to determine which stats to use
) -> int:
    """Calculates damage dealt using provided stats, considering physical/magical."""
    # MVP Simplification: Ignore effectiveness, terrain DEF (handled before call), M Up.
    attack_power = attacker_stat + attacker_weapon_might
    defense_power = defender_resistance_stat
    return max(0, attack_power - defense_power)

def calculate_crit_rate(unit: Unit, game_state: GameState) -> int: # Add game_state
    """Calculates base Critical Rate. Simplified: Weapon Crit + Skill."""
    # Thracia: Crit = Weapon Crit + Skill + Support bonus - enemy Crit Evade
    # MVP Simplification: Ignore Support, enemy evade here (handled in battle calc)
    if not unit.is_alive: return 0
    weapon_crit = unit.equipped_weapon.crit if unit.equipped_weapon else 0
    # Ensure base crit isn't negative
    return max(0, weapon_crit + unit.skill)

def calculate_crit_evade(unit: Unit, game_state: GameState) -> int: # Add game_state
    """Calculates Critical Evade (Dodge). Simplified: Luck / 2."""
    # Thracia: Crit Evade = (Luck / 2) + support bonus
    # MVP Simplification: Ignore Support
    if not unit.is_alive: return 0
    # Use floor division for integer result
    return max(0, unit.luck // 2)

def does_double(attacker: Unit, defender: Unit, game_state: GameState) -> bool: # Add game_state
    """Checks if the attacker doubles the defender (using base stats)."""
    # Thracia: Double if Attacker AS >= Defender AS + 4
    if not attacker.is_alive or not defender.is_alive: return False
    attacker_as = calculate_attack_speed(attacker, game_state) # Pass game_state
    defender_as = calculate_attack_speed(defender, game_state) # Pass game_state
    return attacker_as >= defender_as + 4


def resolve_attack(
    attacker: Unit,
    defender: Unit,
    game_state: GameState,
    is_capture_attempt: bool = False,
    capture_penalty_active: bool = False, # Is the penalty applied to *this* attacker?
    is_follow_up: bool = False # NEW: Flag for PCC calculation
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
    defender_avoid_final = calculate_avoid(defender, game_state) # Pass game_state

    # Get defender terrain bonus (skip for Flying)
    defender_terrain_def_bonus = 0
    if defender.move_type != MoveType.FLYING:
        def_tile = game_state.game_map.get_tile(defender.position[0], defender.position[1])
        if def_tile:
            def_terrain_props = TERRAIN_PROPERTIES.get(def_tile.terrain_type, {})
            defender_terrain_def_bonus = def_terrain_props.get('def', 0)
            defender_def_final += defender_terrain_def_bonus # Add terrain def bonus here

    if defender_penalty_active:
         # Apply penalty AFTER terrain bonus has been added to base defense
         defender_def_final = math.floor(defender_def_final / 2)
         # Recalculate defender's avoid based on halved stats if they are carrying
         def_temp_spd = math.floor(defender.speed / 2)
         def_weapon_weight = defender.equipped_weapon.weight if defender.equipped_weapon else 0
         def_effective_weight = max(0, def_weapon_weight - defender.constitution)
         def_temp_as = max(0, def_temp_spd - def_effective_weight)
         defender_avoid_final = max(0, (2 * def_temp_as) + defender.luck)


    # --- Weapon Triangle Bonus ---
    triangle_bonus = 0
    attacker_weapon = attacker.equipped_weapon
    defender_weapon = defender.equipped_weapon
    if attacker_weapon and defender_weapon:
        atk_wtype = attacker_weapon.wtype
        def_wtype = defender_weapon.wtype

        # Physical Triangle
        if atk_wtype in PHYSICAL_TRIANGLE and def_wtype in PHYSICAL_TRIANGLE[atk_wtype]:
            if PHYSICAL_TRIANGLE[atk_wtype][def_wtype]: # Advantage
                triangle_bonus = WEAPON_TRIANGLE_BONUS
            else: # Disadvantage
                triangle_bonus = -WEAPON_TRIANGLE_BONUS
        # Anima Triangle
        elif atk_wtype in ANIMA_TRIANGLE and def_wtype in ANIMA_TRIANGLE[atk_wtype]:
            if ANIMA_TRIANGLE[atk_wtype][def_wtype]: # Advantage
                triangle_bonus = WEAPON_TRIANGLE_BONUS
            else: # Disadvantage
                triangle_bonus = -WEAPON_TRIANGLE_BONUS
        # Light/Dark vs Anima
        elif atk_wtype in LIGHT_DARK_TYPES and def_wtype in ANIMA_TYPES:
            triangle_bonus = WEAPON_TRIANGLE_BONUS # Light/Dark beats Anima
        elif atk_wtype in ANIMA_TYPES and def_wtype in LIGHT_DARK_TYPES:
            triangle_bonus = -WEAPON_TRIANGLE_BONUS # Anima loses to Light/Dark

    # --- Final Hit Calculation ---
    # Use attacker's temp hit rate vs defender's final avoid (potentially penalized) + triangle
    hit_chance = max(1, min(99, temp_hit_rate - defender_avoid_final + triangle_bonus))
    penalty_str = ""
    if is_capture_attempt: penalty_str += " [Capture]"
    # Show penalty if attacker is carrying OR if it's a capture attempt
    if capture_penalty_active: penalty_str += " [Penalty]"
    if defender_penalty_active: penalty_str += f" [vs Carry Penalty]"

    print(f"  {attacker.name} attacks {defender.name} (Hit%: {hit_chance}){penalty_str}")

    roll = random.randint(1, 100)
    if roll <= hit_chance:
        # --- Critical Hit Calculation ---
        attacker_crit_rate = calculate_crit_rate(attacker, game_state) # Pass game_state
        defender_crit_evade = calculate_crit_evade(defender, game_state) # Pass game_state
        battle_crit_chance = max(0, attacker_crit_rate - defender_crit_evade)

        # Apply PCC and 25% cap
        if is_follow_up:
            # Apply PCC multiplier on follow-up
            battle_crit_chance = min(100, battle_crit_chance * attacker.pcc)
        else:
            # Apply 25% cap on first hit
            battle_crit_chance = min(25, battle_crit_chance)

        # Roll for critical
        crit_roll = random.randint(1, 100)
        is_critical = crit_roll <= battle_crit_chance

        # --- Damage Calculation ---
        weapon = attacker.equipped_weapon
        weapon_might = weapon.might if weapon else 0
        is_magical = weapon and weapon.damage_type == "Magical"

        # --- Weapon Effectiveness Check ---
        effective_bonus = 1
        # Use defender.move_type (which is a string like "Cavalry")
        if weapon and defender.move_type in weapon.effective_against:
            effective_bonus = 3 # Thracia uses 3x Might multiplier
            print(f"  ({weapon.name} is effective against {defender.move_type}!)")
        weapon_might *= effective_bonus # Apply multiplier to might before damage calc

        # Select attacker stat (Str/Mag) - Use temp stats if penalized
        attacker_offensive_stat = temp_str # Default to temp_str
        if is_magical:
            # Need temp_mag if capture penalty applies
            temp_mag = attacker.magic
            if capture_penalty_active:
                temp_mag = math.floor(attacker.magic / 2)
            attacker_offensive_stat = temp_mag

        # Select defender resistance stat (Def/Mag) - Use final penalized def if applicable
        defender_resistance_stat = defender_def_final # Default to final penalized def
        if is_magical:
            # Thracia uses Magic stat for magic defense
            # Check if defender has penalty active (already applied to defender_def_final, need to apply to Mag too?)
            # For now, assume penalty doesn't affect Mag resistance, just use base Mag.
            # TODO: Verify if capture penalty halves Magic stat for resistance. Assuming NO for now.
            defender_resistance_stat = defender.magic

        damage = calculate_damage(
            attacker_offensive_stat,
            weapon_might,
            defender_resistance_stat,
            is_magical # Pass flag
        )

        # Apply critical damage multiplier
        crit_str = ""
        if is_critical:
            damage *= 2 # Thracia: Double final damage
            crit_str = " CRITICAL HIT!"

        # --- DEBUG ---
        print(f"  DEBUG: {defender.name} HP before damage: {defender.hp}, Damage calculated: {damage}{crit_str}")
        # -----------

        # Apply damage
        defender.hp = max(0, defender.hp - damage)
        print(f"  HIT!{crit_str} {defender.name} takes {damage} damage. (HP: {defender.hp}/{defender.max_hp})")

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
    # Increment fatigue for attacker participating
    attacker.fatigue += FATIGUE_COST_COMBAT
    print(f"  (+{FATIGUE_COST_COMBAT} Fatigue for {attacker.name}. Total: {attacker.fatigue})")
    hit_landed = resolve_attack(attacker, defender, game_state, is_capture_attempt, attacker_penalty, is_follow_up=False)

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
                # Increment fatigue for defender participating
                defender.fatigue += FATIGUE_COST_COMBAT
                print(f"  (+{FATIGUE_COST_COMBAT} Fatigue for {defender.name}. Total: {defender.fatigue})")
                resolve_attack(defender, attacker, game_state, False, defender_penalty, is_follow_up=False)
                # Check if attacker was defeated by counter
                if not attacker.is_alive:
                    print(f"--- Combat End ---")
                    return # End if attacker defeated
            # else: attacker already defeated, no counter possible
        # else: out of range for counter

    # 3. Attacker's follow-up attack (if doubling and both are alive)
    can_double = does_double(attacker, defender, game_state) # Pass game_state
    # Check aliveness *after* potential counter-attack
    if attacker.is_alive and defender.is_alive and can_double:
        if is_capture_attempt:
             print(f"  (Doubling prevented during capture attempt)")
        else:
            print(f"  {attacker.name} performs a follow-up attack!")
            # Increment fatigue for attacker participating in follow-up
            attacker.fatigue += FATIGUE_COST_COMBAT
            print(f"  (+{FATIGUE_COST_COMBAT} Fatigue for {attacker.name}. Total: {attacker.fatigue})")
            followup_attacker_penalty = attacker.is_capturing is not None
            resolve_attack(attacker, defender, game_state, False, followup_attacker_penalty, is_follow_up=True)
            # Check if defender defeated by follow-up
            if not defender.is_alive:
                 print(f"--- Combat End ---")
                 return

    # 4. Defender's follow-up attack (Rare)
    can_defender_double = does_double(defender, attacker, game_state) # Pass game_state
    # Check aliveness *after* potential attacker follow-up
    if defender.is_alive and attacker.is_alive and can_defender_double:
        if is_capture_attempt:
            pass
        else:
            print(f"  {defender.name} performs a follow-up counter-attack!")
            # Increment fatigue for defender participating in follow-up
            defender.fatigue += FATIGUE_COST_COMBAT
            print(f"  (+{FATIGUE_COST_COMBAT} Fatigue for {defender.name}. Total: {defender.fatigue})")
            resolve_attack(defender, attacker, game_state, False, defender_penalty, is_follow_up=True)
            # No need to check attacker death again, as combat ends after this sequence anyway

    print(f"--- Combat End ---")