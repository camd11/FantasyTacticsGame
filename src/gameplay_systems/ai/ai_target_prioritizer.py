"""
Thracia 776 AI Target Prioritizer Module

This module implements the canonical targeting priorities from Fire Emblem: Thracia 776,
determining how AI units select which enemy units to prioritize in combat.

According to the Thracia 776 documentation, AI units prioritize targets in this order:
1. Units they can defeat in one round
2. Units they can damage significantly
3. Units that cannot counter-attack
4. Units with low HP or low Def/Mag
5. Special targets based on chapter objectives (e.g., Lord units)
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import math

class ThraciaTargetPrioritizer:
    """
    Implements the Fire Emblem Thracia 776 enemy targeting prioritization system.
    
    Main targeting priorities (in descending order):
    1. Units that can be defeated in one round of combat
    2. Units that would take significant damage
    3. Units that cannot counter-attack
    4. Units with low HP or low defensive stats
    5. Special targeting based on unit roles/chapter objectives
    """
    
    def __init__(self):
        """Initialize the prioritizer with default weights"""
        self.logger = logging.getLogger(__name__)
        
        # Weights for different targeting factors (higher = more important)
        self.weights = {
            "can_defeat": 100,        # Can defeat in one round
            "damage_ratio": 80,       # Damage as % of target's HP
            "no_counter": 70,         # Target cannot counter-attack
            "low_hp_ratio": 60,       # Target has low HP %
            "low_def": 50,            # Target has low defensive stats
            "weapon_advantage": 40,   # Has weapon triangle advantage
            "class_priority": 30,     # Priority based on unit class
            "leadership": 20,         # Target is a leader unit
            "distance": 10            # Distance to target (inverse)
        }
        
    def prioritize_targets(self, ai_unit, enemy_units, game_state, combat_system, ai_persona=None) -> List[Tuple[Any, float]]:
        """
        Prioritize potential targets based on Thracia 776 targeting logic.
        
        Args:
            ai_unit: The AI unit doing the targeting
            enemy_units: List of potential enemy targets
            game_state: Current game state for context
            combat_system: Combat system for damage calculations
            ai_persona: Optional AI persona to influence priorities
            
        Returns:
            List[Tuple[unit, score]]: Prioritized list of targets with scores
        """
        if not enemy_units:
            return []
            
        scored_targets = []
        
        # Adjust weights based on persona if available
        adjusted_weights = self._adjust_weights_for_persona(ai_persona)
        
        for target in enemy_units:
            # Skip defeated units
            if hasattr(target, 'is_defeated') and target.is_defeated:
                continue
                
            # Calculate base score
            score = 0
            
            # Factor 1: Can defeat in one round
            can_defeat = self._can_defeat_in_one_round(ai_unit, target, combat_system)
            if can_defeat:
                score += adjusted_weights["can_defeat"]
                
            # Factor 2: Damage ratio (damage dealt as % of target's HP)
            damage_ratio = self._calculate_damage_ratio(ai_unit, target, combat_system)
            score += adjusted_weights["damage_ratio"] * damage_ratio
            
            # Factor 3: No counter-attack
            if self._cannot_counter(ai_unit, target, combat_system):
                score += adjusted_weights["no_counter"]
                
            # Factor 4: Low HP ratio
            hp_ratio = self._calculate_hp_ratio(target)
            low_hp_score = adjusted_weights["low_hp_ratio"] * (1 - hp_ratio)
            score += low_hp_score
                
            # Factor 5: Low defensive stats
            def_score = self._calculate_defensive_vulnerability(ai_unit, target)
            score += adjusted_weights["low_def"] * def_score
                
            # Factor 6: Weapon advantage
            if self._has_weapon_advantage(ai_unit, target):
                score += adjusted_weights["weapon_advantage"]
                
            # Factor 7: Class priority
            class_score = self._get_class_priority_score(target)
            score += adjusted_weights["class_priority"] * class_score
                
            # Factor 8: Leadership
            if self._is_leader_unit(target):
                score += adjusted_weights["leadership"]
                
            # Factor 9: Distance (inverse - closer is better)
            distance_factor = self._calculate_distance_factor(ai_unit, target)
            score += adjusted_weights["distance"] * distance_factor
                
            # Add to scored list
            scored_targets.append((target, score))
            
        # Sort targets by score (highest first)
        sorted_targets = sorted(scored_targets, key=lambda x: x[1], reverse=True)
        
        # Log the top 3 targets for debugging
        if sorted_targets:
            debug_str = "Top 3 Thracia prioritized targets:\n"
            for i, (unit, score) in enumerate(sorted_targets[:3]):
                debug_str += f"  {i+1}. Unit ID: {unit.id}, Score: {score:.2f}\n"
            self.logger.debug(debug_str)
            
        return sorted_targets
        
    def _adjust_weights_for_persona(self, persona) -> Dict[str, float]:
        """Adjust targeting weights based on AI persona"""
        adjusted = self.weights.copy()
        
        if not persona:
            return adjusted
            
        # Adjust based on persona type
        if hasattr(persona, 'type'):
            persona_type = persona.type
            
            if persona_type == "AGGRESSOR":
                adjusted["can_defeat"] *= 1.2
                adjusted["damage_ratio"] *= 1.2
                adjusted["weapon_advantage"] *= 1.3
            elif persona_type == "DEFENDER":
                adjusted["low_hp_ratio"] *= 0.8
                adjusted["distance"] *= 1.3
            elif persona_type == "SUPPORT":
                adjusted["class_priority"] *= 1.5
                adjusted["leadership"] *= 1.5
            elif persona_type == "OBJECTIVE-FOCUSED":
                adjusted["leadership"] *= 2.0
                
        # Adjust based on specific weights if available
        if hasattr(persona, 'tactical_weights'):
            weights = persona.tactical_weights
            
            if "target_defeat_priority" in weights:
                adjusted["can_defeat"] *= weights["target_defeat_priority"]
                
            if "target_damage_priority" in weights:
                adjusted["damage_ratio"] *= weights["target_damage_priority"]
                
            if "target_vulnerability_priority" in weights:
                adjusted["no_counter"] *= weights["target_vulnerability_priority"]
                adjusted["low_def"] *= weights["target_vulnerability_priority"]
                
            if "target_class_priority" in weights:
                adjusted["class_priority"] *= weights["target_class_priority"]
                
            if "target_leader_priority" in weights:
                adjusted["leadership"] *= weights["target_leader_priority"]
                
        return adjusted
        
    def _can_defeat_in_one_round(self, attacker, defender, combat_system) -> bool:
        """Check if attacker can defeat defender in one round of combat"""
        try:
            # Attempt to use combat system for prediction
            if hasattr(combat_system, 'predict_combat'):
                prediction = combat_system.predict_combat(attacker, defender)
                if hasattr(prediction, 'defender_hp_remaining'):
                    return prediction.defender_hp_remaining <= 0
                    
            # Fallback calculation
            attacker_stats = getattr(attacker, 'battle_stats', getattr(attacker, 'stats', {}))
            defender_stats = getattr(defender, 'battle_stats', getattr(defender, 'stats', {}))
            
            # Get attacker's damage and number of attacks
            atk = attacker_stats.get('ATK', 0)
            spd = attacker_stats.get('SPD', 0)
            defender_hp = defender_stats.get('HP', 100)
            defender_def = defender_stats.get('DEF', 0)
            
            # Calculate damage per hit
            damage_per_hit = max(0, atk - defender_def)
            
            # Determine number of attacks (double attack if speed difference >= 4)
            num_attacks = 2 if spd >= (defender_stats.get('SPD', 0) + 4) else 1
            
            # Calculate total damage
            total_damage = damage_per_hit * num_attacks
            
            return total_damage >= defender_hp
            
        except Exception as e:
            self.logger.warning(f"Error in defeat calculation: {e}")
            return False
            
    def _calculate_damage_ratio(self, attacker, defender, combat_system) -> float:
        """Calculate expected damage as ratio of defender's HP"""
        try:
            # Attempt to use combat system for prediction
            if hasattr(combat_system, 'predict_combat'):
                prediction = combat_system.predict_combat(attacker, defender)
                if hasattr(prediction, 'damage_to_defender') and hasattr(prediction, 'defender_max_hp'):
                    return min(1.0, prediction.damage_to_defender / max(1, prediction.defender_max_hp))
                    
            # Fallback calculation
            attacker_stats = getattr(attacker, 'battle_stats', getattr(attacker, 'stats', {}))
            defender_stats = getattr(defender, 'battle_stats', getattr(defender, 'stats', {}))
            
            # Get attacker's damage and number of attacks
            atk = attacker_stats.get('ATK', 0)
            spd = attacker_stats.get('SPD', 0)
            defender_hp = defender_stats.get('HP', 100)
            defender_def = defender_stats.get('DEF', 0)
            
            # Calculate damage per hit
            damage_per_hit = max(0, atk - defender_def)
            
            # Determine number of attacks (double attack if speed difference >= 4)
            num_attacks = 2 if spd >= (defender_stats.get('SPD', 0) + 4) else 1
            
            # Calculate total damage
            total_damage = damage_per_hit * num_attacks
            
            return min(1.0, total_damage / max(1, defender_hp))
            
        except Exception as e:
            self.logger.warning(f"Error in damage ratio calculation: {e}")
            return 0.0
            
    def _cannot_counter(self, attacker, defender, combat_system) -> bool:
        """Check if defender cannot counter-attack"""
        try:
            # First check with combat system
            if hasattr(combat_system, 'can_counter_attack'):
                return not combat_system.can_counter_attack(defender, attacker)
                
            # Fallback: check if defender has a weapon
            if hasattr(defender, 'equipment'):
                return not defender.equipment.get('weapon')
                
            # Another fallback check
            if hasattr(defender, 'has_equipped_weapon'):
                return not defender.has_equipped_weapon()
                
            return False
            
        except Exception as e:
            self.logger.warning(f"Error in counter-attack calculation: {e}")
            return False
            
    def _calculate_hp_ratio(self, unit) -> float:
        """Calculate unit's current HP as a ratio of max HP"""
        try:
            current_hp = getattr(unit, 'current_hp', getattr(unit, 'hp', 0))
            max_hp = getattr(unit, 'max_hp', getattr(unit, 'stats', {}).get('HP', 100))
            
            return min(1.0, current_hp / max(1, max_hp))
            
        except Exception as e:
            self.logger.warning(f"Error in HP ratio calculation: {e}")
            return 1.0
            
    def _calculate_defensive_vulnerability(self, attacker, defender) -> float:
        """Calculate how vulnerable defender is based on their defensive stats"""
        try:
            # Get attacker's offensive and defender's defensive stats
            attacker_stats = getattr(attacker, 'battle_stats', getattr(attacker, 'stats', {}))
            defender_stats = getattr(defender, 'battle_stats', getattr(defender, 'stats', {}))
            
            # Determine if attacker is physical or magical
            is_physical = True
            if hasattr(attacker, 'equipment') and attacker.equipment.get('weapon'):
                is_physical = attacker.equipment['weapon'].get('attack_type', 'physical') == 'physical'
            
            # Get relevant defensive stat
            if is_physical:
                def_stat = defender_stats.get('DEF', 0)
            else:
                def_stat = defender_stats.get('RES', defender_stats.get('DEF', 0))
                
            # Calculate vulnerability score (0 to 1)
            # Lower defense = higher vulnerability score
            max_expected_def = 30  # Maximum expected defense value
            vulnerability = 1.0 - (def_stat / max_expected_def)
            
            return max(0.0, min(1.0, vulnerability))
            
        except Exception as e:
            self.logger.warning(f"Error in defensive vulnerability calculation: {e}")
            return 0.5
            
    def _has_weapon_advantage(self, attacker, defender) -> bool:
        """Check if attacker has weapon triangle advantage over defender"""
        try:
            # First check with combat system if it has this capability
            if hasattr(attacker, 'has_weapon_advantage'):
                return attacker.has_weapon_advantage(defender)
                
            # Fallback: check weapon types
            if hasattr(attacker, 'equipment') and hasattr(defender, 'equipment'):
                attacker_weapon = attacker.equipment.get('weapon', {})
                defender_weapon = defender.equipment.get('weapon', {})
                
                attacker_type = attacker_weapon.get('type', '')
                defender_type = defender_weapon.get('type', '')
                
                # Basic weapon triangle: sword > axe > lance > sword
                if attacker_type == 'sword' and defender_type == 'axe':
                    return True
                elif attacker_type == 'axe' and defender_type == 'lance':
                    return True
                elif attacker_type == 'lance' and defender_type == 'sword':
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.warning(f"Error in weapon advantage calculation: {e}")
            return False
            
    def _get_class_priority_score(self, unit) -> float:
        """Get priority score based on unit class (0.0 to 1.0)"""
        try:
            unit_class = getattr(unit, 'unit_class', getattr(unit, 'class_type', None))
            
            if not unit_class:
                return 0.5
                
            # Class priorities based on Thracia 776 logic
            high_priority_classes = ['mage', 'priest', 'cleric', 'sage', 'bishop', 'druid', 'summoner', 'thief', 'dancer', 'bard']
            medium_priority_classes = ['archer', 'sniper', 'nomad', 'warrior', 'hero', 'paladin', 'wyvern rider', 'pegasus knight']
            
            if isinstance(unit_class, str):
                unit_class = unit_class.lower()
                
                if unit_class in high_priority_classes:
                    return 1.0
                elif unit_class in medium_priority_classes:
                    return 0.75
                    
            return 0.5
            
        except Exception as e:
            self.logger.warning(f"Error in class priority calculation: {e}")
            return 0.5
            
    def _is_leader_unit(self, unit) -> bool:
        """Check if unit is a leader unit (boss, commander, etc.)"""
        try:
            # Check if unit has leadership flag
            if hasattr(unit, 'is_leader'):
                return unit.is_leader
                
            # Check if unit has boss flag
            if hasattr(unit, 'is_boss'):
                return unit.is_boss
                
            # Check unit tags
            if hasattr(unit, 'tags'):
                return any(tag in ['leader', 'boss', 'commander', 'vip'] for tag in unit.tags)
                
            return False
            
        except Exception as e:
            self.logger.warning(f"Error in leader check: {e}")
            return False
            
    def _calculate_distance_factor(self, ai_unit, target_unit) -> float:
        """Calculate distance factor (inverse distance - closer is better)"""
        try:
            ai_pos = ai_unit.position
            target_pos = target_unit.position
            
            # Calculate Manhattan distance
            distance = abs(ai_pos[0] - target_pos[0]) + abs(ai_pos[1] - target_pos[1])
            
            # Convert to a 0-1 score (closer = higher score)
            max_expected_distance = 20  # Maximum expected distance on map
            distance_factor = 1.0 - (min(distance, max_expected_distance) / max_expected_distance)
            
            return distance_factor
            
        except Exception as e:
            self.logger.warning(f"Error in distance calculation: {e}")
            return 0.5 