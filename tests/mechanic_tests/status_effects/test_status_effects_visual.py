#!/usr/bin/env python3
"""
Status Effects Visual Test

This script demonstrates various status effects that can be applied to units,
showing their visual appearance and gameplay impacts.
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

class StatusEffectType(Enum):
    """Status effect types for the demonstration."""
    NONE = "NONE"
    POISON = "POISON"
    BURN = "BURN"
    FREEZE = "FREEZE"
    STUN = "STUN"
    SILENCE = "SILENCE"  # Cannot use special abilities
    WEAKEN = "WEAKEN"    # Reduced attack

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
        
        # Create test units
        self.create_units()
    
    def create_units(self):
        """Create test units."""
        class StatusEffect:
            def __init__(self, effect_type, duration, strength=1):
                self.effect_type = effect_type
                self.duration = duration
                self.strength = strength
                self.start_turn = 1
                
            def get_effect_name(self):
                return self.effect_type.value
                
            def get_duration(self):
                return self.duration
                
            def get_turns_remaining(self, current_turn):
                return max(0, self.duration - (current_turn - self.start_turn))
        
        class DummyUnit:
            def __init__(self, id, name, faction, position, hp, max_hp):
                self.id = id
                self.name = name
                self.faction = type('Faction', (), {'name': faction})
                self.position = position
                self.current_hp = hp
                self.max_hp = max_hp
                self.disposition = type('Disposition', (), {'name': 'ACTIVE'})
                self.status_effects = []
                # Combat stats
                self.hit_rate = 85
                self.damage = 8
                self.defense = 5
                self.speed = 6
                self.movement = 5
            
            def add_status_effect(self, effect_type, duration, strength=1):
                """Add a status effect to the unit."""
                # Remove existing effect of same type if any
                self.status_effects = [effect for effect in self.status_effects if effect.effect_type != effect_type]
                
                # Add new effect
                if effect_type != StatusEffectType.NONE:
                    self.status_effects.append(StatusEffect(effect_type, duration, strength))
            
            def get_status_effects(self):
                """Get unit's status effects."""
                return self.status_effects
            
            def has_status_effect(self, effect_type):
                """Check if unit has a specific status effect."""
                return any(effect.effect_type == effect_type for effect in self.status_effects)
        
        # Create player units (no status effects initially)
        self.units["player_knight"] = DummyUnit("player_knight", "Knight", "PLAYER", (3, 3), 30, 30)
        self.units["player_mage"] = DummyUnit("player_mage", "Mage", "PLAYER", (5, 3), 20, 20)
        self.units["player_archer"] = DummyUnit("player_archer", "Archer", "PLAYER", (7, 3), 25, 25)
        self.units["player_healer"] = DummyUnit("player_healer", "Healer", "PLAYER", (9, 3), 18, 18)
        self.units["player_cavalier"] = DummyUnit("player_cavalier", "Cavalier", "PLAYER", (11, 3), 28, 28)
        
        # Create enemy units (will receive status effects)
        self.units["enemy_knight"] = DummyUnit("enemy_knight", "Enemy Knight", "ENEMY", (3, 9), 30, 30)
        self.units["enemy_mage"] = DummyUnit("enemy_mage", "Enemy Mage", "ENEMY", (5, 9), 20, 20)
        self.units["enemy_archer"] = DummyUnit("enemy_archer", "Enemy Archer", "ENEMY", (7, 9), 25, 25)
        self.units["enemy_healer"] = DummyUnit("enemy_healer", "Enemy Healer", "ENEMY", (9, 9), 18, 18)
        self.units["enemy_cavalier"] = DummyUnit("enemy_cavalier", "Enemy Cavalier", "ENEMY", (11, 9), 28, 28)
    
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

    def apply_status_effects(self):
        """Apply status effect damage and impacts for all units."""
        for unit in self.get_all_units():
            for effect in unit.status_effects:
                if effect.effect_type == StatusEffectType.POISON:
                    # Poison does damage per turn
                    damage = effect.strength * 2
                    unit.current_hp = max(1, unit.current_hp - damage)  # Poison won't kill
                    print(f"{unit.name} took {damage} poison damage. HP: {unit.current_hp}/{unit.max_hp}")
                    
                elif effect.effect_type == StatusEffectType.BURN:
                    # Burn does damage per turn
                    damage = effect.strength * 3
                    unit.current_hp = max(0, unit.current_hp - damage)  # Burn can kill
                    print(f"{unit.name} took {damage} burn damage. HP: {unit.current_hp}/{unit.max_hp}")
                    
                elif effect.effect_type == StatusEffectType.FREEZE:
                    # Freeze reduces movement
                    unit.movement = max(0, unit.movement - 3)
                    print(f"{unit.name} is frozen. Movement reduced to {unit.movement}")
                    
                elif effect.effect_type == StatusEffectType.STUN:
                    # Stun prevents action
                    print(f"{unit.name} is stunned and cannot take action")
                    
                elif effect.effect_type == StatusEffectType.SILENCE:
                    # Silence prevents special abilities
                    print(f"{unit.name} is silenced and cannot use special abilities")
                    
                elif effect.effect_type == StatusEffectType.WEAKEN:
                    # Weaken reduces damage
                    unit.damage = max(1, unit.damage - 3)
                    print(f"{unit.name} is weakened. Damage reduced to {unit.damage}")

class StatusEffectsDemo:
    """Class to demonstrate status effects."""
    
    def __init__(self):
        """Initialize the demonstration."""
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.window_size = (1024, 768)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Status Effects Demonstration")
        
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
        self.log_file = os.path.join(PROJECT_ROOT, "logs", "mechanic_tests", "status_effects", f"status_effects_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self.visual_logger = VisualScenarioLogger(
            game_state_manager=self.gsm,
            enabled=True,
            fixed_log_path=self.log_file
        )
        
        # Setup fonts
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Status effect colors
        self.status_colors = {
            StatusEffectType.POISON: (128, 0, 128, 200),  # Purple
            StatusEffectType.BURN: (255, 69, 0, 200),     # Red-orange
            StatusEffectType.FREEZE: (0, 191, 255, 200),  # Deep sky blue
            StatusEffectType.STUN: (255, 215, 0, 200),    # Gold
            StatusEffectType.SILENCE: (105, 105, 105, 200), # Dark gray
            StatusEffectType.WEAKEN: (139, 69, 19, 200)   # Brown
        }
    
    def setup_demos(self):
        """Set up the demonstration timers."""
        # Show introduction text
        self.timers["intro"] = self.start_time + 1.0
        
        # Demo 1: Apply Poison
        self.timers["apply_poison"] = self.start_time + 5.0
        
        # Demo 2: Apply Burn
        self.timers["apply_burn"] = self.start_time + 15.0
        
        # Demo 3: Apply Freeze
        self.timers["apply_freeze"] = self.start_time + 25.0
        
        # Demo 4: Apply Stun
        self.timers["apply_stun"] = self.start_time + 35.0
        
        # Demo 5: Apply Silence
        self.timers["apply_silence"] = self.start_time + 45.0
        
        # Demo 6: Apply Weaken
        self.timers["apply_weaken"] = self.start_time + 55.0
        
        # Demo 7: Advance Turn (apply status effects)
        self.timers["advance_turn"] = self.start_time + 65.0
        
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
            self.visual_logger.log_action("SYSTEM", "INTRO", "Status Effects Demonstration")
            self.visual_logger.log_action("SYSTEM", "INFO", "Demonstrating various status effects and their impacts")
            
            del self.timers["intro"]
        
        # Demo 1: Apply Poison
        if "apply_poison" in self.timers and current_time >= self.timers["apply_poison"]:
            self.apply_status_effect("enemy_knight", StatusEffectType.POISON, 3)
            del self.timers["apply_poison"]
        
        # Demo 2: Apply Burn
        if "apply_burn" in self.timers and current_time >= self.timers["apply_burn"]:
            self.apply_status_effect("enemy_mage", StatusEffectType.BURN, 3)
            del self.timers["apply_burn"]
        
        # Demo 3: Apply Freeze
        if "apply_freeze" in self.timers and current_time >= self.timers["apply_freeze"]:
            self.apply_status_effect("enemy_archer", StatusEffectType.FREEZE, 2)
            del self.timers["apply_freeze"]
        
        # Demo 4: Apply Stun
        if "apply_stun" in self.timers and current_time >= self.timers["apply_stun"]:
            self.apply_status_effect("enemy_healer", StatusEffectType.STUN, 1)
            del self.timers["apply_stun"]
        
        # Demo 5: Apply Silence
        if "apply_silence" in self.timers and current_time >= self.timers["apply_silence"]:
            self.apply_status_effect("enemy_cavalier", StatusEffectType.SILENCE, 2)
            del self.timers["apply_silence"]
        
        # Demo 6: Apply Weaken
        if "apply_weaken" in self.timers and current_time >= self.timers["apply_weaken"]:
            self.apply_status_effect("player_knight", StatusEffectType.WEAKEN, 2)
            del self.timers["apply_weaken"]
        
        # Demo 7: Advance Turn (apply status effects)
        if "advance_turn" in self.timers and current_time >= self.timers["advance_turn"]:
            self.advance_turn()
            del self.timers["advance_turn"]
        
        # End demo
        if "end" in self.timers and current_time >= self.timers["end"]:
            self.visual_logger.log_action("SYSTEM", "END", "Status Effects Demonstration Complete")
            self.visual_logger.finalize_log()
            
            print(f"\nDemonstration complete. Log saved to: {self.log_file}")
            print("Press ESC to exit.")
            
            self.exit_message_shown = True
            del self.timers["end"]
        
        # Update renderer
        self.renderer.update()
    
    def apply_status_effect(self, unit_id, effect_type, duration):
        """Apply a status effect to a unit."""
        unit = self.gsm.get_unit(unit_id)
        if not unit:
            return
        
        # Log the status effect application
        self.visual_logger.log_action("SYSTEM", "STATUS_EFFECT_APPLY", 
                                   f"Applied {effect_type.value} to {unit.name} for {duration} turns")
        
        # Apply the status effect
        unit.add_status_effect(effect_type, duration)
        
        # Visualize the status effect
        effect_color = self.status_colors.get(effect_type, (255, 255, 255, 150))
        
        # Visual highlight of affected unit
        self.renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=[unit.position],
            color=effect_color,
            duration_ms=5000  # 5 seconds
        )
        
        # Particle effect based on status type
        effect_map = {
            StatusEffectType.POISON: "poison",
            StatusEffectType.BURN: "explosion",
            StatusEffectType.FREEZE: "snow",
            StatusEffectType.STUN: "sparks",
            StatusEffectType.SILENCE: "smoke",
            StatusEffectType.WEAKEN: "smoke"
        }
        
        # Play particle effect if available for this status
        effect_name = effect_map.get(effect_type)
        if effect_name:
            self.renderer.play_animation(
                AnimationType.PARTICLE_EFFECT,
                effect_position=unit.position,
                effect_type=effect_name,
                duration=2000
            )
    
    def advance_turn(self):
        """Advance to the next turn and apply status effects."""
        self.gsm.current_turn += 1
        
        self.visual_logger.log_action("SYSTEM", "TURN_ADVANCE", f"Advanced to turn {self.gsm.current_turn}")
        self.visual_logger.log_action("SYSTEM", "STATUS_EFFECT_PHASE", "Applying status effects")
        
        # Apply status effects to all units
        self.gsm.apply_status_effects()
        
        # Visual updates for each unit with status effects
        for unit in self.gsm.get_all_units():
            for effect in unit.status_effects:
                self.visual_logger.log_action(unit.id, "STATUS_EFFECT_ACTIVE", 
                                           f"{effect.effect_type.value} - {effect.get_turns_remaining(self.gsm.current_turn)} turns remaining")
                
                # Update visual for this status effect
                effect_color = self.status_colors.get(effect.effect_type, (255, 255, 255, 150))
                
                # Show the status is still active
                self.renderer.play_animation(
                    AnimationType.HIGHLIGHT_TILES,
                    tile_positions=[unit.position],
                    color=effect_color,
                    duration_ms=3000  # 3 seconds
                )
                
                # Show damage animation for damaging effects
                if effect.effect_type in [StatusEffectType.POISON, StatusEffectType.BURN]:
                    damage = 2 if effect.effect_type == StatusEffectType.POISON else 3
                    self.renderer.play_animation(
                        AnimationType.TAKE_DAMAGE,
                        unit_pos=unit.position,
                        damage=damage,
                        duration=1000
                    )
    
    def render(self):
        """Render the demonstration."""
        # Let the renderer handle the base rendering
        self.renderer.render()
        
        # Add custom UI elements for status effects
        self.draw_status_effects_ui()
        self.draw_active_status_effects()
        
        # Update the display
        pygame.display.flip()
    
    def draw_status_effects_ui(self):
        """Draw UI elements explaining status effects."""
        # Draw a semi-transparent background panel at the top of the screen
        panel_rect = pygame.Rect(10, 10, self.window_size[0] - 20, 100)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(panel_surface, panel_rect)
        
        # Draw title
        title_text = self.title_font.render("Status Effects System", True, (255, 255, 255))
        self.screen.blit(title_text, (20, 20))
        
        # Draw current turn
        turn_text = self.font.render(f"Current Turn: {self.gsm.current_turn}", True, (255, 255, 255))
        self.screen.blit(turn_text, (20, 50))
        
        # Draw status effect descriptions
        effects_info = [
            ("Poison", "Deals 2 damage per turn, won't kill"),
            ("Burn", "Deals 3 damage per turn, can kill"),
            ("Freeze", "Reduces movement by 3"),
            ("Stun", "Prevents action"),
            ("Silence", "Prevents special abilities"),
            ("Weaken", "Reduces damage by 3")
        ]
        
        # Position for effect descriptions
        y_offset = 70
        for effect, desc in effects_info:
            effect_color = self.status_colors.get(StatusEffectType[effect.upper()], (255, 255, 255))
            effect_text = self.font.render(effect + ":", True, effect_color[:3])  # Use RGB part only
            desc_text = self.font.render(desc, True, (200, 200, 200))
            
            self.screen.blit(effect_text, (20, y_offset))
            self.screen.blit(desc_text, (120, y_offset))
            
            y_offset += 20
    
    def draw_active_status_effects(self):
        """Draw indicators for active status effects on units."""
        # Draw status effect indicators above units
        for unit in self.gsm.get_all_units():
            if not unit.status_effects:
                continue
                
            # Calculate screen position for unit
            unit_screen_pos = self.renderer.get_screen_position_for_map_position(unit.position)
            
            if not unit_screen_pos:
                continue
                
            # Draw each active status effect as a colored circle
            x, y = unit_screen_pos
            for i, effect in enumerate(unit.status_effects):
                color = self.status_colors.get(effect.effect_type, (255, 255, 255))
                # Draw circle above unit
                pygame.draw.circle(self.screen, color[:3], (x + 16 + i*20, y - 10), 8)
                
                # Draw turns remaining
                turns_text = self.font.render(str(effect.get_turns_remaining(self.gsm.current_turn)), True, (0, 0, 0))
                text_rect = turns_text.get_rect(center=(x + 16 + i*20, y - 10))
                self.screen.blit(turns_text, text_rect)
    
    def run(self):
        """Run the demonstration."""
        print("Status Effects Demonstration")
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
    demo = StatusEffectsDemo()
    demo.run()

if __name__ == "__main__":
    main() 