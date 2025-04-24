#!/usr/bin/env python3
"""
Improved Visuals Demonstration

This script demonstrates the improved field of view visualization and movement
animations with units moving along cardinal directions only (no diagonal movement).
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
from src.ui.pygame_renderer import GameRenderer, AnimationType

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
        
        # Add some variety - create a complex terrain layout for pathing
        # Forests
        for x, y in [(3, 4), (4, 4), (3, 5), (4, 5), (8, 2), (9, 2), (10, 9), (10, 10)]:
            self.terrain_grid[y][x] = TerrainType("FOREST")
                
        # Mountains (impassable)
        for x, y in [(7, 6), (8, 6), (7, 7), (8, 7), (2, 10), (2, 11), (3, 10), (3, 11)]:
            self.terrain_grid[y][x] = TerrainType("MOUNTAIN")
        
        # Rivers
        for y in range(3, 8):
            self.terrain_grid[y][5] = TerrainType("RIVER")
        
        # Forts
        self.terrain_grid[2][2] = TerrainType("FORT")
        self.terrain_grid[12][12] = TerrainType("FORT")
        
        # Create test units
        self.create_units()
    
    def create_units(self):
        """Create test units."""
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
        
        # Player units
        self.units["scout"] = DummyUnit("scout", "Scout", "PLAYER", (2, 3), "INFANTRY", 20, 20)
        self.units["knight"] = DummyUnit("knight", "Knight", "PLAYER", (4, 2), "CAVALRY", 25, 25)
        self.units["archer"] = DummyUnit("archer", "Archer", "PLAYER", (3, 2), "INFANTRY", 15, 15)
        
        # Enemy units
        self.units["enemy1"] = DummyUnit("enemy1", "Enemy Scout", "ENEMY", (12, 10), "INFANTRY", 15, 15)
        self.units["enemy2"] = DummyUnit("enemy2", "Enemy Mage", "ENEMY", (10, 12), "INFANTRY", 10, 10)
    
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

class ImprovedVisualDemo:
    """Class to demonstrate improved field of view and animations."""
    
    def __init__(self):
        """Initialize the demonstration."""
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.window_size = (1024, 768)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Improved Visuals Demonstration")
        
        # Create game state manager
        self.gsm = DummyGameStateManager()
        
        # Create renderer
        self.renderer = GameRenderer(self.gsm, self.window_size)
        
        # Center camera on the map
        self.renderer.center_camera_on_position(7, 7)
        
        # Demo timers and state
        self.timers = {}
        self.start_time = time.time()
        self.max_runtime = 30  # Force exit after 30 seconds
        self.exit_message_shown = False
        self.running = True
        self.clock = pygame.time.Clock()
    
    def setup_demos(self):
        """Set up the demonstration timers."""
        # Highlight important terrain features
        self.timers["highlight_terrain"] = self.start_time + 1.0
        
        # Demo 1: Scout patrol with field of view
        self.timers["scout_patrol"] = self.start_time + 3.0
        
        # Demo 2: Knight and Archer coordinated movement
        self.timers["coordinated_movement"] = self.start_time + 15.0
    
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
        
        # Highlight terrain features
        if "highlight_terrain" in self.timers and current_time >= self.timers["highlight_terrain"]:
            print("\nHighlighting important terrain features:")
            
            # Collect positions by terrain type
            terrain_positions = {
                "FOREST": [],
                "MOUNTAIN": [],
                "RIVER": [],
                "FORT": []
            }
            
            for y in range(self.gsm.map_height):
                for x in range(self.gsm.map_width):
                    terrain = self.gsm.terrain_grid[y][x].name
                    if terrain in terrain_positions:
                        terrain_positions[terrain].append((x, y))
            
            # Highlight each terrain type with a different color
            colors = {
                "FOREST": (0, 150, 0, 100),    # Green
                "MOUNTAIN": (100, 100, 100, 100),  # Gray
                "RIVER": (0, 100, 255, 100),   # Blue
                "FORT": (200, 200, 0, 100)     # Yellow
            }
            
            for terrain_type, positions in terrain_positions.items():
                if positions:
                    print(f"  {terrain_type}: {len(positions)} tiles")
                    self.renderer.play_animation(
                        AnimationType.HIGHLIGHT_TILES,
                        tile_positions=positions,
                        color=colors[terrain_type],
                        duration_ms=8000
                    )
            
            del self.timers["highlight_terrain"]
        
        # Demo 1: Scout patrol with field of view
        if "scout_patrol" in self.timers and current_time >= self.timers["scout_patrol"]:
            print("\nDemo 1: Scout patrol with field of view")
            
            scout = self.gsm.get_unit("scout")
            
            # Define a patrol path using only cardinal directions
            patrol_path = [
                (2, 3),  # Start position
                (2, 6),  # Move south
                (4, 6),  # Move east
                (4, 9),  # Move south
                (6, 9),  # Move east
                (6, 4),  # Move north
                (2, 4),  # Move west
                (2, 3)   # Return to start
            ]
            
            # Set up patrol timers
            for i, position in enumerate(patrol_path):
                # Schedule this patrol point for future execution
                patrol_time = current_time + i * 1.5  # 1.5 seconds per point
                
                # Get the next position for field of view direction
                next_position = patrol_path[(i + 1) % len(patrol_path)]
                
                # Store in timers
                self.timers[f"scout_patrol_{i}"] = (patrol_time, position, next_position)
            
            del self.timers["scout_patrol"]
        
        # Demo 2: Knight and Archer coordinated movement
        if "coordinated_movement" in self.timers and current_time >= self.timers["coordinated_movement"]:
            print("\nDemo 2: Knight and Archer coordinated movement")
            
            knight = self.gsm.get_unit("knight")
            archer = self.gsm.get_unit("archer")
            
            # Define paths for knight and archer
            knight_path = [
                (4, 2),  # Start position
                (9, 2),  # Move east
                (9, 5),  # Move south
                (12, 5), # Move east
                (12, 8)  # Move south
            ]
            
            archer_path = [
                (3, 2),  # Start position
                (3, 4),  # Move south
                (6, 4),  # Move east
                (6, 8),  # Move south
                (9, 8),  # Move east
                (9, 11), # Move south
                (12, 11) # Move east
            ]
            
            # Setup movement timers for knight
            for i, position in enumerate(knight_path):
                # Knight moves first
                move_time = current_time + i * 1.2  # 1.2 seconds per knight move
                
                # Store in timers
                self.timers[f"knight_move_{i}"] = (move_time, "knight", position)
            
            # Setup movement timers for archer - delayed start
            for i, position in enumerate(archer_path):
                # Archer follows after slight delay
                move_time = current_time + 2.0 + i * 1.2  # 1.2 seconds per archer move
                
                # Store in timers
                self.timers[f"archer_move_{i}"] = (move_time, "archer", position)
            
            del self.timers["coordinated_movement"]
        
        # Handle scout patrol timers
        scout_patrol_keys = [k for k in self.timers.keys() if k.startswith("scout_patrol_")]
        for key in scout_patrol_keys:
            if current_time >= self.timers[key][0]:  # Check if it's time for this patrol point
                patrol_time, position, next_position = self.timers[key]
                
                # Get scout
                scout = self.gsm.get_unit("scout")
                
                # Only move if we're not at the destination already
                if scout.position != position:
                    # Create a path for movement animation
                    path = [scout.position, position]
                    
                    # Play movement animation
                    print(f"  Scout moves to {position}")
                    self.renderer.play_animation(AnimationType.MOVE, unit_id="scout", path=path)
                    
                    # Update position after animation starts
                    scout.position = position
                
                # Show field of view in the direction of the next position
                print(f"  Scout looks towards {next_position}")
                self.renderer.visualize_field_of_view_towards("scout", next_position, 2000, 80)
                
                # Remove this patrol timer
                del self.timers[key]
        
        # Handle knight and archer movement timers
        unit_move_keys = [k for k in self.timers.keys() if k.startswith("knight_move_") or k.startswith("archer_move_")]
        for key in unit_move_keys:
            if current_time >= self.timers[key][0]:  # Check if it's time for this move
                move_time, unit_id, position = self.timers[key]
                
                # Get unit
                unit = self.gsm.get_unit(unit_id)
                
                # Only move if we're not at the destination already
                if unit.position != position:
                    # Create a path for movement animation
                    path = [unit.position, position]
                    
                    # Play movement animation
                    print(f"  {unit.name} moves to {position}")
                    self.renderer.play_animation(AnimationType.MOVE, unit_id=unit_id, path=path)
                    
                    # Update position after animation starts
                    unit.position = position
                    
                    # For the knight, add field of view in the direction of movement
                    if unit_id == "knight" and random.random() < 0.7:  # 70% chance
                        # Calculate direction vector
                        dx = position[0] - unit.position[0]
                        dy = position[1] - unit.position[1]
                        
                        # Look ahead of movement direction
                        if abs(dx) > abs(dy):  # Moving horizontally
                            look_pos = (position[0] + (1 if dx > 0 else -1), position[1])
                        else:  # Moving vertically
                            look_pos = (position[0], position[1] + (1 if dy > 0 else -1))
                        
                        print(f"  Knight scans ahead towards {look_pos}")
                        self.renderer.visualize_field_of_view_towards(unit_id, look_pos, 800, 60)
                
                # Remove this move timer
                del self.timers[key]
        
        # Update renderer
        self.renderer.update()
        
        # Check if all demos are complete
        if not any(k != "exit_timer" and not k.startswith("_") for k in self.timers) and not self.renderer.are_animations_active():
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
        print("Improved Visuals Demonstration")
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
    demo = ImprovedVisualDemo()
    demo.run()

if __name__ == "__main__":
    main() 