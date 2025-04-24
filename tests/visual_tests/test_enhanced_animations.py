#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Animation Test

This script demonstrates the enhanced animation features:
1. Fade animations for screen transitions
2. Animation chaining for sequential animations
3. Particle effects for visual flair
"""

import os
import sys
import time
import pygame

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import required modules from the game
from src.ui.pygame_renderer import (
    AnimationType, FadeAnimation, ParticleEffectAnimation, 
    GameRenderer, TILE_SIZE
)

class DummyGameStateManager:
    """Dummy game state manager for testing."""
    def __init__(self):
        self.current_turn = 1
        self.current_phase = "PLAYER"
        self.selected_unit = None
        self.units = {}
        
        # Create a 10x10 map
        self.terrain_grid = [[None for _ in range(10)] for _ in range(10)]
        
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
        for y in range(10):
            for x in range(10):
                self.terrain_grid[y][x] = TerrainType("PLAIN")
        
        # Add some variety
        self.terrain_grid[2][3] = TerrainType("FOREST")
        self.terrain_grid[2][4] = TerrainType("FOREST")
        self.terrain_grid[3][3] = TerrainType("FOREST")
        self.terrain_grid[5][7] = TerrainType("MOUNTAIN")
        self.terrain_grid[6][7] = TerrainType("MOUNTAIN")
        self.terrain_grid[4][1] = TerrainType("RIVER")
        self.terrain_grid[5][1] = TerrainType("RIVER")
        self.terrain_grid[6][1] = TerrainType("RIVER")
    
    def get_map_dimensions(self):
        return (10, 10)
    
    def get_terrain_at(self, position):
        x, y = position
        if 0 <= x < 10 and 0 <= y < 10:
            return self.terrain_grid[y][x]
        return None
    
    def get_all_units(self):
        return list(self.units.values())
    
    def get_unit(self, unit_id):
        return self.units.get(unit_id)

class DummyUnit:
    """Dummy unit for testing."""
    def __init__(self, id, name, faction, position, movement_type, hp, max_hp):
        self.id = id
        self.name = name
        self.faction = type('Faction', (), {'name': faction})
        self.position = position
        self.movement_type = type('MovementType', (), {'name': movement_type})
        self.current_hp = hp
        self.max_hp = max_hp
        self.disposition = type('Disposition', (), {'name': 'ACTIVE'})
        self.status_effects = []

def main():
    """Main function for testing enhanced animations."""
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Create window
    window_size = (800, 600)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Enhanced Animation Test")
    
    # Create game state manager and add units
    gsm = DummyGameStateManager()
    gsm.units["player1"] = DummyUnit("player1", "Hero", "PLAYER", (3, 4), "INFANTRY", 20, 20)
    gsm.units["enemy1"] = DummyUnit("enemy1", "Bandit", "ENEMY", (6, 5), "INFANTRY", 15, 20)
    
    # Create renderer
    renderer = GameRenderer(gsm, window_size)
    
    # Set up animation sequence for demonstration
    def setup_animation_demo():
        print("Setting up animation demonstration...")
        
        # 1. Start with a fade in
        fade_in = renderer.play_animation(AnimationType.FADE, 
                                        fade_in=True, 
                                        color=(0, 0, 0), 
                                        duration=1000)
        
        # 2. Chain a particle effect (explosion)
        explosion = fade_in.chain(
            renderer.play_animation(AnimationType.PARTICLE_EFFECT, 
                                 position=(5, 5), 
                                 effect_type="explosion", 
                                 num_particles=30, 
                                 duration=1000)
        )
        
        # 3. Chain a highlight tiles animation
        highlight = explosion.chain(
            renderer.play_animation(AnimationType.HIGHLIGHT_TILES, 
                                 tile_positions=[(4, 4), (4, 5), (5, 4), (5, 5), (6, 5)], 
                                 color=(255, 255, 0, 150), 
                                 duration=1500)
        )
        
        # 4. Chain a movement animation
        if "player1" in gsm.units:
            path = [(3, 4), (3, 5), (4, 5), (5, 5)]
            move = highlight.chain(
                renderer.play_animation(AnimationType.MOVE, 
                                    unit_id="player1", 
                                    path=path)
            )
            gsm.units["player1"].position = path[-1]
            
            # 5. Chain an attack animation
            if "enemy1" in gsm.units:
                attack = move.chain(
                    renderer.play_animation(AnimationType.ATTACK, 
                                        attacker_pos=path[-1], 
                                        defender_pos=gsm.units["enemy1"].position, 
                                        duration=800)
                )
                
                # 6. Chain a damage animation
                damage = attack.chain(
                    renderer.play_animation(AnimationType.TAKE_DAMAGE, 
                                        unit_pos=gsm.units["enemy1"].position, 
                                        damage=5)
                )
                gsm.units["enemy1"].current_hp -= 5
                
                # 7. Chain a smoke effect
                smoke = damage.chain(
                    renderer.play_animation(AnimationType.PARTICLE_EFFECT, 
                                        position=gsm.units["enemy1"].position, 
                                        effect_type="smoke", 
                                        num_particles=15, 
                                        duration=1500)
                )
                
                # 8. Chain a sparks effect
                sparks = smoke.chain(
                    renderer.play_animation(AnimationType.PARTICLE_EFFECT, 
                                        position=(7, 7), 
                                        effect_type="sparks", 
                                        num_particles=25, 
                                        duration=1200)
                )
                
                # 9. Finally, fade out
                fade_out = sparks.chain(
                    renderer.play_animation(AnimationType.FADE, 
                                        fade_in=False, 
                                        color=(0, 0, 0), 
                                        duration=1500)
                )
    
    # Run the demo
    setup_animation_demo()
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    print("Animation demonstration started! Press ESC to exit.")
    print("The animations will play in sequence automatically.")
    
    start_time = time.time()
    max_duration = 15  # Max 15 seconds for the demo
    
    while running and time.time() - start_time < max_duration:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update animations
        renderer.update()
        
        # Render
        renderer.render()
        
        # Cap frame rate
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    print("Animation demonstration completed.")

if __name__ == "__main__":
    main() 