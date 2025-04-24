#!/usr/bin/env python3
"""
Visual Tests with GUI Renderer

This script provides a GUI interface to run and visualize various game mechanic tests
using the pygame renderer instead of ASCII output.
"""

import sys
import os
import pygame
import importlib
import time
import random
from enum import Enum, auto
from pathlib import Path
import math

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import game renderer
from src.ui.pygame_renderer import GameRenderer, AnimationType

# Fix for pygame.math.sin issue
import math

# Create our own version of the HighlightTilesAnimation class if needed
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

class TestState(Enum):
    """States for the test runner."""
    MAIN_MENU = auto()
    CATEGORY_MENU = auto()
    TEST_MENU = auto()
    RUNNING_TEST = auto()

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

class VisualTestRunner:
    """GUI-based visual test runner."""
    
    def __init__(self, window_size=(1024, 768)):
        """Initialize the test runner."""
        self.window_size = window_size
        self.font = None
        self.large_font = None
        self.title_font = None
        self.screen = None
        self.state = TestState.MAIN_MENU
        self.current_category = None
        self.current_test = None
        self.clock = pygame.time.Clock()
        self.running = True
        self.renderer = None
        self.menu_offset = 0
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Fantasy Tactics - Visual Test Runner")
        
        # Load fonts
        self.font = pygame.font.SysFont("Arial", 20)
        self.large_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
    
    def run(self):
        """Main loop for the test runner."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
    
    def handle_events(self):
        """Handle user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == TestState.MAIN_MENU:
                        self.running = False
                    elif self.state == TestState.CATEGORY_MENU:
                        self.state = TestState.MAIN_MENU
                    elif self.state == TestState.TEST_MENU:
                        self.state = TestState.CATEGORY_MENU
                    elif self.state == TestState.RUNNING_TEST:
                        # Stop the test and return to test menu
                        if self.renderer:
                            self.renderer.close()
                            self.renderer = None
                        self.state = TestState.TEST_MENU
                
                elif event.key == pygame.K_UP:
                    self.menu_offset = max(0, self.menu_offset - 1)
                
                elif event.key == pygame.K_DOWN:
                    if self.state == TestState.MAIN_MENU:
                        self.menu_offset = min(len(MECHANIC_CATEGORIES) - 1, self.menu_offset + 1)
                    elif self.state == TestState.CATEGORY_MENU:
                        current_tests = MECHANIC_CATEGORIES[self.current_category]["tests"]
                        self.menu_offset = min(len(current_tests) - 1, self.menu_offset + 1)
                
                elif event.key == pygame.K_RETURN:
                    if self.state == TestState.MAIN_MENU:
                        self.current_category = self.menu_offset
                        self.state = TestState.CATEGORY_MENU
                        self.menu_offset = 0
                    
                    elif self.state == TestState.CATEGORY_MENU:
                        current_tests = MECHANIC_CATEGORIES[self.current_category]["tests"]
                        self.current_test = current_tests[self.menu_offset]
                        self.state = TestState.TEST_MENU
                        self.menu_offset = 0
                    
                    elif self.state == TestState.TEST_MENU:
                        # Start the selected test
                        if self.menu_offset == 0:  # Run the test
                            self.run_test(self.current_test)
                        else:  # Return to category menu
                            self.state = TestState.CATEGORY_MENU
                            self.menu_offset = 0
    
    def update(self):
        """Update the test runner state."""
        if self.state == TestState.RUNNING_TEST and self.renderer:
            # Update the renderer
            self.renderer.update()
    
    def render(self):
        """Render the current state of the test runner."""
        self.screen.fill((0, 0, 0))
        
        if self.state == TestState.MAIN_MENU:
            self.render_main_menu()
        elif self.state == TestState.CATEGORY_MENU:
            self.render_category_menu()
        elif self.state == TestState.TEST_MENU:
            self.render_test_menu()
        elif self.state == TestState.RUNNING_TEST and self.renderer:
            # Let the renderer handle drawing
            self.renderer.render()
        
        pygame.display.flip()
    
    def render_main_menu(self):
        """Render the main menu showing all mechanic categories."""
        title = self.title_font.render("Fantasy Tactics - Visual Test Runner", True, (255, 255, 255))
        self.screen.blit(title, (self.window_size[0]//2 - title.get_width()//2, 50))
        
        instructions = self.font.render("Select a mechanic category to test:", True, (200, 200, 200))
        self.screen.blit(instructions, (self.window_size[0]//2 - instructions.get_width()//2, 100))
        
        for i, category in enumerate(MECHANIC_CATEGORIES):
            if i == self.menu_offset:
                color = (255, 255, 0)  # Highlight selected option
                text = self.large_font.render(f"> {category['name']}", True, color)
            else:
                color = (200, 200, 200)
                text = self.font.render(f"  {category['name']}", True, color)
            
            self.screen.blit(text, (self.window_size[0]//2 - text.get_width()//2, 150 + i * 40))
        
        help_text = self.font.render("Arrow keys: Navigate | Enter: Select | ESC: Exit", True, (150, 150, 150))
        self.screen.blit(help_text, (self.window_size[0]//2 - help_text.get_width()//2, self.window_size[1] - 50))
    
    def render_category_menu(self):
        """Render the category menu showing tests within the selected category."""
        category = MECHANIC_CATEGORIES[self.current_category]
        title = self.title_font.render(f"{category['name']} Tests", True, (255, 255, 255))
        self.screen.blit(title, (self.window_size[0]//2 - title.get_width()//2, 50))
        
        instructions = self.font.render("Select a test to run:", True, (200, 200, 200))
        self.screen.blit(instructions, (self.window_size[0]//2 - instructions.get_width()//2, 100))
        
        for i, test in enumerate(category["tests"]):
            if i == self.menu_offset:
                color = (255, 255, 0)  # Highlight selected option
                text = self.large_font.render(f"> {test}", True, color)
            else:
                color = (200, 200, 200)
                text = self.font.render(f"  {test}", True, color)
            
            self.screen.blit(text, (self.window_size[0]//2 - text.get_width()//2, 150 + i * 40))
        
        help_text = self.font.render("Arrow keys: Navigate | Enter: Select | ESC: Back", True, (150, 150, 150))
        self.screen.blit(help_text, (self.window_size[0]//2 - help_text.get_width()//2, self.window_size[1] - 50))
    
    def render_test_menu(self):
        """Render the test menu for the selected test."""
        category = MECHANIC_CATEGORIES[self.current_category]["name"]
        title = self.title_font.render(f"{category} - {self.current_test}", True, (255, 255, 255))
        self.screen.blit(title, (self.window_size[0]//2 - title.get_width()//2, 50))
        
        options = ["Run Test", "Back to Category Menu"]
        
        for i, option in enumerate(options):
            if i == self.menu_offset:
                color = (255, 255, 0)  # Highlight selected option
                text = self.large_font.render(f"> {option}", True, color)
            else:
                color = (200, 200, 200)
                text = self.font.render(f"  {option}", True, color)
            
            self.screen.blit(text, (self.window_size[0]//2 - text.get_width()//2, 150 + i * 40))
        
        help_text = self.font.render("Enter: Select | ESC: Back", True, (150, 150, 150))
        self.screen.blit(help_text, (self.window_size[0]//2 - help_text.get_width()//2, self.window_size[1] - 50))
    
    def run_test(self, test_name):
        """Run the selected test with the GUI renderer."""
        print(f"Running test: {test_name}")
        
        # Create dummy game state for visualization
        gsm = self.create_test_game_state(test_name)
        
        # Create the custom renderer with our screen
        self.renderer = TestGameRenderer(gsm, window_size=self.window_size, 
                                         title=f"Visual Test: {test_name}",
                                         screen=self.screen)
        
        # Set the state to running
        self.state = TestState.RUNNING_TEST
        
        # Setup test callback
        self.renderer.handle_events = lambda: self.handle_test_events()
        
        # Center camera on a player unit if available
        if "player1" in gsm.units:
            unit = gsm.units["player1"]
            self.renderer.center_camera_on_position(unit.position[0], unit.position[1])
        
        # Schedule automatic animations based on the test type
        self.schedule_test_animations(test_name)
    
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
                    
                    # Add status effects
                    self.units["player1"].status_effects = ["POISONED"]
                    self.units["enemy1"].status_effects = ["SLOWED"]
                
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
    
    def handle_test_events(self):
        """Handle events during test execution."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.renderer:
                    self.renderer.running = False
                    self.renderer.close()
                    self.renderer = None
                self.state = TestState.TEST_MENU
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.renderer:
                        self.renderer.running = False
                        self.renderer.close()
                        self.renderer = None
                    self.state = TestState.TEST_MENU
                
                # Camera controls
                elif event.key == pygame.K_UP:
                    self.renderer.target_camera_offset[1] -= 1
                elif event.key == pygame.K_DOWN:
                    self.renderer.target_camera_offset[1] += 1
                elif event.key == pygame.K_LEFT:
                    self.renderer.target_camera_offset[0] -= 1
                elif event.key == pygame.K_RIGHT:
                    self.renderer.target_camera_offset[0] += 1
                
                # Zoom controls
                elif event.key == pygame.K_z:
                    self.renderer.adjust_zoom(-0.1)
                elif event.key == pygame.K_x:
                    self.renderer.adjust_zoom(0.1)
                
                # Toggle debug
                elif event.key == pygame.K_d:
                    self.renderer.show_debug_info = not self.renderer.show_debug_info
    
    def schedule_test_animations(self, test_name):
        """Schedule animations for the specific test."""
        if not self.renderer:
            return
        
        gsm = self.renderer.game_state_manager
        
        # Set up test-specific animations
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
        if "player1" in gsm.units:
            unit = gsm.units["player1"]
            path = [unit.position, (unit.position[0]+1, unit.position[1]), 
                   (unit.position[0]+2, unit.position[1]+1), (unit.position[0]+3, unit.position[1]+2)]
            self.renderer.play_animation(AnimationType.MOVE, unit_id="player1", path=path)
            unit.position = path[-1]
        
        if "player2" in gsm.units:
            unit = gsm.units["player2"]
            path = [unit.position, (unit.position[0], unit.position[1]+1), 
                   (unit.position[0]+1, unit.position[1]+2), (unit.position[0]+2, unit.position[1]+2)]
            # Delay second animation - use simple timer instead of event handling
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)
            
            # Add the event to the renderer's update callback
            self.player2_moved = False
            
            def original_update_method(delta_time=None):
                # Call original update method
                self.renderer.original_update(delta_time)
                
                # Check if it's time to move player2
                current_time = pygame.time.get_ticks()
                if not self.player2_moved and current_time > self.player2_move_time:
                    self.renderer.play_animation(AnimationType.MOVE, unit_id="player2", path=path)
                    unit.position = path[-1]
                    self.player2_moved = True
            
            # Store the original update method
            self.renderer.original_update = self.renderer.update
            # Replace with our custom method
            self.renderer.update = original_update_method
            # Set the time for player2 to move
            self.player2_move_time = pygame.time.get_ticks() + 2000
            self.player2_moved = False
    
    def schedule_combat_test(self, gsm):
        """Schedule animations for combat test."""
        if "player1" in gsm.units and "enemy1" in gsm.units:
            player_unit = gsm.units["player1"]
            enemy_unit = gsm.units["enemy1"]
            
            # Move player1 closer to enemy1
            path = [player_unit.position, (5, 5), (6, 6), (7, 7), (8, 8)]
            self.renderer.play_animation(AnimationType.MOVE, unit_id="player1", path=path)
            player_unit.position = path[-1]
            
            # Store original update method
            self.renderer.original_update = self.renderer.update
            self.attack_happened = False
            self.attack_time = pygame.time.get_ticks() + 3000
            
            # Create custom update method
            def custom_update_method(delta_time=None):
                # Call original update method
                self.renderer.original_update(delta_time)
                
                # Check if it's time to show attack
                current_time = pygame.time.get_ticks()
                if not self.attack_happened and current_time > self.attack_time:
                    self.renderer.play_animation(AnimationType.ATTACK, 
                                           attacker_pos=player_unit.position,
                                           defender_pos=enemy_unit.position)
                    
                    # Play damage animation right after
                    self.renderer.play_animation(AnimationType.TAKE_DAMAGE,
                                           unit_pos=enemy_unit.position,
                                           damage=5)
                    
                    # Update HP
                    enemy_unit.current_hp = max(0, enemy_unit.current_hp - 5)
                    self.attack_happened = True
            
            # Replace update method
            self.renderer.update = custom_update_method
    
    def schedule_status_effect_test(self, gsm):
        """Schedule animations for status effect test."""
        if "player1" in gsm.units:
            unit = gsm.units["player1"]
            
            # Apply status effect animation
            self.renderer.play_animation(AnimationType.APPLY_STATUS,
                                       unit_pos=unit.position,
                                       status_type="POISONED")
            
            # Store original update method
            self.renderer.original_update = self.renderer.update
            self.status_removed = False
            self.status_remove_time = pygame.time.get_ticks() + 4000
            
            # Create custom update method
            def custom_update_method(delta_time=None):
                # Call original update method
                self.renderer.original_update(delta_time)
                
                # Check if it's time to remove status
                current_time = pygame.time.get_ticks()
                if not self.status_removed and current_time > self.status_remove_time:
                    self.renderer.play_animation(AnimationType.REMOVE_STATUS,
                                           unit_pos=unit.position,
                                           status_type="POISONED")
                    self.status_removed = True
            
            # Replace update method
            self.renderer.update = custom_update_method
    
    def schedule_generic_test(self, gsm):
        """Schedule generic animations for tests without specific animations."""
        # Highlight random tiles
        random_positions = []
        for _ in range(5):
            x = random.randint(0, gsm.map_width - 1)
            y = random.randint(0, gsm.map_height - 1)
            random_positions.append((x, y))
        
        self.renderer.play_animation(AnimationType.HIGHLIGHT_TILES,
                                   tile_positions=random_positions,
                                   color=(255, 255, 0, 150),
                                   duration_ms=3000)
        
        # Move a unit if available
        if "player1" in gsm.units:
            unit = gsm.units["player1"]
            
            # Store original update method
            self.renderer.original_update = self.renderer.update
            self.unit_moved = False
            self.move_time = pygame.time.get_ticks() + 4000
            
            # Create custom update method
            def custom_update_method(delta_time=None):
                # Call original update method
                self.renderer.original_update(delta_time)
                
                # Check if it's time to move the unit
                current_time = pygame.time.get_ticks()
                if not self.unit_moved and current_time > self.move_time:
                    path = [unit.position, 
                           (unit.position[0] + 1, unit.position[1]),
                           (unit.position[0] + 1, unit.position[1] + 1),
                           (unit.position[0] + 2, unit.position[1] + 1)]
                    self.renderer.play_animation(AnimationType.MOVE, unit_id="player1", path=path)
                    unit.position = path[-1]
                    self.unit_moved = True
            
            # Replace update method
            self.renderer.update = custom_update_method

def main():
    """Main entry point."""
    # Apply our fix to GameRenderer.play_animation
    GameRenderer.play_animation = fixed_play_animation
    
    test_runner = VisualTestRunner()
    test_runner.run()

if __name__ == "__main__":
    main() 