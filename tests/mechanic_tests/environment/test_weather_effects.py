#!/usr/bin/env python3
"""
Weather Effects Visual Test

This script demonstrates the weather system and its effects on gameplay,
including rain, snow, fog, and sandstorm conditions.
"""

import os
import sys
import time
import random
import pygame

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, PROJECT_ROOT)

# Import game renderer and animation types
from src.ui.pygame_renderer import GameRenderer, AnimationType, ParticleSystemEffect
from src.utils.visual_logger import VisualScenarioLogger

class WeatherType:
    """Weather types for the demonstration."""
    CLEAR = "CLEAR"
    RAIN = "RAIN"
    SNOW = "SNOW"
    FOG = "FOG"
    SANDSTORM = "SANDSTORM"

class WeatherEffect:
    """Effects that weather applies to gameplay."""
    def __init__(self, weather_type):
        self.weather_type = weather_type
        
        # Set default effects
        self.movement_penalty = 0
        self.vision_penalty = 0
        self.accuracy_penalty = 0
        self.evasion_bonus = 0
        self.damage_modifier = 0
        
        # Set specific effects for each weather type
        if weather_type == WeatherType.RAIN:
            self.movement_penalty = 1     # Units move 1 less space
            self.accuracy_penalty = 10    # -10% hit rate
            self.description = "Rain reduces movement by 1, decreases accuracy by 10%"
        elif weather_type == WeatherType.SNOW:
            self.movement_penalty = 2     # Units move 2 less spaces
            self.accuracy_penalty = 5     # -5% hit rate
            self.description = "Snow reduces movement by 2, decreases accuracy by 5%"
        elif weather_type == WeatherType.FOG:
            self.vision_penalty = 3       # Units see 3 fewer tiles
            self.evasion_bonus = 15       # +15% evasion
            self.description = "Fog reduces vision by 3, increases evasion by 15%"
        elif weather_type == WeatherType.SANDSTORM:
            self.movement_penalty = 1     # Units move 1 less space
            self.vision_penalty = 2       # Units see 2 fewer tiles
            self.accuracy_penalty = 15    # -15% hit rate
            self.damage_modifier = -1     # 1 less damage
            self.description = "Sandstorm reduces movement by 1, vision by 2, accuracy by 15%, and damage by 1"
        else:  # CLEAR
            self.description = "Clear weather has no effect on gameplay"

class DummyGameStateManager:
    """Dummy game state manager for testing."""
    def __init__(self):
        self.current_turn = 1
        self.current_phase = "PLAYER"
        self.selected_unit = None
        self.units = {}
        self.current_weather = WeatherType.CLEAR
        self.weather_effect = WeatherEffect(WeatherType.CLEAR)
        
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
            DESERT = "DESERT"
            
            def __init__(self, name):
                self.name = name
                # Default movement cost
                self.movement_cost = 1
                if name == "FOREST":
                    self.movement_cost = 2
                elif name == "MOUNTAIN":
                    self.movement_cost = 3
                elif name == "RIVER":
                    self.movement_cost = 2
        
        # Fill the map with plains
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.terrain_grid[y][x] = TerrainType("PLAIN")
        
        # Add forest terrain
        for x, y in [(3, 3), (4, 3), (3, 4), (4, 4)]:
            self.terrain_grid[y][x] = TerrainType("FOREST")
                
        # Add mountain terrain
        for x, y in [(10, 3), (11, 3), (10, 4), (11, 4)]:
            self.terrain_grid[y][x] = TerrainType("MOUNTAIN")
        
        # Add river terrain
        for y in range(7, 10):
            for x in range(5, 8):
                self.terrain_grid[y][x] = TerrainType("RIVER")
        
        # Add desert terrain
        for x, y in [(12, 10), (13, 10), (12, 11), (13, 11), (12, 12), (13, 12)]:
            self.terrain_grid[y][x] = TerrainType("DESERT")
        
        # Create test units
        self.create_units()
    
    def create_units(self):
        """Create test units."""
        class DummyUnit:
            def __init__(self, id, name, faction, position, unit_type, movement):
                self.id = id
                self.name = name
                self.faction = type('Faction', (), {'name': faction})
                self.position = position
                self.unit_type = unit_type
                self.base_movement = movement
                self.disposition = type('Disposition', (), {'name': 'ACTIVE'})
                # Combat stats
                self.hit_rate = 85
                self.evasion = 20
                self.damage = 8
                self.defense = 5
                self.speed = 6
                # Current movement available (affected by weather)
                self.movement = movement
                # Vision range (affected by weather)
                self.vision_range = 5
            
            def apply_weather_effects(self, weather_effect):
                """Apply weather effects to this unit."""
                # Reset to base stats
                self.movement = max(1, self.base_movement - weather_effect.movement_penalty)
                self.vision_range = max(1, 5 - weather_effect.vision_penalty)
                self.hit_rate = max(0, 85 - weather_effect.accuracy_penalty)
                self.evasion = min(95, 20 + weather_effect.evasion_bonus)
                
                # Special unit type effects
                if self.unit_type == "FLIER" and weather_effect.weather_type in [WeatherType.RAIN, WeatherType.SNOW]:
                    # Fliers are more affected by rain and snow
                    self.movement = max(1, self.movement - 1)
                    self.hit_rate = max(0, self.hit_rate - 5)
                
                if self.unit_type == "ARMORED" and weather_effect.weather_type == WeatherType.SNOW:
                    # Armored units struggle more in snow
                    self.movement = max(1, self.movement - 1)
                
                if self.unit_type == "CAVALRY" and weather_effect.weather_type in [WeatherType.RAIN, WeatherType.SNOW]:
                    # Cavalry are greatly affected by rain and snow
                    self.movement = max(1, self.movement - 1)
                
                if self.unit_type == "MAGE" and weather_effect.weather_type == WeatherType.RAIN:
                    # Mages' magic is less effective in rain
                    self.hit_rate = max(0, self.hit_rate - 10)
        
        # Create player units with different types
        self.units["player_infantry"] = DummyUnit("player_infantry", "Infantry", "PLAYER", (2, 2), "INFANTRY", 5)
        self.units["player_cavalry"] = DummyUnit("player_cavalry", "Cavalry", "PLAYER", (4, 2), "CAVALRY", 7)
        self.units["player_flier"] = DummyUnit("player_flier", "Pegasus Knight", "PLAYER", (6, 2), "FLIER", 8)
        self.units["player_armored"] = DummyUnit("player_armored", "Knight", "PLAYER", (8, 2), "ARMORED", 4)
        self.units["player_mage"] = DummyUnit("player_mage", "Mage", "PLAYER", (10, 2), "MAGE", 5)
        
        # Create enemy units
        self.units["enemy_infantry"] = DummyUnit("enemy_infantry", "Enemy Infantry", "ENEMY", (2, 12), "INFANTRY", 5)
        self.units["enemy_cavalry"] = DummyUnit("enemy_cavalry", "Enemy Cavalry", "ENEMY", (5, 12), "CAVALRY", 7)
        self.units["enemy_flier"] = DummyUnit("enemy_flier", "Wyvern Rider", "ENEMY", (8, 12), "FLIER", 8)
        self.units["enemy_armored"] = DummyUnit("enemy_armored", "General", "ENEMY", (11, 12), "ARMORED", 4)
    
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
    
    def get_units_at(self, position):
        """Get units at the specified position."""
        return [unit for unit in self.get_all_units() if unit.position == position]
    
    def set_weather(self, weather_type):
        """Set the current weather."""
        self.current_weather = weather_type
        self.weather_effect = WeatherEffect(weather_type)
        
        # Apply weather effects to all units
        for unit in self.get_all_units():
            unit.apply_weather_effects(self.weather_effect)
        
        return self.weather_effect

class WeatherDemo:
    """Class to demonstrate weather effects."""
    
    def __init__(self):
        """Initialize the demonstration."""
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.window_size = (1024, 768)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Weather Effects Demonstration")
        
        # Create game state manager
        self.gsm = DummyGameStateManager()
        
        # Create renderer
        self.renderer = GameRenderer(self.gsm, self.window_size)
        
        # Create CLI display for visual logger
        class DummyCLIDisplay:
            def render_map_to_text(self, map_state):
                return "Map display placeholder"
            
        self.cli_display = DummyCLIDisplay()
        
        # Create visual logger with CLI display
        self.logger = VisualScenarioLogger(self.gsm, self.cli_display, log_dir="logs/weather_demo", enabled=True)
        
        # Center camera on the map
        self.renderer.center_camera_on_position(7, 7)
        
        # Weather overlay
        self.current_weather_overlay = None
        
        # Demo timers and state
        self.timers = {}
        self.start_time = time.time()
        self.max_runtime = 90  # Force exit after 90 seconds
        self.exit_message_shown = False
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Setup fonts
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.info_font = pygame.font.SysFont('Arial', 14)
        
        # Unit being moved for demonstration
        self.moving_unit = None
        self.movement_path = []
        self.movement_index = 0
        self.movement_timer = 0
        self.movement_interval = 0.5  # seconds between movement steps
    
    def setup_demos(self):
        """Set up the demonstration timers."""
        # Show introduction text
        self.timers["intro"] = self.start_time + 1.0
        
        # Demo 1: Show clear weather
        self.timers["clear_weather"] = self.start_time + 4.0
        
        # Demo 2: Rain weather
        self.timers["rain_weather"] = self.start_time + 12.0
        
        # Demo 3: Show movement in rain
        self.timers["rain_movement"] = self.start_time + 15.0
        
        # Demo 4: Snow weather
        self.timers["snow_weather"] = self.start_time + 25.0
        
        # Demo 5: Show movement in snow
        self.timers["snow_movement"] = self.start_time + 28.0
        
        # Demo 6: Fog weather
        self.timers["fog_weather"] = self.start_time + 38.0
        
        # Demo 7: Show vision in fog
        self.timers["fog_vision"] = self.start_time + 41.0
        
        # Demo 8: Sandstorm weather
        self.timers["sandstorm_weather"] = self.start_time + 51.0
        
        # Demo 9: Show movement in sandstorm
        self.timers["sandstorm_movement"] = self.start_time + 54.0
        
        # Return to clear weather
        self.timers["return_to_clear"] = self.start_time + 64.0
        
        # End demo
        self.timers["end"] = self.start_time + 70.0
    
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
            self.logger.log_action("SYSTEM", "INTRO", "Weather Effects Demonstration")
            self.logger.log_action("SYSTEM", "INFO", "Demonstrating weather effects on gameplay mechanics")
            
            del self.timers["intro"]
        
        # Clear weather
        if "clear_weather" in self.timers and current_time >= self.timers["clear_weather"]:
            self.set_weather(WeatherType.CLEAR)
            del self.timers["clear_weather"]
        
        # Rain weather
        if "rain_weather" in self.timers and current_time >= self.timers["rain_weather"]:
            self.set_weather(WeatherType.RAIN)
            del self.timers["rain_weather"]
        
        # Show movement in rain
        if "rain_movement" in self.timers and current_time >= self.timers["rain_movement"]:
            self.demonstrate_movement("player_cavalry", [(4, 2), (4, 3), (4, 4), (4, 5), (4, 6)])
            del self.timers["rain_movement"]
        
        # Snow weather
        if "snow_weather" in self.timers and current_time >= self.timers["snow_weather"]:
            self.set_weather(WeatherType.SNOW)
            del self.timers["snow_weather"]
        
        # Show movement in snow
        if "snow_movement" in self.timers and current_time >= self.timers["snow_movement"]:
            self.demonstrate_movement("player_armored", [(8, 2), (8, 3), (8, 4)])
            del self.timers["snow_movement"]
        
        # Fog weather
        if "fog_weather" in self.timers and current_time >= self.timers["fog_weather"]:
            self.set_weather(WeatherType.FOG)
            del self.timers["fog_weather"]
        
        # Show vision in fog
        if "fog_vision" in self.timers and current_time >= self.timers["fog_vision"]:
            self.demonstrate_vision("player_mage")
            del self.timers["fog_vision"]
        
        # Sandstorm weather
        if "sandstorm_weather" in self.timers and current_time >= self.timers["sandstorm_weather"]:
            self.set_weather(WeatherType.SANDSTORM)
            del self.timers["sandstorm_weather"]
        
        # Show movement in sandstorm
        if "sandstorm_movement" in self.timers and current_time >= self.timers["sandstorm_movement"]:
            self.demonstrate_movement("player_flier", [(6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7)])
            del self.timers["sandstorm_movement"]
        
        # Return to clear weather
        if "return_to_clear" in self.timers and current_time >= self.timers["return_to_clear"]:
            self.set_weather(WeatherType.CLEAR)
            del self.timers["return_to_clear"]
        
        # End demo
        if "end" in self.timers and current_time >= self.timers["end"]:
            self.logger.log_action("SYSTEM", "END", "Weather Effects Demonstration Complete")
            self.logger.finalize_log()
            
            print(f"\nDemonstration complete. Log saved to: {self.logger.log_file}")
            print("Press ESC to exit.")
            
            self.exit_message_shown = True
            del self.timers["end"]
        
        # Update movement animation if active
        if self.moving_unit and self.movement_path:
            if current_time >= self.movement_timer:
                if self.movement_index < len(self.movement_path):
                    # Move to next position
                    unit = self.gsm.get_unit(self.moving_unit)
                    if unit:
                        new_position = self.movement_path[self.movement_index]
                        unit.position = new_position
                        
                        # Log movement
                        self.logger.log_action(unit.id, "MOVE", 
                                                   f"{unit.name} moved to {new_position}")
                        
                        # Update timer for next movement
                        self.movement_timer = current_time + self.movement_interval
                        self.movement_index += 1
                else:
                    # Movement complete
                    self.moving_unit = None
                    self.movement_path = []
                    self.movement_index = 0
        
        # Update renderer
        self.renderer.update()
    
    def set_weather(self, weather_type):
        """Set the current weather type and visualize it."""
        # Clear existing weather overlay
        if self.current_weather_overlay is not None:
            self.renderer.remove_particle_system(self.current_weather_overlay)
            self.current_weather_overlay = None
        
        # Set the new weather in the game state
        weather_effect = self.gsm.set_weather(weather_type)
        
        # Log the weather change
        self.logger.log_action("SYSTEM", "WEATHER_CHANGE", 
                                    f"Weather changed to {weather_type}")
        self.logger.log_action("SYSTEM", "WEATHER_EFFECT", 
                                    weather_effect.description)
        
        # Create visual effect for the weather
        if weather_type == WeatherType.RAIN:
            self.current_weather_overlay = self.renderer.create_particle_system('rain', 500, gravity=0.3)
        elif weather_type == WeatherType.SNOW:
            self.current_weather_overlay = self.renderer.create_particle_system('snow', 300, gravity=0.05)
        elif weather_type == WeatherType.FOG:
            # Create a fog overlay (using custom fog effect or smoke particles)
            self.current_weather_overlay = self.renderer.create_particle_system('smoke', 200, gravity=0.02)
        elif weather_type == WeatherType.SANDSTORM:
            # Create a sandstorm effect (using custom effect or mix of particles)
            self.current_weather_overlay = self.renderer.create_particle_system('smoke', 300, gravity=0.1)
        
        # Highlight the entire map to show the weather effect
        self.renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=[(x, y) for x in range(self.gsm.map_width) for y in range(self.gsm.map_height)],
            color=(255, 255, 255, 50),
            duration_ms=1500
        )
        
        # Display stats changes for all units
        for unit in self.gsm.get_all_units():
            if unit.faction.name == "PLAYER":
                self.logger.log_action(unit.id, "STATS_CHANGE", 
                                           f"{unit.name}: Movement={unit.movement}, Vision={unit.vision_range}, Hit={unit.hit_rate}%, Evasion={unit.evasion}%")
    
    def demonstrate_movement(self, unit_id, path):
        """Demonstrate unit movement with weather effects."""
        unit = self.gsm.get_unit(unit_id)
        if not unit:
            return
        
        # Set up movement animation
        self.moving_unit = unit_id
        self.movement_path = path
        self.movement_index = 0
        self.movement_timer = time.time()
        
        # Show movement range
        self.show_movement_range(unit)
        
        # Log movement demonstration
        self.logger.log_action(unit.id, "MOVEMENT_DEMO", 
                                    f"Demonstrating movement for {unit.name} in {self.gsm.current_weather} weather")
        self.logger.log_action(unit.id, "MOVEMENT_STATS", 
                                    f"Base movement: {unit.base_movement}, Weather adjusted: {unit.movement}")
    
    def show_movement_range(self, unit):
        """Show the movement range for a unit."""
        # For demonstration, show a simple diamond shape for movement range
        range_tiles = []
        for dx in range(-unit.movement, unit.movement + 1):
            for dy in range(-unit.movement, unit.movement + 1):
                if abs(dx) + abs(dy) <= unit.movement:
                    pos = (unit.position[0] + dx, unit.position[1] + dy)
                    # Check if position is on the map
                    if (0 <= pos[0] < self.gsm.map_width and
                        0 <= pos[1] < self.gsm.map_height):
                        range_tiles.append(pos)
        
        # Highlight movement range
        self.renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=range_tiles,
            color=(100, 100, 255, 150),
            duration_ms=3000
        )
    
    def demonstrate_vision(self, unit_id):
        """Demonstrate vision range with weather effects."""
        unit = self.gsm.get_unit(unit_id)
        if not unit:
            return
        
        # Show vision range
        range_tiles = []
        for dx in range(-unit.vision_range, unit.vision_range + 1):
            for dy in range(-unit.vision_range, unit.vision_range + 1):
                if abs(dx) + abs(dy) <= unit.vision_range:
                    pos = (unit.position[0] + dx, unit.position[1] + dy)
                    # Check if position is on the map
                    if (0 <= pos[0] < self.gsm.map_width and
                        0 <= pos[1] < self.gsm.map_height):
                        range_tiles.append(pos)
        
        # Log vision demonstration
        self.logger.log_action(unit.id, "VISION_DEMO", 
                                    f"Demonstrating vision for {unit.name} in {self.gsm.current_weather} weather")
        self.logger.log_action(unit.id, "VISION_STATS", 
                                    f"Base vision: 5, Weather adjusted: {unit.vision_range}")
        
        # Highlight vision range
        self.renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=range_tiles,
            color=(255, 255, 100, 150),
            duration_ms=5000
        )
    
    def render(self):
        """Render the demonstration."""
        # Let the renderer handle the base rendering
        self.renderer.render()
        
        # Add custom UI elements
        self.draw_ui()
        
        # Update the display
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw UI elements."""
        # Draw a semi-transparent background panel at the top of the screen
        panel_rect = pygame.Rect(10, 10, self.window_size[0] - 20, 100)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(panel_surface, panel_rect)
        
        # Draw title
        title_text = self.title_font.render("Weather Effects Demo", True, (255, 255, 255))
        self.screen.blit(title_text, (20, 20))
        
        # Draw current weather
        weather_text = self.font.render(f"Current Weather: {self.gsm.current_weather}", True, (255, 255, 255))
        self.screen.blit(weather_text, (20, 50))
        
        # Draw weather effects
        if self.gsm.weather_effect.description:
            # Split description into lines if it's too long
            words = self.gsm.weather_effect.description.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                text = ' '.join(current_line)
                if self.info_font.size(text)[0] > panel_rect.width - 40:
                    current_line.pop()  # Remove the last word
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for i, line in enumerate(lines):
                effect_text = self.info_font.render(line, True, (200, 200, 255))
                self.screen.blit(effect_text, (20, 70 + i * 20))
    
    def run(self):
        """Run the demonstration."""
        print("Weather Effects Demonstration")
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
    demo = WeatherDemo()
    demo.run()

if __name__ == "__main__":
    main() 