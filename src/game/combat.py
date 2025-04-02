# src/game/combat.py (Corrected Indentation & Status Effects)

import random
import math # Need math for floor/ceil if halving stats
from typing import Optional, Tuple
from .models import (Unit, GameState, Weapon, MoveType, FATIGUE_COST_COMBAT, # Existing
                      TERRAIN_PROPERTIES, TerrainType, # Terrain
                      WEAPON_TRIANGLE_BONUS, PHYSICAL_TRIANGLE, ANIMA_TRIANGLE, # Triangle
                      ANIMA_TYPES, LIGHT_DARK_TYPES, Faction, StatusEffect, # Triangle helpers, ADDED Faction, StatusEffect
                      SUPPORTS, CHARISMA_SKILL_NAME) # NEW: Import support data and charisma skill name

# --- Bonus Calculation Helpers ---

def get_distance(unit1: Unit, unit2: Unit) -> int:
    """Calculates Manhattan distance between two units."""
    return abs(unit1.position[0] - unit2.position[0]) + abs(unit1.position[1] - unit2.position[1])

def calculate_support_bonus(unit: Unit, game_state: GameState) -> Tuple[int, int, int, int]:
    """Calculates total support bonus (Hit, Avo, Crit, CritEvade) for a unit."""
    # Thracia: Supports are within 3 tiles, stack up to +30 total.
    total_bonus = 0
    receiver_name = unit.name
    for other_unit in game_state.units.values():
        if other_unit.id == unit.id or not other_unit.is_alive or other_unit.faction != unit.faction:
            continue # Skip self, dead units, or different factions

        giver_name = other_unit.name
        if giver_name in SUPPORTS and receiver_name in SUPPORTS[giver_name]:
            distance = get_distance(unit, other_unit)
            if distance <= 3:
                bonus = SUPPORTS[giver_name][receiver_name]
                total_bonus += bonus
                # print(f"  DEBUG: {unit.name} receives +{bonus} support from {giver_name} (Dist: {distance})") # Debug

    # Cap bonus at +30
    capped_bonus = min(total_bonus, 30)
    # Thracia: Support bonus applies equally to Hit, Avo, Crit, CritEvade
    return capped_bonus, capped_bonus, capped_bonus, capped_bonus

def calculate_leadership_bonus(unit: Unit, game_state: GameState) -> Tuple[int, int]:
    """Calculates total leadership bonus (Hit, Avo) for a unit."""
    # Thracia: Leadership stars * 3, global bonus from all leaders of the same faction.
    total_stars = 0
    for leader_unit in game_state.units.values():
        if leader_unit.faction == unit.faction and leader_unit.is_alive and leader_unit.leadership_stars > 0:
            total_stars += leader_unit.leadership_stars

    bonus = total_stars * 3
    # print(f"  DEBUG: {unit.name} receives +{bonus} leadership bonus (Total Stars: {total_stars})") # Debug
    # Leadership applies to Hit and Avoid
    return bonus, bonus

def calculate_charisma_bonus(unit: Unit, game_state: GameState) -> Tuple[int, int]:
    """Calculates total charisma bonus (Hit, Avo) for a unit."""
    # Thracia: +10 Hit/Avo for each ally with Charisma within 3 tiles. Stacks.
    total_bonus = 0
    for char_unit in game_state.units.values():
        if char_unit.id == unit.id or not char_unit.is_alive or char_unit.faction != unit.faction:
            continue

        if CHARISMA_SKILL_NAME in char_unit.skills:
            distance = get_distance(unit, char_unit)
            if distance <= 3:
                total_bonus += 10
                # print(f"  DEBUG: {unit.name} receives +10 charisma bonus from {char_unit.name} (Dist: {distance})") # Debug

    # Charisma applies to Hit and Avoid
    return total_bonus, total_bonus

# --- Combat Calculation Helpers ---
def calculate_attack_speed(unit: Unit, game_state: GameState) -> int: # Add game_state
    """Calculates Attack Speed (AS)."""
    # Thracia: AS = Speed – max( (Weapon Weight – Con), 0 ) for physical
    # Thracia: AS = Speed – Weapon Weight for magic
    if not unit.equipped_weapon or not unit.is_alive: # Check if alive
        return unit.speed # No weapon or dead, AS is just Speed
    if unit.status_effect == StatusEffect.SLEEP:
        return 0 # Sleeping units have 0 effective speed

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
    """Calculates Hit Rate including bonuses."""
    # Thracia: Hit = Weapon Hit + (2 * Skill) + Luck + Support + Leadership + Charisma + WTriangle
    if not unit.is_alive: return 0
    if unit.status_effect == StatusEffect.SLEEP:
        return 0 # Sleeping units have 0 effective skill/luck for hit calc

    weapon_hit = unit.equipped_weapon.hit if unit.equipped_weapon else 0
    base_hit = max(0, weapon_hit + (2 * unit.skill) + unit.luck)

    # Calculate bonuses
    support_hit, _, _, _ = calculate_support_bonus(unit, game_state)
    leadership_hit, _ = calculate_leadership_bonus(unit, game_state)
    charisma_hit, _ = calculate_charisma_bonus(unit, game_state)

    # Add bonuses
    total_hit = base_hit + support_hit + leadership_hit + charisma_hit
    return max(0, total_hit) # Ensure final hit isn't negative

def calculate_avoid(unit: Unit, game_state: GameState) -> int: # Add game_state
    """Calculates Avoid Rate including bonuses and terrain."""
    # Thracia: Avoid = (2 * Attack Speed) + Luck + Support + Leadership + Charisma + Terrain
    if not unit.is_alive: return 0
    if unit.status_effect == StatusEffect.SLEEP:
        return 0 # Sleeping units have 0 avoid

    attack_speed = calculate_attack_speed(unit, game_state) # Pass game_state
    base_avoid = max(0, (2 * attack_speed) + unit.luck)

    # Calculate bonuses
    _, support_avo, _, _ = calculate_support_bonus(unit, game_state)
    _, leadership_avo = calculate_leadership_bonus(unit, game_state)
    _, charisma_avo = calculate_charisma_bonus(unit, game_state)

    # Calculate terrain bonus (skip for Flying)
    terrain_avo_bonus = 0
    if unit.move_type != MoveType.FLYING:
        tile = game_state.game_map.get_tile(unit.position[0], unit.position[1])
        if tile:
            terrain_props = TERRAIN_PROPERTIES.get(tile.terrain_type, {})
            terrain_avo_bonus = terrain_props.get('avo', 0)

    # Add bonuses
    total_avoid = base_avoid + support_avo + leadership_avo + charisma_avo + terrain_avo_bonus
    return max(0, total_avoid) # Ensure final avoid isn't negative

def calculate_damage(
    attacker_stat: int, # Can be Str or Mag
    attacker_weapon_might: int,
    defender_resistance_stat: int, # Can be Def or Mag
    is_magical_attack: bool # Flag to determine which stats to use
) -> int:
    """Calculates damage dealt using provided stats, considering physical/magical."""
    attack_power = attacker_stat + attacker_weapon_might
    defense_power = defender_resistance_stat
    return max(0, attack_power - defense_power)

def calculate_crit_rate(unit: Unit, game_state: GameState) -> int: # Add game_state
    """Calculates base Critical Rate including support bonus."""
    # Thracia: Crit = Weapon Crit + Skill + Support bonus
    if not unit.is_alive: return 0
    if unit.status_effect == StatusEffect.SLEEP: return 0 # No crits while sleeping

    weapon_crit = unit.equipped_weapon.crit if unit.equipped_weapon else 0
    base_crit = max(0, weapon_crit + unit.skill)

    # Calculate support bonus
    _, _, support_crit, _ = calculate_support_bonus(unit, game_state)

    total_crit = base_crit + support_crit
    return max(0, total_crit)

def calculate_crit_evade(unit: Unit, game_state: GameState) -> int: # Add game_state
    """Calculates Critical Evade (Dodge) including support bonus."""
    # Thracia: Crit Evade = (Luck / 2) + support bonus
    if not unit.is_alive: return 0
    if unit.status_effect == StatusEffect.SLEEP: return 0 # No crit evade while sleeping

    base_crit_evade = max(0, unit.luck // 2)

    # Calculate support bonus
    _, _, _, support_crit_evade = calculate_support_bonus(unit, game_state)

    total_crit_evade = base_crit_evade + support_crit_evade
    return max(0, total_crit_evade)

def does_double(attacker: Unit, defender: Unit, game_state: GameState) -> bool: # Add game_state
    """Checks if the attacker doubles the defender (using base stats)."""
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
    is_follow_up: bool = False, # NEW: Flag for PCC calculation
    is_counter_attack: bool = False # NEW: Flag for Wrath check
) -> Tuple[bool, bool]: # Return (hit_landed, was_critical)
    """Resolves a single attack instance (hit check, damage application)."""
    # --- Pre-computation & Checks ---
    if not attacker.is_alive or not defender.is_alive:
        return False, False # Hit didn't land, wasn't critical

    # Apply capture penalties temporarily if needed for *this* attack
    temp_str = attacker.strength
    temp_str = attacker.strength
    temp_mag = attacker.magic # Get base magic
    temp_skl = attacker.skill
    temp_spd = attacker.speed
    temp_def = attacker.defense # Base defense before status/penalty

    # Apply Attacker Status Effects (Sleep/Berserk sets Str, Mag, Skl, Spd, Def to 0)
    if attacker.status_effect in [StatusEffect.SLEEP, StatusEffect.BERSERK]:
        print(f"  DEBUG: {attacker.name} is {attacker.status_effect}, combat stats set to 0.") # Debug
        temp_str = 0
        temp_mag = 0
        temp_skl = 0
        temp_spd = 0
        temp_def = 0

    # Thracia: Str, Mag, Skl, Spd, Def halved (floor?) during capture attempt/carry
    if capture_penalty_active:
        temp_str = math.floor(temp_str / 2)
        # temp_mag = math.floor(attacker.magic / 2) # Add later
        temp_skl = math.floor(temp_skl / 2)
        temp_spd = math.floor(temp_spd / 2)
        # Apply penalty AFTER status effect check
        temp_def = math.floor(temp_def / 2) # Penalty applies to Def too

    # --- Recalculate combat stats using potentially modified temp stats ---
    # AS (uses temp_spd, but also Con which isn't halved)
    weapon_weight = attacker.equipped_weapon.weight if attacker.equipped_weapon else 0
    effective_weight = 0
    if attacker.equipped_weapon:
        if attacker.equipped_weapon.damage_type == "Magical":
             effective_weight = weapon_weight
        else:
             effective_weight = max(0, weapon_weight - attacker.constitution) # Con is NOT halved
    temp_as = max(0, temp_spd - effective_weight)

    # Hit Rate (uses temp_skl) - Base calculation before bonuses/Miracle/Triangle
    # Note: calculate_hit_rate already includes bonuses, but we need the base here
    # to apply triangle/miracle correctly before capping.
    weapon_hit = attacker.equipped_weapon.hit if attacker.equipped_weapon else 0
    attacker_stat_hit = max(0, weapon_hit + (2 * temp_skl) + attacker.luck) # Luck is NOT halved

    # Calculate attacker bonuses separately for clarity in final hit calc
    attacker_support_hit, _, _, _ = calculate_support_bonus(attacker, game_state)
    attacker_leadership_hit, _ = calculate_leadership_bonus(attacker, game_state)
    attacker_charisma_hit, _ = calculate_charisma_bonus(attacker, game_state)
    attacker_total_bonus_hit = attacker_support_hit + attacker_leadership_hit + attacker_charisma_hit

    # --- Defender's Stats ---
    defender_penalty_active = defender.is_capturing is not None
    defender_def_base = defender.defense # Base defense before status/terrain/penalty
    # Defender Avoid (Base calculation before bonuses/penalty/status)
    # Note: calculate_avoid includes bonuses, but we need the base here for final calc
    defender_as_for_avoid = calculate_attack_speed(defender, game_state) # Use current AS
    defender_stat_avoid = max(0, (2 * defender_as_for_avoid) + defender.luck)

    # Calculate defender bonuses separately
    _, defender_support_avo, _, _ = calculate_support_bonus(defender, game_state)
    _, defender_leadership_avo = calculate_leadership_bonus(defender, game_state)
    _, defender_charisma_avo = calculate_charisma_bonus(defender, game_state)
    defender_total_bonus_avoid = defender_support_avo + defender_leadership_avo + defender_charisma_avo

    # Apply Defender Status Effects (Sleep/Berserk affects Def, Mag, Avoid)
    defender_magic_base = defender.magic # Get base magic before status
    if defender.status_effect in [StatusEffect.SLEEP, StatusEffect.BERSERK]:
        print(f"  DEBUG: {defender.name} is {defender.status_effect}, defensive stats set to 0.") # Debug
        defender_def_base = 0
        defender_magic_base = 0 # Magic (resistance) also becomes 0
        defender_stat_avoid = 0 # Base avoid from stats becomes 0
        defender_total_bonus_avoid = 0 # Bonuses also negated while status'd

    defender_def_final = defender_def_base # Start with potentially status-modified defense

    # Get defender terrain bonus (skip for Flying)
    defender_terrain_def_bonus = 0
    if defender.move_type != MoveType.FLYING:
        def_tile = game_state.game_map.get_tile(defender.position[0], defender.position[1])
        if def_tile:
            def_terrain_props = TERRAIN_PROPERTIES.get(def_tile.terrain_type, {})
            defender_terrain_def_bonus = def_terrain_props.get('def', 0)
            defender_def_final += defender_terrain_def_bonus # Add terrain def bonus

    if defender_penalty_active:
         # Apply penalty AFTER terrain bonus has been added
         defender_def_final = math.floor(defender_def_final / 2)
         # Recalculate defender's avoid based on halved stats if they are carrying
         def_temp_spd = math.floor(defender.speed / 2)
         def_weapon_weight = defender.equipped_weapon.weight if defender.equipped_weapon else 0
         def_effective_weight = max(0, def_weapon_weight - defender.constitution)
         def_temp_as = max(0, def_temp_spd - def_effective_weight)
         # Recalculate avoid using penalized AS
         defender_stat_avoid = max(0, (2 * def_temp_as) + defender.luck) # Recalculate base avoid from stats
         # Bonuses are NOT halved when carrying, only base stats
         # Note: Terrain avoid bonus is added later in the final hit chance calculation

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
    # --- Final Hit Calculation (incorporating all bonuses) ---
    # Start with attacker's base hit from stats + weapon
    final_hit_rate = attacker_stat_hit
    # Add attacker's bonuses
    final_hit_rate += attacker_total_bonus_hit
    # Add weapon triangle bonus
    final_hit_rate += triangle_bonus

    # Subtract defender's base avoid from stats (potentially penalized/status)
    final_hit_rate -= defender_stat_avoid
    # Subtract defender's bonuses (not penalized when carrying)
    final_hit_rate -= defender_total_bonus_avoid

    # Subtract defender terrain avoid bonus
    defender_terrain_avo_bonus = 0
    # Sleeping units don't benefit from terrain avoid
    if defender.move_type != MoveType.FLYING and defender.status_effect != StatusEffect.SLEEP:
        def_tile = game_state.game_map.get_tile(defender.position[0], defender.position[1])
        if def_tile:
            def_terrain_props = TERRAIN_PROPERTIES.get(def_tile.terrain_type, {})
            defender_terrain_avo_bonus = def_terrain_props.get('avo', 0)
    final_hit_rate -= defender_terrain_avo_bonus

    # --- Miracle Check (Defender) ---
    if "Miracle" in defender.skills and defender.hp <= 10:
        print(f"  ({defender.name}'s Miracle activates!)")
        hit_chance = 1 # Force hit to minimum
    else:
        hit_chance = max(1, min(99, final_hit_rate))

    # --- Display Hit Chance ---
    penalty_str = ""
    if is_capture_attempt: penalty_str += " [Capture]"
    if capture_penalty_active: penalty_str += " [Penalty]"
    if defender_penalty_active: penalty_str += f" [vs Carry Penalty]"
    if defender.status_effect == StatusEffect.SLEEP: penalty_str += " [vs Sleep]"

    print(f"  {attacker.name} attacks {defender.name} (Hit%: {hit_chance}){penalty_str}")

    # --- Hit Roll ---
    roll = random.randint(1, 100)
    if roll <= hit_chance:
        # --- Critical Hit Calculation ---
        is_critical = False # Initialize before checks
        # Check for Wrath first (triggers on counter-attack OR any attack during enemy phase)
        is_enemy_phase = game_state.active_faction == Faction.ENEMY
        if ("Wrath" in attacker.skills) and (is_counter_attack or is_enemy_phase):
            print(f"  ({attacker.name}'s Wrath activates!)")
            is_critical = True # Wrath guarantees crit
        else:
            # Normal critical calculation
            # Use the full calculation functions which include support bonuses
            attacker_crit_rate_with_bonus = calculate_crit_rate(attacker, game_state)
            defender_crit_evade_with_bonus = calculate_crit_evade(defender, game_state)
            battle_crit_chance = max(0, attacker_crit_rate_with_bonus - defender_crit_evade_with_bonus)

            # Apply PCC and 25% cap
            if is_follow_up:
                battle_crit_chance = min(100, battle_crit_chance * attacker.pcc)
            else:
                battle_crit_chance = min(25, battle_crit_chance)

            # Roll for critical
            crit_roll = random.randint(1, 100)
            is_critical = crit_roll <= battle_crit_chance # Check if normal crit roll succeeds

        # --- Nihil Check (Defender) ---
        if "Nihil" in defender.skills and is_critical:
            print(f"  ({defender.name}'s Nihil negates the critical!)")
            is_critical = False # Override critical if defender has Nihil

        # --- Damage Calculation ---
        weapon = attacker.equipped_weapon
        weapon_might = weapon.might if weapon else 0
        is_magical = weapon and weapon.damage_type == "Magical"

        # Check for Silence on magical attacks
        if is_magical and attacker.status_effect == StatusEffect.SILENCE:
            print(f"  ({attacker.name} is Silenced and cannot use magic!)")
            return False, False # Attack fails automatically

        # --- Weapon Effectiveness Check ---
        effective_bonus = 1
        if weapon and defender.move_type in weapon.effective_against:
            effective_bonus = 3 # Thracia uses 3x Might multiplier
            print(f"  ({weapon.name} is effective against {defender.move_type}!)")
        weapon_might *= effective_bonus # Apply multiplier to might before damage calc

        # Select attacker stat (Str/Mag) - Use temp stats if penalized
        attacker_offensive_stat = temp_str # Default to temp_str
        if is_magical:
            temp_mag = attacker.magic
            if capture_penalty_active: # Check if attacker has penalty
                temp_mag = math.floor(attacker.magic / 2)
            attacker_offensive_stat = temp_mag

        # Select defender resistance stat (Def/Mag) - Use potentially status-modified stats
        defender_resistance_stat = defender_def_final # Default to final physical defense (already includes status effect if applicable)
        if is_magical:
            # Use magic_base which includes status effect if applicable
            defender_resistance_stat = defender_magic_base

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
                can_capture = False
                is_mounted_attacker = attacker.move_type == MoveType.CAVALRY
                is_mounted_defender = defender.move_type == MoveType.CAVALRY

                # --- Immunity Checks (Thracia Rules) ---
                is_immune = False
                if defender.constitution >= 20:
                    print(f"  Capture Immune: Target Con ({defender.constitution}) >= 20.")
                    is_immune = True
                elif is_mounted_defender:
                    print(f"  Capture Immune: Target is mounted.")
                    is_immune = True

                # --- Capture Condition Checks (Only if not immune) ---
                if not is_immune:
                    if attacker.constitution > defender.constitution:
                        can_capture = True
                    elif is_mounted_attacker and not is_mounted_defender:
                        can_capture = True
                        print("  (Mounted capture bonus applied vs non-mounted target)")

                # --- Resolve Capture/Death ---
                if can_capture and not is_immune:
                    game_state.handle_unit_capture(attacker, defender)
                    return True, False # Hit landed, wasn't critical (capture overrides)
                else:
                    print(f"  Capture failed (Check: AtkCon {attacker.constitution} vs TgtCon {defender.constitution}, AtkMounted {is_mounted_attacker}). {defender.name} is defeated.")
                    game_state.handle_unit_death(defender) # Treat as death if capture fails
            else:
                # Normal death
                game_state.handle_unit_death(defender)
        # Return hit status and whether it was critical
        return True, is_critical
    else:
        print(f"  MISS!")
        return False, False # Attack missed, wasn't critical

# --- Main Combat Simulation (Updated) ---

def simulate_combat(
    attacker: Unit,
    defender: Unit,
    game_state: GameState,
    is_capture_attempt: bool = False # Add flag
):
    """Simulates a full round of combat between two units."""
    print(f"\n--- Combat: {attacker.name} vs {defender.name}{' (Capture Attempt)' if is_capture_attempt else ''} ---")

    # Check initial status effects preventing action
    if attacker.status_effect == StatusEffect.SLEEP:
        print(f"  {attacker.name} cannot attack (Sleeping).")
        print(f"--- Combat End ---")
        return
    if attacker.status_effect == StatusEffect.BERSERK:
        print(f"  {attacker.name} cannot be controlled (Berserk).") # AI handles berserk actions
        print(f"--- Combat End ---")
        return

    if not attacker.equipped_weapon:
        print(f"  {attacker.name} cannot attack (no weapon equipped).")
        print(f"--- Combat End ---")
        return

    attacker_penalty = is_capture_attempt or (attacker.is_capturing is not None)
    defender_penalty = defender.is_capturing is not None

    # 1. Attacker's first strike
    attacker.fatigue += FATIGUE_COST_COMBAT
    print(f"  (+{FATIGUE_COST_COMBAT} Fatigue for {attacker.name}. Total: {attacker.fatigue})")
    hit_landed, _ = resolve_attack(attacker, defender, game_state, is_capture_attempt, attacker_penalty, is_follow_up=False, is_counter_attack=False) # Get hit status

    # --- Adept Check (Attacker) ---
    if hit_landed and attacker.is_alive and defender.is_alive and not is_capture_attempt and "Adept" in attacker.skills:
        adept_chance = attacker.skill # Thracia Adept chance = Skill%
        adept_roll = random.randint(1, 100)
        print(f"  (Adept Check: Roll {adept_roll} vs Chance {adept_chance})") # Debug
        if adept_roll <= adept_chance:
            print(f"  ({attacker.name}'s Adept activates!)")
            attacker.fatigue += FATIGUE_COST_COMBAT # Fatigue for extra attack
            print(f"  (+{FATIGUE_COST_COMBAT} Fatigue for {attacker.name}. Total: {attacker.fatigue})")
            resolve_attack(attacker, defender, game_state, False, attacker_penalty, is_follow_up=True, is_counter_attack=False)
            if not defender.is_alive:
                print(f"--- Combat End ---")
                return # End combat if Adept killed
    # -----------------------------

    # Check if target was captured OR defeated by the first hit or Adept
    if defender.is_captured or not defender.is_alive:
        print(f"--- Combat End ---")
        return # End combat immediately

    # 2. Defender's counter-attack (if alive and in range)
    if defender.equipped_weapon: # Check weapon first
        # Check if defender can counter (not asleep/berserk)
        if defender.status_effect == StatusEffect.SLEEP:
            print(f"  {defender.name} cannot counter (Sleeping).")
        elif defender.status_effect == StatusEffect.BERSERK:
             print(f"  {defender.name} cannot counter (Berserk).") # Or AI would handle
        else:
            dist_x = abs(attacker.position[0] - defender.position[0])
            dist_y = abs(attacker.position[1] - defender.position[1])
            distance = dist_x + dist_y
            weapon = defender.equipped_weapon
            if weapon.range_min <= distance <= weapon.range_max:
                # Check attacker aliveness again before counter
                if attacker.is_alive:
                    print(f"  {defender.name} counters!")
                    defender.fatigue += FATIGUE_COST_COMBAT
                    print(f"  (+{FATIGUE_COST_COMBAT} Fatigue for {defender.name}. Total: {defender.fatigue})")
                    resolve_attack(defender, attacker, game_state, False, defender_penalty, is_follow_up=False, is_counter_attack=True) # Resolve counter
                    if not attacker.is_alive:
                        print(f"--- Combat End ---")
                        return # End if attacker defeated
                # else: attacker already defeated, no counter possible
            # else: out of range for counter
    # else: defender has no weapon or cannot counter due to status

    # 3. Attacker's follow-up attack (if doubling and both are alive)
    can_double = does_double(attacker, defender, game_state) # Pass game_state
    if attacker.is_alive and defender.is_alive and can_double:
        if is_capture_attempt:
             print(f"  (Doubling prevented during capture attempt)")
        else:
            print(f"  {attacker.name} performs a follow-up attack!")
            attacker.fatigue += FATIGUE_COST_COMBAT
            print(f"  (+{FATIGUE_COST_COMBAT} Fatigue for {attacker.name}. Total: {attacker.fatigue})")
            followup_attacker_penalty = attacker.is_capturing is not None # Check penalty again
            resolve_attack(attacker, defender, game_state, False, followup_attacker_penalty, is_follow_up=True, is_counter_attack=False) # Resolve follow-up
            if not defender.is_alive:
                 print(f"--- Combat End ---")
                 return

    # 4. Defender's follow-up attack (Rare)
    can_defender_double = does_double(defender, attacker, game_state) # Pass game_state
    if defender.is_alive and attacker.is_alive and can_defender_double:
        if is_capture_attempt:
            pass
        else:
            print(f"  {defender.name} performs a follow-up counter-attack!")
            defender.fatigue += FATIGUE_COST_COMBAT
            print(f"  (+{FATIGUE_COST_COMBAT} Fatigue for {defender.name}. Total: {defender.fatigue})")
            resolve_attack(defender, attacker, game_state, False, defender_penalty, is_follow_up=True, is_counter_attack=True) # Resolve defender follow-up
            # No need to check attacker death again, as combat ends after this sequence anyway

    print(f"--- Combat End ---")