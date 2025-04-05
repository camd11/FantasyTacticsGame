# src/game/staff_actions.py

import random
from typing import Optional, Tuple
from .models import Unit, Weapon, Faction, StatusEffect, Item # Import necessary models

# --- Staff Command Helper Functions ---

def _validate_staff_target(caster: Unit, target_unit: Optional[Unit], target_pos: Tuple[int, int], required_faction: Optional[Faction] = None, allow_no_status: bool = False) -> bool:
    """Validates a potential staff target."""
    if not target_unit:
        print(f"No unit at ({target_pos[0]}, {target_pos[1]}).")
        return False
    if not target_unit.is_alive or target_unit.is_captured:
        print(f"Cannot target defeated or captured unit {target_unit.name}.")
        return False
    if required_faction is not None and target_unit.faction != required_faction:
        print(f"Cannot target non-{required_faction.value} unit {target_unit.name}.")
        return False
    # Specific check for Restore staff needing a status effect
    if not allow_no_status and required_faction == caster.faction and target_unit.status_effect == StatusEffect.NONE:
         # Check if the staff being used is Restore before printing the "no status" message
         equipped_staff = caster.equipped_weapon
         if equipped_staff and equipped_staff.name.lower() == "restore staff":
              print(f"{target_unit.name} has no status condition to restore.")
              return False
    return True

def _apply_staff_costs(caster: Unit, equipped_staff: Weapon, game_state): # game_state needed for remove_item
    """Applies WExp, Fatigue, and Use consumption after successful staff use."""
    # --- Grant Staff WExp ---
    from .models import WEXP_THRESHOLDS, WEAPON_RANKS, FATIGUE_COST_STAFF # Import constants locally
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
        # Consider if action should still complete or not

def _handle_heal_staff(caster: Unit, target_unit: Unit, equipped_staff: Weapon) -> bool:
    """Handles the logic for Heal and Mend staves."""
    if target_unit.hp >= target_unit.max_hp:
        print(f"{target_unit.name} is already at full HP.")
        return False # Indicate staff effect did not apply

    # Calculate Heal Amount (Example: Heal=10+Mag, Mend=20+Mag)
    # TODO: Differentiate between Heal/Mend based on name or add specific classes
    heal_base = 10 # Default for Heal
    if equipped_staff.name.lower() == "mend staff":
        heal_base = 20
    heal_amount = heal_base + caster.magic
    actual_healed = min(heal_amount, target_unit.max_hp - target_unit.hp)
    target_unit.hp += actual_healed
    print(f"{caster.name} used {equipped_staff.name} on {target_unit.name}, recovering {actual_healed} HP. (HP: {target_unit.hp}/{target_unit.max_hp})")
    return True # Indicate staff effect applied

def _handle_restore_staff(caster: Unit, target_unit: Unit, equipped_staff: Weapon) -> bool:
    """Handles the logic for the Restore staff."""
    # Validation for status already done by _validate_staff_target
    old_status = target_unit.status_effect
    target_unit.status_effect = StatusEffect.NONE
    print(f"{caster.name} used {equipped_staff.name} on {target_unit.name}, curing {old_status.value}.") # Use .value for enum display
    return True # Indicate staff effect applied

def _handle_status_staff(caster: Unit, target_unit: Unit, equipped_staff: Weapon, staff_name: str) -> bool:
    """Handles the logic for status-inflicting staves (Sleep, Silence, Berserk)."""
    # TODO: Add check for status immunity later (e.g., Nihil or specific bosses)

    # Calculate Staff Hit Chance (Base 60 + 4*Skill, capped 1-99)
    base_hit = 60 # Base for most status staves
    staff_hit_chance = min(99, max(1, base_hit + (4 * caster.skill)))
    print(f"  (Staff Hit Chance: {staff_hit_chance}%)")

    # Roll for hit
    hit_roll = random.randint(1, 100)
    print(f"  (Hit Roll: {hit_roll})")

    if hit_roll <= staff_hit_chance:
        # Determine status to apply
        status_to_apply = StatusEffect.NONE
        if staff_name == "sleep staff":
            status_to_apply = StatusEffect.SLEEP
        elif staff_name == "silence staff":
            status_to_apply = StatusEffect.SILENCE
        elif staff_name == "berserk staff":
            status_to_apply = StatusEffect.BERSERK

        if status_to_apply != StatusEffect.NONE:
            target_unit.status_effect = status_to_apply
            print(f"  Success! {target_unit.name} is now afflicted with {status_to_apply.value}.")
        else:
            print(f"  Error: Could not determine status for {staff_name}.") # Should not happen
    else:
        print(f"  Miss! {equipped_staff.name} failed to affect {target_unit.name}.")

    # Costs/Fatigue/WExp apply even on miss for status staves
    return True # Indicate staff was used (even if missed)

def _handle_repair_staff(caster: Unit, target_unit: Unit, equipped_staff: Weapon, item_index_to_repair: int) -> bool:
    """Handles the logic for the Repair staff."""
    if not target_unit: # Should be validated already, but double-check
        print("Invalid target for Repair Staff.")
        return False

    # Validate item index
    if not (0 <= item_index_to_repair < len(target_unit.inventory)):
        print(f"Invalid item index {item_index_to_repair} for {target_unit.name}'s inventory.")
        return False

    item_to_repair = target_unit.inventory[item_index_to_repair]

    # Check if the item is repairable (has uses and max_uses, and is not already full)
    if not hasattr(item_to_repair, 'uses') or not hasattr(item_to_repair, 'max_uses') or \
       item_to_repair.uses is None or item_to_repair.max_uses is None:
        print(f"Cannot repair '{item_to_repair.name}' - it does not have durability.")
        return False

    if item_to_repair.uses >= item_to_repair.max_uses:
        print(f"'{item_to_repair.name}' is already at maximum uses ({item_to_repair.max_uses}/{item_to_repair.max_uses}).")
        return False

    # Perform the repair
    old_uses = item_to_repair.uses
    item_to_repair.uses = item_to_repair.max_uses
    print(f"{caster.name} used {equipped_staff.name} on {target_unit.name}'s {item_to_repair.name}.")
    print(f"  Restored uses from {old_uses} to {item_to_repair.max_uses}.")

    return True # Indicate staff effect applied successfully