#!/usr/bin/env python3
"""
Test script for the GUI renderer using dummy data
This script creates a test environment for the GUI renderer without relying on game initialization
"""

import sys
import os
import time
import pygame

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.ui.pygame_renderer import GameRenderer, AnimationType

def main():
    """Test the renderer with dummy data."""
    # Initialize pygame
    pygame.init()
    
    try:
        # Create a dummy game state manager
        class DummyGameStateManager:
            def __init__(self):
                self.current_turn = 1
                self.current_phase = "PLAYER"
                self.selected_unit = None
                self.units = {}
                
                # Create a 15x15 map
                self.terrain_grid = [[None for _ in range(15)] for _ in range(15)]
                
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
                for y in range(15):
                    for x in range(15):
                        self.terrain_grid[y][x] = TerrainType("PLAIN")
                
                # Add some variety
                for x in range(2, 5):
                    for y in range(3, 6):
                        self.terrain_grid[y][x] = TerrainType("FOREST")
                        
                for x in range(10, 12):
                    for y in range(7, 10):
                        self.terrain_grid[y][x] = TerrainType("MOUNTAIN")
                
                for y in range(2, 12):
                    self.terrain_grid[y][7] = TerrainType("RIVER")
                
                self.terrain_grid[2][2] = TerrainType("FORT")
                self.terrain_grid[12][12] = TerrainType("FORT")
                
                for x in range(0, 3):
                    self.terrain_grid[0][x] = TerrainType("WALL")
                    self.terrain_grid[14][x] = TerrainType("WALL")
            
            def get_map_dimensions(self):
                return (15, 15)
            
            def get_terrain_at(self, position):
                x, y = position
                if 0 <= x < 15 and 0 <= y < 15:
                    return self.terrain_grid[y][x]
                return None
            
            def get_all_units(self):
                return list(self.units.values())
            
            def get_unit(self, unit_id):
                return self.units.get(unit_id)
        
        # Create test game state manager
        gsm = DummyGameStateManager()
        
        # Create sample units
        class DummyUnit:
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
        
        # Add various units to game state
        gsm.units["player1"] = DummyUnit("player1", "Hero", "PLAYER", (3, 4), "INFANTRY", 20, 20)
        gsm.units["player2"] = DummyUnit("player2", "Archer", "PLAYER", (4, 3), "INFANTRY", 15, 15)
        gsm.units["player3"] = DummyUnit("player3", "Cavalier", "PLAYER", (2, 5), "CAVALRY", 22, 25)
        
        gsm.units["enemy1"] = DummyUnit("enemy1", "Bandit", "ENEMY", (10, 10), "INFANTRY", 15, 20)
        gsm.units["enemy2"] = DummyUnit("enemy2", "Mage", "ENEMY", (11, 9), "INFANTRY", 10, 15)
        gsm.units["enemy3"] = DummyUnit("enemy3", "Archer", "ENEMY", (9, 11), "INFANTRY", 12, 15)
        
        gsm.units["npc1"] = DummyUnit("npc1", "Villager", "NPC", (8, 2), "INFANTRY", 10, 10)
        gsm.units["npc2"] = DummyUnit("npc2", "Merchant", "NPC", (8, 3), "INFANTRY", 8, 10)
        
        # Set selected unit for UI display
        gsm.selected_unit = gsm.units["player1"]
        
        # Create the renderer
        print("Starting enhanced renderer test with interactive controls")
        renderer = GameRenderer(gsm, window_size=(1024, 768), title="Fantasy Tactics - Renderer Test")
        
        # Show instructions
        print("\nControls:")
        print("- Arrow Keys: Move camera")
        print("- Z/X: Zoom in/out")
        print("- D: Toggle debug info")
        print("- M: Play movement animation")
        print("- A: Play attack animation")
        print("- H: Highlight random tiles")
        print("- ESC: Exit")
        
        # Animation variables
        last_animation_time = 0
        
        # Update function for interactions
        def test_callback(renderer, delta_time):
            nonlocal last_animation_time
            current_time = pygame.time.get_ticks()
            
            # Process keyboard input for animations
            keys = pygame.key.get_pressed()
            
            # Only allow new animations every second (to prevent spamming)
            if current_time - last_animation_time < 1000:
                return
                
            # M key for movement animation
            if keys[pygame.K_m]:
                print("Playing movement animation")
                # Move player1 unit towards the center
                player_unit = gsm.units["player1"]
                current_pos = player_unit.position
                path = [current_pos, 
                       (current_pos[0] + 1, current_pos[1]),
                       (current_pos[0] + 1, current_pos[1] + 1),
                       (current_pos[0] + 2, current_pos[1] + 1)]
                renderer.play_animation(AnimationType.MOVE, unit_id="player1", path=path)
                player_unit.position = path[-1]  # Update position after animation
                last_animation_time = current_time
            
            # A key for attack animation
            elif keys[pygame.K_a]:
                print("Playing attack animation")
                player_unit = gsm.units["player1"]
                enemy_unit = gsm.units["enemy1"]
                # Only play attack if units are within reasonable distance
                manhattan_dist = abs(player_unit.position[0] - enemy_unit.position[0]) + \
                                 abs(player_unit.position[1] - enemy_unit.position[1])
                if manhattan_dist <= 10:  # Allow "ranged" attacks for demo
                    renderer.play_animation(AnimationType.ATTACK, 
                                          attacker_pos=player_unit.position,
                                          defender_pos=enemy_unit.position)
                    
                    # Play damage animation right after
                    renderer.play_animation(AnimationType.TAKE_DAMAGE,
                                          unit_pos=enemy_unit.position,
                                          damage=5)
                    
                    # Update HP
                    enemy_unit.current_hp = max(0, enemy_unit.current_hp - 5)
                else:
                    print("Enemy too far away for attack")
                last_animation_time = current_time
            
            # H key for tile highlighting
            elif keys[pygame.K_h]:
                print("Highlighting random tiles")
                import random
                # Highlight a 3x3 area around a random position
                x = random.randint(1, 13)
                y = random.randint(1, 13)
                tiles = [(x+dx, y+dy) for dx in range(-1, 2) for dy in range(-1, 2)]
                renderer.play_animation(AnimationType.HIGHLIGHT_TILES,
                                      tile_positions=tiles,
                                      color=(255, 255, 0, 150),
                                      duration_ms=2000)
                last_animation_time = current_time
        
        # Run the renderer with callback
        renderer.run(test_callback)
        
    except Exception as e:
        print(f"Error during renderer test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("Renderer test completed.")

if __name__ == "__main__":
    main() 