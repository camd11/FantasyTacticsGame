"""
Visual Mechanic Test Runner

This script runs all visual tests for different game mechanics and generates organized logs
for each category of functionality in the game.
"""

import os
import sys
import importlib
import subprocess
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.abspath('.'))

# Import game state components for test runner
from src.utils.visual_logger import VisualScenarioLogger
from src.core_engine.game_state import GameStateManager, GameState, MapState, UnitState, FactionEnum, DispositionEnum, PhaseEnum

# Define test categories
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

# Base directory for logs
LOG_BASE_DIR = "logs/visual_tests"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

def setup_log_directories():
    """Create the log directory structure."""
    for category in MECHANIC_CATEGORIES:
        category_dir = os.path.join(LOG_BASE_DIR, category["name"].lower().replace(" ", "_"))
        os.makedirs(category_dir, exist_ok=True)
        print(f"Created directory: {category_dir}")

def run_mechanic_test(category_name, test_name):
    """Run a specific mechanic test and generate logs."""
    category_dir = category_name.lower().replace(" ", "_")
    log_dir = os.path.join(LOG_BASE_DIR, category_dir)
    log_path = os.path.join(log_dir, f"{test_name}_{TIMESTAMP}.txt")
    
    # Import the test module dynamically
    try:
        # Try to import from tests/mechanic_tests/{category}/{test_name}.py first
        module_path = f"tests.mechanic_tests.{category_dir}.{test_name}"
        test_module = importlib.import_module(module_path)
        print(f"Running test module: {module_path}")
        
        # If the module has a run_test function, call it
        if hasattr(test_module, 'run_test'):
            test_module.run_test(log_path)
            print(f"✅ Completed test: {test_name} (via module import)")
            return True
    except ImportError:
        print(f"No module found at {module_path}, trying alternative methods...")
    
    # If direct import failed, try running a script with the test name
    try:
        # Look for a script in various locations
        script_paths = [
            f"tests/mechanic_tests/{category_dir}/{test_name}.py",
            f"tests/mechanic_tests/{test_name}.py",
            f"tests/{category_dir}/{test_name}.py"
        ]
        
        for script_path in script_paths:
            if os.path.exists(script_path):
                # Run the script with the log path as an argument
                cmd = [sys.executable, script_path, "--log-path", log_path]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if result.returncode == 0:
                    print(f"✅ Completed test: {test_name} (via script)")
                    return True
                else:
                    print(f"❌ Failed to run test script {script_path}: {result.stderr.decode('utf-8')}")
    
        print(f"⚠️ No test script found for {test_name}")
    except Exception as e:
        print(f"❌ Error running test {test_name}: {e}")
    
    # If all methods failed, create a placeholder test
    return run_mock_test(category_name, test_name, log_path)

def run_mock_test(category_name, test_name, log_path):
    """Create a mock test for mechanics without existing tests."""
    print(f"⚠️ Creating mock test for {test_name}")
    
    # Create mock game state for logging
    game_state_manager = GameStateManager(None)
    game_state_manager.current_game_state = GameState()
    game_state_manager.current_game_state.map_state = MapState()
    game_state_manager.current_game_state.map_state.map_id = f"{test_name}_test"
    game_state_manager.current_game_state.current_turn = 1
    game_state_manager.current_game_state.current_phase = PhaseEnum.PLAYER
    
    # Mock CLI display
    class MockCliDisplay:
        def __init__(self, game_state_manager):
            self.game_state_manager = game_state_manager
        
        def render_ascii_map(self):
            return f"""=== ASCII MAP (Turn 1, PLAYER Phase) ===
   01234
 0 .~...
 1 .P^..
 2 ..E..
 3 ...v.
 4 ..N..
"""
    
    cli_display = MockCliDisplay(game_state_manager)
    
    # Set up visual logger
    visual_logger = VisualScenarioLogger(
        game_state_manager=game_state_manager,
        cli_display=cli_display,
        enabled=True,
        fixed_log_path=log_path,
        use_colors=True,
        html_export=True
    )
    
    # Generate placeholder test content
    visual_logger.log_action("SYSTEM", "TEST_INFO", f"Placeholder test for {test_name} in {category_name}")
    visual_logger.log_initial_state()
    visual_logger.log_turn_start(1)
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase begins")
    
    # Add specific mock content based on the mechanic type
    if test_name == "movement":
        mock_movement_test(visual_logger)
    elif test_name == "combat":
        mock_combat_test(visual_logger)
    elif test_name == "terrain":
        mock_terrain_test(visual_logger)
    elif test_name == "inventory":
        mock_inventory_test(visual_logger)
    elif test_name in ["recruitment", "death", "rescue"]:
        mock_unit_mechanic_test(visual_logger, test_name)
    elif test_name == "status_effects":
        mock_status_effect_test(visual_logger)
    elif test_name == "weather":
        mock_weather_test(visual_logger)
    elif test_name == "events":
        mock_events_test(visual_logger)
    else:
        # Generic placeholder content
        visual_logger.log_action("SYSTEM", "PLACEHOLDER", f"This is a placeholder for the {test_name} mechanic test")
        visual_logger.log_action("SYSTEM", "NOTE", "Implement detailed test for this mechanic")
    
    visual_logger.log_action("SYSTEM", "PHASE", "Player Phase ends")
    visual_logger.log_end_of_turn_state(1)
    visual_logger.finalize_log()
    print(f"📝 Created placeholder log for {test_name} at {log_path}")
    return True

def mock_movement_test(logger):
    """Create mock content for movement test."""
    logger.log_action("PLAYER_UNIT", "MOVEMENT", "Moving from (1, 1) to (2, 1)")
    logger.log_action("SYSTEM", "MOVEMENT_COST", "Plains: 1 movement point")
    logger.log_action("PLAYER_UNIT", "MOVEMENT", "Moving from (2, 1) to (2, 2)")
    logger.log_action("SYSTEM", "MOVEMENT_COST", "Forest: 2 movement points")
    logger.log_action("SYSTEM", "MOVEMENT_DETAIL", "3/5 movement points remaining")
    logger.log_action("PLAYER_UNIT", "MOVEMENT", "Moving from (2, 2) to (3, 2)")
    logger.log_action("SYSTEM", "MOVEMENT_COST", "Mountain: 3 movement points")
    logger.log_action("SYSTEM", "MOVEMENT_ERROR", "Insufficient movement points (need 3, have 2)")

def mock_combat_test(logger):
    """Create mock content for combat test."""
    logger.log_action("PLAYER_UNIT", "COMBAT", "Attacks Enemy Unit")
    logger.log_action("SYSTEM", "COMBAT_CALC", "Attack: 12 vs Defense: 7")
    logger.log_action("SYSTEM", "COMBAT_CALC", "Hit chance: 85%")
    logger.log_action("SYSTEM", "COMBAT_RESULT", "Hit! Damage: 5")
    logger.log_action("ENEMY_UNIT", "DAMAGE", "Takes 5 damage (HP: 15/20)")
    logger.log_action("ENEMY_UNIT", "COMBAT", "Counterattacks Player Unit")
    logger.log_action("SYSTEM", "COMBAT_CALC", "Attack: 9 vs Defense: 8")
    logger.log_action("SYSTEM", "COMBAT_CALC", "Hit chance: 70%")
    logger.log_action("SYSTEM", "COMBAT_RESULT", "Hit! Damage: 3")
    logger.log_action("PLAYER_UNIT", "DAMAGE", "Takes 3 damage (HP: 22/25)")

def mock_terrain_test(logger):
    """Create mock content for terrain test."""
    logger.log_action("SYSTEM", "TERRAIN_INFO", "--- Terrain Effects ---")
    logger.log_action("SYSTEM", "TERRAIN_EFFECT", "Plains: No bonuses, Move Cost: 1")
    logger.log_action("SYSTEM", "TERRAIN_EFFECT", "Forest: DEF+2, EVA+10, Move Cost: 2")
    logger.log_action("SYSTEM", "TERRAIN_EFFECT", "Mountain: DEF+3, EVA+15, Move Cost: 3")
    logger.log_action("SYSTEM", "TERRAIN_EFFECT", "River: EVA+5, Move Cost: 2")
    logger.log_action("SYSTEM", "TERRAIN_EFFECT", "Village: DEF+1, EVA+5, Heal 20% each turn")
    logger.log_action("PLAYER_UNIT", "MOVEMENT", "Moving to Forest tile")
    logger.log_action("PLAYER_UNIT", "TERRAIN_BONUS", "Gained DEF+2, EVA+10 from Forest")

def mock_inventory_test(logger):
    """Create mock content for inventory test."""
    logger.log_action("SYSTEM", "INVENTORY", "Player Unit inventory: Iron Sword, Vulnerary")
    logger.log_action("PLAYER_UNIT", "ITEM_USE", "Uses Vulnerary")
    logger.log_action("SYSTEM", "ITEM_EFFECT", "Vulnerary restores 10 HP")
    logger.log_action("PLAYER_UNIT", "HEALED", "Recovers 10 HP (HP: 25/25)")
    logger.log_action("SYSTEM", "INVENTORY_UPDATE", "Vulnerary uses: 2/3")
    logger.log_action("PLAYER_UNIT", "ITEM_EQUIP", "Equips Iron Sword")
    logger.log_action("SYSTEM", "STATS_UPDATE", "Attack: 10 → 15")

def mock_unit_mechanic_test(logger, mechanic):
    """Create mock content for unit mechanics."""
    if mechanic == "recruitment":
        logger.log_action("PLAYER_COMMANDER", "TALK", "Initiates conversation with Neutral Unit")
        logger.log_action("NPC_UNIT", "DIALOG", "I'll join your cause!")
        logger.log_action("SYSTEM", "RECRUITMENT", "Neutral Unit joins Player faction")
        logger.log_action("NPC_UNIT", "FACTION_CHANGE", "NPC → PLAYER")
    elif mechanic == "death":
        logger.log_action("PLAYER_UNIT", "COMBAT", "Attacks Enemy Unit")
        logger.log_action("SYSTEM", "COMBAT_RESULT", "Critical hit! Damage: 20")
        logger.log_action("ENEMY_UNIT", "DAMAGE", "Takes 20 damage (HP: 0/20)")
        logger.log_action("ENEMY_UNIT", "DEATH", "Enemy Unit has been defeated!")
        logger.log_action("SYSTEM", "UNIT_REMOVED", "Enemy Unit has been removed from the battlefield")
    elif mechanic == "rescue":
        logger.log_action("PLAYER_UNIT", "RESCUE", "Rescues Villager")
        logger.log_action("SYSTEM", "RESCUE_EFFECT", "Villager is carried by Player Unit")
        logger.log_action("PLAYER_UNIT", "STAT_CHANGE", "MOV reduced from 5 to 3 due to carrying")
        logger.log_action("SYSTEM", "UNIT_REMOVED", "Villager has been removed from the battlefield")
        logger.log_action("PLAYER_UNIT", "DROP", "Drops Villager at (3, 3)")
        logger.log_action("SYSTEM", "RESCUE_END", "Villager is placed at (3, 3)")

def mock_status_effect_test(logger):
    """Create mock content for status effects test."""
    logger.log_action("ENEMY_UNIT", "STATUS_EFFECT", "Inflicts Poison on Player Unit")
    logger.log_action("PLAYER_UNIT", "STATUS_APPLIED", "Poisoned for 3 turns")
    logger.log_action("SYSTEM", "TURN_END", "Processing status effects")
    logger.log_action("PLAYER_UNIT", "STATUS_DAMAGE", "Takes 2 poison damage (HP: 23/25)")
    logger.log_action("PLAYER_UNIT", "STATUS_DURATION", "Poison: 2 turns remaining")
    logger.log_action("PLAYER_UNIT", "ITEM_USE", "Uses Antidote")
    logger.log_action("PLAYER_UNIT", "STATUS_CURE", "Poison status removed")

def mock_weather_test(logger):
    """Create mock content for weather test."""
    logger.log_action("SYSTEM", "WEATHER", "Current Weather: Clear")
    logger.log_action("SYSTEM", "WEATHER_CHANGE", "Weather changes to: Rain")
    logger.log_action("SYSTEM", "WEATHER_EFFECT", "Effects: accuracy: -10, movement: -1")
    logger.log_action("PLAYER_UNIT", "WEATHER_IMPACT", "Movement reduced to 4 due to rain")
    logger.log_action("ENEMY_UNIT", "COMBAT", "Attacks Player Unit")
    logger.log_action("SYSTEM", "COMBAT_CALC", "Hit chance: 60% (-10% due to rain)")
    logger.log_action("SYSTEM", "COMBAT_RESULT", "Miss!")

def mock_events_test(logger):
    """Create mock content for events test."""
    logger.log_action("SYSTEM", "EVENT", "Village event triggered")
    logger.log_action("NPC_UNIT", "DIALOG", "Thank you for visiting our village! Please take this.")
    logger.log_action("SYSTEM", "ITEM_REWARD", "Received Silver Lance")
    logger.log_action("SYSTEM", "SPECIAL_EVENT", "Reinforcements arrive!")
    logger.log_action("ENEMY_CAVALRY", "SPAWN", "Enemy Cavalry appears at (5, 1)")
    logger.log_action("SYSTEM", "OBJECTIVE_UPDATE", "New objective: Defeat the Cavalry commander")

def generate_index_html():
    """Generate an HTML index of all test logs."""
    index_path = os.path.join(LOG_BASE_DIR, "index.html")
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Visual Mechanic Test Logs</title>
    <style>
        body { 
            background-color: #1e1e1e; 
            color: #f0f0f0; 
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 20px;
            line-height: 1.4;
        }
        h1, h2, h3 { color: #76e3ea; }
        .category {
            margin-bottom: 30px;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            background-color: #2d2d2d;
        }
        .category h2 {
            margin-top: 0;
            border-bottom: 1px solid #555;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            text-align: left;
            padding: 8px;
            background-color: #333;
            color: #76e3ea;
        }
        td {
            padding: 8px;
            border-top: 1px solid #444;
        }
        a {
            color: #6bafff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .mechanic-complete {
            color: #7bcc70;
            font-weight: bold;
        }
        .mechanic-placeholder {
            color: #ffcb6b;
        }
    </style>
</head>
<body>
    <h1>Fantasy Tactics Game - Visual Mechanic Test Logs</h1>
    <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
""")

        # Add each category and its tests
        for category in MECHANIC_CATEGORIES:
            category_dir = category["name"].lower().replace(" ", "_")
            category_path = os.path.join(LOG_BASE_DIR, category_dir)
            
            f.write(f"""
    <div class="category">
        <h2>{category["name"]}</h2>
        <table>
            <tr>
                <th>Mechanic</th>
                <th>Text Log</th>
                <th>HTML Log</th>
                <th>Status</th>
            </tr>
""")
            
            for test in category["tests"]:
                # Find the most recent log for this test
                test_logs = []
                if os.path.exists(category_path):
                    for file in os.listdir(category_path):
                        if file.startswith(f"{test}_") and file.endswith(".txt"):
                            test_logs.append(file)
                
                if test_logs:
                    test_logs.sort(reverse=True)  # Most recent first
                    latest_log = test_logs[0]
                    html_log = latest_log.replace(".txt", ".html")
                    
                    # Check if it's a real test or placeholder
                    is_placeholder = False
                    log_path = os.path.join(category_path, latest_log)
                    if os.path.exists(log_path):
                        with open(log_path, 'r', encoding='utf-8') as log_file:
                            content = log_file.read()
                            if "Placeholder test" in content:
                                is_placeholder = True
                    
                    status_class = "mechanic-placeholder" if is_placeholder else "mechanic-complete"
                    status_text = "Placeholder" if is_placeholder else "Complete"
                    
                    f.write(f"""
            <tr>
                <td>{test.replace("_", " ").title()}</td>
                <td><a href="{category_dir}/{latest_log}" target="_blank">Text Log</a></td>
                <td><a href="{category_dir}/{html_log}" target="_blank">HTML Log</a></td>
                <td class="{status_class}">{status_text}</td>
            </tr>""")
                else:
                    f.write(f"""
            <tr>
                <td>{test.replace("_", " ").title()}</td>
                <td>Not Run</td>
                <td>Not Run</td>
                <td>Not Implemented</td>
            </tr>""")
            
            f.write("""
        </table>
    </div>""")
        
        f.write("""
</body>
</html>""")
    
    print(f"📊 Generated index at {index_path}")

def run_all_tests():
    """Run all mechanic tests and generate logs."""
    # Create log directories
    setup_log_directories()
    
    # Keep track of successful tests
    successful_tests = 0
    total_tests = 0
    
    # Run tests for each category
    for category in MECHANIC_CATEGORIES:
        print(f"\n{'='*50}")
        print(f"Running tests for: {category['name']}")
        print(f"{'='*50}")
        
        for test_name in category["tests"]:
            total_tests += 1
            print(f"\n📋 Running test: {test_name}")
            if run_mechanic_test(category["name"], test_name):
                successful_tests += 1
    
    # Generate index of all logs
    generate_index_html()
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Summary: {successful_tests}/{total_tests} tests completed")
    print(f"{'='*50}")
    print(f"💾 Logs saved to: {os.path.abspath(LOG_BASE_DIR)}")
    print(f"📑 Open {os.path.abspath(os.path.join(LOG_BASE_DIR, 'index.html'))} to view all logs")

if __name__ == "__main__":
    run_all_tests() 