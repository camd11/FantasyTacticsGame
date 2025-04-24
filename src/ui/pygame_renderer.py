#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pygame-based renderer for the Fantasy Tactics Game.
This module provides a visual representation of the game state.
"""

import os
import sys
import time
import pygame
import math
from enum import Enum
from typing import List, Dict, Tuple, Set, Optional, Any, Callable

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)

# Define constants
TILE_SIZE = 64  # Pixel size of each tile
SPRITE_SIZE = 48  # Pixel size of unit sprites
FPS = 60  # Frames per second

# Sound configuration
SOUND_ENABLED = True
SOUND_VOLUME = 0.7  # 0.0 to 1.0

class AnimationType(Enum):
    """Types of animations that can be played."""
    MOVE = 1
    ATTACK = 2
    TAKE_DAMAGE = 3
    HEAL = 4
    APPLY_STATUS = 5
    REMOVE_STATUS = 6
    HIGHLIGHT_TILES = 7

class Animation:
    """Base class for animations."""
    def __init__(self, duration_ms=500, sound_effect=None):
        self.start_time = pygame.time.get_ticks()
        self.duration_ms = duration_ms
        self.completed = False
        self.sound_effect = sound_effect
        self.sound_played = False
    
    def update(self):
        """Update the animation state."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        # Play sound effect if not already played
        if SOUND_ENABLED and self.sound_effect and not self.sound_played:
            self.sound_effect.play()
            self.sound_played = True
        
        # Check if animation is complete
        if elapsed >= self.duration_ms:
            self.completed = True
        
        # Calculate progress from 0.0 to 1.0
        self.progress = min(1.0, elapsed / self.duration_ms)
        
        return self.completed
    
    def draw(self, surface):
        """Draw the animation on the surface."""
        pass

class MoveAnimation(Animation):
    """Animation for unit movement."""
    def __init__(self, unit_id, path, sprite, duration_ms=1000, sound_effect=None):
        super().__init__(duration_ms, sound_effect)
        self.unit_id = unit_id
        self.path = path
        self.sprite = sprite
        self.start_pos = path[0]
        self.end_pos = path[-1]
        
        # If path has intermediate steps, use them
        if len(path) > 2:
            self.waypoints = path
        else:
            self.waypoints = [self.start_pos, self.end_pos]
        
        self.current_segment = 0
        self.segment_progress = 0.0
    
    def update(self):
        """Update the movement animation."""
        completed = super().update()
        
        # Calculate which segment of the path we're on
        if len(self.waypoints) > 1:
            segment_length = 1.0 / (len(self.waypoints) - 1)
            self.current_segment = min(len(self.waypoints) - 2, int(self.progress / segment_length))
            self.segment_progress = (self.progress - (self.current_segment * segment_length)) / segment_length
        
        return completed
    
    def get_current_position(self):
        """Get the current interpolated position."""
        if self.completed:
            return self.end_pos
        
        if self.current_segment < len(self.waypoints) - 1:
            start = self.waypoints[self.current_segment]
            end = self.waypoints[self.current_segment + 1]
            
            # Interpolate between start and end
            x = start[0] + (end[0] - start[0]) * self.segment_progress
            y = start[1] + (end[1] - start[1]) * self.segment_progress
            
            return (x, y)
        
        return self.end_pos
    
    def draw(self, surface):
        """Draw the moving unit."""
        if self.completed:
            return
        
        # Get current position
        pos = self.get_current_position()
        
        # Convert grid position to pixel position
        pixel_x = pos[0] * TILE_SIZE + (TILE_SIZE - SPRITE_SIZE) // 2
        pixel_y = pos[1] * TILE_SIZE + (TILE_SIZE - SPRITE_SIZE) // 2
        
        # Draw the sprite
        surface.blit(self.sprite, (pixel_x, pixel_y))

class HighlightTilesAnimation(Animation):
    """Animation for highlighting tiles."""
    def __init__(self, tile_positions, color=(100, 200, 255, 150), duration_ms=5000, sound_effect=None):
        super().__init__(duration_ms, sound_effect)
        self.tile_positions = tile_positions
        self.base_color = color
        self.color = list(color)
    
    def update(self):
        """Update the highlight animation."""
        completed = super().update()
        
        # Pulse the alpha value
        pulse = abs(pygame.math.sin(self.progress * 6.28 * 2))  # 2 complete pulses
        self.color[3] = int(self.base_color[3] * (0.5 + 0.5 * pulse))
        
        return completed
    
    def draw(self, surface):
        """Draw the highlighted tiles."""
        if self.completed:
            return
        
        # Create a surface for the highlight
        highlight_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, self.color, (0, 0, TILE_SIZE, TILE_SIZE))
        
        # Draw highlight over each tile
        for pos in self.tile_positions:
            pixel_x = pos[0] * TILE_SIZE
            pixel_y = pos[1] * TILE_SIZE
            surface.blit(highlight_surface, (pixel_x, pixel_y))

class AttackAnimation(Animation):
    """Animation for an attack."""
    def __init__(self, attacker_pos, defender_pos, duration_ms=500, sound_effect=None):
        super().__init__(duration_ms, sound_effect)
        self.attacker_pos = attacker_pos
        self.defender_pos = defender_pos
        
        # Calculate direction vector
        self.direction = (
            defender_pos[0] - attacker_pos[0],
            defender_pos[1] - attacker_pos[1]
        )
        
        # Normalize if diagonal
        length = max(abs(self.direction[0]), abs(self.direction[1]))
        if length > 0:
            self.direction = (self.direction[0] / length, self.direction[1] / length)
    
    def draw(self, surface):
        """Draw the attack animation."""
        if self.completed:
            return
        
        # Calculate the attack line path
        attacker_pixel = (
            self.attacker_pos[0] * TILE_SIZE + TILE_SIZE // 2,
            self.attacker_pos[1] * TILE_SIZE + TILE_SIZE // 2
        )
        
        defender_pixel = (
            self.defender_pos[0] * TILE_SIZE + TILE_SIZE // 2,
            self.defender_pos[1] * TILE_SIZE + TILE_SIZE // 2
        )
        
        # Draw attack line
        if self.progress < 0.5:
            # Forward slash
            lerp = self.progress * 2  # 0 to 1 during first half
            end_x = attacker_pixel[0] + (defender_pixel[0] - attacker_pixel[0]) * lerp
            end_y = attacker_pixel[1] + (defender_pixel[1] - attacker_pixel[1]) * lerp
            
            pygame.draw.line(surface, (255, 0, 0), attacker_pixel, (end_x, end_y), 3)
        else:
            # Return slash
            lerp = 2 - self.progress * 2  # 1 to 0 during second half
            end_x = attacker_pixel[0] + (defender_pixel[0] - attacker_pixel[0]) * lerp
            end_y = attacker_pixel[1] + (defender_pixel[1] - attacker_pixel[1]) * lerp
            
            pygame.draw.line(surface, (255, 0, 0), attacker_pixel, (end_x, end_y), 3)

class DamageAnimation(Animation):
    """Animation for taking damage."""
    def __init__(self, unit_pos, damage, duration_ms=1000, sound_effect=None):
        super().__init__(duration_ms, sound_effect)
        self.unit_pos = unit_pos
        self.damage = damage
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.text = self.font.render(str(damage), True, (255, 0, 0))
    
    def draw(self, surface):
        """Draw the damage number rising up."""
        if self.completed:
            return
        
        # Calculate position
        center_x = self.unit_pos[0] * TILE_SIZE + TILE_SIZE // 2
        base_y = self.unit_pos[1] * TILE_SIZE
        
        # Move upward with progress
        offset_y = int(30 * self.progress)
        text_pos = (center_x - self.text.get_width() // 2, base_y - offset_y)
        
        # Fade out near the end
        alpha = 255
        if self.progress > 0.7:
            alpha = int(255 * (1 - (self.progress - 0.7) / 0.3))
        
        # Apply alpha
        text_surface = pygame.Surface(self.text.get_size(), pygame.SRCALPHA)
        text_surface.fill((255, 255, 255, 0))
        self.text.set_alpha(alpha)
        text_surface.blit(self.text, (0, 0))
        
        # Draw text
        surface.blit(text_surface, text_pos)

class StatusEffectAnimation(Animation):
    """Animation for applying or removing a status effect."""
    def __init__(self, unit_pos, status_icon, is_applying=True, duration_ms=1000, sound_effect=None):
        super().__init__(duration_ms, sound_effect)
        self.unit_pos = unit_pos
        self.status_icon = status_icon
        self.is_applying = is_applying
    
    def draw(self, surface):
        """Draw the status effect icon appearing or disappearing."""
        if self.completed:
            return
        
        # Calculate icon position
        center_x = self.unit_pos[0] * TILE_SIZE + TILE_SIZE // 2
        center_y = self.unit_pos[1] * TILE_SIZE + TILE_SIZE // 2
        
        # Scale based on progress
        if self.is_applying:
            scale = self.progress
        else:
            scale = 1 - self.progress
        
        # Avoid scaling to zero which would raise an error
        if scale < 0.1:
            return
        
        # Scale the icon
        icon_width = int(self.status_icon.get_width() * scale)
        icon_height = int(self.status_icon.get_height() * scale)
        if icon_width > 0 and icon_height > 0:
            scaled_icon = pygame.transform.scale(self.status_icon, (icon_width, icon_height))
            
            # Draw centered
            pos = (center_x - scaled_icon.get_width() // 2, 
                  center_y - scaled_icon.get_height() // 2)
            surface.blit(scaled_icon, pos)

class GameRenderer:
    """Main renderer class for the game."""
    def __init__(self, game_state_manager, window_size=(800, 600), title="Fantasy Tactics Game"):
        """Initialize the renderer."""
        self.game_state_manager = game_state_manager
        self.window_size = window_size
        self.title = title
        
        # Initialize pygame
        pygame.init()
        pygame.mixer.init() if SOUND_ENABLED else None
        pygame.display.set_caption(title)
        
        # Create the window
        self.screen = pygame.display.set_mode(window_size)
        self.clock = pygame.time.Clock()
        
        # Set up fonts
        self.font = pygame.font.SysFont('Arial', 14)
        self.ui_font = pygame.font.SysFont('Arial', 18, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Load assets
        self.assets = self.load_assets()
        
        # Load sounds
        self.sounds = self.load_sounds() if SOUND_ENABLED else {}
        
        # Active animations
        self.animations = []
        
        # Camera settings
        self.camera_offset = [0, 0]  # in tile coordinates
        self.target_camera_offset = [0, 0]  # for smooth camera movement
        self.camera_zoom = 1.0
        self.target_zoom = 1.0
        
        # UI settings
        self.show_debug_info = False
        self.show_grid_coords = False
        self.ui_panel_height = 100  # height of the bottom UI panel
        
        # Performance monitoring
        self.frame_times = []
        self.max_frame_times = 60  # store last 60 frames for avg FPS
        
        # Flag for running
        self.running = False
    
    def load_assets(self):
        """Load all game assets."""
        assets = {
            'tiles': {},
            'units': {},
            'effects': {},
            'ui': {}
        }
        
        # Load terrain tiles
        tiles_dir = os.path.join(PROJECT_ROOT, "assets", "tiles")
        for terrain_name in ["plain", "forest", "mountain", "river", "fort", "wall"]:
            file_path = os.path.join(tiles_dir, f"{terrain_name}.png")
            if os.path.exists(file_path):
                assets['tiles'][terrain_name] = pygame.image.load(file_path)
        
        # Load unit sprites
        units_dir = os.path.join(PROJECT_ROOT, "assets", "sprites", "units")
        for faction in ["player", "enemy", "npc"]:
            for unit_type in ["infantry", "cavalry", "flier", "armor", "archer", "mage", "healer"]:
                file_path = os.path.join(units_dir, f"{faction}_{unit_type}.png")
                if os.path.exists(file_path):
                    assets['units'][f"{faction}_{unit_type}"] = pygame.image.load(file_path)
        
        # Load status effect icons
        effects_dir = os.path.join(PROJECT_ROOT, "assets", "sprites", "effects")
        for effect_name in ["poison", "sleep", "silence", "berserk", "stat_boost"]:
            file_path = os.path.join(effects_dir, f"{effect_name}.png")
            if os.path.exists(file_path):
                assets['effects'][effect_name] = pygame.image.load(file_path)
        
        # Load UI elements
        ui_dir = os.path.join(PROJECT_ROOT, "assets", "ui")
        for ui_element in ["panel", "button", "cursor"]:
            file_path = os.path.join(ui_dir, f"{ui_element}.png")
            if os.path.exists(file_path):
                assets['ui'][ui_element] = pygame.image.load(file_path)
        
        return assets
    
    def load_sounds(self):
        """Load all sound effects."""
        sounds = {
            'move': None,
            'attack': None,
            'damage': None,
            'heal': None,
            'status': None,
            'menu': None,
            'select': None,
            'cancel': None
        }
        
        sounds_dir = os.path.join(PROJECT_ROOT, "assets", "sounds")
        
        # Try to load each sound
        for sound_name in sounds.keys():
            file_path = os.path.join(sounds_dir, f"{sound_name}.wav")
            if os.path.exists(file_path):
                sounds[sound_name] = pygame.mixer.Sound(file_path)
                sounds[sound_name].set_volume(SOUND_VOLUME)
        
        return sounds
    
    def get_terrain_image(self, terrain_type):
        """Get the image for a terrain type."""
        # Convert enum to string
        terrain_name = terrain_type.name.lower()
        return self.assets['tiles'].get(terrain_name, self.assets['tiles'].get('plain'))
    
    def get_unit_sprite(self, unit):
        """Get the sprite for a unit based on faction and type."""
        faction = unit.faction.name.lower()
        
        # Determine unit type based on movement_type if available
        if hasattr(unit, 'movement_type'):
            unit_type = unit.movement_type.name.lower()
        else:
            # Default to infantry if movement_type not available
            unit_type = "infantry"
        
        # Try to get the specific sprite
        sprite_key = f"{faction}_{unit_type}"
        if sprite_key in self.assets['units']:
            return self.assets['units'][sprite_key]
        
        # Fallback to a generic sprite
        return self.assets['units'].get(f"{faction}_infantry")
    
    def get_status_effect_icon(self, status_type):
        """Get the icon for a status effect."""
        # Convert enum to string
        status_name = status_type.name.lower()
        return self.assets['effects'].get(status_name)
    
    def smooth_camera_movement(self, delta_time):
        """Smoothly move camera toward target position."""
        # Camera position lerping
        lerp_factor = min(1.0, 5.0 * delta_time)  # Adjust speed here
        
        # Update camera offset with smooth lerping
        self.camera_offset[0] += (self.target_camera_offset[0] - self.camera_offset[0]) * lerp_factor
        self.camera_offset[1] += (self.target_camera_offset[1] - self.camera_offset[1]) * lerp_factor
        
        # Update zoom with smooth lerping
        self.camera_zoom += (self.target_zoom - self.camera_zoom) * lerp_factor
    
    def set_camera_offset(self, x, y):
        """Set the target camera offset in grid coordinates."""
        self.target_camera_offset = [x, y]
    
    def center_camera_on_position(self, grid_x, grid_y):
        """Center the camera on a grid position."""
        visible_tiles_x = (self.window_size[0] // TILE_SIZE) / self.camera_zoom
        visible_tiles_y = ((self.window_size[1] - self.ui_panel_height) // TILE_SIZE) / self.camera_zoom
        
        self.target_camera_offset[0] = grid_x - visible_tiles_x // 2
        self.target_camera_offset[1] = grid_y - visible_tiles_y // 2
    
    def set_zoom(self, zoom_level):
        """Set the target zoom level (1.0 is normal)."""
        self.target_zoom = max(0.5, min(2.0, zoom_level))  # Clamp between 0.5 and 2.0
    
    def adjust_zoom(self, amount):
        """Adjust the zoom by the given amount."""
        self.set_zoom(self.target_zoom + amount)
    
    def grid_to_screen(self, grid_x, grid_y):
        """Convert grid coordinates to screen coordinates with zoom."""
        effective_tile_size = TILE_SIZE * self.camera_zoom
        screen_x = (grid_x - self.camera_offset[0]) * effective_tile_size
        screen_y = (grid_y - self.camera_offset[1]) * effective_tile_size
        return screen_x, screen_y
    
    def screen_to_grid(self, screen_x, screen_y):
        """Convert screen coordinates to grid coordinates with zoom."""
        effective_tile_size = TILE_SIZE * self.camera_zoom
        grid_x = screen_x / effective_tile_size + self.camera_offset[0]
        grid_y = screen_y / effective_tile_size + self.camera_offset[1]
        return int(grid_x), int(grid_y)
    
    def draw_map(self):
        """Draw the terrain grid with zoom support."""
        # Get map dimensions
        map_width, map_height = self.game_state_manager.get_map_dimensions()
        
        # Calculate visible range based on zoom
        effective_tile_size = TILE_SIZE * self.camera_zoom
        visible_tiles_x = math.ceil(self.window_size[0] / effective_tile_size) + 1
        visible_tiles_y = math.ceil((self.window_size[1] - self.ui_panel_height) / effective_tile_size) + 1
        
        start_x = max(0, int(self.camera_offset[0]))
        start_y = max(0, int(self.camera_offset[1]))
        end_x = min(map_width, start_x + visible_tiles_x)
        end_y = min(map_height, start_y + visible_tiles_y)
        
        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                terrain = self.game_state_manager.get_terrain_at((x, y))
                terrain_image = self.get_terrain_image(terrain)
                
                screen_x, screen_y = self.grid_to_screen(x, y)
                
                # Scale the terrain image based on zoom
                if self.camera_zoom != 1.0:
                    scaled_size = (int(TILE_SIZE * self.camera_zoom), int(TILE_SIZE * self.camera_zoom))
                    scaled_image = pygame.transform.scale(terrain_image, scaled_size)
                    self.screen.blit(scaled_image, (screen_x, screen_y))
                else:
                    self.screen.blit(terrain_image, (screen_x, screen_y))
                
                # Draw grid coordinates for debugging
                if self.show_grid_coords:
                    text = self.font.render(f"{x},{y}", True, (0, 0, 0))
                    self.screen.blit(text, (screen_x + 5, screen_y + 5))
    
    def draw_units(self):
        """Draw all units on the map with zoom support."""
        # Skip units that are being animated
        animated_unit_ids = set()
        for anim in self.animations:
            if isinstance(anim, MoveAnimation):
                animated_unit_ids.add(anim.unit_id)
        
        # Draw each unit
        for unit in self.game_state_manager.get_all_units():
            # Skip if unit is being animated
            if unit.id in animated_unit_ids:
                continue
            
            # Skip if unit is not active
            if unit.disposition.name != "ACTIVE":
                continue
            
            # Get unit sprite
            sprite = self.get_unit_sprite(unit)
            
            # Calculate position
            grid_x, grid_y = unit.position
            screen_x, screen_y = self.grid_to_screen(grid_x, grid_y)
            
            # Scale the sprite based on zoom
            effective_sprite_size = int(SPRITE_SIZE * self.camera_zoom)
            
            # Adjust for sprite size
            screen_x += (TILE_SIZE * self.camera_zoom - effective_sprite_size) // 2
            screen_y += (TILE_SIZE * self.camera_zoom - effective_sprite_size) // 2
            
            # Scale and draw the unit
            if self.camera_zoom != 1.0:
                scaled_sprite = pygame.transform.scale(sprite, (effective_sprite_size, effective_sprite_size))
                self.screen.blit(scaled_sprite, (screen_x, screen_y))
            else:
                self.screen.blit(sprite, (screen_x, screen_y))
            
            # Draw HP bar
            hp_width = int((unit.current_hp / unit.max_hp) * (effective_sprite_size - 4))
            hp_height = max(2, int(4 * self.camera_zoom))
            hp_x = screen_x + 2
            hp_y = screen_y + effective_sprite_size - 6 * self.camera_zoom
            
            # Background
            pygame.draw.rect(self.screen, (0, 0, 0), (hp_x, hp_y, effective_sprite_size - 4, hp_height))
            # Foreground
            if hp_width > 0:
                hp_color = (0, 255, 0)  # Green
                if unit.current_hp < unit.max_hp * 0.5:
                    hp_color = (255, 255, 0)  # Yellow
                if unit.current_hp < unit.max_hp * 0.25:
                    hp_color = (255, 0, 0)  # Red
                pygame.draw.rect(self.screen, hp_color, (hp_x, hp_y, hp_width, hp_height))
            
            # Draw status effects
            if hasattr(unit, 'status_effects') and unit.status_effects:
                status_x = screen_x + effective_sprite_size - 16 * self.camera_zoom
                status_y = screen_y
                status_size = int(16 * self.camera_zoom)
                
                for effect in unit.status_effects:
                    status_icon = self.get_status_effect_icon(effect.type)
                    if status_icon:
                        # Scale icon based on zoom
                        status_icon = pygame.transform.scale(status_icon, (status_size, status_size))
                        self.screen.blit(status_icon, (status_x, status_y))
                        status_y += status_size  # Stack status icons vertically
    
    def draw_enhanced_ui(self):
        """Draw enhanced UI elements with panels and additional info."""
        screen_width, screen_height = self.window_size
        
        # Draw bottom panel background
        panel_rect = pygame.Rect(0, screen_height - self.ui_panel_height, 
                               screen_width, self.ui_panel_height)
        
        # Use panel image from assets if available, or draw a simple panel
        if 'panel' in self.assets['ui']:
            panel_image = pygame.transform.scale(self.assets['ui']['panel'], 
                                              (panel_rect.width, panel_rect.height))
            self.screen.blit(panel_image, panel_rect)
        else:
            pygame.draw.rect(self.screen, (40, 40, 40), panel_rect)
            pygame.draw.rect(self.screen, (80, 80, 80), panel_rect, 2)
        
        # Draw game info (turn counter, phase, etc.)
        padding = 15
        y_pos = screen_height - self.ui_panel_height + padding
        
        # Turn counter with enhanced styling
        if hasattr(self.game_state_manager, 'current_turn'):
            turn_label = self.ui_font.render("TURN:", True, (220, 220, 100))
            turn_value = self.title_font.render(f"{self.game_state_manager.current_turn}", True, (255, 255, 255))
            
            self.screen.blit(turn_label, (padding, y_pos))
            self.screen.blit(turn_value, (padding + turn_label.get_width() + 10, y_pos - 2))
            
            y_pos += turn_value.get_height() + 10
        
        # Current phase if available
        if hasattr(self.game_state_manager, 'current_phase'):
            phase_label = self.ui_font.render("PHASE:", True, (220, 220, 100))
            phase_value = self.title_font.render(f"{self.game_state_manager.current_phase}", True, (255, 255, 255))
            
            self.screen.blit(phase_label, (padding, y_pos))
            self.screen.blit(phase_value, (padding + phase_label.get_width() + 10, y_pos - 2))
            
            y_pos += phase_value.get_height() + 10
        
        # Show selected unit info on the right side
        if hasattr(self.game_state_manager, 'selected_unit') and self.game_state_manager.selected_unit:
            unit = self.game_state_manager.selected_unit
            
            # Unit sprite
            sprite = self.get_unit_sprite(unit)
            sprite_pos = (screen_width - padding - SPRITE_SIZE, 
                         screen_height - self.ui_panel_height + padding)
            self.screen.blit(sprite, sprite_pos)
            
            # Unit info text
            info_x = sprite_pos[0] - 180
            info_y = sprite_pos[1]
            
            unit_name = self.ui_font.render(unit.name, True, (255, 255, 255))
            unit_hp = self.ui_font.render(f"HP: {unit.current_hp}/{unit.max_hp}", True, (100, 255, 100))
            unit_pos = self.ui_font.render(f"Pos: {unit.position[0]},{unit.position[1]}", True, (100, 200, 255))
            
            self.screen.blit(unit_name, (info_x, info_y))
            self.screen.blit(unit_hp, (info_x, info_y + unit_name.get_height() + 5))
            self.screen.blit(unit_pos, (info_x, info_y + unit_name.get_height() + unit_hp.get_height() + 10))
        
        # Display controls hint in the center
        controls_text = self.ui_font.render("Controls: Arrows=Move Camera  Z/X=Zoom  D=Debug", True, (180, 180, 180))
        controls_pos = (screen_width // 2 - controls_text.get_width() // 2, 
                       screen_height - padding - controls_text.get_height())
        self.screen.blit(controls_text, controls_pos)
    
    def draw_debug_info(self):
        """Draw debug information."""
        if not self.show_debug_info:
            return
        
        # Calculate FPS
        if len(self.frame_times) > 0:
            fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
        else:
            fps = 0
        
        # Debug panel
        debug_surface = pygame.Surface((300, 100), pygame.SRCALPHA)
        debug_surface.fill((0, 0, 0, 180))
        
        # Debug text
        y_offset = 5
        debug_items = [
            f"FPS: {fps:.1f}",
            f"Zoom: {self.camera_zoom:.2f}",
            f"Camera: {self.camera_offset[0]:.1f}, {self.camera_offset[1]:.1f}",
            f"Animations: {len(self.animations)}",
            f"Visible Units: {len(self.game_state_manager.get_all_units())}"
        ]
        
        for item in debug_items:
            text = self.font.render(item, True, (255, 255, 255))
            debug_surface.blit(text, (10, y_offset))
            y_offset += text.get_height() + 5
        
        # Position in top-right corner
        self.screen.blit(debug_surface, (self.window_size[0] - 310, 10))
    
    def play_animation(self, animation_type, **kwargs):
        """Play an animation of the specified type."""
        animation = None
        sound_effect = None
        
        # Determine which sound effect to use
        if SOUND_ENABLED:
            if animation_type == AnimationType.MOVE:
                sound_effect = self.sounds.get('move')
            elif animation_type == AnimationType.ATTACK:
                sound_effect = self.sounds.get('attack')
            elif animation_type == AnimationType.TAKE_DAMAGE:
                sound_effect = self.sounds.get('damage')
            elif animation_type == AnimationType.HEAL:
                sound_effect = self.sounds.get('heal')
            elif animation_type in [AnimationType.APPLY_STATUS, AnimationType.REMOVE_STATUS]:
                sound_effect = self.sounds.get('status')
        
        if animation_type == AnimationType.MOVE:
            # Movement animation
            unit_id = kwargs.get('unit_id')
            path = kwargs.get('path', [])
            
            if unit_id and path:
                unit = self.game_state_manager.get_unit(unit_id)
                if unit:
                    sprite = self.get_unit_sprite(unit)
                    animation = MoveAnimation(unit_id, path, sprite, sound_effect=sound_effect)
        
        elif animation_type == AnimationType.HIGHLIGHT_TILES:
            # Highlight tiles animation
            tile_positions = kwargs.get('tile_positions', set())
            color = kwargs.get('color', (100, 200, 255, 150))
            duration = kwargs.get('duration', 3000)
            
            if tile_positions:
                animation = HighlightTilesAnimation(tile_positions, color, duration, sound_effect)
        
        elif animation_type == AnimationType.ATTACK:
            # Attack animation
            attacker_pos = kwargs.get('attacker_pos')
            defender_pos = kwargs.get('defender_pos')
            
            if attacker_pos and defender_pos:
                animation = AttackAnimation(attacker_pos, defender_pos, sound_effect=sound_effect)
        
        elif animation_type == AnimationType.TAKE_DAMAGE:
            # Damage animation
            unit_pos = kwargs.get('unit_pos')
            damage = kwargs.get('damage', 0)
            
            if unit_pos is not None and damage > 0:
                animation = DamageAnimation(unit_pos, damage, sound_effect=sound_effect)
        
        elif animation_type == AnimationType.APPLY_STATUS or animation_type == AnimationType.REMOVE_STATUS:
            # Status effect animation
            unit_pos = kwargs.get('unit_pos')
            status_type = kwargs.get('status_type')
            
            if unit_pos and status_type:
                status_icon = self.get_status_effect_icon(status_type)
                if status_icon:
                    is_applying = animation_type == AnimationType.APPLY_STATUS
                    animation = StatusEffectAnimation(unit_pos, status_icon, is_applying, sound_effect=sound_effect)
        
        # Add the animation to the list if valid
        if animation:
            self.animations.append(animation)
            return True
        
        return False
    
    def update(self, delta_time=None):
        """Update all active animations and camera movement."""
        # Update camera movement
        if delta_time:
            self.smooth_camera_movement(delta_time)
            
            # Update frame time list for FPS calculation
            self.frame_times.append(delta_time)
            if len(self.frame_times) > self.max_frame_times:
                self.frame_times.pop(0)
        
        # Update animations and remove completed ones
        self.animations = [anim for anim in self.animations if not anim.update()]
    
    def render(self):
        """Render the current game state."""
        # Clear the screen
        self.screen.fill((20, 20, 30))  # Darker background color
        
        # Draw the map
        self.draw_map()
        
        # Draw units
        self.draw_units()
        
        # Draw active animations
        for animation in self.animations:
            animation.draw(self.screen)
        
        # Draw enhanced UI
        self.draw_enhanced_ui()
        
        # Draw debug info if enabled
        self.draw_debug_info()
        
        # Update the display
        pygame.display.flip()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # Camera controls
                elif event.key == pygame.K_UP:
                    self.target_camera_offset[1] -= 1
                elif event.key == pygame.K_DOWN:
                    self.target_camera_offset[1] += 1
                elif event.key == pygame.K_LEFT:
                    self.target_camera_offset[0] -= 1
                elif event.key == pygame.K_RIGHT:
                    self.target_camera_offset[0] += 1
                
                # Zoom controls
                elif event.key == pygame.K_z:
                    self.adjust_zoom(-0.1)  # Zoom out
                elif event.key == pygame.K_x:
                    self.adjust_zoom(0.1)   # Zoom in
                
                # Toggle debug info
                elif event.key == pygame.K_d:
                    self.show_debug_info = not self.show_debug_info
                
                # Toggle grid coordinates
                elif event.key == pygame.K_g:
                    self.show_grid_coords = not self.show_grid_coords
            
            elif event.type == pygame.MOUSEWHEEL:
                # Mouse wheel for zoom
                self.adjust_zoom(event.y * 0.1)
            
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[2]:  # Right mouse button
                    # Pan camera with right mouse drag
                    dx, dy = event.rel
                    effective_tile_size = TILE_SIZE * self.camera_zoom
                    self.target_camera_offset[0] -= dx / effective_tile_size
                    self.target_camera_offset[1] -= dy / effective_tile_size
    
    def are_animations_active(self):
        """Check if there are active animations."""
        return len(self.animations) > 0
    
    def wait_for_animations(self, max_wait_ms=5000):
        """Wait for all animations to complete."""
        start_time = pygame.time.get_ticks()
        
        while self.are_animations_active():
            current_time = pygame.time.get_ticks()
            if current_time - start_time > max_wait_ms:
                print("Warning: Maximum animation wait time exceeded!")
                self.animations = []  # Clear animations
                break
            
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
    
    def run(self, callback=None):
        """Run the main loop."""
        self.running = True
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Handle events
            self.handle_events()
            
            # Run callback if provided
            if callback:
                callback(self, delta_time)
            
            # Update animations
            self.update(delta_time)
            
            # Render
            self.render()
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def close(self):
        """Close the renderer."""
        self.running = False
        pygame.quit()


def main():
    """Main function for testing the renderer."""
    # Initialize pygame
    pygame.init()
    pygame.mixer.init() if SOUND_ENABLED else None
    
    try:
        # Create a dummy game state manager
        class DummyGameStateManager:
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
                self.terrain_grid[7][1] = TerrainType("RIVER")
                self.terrain_grid[7][2] = TerrainType("RIVER")
                self.terrain_grid[7][3] = TerrainType("RIVER")
                self.terrain_grid[8][8] = TerrainType("FORT")
                self.terrain_grid[1][8] = TerrainType("WALL")
                self.terrain_grid[1][9] = TerrainType("WALL")
            
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
        
        # Add units to game state
        gsm.units["player1"] = DummyUnit("player1", "Hero", "PLAYER", (3, 4), "INFANTRY", 20, 20)
        gsm.units["enemy1"] = DummyUnit("enemy1", "Bandit", "ENEMY", (6, 5), "INFANTRY", 15, 20)
        gsm.units["npc1"] = DummyUnit("npc1", "Villager", "NPC", (8, 2), "INFANTRY", 10, 10)
        
        # Set selected unit for UI display
        gsm.selected_unit = gsm.units["player1"]
        
        # Create the renderer
        renderer = GameRenderer(gsm, window_size=(800, 600), title="Pygame Renderer Test")
        
        # Animation counter to track completion
        animation_played = False
        animation_completed = False
        test_timeout = 5000  # 5 seconds timeout
        start_time = pygame.time.get_ticks()
        
        # Define a test callback for animations
        def test_callback(renderer, delta_time):
            nonlocal animation_played, animation_completed, start_time
            
            # Add a simple animation if none have been played
            if not animation_played:
                print("Playing unit movement animation...")
                path = [(3, 4), (3, 5), (4, 5), (5, 5)]
                renderer.play_animation(AnimationType.MOVE, unit_id="player1", path=path)
                gsm.units["player1"].position = (5, 5)
                animation_played = True
            
            # Check if animations are done
            if animation_played and not renderer.are_animations_active() and not animation_completed:
                animation_completed = True
                print("Animation completed! Press any key to exit.")
            
            # Auto-exit after timeout if no activity
            current_time = pygame.time.get_ticks()
            if current_time - start_time > test_timeout:
                if not animation_completed:
                    print("Test timeout reached, exiting.")
                renderer.running = False
        
        # Override handle_events to exit on any key after animation completes
        original_handle_events = renderer.handle_events
        
        def new_handle_events():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    renderer.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        renderer.running = False
                    elif animation_completed:
                        # Any key exits after animation completes
                        renderer.running = False
                    # Camera controls
                    elif event.key == pygame.K_UP:
                        renderer.target_camera_offset[1] -= 1
                    elif event.key == pygame.K_DOWN:
                        renderer.target_camera_offset[1] += 1
                    elif event.key == pygame.K_LEFT:
                        renderer.target_camera_offset[0] -= 1
                    elif event.key == pygame.K_RIGHT:
                        renderer.target_camera_offset[0] += 1
                    # Zoom controls
                    elif event.key == pygame.K_z:
                        renderer.adjust_zoom(-0.1)
                    elif event.key == pygame.K_x:
                        renderer.adjust_zoom(0.1)
                    # Toggle debug
                    elif event.key == pygame.K_d:
                        renderer.show_debug_info = not renderer.show_debug_info
        
        renderer.handle_events = new_handle_events
        
        # Run the renderer
        print("Starting renderer test - ESC key or any key after animation to exit")
        print("Controls: Arrow Keys=Move, Z/X=Zoom, D=Toggle Debug Info")
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