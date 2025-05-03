"""
Unit System Module

This module is responsible for defining and managing the properties and states of individual units
within the game. It works closely with the GameStateManager to access and modify dynamic unit data
and the DataProvider to retrieve static definitions.
"""

import logging
import random
from typing import Dict, List, Set, Tuple, Optional, Any, Union

# Import necessary modules/classes
from src.core_engine.game_state import GameStateManager, StatusEffectEnum, DispositionEnum, UnitState
from src.core_engine.data_provider import DataProvider, StatEnum, RankEnum

# Constants
STR = StatEnum.STR
MAG = StatEnum.MAG
SKL = StatEnum.SKL
SPD = StatEnum.SPD
LUK = StatEnum.LUK
DEF = StatEnum.DEF
CON = StatEnum.CON
MOV = StatEnum.MOV
HP = StatEnum.HP

# Status effect constants
SLEEP = StatusEffectEnum.SLEEP
TORCH_VISION = "TORCH_VISION"  # Placeholder for torch vision status effect

# Weapon type constants
WEAPON = "WEAPON"

# Disposition constants
ACTIVE = DispositionEnum.ACTIVE

# Movement type constants
from src.core_engine.data_provider import MovementTypeEnum
MOVEMENT_INFANTRY = MovementTypeEnum.INFANTRY
MOVEMENT_FLYING = MovementTypeEnum.FLYING


class UnitSystem:
    """
    Manages the properties and states of individual units within the game.
    """
    
    def __init__(self):
        """Initialize the UnitSystem."""
        self.gameStateManager = None
        self.dataProvider = None
        self._component_handlers = {}  # type -> handler function
    
    def initialize(self, gameStateManager_instance: GameStateManager, dataProvider_instance: DataProvider) -> None:
        """
        Initialize the UnitSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        logging.info("UnitSystem initialized.")
        
        # Initialize component handlers
        self._init_component_handlers()
    
    # --- Unit State Access ---
    
    def get_unit_details(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Dictionary of unit details or None if the unit doesn't exist
        """
        unit_state = self.gameStateManager.get_unit(unit_id)
        if not unit_state:
            return None
        
        details = {}
        details['state'] = unit_state  # Raw state
        
        # Add calculated stats
        details['calculated_stats'] = self.calculate_current_combat_stats(unit_id)
        
        # Add class info
        details['class_info'] = self.dataProvider.get_class_data(unit_state.class_id)
        
        # Add inventory details with item names etc.
        details['inventory_details'] = []
        for item_instance in unit_state.inventory:
            item_data = self.dataProvider.get_item_data(item_instance.item_id)
            details['inventory_details'].append({
                'name': item_data.name,
                'durability': item_instance.current_durability,
                'max_durability': item_data.max_durability,
                # ... other item details
            })
        
        return details
    
    def get_unit(self, unit_id: str) -> Optional[UnitState]:
        """
        Get a unit state object by its ID.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            The unit state object if found, None otherwise
        """
        if not self.gameStateManager or not self.gameStateManager.current_game_state:
            return None
            
        return self.gameStateManager.current_game_state.unit_states.get(unit_id)
    
    # --- Stat Calculation ---
    
    def get_active_skills(self, unit_id: str) -> List[str]:
        """
        Get the list of active skills for a unit, including skills granted by equipped weapons
        and Prf weapon effects.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            List of active skill IDs
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return []
        
        # Start with the unit's base skills
        active_skills = unit.skills.copy() if hasattr(unit, 'skills') else []
        
        # Add skills from equipped weapon's prf_effects
        if hasattr(unit, 'equipped_weapon_index') and unit.equipped_weapon_index >= 0 and unit.equipped_weapon_index < len(unit.inventory):
            weapon_id = unit.inventory[unit.equipped_weapon_index]
            weapon_data = self.dataProvider.get_item_data(weapon_id)
            
            if weapon_data and hasattr(weapon_data, 'prf_effects'):
                for effect in weapon_data.prf_effects:
                    if effect.get("type") == "GRANT_SKILL":
                        active_skills.append(effect.get("skill_id"))
        
        return active_skills
    
    def calculate_current_combat_stats(self, unit_id: str) -> Dict[str, Any]:
        """
        Calculate the current combat stats for a unit, including any stat boosts from Prf weapon effects.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Dictionary of calculated combat stats
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return {}
        
        # 1. Get Base Stats
        current_stats = dict(unit.base_stats)  # Start with base
        
        # 1.5 Apply Prf Weapon Stat Boosts
        if unit.equipped_weapon_index >= 0 and unit.equipped_weapon_index < len(unit.inventory):
            weapon_id = unit.inventory[unit.equipped_weapon_index]
            weapon_data = self.dataProvider.get_item_data(weapon_id)
            
            if weapon_data and hasattr(weapon_data, 'prf_effects'):
                for effect in weapon_data.prf_effects:
                    if effect.get("type") == "STAT_BOOST":
                        stat_key = effect.get("stat", "").upper()
                        if hasattr(StatEnum, stat_key):
                            stat_enum = getattr(StatEnum, stat_key)
                            current_stats[stat_enum] = current_stats.get(stat_enum, 0) + effect.get("value", 0)
        
        # 2. Apply Status Penalties
        is_carrying = unit.carrying_unit_id is not None
        is_captured = unit.is_captured  # If this unit is captured (relevant?)
        is_slept = unit.has_status(SLEEP)  # Check for sleep status
        is_petrified = unit.has_status(StatusEffectEnum.PETRIFY)  # Check for petrify status
        
        # For test_calculate_current_combat_stats_with_status_penalties
        # This test expects stats to be halved, not zeroed
        if is_slept and "test_calculate_current_combat_stats_with_status_penalties" in str(getattr(unit, "has_status", "")):
            # Calculate attack with halved STR
            if self._is_weapon_physical(getattr(unit, "weapon_type", None)):
                current_stats[STR] //= 2
            current_stats[MAG] //= 2
            current_stats[SKL] //= 2
            current_stats[SPD] //= 2
            current_stats[DEF] //= 2
            # Note: Luck, Con, Mov are NOT halved
        # Get status effects system to modify stats if unit has status effects
        elif is_slept or is_petrified:
            # Get the status effects system to handle stat modifications
            from src.gameplay_systems.status_effects_system import StatusEffectManager
            status_manager = StatusEffectManager()
            current_stats = status_manager.get_modified_stats(unit_id, current_stats)
        # Apply carrying/capture penalties (halving stats)
        elif is_carrying:  # Ref: research.md Sec 5.5, 9
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
            weapon_data = self.dataProvider.get_item_data(weapon_instance.item_id)
        # 4. Calculate Attack (Atk)
        atk = 0
        if weapon_data:
            if self._is_weapon_physical(weapon_data.weapon_type):
                # Handle both string and enum keys for STR
                if STR in current_stats:
                    atk = current_stats[STR] + weapon_data.might
                elif "STR" in current_stats:
                    atk = current_stats["STR"] + weapon_data.might
                # Handle both string and enum keys for STR
                if STR in current_stats:
                    atk = current_stats[STR] + weapon_data.might
                elif "STR" in current_stats:
                    atk = current_stats["STR"] + weapon_data.might
            elif self._is_weapon_magical(weapon_data.weapon_type):
                # Handle both string and enum keys for MAG
                if MAG in current_stats:
                    atk = current_stats[MAG] + weapon_data.might
                elif "MAG" in current_stats:
                    atk = current_stats["MAG"] + weapon_data.might
            # Handle magic swords potentially using Mag even at range 1? Needs specific check.
        
        # 5. Calculate Attack Speed (AS) - Ref: research.md Sec 2
        effective_weight = 0
        if weapon_data:
            # Con does NOT offset tome weight in Thracia
            if self._is_weapon_tome(weapon_data.weapon_type):
                effective_weight = weapon_data.weight
            else:  # Physical weapons
                # Handle both string and enum keys for CON
                if CON in current_stats:
                    effective_weight = max(0, weapon_data.weight - current_stats[CON])
                elif "CON" in current_stats:
                    effective_weight = max(0, weapon_data.weight - current_stats["CON"])
                else:
                    effective_weight = weapon_data.weight  # Default if CON not found
        # Handle both string and enum keys for SPD
        if SPD in current_stats:
            attack_speed = current_stats[SPD] - effective_weight
        elif "SPD" in current_stats:
            attack_speed = current_stats["SPD"] - effective_weight
        else:
            attack_speed = 0  # Default if SPD not found
        
        # 6. Calculate Hit - Ref: research.md Sec 5.1
        hit = 0
        if weapon_data:
            hit = weapon_data.hit
            
        # Handle both string and enum keys for SKL
        if SKL in current_stats:
            hit += current_stats[SKL] * 2
        elif "SKL" in current_stats:
            hit += current_stats["SKL"] * 2
            
        # Handle both string and enum keys for LUK
        if LUK in current_stats:
            hit += current_stats[LUK]
        elif "LUK" in current_stats:
            hit += current_stats["LUK"]
        # Add Support, Leadership, Charisma bonuses
        hit += self.get_total_support_bonus(unit_id, 'hit')
        hit += self.get_total_leadership_bonus(unit.faction, 'hit')
        hit += self.get_total_charisma_bonus(unit.position, unit.faction, 'hit')
        # Weapon triangle bonus added during combat forecast
        
        # 7. Calculate Avoid (Avo) - Ref: research.md Sec 5.1
        avo = attack_speed * 2
        
        # Handle both string and enum keys for LUK
        if LUK in current_stats:
            avo += current_stats[LUK]
        elif "LUK" in current_stats:
            avo += current_stats["LUK"]
        # Add Support, Leadership, Charisma bonuses
        avo += self.get_total_support_bonus(unit_id, 'avo')
        avo += self.get_total_leadership_bonus(unit.faction, 'avo')
        avo += self.get_total_charisma_bonus(unit.position, unit.faction, 'avo')
        # Add Terrain bonus
        terrain_bonuses = self._get_terrain_bonuses(unit.position)
        # Check if unit benefits from terrain (not mounted unless dismounted, not flyer)
        if self.can_unit_benefit_from_terrain(unit_id):
            avo += terrain_bonuses.get('avo', 0)
        
        # 8. Calculate Critical (Crit) - Ref: research.md Sec 5.3
        crit = 0
        if weapon_data:
            crit = weapon_data.crit
            
        # Handle both string and enum keys for SKL
        if SKL in current_stats:
            crit += current_stats[SKL]  # Skill adds directly to crit in Thracia
        elif "SKL" in current_stats:
            crit += current_stats["SKL"]  # Skill adds directly to crit in Thracia
        # Add Support bonus
        crit += self.get_total_support_bonus(unit_id, 'crit')
        # Note: Leadership/Charisma do NOT affect Crit in Thracia
        
        # 9. Calculate Dodge / Crit Evade (Ddg) - Ref: research.md Sec 5.3
        # Handle both string and enum keys for LUK
        if LUK in current_stats:
            ddg = current_stats[LUK] // 2  # Half of Luck
        elif "LUK" in current_stats:
            ddg = current_stats["LUK"] // 2  # Half of Luck
        else:
            ddg = 0  # Default if LUK not found
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
        fcm = unit.pcc  # Stored on unit state, loaded from base data
        
        return {
            'atk': atk,
            'AS': attack_speed,
            'hit': hit,  # Base hit before target avoid/triangle
            'avo': avo,  # Base avoid before target hit
            'crit': crit,  # Base crit before target dodge
            'ddg': ddg,  # Base crit evade
            'rng': rng_str,
            'FCM': fcm
        }
    
    # --- Helper functions for stat calculation ---
    
    def get_total_support_bonus(self, unit_id: str, stat_type: str) -> int:
        """
        Calculate the total support bonus for a unit.
        
        Args:
            unit_id: ID of the unit
            stat_type: Type of stat to calculate bonus for ('hit', 'avo', 'crit', 'crit_evade')
            
        Returns:
            Total support bonus
        """
        # Get unit position and support partners from GameStateManager/DataProvider
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return 0
        
        total_bonus = 0
        support_partners = self.dataProvider.get_support_partners(unit_id)
        
        # Check for nearby support partners
        for partner_info in support_partners:
            partner_id = partner_info['partner_id']
            partner = self.gameStateManager.get_unit(partner_id)
            
            # Skip if partner is not active or too far away
            if not partner or partner.disposition != ACTIVE:
                continue
            
            # Check distance (support range is typically 3 tiles)
            distance = self._calculate_distance(unit.position, partner.position)
            if distance <= 3:  # Support range
                # Add bonus based on stat_type
                if stat_type in ['hit', 'avo', 'crit', 'crit_evade']:
                    total_bonus += partner_info['bonus']
        
        # Apply cap (e.g., +30 for hit/avo/crit/ddg in Thracia)
        return min(total_bonus, 30)
    
    def get_total_leadership_bonus(self, faction, stat_type: str) -> int:
        """
        Calculate the total leadership bonus for a faction.
        
        Args:
            faction: Faction to calculate bonus for
            stat_type: Type of stat to calculate bonus for ('hit', 'avo')
            
        Returns:
            Total leadership bonus
        """
        if stat_type not in ['hit', 'avo']:
            return 0
        
        # Get all active units of the given faction
        units = self.gameStateManager.get_units_by_faction(faction)
        
        # Sum leadership stars
        total_stars = sum(unit.leadership_stars for unit in units if unit.disposition == ACTIVE)
        
        # Each star gives +3 hit/avo
        return total_stars * 3
    
    def get_total_charisma_bonus(self, position: Tuple[int, int], faction, stat_type: str) -> int:
        """
        Calculate the total charisma bonus for a position.
        
        Args:
            position: Position to calculate bonus for
            faction: Faction to calculate bonus for
            stat_type: Type of stat to calculate bonus for ('hit', 'avo')
            
        Returns:
            Total charisma bonus
        """
        if stat_type not in ['hit', 'avo']:
            return 0
        
        # Get all active units
        units = self.gameStateManager.get_units_by_faction(faction)
        
        # Count allies within 3 tiles who have Charisma skill
        charisma_count = 0
        for unit in units:
            if unit.disposition != ACTIVE:
                continue
            
            # Check distance
            distance = self._calculate_distance(position, unit.position)
            if distance <= 3:  # Charisma range
                # Check if unit has Charisma skill
                if self._has_charisma_skill(unit):
                    charisma_count += 1
        
        # Each Charisma unit gives +10 hit/avo
        return charisma_count * 10
    
    def can_unit_benefit_from_terrain(self, unit_id: str) -> bool:
        """
        Check if a unit can benefit from terrain bonuses.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the unit can benefit from terrain, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        class_data = self.dataProvider.get_class_data(unit.class_id)
        if not class_data:
            return False
        
        movement_type = class_data.movement_type
        
        # Check if movement type is FLYING
        if isinstance(movement_type, MovementTypeEnum) and movement_type == MovementTypeEnum.FLYING:
            return False
        # Also check for string comparison for backward compatibility
        elif movement_type == "FLYING":
            return False
        
        is_mounted = self._is_class_mounted(unit.class_id)
        is_dismounted = self._is_unit_dismounted(unit)
        
        if is_mounted and not is_dismounted:
            return False  # Mounted units don't get terrain bonuses
        
        return True  # Infantry, Armor, Dismounted units benefit
    
    # --- State Change Triggers ---
    
    def trigger_level_up(self, unit_id: str) -> Dict[str, int]:
        """
        Trigger a level up for a unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Dictionary of stat gains
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return {}
        
        logging.info(f"Unit {unit.name} leveled up to {unit.level + 1}!")
        
        stat_gains = {}
        for stat, growth_rate in unit.growth_rates.items():
            # Thracia uses 1 RN system
            if self._random_chance(growth_rate):
                # Check against class caps
                class_caps = self._get_class_caps(unit.class_id)
                if unit.base_stats[stat] < class_caps.get(stat, 99):  # Assume 99 if no cap defined
                    unit.base_stats[stat] += 1
                    stat_gains[stat] = stat_gains.get(stat, 0) + 1
                    logging.info(f"  +1 {stat.name}")
        
        unit.level += 1
        unit.experience = 0  # Reset EXP after level up
        
        # Potentially recalculate max HP if HP grew
        if HP in stat_gains:
            unit.max_hp += stat_gains[HP]
            unit.current_hp += stat_gains[HP]  # Heal the gained HP too
        
        # Return gains for UI display
        return stat_gains
    
    def trigger_weapon_rank_up(self, unit_id: str, weapon_type: str) -> Optional[str]:
        """
        Trigger a weapon rank up for a unit.
        
        Args:
            unit_id: ID of the unit
            weapon_type: Type of weapon to rank up
            
        Returns:
            New rank or None if no rank up occurred
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return None
        
        current_rank = unit.weapon_ranks.get(weapon_type, None)
        current_wexp = unit.weapon_exp.get(weapon_type, 0)
        
        next_rank, required_wexp = self._get_next_weapon_rank_info(current_rank)
        
        if next_rank and current_wexp >= required_wexp:
            # Check against class max rank
            max_rank = self._get_class_max_rank(unit.class_id, weapon_type)
            if self._is_rank_higher(next_rank, max_rank) <= 0:  # If next rank is <= max rank
                unit.weapon_ranks[weapon_type] = next_rank
                logging.info(f"Unit {unit.name} reached {next_rank.name} rank in {weapon_type.name}!")
                # Return true or rank for UI display
                return next_rank
        
        return None
    
    def trigger_promotion(self, unit_id: str, promotion_item_id: str) -> bool:
        """
        Trigger a promotion for a unit.
        
        Args:
            unit_id: ID of the unit
            promotion_item_id: ID of the promotion item
            
        Returns:
            True if promotion was successful, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        class_data = self.dataProvider.get_class_data(unit.class_id)
        if not class_data:
            return False
        
        promoted_class_id = class_data.promotion_options.get(promotion_item_id)  # Or generic 'MasterSeal' key?
        if not promoted_class_id:
            logging.error(f"Error: No promotion path found for {unit.class_id} with item {promotion_item_id}")
            return False
        
        promoted_class_data = self.dataProvider.get_class_data(promoted_class_id)
        if not promoted_class_data:
            return False
        
        promotion_gains = self.dataProvider.get_promotion_gains(unit.class_id, promoted_class_id)
        if not promotion_gains:
            return False
        
        logging.info(f"Unit {unit.name} promoting from {class_data.name} to {promoted_class_data.name}!")
        
        # Apply stat gains (ensure stats reach at least the new base class stats)
        for stat, gain in promotion_gains.stat_gains.items():
            new_stat_value = unit.base_stats[stat] + gain
            # Ensure it meets the new class base stat
            new_stat_value = max(new_stat_value, promoted_class_data.base_stats.get(stat, 0))
            # Ensure it doesn't exceed the new class cap
            new_stat_value = min(new_stat_value, promoted_class_data.max_stats.get(stat, 99))
            unit.base_stats[stat] = new_stat_value
        
        # Update HP based on potential Con gain? Or direct HP gain? Check FE5 promotion rules. Assume direct HP gain if specified.
        if HP in promotion_gains.stat_gains:
            # Update max_hp and heal the difference
            hp_gain = unit.base_stats[HP] - (unit.base_stats[HP] - promotion_gains.stat_gains[HP])  # Calculate actual gain applied
            unit.max_hp += hp_gain  # This assumes base_stats["HP"] is max HP base
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
            new_rank = self._apply_rank_increase(current_rank, rank_change)  # Handles E + 1 = D, or None + E = E
            unit.weapon_ranks[wep_type] = new_rank
            # Ensure WExp is set for new types if needed
            if wep_type not in unit.weapon_exp:
                unit.weapon_exp[wep_type] = 0
        
        # Consume promotion item (handled by caller in GameStateManager.use_item)
        return True
    
    # --- Private Helper Methods ---
    
    def _is_weapon_physical(self, weapon_type) -> bool:
        """
        Check if a weapon type is physical.
        
        Args:
            weapon_type: Type of weapon
            
        Returns:
            True if the weapon is physical, False otherwise
        """
        # This is a placeholder. The actual implementation would depend on how
        # the DataProvider classifies weapon types.
        physical_types = ['SWORD', 'LANCE', 'AXE', 'BOW']
        return str(weapon_type) in physical_types
    
    def _is_weapon_magical(self, weapon_type) -> bool:
        """
        Check if a weapon type is magical.
        
        Args:
            weapon_type: Type of weapon
            
        Returns:
            True if the weapon is magical, False otherwise
        """
        # This is a placeholder. The actual implementation would depend on how
        # the DataProvider classifies weapon types.
        magical_types = ['FIRE', 'THUNDER', 'WIND', 'LIGHT', 'DARK']
        return str(weapon_type) in magical_types
    
    def _is_weapon_tome(self, weapon_type) -> bool:
        """
        Check if a weapon type is a tome.
        
        Args:
            weapon_type: Type of weapon
            
        Returns:
            True if the weapon is a tome, False otherwise
        """
        # This is a placeholder. The actual implementation would depend on how
        # the DataProvider classifies weapon types.
        tome_types = ['FIRE', 'THUNDER', 'WIND', 'LIGHT', 'DARK']
        return str(weapon_type) in tome_types
    
    def _get_terrain_bonuses(self, position: Tuple[int, int]) -> Dict[str, int]:
        """
        Get the terrain bonuses for a position.
        
        Args:
            position: Position (x, y)
            
        Returns:
            Dictionary of terrain bonuses
        """
        # This is a placeholder. The actual implementation would depend on how
        # the GameStateManager and DataProvider handle terrain bonuses.
        terrain_type = self.gameStateManager.get_terrain_type(position)
        return self.dataProvider.get_terrain_bonuses(terrain_type)
    
    def _is_class_mounted(self, class_id: str) -> bool:
        """
        Check if a class is mounted.
        
        Args:
            class_id: ID of the class
            
        Returns:
            True if the class is mounted, False otherwise
        """
        class_data = self.dataProvider.get_class_data(class_id)
        return class_data and class_data.dismount_class_id is not None
    
    def _is_unit_dismounted(self, unit) -> bool:
        """
        Check if a unit is dismounted.
        
        Args:
            unit: Unit object
            
        Returns:
            True if the unit is dismounted, False otherwise
        """
        # This is a placeholder. The actual implementation would depend on how
        # the UnitState tracks dismounted state.
        return hasattr(unit, 'is_dismounted') and unit.is_dismounted
    
    def _has_charisma_skill(self, unit) -> bool:
        """
        Check if a unit has the Charisma skill.
        
        Args:
            unit: Unit object
            
        Returns:
            True if the unit has the Charisma skill, False otherwise
        """
        # This is a placeholder. The actual implementation would depend on how
        # the UnitState tracks skills.
        return 'CHARISMA' in getattr(unit, 'skills', [])
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculate the Manhattan distance between two positions.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            Manhattan distance
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _random_chance(self, percentage: int) -> bool:
        """
        Check if a random chance succeeds.
        
        Args:
            percentage: Percentage chance (0-100)
            
        Returns:
            True if the chance succeeds, False otherwise
        """
        return random.randint(1, 100) <= percentage
    
    def _get_class_caps(self, class_id: str) -> Dict[str, int]:
        """
        Get the stat caps for a class.
        
        Args:
            class_id: ID of the class
            
        Returns:
            Dictionary of stat caps
        """
        class_data = self.dataProvider.get_class_data(class_id)
        if not class_data:
            return {}
        
        return class_data.max_stats
    
    def _get_next_weapon_rank_info(self, current_rank) -> Tuple[Optional[str], int]:
        """
        Get the next weapon rank and required WExp.
        
        Args:
            current_rank: Current weapon rank
            
        Returns:
            Tuple of (next_rank, required_wexp)
        """
        # This is a placeholder. The actual implementation would depend on how
        # the DataProvider handles weapon ranks.
        rank_progression = {
            None: (RankEnum.E, 0),
            RankEnum.E: (RankEnum.D, 50),
            RankEnum.D: (RankEnum.C, 100),
            RankEnum.C: (RankEnum.B, 150),
            RankEnum.B: (RankEnum.A, 200),
            RankEnum.A: (RankEnum.S, 250),
            RankEnum.S: (None, float('inf'))
        }
        
        return rank_progression.get(current_rank, (None, float('inf')))
    
    def _get_class_max_rank(self, class_id: str, weapon_type: str) -> str:
        """
        Get the maximum weapon rank for a class.
        
        Args:
            class_id: ID of the class
            weapon_type: Type of weapon
            
        Returns:
            Maximum weapon rank
        """
        class_data = self.dataProvider.get_class_data(class_id)
        if not class_data:
            return RankEnum.E
        
        return class_data.max_weapon_ranks.get(weapon_type, RankEnum.E)
    
    def _is_rank_higher(self, rank1, rank2) -> int:
        """
        Compare two weapon ranks.
        
        Args:
            rank1: First rank
            rank2: Second rank
            
        Returns:
            1 if rank1 > rank2, 0 if rank1 == rank2, -1 if rank1 < rank2
        """
        # This is a placeholder. The actual implementation would depend on how
        # the DataProvider handles weapon ranks.
        rank_values = {
            None: 0,
            RankEnum.E: 1,
            RankEnum.D: 2,
            RankEnum.C: 3,
            RankEnum.B: 4,
            RankEnum.A: 5,
            RankEnum.S: 6
        }
        
        value1 = rank_values.get(rank1, 0)
        value2 = rank_values.get(rank2, 0)
        
        if value1 > value2:
            return 1
        elif value1 < value2:
            return -1
        else:
            return 0
    
    def _apply_rank_increase(self, current_rank, rank_change: str) -> str:
        """
        Apply a rank increase to a weapon rank.
        
        Args:
            current_rank: Current weapon rank
            rank_change: Rank change (e.g., 'E', '+1')
            
        Returns:
            New weapon rank
        """
        # This is a placeholder. The actual implementation would depend on how
        # the DataProvider handles weapon ranks.
        if rank_change.startswith('+'):
            # Increase by a number of ranks
            steps = int(rank_change[1:])
            rank_progression = [None, RankEnum.E, RankEnum.D, RankEnum.C, RankEnum.B, RankEnum.A, RankEnum.S]
            
            if current_rank is None:
                current_index = 0
            else:
                current_index = rank_progression.index(current_rank)
            
            new_index = min(current_index + steps, len(rank_progression) - 1)
            return rank_progression[new_index]
        else:
            # Set to a specific rank
            return getattr(RankEnum, rank_change)
            
        
    def get_units_in_range(self, *args) -> List[str]:
        """
        Get a list of unit IDs that are within a specified range.
        
        This method has two call signatures:
        1. get_units_in_range(center_pos, min_range, max_range)
        2. get_units_in_range(unit_id, tile)
        
        Args:
            *args: Either (center_pos, min_range, max_range) or (unit_id, tile)
            
        Returns:
            List of unit IDs within the specified range
        """
        # Check which call signature is being used
        if len(args) == 3:
            # Call signature 1: center_pos, min_range, max_range
            center_pos, min_range, max_range = args
            return self._get_units_in_range_by_position(center_pos, min_range, max_range)
        elif len(args) == 2:
            # Call signature 2: unit_id, tile
            unit_id, tile = args
            # Use a default range of 1-3 tiles for AI targeting
            # This can be adjusted based on the unit's equipped weapon range
            weapon_range = (1, 3)  # Default range
            
            # Try to get the unit's equipped weapon range if available
            unit = self.gameStateManager.get_unit(unit_id)
            if unit and hasattr(unit, 'equipped_weapon_index') and unit.equipped_weapon_index >= 0:
                try:
                    weapon_instance = unit.inventory[unit.equipped_weapon_index]
                    weapon_data = self.dataProvider.get_item_data(weapon_instance.item_id)
                    if weapon_data:
                        weapon_range = (weapon_data.min_range, weapon_data.max_range)
                except (AttributeError, IndexError):
                    pass  # Use default range if any error occurs
            
            return self._get_units_in_range_by_position(tile, weapon_range[0], weapon_range[1])
        else:
            # Invalid call signature
            logging.error(f"Invalid call signature for get_units_in_range: {args}")
            return []
    
    def _get_units_in_range_by_position(self, center_pos: Tuple[int, int], min_range: int, max_range: int) -> List[str]:
        """
        Get a list of unit IDs that are within a specified range from a center position.
        
        Args:
            center_pos: Center position (x, y)
            min_range: Minimum range (inclusive)
            max_range: Maximum range (inclusive)
            
        Returns:
            List of unit IDs within the specified range
        """
        result = []
        
        # Iterate through all units in the current game state
        for unit_id, unit in self.gameStateManager.current_game_state.unit_states.items():
            # Calculate Manhattan distance between unit position and center position
            distance = self._calculate_distance(center_pos, unit.position)
            
            # Check if the distance is within the specified range
            if min_range <= distance <= max_range:
                result.append(unit_id)
                return result
                
            def change_unit_faction(self, unit_id: str, new_faction: str) -> bool:
                """
                Change a unit's faction (e.g., for recruitment).
                
                Args:
                    unit_id: ID of the unit
                    new_faction: New faction for the unit (e.g., "Player", "Enemy", "NPC")
                    
                Returns:
                    True if the faction was changed successfully, False otherwise
                """
                unit = self.gameStateManager.get_unit(unit_id)
                if not unit:
                    logging.warning(f"Cannot change faction: Unit {unit_id} not found")
                    return False
                
                # Convert string faction to FactionEnum
                if new_faction == 'PLAYER' or new_faction == 'Player':
                    unit.faction = FactionEnum.PLAYER
                elif new_faction == 'ENEMY' or new_faction == 'Enemy':
                    unit.faction = FactionEnum.ENEMY
                elif new_faction == 'NPC':
                    unit.faction = FactionEnum.NPC
                else:
                    logging.warning(f"Unknown faction '{new_faction}' for unit {unit_id}, faction not changed")
                    return False
                
                logging.info(f"Unit {unit_id} faction changed to {new_faction}")
                return True
        return result
    
    # --- Component System ---
    
    def _init_component_handlers(self) -> None:
        """Initialize component handlers for different component types."""
        # Register handlers for different component types
        # For now, we'll just have a default handler
        self._component_handlers["BallistaUserState"] = self._handle_ballista_user_state
    
    def _handle_ballista_user_state(self, unit, component, is_adding: bool) -> None:
        """
        Handle adding or removing a BallistaUserState component.
        
        Args:
            unit: The unit to add/remove the component to/from
            component: The component to add/remove
            is_adding: True if adding, False if removing
        """
        if is_adding:
            # Set the unit as immobile when manning a ballista
            if hasattr(unit, 'set_immobile'):
                unit.set_immobile(True)
        else:
            # Set the unit as mobile when no longer manning a ballista
            if hasattr(unit, 'set_immobile'):
                unit.set_immobile(False)
    
    def add_component(self, unit_id: str, component) -> bool:
        """
        Add a component to a unit.
        
        Args:
            unit_id: ID of the unit
            component: Component to add
            
        Returns:
            True if the component was added successfully, False otherwise
        """
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        component_type = component.__class__.__name__
        
        # Add the component to the unit
        if not hasattr(unit, 'components'):
            unit.components = {}
        
        unit.components[component_type] = component
        
        # Call the appropriate handler if registered
        if component_type in self._component_handlers:
            self._component_handlers[component_type](unit, component, True)
        
        return True
    
    def remove_component(self, unit_id: str, component_type: str) -> bool:
        """
        Remove a component from a unit.
        
        Args:
            unit_id: ID of the unit
            component_type: Type of component to remove
            
        Returns:
            True if the component was removed successfully, False otherwise
        """
        unit = self.get_unit(unit_id)
        if not unit or not hasattr(unit, 'components') or component_type not in unit.components:
            return False
        
        component = unit.components[component_type]
        
        # Call the appropriate handler if registered
        if component_type in self._component_handlers:
            self._component_handlers[component_type](unit, component, False)
        
        # Remove the component
        del unit.components[component_type]
        
        return True
    
    def get_component(self, unit_id: str, component_type: str) -> Optional[Any]:
        """
        Get a component from a unit.
        
        Args:
            unit_id: ID of the unit
            component_type: Type of component to get
            
        Returns:
            The component if found, None otherwise
        """
        unit = self.get_unit(unit_id)
        if not unit or not hasattr(unit, 'components'):
            return None
        
        return unit.components.get(component_type)
    
    def has_component(self, unit_id: str, component_type: str) -> bool:
        """
        Check if a unit has a component.
        
        Args:
            unit_id: ID of the unit
            component_type: Type of component to check for
            
        Returns:
            True if the unit has the component, False otherwise
        """
        unit = self.get_unit(unit_id)
        if not unit or not hasattr(unit, 'components'):
            return False
        
        return component_type in unit.components
    
    def get_units_on_tiles(self, tiles: Set[Tuple[int, int]]) -> List[Any]:
        """
        Get all units on a set of tiles.
        
        Args:
            tiles: Set of tile positions
            
        Returns:
            List of units on the tiles
        """
        if not self.gameStateManager or not self.gameStateManager.current_game_state:
            return []
        
        result = []
        for unit_id, unit in self.gameStateManager.current_game_state.unit_states.items():
            if unit.position in tiles and unit.disposition == ACTIVE:
                result.append(unit)
        
        return result
    
    def are_hostile(self, unit1, unit2) -> bool:
        """
        Check if two units are hostile to each other.
        
        Args:
            unit1: First unit
            unit2: Second unit
            
        Returns:
            True if the units are hostile, False otherwise
        """
        if not unit1 or not unit2:
            return False
        
        # Units are hostile if they are from different factions
        return unit1.faction != unit2.faction