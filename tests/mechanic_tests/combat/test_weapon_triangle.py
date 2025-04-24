#!/usr/bin/env python3
"""
Weapon Triangle Visual Test

This script demonstrates the weapon triangle system in action, showing how different
weapon types (sword, lance, axe) interact with bonuses and penalties in combat.
"""

import os
import sys
import time
import random
import pygame
from enum import Enum

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

# Import game renderer and animation types
from src.ui.pygame_renderer import GameRenderer, AnimationType
from src.utils.visual_logger import VisualScenarioLogger

class WeaponType(Enum):
    """Weapon types for the demonstration."""
    SWORD = "SWORD"
    LANCE = "LANCE"
    AXE = "AXE"
    BOW = "BOW"
    TOME = "TOME"

class DummyGameStateManager:
    """Dummy game state manager for testing."""
    def __init__(self):
        self.current_turn = 1
        self.current_phase = "PLAYER"
        self.selected_unit = None
        self.units = {}
        
        # Create a 15x15 map
        self.map_width = 15
        self.map_height = 15
        self.terrain_grid = [[None for _ in range(self.map_width)] for _ in range(self.map_height)]
        
        # Define terrain types
        class TerrainType:
            PLAIN = "PLAIN"
            FOREST = "FOREST"
            MOUNTAIN = "MOUNTAIN"
            RIVER = "RIVER"
            FORT = "FORT"
            WALL = "WALL"
            
            def __init__(self, name):
                self.name = name
        
        # Fill the map with plains
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.terrain_grid[y][x] = TerrainType("PLAIN")
        
        # Add some variety
        for x, y in [(3, 4), (4, 4), (3, 5), (4, 5)]:
            self.terrain_grid[y][x] = TerrainType("FOREST")
                
        for x, y in [(10, 10), (11, 10), (10, 11), (11, 11)]:
            self.terrain_grid[y][x] = TerrainType("MOUNTAIN")
        
        self.terrain_grid[7][7] = TerrainType("FORT")
        
        # Create test units with different weapon types
        self.create_units()
    
    def create_units(self):
        """Create test units with different weapon types."""
        class DummyUnit:
            def __init__(self, id, name, faction, position, weapon_type, hp, max_hp):
                self.id = id
                self.name = name
                self.faction = type('Faction', (), {'name': faction})
                self.position = position
                self.weapon_type = weapon_type
                self.current_hp = hp
                self.max_hp = max_hp
                self.disposition = type('Disposition', (), {'name': 'ACTIVE'})
                self.status_effects = []
                # Add weapon triangle stats
                self.hit_rate = 85
                self.avoid = 30
                self.damage = 8
                self.defense = 5
                # Track combat advantage
                self.triangle_advantage = None
        
        # Player units with different weapons
        self.units["sword_user"] = DummyUnit("sword_user", "Swordsman", "PLAYER", (3, 3), WeaponType.SWORD, 25, 25)
        self.units["lance_user"] = DummyUnit("lance_user", "Lancer", "PLAYER", (7, 3), WeaponType.LANCE, 28, 28)
        self.units["axe_user"] = DummyUnit("axe_user", "Axeman", "PLAYER", (11, 3), WeaponType.AXE, 30, 30)
        
        # Enemy units with different weapons
        self.units["enemy_sword"] = DummyUnit("enemy_sword", "Enemy Swordsman", "ENEMY", (3, 9), WeaponType.SWORD, 25, 25)
        self.units["enemy_lance"] = DummyUnit("enemy_lance", "Enemy Lancer", "ENEMY", (7, 9), WeaponType.LANCE, 28, 28)
        self.units["enemy_axe"] = DummyUnit("enemy_axe", "Enemy Axeman", "ENEMY", (11, 9), WeaponType.AXE, 30, 30)
    
    def get_map_dimensions(self):
        """Get the dimensions of the map."""
        return (self.map_width, self.map_height)
    
    def get_terrain_at(self, position):
        """Get the terrain at the specified position."""
        x, y = position
        if 0 <= x < self.map_width and 0 <= y < self.map_height:
            return self.terrain_grid[y][x]
        return None
    
    def get_all_units(self):
        """Get all units."""
        return list(self.units.values())
    
    def get_unit(self, unit_id):
        """Get a unit by ID."""
        return self.units.get(unit_id)
    
    def apply_weapon_triangle(self, attacker_id, defender_id):
        """Apply weapon triangle advantages/disadvantages."""
        attacker = self.get_unit(attacker_id)
        defender = self.get_unit(defender_id)
        
        if not attacker or not defender:
            return
            
        # Reset previous advantages
        attacker.triangle_advantage = None
        defender.triangle_advantage = None
        
        # Weapon triangle: Sword > Axe > Lance > Sword
        if attacker.weapon_type == WeaponType.SWORD and defender.weapon_type == WeaponType.AXE:
            # Sword has advantage over Axe
            attacker.triangle_advantage = "Advantage"
            defender.triangle_advantage = "Disadvantage"
            attacker.hit_rate += 15
            attacker.damage += 1
            defender.hit_rate -= 15
        elif attacker.weapon_type == WeaponType.AXE and defender.weapon_type == WeaponType.LANCE:
            # Axe has advantage over Lance
            attacker.triangle_advantage = "Advantage"
            defender.triangle_advantage = "Disadvantage"
            attacker.hit_rate += 15
            attacker.damage += 1
            defender.hit_rate -= 15
        elif attacker.weapon_type == WeaponType.LANCE and defender.weapon_type == WeaponType.SWORD:
            # Lance has advantage over Sword
            attacker.triangle_advantage = "Advantage"
            defender.triangle_advantage = "Disadvantage"
            attacker.hit_rate += 15
            attacker.damage += 1
            defender.hit_rate -= 15
        elif defender.weapon_type == WeaponType.SWORD and attacker.weapon_type == WeaponType.AXE:
            # Defender Sword has advantage over Attacker Axe
            defender.triangle_advantage = "Advantage"
            attacker.triangle_advantage = "Disadvantage"
            defender.hit_rate += 15
            defender.damage += 1
            attacker.hit_rate -= 15
        elif defender.weapon_type == WeaponType.AXE and attacker.weapon_type == WeaponType.LANCE:
            # Defender Axe has advantage over Attacker Lance
            defender.triangle_advantage = "Advantage"
            attacker.triangle_advantage = "Disadvantage"
            defender.hit_rate += 15
            defender.damage += 1
            attacker.hit_rate -= 15
        elif defender.weapon_type == WeaponType.LANCE and attacker.weapon_type == WeaponType.SWORD:
            # Defender Lance has advantage over Attacker Sword
            defender.triangle_advantage = "Advantage"
            attacker.triangle_advantage = "Disadvantage"
            defender.hit_rate += 15
            defender.damage += 1
            attacker.hit_rate -= 15

class WeaponTriangleDemo:
    """Class to demonstrate weapon triangle system."""
    
    def __init__(self):
        """Initialize the demonstration."""
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.window_size = (1024, 768)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Weapon Triangle Demonstration")
        
        # Create game state manager
        self.gsm = DummyGameStateManager()
        
        # Create renderer
        self.renderer = GameRenderer(self.gsm, self.window_size)
        
        # Center camera on the map
        self.renderer.center_camera_on_position(7, 7)
        
        # Demo timers and state
        self.timers = {}
        self.start_time = time.time()
        self.max_runtime = 60  # Force exit after 60 seconds
        self.exit_message_shown = False
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Create a visual logger
        self.log_file = os.path.join(PROJECT_ROOT, "logs", "mechanic_tests", "combat", f"weapon_triangle_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self.visual_logger = VisualScenarioLogger(
            game_state_manager=self.gsm,
            enabled=True,
            fixed_log_path=self.log_file
        )
        
        # Setup fonts
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
    
    def setup_demos(self):
        """Set up the demonstration timers."""
        # Show introduction text
        self.timers["intro"] = self.start_time + 1.0
        
        # Demo 1: Sword vs Axe (Sword advantage)
        self.timers["sword_vs_axe"] = self.start_time + 5.0
        
        # Demo 2: Axe vs Lance (Axe advantage)
        self.timers["axe_vs_lance"] = self.start_time + 15.0
        
        # Demo 3: Lance vs Sword (Lance advantage)
        self.timers["lance_vs_sword"] = self.start_time + 25.0
        
        # Demo 4: Same weapon type (No advantage)
        self.timers["same_weapon"] = self.start_time + 35.0
        
        # End demo
        self.timers["end"] = self.start_time + 45.0
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        """Update the demonstration state."""
        current_time = time.time()
        
        # Force exit if max runtime exceeded
        if current_time - self.start_time > self.max_runtime:
            print(f"\nMax runtime ({self.max_runtime} seconds) exceeded. Exiting...")
            self.running = False
            return
        
        # Introduction
        if "intro" in self.timers and current_time >= self.timers["intro"]:
            # Log the introduction
            self.visual_logger.log_action("SYSTEM", "INTRO", "Weapon Triangle Demonstration")
            self.visual_logger.log_action("SYSTEM", "INFO", "Sword > Axe > Lance > Sword")
            self.visual_logger.log_action("SYSTEM", "INFO", "Advantage grants +15 Hit and +1 Damage")
            
            # Highlight weapon types on the map
            self.highlight_units_by_weapon()
            
            del self.timers["intro"]
        
        # Demo 1: Sword vs Axe
        if "sword_vs_axe" in self.timers and current_time >= self.timers["sword_vs_axe"]:
            self.show_combat_demo("sword_user", "enemy_axe", "Sword vs Axe")
            del self.timers["sword_vs_axe"]
        
        # Demo 2: Axe vs Lance
        if "axe_vs_lance" in self.timers and current_time >= self.timers["axe_vs_lance"]:
            self.show_combat_demo("axe_user", "enemy_lance", "Axe vs Lance")
            del self.timers["axe_vs_lance"]
        
        # Demo 3: Lance vs Sword
        if "lance_vs_sword" in self.timers and current_time >= self.timers["lance_vs_sword"]:
            self.show_combat_demo("lance_user", "enemy_sword", "Lance vs Sword")
            del self.timers["lance_vs_sword"]
        
        # Demo 4: Same weapon type (no advantage)
        if "same_weapon" in self.timers and current_time >= self.timers["same_weapon"]:
            self.show_combat_demo("sword_user", "enemy_sword", "Sword vs Sword (No Advantage)")
            del self.timers["same_weapon"]
        
        # End demo
        if "end" in self.timers and current_time >= self.timers["end"]:
            self.visual_logger.log_action("SYSTEM", "END", "Weapon Triangle Demonstration Complete")
            self.visual_logger.finalize_log()
            
            print(f"\nDemonstration complete. Log saved to: {self.log_file}")
            print("Press ESC to exit.")
            
            self.exit_message_shown = True
            del self.timers["end"]
        
        # Update renderer
        self.renderer.update()
    
    def highlight_units_by_weapon(self):
        """Highlight units on the map by weapon type."""
        # Group units by weapon type
        weapon_groups = {
            WeaponType.SWORD: [],
            WeaponType.LANCE: [],
            WeaponType.AXE: []
        }
        
        for unit in self.gsm.get_all_units():
            if unit.weapon_type in weapon_groups:
                weapon_groups[unit.weapon_type].append(unit.position)
        
        # Highlight each group with a different color
        colors = {
            WeaponType.SWORD: (200, 50, 50, 150),  # Red
            WeaponType.LANCE: (50, 50, 200, 150),  # Blue
            WeaponType.AXE: (50, 200, 50, 150)     # Green
        }
        
        for weapon_type, positions in weapon_groups.items():
            if positions:
                self.renderer.play_animation(
                    AnimationType.HIGHLIGHT_TILES,
                    tile_positions=positions,
                    color=colors[weapon_type],
                    duration_ms=10000  # 10 seconds
                )
                
                # Log the highlighting
                self.visual_logger.log_action("SYSTEM", "HIGHLIGHT", 
                                           f"Highlighted {weapon_type.value} users on the map")
    
    def show_combat_demo(self, attacker_id, defender_id, description):
        """Show a combat demonstration between two units."""
        attacker = self.gsm.get_unit(attacker_id)
        defender = self.gsm.get_unit(defender_id)
        
        if not attacker or not defender:
            return
        
        # Log the combat start
        self.visual_logger.log_action("SYSTEM", "COMBAT_START", description)
        
        # Log pre-combat stats
        self.visual_logger.log_action(attacker.id, "PRE_COMBAT", 
                                   f"{attacker.name}: Hit: {attacker.hit_rate}, Damage: {attacker.damage}")
        self.visual_logger.log_action(defender.id, "PRE_COMBAT", 
                                   f"{defender.name}: Hit: {defender.hit_rate}, Damage: {defender.damage}")
        
        # Apply weapon triangle effects
        self.gsm.apply_weapon_triangle(attacker_id, defender_id)
        
        # Log the weapon triangle effects
        if attacker.triangle_advantage:
            self.visual_logger.log_action(attacker.id, "TRIANGLE", 
                                      f"{attacker.triangle_advantage}: +15 Hit, +1 Damage")
        if defender.triangle_advantage:
            self.visual_logger.log_action(defender.id, "TRIANGLE", 
                                      f"{defender.triangle_advantage}: +15 Hit, +1 Damage (if counterattack)")
        
        # Log post-triangle stats
        self.visual_logger.log_action(attacker.id, "POST_TRIANGLE", 
                                   f"{attacker.name}: Hit: {attacker.hit_rate}, Damage: {attacker.damage}")
        self.visual_logger.log_action(defender.id, "POST_TRIANGLE", 
                                   f"{defender.name}: Hit: {defender.hit_rate}, Damage: {defender.damage}")
        
        # Calculate and apply combat results
        hit_roll = random.randint(1, 100)
        hit_success = hit_roll <= attacker.hit_rate
        
        # Show attack animation
        self.renderer.play_animation(
            AnimationType.ATTACK,
            attacker_pos=attacker.position,
            defender_pos=defender.position,
            duration=1000
        )
        
        # Log the attack roll
        self.visual_logger.log_action(attacker.id, "ATTACK_ROLL", 
                                   f"Roll: {hit_roll}, Need: {attacker.hit_rate}, Hit: {hit_success}")
        
        # Show damage animation if hit succeeds
        if hit_success:
            damage_dealt = max(1, attacker.damage - defender.defense)
            defender.current_hp = max(0, defender.current_hp - damage_dealt)
            
            # Show damage animation
            self.renderer.play_animation(
                AnimationType.TAKE_DAMAGE,
                unit_pos=defender.position,
                damage=damage_dealt,
                duration=1000
            )
            
            # Log the damage
            self.visual_logger.log_action(defender.id, "DAMAGE_TAKEN", 
                                      f"Took {damage_dealt} damage, HP: {defender.current_hp}/{defender.max_hp}")
        else:
            # Show miss animation (just a text indicator)
            self.visual_logger.log_action(attacker.id, "MISS", f"Attack missed!")
        
        # Log combat end
        self.visual_logger.log_action("SYSTEM", "COMBAT_END", f"{description} complete")
    
    def render(self):
        """Render the demonstration."""
        # Let the renderer handle the base rendering
        self.renderer.render()
        
        # Add custom UI elements for the weapon triangle
        self.draw_weapon_triangle_ui()
        
        # Update the display
        pygame.display.flip()
    
    def draw_weapon_triangle_ui(self):
        """Draw UI elements explaining the weapon triangle."""
        # Draw a semi-transparent background panel at the top of the screen
        panel_rect = pygame.Rect(10, 10, self.window_size[0] - 20, 100)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(panel_surface, panel_rect)
        
        # Draw title
        title_text = self.title_font.render("Weapon Triangle System", True, (255, 255, 255))
        self.screen.blit(title_text, (20, 20))
        
        # Draw weapon relationships
        relationship_text = self.font.render("Sword > Axe > Lance > Sword", True, (255, 255, 255))
        self.screen.blit(relationship_text, (20, 50))
        
        # Draw advantage bonus
        advantage_text = self.font.render("Advantage grants: +15 Hit Rate, +1 Damage", True, (255, 255, 255))
        self.screen.blit(advantage_text, (20, 70))
        
        # Draw color key
        colors = [
            ("Sword", (200, 50, 50)), 
            ("Lance", (50, 50, 200)), 
            ("Axe", (50, 200, 50))
        ]
        
        x_position = self.window_size[0] - 200
        for i, (weapon, color) in enumerate(colors):
            # Draw color square
            pygame.draw.rect(self.screen, color, (x_position, 40 + i*20, 15, 15))
            # Draw weapon name
            weapon_text = self.font.render(weapon, True, (255, 255, 255))
            self.screen.blit(weapon_text, (x_position + 25, 40 + i*20))
    
    def run(self):
        """Run the demonstration."""
        print("Weapon Triangle Demonstration")
        print("Press ESC to exit")
        
        # Setup demos
        self.setup_demos()
        
        # Main loop
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        # Clean up
        self.renderer.close()
        pygame.quit()

def main():
    """Main entry point for the demonstration."""
    demo = WeaponTriangleDemo()
    demo.run()

if __name__ == "__main__":
    main() 