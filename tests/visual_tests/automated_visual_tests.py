#!/usr/bin/env python3
"""
Automated Visual Tests Runner

This script automatically runs all visual tests in sequence without requiring user interaction,
logs any issues, and self-terminates when complete.
"""

import sys
import os
import pygame
import time
import logging
import traceback
from datetime import datetime
import math
import random
from enum import Enum, auto
from pathlib import Path
import pygame.math

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import game renderer
from src.ui.pygame_renderer import (
    GameRenderer, 
    AnimationType, 
    ParticleSystemEffect, 
    ParticleEffectAnimation
)

# Configure logging
LOG_DIR = os.path.join(PROJECT_ROOT, "logs", "visual_tests")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"visual_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("VisualTests")

# Define status type as an enum
class StatusType(Enum):
    POISONED = "POISONED"
    SLOWED = "SLOWED"
    STUNNED = "STUNNED"
    CONFUSED = "CONFUSED"
    FROZEN = "FROZEN"

# Status effect class for testing
class StatusEffect:
    def __init__(self, effect_type):
        self.type = effect_type
        self.duration = 3
        self.intensity = 1

    def __str__(self):
        return f"{self.type.name}"

# Fix for pygame.math.sin issue (as in visual_tests_gui.py)
class FixedHighlightTilesAnimation:
    """Fixed version of highlight tiles animation that doesn't disappear immediately."""
    
    def __init__(self, tile_positions, color=(100, 200, 255, 150), duration_ms=5000):
        """Initialize the highlight animation.
        
        Args:
            tile_positions: List of (x,y) tile positions to highlight
            color: RGBA color to use for highlighting
            duration_ms: How long the highlight should last in milliseconds
        """
        self.tile_positions = tile_positions
        self.color = color
        self.duration_ms = duration_ms
        self.start_time = time.time()
        self.is_active = True
    
    @property
    def completed(self):
        """Property that returns whether the animation is completed (opposite of is_active)."""
        return not self.is_active

    def update(self):
        """Update the animation state."""
        if time.time() - self.start_time > self.duration_ms / 1000:
            self.is_active = False
    
    def draw(self, surface):
        """Draw the highlight on the surface."""
        # Only draw if active
        if not self.is_active:
            return
            
        # Draw highlight for each tile
        for pos in self.tile_positions:
            # Calculate screen position
            screen_x = pos[0] * 32  # Use fixed tile size of 32 pixels
            screen_y = pos[1] * 32
            
            # Create a semi-transparent surface for the highlight
            highlight_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            highlight_surface.fill(self.color)
            
            # Draw the highlight
            surface.blit(highlight_surface, (screen_x, screen_y))

# Override GameRenderer.play_animation for the test
original_play_animation = GameRenderer.play_animation

def fixed_play_animation(self, animation_type, **kwargs):
    """Fixed version of play_animation that uses our fixed HighlightTilesAnimation."""
    # Special case for highlight tiles animation
    if animation_type == AnimationType.HIGHLIGHT_TILES:
        tile_positions = kwargs.get('tile_positions', [])
        color = kwargs.get('color', (100, 200, 255, 150))
        duration_ms = kwargs.get('duration_ms', 5000)
        
        # Use our fixed version
        animation = FixedHighlightTilesAnimation(
            tile_positions=tile_positions,
            color=color,
            duration_ms=duration_ms
        )
        
        self.animations.append(animation)
        return animation
    
    # Use original method for other animation types
    return original_play_animation(self, animation_type, **kwargs)

# Create custom renderer class to avoid reinitializing pygame
class TestGameRenderer(GameRenderer):
    """Custom GameRenderer that doesn't reinitialize pygame."""
    def __init__(self, game_state_manager, window_size=(800, 600), title="Fantasy Tactics Game", screen=None):
        # Skip the pygame initialization - screen is provided
        self.gsm = game_state_manager
        self.window_size = window_size
        self.title = title
        self.screen = screen
        
        # Get map dimensions
        map_width, map_height = game_state_manager.get_map_dimensions()
        
        # Calculate tile size based on window and map size
        self.tile_size = min(
            int(window_size[0] * 0.8 / map_width),
            int(window_size[1] * 0.8 / map_height)
        )
        
        # Set up camera
        self.camera_pos = [0, 0]
        self.target_camera_pos = [0, 0]
        self.camera_speed = 0.2
        
        # Initialize animations and effects
        self.animations = []
        self.effects = []
        
        # Load assets
        self.load_assets()
        
        # Set up fonts
        self.font = pygame.font.SysFont("Arial", 14)
        self.big_font = pygame.font.SysFont("Arial", 24)
        
        # Added for custom update function
        self.custom_update_function = None
        
        # Debug options
        self.show_grid = True
        self.show_coordinates = True
        self.show_fps = True
        self.last_frame_time = time.time()
        self.frame_times = []  # Store last 10 frame times for averaging
        
        # Use provided screen
        self.clock = pygame.time.Clock()
        
        # Set up fonts
        self.ui_font = pygame.font.SysFont('Arial', 18, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Load sounds
        self.sounds = {}  # Skip sounds for tests
        
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
        self.max_frame_times = 60  # store last 60 frames for avg FPS
        
        # Flag for running
        self.running = True
    
    def close(self):
        """Modified close method that doesn't quit pygame."""
        self.running = False
        
    def draw(self, surface):
        """Draw the current game state to the provided surface."""
        # Clear the surface
        surface.fill((20, 20, 30))  # Darker background color
        
        # Draw the map
        self.draw_map()
        
        # Draw units
        self.draw_units()
        
        # Draw active animations
        for animation in self.animations:
            animation.draw(surface)
        
        # Draw enhanced UI
        self.draw_enhanced_ui()
        
        # Draw debug info if enabled
        self.draw_debug_info()

    def update(self):
        """Update the renderer state."""
        if self.custom_update_function:
            # If a custom update function is set, use that instead
            self.custom_update_function()
        else:
            # Otherwise call the original update logic
            self._update()
    
    def _update(self):
        """Original update logic."""
        # Calculate delta time
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Track frame times for FPS calculation
        self.frame_times.append(delta_time)
        if len(self.frame_times) > 10:
            self.frame_times.pop(0)
        
        # Smooth camera movement
        dx = self.target_camera_pos[0] - self.camera_pos[0]
        dy = self.target_camera_pos[1] - self.camera_pos[1]
        
        self.camera_pos[0] += dx * self.camera_speed
        self.camera_pos[1] += dy * self.camera_speed
        
        # Update animations
        for anim in list(self.animations):
            anim.update()
            if anim.completed:
                self.animations.remove(anim)
        
        # Update effects
        for effect in list(self.effects):
            effect.update()
            if not effect.is_active:
                self.effects.remove(effect)

    def map_to_screen_coords(self, map_x, map_y):
        """Convert map coordinates to screen coordinates.
        
        Args:
            map_x: Map x-coordinate
            map_y: Map y-coordinate
            
        Returns:
            (screen_x, screen_y) tuple of screen coordinates
        """
        # Calculate screen position based on map position, camera, and tile size
        screen_x = int((map_x - self.camera_pos[0]) * self.tile_size + self.window_size[0] / 2)
        screen_y = int((map_y - self.camera_pos[1]) * self.tile_size + self.window_size[1] / 2)
        
        return (screen_x, screen_y)

    # Add property to map gsm to game_state_manager for compatibility
    @property
    def game_state_manager(self):
        return self.gsm

    def load_assets(self):
        """Load assets for the renderer."""
        # In the test environment, we'll use minimal assets
        self.assets = {
            'tiles': {
                'plain': pygame.Surface((32, 32)),
                'forest': pygame.Surface((32, 32)),
                'mountain': pygame.Surface((32, 32)),
                'river': pygame.Surface((32, 32)),
                'fort': pygame.Surface((32, 32)),
                'wall': pygame.Surface((32, 32)),
                'village': pygame.Surface((32, 32)),
                'desert': pygame.Surface((32, 32))
            },
            'units': {
                'infantry_player': pygame.Surface((32, 32)),
                'cavalry_player': pygame.Surface((32, 32)),
                'archer_player': pygame.Surface((32, 32)),
                'infantry_enemy': pygame.Surface((32, 32)),
                'cavalry_enemy': pygame.Surface((32, 32)),
                'archer_enemy': pygame.Surface((32, 32))
            },
            'ui': {
                'cursor': pygame.Surface((32, 32)),
                'move_tile': pygame.Surface((32, 32)),
                'attack_tile': pygame.Surface((32, 32))
            },
            'effects': {
                'explosion': pygame.Surface((32, 32)),
                'spark': pygame.Surface((32, 32)),
                'fire': pygame.Surface((32, 32))
            }
        }
        
        # Set some colors to differentiate the surfaces
        self.assets['tiles']['plain'].fill((200, 200, 100))
        self.assets['tiles']['forest'].fill((50, 150, 50))
        self.assets['tiles']['mountain'].fill((150, 150, 150))
        self.assets['tiles']['river'].fill((100, 100, 255))
        self.assets['tiles']['fort'].fill((200, 200, 50))
        self.assets['tiles']['wall'].fill((100, 100, 100))
        self.assets['tiles']['village'].fill((200, 100, 100))
        self.assets['tiles']['desert'].fill((240, 220, 130))
        
        self.assets['units']['infantry_player'].fill((0, 0, 255))
        self.assets['units']['cavalry_player'].fill((0, 0, 200))
        self.assets['units']['archer_player'].fill((0, 100, 255))
        self.assets['units']['infantry_enemy'].fill((255, 0, 0))
        self.assets['units']['cavalry_enemy'].fill((200, 0, 0))
        self.assets['units']['archer_enemy'].fill((255, 100, 0))
        
        self.assets['ui']['cursor'].fill((255, 255, 0))
        self.assets['ui']['move_tile'].fill((0, 255, 255, 100))
        self.assets['ui']['attack_tile'].fill((255, 0, 0, 100))
        
        self.assets['effects']['explosion'].fill((255, 100, 0))
        self.assets['effects']['spark'].fill((255, 255, 0))
        self.assets['effects']['fire'].fill((255, 50, 0))
        
        return self.assets

    def get_unit_sprite(self, unit):
        """Get a sprite for the given unit.
        
        Args:
            unit: Unit object
            
        Returns:
            Surface for the unit
        """
        # Create a simple colored sprite for the unit
        sprite = pygame.Surface((24, 24))
        
        # Color based on faction and movement type
        if unit.faction.name == "PLAYER":
            if hasattr(unit, 'weapon_type'):
                if unit.weapon_type == "SWORD":
                    sprite.fill((0, 0, 200))  # Blue for player swords
                elif unit.weapon_type == "BOW":
                    sprite.fill((0, 150, 255))  # Light blue for player bows
                elif unit.weapon_type == "MAGIC":
                    sprite.fill((150, 100, 255))  # Purple for player magic
                else:
                    sprite.fill((0, 0, 255))  # Default blue for player
            else:
                sprite.fill((0, 0, 255))
        else:
            if hasattr(unit, 'weapon_type'):
                if unit.weapon_type == "SWORD":
                    sprite.fill((200, 0, 0))  # Dark red for enemy swords
                elif unit.weapon_type == "BOW":
                    sprite.fill((255, 120, 0))  # Orange for enemy bows
                elif unit.weapon_type == "MAGIC":
                    sprite.fill((255, 0, 255))  # Magenta for enemy magic
                else:
                    sprite.fill((255, 0, 0))  # Default red for enemy
            else:
                sprite.fill((255, 0, 0))
        
        return sprite

# Test categories from run_all_visual_tests.py
MECHANIC_CATEGORIES = [
    {
        "name": "Core Mechanics",
        "tests": [
            "movement", 
            "combat", 
            "terrain",
            "inventory",
            "attack_mechanics"
        ]
    },
    {
        "name": "Unit Mechanics",
        "tests": [
            "recruitment", 
            "death", 
            "rescue", 
            "status_effects",
            "promotion"
        ]
    },
    {
        "name": "Special Mechanics",
        "tests": [
            "weather", 
            "events", 
            "objectives",
            "reinforcements",
            "effects",
            "field_of_view"
        ]
    },
    {
        "name": "Integrated Scenarios",
        "tests": [
            "simple_battle",
            "tactical_challenge",
            "strategic_battle"
        ]
    }
]

class AutomatedTestRunner:
    """Automated test runner that runs through all tests without user interaction."""
    
    def __init__(self, window_size=(1024, 768), test_duration=8):
        """Initialize the test runner.
        
        Args:
            window_size: Tuple of (width, height) for the window
            test_duration: How long to run each test in seconds
        """
        self.window_size = window_size
        self.test_duration = test_duration
        self.screen = None
        self.clock = pygame.time.Clock()
        self.current_renderer = None
        self.total_tests = sum(len(category["tests"]) for category in MECHANIC_CATEGORIES)
        self.tests_completed = 0
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Fantasy Tactics - Automated Visual Tests")
        
        # Apply fix for highlight animation
        GameRenderer.play_animation = fixed_play_animation
        
    def run_all_tests(self):
        """Run all the visual tests automatically."""
        start_time = time.time()
        logger.info(f"Starting automated test run of {self.total_tests} tests")
        
        try:
            # Run through all categories and tests
            for category_idx, category in enumerate(MECHANIC_CATEGORIES):
                category_name = category["name"]
                logger.info(f"Starting category {category_idx+1}/{len(MECHANIC_CATEGORIES)}: {category_name}")
                
                for test_idx, test_name in enumerate(category["tests"]):
                    self.tests_completed += 1
                    progress = f"({self.tests_completed}/{self.total_tests})"
                    logger.info(f"Running test {progress}: {category_name} - {test_name}")
                    
                    try:
                        self.run_test(test_name, category_name)
                    except Exception as e:
                        logger.error(f"Error in test {test_name}: {str(e)}")
                        logger.error(traceback.format_exc())
                    
                    # Process events to keep window responsive
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            raise KeyboardInterrupt("User closed the window")
                
                logger.info(f"Completed category: {category_name}")
            
            total_time = time.time() - start_time
            logger.info(f"All tests completed in {total_time:.2f} seconds")
            
        except KeyboardInterrupt:
            logger.info("Test run interrupted by user")
        finally:
            # Clean up and exit
            if self.current_renderer:
                self.current_renderer.close()
            pygame.quit()
    
    def run_test(self, test_name, category_name):
        """Run a single test with automatic screen capture and logging.
        
        Args:
            test_name: Name of the test to run
            category_name: Name of the category this test belongs to
        """
        # Create test state
        gsm = self.create_test_game_state(test_name)
        
        # Create renderer
        self.current_renderer = TestGameRenderer(
            gsm, 
            window_size=self.window_size,
            title=f"Visual Test: {test_name}",
            screen=self.screen
        )
        
        # Center camera on player if available
        if "player1" in gsm.units:
            unit = gsm.units["player1"]
            self.current_renderer.center_camera_on_position(unit.position[0], unit.position[1])
        
        # Schedule animations based on test type
        self.schedule_test_animations(test_name, gsm)
        
        # Create a header text for the test
        status_font = pygame.font.SysFont("Arial", 20)
        status_text = f"{category_name} - {test_name} ({self.tests_completed}/{self.total_tests})"
        text_surface = status_font.render(status_text, True, (255, 255, 255), (0, 0, 0))
        
        # Run test for the specified duration
        start_time = time.time()
        frame_count = 0
        
        # Save screenshot path (with fixed filename, no timestamp)
        screenshot_dir = os.path.join(LOG_DIR, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(
            screenshot_dir, 
            f"{category_name.replace(' ', '_')}_{test_name}.jpg"
        )
        
        screenshot_taken = False
        
        while time.time() - start_time < self.test_duration:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt("User closed the window")
            
            # Update renderer
            self.current_renderer.update()
            
            # Render
            self.current_renderer.render()
            
            # Add status text at the top
            self.screen.blit(text_surface, (10, 10))
            
            # Take a screenshot after a couple of seconds (when animations have started)
            if not screenshot_taken and time.time() - start_time > 2.0:
                # Save as JPG for better compression
                pygame.image.save(self.screen, screenshot_path)
                logger.info(f"Saved screenshot to {screenshot_path}")
                screenshot_taken = True
            
            # Update display and control framerate
            pygame.display.flip()
            self.clock.tick(60)
            frame_count += 1
        
        # Log performance info
        fps = frame_count / self.test_duration
        logger.info(f"Test {test_name} ran at {fps:.1f} FPS")
        
        # Clean up renderer
        self.current_renderer.close()
        self.current_renderer = None
    
    def create_test_game_state(self, test_name):
        """Create a dummy game state for the selected test."""
        class DummyGameStateManager:
            def __init__(self, test_name):
                self.current_turn = 1
                self.current_phase = "PLAYER"
                self.selected_unit = None
                self.units = {}
                self.test_name = test_name
                
                # Create a map appropriate for the test
                if test_name == "terrain":
                    self.map_width = 20
                    self.map_height = 15
                else:
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
                    VILLAGE = "VILLAGE"
                    DESERT = "DESERT"
                    
                    def __init__(self, name):
                        self.name = name
                
                # Fill the map based on test type
                self.fill_map_for_test(TerrainType)
                
                # Add units based on test type
                self.create_units_for_test()
                
                # Set selected unit
                if "player1" in self.units:
                    self.selected_unit = self.units["player1"]
            
            def fill_map_for_test(self, TerrainType):
                """Fill the map with appropriate terrain for the test."""
                # Default to plains
                for y in range(self.map_height):
                    for x in range(self.map_width):
                        self.terrain_grid[y][x] = TerrainType("PLAIN")
                
                if self.test_name == "movement":
                    # Create a varied map with different terrain for movement costs
                    for x in range(3, 6):
                        for y in range(4, 7):
                            self.terrain_grid[y][x] = TerrainType("FOREST")
                    
                    for x in range(8, 10):
                        for y in range(6, 9):
                            self.terrain_grid[y][x] = TerrainType("MOUNTAIN")
                    
                    for y in range(3, 12):
                        self.terrain_grid[y][12] = TerrainType("RIVER")
                    
                    self.terrain_grid[2][2] = TerrainType("FORT")
                    self.terrain_grid[12][12] = TerrainType("FORT")
                
                elif self.test_name == "combat":
                    # Create a battlefield with various terrain
                    for x in range(3, 6):
                        for y in range(4, 7):
                            self.terrain_grid[y][x] = TerrainType("FOREST")
                    
                    self.terrain_grid[7][7] = TerrainType("FORT")
                    self.terrain_grid[10][10] = TerrainType("MOUNTAIN")
                
                elif self.test_name == "terrain":
                    # Create a showcase of all terrain types
                    terrain_types = ["PLAIN", "FOREST", "MOUNTAIN", "RIVER", "FORT", "WALL", "VILLAGE", "DESERT"]
                    for i, terrain in enumerate(terrain_types):
                        for y in range(3, 12):
                            for x in range(i*2 + 2, i*2 + 4):
                                if x < self.map_width:
                                    self.terrain_grid[y][x] = TerrainType(terrain)
                
                elif self.test_name in ["status_effects", "weather"]:
                    # Just add a few terrain features
                    for x in range(3, 6):
                        for y in range(3, 6):
                            self.terrain_grid[y][x] = TerrainType("FOREST")
                    
                    self.terrain_grid[7][7] = TerrainType("FORT")
                    self.terrain_grid[10][10] = TerrainType("MOUNTAIN")
                    self.terrain_grid[12][3] = TerrainType("VILLAGE")
                
                elif self.test_name in ["recruitment", "promotion"]:
                    # Create a village and fort
                    self.terrain_grid[5][5] = TerrainType("VILLAGE")
                    self.terrain_grid[10][10] = TerrainType("FORT")
                
                else:
                    # Generic map with some features for other tests
                    for x in range(2, 5):
                        for y in range(2, 5):
                            self.terrain_grid[y][x] = TerrainType("FOREST")
                            
                    for x in range(10, 12):
                        for y in range(10, 12):
                            self.terrain_grid[y][x] = TerrainType("MOUNTAIN")
                    
                    for y in range(6, 8):
                        self.terrain_grid[y][7] = TerrainType("RIVER")
                    
                    self.terrain_grid[3][3] = TerrainType("FORT")
                    self.terrain_grid[12][12] = TerrainType("VILLAGE")
            
            def create_units_for_test(self):
                """Create units appropriate for the test."""
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
                
                # Add units based on test type
                if self.test_name == "combat":
                    # Add more units for combat testing
                    self.units["player1"] = DummyUnit("player1", "Hero", "PLAYER", (3, 3), "INFANTRY", 20, 20)
                    self.units["player2"] = DummyUnit("player2", "Archer", "PLAYER", (4, 2), "INFANTRY", 15, 15)
                    self.units["player3"] = DummyUnit("player3", "Cavalier", "PLAYER", (2, 4), "CAVALRY", 22, 25)
                    
                    self.units["enemy1"] = DummyUnit("enemy1", "Bandit", "ENEMY", (10, 10), "INFANTRY", 15, 20)
                    self.units["enemy2"] = DummyUnit("enemy2", "Mage", "ENEMY", (11, 9), "INFANTRY", 10, 15)
                    self.units["enemy3"] = DummyUnit("enemy3", "Archer", "ENEMY", (9, 11), "INFANTRY", 12, 15)
                
                elif self.test_name == "movement":
                    # Just a few units for movement testing
                    self.units["player1"] = DummyUnit("player1", "Hero", "PLAYER", (2, 2), "INFANTRY", 20, 20)
                    self.units["player2"] = DummyUnit("player2", "Cavalier", "PLAYER", (3, 3), "CAVALRY", 25, 25)
                    self.units["player3"] = DummyUnit("player3", "Pegasus Knight", "PLAYER", (4, 2), "FLYING", 18, 18)
                
                elif self.test_name == "status_effects":
                    # Units for status effect testing
                    self.units["player1"] = DummyUnit("player1", "Hero", "PLAYER", (3, 3), "INFANTRY", 15, 20)
                    self.units["player2"] = DummyUnit("player2", "Mage", "PLAYER", (4, 4), "INFANTRY", 10, 15)
                    self.units["player3"] = DummyUnit("player3", "Cleric", "PLAYER", (5, 5), "INFANTRY", 12, 15)
                    self.units["enemy1"] = DummyUnit("enemy1", "Bandit", "ENEMY", (8, 8), "INFANTRY", 18, 20)
                    
                    # Add status effects using the new class
                    self.units["player1"].status_effects = [StatusEffect(StatusType.POISONED)]
                    self.units["enemy1"].status_effects = [StatusEffect(StatusType.SLOWED)]
                
                elif self.test_name == "terrain":
                    # Units for terrain showcase
                    self.units["player1"] = DummyUnit("player1", "Hero", "PLAYER", (2, 2), "INFANTRY", 20, 20)
                    self.units["player2"] = DummyUnit("player2", "Cavalier", "PLAYER", (4, 4), "CAVALRY", 25, 25)
                    self.units["player3"] = DummyUnit("player3", "Pegasus Knight", "PLAYER", (6, 6), "FLYING", 18, 18)
                    self.units["enemy1"] = DummyUnit("enemy1", "Bandit", "ENEMY", (12, 10), "INFANTRY", 15, 20)
                
                else:
                    # Generic units for other tests
                    self.units["player1"] = DummyUnit("player1", "Hero", "PLAYER", (3, 4), "INFANTRY", 20, 20)
                    self.units["player2"] = DummyUnit("player2", "Archer", "PLAYER", (4, 3), "INFANTRY", 15, 15)
                    self.units["enemy1"] = DummyUnit("enemy1", "Bandit", "ENEMY", (10, 10), "INFANTRY", 15, 20)
                    self.units["npc1"] = DummyUnit("npc1", "Villager", "NPC", (8, 2), "INFANTRY", 10, 10)
            
            def get_map_dimensions(self):
                return (self.map_width, self.map_height)
            
            def get_terrain_at(self, position):
                x, y = position
                if 0 <= x < self.map_width and 0 <= y < self.map_height:
                    return self.terrain_grid[y][x]
                return None
            
            def get_all_units(self):
                return list(self.units.values())
            
            def get_unit(self, unit_id):
                return self.units.get(unit_id)
        
        # Create the game state manager
        return DummyGameStateManager(test_name)
    
    def schedule_test_animations(self, test_name, gsm):
        """Schedule animations to run for the given test type."""
        # Clear any existing custom update functions
        self.current_renderer.custom_update_function = None
        
        # Based on test name, set up appropriate animations
        if test_name == "movement":
            self.schedule_movement_test(gsm)
        elif test_name == "combat":
            self.schedule_combat_test(gsm)
        elif test_name == "status_effects":
            self.schedule_status_effect_test(gsm)
        elif test_name == "effects":
            self.schedule_effects_test(gsm)
        elif test_name == "field_of_view":
            self.schedule_field_of_view_test(gsm)
        elif test_name == "attack_mechanics":
            self.schedule_attack_mechanics_test(gsm)
        else:
            # Generic test with basic animations
            self.schedule_generic_test(gsm)
        
        logger.info(f"Scheduled animations for test: {test_name}")
    
    def schedule_movement_test(self, gsm):
        """Schedule animations for movement test."""
        # Set up initial timer variables
        self.movement_timers = {}
        start_time = time.time()
        
        if "player1" in gsm.units:
            unit = gsm.units["player1"]
            # Schedule player1 movement right away
            path = [unit.position, (unit.position[0]+1, unit.position[1]), 
                   (unit.position[0]+2, unit.position[1]+1), (unit.position[0]+3, unit.position[1]+2)]
            self.current_renderer.play_animation(AnimationType.MOVE, unit_id="player1", path=path)
            unit.position = path[-1]
            
            # Schedule another move after 3 seconds
            self.movement_timers["player1_move2"] = start_time + 3
        
        if "player2" in gsm.units:
            unit = gsm.units["player2"]
            # Schedule player2 movement after 1.5 seconds
            self.movement_timers["player2_move"] = start_time + 1.5
            
        # Update function to handle timed animations
        original_update = self.current_renderer.update
        
        def timed_update_function(delta_time=None):
            # Call the original update first
            original_update(delta_time)
            
            # Check movement timers
            current_time = time.time()
            
            # Check player1 second move timer
            if "player1_move2" in self.movement_timers and current_time >= self.movement_timers["player1_move2"]:
                if "player1" in gsm.units:
                    unit = gsm.units["player1"]
                    path = [unit.position, 
                           (unit.position[0]+1, unit.position[1]), 
                           (unit.position[0]+2, unit.position[1]-1)]
                    self.current_renderer.play_animation(AnimationType.MOVE, unit_id="player1", path=path)
                    unit.position = path[-1]
                del self.movement_timers["player1_move2"]
            
            # Check player2 move timer
            if "player2_move" in self.movement_timers and current_time >= self.movement_timers["player2_move"]:
                if "player2" in gsm.units:
                    unit = gsm.units["player2"]
                    path = [unit.position, (unit.position[0], unit.position[1]+1), 
                           (unit.position[0]+1, unit.position[1]+2), (unit.position[0]+2, unit.position[1]+2)]
                    self.current_renderer.play_animation(AnimationType.MOVE, unit_id="player2", path=path)
                    unit.position = path[-1]
                del self.movement_timers["player2_move"]
        
        # Replace the update function
        self.current_renderer.custom_update_function = timed_update_function
    
    def schedule_combat_test(self, gsm):
        """Schedule animations for combat test."""
        # Set up timer variables
        self.combat_timers = {}
        start_time = time.time()
        
        if "player1" in gsm.units and "enemy1" in gsm.units:
            player_unit = gsm.units["player1"]
            enemy_unit = gsm.units["enemy1"]
            
            # Move player1 closer to enemy1 right away
            path = [player_unit.position, (5, 5), (6, 6), (7, 7), (8, 8)]
            self.current_renderer.play_animation(AnimationType.MOVE, unit_id="player1", path=path)
            player_unit.position = path[-1]
            
            # Schedule attack after 2 seconds
            self.combat_timers["attack"] = start_time + 2
            
            # Schedule counterattack after 4 seconds
            self.combat_timers["counterattack"] = start_time + 4
        
        # Update function to handle timed animations
        original_update = self.current_renderer.update
        
        def timed_update_function(delta_time=None):
            # Call the original update first
            original_update(delta_time)
            
            # Check combat timers
            current_time = time.time()
            
            # Check attack timer
            if "attack" in self.combat_timers and current_time >= self.combat_timers["attack"]:
                if "player1" in gsm.units and "enemy1" in gsm.units:
                    player_unit = gsm.units["player1"]
                    enemy_unit = gsm.units["enemy1"]
                    
                    self.current_renderer.play_animation(AnimationType.ATTACK, 
                                                attacker_pos=player_unit.position,
                                                defender_pos=enemy_unit.position)
                    
                    # Play damage animation right after
                    self.current_renderer.play_animation(AnimationType.TAKE_DAMAGE,
                                                unit_pos=enemy_unit.position,
                                                damage=5)
                    
                    # Update HP
                    enemy_unit.current_hp = max(0, enemy_unit.current_hp - 5)
                
                del self.combat_timers["attack"]
            
            # Check counterattack timer
            if "counterattack" in self.combat_timers and current_time >= self.combat_timers["counterattack"]:
                if "player1" in gsm.units and "enemy1" in gsm.units:
                    player_unit = gsm.units["player1"]
                    enemy_unit = gsm.units["enemy1"]
                    
                    self.current_renderer.play_animation(AnimationType.ATTACK, 
                                                attacker_pos=enemy_unit.position,
                                                defender_pos=player_unit.position)
                    
                    # Play damage animation right after
                    self.current_renderer.play_animation(AnimationType.TAKE_DAMAGE,
                                                unit_pos=player_unit.position,
                                                damage=3)
                    
                    # Update HP
                    player_unit.current_hp = max(0, player_unit.current_hp - 3)
                
                del self.combat_timers["counterattack"]
        
        # Replace the update function
        self.current_renderer.custom_update_function = timed_update_function
    
    def schedule_status_effect_test(self, gsm):
        """Schedule animations for status effect test."""
        # Set up timer variables
        self.status_timers = {}
        start_time = time.time()
        
        if "player1" in gsm.units:
            unit = gsm.units["player1"]
            
            # Apply status effect animation right away
            self.current_renderer.play_animation(AnimationType.APPLY_STATUS,
                                       unit_pos=unit.position,
                                       status_type=StatusType.POISONED)
            
            # Schedule status effect removal after a delay
            self.status_timers["remove_status"] = start_time + 3
        
        # Update function to handle timed animations
        original_update = self.current_renderer.update
        
        def timed_update_function(delta_time=None):
            # Call the original update first
            original_update(delta_time)
            
            # Check status effect timers
            current_time = time.time()
            
            # Check status removal timer
            if "remove_status" in self.status_timers and current_time >= self.status_timers["remove_status"]:
                if "player1" in gsm.units:
                    unit = gsm.units["player1"]
                    
                    # Use the same status enum
                    self.current_renderer.play_animation(AnimationType.REMOVE_STATUS,
                                                unit_pos=unit.position,
                                                status_type=StatusType.POISONED)
                
                del self.status_timers["remove_status"]
        
        # Replace the update function
        self.current_renderer.custom_update_function = timed_update_function
    
    def schedule_effects_test(self, gsm):
        """Schedule animations for visual effects test."""
        # Set up timer variables
        self.effects_timers = {}
        start_time = time.time()
        
        # Start with a fade in
        fade_in = self.current_renderer.play_animation(AnimationType.FADE,
                                         fade_in=True,
                                         color=(0, 0, 0),
                                         duration=1000)
        
        # Schedule particle effects at intervals
        self.effects_timers["explosion"] = start_time + 1.5
        self.effects_timers["sparks"] = start_time + 3.0
        self.effects_timers["smoke"] = start_time + 4.5
        self.effects_timers["fade_out"] = start_time + 6.0
        
        # Update function to handle timed animations
        original_update = self.current_renderer.update
        
        def timed_update_function(delta_time=None):
            # Call the original update first
            original_update(delta_time)
            
            # Check effects timers
            current_time = time.time()
            
            # Check explosion timer
            if "explosion" in self.effects_timers and current_time >= self.effects_timers["explosion"]:
                explosion_positions = [(3, 3), (6, 6), (8, 2)]
                for pos in explosion_positions:
                    self.current_renderer.play_animation(AnimationType.PARTICLE_EFFECT,
                                              position=pos,
                                              effect_type="explosion",
                                              num_particles=25,
                                              duration=1000)
                
                del self.effects_timers["explosion"]
            
            # Check sparks timer
            if "sparks" in self.effects_timers and current_time >= self.effects_timers["sparks"]:
                spark_positions = [(4, 5), (7, 4), (2, 7)]
                for pos in spark_positions:
                    self.current_renderer.play_animation(AnimationType.PARTICLE_EFFECT,
                                              position=pos,
                                              effect_type="sparks",
                                              num_particles=20,
                                              duration=1000)
                
                del self.effects_timers["sparks"]
            
            # Check smoke timer
            if "smoke" in self.effects_timers and current_time >= self.effects_timers["smoke"]:
                smoke_positions = [(5, 2), (8, 5), (3, 8)]
                for pos in smoke_positions:
                    self.current_renderer.play_animation(AnimationType.PARTICLE_EFFECT,
                                              position=pos,
                                              effect_type="smoke",
                                              num_particles=15,
                                              duration=1500)
                
                del self.effects_timers["smoke"]
            
            # Check fade out timer
            if "fade_out" in self.effects_timers and current_time >= self.effects_timers["fade_out"]:
                self.current_renderer.play_animation(AnimationType.FADE,
                                          fade_in=False,
                                          color=(0, 0, 0),
                                          duration=1500)
                
                del self.effects_timers["fade_out"]
        
        # Replace the update function
        self.current_renderer.custom_update_function = timed_update_function
    
    def schedule_field_of_view_test(self, gsm):
        """Schedule animations for field of view test."""
        # Set up timer variables
        self.fov_timers = {}
        start_time = time.time()
        
        # Highlight some tiles to show the map area
        highlight_positions = [(x, y) for x in range(5, 10) for y in range(5, 10)]
        self.current_renderer.play_animation(AnimationType.HIGHLIGHT_TILES,
                                   tile_positions=highlight_positions,
                                   color=(100, 200, 255, 50),  # Light blue, very transparent
                                   duration_ms=self.test_duration * 1000)  # Last the entire test
        
        # Create a player unit if not already present
        if "player1" not in gsm.units:
            # Create a dummy unit for the test
            from automated_visual_tests import DummyUnit
            gsm.units["player1"] = DummyUnit("player1", "Scout", "PLAYER", (7, 7), "INFANTRY", 20, 20)
            self.current_renderer.center_camera_on_position(7, 7)
        
        # Get player position
        player_pos = gsm.units["player1"].position
        
        # Start with field of view facing right (0 radians)
        self.current_renderer.play_animation(AnimationType.PARTICLE_EFFECT,
                                   position=player_pos,
                                   effect_type="field_of_view",
                                   num_particles=100,
                                   duration=2000,
                                   direction=0)  # facing right
        
        # Schedule field of view changes at intervals
        self.fov_timers["fov_change1"] = start_time + 2.0
        self.fov_timers["fov_change2"] = start_time + 4.0
        
        # Update function to handle timed animations
        original_update = self.current_renderer.update
        
        def timed_update_function(delta_time=None):
            # Call the original update first
            original_update(delta_time)
            
            # Check FOV timers
            current_time = time.time()
            
            # Check first FOV change timer - change to face down
            if "fov_change1" in self.fov_timers and current_time >= self.fov_timers["fov_change1"]:
                # Change the FOV angle to face down (PI/2 radians)
                self.current_renderer.play_animation(AnimationType.PARTICLE_EFFECT,
                                          position=player_pos,
                                          effect_type="field_of_view",
                                          num_particles=150,
                                          duration=2000,
                                          direction=math.pi/2)  # facing down
                
                del self.fov_timers["fov_change1"]
            
            # Check second FOV change timer - show multiple FOVs in different directions
            if "fov_change2" in self.fov_timers and current_time >= self.fov_timers["fov_change2"]:
                # Show multiple FOVs in different directions
                directions = [
                    math.pi,       # facing left
                    -math.pi/2,    # facing up
                    math.pi*3/4,   # facing down-left
                    -math.pi/4     # facing up-right
                ]
                
                for direction in directions:
                    self.current_renderer.play_animation(AnimationType.PARTICLE_EFFECT,
                                              position=player_pos,
                                              effect_type="field_of_view",
                                              num_particles=60,
                                              duration=2000,
                                              direction=direction)
                
                del self.fov_timers["fov_change2"]
        
        # Replace the update function
        self.current_renderer.custom_update_function = timed_update_function
    
    def schedule_attack_mechanics_test(self, gsm):
        """Schedule animations for the attack mechanics test."""
        # Ensure we have at least a player knight, archer, mage and enemy units
        if "knight" not in gsm.units:
            # Create units if not already present
            gsm.units["knight"] = type('DummyUnit', (), {
                'id': "knight",
                'name': "Knight",
                'faction': type('Faction', (), {'name': 'PLAYER'}),
                'position': (3, 3),
                'movement_type': type('MovementType', (), {'name': 'CAVALRY'}),
                'weapon_type': "SWORD",
                'current_hp': 30,
                'max_hp': 30,
                'disposition': type('Disposition', (), {'name': 'ACTIVE'}),
                'status_effects': []
            })
            gsm.units["archer"] = type('DummyUnit', (), {
                'id': "archer",
                'name': "Archer",
                'faction': type('Faction', (), {'name': 'PLAYER'}),
                'position': (2, 5),
                'movement_type': type('MovementType', (), {'name': 'INFANTRY'}),
                'weapon_type': "BOW",
                'current_hp': 20,
                'max_hp': 20,
                'disposition': type('Disposition', (), {'name': 'ACTIVE'}),
                'status_effects': []
            })
            gsm.units["mage"] = type('DummyUnit', (), {
                'id': "mage",
                'name': "Mage",
                'faction': type('Faction', (), {'name': 'PLAYER'}),
                'position': (4, 5),
                'movement_type': type('MovementType', (), {'name': 'INFANTRY'}),
                'weapon_type': "MAGIC",
                'current_hp': 15,
                'max_hp': 15,
                'disposition': type('Disposition', (), {'name': 'ACTIVE'}),
                'status_effects': []
            })
            gsm.units["enemy_knight"] = type('DummyUnit', (), {
                'id': "enemy_knight",
                'name': "Enemy Knight",
                'faction': type('Faction', (), {'name': 'ENEMY'}),
                'position': (7, 3),
                'movement_type': type('MovementType', (), {'name': 'CAVALRY'}),
                'weapon_type': "SWORD",
                'current_hp': 28,
                'max_hp': 28,
                'disposition': type('Disposition', (), {'name': 'ACTIVE'}),
                'status_effects': []
            })
            gsm.units["enemy_archer"] = type('DummyUnit', (), {
                'id': "enemy_archer",
                'name': "Enemy Archer",
                'faction': type('Faction', (), {'name': 'ENEMY'}),
                'position': (9, 6),
                'movement_type': type('MovementType', (), {'name': 'INFANTRY'}),
                'weapon_type': "BOW",
                'current_hp': 18,
                'max_hp': 18,
                'disposition': type('Disposition', (), {'name': 'ACTIVE'}),
                'status_effects': []
            })
            gsm.units["enemy_mage"] = type('DummyUnit', (), {
                'id': "enemy_mage",
                'name': "Enemy Mage",
                'faction': type('Faction', (), {'name': 'ENEMY'}),
                'position': (8, 4),
                'movement_type': type('MovementType', (), {'name': 'INFANTRY'}),
                'weapon_type': "MAGIC",
                'current_hp': 14,
                'max_hp': 14,
                'disposition': type('Disposition', (), {'name': 'ACTIVE'}),
                'status_effects': []
            })
        
        # Center the camera on the map
        self.current_renderer.center_camera_on_position(7, 5)
        
        # Highlight units
        player_units = []
        enemy_units = []
        
        for unit in gsm.get_all_units():
            if unit.faction.name == "PLAYER":
                player_units.append(unit.position)
            else:
                enemy_units.append(unit.position)
        
        # Highlight player units in blue
        self.current_renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=player_units,
            color=(0, 100, 255, 100),
            duration_ms=3000
        )
        
        # Highlight enemy units in red
        self.current_renderer.play_animation(
            AnimationType.HIGHLIGHT_TILES,
            tile_positions=enemy_units,
            color=(255, 50, 50, 100),
            duration_ms=3000
        )
        
        # Set up the animation sequence
        animation_timings = {
            # Knight attacks
            1.0: lambda: self.current_renderer.play_animation(
                AnimationType.MOVE,
                unit_id="knight",
                path=[(3, 3), (5, 3)]
            ),
            3.0: lambda: self.current_renderer.play_animation(
                AnimationType.HIGHLIGHT_TILES,
                tile_positions=[(6, 3)],
                color=(255, 0, 0, 150),
                duration_ms=1000
            ),
            4.0: lambda: self.current_renderer.play_animation(
                AnimationType.ATTACK,
                attacker_id="knight",
                defender_id="enemy_knight"
            ),
            4.2: lambda: self.current_renderer.add_effect(ParticleEffectAnimation(
                position=self.current_renderer.map_to_screen_coords(7, 3),
                effect_type="sparks",
                num_particles=20,
                duration=500
            )),
            4.5: lambda: self.current_renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=(7, 3),
                value=8
            ),
            5.2: lambda: self.current_renderer.play_animation(
                AnimationType.ATTACK,
                attacker_id="enemy_knight",
                defender_id="knight"
            ),
            5.4: lambda: self.current_renderer.add_effect(ParticleEffectAnimation(
                position=self.current_renderer.map_to_screen_coords(5, 3),
                effect_type="sparks",
                num_particles=15,
                duration=500
            )),
            5.6: lambda: self.current_renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=(5, 3),
                value=6
            ),
            
            # Archer attacks
            6.5: lambda: self.current_renderer.play_animation(
                AnimationType.MOVE,
                unit_id="archer",
                path=[(2, 5), (4, 7)]
            ),
            8.0: lambda: self.current_renderer.play_animation(
                AnimationType.HIGHLIGHT_TILES,
                tile_positions=[(9, 6)],
                color=(255, 0, 0, 150),
                duration_ms=1000
            ),
            8.2: lambda: self.current_renderer.play_animation(
                AnimationType.ATTACK_PATH,
                start_pos=(4, 7),
                end_pos=(9, 6),
                color=(255, 255, 0),
                duration_ms=1000
            ),
            9.0: lambda: self.current_renderer.play_animation(
                AnimationType.RANGED_ATTACK,
                attacker_id="archer",
                defender_id="enemy_archer",
                projectile_type="arrow"
            ),
            9.3: lambda: self.current_renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=(9, 6),
                value=7
            ),
            10.0: lambda: self.current_renderer.play_animation(
                AnimationType.RANGED_ATTACK,
                attacker_id="enemy_archer",
                defender_id="archer",
                projectile_type="arrow"
            ),
            10.3: lambda: self.current_renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=(4, 7),
                value=6
            ),
            
            # Mage attacks
            11.0: lambda: self.current_renderer.play_animation(
                AnimationType.MOVE,
                unit_id="mage",
                path=[(4, 5), (6, 5)]
            ),
            12.5: lambda: self.current_renderer.play_animation(
                AnimationType.HIGHLIGHT_TILES,
                tile_positions=[(8, 4)],
                color=(255, 0, 0, 150),
                duration_ms=1000
            ),
            13.5: lambda: self.current_renderer.play_animation(
                AnimationType.MAGIC_ATTACK,
                attacker_id="mage",
                defender_id="enemy_mage",
                magic_type="fire"
            ),
            13.7: lambda: self.current_renderer.add_effect(ParticleEffectAnimation(
                position=self.current_renderer.map_to_screen_coords(8, 4),
                effect_type="explosion",
                num_particles=30,
                duration=800
            )),
            14.0: lambda: self.current_renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=(8, 4),
                value=10
            ),
            14.5: lambda: self.current_renderer.play_animation(
                AnimationType.MAGIC_ATTACK,
                attacker_id="enemy_mage",
                defender_id="mage",
                magic_type="lightning"
            ),
            14.7: lambda: self.current_renderer.add_effect(ParticleEffectAnimation(
                position=self.current_renderer.map_to_screen_coords(6, 5),
                effect_type="sparks",
                num_particles=40,
                duration=600
            )),
            15.0: lambda: self.current_renderer.play_animation(
                AnimationType.DAMAGE_INDICATOR,
                position=(6, 5),
                value=9
            ),
        }
        
        # Define the update function
        start_time = time.time()
        
        def timed_update_function(delta_time=None):
            # Call the original update first
            self.current_renderer._update()
            
            # Get elapsed time
            elapsed = time.time() - start_time
            
            # Check if any animations need to be triggered
            for timing, action in list(animation_timings.items()):
                if elapsed >= timing:
                    action()
                    del animation_timings[timing]
        
        # Set the custom update function
        self.current_renderer.custom_update_function = timed_update_function
    
    def schedule_generic_test(self, gsm):
        """Schedule generic animations for tests without specific animations."""
        # Set up timer variables
        self.generic_timers = {}
        start_time = time.time()
        
        # Highlight random tiles right away
        random_positions = []
        for _ in range(5):
            x = random.randint(0, gsm.map_width - 1)
            y = random.randint(0, gsm.map_height - 1)
            random_positions.append((x, y))
        
        self.current_renderer.play_animation(AnimationType.HIGHLIGHT_TILES,
                                   tile_positions=random_positions,
                                   color=(255, 255, 0, 150),
                                   duration_ms=3000)
        
        # Schedule move animation after a delay
        if "player1" in gsm.units:
            self.generic_timers["move_unit"] = start_time + 2
        
        # Update function to handle timed animations
        original_update = self.current_renderer.update
        
        def timed_update_function(delta_time=None):
            # Call the original update first
            original_update(delta_time)
            
            # Check generic timers
            current_time = time.time()
            
            # Check move unit timer
            if "move_unit" in self.generic_timers and current_time >= self.generic_timers["move_unit"]:
                if "player1" in gsm.units:
                    unit = gsm.units["player1"]
                    
                    path = [unit.position, 
                           (unit.position[0] + 1, unit.position[1]),
                           (unit.position[0] + 1, unit.position[1] + 1),
                           (unit.position[0] + 2, unit.position[1] + 1)]
                    self.current_renderer.play_animation(AnimationType.MOVE, unit_id="player1", path=path)
                    unit.position = path[-1]
                
                del self.generic_timers["move_unit"]
        
        # Replace the update function
        self.current_renderer.custom_update_function = timed_update_function

def main():
    """Main entry point for automated visual tests."""
    logger.info("Starting automated visual tests")
    
    # Create and run the automated test runner
    test_runner = AutomatedTestRunner(test_duration=6)  # 6 seconds per test
    test_runner.run_all_tests()
    
    logger.info("Automated visual tests completed")

if __name__ == "__main__":
    main() 