#!/usr/bin/env python3
"""
Integrated Combat Scenario Visual Test

This script demonstrates a full tactical combat scenario with multiple units,
movement, attacks, and various combat mechanics in a Fire Emblem style.
"""

import os
import sys
import time
import random
import pygame

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

# Import game modules
from src.ui.pygame_renderer import GameRenderer, AnimationType, ParticleSystemEffect
from src.utils.visual_logger import VisualScenarioLogger
from src.core.game_state_manager import GameStateManager
from src.core.map import GameMap
from src.core.unit import Unit
from src.core.faction import Faction
from src.core.item import Weapon

class DummyGameStateManager:
    """Simplified game state manager for the demo."""
    
    def __init__(self):
        """Initialize the game state manager with a map and units."""
        # Create map
        self.map = GameMap(15, 15)
        self.map.generate_simple_terrain()
        
        # Create factions
        self.player_faction = Faction("PLAYER", "Player")
        self.enemy_faction = Faction("ENEMY", "Enemy")
        
        # Initialize unit lists and game state
        self.units = []
        self.selected_unit = None
        self.current_phase = "PLAYER"
        self.turn_number = 1
        
        # Create units
        self._create_units()
        
        # Combat log
        self.combat_log = []
    
    def _create_units(self):
        """Create units for the demonstration."""
        # Player units
        knight = Unit("knight_1", "Knight", self.player_faction)
        knight.position = (2, 2)
        knight.max_hp = 30
        knight.hp = 30
        knight.attack = 8
        knight.defense = 10
        knight.movement = 3
        knight.vision_range = 5
        knight.equipped_weapon = Weapon("Steel Lance", 8, 1, 2, 90)
        self.units.append(knight)
        
        archer = Unit("archer_1", "Archer", self.player_faction)
        archer.position = (3, 4)
        archer.max_hp = 22
        archer.hp = 22
        archer.attack = 7
        archer.defense = 4
        archer.movement = 4
        archer.vision_range = 6
        archer.equipped_weapon = Weapon("Longbow", 7, 2, 3, 85)
        self.units.append(archer)
        
        mage = Unit("mage_1", "Mage", self.player_faction)
        mage.position = (1, 4)
        mage.max_hp = 20
        mage.hp = 20
        mage.attack = 10
        mage.defense = 3
        mage.movement = 4
        mage.vision_range = 5
        mage.equipped_weapon = Weapon("Fire Tome", 10, 1, 2, 80)
        self.units.append(mage)
        
        # Enemy units
        enemy_knight = Unit("enemy_knight_1", "Enemy Knight", self.enemy_faction)
        enemy_knight.position = (10, 10)
        enemy_knight.max_hp = 28
        enemy_knight.hp = 28
        enemy_knight.attack = 7
        enemy_knight.defense = 9
        enemy_knight.movement = 3
        enemy_knight.vision_range = 4
        enemy_knight.equipped_weapon = Weapon("Iron Lance", 7, 1, 1, 95)
        self.units.append(enemy_knight)
        
        enemy_archer = Unit("enemy_archer_1", "Enemy Archer", self.enemy_faction)
        enemy_archer.position = (12, 8)
        enemy_archer.max_hp = 20
        enemy_archer.hp = 20
        enemy_archer.attack = 6
        enemy_archer.defense = 4
        enemy_archer.movement = 4
        enemy_archer.vision_range = 6
        enemy_archer.equipped_weapon = Weapon("Shortbow", 6, 2, 3, 90)
        self.units.append(enemy_archer)
        
        enemy_soldier = Unit("enemy_soldier_1", "Enemy Soldier", self.enemy_faction)
        enemy_soldier.position = (8, 12)
        enemy_soldier.max_hp = 25
        enemy_soldier.hp = 25
        enemy_soldier.attack = 6
        enemy_soldier.defense = 6
        enemy_soldier.movement = 5
        enemy_soldier.vision_range = 4
        enemy_soldier.equipped_weapon = Weapon("Iron Spear", 6, 1, 1, 95)
        self.units.append(enemy_soldier)
    
    def get_all_units(self):
        """Return all units."""
        return self.units
    
    def get_unit_at_position(self, x, y):
        """Return unit at the given position or None."""
        for unit in self.units:
            if unit.position == (x, y):
                return unit
        return None
    
    def get_map(self):
        """Return the game map."""
        return self.map
    
    def get_current_phase(self):
        """Return the current phase."""
        return self.current_phase
    
    def get_turn_number(self):
        """Return the current turn number."""
        return self.turn_number
    
    def move_unit(self, unit, target_position):
        """Move a unit to the target position."""
        if not unit:
            return False
        
        # Check if the move is valid (simplified)
        x1, y1 = unit.position
        x2, y2 = target_position
        distance = abs(x2 - x1) + abs(y2 - y1)  # Manhattan distance for grid movement
        
        if distance > unit.movement:
            return False
        
        # Check if target position is occupied
        if self.get_unit_at_position(x2, y2):
            return False
        
        # Move unit
        unit.position = target_position
        return True
    
    def perform_attack(self, attacker, defender):
        """Perform an attack between two units."""
        if not attacker or not defender:
            return False
        
        # Check if defender is in range
        x1, y1 = attacker.position
        x2, y2 = defender.position
        distance = abs(x2 - x1) + abs(y2 - y1)
        
        weapon = attacker.equipped_weapon
        if not weapon or distance < weapon.min_range or distance > weapon.max_range:
            return False
        
        # Calculate hit chance
        hit_chance = weapon.accuracy
        
        # Calculate damage
        base_damage = attacker.attack
        mitigated_damage = max(1, base_damage - defender.defense)
        
        # Roll for hit
        hit_roll = random.randint(1, 100)
        hit = hit_roll <= hit_chance
        
        # Apply damage if hit
        if hit:
            defender.hp = max(0, defender.hp - mitigated_damage)
            
            # Log the combat
            self.combat_log.append({
                "attacker": attacker.name,
                "defender": defender.name,
                "damage": mitigated_damage,
                "defender_hp": defender.hp,
                "hit": True
            })
            
            # Check if defender is defeated
            if defender.hp <= 0:
                defender.is_alive = False
                self.units = [u for u in self.units if u.is_alive]
        else:
            # Log the miss
            self.combat_log.append({
                "attacker": attacker.name,
                "defender": defender.name,
                "damage": 0,
                "defender_hp": defender.hp,
                "hit": False
            })
        
        return hit

class CombatScenarioDemo:
    """Class to demonstrate a complete combat scenario."""
    
    def __init__(self, duration=60):
        """Initialize the demonstration."""
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.window_size = (1024, 768)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Combat Scenario Demonstration")
        
        # Create game state manager
        self.gsm = DummyGameStateManager()
        
        # Create renderer
        self.renderer = GameRenderer(self.gsm, self.window_size)
        
        # Create CLI display for visual logger
        class DummyCLIDisplay:
            def render_map_to_text(self, map_state):
                return "Map display placeholder"
            
        self.cli_display = DummyCLIDisplay()
        
        # Create visual logger
        self.logger = VisualScenarioLogger(self.gsm, self.cli_display, log_dir="logs/combat_scenario", enabled=True)
        
        # Center camera on the map
        self.renderer.center_camera_on_position(7, 7)
        
        # Demo timers and state
        self.scripted_events = []
        self._setup_demo_script()
        self.start_time = time.time()
        self.max_runtime = duration
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Setup fonts
        self.font = pygame.font.SysFont("Arial", 20)
        
        # Animation tracking
        self.current_animation = None
        self.animation_unit = None
    
    def _setup_demo_script(self):
        """Set up the scripted events for the demonstration."""
        # List of (time_offset, event_function) tuples
        self.scripted_events = [
            # Start with introduction
            (1.0, self._event_introduction),
            
            # Player phase - Knight moves and attacks
            (4.0, self._event_player_phase_start),
            (6.0, lambda: self._event_move_unit("knight_1", (5, 5))),
            (9.0, lambda: self._event_attack_unit("knight_1", "enemy_soldier_1")),
            
            # Player phase - Archer moves and attacks
            (12.0, lambda: self._event_move_unit("archer_1", (5, 7))),
            (15.0, lambda: self._event_attack_unit("archer_1", "enemy_archer_1")),
            
            # Player phase - Mage moves
            (18.0, lambda: self._event_move_unit("mage_1", (4, 4))),
            
            # Switch to enemy phase
            (20.0, self._event_enemy_phase_start),
            
            # Enemy phase - Enemy units move and attack
            (22.0, lambda: self._event_move_unit("enemy_knight_1", (8, 8))),
            (25.0, lambda: self._event_move_unit("enemy_archer_1", (10, 7))),
            (28.0, lambda: self._event_attack_unit("enemy_archer_1", "knight_1")),
            (31.0, lambda: self._event_move_unit("enemy_soldier_1", (7, 10))),
            
            # Turn 2 starts
            (34.0, self._event_new_turn),
            
            # Player phase - Knight attacks
            (36.0, lambda: self._event_attack_unit("knight_1", "enemy_soldier_1")),
            
            # Player phase - Archer moves and attacks
            (39.0, lambda: self._event_move_unit("archer_1", (6, 9))),
            (42.0, lambda: self._event_attack_unit("archer_1", "enemy_soldier_1")),
            
            # Player phase - Mage moves and attacks
            (45.0, lambda: self._event_move_unit("mage_1", (6, 6))),
            (48.0, lambda: self._event_attack_unit("mage_1", "enemy_knight_1")),
            
            # End demo
            (55.0, self._event_end_demo)
        ]
    
    def run(self):
        """Run the demonstration."""
        self.logger.log_action("SYSTEM", "START", "Combat Scenario Demonstration")
        
        while self.running:
            current_time = time.time() - self.start_time
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Check for scripted events
            self._process_scripted_events(current_time)
            
            # Update renderer
            self.renderer.update()
            
            # Draw
            self.renderer.draw(self.screen)
            
            # Draw scenario info
            self._draw_scenario_info()
            
            # Update display
            pygame.display.flip()
            
            # Cap at 60 FPS
            self.clock.tick(60)
            
            # Check if max runtime reached
            if current_time > self.max_runtime:
                print("Maximum runtime reached.")
                break
        
        # Clean up
        pygame.quit()
    
    def _process_scripted_events(self, current_time):
        """Process any scripted events due at the current time."""
        events_to_remove = []
        
        for time_offset, event_func in self.scripted_events:
            if current_time >= time_offset:
                event_func()
                events_to_remove.append((time_offset, event_func))
        
        # Remove processed events
        for event in events_to_remove:
            self.scripted_events.remove(event)
    
    def _draw_scenario_info(self):
        """Draw scenario information on the screen."""
        # Draw turn and phase info
        turn_text = f"Turn: {self.gsm.get_turn_number()}"
        phase_text = f"Phase: {self.gsm.get_current_phase()}"
        
        turn_surface = self.font.render(turn_text, True, (255, 255, 255))
        phase_surface = self.font.render(phase_text, True, (255, 255, 255))
        
        self.screen.blit(turn_surface, (10, 10))
        self.screen.blit(phase_surface, (10, 40))
        
        # Draw recent combat log if available
        if self.gsm.combat_log:
            # Get the most recent combat entry
            recent_combat = self.gsm.combat_log[-1]
            
            if recent_combat["hit"]:
                combat_text = f"{recent_combat['attacker']} hit {recent_combat['defender']} for {recent_combat['damage']} damage"
                color = (255, 200, 0)
            else:
                combat_text = f"{recent_combat['attacker']} missed {recent_combat['defender']}"
                color = (200, 200, 200)
            
            combat_surface = self.font.render(combat_text, True, color)
            self.screen.blit(combat_surface, (10, 70))
    
    # Event handling methods
    def _event_introduction(self):
        """Introduction event."""
        self.logger.log_action("SYSTEM", "INTRO", "Combat Scenario Demonstration")
        self.logger.log_action("SYSTEM", "INFO", "Demonstrating tactical combat with multiple units")
        print("Starting combat scenario demonstration...")
    
    def _event_player_phase_start(self):
        """Start player phase."""
        self.gsm.current_phase = "PLAYER"
        self.logger.log_action("SYSTEM", "PHASE", f"Player Phase - Turn {self.gsm.get_turn_number()}")
        print(f"Player Phase - Turn {self.gsm.get_turn_number()}")
    
    def _event_enemy_phase_start(self):
        """Start enemy phase."""
        self.gsm.current_phase = "ENEMY"
        self.logger.log_action("SYSTEM", "PHASE", f"Enemy Phase - Turn {self.gsm.get_turn_number()}")
        print(f"Enemy Phase - Turn {self.gsm.get_turn_number()}")
    
    def _event_new_turn(self):
        """Start a new turn."""
        self.gsm.turn_number += 1
        self.gsm.current_phase = "PLAYER"
        self.logger.log_action("SYSTEM", "TURN", f"Turn {self.gsm.get_turn_number()} begins")
        self.logger.log_action("SYSTEM", "PHASE", f"Player Phase - Turn {self.gsm.get_turn_number()}")
        print(f"Turn {self.gsm.get_turn_number()} begins - Player Phase")
    
    def _event_move_unit(self, unit_id, target_position):
        """Move a unit to the target position."""
        # Find unit
        unit = next((u for u in self.gsm.get_all_units() if u.id == unit_id), None)
        if not unit:
            print(f"Unit {unit_id} not found")
            return
        
        start_pos = unit.position
        
        # Move the unit
        success = self.gsm.move_unit(unit, target_position)
        
        if success:
            # Log the movement
            self.logger.log_action(unit.id, "MOVE", f"{unit.name} moved from {start_pos} to {target_position}")
            print(f"{unit.name} moved from {start_pos} to {target_position}")
            
            # Add movement animation
            self.renderer.add_movement_animation(unit, start_pos, target_position)
        else:
            print(f"Failed to move {unit.name}")
    
    def _event_attack_unit(self, attacker_id, defender_id):
        """Perform an attack between units."""
        # Find units
        attacker = next((u for u in self.gsm.get_all_units() if u.id == attacker_id), None)
        defender = next((u for u in self.gsm.get_all_units() if u.id == defender_id), None)
        
        if not attacker or not defender:
            print(f"Units not found: {attacker_id} or {defender_id}")
            return
        
        # Perform the attack
        hit = self.gsm.perform_attack(attacker, defender)
        
        # Get the most recent combat log entry
        if self.gsm.combat_log:
            combat_entry = self.gsm.combat_log[-1]
            
            if hit:
                # Log the attack
                self.logger.log_action(attacker.id, "ATTACK", 
                                      f"{attacker.name} attacked {defender.name} for {combat_entry['damage']} damage")
                print(f"{attacker.name} attacked {defender.name} for {combat_entry['damage']} damage")
                
                # Add attack animation and particle effect
                self.renderer.add_attack_animation(attacker, defender)
                
                # Add damage text animation
                self.renderer.add_floating_text(defender.position, str(combat_entry['damage']), (255, 0, 0))
                
                # Add particle effect at defender's position
                if "Bow" in attacker.equipped_weapon.name:
                    effect_type = "sparks"
                elif "Tome" in attacker.equipped_weapon.name:
                    effect_type = "explosion"
                else:
                    effect_type = "sparks"
                
                self.renderer.add_particle_effect(defender.position, effect_type, 20)
                
                # Check if defender was defeated
                if defender.hp <= 0:
                    self.logger.log_action(defender.id, "DEFEATED", f"{defender.name} was defeated")
                    print(f"{defender.name} was defeated")
            else:
                # Log the miss
                self.logger.log_action(attacker.id, "MISS", f"{attacker.name} missed {defender.name}")
                print(f"{attacker.name} missed {defender.name}")
        else:
            print(f"Attack failed between {attacker.name} and {defender.name}")
    
    def _event_end_demo(self):
        """End the demonstration."""
        self.logger.log_action("SYSTEM", "END", "Combat Scenario Demonstration Complete")
        self.logger.finalize_log()
        
        print(f"\nDemonstration complete. Log saved to: {self.logger.log_file}")
        print("Press ESC to exit.")

def main():
    """Main function to run the combat scenario demonstration."""
    print("Starting Combat Scenario Demonstration...")
    
    # Get duration from command line if provided
    import argparse
    parser = argparse.ArgumentParser(description="Run the Combat Scenario Demonstration")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds to run the demo")
    args = parser.parse_args()
    
    # Create and run the demonstration
    demo = CombatScenarioDemo(duration=args.duration)
    demo.run()
    
    print("Combat Scenario Demonstration complete.")

if __name__ == "__main__":
    main() 