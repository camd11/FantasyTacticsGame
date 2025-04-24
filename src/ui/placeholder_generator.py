#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate placeholder graphics for the game.
This creates simple colored squares for different terrain types and unit types.
"""

import os
import pygame
import sys

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)

# Initialize pygame
pygame.init()

def generate_terrain_tiles():
    """Generate placeholder tiles for different terrain types."""
    tile_size = 64
    
    # Define terrain colors (RGB)
    terrain_colors = {
        "plain": (180, 230, 130),      # Light green
        "forest": (34, 139, 34),       # Forest green
        "mountain": (139, 137, 137),   # Gray
        "river": (65, 105, 225),       # Blue
        "fort": (205, 133, 63),        # Brown
        "wall": (105, 105, 105)        # Dark gray
    }
    
    # Create the tiles directory if it doesn't exist
    tiles_dir = os.path.join(PROJECT_ROOT, "assets", "tiles")
    os.makedirs(tiles_dir, exist_ok=True)
    
    # Generate tiles
    for terrain_name, color in terrain_colors.items():
        # Create a surface
        tile = pygame.Surface((tile_size, tile_size))
        tile.fill(color)
        
        # Add a grid outline
        pygame.draw.rect(tile, (0, 0, 0), (0, 0, tile_size, tile_size), 1)
        
        # Add some simple texture/pattern based on terrain type
        if terrain_name == "forest":
            # Draw some tree-like shapes
            pygame.draw.polygon(tile, (0, 100, 0), [(32, 10), (45, 40), (20, 40)])
            pygame.draw.rect(tile, (139, 69, 19), (28, 40, 8, 15))
        elif terrain_name == "mountain":
            # Draw mountain peak
            pygame.draw.polygon(tile, (169, 169, 169), [(20, 50), (32, 15), (44, 50)])
        elif terrain_name == "river":
            # Draw wavy pattern
            for i in range(0, tile_size, 8):
                pygame.draw.line(tile, (30, 144, 255), (0, i+2), (tile_size, i-2), 2)
        elif terrain_name == "fort":
            # Draw fort walls
            pygame.draw.rect(tile, (160, 82, 45), (10, 10, tile_size-20, tile_size-20), 3)
            pygame.draw.rect(tile, (160, 82, 45), (20, 20, tile_size-40, tile_size-40), 2)
        elif terrain_name == "wall":
            # Draw brick pattern
            for y in range(0, tile_size, 10):
                offset = 0 if y % 20 == 0 else 10
                for x in range(offset, tile_size, 20):
                    pygame.draw.rect(tile, (80, 80, 80), (x, y, 10, 10))
        
        # Save the tile
        pygame.image.save(tile, os.path.join(tiles_dir, f"{terrain_name}.png"))
        print(f"Generated {terrain_name} tile")

def generate_unit_sprites():
    """Generate placeholder sprites for different unit types."""
    sprite_size = 48
    
    # Define unit colors by faction (RGB)
    unit_colors = {
        "player": (0, 0, 255),      # Blue
        "enemy": (255, 0, 0),       # Red
        "npc": (255, 255, 0)        # Yellow
    }
    
    # Define unit types and their shapes
    unit_types = ["infantry", "cavalry", "flier", "armor", "archer", "mage", "healer"]
    
    # Create the sprites directory if it doesn't exist
    sprites_dir = os.path.join(PROJECT_ROOT, "assets", "sprites", "units")
    os.makedirs(sprites_dir, exist_ok=True)
    
    # Generate unit sprites
    for faction, color in unit_colors.items():
        for unit_type in unit_types:
            # Create a surface with alpha channel
            sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            
            # Base shape is a circle for all units
            pygame.draw.circle(sprite, color, (sprite_size//2, sprite_size//2), sprite_size//2-4)
            pygame.draw.circle(sprite, (0, 0, 0), (sprite_size//2, sprite_size//2), sprite_size//2-4, 2)
            
            # Add distinguishing features based on unit type
            if unit_type == "infantry":
                # Simple sword
                pygame.draw.line(sprite, (200, 200, 200), (30, 15), (15, 30), 3)
            elif unit_type == "cavalry":
                # Horse-like shape
                pygame.draw.ellipse(sprite, (150, 75, 0), (10, 25, 30, 15))
            elif unit_type == "flier":
                # Wings
                pygame.draw.line(sprite, (255, 255, 255), (24, 20), (5, 15), 3)
                pygame.draw.line(sprite, (255, 255, 255), (24, 20), (5, 25), 3)
                pygame.draw.line(sprite, (255, 255, 255), (24, 20), (43, 15), 3)
                pygame.draw.line(sprite, (255, 255, 255), (24, 20), (43, 25), 3)
            elif unit_type == "armor":
                # Shield
                pygame.draw.rect(sprite, (100, 100, 100), (15, 15, 18, 25))
            elif unit_type == "archer":
                # Bow
                pygame.draw.arc(sprite, (150, 75, 0), (10, 10, 20, 30), 1.5, 4.7, 2)
            elif unit_type == "mage":
                # Hat
                pygame.draw.polygon(sprite, (75, 0, 130), [(15, 15), (24, 5), (33, 15)])
            elif unit_type == "healer":
                # Cross
                pygame.draw.rect(sprite, (255, 255, 255), (20, 15, 8, 20))
                pygame.draw.rect(sprite, (255, 255, 255), (14, 21, 20, 8))
            
            # Save the sprite
            pygame.image.save(sprite, os.path.join(sprites_dir, f"{faction}_{unit_type}.png"))
            print(f"Generated {faction} {unit_type} sprite")

def generate_status_effect_icons():
    """Generate placeholder icons for status effects."""
    icon_size = 32
    
    # Define status effects and their colors
    status_effects = {
        "poison": (128, 0, 128),    # Purple
        "sleep": (100, 149, 237),   # Cornflower blue
        "silence": (169, 169, 169), # Gray
        "berserk": (255, 0, 0),     # Red
        "stat_boost": (50, 205, 50) # Lime green
    }
    
    # Create the effects directory if it doesn't exist
    effects_dir = os.path.join(PROJECT_ROOT, "assets", "sprites", "effects")
    os.makedirs(effects_dir, exist_ok=True)
    
    # Generate status effect icons
    for effect_name, color in status_effects.items():
        # Create a surface with alpha channel
        icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        
        # Draw the base icon - a rounded rectangle
        pygame.draw.rect(icon, color, (2, 2, icon_size-4, icon_size-4), 0, 5)
        pygame.draw.rect(icon, (0, 0, 0), (2, 2, icon_size-4, icon_size-4), 1, 5)
        
        # Add specific symbols for each status
        if effect_name == "poison":
            # Skull and crossbones
            pygame.draw.circle(icon, (255, 255, 255), (16, 12), 5)
            pygame.draw.line(icon, (255, 255, 255), (10, 20), (22, 20), 2)
            pygame.draw.line(icon, (255, 255, 255), (13, 17), (19, 23), 2)
            pygame.draw.line(icon, (255, 255, 255), (19, 17), (13, 23), 2)
        elif effect_name == "sleep":
            # ZZZ
            pygame.draw.line(icon, (255, 255, 255), (10, 10), (20, 10), 2)
            pygame.draw.line(icon, (255, 255, 255), (15, 15), (25, 15), 2)
            pygame.draw.line(icon, (255, 255, 255), (12, 20), (22, 20), 2)
        elif effect_name == "silence":
            # Slash through mouth
            pygame.draw.ellipse(icon, (255, 255, 255), (8, 11, 16, 10), 1)
            pygame.draw.line(icon, (255, 0, 0), (6, 25), (26, 7), 2)
        elif effect_name == "berserk":
            # Angry eyes
            pygame.draw.line(icon, (255, 255, 255), (10, 10), (14, 14), 2)
            pygame.draw.line(icon, (255, 255, 255), (18, 14), (22, 10), 2)
            pygame.draw.arc(icon, (255, 255, 255), (8, 15, 16, 10), 3.14, 6.28, 2)
        elif effect_name == "stat_boost":
            # Up arrow
            pygame.draw.line(icon, (255, 255, 255), (16, 8), (16, 24), 2)
            pygame.draw.line(icon, (255, 255, 255), (16, 8), (10, 14), 2)
            pygame.draw.line(icon, (255, 255, 255), (16, 8), (22, 14), 2)
        
        # Save the icon
        pygame.image.save(icon, os.path.join(effects_dir, f"{effect_name}.png"))
        print(f"Generated {effect_name} status effect icon")

def main():
    """Generate all placeholder assets."""
    generate_terrain_tiles()
    generate_unit_sprites()
    generate_status_effect_icons()
    print("All placeholder assets generated successfully!")

if __name__ == "__main__":
    main()
    pygame.quit() 