# Specification: Unit System

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The Unit System is responsible for defining and managing the properties and states of individual units within the game. It works closely with the `GameStateManager` to access and modify dynamic unit data (like current HP, position, status, fatigue) and the `DataProvider` to retrieve static definitions (like base stats, growths, class details, skills). While actions like movement and combat are handled by other systems, the Unit System provides the foundational data and state management upon which those actions operate.

## 2. Functional Requirements

### 2.1. Unit Representation
    - Define the core attributes of a unit, aligning with the `UnitState` structure in `GameStateManager`. This includes:
        - Identifiers (ID, Name, Class ID, Faction).
        - Position.
        - Health (Current HP, Max HP).
        - Stats (Base Stats, Growths, Level, EXP).
        - Inventory (Items, Durability, Equipped Weapon).
        - Proficiency (Weapon Ranks, WExp).
        - Status (Fatigue, Status Effects).
        - Action State (has_moved, has_acted).
        - Relationships/Bonuses (Supports, Leadership, PCC).
        - Capture/Rescue State.
        - Overall Disposition (Active, Dead, etc.).

### 2.2. Unit Initialization (Deployment)
    - Relies on `GameStateManager` and `DataProvider` to create `UnitState` instances during chapter initialization based on placement data.
    - Ensures units start with correct base stats, level, inventory, position, and faction.
    - Handles potential autoleveling for units based on chapter data (Ref: `research.md`, Sec 10).

### 2.3. Stat Calculation
    - Provide mechanisms or interfaces (potentially via `GameStateManager` or a dedicated `StatCalculator` module) to calculate derived combat stats (Atk, AS, Hit, Avo, Crit, Ddg) based on:
        - Base Stats (`UnitState`).
        - Equipped Weapon (`UnitState`, `DataProvider`).
        - Class Bonuses/Penalties (`DataProvider`).
        - Status Effects (e.g., halved stats when carrying/captured/slept) (`UnitState`, Ref: `research.md`, Sec 5.5, 9).
        - Terrain Bonuses (`MapSystem`, `DataProvider`).
        - Support Bonuses (`GameStateManager`, `DataProvider`, Ref: `research.md`, Sec 12).
        - Leadership Bonuses (`GameStateManager`, `DataProvider`, Ref: `research.md`, Sec 12).
        - Charisma Bonuses (`GameStateManager`, `DataProvider`, Ref: `research.md`, Sec 12).
        - Weapon Triangle (`DataProvider`).

### 2.4. State Management
    - **Health:** Manage HP changes via `GameStateManager` (damage/healing). Handle transition to Dead/Captured state when HP reaches 0.
    - **Status Effects:** Apply and remove status effects (Poison, Sleep, Silence, Berserk, etc.) via `GameStateManager`. Ensure effects persist according to Thracia rules (until cured or chapter end) (Ref: `research.md`, Sec 9). Manage stat penalties associated with statuses.
    - **Fatigue:** Track fatigue accumulation based on actions (combat, staff use, steal, dance) via `GameStateManager`. Check fatigue threshold against Max HP (Ref: `research.md`, Sec 7). Handle fatigue reset (benching, S-Drink).
    - **Action State:** Update `has_moved` and `has_acted` flags in `GameStateManager` as actions are performed. Handle Movement Star procs resetting `has_acted`.
    - **Capture/Rescue:** Manage the `carrying_unit_id` and `is_captured` flags in `GameStateManager`. Apply stat penalties to units carrying others (Ref: `research.md`, Sec 5.5).
    - **Dismount:** Manage mounted/dismounted state, potentially via a flag in `UnitState`. Ensure stat/movement/weapon restrictions are applied when dismounted (Ref: `research.md`, Sec 3, 8).

### 2.5. Progression
    - **Experience (EXP):** Award EXP for actions (combat, healing, potentially others like stealing/dancing) via `GameStateManager`.
    - **Level Ups:** Trigger level up when EXP reaches 100. Apply stat increases based on unit's growth rates using 1 RN system (`GameStateManager`, `DataProvider`). Handle potential Con and Mov growths (Ref: `research.md`, Sec 2). Respect stat caps (`DataProvider`). Reset EXP to 0.
    - **Weapon Experience (WExp):** Award WExp for weapon/staff usage via `GameStateManager`. Handle rank increases when WExp thresholds are met (Ref: `research.md`, Sec 4). Respect max weapon ranks per class (`DataProvider`).
    - **Promotion:** Handle class change via `GameStateManager` when a promotion item is used or event occurs. Apply fixed stat bonuses (`DataProvider`). Reset level to 1. Update weapon ranks/access (`DataProvider`).

### 2.6. Inventory Management
    - Manage adding, removing, using, and trading items via `GameStateManager`.
    - Track item durability and handle breaking (turning into "Broken" item in Thracia) (Ref: `research.md`, Sec 13).
    - Handle equipping weapons.

## 3. Pseudocode (unit_system.py - Conceptual)

*Note: Much of the direct state manipulation happens within `GameStateManager`. This pseudocode outlines the conceptual responsibilities and interactions.*

```python
# --- unit_system.py ---

# Import necessary modules/classes (GameStateManager, DataProvider, StatCalculator)
# Import enums (StatEnum, StatusEffectEnum, RankEnum, etc.)

class UnitSystem:
    gameStateManager = null
    dataProvider = null
    statCalculator = null # Optional dedicated calculator

    function initialize(gameStateManager_instance, dataProvider_instance):
        gameStateManager = gameStateManager_instance
        dataProvider = dataProvider_instance
        # statCalculator = StatCalculator(gameStateManager, dataProvider) # If using separate calc
        log("UnitSystem initialized.")

    # --- Unit State Access --- 
    # Primarily delegates to GameStateManager

    # TDD: Test get_unit_details retrieves all relevant info for display/logic
    function get_unit_details(unit_id):
        unit_state = gameStateManager.get_unit(unit_id)
        if not unit_state: return null
        
        details = {}
        details['state'] = unit_state # Raw state
        
        # Add calculated stats
        details['calculated_stats'] = self.calculate_current_combat_stats(unit_id)
        
        # Add class info
        details['class_info'] = dataProvider.get_class_data(unit_state.class_id)
        
        # Add inventory details with item names etc.
        details['inventory_details'] = []
        for item_instance in unit_state.inventory:
             item_data = dataProvider.get_item_data(item_instance.item_id)
             details['inventory_details'].append({
                 'name': item_data.name,
                 'durability': item_instance.current_durability,
                 'max_durability': item_data.max_durability,
                 # ... other item details
             })
        
        return details

    # --- Stat Calculation --- 
    # Might live here, in GameStateManager, or a dedicated StatCalculator

    # TDD: Test calculate_current_combat_stats reflects base stats, items, status, supports, terrain etc.
    function calculate_current_combat_stats(unit_id):
        unit = gameStateManager.get_unit(unit_id)
        if not unit: return {}

        # 1. Get Base Stats
        current_stats = dict(unit.base_stats) # Start with base

        # 2. Apply Status Penalties (Halving for carry/capture/sleep)
        is_carrying = unit.carrying_unit_id is not null
        is_captured = unit.is_captured # If this unit is captured (relevant?)
        is_slept = unit.has_status(SLEEP) # Check for sleep/petrify etc.
        
        if is_carrying or is_slept: # Ref: research.md Sec 5.5, 9
             current_stats[STR] //= 2
             current_stats[MAG] //= 2
             current_stats[SKL] //= 2
             current_stats[SPD] //= 2
             current_stats[DEF] //= 2
             # Note: Luck, Con, Mov are NOT halved

        # 3. Get Equipped Weapon Data
        weapon_data = None
        if unit.equipped_weapon_index >= 0:
            weapon_instance = unit.inventory[unit.equipped_weapon_index]
            weapon_data = dataProvider.get_item_data(weapon_instance.item_id)

        # 4. Calculate Attack (Atk)
        atk = 0
        if weapon_data:
             if dataProvider.is_weapon_physical(weapon_data.weapon_type): # Need helper
                  atk = current_stats[STR] + weapon_data.might
             elif dataProvider.is_weapon_magical(weapon_data.weapon_type): # Need helper
                  atk = current_stats[MAG] + weapon_data.might
             # Handle magic swords potentially using Mag even at range 1? Needs specific check.

        # 5. Calculate Attack Speed (AS) - Ref: research.md Sec 2
        effective_weight = 0
        if weapon_data:
             # Con does NOT offset tome weight in Thracia
             if dataProvider.is_weapon_tome(weapon_data.weapon_type): # Need helper
                  effective_weight = weapon_data.weight
             else: # Physical weapons
                  effective_weight = max(0, weapon_data.weight - current_stats[CON])
        
        attack_speed = current_stats[SPD] - effective_weight

        # 6. Calculate Hit - Ref: research.md Sec 5.1
        hit = 0
        if weapon_data:
             hit = weapon_data.hit
        hit += current_stats[SKL] * 2
        hit += current_stats[LUK]
        # Add Support, Leadership, Charisma bonuses (fetched via GameStateManager/DataProvider)
        hit += self.get_total_support_bonus(unit_id, 'hit')
        hit += self.get_total_leadership_bonus(unit.faction, 'hit')
        hit += self.get_total_charisma_bonus(unit.position, unit.faction, 'hit')
        # Weapon triangle bonus added during combat forecast

        # 7. Calculate Avoid (Avo) - Ref: research.md Sec 5.1
        avo = attack_speed * 2
        avo += current_stats[LUK]
        # Add Support, Leadership, Charisma bonuses
        avo += self.get_total_support_bonus(unit_id, 'avo')
        avo += self.get_total_leadership_bonus(unit.faction, 'avo')
        avo += self.get_total_charisma_bonus(unit.position, unit.faction, 'avo')
        # Add Terrain bonus
        terrain_bonuses = dataProvider.get_terrain_bonuses(unit.position)
        # Check if unit benefits from terrain (not mounted unless dismounted, not flyer)
        if self.can_unit_benefit_from_terrain(unit_id):
             avo += terrain_bonuses.get('avo', 0)

        # 8. Calculate Critical (Crit) - Ref: research.md Sec 5.3
        crit = 0
        if weapon_data:
             crit = weapon_data.crit
        crit += current_stats[SKL] # Skill adds directly to crit in Thracia
        # Add Support bonus
        crit += self.get_total_support_bonus(unit_id, 'crit')
        # Note: Leadership/Charisma do NOT affect Crit in Thracia

        # 9. Calculate Dodge / Crit Evade (Ddg) - Ref: research.md Sec 5.3
        ddg = current_stats[LUK] // 2 # Half of Luck
        # Add Support bonus
        ddg += self.get_total_support_bonus(unit_id, 'crit_evade')
        # Note: Leadership/Charisma do NOT affect Crit Evade

        # 10. Range (Rng)
        rng_str = "-"
        if weapon_data:
             if weapon_data.range_min == weapon_data.range_max:
                  rng_str = str(weapon_data.range_min)
             else:
                  rng_str = f"{weapon_data.range_min}-{weapon_data.range_max}"

        # 11. Follow-up Critical Multiplier (FCM / PCC)
        fcm = unit.pcc # Stored on unit state, loaded from base data

        return {
            'atk': atk,
            'AS': attack_speed,
            'hit': hit, # Base hit before target avoid/triangle
            'avo': avo, # Base avoid before target hit
            'crit': crit, # Base crit before target dodge
            'ddg': ddg, # Base crit evade
            'rng': rng_str,
            'FCM': fcm
        }

    # --- Helper functions for stat calculation ---

    # TDD: Test support bonus calculation considers range and stacking cap
    function get_total_support_bonus(unit_id, stat_type):
        # Get unit position and support partners from GameStateManager/DataProvider
        # Iterate nearby allies, check if they are support partners
        # Sum bonuses based on dataProvider.get_support_bonus(unit_id, partner_id)
        # Apply cap (e.g., +30 for hit/avo/crit/ddg in Thracia)
        # Return total bonus for the specified stat_type ('hit', 'avo', 'crit', 'crit_evade')
        return 0 # Placeholder

    # TDD: Test leadership bonus calculation sums stars correctly
    function get_total_leadership_bonus(faction, stat_type):
        # Get all active units of the given faction from GameStateManager
        # Sum leadership stars for those units
        # Return total_stars * 3 if stat_type is 'hit' or 'avo', else 0
        return 0 # Placeholder

    # TDD: Test charisma bonus calculation considers range and stacking
    function get_total_charisma_bonus(position, faction, stat_type):
        # Get all active units from GameStateManager
        # Find allies within 3 tiles of 'position' who have Charisma skill (check DataProvider)
        # Return count * 10 if stat_type is 'hit' or 'avo', else 0
        return 0 # Placeholder

    # TDD: Test terrain benefit check considers mounted/flying status
    function can_unit_benefit_from_terrain(unit_id):
        unit = gameStateManager.get_unit(unit_id)
        class_data = dataProvider.get_class_data(unit.class_id)
        movement_type = class_data.movement_type
        
        if movement_type == MOVEMENT_FLYING: return False
        
        is_mounted = dataProvider.is_class_mounted(unit.class_id)
        is_dismounted = unit.is_dismounted() # Need flag
        
        if is_mounted and not is_dismounted: return False # Mounted units don't get terrain bonuses
        
        return True # Infantry, Armor, Dismounted units benefit

    # --- State Change Triggers (Called by EngineCore/GameStateManager) ---

    # TDD: Test level up applies growths correctly respecting caps
    function trigger_level_up(unit_id):
        unit = gameStateManager.get_unit(unit_id)
        log(f"Unit {unit.name} leveled up to {unit.level + 1}!")
        
        stat_gains = {}
        for stat, growth_rate in unit.growth_rates.items():
            # Thracia uses 1 RN system
            if random_chance(growth_rate):
                 # Check against class caps
                 class_caps = dataProvider.get_class_caps(unit.class_id)
                 if unit.base_stats[stat] < class_caps.get(stat, 99): # Assume 99 if no cap defined
                      unit.base_stats[stat] += 1
                      stat_gains[stat] = stat_gains.get(stat, 0) + 1
                      log(f"  +1 {stat.name}")
        
        unit.level += 1
        unit.experience = 0 # Reset EXP after level up
        
        # Potentially recalculate max HP if HP grew
        if HP in stat_gains:
             unit.max_hp += stat_gains[HP]
             unit.current_hp += stat_gains[HP] # Heal the gained HP too

        # Return gains for UI display
        return stat_gains

    # TDD: Test weapon rank up occurs at correct WExp thresholds
    function trigger_weapon_rank_up(unit_id, weapon_type):
        unit = gameStateManager.get_unit(unit_id)
        current_rank = unit.weapon_ranks.get(weapon_type, None)
        current_wexp = unit.weapon_exp.get(weapon_type, 0)
        
        next_rank, required_wexp = dataProvider.get_next_weapon_rank_info(current_rank)
        
        if next_rank and current_wexp >= required_wexp:
             # Check against class max rank
             max_rank = dataProvider.get_class_max_rank(unit.class_id, weapon_type)
             if dataProvider.is_rank_higher(next_rank, max_rank) <= 0: # If next rank is <= max rank
                  unit.weapon_ranks[weapon_type] = next_rank
                  log(f"Unit {unit.name} reached {next_rank.name} rank in {weapon_type.name}!")
                  # Return true or rank for UI display
                  return next_rank
        return None

    # TDD: Test promotion applies bonuses, resets level, updates class/ranks
    function trigger_promotion(unit_id, promotion_item_id):
        unit = gameStateManager.get_unit(unit_id)
        class_data = dataProvider.get_class_data(unit.class_id)
        
        promoted_class_id = class_data.promotion_options.get(promotion_item_id) # Or generic 'MasterSeal' key?
        if not promoted_class_id:
             log(f"Error: No promotion path found for {unit.class_id} with item {promotion_item_id}")
             return False

        promoted_class_data = dataProvider.get_class_data(promoted_class_id)
        promotion_gains = dataProvider.get_promotion_gains(unit.class_id, promoted_class_id)

        log(f"Unit {unit.name} promoting from {class_data.name} to {promoted_class_data.name}!")

        # Apply stat gains (ensure stats reach at least the new base class stats)
        for stat, gain in promotion_gains.stat_bonuses.items():
             new_stat_value = unit.base_stats[stat] + gain
             # Ensure it meets the new class base stat
             new_stat_value = max(new_stat_value, promoted_class_data.base_stats.get(stat, 0))
             # Ensure it doesn't exceed the new class cap
             new_stat_value = min(new_stat_value, promoted_class_data.max_stats.get(stat, 99))
             unit.base_stats[stat] = new_stat_value
        
        # Update HP based on potential Con gain? Or direct HP gain? Check FE5 promotion rules. Assume direct HP gain if specified.
        if HP in promotion_gains.stat_bonuses:
             # Update max_hp and heal the difference
             hp_gain = unit.base_stats[HP] - (unit.base_stats[HP] - promotion_gains.stat_bonuses[HP]) # Calculate actual gain applied
             unit.max_hp += hp_gain # This assumes base_stats[HP] is max HP base
             unit.current_hp += hp_gain

        # Update class ID
        unit.class_id = promoted_class_id

        # Reset level and experience
        unit.level = 1
        unit.experience = 0

        # Update weapon ranks
        for wep_type, rank_change in promotion_gains.rank_changes.items():
             # Handle rank increase or gaining new weapon type at base rank
             current_rank = unit.weapon_ranks.get(wep_type, None)
             new_rank = dataProvider.apply_rank_increase(current_rank, rank_change) # Handles E + 1 = D, or None + E = E
             unit.weapon_ranks[wep_type] = new_rank
             # Ensure WExp is set for new types if needed
             if wep_type not in unit.weapon_exp: unit.weapon_exp[wep_type] = 0
        
        # Consume promotion item (handled by caller in GameStateManager.use_item)
        return True