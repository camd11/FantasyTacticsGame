"""
Status Effect Mechanics Test

This test demonstrates the status effect mechanics in the game, including:
- Applying buffs (strength boost, defense boost)
- Applying debuffs (poison, silence, sleep)
- Status effect duration and cleansing
- Multiple status effects on a single unit
"""

import os
import sys
import random
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.abspath('.'))

# Import the necessary modules
from src.utils.visual_logger import VisualScenarioLogger
from src.core_engine.game_state import GameStateManager, GameState, MapState, UnitState, FactionEnum, DispositionEnum, PhaseEnum

class StatusEffect:
    """Represents a status effect that can be applied to a unit."""
    def __init__(self, name, effect_type, duration, strength=1, description=None):
        self.name = name
        self.effect_type = effect_type  # "buff", "debuff", "control"
        self.duration = duration  # number of turns effect lasts
        self.strength = strength  # how strong the effect is (for scaling effects)
        self.description = description or f"{effect_type.capitalize()} effect"
        
    def __str__(self):
        return f"{self.name} ({self.duration} turns remaining)"

class MockCLIDisplay:
    """Mock CLI display for rendering the game state."""
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager
    
    def render_ascii_map(self):
        """Render an ASCII representation of the current game state."""
        map_width, map_height = 7, 7
        
        # Get unit positions - in a real game, this would come from the game state
        unit_positions = {}
        for unit in self.game_state_manager.get_all_units():
            if hasattr(unit, 'position') and unit.position and unit.disposition == DispositionEnum.ACTIVE:
                unit_positions[unit.position] = unit
        
        # Initialize the map with empty cells
        map_data = [['.' for _ in range(map_width)] for _ in range(map_height)]
        
        # Place units on the map
        for pos, unit in unit_positions.items():
            x, y = pos
            if 0 <= x < map_width and 0 <= y < map_height:
                # Show unit with a status indicator if they have status effects
                if hasattr(unit, 'status_effects') and unit.status_effects:
                    if unit.faction == FactionEnum.PLAYER:
                        map_data[y][x] = 'P*'
                    elif unit.faction == FactionEnum.ENEMY:
                        map_data[y][x] = 'E*'
                    else:
                        map_data[y][x] = 'N*'
                else:
                    if unit.faction == FactionEnum.PLAYER:
                        map_data[y][x] = 'P'
                    elif unit.faction == FactionEnum.ENEMY:
                        map_data[y][x] = 'E'
                    else:
                        map_data[y][x] = 'N'
        
        # Build the map string
        map_string = f"=== ASCII MAP (Turn {self.game_state_manager.current_game_state.current_turn}, {self.game_state_manager.current_game_state.current_phase.name} Phase) ===\n"
        map_string += "   " + "".join([str(i) for i in range(map_width)]) + "\n"
        
        for y in range(map_height):
            map_string += f" {y} "
            for x in range(map_width):
                cell = map_data[y][x]
                if len(cell) == 1:
                    map_string += cell + " "
                else:
                    map_string += cell
            map_string += "\n"
        
        map_string += "\nLegend: P=Player, E=Enemy, N=NPC, *=Has Status Effect\n"
        
        return map_string

def create_unit(unit_id, name, faction, position, hp, max_hp, stats=None):
    """Helper function to create a unit for testing."""
    unit = UnitState()
    unit.id = unit_id
    unit.name = name
    unit.faction = faction
    unit.position = position
    unit.current_hp = hp
    unit.max_hp = max_hp
    unit.disposition = DispositionEnum.ACTIVE
    unit.base_stats = stats or {}
    unit.status_effects = []
    return unit

class MockGameStateManager(GameStateManager):
    """Mock GameStateManager for testing."""
    def __init__(self):
        super().__init__(None)
        self.current_game_state = GameState()
        self.current_game_state.map_state = MapState()
        self.current_game_state.unit_states = {}
        
    def add_unit(self, unit):
        """Add a unit to the game state."""
        self.current_game_state.unit_states[unit.id] = unit
        
    def get_all_units(self):
        """Return all units in the game state."""
        return list(self.current_game_state.unit_states.values())

def apply_status_effect(unit, effect, visual_logger):
    """Apply a status effect to a unit."""
    # Check if the unit already has this effect
    for existing_effect in unit.status_effects:
        if existing_effect.name == effect.name:
            # Same effect - refresh duration
            visual_logger.log_action(unit.id, "STATUS_REFRESH", f"{unit.name}'s {effect.name} effect refreshed to {effect.duration} turns")
            existing_effect.duration = effect.duration
            existing_effect.strength = max(existing_effect.strength, effect.strength)
            return
    
    # New effect - add it
    unit.status_effects.append(effect)
    visual_logger.log_action(unit.id, "STATUS_APPLIED", f"{unit.name} is affected by {effect.name} for {effect.duration} turns")
    
    # Apply immediate stat changes for certain effects
    if effect.effect_type == "buff":
        if effect.name == "Strength Boost":
            visual_logger.log_action(unit.id, "STAT_BOOST", f"{unit.name} gains +{effect.strength} STR")
        elif effect.name == "Defense Boost":
            visual_logger.log_action(unit.id, "STAT_BOOST", f"{unit.name} gains +{effect.strength} DEF")
        elif effect.name == "Speed Boost":
            visual_logger.log_action(unit.id, "STAT_BOOST", f"{unit.name} gains +{effect.strength} SPD")
    elif effect.effect_type == "debuff":
        if effect.name == "Weakness":
            visual_logger.log_action(unit.id, "STAT_PENALTY", f"{unit.name} suffers -{effect.strength} STR")
        elif effect.name == "Vulnerability":
            visual_logger.log_action(unit.id, "STAT_PENALTY", f"{unit.name} suffers -{effect.strength} DEF")
        elif effect.name == "Slow":
            visual_logger.log_action(unit.id, "STAT_PENALTY", f"{unit.name} suffers -{effect.strength} SPD")

def process_status_effects(unit, visual_logger, is_turn_start=True):
    """Process status effects at the start or end of a turn."""
    if not unit.status_effects:
        return
    
    phase = "turn start" if is_turn_start else "turn end"
    visual_logger.log_action(unit.id, "STATUS_CHECK", f"Checking {unit.name}'s status effects at {phase}")
    
    effects_to_remove = []
    
    for effect in unit.status_effects:
        # Handle effects that trigger at the start of turn
        if is_turn_start:
            if effect.name == "Poison":
                damage = effect.strength
                unit.current_hp = max(1, unit.current_hp - damage)  # Poison doesn't kill
                visual_logger.log_action(unit.id, "POISON_DAMAGE", f"{unit.name} takes {damage} poison damage (HP: {unit.current_hp}/{unit.max_hp})")
            elif effect.name == "Regeneration":
                healing = effect.strength
                old_hp = unit.current_hp
                unit.current_hp = min(unit.max_hp, unit.current_hp + healing)
                actual_healing = unit.current_hp - old_hp
                visual_logger.log_action(unit.id, "REGENERATION", f"{unit.name} recovers {actual_healing} HP (HP: {unit.current_hp}/{unit.max_hp})")
            elif effect.name == "Sleep":
                visual_logger.log_action(unit.id, "SLEEP", f"{unit.name} is asleep and cannot act this turn")
            elif effect.name == "Silence":
                visual_logger.log_action(unit.id, "SILENCE", f"{unit.name} is silenced and cannot use spells this turn")
        
        # Reduce duration at the end of the turn
        if not is_turn_start:
            effect.duration -= 1
            if effect.duration <= 0:
                effects_to_remove.append(effect)
                visual_logger.log_action(unit.id, "STATUS_EXPIRED", f"{unit.name}'s {effect.name} effect has expired")
            else:
                visual_logger.log_action(unit.id, "STATUS_DURATION", f"{unit.name}'s {effect.name} effect has {effect.duration} turns remaining")
    
    # Remove expired effects
    for effect in effects_to_remove:
        unit.status_effects.remove(effect)

def cleanse_status_effects(unit, effect_types, visual_logger):
    """Remove status effects of specific types from a unit."""
    if not unit.status_effects:
        visual_logger.log_action(unit.id, "CLEANSE_NONE", f"{unit.name} has no status effects to cleanse")
        return
    
    effects_to_remove = []
    
    for effect in unit.status_effects:
        if effect.effect_type in effect_types:
            effects_to_remove.append(effect)
    
    for effect in effects_to_remove:
        unit.status_effects.remove(effect)
        visual_logger.log_action(unit.id, "CLEANSED", f"{unit.name}'s {effect.name} effect has been cleansed")
    
    if not effects_to_remove:
        visual_logger.log_action(unit.id, "CLEANSE_NONE", f"{unit.name} has no matching status effects to cleanse")

def run_test(log_path=None):
    """Run the status effect mechanics test."""
    # Create log file path if not provided
    if log_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("logs/mechanic_tests/status_effects", exist_ok=True)
        log_path = f"logs/mechanic_tests/status_effects/status_effect_mechanics_{timestamp}.txt"
    
    # Create mock game state
    game_state_manager = MockGameStateManager()
    game_state_manager.current_game_state.map_state.map_id = "status_effect_test_map"
    game_state_manager.current_game_state.current_turn = 1
    game_state_manager.current_game_state.current_phase = PhaseEnum.PLAYER
    
    # Create mock CLI display
    cli_display = MockCLIDisplay(game_state_manager)
    
    # Initialize the visual logger
    visual_logger = VisualScenarioLogger(
        game_state_manager=game_state_manager,
        cli_display=cli_display,
        enabled=True,
        fixed_log_path=log_path,
        use_colors=True,
        html_export=True
    )
    
    print(f"Status effect mechanics test log will be written to: {log_path}")
    print(f"HTML log will be written to: {log_path.replace('.txt', '.html')}")
    
    # Define status effects
    poison_effect = StatusEffect("Poison", "debuff", 3, 2, "Takes damage at the start of each turn")
    strength_boost = StatusEffect("Strength Boost", "buff", 2, 3, "Increases STR stat")
    sleep_effect = StatusEffect("Sleep", "control", 2, 1, "Cannot act until effect expires or unit takes damage")
    defense_boost = StatusEffect("Defense Boost", "buff", 3, 2, "Increases DEF stat")
    silence_effect = StatusEffect("Silence", "debuff", 2, 1, "Cannot use spells")
    regeneration = StatusEffect("Regeneration", "buff", 3, 2, "Recovers HP at the start of each turn")
    
    # Create units for the test
    player_warrior = create_unit(
        "PLAYER_WARRIOR", "Warrior", FactionEnum.PLAYER, 
        (2, 3), 25, 25, {"STR": 8, "DEF": 6, "SKL": 7, "SPD": 5, "MOV": 5}
    )
    
    player_mage = create_unit(
        "PLAYER_MAGE", "Mage", FactionEnum.PLAYER, 
        (3, 3), 18, 18, {"STR": 3, "DEF": 4, "SKL": 8, "SPD": 6, "MOV": 4, "MAG": 9}
    )
    
    player_healer = create_unit(
        "PLAYER_HEALER", "Healer", FactionEnum.PLAYER, 
        (2, 4), 16, 16, {"STR": 2, "DEF": 3, "SKL": 7, "SPD": 5, "MOV": 4, "MAG": 8}
    )
    
    enemy_archer = create_unit(
        "ENEMY_ARCHER", "Archer", FactionEnum.ENEMY, 
        (5, 3), 20, 20, {"STR": 7, "DEF": 5, "SKL": 9, "SPD": 7, "MOV": 5}
    )
    
    enemy_mage = create_unit(
        "ENEMY_MAGE", "Dark Mage", FactionEnum.ENEMY, 
        (4, 4), 17, 17, {"STR": 3, "DEF": 4, "SKL": 8, "SPD": 6, "MOV": 4, "MAG": 10}
    )
    
    # Register units with the game state manager
    game_state_manager.add_unit(player_warrior)
    game_state_manager.add_unit(player_mage)
    game_state_manager.add_unit(player_healer)
    game_state_manager.add_unit(enemy_archer)
    game_state_manager.add_unit(enemy_mage)
    
    # Start the test scenario
    visual_logger.log_action("SYSTEM", "SCENARIO_START", "Starting Status Effect Mechanics Test")
    visual_logger.log_initial_state()
    
    # Log the test description
    visual_logger.log_action("SYSTEM", "TEST_INFO", "This test demonstrates how status effects are applied, affect units, and expire")
    
    # Log status effect info
    visual_logger.log_action("SYSTEM", "STATUS_EFFECTS", "==== Status Effect Details ====")
    for effect in [poison_effect, strength_boost, sleep_effect, defense_boost, silence_effect, regeneration]:
        visual_logger.log_action("SYSTEM", "EFFECT_INFO", f"{effect.name} ({effect.effect_type}): {effect.description}, Duration: {effect.duration} turns, Strength: {effect.strength}")
    
    # Turn 1
    visual_logger.log_turn_start(1)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Process start-of-turn status effects (none yet)
    for unit in game_state_manager.get_all_units():
        process_status_effects(unit, visual_logger, True)
    
    # Player actions - Apply buffs to allies
    visual_logger.log_action("PLAYER_HEALER", "BUFF_CAST", "Healer casts Regeneration on Warrior")
    apply_status_effect(player_warrior, regeneration, visual_logger)
    
    visual_logger.log_action("PLAYER_MAGE", "BUFF_CAST", "Mage casts Strength Boost on Warrior")
    apply_status_effect(player_warrior, strength_boost, visual_logger)
    
    # End player phase
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # Enemy phase
    game_state_manager.current_game_state.current_phase = PhaseEnum.ENEMY
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
    
    # Enemy actions - Apply debuffs to player units
    visual_logger.log_action("ENEMY_MAGE", "DEBUFF_CAST", "Dark Mage casts Poison on Mage")
    apply_status_effect(player_mage, poison_effect, visual_logger)
    
    visual_logger.log_action("ENEMY_ARCHER", "ATTACK", "Archer attacks Warrior")
    # Simulate attack
    damage = 5
    player_warrior.current_hp = max(0, player_warrior.current_hp - damage)
    visual_logger.log_action("PLAYER_WARRIOR", "DAMAGE", f"Warrior takes {damage} damage (HP: {player_warrior.current_hp}/{player_warrior.max_hp})")
    
    # End enemy phase
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
    
    # Process end-of-turn status effects (duration decreases)
    for unit in game_state_manager.get_all_units():
        process_status_effects(unit, visual_logger, False)
    
    # Log end of turn state
    visual_logger.log_end_of_turn_state(1)
    
    # Turn 2
    game_state_manager.current_game_state.current_turn = 2
    game_state_manager.current_game_state.current_phase = PhaseEnum.PLAYER
    visual_logger.log_turn_start(2)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Process start-of-turn status effects
    for unit in game_state_manager.get_all_units():
        process_status_effects(unit, visual_logger, True)
    
    # Player actions - Apply more status effects
    visual_logger.log_action("PLAYER_HEALER", "BUFF_CAST", "Healer casts Defense Boost on Mage")
    apply_status_effect(player_mage, defense_boost, visual_logger)
    
    # Cleanse poison from Mage
    visual_logger.log_action("PLAYER_HEALER", "CLEANSE", "Healer cleanses debuffs from Mage")
    cleanse_status_effects(player_mage, ["debuff"], visual_logger)
    
    # End player phase
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # Enemy phase
    game_state_manager.current_game_state.current_phase = PhaseEnum.ENEMY
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
    
    # Enemy actions - Apply more status effects
    visual_logger.log_action("ENEMY_MAGE", "DEBUFF_CAST", "Dark Mage casts Silence on Mage")
    apply_status_effect(player_mage, silence_effect, visual_logger)
    
    visual_logger.log_action("ENEMY_MAGE", "DEBUFF_CAST", "Dark Mage casts Sleep on Healer")
    apply_status_effect(player_healer, sleep_effect, visual_logger)
    
    # End enemy phase
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
    
    # Process end-of-turn status effects
    for unit in game_state_manager.get_all_units():
        process_status_effects(unit, visual_logger, False)
    
    # Log end of turn state
    visual_logger.log_end_of_turn_state(2)
    
    # Turn 3
    game_state_manager.current_game_state.current_turn = 3
    game_state_manager.current_game_state.current_phase = PhaseEnum.PLAYER
    visual_logger.log_turn_start(3)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Process start-of-turn status effects
    for unit in game_state_manager.get_all_units():
        process_status_effects(unit, visual_logger, True)
    
    # Player actions
    visual_logger.log_action("PLAYER_WARRIOR", "ATTACK", "Warrior attacks Dark Mage (with Strength Boost)")
    # Simulate attack with boosted strength
    boosted_damage = 8
    enemy_mage.current_hp = max(0, enemy_mage.current_hp - boosted_damage)
    visual_logger.log_action("ENEMY_MAGE", "DAMAGE", f"Dark Mage takes {boosted_damage} damage (HP: {enemy_mage.current_hp}/{enemy_mage.max_hp})")
    
    # Wake up Healer by taking damage
    visual_logger.log_action("ENEMY_ARCHER", "ATTACK", "Archer attacks sleeping Healer")
    damage = 4
    player_healer.current_hp = max(0, player_healer.current_hp - damage)
    visual_logger.log_action("PLAYER_HEALER", "DAMAGE", f"Healer takes {damage} damage (HP: {player_healer.current_hp}/{player_healer.max_hp})")
    
    # Remove sleep when taking damage
    sleep_effect_to_remove = None
    for effect in player_healer.status_effects:
        if effect.name == "Sleep":
            sleep_effect_to_remove = effect
            break
    
    if sleep_effect_to_remove:
        player_healer.status_effects.remove(sleep_effect_to_remove)
        visual_logger.log_action("PLAYER_HEALER", "SLEEP_BROKEN", "Healer wakes up from sleep due to taking damage")
    
    # End player phase
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    
    # Enemy phase
    game_state_manager.current_game_state.current_phase = PhaseEnum.ENEMY
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase begins")
    
    # Enemy actions
    visual_logger.log_action("ENEMY_MAGE", "EFFECT_INTERACTION", "Dark Mage tries to cast a spell but is too injured to act effectively")
    
    # End enemy phase
    visual_logger.log_action("SYSTEM", "PHASE", "Enemy Phase ends")
    
    # Process end-of-turn status effects
    for unit in game_state_manager.get_all_units():
        process_status_effects(unit, visual_logger, False)
    
    # Log end of turn state
    visual_logger.log_end_of_turn_state(3)
    
    # Final summary
    visual_logger.log_action("SYSTEM", "SCENARIO_END", "Status Effect Mechanics Test Completed")
    
    visual_logger.log_action("SYSTEM", "TEST_SUMMARY", "=== TEST SUMMARY ===")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "The test demonstrated:")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "1. Application of various status effects (buffs, debuffs, control effects)")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "2. Status effect duration and expiration")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "3. Cleansing of status effects")
    visual_logger.log_action("SYSTEM", "TEST_RESULT", "4. Breaking of control effects through damage")
    
    # Log final status of units and their status effects
    visual_logger.log_action("SYSTEM", "FINAL_STATUS", "=== FINAL UNIT STATUS ===")
    for unit in game_state_manager.get_all_units():
        status_str = ""
        if unit.status_effects:
            effects = [str(effect) for effect in unit.status_effects]
            status_str = f" - Status Effects: {', '.join(effects)}"
        
        visual_logger.log_action(unit.id, "STATUS", f"{unit.name}: HP {unit.current_hp}/{unit.max_hp}{status_str}")
    
    # Finalize the log
    visual_logger.finalize_log()
    print("Status effect mechanics test completed.")
    
    return True

if __name__ == "__main__":
    # If run directly, use default log path
    run_test() 