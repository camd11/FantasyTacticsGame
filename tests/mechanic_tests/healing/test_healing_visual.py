#!/usr/bin/env python3
"""
Healing and Reinforcements Visual Test

This script demonstrates the healing system and reinforcement mechanics,
including staff healing, terrain-based recovery, and spawning of new units.
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
from src.ui.pygame_renderer import GameRenderer, AnimationType
from src.utils.visual_logger import VisualScenarioLogger

class HealingType:
    """Healing types for the demonstration."""
    STAFF = "STAFF"
    TERRAIN = "TERRAIN"
    ITEM = "ITEM"

class ReinforcementType:
    """Reinforcement types for the demonstration."""
    NORMAL = "NORMAL"
    BOSS = "BOSS"
    AMBUSH = "AMBUSH"  # Spawn and can move immediately

class DummyGameStateManager:
    """Dummy game state manager for testing."""
    def __init__(self):
        self.current_turn = 1
        self.current_phase = "PLAYER"
        self.selected_unit = None
        self.units = {}
        self.reinforcement_points = []
        
        # Create a 15x15 map
        self.map_width = 15
        self.map_height = 15
        self.terrain_grid = [[None for _ in range(self.map_width)] for _ in range(self.map_height)]
        
        # Define terrain types with healing properties
        class TerrainType:
            PLAIN = "PLAIN"
            FOREST = "FOREST"
            MOUNTAIN = "MOUNTAIN"
            RIVER = "RIVER"
            FORT = "FORT"     # Heals 20% HP per turn
            CASTLE = "CASTLE" # Heals 30% HP per turn
            
            def __init__(self, name):
                self.name = name
                # Healing percentage for this terrain
                self.healing_percent = 0
                if name == "FORT":
                    self.healing_percent = 20
                elif name == "CASTLE":
                    self.healing_percent = 30
        
        # Fill the map with plains
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.terrain_grid[y][x] = TerrainType("PLAIN")
        
        # Add healing terrain
        for x, y in [(3, 5), (4, 5), (3, 6), (4, 6)]:
            self.terrain_grid[y][x] = TerrainType("FORT")
                
        for x, y in [(10, 7), (11, 7), (10, 8), (11, 8)]:
            self.terrain_grid[y][x] = TerrainType("CASTLE")
        
        # Add forest and mountain terrain
        for x, y in [(7, 2), (8, 2), (7, 3), (8, 3)]:
            self.terrain_grid[y][x] = TerrainType("FOREST")
            
        for x, y in [(12, 12), (13, 12), (12, 13), (13, 13)]:
            self.terrain_grid[y][x] = TerrainType("MOUNTAIN")
        
        # Define reinforcement spawn points
        self.reinforcement_points = [(1, 1), (13, 1), (1, 13), (13, 13)]
        
        # Create test units
        self.create_units()
    
    def create_units(self):
        """Create test units."""
        class DummyUnit:
            def __init__(self, id, name, faction, position, hp, max_hp):
                self.id = id
                self.name = name
                self.faction = type('Faction', (), {'name': faction})
                self.position = position
                self.current_hp = hp
                self.max_hp = max_hp
                self.disposition = type('Disposition', (), {'name': 'ACTIVE'})
                # Combat stats
                self.hit_rate = 85
                self.damage = 8
                self.defense = 5
                self.speed = 6
                self.movement = 5
                # Healing ability
                self.can_heal = "healer" in id.lower()
                self.heal_power = 15 if self.can_heal else 0
                self.heal_range = 2 if self.can_heal else 0
            
            def heal(self, target, heal_amount):
                """Heal target unit."""
                if not self.can_heal:
                    return False
                
                old_hp = target.current_hp
                target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
                return target.current_hp > old_hp
        
        # Create player units
        self.units["player_knight"] = DummyUnit("player_knight", "Knight", "PLAYER", (3, 3), 10, 30)
        self.units["player_mage"] = DummyUnit("player_mage", "Mage", "PLAYER", (5, 3), 5, 20)
        self.units["player_archer"] = DummyUnit("player_archer", "Archer", "PLAYER", (7, 4), 12, 25)
        self.units["player_healer"] = DummyUnit("player_healer", "Healer", "PLAYER", (9, 3), 18, 18)
        self.units["player_cavalier"] = DummyUnit("player_cavalier", "Cavalier", "PLAYER", (11, 4), 15, 28)
        
        # Create enemy units
        self.units["enemy_knight"] = DummyUnit("enemy_knight", "Enemy Knight", "ENEMY", (3, 10), 15, 30)
        self.units["enemy_mage"] = DummyUnit("enemy_mage", "Enemy Mage", "ENEMY", (5, 10), 8, 20)
        self.units["enemy_archer"] = DummyUnit("enemy_archer", "Enemy Archer", "ENEMY", (7, 10), 13, 25)
        self.units["enemy_healer"] = DummyUnit("enemy_healer", "Enemy Healer", "ENEMY", (9, 10), 8, 18)
        self.units["enemy_cavalier"] = DummyUnit("enemy_cavalier", "Enemy Cavalier", "ENEMY", (11, 10), 20, 28)
    
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
    
    def apply_terrain_healing(self):
        """Apply terrain-based healing to all units."""
        healed_units = []
        
        for unit in self.get_all_units():
            terrain = self.get_terrain_at(unit.position)
            if not terrain or terrain.healing_percent <= 0:
                continue
            
            # Calculate healing amount based on terrain
            heal_amount = int((unit.max_hp * terrain.healing_percent) / 100)
            if heal_amount <= 0:
                continue
                
            old_hp = unit.current_hp
            unit.current_hp = min(unit.max_hp, unit.current_hp + heal_amount)
            
            if unit.current_hp > old_hp:
                healed_units.append((unit, heal_amount))
                
        return healed_units
    
    def spawn_reinforcement(self, position, reinforcement_type=ReinforcementType.NORMAL):
        """Spawn a reinforcement unit at the specified position."""
        # Check if position is valid and no unit exists there
        if (position[0] < 0 or position[0] >= self.map_width or
            position[1] < 0 or position[1] >= self.map_height or
            self.get_units_at(position)):
            return None
        
        # Create a reinforcement unit
        unit_id = f"enemy_reinforcement_{int(time.time())}"
        unit_name = "Boss Reinforcement" if reinforcement_type == ReinforcementType.BOSS else "Reinforcement"
        max_hp = 40 if reinforcement_type == ReinforcementType.BOSS else 25
        
        unit = type('DummyUnit', (), {
            'id': unit_id,
            'name': unit_name,
            'faction': type('Faction', (), {'name': 'ENEMY'}),
            'position': position,
            'current_hp': max_hp,
            'max_hp': max_hp,
            'disposition': type('Disposition', (), {'name': 'ACTIVE'}),
            'hit_rate': 85,
            'damage': 12 if reinforcement_type == ReinforcementType.BOSS else 8,
            'defense': 8 if reinforcement_type == ReinforcementType.BOSS else 5,
            'speed': 5,
            'movement': 5,
            'can_heal': False,
            'heal_power': 0,
            'heal_range': 0,
            'heal': lambda self, target, heal_amount: False
        })
        
        # Add the unit to the game state
        self.units[unit_id] = unit
        
        return unit

class HealingAndReinforcementsDemo:
    """Class to demonstrate healing and reinforcements."""
    
    def __init__(self):
        """Initialize the demonstration."""
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.window_size = (1024, 768)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Healing and Reinforcements Demonstration")
        
        # Create game state manager
        self.gsm = DummyGameStateManager()
        
        # Create renderer
        self.renderer = GameRenderer(self.gsm, self.window_size)
        
        # Center camera on the map
        self.renderer.center_camera_on_position(7, 7)
        
        # Demo timers and state
        self.timers = {}
        self.start_time = time.time()
        self.max_runtime = 90  # Force exit after 90 seconds
        self.exit_message_shown = False
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Create a visual logger
        self.log_file = os.path.join(PROJECT_ROOT, "logs", "mechanic_tests", "healing", f"healing_{time.strftime('%Y%m%d_%H%M%S')}.txt")
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
        
        # Demo 1: Staff Healing
        self.timers["staff_healing"] = self.start_time + 5.0
        
        # Demo 2: Show healing terrain
        self.timers["show_healing_terrain"] = self.start_time + 15.0
        
        # Demo 3: Move unit to healing terrain
        self.timers["move_to_terrain"] = self.start_time + 20.0
        
        # Demo 4: Apply terrain healing
        self.timers["terrain_healing"] = self.start_time + 30.0
        
        # Demo 5: Spawn normal reinforcement
        self.timers["spawn_reinforcement"] = self.start_time + 40.0
        
        # Demo 6: Spawn boss reinforcement
        self.timers["spawn_boss"] = self.start_time + 50.0
        
        # Demo 7: Spawn ambush reinforcement
        self.timers["spawn_ambush"] = self.start_time + 60.0
        
        # End demo
        self.timers["end"] = self.start_time + 75.0
    
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
            self.visual_logger.log_action("SYSTEM", "INTRO", "Healing and Reinforcements Demonstration")
            self.visual_logger.log_action("SYSTEM", "INFO", "Demonstrating healing systems and reinforcement mechanics")
            
            del self.timers["intro"]
        
        # Demo 1: Staff Healing
        if "staff_healing" in self.timers and current_time >= self.timers["staff_healing"]:
            self.perform_staff_healing("player_healer", "player_mage")
            del self.timers["staff_healing"]
        
        # Demo 2: Show healing terrain
        if "show_healing_terrain" in self.timers and current_time >= self.timers["show_healing_terrain"]:
            self.highlight_healing_terrain()
            del self.timers["show_healing_terrain"]
        
        # Demo 3: Move unit to healing terrain
        if "move_to_terrain" in self.timers and current_time >= self.timers["move_to_terrain"]:
            self.move_unit_to_terrain("player_knight", (3, 5))  # Move to fort
            self.move_unit_to_terrain("player_mage", (10, 7))   # Move to castle
            del self.timers["move_to_terrain"]
        
        # Demo 4: Apply terrain healing
        if "terrain_healing" in self.timers and current_time >= self.timers["terrain_healing"]:
            self.apply_terrain_healing()
            del self.timers["terrain_healing"]
        
        # Demo 5: Spawn normal reinforcement
        if "spawn_reinforcement" in self.timers and current_time >= self.timers["spawn_reinforcement"]:
            self.spawn_reinforcement(self.gsm.reinforcement_points[0], ReinforcementType.NORMAL)
            del self.timers["spawn_reinforcement"]
        
        # Demo 6: Spawn boss reinforcement
        if "spawn_boss" in self.timers and current_time >= self.timers["spawn_boss"]:
            self.spawn_reinforcement(self.gsm.reinforcement_points[1], ReinforcementType.BOSS)
            del self.timers["spawn_boss"]
        
        # Demo 7: Spawn ambush reinforcement
        if "spawn_ambush" in self.timers and current_time >= self.timers["spawn_ambush"]:
            self.spawn_reinforcement(self.gsm.reinforcement_points[2], ReinforcementType.AMBUSH)
            del self.timers["spawn_ambush"]
        
        # End demo
        if "end" in self.timers and current_time >= self.timers["end"]:
            self.visual_logger.log_action("SYSTEM", "END", "Healing and Reinforcements Demonstration Complete")
            self.visual_logger.finalize_log()
            
            print(f"\nDemonstration complete. Log saved to: {self.log_file}")
            print("Press ESC to exit.")
            
            self.exit_message_shown = True
            del self.timers["end"]
        
        # Update renderer
        self.renderer.update()
    
    def perform_staff_healing(self, healer_id, target_id):
        """Perform staff healing."""
        healer = self.gsm.get_unit(healer_id)
        target = self.gsm.get_unit(target_id)
        
        if not healer or not target or not healer.can_heal:
            return
        
        # Log the healing action
        self.visual_logger.log_action(healer.id, "STAFF_HEAL", 
                                    f"{healer.name} heals {target.name} for {healer.heal_power} HP")
        
        # Show heal range
        heal_range_tiles = []
        for dx in range(-healer.heal_range, healer.heal_range + 1):
            for dy in range(-healer.heal_range, healer.heal_range + 1):
                if abs(dx) + abs(dy) <= healer.heal_range:
                    pos = (healer.position[0] + dx, healer.position[1] + dy)
                    heal_range_tiles.append(pos)
        
        self.renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=heal_range_tiles,
            color=(100, 200, 100, 150),
            duration_ms=2000
        )
        
        # Record old HP
        old_hp = target.current_hp
        
        # Perform the healing
        healer.heal(target, healer.heal_power)
        
        # Log the result
        self.visual_logger.log_action(target.id, "HEALED",
                                    f"{target.name} healed from {old_hp} to {target.current_hp} HP")
        
        # Show healing effect
        self.renderer.play_animation(
            AnimationType.HEALING,
            unit_pos=target.position,
            heal_amount=target.current_hp - old_hp,
            duration=1500
        )
    
    def highlight_healing_terrain(self):
        """Highlight terrain with healing properties."""
        # Find all healing terrain
        healing_tiles = []
        fort_tiles = []
        castle_tiles = []
        
        for y in range(self.gsm.map_height):
            for x in range(self.gsm.map_width):
                terrain = self.gsm.get_terrain_at((x, y))
                if terrain and terrain.healing_percent > 0:
                    healing_tiles.append((x, y))
                    if terrain.name == "FORT":
                        fort_tiles.append((x, y))
                    elif terrain.name == "CASTLE":
                        castle_tiles.append((x, y))
        
        # Log terrain types
        self.visual_logger.log_action("SYSTEM", "TERRAIN_INFO", 
                                   f"Fort: Heals 20% HP per turn, Castle: Heals 30% HP per turn")
        
        # Highlight fort tiles
        self.renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=fort_tiles,
            color=(100, 150, 255, 180),
            duration_ms=5000
        )
        
        # Highlight castle tiles
        self.renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=castle_tiles,
            color=(100, 255, 150, 180),
            duration_ms=5000
        )
    
    def move_unit_to_terrain(self, unit_id, destination):
        """Move a unit to healing terrain."""
        unit = self.gsm.get_unit(unit_id)
        if not unit:
            return
            
        # Log the movement
        self.visual_logger.log_action(unit.id, "MOVE",
                                    f"{unit.name} moving from {unit.position} to {destination}")
        
        # Calculate path (simplified)
        start_x, start_y = unit.position
        end_x, end_y = destination
        
        # Highlight path
        path = []
        if start_x != end_x or start_y != end_y:
            # Just a direct line for demo purposes
            dx = 1 if end_x > start_x else (-1 if end_x < start_x else 0)
            dy = 1 if end_y > start_y else (-1 if end_y < start_y else 0)
            
            x, y = start_x, start_y
            while x != end_x or y != end_y:
                if x != end_x:
                    x += dx
                elif y != end_y:
                    y += dy
                path.append((x, y))
        
        self.renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=path,
            color=(255, 255, 0, 150),
            duration_ms=2000
        )
        
        # Update unit position
        unit.position = destination
        
        # Log the new position
        terrain = self.gsm.get_terrain_at(destination)
        if terrain and terrain.healing_percent > 0:
            self.visual_logger.log_action(unit.id, "ENTER_HEALING_TERRAIN",
                                       f"{unit.name} entered {terrain.name} terrain which heals {terrain.healing_percent}% HP per turn")
    
    def apply_terrain_healing(self):
        """Apply terrain-based healing."""
        # Advance turn
        self.gsm.current_turn += 1
        self.visual_logger.log_action("SYSTEM", "TURN_ADVANCE", f"Advanced to turn {self.gsm.current_turn}")
        
        # Apply terrain healing
        healed_units = self.gsm.apply_terrain_healing()
        
        # Log and visualize healing
        for unit, heal_amount in healed_units:
            terrain = self.gsm.get_terrain_at(unit.position)
            self.visual_logger.log_action(unit.id, "TERRAIN_HEAL",
                                       f"{unit.name} healed for {heal_amount} HP from {terrain.name} terrain")
            
            # Show healing effect
            self.renderer.play_animation(
                AnimationType.HEALING,
                unit_pos=unit.position,
                heal_amount=heal_amount,
                duration=1500
            )
    
    def spawn_reinforcement(self, position, reinforcement_type):
        """Spawn a reinforcement unit."""
        type_name = reinforcement_type
        
        # Log the reinforcement
        self.visual_logger.log_action("SYSTEM", "REINFORCEMENT",
                                   f"Spawning {type_name} reinforcement at {position}")
        
        # Spawn the unit
        unit = self.gsm.spawn_reinforcement(position, reinforcement_type)
        
        if not unit:
            self.visual_logger.log_action("SYSTEM", "ERROR",
                                       f"Failed to spawn reinforcement at {position}")
            return
        
        # Highlight spawn location
        self.renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=[position],
            color=(255, 0, 0, 180),
            duration_ms=3000
        )
        
        # Show spawn effect
        self.renderer.play_animation(
            AnimationType.PARTICLE_EFFECT,
            effect_position=position,
            effect_type="explosion" if reinforcement_type == ReinforcementType.BOSS else "smoke",
            duration=2000
        )
        
        # For ambush reinforcements, immediately show movement
        if reinforcement_type == ReinforcementType.AMBUSH:
            # Wait a bit, then move the unit
            time.sleep(1)
            
            # Calculate a random position to move to
            move_range = 3
            valid_move_positions = []
            
            for dx in range(-move_range, move_range + 1):
                for dy in range(-move_range, move_range + 1):
                    if abs(dx) + abs(dy) <= move_range:
                        new_pos = (position[0] + dx, position[1] + dy)
                        # Check if position is on the map and no unit exists there
                        if (0 <= new_pos[0] < self.gsm.map_width and
                            0 <= new_pos[1] < self.gsm.map_height and
                            not self.gsm.get_units_at(new_pos)):
                            valid_move_positions.append(new_pos)
            
            if valid_move_positions:
                # Choose a random position
                new_position = random.choice(valid_move_positions)
                
                # Log ambush movement
                self.visual_logger.log_action(unit.id, "AMBUSH_MOVE",
                                           f"Ambush reinforcement moving to {new_position}")
                
                # Highlight movement path
                self.renderer.play_animation(
                    AnimationType.HIGHLIGHT_TILES,
                    tile_positions=[new_position],
                    color=(255, 165, 0, 180),
                    duration_ms=2000
                )
                
                # Update position
                unit.position = new_position
    
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
        panel_rect = pygame.Rect(10, 10, self.window_size[0] - 20, 80)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(panel_surface, panel_rect)
        
        # Draw title
        title_text = self.title_font.render("Healing and Reinforcements Demo", True, (255, 255, 255))
        self.screen.blit(title_text, (20, 20))
        
        # Draw current turn
        turn_text = self.font.render(f"Current Turn: {self.gsm.current_turn}", True, (255, 255, 255))
        self.screen.blit(turn_text, (20, 50))
        
        # Draw unit count
        unit_count = len(self.gsm.get_all_units())
        units_text = self.font.render(f"Units: {unit_count} ({len([u for u in self.gsm.get_all_units() if u.faction.name == 'PLAYER'])} Player, {len([u for u in self.gsm.get_all_units() if u.faction.name == 'ENEMY'])} Enemy)", True, (255, 255, 255))
        self.screen.blit(units_text, (20, 70))
    
    def run(self):
        """Run the demonstration."""
        print("Healing and Reinforcements Demonstration")
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
    demo = HealingAndReinforcementsDemo()
    demo.run()

if __name__ == "__main__":
    main() 