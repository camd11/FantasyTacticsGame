#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for status effect mechanics.
This test covers applying, removing, and turn-based status effects.
"""

import os
import sys
import random
import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, PROJECT_ROOT)

# Define enums
class FactionEnum(Enum):
    PLAYER = 1
    ENEMY = 2
    NPC = 3

class DispositionEnum(Enum):
    ACTIVE = 1
    DEAD = 2
    ESCAPED = 3
    RETREATED = 4

class StatusEffectEnum(Enum):
    POISON = 1
    SLEEP = 2
    SILENCE = 3
    BERSERK = 4
    STAT_BOOST = 5

# Define simplified state classes
class StatusEffect:
    """Simplified status effect for testing."""
    def __init__(self, type, duration, magnitude=0):
        self.type = type
        self.duration = duration  # turns remaining (-1 for permanent)
        self.magnitude = magnitude  # for stat boosts
        self.applied_at_turn = 0

class UnitState:
    """Simplified unit state for testing."""
    def __init__(self):
        self.id = ""
        self.name = ""
        self.faction = None
        self.position = (0, 0)
        self.current_hp = 0
        self.max_hp = 0
        self.base_stats = {}
        self.status_effects = []
        self.can_act = True
        self.can_move = True
        self.can_use_items = True
        self.can_use_skills = True
        self.disposition = DispositionEnum.ACTIVE
    
    def get_status_effect(self, status_type):
        """Get a status effect by type."""
        for effect in self.status_effects:
            if effect.type == status_type:
                return effect
        return None
    
    def has_status_effect(self, status_type):
        """Check if the unit has a specific status effect."""
        return self.get_status_effect(status_type) is not None
    
    def add_status_effect(self, effect):
        """Add a status effect to the unit."""
        # Remove existing effect of the same type
        self.remove_status_effect(effect.type)
        self.status_effects.append(effect)
        
        # Apply effect to unit attributes
        self._apply_status_effect_attributes(effect)
    
    def remove_status_effect(self, status_type):
        """Remove a status effect from the unit."""
        effect = self.get_status_effect(status_type)
        if effect:
            # Remove effect from unit attributes
            self._remove_status_effect_attributes(effect)
            self.status_effects = [e for e in self.status_effects if e.type != status_type]
            return True
        return False
    
    def update_status_effects(self, current_turn):
        """Update status effects for the new turn, removing expired ones."""
        effects_to_remove = []
        
        for effect in self.status_effects:
            if effect.duration > 0:
                turns_elapsed = current_turn - effect.applied_at_turn
                if turns_elapsed >= effect.duration:
                    effects_to_remove.append(effect.type)
        
        # Remove expired effects
        for status_type in effects_to_remove:
            self.remove_status_effect(status_type)
        
        return effects_to_remove
    
    def _apply_status_effect_attributes(self, effect):
        """Apply the attributes of a status effect to the unit."""
        if effect.type == StatusEffectEnum.POISON:
            # No immediate effect, damage on turn start
            pass
        elif effect.type == StatusEffectEnum.SLEEP:
            self.can_act = False
            self.can_move = False
        elif effect.type == StatusEffectEnum.SILENCE:
            self.can_use_skills = False
        elif effect.type == StatusEffectEnum.BERSERK:
            self.can_act = False  # Unit acts on its own
        elif effect.type == StatusEffectEnum.STAT_BOOST:
            # Stat boosts are applied when getting stats
            pass
    
    def _remove_status_effect_attributes(self, effect):
        """Remove the attributes of a status effect from the unit."""
        if effect.type == StatusEffectEnum.POISON:
            # No immediate effect to remove
            pass
        elif effect.type == StatusEffectEnum.SLEEP:
            self.can_act = True
            self.can_move = True
        elif effect.type == StatusEffectEnum.SILENCE:
            self.can_use_skills = True
        elif effect.type == StatusEffectEnum.BERSERK:
            self.can_act = True
        elif effect.type == StatusEffectEnum.STAT_BOOST:
            # Stat boosts are removed when getting stats
            pass
    
    def get_stat(self, stat_name):
        """Get a unit's stat, including effects from status effects."""
        base_value = self.base_stats.get(stat_name, 0)
        
        # Apply stat boosts from status effects
        for effect in self.status_effects:
            if effect.type == StatusEffectEnum.STAT_BOOST and effect.magnitude != 0:
                base_value += effect.magnitude
        
        return base_value

class GameStateManager:
    """Simplified game state manager for testing."""
    def __init__(self):
        self.units = {}
        self.current_turn = 1
    
    def get_unit(self, unit_id):
        """Get a unit by ID."""
        return self.units.get(unit_id)
    
    def advance_turn(self):
        """Advance to the next turn and process status effects."""
        self.current_turn += 1
        
        # Update status effects for all units
        for unit in self.units.values():
            # Process poison damage
            poison_effect = unit.get_status_effect(StatusEffectEnum.POISON)
            if poison_effect:
                unit.current_hp = max(1, unit.current_hp - poison_effect.magnitude)
            
            # Update status durations
            unit.update_status_effects(self.current_turn)
            
            # Handle sleep state chance of waking up
            sleep_effect = unit.get_status_effect(StatusEffectEnum.SLEEP)
            if sleep_effect:
                # 30% chance to wake up each turn
                if random.random() < 0.3:
                    unit.remove_status_effect(StatusEffectEnum.SLEEP)
    
    def apply_status_effect(self, unit_id, status_type, duration, magnitude=0):
        """Apply a status effect to a unit."""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        effect = StatusEffect(status_type, duration, magnitude)
        effect.applied_at_turn = self.current_turn
        unit.add_status_effect(effect)
        return True
    
    def remove_status_effect(self, unit_id, status_type):
        """Remove a status effect from a unit."""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        return unit.remove_status_effect(status_type)

class StatusEffectsSystem:
    """Simplified status effects system for testing."""
    def __init__(self):
        self.game_state_manager = None
    
    def initialize(self, game_state_manager):
        """Initialize the status effects system with a game state manager."""
        self.game_state_manager = game_state_manager
    
    def apply_poison(self, target_id, duration, damage_per_turn):
        """Apply poison status to a target."""
        return self.game_state_manager.apply_status_effect(
            target_id, StatusEffectEnum.POISON, duration, damage_per_turn
        )
    
    def apply_sleep(self, target_id, duration):
        """Apply sleep status to a target."""
        return self.game_state_manager.apply_status_effect(
            target_id, StatusEffectEnum.SLEEP, duration
        )
    
    def apply_silence(self, target_id, duration):
        """Apply silence status to a target."""
        return self.game_state_manager.apply_status_effect(
            target_id, StatusEffectEnum.SILENCE, duration
        )
    
    def apply_berserk(self, target_id, duration):
        """Apply berserk status to a target."""
        return self.game_state_manager.apply_status_effect(
            target_id, StatusEffectEnum.BERSERK, duration
        )
    
    def apply_stat_boost(self, target_id, duration, boost_amount):
        """Apply stat boost status to a target."""
        return self.game_state_manager.apply_status_effect(
            target_id, StatusEffectEnum.STAT_BOOST, duration, boost_amount
        )
    
    def cure_status(self, target_id, status_type):
        """Cure a specific status effect."""
        return self.game_state_manager.remove_status_effect(target_id, status_type)
    
    def cure_all_status(self, target_id):
        """Cure all status effects."""
        unit = self.game_state_manager.get_unit(target_id)
        if not unit:
            return False
        
        status_types = [effect.type for effect in unit.status_effects]
        for status_type in status_types:
            unit.remove_status_effect(status_type)
        
        return True

class MockGameStateManager(GameStateManager):
    """Mock game state manager for testing status effect mechanics."""
    def __init__(self):
        super().__init__()
        self.units = {}
        self.random = random.Random(42)  # Fixed seed for deterministic tests
        
    def add_unit(self, unit):
        """Add a unit to the game state."""
        self.units[unit.id] = unit
        return unit.id
        
    def get_all_units(self):
        """Return all units in the game state."""
        return list(self.units.values())

class VisualScenarioLogger:
    """Simplified logger for tests."""
    def __init__(self, game_state_manager, log_dir=None):
        self.game_state_manager = game_state_manager
        self.log_dir = log_dir
        self.log_file = None
        self.log_buffer = []
    
    def set_log_file(self, log_path):
        """Set the log file path and write any buffered logs."""
        self.log_file = log_path
        # Write any buffered logs
        if self.log_buffer:
            with open(self.log_file, 'w') as f:
                f.write('\n'.join(self.log_buffer))
            self.log_buffer = []
    
    def log(self, message):
        """Log a message."""
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"{message}\n")
        else:
            self.log_buffer.append(message)
    
    def log_initial_state(self, title):
        """Log the initial state of the game."""
        self.log(f"=== {title} ===")
        self.log(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("")
    
    def log_unit_status(self, unit):
        """Log a unit's status."""
        self.log(f"{unit.name} (ID: {unit.id}): HP {unit.current_hp}/{unit.max_hp}")
        self.log(f"  Can act: {unit.can_act}, Can move: {unit.can_move}, Can use skills: {unit.can_use_skills}")
        
        if unit.status_effects:
            status_list = []
            for effect in unit.status_effects:
                duration_text = "Permanent" if effect.duration < 0 else f"{effect.duration} turns"
                magnitude_text = f" ({effect.magnitude})" if effect.magnitude != 0 else ""
                status_list.append(f"{effect.type.name}{magnitude_text} ({duration_text})")
            
            self.log(f"  Status Effects: {', '.join(status_list)}")
        else:
            self.log("  Status Effects: None")
    
    def close(self):
        """Close the logger."""
        pass

def create_unit(unit_id, name, faction, hp=20, max_hp=20, stats=None):
    """Helper function to create a unit for testing."""
    unit = UnitState()
    unit.id = unit_id
    unit.name = name
    unit.faction = faction
    unit.current_hp = hp
    unit.max_hp = max_hp
    unit.disposition = DispositionEnum.ACTIVE
    unit.base_stats = stats or {"STR": 5, "DEF": 3, "SKL": 4, "SPD": 3}
    unit.status_effects = []
    return unit

def test_status_effects():
    """Test status effect mechanics."""
    # Setup game state and systems
    game_state_manager = MockGameStateManager()
    status_effects_system = StatusEffectsSystem()
    status_effects_system.initialize(game_state_manager)
    
    # Create log directory if it doesn't exist
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../logs/mechanic_tests/status_effects'))
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a log file
    log_path = os.path.join(log_dir, f"status_effects_mechanics.txt")
    
    visual_logger = VisualScenarioLogger(game_state_manager, log_dir)
    visual_logger.set_log_file(log_path)
    
    # Log initial state
    visual_logger.log_initial_state("Status Effect Mechanics Test")
    
    # Create test units
    knight = create_unit("PLAYER_KNIGHT", "Knight", FactionEnum.PLAYER, hp=25, max_hp=25,
                         stats={"STR": 8, "DEF": 7, "SKL": 6, "SPD": 5})
    
    mage = create_unit("PLAYER_MAGE", "Mage", FactionEnum.PLAYER, hp=18, max_hp=18,
                      stats={"STR": 3, "DEF": 2, "SKL": 7, "SPD": 6, "MAG": 9})
    
    bandit = create_unit("ENEMY_BANDIT", "Bandit", FactionEnum.ENEMY, hp=22, max_hp=22,
                        stats={"STR": 7, "DEF": 3, "SKL": 4, "SPD": 6})
    
    # Add units to game state
    game_state_manager.add_unit(knight)
    game_state_manager.add_unit(mage)
    game_state_manager.add_unit(bandit)
    
    visual_logger.log(f"Current Turn: {game_state_manager.current_turn}")
    visual_logger.log("\nInitial Unit States:")
    for unit in game_state_manager.get_all_units():
        visual_logger.log_unit_status(unit)
    
    # Test 1: Poison Status Effect
    visual_logger.log("\n=== TEST 1: POISON STATUS EFFECT ===")
    
    # Apply poison to bandit
    poison_result = status_effects_system.apply_poison("ENEMY_BANDIT", 3, 2)
    visual_logger.log(f"Applying poison to Bandit. Result: {poison_result}")
    
    bandit = game_state_manager.get_unit("ENEMY_BANDIT")
    visual_logger.log_unit_status(bandit)
    
    # Advance turn
    visual_logger.log("\nAdvancing to next turn...")
    game_state_manager.advance_turn()
    visual_logger.log(f"Current Turn: {game_state_manager.current_turn}")
    
    # Check bandit state after poison damage
    visual_logger.log("\nBandit state after poison damage:")
    visual_logger.log_unit_status(bandit)
    
    # Test 2: Sleep Status Effect
    visual_logger.log("\n=== TEST 2: SLEEP STATUS EFFECT ===")
    
    # Apply sleep to knight
    sleep_result = status_effects_system.apply_sleep("PLAYER_KNIGHT", 2)
    visual_logger.log(f"Applying sleep to Knight. Result: {sleep_result}")
    
    knight = game_state_manager.get_unit("PLAYER_KNIGHT")
    visual_logger.log_unit_status(knight)
    
    # Advance turn
    visual_logger.log("\nAdvancing to next turn...")
    game_state_manager.advance_turn()
    visual_logger.log(f"Current Turn: {game_state_manager.current_turn}")
    
    # Check unit states after advancing turn
    visual_logger.log("\nUnit states after advancing turn:")
    for unit in game_state_manager.get_all_units():
        visual_logger.log_unit_status(unit)
    
    # Test 3: Silence Status Effect
    visual_logger.log("\n=== TEST 3: SILENCE STATUS EFFECT ===")
    
    # Apply silence to mage
    silence_result = status_effects_system.apply_silence("PLAYER_MAGE", 3)
    visual_logger.log(f"Applying silence to Mage. Result: {silence_result}")
    
    mage = game_state_manager.get_unit("PLAYER_MAGE")
    visual_logger.log_unit_status(mage)
    
    # Test 4: Stat Boost Status Effect
    visual_logger.log("\n=== TEST 4: STAT BOOST STATUS EFFECT ===")
    
    # Apply stat boost to knight
    boost_result = status_effects_system.apply_stat_boost("PLAYER_KNIGHT", 2, 5)
    visual_logger.log(f"Applying STR boost to Knight. Result: {boost_result}")
    
    knight = game_state_manager.get_unit("PLAYER_KNIGHT")
    visual_logger.log(f"Knight STR before boost: {knight.base_stats['STR']}")
    visual_logger.log(f"Knight STR with boost: {knight.get_stat('STR')}")
    visual_logger.log_unit_status(knight)
    
    # Test 5: Status Effect Removal
    visual_logger.log("\n=== TEST 5: STATUS EFFECT REMOVAL ===")
    
    # Cure mage's silence
    cure_result = status_effects_system.cure_status("PLAYER_MAGE", StatusEffectEnum.SILENCE)
    visual_logger.log(f"Curing Mage's silence. Result: {cure_result}")
    
    mage = game_state_manager.get_unit("PLAYER_MAGE")
    visual_logger.log_unit_status(mage)
    
    # Advance turn to expire some effects
    visual_logger.log("\nAdvancing to next turn...")
    game_state_manager.advance_turn()
    visual_logger.log(f"Current Turn: {game_state_manager.current_turn}")
    
    # Check unit states after advancing turn
    visual_logger.log("\nUnit states after advancing turn:")
    for unit in game_state_manager.get_all_units():
        visual_logger.log_unit_status(unit)
    
    # Test 6: Multiple Status Effects
    visual_logger.log("\n=== TEST 6: MULTIPLE STATUS EFFECTS ===")
    
    # Apply multiple status effects to bandit
    status_effects_system.apply_sleep("ENEMY_BANDIT", 2)
    status_effects_system.apply_stat_boost("ENEMY_BANDIT", 3, -2)  # Defense down
    
    bandit = game_state_manager.get_unit("ENEMY_BANDIT")
    visual_logger.log("Applied multiple status effects to Bandit:")
    visual_logger.log_unit_status(bandit)
    
    # Test 7: Cure All Status Effects
    visual_logger.log("\n=== TEST 7: CURE ALL STATUS EFFECTS ===")
    
    # Cure all status effects on bandit
    cure_all_result = status_effects_system.cure_all_status("ENEMY_BANDIT")
    visual_logger.log(f"Curing all status effects on Bandit. Result: {cure_all_result}")
    
    bandit = game_state_manager.get_unit("ENEMY_BANDIT")
    visual_logger.log_unit_status(bandit)
    
    # Final state
    visual_logger.log("\n=== FINAL STATE ===")
    visual_logger.log(f"Current Turn: {game_state_manager.current_turn}")
    
    for unit in game_state_manager.get_all_units():
        visual_logger.log_unit_status(unit)
    
    visual_logger.log("\nSTATUS_EFFECTS_MECHANICS_TEST_COMPLETE")
    visual_logger.close()

if __name__ == "__main__":
    test_status_effects() 