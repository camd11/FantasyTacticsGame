#!/usr/bin/env python3
"""
Attack Mechanics Demonstration

This script demonstrates combat mechanics including melee attacks, ranged attacks,
and magic attacks with appropriate visual effects and animations.
"""

import os
import sys
import time
import math
import random
import pygame

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import game renderer and animation types
from src.ui.pygame_renderer import GameRenderer, AnimationType, ParticleEffectAnimation

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
            
            def __init__(self, name):
                self.name = name
        
        # Fill the map with plains
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.terrain_grid[y][x] = TerrainType("PLAIN")
        
        # Add some variety
        # Forests
        for x, y in [(3, 4), (4, 4), (3, 5), (4, 5), (8, 8), (9, 9)]:
            self.terrain_grid[y][x] = TerrainType("FOREST")
                
        # Mountains
        for x, y in [(11, 6), (12, 6), (11, 7), (12, 7)]:
            self.terrain_grid[y][x] = TerrainType("MOUNTAIN")
        
        # Create test units
        self.create_units()
    
    def create_units(self):
        """Create test units."""
        class DummyUnit:
            def __init__(self, id, name, faction, position, unit_type, weapon_type, hp, max_hp, attack_range=(1, 1)):
                self.id = id
                self.name = name
                self.faction = type('Faction', (), {'name': faction})
                self.position = position
                self.movement_type = type('MovementType', (), {'name': unit_type})
                self.weapon_type = weapon_type
                self.current_hp = hp
                self.max_hp = max_hp
                self.attack_range = attack_range
                self.disposition = type('Disposition', (), {'name': 'ACTIVE'})
                self.status_effects = []
        
        # Player units
        self.units["knight"] = DummyUnit("knight", "Knight", "PLAYER", (3, 3), "CAVALRY", "SWORD", 30, 30)
        self.units["archer"] = DummyUnit("archer", "Archer", "PLAYER", (2, 5), "INFANTRY", "BOW", 20, 20, (2, 3))
        self.units["mage"] = DummyUnit("mage", "Mage", "PLAYER", (4, 5), "INFANTRY", "MAGIC", 15, 15, (1, 2))
        
        # Enemy units
        self.units["enemy_knight"] = DummyUnit("enemy_knight", "Enemy Knight", "ENEMY", (7, 3), "CAVALRY", "SWORD", 28, 28)
        self.units["enemy_archer"] = DummyUnit("enemy_archer", "Enemy Archer", "ENEMY", (9, 6), "INFANTRY", "BOW", 18, 18, (2, 3))
        self.units["enemy_mage"] = DummyUnit("enemy_mage", "Enemy Mage", "ENEMY", (8, 4), "INFANTRY", "MAGIC", 14, 14, (1, 2))
    
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

class ExtendedGameRenderer(GameRenderer):
    """Extended game renderer with additional utility methods."""
    
    def __init__(self, game_state_manager, window_size=(800, 600), title="Fantasy Tactics Game"):
        """Initialize the extended renderer."""
        super().__init__(game_state_manager, window_size, title)
        # Additional storage for effects
        self.effects = []
    
    def map_to_screen_coords(self, map_x, map_y):
        """Convert map coordinates to screen coordinates.
        
        Args:
            map_x: Map x-coordinate
            map_y: Map y-coordinate
            
        Returns:
            (screen_x, screen_y) tuple of screen coordinates
        """
        # Calculate the screen coordinates based on the tile size and camera offset
        # Use self.grid_to_screen if it's available
        if hasattr(self, 'grid_to_screen'):
            return self.grid_to_screen(map_x, map_y)
        
        # Fallback implementation
        tile_size = 64  # Default tile size in GameRenderer
        screen_x = int((map_x - self.camera_offset[0]) * tile_size)
        screen_y = int((map_y - self.camera_offset[1]) * tile_size)
        
        return (screen_x, screen_y)
    
    def add_effect(self, effect):
        """Add a particle effect to the renderer.
        
        Args:
            effect: The effect to add (usually a ParticleEffectAnimation)
        """
        self.effects.append(effect)
    
    def update(self):
        """Extended update method that also updates effects."""
        # Call parent update
        super().update()
        
        # Update effects
        for effect in list(self.effects):
            effect.update()
            if not effect.is_active:
                self.effects.remove(effect)
    
    def render(self):
        """Extended render method that also draws effects."""
        # Call parent render (clears screen, draws map, units, animations)
        super().render()
        
        # Draw effects on top
        for effect in self.effects:
            effect.draw(self.screen)
        
        # Update display
        pygame.display.flip()

class AttackMechanicsDemo:
    """Class to demonstrate attack mechanics."""
    
    def __init__(self):
        """Initialize the demonstration."""
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.window_size = (1024, 768)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Attack Mechanics Demonstration")
        
        # Create game state manager
        self.gsm = DummyGameStateManager()
        
        # Create renderer
        self.renderer = ExtendedGameRenderer(self.gsm, self.window_size)
        
        # Center camera on the map
        self.renderer.center_camera_on_position(7, 5)
        
        # Demo timers and state
        self.timers = {}
        self.start_time = time.time()
        self.max_runtime = 60  # Force exit after 60 seconds
        self.exit_message_shown = False
        self.running = True
        self.clock = pygame.time.Clock()
    
    def setup_demos(self):
        """Set up the demonstration timers."""
        # Add highlights for units
        self.timers["highlight_units"] = self.start_time + 1.0
        
        # Demo 1: Melee combat between knights
        self.timers["melee_combat"] = self.start_time + 4.0
        
        # Demo 2: Ranged combat with archers
        self.timers["ranged_combat"] = self.start_time + 15.0
        
        # Demo 3: Magic combat with mages
        self.timers["magic_combat"] = self.start_time + 30.0
    
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
        
        # Highlight units
        if "highlight_units" in self.timers and current_time >= self.timers["highlight_units"]:
            print("\nHighlighting units:")
            
            # Group units by faction
            player_units = []
            enemy_units = []
            
            for unit in self.gsm.get_all_units():
                if unit.faction.name == "PLAYER":
                    player_units.append(unit.position)
                    print(f"  Player: {unit.name} ({unit.weapon_type}) at {unit.position}")
                else:
                    enemy_units.append(unit.position)
                    print(f"  Enemy: {unit.name} ({unit.weapon_type}) at {unit.position}")
            
            # Highlight player units in blue
            self.renderer.play_animation(
                AnimationType.HIGHLIGHT_TILES,
                tile_positions=player_units,
                color=(0, 100, 255, 100),
                duration_ms=3000
            )
            
            # Highlight enemy units in red
            self.renderer.play_animation(
                AnimationType.HIGHLIGHT_TILES,
                tile_positions=enemy_units,
                color=(255, 50, 50, 100),
                duration_ms=3000
            )
            
            del self.timers["highlight_units"]
        
        # Demo 1: Melee combat between knights
        if "melee_combat" in self.timers and current_time >= self.timers["melee_combat"]:
            print("\nDemo 1: Melee Combat - Knight vs Enemy Knight")
            
            # Get units
            knight = self.gsm.get_unit("knight")
            enemy_knight = self.gsm.get_unit("enemy_knight")
            
            # Move knight closer to enemy knight
            knight_path = [(3, 3), (5, 3)]
            
            print(f"  Knight moves from {knight.position} to {knight_path[-1]}")
            self.renderer.play_animation(
                AnimationType.MOVE, 
                unit_id="knight", 
                path=knight_path
            )
            knight.position = knight_path[-1]
            
            # Set up attack timer after movement completes
            self.timers["knight_attack"] = current_time + 2.0
            
            del self.timers["melee_combat"]
        
        # Knight attack timer
        if "knight_attack" in self.timers and current_time >= self.timers["knight_attack"]:
            knight = self.gsm.get_unit("knight")
            enemy_knight = self.gsm.get_unit("enemy_knight")
            
            # Highlight attack range
            attack_range = [(6, 3)]
            self.renderer.play_animation(
                AnimationType.HIGHLIGHT_TILES,
                tile_positions=attack_range,
                color=(255, 0, 0, 150),
                duration_ms=1000
            )
            
            # Set up final attack timer
            self.timers["knight_execute_attack"] = current_time + 1.0
            
            del self.timers["knight_attack"]
        
        # Knight execute attack timer
        if "knight_execute_attack" in self.timers and current_time >= self.timers["knight_execute_attack"]:
            knight = self.gsm.get_unit("knight")
            enemy_knight = self.gsm.get_unit("enemy_knight")
            
            # Play attack animation
            print(f"  Knight attacks Enemy Knight!")
            self.renderer.play_animation(
                AnimationType.ATTACK,
                attacker_id="knight",
                defender_id="enemy_knight"
            )
            
            # Add particle effect for sword clash
            tile_pos = enemy_knight.position
            screen_pos = self.renderer.map_to_screen_coords(tile_pos[0], tile_pos[1])
            self.renderer.add_effect(ParticleEffectAnimation(
                position=screen_pos,
                effect_type="sparks",
                num_particles=20,
                duration_ms=500
            ))
            
            # Reduce enemy health
            damage = 8
            enemy_knight.current_hp -= damage
            print(f"  Enemy Knight takes {damage} damage! HP: {enemy_knight.current_hp}/{enemy_knight.max_hp}")
            
            # Show damage number
            self.renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=enemy_knight.position,
                value=damage
            )
            
            # Enemy counterattack timer
            self.timers["enemy_knight_counterattack"] = current_time + 1.5
            
            del self.timers["knight_execute_attack"]
        
        # Enemy knight counterattack
        if "enemy_knight_counterattack" in self.timers and current_time >= self.timers["enemy_knight_counterattack"]:
            knight = self.gsm.get_unit("knight")
            enemy_knight = self.gsm.get_unit("enemy_knight")
            
            # Play counterattack animation
            print(f"  Enemy Knight counterattacks!")
            self.renderer.play_animation(
                AnimationType.ATTACK,
                attacker_id="enemy_knight",
                defender_id="knight"
            )
            
            # Add particle effect for sword clash
            tile_pos = knight.position
            screen_pos = self.renderer.map_to_screen_coords(tile_pos[0], tile_pos[1])
            self.renderer.add_effect(ParticleEffectAnimation(
                position=screen_pos,
                effect_type="sparks",
                num_particles=15,
                duration_ms=500
            ))
            
            # Reduce player health
            damage = 6
            knight.current_hp -= damage
            print(f"  Knight takes {damage} damage! HP: {knight.current_hp}/{knight.max_hp}")
            
            # Show damage number
            self.renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=knight.position,
                value=damage
            )
            
            del self.timers["enemy_knight_counterattack"]
        
        # Demo 2: Ranged combat with archers
        if "ranged_combat" in self.timers and current_time >= self.timers["ranged_combat"]:
            print("\nDemo 2: Ranged Combat - Archer vs Enemy Archer")
            
            # Get units
            archer = self.gsm.get_unit("archer")
            enemy_archer = self.gsm.get_unit("enemy_archer")
            
            # Move archer to better position
            archer_path = [(2, 5), (4, 7)]
            
            print(f"  Archer moves from {archer.position} to {archer_path[-1]}")
            self.renderer.play_animation(
                AnimationType.MOVE, 
                unit_id="archer", 
                path=archer_path
            )
            archer.position = archer_path[-1]
            
            # Set up attack timer after movement completes
            self.timers["archer_attack"] = current_time + 2.0
            
            del self.timers["ranged_combat"]
        
        # Archer attack timer
        if "archer_attack" in self.timers and current_time >= self.timers["archer_attack"]:
            archer = self.gsm.get_unit("archer")
            enemy_archer = self.gsm.get_unit("enemy_archer")
            
            # Highlight attack range
            self.renderer.play_animation(
                AnimationType.HIGHLIGHT_TILES,
                tile_positions=[enemy_archer.position],
                color=(255, 0, 0, 150),
                duration_ms=1000
            )
            
            # Draw attack path
            self.renderer.play_animation(
                AnimationType.ATTACK_PATH,
                start_pos=archer.position,
                end_pos=enemy_archer.position,
                color=(255, 255, 0),
                duration_ms=1000
            )
            
            # Set up final attack timer
            self.timers["archer_execute_attack"] = current_time + 1.0
            
            del self.timers["archer_attack"]
        
        # Archer execute attack timer
        if "archer_execute_attack" in self.timers and current_time >= self.timers["archer_execute_attack"]:
            archer = self.gsm.get_unit("archer")
            enemy_archer = self.gsm.get_unit("enemy_archer")
            
            # Play attack animation
            print(f"  Archer shoots at Enemy Archer!")
            self.renderer.play_animation(
                AnimationType.RANGED_ATTACK,
                attacker_id="archer",
                defender_id="enemy_archer",
                projectile_type="arrow"
            )
            
            # Reduce enemy health
            damage = 7
            enemy_archer.current_hp -= damage
            print(f"  Enemy Archer takes {damage} damage! HP: {enemy_archer.current_hp}/{enemy_archer.max_hp}")
            
            # Show damage number
            self.renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=enemy_archer.position,
                value=damage
            )
            
            # Enemy counterattack timer
            self.timers["enemy_archer_counterattack"] = current_time + 1.5
            
            del self.timers["archer_execute_attack"]
        
        # Enemy archer counterattack
        if "enemy_archer_counterattack" in self.timers and current_time >= self.timers["enemy_archer_counterattack"]:
            archer = self.gsm.get_unit("archer")
            enemy_archer = self.gsm.get_unit("enemy_archer")
            
            # Play counterattack animation
            print(f"  Enemy Archer returns fire!")
            self.renderer.play_animation(
                AnimationType.RANGED_ATTACK,
                attacker_id="enemy_archer",
                defender_id="archer",
                projectile_type="arrow"
            )
            
            # Reduce player health
            damage = 6
            archer.current_hp -= damage
            print(f"  Archer takes {damage} damage! HP: {archer.current_hp}/{archer.max_hp}")
            
            # Show damage number
            self.renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=archer.position,
                value=damage
            )
            
            del self.timers["enemy_archer_counterattack"]
        
        # Demo 3: Magic combat with mages
        if "magic_combat" in self.timers and current_time >= self.timers["magic_combat"]:
            print("\nDemo 3: Magic Combat - Mage vs Enemy Mage")
            
            # Get units
            mage = self.gsm.get_unit("mage")
            enemy_mage = self.gsm.get_unit("enemy_mage")
            
            # Move mage to better position
            mage_path = [(4, 5), (6, 5)]
            
            print(f"  Mage moves from {mage.position} to {mage_path[-1]}")
            self.renderer.play_animation(
                AnimationType.MOVE, 
                unit_id="mage", 
                path=mage_path
            )
            mage.position = mage_path[-1]
            
            # Set up attack timer after movement completes
            self.timers["mage_attack"] = current_time + 2.0
            
            del self.timers["magic_combat"]
        
        # Mage attack timer
        if "mage_attack" in self.timers and current_time >= self.timers["mage_attack"]:
            mage = self.gsm.get_unit("mage")
            enemy_mage = self.gsm.get_unit("enemy_mage")
            
            # Highlight attack range
            self.renderer.play_animation(
                AnimationType.HIGHLIGHT_TILES,
                tile_positions=[enemy_mage.position],
                color=(255, 0, 0, 150),
                duration_ms=1000
            )
            
            # Set up final attack timer
            self.timers["mage_execute_attack"] = current_time + 1.0
            
            del self.timers["mage_attack"]
        
        # Mage execute attack timer
        if "mage_execute_attack" in self.timers and current_time >= self.timers["mage_execute_attack"]:
            mage = self.gsm.get_unit("mage")
            enemy_mage = self.gsm.get_unit("enemy_mage")
            
            # Play attack animation with magic effect
            print(f"  Mage casts fireball at Enemy Mage!")
            self.renderer.play_animation(
                AnimationType.MAGIC_ATTACK,
                attacker_id="mage",
                defender_id="enemy_mage",
                magic_type="fire"
            )
            
            # Add explosion effect at target location
            tile_pos = enemy_mage.position
            screen_pos = self.renderer.map_to_screen_coords(tile_pos[0], tile_pos[1])
            self.renderer.add_effect(ParticleEffectAnimation(
                position=screen_pos,
                effect_type="explosion",
                num_particles=30,
                duration_ms=800
            ))
            
            # Reduce enemy health
            damage = 10
            enemy_mage.current_hp -= damage
            print(f"  Enemy Mage takes {damage} damage! HP: {enemy_mage.current_hp}/{enemy_mage.max_hp}")
            
            # Show damage number
            self.renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=enemy_mage.position,
                value=damage
            )
            
            # Enemy counterattack timer
            self.timers["enemy_mage_counterattack"] = current_time + 1.5
            
            del self.timers["mage_execute_attack"]
        
        # Enemy mage counterattack
        if "enemy_mage_counterattack" in self.timers and current_time >= self.timers["enemy_mage_counterattack"]:
            mage = self.gsm.get_unit("mage")
            enemy_mage = self.gsm.get_unit("enemy_mage")
            
            # Play counterattack animation
            print(f"  Enemy Mage casts lightning bolt!")
            self.renderer.play_animation(
                AnimationType.MAGIC_ATTACK,
                attacker_id="enemy_mage",
                defender_id="mage",
                magic_type="lightning"
            )
            
            # Add lightning effect
            tile_pos = mage.position
            screen_pos = self.renderer.map_to_screen_coords(tile_pos[0], tile_pos[1])
            self.renderer.add_effect(ParticleEffectAnimation(
                position=screen_pos,
                effect_type="sparks",
                num_particles=40,
                duration_ms=600
            ))
            
            # Reduce player health
            damage = 9
            mage.current_hp -= damage
            print(f"  Mage takes {damage} damage! HP: {mage.current_hp}/{mage.max_hp}")
            
            # Show damage number
            self.renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=mage.position,
                value=damage
            )
            
            del self.timers["enemy_mage_counterattack"]
        
        # Update renderer
        self.renderer.update()
        
        # Check if all demos are complete
        if not any(k != "exit_timer" for k in self.timers) and not self.renderer.are_animations_active():
            if not self.exit_message_shown:
                print("\nDemonstration complete. Press ESC to exit.")
                self.exit_message_shown = True
                self.timers["exit_timer"] = current_time + 5
            elif "exit_timer" in self.timers and current_time >= self.timers["exit_timer"]:
                print("Automatically exiting...")
                self.running = False
    
    def render(self):
        """Render the demonstration."""
        self.renderer.render()
        pygame.display.flip()
    
    def run(self):
        """Run the demonstration."""
        print("Attack Mechanics Demonstration")
        print("Press ESC to exit")
        
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
    demo = AttackMechanicsDemo()
    demo.run()

if __name__ == "__main__":
    main() 