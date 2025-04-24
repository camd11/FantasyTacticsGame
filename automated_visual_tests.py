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
from enum import Enum

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import game renderer
from src.ui.pygame_renderer import GameRenderer, AnimationType

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
    """Fixed version of HighlightTilesAnimation."""
    def __init__(self, tile_positions, color=(100, 200, 255, 150), duration_ms=5000):
        self.tile_positions = tile_positions
        self.base_color = color
        self.color = list(color)
        self.start_time = pygame.time.get_ticks()
        self.duration_ms = duration_ms
        self.completed = False
        self.progress = 0.0
    
    def update(self):
        """Update the highlight animation."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        # Check if animation is complete
        if elapsed >= self.duration_ms:
            self.completed = True
        
        # Calculate progress from 0.0 to 1.0
        self.progress = min(1.0, elapsed / self.duration_ms)
        
        # Pulse the alpha value
        pulse = abs(math.sin(self.progress * 6.28 * 2))  # 2 complete pulses
        self.color[3] = int(self.base_color[3] * (0.5 + 0.5 * pulse))
        
        return self.completed
    
    def draw(self, surface):
        """Draw the highlighted tiles."""
        if self.completed:
            return
        
        # Create a surface for the highlight
        tile_size = 64  # Default tile size
        highlight_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, self.color, (0, 0, tile_size, tile_size))
        
        # Draw highlight over each tile
        for pos in self.tile_positions:
            pixel_x = pos[0] * tile_size
            pixel_y = pos[1] * tile_size
            surface.blit(highlight_surface, (pixel_x, pixel_y))

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
        self.game_state_manager = game_state_manager
        self.window_size = window_size
        self.title = title
        
        # Use provided screen
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Set up fonts
        self.font = pygame.font.SysFont('Arial', 14)
        self.ui_font = pygame.font.SysFont('Arial', 18, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Load assets
        self.assets = self.load_assets()
        
        # Load sounds
        self.sounds = {}  # Skip sounds for tests
        
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

# Test categories from run_all_visual_tests.py
MECHANIC_CATEGORIES = [
    {
        "name": "Core Mechanics",
        "tests": [
            "movement", 
            "combat", 
            "terrain",
            "inventory"
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
            "reinforcements"
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
        """Schedule animations for the specific test."""
        if test_name == "movement":
            self.schedule_movement_test(gsm)
        elif test_name == "combat":
            self.schedule_combat_test(gsm)
        elif test_name == "status_effects":
            self.schedule_status_effect_test(gsm)
        else:
            # Generic test animations
            self.schedule_generic_test(gsm)
    
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
        self.current_renderer.update = timed_update_function
    
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
        self.current_renderer.update = timed_update_function
    
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
        self.current_renderer.update = timed_update_function
    
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
        self.current_renderer.update = timed_update_function

def main():
    """Main entry point for automated visual tests."""
    logger.info("Starting automated visual tests")
    
    # Create and run the automated test runner
    test_runner = AutomatedTestRunner(test_duration=6)  # 6 seconds per test
    test_runner.run_all_tests()
    
    logger.info("Automated visual tests completed")

if __name__ == "__main__":
    main() 