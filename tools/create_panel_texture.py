#!/usr/bin/env python3
"""
Script to generate a simple UI panel texture
"""

import os
import pygame

# Initialize pygame
pygame.init()

# Ensure directory exists
os.makedirs("assets/ui", exist_ok=True)

# Create a simple panel texture
panel_size = (200, 100)
panel = pygame.Surface(panel_size, pygame.SRCALPHA)

# Fill with a semi-transparent dark color
panel.fill((40, 40, 60, 220))

# Add a border
pygame.draw.rect(panel, (100, 100, 150, 255), (0, 0, panel_size[0], panel_size[1]), 2)

# Add some decoration
pygame.draw.line(panel, (100, 100, 150, 150), (0, 10), (panel_size[0], 10), 1)
pygame.draw.line(panel, (100, 100, 150, 150), (0, panel_size[1]-10), (panel_size[0], panel_size[1]-10), 1)

# Save the panel
pygame.image.save(panel, "assets/ui/panel.png")
print("Created UI panel texture at assets/ui/panel.png")

# Create a simple button texture
button_size = (80, 30)
button = pygame.Surface(button_size, pygame.SRCALPHA)

# Fill with a semi-transparent color
button.fill((60, 60, 100, 220))

# Add a border
pygame.draw.rect(button, (120, 120, 180, 255), (0, 0, button_size[0], button_size[1]), 2)

# Add a highlight
pygame.draw.line(button, (150, 150, 200, 200), (2, 2), (button_size[0]-2, 2), 1)

# Save the button
pygame.image.save(button, "assets/ui/button.png")
print("Created button texture at assets/ui/button.png")

# Create a simple cursor texture
cursor_size = (32, 32)
cursor = pygame.Surface(cursor_size, pygame.SRCALPHA)

# Draw a cursor arrow
points = [(0, 0), (20, 10), (10, 15), (15, 25), (8, 22), (5, 15), (0, 20)]
pygame.draw.polygon(cursor, (220, 220, 250, 220), points)
pygame.draw.polygon(cursor, (100, 100, 180, 255), points, 1)

# Save the cursor
pygame.image.save(cursor, "assets/ui/cursor.png")
print("Created cursor texture at assets/ui/cursor.png")

pygame.quit()
print("All UI textures created successfully!") 