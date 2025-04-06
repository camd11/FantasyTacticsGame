"""
Combat System Module

This module orchestrates battles between units. It calculates the outcome of attacks based on unit stats,
equipment, skills, terrain, and support bonuses, following the specific mechanics of Thracia 776.
It determines hit rates, damage, critical hits, follow-up attacks, and applies the results.
"""

import logging
import random
from typing import Dict, List, Tuple, Optional, Any, Set, Union

# Import necessary modules/classes
from src.core_engine.game_state import GameStateManager, StatusEffectEnum
from src.core_engine.data_provider import DataProvider, ItemTypeEnum, WeaponTypeEnum
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.inventory_system import InventorySystem

# Constants
WEAPON = ItemTypeEnum.WEAPON
STAFF = ItemTypeEnum.STAFF
SCROLL = ItemTypeEnum.SCROLL

# Skill constants (would be defined in a proper enum in a real implementation)
WRATH = "WRATH"
ADEPT = "ADEPT"
MIRACLE = "MIRACLE"
NIHIL = "NIHIL"
SOL = "SOL"
LUNA = "LUNA"
PAVISE = "PAVISE"

class CombatSystem:
    """
    Orchestrates battles between units, calculating outcomes based on stats, equipment, skills, etc.
    """
    
    def __init__(self):
        """Initialize the CombatSystem."""
        self.gameStateManager = None
        self.dataProvider = None
        self.unitSystem = None
        self.mapSystem = None
        self.inventorySystem = None
    
    def initialize(self, gameStateManager_instance: GameStateManager, dataProvider_instance: DataProvider,
                  unitSystem_instance: UnitSystem, mapSystem_instance: MapSystem,
                  inventorySystem_instance: InventorySystem) -> None:
        """
        Initialize the CombatSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
            unitSystem_instance: Instance of the UnitSystem
            mapSystem_instance: Instance of the MapSystem
            inventorySystem_instance: Instance of the InventorySystem
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        self.unitSystem = unitSystem_instance
        self.mapSystem = mapSystem_instance
        self.inventorySystem = inventorySystem_instance
        logging.info("CombatSystem initialized.")
    
    # --- Combat Simulation (Forecast) ---
    
    def simulate_combat(self, attacker_id: str, defender_id: str, is_capture: bool = False) -> Dict[str, Any]:
        """
        Simulate combat between two units without applying changes.
        
        Args:
            attacker_id: ID of the attacking unit
            defender_id: ID of the defending unit
            is_capture: Whether this is a capture attempt
            
        Returns:
            Dictionary containing combat forecast data
        """
        attacker = self.gameStateManager.get_unit(attacker_id)
        defender = self.gameStateManager.get_unit(defender_id)
        if not attacker or not defender:
            logging.warning(f"Cannot simulate combat: One or both units not found")
            return None
        
        # Calculate stats for both units
        attacker_stats = self.unitSystem.calculate_current_combat_stats(attacker_id)
        defender_stats = self.unitSystem.calculate_current_combat_stats(defender_id)
        
        if is_capture:
            # Apply capture penalty to attacker's stats
            self._apply_capture_penalty_to_stats(attacker_stats)
        
        # Get weapon data
        attacker_weapon = self._get_equipped_weapon_data(attacker)
        defender_weapon = self._get_equipped_weapon_data(defender)
        
        # Calculate Attacker -> Defender forecast
        atk_hit, atk_dmg, atk_crit = self._calculate_single_attack_outcome(
            attacker, attacker_stats, attacker_weapon,
            defender, defender_stats, defender_weapon,
            is_first_hit=True, pcc_multiplier=attacker_stats.get('FCM', 1)
        )
        
        # Calculate Defender -> Attacker forecast (if defender can counter)
        def_hit, def_dmg, def_crit = 0, 0, 0
        if self._defender_can_counter(attacker, defender, defender_weapon):
            def_hit, def_dmg, def_crit = self._calculate_single_attack_outcome(
                defender, defender_stats, defender_weapon,
                attacker, attacker_stats, attacker_weapon,
                is_first_hit=True, pcc_multiplier=defender_stats.get('FCM', 1)
            )
        
        # Check doubling
        attacker_doubles = attacker_stats.get('AS', 0) >= defender_stats.get('AS', 0) + 4
        defender_doubles = defender_stats.get('AS', 0) >= attacker_stats.get('AS', 0) + 4
        
        forecast = {
            'attacker': {
                'dmg': atk_dmg,
                'hit': atk_hit,
                'crit': atk_crit,
                'doubles': attacker_doubles
            },
            'defender': {
                'dmg': def_dmg,
                'hit': def_hit,
                'crit': def_crit,
                'doubles': defender_doubles
            }
        }
        
        return forecast
    
    # --- Combat Execution ---
    
    def execute_combat(self, attacker_id: str, defender_id: str, is_capture: bool = False) -> List[Dict[str, Any]]:
        """
        Execute combat between two units.
        
        Args:
            attacker_id: ID of the attacking unit
            defender_id: ID of the defending unit
            is_capture: Whether this is a capture attempt
            
        Returns:
            List of strike results detailing the combat
        """
        attacker = self.gameStateManager.get_unit(attacker_id)
        defender = self.gameStateManager.get_unit(defender_id)
        if not attacker or not defender:
            logging.warning(f"Cannot execute combat: One or both units not found")
            return []
        
        logging.info(f"Executing combat: {attacker.name} vs {defender.name} {'(Capture)' if is_capture else ''}")
        
        # Store initial state for EXP calculation
        initial_attacker_hp = attacker.current_hp
        initial_defender_hp = defender.current_hp
        
        # Get base stats and weapon data
        attacker_stats_base = self.unitSystem.calculate_current_combat_stats(attacker_id)
        defender_stats_base = self.unitSystem.calculate_current_combat_stats(defender_id)
        attacker_weapon = self._get_equipped_weapon_data(attacker)
        defender_weapon = self._get_equipped_weapon_data(defender)
        
        # Apply capture penalty if needed
        attacker_stats = dict(attacker_stats_base)
        defender_stats = dict(defender_stats_base)
        if is_capture:
            self._apply_capture_penalty_to_stats(attacker_stats)
        
        # Determine combat sequence parameters
        attacker_doubles = attacker_stats.get('AS', 0) >= defender_stats.get('AS', 0) + 4
        defender_doubles = defender_stats.get('AS', 0) >= attacker_stats.get('AS', 0) + 4
        defender_can_ctr = self._defender_can_counter(attacker, defender, defender_weapon)
        
        # --- Combat Round ---
        combat_log = []  # Store events for display/result processing
        
        # 1. Attacker's First Strike(s)
        num_attacker_hits = 1
        if attacker_weapon and getattr(attacker_weapon, 'is_brave', False):
            num_attacker_hits = 2  # Brave weapons get two strikes
        
        for i in range(num_attacker_hits):
            if attacker.current_hp > 0 and defender.current_hp > 0:
                strike_result = self._perform_strike(
                    attacker, attacker_stats, attacker_weapon,
                    defender, defender_stats, defender_weapon,
                    is_follow_up=(i > 0)
                )
                combat_log.append(strike_result)
                if defender.current_hp <= 0:
                    break  # Stop if defender falls
        
        # 2. Defender's Counterattack(s)
        if defender.current_hp > 0 and attacker.current_hp > 0 and defender_can_ctr:
            num_defender_hits = 1
            # Check for Wrath activation
            has_wrath = self._unit_has_skill(defender_id, WRATH)
            
            for i in range(num_defender_hits):
                if attacker.current_hp > 0 and defender.current_hp > 0:
                    strike_result = self._perform_strike(
                        defender, defender_stats, defender_weapon,
                        attacker, attacker_stats, attacker_weapon,
                        is_follow_up=(i > 0), force_crit=has_wrath
                    )
                    combat_log.append(strike_result)
                    if attacker.current_hp <= 0:
                        break  # Stop if attacker falls
        
        # 3. Attacker's Follow-Up Strike
        if attacker.current_hp > 0 and defender.current_hp > 0 and attacker_doubles:
            strike_result = self._perform_strike(
                attacker, attacker_stats, attacker_weapon,
                defender, defender_stats, defender_weapon,
                is_follow_up=True
            )
            combat_log.append(strike_result)
        
        # 4. Defender's Follow-Up Strike
        if defender.current_hp > 0 and attacker.current_hp > 0 and defender_can_ctr and defender_doubles:
            has_wrath = self._unit_has_skill(defender_id, WRATH)
            strike_result = self._perform_strike(
                defender, defender_stats, defender_weapon,
                attacker, attacker_stats, attacker_weapon,
                is_follow_up=True, force_crit=has_wrath
            )
            combat_log.append(strike_result)
        
        # --- Post-Combat Updates ---
        
        # Check which units participated
        attacker_participated = any(r['attacker_id'] == attacker_id and r['did_attack'] for r in combat_log)
        defender_participated = any(r['attacker_id'] == defender_id and r['did_attack'] for r in combat_log)
        
        # Apply fatigue
        if attacker_participated:
            self.gameStateManager.update_fatigue(attacker_id, 1)
        if defender_participated:
            self.gameStateManager.update_fatigue(defender_id, 1)
        
        # Check final death/capture state
        attacker_survived = attacker.current_hp > 0
        defender_survived = defender.current_hp > 0
        
        if not defender_survived:
            if is_capture:
                self._set_unit_captured(defender_id, attacker_id)
                logging.info(f"{defender.name} captured by {attacker.name}!")
            else:
                self._set_unit_dead(defender_id)
                logging.info(f"{defender.name} defeated!")
        
        if not attacker_survived:
            self._set_unit_dead(attacker_id)
            logging.info(f"{attacker.name} defeated!")
        
        # Award EXP/WExp
        self._award_exp_wexp(
            combat_log, attacker_id, defender_id,
            initial_attacker_hp, initial_defender_hp,
            attacker_survived, defender_survived,
            is_capture
        )
        
        logging.info(f"Combat finished between {attacker.name} and {defender.name}")
        return combat_log
    
    # --- Staff Combat ---
    
    def execute_staff_attack(self, caster_id: str, target_id: str, staff_item_index: int) -> bool:
        """
        Execute a staff attack.
        
        Args:
            caster_id: ID of the casting unit
            target_id: ID of the target unit
            staff_item_index: Index of the staff in the caster's inventory
            
        Returns:
            True if the staff attack was successful, False otherwise
        """
        caster = self.gameStateManager.get_unit(caster_id)
        target = self.gameStateManager.get_unit(target_id)
        if not caster or not target or staff_item_index < 0 or staff_item_index >= len(caster.inventory):
            logging.warning(f"Cannot execute staff attack: Invalid units or staff index")
            return False
        
        # Get staff data
        staff_instance = caster.inventory[staff_item_index]
        staff_data = self.dataProvider.get_item_data(staff_instance.item_id)
        if not staff_data or staff_data.type != STAFF:
            logging.warning(f"Invalid staff: {staff_instance.item_id}")
            return False
        
        # Calculate staff hit rate
        caster_stats = self.unitSystem.calculate_current_combat_stats(caster_id)
        base_staff_hit = getattr(staff_data, 'base_hit', 60)  # Default to 60% for most staves
        staff_hit_rate = min(99, max(1, base_staff_hit + (4 * caster_stats.get('SKL', 0))))
        
        # Roll for hit
        hit_roll = random.randint(1, 100)
        hit_success = hit_roll <= staff_hit_rate
        
        if hit_success:
            # Apply staff effect
            self._apply_staff_effect(caster_id, target_id, staff_data)
            logging.info(f"{caster.name}'s {staff_data.name} hit {target.name}!")
        else:
            logging.info(f"{caster.name}'s {staff_data.name} missed {target.name}!")
        
        # Decrement staff durability
        self.inventorySystem.decrement_item_durability(caster_id, staff_item_index)
        
        # Update caster's fatigue based on staff rank
        fatigue_cost = self._get_staff_fatigue_cost(staff_data)
        self.gameStateManager.update_fatigue(caster_id, fatigue_cost)
        
        # Award WExp to caster
        self._apply_weapon_exp(caster_id, getattr(staff_data, 'weapon_type', None), 1)
        
        return hit_success
    
    # --- Helper Methods: Strike Execution ---
    
    def _perform_strike(self, striker, striker_stats, striker_weapon, target, target_stats, target_weapon,
                       is_follow_up=False, force_crit=False) -> Dict[str, Any]:
        """
        Perform a single strike in combat.
        
        Args:
            striker: The attacking unit
            striker_stats: Stats of the attacking unit
            striker_weapon: Weapon data of the attacking unit
            target: The defending unit
            target_stats: Stats of the defending unit
            target_weapon: Weapon data of the defending unit
            is_follow_up: Whether this is a follow-up attack
            force_crit: Whether to force a critical hit
            
        Returns:
            Dictionary containing the strike result
        """
        strike_log = {
            'attacker_id': striker.id,
            'target_id': target.id,
            'did_attack': True,
            'hit': False,
            'crit': False,
            'damage': 0,
            'skills_activated': []
        }
        
        if not striker_weapon:
            strike_log['did_attack'] = False
            return strike_log  # Cannot attack without weapon
        
        # Calculate Hit/Dmg/Crit for this specific strike
        hit_chance, base_dmg, crit_chance = self._calculate_single_attack_outcome(
            striker, striker_stats, striker_weapon,
            target, target_stats, target_weapon,
            is_first_hit=(not is_follow_up),
            pcc_multiplier=striker_stats.get('FCM', 1)
        )
        
        # Check for Miracle activation
        if self._unit_has_skill(target.id, MIRACLE) and target.current_hp <= 10:
            logging.info(f"{target.name}'s Miracle activated!")
            strike_log['skills_activated'].append(MIRACLE)
            hit_chance = 0  # Negates hit
        
        # Roll for hit
        hit_roll = random.randint(1, 100)
        if hit_roll <= hit_chance:
            strike_log['hit'] = True
            
            # Check for Pavise activation
            if self._unit_has_skill(target.id, PAVISE):
                # Roll for Pavise activation (Level%)
                if random.randint(1, 100) <= target.level:
                    logging.info(f"{target.name}'s Pavise activated!")
                    strike_log['skills_activated'].append(PAVISE)
                    base_dmg = 0  # Negates damage
            
            actual_dmg = base_dmg
            is_crit = False
            
            # Roll for critical hit - check Nihil first
            if base_dmg > 0 and not self._unit_has_skill(target.id, NIHIL):
                if force_crit or (random.randint(1, 100) <= crit_chance):
                    is_crit = True
                    actual_dmg *= 2  # Apply crit bonus
                    strike_log['crit'] = True
                    logging.info("Critical Hit!")
            
            # Check for Sol/Luna activation - check Nihil first
            if base_dmg > 0 and not self._unit_has_skill(target.id, NIHIL):
                if self._unit_has_skill(striker.id, LUNA):
                    # Roll for Luna activation (Skill%)
                    if random.randint(1, 100) <= striker_stats.get('SKL', 0):
                        logging.info(f"{striker.name}'s Luna activated!")
                        strike_log['skills_activated'].append(LUNA)
                        # Recalculate damage ignoring defense
                        actual_dmg = self._calculate_damage_ignoring_defense(
                            striker, striker_stats, striker_weapon,
                            target, target_stats, is_crit
                        )
                
                if self._unit_has_skill(striker.id, SOL):
                    # Roll for Sol activation (Skill%)
                    if random.randint(1, 100) <= striker_stats.get('SKL', 0):
                        logging.info(f"{striker.name}'s Sol activated!")
                        strike_log['skills_activated'].append(SOL)
                        self.gameStateManager.apply_healing(striker.id, actual_dmg)  # Heal for damage dealt
            
            # Apply final damage
            self.gameStateManager.apply_damage(target.id, actual_dmg)
            strike_log['damage'] = actual_dmg
            
            # Apply weapon status effects
            self._apply_weapon_status_effects(striker_weapon, target.id)
        
        else:  # Miss
            logging.info("Attack missed.")
            strike_log['hit'] = False
        
        # Decrement weapon durability
        if striker.equipped_weapon_index >= 0:
            self.inventorySystem.decrement_item_durability(striker.id, striker.equipped_weapon_index)
            
        # Check for Adept (Continue) skill activation
        if (strike_log['hit'] and
            striker.current_hp > 0 and
            target.current_hp > 0 and
            self._unit_has_skill(striker.id, ADEPT) and
            not self._unit_has_skill(target.id, NIHIL)):
            
            # Roll for Adept activation (Skill%)
            if random.randint(1, 100) <= striker_stats.get('SKL', 0):
                logging.info(f"{striker.name}'s Adept activated! Extra attack!")
                # Recursive call for extra attack, using follow-up rules for PCC
                adept_strike = self._perform_strike(
                    striker, striker_stats, striker_weapon,
                    target, target_stats, target_weapon,
                    is_follow_up=True, force_crit=force_crit
                )
                # Add Adept to skills activated in the original strike
                strike_log['skills_activated'].append(ADEPT)
                # Return both strikes as a list
                return [strike_log, adept_strike]
        
        return strike_log
    
    # --- Helper Methods: Combat Calculations ---
    
    def _calculate_single_attack_outcome(self, striker, striker_stats, striker_weapon,
                                        target, target_stats, target_weapon,
                                        is_first_hit=True, pcc_multiplier=1) -> Tuple[int, int, int]:
        """
        Calculate the outcome of a single attack.
        
        Args:
            striker: The attacking unit
            striker_stats: Stats of the attacking unit
            striker_weapon: Weapon data of the attacking unit
            target: The defending unit
            target_stats: Stats of the defending unit
            target_weapon: Weapon data of the defending unit
            is_first_hit: Whether this is the first hit
            pcc_multiplier: Pursuit Critical Coefficient multiplier
            
        Returns:
            Tuple of (hit_chance, damage, crit_chance)
        """
        if not striker_weapon:
            return 0, 0, 0
        
        # 1. Calculate Hit vs Avoid
        base_hit = striker_stats.get('hit', 0)
        target_avo = target_stats.get('avo', 0)
        
        # 2. Weapon Triangle
        wt_bonus = self._get_weapon_triangle_bonus(
            getattr(striker_weapon, 'weapon_type', None),
            getattr(target_weapon, 'weapon_type', None) if target_weapon else None
        )
        
        # 3. Final Hit Chance (Capped 1-99)
        hit_chance = max(1, min(99, base_hit - target_avo + wt_bonus))
        
        # 4. Calculate Damage
        effectiveness_mult = self._get_effectiveness_multiplier(
            getattr(striker_weapon, 'id', ''),
            getattr(target, 'class_id', '')
        )
        effective_might = getattr(striker_weapon, 'might', 0) * effectiveness_mult
        
        target_def = 0
        if self._is_weapon_physical(getattr(striker_weapon, 'weapon_type', None)):
            # Physical damage
            terrain_bonus = self.mapSystem.get_terrain_bonus(target.position).get('def', 0)
            target_def = target_stats.get('DEF', 0) + terrain_bonus
        else:
            # Magical damage
            target_def = target_stats.get('MAG', 0)  # Magic is used for magical defense in Thracia
        
        base_dmg = max(0, striker_stats.get('atk', 0) - target_def)
        
        # 5. Calculate Crit Chance
        base_crit = striker_stats.get('crit', 0)
        target_ddg = target_stats.get('ddg', 0)
        calculated_crit = max(0, base_crit - target_ddg)
        
        # Apply PCC / First Hit Cap / Scroll / Nihil rules
        crit_chance = 0
        if not self._unit_has_item_type(target.id, SCROLL) and not self._unit_has_skill(target.id, NIHIL):
            if is_first_hit:
                crit_chance = min(25, calculated_crit)  # First hit capped at 25%
            else:
                crit_chance = min(100, calculated_crit * pcc_multiplier)  # Follow-up uses PCC
        return hit_chance, base_dmg, crit_chance
    
    def _calculate_damage_ignoring_defense(self, striker, striker_stats, striker_weapon,
                                          target, target_stats, is_crit=False) -> int:
        """
        Calculate damage ignoring the target's defense (for Luna skill).
        
        Args:
            striker: The attacking unit
            striker_stats: Stats of the attacking unit
            striker_weapon: Weapon data of the attacking unit
            target: The defending unit
            target_stats: Stats of the defending unit
            is_crit: Whether this is a critical hit
            
        Returns:
            Calculated damage
        """
        effectiveness_mult = self._get_effectiveness_multiplier(
            getattr(striker_weapon, 'id', ''),
            getattr(target, 'class_id', '')
        )
        effective_might = getattr(striker_weapon, 'might', 0) * effectiveness_mult
        
        # For Luna, ignore defense completely
        damage = striker_stats.get('atk', 0)
        
        # Apply crit bonus if applicable
        if is_crit:
            damage *= 2
        
        return max(0, damage)
    
    # --- Helper Methods: Post-Combat ---
    
    def _award_exp_wexp(self, combat_log, attacker_id, defender_id,
                       initial_attacker_hp, initial_defender_hp,
                       attacker_survived, defender_survived,
                       is_capture=False) -> None:
        """
        Award experience and weapon experience after combat.
        
        Args:
            combat_log: List of strike results
            attacker_id: ID of the attacking unit
            defender_id: ID of the defending unit
            initial_attacker_hp: Initial HP of the attacker
            initial_defender_hp: Initial HP of the defender
            attacker_survived: Whether the attacker survived
            defender_survived: Whether the defender survived
            is_capture: Whether this was a capture attempt
        """
        attacker = self.gameStateManager.get_unit(attacker_id)
        defender = self.gameStateManager.get_unit(defender_id)
        if not attacker or not defender:
            return
        
        # Calculate damage dealt
        attacker_damage_dealt = initial_defender_hp - (defender.current_hp if defender_survived else 0)
        defender_damage_dealt = initial_attacker_hp - (attacker.current_hp if attacker_survived else 0)
        
        # Calculate EXP
        attacker_exp = self._calculate_exp(
            attacker, defender,
            attacker_damage_dealt, not defender_survived,
            is_capture
        )
        
        defender_exp = self._calculate_exp(
            defender, attacker,
            defender_damage_dealt, not attacker_survived,
            False  # Defender cannot capture
        )
        
        # Apply EXP
        if attacker_exp > 0:
            self._apply_experience(attacker_id, attacker_exp)
        
        if defender_exp > 0:
            self._apply_experience(defender_id, defender_exp)
        
        # Calculate and apply WExp
        attacker_weapon = self._get_equipped_weapon_data(attacker)
        defender_weapon = self._get_equipped_weapon_data(defender)
        
        # Count hits landed by each unit
        attacker_hits = sum(1 for r in combat_log if r['attacker_id'] == attacker_id and r['hit'])
        defender_hits = sum(1 for r in combat_log if r['attacker_id'] == defender_id and r['hit'])
        
        # Apply WExp (typically 1 per hit landed)
        if attacker_hits > 0 and attacker_weapon:
            self._apply_weapon_exp(attacker_id, getattr(attacker_weapon, 'weapon_type', None), attacker_hits)
        
        if defender_hits > 0 and defender_weapon:
            self._apply_weapon_exp(defender_id, getattr(defender_weapon, 'weapon_type', None), defender_hits)
    
    def _calculate_exp(self, unit, opponent, damage_dealt, defeated_opponent, is_capture=False) -> int:
        """
        Calculate experience gained from combat based on Fire Emblem standards.
        
        Args:
            unit: The unit gaining experience
            opponent: The opposing unit
            damage_dealt: Amount of damage dealt
            defeated_opponent: Whether the opponent was defeated
            is_capture: Whether this was a capture attempt
            
        Returns:
            Amount of experience gained
        """
        # Base EXP for combat participation
        base_exp = 1
        
        # Base EXP for hitting an enemy
        hit_exp = 10 if damage_dealt > 0 else 0
        
        # Level difference modifier
        # Higher bonus when defeating higher level enemies, penalty for lower level
        level_diff = opponent.level - unit.level
        level_modifier = max(-10, min(20, level_diff * 2))
        
        # Damage modifier - reward for dealing more damage
        damage_modifier = min(10, damage_dealt)
        
        # Defeat bonus - significant reward for defeating an enemy
        defeat_bonus = 30 if defeated_opponent else 0
        
        # Capture bonus - extra reward for successful capture
        capture_bonus = 20 if is_capture and defeated_opponent else 0
        
        # Boss bonus - check if opponent is a boss class
        is_boss = self._is_boss_unit(opponent)
        boss_bonus = 20 if is_boss and defeated_opponent else 0
        
        # Class bonus - some classes like thieves get less EXP
        class_modifier = self._get_class_exp_modifier(unit)
        
        # Total EXP calculation
        total_exp = (base_exp + hit_exp + level_modifier + damage_modifier +
                    defeat_bonus + capture_bonus + boss_bonus) * class_modifier
        
        # Cap at 100 EXP
        return min(100, max(1, int(total_exp)))
    
    def _is_boss_unit(self, unit) -> bool:
        """
        Check if a unit is considered a boss for EXP calculation.
        
        Args:
            unit: The unit to check
            
        Returns:
            True if the unit is a boss, False otherwise
        """
        # Check if the unit has boss flag or is a boss class
        # This would typically be stored in the unit data or class data
        boss_classes = ["Baron", "Emperor", "King", "Queen", "Overlord"]
        return hasattr(unit, 'is_boss') and unit.is_boss or unit.class_name in boss_classes
    
    def _get_class_exp_modifier(self, unit) -> float:
        """
        Get the EXP modifier based on unit class.
        
        Args:
            unit: The unit to check
            
        Returns:
            EXP modifier (1.0 for normal classes, less for special classes)
        """
        # Some classes like Thieves might get less EXP
        low_exp_classes = ["Thief", "Dancer", "Bard"]
        if unit.class_name in low_exp_classes:
            return 0.8
        return 1.0
    
    def _apply_experience(self, unit_id: str, exp_amount: int) -> None:
        """
        Apply experience to a unit.
        
        Args:
            unit_id: ID of the unit
            exp_amount: Amount of experience to apply
        """
        # This would typically call GameStateManager's method
        # For now, implement directly
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return
        
        logging.info(f"{unit.name} gained {exp_amount} EXP")
        
        # Add experience
        unit.experience += exp_amount
        
        # Check for level up
        while unit.experience >= 100:
            unit.experience -= 100
            self.unitSystem.trigger_level_up(unit_id)
    
    def _apply_weapon_exp(self, unit_id: str, weapon_type, wexp_amount: int) -> None:
        """
        Apply weapon experience to a unit based on Thracia 776 rules.
        
        Args:
            unit_id: ID of the unit
            weapon_type: Type of weapon
            wexp_amount: Amount of weapon experience to apply
        """
        if not weapon_type:
            return
        
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return
        
        # Check if unit has this weapon type
        if weapon_type not in unit.weapon_exp:
            return
        
        # In Thracia, WExp gain is based on weapon/staff rank
        # For weapons: +1 WExp per hit
        # For staves: varies by rank (E: +1, D: +2, C: +3, B: +4, A: +5)
        adjusted_wexp = wexp_amount
        
        # If it's a staff, adjust WExp based on rank
        if self._is_staff_type(weapon_type):
            rank = unit.weapon_ranks.get(weapon_type, 'E')
            rank_multipliers = {'E': 1, 'D': 2, 'C': 3, 'B': 4, 'A': 5, '*': 5}
            adjusted_wexp = wexp_amount * rank_multipliers.get(rank, 1)
        
        # Add weapon experience
        unit.weapon_exp[weapon_type] += adjusted_wexp
        logging.info(f"{unit.name} gained {adjusted_wexp} WExp in {weapon_type}")
        
        # Check for rank up and trigger it
        self.unitSystem.trigger_weapon_rank_up(unit_id, weapon_type)
    
    def _is_staff_type(self, weapon_type) -> bool:
        """
        Check if a weapon type is a staff.
        
        Args:
            weapon_type: Type of weapon to check
            
        Returns:
            True if the weapon type is a staff, False otherwise
        """
        # This would depend on how weapon types are defined in your system
        return weapon_type == WeaponTypeEnum.STAFF
    
    def _apply_staff_effect(self, caster_id: str, target_id: str, staff_data) -> None:
        """
        Apply the effect of a staff.
        
        Args:
            caster_id: ID of the casting unit
            target_id: ID of the target unit
            staff_data: Data of the staff
        """
        # This would be implemented based on staff effects
        # For now, just log the effect
        logging.info(f"Applied staff effect from {caster_id} to {target_id}")
        
        # Example implementation for common staff effects
        if hasattr(staff_data, 'effects'):
            for effect in staff_data.effects:
                effect_type = effect.get('type')
                
                if effect_type == 'HEAL':
                    # Healing staff
                    amount = effect.get('amount', 10)
                    self.gameStateManager.apply_healing(target_id, amount)
                    
                elif effect_type == 'STATUS':
                    # Status staff (Sleep, Silence, etc.)
                    status = effect.get('status')
                    duration = effect.get('duration', 3)
                    if status:
                        status_enum = getattr(StatusEffectEnum, status, None)
                        if status_enum:
                            self.gameStateManager.add_status_effect(target_id, status_enum, duration)
                
                elif effect_type == 'WARP':
                    # Warp staff (would need position data)
                    pass
    
    def _apply_weapon_status_effects(self, weapon_data, target_id: str) -> None:
        """
        Apply status effects from a weapon.
        
        Args:
            weapon_data: Data of the weapon
            target_id: ID of the target unit
        """
        # This would be implemented based on weapon effects
        # For now, just check for poison effect as an example
        if hasattr(weapon_data, 'effects'):
            for effect in weapon_data.effects:
                if effect.get('type') == 'POISON':
                    self.gameStateManager.add_status_effect(
                        target_id, StatusEffectEnum.POISON,
                        effect.get('duration', 3),
                        effect.get('magnitude', 0)
                    )
    
    def _get_staff_fatigue_cost(self, staff_data) -> int:
        """
        Get the fatigue cost for using a staff.
        
        Args:
            staff_data: Data of the staff
            
        Returns:
            Fatigue cost
        """
        # Fatigue cost based on staff rank
        rank_costs = {
            'E': 1,
            'D': 2,
            'C': 3,
            'B': 4,
            'A': 5,
            'S': 6
        }
        
        rank = getattr(staff_data, 'required_rank', 'E')
        return rank_costs.get(str(rank), 1)
    
    # --- Helper Methods: Utility ---
    
    def _get_equipped_weapon_data(self, unit) -> Optional[Any]:
        """
        Get the data for a unit's equipped weapon.
        
        Args:
            unit: The unit
            
        Returns:
            Weapon data or None if no weapon is equipped
        """
        if not unit or unit.equipped_weapon_index < 0 or unit.equipped_weapon_index >= len(unit.inventory):
            return None
        
        item_instance = unit.inventory[unit.equipped_weapon_index]
        return self.dataProvider.get_item_data(item_instance.item_id)
    
    def _defender_can_counter(self, attacker, defender, defender_weapon) -> bool:
        """
        Check if the defender can counter the attacker.
        
        Args:
            attacker: The attacking unit
            defender: The defending unit
            defender_weapon: The defender's weapon data
            
        Returns:
            True if the defender can counter, False otherwise
        """
        if not defender_weapon:
            return False
        
        attacker_weapon = self._get_equipped_weapon_data(attacker)
        if not attacker_weapon:
            return False
        
        # Check if defender has a weapon
        if defender.equipped_weapon_index < 0:
            return False
        
        # Check if defender's weapon is broken
        if defender_weapon.max_durability > 0 and defender.inventory[defender.equipped_weapon_index].current_durability <= 0:
            return False
        
        # Check range
        attacker_range = self._calculate_distance(attacker.position, defender.position)
        defender_min_range = getattr(defender_weapon, 'range_min', 1)
        defender_max_range = getattr(defender_weapon, 'range_max', 1)
        
        return defender_min_range <= attacker_range <= defender_max_range
    
    def _apply_capture_penalty_to_stats(self, stats: Dict[str, Any]) -> None:
        """
        Apply capture penalty to stats.
        
        Args:
            stats: Stats to modify
        """
        # In Thracia 776, capturing halves Str, Mag, Skl, Spd, Def
        for stat in ['STR', 'MAG', 'SKL', 'SPD', 'DEF']:
            if stat in stats:
                stats[stat] //= 2
        
        # Recalculate derived stats
        if 'atk' in stats:
            # This is a simplification; actual recalculation would depend on weapon
            stats['atk'] //= 2
        
        if 'AS' in stats and 'SPD' in stats:
            # Recalculate AS based on new SPD
            stats['AS'] = stats['SPD']  # Simplified; would need to account for weapon weight
    
    def _set_unit_dead(self, unit_id: str) -> None:
        """
        Set a unit as dead.
        
        Args:
            unit_id: ID of the unit
        """
        # This would typically call GameStateManager's method
        unit = self.gameStateManager.get_unit(unit_id)
        if unit:
            unit.disposition = "DEAD"  # Use proper enum in real implementation
    
    def _set_unit_captured(self, captive_id: str, captor_id: str) -> None:
        """
        Set a unit as captured.
        
        Args:
            captive_id: ID of the captured unit
            captor_id: ID of the capturing unit
        """
        # This would typically call GameStateManager's method
        captive = self.gameStateManager.get_unit(captive_id)
        captor = self.gameStateManager.get_unit(captor_id)
        if captive and captor:
            captive.is_captured = True
            captor.carrying_unit_id = captive_id
    
    def _unit_has_skill(self, unit_id: str, skill_id: str) -> bool:
        """
        Check if a unit has a specific skill.
        
        Args:
            unit_id: ID of the unit
            skill_id: ID of the skill
            
        Returns:
            True if the unit has the skill, False otherwise
        """
        # Use DataProvider to check if the unit has the skill
        return self.dataProvider.unit_has_skill(unit_id, skill_id)
    
    def _unit_has_item_type(self, unit_id: str, item_type) -> bool:
        """
        Check if a unit has an item of a specific type.
        
        Args:
            unit_id: ID of the unit
            item_type: Type of item
            
        Returns:
            True if the unit has an item of the specified type, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return False
        
        for item_instance in unit.inventory:
            item_data = self.dataProvider.get_item_data(item_instance.item_id)
            if item_data and item_data.type == item_type:
                return True
        
        return False
    
    def _get_weapon_triangle_bonus(self, attacker_type, defender_type) -> int:
        """
        Get the weapon triangle bonus.
        
        Args:
            attacker_type: Type of the attacker's weapon
            defender_type: Type of the defender's weapon
            
        Returns:
            Weapon triangle bonus
        """
        if not attacker_type or not defender_type:
            return 0
        
        return self.dataProvider.get_weapon_triangle_bonus(attacker_type, defender_type)
    
    def _get_effectiveness_multiplier(self, weapon_id: str, class_id: str) -> int:
        """
        Get the effectiveness multiplier for a weapon against a class.
        
        Args:
            weapon_id: ID of the weapon
            class_id: ID of the class
            
        Returns:
            Effectiveness multiplier (typically 1 or 3)
        """
        # Use DataProvider to check weapon effectiveness against class
        # In Thracia 776, effective weapons deal 3x might
        return self.dataProvider.get_effectiveness_multiplier(weapon_id, class_id)
    
    def _is_weapon_physical(self, weapon_type) -> bool:
        """
        Check if a weapon type is physical.
        
        Args:
            weapon_type: Type of weapon
            
        Returns:
            True if the weapon is physical, False otherwise
        """
        physical_types = [WeaponTypeEnum.SWORD, WeaponTypeEnum.LANCE, WeaponTypeEnum.AXE, WeaponTypeEnum.BOW]
        return weapon_type in physical_types
    
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
