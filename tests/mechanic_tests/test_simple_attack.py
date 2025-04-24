#!/usr/bin/env python3
"""
Simple Attack Demonstration

This script demonstrates combat mechanics with simplified animations directly with pygame.
"""

import os
import sys
import time
import math
import random
import pygame

# Add the project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

class UnitSprite:
    """Represents a unit on the game map."""
    
    def __init__(self, name, faction, position, unit_type, color):
        """Initialize the unit.
        
        Args:
            name: Name of the unit
            faction: Faction the unit belongs to ("PLAYER" or "ENEMY")
            position: (x, y) tuple of the unit's position
            unit_type: Type of unit ("KNIGHT", "ARCHER", "MAGE")
            color: Color tuple (r, g, b) for the unit's sprite
        """
        self.name = name
        self.faction = faction
        self.position = position
        self.unit_type = unit_type
        self.color = color
        self.current_hp = 30
        self.max_hp = 30
        self.sprite = pygame.Surface((24, 24))
        self.sprite.fill(color)
        self.moving = False
        self.move_path = []
        self.move_progress = 0

class ParticleEffect:
    """Simple particle effect system."""
    
    def __init__(self, position, effect_type="sparks", num_particles=20, duration=800):
        """Initialize the particle effect.
        
        Args:
            position: (x, y) position for the effect
            effect_type: Type of effect ("sparks", "explosion", "magic")
            num_particles: Number of particles to create
            duration: Duration of the effect in milliseconds
        """
        self.position = position
        self.effect_type = effect_type
        self.start_time = time.time()
        self.duration = duration / 1000.0  # Convert to seconds
        self.particles = []
        
        # Generate particles based on effect type
        if effect_type == "sparks":
            color = (255, 255, 0)  # Yellow
            size_range = (2, 4)
            speed_range = (30, 100)
        elif effect_type == "explosion":
            color = (255, 100, 0)  # Orange
            size_range = (3, 6)
            speed_range = (50, 150)
        elif effect_type == "magic":
            color = (100, 100, 255)  # Blue
            size_range = (2, 5)
            speed_range = (40, 120)
        else:
            color = (255, 255, 255)  # White
            size_range = (2, 4)
            speed_range = (30, 100)
        
        for _ in range(num_particles):
            # Random angle and speed
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(speed_range[0], speed_range[1])
            
            # Calculate velocity components
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Random size and life
            size = random.uniform(size_range[0], size_range[1])
            life = random.uniform(0.3, self.duration * 0.9)
            
            # Create the particle
            self.particles.append({
                'position': [float(position[0]), float(position[1])],
                'velocity': [vx, vy],
                'size': size,
                'color': color,
                'life': life,
                'remaining': life
            })
    
    def update(self, delta_time):
        """Update all particles in the effect.
        
        Args:
            delta_time: Time since last update in seconds
        """
        for particle in self.particles[:]:
            # Update position
            particle['position'][0] += particle['velocity'][0] * delta_time
            particle['position'][1] += particle['velocity'][1] * delta_time
            
            # Apply gravity for some effects
            if self.effect_type in ["explosion", "sparks"]:
                particle['velocity'][1] += 100 * delta_time  # Gravity
            
            # Decrease remaining life
            particle['remaining'] -= delta_time
            
            # Remove dead particles
            if particle['remaining'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Draw all particles to the surface.
        
        Args:
            surface: Surface to draw on
        """
        for particle in self.particles:
            # Calculate opacity based on remaining life
            alpha = int(255 * particle['remaining'] / particle['life'])
            
            # Create a temporary surface for the particle with alpha
            size = int(particle['size'])
            if size < 1:
                size = 1
                
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            # Draw the particle as a circle
            pygame.draw.circle(
                particle_surf, 
                (*particle['color'], alpha), 
                (size, size), 
                size
            )
            
            # Blit the particle to the main surface
            pos = (int(particle['position'][0] - size), int(particle['position'][1] - size))
            surface.blit(particle_surf, pos)
    
    def is_active(self):
        """Check if the effect is still active.
        
        Returns:
            True if the effect has particles or the duration hasn't expired
        """
        return len(self.particles) > 0 and (time.time() - self.start_time) < self.duration

class DamageNumber:
    """Floating damage number effect."""
    
    def __init__(self, position, value, color=(255, 0, 0)):
        """Initialize the damage number.
        
        Args:
            position: (x, y) position to show the number
            value: Damage value to display
            color: Color of the number
        """
        self.position = list(position)
        self.value = value
        self.color = color
        self.start_time = time.time()
        self.duration = 1.0  # 1 second
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.text = self.font.render(str(value), True, color)
        self.offset = [0, 0]
    
    def update(self, delta_time):
        """Update the damage number position.
        
        Args:
            delta_time: Time since last update in seconds
        """
        # Move upward
        self.offset[1] -= 40 * delta_time
        
        # Slight horizontal movement
        self.offset[0] += random.uniform(-5, 5) * delta_time
    
    def draw(self, surface):
        """Draw the damage number to the surface.
        
        Args:
            surface: Surface to draw on
        """
        # Calculate opacity based on remaining time
        elapsed = time.time() - self.start_time
        alpha = 255
        if elapsed > self.duration * 0.7:
            # Fade out in the last 30% of duration
            fade_progress = (elapsed - self.duration * 0.7) / (self.duration * 0.3)
            alpha = int(255 * (1 - fade_progress))
        
        # Create a surface with alpha
        if alpha < 255:
            text = self.font.render(str(self.value), True, self.color)
            text.set_alpha(alpha)
        else:
            text = self.text
        
        # Calculate draw position
        x = int(self.position[0] + self.offset[0] - text.get_width() // 2)
        y = int(self.position[1] + self.offset[1] - text.get_height() // 2)
        
        # Draw the text
        surface.blit(text, (x, y))
    
    def is_active(self):
        """Check if the damage number is still active.
        
        Returns:
            True if the duration hasn't expired
        """
        return (time.time() - self.start_time) < self.duration

class CombatDemo:
    """Simple combat demonstration."""
    
    def __init__(self):
        """Initialize the combat demo."""
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.window_size = (800, 600)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Combat Demonstration")
        
        # Tile size and grid
        self.tile_size = 40
        self.grid_width = 15
        self.grid_height = 12
        
        # Create game objects
        self.units = {
            "knight": UnitSprite("Knight", "PLAYER", (5, 5), "KNIGHT", (0, 0, 200)),
            "archer": UnitSprite("Archer", "PLAYER", (3, 6), "ARCHER", (0, 100, 255)),
            "mage": UnitSprite("Mage", "PLAYER", (4, 7), "MAGE", (100, 0, 255)),
            "enemy_knight": UnitSprite("Enemy Knight", "ENEMY", (9, 5), "KNIGHT", (200, 0, 0)),
            "enemy_archer": UnitSprite("Enemy Archer", "ENEMY", (10, 6), "ARCHER", (255, 100, 0)),
            "enemy_mage": UnitSprite("Enemy Mage", "ENEMY", (11, 7), "MAGE", (255, 0, 255))
        }
        
        # Adjust HP values
        self.units["archer"].current_hp = 20
        self.units["archer"].max_hp = 20
        self.units["mage"].current_hp = 15
        self.units["mage"].max_hp = 15
        self.units["enemy_archer"].current_hp = 18
        self.units["enemy_archer"].max_hp = 18
        self.units["enemy_mage"].current_hp = 14
        self.units["enemy_mage"].max_hp = 14
        
        # Visual effects
        self.effects = []
        self.damage_numbers = []
        
        # Animation timers and flags
        self.timers = {}
        self.start_time = time.time()
        
        # Demo state
        self.last_time = time.time()
        self.running = True
        self.clock = pygame.time.Clock()
    
    def setup_demo(self):
        """Set up the combat demonstration timers."""
        # Demo 1: Knight vs Enemy Knight
        self.timers["knight_attack"] = self.start_time + 2.0
        
        # Demo 2: Archer vs Enemy Archer
        self.timers["archer_attack"] = self.start_time + 6.0
        
        # Demo 3: Mage vs Enemy Mage
        self.timers["mage_attack"] = self.start_time + 10.0
        
        # Add title text
        print("Combat Demonstration")
        print("Press ESC to exit")
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        """Update the demo state."""
        # Calculate delta time
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # Demo 1: Knight vs Enemy Knight
        if "knight_attack" in self.timers and current_time >= self.timers["knight_attack"]:
            print("\nDemo 1: Knight attacks Enemy Knight!")
            
            # Create sparks effect at target position
            target_pos = self.grid_to_screen(self.units["enemy_knight"].position)
            self.effects.append(ParticleEffect(
                position=target_pos,
                effect_type="sparks",
                num_particles=20,
                duration=800
            ))
            
            # Apply damage to enemy knight
            damage = 8
            self.units["enemy_knight"].current_hp -= damage
            print(f"  Enemy Knight takes {damage} damage! HP: {self.units['enemy_knight'].current_hp}/{self.units['enemy_knight'].max_hp}")
            
            # Add damage number
            self.damage_numbers.append(DamageNumber(
                position=target_pos,
                value=damage
            ))
            
            # Set up enemy counterattack
            self.timers["enemy_knight_attack"] = current_time + 1.0
            
            # Remove the timer
            del self.timers["knight_attack"]
        
        # Enemy Knight counterattack
        if "enemy_knight_attack" in self.timers and current_time >= self.timers["enemy_knight_attack"]:
            print("  Enemy Knight counterattacks!")
            
            # Create sparks effect at target position
            target_pos = self.grid_to_screen(self.units["knight"].position)
            self.effects.append(ParticleEffect(
                position=target_pos,
                effect_type="sparks",
                num_particles=15,
                duration=600
            ))
            
            # Apply damage to knight
            damage = 6
            self.units["knight"].current_hp -= damage
            print(f"  Knight takes {damage} damage! HP: {self.units['knight'].current_hp}/{self.units['knight'].max_hp}")
            
            # Add damage number
            self.damage_numbers.append(DamageNumber(
                position=target_pos,
                value=damage
            ))
            
            # Remove the timer
            del self.timers["enemy_knight_attack"]
        
        # Demo 2: Archer vs Enemy Archer
        if "archer_attack" in self.timers and current_time >= self.timers["archer_attack"]:
            print("\nDemo 2: Archer shoots Enemy Archer!")
            
            # Create arrow effect (basic sparks for now)
            target_pos = self.grid_to_screen(self.units["enemy_archer"].position)
            self.effects.append(ParticleEffect(
                position=target_pos,
                effect_type="sparks",
                num_particles=10,
                duration=500
            ))
            
            # Apply damage to enemy archer
            damage = 7
            self.units["enemy_archer"].current_hp -= damage
            print(f"  Enemy Archer takes {damage} damage! HP: {self.units['enemy_archer'].current_hp}/{self.units['enemy_archer'].max_hp}")
            
            # Add damage number
            self.damage_numbers.append(DamageNumber(
                position=target_pos,
                value=damage
            ))
            
            # Set up enemy counterattack
            self.timers["enemy_archer_attack"] = current_time + 1.0
            
            # Remove the timer
            del self.timers["archer_attack"]
        
        # Enemy Archer counterattack
        if "enemy_archer_attack" in self.timers and current_time >= self.timers["enemy_archer_attack"]:
            print("  Enemy Archer returns fire!")
            
            # Create arrow effect
            target_pos = self.grid_to_screen(self.units["archer"].position)
            self.effects.append(ParticleEffect(
                position=target_pos,
                effect_type="sparks",
                num_particles=10,
                duration=500
            ))
            
            # Apply damage to archer
            damage = 6
            self.units["archer"].current_hp -= damage
            print(f"  Archer takes {damage} damage! HP: {self.units['archer'].current_hp}/{self.units['archer'].max_hp}")
            
            # Add damage number
            self.damage_numbers.append(DamageNumber(
                position=target_pos,
                value=damage
            ))
            
            # Remove the timer
            del self.timers["enemy_archer_attack"]
        
        # Demo 3: Mage vs Enemy Mage
        if "mage_attack" in self.timers and current_time >= self.timers["mage_attack"]:
            print("\nDemo 3: Mage casts fireball at Enemy Mage!")
            
            # Create explosion effect
            target_pos = self.grid_to_screen(self.units["enemy_mage"].position)
            self.effects.append(ParticleEffect(
                position=target_pos,
                effect_type="explosion",
                num_particles=30,
                duration=800
            ))
            
            # Apply damage to enemy mage
            damage = 10
            self.units["enemy_mage"].current_hp -= damage
            print(f"  Enemy Mage takes {damage} damage! HP: {self.units['enemy_mage'].current_hp}/{self.units['enemy_mage'].max_hp}")
            
            # Add damage number
            self.damage_numbers.append(DamageNumber(
                position=target_pos,
                value=damage
            ))
            
            # Set up enemy counterattack
            self.timers["enemy_mage_attack"] = current_time + 1.0
            
            # Remove the timer
            del self.timers["mage_attack"]
        
        # Enemy Mage counterattack
        if "enemy_mage_attack" in self.timers and current_time >= self.timers["enemy_mage_attack"]:
            print("  Enemy Mage casts lightning bolt!")
            
            # Create lightning effect
            target_pos = self.grid_to_screen(self.units["mage"].position)
            self.effects.append(ParticleEffect(
                position=target_pos,
                effect_type="magic",
                num_particles=25,
                duration=700
            ))
            
            # Apply damage to mage
            damage = 9
            self.units["mage"].current_hp -= damage
            print(f"  Mage takes {damage} damage! HP: {self.units['mage'].current_hp}/{self.units['mage'].max_hp}")
            
            # Add damage number
            self.damage_numbers.append(DamageNumber(
                position=target_pos,
                value=damage
            ))
            
            # Remove the timer
            del self.timers["enemy_mage_attack"]
        
        # Update units
        for unit in self.units.values():
            # Update movement animations here if needed
            pass
        
        # Update effects
        for effect in list(self.effects):
            effect.update(delta_time)
            if not effect.is_active():
                self.effects.remove(effect)
        
        # Update damage numbers
        for number in list(self.damage_numbers):
            number.update(delta_time)
            if not number.is_active():
                self.damage_numbers.remove(number)
        
        # Check if all demos are complete
        if len(self.timers) == 0 and len(self.effects) == 0 and len(self.damage_numbers) == 0:
            # Exit after a short delay
            if not hasattr(self, 'exit_timer'):
                self.exit_timer = current_time + 3.0
                print("\nDemonstration complete. Exiting in 3 seconds...")
            elif current_time >= self.exit_timer:
                self.running = False
    
    def grid_to_screen(self, grid_pos):
        """Convert grid coordinates to screen coordinates.
        
        Args:
            grid_pos: (x, y) grid position
            
        Returns:
            (screen_x, screen_y) tuple of screen coordinates
        """
        grid_x, grid_y = grid_pos
        screen_x = grid_x * self.tile_size + self.tile_size // 2
        screen_y = grid_y * self.tile_size + self.tile_size // 2
        return (screen_x, screen_y)
    
    def draw(self):
        """Draw the current state of the demo."""
        # Clear the screen
        self.screen.fill((50, 50, 50))
        
        # Draw grid
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(self.screen, (80, 80, 80), rect, 1)
        
        # Draw units
        for unit in self.units.values():
            # Convert grid position to screen position
            screen_x, screen_y = self.grid_to_screen(unit.position)
            
            # Draw unit sprite (centered on the tile)
            screen_x -= unit.sprite.get_width() // 2
            screen_y -= unit.sprite.get_height() // 2
            self.screen.blit(unit.sprite, (screen_x, screen_y))
            
            # Draw HP bar
            hp_width = 30
            hp_height = 4
            hp_x = screen_x - (hp_width - unit.sprite.get_width()) // 2
            hp_y = screen_y + unit.sprite.get_height() + 2
            
            # Background
            pygame.draw.rect(self.screen, (50, 50, 50), (hp_x, hp_y, hp_width, hp_height))
            
            # HP fill
            hp_fill_width = int(hp_width * (unit.current_hp / unit.max_hp))
            hp_color = (0, 255, 0) if unit.faction == "PLAYER" else (255, 0, 0)
            pygame.draw.rect(self.screen, hp_color, (hp_x, hp_y, hp_fill_width, hp_height))
            
            # Border
            pygame.draw.rect(self.screen, (200, 200, 200), (hp_x, hp_y, hp_width, hp_height), 1)
        
        # Draw effects
        for effect in self.effects:
            effect.draw(self.screen)
        
        # Draw damage numbers
        for number in self.damage_numbers:
            number.draw(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Run the demonstration."""
        self.setup_demo()
        
        # Main loop
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        # Clean up
        pygame.quit()

def main():
    """Main entry point for the demonstration."""
    demo = CombatDemo()
    demo.run()

if __name__ == "__main__":
    main() 