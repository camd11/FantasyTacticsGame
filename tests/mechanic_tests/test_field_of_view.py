#!/usr/bin/env python3
"""
Field of View Demonstration

This script demonstrates the different ways to use the field of view visualization effect.
"""

import os
import sys
import time
import math
import pygame

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import game renderer
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
        
        # Add some variety
        for x in range(3, 5):
            for y in range(3, 5):
                self.terrain_grid[y][x] = TerrainType("FOREST")
                
        for x in range(10, 12):
            for y in range(10, 12):
                self.terrain_grid[y][x] = TerrainType("MOUNTAIN")
                
        self.terrain_grid[7][7] = TerrainType("FORT")
        
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
        self.units["player1"] = DummyUnit("player1", "Scout", "PLAYER", (3, 7), "INFANTRY", 20, 20)
        self.units["player2"] = DummyUnit("player2", "Archer", "PLAYER", (5, 5), "INFANTRY", 15, 15)
        self.units["player3"] = DummyUnit("player3", "Knight", "PLAYER", (7, 3), "CAVALRY", 25, 25)
        
        # Enemy units
        self.units["enemy1"] = DummyUnit("enemy1", "Bandit", "ENEMY", (10, 7), "INFANTRY", 15, 15)
        self.units["enemy2"] = DummyUnit("enemy2", "Mage", "ENEMY", (8, 10), "INFANTRY", 10, 10)
    
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

class FieldOfViewDemo:
    """Class to manage the field of view demonstration."""
    
    def __init__(self):
        """Initialize the demonstration."""
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.window_size = (1024, 768)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Field of View Demonstration")
        
        # Create game state manager
        self.gsm = DummyGameStateManager()
        
        # Create renderer
        self.renderer = GameRenderer(self.gsm, self.window_size)
        
        # Center camera on the map
        self.renderer.center_camera_on_position(7, 7)
        
        # Demo timers and state
        self.demo_timers = {}
        self.start_time = time.time()
        self.max_runtime = 20  # Force exit after 20 seconds
        self.exit_message_shown = False
        self.running = True
        self.clock = pygame.time.Clock()
    
    def setup_demos(self):
        """Set up the demonstration timers."""
        # Demo 1: Basic field of view in 4 directions
        self.demo_timers["demo1"] = self.start_time + 1
        
        # Demo 2: Field of view towards targets
        self.demo_timers["demo2"] = self.start_time + 5
        
        # Demo 3: Dynamic field of view tracking
        self.demo_timers["demo3"] = self.start_time + 9
    
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
        
        # Demo 1: Basic field of view in 4 directions
        if "demo1" in self.demo_timers and current_time >= self.demo_timers["demo1"]:
            print("\nDemo 1: Basic field of view in 4 directions")
            
            # Directions for the scouts (right, down, left, up)
            directions = [0, math.pi/2, math.pi, -math.pi/2]
            labels = ["Right", "Down", "Left", "Up"]
            
            for direction, label in zip(directions, labels):
                print(f"  Scout looking {label}")
                self.renderer.visualize_field_of_view("player1", direction, 2000, 80)
            
            del self.demo_timers["demo1"]
        
        # Demo 2: Field of view towards targets
        if "demo2" in self.demo_timers and current_time >= self.demo_timers["demo2"]:
            print("\nDemo 2: Field of view towards targets")
            
            # Archer looks at enemy units
            print("  Archer targeting enemies")
            for enemy_id in ["enemy1", "enemy2"]:
                enemy = self.gsm.get_unit(enemy_id)
                self.renderer.visualize_field_of_view_towards("player2", enemy.position, 2000, 80)
            
            del self.demo_timers["demo2"]
        
        # Demo 3: Dynamic field of view tracking
        if "demo3" in self.demo_timers and current_time >= self.demo_timers["demo3"]:
            print("\nDemo 3: Knight patrolling with field of view")
            
            # Knight patrols and looks around
            knight = self.gsm.get_unit("player3")
            
            # Non-diagonal movement path (only horizontal and vertical steps)
            # Starting at (7, 3) and moving around the map in a grid-like pattern
            patrol_points = [
                (7, 3),  # Start
                (9, 3),  # Move right
                (9, 5),  # Move down
                (11, 5), # Move right
                (11, 8), # Move down
                (8, 8),  # Move left
                (8, 10), # Move down
                (5, 10), # Move left
                (5, 7),  # Move up
                (3, 7),  # Move left
                (3, 5),  # Move up
                (7, 5),  # Move right
                (7, 3)   # Return to start
            ]
            
            # Set up patrol timers instead of blocking loop
            for i, point in enumerate(patrol_points):
                # Schedule this patrol point for future execution
                patrol_time = current_time + i * 1.2  # 1.2 seconds per point
                
                # Store the point and target information in the timer dictionary
                next_point = patrol_points[(i + 1) % len(patrol_points)]
                self.demo_timers[f"patrol{i}"] = (patrol_time, point, next_point)
            
            # Remove the demo3 timer since we've set up the patrol timers
            del self.demo_timers["demo3"]
        
        # Handle patrol point timers
        patrol_keys = [k for k in self.demo_timers.keys() if k.startswith("patrol")]
        for key in patrol_keys:
            if current_time >= self.demo_timers[key][0]:  # Check if it's time for this patrol point
                patrol_time, point, next_point = self.demo_timers[key]
                
                # Move the knight
                knight = self.gsm.get_unit("player3")
                
                # Only move if we're not at the destination already
                if knight.position != point:
                    # Create a path for movement animation
                    path = [knight.position, point]
                    
                    # Play movement animation
                    self.renderer.play_animation(AnimationType.MOVE, unit_id="player3", path=path)
                    
                    # Update position after animation starts
                    knight.position = point
                
                # Show field of view
                print(f"  Knight moves to {point} and looks towards {next_point}")
                self.renderer.visualize_field_of_view_towards("player3", next_point, 1000, 80)
                
                # Remove this patrol timer
                del self.demo_timers[key]
        
        # Update renderer
        self.renderer.update()
        
        # Check if all demos are complete
        if not any(key != "exit_timer" for key in self.demo_timers) and not self.renderer.are_animations_active():
            if not self.exit_message_shown:
                print("\nDemonstration complete. Press ESC to exit.")
                self.exit_message_shown = True
                self.demo_timers["exit_timer"] = current_time + 5
            elif "exit_timer" in self.demo_timers and current_time >= self.demo_timers["exit_timer"]:
                print("Automatically exiting...")
                self.running = False
    
    def render(self):
        """Render the demonstration."""
        self.renderer.render()
        pygame.display.flip()
    
    def run(self):
        """Run the demonstration."""
        print("Field of View Demonstration")
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
    demo = FieldOfViewDemo()
    demo.run()

if __name__ == "__main__":
    main() 